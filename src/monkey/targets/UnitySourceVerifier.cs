// Verify schema-derived candidates; optionally save a fresh independent Prefab copy. Never invokes game methods.
using System;
using System.IO;
using System.Linq;
using System.Reflection;
using UnityEngine;
using UnityEditor;

namespace Monkey.UnityRecovery {
public static class SourceVerifier {
    [Serializable] public class Spec { public string prefabPath; public string className; public string scriptPath; public string[] fields; public string deadlineUtc; public int budgetSeconds; public bool saveRoundtrip; public int expectedSpriteReferences; }
    [Serializable] public class Field { public string name; public string type; public int arrayLength; public int nullElements; }
    [Serializable] public class Result { public string status; public string unityVersion; public string prefabPath; public string guid; public string rootFileId; public string componentFileId; public string scriptGuid; public string scriptFileId; public string scriptClass; public string[] componentTypes; public Vector3 localPosition; public Vector3 localScale; public Quaternion localRotation; public bool active; public int nodeCount; public int missingScripts; public bool classFound; public Field[] fields; public bool saved; public bool prefabReloaded; public bool referencesPreserved; public int spriteReferences; public string error; }
    static string ReferenceSignature(MonoBehaviour component,string[] names,out int count) {
        int found=0;
        var signature=string.Join("|",names.Select(name=>{
            var field=component.GetType().GetField(name,BindingFlags.Instance|BindingFlags.Public|BindingFlags.DeclaredOnly);
            if(field==null)throw new Exception("Missing schema field: "+name);
            var array=field.GetValue(component) as Array;
            return name+":"+(array==null?"null":array.Length.ToString())+":"+(array==null?"":string.Join(",",array.Cast<object>().Select(value=>{
                var asset=value as UnityEngine.Object;
                if(asset==null)throw new Exception("Unresolved dependency; save blocked");
                string guid;long id;
                if(!AssetDatabase.TryGetGUIDAndLocalFileIdentifier(asset,out guid,out id))throw new Exception("Native reference identity missing");
                if(asset is Sprite)found++;
                return guid+"/"+id.ToString(System.Globalization.CultureInfo.InvariantCulture);
            })));
        }));
        count=found;return signature;
    }
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
            var script=AssetDatabase.LoadAssetAtPath<MonoScript>(spec.scriptPath);
            if(script!=null) {
                result.scriptClass=script.GetClass()==null?"":script.GetClass().FullName;
                if(AssetDatabase.TryGetGUIDAndLocalFileIdentifier(script,out nativeGuid,out nativeId)) {result.scriptGuid=nativeGuid;result.scriptFileId=nativeId.ToString(System.Globalization.CultureInfo.InvariantCulture);}
            }
            result.componentTypes=prefab.GetComponentsInChildren<Component>(true).Select(c=>c==null?"<missing>":c.GetType().FullName).ToArray();
            var component=prefab.GetComponentsInChildren<MonoBehaviour>(true).FirstOrDefault(c=>c!=null&&c.GetType().FullName==spec.className);
            result.classFound=component!=null;
            if(component==null)throw new Exception("Schema-derived component not registered");
            if(!AssetDatabase.TryGetGUIDAndLocalFileIdentifier(component,out nativeGuid,out nativeId))throw new Exception("Component identity unavailable");
            result.componentFileId=nativeId.ToString(System.Globalization.CultureInfo.InvariantCulture);
            if(script==null || !AssetDatabase.TryGetGUIDAndLocalFileIdentifier(script,out nativeGuid,out nativeId))throw new Exception("Script identity unavailable");
            result.scriptGuid=nativeGuid;result.scriptFileId=nativeId.ToString(System.Globalization.CultureInfo.InvariantCulture);
            result.fields=spec.fields.Select(name=>{
                checkpoint();var f=component.GetType().GetField(name,BindingFlags.Instance|BindingFlags.Public|BindingFlags.DeclaredOnly);
                if(f==null)throw new Exception("Missing schema field: "+name);
                var value=f.GetValue(component);var array=value as Array;
                int missing=array==null?0:array.Cast<object>().Count(v=>v==null || (v is UnityEngine.Object && (UnityEngine.Object)v==null));
                return new Field {name=name,type=f.FieldType.FullName,arrayLength=array==null?-1:array.Length,nullElements=missing};
            }).ToArray();
            if(spec.saveRoundtrip) {
                int references;var before=ReferenceSignature(component,spec.fields,out references);
                if(references!=spec.expectedSpriteReferences)throw new Exception("Sprite reference count differs before save");
                const string folder="Assets/MonkeyRecoveryVerification";
                if(AssetDatabase.IsValidFolder(folder))throw new Exception("Fresh verification folder required");
                AssetDatabase.CreateFolder("Assets","MonkeyRecoveryVerification");
                const string copy=folder+"/Roundtrip.prefab";
                var contents=PrefabUtility.LoadPrefabContents(spec.prefabPath);
                try {
                    checkpoint();bool saved;
                    var asset=PrefabUtility.SaveAsPrefabAsset(contents,copy,out saved);
                    if(!saved || asset==null)throw new Exception("Editable prefab save failed");
                    result.saved=true;
                } finally { PrefabUtility.UnloadPrefabContents(contents); }
                AssetDatabase.ImportAsset(copy,ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);
                var reopened=PrefabUtility.LoadPrefabContents(copy);
                try {
                    checkpoint();var typed=reopened.GetComponentsInChildren<MonoBehaviour>(true).FirstOrDefault(c=>c!=null&&c.GetType().FullName==spec.className);
                    if(typed==null || reopened.GetComponentsInChildren<Transform>(true).Sum(t=>GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject))!=0)throw new Exception("Saved prefab component missing");
                    int reopenedCount;var after=ReferenceSignature(typed,spec.fields,out reopenedCount);
                    if(before!=after || references!=reopenedCount)throw new Exception("Saved prefab references changed");
                    result.prefabReloaded=true;result.referencesPreserved=true;result.spriteReferences=reopenedCount;
                } finally { PrefabUtility.UnloadPrefabContents(reopened); }
                result.status="resource_subset_verified";
            } else result.status="read_only_partial";
            exitCode=0;
        } catch(Exception error) { result.error=error.GetType().Name+": "+error.Message; }
        Directory.CreateDirectory("Analysis");File.WriteAllText("Analysis/unity-source-readback.json",JsonUtility.ToJson(result,true));
        EditorApplication.Exit(exitCode);
    }
}
}
