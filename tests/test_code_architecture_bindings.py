import hashlib
import json
import unittest

from monkey.code_architecture_bindings import (
    _native_field_type_match,
    build_prefab_authoring_plan,
    extract_serialized_csharp_fields,
    extract_source_component_fields,
)
from monkey.sources.compiled import ParseError


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def plain_compiled_document(objects):
    classes, masks, values = [], [], []
    for index, obj in enumerate(objects):
        keys = [key for key in obj if key != '__type__']
        classes.append([obj['__type__'], keys, len(keys) + 1])
        masks.append([index, *range(len(keys)), len(keys) + 1])
        values.append([index, *[obj[key] for key in keys]])
    return [1, [], [], classes, masks, values, [], [], [], [], []]


def fixture(*, node_types=('UnityEngine.RectTransform',), preview_reference=None):
    source_asset = 'gameAsset:source-prefab'
    source_root = source_asset + '#1'
    source_component = source_asset + '#1/components/1'
    code_region = 'bundle:game.js#DemoView@0'
    unit_id = 'module:abc:0:100'
    source_file = b'n([property(cc.Node)],i.prototype,"nodeRef",void 0);'
    class_path = 'Assets/Game/Presentation/Demo/View.cs'
    class_source = b'''using UnityEngine;
public sealed class View : MonoBehaviour
{
    [SerializeField] private UnityEngine.RectTransform nodeRef;
}
'''
    prefab = b'''%YAML 1.1
--- !u!1 &100
GameObject:
  m_Name: Root
--- !u!224 &101
RectTransform:
  m_GameObject: {fileID: 100}
  m_Father: {fileID: 0}
'''
    prefab_meta = b'fileFormatVersion: 2\nguid: ' + b'1' * 32 + b'\n'
    script_meta = b'fileFormatVersion: 2\nguid: ' + b'2' * 32 + b'\n'
    source_span = {'start': 0, 'end': len(source_file)}
    source_context = {
        'sourceUnitId': unit_id, 'sourcePath': 'Source/game.js',
        'sourceSha256': sha(source_file), 'sourceBytes': source_span,
        'spanSha256': sha(source_file),
    }
    architecture_sha = 'a' * 64
    source_manifest_sha = 'b' * 64
    class_record = {
        'id': 'Demo.View', 'name': 'View', 'kind': 'class', 'layer': 'Presentation', 'module': 'Demo',
        'path': class_path, 'sourceUnitIds': [unit_id], 'fields': [
            {'name': 'nodeRef', 'type': 'UnityEngine.RectTransform', 'role': 'serialized view binding'}],
    }
    architecture = {'schemaVersion': 'monkey-native-code-architecture/1',
                    'sourceManifestSha256': source_manifest_sha, 'classes': [class_record]}
    module_manifest = {
        'schemaVersion': 'monkey-native-architecture-module/1', 'moduleId': 'Demo',
        'sourceManifestSha256': source_manifest_sha, 'architectureSha256': architecture_sha,
        'classes': [{'classId': 'Demo.View', 'module': 'Demo', 'path': class_path, 'bytes': len(class_source)}],
        'files': [
            {'path': class_path, 'targetPath': class_path, 'sha256': sha(class_source), 'bytes': len(class_source)},
            {'path': class_path + '.meta', 'targetPath': class_path + '.meta', 'sha256': sha(script_meta), 'bytes': len(script_meta)},
        ],
        'sourceContexts': [source_context],
    }
    source_node_readback = {'sourceId': source_root, 'sourceAsset': source_asset,
                            'hierarchy': 'Root', 'componentTypes': ['UnityEngine.RectTransform']}
    context = {
        'schemaVersion': 'monkey-code-architecture-asset-context/1',
        'sourceManifestSha256': source_manifest_sha, 'architectureSha256': architecture_sha,
        'bindings': [{
            'codeRegion': code_region, 'evidence': 'exact_literal_script_identity',
            'sourceOwnership': {'sourceUnitIds': [unit_id], 'classesWithThisSourceUnit': ['Demo.View']},
            'sourceAsset': source_asset, 'sourceComponent': source_component, 'sourceNode': source_root,
            'nativeComponentStatus': 'not_implemented',
            'sourceMapNodes': [{'sourceId': source_root, 'name': 'Root', 'target': 'Assets/Game/Prefabs/Demo.prefab'}],
            'sourceMapComponents': [{'sourceId': source_component, 'node': source_root, 'type': 'demo-script'}],
            'sourcePrefabReadback': [{'sourceId': source_asset, 'path': 'Assets/Game/Prefabs/Demo.prefab',
                                      'guid': '1' * 32, 'identityMatch': True}],
            'sourcePrefabNodeReadback': [source_node_readback],
            'assetIdentity': {'nativeTargets': [{
                'path': 'Assets/Game/Prefabs/Demo.prefab', 'type': 'prefab', 'guid': '1' * 32,
                'sha256': sha(prefab), 'bytes': len(prefab), 'metaSha256': sha(prefab_meta), 'metaBytes': len(prefab_meta),
            }]},
            'previewReadbackReference': preview_reference,
        }],
    }
    graph = {
        'sourceAssetId': source_asset, 'rootSourceNodeId': source_root,
        'nodes': [
            {'sourceNodeId': source_root, 'name': 'Root', 'parentSourceNodeId': None, 'childIndex': None},
            {'sourceNodeId': source_asset + '#2', 'name': 'Label', 'parentSourceNodeId': source_root, 'childIndex': 0},
        ],
        'componentProperties': [{
            'sourceComponentId': source_component, 'sourceProperty': 'nodeRef',
            'targetSourceNodeId': source_asset + '#2', 'evidencePath': 'Analysis/SourceModel/demo-prefab.json',
            'evidenceSha256': sha(b'exact source component field reference'),
        }],
    }
    target_nodes = [{'sourceId': source_asset + '#2', 'prefabPath': 'Assets/Game/Prefabs/Demo.prefab',
                     'prefabGuid': '1' * 32, 'componentTypes': list(node_types)}]
    kwargs = dict(
        architecture=architecture, module_manifest=module_manifest, asset_context=context,
        class_id='Demo.View', architecture_sha256=architecture_sha, code_region=code_region,
        source_unit_id=unit_id, source_file_bytes=source_file, class_source_bytes=class_source,
        prefab_bytes=prefab, prefab_meta_bytes=prefab_meta,
        field_mappings=[{'sourceProperty': 'nodeRef', 'csharpField': 'nodeRef'}],
        source_reference_graph=graph, target_node_readback=target_nodes, script_meta_bytes=script_meta,
    )
    return kwargs


