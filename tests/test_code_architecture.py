import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from monkey import code_architecture as architecture
from monkey.io import encoded,sha
from monkey.sources.compiled import ParseError


class ArchitectureStageTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir='/private/tmp');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'Source';self.root.mkdir()
        self.raw='// own λ\nfunction Add(v){return v+1;}\n// retained tail\n'.encode()
        a=self.raw.index(b'function');b=self.raw.index(b'}')+1;self.span=(a,b)
        source='SourceRecovery/Code/Source/own.js'
        item=dict(entryType='module_candidate',name='Add',sourceId='own:Add',sourceSnapshotPath='own.js',
            source_bytes=dict(start=a,end=b),sha256=sha(self.raw[a:b]),layer='Gameplay',codeModule='Math',
            syntax=dict(members=dict(methods=[dict(name='Add',parameters=['v'],sourceBytes=dict(start=a,end=b),sourceSha256=sha(self.raw[a:b]))])))
        files={source:self.raw,'Analysis/Code/package-csharp-drafts.json':encoded(dict(sources=[dict(source=dict(sha256=sha(self.raw),bytes=len(self.raw)),sourceMembers=[source])])),
            'Analysis/Code/code-index.json':encoded(dict(modules=[item])),
            'Assets/Game/Content/Config/Math/Values.json':encoded(dict(rows=[dict(id=1,reward=7)]))}
        rows=[]
        for path,raw in files.items():
            p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
            rows.append(dict(path=path,sha256=sha(raw),bytes=len(raw),owner='generated'))
        self.manifest=encoded(dict(schemaVersion=1,targetProfile='unity-6000.6.2f1-ugui',namespace='own-source',files=rows))
        (self.root/'manifest.json').write_bytes(self.manifest);self.pin=sha(self.manifest)

    def test_catalog_preserves_every_source_byte_and_exact_registered_members(self):
        catalog,contexts=architecture.build_catalog(self.root,self.pin)
        units=catalog['sourceUnits'];self.assertEqual(len(units),3)
        intervals=sorted((u['sourceBytes']['start'],u['sourceBytes']['end'])for u in units)
        self.assertEqual(intervals[0][0],0);self.assertEqual(intervals[-1][1],len(self.raw))
        self.assertTrue(all(a[1]==b[0]for a,b in zip(intervals,intervals[1:])))
        module=next(u for u in units if u['kind']=='registered-source-module')
        self.assertEqual(module['members'][0]['sourceSha256'],sha(self.raw[slice(*self.span)]))
        self.assertEqual(contexts['Sources/'+sha(self.raw)[:12]+'.js'],self.raw)
        self.assertFalse(catalog['sourceExecuted']);self.assertEqual(len(catalog['configurations']),1)

    def test_prepare_uses_new_architecture_seed_and_leaves_source_unchanged(self):
        observed={}
        def prepare(seed,paths,pin,out,task,**kw):
            observed.update(seed=seed,paths=paths,kw=kw,task=task)
            return type('Prepared',(),dict(output=out))()
        output=Path(self.tmp.name)/'Architecture01'
        with patch.object(architecture.worker,'prepare',side_effect=prepare):
            result=architecture.prepare(self.root,self.pin,output,namespace='OwnGame')
        self.assertEqual(result['status'],'prepared');self.assertTrue(observed['kw']['architecture_stage'])
        self.assertEqual(observed['paths'],[architecture.PLAN_PATH]);self.assertIn('ALL source units',observed['task'])
        self.assertIn('architecture-contract.json',observed['kw']['context_files'])
        self.assertEqual((self.root/'manifest.json').read_bytes(),self.manifest)
        self.assertEqual((self.root/'SourceRecovery/Code/Source/own.js').read_bytes(),self.raw)
        self.assertNotIn('SourceRecovery/CSharp',str(observed['seed']))

    def test_changed_owned_input_is_rejected_instead_of_silently_reparsed(self):
        (self.root/'SourceRecovery/Code/Source/own.js').write_bytes(self.raw+b'// changed')
        with self.assertRaises(ParseError)as error:architecture.build_catalog(self.root,self.pin)
        self.assertEqual(error.exception.code,'CODE_ARCHITECTURE_SOURCE')

    def test_member_shards_retain_ids_and_reject_changed_immutable_evidence(self):
        output=Path(self.tmp.name)/'Architecture01'
        with patch.object(architecture.worker,'prepare',side_effect=lambda s,p,h,o,t,**k:type('Prepared',(),dict(output=o))()):
            architecture.prepare(self.root,self.pin,output)
        request=json.loads((output/'request.json').read_bytes());catalog=architecture._catalog_for_validation(output,request)
        unit=next(u for u in catalog['sourceUnits']if u['kind']=='registered-source-module')
        self.assertEqual(len(unit['members']),1);self.assertEqual(unit['memberCount'],1)
        part=output/'Evidence'/catalog['memberShards'][0]['path'];part.write_bytes(part.read_bytes()+b' ')
        with self.assertRaises(ParseError)as error:architecture._catalog_for_validation(output,request)
        self.assertEqual(error.exception.code,'CODE_ARCHITECTURE_SOURCE')
