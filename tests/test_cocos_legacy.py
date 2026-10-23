import json,tempfile,unittest
from pathlib import Path
from PIL import Image
from monkey.sources.cocos_legacy import inspect,document
from monkey.normalize import normalize
from monkey.io import load,read
from monkey.sources.compiled import ParseError


class LegacyResourcesTests(unittest.TestCase):
    def fixture(self,root):
        source=root/'source';source.mkdir();key='12345678-1234-1234-1234-123456789abc';texture='012345678'
        settings=dict(uuids=[key,texture],packedAssets={},md5AssetsMap={'import':[key,'abcde'],'raw-assets':[texture,'12345']})
        (source/'engine.js').write_text('cc.ENGINE_VERSION="2.1.2";window._CCSettings='+json.dumps(settings)+';')
        (source/('res-import-12-'+key+'.abcde.json')).write_text(json.dumps({'__type__':'cc.SpriteFrame','content':dict(name='original',texture=texture,rect=[0,0,2,2],offset=[0,0],originalSize=[2,2],capInsets=[0,0,0,0])}))
        Image.new('RGBA',(2,2),(24,36,48,255)).save(source/('res-raw-assets-01-'+texture+'.12345.png'))
        return source

    def test_original_identity_version_and_full_pixels_feed_shared_ir(self):
        with tempfile.TemporaryDirectory()as t:
            root=Path(t).resolve();source=self.fixture(root);result=inspect(source,root/'inspect')
            self.assertFalse(result['sourceCodeExecuted']);self.assertEqual(result['missingDeclaredAssets'],[])
            ir=normalize(root/'inspect/source-manifest.json',root/'normalize')
            self.assertEqual(len(ir['spriteFrames']),1);self.assertEqual(ir['nodes'],[])
            with Image.open(root/'normalize'/ir['spriteFrames'][0]['image'])as image:self.assertEqual(image.getpixel((0,0)),(24,36,48,255))

    def test_wrong_cache_version_is_a_gap_and_never_selected(self):
        with tempfile.TemporaryDirectory()as t:
            root=Path(t).resolve();source=self.fixture(root)
            path=next(source.glob('*.png'));path.rename(path.with_name(path.name.replace('12345.png','fffff.png')))
            result=inspect(source,root/'inspect');self.assertTrue(result['missingDeclaredAssets'])
            ir=normalize(root/'inspect/source-manifest.json',root/'normalize');self.assertEqual(ir['spriteFrames'],[])
            self.assertTrue(any(d['code']=='LEGACY_CACHE_VERSION_MISMATCH'for d in result['diagnostics']))

    def test_unknown_geometry_is_not_silently_projected(self):
        with self.assertRaises(ParseError):document({'__type__':'cc.SpriteFrame','content':{'vertices':[1,2]}})


if __name__=='__main__':unittest.main()
