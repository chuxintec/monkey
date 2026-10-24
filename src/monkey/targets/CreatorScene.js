'use strict';
// Editor scene script. It creates an isolated native tree, never touches the open scene.
const cc = require('cc');
const motion=require('./animation.js');
const prefabs=require('./prefab.js');
const relations=require('./prefab-instances.js');
const dynamic=require('./dynamic-ui.js');
const batch=require('./batch.js');
const jobs=require('./jobs.js');
const numeric=require('./numeric-code.js');
const color = a => new cc.Color(...a);
const checkTime=plan=>{if(plan.nativeDeadlineMs&&Date.now()>=plan.nativeDeadlineMs)throw Error('NATIVE_BUDGET_EXHAUSTED');};
const loadAsset = (uuid, type) => new Promise((resolve,reject) => cc.assetManager.loadAny({uuid}, {reloadAsset:type===cc.SpriteFrame}, (e,a) => {
    if (e) reject(e); else if (!(a instanceof type)) reject(Error('Unexpected native asset type: '+uuid)); else resolve(a);
}));
function describe(root, plan) {
    const nodes=[];
    const visit=n=>{nodes.push(n);for(const child of n.children)visit(child);};visit(root);
    return {nodeCount:plan.nodes.length, treeNodeCount:nodes.length};
}
module.exports = {
    load() {}, unload() {},
    methods: {
        beginJob(method,args){return jobs.begin(method,args,module.exports.methods);},
        jobStatus(id){return jobs.status(id);},
        takeJob(id){return jobs.take(id);},
        releaseAssembly(id){relations.release(id);},
        async serializePrefab(id,sid,saved,plan){return relations.serializePrefab(id,sid,saved,plan,loadAsset);},
        async finishAssembly(id,saved,plan){return relations.finish(id,saved,plan,loadAsset);},
        async assemble(plan) {
            if (!globalThis.EditorExtends || typeof EditorExtends.serialize !== 'function') throw Error('Native serializer unavailable');
            const scene = new cc.Scene('Candidate');
            let retained=false;
            try {
                const canvasNode = new cc.Node('Canvas');canvasNode.layer=cc.Layers.Enum.UI_2D;canvasNode.parent=scene;
                canvasNode.addComponent(cc.UITransform).setContentSize(...plan.designSize);
                const canvas=canvasNode.addComponent(cc.Canvas);
                const cameraNode=new cc.Node('Camera');cameraNode.parent=scene;cameraNode.setPosition(0,0,1000);
                const camera=cameraNode.addComponent(cc.Camera);camera.projection=cc.Camera.ProjectionType.ORTHO;
                camera.orthoHeight=plan.designSize[1]/2;camera.near=1;camera.far=2000;camera.visibility=cc.Layers.Enum.UI_2D;canvas.cameraComponent=camera;
                const design = new cc.Node('DesignRoot');design.parent=canvasNode;design.layer=cc.Layers.Enum.UI_2D;
                design.addComponent(cc.UITransform).setContentSize(...plan.designSize);design.getComponent(cc.UITransform).setAnchorPoint(0,0);
                design.setPosition(-plan.designSize[0]/2,-plan.designSize[1]/2,0);
                const nodes=new Map();const sourceNodes=new Map(plan.nodes.map(n=>[n.sourceId,n]));const assets=new Map(plan.assets.map(a=>[a.sourceId,a]));
                const native=new Map();
                let loaded=0;
                await batch.map(plan.assets,16,async a=>{checkTime(plan);native.set(a.sourceId,await loadAsset(a.kind==='sprite'?a.spriteFrameUuid:a.uuid,a.kind==='sprite'?cc.SpriteFrame:a.kind==='json'?cc.JsonAsset:cc.Font));jobs.progress('textures',++loaded,plan.assets.length);});
                let nodeProgress=0;
                for(const n of plan.nodes) {
                    if(nodeProgress%256===0){jobs.progress('hierarchy',nodeProgress,plan.nodes.length);await new Promise(resolve=>setTimeout(resolve,0));}nodeProgress++;
                    checkTime(plan);
                    const node=new cc.Node(n.name);node.layer=n.sourceLayer??cc.Layers.Enum.UI_2D;nodes.set(n.sourceId,node);
                    node.setPosition(...n.position);node.setRotation(new cc.Quat(...n.rotation));node.setScale(...n.scale);
                    const ui=node.addComponent(cc.UITransform);ui.setContentSize(...n.size);ui.setAnchorPoint(...n.anchor);
                    if(n.sourceUITransformEnabled===false)ui.enabled=false;
                    if(n.opacity!==255)node.addComponent(cc.UIOpacity).opacity=n.opacity;
                    node.active=n.active;
                }
                for(const n of plan.nodes) {
                    const node=nodes.get(n.sourceId);node.parent=n.parent?nodes.get(n.parent):design;
                }
                for(const n of plan.nodes)for(let i=0;i<n.children.length;i++)nodes.get(n.children[i]).setSiblingIndex(i);
                const nativeRefs=[];const codeEntries=[];
                let componentProgress=0;
                for(const c of plan.components) {
                    if(componentProgress%256===0){jobs.progress('components',componentProgress,plan.components.length);await new Promise(resolve=>setTimeout(resolve,0));}componentProgress++;
                    checkTime(plan);
                    if(!c.convertible || c.type==='cc.LabelOutline')continue;
                    const node=nodes.get(c.node);const source=sourceNodes.get(c.node);let comp;
                    if(c.type==='cc.Sprite') {
                        comp=node.addComponent(cc.Sprite);comp.type=c.mode;comp.sizeMode=c.nativeSizeMode??c.sizeMode;comp.trim=c.trim;
                        comp.spriteFrame=c.spriteFrame?native.get(c.spriteFrame):null;comp.color=color(source.color);
                        comp.enabled=c.enabled&&!c.needsSpriteBinding;
                    } else if(c.type==='cc.Label') {
                        comp=node.addComponent(c.codeClassName?numeric.type(c):cc.Label);if(c.codeClassName)codeEntries.push({component:comp,spec:c});comp.overflow=c.nativeOverflow??c.overflow;comp.useSystemFont=false;comp.font=native.get(c.font);
                        comp.string=c.text;comp.fontSize=c.fontSize;comp.lineHeight=c.lineHeight;comp.spacingX=c.spacing;
                        comp.horizontalAlign=c.horizontalAlign;comp.verticalAlign=c.verticalAlign;
                        comp.enableWrapText=c.wrap;comp.isBold=!!c.bold;comp.isItalic=!!c.italic;comp.isUnderline=!!c.underline;comp.color=color(source.color);
                    } else if(c.type==='cc.Button') {
                        comp=node.addComponent(cc.Button);comp.target=node;comp.transition=c.transition;comp.duration=c.duration;
                        comp.zoomScale=c.zoomScale;comp.interactable=c.interactable;comp.clickEvents=[];
                    } else if(c.type==='cc.Mask') {comp=node.addComponent(cc.Mask);comp.type=cc.Mask.Type.GRAPHICS_RECT;
                    } else if(c.type==='cc.ScrollView') {
                        comp=node.addComponent(cc.ScrollView);comp.enabled=c.enabled;comp.horizontal=c.horizontal;comp.vertical=c.vertical;comp.content=nodes.get(c.content);
                    } else if(c.type==='cc.Widget') {
                        comp=node.addComponent(cc.Widget);comp.target=c.target?nodes.get(c.target):null;comp.alignMode=c.alignMode;
                        comp.isAlignTop=!!(c.flags&1);comp.isAlignBottom=!!(c.flags&4);comp.isAlignLeft=!!(c.flags&8);comp.isAlignRight=!!(c.flags&32);
                        [comp.left,comp.bottom,comp.right,comp.top]=c.margins;
                        [comp.isAbsoluteLeft,comp.isAbsoluteBottom,comp.isAbsoluteRight,comp.isAbsoluteTop]=c.absolute;
                        [comp.horizontalCenter,comp.verticalCenter]=c.center||[0,0];
                        [comp.isAbsoluteHorizontalCenter,comp.isAbsoluteVerticalCenter]=c.centerAbsolute||[true,true];
                    } else if(c.type==='cc.Layout') {
                        comp=node.addComponent(cc.Layout);comp.type=c.layoutType;comp.resizeMode=c.resize;comp.cellSize=new cc.Size(...c.cellSize);
                        [comp.paddingLeft,comp.paddingBottom,comp.paddingRight,comp.paddingTop]=c.padding;
                        [comp.spacingX,comp.spacingY]=c.spacingXY;comp.startAxis=c.startAxis;
                        comp.horizontalDirection=c.horizontalDirection;comp.verticalDirection=c.verticalDirection;comp.affectedByScale=c.affectedByScale;
                        if(c.layoutType===1)comp.alignVertical=!!c.alignCross;
                        if(c.layoutType===2)comp.alignHorizontal=!!c.alignCross;
                        comp.constraint=c.constraint||0;comp.constraintNum=c.constraintCount||2;
                    } else throw Error('Unimplemented native type: '+c.type);
                    if(c.type!=='cc.Sprite')comp.enabled=c.enabled;
                    nativeRefs.push({sourceId:c.sourceId,nodeUuid:node.uuid,componentUuid:comp.uuid,type:c.type});
                }
                for(const c of plan.components.filter(c=>c.convertible&&c.type==='cc.LabelOutline')) {
                    const label=nodes.get(c.node).getComponent(cc.Label);
                    if(!label)throw Error('Outline requires mapped Label');
                    if(!(label.font instanceof cc.BitmapFont)) {label.enableOutline=true;label.outlineColor=color(c.outlineColor);label.outlineWidth=c.width;}
                    nativeRefs.push({sourceId:c.sourceId,nodeUuid:label.node.uuid,componentUuid:label.uuid,type:c.type});
                }
                // Components are built in an isolated, non-running Scene. Flush the
                // public Label API after all properties/outlines so the default
                // "Label" measurement cannot leak into the saved UITransform.
                for(const c of plan.components.filter(c=>c.convertible&&c.type==='cc.Label')) {
                    checkTime(plan);nodes.get(c.node).getComponent(cc.Label).updateRenderData(true);
                }
                const numericCodeExercise=numeric.exercise(codeEntries);
                const animationAssets=[];
                for(const spec of plan.animations||[])if(spec.convertible) {
                    const clip=motion.create(spec,nodes);const raw=EditorExtends.serialize(clip);
                    animationAssets.push({id:spec.id,path:spec.path,serialized:typeof raw==='string'?raw:JSON.stringify(raw)});
                }
                if((plan.prefabInstances||[]).length) {
                    const assemblyId=relations.keep(plan,scene,nodes,{nativeRefs,animationAssets,numericCodeExercise,...describe(scene,plan)});
                    retained=true;return {assemblyId,nativeRefs,animationAssets,numericCodeExercise};
                }
                dynamic.settle(scene,nodes,plan);
                const nativeInitialNodes=dynamic.capture(nodes);
                const asset=new cc.SceneAsset();asset.scene=scene;
                jobs.progress('candidate-save',0,1);
                const serialized=EditorExtends.serialize(asset);
                const sourcePrefabs=await prefabs.serialize(plan,nodes);
                return {serialized:typeof serialized==='string'?serialized:JSON.stringify(serialized),nativeInitialNodes,nativeRefs,animationAssets,
                    sourcePrefabs,numericCodeExercise,
                    nodes:plan.nodes.map(n=>({sourceId:n.sourceId,nodeUuid:nodes.get(n.sourceId).uuid})),...describe(scene,plan)};
            } finally {if(!retained){dynamic.release(scene);scene.destroy();}}
        },
        async readSaved(uuid,plan) {
            const asset=await loadAsset(uuid,cc.SceneAsset);const scene=asset.scene;
            // Loading a SceneAsset alone does not perform Scene._load, which is
            // where Creator expands native instance placeholders. Initialize
            // this owned, inactive Scene without running/activating it.
            if((plan.prefabInstances||[]).length)scene._load();
            const nodes=[];const visit=n=>{nodes.push(n);for(const child of n.children)visit(child);};visit(scene);
            const design=nodes.find(n=>n.name==='DesignRoot');if(!design)throw Error('Saved scene missing DesignRoot');
            const saved=[];const walk=n=>{saved.push(n);for(const child of n.children)walk(child);};for(const n of design.children)walk(n);
            if(saved.length!==plan.nodes.length)throw Error('Saved source node count mismatch: '+saved.length+'/'+plan.nodes.length);
            // Match hierarchy by child indices; duplicate source names do not lose identity.
            const mapped=new Map(),sourceNodes=new Map(plan.nodes.map(n=>[n.sourceId,n]));
            function match(sid,n) {
                const src=sourceNodes.get(sid);if(!src||src.name!==n.name||src.children.length!==n.children.length)throw Error('Saved hierarchy differs');
                mapped.set(sid,n);src.children.forEach((id,i)=>match(id,n.children[i]));
            }
            plan.nodes.filter(n=>n.parent===null).forEach((n,i)=>match(n.sourceId,design.children[i]));
            for(const n of plan.nodes)if(n.sourceUITransformEnabled===false&&mapped.get(n.sourceId).getComponent(cc.UITransform).enabled!==false)throw Error('Saved UITransform enabled state differs');
            const labels=[];const refs=[];const numericCodeBindings=[];
            for(const c of plan.components.filter(c=>c.convertible)) {
                const n=mapped.get(c.node);const type=c.type==='cc.LabelOutline'?'Label':c.type.slice(3);const comp=n.getComponent(cc[type]);
                if(!comp)throw Error('Saved component missing: '+c.type);
                if(c.codeClassName)numericCodeBindings.push(numeric.read(comp,c));
                if(c.type==='cc.Label'&&comp.overflow!==(c.nativeOverflow??c.overflow))throw Error('Saved Label overflow policy differs: '+c.sourceId);
                if(c.type==='cc.Sprite'&&comp.sizeMode!==(c.nativeSizeMode??c.sizeMode))throw Error('Saved Sprite sizing policy differs: '+c.sourceId);
                refs.push({sourceId:c.sourceId,nodeUuid:n.uuid,componentUuid:comp.uuid,type:c.type});
                if(c.type==='cc.Label')labels.push({sourceId:c.sourceId,text:comp.string,fontUuid:comp.font&&comp.font._uuid});
            }
            const frames=[];
            const savedFrames=new Map(saved.flatMap(n=>n.getComponents(cc.Sprite)).map(s=>s.spriteFrame).filter(Boolean).map(sf=>[sf._uuid,sf]));
            for(const a of plan.assets.filter(a=>a.kind==='sprite')) {
                // Resolve from saved Sprite where available or load the importer-owned subresource.
                let sf=savedFrames.get(a.spriteFrameUuid);
                if(!sf) {
                    // Native importer identities are sent by the main process for unused source assets.
                    if(!a.spriteFrameUuid)throw Error('Native SpriteFrame identity required for readback');
                    sf=await loadAsset(a.spriteFrameUuid,cc.SpriteFrame);
                }
                frames.push({sourceId:a.sourceId,uuid:sf._uuid,textureUuid:sf.texture&&sf.texture._uuid,
                    rect:[sf.rect.x,sf.rect.y,sf.rect.width,sf.rect.height],originalSize:[sf.originalSize.width,sf.originalSize.height],
                    offset:[sf.offset.x,sf.offset.y],border:[sf.insetLeft,sf.insetTop,sf.insetRight,sf.insetBottom],
                    mesh:sf.vertices?{rawPosition:sf.vertices.rawPosition.flatMap(v=>[v.x,v.y,v.z]),indexes:Array.from(sf.vertices.indexes),uv:Array.from(sf.vertices.uv),nuv:Array.from(sf.vertices.nuv)}:null});
            }
            const animations=[];
            for(const info of plan.animationAssets||[]) {
                const spec=(plan.animations||[]).find(s=>s.id===info.id);
                animations.push(motion.read(await loadAsset(info.uuid,cc.AnimationClip),spec));
            }
            const jsonAssets=[];
            for(const a of plan.assets.filter(a=>a.kind==='json')) {
                const json=await loadAsset(a.uuid,cc.JsonAsset);jsonAssets.push({sourceId:a.sourceId,uuid:json._uuid,value:json.json});
            }
            const fontPages=[];
            for(const a of plan.assets.filter(a=>a.kind==='bitmap')) {
                const font=await loadAsset(a.uuid,cc.BitmapFont),sf=font.spriteFrame;
                if(!(sf instanceof cc.SpriteFrame)||!sf.texture)throw Error('Native BitmapFont page absent');
                fontPages.push({sourceId:a.sourceId,fontUuid:font._uuid,spriteFrameUuid:sf._uuid,textureUuid:sf.texture._uuid,
                    rect:[sf.rect.x,sf.rect.y,sf.rect.width,sf.rect.height]});
            }
            const templates=new Map();
            for(const info of plan.savedPrefabs||[])templates.set(info.sourceId,await loadAsset(info.uuid,cc.Prefab));
            const prefabInstances=relations.read(plan,mapped,templates,plan.savedPrefabs||[]);
            const sourcePrefabs=[];
            for(const spec of plan.sourcePrefabs||[]) {
                jobs.progress('native-readback',sourcePrefabs.length,(plan.sourcePrefabs||[]).length);
                if(sourcePrefabs.length%16===0)await new Promise(resolve=>setTimeout(resolve,0));
                checkTime(plan);
                const info=(plan.savedPrefabs||[]).find(p=>p.sourceId===spec.sourceId);
                if(!info)throw Error('Saved prefab identity absent');
                sourcePrefabs.push(prefabs.read(templates.get(spec.sourceId),spec,plan,info,templates));
            }
            return {dynamicUiProbes:dynamic.probe(plan,design),nativeInitialNodes:plan.nativeInitialNodes,sourcePrefabs,prefabInstances,jsonAssets,fontPages,animations,numericCodeBindings,nodeCount:saved.length,nodes:[...mapped].map(([sourceId,n])=>({sourceId,nodeUuid:n.uuid,name:n.name,
                position:[n.position.x,n.position.y,n.position.z],size:[n.getComponent(cc.UITransform).width,n.getComponent(cc.UITransform).height],
                pivot:[n.getComponent(cc.UITransform).anchorX,n.getComponent(cc.UITransform).anchorY],scale:[n.scale.x,n.scale.y,n.scale.z],
                rotation:[n.rotation.x,n.rotation.y,n.rotation.z,n.rotation.w],active:n.active,...prefabs.uiState(n,sourceNodes.get(sourceId))})),components:refs,labels,frames};
        }
    }
};
