import copy
import tempfile
import unittest
from pathlib import Path
from monkey.assets.animation import normalize_clip,plan_clips,sample,verify_native
from monkey.io import write_json,read,load,finish
from monkey.sources.compiled import ParseError
from monkey.targets import unity,cocos


def base():
    return dict(__type__='cc.AnimationClip',_name='Synthetic finite UI',_duration=1,sample=30,curveData=dict(paths={'child':dict(props={
        'x':[dict(frame=0,value=10),dict(frame=1,value=30)],
        'scale':[dict(frame=0,value=[1,1,1],curve='constant'),dict(frame=1,value=[2,3,1])],
        'opacity':[dict(frame=0,value=0),dict(frame=1,value=255)]})}),events=[dict(frame=.5,func='reward',params=['item',2])])


def ir_for(clip):
    def node(sid,name,parent,children):return dict(sourceId=sid,name=name,parent=parent,children=children,components=[],position=[0,0,0],scale=[1,1,1],rotation=[0,0,0,1],size=[100,100],anchor=[.5,.5],active=True,color=[255]*4,opacity=255)
    c,g=normalize_clip(clip,'source:clip','fixture.anim#instances/0')
    return dict(schemaVersion=1,sourceProfile='cocos-2.4.15-project',sourceManifestSha256='0'*64,sourceRoots={},sourceLocations={},aliases={},
        nodes=[node('root','Root',None,['child']),node('child','child','root',[])],assets=[],spriteFrames=[],bitmapFonts=[],materials=[],diagnostics=g,
        animationSchemaVersion=1,animationClips=[c],components=[dict(sourceId='root#anim',node='root',type='cc.Animation',clips=['source:clip'],enabled=True,materials=[])])


