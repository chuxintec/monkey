import argparse
import json
import sys
from . import __version__
from .sources.bundle import inspect, PROFILE
from .sources.compiled import ParseError
from .sources.project import inspect as inspect_project, catalog, PROFILE as PROJECT_PROFILE
from .normalize import normalize
from .targets.unity import plan, export, verify, handoff, PROFILE as UNITY_PROFILE
from .targets import cocos
from . import incremental
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(prog='monkey')
    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    sub = parser.add_subparsers(dest='command', required=True)
    cap = sub.add_parser('capabilities')
    cap.add_argument('--json', action='store_true')
    p = sub.add_parser('convert', help='Convert a source project into an isolated native project candidate')
    p.add_argument('--source', help='Local wxapkg/APK, resource/project directory, project.json or bundle config.json')
    p.add_argument('--format',choices=['none','grea'],default=None,help='Optional post-export layout; default none. Fresh package conversion only.')
    p.add_argument('--source-family', choices=['auto','cocos','unity','laya','layaair','egret','eraget','custom','other'], default='auto')
    p.add_argument('--provider-python', help='Existing Python with UnityPy 1.25.3 for Unity source conversion')
    p.add_argument('--asset-ripper', help='Existing exact AssetRipper 2.0.0 provider executable')
    p.add_argument('--provider-budget-seconds', type=int, default=600)
    p.add_argument('--unity-texture-cache',help='Explicit local ASTC cache pool for supported Unity texture-key hydration')
    p.add_argument('--unity-quarantine-invalid-textures',action='store_true',help='Explicit partial export excluding exact invalid ETC1 objects; originals and unresolved references retained')
    p.add_argument('--unity-dependency-manifest',help='Frozen Unity bundle lookup pool; export only exact reachable serialized-file closure')
    p.add_argument('--unity-export-scope',choices=['reachable','all'],default='reachable',help='all exports every unique container in the explicit Unity bundle manifest')
    p.add_argument('--unity-prepared-textures',help='Frozen prepare-unity-bulk output; reuse exact derived containers')
    p.add_argument('--unity-reuse-provider-export',help='Frozen export-unity-bulk output; assemble without relaunching provider')
    p.add_argument('--unity-reuse-inspection',help='Reuse an exact same-worker complete inspect-unity --bundle-manifest snapshot')
    p.add_argument('--unity-code-evidence',help='Frozen metadata/declaration/source-code evidence manifest for a self-contained AI handoff')
    p.add_argument('--unity-schema-manifest',help='Frozen bundle pool for exact missing TypeTree lookup during Unity conversion')
    p.add_argument('--numeric-code-contract',help='Explicit source identity and numeric Label-field or reviewed static Number-method contract; fresh package conversion only')
    p.add_argument('--cocos-code-language',choices=['ts','js'],default='ts',help='Cocos code output; TypeScript first; JS uses an explicit ESM package boundary')
    p.add_argument('--reuse-source-stages',help='Fresh package output using verified source stages; supports names-v1 metadata migration')
    p.add_argument('--input-set', help='Explicit local roots and identity/provenance manifest (schema 1)')
    p.add_argument('--target', choices=['unity','cocos','unity6','cocos38','both',UNITY_PROFILE,cocos.PROFILE])
    p.add_argument('--package', action='store_true', help='Inventory all input files and generate self-contained recovery workspaces')
    p.add_argument('--out', '--output', help='Fresh output directory; package targets use UnityProject/ and CocosProject/')
    p.add_argument('--resume', help='Resume a conversion with identity/hash checks; packages also require --input-set')
    p.add_argument('--recipe', help='Reusable JSON input/selection options; combine with --out')
    p.add_argument('--offline', action='store_true', help='Explicitly generate and verify an offline candidate only')
    p.add_argument('--namespace')
    p.add_argument('--source-profile', choices=[PROFILE,PROJECT_PROFILE,'generic-image-resources-v1','egret-custom-resource-plist-v1'])
    pick = p.add_mutually_exclusive_group()
    pick.add_argument('--asset-index', type=int, action='append')
    pick.add_argument('--all-assets', action='store_true', help='Explicitly select every bundle entry (project default)')
    p.add_argument('--dependency-source', action='append', default=[])
    p.add_argument('--evidence-source', action='append', default=[])
    p.add_argument('--bindings')
    p.add_argument('--animation', action='append')
    p.add_argument('--native', action='store_true', help='After fresh package conversion, execute sequential bounded native imports')
    p.add_argument('--native-out', help='Fresh separate native workspace; default OUTPUT-native')
    p.add_argument('--unity-editor', help='Exact installed Unity executable for --native')
    p.add_argument('--creator-editor', help='Exact installed CocosCreator executable for --native')
    p.add_argument('--native-budget-seconds', type=int, default=1200, help='Method budget per Editor, 1..1200; each window is at most 30 minutes')
    p.add_argument('--remote-manifest', help='Explicit URL/path/SHA/byte downloads; Cocos requires --input-set, Unity accepts an explicit source container')
    p.add_argument('--remote-cache-root', help='Read-only root for paths in the remote manifest')
    p.add_argument('--acquisition-out', help='Fresh acquired-files workspace; default OUTPUT-acquired')
    p.add_argument('--remote-budget-seconds', type=int, default=900, help='Acquisition budget, 30..3600 seconds')
    p = sub.add_parser('acquire-unity-textures',help='Capture exact serialized ASTC keys under a literal original DATA_CDN')
    for name in ('inspection','cache-manifest','cdn-source','cdn-root','out'):p.add_argument('--'+name,required=True)
    p.add_argument('--cache-root');p.add_argument('--budget-seconds',type=int,default=1200);p.add_argument('--workers',type=int,default=8);p.add_argument('--resume',action='store_true')
    p = sub.add_parser('hydrate-unity', help='Resolve explicit WeChat texture keys against a pinned local ASTC cache pool')
    p.add_argument('--source',required=True)
    p.add_argument('--texture-cache',required=True)
    p.add_argument('--provider-python',required=True)
    p.add_argument('--out',required=True)
    p.add_argument('--budget-seconds',type=int,default=120)
    p = sub.add_parser('index-unity', help='Index exact serialized files and PPtr IDs from an explicit frozen bundle list')
    p.add_argument('--manifest', required=True)
    p.add_argument('--provider-python', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--budget-seconds',type=int,default=600)
    p = sub.add_parser('unity-field-plan', help='Validate frozen field semantics and exact source/target identities; never edits Unity assets')
    for name in ('candidate','trusted','trusted-sha256','bindings','inventory','inventory-sha256','source','metadata','target-root','out'):
        p.add_argument('--'+name, required=True)
    p = sub.add_parser('unity-code-model', help='Recover named C# data fields from embedded Unity TypeTree evidence')
    p.add_argument('--inspection', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--bulk',action='store_true',help='Alias repeated MonoScript only with exact raw bytes and proven field equality')
    p = sub.add_parser('export-unity', help='Export a Unity bundle through an existing fixed AssetRipper in an isolated copy')
    p.add_argument('--source', required=True)
    p.add_argument('--asset-ripper', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--budget-seconds', type=int, default=600)
    p = sub.add_parser('inspect-unity', help='Strict typed inspection of an explicit Unity serialized file or AssetBundle')
    p.add_argument('--source', required=True)
    p.add_argument('--schema-manifest', help='Explicit frozen bundle pool; borrow only identical version/platform/script/type hashes')
    p.add_argument('--provider-python', required=True, help='Existing Python with UnityPy 1.25.3; never installed automatically')
    p.add_argument('--out', required=True)
    p.add_argument('--budget-seconds', type=int, default=120)
    p.add_argument('--bundle-manifest',help='Inspect every unique container in the explicit frozen bundle pool in one worker')
    p = sub.add_parser('format-project',help='Preview or apply a typed GREA layout into a fresh unimported Unity/Creator candidate')
    p.add_argument('--project',required=True)
    p.add_argument('--profile',choices=['grea'],default='grea')
    pick=p.add_mutually_exclusive_group(required=True)
    pick.add_argument('--preview',action='store_true')
    pick.add_argument('--plan')
    p.add_argument('--out',required=True)
    p = sub.add_parser('project-model', help='Inspect explicit target asset path slots and identity without moving files')
    p.add_argument('--candidate', required=True)
    p.add_argument('--out', required=True)
    p = sub.add_parser('code-emit', help='Emit source-proven numeric field methods as C# and default TypeScript; unknown methods stay pending')
    p.add_argument('--source',required=True)
    p.add_argument('--code-model',required=True)
    p.add_argument('--namespace',default='monkey-project')
    p.add_argument('--numeric-field',action='append',required=True,help='Explicit numeric call-subdomain contract; not a global JS type inference')
    p.add_argument('--cocos-code-language',choices=['ts','js'],default='ts')
    p.add_argument('--out',required=True)
    p = sub.add_parser('code-handoff',help='Generate source-bound named drafts from a frozen Cocos candidate; optional additive owned-copy handoff')
    p.add_argument('--candidate',required=True);p.add_argument('--out',required=True)
    p.add_argument('--expected-manifest');p.add_argument('--apply-owned',action='store_true');p.add_argument('--reuse-facts');p.add_argument('--expected-facts')
    p = sub.add_parser('code-model', help='Inspect named methods and evidenced semantic candidates without executing JavaScript')
    p.add_argument('--source', required=True)
    p.add_argument('--module-name', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--bulk',action='store_true',help='Preserve ambiguous whole-file assignments as unsupported evidence')
    p = sub.add_parser('research-matrix', help='Discover every Research game without converting or following external sources')
    p.add_argument('--root', required=True)
    p.add_argument('--out', required=True)
    p = sub.add_parser('freeze-unity-handoff',help='Freeze complete original/acquired input dispositions in a Unity-source initial')
    p.add_argument('--candidate',required=True);p.add_argument('--texture-cache',required=True);p.add_argument('--source-manifest',required=True);p.add_argument('--source-root',required=True);p.add_argument('--expected-manifest',required=True);p.add_argument('--out',required=True)
    p = sub.add_parser('freeze-handoff',help='Freeze an additive source-native identity and named-code initial handoff')
    p.add_argument('--candidate',required=True);p.add_argument('--native-contract',required=True);p.add_argument('--verification',required=True);p.add_argument('--expected-manifest',required=True);p.add_argument('--out',required=True);p.add_argument('--apply-owned',action='store_true')
    p = sub.add_parser('export-unity-bulk',help='Export all frozen prepared containers in one separately bounded AssetRipper stage')
    p.add_argument('--prepared',required=True);p.add_argument('--asset-ripper',required=True);p.add_argument('--out',required=True);p.add_argument('--budget-seconds',type=int,default=1200)
    p.add_argument('--deadline-utc',required=True);p.add_argument('--window-end-utc',required=True)
    p = sub.add_parser('prepare-unity-bulk',help='Resume exact whole-pool texture preparation independently of provider export')
    p.add_argument('--inspection',required=True);p.add_argument('--texture-cache',required=True);p.add_argument('--capture',required=True);p.add_argument('--provider-python',required=True);p.add_argument('--out',required=True)
    p.add_argument('--budget-seconds',type=int,default=1200);p.add_argument('--resume',action='store_true')
    p = sub.add_parser('native-finish-plan',help='Prepare incremental source Scene export and SHRINK evidence using existing native assets')
    p.add_argument('--candidate',required=True);p.add_argument('--out',required=True);p.add_argument('--exclude-scene',action='append',default=[])
    p = sub.add_parser('native-finish',help='Plan or execute one bounded incremental finish in an explicitly owned native project')
    p.add_argument('--candidate',required=True);p.add_argument('--preparation',required=True);p.add_argument('--out',required=True)
    p.add_argument('--editor-path',required=True);p.add_argument('--expected-manifest',required=True)
    p.add_argument('--budget-seconds',type=int,default=600);p.add_argument('--deadline-utc',required=True)
    p.add_argument('--window-end-utc',required=True);p.add_argument('--execute',action='store_true');p.add_argument('--previous-execution')
    p = sub.add_parser('native-import',help='Plan or explicitly execute a bounded Unity/Creator import in a fresh copy')
    p.add_argument('--candidate',required=True);p.add_argument('--out',required=True)
    p.add_argument('--editor-path',required=True);p.add_argument('--expected-manifest',required=True)
    p.add_argument('--budget-seconds',type=int,default=600);p.add_argument('--deadline-utc',required=True)
    p.add_argument('--window-end-utc',required=True);p.add_argument('--execute',action='store_true')
    p = sub.add_parser('preflight',help='Check frozen candidate and classify startup logs without launching an Editor')
    p.add_argument('--candidate',required=True);p.add_argument('--out',required=True);p.add_argument('--log');p.add_argument('--progress')
    p = sub.add_parser('inspect')
    p.add_argument('--source', required=True)
    p.add_argument('--source-profile', choices=[PROFILE,PROJECT_PROFILE], required=True)
    p.add_argument('--evidence-source',action='append',default=[])
    p.add_argument('--dependency-source',action='append',default=[])
    p.add_argument('--asset-index', type=int, action='append', required=True)
    p.add_argument('--out', required=True)
    p = sub.add_parser('catalog')
    p.add_argument('--source',required=True)
    p.add_argument('--source-profile',choices=[PROJECT_PROFILE],required=True)
    p.add_argument('--out',required=True)
    p = sub.add_parser('normalize')
    p.add_argument('--manifest', required=True)
    p.add_argument('--out', required=True)
    p = sub.add_parser('plan')
    p.add_argument('--ir',required=True)
    p.add_argument('--namespace',required=True)
    p.add_argument('--bindings')
    p.add_argument('--animation',action='append',help='Select a source AnimationClip ID; default all normalized clips')
    p.add_argument('--target-profile',choices=[UNITY_PROFILE,cocos.PROFILE],required=True)
    p.add_argument('--out',required=True)
    p = sub.add_parser('export')
    p.add_argument('--plan',required=True)
    p.add_argument('--out',required=True)
    p = sub.add_parser('verify')
    p.add_argument('--candidate',required=True)
    p.add_argument('--level',choices=['static','editor'],default='static')
    p.add_argument('--out',required=True)
    p = sub.add_parser('handoff')
    p.add_argument('--candidate',required=True)
    p.add_argument('--out',required=True)
    p.add_argument('--native-contract',action='store_true',help='Read existing Sprite importer, actual fileID and Prefab reference evidence')
    p = sub.add_parser('diff')
    p.add_argument('--before',required=True);p.add_argument('--after',required=True);p.add_argument('--out',required=True)
    p = sub.add_parser('register')
    p.add_argument('--candidate',required=True);p.add_argument('--out',required=True)
    p = sub.add_parser('apply')
    p.add_argument('--target',required=True);p.add_argument('--candidate',required=True)
    p.add_argument('--expected-manifest',required=True);p.add_argument('--out',required=True)
    p.add_argument('--write',action='store_true');p.add_argument('--preview')
    args = parser.parse_args(argv)
    try:
        if args.command == 'capabilities':
            print(json.dumps(dict(version=__version__, profiles=[PROFILE,PROJECT_PROFILE,'cocos-2.4.11-bundle','cocos-3.8.7-bundle','cocos-3.4.1-bundle','cocos-2.1.2-resource','generic-image-resources-v1','egret-custom-resource-plist-v1'], targetProfiles=[UNITY_PROFILE,cocos.PROFILE],
                additionalPackageProfiles={'cocos-3.4.1-bundle':dict(scope='version-proven-node-ui-prefab-and-resource-subset',graphs='856-of-857-source-graphs;22503-nodes;52-instances;one-null-quaternion-rejected',native='5-source-frames-plus-6-prefabs-331-nodes-8-instances-7-mounted-nodes-1-mounted-widget-both-targets-verified',operations=['package-convert']), 'egret-custom-resource-plist-v1':dict(scope='reviewed-custom-resource-manifest-plist-binjson-v2',targets=['unity6'],sourceSkins='typed-data-only-native-layout-pending',remoteAcquisition='explicit-manifest-cache-and-bounded-fetch',native='132-source-frames-verified; expanded-atlas-set-pending',operations=['package-convert']), 'cocos-2.1.2-resource':dict(scope='version-proven-resource-subset',native='211-source-frames-both-targets-verified',graphs='pending',operations=['package-convert']), 'generic-image-resources-v1':dict(scope='derived-original-image-gallery-only',families=['laya','layaair','egret','eraget','custom','other'],targets=['unity6'],native='Egret-16-derived-images-verified',sourceGraphs='not-restored',operations=['package-convert']), 'cocos-2.4.11-bundle':dict(scope='version-proven-published-bundle-subset',native='91-source-graphs-both-targets-verified',operations=['package-convert']), 'cocos-3.8.7-bundle':dict(scope='version-proven-node-ui-template-and-resource-subset',native='83-static-graphs-plus-4-prefab-5-native-relations-and-16-node-dynamic-ui-representatives-both-targets-verified',graphs='114-root-closures-static;5-graphs-missing-6-exact-templates;not-all-native-validated',operations=['package-convert'])},
                schemaVersion=1, dynamicUi=dict(probeVersion=2,verifiedLayoutGroups=6,verifiedLayoutStates=54,native='bounded-grid-scale-constraints-child-resize-and-linear-scale-representatives',timing='Editor-native-forced-update;Player-not_run'), formatting=dict(implemented=['unity-creator-unimported-owned-grea-v1','fresh-package-convert-none-grea'],pending=['unity-general-scene-native-format','unity-source-positive-native-move-sample'],rejected=['materialized-native-assets-require-a-future-native-move-adapter']), unitySourceProfile=dict(name='unityfs-unitypy-1.25.3-assetripper-2.0.0',status='partial',inputs='explicit-unity-bundle-or-webdata-files-and-exact-local-texture-cache',additionalContainers=['UnityWebData1.0'],invalidTexturePolicy='block-default-explicit-quarantine-retains-original',dependencyClosure='explicit-frozen-pool-exact-serialized-file-closure',editor='one-prefab-schema-reference-save-reload-verified',publicNative=True,nativeProfile='unity-leaf-prefab-sprite-array-v1',nativeFormatting='typed-resource-moves-with-dynamic-path-pins; real sample pinned all 134 assets',methodsRecovered=0), implemented=['unity-field-plan','convert','catalog','inspect','normalize','plan','export','verify','handoff','diff','register','apply','preflight','native-import','research-matrix','code-model','code-emit','format-project','project-model','inspect-unity','export-unity','unity-code-model','index-unity','hydrate-unity','code-handoff','native-finish-plan','native-finish','acquire-unity-textures','prepare-unity-bulk','export-unity-bulk','freeze-handoff','freeze-unity-handoff'], planned=[],
                targetValidation={UNITY_PROFILE:dict(static='implemented',editor='representative-subset-verified',visual='not_run'),cocos.PROFILE:dict(static='implemented',editor='representative-subset-verified',visual='not_run')},
                compiledFormats=['compiled-v1','pack-v1','texture-pack-v1'],
                containerFormats=['plain-wxapkg','APK-ZIP','Cocos-resource-directory'],
                packageWorkflow=dict(fileAccounting='implemented',staticModuleRecovery='partial',codeDrafts='source-linked-contracts',
                                     nativeObjectRecovery='shared-ir-supported-subset',packageResume='hash-checked',inputSets='explicit-local-roots',editorOrchestration='manifest-bound-native-import-command',remoteAcquisition='explicit-manifest-bounded-fetch',cocosCodeLanguages=['ts','js'],defaultCocosCodeLanguage='ts',numericCodeContracts=['numeric-call-subdomain-v1','static-number-methods-v1'],staticNumericScope='reviewed-Creator3-descriptor-helper-and-lexical-dependency; no component binding'),
                imageFormats=['PNG','JPEG','ASTC (optional pinned decoder)'],animationSchemaVersion=1,
                animationSubset=['local-position','local-scale','opacity','linear','constant-step','Normal','Loop'],animationEvents='manual-contract-only', targetEditorValidation='representative-subsets-only'), ensure_ascii=False))
            return 0
        if args.command == 'code-emit':
            from .code_emit import emit
            result=emit(args.source,args.code_model,args.out,args.numeric_field,args.cocos_code_language,args.namespace)
            print(json.dumps(result,ensure_ascii=False));return 1
        if args.command == 'acquire-unity-textures':
            from .unity_texture_acquisition import acquire
            result=acquire(args.inspection,args.cache_manifest,args.cdn_source,args.cdn_root,args.out,args.cache_root,args.budget_seconds,args.workers,args.resume)
            print(json.dumps(result,ensure_ascii=False));return 0 if result['status']=='captured'else 1
        if args.command == 'hydrate-unity':
            from .unity_textures import hydrate
            result=hydrate(args.source,args.texture_cache,args.provider_python,args.out,args.budget_seconds)
            print(json.dumps(result,ensure_ascii=False))
            return 0 if result['status']=='hydrated' else 1
        if args.command == 'index-unity':
            from .unity_index import catalog as index_unity
            result=index_unity(args.manifest,args.provider_python,args.out,args.budget_seconds)
            print(json.dumps(result,ensure_ascii=False))
            return 0 if result['status']=='indexed' else 1
        if args.command == 'unity-field-plan':
            from .unity_field_plan import plan as unity_field_plan
            result = unity_field_plan(args.candidate,args.trusted,args.trusted_sha256,args.bindings,args.inventory,
                                      args.inventory_sha256,args.source,args.metadata,args.target_root,args.out)
            print(json.dumps(result,ensure_ascii=False))
            return 0 if result['writable'] else 1
        if args.command == 'unity-code-model':
            from .unity_code_model import model as unity_code_model
            print(json.dumps(unity_code_model(args.inspection,args.out,args.bulk),ensure_ascii=False))
            return 1
        if args.command == 'export-unity':
            from .providers.assetripper import export as export_unity
            result=export_unity(args.source,args.asset_ripper,args.out,args.budget_seconds)
            print(json.dumps(result,ensure_ascii=False))
            return 1
        if args.command == 'inspect-unity':
            from .sources.unity_serialized import inspect as inspect_unity
            if args.bundle_manifest:
                from .unity_batch import inspect_set
                result=inspect_set(args.source,args.bundle_manifest,args.provider_python,args.out,args.budget_seconds,args.schema_manifest)
            else:
                result = inspect_unity(args.source,args.provider_python,args.out,args.budget_seconds,schema_manifest=args.schema_manifest)
            print(json.dumps(result,ensure_ascii=False))
            return 0 if result['status']=='inspected' else 1
        if args.command == 'format-project':
            from .formatting import preview as format_preview,apply as format_apply
            result=format_preview(args.project,args.out)if args.preview else format_apply(args.project,args.plan,args.out)
            print(json.dumps(result,ensure_ascii=False));return 0 if args.preview else 1
        if args.command == 'project-model':
            from .project_model import inspect as project_model
            print(json.dumps(project_model(args.candidate,args.out),ensure_ascii=False))
            return 0
        if args.command == 'freeze-unity-handoff':
            from .unity_bulk_freeze import freeze as freeze_unity
            print(json.dumps(freeze_unity(args.candidate,args.texture_cache,args.source_manifest,args.source_root,args.out,args.expected_manifest),ensure_ascii=False));return 0
        if args.command == 'freeze-handoff':
            from .bulk_handoff import freeze
            print(json.dumps(freeze(args.candidate,args.native_contract,args.verification,args.out,args.expected_manifest,args.apply_owned),ensure_ascii=False));return 0
        if args.command == 'export-unity-bulk':
            from .unity_bulk_prepare import export_prepared
            result=export_prepared(args.prepared,args.asset_ripper,args.out,args.budget_seconds,args.deadline_utc,args.window_end_utc)
            print(json.dumps({k:result.get(k)for k in ('status','stage','pid','processExited','exitCode','outputFiles','outputBytes','nativeAssetFiles','sourceUnchanged','error')},ensure_ascii=False));return 0 if result['status']=='exported_partial'else 1
        if args.command == 'prepare-unity-bulk':
            from .unity_bulk_prepare import prepare as prepare_bulk
            result=prepare_bulk(args.inspection,args.texture_cache,args.capture,args.provider_python,args.out,args.budget_seconds,args.resume)
            print(json.dumps(result,ensure_ascii=False));return 0 if result['status']=='prepared'else 1
        if args.command == 'native-finish':
            from .cocos_native_finish import execute as native_finish
            result=native_finish(args.candidate,args.preparation,args.out,args.editor_path,args.expected_manifest,args.budget_seconds,args.deadline_utc,args.window_end_utc,args.execute,args.previous_execution)
            print(json.dumps(result,ensure_ascii=False));return 0 if result['status']in ('planned','completed')else 1
        if args.command == 'native-finish-plan':
            from .cocos_native_finish import prepare
            print(json.dumps(prepare(args.candidate,args.out,args.exclude_scene),ensure_ascii=False));return 0
        if args.command == 'handoff' and args.native_contract:
            from .cocos_native_contract import export as native_contract
            print(json.dumps(native_contract(args.candidate,args.out),ensure_ascii=False));return 0
        if args.command == 'code-handoff':
            from .cocos_code_handoff import enrich
            print(json.dumps(enrich(args.candidate,args.out,args.expected_manifest,args.apply_owned,args.reuse_facts,args.expected_facts),ensure_ascii=False))
            return 1
        if args.command == 'code-model':
            from .code_model import inspect as code_model
            print(json.dumps(code_model(args.source,args.out,args.module_name,bulk=args.bulk),ensure_ascii=False))
            return 1
        if args.command == 'research-matrix':
            from .research_cases import discover
            print(json.dumps(discover(args.root,args.out),ensure_ascii=False))
            return 0
        if args.command == 'convert':
            if args.numeric_code_contract and any((args.resume,args.recipe,args.reuse_source_stages,args.asset_index,args.bindings,args.animation)):
                parser.error('--numeric-code-contract requires fresh package source stages')
            if args.cocos_code_language!='ts' and not args.numeric_code_contract:parser.error('--cocos-code-language requires --numeric-code-contract')
            if args.format is not None and (args.resume or args.recipe):parser.error('--format requires a fresh package conversion; resume/recipe retain their declared contract')
            generic_selection=None
            generic_family=args.source_family if args.source_family in ('laya','layaair','egret','eraget','custom','other')else None
            if args.source_family=='auto' and args.source_profile in ('generic-image-resources-v1','egret-custom-resource-plist-v1'):
                generic_family='egret'if args.source_profile=='egret-custom-resource-plist-v1'else'other'
            if args.input_set and args.source_family=='auto':
                from .inputs import input_set
                generic_selection=input_set(args.input_set)
                if generic_selection['sourceProfile']=='generic-image-resources-v1':generic_family='other'
                elif generic_selection['sourceProfile']=='egret-custom-resource-plist-v1':generic_family='egret'
            if generic_family:
                if args.target not in ('unity','unity6',UNITY_PROFILE):parser.error('Non-Cocos sources target Unity 6 only')
                if not all((args.source or args.input_set,args.target,args.out))or args.source and args.input_set:parser.error('Image-resource conversion requires --source or --input-set, --target unity6 and --out')
                if args.source_profile and args.source_profile not in ('generic-image-resources-v1','egret-custom-resource-plist-v1'):parser.error('Resource sources require a supported explicit resource profile')
                if any((args.resume,args.recipe,args.reuse_source_stages,args.numeric_code_contract,args.provider_python,args.asset_ripper,args.unity_texture_cache,args.unity_schema_manifest,args.unity_dependency_manifest,args.unity_quarantine_invalid_textures,args.asset_index,args.all_assets,args.bindings,args.animation,args.dependency_source,args.evidence_source,args.cocos_code_language!='ts',args.provider_budget_seconds!=600)):
                    parser.error('Initial generic image profile supports explicit local roots; source adapters, remote manifests and source code binding are pending')
                if not args.remote_manifest and any((args.remote_cache_root,args.acquisition_out,args.remote_budget_seconds!=900)):parser.error('Remote options require --remote-manifest')
                acquired=None;remote_settings=None;conversion_input_set=args.input_set
                if args.remote_manifest:
                    if not args.input_set:parser.error('Egret remote acquisition requires an explicit --input-set')
                    from .inputs import input_set
                    generic_selection=generic_selection or input_set(args.input_set)
                    if generic_selection['sourceProfile']!='egret-custom-resource-plist-v1':parser.error('Generic family image acquisition is pending; remote resource roots require the reviewed Egret profile')
                    from .acquisition import prepare
                    acquisition_out=Path(args.acquisition_out).resolve()if args.acquisition_out else Path(args.out).resolve().with_name(Path(args.out).resolve().name+'-acquired')
                    remote_settings=prepare(args.remote_manifest,acquisition_out,generic_selection,args.remote_cache_root,args.remote_budget_seconds,[Path(args.out).resolve()])
                if args.native and args.offline:parser.error('--native cannot combine with --offline')
                if not args.native and any((args.native_out,args.unity_editor,args.creator_editor,args.native_budget_seconds!=1200)):parser.error('native options require --native')
                settings=None
                if args.native:
                    from .orchestration import options
                    from .inputs import input_set
                    generic_selection=generic_selection or (input_set(args.input_set)if args.input_set else None)
                    roots=[r['path']for r in generic_selection['inputs']]if generic_selection else [args.source]
                    if remote_settings:roots.append(acquisition_out)
                    settings=options(args.out,args.target,args.native_out,args.unity_editor,args.creator_editor,args.native_budget_seconds,roots)
                if remote_settings:
                    from .acquisition import acquire
                    acquired=acquire(remote_settings,args.offline);conversion_input_set=str(acquired['inputSet'])
                from .resource_package import convert as convert_images
                result=convert_images(args.source,args.target,args.out,args.namespace or 'monkey-project',args.offline,conversion_input_set,args.format or 'none',generic_family,args.source_profile)
                if acquired:
                    from .acquisition import attach
                    attach(result,args.out,acquired)
                summary=dict(status=result['workflowStatus'],completed=result['completed'],resultKind=result['resultKind'],sourceFamily=result['sourceFamily'],sourceProfile=result['sourceProfile'],completionScope=result['completionScope'],sourceSpriteFrames=result['sourceSpriteFrames'],derivedFullImageFrames=result.get('derivedFullImageFrames',0),sourceData=result.get('sourceData'),projects=result['projects'],diagnostics=result['diagnostics'],report=str(Path(args.out).resolve()/'conversion-result.json'))
                if settings:
                    from .orchestration import run
                    summary['nativeExecution']=run(result,settings)
                print(json.dumps(summary,ensure_ascii=False));return 1
            source_file=Path(args.source) if args.source else None
            unity_source=args.source_family=='unity'
            if args.source_family=='auto' and source_file and source_file.is_file():
                from .io import safe as safe_source
                from .sources.unity_serialized import container_kind
                with safe_source(source_file).open('rb') as stream:unity_source=container_kind(stream.read(16)) is not None
            if unity_source:
                if args.numeric_code_contract or args.cocos_code_language!='ts':parser.error('Numeric JS code contracts/language selection require Cocos package sources')
                if args.format=='grea' and not args.native:parser.error('Unity source --format grea requires --native for typed AssetDatabase moves')
                if args.native and args.offline:parser.error('--native cannot combine with --offline')
                if args.native and (not args.unity_editor or args.creator_editor):parser.error('Unity source --native requires only --unity-editor')
                if not args.native and any((args.native_out,args.unity_editor,args.creator_editor,args.native_budget_seconds!=1200)):parser.error('native options require --native')
                if args.target not in ('unity','unity6',UNITY_PROFILE):parser.error('Unity sources target Unity 6 only')
                if not all((args.source,args.out,args.provider_python,args.asset_ripper)):parser.error('Unity source requires --source --out --provider-python --asset-ripper')
                if any((args.input_set,args.resume,args.recipe,args.reuse_source_stages,args.asset_index,args.all_assets,args.bindings,args.animation,args.evidence_source,args.source_profile,args.namespace)):
                    parser.error('Unity source profile accepts explicit bundle/dependency/texture inputs; input sets/slice options are not implemented')
                if not args.remote_manifest and any((args.remote_cache_root,args.acquisition_out,args.remote_budget_seconds!=900)):parser.error('remote options require --remote-manifest')
                if args.unity_dependency_manifest and args.dependency_source:parser.error('Choose --unity-dependency-manifest or explicit --dependency-source')
                native_settings=None;remote_settings=None;acquired=None
                protected=[]
                if args.native or args.remote_manifest:
                    from .unity_acquisition import protected_inputs
                    protected=protected_inputs(args.source,args.dependency_source,args.unity_texture_cache,args.unity_schema_manifest,args.unity_dependency_manifest,args.provider_python,args.asset_ripper)
                if args.remote_manifest:
                    from .unity_acquisition import prepare
                    from .io import safe
                    if safe(args.out).exists():parser.error('Choose a fresh conversion output before acquisition')
                    acquisition_out=safe(args.acquisition_out or str(args.out)+'-acquired')
                    remote_settings=prepare(args.source,acquisition_out,args.remote_manifest,args.remote_cache_root,args.remote_budget_seconds,[*protected,safe(args.out)])
                    protected.extend([acquisition_out,remote_settings['manifest']])
                    if remote_settings['cache']:protected.append(remote_settings['cache'])
                if args.native:
                    from .orchestration import options
                    native_settings=options(args.out,args.target,args.native_out,args.unity_editor,args.creator_editor,args.native_budget_seconds,protected)
                inputs=dict(dependencies=args.dependency_source,texture_cache=args.unity_texture_cache,dependency_manifest=args.unity_dependency_manifest)
                if remote_settings:
                    from .acquisition import acquire
                    from .unity_acquisition import merge
                    acquired=acquire(remote_settings,args.offline)
                    inputs=merge(acquired,**{k:inputs[k]for k in ('texture_cache','dependency_manifest','dependencies')})
                from .recover_unity import convert as convert_unity
                result=convert_unity(args.source,args.out,args.provider_python,args.asset_ripper,args.provider_budget_seconds,schema_manifest=args.unity_schema_manifest,quarantine_invalid_textures=args.unity_quarantine_invalid_textures,export_scope=args.unity_export_scope,code_evidence=args.unity_code_evidence,reuse_inspection=args.unity_reuse_inspection,prepared_textures=args.unity_prepared_textures,reuse_export=args.unity_reuse_provider_export,**inputs)
                if acquired:
                    from .unity_acquisition import attach
                    attach(result,args.out,acquired)
                if native_settings:
                    from .unity_native import finish_conversion
                    result=finish_conversion(result,native_settings,args.format or 'none')
                print(json.dumps(dict(status=result['status'],completed=result['completed'],resultKind=result['resultKind'],sourceFamily='unity',projects=result['projects'],diagnostics=[{k:d.get(k)for k in ('code','references','message')}for d in result['diagnostics']],nativeExecution=result.get('nativeExecution'),remoteAcquisition=result.get('acquisition'),format=result['format'],report=str(Path(args.out).resolve()/'conversion-result.json')),ensure_ascii=False))
                return 1
            if args.unity_export_scope!='reachable' or args.unity_code_evidence or args.unity_reuse_inspection or args.unity_prepared_textures or args.unity_reuse_provider_export:parser.error('Unity bulk export/code evidence require a Unity source')
            if args.provider_python or args.asset_ripper or args.unity_texture_cache or args.unity_schema_manifest or args.unity_dependency_manifest or args.unity_quarantine_invalid_textures or args.provider_budget_seconds!=600:parser.error('Unity provider options require a Unity source')
            from .convert import convert, resume, recipe
            if not args.remote_manifest and any((args.remote_cache_root,args.acquisition_out,args.remote_budget_seconds!=900)):
                parser.error('remote options require --remote-manifest')
            if args.remote_manifest and (not args.input_set or args.resume):
                parser.error('--remote-manifest requires a fresh conversion with explicit --input-set')
            if not args.native and any((args.native_out,args.unity_editor,args.creator_editor,args.native_budget_seconds!=1200)):
                parser.error('native options require --native')
            if args.native and (args.offline or args.resume or args.recipe):
                parser.error('--native requires a fresh package conversion and cannot combine with --offline/--resume/--recipe')
            if args.reuse_source_stages and not args.input_set:parser.error('--reuse-source-stages requires --input-set and fresh --out')
            if args.resume and args.input_set:
                if any((args.source,args.target,args.out,args.recipe,args.asset_index,args.all_assets,args.bindings,
                        args.dependency_source,args.evidence_source,args.animation,args.source_profile,args.namespace,args.package,args.reuse_source_stages)):
                    parser.error('package resume accepts --resume, --input-set and optional --offline only')
                from .package import resume_package
                result=resume_package(args.resume,args.input_set,args.offline)
                print(json.dumps(dict(status=result['workflowStatus'],resultKind=result['resultKind'],completed=result['completed'],
                                      projects=result['projects'],report=str(Path(args.resume).resolve()/'conversion-result.json')),ensure_ascii=False))
                return 1
            source_path=Path(args.source) if args.source else None
            package_mode=args.input_set or args.package or args.target in ('both','unity6','cocos38') or (source_path is not None and
                (source_path.suffix.lower() in ('.apk','.wxapkg') or source_path.is_dir() and not args.asset_index and not args.recipe))
            if args.numeric_code_contract and not package_mode:parser.error('--numeric-code-contract requires package conversion')
            if package_mode:
                if not all((args.source or args.input_set,args.target,args.out)) or args.source and args.input_set or any((args.resume,args.recipe,args.asset_index,
                        args.dependency_source,args.evidence_source,args.bindings,args.animation,args.source_profile)):
                    parser.error('package conversion requires --source/--target/--out; slice options are unsupported')
                from .package import convert_package
                selection=None
                if args.input_set and (args.native or args.remote_manifest):
                    from .inputs import input_set
                    selection=input_set(args.input_set)
                acquired=None;remote_settings=None
                acquisition_out=Path(args.acquisition_out).resolve() if args.acquisition_out else Path(args.out).resolve().with_name(Path(args.out).resolve().name+'-acquired')
                if args.remote_manifest:
                    from .acquisition import prepare
                    remote_settings=prepare(args.remote_manifest,acquisition_out,selection,args.remote_cache_root,args.remote_budget_seconds,[Path(args.out).resolve()])
                native_settings=None
                if args.native:
                    from .orchestration import options
                    if args.input_set:
                        source_roots=[r['path'] for r in selection['inputs']]
                    else:source_roots=[args.source]
                    if remote_settings:source_roots.append(acquisition_out)
                    native_settings=options(args.out,args.target,args.native_out,args.unity_editor,args.creator_editor,args.native_budget_seconds,source_roots)
                conversion_input_set=args.input_set
                if remote_settings:
                    from .acquisition import acquire
                    acquired=acquire(remote_settings,args.offline);conversion_input_set=str(acquired['inputSet'])
                    if args.reuse_source_stages and Path(conversion_input_set).resolve()!=Path(args.input_set).resolve():
                        raise ValueError('New acquired files require fresh source stages; acquired evidence is preserved')
                result=convert_package(args.source,args.target,args.out,args.namespace or 'monkey-project',args.offline,conversion_input_set,reuse_source_stages=args.reuse_source_stages,format_profile=args.format or 'none',code_contract=args.numeric_code_contract,cocos_code_language=args.cocos_code_language)
                if acquired:
                    from .acquisition import attach
                    attach(result,args.out,acquired)
                summary=dict(status=result['workflowStatus'],resultKind=result['resultKind'],
                     completed=result['completed'],projects=result['projects'],format=result.get('format'),inputFiles=result['inputFiles'],
                     inputBytes=result['inputBytes'],diagnostics=len(result['diagnostics']),nextAction=result['nextAction'],
                     report=str(Path(args.out).resolve()/'conversion-result.json'))
                if acquired:summary['remoteAcquisition']=dict(acquired['summary'],receipt=str(acquired['receipt']))
                if native_settings:
                    from .orchestration import run
                    summary['nativeExecution']=run(result,native_settings)
                    if summary['nativeExecution']['status']!='not_run':
                        summary['nextAction']=dict(code='REVIEW_NATIVE_AND_SOURCE_GAPS',message='Review native receipt; source/visual/business gaps remain separate')
                print(json.dumps(summary,ensure_ascii=False))
                return 1
            if args.format=='grea':parser.error('--format grea requires a fresh package conversion')
            if args.native:parser.error('--native requires package conversion (use --target unity6/cocos38/both or --package)')
            if args.resume:
                if any((args.source,args.target,args.out,args.source_profile,args.asset_index,args.all_assets,
                        args.dependency_source,args.evidence_source,args.bindings,args.animation,args.offline,args.recipe,args.namespace)):
                    parser.error('--resume cannot be combined with conversion inputs')
                result = resume(args.resume)
            elif args.recipe:
                if not args.out or any((args.source,args.target,args.source_profile,args.asset_index,args.all_assets,
                                        args.dependency_source,args.evidence_source,args.bindings,args.animation,args.namespace)):
                    parser.error('--recipe requires --out and cannot be combined with explicit input options')
                result = convert(output=args.out,offline=args.offline,**recipe(args.recipe))
            else:
                if not all((args.source,args.target,args.out)):
                    parser.error('convert requires --source, --target and --out (or --resume)')
                result = convert(args.source,args.target,args.out,args.namespace or 'monkey-project',args.source_profile,
                             args.asset_index,args.all_assets,args.dependency_source,args.evidence_source,
                             args.bindings,args.animation,args.offline)
            print(json.dumps(dict(status=result['workflowStatus'], resultKind=result['resultKind'], completed=result['completed'], project=result['project'],
                                  diagnostics=len(result['diagnostics']), validation=result['validation'],
                                  nextAction=result['nextAction'],report=result.get('report') or str(Path(args.out).resolve()/'manifest.json')), ensure_ascii=False))
            return 2 if result['workflowStatus']=='failed' else 1
        if args.command == 'inspect':
            if args.source_profile == PROJECT_PROFILE:
                if args.dependency_source or args.evidence_source: parser.error('Editable project does not accept bundle dependencies')
                result=inspect_project(args.source,args.asset_index,args.out)
            else:
                result = inspect(args.source, args.asset_index, args.out,args.dependency_source,args.evidence_source)
        elif args.command == 'catalog':
            result=catalog(args.source,args.out)
        elif args.command == 'normalize':
            result = normalize(args.manifest, args.out)
        elif args.command == 'plan':
            result = (cocos.plan if args.target_profile==cocos.PROFILE else plan)(args.ir,args.namespace,args.out,args.bindings,args.animation)
        elif args.command == 'diff':
            result=incremental.diff(args.before,args.after,args.out)
        elif args.command == 'apply':
            result=incremental.apply(args.target,args.candidate,args.expected_manifest,args.out,Path.cwd(),args.write,args.preview)
        elif args.command == 'register':
            from .io import new_output, write_json, finish
            record=incremental.register(args.candidate,Path.cwd())
            out=new_output(args.out,[Path(args.candidate).resolve()]);write_json(out/'registration.json',record)
            result=finish(out,dict(schemaVersion=1,diagnostics=[],registration=record))
        elif args.command == 'export':
            from .io import read, load
            profile=load(read(args.plan)).get('targetProfile')
            result = (cocos.export if profile==cocos.PROFILE else export)(args.plan,args.out)
            output_path=Path(args.out).resolve()
            if output_path.is_relative_to(Path.cwd()/'outputs'):
                incremental.register(output_path,Path.cwd())
        elif args.command == 'native-import':
            from .native import native_import
            result=native_import(args.candidate,args.out,args.editor_path,args.expected_manifest,args.budget_seconds,args.deadline_utc,args.window_end_utc,args.execute)
            print(json.dumps({k:result.get(k) for k in ('status','processStarted','processExited','pid','reason','report')},ensure_ascii=False))
            return 0 if result['status'] in ('planned','candidate') else 1
        elif args.command == 'preflight':
            from .preflight import preflight
            result=preflight(args.candidate,args.out,args.log,args.progress)
        elif args.command == 'verify':
            from .io import safe, read, load
            from .io import stage_manifest
            profile=stage_manifest(safe(args.candidate)).get('targetProfile')
            result = (cocos.verify if profile==cocos.PROFILE else verify)(args.candidate,args.out,args.level)
        else:
            result = handoff(args.candidate,args.out)
        print(json.dumps(dict(status=result['status'], assets=result.get('counts',{}).get('assets',len(result.get('assets',[]))),
                              spriteFrames=result.get('counts',{}).get('spriteFrames',len(result.get('spriteFrames',[]))),
                              diagnostics=len(result['diagnostics']), report=str(args.out)+'/manifest.json'), ensure_ascii=False))
        return 1 if result['status'] == 'partial' else 0
    except (ParseError, OSError, ValueError, KeyError, TypeError, IndexError, RecursionError) as error:
        print(json.dumps(dict(status='error', code=getattr(error,'code','INPUT_ERROR'), message=str(error)), ensure_ascii=False), file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
