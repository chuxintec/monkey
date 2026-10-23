"""Optional post-export format stage; keep every unformatted project before promotion."""
from pathlib import Path
from .io import read,load,write_json,stage_manifest,sha,diagnostic
from .sources.compiled import fail


def run(report,output,profile):
    root=Path(output);rows=report['projects'];report['format']=dict(profile=profile,status='not_requested'if profile=='none'else'pending',applied=False,baseExportCompleted=report.get('completed')is True,projects=[])
    for row in rows:
        project=root/row['path'];m=stage_manifest(project);m['format']=dict(profile='none',applied=False)
        write_json(project/'manifest.json',m);row['manifestSha256']=sha(read(project/'manifest.json',max_bytes=128*1024*1024))
    write_json(root/'conversion-result.json',report)
    if profile=='none' or report.get('completed')is not True:return report
    from .formatting import preview,apply
    report['format']['status']='running';report['completed']=False;write_json(root/'conversion-result.json',report)
    stages=root/'Formatting';stages.mkdir();prepared=[]
    try:
        for row in rows:
            name=row['path']
            if name not in ('UnityProject','CocosProject'):fail('FORMAT_PROJECT_PATH',name,'Expected canonical generated project')
            stage=stages/name;stage.mkdir();source=root/name
            planned=preview(source,stage/'Preview');result=apply(source,stage/'Preview/format-plan.json',stage/'Project')
            prepared.append((row,stage/'Project',source))
            report['format']['projects'].append(dict(targetProfile=row['targetProfile'],status='prepared',preview=planned,result=result))
            write_json(root/'conversion-result.json',report)
        backup=root/'Unformatted';backup.mkdir()
        # All targets have passed formatting before any canonical project is changed.
        for row,formatted,source in prepared:
            original=backup/row['path'];source.rename(original)
            try:formatted.rename(source)
            except Exception:
                original.rename(source);raise
            row.update(unformattedPath=original.relative_to(root).as_posix(),formatProfile='grea',manifestSha256=sha(read(source/'manifest.json',max_bytes=128*1024*1024)))
            structured=report.get('structuredRecovery',{}).get('projects',{}).get(row['targetProfile'])
            if structured is not None:structured.update(layout='grea-typed-v1',formatProfile='grea')
        report['format'].update(status='applied',applied=True)
        report['completed']=True
    except Exception as error:
        report['format'].update(status='failed',error=dict(code=getattr(error,'code','FORMAT_STAGE_FAILED'),message=str(error)),unformattedExportPreserved=True)
        report.update(completed=False,status='partial',workflowStatus='needs_action',failedStage='formatting',nextAction=dict(code='FORMAT_STAGE_PENDING',message='Unformatted export is retained; inspect Formatting and resolve the concrete format error'))
        report['diagnostics'].append(diagnostic('FORMAT_STAGE_PENDING','Formatting',str(error)))
    write_json(root/'conversion-result.json',report);return report
