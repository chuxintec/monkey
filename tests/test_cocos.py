import tempfile
import unittest
from pathlib import Path
from fixtures import fixture
from monkey.sources.bundle import inspect
from monkey.normalize import normalize
from monkey.targets import cocos
from monkey.io import read, load, sha, write_json
from monkey.sources.compiled import ParseError


class CreatorTests(unittest.TestCase):
    def build(self,root):
        config=fixture(root/'source');inspect(config,[2],root/'inspect');normalize(root/'inspect/source-manifest.json',root/'ir')
        return cocos.plan(root/'ir/ir.json','synthetic',root/'plan')

    def test_deterministic_asset_identity_closed_logical_refs_and_native_pending(self):
        with tempfile.TemporaryDirectory() as temp:
            r=Path(temp).resolve();p=self.build(r)
            cocos.export(r/'plan/plan.json',r/'first');cocos.export(r/'plan/plan.json',r/'second')
            self.assertEqual(read(r/'first/manifest.json'),read(r/'second/manifest.json'))
            self.assertEqual(cocos.verify(r/'first',r/'static')['staticValidation'],'pass')
            self.assertEqual(cocos.verify(r/'first',r/'editor','editor')['editorValidation'],'not_run')
            image=next(a for a in p['assets'] if not a['sourceId'].endswith('@original'))
            m=load(read(r/'first'/ (image['path']+'.meta')))
            self.assertEqual(m['uuid'],image['uuid']);self.assertEqual(m['subMetas'],{})
            self.assertEqual(image['size'],[3,2]);self.assertEqual(image['originalSize'],[7,6])
            self.assertEqual(image['trimOrigin'],[3,3])
            original=read(r/'first'/image['path']);(r/'first'/image['path']).write_bytes(original+b'edit')
            self.assertEqual(cocos.verify(r/'first',r/'tampered')['staticValidation'],'conflict')
            with self.assertRaises(ParseError):cocos.export(r/'plan/plan.json',r/'first')

    def test_bitmap_top_origin_signed_kerning_and_native_readback_rejection(self):
        font=dict(pointSize=10,lineHeight=12,atlasSize=[8,8],glyphs=[dict(unicode=65,sourceRect=[2,1,3,4],metrics=[3,4,-1,8,5])],
                  kernings=[dict(first=65,second=65,advance=-2)])
        text=cocos.bitmap_text(font,'atlas.png').decode()
        self.assertIn('x=2 y=1 width=3 height=4 xoffset=-1 yoffset=2',text)
        self.assertIn('amount=-2',text)
        with tempfile.TemporaryDirectory() as temp:
            r=Path(temp).resolve();self.build(r);cocos.export(r/'plan/plan.json',r/'candidate')
            write_json(r/'candidate/Analysis/editor-readback.json',dict(creatorVersion='3.8.8',projectUuid='wrong',assets=[],nodeCount=1))
            self.assertEqual(cocos.verify(r/'candidate',r/'verify','editor')['editorValidation'],'fail')

    def test_independent_prefab_plan_preserves_source_name_and_is_not_native_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            r=Path(temp).resolve();p=self.build(r)
            self.assertEqual(len(p['sourcePrefabs']),1)
            spec=p['sourcePrefabs'][0]
            self.assertEqual(spec['nodeCount'],1)
            self.assertEqual(spec['rootNamePolicy'],'creator-asset-basename-v1')
            self.assertEqual(spec['nativeRootName'],Path(spec['path']).stem)
            self.assertEqual(spec['sourceRootName'],next(n['name'] for n in p['nodes'] if n['sourceId']==spec['root']))
            self.assertTrue(spec['path'].endswith('/UI/fixture.prefab'),spec['path'])
            cocos.export(r/'plan/plan.json',r/'candidate')
            instruction=load(read(r/'candidate/extensions/monkey-import/import-plan.json'))
            self.assertEqual(instruction['sourcePrefabs'],p['sourcePrefabs'])
            self.assertFalse((r/'candidate'/spec['path']).exists())
            from monkey.formatting import preview,apply
            preview(r/'candidate',r/'format-preview');apply(r/'candidate',r/'format-preview/format-plan.json',r/'formatted')
            instruction=load(read(r/'formatted/extensions/monkey-import/import-plan.json'))
            self.assertTrue(instruction['sourcePrefabs'][0]['path'].startswith('assets/content/prefabs/'))
            self.assertEqual(cocos.verify(r/'formatted',r/'verify','editor')['editorValidation'],'not_run')

    def test_bitmap_font_page_is_adjacent_and_owned_after_standard_layout(self):
        import re
        from fixtures import FONT,FRAME,normal
        from monkey.formatting import preview,apply
        with tempfile.TemporaryDirectory() as temp:
            r=Path(temp).resolve();config=fixture(r/'source')
            font=dict(name='OriginalFont',fontSize=20,spriteFrame={'__uuid__':FRAME},_fntConfig=dict(fontSize=20,commonHeight=20,
                fontDefDictionary={'65':dict(rect=dict(x=0,y=0,width=2,height=1),xOffset=0,yOffset=0,xAdvance=2)},kerningDict={}))
            write_json(r/('source/import/00/'+FONT+'.a.json'),normal([dict(__type__='cc.BitmapFont',**font)]))
            inspect(config,[2],r/'inspect');normalize(r/'inspect/source-manifest.json',r/'ir')
            plan=cocos.plan(r/'ir/ir.json','bitmap-adjacency',r/'plan')
            self.assertEqual(len([a for a in plan['assets'] if a['kind']=='bitmap']),1)
            cocos.export(r/'plan/plan.json',r/'candidate');preview(r/'candidate',r/'format-preview');apply(r/'candidate',r/'format-preview/format-plan.json',r/'formatted')
            native=load(read(r/'formatted/extensions/monkey-import/import-plan.json'));font=next(a for a in native['assets'] if a['kind']=='bitmap')
            atlas=next(a for a in native['assets'] if a['sourceId']==font['atlas'])
            fnt=r/'formatted'/font['path'];page=re.search(r'page id=0 file="([^"]+)"',fnt.read_text())[1]
            self.assertEqual(fnt.parent,(r/'formatted'/atlas['path']).parent)
            self.assertEqual(page,Path(page).name)
            self.assertTrue((fnt.parent/page).is_file())
            self.assertEqual(sha((fnt.parent/page).read_bytes()),atlas['sha256'])
            self.assertEqual(cocos.verify(r/'candidate',r/'checked')['staticValidation'],'pass')
            from monkey.targets import unity
            u=unity.plan(r/'ir/ir.json','bitmap-adjacency',r/'unity-plan')
            unity.export(r/'unity-plan/plan.json',r/'unity')
            spec=u['bitmapFonts'][0]
            write_json(r/'unity/Analysis/editor-readback.json',dict(status='imported',unityVersion='6000.6.2f1',missingScripts=0,
                diagnostics=[],nativeFiles=[],nodes=[],sprites=[],labels=[],fonts=[dict(id=spec['id'],guid='font',
                    glyphCount=len(spec['glyphs']),pointSize=spec['pointSize'],lineHeight=spec['lineHeight'],atlasGuid='',materialAtlasGuid='')]))
            checked=unity.verify(r/'unity',r/'unity-checked','editor')
            self.assertTrue(any(d['code']=='BITMAP_ATLAS_READBACK_MISMATCH' for d in checked['diagnostics']))

    def test_cached_sprite_rect_keeps_original_mode_and_explicit_resize_handoff(self):
        from monkey.io import finish
        for size,needs_handoff in [([7,6],False),([100,144],True)]:
            with self.subTest(size=size),tempfile.TemporaryDirectory() as temp:
                root=Path(temp).resolve();self.build(root)
                ir=load(read(root/'ir/ir.json'));sprite=next(c for c in ir['components'] if c['type']=='cc.Sprite')
                sprite['sizeMode']=2;node=next(n for n in ir['nodes'] if n['sourceId']==sprite['node']);node['size']=size
                write_json(root/'ir/ir.json',ir);finish(root/'ir',ir)
                plan=cocos.plan(root/'ir/ir.json','cached-size',root/'cached-plan')
                actual=next(c for c in plan['components'] if c['sourceId']==sprite['sourceId'])
                self.assertEqual(actual['sizeMode'],2)
                self.assertEqual(actual.get('nativeSizeMode')==0,needs_handoff)
                self.assertEqual(any(d['code']=='SPRITE_CACHED_SIZE_HANDOFF' for d in plan['diagnostics']),needs_handoff)

    def test_native_scene_identity_without_geometry_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();plan=self.build(root);cocos.export(root/'plan/plan.json',root/'candidate')
            write_json(root/'candidate/Analysis/editor-readback.json',dict(creatorVersion='3.8.8',projectUuid='wrong',
                nodeCount=len(plan['nodes']),nodes=[dict(sourceId=n['sourceId'],nodeUuid='id') for n in plan['nodes']],assets=[],nativeFiles=[]))
            result=cocos.verify(root/'candidate',root/'checked','editor')
            self.assertIn('SCENE_GEOMETRY_MISMATCH',{d['code'] for d in result['diagnostics']})

    def test_ir_and_plan_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            r=Path(temp).resolve();self.build(r)
            raw=load(read(r/'plan/plan.json'));raw['copies'][0]['target']='../../escape.png';write_json(r/'plan/plan.json',raw)
            with self.assertRaises(ParseError):cocos.export(r/'plan/plan.json',r/'bad')
            self.assertFalse((r/'bad').exists())
            (r/'ir/ir.json').write_bytes(b'{}')
            with self.assertRaises(ParseError):cocos.plan(r/'ir/ir.json','test',r/'bad2')
