import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from monkey.code_graph import facts
from monkey.code_profiles import load_profile
from monkey.code_selection import select_modules, write_selection
from monkey.code_modules import prepare
from monkey.io import write_json
from monkey.sources.compiled import ParseError
from monkey.io import load


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'outputs/foodstreet-unified-textures/UnityProject/SourceRecovery/Code/Source/snapshot/_subpackages_main_/subpackages/main/game.js'
PROFILE = 'foodstreet-demand-health-v1'


class CodeSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SOURCE.is_file():
            raise unittest.SkipTest('Frozen FoodStreet source is unavailable')
        cls.spec = load(load_profile(PROFILE, SOURCE))

    def test_selected_caller_closes_typed_cross_class_and_same_class_dependencies(self):
        result = select_modules(SOURCE, [{'classId': 'class@binding@926434', 'methodId': 'method@936255'}], self.spec)
        self.assertEqual(result['status'], 'selected_ready')
        self.assertEqual(result['requested'], ['method@936255'])
        self.assertEqual(set(result['autoAdded']), {'method@616964', 'method@617302'})
        self.assertNotIn('method@933413', result['selected'])  # only a falsey fallback; required Map input is truthy
        selected_names = {m['id']: [row['name'] for row in m['methods']] for m in result['contract']['modules']}
        self.assertEqual(selected_names['OrderRules'], ['FindDishOrderDemands'])
        self.assertEqual(selected_names['RecipeCatalog'], ['IsDish', 'GetRecipeOf'])
        self.assertEqual(result['contract']['records'], [self.spec['records'][i] for i in range(len(self.spec['records'])) if self.spec['records'][i]['name'] == 'Recipe'])
        self.assertEqual(result['contract']['recordShapeEvidence'], [{
            'methodId': 'method@621011',
            'methodSha256': '9bf3773ef1f94374aec1958e38f499b4ba698f73de73fd454ae0fe6701048061',
        }])
        self.assertFalse(result['sourceExecuted'])

    def test_record_shape_witness_cannot_be_forged_or_omitted(self):
        result = select_modules(SOURCE, [{'classId': 'class@binding@926434', 'methodId': 'method@936255'}], self.spec)
        with tempfile.TemporaryDirectory(dir='/private/tmp') as temporary:
            path=Path(temporary)/'contract.json'
            for mutation,code in [('forged','RECORD_EVIDENCE'),('omitted','CODE_MODULE_RECORD')]:
                contract=copy.deepcopy(result['contract'])
                if mutation=='forged': contract['recordShapeEvidence'][0]['methodSha256']='0'*64
                else: contract['recordShapeEvidence']=[]
                write_json(path,contract)
                with self.assertRaisesRegex(ParseError,code): prepare(SOURCE,path)

    def test_source_consumer_with_unresolved_class_is_not_reported_missing(self):
        result=select_modules(SOURCE,[{'classId':None,'methodId':'method@3177644'}],self.spec)
        self.assertEqual(result['status'],'unsupported_semantics')
        self.assertEqual(result['diagnostics'][0]['code'],'CODE_SELECTION_CLASS_UNRESOLVED')

    def test_cli_boundary_checks_lowering_and_does_not_write_blocked_contract(self):
        source_bytes=b'var X=(function(){function C(){}; C.run=function(x){return x >> 1;}; return C;})();'
        with tempfile.TemporaryDirectory(dir='/private/tmp') as temporary:
            root=Path(temporary);source=root/'source.js';source.write_bytes(source_bytes)
            graph=facts(source);cls=graph['classes'][0];method=graph['methods'][0]
            contract=dict(schemaVersion=1,namespace='Test.Recovered',sourceSha256=hashlib.sha256(source_bytes).hexdigest(),records=[],modules=[dict(id='X',targetClass='X',classId=cls['id'],classSha256=cls['sourceSha256'],fields={},methods=[dict(id=method['id'],sha256=method['sourceSha256'],name='Run',parameters=['Number'],returns='Number')])])
            write_json(root/'types.json',contract);write_json(root/'roots.json',[dict(classId=cls['id'],methodId=method['id'])])
            result=write_selection(source,root/'roots.json',root/'out',type_evidence=root/'types.json')
            self.assertEqual(result['status'],'unsupported_semantics');self.assertEqual(result['lowering'],'blocked')
            self.assertFalse((root/'out/module-contract.json').exists())

    def test_existing_source_method_without_type_contract_is_explicit_gap(self):
        result = select_modules(SOURCE, [{'classId': 'class@binding@926434', 'methodId': 'method@933413'}], self.spec)
        self.assertEqual(result['status'], 'missing_type_or_dependency_contract')
        self.assertEqual(result['diagnostics'][0]['code'], 'CODE_SELECTION_TYPE_CONTRACT_MISSING')

    def test_unknown_type_is_not_guessed(self):
        spec = copy.deepcopy(self.spec)
        method = next(m for module in spec['modules'] for m in module['methods'] if m['id'] == 'method@933967')
        method['parameters'] = ['NotReviewed']
        result = select_modules(SOURCE, [{'classId': 'class@binding@926434', 'methodId': 'method@933967'}], spec)
        self.assertEqual(result['status'], 'missing_type_or_dependency_contract')
        self.assertTrue(any(d['code'] == 'CODE_TYPE' and 'parameters' in d['location'] for d in result['diagnostics']))

    def test_async_source_method_is_classified_as_unsupported(self):
        source_bytes = b'var X=(function(){function C(){}; C.prototype.run=async function(){return 1;}; return C;})();\n'
        with tempfile.TemporaryDirectory(dir='/private/tmp') as temporary:
            source = Path(temporary) / 'mini.js'
            source.write_bytes(source_bytes)
            graph = facts(source)
            cls = graph['classes'][0]
            method = next(m for m in graph['methods'] if m['name'] == 'run')
            evidence = {'schemaVersion': 1, 'sourceSha256': hashlib.sha256(source_bytes).hexdigest(),
                        'namespace': 'Test.Recovered', 'records': [], 'callDomain': 'finite test domain',
                        'modules': [{'id': 'X', 'targetClass': 'X', 'classId': cls['id'], 'classSha256': cls['sourceSha256'],
                                     'fields': {}, 'methods': [{'id': method['id'], 'name': 'run', 'sha256': method['sourceSha256'],
                                                                'parameters': [], 'returns': 'Number', 'locals': {}}]}]}
            result = select_modules(source, [{'classId': cls['id'], 'methodId': method['id']}], evidence)
        self.assertEqual(result['status'], 'unsupported_semantics')
        self.assertEqual(result['diagnostics'][0]['code'], 'CODE_SELECTION_UNSUPPORTED_ASYNC')

    def test_source_identity_mismatch_is_missing_source_and_is_deterministic(self):
        with tempfile.TemporaryDirectory(dir='/private/tmp') as temporary:
            source = Path(temporary) / 'wrong.js'
            source.write_text('var unrelated = 1;\n', encoding='utf-8')
            result = select_modules(source, [{'classId': 'class@binding@926434', 'methodId': 'method@936255'}], self.spec)
            self.assertEqual(result['status'], 'missing_source')
            self.assertEqual(result['diagnostics'][0]['code'], 'CODE_GRAPH_SOURCE_IDENTITY')
        args = (SOURCE, [{'classId': 'class@binding@926434', 'methodId': 'method@936255'}], self.spec)
        first, second = select_modules(*args), select_modules(*args)
        self.assertEqual(first, second)


if __name__ == '__main__':
    unittest.main()
