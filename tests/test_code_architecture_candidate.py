import json
import tempfile
import unittest
from pathlib import Path

from monkey.code_architecture_candidate import assemble_native_candidate, script_guid
from monkey.candidate_snapshot import snapshot, verify
from monkey.io import encoded, sha
from monkey.sources.compiled import ParseError


class ArchitectureCandidateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir='/private/tmp')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.candidate = self.root / 'Candidate07'
        self.candidate.mkdir()
        self.modules = self.root / 'Modules'
        self.modules.mkdir()
        self.plan_path = self.root / 'architecture.json'
        self.validation_path = self.root / 'validation.json'
        self.output = self.root / 'Assembled'

        resources = {
            'Assets/Game/Content/Config/Base/values.json': b'{"coin":1}\n',
            'Assets/Game/Content/Config/Base/values.json.meta': b'fileFormatVersion: 2\nguid: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n',
            'Assets/Game/Content/Scenes/Main.unity': b'%YAML 1.1\n',
            'Assets/Game/Content/Prefabs/Layout.prefab': b'--- !u!114 &1\nMonoBehaviour:\n  m_Script: {fileID: 11500000, guid: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb}\n',
            'ProjectSettings/ProjectVersion.txt': b'm_EditorVersion: 6000.6.2f1\n',
            'Packages/manifest.json': b'{"dependencies":{"com.unity.ugui":"2.6.0"}}\n',
            'Assets/Game/Gameplay/OldDraft.cs': b'class OldDraft {}\n',
            'SourceRecovery/Code/old.js': b'function old() {}\n',
            'Assets/Game/Presentation/Common/Layout/NativeLinearLayoutGroup.cs': b'public sealed class NativeLinearLayoutGroup {}\npublic sealed class NativeChildLayoutGroup {}\n',
            'Assets/Game/Presentation/Common/Layout/NativeLinearLayoutGroup.cs.meta': b'fileFormatVersion: 2\nguid: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\n',
        }
        self.candidate_rows = []
        for path, raw in resources.items():
            target = self.candidate / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            self.candidate_rows.append(dict(path=path, sha256=sha(raw), bytes=len(raw), owner='generated'))
        manifest_raw = encoded(dict(schemaVersion=1, targetProfile='unity-6000.6.2f1-ugui',
                                    namespace='Fixture.Native', scopeMode='whole-input', files=self.candidate_rows))
        (self.candidate / 'manifest.json').write_bytes(manifest_raw)
        self.candidate_pin = sha(manifest_raw)

        self.plan = {
            'schemaVersion': 'monkey-native-code-architecture/1',
            'sourceManifestSha256': self.candidate_pin,
            'rootNamespace': 'Game',
            'modules': [{'id': 'Core', 'sourceUnitIds': ['unit-a'], 'classIds': ['state'],
                         'responsibility': 'Own model state'}],
            'classes': [{'id': 'state', 'name': 'PlayerState', 'layer': 'Domain', 'module': 'Core',
                         'sourceUnitIds': ['unit-a'], 'fields': [],
                         'methods': [{'name': 'Add', 'sourceMemberIds': ['member-a']}]}],
        }
        self.plan_raw = encoded(self.plan)
        self.plan_path.write_bytes(self.plan_raw)
        self.plan_pin = sha(self.plan_raw)
        self.validation = {
            'valid': True,
            'classPaths': {'state': 'Assets/Game/Domain/Core/PlayerState.cs'},
            'assemblyReferences': {
                'Domain': [], 'Gameplay': ['Domain'],
                'Presentation': ['Domain', 'Gameplay'], 'Services': ['Domain', 'Gameplay'],
                'Bootstrap': ['Domain', 'Gameplay', 'Presentation', 'Services'],
            },
        }
        self.validation_raw = encoded(self.validation)
        self.validation_path.write_bytes(self.validation_raw)
        self.validation_pin = sha(self.validation_raw)
        self.class_source = b'namespace Game.Domain.Core { public sealed class PlayerState { public int Coins; } }\n'
        self._write_module_manifest(self.class_source)

    def _write_module_manifest(self, raw, *, path='Assets/Game/Domain/Core/PlayerState.cs', class_id='state',
                               status='complete', source_units=None, source_members=None,
                               unresolved_units=None, unresolved_members=None):
        for item in sorted(self.modules.rglob('*'), reverse=True):
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                item.rmdir()
        target = self.modules / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        manifest_raw = encoded({
            'schemaVersion': 1,
            'sourceManifestSha256': self.candidate_pin,
            'architectureSha256': self.plan_pin,
            'modules': [{'id': 'Core', 'status': status}],
            'files': [dict(path=path, sha256=sha(raw), bytes=len(raw), classId=class_id,
                           sourceUnitIds=['unit-a'] if source_units is None else source_units,
                           sourceMemberIds=['member-a'] if source_members is None else source_members,
                           unresolvedSourceUnitIds=[] if unresolved_units is None else unresolved_units,
                           unresolvedSourceMemberIds=[] if unresolved_members is None else unresolved_members,
                           status=status)],
        })
        (self.modules / 'manifest.json').write_bytes(manifest_raw)
        self.module_pin = sha(manifest_raw)

    def assemble(self, **kwargs):
        return assemble_native_candidate(
            self.candidate, self.candidate_pin, self.plan_path, self.plan_pin,
            self.validation_path, self.validation_pin, self.modules, self.module_pin,
            self.output, **kwargs)

    def test_builds_only_pinned_resources_and_implemented_planned_code(self):
        report = self.assemble()
        self.assertEqual(report['status'], 'assembled')
        self.assertEqual(report['compileStatus'], 'not_run')
        self.assertFalse(report['compiled'])
        self.assertTrue((self.output / 'Assets/Game/Content/Scenes/Main.unity').is_file())
        self.assertTrue((self.output / 'Assets/Game/Content/Config/Base/values.json.meta').is_file())
        self.assertTrue((self.output / 'Packages/manifest.json').is_file())
        self.assertTrue((self.output / 'ProjectSettings/ProjectVersion.txt').is_file())
        self.assertFalse((self.output / 'Assets/Game/Gameplay/OldDraft.cs').exists())
        self.assertFalse((self.output / 'SourceRecovery/Code/old.js').exists())
        self.assertFalse((self.output / 'Assets/Game/Presentation/Common/Layout/NativeLinearLayoutGroup.cs').exists())
        asmdef = json.loads((self.output / 'Assets/Game/Domain/Domain.asmdef').read_bytes())
        self.assertEqual(asmdef['references'], [])
        self.assertTrue(asmdef['noEngineReferences'])
        src = self.modules / 'Assets/Game/Domain/Core/PlayerState.cs'
        dst = self.output / 'Assets/Game/Domain/Core/PlayerState.cs'
        self.assertNotEqual(src.stat().st_ino, dst.stat().st_ino)

    def test_output_manifest_is_readable_by_standard_candidate_snapshot(self):
        self.assemble()
        root, manifest, files, digest = snapshot(self.output)
        verify(root, files)
        self.assertEqual(manifest['schemaVersion'], 1)
        self.assertEqual(manifest['targetProfile'], 'unity-6000.6.2f1-ugui')
        self.assertEqual(manifest['namespace'], 'Fixture.Native')
        self.assertEqual(manifest['scopeMode'], 'whole-input')
        self.assertEqual(manifest['architectureSchemaVersion'], 'monkey-native-architecture-candidate/1')
        self.assertEqual(manifest['provenance']['architecturePlanSha256'], self.plan_pin)
        self.assertEqual(files['Assets/Game/Domain/Core/PlayerState.cs']['owner'], 'generated')
        self.assertEqual(files['Assets/Game/Content/Scenes/Main.unity']['owner'], 'retained')
        self.assertTrue(digest)

    def test_explicit_partial_is_recorded_without_compile_claim(self):
        self._write_module_manifest(self.class_source, status='partial', source_members=[], unresolved_members=['member-a'])
        report = self.assemble(allow_partial=True)
        self.assertEqual(report['status'], 'partial')
        self.assertEqual(report['partialClassPaths'], ['Assets/Game/Domain/Core/PlayerState.cs'])
        self.assertEqual(report['compileStatus'], 'not_run')

    def test_generated_script_meta_is_stable_across_output_and_code_revision(self):
        first=self.assemble()
        script='Assets/Game/Domain/Core/PlayerState.cs'
        meta=(self.output/(script+'.meta')).read_bytes()
        self.assertFalse((self.modules/(script+'.meta')).exists())
        identity=first['scriptIdentities']['state']
        self.assertEqual(identity['sha256'],sha(self.class_source))
        self.assertEqual(identity['metaSha256'],sha(meta))
        self.assertEqual(identity['unityTypeStatus'],'not_compiled')
        guids=[row['provenance']['guid'] for row in first['files']
               if row['sourceKind'] in ('architecture-script-meta','architecture-assembly-meta')]
        self.assertEqual(len(guids),6)
        self.assertEqual(len(set(guids)),6)
        self.output=self.output.with_name('second-output')
        changed=self.class_source.replace(b'int Coins;',b'long Coins;')
        self._write_module_manifest(changed)
        second=self.assemble()
        self.assertEqual((self.output/(script+'.meta')).read_bytes(),meta)
        self.assertNotEqual(second['scriptIdentities']['state']['sha256'],identity['sha256'])
        self.assertEqual(second['scriptIdentities']['state']['guid'],identity['guid'])

    def test_generated_script_guid_collision_with_resource_is_rejected(self):
        path='Assets/Game/Content/Config/Base/values.json.meta'
        raw=('fileFormatVersion: 2\nguid: '+script_guid('Fixture.Native','Game','state')+'\n').encode()
        (self.candidate/path).write_bytes(raw)
        for row in self.candidate_rows:
            if row['path']==path:row.update(sha256=sha(raw),bytes=len(raw))
        candidate=json.loads((self.candidate/'manifest.json').read_bytes());candidate['files']=self.candidate_rows
        (self.candidate/'manifest.json').write_bytes(encoded(candidate))
        self.candidate_pin=sha((self.candidate/'manifest.json').read_bytes())
        self.plan['sourceManifestSha256']=self.candidate_pin
        self.plan_raw=encoded(self.plan);self.plan_path.write_bytes(self.plan_raw);self.plan_pin=sha(self.plan_raw)
        self._write_module_manifest(self.class_source)
        with self.assertRaises(ParseError) as caught:self.assemble()
        self.assertEqual(caught.exception.code,'ARCH_CANDIDATE_DUPLICATE_GUID')
        self.assertFalse(self.output.exists())

    def test_empty_placeholder_type_is_rejected(self):
        self._write_module_manifest(b'// planned implementation goes here\n')
        with self.assertRaises(ParseError) as caught:
            self.assemble()
        self.assertEqual(caught.exception.code, 'ARCH_CANDIDATE_EMPTY_IMPLEMENTATION')

    def test_missing_implementation_requires_explicit_partial_assembly(self):
        for item in sorted(self.modules.rglob('*'), reverse=True):
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                item.rmdir()
        (self.modules / 'manifest.json').write_bytes(encoded({
            'sourceManifestSha256': self.candidate_pin,
            'architectureSha256': self.plan_pin,
            'files': [], 'modules': [{'id': 'Core', 'status': 'partial'}],
        }))
        self.module_pin = sha((self.modules / 'manifest.json').read_bytes())
        with self.assertRaises(ParseError) as caught:
            self.assemble()
        self.assertEqual(caught.exception.code, 'ARCH_CANDIDATE_MISSING_IMPLEMENTATION')
        report = self.assemble(allow_partial=True)
        self.assertEqual(report['status'], 'partial')
        self.assertEqual(report['missingClassPaths'], ['Assets/Game/Domain/Core/PlayerState.cs'])

    def test_rejects_unplanned_class_path_and_wrong_module_owner(self):
        other = 'Assets/Game/Domain/Core/Unexpected.cs'
        self._write_module_manifest(b'public class PlayerState {}\n', path=other)
        with self.assertRaises(ParseError) as caught:
            self.assemble()
        self.assertEqual(caught.exception.code, 'ARCH_CANDIDATE_MODULE_PATH')

    def test_native_layout_support_is_retained_only_as_explicit_cs_meta_pair(self):
        pair = [
            'Assets/Game/Presentation/Common/Layout/NativeLinearLayoutGroup.cs',
            'Assets/Game/Presentation/Common/Layout/NativeLinearLayoutGroup.cs.meta',
        ]
        report = self.assemble(retained_support_paths=pair)
        support = self.output / pair[0]
        self.assertTrue(support.is_file())
        self.assertIn('NativeChildLayoutGroup', support.read_text())
        record = next(row for row in report['files'] if row['path'] == pair[0])
        self.assertEqual(record['owner'], 'retained')
        self.assertEqual(record['sourceKind'], 'existing-implementation')
        self.assertEqual(record['provenance']['kind'], 'native-layout-support')
        self.assertEqual(report['retainedSupportPaths'], sorted(pair))

    def test_support_rejects_unapproved_paths_and_missing_meta_pair(self):
        with self.assertRaises(ParseError) as caught:
            self.assemble(retained_support_paths=['Assets/Game/Presentation/Common/Layout/NativeLinearLayoutGroup.cs'])
        self.assertEqual(caught.exception.code, 'ARCH_CANDIDATE_SUPPORT_PATHS')
        with self.assertRaises(ParseError) as caught:
            self.assemble(retained_support_paths=[
                'Assets/Game/Presentation/Common/Layout/OtherHelper.cs',
                'Assets/Game/Presentation/Common/Layout/OtherHelper.cs.meta'])
        self.assertEqual(caught.exception.code, 'ARCH_CANDIDATE_SUPPORT_PATHS')

    def test_module_manifest_pins_and_source_mapping_are_bound_to_plan(self):
        self._write_module_manifest(self.class_source, source_units=['unit-other'])
        with self.assertRaises(ParseError) as caught:
            self.assemble()
        self.assertEqual(caught.exception.code, 'ARCH_CANDIDATE_MODULE_MAPPING')
        self._write_module_manifest(self.class_source)
        doc = json.loads((self.modules / 'manifest.json').read_bytes())
        doc['architectureSha256'] = 'd' * 64
        raw = encoded(doc)
        (self.modules / 'manifest.json').write_bytes(raw)
        self.module_pin = sha(raw)
        with self.assertRaises(ParseError) as caught:
            self.assemble()
        self.assertEqual(caught.exception.code, 'ARCH_CANDIDATE_MODULE_ARCHITECTURE_PIN')

    def test_complete_rows_must_cover_planned_members_and_cannot_add_unknown_members(self):
        self._write_module_manifest(self.class_source, source_members=[])
        with self.assertRaises(ParseError) as caught:
            self.assemble()
        self.assertEqual(caught.exception.code, 'ARCH_CANDIDATE_MODULE_MAPPING')
        self._write_module_manifest(self.class_source, source_members=['member-a', 'unplanned-member'])
        with self.assertRaises(ParseError) as caught:
            self.assemble()
        self.assertEqual(caught.exception.code, 'ARCH_CANDIDATE_MODULE_MAPPING')

    def test_plan_source_pin_must_match_candidate_manifest(self):
        plan = dict(self.plan)
        plan['sourceManifestSha256'] = 'd' * 64
        raw = encoded(plan)
        self.plan_path.write_bytes(raw)
        self.plan_pin = sha(raw)
        self._write_module_manifest(self.class_source)
        with self.assertRaises(ParseError) as caught:
            self.assemble()
        self.assertEqual(caught.exception.code, 'ARCH_CANDIDATE_PLAN_SOURCE_PIN')

    def test_empty_class_shell_is_rejected_but_does_not_claim_business_completeness(self):
        self._write_module_manifest(b'public sealed class PlayerState { }\n')
        with self.assertRaises(ParseError) as caught:
            self.assemble()
        self.assertEqual(caught.exception.code, 'ARCH_CANDIDATE_EMPTY_IMPLEMENTATION')

    def test_rejects_stale_source_and_output_conflict(self):
        (self.candidate / 'Assets/Game/Content/Scenes/Main.unity').write_bytes(b'changed')
        with self.assertRaises(ParseError) as caught:
            self.assemble()
        self.assertEqual(caught.exception.code, 'ARCH_CANDIDATE_SOURCE_CHANGED')
        (self.candidate / 'Assets/Game/Content/Scenes/Main.unity').write_bytes(b'%YAML 1.1\n')
        self.output.mkdir()
        with self.assertRaises(ParseError) as caught:
            self.assemble()
        self.assertEqual(caught.exception.code, 'ARCH_CANDIDATE_OUTPUT_EXISTS')


if __name__ == '__main__':
    unittest.main()
