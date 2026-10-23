import unittest
from monkey.sources.unity_worker import portable, identifier, texture_payload


class UnityIdentityTests(unittest.TestCase):
    def test_negative_path_id_survives_json_and_distinguishes_files(self):
        import json
        path_id = -9223372036854775807
        refs=[]
        data=portable({'first':{'m_FileID':0,'m_PathID':path_id},
                       'other':{'m_FileID':2,'m_PathID':path_id},
                       'unsignedData':18446744073709551615},refs)
        # A JavaScript consumer receives no unsafe number, including ordinary large values.
        restored=json.loads(json.dumps(data))
        self.assertEqual(restored['first']['pathId'],str(path_id))
        self.assertEqual(restored['first']['fileId'],'0')
        self.assertEqual(restored['other']['fileId'],'2')
        self.assertEqual(restored['unsignedData']['decimal'],'18446744073709551615')
        self.assertEqual([r['location'] for r in refs],['$/first','$/other'])
        for bad in [1<<63,-(1<<63)-1,True,1.0,'1']:
            with self.assertRaises(ValueError):identifier(bad)

    def test_binary_text_and_nonfinite_are_losslessly_explicit(self):
        import base64,json
        raw=b'\xff\xfe\x00a';data=portable({'text':raw.decode('utf-8',errors='surrogateescape'),'unknown':float('inf')},[])
        json.dumps(data,ensure_ascii=False,allow_nan=False).encode('utf-8')
        self.assertEqual(base64.b64decode(data['text']['base64']),raw)
        self.assertEqual(data['unknown'],{'$type':'nonfinite','value':'inf'})

    def test_external_texture_key_is_reported_as_unresolved_not_pixels(self):
        key=b'Atlas%20Page.0123abcd'
        row=texture_payload({'image data':bytes([len(key)])+key})
        self.assertEqual(row['kind'],'external-key-token-candidate')
        self.assertEqual(row['resourceResolution'],'required')
        self.assertFalse(row['nativePixelsVerified'])
        self.assertEqual(texture_payload({'image data':b'wrong'+key})['kind'],'inline-payload')

    def test_partial_pptr_is_preserved_as_data_instead_of_guessed_reference(self):
        refs=[];data=portable({'m_FileID':2,'m_PathID':7,'differentSchema':True},refs)
        self.assertEqual(data['differentSchema'],True);self.assertEqual(refs,[])
        with self.assertRaises(ValueError):portable([[[None]]],[],depth=96)


if __name__=='__main__':unittest.main()
