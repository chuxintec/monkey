import json
import shutil
import subprocess
import unittest
from pathlib import Path

from monkey.targets.unity_layout import cross_axis_mapping


class NativeGeometryTests(unittest.TestCase):
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

    @unittest.skipUnless(shutil.which('node'),'Node unavailable')
    def test_prefab_collects_all_geometry_differences_without_claiming_verified(self):
        adapter=Path(__file__).resolve().parents[1]/'src/monkey/targets/CreatorPrefab.js'
        script=r'''
const Module=require('module'),load=Module._load;
Module._load=function(name,...args){if(name==='cc')return {instantiate:x=>x,UITransform:class {},Widget:class {}};return load.call(this,name,...args);};
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
        result=subprocess.run(['node','-e',script,str(adapter)],capture_output=True,text=True,check=True)
        self.assertEqual([v['sourceId'] for v in json.loads(result.stdout)['geometryMismatches']],['root','child'])
