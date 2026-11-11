"""Run the pre-change checker matrix in the designated isolated clone."""
from pathlib import Path
import hashlib
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path('G:/CODEX/New Manga.workspace/GOV-CHECKER-NOTASK-1/baseline-blob')
STATUS = ROOT / 'doc/STATUS.md'
TASK = ROOT / 'doc/tasks/GOV-CHECKER-NOTASK-1.md'
LEDGER = ROOT / 'doc/TASK_LEDGER.md'
paths = [STATUS, TASK, LEDGER]
original = {p: p.read_bytes() for p in paths}
line_pattern = r'(?m)^- 当前 Task：[^\r\n]*'

def run(args):
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                            encoding='utf-8', errors='replace')
    return result.returncode, result.stdout + result.stderr

def restore():
    for path, content in original.items():
        path.write_bytes(content)

def status_line(value):
    text = original[STATUS].decode('utf-8')
    text, count = re.subn(line_pattern, lambda _: value, text)
    if count != 1:
        raise RuntimeError(f'expected one STATUS pointer, found {count}')
    STATUS.write_bytes(text.encode('utf-8'))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def case(name, replacement=None, pending=False):
    restore()
    if replacement is not None:
        status_line(replacement)
    command = ['pwsh', '-NoProfile', '-File', 'tools/governance/check.ps1']
    if pending:
        text = original[TASK].decode('utf-8')
        text = text.replace('status: in_progress', 'status: done', 1)
        text = text.replace('integration_commit: null', 'integration_commit: pending', 1)
        TASK.write_bytes(text.encode('utf-8'))
        ledger_exit, ledger_output = run(['python', 'tools/governance/task_ledger.py', '--write'])
        print(f'LEDGER_EXIT={ledger_exit}\n{ledger_output}')
        command.extend(['-TaskPath', 'doc/tasks/GOV-CHECKER-NOTASK-1.md'])
    code, output = run(command)
    print(f'\nCASE={name}\nCOMMAND={" ".join(command)}\n{output}EXIT={code}')
    return code, output

def main():
    head_code, head = run(['git', 'rev-parse', 'HEAD'])
    status_code, state = run(['git', 'status', '--porcelain'])
    print(f'HEAD_GENERATED={head.strip()}\nHEAD_EXIT={head_code}\nCLONE_STATUS_BEFORE={state.strip() or "CLEAN"}\nSTATUS_EXIT={status_code}')
    print(f'STARTED={datetime.now(timezone.utc).isoformat()}')
    print(f'CHECKER_SHA256={digest(ROOT / "tools/governance/check.ps1")}')
    results = {}
    try:
        results['active'] = case('active')
        results['empty'] = case('explicit-empty', '- 当前 Task：无（S5 收口空窗；default gate EXIT 1 为已披露 checker limitation，用 -TaskPath）。')
        results['missing'] = case('missing-line', '- 当前工作：无')
        results['ambiguous'] = case('ambiguous-empty', '- 当前 Task：无效')
        results['missing_path'] = case('missing-path', '- 当前 Task：MISSING (tasks/GOV-CHECKER-NOTASK-MISSING.md)')
        results['terminal'] = case('terminal-pointer', '- 当前 Task：FEA-15-PIN-POLICY-1 (tasks/FEA-15-PIN-POLICY-1.md)')
        results['pending'] = case('done-pending-integration', pending=True)
    finally:
        restore()
    status_code, state = run(['git', 'status', '--porcelain'])
    print(f'\nCLONE_STATUS_AFTER={state.strip() or "CLEAN"}\nSTATUS_EXIT={status_code}')
    print('RESTORE_SHA256=' + ','.join(f'{p.name}:{digest(p)}' for p in paths))
    print(f'FINISHED={datetime.now(timezone.utc).isoformat()}')
    expected = (results['active'][0] == 0 and
                all(results[key][0] != 0 for key in ('empty', 'missing', 'ambiguous', 'missing_path', 'terminal', 'pending')) and
                'STATUS 仍指向终态 Task' in results['terminal'][1] and
                'DONE 必须记录 integration_commit' in results['pending'][1] and
                not state.strip() and status_code == 0)
    print(f'MATRIX_EXPECTATIONS={"PASS" if expected else "FAIL"}')
    return 0 if expected else 1

if __name__ == '__main__':
    sys.exit(main())
