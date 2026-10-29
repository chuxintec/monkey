import tempfile
import unittest
from pathlib import Path
from fixtures import fixture, normal, PREFAB
from monkey.io import write_json, read, load
from monkey.sources.bundle import inspect
from monkey.normalize import normalize
from monkey.targets import unity, cocos


class InputBlockerTests(unittest.TestCase):
    def test_source_blocker_survives_both_native_plans_and_exports(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            config = fixture(root / 'source')
            write_json(config.parent / 'import' / PREFAB[:2] / (PREFAB + '.a.json'), normal([
                {'__type__': 'cc.Prefab', 'data': {'__id__': 1}},
                {'__type__': 'cc.Node', '_name': 'InputShield', '_children': [],
                 '_components': [{'__id__': 2}], '_contentSize': {'width': 200, 'height': 100}},
                {'__type__': 'cc.BlockInputEvents', 'node': {'__id__': 1}, '_enabled': False},
            ]))
            inspect(config, [2], root / 'inspect')
            normalize(root / 'inspect/source-manifest.json', root / 'normalized')
            ir = load(read(root / 'normalized/ir.json'))
            self.assertEqual(ir['prefabCompleteness']['sourceComponents'], 1)
            self.assertFalse(ir['prefabCompleteness']['complete'])
            for adapter, name in [(unity, 'unity'), (cocos, 'creator')]:
                plan = adapter.plan(root / 'normalized/ir.json', 'input-shield', root / (name + '-plan'))
                component = plan['components'][0]
                self.assertEqual(component['type'], 'cc.BlockInputEvents')
                self.assertTrue(component['convertible'])
                self.assertFalse(component['enabled'])
                exported = adapter.export(root / (name + '-plan/plan.json'), root / name)
                if name == 'unity':
                    paths = [f['path'] for f in exported['files']]
                    self.assertTrue(any(p.endswith('/NativeInputBlocker.cs') for p in paths))
                    self.assertTrue(any(p.endswith('/NativeInputBlockerSurface.cs') for p in paths))
