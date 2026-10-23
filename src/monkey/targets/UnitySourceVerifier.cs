// Read-only verification of schema-derived recovery candidates. Does not invoke game methods.
using System;
using System.IO;
using System.Linq;
using System.Reflection;
using UnityEngine;
using UnityEditor;

namespace Monkey.UnityRecovery {
public static class SourceVerifier {
    [Serializable] public class Spec { public string prefabPath; public string className; public string scriptPath; public string[] fields; public string deadlineUtc; public int budgetSeconds; }
    [Serializable] public class Field { public string name; public string type; public int arrayLength; public int nullElements; }
    [Serializable] public class Result { public string status; public string unityVersion; public string prefabPath; public string guid; public string rootFileId; public string componentFileId; public string scriptGuid; public string scriptFileId; public Vector3 localPosition; public Vector3 localScale; public Quaternion localRotation; public bool active; public int nodeCount; public int missingScripts; public bool classFound; public Field[] fields; public bool saved; public string error; }
    public static void Run() {
        var result=new Result { status="failed",unityVersion=Application.unityVersion,saved=false };
        int exitCode=1;
        try {
            var spec=JsonUtility.FromJson<Spec>(File.ReadAllText("Analysis/native-check-spec.json"));
            if(!spec.prefabPath.StartsWith("Assets/",StringComparison.Ordinal) || spec.prefabPath.Contains("..") || !spec.prefabPath.EndsWith(".prefab",StringComparison.Ordinal)) throw new Exception("Unsafe prefab path");
            if(spec.budgetSeconds<1 || spec.budgetSeconds>1200)throw new Exception("Invalid method budget");
            var started=DateTime.UtcNow;
            var deadline=DateTime.Parse(spec.deadlineUtc,null,System.Globalization.DateTimeStyles.AdjustToUniversal);
            Action checkpoint=()=>{if(DateTime.UtcNow>=deadline || (DateTime.UtcNow-started).TotalSeconds>spec.budgetSeconds)throw new TimeoutException("Native readback deadline");};
            checkpoint();
            var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(spec.prefabPath);
            if(prefab==null)throw new Exception("Prefab could not be loaded");
            var nodes=prefab.GetComponentsInChildren<Transform>(true);
            result.prefabPath=spec.prefabPath;result.guid=AssetDatabase.AssetPathToGUID(spec.prefabPath);result.nodeCount=nodes.Length;
            string nativeGuid;long nativeId;
            if(!AssetDatabase.TryGetGUIDAndLocalFileIdentifier(prefab,out nativeGuid,out nativeId))throw new Exception("Prefab identity unavailable");
            result.rootFileId=nativeId.ToString(System.Globalization.CultureInfo.InvariantCulture);
            result.localPosition=prefab.transform.localPosition;result.localScale=prefab.transform.localScale;result.localRotation=prefab.transform.localRotation;result.active=prefab.activeSelf;
            result.missingScripts=nodes.Sum(t=>GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject));
            var component=prefab.GetComponentsInChildren<MonoBehaviour>(true).FirstOrDefault(c=>c!=null&&c.GetType().FullName==spec.className);
            result.classFound=component!=null;
            if(component==null)throw new Exception("Schema-derived component not registered");
            if(!AssetDatabase.TryGetGUIDAndLocalFileIdentifier(component,out nativeGuid,out nativeId))throw new Exception("Component identity unavailable");
            result.componentFileId=nativeId.ToString(System.Globalization.CultureInfo.InvariantCulture);
            var script=AssetDatabase.LoadAssetAtPath<MonoScript>(spec.scriptPath);
            if(script==null || !AssetDatabase.TryGetGUIDAndLocalFileIdentifier(script,out nativeGuid,out nativeId))throw new Exception("Script identity unavailable");
            result.scriptGuid=nativeGuid;result.scriptFileId=nativeId.ToString(System.Globalization.CultureInfo.InvariantCulture);
            result.fields=spec.fields.Select(name=>{
                checkpoint();var f=component.GetType().GetField(name,BindingFlags.Instance|BindingFlags.Public|BindingFlags.DeclaredOnly);
                if(f==null)throw new Exception("Missing schema field: "+name);
                var value=f.GetValue(component);var array=value as Array;
                int missing=array==null?0:array.Cast<object>().Count(v=>v==null || (v is UnityEngine.Object && (UnityEngine.Object)v==null));
                return new Field {name=name,type=f.FieldType.FullName,arrayLength=array==null?-1:array.Length,nullElements=missing};
            }).ToArray();
            // Missing external Sprite references are a known source gap: no dependent save/integration.
            result.status="read_only_partial";exitCode=0;
        } catch(Exception error) { result.error=error.GetType().Name+": "+error.Message; }
        Directory.CreateDirectory("Analysis");File.WriteAllText("Analysis/unity-source-readback.json",JsonUtility.ToJson(result,true));
        EditorApplication.Exit(exitCode);
    }
}
}
