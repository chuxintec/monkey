"""Complete-source lexical evidence, separate from executable code recovery."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from .io import safe,read,load,sha,write_json,new_output,finish
from .sources.compiled import fail


def facts(source,expected_sha256=None,selected=()):
    source=safe(source);raw=read(source)
    if expected_sha256 is not None and sha(raw)!=expected_sha256:fail('CODE_GRAPH_SOURCE_IDENTITY',str(source),'Exact source SHA256 required')
    node=shutil.which('node')
    if not node:fail('DEPENDENCY_MISSING','Node','Pinned static Acorn parser requires the installed Node runtime')
    env={k:v for k,v in os.environ.items()if k not in ('NODE_OPTIONS','NODE_PATH')}
    with tempfile.TemporaryDirectory(prefix='monkey-code-graph-')as temp:
        args=[node,'--max-old-space-size=768',str(Path(__file__).with_name('code-graph.cjs'))]
        if selected:
            request=Path(temp)/'selected.json';write_json(request,list(selected));args+=['methods',str(request)]
        with source.open('rb')as stream:
            try:r=subprocess.run(args,stdin=stream,capture_output=True,timeout=120,env=env)
            except subprocess.TimeoutExpired:fail('CODE_GRAPH_TIME_BUDGET',str(source),'Static graph exceeded 120 seconds; source was not executed')
    if r.returncode:
        # Never reproduce source text or environment from parser stderr.
        fail('CODE_GRAPH_PARSE_FAILED',str(source),'Static graph failed within the fixed parser/heap/node budgets')
    if len(r.stdout)>128*1024*1024:fail('CODE_GRAPH_OUTPUT_BUDGET',str(source),'Use a bounded source slice; graph exceeds128MiB')
    report=load(r.stdout,max_nodes=8_000_000)
    if report.get('source')!={'sha256':sha(raw),'bytes':len(raw)}or report.get('sourceExecuted')is not False:
        fail('CODE_GRAPH_SOURCE_IDENTITY',str(source),'Worker evidence differs from input')
    for row in [*report['methods'],*report['classes'],*report.get('methodInventory',[])]:
        span=row['sourceBytes'];a,b=span['start'],span['end']
        if type(a)is not int or type(b)is not int or not 0<=a<b<=len(raw)or sha(raw[a:b])!=row['sourceSha256']:
            fail('CODE_GRAPH_SPAN_IDENTITY',row['id'],'Original byte span/hash differs')
    if sha(read(source))!=sha(raw):fail('SOURCE_CHANGED',str(source),'Source changed while indexing')
    return report


def inspect(source,output,expected_sha256=None,selected=()):
    report=facts(source,expected_sha256,selected);out=new_output(output,[safe(source)])
    report.update(status='source_indexed; methods_not_yet_recovered',compiled='not_run',behavior='not_run',nativeBinding='not_run')
    write_json(out/'code-graph.json',report);finish(out,dict(schemaVersion=1,scopeMode='code-source-index',diagnostics=[]))
    return dict(status='source_indexed',source=report['source'],summary=report['summary'],report=str(out/'code-graph.json'),sourceExecuted=False)
