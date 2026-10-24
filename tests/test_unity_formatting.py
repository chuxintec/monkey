import tempfile,unittest
from pathlib import Path
from fixtures import fixture
from monkey.sources.bundle import inspect
from monkey.normalize import normalize
from monkey.targets import unity
from monkey.io import read,load,write_json,finish,sha
from monkey.formatting import preview,apply
from monkey.sources.compiled import ParseError
from monkey.code_validation import numeric

class UnityFormattingTests(unittest.TestCase):
    def candidate(self,root):
        config=fixture(root/'source');inspect(config,[2],root/'inspect');normalize(root/'inspect/source-manifest.json',root/'ir')
        unity.plan(root/'ir/ir.json','format-fixture',root/'plan');unity.export(root/'plan/plan.json',root/'candidate');return root/'candidate'

    def test_typed_paths_preserve_meta_guid_json_names_and_editor_source_bytes(self):
        with tempfile.TemporaryDirectory()as temp:
            root=Path(temp).resolve();candidate=self.candidate(root);manifest=load(read(candidate/'manifest.json'));instruction=candidate/'Assets/Monkey/Editor/import-plan.json';data=load(read(instruction));old=data['textures'][0]['path'];data['nodes'][0]['name']=old;write_json(instruction,data);finish(candidate,manifest)
            before=sha(read(candidate/'manifest.json'));preview(candidate,root/'preview');apply(candidate,root/'preview/format-plan.json',root/'formatted')
            new=load(read(root/'formatted/Assets/Game/Editor/Conversion/import-plan.json'));self.assertEqual(data['nodes'],new['nodes']);self.assertNotEqual(new['textures'][0]['path'],old)
            self.assertEqual(read(candidate/old),read(root/'formatted'/new['textures'][0]['path']));self.assertEqual(read(candidate/(old+'.meta')),read(root/'formatted'/(new['textures'][0]['path']+'.meta')))
            self.assertEqual(read(candidate/'Assets/Monkey/Editor/MonkeyImporter.cs'),read(root/'formatted/Assets/Game/Editor/Conversion/MonkeyImporter.cs'))
            self.assertEqual(sha(read(candidate/'manifest.json')),before);self.assertEqual(unity.verify(root/'formatted',root/'verified')['staticValidation'],'pass')
            paths=load(read(root/'formatted/Analysis/output-paths.json'));self.assertEqual(paths['materialsRoot'],'Assets/Game/Content/Materials')
            (candidate/(old+'.meta')).write_text('human GUID edit')
            with self.assertRaises(ParseError)as e:apply(candidate,root/'preview/format-plan.json',root/'drift')
            self.assertEqual(e.exception.code,'FORMAT_OWNERSHIP_DRIFT');self.assertFalse((root/'drift').exists())

    def test_numeric_counts_without_native_script_and_lossless_ids_are_rejected(self):
        spec=dict(sourceId='component:one',sourceScriptIdentity='rf:one',codeClassName='Meter',codeScriptGuid='a'*32,convertible=True)
        self.assertTrue(numeric([spec],[dict(sourceId='component:one',uninitialized=True)],'unity','scene'))
        row=dict(sourceId='component:one',sourceScriptIdentity='rf:one',scriptGuid='a'*32,componentFileId='9007199254740993',labelFileId='9007199254740995',fileIdOwner='persistent-asset',bound=True,uninitialized=True)
        self.assertFalse(numeric([spec],[row],'unity','scene'));row['componentFileId']=9007199254740993
        self.assertTrue(numeric([spec],[row],'unity','scene'))

if __name__=='__main__':unittest.main()
