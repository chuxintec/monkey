using System;
using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;

public static partial class MonkeyImporter
{
    [Serializable] public class StaticReferenceIdentity { public string field,sourceId,guid; public long localFileId; public bool persistent; }
    [Serializable] public class StaticFieldResult { public UnityStaticFields.Readback binding; public string assetGuid; public long localFileId; public StaticReferenceIdentity[] references; }
    static MonoBehaviour StaticComponent(ComponentSpec c, GameObject node) {
        var candidates=node.GetComponents<MonoBehaviour>().Where(x=>x!=null&&x.GetType().FullName==c.staticFieldBinding.typeName).ToArray();
        Func<MonoBehaviour,string> identity=x=>(string)x.GetType().GetField("__monkeySourceId").GetValue(x);
        var exact=candidates.SingleOrDefault(x=>identity(x)==c.sourceId);
        if(exact!=null||string.IsNullOrEmpty(c.staticFieldBinding.sourceTemplateId))return exact;
        return candidates.SingleOrDefault(x=>identity(x)==c.staticFieldBinding.sourceTemplateId);
    }
    static void CreateStaticFields(Plan plan, Dictionary<string,GameObject> nodes) {
        foreach(var c in plan.components.Where(x=>x.staticFieldBinding!=null&&!string.IsNullOrEmpty(x.staticFieldBinding.typeName)&&nodes.ContainsKey(x.node)))
            if(StaticComponent(c,nodes[c.node])==null)UnityStaticFields.Create(c.staticFieldBinding,nodes[c.node]);
    }
    static UnityEngine.Object StaticReference(Plan plan, Dictionary<string,GameObject> nodes,string id) {
        if(nodes.TryGetValue(id,out var node))return node;
        var c=plan.components.FirstOrDefault(x=>x.sourceId==id);
        if(c!=null&&nodes.TryGetValue(c.node,out node)) {
            if(c.staticFieldBinding!=null&&!string.IsNullOrEmpty(c.staticFieldBinding.typeName))return StaticComponent(c,node);
            if(!c.convertible)return null;
            if(c.behaviorBinding!=null&&!string.IsNullOrEmpty(c.behaviorBinding.typeName))return node.GetComponents<MonoBehaviour>().SingleOrDefault(x=>x!=null&&x.GetType().FullName==c.behaviorBinding.typeName);
            switch(c.type) {
                case "cc.Sprite":return node.GetComponent<UnityEngine.UI.Image>();
                case "cc.Label":case "cc.RichText":case "cc.LabelOutline":return node.GetComponent<TMPro.TextMeshProUGUI>();
                case "cc.Button":return node.GetComponent<UnityEngine.UI.Button>();
                case "cc.Toggle":return node.GetComponent<UnityEngine.UI.Toggle>();
                case "cc.ToggleContainer":return node.GetComponent<UnityEngine.UI.ToggleGroup>();
                case "cc.Widget":return node.GetComponent<NativeRectConstraints>();
                case "cc.Layout":return node.GetComponent<UnityEngine.UI.LayoutGroup>();
                case "cc.ScrollView":return node.GetComponent<UnityEngine.UI.ScrollRect>();
                case "cc.Mask":return node.GetComponent<UnityEngine.UI.RectMask2D>();
                case "cc.ProgressBar":return node.GetComponent<UnityEngine.UI.Slider>();
                case "cc.BlockInputEvents":return node.GetComponent<NativeInputBlocker>();
            }
            UnityEngine.Object spineComponent=null;ResolveStaticSpineReference(id,nodes,ref spineComponent);if(spineComponent==null)ResolveOptionalSpriteOutline(id,nodes,ref spineComponent);return spineComponent;
        }
        UnityEngine.Object spineAsset=null;ResolveStaticSpineReference(id,nodes,ref spineAsset);if(spineAsset==null)ResolveOptionalSpriteOutline(id,nodes,ref spineAsset);if(spineAsset!=null)return spineAsset;
        var texture=plan.textures.FirstOrDefault(x=>x.id==id);
        if(texture!=null)return AssetDatabase.LoadAssetAtPath<Sprite>(texture.path);
        if(plan.materialBinding!=null&&plan.materialBinding.materialSourceId==id)
            return AssetDatabase.LoadAssetAtPath<Material>(plan.materialBinding.materialPath);
        var asset=plan.assets.FirstOrDefault(x=>x.id==id);
        if(asset!=null)return AssetDatabase.LoadMainAssetAtPath(asset.path);
        var prefab=(plan.sourcePrefabs??Array.Empty<SourcePrefabSpec>()).FirstOrDefault(x=>x.sourceId==id);
        return prefab==null?null:AssetDatabase.LoadAssetAtPath<GameObject>(prefab.path);
    }
    static void AssignStaticFields(Plan plan, Dictionary<string,GameObject> nodes) {
        foreach(var c in plan.components.Where(x=>x.staticFieldBinding!=null&&!string.IsNullOrEmpty(x.staticFieldBinding.typeName)&&nodes.ContainsKey(x.node))) {
            var component=StaticComponent(c,nodes[c.node]);
            if(component!=null)UnityStaticFields.Assign(c.staticFieldBinding,component,id=>StaticReference(plan,nodes,id));
        }
    }
    static UnityStaticToggle.Readback ReadStaticToggles(Plan plan,Dictionary<string,GameObject> nodes) {
        if(plan.toggleBinding==null)return null;
        var spec=new UnityStaticToggle.Spec{bindings=plan.toggleBinding.bindings.Where(x=>nodes.ContainsKey(x.nodeSourceId)).ToArray()};
        var result=UnityStaticToggle.Read(spec,id=>nodes.TryGetValue(id,out var n)?n:null,id=>StaticReference(plan,nodes,id));
        if(result.fields.Any(x=>!x.verified))throw new InvalidOperationException("STATIC_TOGGLE_SAVED_READBACK_FAILED: "+JsonUtility.ToJson(result));
        return result;
    }
    static StaticFieldResult[] ReadStaticFields(Plan plan, Dictionary<string,GameObject> nodes) {
        return plan.components.Where(x=>x.staticFieldBinding!=null&&!string.IsNullOrEmpty(x.staticFieldBinding.typeName)&&nodes.ContainsKey(x.node)).Select(c=> {
            var component=StaticComponent(c,nodes[c.node]);
            var read=UnityStaticFields.Read(c.staticFieldBinding,component,id=>StaticReference(plan,nodes,id));
            string guid=null;long localId=0;
            if(component!=null)AssetDatabase.TryGetGUIDAndLocalFileIdentifier(component,out guid,out localId);
            var references=new List<StaticReferenceIdentity>();
            if(component!=null)foreach(var f in c.staticFieldBinding.fields??Array.Empty<UnityStaticFields.FieldSpec>()) {
                if(f.nullExpected||f.storageType!="UnityEngine.Object"&&f.storageType!="UnityEngine.Object[]")continue;
                var field=component.GetType().GetField(f.fieldName);
                var values=f.storageType=="UnityEngine.Object"?new[]{field?.GetValue(component) as UnityEngine.Object}:field?.GetValue(component) as UnityEngine.Object[];
                var ids=f.storageType=="UnityEngine.Object"?new[]{f.refValue}:f.refValues;
                for(int i=0;i<(values?.Length??0);i++) {
                    string refGuid=null;long refId=0;var value=values[i];
                    bool persistent=value!=null&&EditorUtility.IsPersistent(value)&&AssetDatabase.TryGetGUIDAndLocalFileIdentifier(value,out refGuid,out refId);
                    references.Add(new StaticReferenceIdentity{field=f.sourceFieldName,sourceId=ids[i],guid=refGuid,localFileId=refId,persistent=persistent});
                }
            }
            return new StaticFieldResult{binding=read,assetGuid=guid,localFileId=localId,references=references.ToArray()};
        }).ToArray();
    }
}
