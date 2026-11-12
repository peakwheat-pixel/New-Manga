"""Local audit runner: persistent logs, bounded commands, isolated application roots."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
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


def _git_status_bytes() -> bytes:
    result = subprocess.run(
        ['git', 'status', '--porcelain'], cwd=ROOT, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=True,
    )
    return result.stdout


def run(name: str, argv: list[str], cwd: Path, timeout: int) -> dict:
    assert cwd.is_dir(), cwd
    started = datetime.now(timezone.utc).isoformat()
    tick = time.perf_counter()
    is_dotnet = name.startswith('dotnet-')
    head = subprocess.run(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=True, text=True, encoding='utf-8',
    ).stdout.strip()
    branch = subprocess.run(
        ['git', 'branch', '--show-current'], cwd=ROOT, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=True, text=True, encoding='utf-8',
    ).stdout.strip()
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
    if is_dotnet:
        env.update(NEWMANGA_WORKSPACE_ROOT=str(RUNTIME),
                   DOTNET_CLI_TELEMETRY_OPTOUT='1', DOTNET_NOLOGO='1')
    if name == 'desktop-build':
        env['TAURI_CONFIG'] = json.dumps({'build': {'frontendDist': str(RUNTIME / 'frontend-dist')}})
    Path(env['TEMP']).mkdir(parents=True, exist_ok=True)
    if is_dotnet:
        external_run = RUNTIME / 'dotnet-runner' / name
        external_run.mkdir(parents=True, exist_ok=True)
        log = external_run / f'{name}.log'
        result_path = external_run / f'{name}.json'
        published_log = AUDIT / 'logs' / f'{name}.log'
        published_result = AUDIT / 'evidence' / f'{name}.json'
        results_directory = Path(argv[argv.index('--results-directory') + 1])
        results_directory.mkdir(parents=True, exist_ok=True)
        status_before = _git_status_bytes()
    else:
        log = AUDIT / 'logs' / f'{name}.log'
        result_path = AUDIT / 'evidence' / f'{name}.json'
        status_before = None
    with log.open('w', encoding='utf-8') as stream:
        stream.write(f'START_UTC={started}\nHEAD={head}\nBRANCH={branch}\nSHELL=Python subprocess (no shell)\nINTERPRETER={sys.executable}\nCWD={cwd}\nARGV={json.dumps(argv)}\nDATA_ROOT={env["NEWMANGA_DATA_ROOT"]}\n')
        if is_dotnet:
            stream.write(f'GIT_STATUS_BEFORE_SHA256={hashlib.sha256(status_before).hexdigest().upper()}\n')
            stream.write(f'GIT_STATUS_BEFORE_HEX={status_before.hex().upper()}\n')
            stream.write(f'RESULTS_DIRECTORY={results_directory}\n')
            stream.write(f'NEWMANGA_WORKSPACE_ROOT={env["NEWMANGA_WORKSPACE_ROOT"]}\n')
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
        status_after = _git_status_bytes() if is_dotnet else None
        if is_dotnet:
            stream.write(f'GIT_STATUS_AFTER_SHA256={hashlib.sha256(status_after).hexdigest().upper()}\n')
            stream.write(f'GIT_STATUS_AFTER_HEX={status_after.hex().upper()}\n')
            stream.write(f'GIT_STATUS_BYTE_IDENTICAL={status_before == status_after}\n')
        stream.write(f'\nEXIT={code}\nTIMED_OUT={timed_out}\nELAPSED_SECONDS={elapsed}\n')
    result = dict(name=name, argv=argv, cwd=str(cwd), started_utc=started,
                  head=head, branch=branch,
                  exit_code=code, timed_out=timed_out, elapsed_seconds=elapsed,
                  log=str((published_log if is_dotnet else log).relative_to(ROOT)))
    if is_dotnet:
        result.update(status_identical=status_before == status_after,
                      status_before_sha256=hashlib.sha256(status_before).hexdigest().upper(),
                      status_after_sha256=hashlib.sha256(status_after).hexdigest().upper(),
                      results_directory=str(results_directory))
    result_path.write_text(json.dumps(result, indent=2), encoding='utf-8')
    if is_dotnet:
        shutil.copy2(log, published_log)
        shutil.copy2(result_path, published_result)
    print(json.dumps(result), flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('suite', choices=['pytest', 'audit03-import', 'frontend', 'rust', 'smoke', 'governance', 'dependencies', 'desktop', 'probes', 'dotnet', 'sidecar-lifecycle'])
    args = parser.parse_args()
    assert ROOT.name == 'New Manga' and (ROOT / '.git').exists()
    npm = shutil.which('npm.cmd') or 'npm.cmd'
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    dotnet_projects = [
        ('App', 'apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj'),
        ('Appearance', 'apps/desktop-avalonia/tests/NewManga.Appearance.Tests/NewManga.Appearance.Tests.csproj'),
        ('ApplicationCore', 'apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/NewManga.ApplicationCore.Tests.csproj'),
        ('CoreClient', 'apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/NewManga.CoreClient.Tests.csproj'),
        ('DesignSystem', 'apps/desktop-avalonia/tests/NewManga.DesignSystem.Tests/NewManga.DesignSystem.Tests.csproj'),
        ('Host', 'apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj'),
        ('PresentationAvalonia', 'apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/NewManga.Presentation.Avalonia.Tests.csproj'),
        ('ThemeEngine', 'apps/desktop-avalonia/tests/NewManga.ThemeEngine.Tests/NewManga.ThemeEngine.Tests.csproj'),
    ]
    dotnet_results = RUNTIME / 'dotnet' / f'results-{run_id}'
    suites = {
        'pytest': [(f'pytest-segment-b-{run_id}', [sys.executable, '-m', 'pytest', 'tests', '-q', '-rs', '--tb=short', '-o', 'cache_dir=' + str(RUNTIME / f'pytest-cache-{run_id}'), '--basetemp=' + str(RUNTIME / f'pytest-temp-{run_id}')], ROOT, 1200)],
        # Split package groups because their same-named conftest.py modules collide when collected together.
        'audit03-import': [
            (f'audit03-core-import-{run_id}', [sys.executable, '-m', 'pytest',
            'tests/library/test_import_images.py', 'tests/library/test_import_sources.py',
            'tests/library/test_page_order.py', 'tests/library/test_sqlite_library.py',
            'tests/library/test_book_crud.py', 'tests/library/test_chapters.py',
            'tests/library/test_production_adapters.py', 'tests/library/test_p09_managed_copy_safety.py',
            'tests/storage/test_managed_storage.py', 'tests/import_formats/test_decode_format_matrix.py',
            '-q', '-rs', '--tb=short', '-o', 'cache_dir=' + str(RUNTIME / f'audit03-pytest-cache-{run_id}'),
            '--basetemp=' + str(RUNTIME / f'audit03-pytest-temp-{run_id}')], ROOT, 600),
            (f'audit03-referenced-import-{run_id}', [sys.executable, '-m', 'pytest',
            'tests/fea09/test_import_source.py', 'tests/fea09/test_referenced_flow.py',
            'tests/fea09/test_referenced_resolve.py', 'tests/fea09/test_referenced_scanner.py',
            'tests/fea09/test_referenced_wire.py', 'tests/fea09/test_referenced_sharing.py',
            'tests/fea09/test_read_paths.py', '-q', '-rs', '--tb=short',
            '-o', 'cache_dir=' + str(RUNTIME / f'audit03-reference-pytest-cache-{run_id}'),
            '--basetemp=' + str(RUNTIME / f'audit03-reference-pytest-temp-{run_id}')], ROOT, 600),
        ],
        'frontend': [(f'frontend-tests-segment-b-{run_id}', [npm, 'test', '--', '--reporter=verbose'], ROOT / 'apps/desktop/frontend', 180),
                     (f'frontend-build-segment-b-{run_id}', [npm, 'run', 'build', '--', '--outDir', str(RUNTIME / f'frontend-dist-{run_id}')], ROOT / 'apps/desktop/frontend', 180)],
        'rust': [(f'cargo-test-segment-b-{run_id}', ['cargo', 'test', '--locked', '--offline'], ROOT / 'apps/desktop/src-tauri', 900)],
        'desktop': [(f'desktop-build-segment-b-{run_id}', ['cargo', 'build', '--locked', '--offline'], ROOT / 'apps/desktop/src-tauri', 900)],
        'probes': [(f'audit-probes-segment-b-{run_id}', [sys.executable, '-m', 'pytest', str(AUDIT / 'tests/test_audit_probes.py'), '-vv', '-s', '-p', 'no:cacheprovider', '--basetemp=' + str(RUNTIME / f'probe-temp-{run_id}')], ROOT, 120)],
        'sidecar-lifecycle': [(f'sidecar-lifecycle-probe-{run_id}', ['pwsh', '-NoProfile', '-File', str(AUDIT / 'tests/sidecar_lifecycle_probe.ps1'), '-WorkspaceRoot', str(RUNTIME / f'sidecar-lifecycle-probe-{run_id}' / 'probe-output')], ROOT, 120)],
        'smoke': [(f'software-smoke-segment-b-{run_id}', [sys.executable, '-m', 'tools.smoke.plugins', '--only', 'core,wire', '--json', str(AUDIT / f'evidence/software-smoke-report-segment-b-{run_id}.json')], ROOT, 180)],
        'governance': [(f'governance-segment-b-{run_id}', ['pwsh', '-NoProfile', '-File', 'tools/governance/check.ps1'], ROOT, 180)],
        'dependencies': [(f'pip-check-segment-b-{run_id}', [sys.executable, '-m', 'pip', 'check'], ROOT, 60),
                         (f'npm-audit-segment-b-{run_id}', [npm, 'audit', '--json'], ROOT / 'apps/desktop/frontend', 90)],
        'dotnet': [
            (f'dotnet-{name.lower()}-{run_id}',
             ['dotnet', 'test', project, '--no-restore',
              '--results-directory', str(dotnet_results),
              '--logger', f'trx;LogFileName={name}-{run_id}.trx',
              '--settings', 'apps/desktop-avalonia/tests/NewManga.runsettings',
              '-v:minimal'], ROOT, 900)
            for name, project in dotnet_projects
        ],
    }
    for spec in suites[args.suite]:
        result = run(*spec)
        if args.suite == 'dotnet' and not result['status_identical']:
            print('STOP: git status --porcelain changed during .NET test; no further projects will run.', file=sys.stderr)
            break
