"""Read-only canonical comparison, including the counterfactual old tail."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from unittest import mock

R=Path(sys.argv[1])
TOOL=Path(sys.argv[2])
O=Path(sys.argv[3])
spec=importlib.util.spec_from_file_location('candidate_guard',TOOL)
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
p=json.loads((R/g.HISTORICAL_EVIDENCE_POLICY).read_bytes())
bindings=p['template_bindings']+p['raw_non_declaration_bindings']
sha=lambda raw:hashlib.sha256(raw).hexdigest()
raw_before={b['origin_file']:sha((R/b['origin_file']).read_bytes()) for b in bindings}
with mock.patch.object(g,'_apply_historical_evidence_interpretation',side_effect=lambda i,c:(i,c)):
    old,old_scan=g.scan_repo_declarations(str(R),str(R.parent/'New Manga.workspace'))
new,new_scan=g.scan_repo_declarations(str(R),str(R.parent/'New Manga.workspace'))
five=[e for b in bindings for e in b['errors']]
assert len(old.errors)==12 and len(new.errors)==7,(old.errors,new.errors)
assert all(old.errors.count(e)==1 for e in five)
assert new.errors==[e for e in old.errors if e not in five]
assert len(new.declarations)-len(old.declarations)==6
assert len(new.warnings)-len(old.warnings)==4
assert set(old.protected)<=set(new.protected)
assert len(new.protected)==len(old.protected)
baseline=json.loads((O/'baseline.json').read_bytes())
assert set(baseline['protected'])<=set(new.protected)
assert baseline['errors']==old.errors
for b in bindings:
    assert raw_before[b['origin_file']]==b['raw_sha256']==sha((R/b['origin_file']).read_bytes())
    tracked=subprocess.check_output(['git','ls-files','--',b['origin_file']],cwd=R)
    assert bool(tracked)==(b['expected_tracking']=='tracked')
for ref in p['reference_guards']:
    assert ref['normalized'] in new.protected
result=dict(status='PASS',old_scan=old_scan,new_scan=new_scan,
            old_counts=old.counts(),new_counts=new.counts(),
            counterfactual_errors=old.errors,remaining_errors=new.errors,
            five_removed=five,original_protected_roots=len(baseline['protected']),
            original_protection_subset=True,guard_roots_added=0,
            original_raw_sha256=raw_before,P22_still_untracked=True,
            real_resource_operations=0)
print(json.dumps(result,ensure_ascii=False,indent=2))
