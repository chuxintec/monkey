'use strict';
// Editor-only native Prefab serialization; no source runtime or business execution.
const cc=require('cc');
const jobs=require('./jobs.js');
const near=(a,b)=>a.length===b.length&&a.every((v,i)=>Math.abs(v-b[i])<0.001);
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
            const rebind=node=>{for(const widget of node.getComponents(cc.Widget))widget.target=node.parent;for(const child of node.children)rebind(child);};
            rebind(root);
            const prefab=new cc.Prefab();prefab.name=root.name;prefab.data=root;
            const raw=EditorExtends.serialize(prefab);
            result.push({sourceId:spec.sourceId,path:spec.path,serialized:typeof raw==='string'?raw:JSON.stringify(raw)});
        } finally {root.destroy();}
    }
    return result;
}
function read(prefab,spec,plan,info) {
    const root=cc.instantiate(prefab);
    try {
        if(root.parent)throw Error('Saved prefab has external parent');
        const sources=new Map(plan.nodes.map(n=>[n.sourceId,n]));const mapped=new Map(),geometryMismatches=[];
        if(spec.rootNamePolicy&&(spec.rootNamePolicy!=='creator-asset-basename-v1'||spec.sourceRootName!==sources.get(spec.root).name||spec.nativeRootName!==spec.path.split('/').pop().slice(0,-7)))throw Error('Prefab name policy differs');
        function match(sid,node) {
            const src=sources.get(sid),ui=node.getComponent(cc.UITransform);
            const expectedName=sid===spec.root&&spec.rootNamePolicy==='creator-asset-basename-v1'?spec.nativeRootName:src&&src.name;
            if(!src||expectedName!==node.name||src.children.length!==node.children.length||!ui)throw Error('Prefab hierarchy differs: '+sid);
            const actual={position:[node.position.x,node.position.y,node.position.z],scale:[node.scale.x,node.scale.y,node.scale.z],
                rotation:[node.rotation.x,node.rotation.y,node.rotation.z,node.rotation.w],size:[ui.width,ui.height],anchor:[ui.anchorX,ui.anchorY],active:node.active};
            const fields=Object.keys(actual).filter(key=>key==='active'?actual[key]!==src[key]:!near(actual[key],src[key]));
            if(fields.length)geometryMismatches.push({sourceId:sid,fields,expected:Object.fromEntries(fields.map(key=>[key,src[key]])),actual:Object.fromEntries(fields.map(key=>[key,actual[key]]))});
            mapped.set(sid,node);src.children.forEach((child,i)=>match(child,node.children[i]));
        }
        match(spec.root,root);
        if(mapped.size!==spec.nodeCount||spec.nodes.some(id=>!mapped.has(id)))throw Error('Prefab node boundary differs');
        const assets=new Map(plan.assets.map(a=>[a.sourceId,a]));const components=[];
        for(const c of plan.components.filter(c=>c.convertible&&mapped.has(c.node))) {
            const node=mapped.get(c.node),comp=node.getComponent(cc[c.type==='cc.LabelOutline'?'Label':c.type.slice(3)]);
            if(!comp)throw Error('Prefab component missing: '+c.sourceId);
            if(c.type==='cc.Sprite'&&c.spriteFrame&&(!comp.spriteFrame||comp.spriteFrame._uuid!==assets.get(c.spriteFrame).spriteFrameUuid))throw Error('Prefab sprite reference differs');
            if(c.type==='cc.Label'&&(!comp.font||comp.font._uuid!==assets.get(c.font).uuid||comp.string!==c.text))throw Error('Prefab font/text reference differs');
            if(c.type==='cc.ScrollView'&&comp.content!==mapped.get(c.content))throw Error('Prefab scroll reference escapes graph');
            if(c.type==='cc.Button'&&comp.target!==node)throw Error('Prefab button reference differs');
            if(c.type==='cc.Widget'&&comp.target!==node.parent)throw Error('Prefab widget reference differs');
            components.push(c.sourceId);
        }
        return {...info,nodeCount:mapped.size,savedReloaded:true,geometryVerified:geometryMismatches.length===0,geometryMismatches,referencesVerified:true,components,
            rootNamePolicy:spec.rootNamePolicy||'source-name-v1',sourceRootName:sources.get(spec.root).name,nativeRootName:root.name};
    } finally {root.destroy();}
}
module.exports={serialize,read};
