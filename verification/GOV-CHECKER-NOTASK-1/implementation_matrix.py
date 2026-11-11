"""Exercise frozen checker cases and mutations in the isolated implementation clone."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import re
import subprocess
import sys

ROOT = Path('G:/CODEX/New Manga.workspace/GOV-CHECKER-NOTASK-1/implementation')
STATUS = ROOT / 'doc/STATUS.md'
TASK = ROOT / 'doc/tasks/GOV-CHECKER-NOTASK-1.md'
LEDGER = ROOT / 'doc/TASK_LEDGER.md'
CHECKER = ROOT / 'tools/governance/check.ps1'
ORIGINAL = {p: p.read_bytes() for p in (STATUS, TASK, LEDGER, CHECKER)}
EMPTY_WARNING = 'STATUS 声明无当前 Task（空窗）；跳过当前 Task 检查。'
NO_POINTER = 'STATUS 未提供可解析的当前 Task 指针。'
NO_FILE = '当前 Task 文件不存在：'
TERMINAL = 'STATUS 仍指向终态 Task：done'
PENDING = 'DONE 必须记录 integration_commit。'
checks = []

def sha(data):
    return hashlib.sha256(data).hexdigest()

def run(args):
    r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return r.returncode, r.stdout + r.stderr

def restore():
    for path, content in ORIGINAL.items():
        path.write_bytes(content)

def scenario(name, status, expected, required=(), forbidden=(), pending=False, mutation=None, warning_count=None):
    restore()
    if name.startswith('after-'):
        restored_sha = sha(CHECKER.read_bytes())
        print(f'RESTORE_BEFORE_CASE={name} SHA256={restored_sha}')
        if restored_sha != sha(ORIGINAL[CHECKER]):
            raise RuntimeError('checker restore mismatch')
    if status is not None:
        text, count = re.subn(r'(?m)^- 当前 Task：[^\r\n]*', lambda _: status, ORIGINAL[STATUS].decode('utf-8'))
        if count != 1:
            raise RuntimeError(f'STATUS replacement count={count}')
        STATUS.write_bytes(text.encode('utf-8'))
    if pending:
        text = ORIGINAL[TASK].decode('utf-8').replace('status: in_progress', 'status: done', 1)
        text = text.replace('integration_commit: null', 'integration_commit: pending', 1)
        TASK.write_bytes(text.encode('utf-8'))
        ledger_code, ledger_output = run(['python', 'tools/governance/task_ledger.py', '--write'])
        if ledger_code:
            raise RuntimeError(f'ledger exit={ledger_code}: {ledger_output}')
    if mutation:
        text = ORIGINAL[CHECKER].decode('utf-8')
        old = "if ($emptyDeclaration -and $line -notmatch '(?i)tasks[/\\\\]')"
        if text.count(old) != 1:
            raise RuntimeError('mutation target is not unique')
        replacement = 'if ($true)' if mutation == 'any-failure' else 'if ($emptyDeclaration)'
        CHECKER.write_bytes(text.replace(old, replacement, 1).encode('utf-8'))
        print(f'MUTATED_CHECKER_SHA256={sha(CHECKER.read_bytes())}')
    command = ['pwsh', '-NoProfile', '-File', 'tools/governance/check.ps1']
    if pending:
        command.extend(['-TaskPath', 'doc/tasks/GOV-CHECKER-NOTASK-1.md'])
    code, output = run(command)
    ok = (code == expected and all(value in output for value in required)
          and all(value not in output for value in forbidden)
          and (warning_count is None or output.count(EMPTY_WARNING) == warning_count))
    checks.append(ok)
    print(f'\nCASE={name}\nCOMMAND={" ".join(command)}\n{output}EXIT={code}\nASSERT={"PASS" if ok else "FAIL"}')

def main():
    head_code, head = run(['git', 'rev-parse', 'HEAD'])
    state_code, state = run(['git', 'status', '--porcelain'])
    print(f'HEAD_GENERATED={head.strip()}\nHEAD_EXIT={head_code}\nCLONE_STATUS_BEFORE={state.strip() or "CLEAN"}\nSTATUS_EXIT={state_code}')
    print(f'STARTED={datetime.now(timezone.utc).isoformat()}\nCHECKER_SHA256={sha(ORIGINAL[CHECKER])}')
    active = '- 当前 Task：GOV-CHECKER-NOTASK-1 (tasks/GOV-CHECKER-NOTASK-1.md)'
    empty = '- 当前 Task：无（S5 收口空窗；default gate EXIT 1 为已披露 checker limitation，用 -TaskPath）。'
    terminal = '- 当前 Task：FEA-15-PIN-POLICY-1 (tasks/FEA-15-PIN-POLICY-1.md)'
    missing = '- 当前工作：无'
    absent = (EMPTY_WARNING,)
    try:
        scenario('baseline-active', None, 0, required=('Task: doc\\tasks\\GOV-CHECKER-NOTASK-1.md',), forbidden=absent)
        scenario('baseline-explicit-empty', empty, 0, required=(EMPTY_WARNING,), forbidden=(NO_POINTER, NO_FILE), warning_count=1)
        scenario('baseline-missing-line', missing, 1, required=(NO_POINTER, NO_FILE), forbidden=absent)
        scenario('baseline-ambiguous-empty', '- 当前 Task：无效', 1, required=(NO_POINTER, NO_FILE), forbidden=absent)
        scenario('baseline-missing-path', '- 当前 Task：MISSING (tasks/GOV-CHECKER-NOTASK-MISSING.md)', 1, required=(NO_FILE,), forbidden=absent)
        scenario('baseline-terminal', terminal, 1, required=(TERMINAL,), forbidden=absent)
        scenario('baseline-pending-taskpath', None, 1, required=(PENDING,), forbidden=absent, pending=True)
        scenario('baseline-empty-suffix', '- 当前 Task：无效', 1, required=(NO_POINTER, NO_FILE), forbidden=absent)
        scenario('baseline-empty-missing-path', '- 当前 Task：无 (tasks/GOV-CHECKER-NOTASK-MISSING.md)', 1, required=(NO_FILE,), forbidden=absent)
        scenario('baseline-duplicate-active', '- 当前 Task：无\n' + active, 0, required=('Task: doc\\tasks\\GOV-CHECKER-NOTASK-1.md',), forbidden=absent)
        scenario('baseline-unclosed', '- 当前 Task：无（未关闭', 1, required=(NO_POINTER, NO_FILE), forbidden=absent)
        scenario('baseline-contradiction', '- 当前 Task：无，但是正在执行某任务', 1, required=(NO_POINTER, NO_FILE), forbidden=absent)
        scenario('empty-with-terminal', '- 当前 Task：无\n' + terminal, 1, required=(TERMINAL,), forbidden=absent)
        scenario('empty-with-pending-taskpath', empty, 1, required=(PENDING,), forbidden=absent, pending=True)
        for name, value in (
            ('dot', '- 当前 Task：无。'), ('ascii-colon', '- 当前 Task: 无'),
            ('nested-fullwidth', '- 当前 Task：无（见（旧）说明）。'),
            ('path-slash', '- 当前 Task：无（tasks/FOO.md）。'),
            ('path-upper', '- 当前 Task：无（TASKS/FOO.md）。'),
            ('path-backslash', '- 当前 Task：无（tasks\\FOO.md）。'),
        ):
            scenario(name, value, 1, required=(NO_POINTER, NO_FILE), forbidden=absent)
        for name, value in (
            ('ascii-path', '- 当前 Task：无 (tasks/FOO.md)。'),
            ('hidden-ascii-path', '- 当前 Task：无（见 (tasks/FOO.md) 注）'),
        ):
            scenario(name, value, 1, required=(NO_FILE, 'FOO.md'), forbidden=absent)
        scenario('bare-empty', '- 当前 Task：无', 0, required=(EMPTY_WARNING,), warning_count=1)
        scenario('two-empty', '- 当前 Task：无\n- 当前 Task：无', 0, required=(EMPTY_WARNING,), warning_count=1)
        scenario('empty-id-comment', '- 当前 Task：无（GOV-CHECKER-NOTASK-1 已收口）', 0, required=(EMPTY_WARNING,), warning_count=1)
        scenario('mutation-any-failure', missing, 0, required=(EMPTY_WARNING,), warning_count=1, mutation='any-failure')
        scenario('after-any-failure-restore', missing, 1, required=(NO_POINTER, NO_FILE), forbidden=absent)
        scenario('after-any-restore-positive', empty, 0, required=(EMPTY_WARNING,), warning_count=1)
        scenario('mutation-no-path-exclusion', '- 当前 Task：无（tasks/FOO.md）。', 0, required=(EMPTY_WARNING,), warning_count=1, mutation='no-path-exclusion')
        scenario('after-path-exclusion-restore', '- 当前 Task：无（tasks/FOO.md）。', 1, required=(NO_POINTER, NO_FILE), forbidden=absent)
        scenario('final-positive', empty, 0, required=(EMPTY_WARNING,), warning_count=1)
    finally:
        restore()
    final_sha = sha(CHECKER.read_bytes())
    state_code, state = run(['git', 'status', '--porcelain'])
    print(f'\nRESTORED_CHECKER_SHA256={final_sha}\nCLONE_STATUS_AFTER={state.strip() or "CLEAN"}\nSTATUS_EXIT={state_code}')
    ok = (head_code == 0 and state_code == 0 and not state.strip() and final_sha == sha(ORIGINAL[CHECKER]) and all(checks))
    print(f'ASSERTIONS={sum(checks)}/{len(checks)}\nMATRIX_RESULT={"PASS" if ok else "FAIL"}\nFINISHED={datetime.now(timezone.utc).isoformat()}')
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main())
