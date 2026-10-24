import unittest,tempfile
from pathlib import Path
from monkey.io import finish,write_json,load,read
from monkey.identities import verify

class AssignedIdentityTests(unittest.TestCase):
    def test_importer_expansion_is_allowed_but_a_rehashed_uuid_change_is_not(self):
        with tempfile.TemporaryDirectory()as temp:
            root=Path(temp).resolve();(root/'assets').mkdir();(root/'assets/raw.png').write_bytes(b'opaque-input')
            old='aaaaaaaa-1111-2222-3333-bbbbbbbbbbbb';path=root/'assets/raw.png.meta';write_json(path,dict(uuid=old,importer='image',imported=False,subMetas={}))
            manifest=finish(root,dict(targetProfile='cocos-3.8.8',diagnostics=[]));meta=load(read(path));meta.update(imported=True,subMetas={'frame':dict(uuid=old+'@frame')});write_json(path,meta)
            self.assertEqual(verify(root,manifest),[])
            meta['uuid']='cccccccc-1111-2222-3333-dddddddddddd';write_json(path,meta)
            # A native file hash receipt may legitimately change, but cannot replace the sealed ID.
            errors=verify(root,manifest);self.assertEqual([e['code']for e in errors],['ASSIGNED_NATIVE_IDENTITY_CHANGED'])

if __name__=='__main__':unittest.main()
