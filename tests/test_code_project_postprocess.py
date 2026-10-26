import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from test_code_postprocess_plan import CodePostprocessPlanTests
from monkey import code_project_postprocess as project
from monkey.io import encoded,sha
from monkey.sources.compiled import ParseError

class ProjectPostprocessTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir='/private/tmp');self.addCleanup(self.tmp.cleanup);self.base=Path(self.tmp.name);self.source=self.base/'source';self.source.mkdir()
  _,self.paths=CodePostprocessPlanTests().build_candidate(self.source)
  m=json.loads((self.source/'manifest.json').read_bytes());m.update(targetProfile='unity-6000.6.2f1-ugui',namespace='own-source',scopeMode='whole-input')
  for i,path in enumerate(self.paths):
   raw=(f'public class Class{i} {{ public dynamic '+('Outer'if i==0 else'Inner')+'() { return 1; }'+(' public static dynamic Value;'if i else'')+' }\n').encode();(self.source/path).write_bytes(raw)
   row=next(x for x in m['files']if x['path']==path);row.update(bytes=len(raw),sha256=sha(raw))
  (self.source/'manifest.json').write_bytes(encoded(m));self.pin=sha(encoded(m));self.codex=self.base/'own-cli';self.codex.write_text('#!/bin/sh\nexit 0\n');self.codex.chmod(0o755);self.output=self.base/'run'
  project.prepare(self.source,self.pin,self.output,max_files=1,codex=self.codex)
 def fake_prepare(self,source,paths,pin,out,task,**kw):
  out=Path(out);(out/'workspace').mkdir(parents=True)
  self.latest=list(paths)
  for path in paths:
   target=out/'workspace'/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((Path(source)/path).read_bytes())
  (out/'request.json').write_bytes(encoded({'state':'finalized'}))
  return type('Prepared',(),{'output':out})()
 def fake_run(self,prepared,**kw):
  plan=json.loads((self.output/'plan.json').read_bytes());records={x['path']:x for x in plan['files']}
  results=[]
  for path in self.latest:
   p=prepared.output/'workspace'/path;p.write_text(p.read_text().replace('return 1','return 2'))
   results.append(dict(path=path,status='partial',summary='Reviewed the literal-return method and original source scope; dynamic domain remains explicit.',unresolved=['Own fixture result only'],membersReviewed=[x['methodId']for x in records[path]['functions']],originalLogicPreserved=True))
  return dict(status='partial',fileResults=results,blockingCondition=None,unexpectedPaths=[],workspaceIntegrityErrors=[],gitBoundary={'valid':True},sessionId='own-fixture',usage={},model='unknown',reasoningEffort='unknown',diffSha256='0'*64)
 def test_all_ready_batches_run_continuously_and_integrate_independent_copy(self):
  with patch.object(project.worker,'prepare',side_effect=self.fake_prepare),patch.object(project.worker,'run',side_effect=self.fake_run) as run:
   result=project.run(self.output)
  self.assertEqual(run.call_count,2);self.assertEqual(result['actuallyProcessed'],2);self.assertEqual(result['status'],'complete_with_partial')
  for p in self.paths:
   self.assertIn('return 1',(self.source/p).read_text());self.assertIn('return 2',(self.output/'UnityProject'/p).read_text())
 def test_real_quota_condition_preserves_pending_scope_and_resume_continues(self):
  blocked=dict(status='failed',fileResults=[],blockingCondition='quota',unexpectedPaths=[],workspaceIntegrityErrors=[],gitBoundary={'valid':True})
  with patch.object(project.worker,'prepare',side_effect=self.fake_prepare),patch.object(project.worker,'run',return_value=blocked):
   first=project.run(self.output)
  self.assertEqual(first['status'],'blocked');self.assertEqual(first['actuallyProcessed'],0);self.assertEqual(first['fileStates']['pending'],1)
  with patch.object(project.worker,'prepare',side_effect=self.fake_prepare),patch.object(project.worker,'run',side_effect=self.fake_run):
   resumed=project.resume(self.output)
  self.assertEqual(resumed['actuallyProcessed'],2)
 def test_manual_change_is_not_overwritten_by_integrated_batch(self):
  path=self.paths[0];target=self.output/'UnityProject'/path;target.write_text('manual work')
  with patch.object(project.worker,'prepare',side_effect=self.fake_prepare),patch.object(project.worker,'run',side_effect=self.fake_run):
   with self.assertRaises(ParseError) as error:project.run(self.output)
  self.assertEqual(error.exception.code,'PROJECT_POSTPROCESS_DIRTY');self.assertEqual(target.read_text(),'manual work')
