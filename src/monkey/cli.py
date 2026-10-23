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
    p.add_argument('--source-family', choices=['auto','cocos','unity'], default='auto')
    p.add_argument('--provider-python', help='Existing Python with UnityPy 1.25.3 for Unity source conversion')
    p.add_argument('--asset-ripper', help='Existing exact AssetRipper 2.0.0 provider executable')
    p.add_argument('--provider-budget-seconds', type=int, default=600)
    p.add_argument('--unity-texture-cache',help='Explicit local ASTC cache pool for supported Unity texture-key hydration')
    p.add_argument('--unity-schema-manifest',help='Frozen bundle pool for exact missing TypeTree lookup during Unity conversion')
    p.add_argument('--numeric-code-contract',help='Explicit source module identity and numeric-call field contract; fresh package conversion only')
    p.add_argument('--cocos-code-language',choices=['ts','js'],default='ts',help='Cocos code output; TypeScript first (package JS binding pending verification)')
    p.add_argument('--reuse-source-stages',help='Fresh package output using verified source stages; supports names-v1 metadata migration')
    p.add_argument('--input-set', help='Explicit local roots and identity/provenance manifest (schema 1)')
    p.add_argument('--target', choices=['unity','cocos','unity6','cocos38','both',UNITY_PROFILE,cocos.PROFILE])
    p.add_argument('--package', action='store_true', help='Inventory all input files and generate self-contained recovery workspaces')
    p.add_argument('--out', '--output', help='Fresh output directory; package targets use UnityProject/ and CocosProject/')
    p.add_argument('--resume', help='Resume a conversion with identity/hash checks; packages also require --input-set')
    p.add_argument('--recipe', help='Reusable JSON input/selection options; combine with --out')
    p.add_argument('--offline', action='store_true', help='Explicitly generate and verify an offline candidate only')
    p.add_argument('--namespace')
    p.add_argument('--source-profile', choices=[PROFILE,PROJECT_PROFILE])
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
    p.add_argument('--remote-manifest', help='Explicit URL/path/SHA/byte download manifest; requires --input-set')
    p.add_argument('--remote-cache-root', help='Read-only root for paths in the remote manifest')
    p.add_argument('--acquisition-out', help='Fresh acquired-files workspace; default OUTPUT-acquired')
    p.add_argument('--remote-budget-seconds', type=int, default=900, help='Acquisition budget, 30..3600 seconds')
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
    p = sub.add_parser('unity-code-model', help='Recover named C# data fields from embedded Unity TypeTree evidence')
    p.add_argument('--inspection', required=True)
    p.add_argument('--out', required=True)
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
    p = sub.add_parser('code-model', help='Inspect named methods and evidenced semantic candidates without executing JavaScript')
    p.add_argument('--source', required=True)
    p.add_argument('--module-name', required=True)
    p.add_argument('--out', required=True)
    p = sub.add_parser('research-matrix', help='Discover every Research game without converting or following external sources')
    p.add_argument('--root', required=True)
    p.add_argument('--out', required=True)
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
            print(json.dumps(dict(version=__version__, profiles=[PROFILE,PROJECT_PROFILE,'cocos-3.8.7-bundle'], targetProfiles=[UNITY_PROFILE,cocos.PROFILE],
                additionalPackageProfiles={'cocos-3.8.7-bundle':dict(scope='version-proven-published-resource-subset',native='986-source-frames-both-targets-verified',graphs='pending',operations=['package-convert'])},
                schemaVersion=1, formatting=dict(implemented=['unity-creator-unimported-owned-grea-v1','fresh-package-convert-none-grea'],pending=['direct-unity-provider-format'],rejected=['materialized-native-assets-require-a-future-native-move-adapter']), unitySourceProfile=dict(name='unityfs-unitypy-1.25.3-assetripper-2.0.0',status='partial',inputs='explicit-bundle-files-and-exact-local-texture-cache',editor='one-prefab-schema-reference-save-reload-verified',publicNative=False,methodsRecovered=0), implemented=['convert','catalog','inspect','normalize','plan','export','verify','handoff','diff','register','apply','preflight','native-import','research-matrix','code-model','code-emit','format-project','project-model','inspect-unity','export-unity','unity-code-model','index-unity','hydrate-unity'], planned=[],
                targetValidation={UNITY_PROFILE:dict(static='implemented',editor='representative-subset-verified',visual='not_run'),cocos.PROFILE:dict(static='implemented',editor='representative-subset-verified',visual='not_run')},
                compiledFormats=['compiled-v1','pack-v1','texture-pack-v1'],
                containerFormats=['plain-wxapkg','APK-ZIP','Cocos-resource-directory'],
                packageWorkflow=dict(fileAccounting='implemented',staticModuleRecovery='partial',codeDrafts='source-linked-contracts',
                                     nativeObjectRecovery='shared-ir-supported-subset',packageResume='hash-checked',inputSets='explicit-local-roots',editorOrchestration='manifest-bound-native-import-command',remoteAcquisition='explicit-manifest-bounded-fetch'),
                imageFormats=['PNG','JPEG','ASTC (optional pinned decoder)'],animationSchemaVersion=1,
                animationSubset=['local-position','local-scale','opacity','linear','constant-step','Normal','Loop'],animationEvents='manual-contract-only', targetEditorValidation='representative-subsets-only'), ensure_ascii=False))
            return 0
        if args.command == 'code-emit':
            from .code_emit import emit
            result=emit(args.source,args.code_model,args.out,args.numeric_field,args.cocos_code_language,args.namespace)
            print(json.dumps(result,ensure_ascii=False));return 1
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
        if args.command == 'unity-code-model':
            from .unity_code_model import model as unity_code_model
            print(json.dumps(unity_code_model(args.inspection,args.out),ensure_ascii=False))
            return 1
        if args.command == 'export-unity':
            from .providers.assetripper import export as export_unity
            result=export_unity(args.source,args.asset_ripper,args.out,args.budget_seconds)
            print(json.dumps(result,ensure_ascii=False))
            return 1
        if args.command == 'inspect-unity':
            from .sources.unity_serialized import inspect as inspect_unity
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
        if args.command == 'code-model':
            from .code_model import inspect as code_model
            print(json.dumps(code_model(args.source,args.out,args.module_name),ensure_ascii=False))
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
            source_file=Path(args.source) if args.source else None
            unity_source=args.source_family=='unity'
            if args.source_family=='auto' and source_file and source_file.is_file():
                from .io import safe as safe_source
                with safe_source(source_file).open('rb') as stream:unity_source=stream.read(9).startswith((b'UnityFS\0',b'UnityRaw\0',b'UnityWeb\0'))
            if unity_source:
                if args.numeric_code_contract:parser.error('Numeric JS code contracts require Cocos package sources')
                if args.format=='grea':parser.error('Direct Unity recovery profile formatting is not implemented yet; preserve a none candidate')
                if args.target not in ('unity','unity6',UNITY_PROFILE):parser.error('Unity sources target Unity 6 only')
                if not all((args.source,args.out,args.provider_python,args.asset_ripper)):parser.error('Unity source requires --source --out --provider-python --asset-ripper')
                if any((args.input_set,args.native,args.resume,args.recipe,args.reuse_source_stages,args.remote_manifest,args.remote_cache_root,args.acquisition_out,args.asset_index,args.all_assets,args.bindings,args.animation,args.evidence_source,args.source_profile,args.namespace,args.native_out,args.unity_editor,args.creator_editor,args.native_budget_seconds!=1200,args.remote_budget_seconds!=900)):
                    parser.error('Initial Unity bundle profile supports one explicit local source and offline provider export; input sets/native/remote/slice options are not implemented')
                from .recover_unity import convert as convert_unity
                result=convert_unity(args.source,args.out,args.provider_python,args.asset_ripper,args.provider_budget_seconds,dependencies=args.dependency_source,texture_cache=args.unity_texture_cache,schema_manifest=args.unity_schema_manifest)
                print(json.dumps(dict(status=result['status'],completed=result['completed'],resultKind=result['resultKind'],sourceFamily='unity',projects=result['projects'],diagnostics=result['diagnostics'],report=str(Path(args.out).resolve()/'conversion-result.json')),ensure_ascii=False))
                return 1
            if args.provider_python or args.asset_ripper or args.unity_texture_cache or args.unity_schema_manifest or args.provider_budget_seconds!=600:parser.error('Unity provider options require a Unity source')
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
