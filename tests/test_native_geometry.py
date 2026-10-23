import json
import shutil
import subprocess
import unittest
import tempfile
from pathlib import Path

from monkey.targets.unity import cross_axis_mapping


class NativeGeometryTests(unittest.TestCase):
    def test_saved_scale_and_rotation_are_required_without_rejecting_quaternion_sign(self):
        from monkey.targets.unity import node_geometry_matches
        source=dict(size=[100,40],anchor=[.5,.5],position=[12,20,0],scale=[1.1,1,1],rotation=[0,0,0,1],active=True)
        actual=dict(size=source['size'],pivot=source['anchor'],position=source['position'],scale=source['scale'],rotation=[0,0,0,-1],active=True)
        self.assertTrue(node_geometry_matches(actual,source,True))
        self.assertFalse(node_geometry_matches(dict(actual,scale=[1,1,1]),source,True))
        self.assertFalse(node_geometry_matches(dict(actual,rotation=[0,0,1,0]),source,True))
        self.assertFalse(node_geometry_matches(dict(actual,position=[12.002,20,0]),source,True))
        old={k:v for k,v in actual.items() if k not in ('scale','rotation')}
        self.assertTrue(node_geometry_matches(old,source,False))
        self.assertFalse(node_geometry_matches(old,source,True))

    def test_unity_prefab_count_only_receipt_does_not_prove_geometry_or_references(self):
        from fixtures import fixture
        from monkey.sources.bundle import inspect
        from monkey.normalize import normalize
        from monkey.targets import unity
        from monkey.io import write_json,sha
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();source=fixture(root/'source')
            inspect(source,[2],root/'inspect');normalize(root/'inspect/source-manifest.json',root/'ir')
            plan=unity.plan(root/'ir/ir.json','prefab-proof',root/'plan');unity.export(root/'plan/plan.json',root/'candidate')
            spec=plan['sourcePrefabs'][0];prefab=root/'candidate'/spec['path'];prefab.parent.mkdir(parents=True,exist_ok=True);prefab.write_bytes(b'native-receipt-negative-fixture')
            write_json(root/'candidate/Analysis/editor-readback.json',dict(status='partial',unityVersion='6000.6.2f1',
                nativeFiles=[dict(path=spec['path'],sha256=sha(prefab.read_bytes()))],sourcePrefabs=[dict(sourceId=spec['sourceId'],
                path=spec['path'],guid='valid-count-only',nodeCount=spec['nodeCount'],missingScripts=0)],nodes=[],sprites=[],fonts=[],labels=[],diagnostics=[],missingScripts=0))
            report=unity.verify(root/'candidate',root/'checked','editor');codes={d['code'] for d in report['diagnostics']}
            self.assertIn('SOURCE_PREFAB_GEOMETRY_NOT_VERIFIED',codes)
            self.assertIn('SOURCE_PREFAB_REFERENCE_MISMATCH',codes)
            self.assertNotIn('SOURCE_PREFAB_NOT_VERIFIED',codes)

    @unittest.skipUnless(shutil.which('node'),'Node unavailable')
    def test_asset_batches_bound_concurrency_preserve_order_and_drain_on_first_error(self):
        adapter=Path(__file__).resolve().parents[1]/'src/monkey/targets/CreatorBatch.js'
        script=r'''
const batch=require(process.argv[1]),assert=require('assert');
(async()=>{
let active=0,max=0;
const values=await batch.map([0,1,2,3,4],2,async n=>{active++;max=Math.max(max,active);await new Promise(r=>setTimeout(r,n%2?1:8));active--;return n*3;});
assert.deepStrictEqual(values,[0,3,6,9,12]);assert.strictEqual(max,2);assert.strictEqual(active,0);
const started=[];let drained=false,rejected=false;
try {await batch.map([0,1,2,3],2,async n=>{started.push(n);if(n===0)throw undefined;await new Promise(r=>setImmediate(r));drained=true;});}
catch(e){rejected=true;assert.strictEqual(e,undefined);assert.strictEqual(drained,true);}
assert.strictEqual(rejected,true);assert.deepStrictEqual(started,[0,1]);
})().catch(e=>{console.error(e);process.exitCode=1;});
'''
        subprocess.run(['node','-e',script,str(adapter)],capture_output=True,text=True,check=True)

    def test_native_alignment_preserves_scaled_pivot_and_rejects_individual_offsets(self):
        layout=dict(layoutType=2,padding=[0,0,0,0])
        parent=dict(size=[300,233.96],anchor=[.5,.5])
        def child(width,pivot,x,scale=1,active=True):
            return dict(size=[width,100],anchor=[pivot,.5],position=[x,0,0],scale=[scale,1,1],active=active)
        children=[child(100,.5,0),child(540,0,-297,1.1)]
        self.assertEqual(cross_axis_mapping(layout,parent,children),dict(crossAxisScale=True,crossAxisAlignment=.5))
        children[1]['position'][0]=-270
        self.assertEqual(cross_axis_mapping(layout,parent,children),dict(crossAxisScale=False,crossAxisAlignment=.5))
        children[1]['position'][0]=-281
        self.assertIsNone(cross_axis_mapping(layout,parent,children))
        children[1]['active']=False
        self.assertIsNotNone(cross_axis_mapping(layout,parent,children))

    def test_stretch_requires_source_parent_and_matching_initial_geometry(self):
        from monkey.targets.unity import widget_geometry_matches
        widget=dict(margins=[0,0,0,0]);node=dict(size=[750,1334],position=[0,0,0],anchor=[.5,.5])
        self.assertFalse(widget_geometry_matches(widget,node,None))
        self.assertTrue(widget_geometry_matches(widget,node,dict(size=[750,1334],anchor=[.5,.5])))
        # An inactive source panel retains its cached height. Native stretch
        # anchors would resize it even before activation; this needs an adapter.
        self.assertFalse(widget_geometry_matches(widget,node,dict(size=[750,1440],anchor=[.5,.5])))

    def test_dynamic_placeholder_is_not_a_zero_height_native_container(self):
        from monkey.targets.unity import linear_container_matches
        layout=dict(layoutType=2,padding=[0,0,0,0],spacingXY=[0,0])
        children=[dict(size=[0,0],active=True)]
        self.assertFalse(linear_container_matches(layout,dict(size=[612,319]),children))
        children[0]['size']=[612,319]
        self.assertTrue(linear_container_matches(layout,dict(size=[612,319]),children))

    def test_grid_extent_rejects_scaled_and_stale_source_cells(self):
        from monkey.targets.unity import grid_native_extent
        grid=dict(padding=[0,0,0,0],spacingXY=[0,-10])
        child=dict(size=[60,36],scale=[1,1,0],active=True)
        self.assertEqual(grid_native_extent(grid,dict(size=[240,36]),[child]),(36,None))
        self.assertEqual(grid_native_extent(grid,dict(size=[240,40]),[child])[1],'GRID_CACHED_CONTAINER_HANDOFF')
        self.assertEqual(grid_native_extent(grid,dict(size=[240,36]),[dict(child,scale=[.5,.5,1])])[1],'GRID_SCALED_CHILD_HANDOFF')

    @unittest.skipUnless(shutil.which('node'),'Node unavailable')
    def test_prefab_collects_all_geometry_differences_without_claiming_verified(self):
        adapter=Path(__file__).resolve().parents[1]/'src/monkey/targets/CreatorPrefab.js'
        script=r'''
const Module=require('module'),load=Module._load;
Module._load=function(name,...args){if(name==='cc')return {instantiate:x=>x,UITransform:class {},Widget:class {}};if(name==='./jobs.js')name=process.argv[2];return load.call(this,name,...args);};
const adapter=require(process.argv[1]);
const make=(name,width)=>({name,parent:null,children:[],position:{x:0,y:0,z:0},scale:{x:1,y:1,z:1},rotation:{x:0,y:0,z:0,w:1},active:true,
getComponent:()=>({width,height:32,anchorX:.5,anchorY:.5}),destroy(){}});
const root=make('root',100),child=make('label',85.63);root.children=[child];child.parent=root;
const spec=(sourceId,name,size,children)=>({sourceId,name,size,children,position:[0,0,0],scale:[1,1,1],rotation:[0,0,0,1],anchor:[.5,.5],active:true});
const plan={nodes:[spec('root','root',[90,32],['child']),spec('child','label',[44.17,32],[])],assets:[],components:[]};
const result=adapter.read(root,{root:'root',nodes:['root','child'],nodeCount:2},plan,{});
if(result.geometryVerified!==false||result.geometryMismatches.length!==2||!result.savedReloaded)throw Error('Geometry differences hidden');
plan.nodes[0].size=[100,32];plan.nodes[1].size=[85.63,32];
const clean=adapter.read(root,{root:'root',nodes:['root','child'],nodeCount:2},plan,{});
if(!clean.geometryVerified||clean.geometryMismatches.length)throw Error('Exact geometry rejected');
process.stdout.write(JSON.stringify(result));
'''
        result=subprocess.run(['node','-e',script,str(adapter),str(adapter.with_name('CreatorJobs.js'))],capture_output=True,text=True,check=True)
        self.assertEqual([v['sourceId'] for v in json.loads(result.stdout)['geometryMismatches']],['root','child'])
