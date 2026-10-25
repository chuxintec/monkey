"""Final conversion receipt. The former --format grea stage is retired: new outputs are already monkey-project/1."""
from pathlib import Path
from .io import read,write_json,stage_manifest,sha,diagnostic
from .layout.standard import VERSION


def run(report,output,profile):
    root=Path(output)
    report['format']=dict(profile=profile,layout=VERSION,status='not_requested' if profile=='none' else 'retired',applied=False,baseExportCompleted=report.get('completed') is True)
    if profile!='none':
        report['diagnostics'].append(diagnostic('FORMAT_PROFILE_RETIRED','--format','Outputs are already '+VERSION+' (docs/PROJECT-SPEC.md); --format '+profile+' is a deprecated alias'))
    for row in report['projects']:
        project=root/row['path'];m=stage_manifest(project);m['format']=dict(profile='none',applied=False);m['projectLayout']=VERSION
        write_json(project/'manifest.json',m);row['manifestSha256']=sha(read(project/'manifest.json',max_bytes=128*1024*1024))
    write_json(root/'conversion-result.json',report);return report
