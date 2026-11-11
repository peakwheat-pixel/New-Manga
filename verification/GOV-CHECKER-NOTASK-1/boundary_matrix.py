"""Collect additional pre-change STATUS boundary observations in the isolated clone."""
from pathlib import Path
import importlib.util
import subprocess
import sys
from datetime import datetime, timezone

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('baseline_matrix', Path(__file__).with_name('baseline_matrix.py'))
matrix = importlib.util.module_from_spec(spec)
spec.loader.exec_module(matrix)

def main():
    head_code, head = matrix.run(['git', 'rev-parse', 'HEAD'])
    status_code, before = matrix.run(['git', 'status', '--porcelain'])
    print(f'HEAD_GENERATED={head.strip()}\nHEAD_EXIT={head_code}\nCLONE_STATUS_BEFORE={before.strip() or "CLEAN"}\nSTATUS_EXIT={status_code}')
    print(f'STARTED={datetime.now(timezone.utc).isoformat()}')
    print(f'CHECKER_SHA256={matrix.digest(matrix.ROOT / "tools/governance/check.ps1")}')
    cases = [
        ('empty-suffix', '- 当前 Task：无效'),
        ('empty-with-missing-path', '- 当前 Task：无 (tasks/GOV-CHECKER-NOTASK-MISSING.md)'),
        ('duplicate-empty-and-active', '- 当前 Task：无\n- 当前 Task：GOV-CHECKER-NOTASK-1 (tasks/GOV-CHECKER-NOTASK-1.md)'),
        ('empty-unclosed-comment', '- 当前 Task：无（未关闭'),
        ('empty-contradictory-text', '- 当前 Task：无，但是正在执行某任务'),
    ]
    results = {}
    try:
        for name, value in cases:
            results[name] = matrix.case(name, value)
    finally:
        matrix.restore()
    status_code, after = matrix.run(['git', 'status', '--porcelain'])
    print(f'\nCLONE_STATUS_AFTER={after.strip() or "CLEAN"}\nSTATUS_EXIT={status_code}')
    print(f'FINISHED={datetime.now(timezone.utc).isoformat()}')
    expected = (head_code == 0 and not before.strip() and status_code == 0 and not after.strip()
                and results['duplicate-empty-and-active'][0] == 0
                and all(results[key][0] != 0 for key in results if key != 'duplicate-empty-and-active'))
    print(f'BOUNDARY_BASELINE={"PASS" if expected else "FAIL"}')
    return 0 if expected else 1

if __name__ == '__main__':
    sys.exit(main())
