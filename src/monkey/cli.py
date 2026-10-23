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
    sub = parser.add_subparsers(dest='command', required=True)
    cap = sub.add_parser('capabilities')
    cap.add_argument('--json', action='store_true')
    p = sub.add_parser('convert', help='Convert a source project into an isolated native project candidate')
    p.add_argument('--source', help='Creator 2.4.15 project directory/project.json or bundle config.json')
    p.add_argument('--target', choices=['unity','cocos','unity6','cocos38','both',UNITY_PROFILE,cocos.PROFILE])
    p.add_argument('--package', action='store_true', help='Inventory all input files and generate self-contained recovery workspaces')
    p.add_argument('--out', '--output', help='Fresh output directory; native project is created under project/')
    p.add_argument('--resume', help='Recheck a previous conversion after native import, with identity checks')
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
                schemaVersion=1, implemented=['convert','catalog','inspect','normalize','plan','export','verify','handoff','diff','register','apply'], planned=[],
                targetValidation={UNITY_PROFILE:dict(static='implemented',editor='not_run',visual='not_run'),cocos.PROFILE:dict(static='implemented',editor='not_run',visual='not_run')},
                compiledFormats=['compiled-v1','pack-v1','texture-pack-v1'],
                containerFormats=['plain-wxapkg','APK-ZIP','Cocos-resource-directory'],
                packageWorkflow=dict(fileAccounting='implemented',staticModuleRecovery='partial',codeDrafts='source-linked-contracts',
                                     nativeObjectRecovery='partial-slice-only',editorOrchestration='not_implemented'),
                imageFormats=['PNG','JPEG','ASTC (optional pinned decoder)'],animationSchemaVersion=1,
                animationSubset=['local-position','local-scale','opacity','linear','constant-step','Normal','Loop'],animationEvents='manual-contract-only', targetEditorValidation='not_run'), ensure_ascii=False))
            return 0
        if args.command == 'convert':
            from .convert import convert, resume, recipe
            source_path=Path(args.source) if args.source else None
            package_mode=args.package or args.target in ('both','unity6','cocos38') or (source_path is not None and
                (source_path.suffix.lower() in ('.apk','.wxapkg') or source_path.is_dir() and not args.asset_index and not args.recipe))
            if package_mode:
                if not all((args.source,args.target,args.out)) or any((args.resume,args.recipe,args.asset_index,
                        args.dependency_source,args.evidence_source,args.bindings,args.animation,args.source_profile)):
                    parser.error('package conversion requires --source/--target/--out; slice options are unsupported')
                from .package import convert_package
                result=convert_package(args.source,args.target,args.out,args.namespace or 'monkey-project',args.offline)
                print(json.dumps(dict(status=result['workflowStatus'],resultKind=result['resultKind'],
                     completed=result['completed'],projects=result['projects'],inputFiles=result['inputFiles'],
                     inputBytes=result['inputBytes'],diagnostics=len(result['diagnostics']),nextAction=result['nextAction'],
                     report=str(Path(args.out).resolve()/'conversion-result.json')),ensure_ascii=False))
                return 1
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
        elif args.command == 'verify':
            from .io import safe, read, load
            profile=load(read(safe(args.candidate)/'manifest.json')).get('targetProfile')
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
