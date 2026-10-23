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
            print(json.dumps(dict(version=__version__, profiles=[PROFILE,PROJECT_PROFILE], targetProfiles=[UNITY_PROFILE,cocos.PROFILE],
                schemaVersion=1, implemented=['convert','catalog','inspect','normalize','plan','export','verify','handoff','diff','register','apply','preflight','native-import','research-matrix'], planned=[],
                targetValidation={UNITY_PROFILE:dict(static='implemented',editor='representative-subset-verified',visual='not_run'),cocos.PROFILE:dict(static='implemented',editor='representative-subset-verified',visual='not_run')},
                compiledFormats=['compiled-v1','pack-v1','texture-pack-v1'],
                containerFormats=['plain-wxapkg','APK-ZIP','Cocos-resource-directory'],
                packageWorkflow=dict(fileAccounting='implemented',staticModuleRecovery='partial',codeDrafts='source-linked-contracts',
                                     nativeObjectRecovery='shared-ir-supported-subset',packageResume='hash-checked',inputSets='explicit-local-roots',editorOrchestration='manifest-bound-native-import-command',remoteAcquisition='explicit-manifest-bounded-fetch'),
                imageFormats=['PNG','JPEG','ASTC (optional pinned decoder)'],animationSchemaVersion=1,
                animationSubset=['local-position','local-scale','opacity','linear','constant-step','Normal','Loop'],animationEvents='manual-contract-only', targetEditorValidation='representative-subsets-only'), ensure_ascii=False))
            return 0
        if args.command == 'research-matrix':
            from .research_cases import discover
            print(json.dumps(discover(args.root,args.out),ensure_ascii=False))
            return 0
        if args.command == 'convert':
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
                result=convert_package(args.source,args.target,args.out,args.namespace or 'monkey-project',args.offline,conversion_input_set,reuse_source_stages=args.reuse_source_stages)
                if acquired:
                    from .acquisition import attach
                    attach(result,args.out,acquired)
                summary=dict(status=result['workflowStatus'],resultKind=result['resultKind'],
                     completed=result['completed'],projects=result['projects'],inputFiles=result['inputFiles'],
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
        print(json.dumps(dict(status=result['status'], assets=len(result.get('assets',[])),
                              spriteFrames=len(result.get('spriteFrames',[])),
                              diagnostics=len(result['diagnostics']), report=str(args.out)+'/manifest.json'), ensure_ascii=False))
        return 1 if result['status'] == 'partial' else 0
    except (ParseError, OSError, ValueError, KeyError, TypeError, IndexError, RecursionError) as error:
        print(json.dumps(dict(status='error', code=getattr(error,'code','INPUT_ERROR'), message=str(error)), ensure_ascii=False), file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
