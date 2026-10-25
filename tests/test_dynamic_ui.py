import copy,unittest,shutil,subprocess
from pathlib import Path
from monkey.targets.dynamic_ui import POLICY,expectations,verify_probes,probe_sources

class DynamicUiEvidenceTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'),'Node unavailable')
    def test_creator_recursive_alignment_keeps_disabled_ancestor_and_restores_lookup(self):
        script=r'''
const Module=require('module'),load=Module._load,assert=require('assert');class Widget{}class UITransform{}
Module._load=function(name,...args){return name==='cc'?{Widget,UITransform}:load.call(this,name,...args);};
const api=require(process.argv[1]),parentWidget={enabled:false},ui={},parent={x:-240,activeInHierarchy:true,getComponent(type){return type===Widget?parentWidget:ui;}},original=Object.getOwnPropertyDescriptor(parent,'getComponent');
const child={x:0,activeInHierarchy:true,getComponent(type){return type===Widget?childWidget:ui;}};
const childWidget={enabled:true,updateAlignment(){if(parent.getComponent(Widget))parent.x=-236;child.x=parent.x+10;assert.strictEqual(parent.getComponent(UITransform),ui);}};
const nodes=new Map([['parent',parent],['child',child]]);api.alignWidgets(nodes,null);
assert.strictEqual(parent.x,-240);assert.strictEqual(child.x,-230);assert.deepStrictEqual(Object.getOwnPropertyDescriptor(parent,'getComponent'),original);
childWidget.updateAlignment=()=>{throw Error('alignment failed');};assert.throws(()=>api.alignWidgets(nodes,null),/alignment failed/);
assert.deepStrictEqual(Object.getOwnPropertyDescriptor(parent,'getComponent'),original);assert.strictEqual(parent.getComponent(Widget),parentWidget);
'''
        path=Path(__file__).resolve().parents[1]/'src/monkey/targets/CreatorDynamicUi.js'
        result=subprocess.run(['node','-e',script,str(path)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr[:2000])

    @unittest.skipUnless(shutil.which('node'),'Node unavailable')
    def test_creator_audio_readback_uses_native_duration_method_and_rejects_invalid_value(self):
        script=r'''
const Module=require('module'),load=Module._load,assert=require('assert');
class SceneAsset{}class AudioClip{getDuration(){return this.seconds;}get duration(){throw Error('No duration property in Creator 3.8');}}
const asset=new SceneAsset();asset.scene={name:'Scene',children:[{name:'DesignRoot',children:[]}]};
const clip=new AudioClip();clip._uuid='audio-id';clip.seconds=3.25;
const cc={SceneAsset,AudioClip,assetManager:{loadAny(request,options,callback){callback(null,request.uuid==='scene-id'?asset:clip);}}};
Module._load=function(name,...args){
 if(name==='cc')return cc;
 if(name==='./prefab-instances.js')return {read:()=>[]};
 if(name==='./dynamic-ui.js')return {probe:async()=>[]};
 if(['./animation.js','./prefab.js','./batch.js','./jobs.js','./numeric-code.js'].includes(name))return {};
 return load.call(this,name,...args);
};
(async()=>{
 const api=require(process.argv[1]),plan={nodes:[],components:[],assets:[{kind:'audio',uuid:'audio-id',sourceId:'source-audio'}]};
 const result=await api.methods.readSaved('scene-id',plan);assert.deepStrictEqual(result.audioAssets,[{sourceId:'source-audio',uuid:'audio-id',duration:3.25}]);
 clip.seconds=NaN;await assert.rejects(api.methods.readSaved('scene-id',plan),/duration unavailable/);
})().catch(e=>{console.error(e);process.exitCode=1;});
'''
        path=Path(__file__).resolve().parents[1]/'src/monkey/targets/CreatorScene.js'
        result=subprocess.run(['node','-e',script,str(path)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr[:2000])

    @unittest.skipUnless(shutil.which('node'),'Node unavailable')
    def test_creator_probe_keeps_layout_siblings_without_cloning_unrelated_source_trees(self):
        script=r'''
const Module=require('module'),load=Module._load,assert=require('assert');
class UITransform{setContentSize(w,h){this.width=w;this.height=h;}setAnchorPoint(x,y){this.anchorX=x;this.anchorY=y;}}
class Node{
 constructor(name){this.name=name;this.children=[];this.ui=new UITransform();this.position={x:1,y:2,z:3};this.rotation={x:0,y:0,z:0,w:1};this.scale={x:1,y:1,z:1};this.layer=7;}
 addComponent(){return this.ui;}getComponent(){return this.ui;}
 setPosition(v){this.position={...v};}setRotation(v){this.rotation={...v};}setScale(v){this.scale={...v};}
 set parent(n){this._parent=n;if(n)n.children.push(this);}get parent(){return this._parent;}destroy(){this.destroyed=true;}
}
const cloned=[];function instantiate(n){cloned.push(n.name);const out=new Node(n.name);for(const child of n.children)instantiate(child).parent=out;return out;}
Module._load=function(name,...args){return name==='cc'?{Node,UITransform,instantiate}:load.call(this,name,...args);};
const api=require(process.argv[1]),design=new Node('DesignRoot');design.ui.setContentSize(750,1334);design.ui.setAnchorPoint(0,0);design.position.x=-375;
const owner=new Node('SourceA'),sibling=new Node('Sibling'),selected=new Node('Label'),unrelated=new Node('SourceB');
owner.parent=design;unrelated.parent=design;selected.parent=owner;sibling.parent=owner;
const plan={nodes:[{sourceId:'a',name:'SourceA',parent:null,children:['label','sibling']},{sourceId:'label',name:'Label',parent:'a',children:[]},{sourceId:'sibling',name:'Sibling',parent:'a',children:[]},{sourceId:'b',name:'SourceB',parent:null,children:[]}],components:[]};
const result=api.probeRoot(plan,design,{node:'label'});
assert.deepStrictEqual(cloned,['SourceA','Label','Sibling']);assert.deepStrictEqual([...result.nodes.keys()],['a','label','sibling']);
assert.notStrictEqual(result.nodes.get('label'),selected);assert.strictEqual(result.nodes.get('label').parent,result.nodes.get('sibling').parent);
assert.deepStrictEqual(result.root.position,design.position);assert.strictEqual(result.root.ui.width,750);assert.strictEqual(result.root.ui.anchorX,0);
assert.strictEqual(design.children.length,2);assert.strictEqual(selected.parent,owner);
plan.components.push({sourceId:'externalWidget',type:'cc.Widget',convertible:true,node:'label',target:'b'});
assert.throws(()=>api.probeRoot(plan,design,{node:'label'}),/crosses source roots/);
assert.strictEqual(cloned.length,3);assert.strictEqual(design.children.length,2);
'''
        path=Path(__file__).resolve().parents[1]/'src/monkey/targets/CreatorDynamicUi.js'
        result=subprocess.run(['node','-e',script,str(path)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr[:2000])

    def test_v2_grid_and_child_resize_cannot_pass_with_only_container_snapshots(self):
        components=[dict(sourceId='grid',node='root',type='cc.Layout',layoutType=3,resize=1,affectedByScale=True,enabled=True,convertible=True),dict(sourceId='fill',node='column',type='cc.Layout',layoutType=2,resize=2,enabled=True,convertible=True)]
        plan=dict(uiGeometryReadback=POLICY,uiStateProbeVersion=2,nodes=[],components=components)
        self.assertEqual(probe_sources(plan),['grid','fill']);self.assertTrue(verify_probes(plan,[]))
        actions=['baseline','add-child','hide-child','show-child','remove-child','container-resize','scale-child','resize-child','hide-show-container']
        rows=[dict(sourceId=c['sourceId'],type=c['type'],status='native-state-changes-passed',states=[dict(action=a,size=[100,50],position=[0,0])for a in actions])for c in components]
        self.assertTrue(verify_probes(plan,rows))
        for row in rows:
            for state in row['states']:state['children']=[dict(index=0,active=True,size=[40,20],position=[1,2],scale=[.8,.8])]
        self.assertEqual(verify_probes(plan,rows),[])
        rows[0]['states'][0]['children'][0]['scale'][0]=float('nan');self.assertTrue(verify_probes(plan,rows))

    @unittest.skipUnless(shutil.which('node'),'Node unavailable')
    def test_creator_editor_alignment_context_is_restored_on_success_and_failure(self):
        script=r'''
const Module=require('module'),load=Module._load,assert=require('assert');
class Label{}class Widget{}class Layout{}class UITransform{}
const manager={isAligning:false},ui={width:10,height:20};
const widget={enabled:true,updateAlignment(){assert(manager.isAligning);ui.width=100;}};
const node={activeInHierarchy:true,position:{x:0,y:0,z:0},getComponent(t){return t===UITransform?ui:t===Widget?widget:null;}};
Module._load=function(name,...args){return name==='cc'?{Label,Widget,Layout,UITransform,widgetManager:manager}:load.call(this,name,...args);};
const api=require(process.argv[1]),plan={uiGeometryReadback:'native-ui-layout-roundtrip-v1'};
const scene={_load(){},_activate(){assert(manager.isAligning);}};
api.settle(scene,new Map([['node',node]]),plan);assert.strictEqual(ui.width,100);assert.strictEqual(manager.isAligning,false);
scene._activate=()=>{throw Error('owned activation failed');};
assert.throws(()=>api.settle(scene,new Map([['node',node]]),plan),/owned activation failed/);assert.strictEqual(manager.isAligning,false);
manager.isAligning=true;assert.throws(()=>api.settle(scene,new Map([['node',node]]),plan),/owned activation failed/);assert.strictEqual(manager.isAligning,true);
'''
        path=Path(__file__).resolve().parents[1]/'src/monkey/targets/CreatorDynamicUi.js'
        result=subprocess.run(['node','-e',script,str(path)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr[:2000])

    def test_driven_geometry_does_not_hide_other_axes_or_mutate_source(self):
        source=dict(sourceId='parent#1',position=[4,5,6],size=[20,30],anchor=[.5,.5])
        plan=dict(uiGeometryReadback=POLICY,nodes=[source],components=[dict(sourceId='label',node='parent#1',type='cc.Label',convertible=True,enabled=True,overflow=3,text='source')])
        original=copy.deepcopy(plan)
        expected,gaps=expectations(plan,[dict(sourceId='parent#1',position=[999,999,999],size=[999,60])],'scene')
        self.assertFalse(gaps);self.assertEqual(expected[0]['size'],[20,60]);self.assertEqual(expected[0]['position'],[4,5,6]);self.assertEqual(plan,original)
        _,gaps=expectations(plan,[dict(sourceId='parent#1',size=[20,float('nan')])],'scene');self.assertTrue(gaps)
        _,gaps=expectations(plan,[],'scene');self.assertTrue(gaps)

    @unittest.skipUnless(shutil.which('node'),'Node unavailable')
    def test_creator_initial_activation_defaults_do_not_replace_source_or_later_edits(self):
        script=r'''
const Module=require('module'),load=Module._load,assert=require('assert');
class UITransform{}class Label{}class Widget{}class Layout{}
const manager={isAligning:false},ui={width:0,height:0,setContentSize(w,h){this.width=w;this.height=h;}};
const node={activeInHierarchy:true,position:{x:-240,y:0,z:0},setPosition(x,y,z){this.position={x,y,z};},getComponent(t){return t===UITransform?ui:null;}};
Module._load=function(name,...args){return name==='cc'?{UITransform,Label,Widget,Layout,widgetManager:manager}:load.call(this,name,...args);};
const api=require(process.argv[1]);let activated=false;
const scene={_load(){},_activate(){if(!activated){activated=true;ui.setContentSize(300,200);node.position.x=-236;}}};
const plan={uiGeometryReadback:'native-ui-layout-roundtrip-v1',nodes:[{sourceId:'n',position:[-240,0,0],size:[0,0]}]},nodes=new Map([['n',node]]);
api.settle(scene,nodes,plan,null,true);assert.strictEqual(ui.height,0);assert.strictEqual(node.position.x,-240);
ui.setContentSize(70,80);node.position.x=42;api.settle(scene,nodes,plan);
assert.strictEqual(ui.height,80);assert.strictEqual(node.position.x,42);assert.strictEqual(manager.isAligning,false);
// A separately instantiated prefab activates again: restore its own settled
// geometry, not every node in the project or the original unlaid-out source.
activated=false;plan.nodes.push({sourceId:'unrelated',position:[0,0,0],size:[10,10]});
const saved=api.capture(nodes);api.settle(scene,nodes,plan,null,saved);
assert.strictEqual(ui.height,80);assert.strictEqual(node.position.x,42);
activated=false;plan.uiDrivenFields={n:{size:[0,1]}};
api.settle(scene,nodes,plan,null,saved);
assert.strictEqual(ui.width,300);assert.strictEqual(ui.height,200);assert.strictEqual(node.position.x,42);
'''
        path=Path(__file__).resolve().parents[1]/'src/monkey/targets/CreatorDynamicUi.js'
        result=subprocess.run(['node','-e',script,str(path)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr[:2000])

    def test_layout_allows_only_declared_main_axis_and_probe_identity_is_required(self):
        parent=dict(sourceId='graph#0',position=[0,0,0],size=[100,50],children=['graph#1'])
        child=dict(sourceId='graph#1',position=[3,17,0],size=[40,20],children=[])
        layout=dict(sourceId='layout',type='cc.Layout',node='graph#0',convertible=True,enabled=True,layoutType=1,resize=1,alignCross=False)
        plan=dict(uiGeometryReadback=POLICY,nodes=[parent,child],components=[layout])
        expected,gaps=expectations(plan,[dict(sourceId='graph#0',size=[80,999]),dict(sourceId='graph#1',position=[25,999,999])],'scene')
        self.assertFalse(gaps);self.assertEqual(expected[0]['size'],[80,50]);self.assertEqual(expected[1]['position'],[25,17,0])
        self.assertTrue(verify_probes(plan,[]))
        proof=dict(sourceId='layout',type='cc.Layout',status='native-state-changes-passed',states=[dict(action=a,size=[100,50],position=[0,0])for a in ['baseline','add-child','hide-child','show-child','remove-child']])
        self.assertEqual(verify_probes(plan,[proof]),[])
        proof['states'].pop();self.assertTrue(verify_probes(plan,[proof]))

if __name__=='__main__':unittest.main()
