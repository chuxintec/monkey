import tempfile,unittest
from pathlib import Path
from fixtures import FRAME,TEXTURE
from test_cocos38 import fixture38
from monkey.io import read,load,write_json
from monkey.package import convert_package
from monkey.sources.cocos34 import texture,image_formats
from monkey.sources.compiled import ParseError
from monkey.sources.bundle import Bundle


def fixture34(root):
    config=fixture38(root);c=load(read(config));c['engineVersion']='3.4.1';c['packs']['texpack']=['1'];write_json(config,c)
    write_json(root/'settings.test.json',dict(CocosEngine='3.4.1'))
    sf=root/'import'/FRAME[:2]/(FRAME+'@f9941.a.json');d=load(read(sf))
    for k in ('pivot','meshType','pixelsToUnit'):d[5][0].pop(k)
    write_json(sf,d)
    write_json(root/'import/te/texpack.a.json',dict(type='cc.Texture2D',data=[dict(base='2,2,0,0,0,0',mipmaps=[TEXTURE])]))
    return config


class Creator34Tests(unittest.TestCase):
    def test_public_both_targets_keep_version_specific_resources_and_do_not_guess_graphs(self):
        with tempfile.TemporaryDirectory()as temp:
            root=Path(temp).resolve();config=fixture34(root/'source');report=convert_package(config.parent,'both',root/'out')
            self.assertTrue(report['completed']);self.assertNotEqual(report['structuredRecovery']['status'],'failed',report['structuredRecovery'])
            ir=load(read(root/'out/Structured/normalize/ir.json'))
            self.assertEqual(ir['sourceProfile'],'cocos-3.4.1-bundle');self.assertEqual(len(ir['spriteFrames']),1);self.assertEqual(ir['nodes'],[])
            self.assertEqual(ir['spriteFrames'][0]['textureRef'],'main:'+TEXTURE)
            self.assertEqual(ir['spriteFrames'][0]['sourceResourceEvidence']['resourceProfile'],'cocos-3.4.1-bundle')
            self.assertTrue(any(d['code']=='COCOS34_RESOURCE_PROFILE_ONLY'for d in ir['diagnostics']))
            self.assertEqual(load(read(root/'out/Structured/inspect/source-manifest.json'))['sourceVersion'],'3.4.1')
            for target in ('UnityProject','CocosProject'):self.assertTrue((root/'out'/target/'manifest.json').is_file())

    def test_settings_proof_is_required_and_later_profile_is_not_accepted(self):
        with tempfile.TemporaryDirectory()as temp:
            root=Path(temp).resolve();config=fixture34(root/'source');declaration=root/'inputs.json'
            write_json(declaration,dict(schemaVersion=1,sourceProfile='cocos-3.4.1-bundle',inputs=[dict(id='source',path=str(config.parent))]))
            (config.parent/'settings.test.json').unlink()
            with self.assertRaisesRegex(ParseError,'COCOS3_VERSION_EVIDENCE_REQUIRED'):convert_package(None,'both',root/'missing-proof',input_set_path=declaration)
            write_json(config.parent/'settings.test.json',dict(CocosEngine='3.8.7'))
            with self.assertRaisesRegex(ParseError,'COCOS3_VERSION_EVIDENCE_REQUIRED'):convert_package(None,'both',root/'wrong-proof',input_set_path=declaration)

    def test_mipmap_and_later_positional_layouts_are_not_silently_collapsed(self):
        self.assertEqual(texture(dict(base='2,2,0,0,0,0',mipmaps=[TEXTURE]),'test')[1],TEXTURE)
        for value in [dict(base='2,2,0,0,0,0',mipmaps=[TEXTURE,FRAME]),['2,2,0,0,0,0',[TEXTURE]],dict(base='bad',mipmaps=[TEXTURE])]:
            with self.assertRaises(ParseError):texture(value,'test')

    def test_pack_envelope_identity_is_not_decoded_as_an_extra_source_object(self):
        with tempfile.TemporaryDirectory()as temp:
            config=fixture34(Path(temp).resolve()/'source');data=load(read(config));data['uuids'].append('texpack');write_json(config,data)
            row=Bundle(config,'cocos-3.4.1-bundle').asset(len(data['uuids'])-1)
            self.assertEqual(row['kind'],'source-pack-container');self.assertIsNone(row['document'])

    def test_public_input_set_joins_acquired_resources_without_copying_into_original_root(self):
        with tempfile.TemporaryDirectory()as temp:
            root=Path(temp).resolve();config=fixture34(root/'source');image=root/'source/native'/TEXTURE[:2]/(TEXTURE+'.b.png')
            moved=root/'remote/main/native'/TEXTURE[:2]/image.name;moved.parent.mkdir(parents=True);image.rename(moved)
            declaration=root/'inputs.json';write_json(declaration,dict(schemaVersion=1,sourceProfile='cocos-3.4.1-bundle',inputs=[dict(id='source',path=str(config.parent)),dict(id='remote',path=str(root/'remote'))]))
            report=convert_package(None,'both',root/'out',input_set_path=declaration)
            self.assertNotEqual(report['structuredRecovery']['status'],'failed',report['structuredRecovery'])
            ir=load(read(root/'out/Structured/normalize/ir.json'));self.assertEqual(len(ir['spriteFrames']),1);self.assertFalse(image.exists())
            objects=load(read(root/'out/UnityProject/Analysis/structured-objects.json'))['objects'];source=next(a for a in objects if a['sourceId']=='main:'+TEXTURE)
            self.assertTrue(any('remote/main/native/'in x for x in source['sourceInputs']))
            self.assertFalse(any(d['code']=='INVALID_BUNDLE_TABLE'for d in report['diagnostics']))

    def test_different_bytes_for_same_acquired_version_are_an_explicit_conflict(self):
        with tempfile.TemporaryDirectory()as temp:
            root=Path(temp).resolve();config=fixture34(root/'source');remote=root/'remote/main/native'/TEXTURE[:2]/(TEXTURE+'.b.png');remote.parent.mkdir(parents=True);remote.write_bytes(b'different bytes')
            bundle=Bundle(config,'cocos-3.4.1-bundle');bundle.provided_tree(root,[root/'source',root/'remote'])
            with self.assertRaisesRegex(ParseError,'CONFLICTING_PROVIDED_RESOURCE'):bundle.select('native',TEXTURE,'b','.png')

    def test_multiple_encodings_use_declared_policy_and_retain_both_locations(self):
        self.assertEqual(image_formats(dict(fmt='7@93_0'),'test'),['.astc','.png'])
        with tempfile.TemporaryDirectory()as temp:
            root=Path(temp).resolve();config=fixture34(root/'source');astc=root/'source/native'/TEXTURE[:2]/(TEXTURE+'.b.astc');astc.write_bytes(b'path selection only; decoder validates bytes later')
            bundle=Bundle(config,'cocos-3.4.1-bundle');entry=dict(sourceId='main:'+TEXTURE,key=TEXTURE,kind='cc.ImageAsset',document=dict(root=0,instances=[dict(data=dict(fmt='7@93_0'))]))
            selected=bundle.native_file(entry,'b');self.assertEqual(selected.suffix,'.astc');self.assertEqual(len(entry['nativeVariantSelection']['available']),2)
