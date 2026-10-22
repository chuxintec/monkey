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


def main(argv=None):
    parser = argparse.ArgumentParser(prog='monkey')
    sub = parser.add_subparsers(dest='command', required=True)
    cap = sub.add_parser('capabilities')
    cap.add_argument('--json', action='store_true')
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
    args = parser.parse_args(argv)
    try:
        if args.command == 'capabilities':
            print(json.dumps(dict(version=__version__, profiles=[PROFILE,PROJECT_PROFILE], targetProfiles=[UNITY_PROFILE,cocos.PROFILE],
                implemented=['catalog','inspect','normalize','plan','export','verify','handoff'], planned=['diff','apply'],
                compiledFormats=['compiled-v1','pack-v1','texture-pack-v1'],
                imageFormats=['PNG','JPEG','ASTC (optional pinned decoder)'], targetEditorValidation='not_run'), ensure_ascii=False))
            return 0
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
            result = (cocos.plan if args.target_profile==cocos.PROFILE else plan)(args.ir,args.namespace,args.out,args.bindings)
        elif args.command == 'export':
            from .io import read, load
            profile=load(read(args.plan)).get('targetProfile')
            result = (cocos.export if profile==cocos.PROFILE else export)(args.plan,args.out)
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
