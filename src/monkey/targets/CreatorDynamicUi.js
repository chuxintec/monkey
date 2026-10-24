'use strict';
const cc=require('cc');
const enabled=plan=>plan.uiGeometryReadback==='native-ui-layout-roundtrip-v1';
function capture(nodes){return [...nodes].map(([sourceId,n])=>({sourceId,position:[n.position.x,n.position.y,n.position.z],size:[n.getComponent(cc.UITransform).width,n.getComponent(cc.UITransform).height]}));}
function settle(scene,nodes,plan,root=null){
    if(!enabled(plan))return;
    const manager=cc.widgetManager;
    if(!manager||typeof manager.isAligning!=='boolean')throw Error('Native Widget update context unavailable');
    const previous=manager.isAligning;manager.isAligning=true;
    try{return settleOwned(scene,nodes,plan,root);}finally{manager.isAligning=previous;}
}
function settleOwned(scene,nodes,plan,root=null){
    if(!enabled(plan))return;
    scene._load();scene._activate(true);
    let differences=[];
    for(let pass=0;pass<8;pass++){
        const before=capture(nodes);
        for(const n of nodes.values())if(n.activeInHierarchy){const label=n.getComponent(cc.Label);if(label&&label.enabled)label.updateRenderData(true);}
        for(const n of nodes.values())if(n.activeInHierarchy&&n!==root){const widget=n.getComponent(cc.Widget);if(widget&&widget.enabled)widget.updateAlignment();}
        for(const n of [...nodes.values()].reverse())if(n.activeInHierarchy){const layout=n.getComponent(cc.Layout);if(layout&&layout.enabled)layout.updateLayout(true);}
        const after=capture(nodes);differences=[];
        after.forEach((row,i)=>{for(const key of ['position','size'])if(row[key].some((v,j)=>!Number.isFinite(v)||Math.abs(v-before[i][key][j])>.001))differences.push({sourceId:row.sourceId,key,before:before[i][key],after:row[key]});});
        if(!differences.length)return;
    }
    throw Error('Native UI layout did not settle within eight passes: '+JSON.stringify(differences.slice(0,2)));
}
function settleRoot(root,nodes,plan){
    if(!enabled(plan))return capture(nodes);
    const scene=new cc.Scene('OwnedPrefabLayoutProbe'),context=new cc.Node('OwnedPrefabUiContext');
    const ui=context.addComponent(cc.UITransform);ui.setContentSize(...plan.designSize);ui.setAnchorPoint(0,0);context.parent=scene;root.parent=context;
    try{settle(scene,nodes,plan,root);return capture(nodes);}
    finally{root.parent=null;scene._activate(false);scene.destroy();}
}
function expected(source,plan,rows){
    if(!enabled(plan))return source;
    const row=(rows||[]).find(x=>x.sourceId===source.sourceId);if(!row)throw Error('Native pre-save geometry absent: '+source.sourceId);
    const result={...source};
    for(const [key,axes]of Object.entries((plan.uiDrivenFields||{})[source.sourceId]||{})){
        result[key]=[...source[key]];for(const axis of axes)result[key][axis]=row[key][axis];
    }
    return result;
}
function release(scene){if(scene&&scene.activeInHierarchy)scene._activate(false);}
function state(action,node){const ui=node.getComponent(cc.UITransform),label=node.getComponent(cc.Label);return {action,size:[ui.width,ui.height],position:[node.position.x,node.position.y],fontSize:label?label.actualFontSize:0,children:node.children.map((n,index)=>{const u=n.getComponent(cc.UITransform);return {index,active:n.active,size:[u.width,u.height],position:[n.position.x,n.position.y],scale:[n.scale.x,n.scale.y]};})};}
function probe(plan,design){
    if(!enabled(plan))return [];
    const selected=new Map();for(const c of plan.components)if(c.convertible&&c.enabled&&((c.type==='cc.Label'&&c.text)||c.type==='cc.Widget'||c.type==='cc.Layout'&&[1,2].includes(c.layoutType)&&c.resize===1)){
        const key=c.type==='cc.Label'?c.type+'/'+c.overflow:c.type;if(!selected.has(key))selected.set(key,c);
    }
    const result=[],source=new Map(plan.nodes.map(n=>[n.sourceId,n]));
    for(const spec of (plan.uiStateProbeVersion>=2?(plan.uiProbeSources||[]).map(sid=>plan.components.find(c=>c.sourceId===sid)):[...selected.values()].slice(0,6))){
        const scene=new cc.Scene('OwnedDynamicUiProbe'),root=cc.instantiate(design),nodes=new Map();root.parent=scene;
        function walk(sid,n){nodes.set(sid,n);source.get(sid).children.forEach((child,i)=>walk(child,n.children[i]));}
        plan.nodes.filter(n=>n.parent===null).forEach((n,i)=>walk(n.sourceId,root.children[i]));
        try{
            const node=nodes.get(spec.node);for(let p=node;p;p=p.parent)p.active=true;
            settle(scene,nodes,plan,root);const states=[state('baseline',node)],ui=node.getComponent(cc.UITransform);
            if(spec.type==='cc.Label'){
                const label=node.getComponent(cc.Label),original=label.string;label.string=spec.overflow===3?original+'\n'+original:original+original;
                settle(scene,nodes,plan,root);states.push(state('text-change',node));
                if(spec.overflow===0&&ui.width+.01<states[0].size[0]||spec.overflow===3&&ui.height+.01<states[0].size[1])throw Error('Native text sizing did not grow');
                node.active=false;label.string=original;node.active=true;settle(scene,nodes,plan,root);states.push(state('show-original-text',node));
                if(Math.abs(ui.width-states[0].size[0])>.01||Math.abs(ui.height-states[0].size[1])>.01)throw Error('Text hidden/restore geometry differs');
            }else if(spec.type==='cc.Widget'){
                const parent=node.parent&&node.parent.getComponent(cc.UITransform);if(!parent)continue;
                const size=[parent.width,parent.height];parent.setContentSize(size[0]+40,size[1]+20);settle(scene,nodes,plan,root);states.push(state('parent-resize',node));
                node.active=false;parent.width=size[0]+80;node.active=true;settle(scene,nodes,plan,root);states.push(state('show-after-resize',node));
            }else if(plan.uiStateProbeVersion>=2){
                const first=node.children.find(n=>n.active),firstUi=first&&first.getComponent(cc.UITransform);
                const child=new cc.Node('OwnedDynamicChild');child.addComponent(cc.UITransform).setContentSize(firstUi?firstUi.width:40,firstUi?firstUi.height:20);if(first)child.setScale(first.scale);child.parent=node;
                settle(scene,nodes,plan,root);states.push(state('add-child',node));
                child.active=false;settle(scene,nodes,plan,root);states.push(state('hide-child',node));
                child.active=true;settle(scene,nodes,plan,root);states.push(state('show-child',node));
                child.parent=null;child.destroy();settle(scene,nodes,plan,root);states.push(state('remove-child',node));
                ui.setContentSize(ui.width+60,ui.height+30);settle(scene,nodes,plan,root);states.push(state('container-resize',node));
                if(first)first.setScale(first.scale.x*1.25,first.scale.y*.75,first.scale.z);
                settle(scene,nodes,plan,root);states.push(state('scale-child',node));
                if(firstUi)firstUi.setContentSize(firstUi.width+12,firstUi.height+8);
                settle(scene,nodes,plan,root);states.push(state('resize-child',node));
                node.active=false;node.active=true;settle(scene,nodes,plan,root);states.push(state('hide-show-container',node));
            }else{
                const child=new cc.Node('OwnedDynamicChild');child.addComponent(cc.UITransform).setContentSize(40,20);child.parent=node;
                settle(scene,nodes,plan,root);states.push(state('add-child',node));const axis=spec.layoutType-1;
                const extent=states[0].size[axis]+(axis===0?40:20)+spec.spacingXY[axis];
                if(Math.abs(states[1].size[axis]-extent)>.01)throw Error('Dynamic child layout extent differs');
                child.active=false;settle(scene,nodes,plan,root);states.push(state('hide-child',node));
                child.active=true;settle(scene,nodes,plan,root);states.push(state('show-child',node));
                child.parent=null;child.destroy();settle(scene,nodes,plan,root);states.push(state('remove-child',node));
                if(Math.abs(states[states.length-1].size[axis]-states[0].size[axis])>.01)throw Error('Dynamic child removal did not restore extent');
            }
            result.push({sourceId:spec.sourceId,type:spec.type,status:'native-state-changes-passed',states});
        }finally{release(scene);scene.destroy();}
    }
    return result;
}
module.exports={enabled,capture,settle,settleRoot,expected,release,probe};
