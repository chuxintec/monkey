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

    def test_ir_and_plan_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            r=Path(temp).resolve();self.build(r)
            raw=load(read(r/'plan/plan.json'));raw['copies'][0]['target']='../../escape.png';write_json(r/'plan/plan.json',raw)
            with self.assertRaises(ParseError):cocos.export(r/'plan/plan.json',r/'bad')
            self.assertFalse((r/'bad').exists())
            (r/'ir/ir.json').write_bytes(b'{}')
            with self.assertRaises(ParseError):cocos.plan(r/'ir/ir.json','test',r/'bad2')