def packed_source_fixture():
    kwargs = fixture()
    source_asset = 'gameAsset:00000000-0000-0000-0000-000000000003'
    source_component = source_asset + '#1/components/1'
    source_root = source_asset + '#1'
    child_id = source_asset + '#4'
    binding = kwargs['asset_context']['bindings'][0]
    binding.update(sourceAsset=source_asset, sourceComponent=source_component, sourceNode=source_root)
    binding['sourceMapComponents'][0].update(sourceId=source_component, node=source_root, type='demo-script')
    binding['sourceMapNodes'][0].update(sourceId=source_root, name='Root')
    binding['sourcePrefabReadback'][0].update(sourceId=source_asset, path='Assets/Game/Prefabs/Demo.prefab')
    binding['sourcePrefabNodeReadback'][0].update(sourceId=source_root, sourceAsset=source_asset, hierarchy='Root')
    kwargs.pop('source_reference_graph')

    objects = [
        {'__type__': 'cc.Prefab', 'data': {'__id__': 1}},
        {'__type__': 'cc.Node', '_name': 'Root', '_components': [{'__id__': 2}, {'__id__': 3}],
         '_children': [{'__id__': 4}]},
        {'__type__': 'cc.Widget', 'node': {'__id__': 1}},
        {'__type__': 'demo-script', 'node': {'__id__': 1}, 'nodeRef': {'__id__': 4}},
        {'__type__': 'cc.Node', '_name': 'Label', '_components': [], '_children': []},
    ]
    encoded = plain_compiled_document(objects)
    pack_bytes = json.dumps(encoded[:5] + [[encoded[5:]]], separators=(',', ':')).encode()
    config_bytes = json.dumps({'uuids': ['00000000-0000-0000-0000-000000000003'],
                               'packs': {'111111111': [0]}}).encode()
    prefab = b'''%YAML 1.1
--- !u!1 &100
GameObject:
  m_Component:
  - component: {fileID: 101}
  m_Name: Root
--- !u!224 &101
RectTransform:
  m_GameObject: {fileID: 100}
  m_Children:
  - {fileID: 201}
  m_Father: {fileID: 0}
--- !u!1 &200
GameObject:
  m_Component:
  - component: {fileID: 201}
  m_Name: Label
--- !u!224 &201
RectTransform:
  m_GameObject: {fileID: 200}
  m_Children: []
  m_Father: {fileID: 101}
'''
    kwargs['prefab_bytes'] = prefab
    kwargs['asset_context']['bindings'][0]['assetIdentity']['nativeTargets'][0].update(
        sha256=sha(prefab), bytes=len(prefab))
    readback = {'sourcePrefabs': [{
        'sourceId': source_asset, 'path': 'Assets/Game/Prefabs/Demo.prefab', 'guid': '1' * 32,
        'nodeCount': 2, 'savedReloaded': True, 'referencesVerified': True,
        'nodes': [
            {'sourceId': source_root, 'hierarchy': 'Root', 'componentTypes': ['UnityEngine.RectTransform']},
            {'sourceId': child_id, 'hierarchy': 'Label', 'componentTypes': ['UnityEngine.RectTransform']},
        ],
    }]}
    kwargs.update(
        source_prefab_pack_bytes=pack_bytes,
        source_project_config_bytes=config_bytes,
        source_pack_id='111111111',
        source_prefab_pack_sha256=sha(pack_bytes),
        source_project_config_sha256=sha(config_bytes),
        native_readback_bytes=json.dumps(readback, separators=(',', ':')).encode(),
    )
    kwargs['native_readback_sha256'] = sha(kwargs['native_readback_bytes'])
    return kwargs