class AnimationTests(unittest.TestCase):
    def test_real_semantic_intervals_scale_step_opacity_units_and_event_contract(self):
        ir=ir_for(base());a,_=plan_clips(ir,'fixture',unity.PROFILE);b,_=plan_clips(ir,'fixture',cocos.PROFILE)
        self.assertEqual(len(a[0]['tracks']),5)
        x=next(t for t in a[0]['tracks'] if t['property']=='position.x');self.assertEqual(sample(x['keys'],.25),15)
        scale=next(t for t in a[0]['tracks'] if t['property']=='scale.x');self.assertEqual(sample(scale['keys'],.999),1);self.assertEqual(sample(scale['keys'],1),2)
        alpha=next(t for t in a[0]['tracks'] if t['property']=='opacity');self.assertEqual(alpha['keys'][-1]['value'],1)
        self.assertEqual(next(t for t in b[0]['tracks'] if t['property']=='opacity')['keys'][-1]['value'],255)
        self.assertFalse(a[0]['autoPlay']);self.assertEqual(a[0]['events'][0]['binding'],'manual-only');self.assertFalse(a[0]['events'][0]['executed'])

    def test_unknown_easing_loop_keytime_and_property_never_silently_linearized(self):
        doc=base();doc['wrapMode']=22;doc['curveData']['paths']['child']['props']['x'][0]['curve']='sineOut'
        doc['curveData']['paths']['child']['props']['active']=[dict(frame=0,value=True)]
        ir=ir_for(doc);a,g=plan_clips(ir,'fixture',unity.PROFILE)
        self.assertFalse(a[0]['convertible']);self.assertNotIn('position.x',[t['property'] for t in a[0]['tracks']])
        self.assertTrue({'ANIMATION_TIMING_UNSUPPORTED','ANIMATION_INTERPOLATION_UNSUPPORTED','ANIMATION_PROPERTY_UNSUPPORTED'}<={d['code'] for d in ir['diagnostics']})
        for times in [[0,0],[.5,.4],[0,2]]:
            doc=base();doc['curveData']['paths']['child']['props']['x']=[dict(frame=t,value=0) for t in times]
            ir=ir_for(doc);self.assertFalse(any(t['property']=='position.x' for t in ir['animationClips'][0]['tracks']))

    def test_missing_ambiguous_targets_overlapping_channels_and_layout_conflicts(self):
        from monkey.assets.animation import handoff_task
        ownerless=ir_for(base());ownerless['components']=[]
        empty,gaps=plan_clips(ownerless,'fixture',unity.PROFILE)
        self.assertEqual(empty,[]);self.assertEqual(handoff_task(empty,gaps)['sourceRefs'],['source:clip'])
        ir=ir_for(base());ir['nodes'][1]['name']='different';a,g=plan_clips(ir,'fixture',unity.PROFILE);self.assertFalse(a[0]['convertible']);self.assertTrue(g)
        ir=ir_for(base());ir['nodes'][0]['children']=['child','other'];n=dict(ir['nodes'][1],sourceId='other');ir['nodes'].append(n)
        a,g=plan_clips(ir,'fixture',unity.PROFILE);self.assertFalse(a[0]['convertible'])
        doc=base();doc['curveData']['paths']['child']['props']['position']=[dict(frame=0,value=[0,0,0]),dict(frame=1,value=[1,1,0])]
        a,g=plan_clips(ir_for(doc),'fixture',unity.PROFILE);self.assertTrue(any(d['code']=='ANIMATION_CHANNEL_COLLISION' for d in g))
        ir=ir_for(base());ir['components'].append(dict(type='cc.Layout',node='root',enabled=True))
        a,g=plan_clips(ir,'fixture',unity.PROFILE);self.assertFalse(any(t['property']=='position.x' for t in a[0]['tracks']))

    def test_native_wrong_binding_midpoint_or_callback_rejected(self):
        a,_=plan_clips(ir_for(base()),'fixture',unity.PROFILE);s=a[0]
        result=dict(id=s['id'],path=s['path'],guid='native-guid',duration=1,wrap='normal',eventCount=0,curveCount=5,tracks=[dict(path=t['path'],property=t['nativeProperty'],nativeType=t['nativeType'],times=[k['time'] for k in t['keys']],values=[k['value'] for k in t['keys']],interpolations=[k['interpolation'] for k in t['keys']],probeTimes=[p['time'] for p in t['probes']],probeValues=[p['value'] for p in t['probes']]) for t in s['tracks']])
        self.assertFalse(verify_native(a,[result],{s['path']:'hash'}))
        for change in ['event','binding','probe']:
            wrong=copy.deepcopy(result)
            if change=='event':wrong['eventCount']=1
            elif change=='binding':wrong['tracks'][0]['path']='other'
            else:wrong['tracks'][0]['probeValues'][1]+=10
            self.assertTrue(verify_native(a,[wrong],{s['path']:'hash'}))

    def test_invalid_opacity_vectors_and_future_animation_schema_rejected(self):
        for prop,value in [('opacity',256),('scale',[1,float('nan'),1]),('position',[1])]:
            doc=base();doc['curveData']['paths']['child']['props'][prop]=[dict(frame=0,value=value)]
            ir=ir_for(doc);self.assertTrue(any(d['code'].startswith('ANIMATION_') and 'EVENT' not in d['code'] for d in ir['diagnostics']))
        ir=ir_for(base());ir['animationSchemaVersion']=2
        with self.assertRaises(ParseError):plan_clips(ir,'fixture',unity.PROFILE)
        old=ir_for(base());old.pop('animationSchemaVersion');old.pop('animationClips')
        self.assertEqual(plan_clips(old,'fixture',unity.PROFILE),([],[]))

    def test_minigame_animation_is_inside_declared_native_import_root(self):
        from monkey.layout import standard
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();ir=ir_for(base())
            ir['sourceNames']={'source:clip':dict(bundle='miniGameRes',logicalPath='Anim/Rope3d/fly')}
            (root/'ir').mkdir();write_json(root/'ir/ir.json',ir);finish(root/'ir',dict(schemaVersion=1,diagnostics=[]))
            unity.plan(root/'ir/ir.json','minigame',root/'plan');unity.export(root/'plan/plan.json',root/'project')
            paths=load(read(root/'project'/standard.unity('outputPaths')))
            plan=load(read(root/'project'/standard.unity('importPlan')))
            clip=next(a for a in plan['animations'] if a['convertible'])
            self.assertIn('/MiniGames/Rope3d/',clip['path'])
            self.assertTrue(clip['path'].startswith(paths['animationsRoot']+'/'),clip['path'])

    def test_shared_ir_dual_export_no_native_files_or_callback_stubs_and_create_only(self):
        with tempfile.TemporaryDirectory() as temp:
            r=Path(temp).resolve();ir=ir_for(base());(r/'ir').mkdir();write_json(r/'ir/ir.json',ir);finish(r/'ir',dict(schemaVersion=1,diagnostics=[]))
            for target in [unity,cocos]:
                prefix='unity' if target is unity else 'creator'
                target.plan(r/'ir/ir.json','fixture',r/(prefix+'-plan'));target.export(r/(prefix+'-plan/plan.json'),r/prefix)
                if target is unity:
                    from monkey.layout import standard
                    helper=(r/prefix/standard.unity('importer')).with_name('NativeButtonAnimations.cs')
                    self.assertEqual(helper.read_bytes(),Path(unity.__file__).with_name('UnityButtonAnimations.cs').read_bytes())
                    self.assertTrue(Path(str(helper)+'.meta').is_file())
                module=load(read(r/prefix/'Analysis/Tasks/animation-module.json'));self.assertFalse(module['callbacksGenerated']);self.assertEqual(len(module['clips']),1)
                self.assertFalse(any((r/prefix).rglob('*.anim')))
                task=next(t for t in load(read(r/prefix/'Analysis/Tasks/handoff.json'))['tasks'] if t['taskId']=='finite-ui-animation');self.assertTrue(task['gaps'])
                self.assertEqual(target.verify(r/prefix,r/(prefix+'-static'))['staticValidation'],'pass')
                with self.assertRaises(ParseError):target.export(r/(prefix+'-plan/plan.json'),r/prefix)
                (r/(prefix+'-plan/plan.json')).write_text('{}')
                with self.assertRaises(ParseError):target.export(r/(prefix+'-plan/plan.json'),r/(prefix+'-tampered'))
