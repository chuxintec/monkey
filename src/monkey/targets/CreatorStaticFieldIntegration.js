'use strict';
const cc=require('cc');
const fields=require('./static-fields.js');
function specs(plan,nodes){return plan.components.filter(c=>c.staticFieldBinding&&nodes.has(c.node));}
function component(c,node){
    const ctor=cc.js.getClassByName(c.staticFieldBinding.typeName);
    if(!ctor)return null;
    const candidates=node.getComponents(ctor),exact=candidates.filter(x=>x.__monkeySourceId===c.sourceId);
    if(exact.length>1)throw Error('STATIC_CARRIER_IDENTITY_AMBIGUOUS');
    if(exact.length)return exact[0];
    const inherited=c.staticFieldBinding.sourceTemplateId?candidates.filter(x=>x.__monkeySourceId===c.staticFieldBinding.sourceTemplateId):[];
    if(inherited.length>1)throw Error('STATIC_CARRIER_TEMPLATE_IDENTITY_AMBIGUOUS');
    return inherited[0]||null;
}
function resolver(plan,nodes,assets){return id=>{
    if(nodes.has(id))return nodes.get(id);
    const c=plan.components.find(x=>x.sourceId===id);
    if(c&&nodes.has(c.node)){
        const node=nodes.get(c.node);
        if(c.staticFieldBinding)return component(c,node);
        if(!c.convertible)return null;
        if(c.behaviorBinding){const ctor=cc.js.getClassByName(c.behaviorBinding.typeName);return ctor?node.getComponent(ctor):null;}
        const type=c.spineBinding?cc.sp.Skeleton:cc[c.type==='cc.LabelOutline'?'Label':c.type.slice(3)];
        return type?node.getComponent(type):null;
    }
    return assets&&assets.get(id)||null;
};}
function createAssign(plan,nodes,assets){
    for(const c of specs(plan,nodes))if(!component(c,nodes.get(c.node)))fields.Create(c.staticFieldBinding,nodes.get(c.node));
    return specs(plan,nodes).map(c=>fields.Assign(c.staticFieldBinding,component(c,nodes.get(c.node)),resolver(plan,nodes,assets)));
}
function read(plan,nodes,assets,assetUuid){
    return specs(plan,nodes).map(c=>{
        const value=component(c,nodes.get(c.node));
        return {binding:fields.Read(c.staticFieldBinding,value,resolver(plan,nodes,assets)),assetUuid,componentUuid:value&&value.uuid};
    });
}
module.exports={createAssign,read,resolver};
