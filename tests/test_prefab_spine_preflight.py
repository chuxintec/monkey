import tempfile
import unittest
from pathlib import Path
from io import BytesIO
from PIL import Image
from monkey.assets.spine import binary_version,atlas_pages,recover_closures
from monkey.targets.prefabs import plan_prefabs
from monkey.preflight import classify_log,validate_progress
from monkey.io import sha
from monkey.sources.compiled import ParseError


class BoundaryTests(unittest.TestCase):
    def test_prefab_roots_and_cross_graph_node_reference(self):
        nodes=[dict(sourceId='a#1',parent=None),dict(sourceId='a#2',parent='a#1'),
               dict(sourceId='b#1',parent=None),dict(sourceId='scene#1',parent=None,sourceType='cc.Scene')]
        plans,gaps=plan_prefabs(dict(nodes=nodes),[])
        self.assertEqual([p['sourceId'] for p in plans],['a','b']);self.assertEqual(plans[0]['nodeCount'],2)
        plans,gaps=plan_prefabs(dict(nodes=nodes),[dict(sourceId='a#3',node='a#2',target='b#1')])
        self.assertEqual([p['sourceId'] for p in plans],['b']);self.assertEqual(gaps[0]['code'],'PREFAB_EXTERNAL_NODE_REFERENCE')
        nodes.append(dict(sourceId='b#4',parent=None));plans,gaps=plan_prefabs(dict(nodes=nodes),[])
        self.assertEqual(gaps[0]['code'],'PREFAB_ROOT_BOUNDARY')

    def test_spine_explicit_page_closure_and_missing_texture(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();source=root/'source';source.mkdir()
            binary=b'\x02h\x073.8.99'+b'original-skeleton-body';(source/'s.bin').write_bytes(binary)
            png=BytesIO();Image.new('RGBA',(2,2),(4,7,8,255)).save(png,format='PNG');(source/'t.png').write_bytes(png.getvalue())
            atlas='\npage.png\nsize: 2,2\nformat: RGBA8888\nregion\n  rotate: false\n'
            self.assertEqual(binary_version(binary),'3.8.99');self.assertIsNone(binary_version(b'bad'))
            with self.assertRaises(ParseError):atlas_pages('../page.png\nsize: 2,2')
            skeleton=dict(sourceId='main:s',bundle='main',kind='sp.SkeletonData',native='s.bin',document=dict(instances=[
                dict(__type__='sp.SkeletonData',_atlasText=atlas,textureNames=['page.png'],textures=[{'__uuid__':'t'}])]))
            texture=dict(sourceId='main:t',bundle='main',kind='cc.Texture2D',native='t.png')
            manifest=dict(bundle='main',sourceRoots={'main':str(source)},assets=[skeleton,texture],inputs=[
                dict(bundle='main',path=p.name,sha256=sha(p.read_bytes())) for p in source.iterdir()])
            result=recover_closures(manifest,root/'out');self.assertEqual(result['closed'],1)
            row=result['skeletons'][0];self.assertEqual(row['runtime'],'not_installed')
            files={Path(f['path']).name:root/'out'/f['path'] for f in row['files']}
            self.assertEqual(next(p for n,p in files.items() if n.endswith('.bin')).read_bytes(),binary);self.assertEqual(next(p for n,p in files.items() if n.endswith('.atlas')).read_text(),atlas)
            inline={'skeleton':{'spine':'3.8-from-4.2.43'},'bones':[{'name':'root'}],'slots':[],'skins':{},'animations':{}}
            skeleton['native']=None;skeleton['document']['instances'][0]['_skeletonJson']=inline
            result=recover_closures(manifest,root/'inline')
            self.assertEqual(result['closed'],1);row=result['skeletons'][0]
            self.assertEqual(row['skeletonVersion'],'3.8-from-4.2.43')
            self.assertEqual(row['runtimeCompatibility'],'not_validated');self.assertIsNone(row['sourceNativeSha256'])
            path=next(f['path'] for f in row['files'] if f['path'].endswith('.json'))
            import json
            self.assertEqual(json.loads((root/'inline'/path).read_text()),inline)
            from monkey.io import finish
            from unittest.mock import patch
            finish(root/'inline',dict(schemaVersion=1,diagnostics=[]))
            with patch('monkey.assets.spine.open_texture',side_effect=AssertionError('pixel decode repeated')):
                reused=recover_closures(manifest,root/'reused',previous=(root/'inline',sha((root/'inline/manifest.json').read_bytes())))
            self.assertEqual(reused['closed'],1,reused);self.assertEqual(reused['decodedPages'],0);self.assertEqual(reused['reusedPages'],1)
            manifest['assets']=[skeleton];result=recover_closures(manifest,root/'missing')
            self.assertEqual(result['unresolved'],1);self.assertEqual(result['skeletons'][0]['reason'],'SPINE_TEXTURE_MISSING')

    def test_startup_access_warning_does_not_claim_license_failure(self):
        result=classify_log('attempt to write a readonly database\nConnection invalid\nAccess token is unavailable\nSuccessfully resolved entitlement details')
        self.assertEqual(result['findings'][0]['code'],'HOST_CACHE_OR_IPC_ACCESS_SUSPECTED')
        self.assertEqual(result['findings'][0]['confidence'],'inference');self.assertFalse(result['engineInitialized'])
        self.assertNotIn('LICENSE_ENTITLEMENT_NOT_CONFIRMED',[r['code'] for r in result['findings']])
        good=classify_log('Initialize engine version: 6000.6.2f1\nSuccessfully resolved entitlement details')
        self.assertEqual(good['findings'],[])
        error=classify_log('TMP_ESSENTIAL_IMPORT_INCOMPLETE: required files absent')
        self.assertEqual(error['findings'][0]['code'],'TMP_ESSENTIAL_IMPORT_INCOMPLETE')

    def test_progress_is_bound_to_exact_plan_and_never_authorizes_resume(self):
        progress=dict(schemaVersion=1,phase='textures',status='budget_exhausted',planSha256='a'*64,
                      processed=128,total=5179,elapsedSeconds=5.2,nativeResumeSupported=False)
        self.assertEqual(validate_progress(progress,'a'*64)['status'],'budget_exhausted')
        for change in [dict(planSha256='b'*64),dict(processed=5180),dict(elapsedSeconds=float('inf')),
                       dict(schemaVersion=True),dict(nativeResumeSupported=True),dict(phase='unknown')]:
            with self.assertRaises(ValueError):validate_progress(dict(progress,**change),'a'*64)
        observed=classify_log("Initialize engine version: 6000.6.2f1\nImported 'GUID: a'\n")
        self.assertEqual(observed['findings'][0]['code'],'NATIVE_IMPORT_COMPLETION_NOT_RECORDED')
        self.assertFalse(observed['converterCompletionRecorded'])


if __name__=='__main__':unittest.main()
