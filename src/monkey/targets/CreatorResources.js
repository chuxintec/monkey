'use strict';
// Resource-only nodes live outside the source hierarchy. No recovered program is attached.
const cc=require('cc');
async function attach(plan,canvas,loadAsset) {
    if(!plan.resourceProbes)return;
    if(plan.resourceProbes.profile!=='creator-spine-3.8-v1')throw Error('Unsupported resource probe profile');
    const root=new cc.Node('NativeResourceProbes');root.parent=canvas;
    for(const spec of plan.resourceProbes.spines) {
        const node=new cc.Node(spec.nodeName);node.parent=root;node.layer=cc.Layers.Enum.UI_2D;
        node.addComponent(cc.UITransform);
        const skeleton=node.addComponent(cc.sp.Skeleton);skeleton.skeletonData=await loadAsset(spec.skeletonUuid,cc.sp.SkeletonData);
    }
}
function pose(skeleton,bones) {
    return bones.slice(0,128).map(data=>{
        const b=skeleton.findBone(data.name);if(!b)throw Error('Native Spine bone missing');
        const values=[b.worldX,b.worldY,b.a,b.b,b.c,b.d];
        if(!values.every(Number.isFinite))throw Error('Native Spine bone pose is nonfinite');
        return values;
    });
}
function applyPose(skeleton,bones) {
    // The detached scene has no render-loop update. Apply the native animation
    // state to the actual component's native skeleton before reading transforms.
    const bone=skeleton.findBone(bones[0].name),state=skeleton.getState();
    const model=bone&&bone.skeleton;
    if(!state||!model)throw Error('Native Spine model/state unavailable');
    state.apply(model);model.updateWorldTransform();
    return pose(skeleton,bones);
}
async function read(plan,scene) {
    if(!plan.resourceProbes)return null;
    const root=scene.getChildByName('Canvas').getChildByName('NativeResourceProbes');if(!root)throw Error('Saved resource probe root missing');
    const rows=[];
    for(const spec of plan.resourceProbes.spines) {
        const nodes=root.children.filter(n=>n.name===spec.nodeName);if(nodes.length!==1)throw Error('Saved Spine probe identity ambiguous');
        const skeleton=nodes[0].getComponent(cc.sp.Skeleton),data=skeleton&&skeleton.skeletonData;
        if(!(data instanceof cc.sp.SkeletonData)||data._uuid!==spec.skeletonUuid)throw Error('Saved Spine asset reference differs');
        if(data.textureNames.length!==spec.pages.length||data.textures.length!==spec.pages.length)throw Error('Native Spine page count differs');
        const textures=spec.pages.map((p,i)=>{
            if(data.textureNames[i]!==p.name||data.textures[i]._uuid!==p.textureUuid)throw Error('Native Spine texture name/UUID differs');
            return {name:p.name,imageUuid:p.imageUuid,textureUuid:p.textureUuid,nativeUuid:data.textures[i]._uuid};
        });
        const runtime=data.getRuntimeData();if(!runtime||!runtime.bones.length||runtime.bones.length>4096)throw Error('Native Spine runtime data unavailable');
        const animation=runtime.animations.find(a=>Number.isFinite(a.duration)&&a.duration>0);
        if(!animation)throw Error('No finite sourced animation for native playback probe');
        // Inactive Scene deserialization does not run component lifecycle. Initialize
        // the existing saved native reference through its public setter, then sample it.
        skeleton.skeletonData=null;skeleton.skeletonData=data;
        const entry=skeleton.setAnimation(0,animation.name,true);if(!entry)throw Error('Native Spine animation did not start');
        skeleton.updateAnimation(0);const before=entry.trackTime,first=applyPose(skeleton,runtime.bones);
        skeleton.updateAnimation(Math.min(.125,animation.duration/4));
        const after=entry.trackTime,last=applyPose(skeleton,runtime.bones);
        if(!(Number.isFinite(before)&&Number.isFinite(after)&&after>before))throw Error('Native Spine animation state did not advance');
        if(JSON.stringify(first)===JSON.stringify(last))throw Error('Selected native Spine pose did not change');
        rows.push({sourceId:spec.sourceId,skeletonUuid:data._uuid,sourceSkeletonSha256:spec.sourceSkeletonSha256,
            version:spec.version,savedReferenceVerified:true,textures,bones:runtime.bones.length,slots:runtime.slots.length,
            animation:animation.name,duration:animation.duration,trackTimeBefore:before,trackTimeAfter:after,
            nativeStateAdvanced:true,poseChanged:true,sampledBones:first.length});
    }
    return {profile:plan.resourceProbes.profile,spines:rows};
}
module.exports={attach,read};
