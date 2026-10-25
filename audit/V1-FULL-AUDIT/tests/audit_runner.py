"""Local audit runner: persistent logs, bounded commands, isolated application roots."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / 'audit/V1-FULL-AUDIT'
RUNTIME = ROOT.parent / 'New Manga.workspace/task-env/NEW-MANGA-V1-FULL-AUDIT'


def run(name: str, argv: list[str], cwd: Path, timeout: int) -> dict:
    assert cwd.is_dir(), cwd
    started = datetime.now(timezone.utc).isoformat()
    tick = time.perf_counter()
    env = os.environ.copy()
    for key in list(env):
        if key.startswith(('M2RC1_', 'M2RC2_', 'M2AC1_', 'NEWMANGA_')):
            env.pop(key)
    env.update(PYTHONPATH=str(ROOT / 'src'), PYTHONDONTWRITEBYTECODE='1',
               PYTHONIOENCODING='utf-8', NEWMANGA_DATA_ROOT=str(RUNTIME / name / 'data'),
               M2RC1_DERIVED_ROOT=str(RUNTIME / name / 'derived'),
               M2RC1_MANAGED_ROOT=str(RUNTIME / name / 'managed'),
               M2RC2_CATALOG_DB=str(RUNTIME / name / 'catalog.sqlite'),
               TEMP=str(RUNTIME / name / 'temp'), TMP=str(RUNTIME / name / 'temp'),
               CARGO_TARGET_DIR=str(RUNTIME / 'cargo-target'))
    if name == 'desktop-build':
        env['TAURI_CONFIG'] = json.dumps({'build': {'frontendDist': str(RUNTIME / 'frontend-dist')}})
    Path(env['TEMP']).mkdir(parents=True, exist_ok=True)
    log = AUDIT / 'logs' / f'{name}.log'
    with log.open('w', encoding='utf-8') as stream:
        stream.write(f'START_UTC={started}\nSHELL=Python subprocess (no shell)\nINTERPRETER={sys.executable}\nCWD={cwd}\nARGV={json.dumps(argv)}\nDATA_ROOT={env["NEWMANGA_DATA_ROOT"]}\n')
        stream.flush()
        process = subprocess.Popen(argv, cwd=cwd, env=env, stdout=stream, stderr=subprocess.STDOUT)
        timed_out = False
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            # Only this runner's child tree; never stop unrelated user processes.
            subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], capture_output=True)
            code = process.wait(timeout=30)
        elapsed = round(time.perf_counter() - tick, 3)
        stream.write(f'\nEXIT={code}\nTIMED_OUT={timed_out}\nELAPSED_SECONDS={elapsed}\n')
    result = dict(name=name, argv=argv, cwd=str(cwd), started_utc=started,
                  exit_code=code, timed_out=timed_out, elapsed_seconds=elapsed,
                  log=str(log.relative_to(ROOT)))
    (AUDIT / 'evidence' / f'{name}.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result), flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('suite', choices=['pytest', 'frontend', 'rust', 'smoke', 'governance', 'dependencies', 'desktop', 'probes'])
    args = parser.parse_args()
    assert ROOT.name == 'New Manga' and (ROOT / '.git').exists()
    npm = shutil.which('npm.cmd') or 'npm.cmd'
    suites = {
        'pytest': [('pytest', [sys.executable, '-m', 'pytest', 'tests', '-q', '-rs', '--tb=short', '-o', 'cache_dir=' + str(RUNTIME / 'pytest-cache'), '--basetemp=' + str(RUNTIME / 'pytest-temp')], ROOT, 1200)],
        'frontend': [('frontend-tests', [npm, 'test', '--', '--reporter=verbose'], ROOT / 'apps/desktop/frontend', 180),
                     ('frontend-build', [npm, 'run', 'build', '--', '--outDir', str(RUNTIME / 'frontend-dist')], ROOT / 'apps/desktop/frontend', 180)],
        'rust': [('cargo-test', ['cargo', 'test', '--locked', '--offline'], ROOT / 'apps/desktop/src-tauri', 900)],
        'desktop': [('desktop-build', ['cargo', 'build', '--locked', '--offline'], ROOT / 'apps/desktop/src-tauri', 900)],
        'probes': [('audit-probes', [sys.executable, '-m', 'pytest', str(AUDIT / 'tests/test_audit_probes.py'), '-vv', '-s', '-p', 'no:cacheprovider', '--basetemp=' + str(RUNTIME / 'probe-temp')], ROOT, 120)],
        'smoke': [('software-smoke', [sys.executable, '-m', 'tools.smoke.plugins', '--only', 'core,wire,packaged', '--json', str(AUDIT / 'evidence/software-smoke-report.json')], ROOT, 180)],
        'governance': [('governance', ['pwsh', '-NoProfile', '-File', 'tools/governance/check.ps1'], ROOT, 180)],
        'dependencies': [('pip-check', [sys.executable, '-m', 'pip', 'check'], ROOT, 60),
                         ('npm-audit', [npm, 'audit', '--json'], ROOT / 'apps/desktop/frontend', 90)],
    }
    for spec in suites[args.suite]:
        run(*spec)