class CodeArchitectureBindingsTests(unittest.TestCase):
    def test_exact_component_property_and_node_path_produce_editor_intent(self):
        plan = build_prefab_authoring_plan(**fixture())
        self.assertEqual(plan['status'], 'ready-for-editor-authoring-after-whole-project-compile')
        self.assertEqual(plan['component']['target']['nodePath'], [{'root': True, 'expectedName': 'Root'}])
        field = plan['fieldMappings'][0]
        self.assertEqual(field['referenceStatus'], 'verified-node-reference')
        self.assertEqual(field['reference']['nodePath'][-1]['childIndex'], 0)
        self.assertEqual(plan['operations'][0]['kind'], 'attach-component-to-root')
        self.assertEqual(plan['operations'][1]['csharpField'], 'nodeRef')
        self.assertIn('not runtime lookup keys', plan['runtimeUse'])

    def test_missing_serialized_reference_stays_unresolved_and_preview_fileid_is_ignored(self):
        kwargs = fixture(preview_reference={'status': 'verified-preview-object-reference-only', 'prefabFileId': '999'})
        kwargs['source_reference_graph'] = {'sourceAssetId': 'gameAsset:source-prefab',
                                             'rootSourceNodeId': 'gameAsset:source-prefab#1',
                                             'nodes': [], 'componentProperties': []}
        plan = build_prefab_authoring_plan(**kwargs)
        self.assertEqual(plan['fieldMappings'][0]['referenceStatus'], 'unresolved')
        self.assertFalse(any(op['kind'] == 'set-serialized-reference' for op in plan['operations']))
        self.assertNotIn('prefabFileId', str(plan))

    def test_no_case_folding_for_source_to_csharp_names(self):
        kwargs = fixture()
        kwargs['field_mappings'] = []
        plan = build_prefab_authoring_plan(**kwargs)
        self.assertTrue(any(row.get('sourceProperty') == 'nodeRef' for row in plan['unresolved']))
        self.assertTrue(any(row.get('csharpField') == 'nodeRef' for row in plan['unresolved']))

    def test_rejects_wrong_candidate_prefab_bytes_and_foreign_script_meta(self):
        kwargs = fixture()
        kwargs['prefab_bytes'] += b'changed'
        with self.assertRaisesRegex(ParseError, 'Prefab bytes differ'):
            build_prefab_authoring_plan(**kwargs)
        kwargs = fixture()
        kwargs['script_meta_bytes'] = b'fileFormatVersion: 2\nguid: ' + b'3' * 32 + b'\n'
        with self.assertRaisesRegex(ParseError, 'Script .meta bytes differ'):
            build_prefab_authoring_plan(**kwargs)

    def test_incompatible_native_component_does_not_emit_reference_assignment(self):
        plan = build_prefab_authoring_plan(**fixture(node_types=('UnityEngine.UI.Image',)))
        self.assertEqual(plan['fieldMappings'][0]['referenceStatus'],
                         'source-reference-and-node-path-verified-target-component-missing')
        self.assertEqual(plan['fieldMappings'][0]['reference']['nodePath'][-1]['expectedName'], 'Label')
        self.assertIn('does not have the required', plan['fieldMappings'][0]['unresolvedReason'])
        self.assertFalse(any(op['kind'] == 'set-serialized-reference' for op in plan['operations']))

    def test_source_and_target_field_extractors_keep_exact_types_and_identity(self):
        source = b'n([property(cc.Node)],i.prototype,"nodeRef",void 0); n([property(cc.ProgressBar)],i.prototype,"bar",void 0);'
        fields = extract_source_component_fields(source, base_offset=30)
        self.assertEqual([(f['sourceProperty'], f['sourceTypeExpression']) for f in fields],
                         [('nodeRef', 'cc.Node'), ('bar', 'cc.ProgressBar')])
        csharp = b'class V { [SerializeField] private UnityEngine.RectTransform nodeRef; }'
        self.assertEqual(extract_serialized_csharp_fields(csharp)[0]['fieldType'], 'UnityEngine.RectTransform')

    def test_rejects_nonmatching_source_hash_and_unknown_field_mapping(self):
        kwargs = fixture()
        kwargs['source_file_bytes'] += b'changed'
        with self.assertRaisesRegex(ParseError, 'Original source file differs'):
            build_prefab_authoring_plan(**kwargs)
        kwargs = fixture()
        kwargs['field_mappings'] = [{'sourceProperty': 'NodeRef', 'csharpField': 'nodeRef'}]
        with self.assertRaisesRegex(ParseError, 'not found in the pinned source component'):
            build_prefab_authoring_plan(**kwargs)

    def test_decodes_exact_pack_component_reference_and_proves_candidate_hierarchy(self):
        kwargs = packed_source_fixture()
        plan = build_prefab_authoring_plan(**kwargs)
        self.assertEqual(plan['sourceReferenceEvidence']['sourcePackSectionIndex'], 0)
        self.assertEqual(plan['sourceReferenceEvidence']['sourceUuidIndex'], 0)
        self.assertEqual(plan['sourcePrefabStructure']['status'], 'verified-isomorphic-child-index-hierarchy')
        field = plan['fieldMappings'][0]
        self.assertEqual(field['referenceStatus'], 'verified-node-reference')
        self.assertEqual(field['serializedSourceValue'], {'__id__': 4})
        self.assertEqual([step.get('expectedName') for step in field['reference']['nodePath']], ['Root', 'Label'])
        self.assertEqual([step.get('candidateNodeType') for step in field['reference']['nodePath']],
                         ['UnityEngine.RectTransform', 'UnityEngine.RectTransform'])
        self.assertEqual(field['reference']['nodePath'][-1]['childIndex'], 0)
        self.assertEqual([operation['kind'] for operation in plan['operations']],
                         ['attach-component-to-root', 'set-serialized-reference'])

    def test_known_serialized_base_field_accepts_only_documented_derived_component_types(self):
        self.assertEqual(_native_field_type_match('TMPro.TMP_Text', ['TMPro.TextMeshProUGUI']), 'known-derived-type')
        self.assertEqual(_native_field_type_match('TMPro.TMP_Text', ['UnityEngine.UI.Image']), 'missing')

    def test_source_property_reference_is_not_authorized_when_candidate_tree_differs(self):
        kwargs = packed_source_fixture()
        changed = kwargs['prefab_bytes'].replace(b'm_Name: Label', b'm_Name: Other')
        kwargs['prefab_bytes'] = changed
        target = kwargs['asset_context']['bindings'][0]['assetIdentity']['nativeTargets'][0]
        target.update(sha256=sha(changed), bytes=len(changed))
        plan = build_prefab_authoring_plan(**kwargs)
        self.assertEqual(plan['sourcePrefabStructure']['status'], 'unresolved-hierarchy-mismatch')
        self.assertEqual(plan['fieldMappings'][0]['referenceStatus'], 'unresolved')
        self.assertFalse(any(row['kind'] == 'set-serialized-reference' for row in plan['operations']))

    def test_packed_source_bytes_require_exact_hash_pins(self):
        kwargs = packed_source_fixture()
        kwargs['source_prefab_pack_sha256'] = '0' * 64
        with self.assertRaisesRegex(ParseError, 'bytes differ from their supplied pins'):
            build_prefab_authoring_plan(**kwargs)

    def test_packed_section_must_be_selected_by_exact_config_uuid_membership(self):
        kwargs = packed_source_fixture()
        config = json.loads(kwargs['source_project_config_bytes'])
        config['packs']['111111111'] = [7]
        kwargs['source_project_config_bytes'] = json.dumps(config, separators=(',', ':')).encode()
        kwargs['source_project_config_sha256'] = sha(kwargs['source_project_config_bytes'])
        with self.assertRaisesRegex(ParseError, 'Source UUID must occur exactly once'):
            build_prefab_authoring_plan(**kwargs)


if __name__ == '__main__':
    unittest.main()
