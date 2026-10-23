'use strict';
// Editor-only native Prefab serialization; no source runtime or business execution.
const cc=require('cc');
const near=(a,b)=>a.length===b.length&&a.every((v,i)=>Math.abs(v-b[i])<0.001);
function serialize(plan,nodes) {
    return (plan.sourcePrefabs||[]).map(spec=>{
        const root=cc.instantiate(nodes.get(spec.root));
        try {
            root.parent=null;
            const rebind=node=>{for(const widget of node.getComponents(cc.Widget))widget.target=node.parent;for(const child of node.children)rebind(child);};
            rebind(root);
            const prefab=new cc.Prefab();prefab.name=root.name;prefab.data=root;
            const raw=EditorExtends.serialize(prefab);
            return {sourceId:spec.sourceId,path:spec.path,serialized:typeof raw==='string'?raw:JSON.stringify(raw)};
        } finally {root.destroy();}
    });
}
function read(prefab,spec,plan,info) {
    const root=cc.instantiate(prefab);
    try {
        if(root.parent)throw Error('Saved prefab has external parent');
        const sources=new Map(plan.nodes.map(n=>[n.sourceId,n]));const mapped=new Map();
        function match(sid,node) {
            const src=sources.get(sid),ui=node.getComponent(cc.UITransform);
            if(!src||src.name!==node.name||src.children.length!==node.children.length||!ui)throw Error('Prefab hierarchy differs: '+sid);
            if(!near([node.position.x,node.position.y,node.position.z],src.position)||
               !near([node.scale.x,node.scale.y,node.scale.z],src.scale)||
               !near([node.rotation.x,node.rotation.y,node.rotation.z,node.rotation.w],src.rotation)||
               !near([ui.width,ui.height],src.size)||!near([ui.anchorX,ui.anchorY],src.anchor)||node.active!==src.active)
                throw Error('Prefab local geometry differs: '+sid);
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
        return {...info,nodeCount:mapped.size,savedReloaded:true,geometryVerified:true,referencesVerified:true,components};
    } finally {root.destroy();}
}
module.exports={serialize,read};
