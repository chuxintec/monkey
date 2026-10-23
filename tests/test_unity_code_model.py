import json,tempfile,unittest
from pathlib import Path
from monkey.io import write_json,sha,read
from monkey.unity_code_model import model,field_type,identifier
from monkey.sources.compiled import ParseError


class UnityCodeSchemaTests(unittest.TestCase):
    def test_original_sprite_pointer_vector_and_uint64_have_explicit_types(self):
        n={'type':'vector','name':'Idle','children':[{'type':'Array','name':'Array','children':[{'type':'int','name':'size'},{'type':'PPtr<$Sprite>','name':'data'}]}]}
        self.assertEqual(field_type(n),'UnityEngine.Sprite[]')
        self.assertEqual(field_type({'type':'UInt64','name':'assetQuantity'}),'ulong')
        self.assertEqual(identifier('class'),'@class')
        with self.assertRaises(ParseError):field_type({'type':'PPtr<$UnknownClass>','name':'Unknown'})
        with self.assertRaises(ParseError):identifier('Name; execute()')

    def test_schema_producer_generates_named_nonempty_fields_and_retains_missing_logic(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t).resolve();source=root/'inspection';source.mkdir()
            schema={'children':[{'name':'m_Script','type':'PPtr<MonoScript>'},{'name':'Volume','type':'float'}]}
            obj={'file':'0','pathId':'-9223372036854775807','type':'MonoBehaviour','status':'parsed','embeddedSchemaId':'shape','rawSha256':'a'*64,'references':[], 'data':{'m_Script':{'fileId':'0','pathId':'2'}}}
            script={'file':'0','pathId':'2','type':'MonoScript','status':'parsed','data':{'m_ClassName':'AudioSettings','m_Namespace':'Game','m_AssemblyName':'GameBase.dll'}}
            data={'source':{'sha256':'b'*64},'objects':[obj,script],'embeddedSchemas':{'shape':schema}}
            write_json(source/'typed-objects.json',data);write_json(source/'inspection.json',{'typedObjectsSha256':sha(read(source/'typed-objects.json'))})
            result=model(source,root/'out');self.assertEqual(result['summary']['fields'],1)
            code=(root/'out/CSharp/GameBase/Game/AudioSettings.cs').read_text();self.assertIn('public float @Volume;',code)
            self.assertNotIn('Invoke',code);self.assertEqual(result['summary']['methodsImplemented'],0)
            (source/'typed-objects.json').write_text('{}')
            with self.assertRaises(ParseError):model(source,root/'changed')
            self.assertFalse((root/'changed').exists())


if __name__=='__main__':unittest.main()
