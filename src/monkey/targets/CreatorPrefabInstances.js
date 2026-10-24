'use strict';
// Creator 3.8.8 Editor-only assembly. Native PrefabInfo/overrides are serialized
// by the installed SDK; no source graph or interpreter is included in Player.
const cc=require('cc');
let current=null,sequence=0;
const api=()=>{
    const u=cc.Prefab._utils,p=globalThis.EditorExtends&&EditorExtends.PrefabUtils;
    if(!u||!p||!u.generateTargetMap||!p.addPrefabInfo||!p.checkAndStripNode)throw Error('Native Prefab SDK unavailable');
    return {u,p};
};
function session(id,plan) {
    if(!current||current.id!==id||current.plan!==plan&&current.plan.projectUuid!==plan.projectUuid)throw Error('Native assembly session differs');
    if(Date.now()>=plan.nativeDeadlineMs)throw Error('NATIVE_BUDGET_EXHAUSTED');
    return current;
}
function keep(plan,scene,nodes,result){if(current)throw Error('Native assembly session already exists');current={id:'prefabs-'+(++sequence),plan,scene,nodes,result,prepared:new Set()};return current.id;}
function release(id){if(current&&current.id===id){current.scene.destroy();current=null;}}
function mapTree(root,spec,plan) {
    const source=new Map(plan.nodes.map(n=>[n.sourceId,n])),mapped=new Map();
    function walk(id,node){const s=source.get(id);if(!s||!node||s.children.length!==node.children.length)throw Error('Native template topology differs: '+id);mapped.set(id,node);s.children.forEach((child,i)=>walk(child,node.children[i]));}
    walk(spec.root,root);return mapped;
}
function value(v,replacements=new Map()) {
    if(v==null||['string','number','boolean'].includes(typeof v))return v;
    if(replacements.has(v))return replacements.get(v);
    if(v instanceof cc.Node||v instanceof cc.Component||v instanceof cc.Asset)return v;
    if(Array.isArray(v))return v.map(x=>value(x,replacements));
    if(v instanceof cc.ValueType&&typeof v.clone==='function')return v.clone();
    if(Object.getPrototypeOf(v)===Object.prototype)return Object.fromEntries(Object.entries(v).map(([k,x])=>[k,value(x,replacements)]));
    throw Error('Unsupported native serialized override value');
}
function equal(a,b) {
    if(a===b)return true;if(a==null||b==null)return false;
    if(a instanceof cc.Asset&&b instanceof cc.Asset)return !!a._uuid&&a._uuid===b._uuid;
    if(a instanceof cc.Node||a instanceof cc.Component||b instanceof cc.Node||b instanceof cc.Component)return false;
    if(a.constructor!==b.constructor)return false;
    if(Array.isArray(a))return a.length===b.length&&a.every((v,i)=>equal(v,b[i]));
    if(typeof a==='object'){const keys=Object.keys(a);return keys.length===Object.keys(b).length&&keys.every(k=>equal(a[k],b[k]));}
    return false;
}
const excluded=new Set(['node','__prefab','_id','_objFlags','_name']);
function componentFields(comp){const keys=comp.constructor.__values__;if(!Array.isArray(keys))throw Error('Native component serialization schema absent');return keys.filter(k=>!excluded.has(k));}
function targetIds(root) {
    const {u}=api(),map={};u.generateTargetMap(root,map,true);const inverse=new Map();
    function walk(v,path){for(const [key,obj]of Object.entries(v)){const p=[...path,key];if(obj instanceof cc.Node||obj instanceof cc.Component)inverse.set(obj,p);else if(obj&&typeof obj==='object')walk(obj,p);}}
    walk(map,[]);return inverse;
}
function delta(instance,obj,key,v,ids) {
    if(equal(obj[key],v))return;
    const localID=ids.get(obj);if(!localID)throw Error('Native override target has no scoped fileID');
    const {u}=api(),patch=new u.PropertyOverrideInfo(),target=new u.TargetInfo();target.localID=localID;
    patch.targetInfo=target;patch.propertyPath=[key];patch.value=value(v);instance.propertyOverrides.push(patch);obj[key]=value(v);
}
function instanceRoots(root){const result=[];function walk(n){if(n!==root&&n._prefab&&n._prefab.instance){result.push(n);return;}n.children.forEach(walk);}walk(root);return result;}
async function prepare(state,owner,saved,load) {
    if(state.prepared.has(owner))return;
    const {plan,nodes}=state,specs=new Map(plan.sourcePrefabs.map(p=>[p.sourceId,p]));
    for(const link of (plan.prefabInstances||[]).filter(x=>x.owner===owner&&x.outermost)) {
        const info=saved.find(x=>x.sourceId===link.template),spec=specs.get(link.template);
        if(!info||!info.sha256)throw Error('Native template must be saved first');
        const asset=await load(info.uuid,cc.Prefab),root=cc.instantiate(asset),previous=nodes.get(link.root),parent=previous.parent,index=previous.getSiblingIndex();
        if(!root._prefab||!root._prefab.instance||root._prefab.asset._uuid!==info.uuid)throw Error('SDK did not create a native Prefab instance');
        const template=mapTree(root,spec,plan),replacements=new Map(),components=[];
        for(const pair of link.nodes){const old=nodes.get(pair.instanceObject),node=template.get(pair.templateObject);if(!old||!node)throw Error('Instance node correspondence absent');replacements.set(old,node);
            const used=new Map();for(const from of old.components){const cls=from.constructor,i=used.get(cls)||0;used.set(cls,i+1);const to=node.getComponents(cls)[i];if(!to)throw Error('Mounted component needs native delta adapter');replacements.set(from,to);components.push([from,to]);}
            if(node.components.length!==old.components.length)throw Error('Removed component needs native delta adapter');
        }
        const ids=targetIds(root),instance=root._prefab.instance;
        for(const pair of link.nodes){const old=nodes.get(pair.instanceObject),node=replacements.get(old);for(const key of ['_name','_active','_layer','_lpos','_lrot','_lscale'])delta(instance,node,key,value(old[key],replacements),ids);}
        for(const [from,to]of components)for(const key of componentFields(from))delta(instance,to,key,value(from[key],replacements),ids);
        root.parent=parent;root.setSiblingIndex(index);
        for(const pair of link.nodes)nodes.set(pair.instanceObject,replacements.get(nodes.get(pair.instanceObject)));
        // Known native node references outside this instance must follow replacements.
        for(const node of nodes.values())for(const c of node.components)for(const key of componentFields(c)){
            if(replacements.has(c[key]))c[key]=replacements.get(c[key]);
        }
        previous.parent=null;previous.destroy();
    }
    state.prepared.add(owner);
}
async function serializePrefab(id,sid,saved,plan,load) {
    const state=session(id,plan),spec=plan.sourcePrefabs.find(p=>p.sourceId===sid);if(!spec)throw Error('Unexpected native prefab owner');
    await prepare(state,sid,saved,load);
    const root=cc.instantiate(state.nodes.get(spec.root));
    try {
        root.parent=null;root.name=spec.nativeRootName;
        const prefab=new cc.Prefab();prefab.name=root.name;prefab.data=root;
        const {p}=api();
        if(root._prefab&&root._prefab.instance)throw Error('Creator root template inheritance requires a dedicated native asset contract');
        p.addPrefabInfo(root,root,prefab);root._prefab.nestedPrefabInstanceRoots=instanceRoots(root);
        p.checkAndStripNode(root,true);
        const raw=EditorExtends.serialize(prefab);return {sourceId:sid,path:spec.path,serialized:typeof raw==='string'?raw:JSON.stringify(raw)};
    }finally{root.destroy();}
}
async function finish(id,saved,plan,load) {
    const state=session(id,plan);
    try {
        for(const owner of new Set(plan.prefabInstances.map(x=>x.owner)))await prepare(state,owner,saved,load);
        const {u,p}=api(),info=new u.PrefabInfo();info.root=state.scene;info.nestedPrefabInstanceRoots=instanceRoots(state.scene);state.scene._prefab=info;
        p.checkAndStripNode(state.scene,true);
        const asset=new cc.SceneAsset();asset.scene=state.scene;const raw=EditorExtends.serialize(asset);
        return {...state.result,serialized:typeof raw==='string'?raw:JSON.stringify(raw)};
    }finally{release(id);}
}
function read(plan,mapped,templates,saved,owner=null){
    const rows=[];
    for(const link of (plan.prefabInstances||[]).filter(x=>owner===null||x.owner===owner)){
        const root=mapped.get(link.root),info=saved.find(x=>x.sourceId===link.template),spec=plan.sourcePrefabs.find(x=>x.sourceId===link.template),asset=templates.get(link.template);
        const actual=root&&root._prefab;if(!actual||!actual.instance||!actual.asset||actual.asset._uuid!==info.uuid)throw Error('Saved native instance template UUID differs: '+link.root);
        const canonical=mapTree(asset.data,spec,plan);
        for(const pair of link.nodes){const n=mapped.get(pair.instanceObject),t=canonical.get(pair.templateObject);if(!n||!t||!n._prefab||!t._prefab||n._prefab.fileId!==t._prefab.fileId||n._prefab.asset._uuid!==t._prefab.asset._uuid)throw Error('Saved native node fileID/asset correspondence differs: '+pair.instanceObject);}
        rows.push({root:link.root,templateSourceId:link.template,templatePath:spec.path,templateUuid:info.uuid,templateRootFileId:asset.data._prefab.fileId,nodeCount:link.nodes.length,nativeInstance:true,correspondingSourceVerified:true,nodeCorrespondenceVerified:true,templateUnchanged:true,propertyModificationCount:actual.instance.propertyOverrides.length});
    }
    return rows;
}
module.exports={keep,release,serializePrefab,finish,read};
