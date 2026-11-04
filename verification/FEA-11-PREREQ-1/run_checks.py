"""Run only authorized contract probes, capture COMMAND/ENV/EXIT evidence."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE='692239408cba40296f4187afb6571e2cf423f417'


def git(*args):
    result=subprocess.run(['git',*args],cwd=ROOT,capture_output=True,check=True)
    return result.stdout


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture(command,name):
    env=os.environ.copy()
    env['PYTHONDONTWRITEBYTECODE']='1'
    env['PYTHONIOENCODING']='utf-8'
    result=subprocess.run(command,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    header=f'COMMAND: {subprocess.list2cmdline(command)}\nENV: shell=PowerShell; OS={platform.platform()}; launcher={sys.executable}; cwd={ROOT}; HEAD={git("rev-parse","HEAD").decode().strip()}; DB=:memory: (Python probes); no system TEMP/AppData\n'
    raw=header+result.stdout.decode('utf-8',errors='replace')+f'\nPROCESS_EXIT: {result.returncode}\n'
    (HERE/name).write_text(raw,encoding='utf-8')
    print(f'{name}: EXIT={result.returncode}')
    if result.returncode:
        print(raw)
        raise SystemExit(result.returncode)


def scope():
    assert git('rev-parse','HEAD').decode().strip()==BASE,'HEAD drift'
    assert git('branch','--show-current').decode().strip()=='main'
    paths=set(git('diff','--name-only','HEAD').decode().splitlines())
    paths.update(git('ls-files','--others','--exclude-standard').decode().splitlines())
    allowed={'doc/tasks/FEA-11-PREREQ-1.md','doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md','doc/plan/FEA-CONTRACT-FROZEN-C17.md','doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md','doc/handoffs/FEA-11-PREREQ-1-handoff.md'}
    outside=sorted(p for p in paths if p not in allowed and not p.startswith('verification/FEA-11-PREREQ-1/'))
    assert not outside,outside
    assert not git('diff','--cached','--name-only').strip(),'unexpected staged content'
    pins_text=(ROOT/'tools/governance/verify_pins.ps1').read_text(encoding='utf-8-sig')
    frozen=re.findall(r"'([A-Za-z0-9]+)'='([^']+\.md)'",pins_text)
    assert len(frozen)==17
    protected=['tools/governance/verify_pins.ps1','doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md','src/infrastructure/sqlite/schema.py','src/infrastructure/sqlite/migrator.py']+[f'doc/plan/{file}' for _,file in frozen]
    baseline={p:{'git_blob':git('rev-parse',f'{BASE}:{p}').decode().strip(),'workspace_sha256':sha(ROOT/p)} for p in protected}
    assert not git('diff','HEAD','--',*protected).strip(),'protected bytes changed'
    # All production/history paths are excluded by complete diff + untracked check.
    result={'base_commit':BASE,'branch':'main','git_common_dir':git('rev-parse','--git-common-dir').decode().strip(),
            'start_workspace':'clean (observed before first edit)','protected':baseline,
            'old_frozen_count':17,'migration_policy':'v1-v7 unchanged; candidate v8 not reserved',
            'user_data':'NOT_ACCESSED','DB':':memory:','external_resources_created':[]}
    (HERE/'baseline.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    text='COMMAND: git diff --name-only HEAD; git ls-files --others --exclude-standard; git diff --cached --name-only; protected diff\n'
    text+=f'ENV: PowerShell / Python {platform.python_version()} / {sys.executable}; cwd={ROOT}; HEAD={BASE}\n'
    text+='\n'.join(sorted(paths))+'\n'
    text+='PASS: 0 outside paths; 0 staged; main/HEAD unchanged; M2-C1/pins/17 frozen contracts/schema/migrator unchanged; no production paths changed\nEXIT: 0\n'
    (HERE/'scope-validation.log').write_text(text,encoding='utf-8')
    print('scope-validation.log: EXIT=0')


def fingerprints():
    rel='doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md'
    path=ROOT/rel
    # hash-object without -w computes filtered Git blob identity, no object mutation.
    blob=git('hash-object','--path='+rel,rel).decode().strip()
    filtered=git('hash-object','--no-filters',rel).decode().strip()
    raw=path.read_bytes()
    # .gitattributes/autocrlf filter verified through the two computed object IDs.
    lf=raw.replace(b'\r\n',b'\n')
    lf_blob=hashlib.sha1(b'blob '+str(len(lf)).encode()+b'\0'+lf).hexdigest()
    assert blob==lf_blob, 'unexpected Git filter; do not assume LF'
    result={'status':'DRAFT_CANDIDATE_NOT_FROZEN','source':rel,'base_commit':BASE,
            'reviewed_head':None,'semantic_commit':None,'final_pin':None,
            'workspace_sha256':hashlib.sha256(raw).hexdigest(),
            'git_filtered_blob_id':blob,'raw_blob_id':filtered,
            'candidate_filtered_blob_sha256':hashlib.sha256(lf).hexdigest(),
            'hash_basis':'workspace raw bytes for future verify_pins; filtered candidate bytes verified against git hash-object, NOT a committed blob',
            'command':['git hash-object --path='+rel+' '+rel,'git hash-object --no-filters '+rel]}
    (HERE/'candidate-fingerprints.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    args=sys.argv[1:]
    if not args or '--probes' in args:
        capture([sys.executable,'-B',str(HERE/'validate_contract.py')],'sql-validation.log')
        capture([sys.executable,'-B',str(HERE/'validate_wire.py')],'wire-validation.log')
        capture([sys.executable,'-B',str(HERE/'validate_examples.py')],'examples.log')
    if not args or '--scope' in args:
        scope()
        fingerprints()
    if '--gates' in args:
        capture(['pwsh','-NoProfile','-File','tools/governance/check.ps1'],'governance.log')
        capture(['pwsh','-NoProfile','-File','tools/governance/verify_pins.ps1'],'pins.log')


if __name__=='__main__':
    main()
