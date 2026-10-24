import copy,tempfile,unittest
from pathlib import Path
from fixtures import fixture
from monkey.sources.bundle import inspect
from monkey.normalize import normalize
from monkey.targets import cocos
from monkey.io import read,load,write_json,sha,finish
from monkey.formatting import preview,apply
from monkey.sources.compiled import ParseError

class FormattingTests(unittest.TestCase):
    def candidate(self,root):
        config=fixture(root/'source');inspect(config,[2],root/'inspect');normalize(root/'inspect/source-manifest.json',root/'ir')
        cocos.plan(root/'ir/ir.json','format-fixture',root/'plan');cocos.export(root/'plan/plan.json',root/'candidate')
        return root/'candidate'

    def test_paths_change_but_assets_identity_source_text_and_dynamic_keys_do_not(self):
        with tempfile.TemporaryDirectory()as temp:
            root=Path(temp).resolve();candidate=self.candidate(root);manifest=load(read(candidate/'manifest.json'));path=candidate/'extensions/monkey-import/import-plan.json';data=load(read(path));old=data['assets'][0]['path']
            data['nodes'][0].update(name=old,text='text '+old,logicalKey=old)
            original_nodes=copy.deepcopy(data['nodes']);write_json(path,data);finish(candidate,manifest)
            source=sha(read(candidate/'manifest.json'));preview(candidate,root/'preview');p=load(read(root/'preview/format-plan.json'))
            self.assertGreater(len(p['physicalMoves']),0);self.assertFalse(p['sourceNamesAndLogicalKeysRewritten'])
            apply(candidate,root/'preview/format-plan.json',root/'formatted');new=load(read(root/'formatted/extensions/monkey-import/import-plan.json'))
            self.assertEqual(new['nodes'],original_nodes);self.assertNotEqual(new['assets'][0]['path'],old)
            for before,after in zip(data['assets'],new['assets']):
                self.assertEqual(before['uuid'],after['uuid']);self.assertEqual(read(candidate/before['path']),read(root/'formatted'/after['path']));self.assertEqual(read(candidate/(before['path']+'.meta')),read(root/'formatted'/(after['path']+'.meta')))
            self.assertEqual(sha(read(candidate/'manifest.json')),source)
            self.assertEqual(cocos.verify(root/'formatted',root/'verify')['staticValidation'],'pass')

    def test_formal_json_bytes_and_load_strings_survive_typed_folder_changes(self):
        with tempfile.TemporaryDirectory()as temp:
            root=Path(temp).resolve();candidate=self.candidate(root);manifest=load(read(candidate/'manifest.json'));instruction=candidate/'extensions/monkey-import/import-plan.json';data=load(read(instruction))
            old='assets/generated/art/Runtime/Numbers.json';raw=b'{"price":1.2500,"load":"assets/generated/art/Runtime/item","zero":-0.0}\n';path=candidate/old;path.parent.mkdir(parents=True);path.write_bytes(raw)
            uid=cocos.identity('format-fixture','numbers');write_json(candidate/(old+'.meta'),cocos.meta(uid,'json','2.0.1'))
            data['assets'].append(dict(sourceId='fixture:numbers',kind='json',path=old,uuid=uid,sha256=sha(raw)));write_json(instruction,data);finish(candidate,manifest)
            preview(candidate,root/'preview');apply(candidate,root/'preview/format-plan.json',root/'formatted')
            target=root/'formatted/assets/content/config/recovered/Runtime/Numbers.json'
            self.assertEqual(read(target),raw);self.assertEqual(read(root/'formatted/assets/content/config/recovered/Runtime/Numbers.json.meta'),read(candidate/(old+'.meta')))

    def test_modified_owned_assets_and_stale_plans_cannot_be_applied(self):
        with tempfile.TemporaryDirectory()as temp:
            root=Path(temp).resolve();candidate=self.candidate(root);preview(candidate,root/'preview');p=load(read(root/'preview/format-plan.json'));p['physicalMoves'][0]['new']='assets/content/evil.png';write_json(root/'preview/format-plan.json',p)
            with self.assertRaises(ParseError)as e:apply(candidate,root/'preview/format-plan.json',root/'forged')
            self.assertEqual(e.exception.code,'FORMAT_STALE_PLAN');self.assertFalse((root/'forged').exists())
            image=next(f['path']for f in load(read(candidate/'manifest.json'))['files']if f['path'].endswith('.png'));(candidate/image).write_bytes(b'human edit')
            with self.assertRaises(ParseError)as e:preview(candidate,root/'drift')
            self.assertEqual(e.exception.code,'FORMAT_OWNERSHIP_DRIFT');self.assertFalse((root/'drift').exists())

    def test_imported_candidates_need_native_moves_and_unknown_owners_are_not_moved(self):
        with tempfile.TemporaryDirectory()as temp:
            root=Path(temp).resolve();candidate=self.candidate(root);(candidate/'Library').mkdir()
            with self.assertRaises(ParseError)as e:preview(candidate,root/'native')
            self.assertEqual(e.exception.code,'FORMAT_NATIVE_REQUIRED');(candidate/'Library').rmdir()
            manifest=load(read(candidate/'manifest.json'));row=next(f for f in manifest['files']if f['path'].endswith('.png'));row['owner']='manual';write_json(candidate/'manifest.json',manifest)
            with self.assertRaises(ParseError)as e:preview(candidate,root/'manual')
            self.assertEqual(e.exception.code,'FORMAT_HUMAN_OWNERSHIP')

if __name__=='__main__':unittest.main()
