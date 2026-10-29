'use strict';
// Editor-only native Prefab serialization; no source runtime or business execution.
const cc=require('cc');
const jobs=require('./jobs.js');
const dynamic=require('./dynamic-ui.js');
const near=(a,b)=>a.length===b.length&&a.every((v,i)=>Math.abs(v-b[i])<0.001);
function uiState(node,src) {
    if(!src.sourceGeometryProfile)return {};
    const group=node.getComponent(cc.UIOpacity);const opacity=group&&group.enabled?group.opacity:255;
    if(node.layer!==src.sourceLayer||Math.abs(opacity-src.opacity)>.001)throw Error('Source UI layer/opacity differs: '+src.sourceId);
    const state={sourceLayer:node.layer,opacity};
    if(src.verifyUiColor) {
        const renderer=node.getComponent(cc.Sprite)||node.getComponent(cc.Label);
        if(!renderer)throw Error('Source UI renderer missing: '+src.sourceId);
        const color=[renderer.color.r,renderer.color.g,renderer.color.b,renderer.color.a];
        if(!near(color,src.color))throw Error('Source renderer color differs: '+src.sourceId);
        state.color=color;
    }
    return state;
}
async function serialize(plan,nodes) {
    const result=[];
    for(const spec of plan.sourcePrefabs||[]) {
        jobs.progress('source-prefabs',result.length,(plan.sourcePrefabs||[]).length);
        if(result.length%16===0)await new Promise(resolve=>setTimeout(resolve,0));
        if(plan.nativeDeadlineMs&&Date.now()>=plan.nativeDeadlineMs)throw Error('NATIVE_BUDGET_EXHAUSTED');
        const root=cc.instantiate(nodes.get(spec.root));
        try {
            root.parent=null;
            if(spec.rootNamePolicy==='creator-asset-basename-v1')root.name=spec.nativeRootName;
            const mapped=new Map();const sources=new Map(plan.nodes.map(n=>[n.sourceId,n]));
            function walk(sid,n){mapped.set(sid,n);sources.get(sid).children.forEach((child,i)=>walk(child,n.children[i]));}walk(spec.root,root);
            const nativeInitialNodes=dynamic.settleRoot(root,mapped,plan);
            const prefab=new cc.Prefab();prefab.name=root.name;prefab.data=root;
            const raw=EditorExtends.serialize(prefab);
            result.push({sourceId:spec.sourceId,path:spec.path,nativeInitialNodes,serialized:typeof raw==='string'?raw:JSON.stringify(raw)});
        } finally {root.destroy();}
    }
    return result;
}
function read(prefab,spec,plan,info,templates) {
    const root=cc.instantiate(prefab);
    try {
        if(root.parent)throw Error('Saved prefab has external parent');
        const sources=new Map(plan.nodes.map(n=>[n.sourceId,n]));const mapped=new Map(),geometryMismatches=[];
        if(spec.rootNamePolicy&&(spec.rootNamePolicy!=='creator-asset-basename-v1'||spec.sourceRootName!==sources.get(spec.root).name||spec.nativeRootName!==spec.path.split('/').pop().slice(0,-7)))throw Error('Prefab name policy differs');
        function match(sid,node) {
            const original=sources.get(sid),src=dynamic.expected(original,plan,info.nativeInitialNodes),ui=node.getComponent(cc.UITransform);
            const expectedName=sid===spec.root&&spec.rootNamePolicy==='creator-asset-basename-v1'?spec.nativeRootName:src&&src.name;
            if(!src||expectedName!==node.name||src.children.length!==node.children.length||!ui)throw Error('Prefab hierarchy differs: '+sid);
            const actual={position:[node.position.x,node.position.y,node.position.z],scale:[node.scale.x,node.scale.y,node.scale.z],
                rotation:[node.rotation.x,node.rotation.y,node.rotation.z,node.rotation.w],size:[ui.width,ui.height],anchor:[ui.anchorX,ui.anchorY],active:node.active,...uiState(node,src)};
            const fields=Object.keys(actual).filter(key=>['active','sourceLayer','opacity'].includes(key)?actual[key]!==src[key]:!near(actual[key],src[key]));
            if(fields.length)geometryMismatches.push({sourceId:sid,fields,expected:Object.fromEntries(fields.map(key=>[key,src[key]])),actual:Object.fromEntries(fields.map(key=>[key,actual[key]]))});
            mapped.set(sid,node);src.children.forEach((child,i)=>match(child,node.children[i]));
        }
        match(spec.root,root);
        const persistent=new Map();
        function savedMap(sid,node){
            if(!node)throw Error('Saved behavior owner absent: '+sid);
            persistent.set(sid,node);sources.get(sid).children.forEach((child,i)=>savedMap(child,node.children[i]));
        }
        savedMap(spec.root,prefab.data);
        if(mapped.size!==spec.nodeCount||spec.nodes.some(id=>!mapped.has(id)))throw Error('Prefab node boundary differs');
        const assets=new Map(plan.assets.map(a=>[a.sourceId,a]));const components=[];const numericCodeBindings=[],behaviorBindings=[];
        for(const c of plan.components.filter(c=>c.convertible&&mapped.has(c.node))) {
            const node=mapped.get(c.node),comp=c.behaviorBinding?
                require('./behavior-bindings.js').read(node,c.behaviorBinding,c.enabled):node.getComponent(c.spineBinding?cc.sp.Skeleton:cc[c.type==='cc.LabelOutline'?'Label':c.type.slice(3)]);
            if(!comp)throw Error('Prefab component missing: '+c.sourceId);
            if(c.type==='cc.ProgressBar')require('./progress.js').read(comp,c,mapped);
            if(c.behaviorBinding)behaviorBindings.push(require('./behavior-bindings.js').readPersistent(persistent.get(c.node),c.behaviorBinding,c.enabled,c.sourceId,info.uuid));
            if(c.codeClassName)numericCodeBindings.push(require('./numeric-code.js').read(comp,c));
            if(c.type==='cc.Sprite'&&c.spriteFrame&&(!comp.spriteFrame||comp.spriteFrame._uuid!==assets.get(c.spriteFrame).spriteFrameUuid))throw Error('Prefab sprite reference differs');
            if(c.nativeMaterialSourceId&&(!plan.materialBinding||!comp.customMaterial||comp.customMaterial._uuid!==plan.materialBinding.creator.materialUuid||
               !require('./material-bindings.js').readBound(plan.materialBinding,comp.customMaterial,comp)))throw Error('Prefab custom material differs: '+c.sourceId);
            if(c.type==='cc.Label') {
                const fontMatches=c.nativeSystemFont?
                    comp.useSystemFont&&comp.font===null&&comp.fontFamily===c.fontFamily:
                    comp.font&&assets.get(c.font)&&comp.font._uuid===assets.get(c.font).uuid;
                if(!fontMatches||comp.string!==c.text)throw Error('Prefab font/text reference differs');
            }
            if(c.type==='cc.Label'&&comp.overflow!==(c.nativeOverflow??c.overflow))throw Error('Prefab Label overflow policy differs');
            if(c.type==='cc.Sprite'&&comp.sizeMode!==(c.nativeSizeMode??c.sizeMode))throw Error('Prefab Sprite sizing policy differs');
            if(c.type==='cc.ScrollView'&&comp.content!==mapped.get(c.content))throw Error('Prefab scroll reference escapes graph');
            if(c.type==='cc.Button'&&comp.target!==node)throw Error('Prefab button reference differs');
            if(c.type==='cc.Widget'&&comp.target!==(c.target?mapped.get(c.target):null))throw Error('Prefab widget reference differs');
            components.push(c.sourceId);
        }
        const spineSpecs=plan.components.filter(c=>c.convertible&&c.spineBinding&&mapped.has(c.node));
        const spineBindings=require('./spine-bindings.js').readCreatorSpineBindings(spineSpecs.map(c=>c.spineBinding),id=> {
            const c=spineSpecs.find(c=>c.sourceId===id);return c?persistent.get(c.node).getComponents(cc.sp.Skeleton):[];
        });
        return {...info,spineBindings,prefabInstances:require('./prefab-instances.js').read(plan,mapped,templates,plan.savedPrefabs||[],spec.sourceId),nodeCount:mapped.size,savedReloaded:true,geometryVerified:geometryMismatches.length===0,geometryMismatches,referencesVerified:true,components,
            numericCodeBindings,behaviorBindings,rootNamePolicy:spec.rootNamePolicy||'source-name-v1',sourceRootName:sources.get(spec.root).name,nativeRootName:root.name};
    } finally {root.destroy();}
}
module.exports={serialize,read,uiState};
