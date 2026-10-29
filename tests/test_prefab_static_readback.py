import copy
import unittest
from monkey.prefab_static_readback import verify

class StaticReadbackTests(unittest.TestCase):
    def fixture(self):
        f=dict(fieldName='caption',sourceFieldName='caption',kind='string',storageType='string',stringValue='original')
        spec=dict(typeName='Generated.Panel',scriptGuid='script',fields=[f])
        components=[dict(sourceId='bundle:panel#2',staticFieldBinding=spec)]
        b=dict(sourceId='bundle:panel#2',typeName='Generated.Panel',nativeScriptGuid='script',nativeSourceId='bundle:panel#2',nativeIdentityVerified=True,enabled=False,fieldsVerified=True,fields=[dict(f)])
        return components,[dict(binding=b,assetGuid='asset',localFileId=9,references=[])]
    def test_checks_actual_fields_identity_and_disabled_policy(self):
        c,rows=self.fixture()
        self.assertEqual(verify(c,rows,'asset','unity','owner'),[])
        for key,value in [('enabled',True),('nativeIdentityVerified',False),('nativeSourceId','wrong'),('nativeScriptGuid','wrong')]:
            bad=copy.deepcopy(rows);bad[0]['binding'][key]=value
            self.assertTrue(verify(c,bad,'asset','unity','owner'))
        rows[0]['binding']['fields'][0]['stringValue']='changed'
        self.assertTrue(verify(c,rows,'asset','unity','owner'))
    def test_absent_or_duplicate_readback_never_passes(self):
        c,rows=self.fixture()
        self.assertTrue(verify(c,[],'asset','unity','owner'))
        self.assertTrue(verify(c,rows+rows,'asset','unity','owner'))
        self.assertTrue(verify(c,rows,'different','unity','owner'))
        self.assertEqual(verify([],None,None,'unity','owner'),[])

if __name__=='__main__':unittest.main()
