import copy,unittest,shutil,subprocess
from pathlib import Path
from monkey.targets.dynamic_ui import POLICY,expectations,verify_probes,probe_sources

class DynamicUiEvidenceTests(unittest.TestCase):
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
