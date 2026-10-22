import pathlib,subprocess,types,importlib.util,copy,json,os,sys
from unittest import mock
R=pathlib.Path('G:/CODEX/New Manga');O=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else pathlib.Path('G:/CODEX/New Manga.workspace/agent-output/codex/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1')
W=R.parent/'New Manga.workspace/worktrees/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1'
old=types.ModuleType('reviewed_r1');old.__file__=str(W/'tools/governance/clean_workspace.py')
exec(compile(subprocess.check_output(['git','show','090bed6f61fceb07267cb1a46de314380e9205fd:tools/governance/clean_workspace.py'],cwd=R),str(W/'tools/governance/clean_workspace.py'),'exec'),old.__dict__)
spec=importlib.util.spec_from_file_location('revised',W/'tools/governance/clean_workspace.py');new=importlib.util.module_from_spec(spec);spec.loader.exec_module(new)
with mock.patch.object(old,'_apply_historical_evidence_interpretation',side_effect=lambda i,c:(i,c)):
 base,counts=old.scan_repo_declarations(str(R),str(R.parent/'New Manga.workspace'))
policy=json.loads((R/old.HISTORICAL_EVIDENCE_POLICY).read_bytes());results=[]
for ref in policy['reference_guards']:
 for mutation in ('missing','regular-file'):
  case=dict(reference=ref['path_rel'],mutation=mutation)
  for label,module in [('before_r1',old),('after_r2',new)]:
   phase=[False];finish=module._finish_declaration_scan;isdir=os.path.isdir;lexists=os.path.lexists
   def mark(i,c):phase[0]=True;return finish(i,c)
   def match(path):return phase[0] and module.norm_abs(path)==ref['normalized']
   initial=copy.deepcopy(base)
   before_declarations=list(initial.declarations);before_protected={k:list(v) for k,v in initial.protected.items()};before_warnings=list(initial.warnings)
   with mock.patch.object(module,'_finish_declaration_scan',side_effect=mark),mock.patch.object(module.os.path,'isdir',side_effect=lambda p:False if match(p) else isdir(p)),mock.patch.object(module.os.path,'lexists',side_effect=lambda p:False if mutation=='missing' and match(p) else lexists(p)):
    result,scan=module._apply_historical_evidence_interpretation(initial,counts)
   case[label]=dict(errors=len(result.errors),last_code=result.errors[-1]['code'],original_index_returned=result is initial)
   assert len(result.errors)==(7 if label=='before_r1' else 13)
   if label=='after_r2':
    assert result is initial and result.errors[:-1]==base.errors and result.errors[-1]['code']=='SOURCE_DRIFT'
    assert result.protected==before_protected and result.declarations==before_declarations and result.warnings==before_warnings
  results.append(case)
print(json.dumps(dict(status='PASS',mode='PURE_MEMORY_NO_WRITES',cases=results),ensure_ascii=False,indent=2))
