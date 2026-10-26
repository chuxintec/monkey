"""Portable installed-wheel CLI smoke; no Editor, global install, source game or CDN."""
import argparse
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--python',default=sys.executable);parser.add_argument('--out',required=True)
    args=parser.parse_args();output=Path(args.out).absolute()
    if output.exists():raise FileExistsError(output)
    python=str(Path(args.python).absolute());checks=[]
    with tempfile.TemporaryDirectory(prefix='monkey-installed-smoke-')as temp:
        work=Path(temp).resolve();env={k:v for k,v in os.environ.items()if k not in ('PYTHONPATH','PYTHONHOME')}
        def run(argv,expected=0):
            result=subprocess.run([python,'-I','-B',*argv],cwd=work,env=env,capture_output=True,text=True,timeout=30)
            checks.append(dict(arguments=argv,exitCode=result.returncode,expectedExitCode=expected))
            if result.returncode!=expected:raise RuntimeError('Installed CLI failed: '+str(argv)+' '+result.stderr[-500:])
            return result.stdout
        identity=json.loads(run(['-c','import json,monkey,sys;print(json.dumps(dict(version=monkey.__version__,module=monkey.__file__,python=sys.version.split()[0])))']))
        if 'site-packages'not in identity['module']:raise RuntimeError('Smoke requires an installed wheel outside the source checkout')
        run(['-m','monkey.cli','--version']);cap=json.loads(run(['-m','monkey.cli','capabilities','--json']))
        for command in ('acquire-resources','diagnose','doctor','space-preview','resource-probe','adopt'):
            run(['-m','monkey.cli',command,'--help'])
        run(['-c','from importlib.resources import files; p=files("monkey.targets"); assert all(p.joinpath(x).is_file() for x in ("CreatorResources.js","RecoveredSprite.shader","UnityShaderProbe.cs"))'])
        (work/'source').mkdir();(work/'source/manual.txt').write_text('retained',encoding='utf-8')
        evidence=work/'evidence.json';evidence.write_text(json.dumps(dict(files=[dict(sourceKey='explicit',path='missing.bin',status='unavailable',httpStatus=404)])),encoding='utf-8')
        run(['-m','monkey.cli','doctor','--out',str(work/'doctor')])
        run(['-m','monkey.cli','space-preview','--root',str(work/'source'),'--out',str(work/'space')])
        run(['-m','monkey.cli','diagnose','--source',str(evidence),'--out',str(work/'diagnose')],expected=1)
        diagnostics=json.loads((work/'diagnose/diagnostics.json').read_bytes())
        assert diagnostics['issues'][0]['code']=='CDN_HTTP_404'
        assert (work/'source/manual.txt').read_text()=='retained'
        report=dict(schemaVersion=1,status='pass',platform=sys.platform,machine=platform.machine(),installed=identity,
                    checks=checks,declaredTargetProfiles=cap['targetProfiles'],editorStarted=False,remoteFetched=False,globalInstall=False)
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='pass',platform=sys.platform,checks=len(checks),report=str(output))))


if __name__=='__main__':main()
