"""Bounded local diagnostics; never writes source main or the frozen r4 repo."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time

REPO = Path('G:/CODEX/New Manga')
PARENT = Path('G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1')
ROOT = Path('G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-DIAG-1')
SOURCE = ROOT / 'source'
HEAD = 'e34a90d001cce1fa966aec7d2b032bb5ad1cf148'
BASE = '349e61faff5f93067af5d4ce2d9e394e0d665b8c'
ROOT.mkdir(parents=True, exist_ok=True)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Evidence is append-only by unique filename; differing output requires a new attempt.
    data = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    if path.exists():
        assert path.read_bytes() == data, f'refusing overwrite: {path}'
    else:
        path.write_bytes(data)


def git(*args, cwd=SOURCE):
    return subprocess.check_output(['git', '-C', str(cwd), *args], text=True).strip()


def run(name, argv, cwd, overrides=None, unset=()):
    log = ROOT / (name + '.log')
    metadata = ROOT / (name + '.json')
    assert not log.exists() and not metadata.exists(), name
    env = os.environ.copy()
    for key in unset:
        env.pop(key, None)
    env.update(overrides or {})
    fields = dict(name=name, argv=argv, cwd=str(cwd), shell=False,
                  head=git('rev-parse', 'HEAD', cwd=cwd),
                  tracked_changes=git('diff', '--name-only', 'HEAD', cwd=cwd),
                  started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  env_overrides=overrides or {}, unset=list(unset),
                  venv=env.get('VIRTUAL_ENV'), python=sys.executable)
    start = time.monotonic()
    with log.open('wb') as stream:
        stream.write(('RUN_HEADER ' + json.dumps(fields, ensure_ascii=False) + '\n').encode())
        stream.flush()
        result = subprocess.run(argv, cwd=cwd, env=env, shell=False, stdout=stream, stderr=subprocess.STDOUT)
        stream.write(f'\nEXIT={result.returncode}\n'.encode())
    fields.update(exit=result.returncode, elapsed_seconds=round(time.monotonic()-start, 3),
                  log=str(log), log_sha256=sha(log))
    write(metadata, fields)
    print(name, 'EXIT', result.returncode, flush=True)
    return fields


def rust_env(label):
    env = dict(M2RC1_DEV_PREVIEW='1', TAURI_CONFIG='{"bundle":{"resources":[]}}',
               CARGO_TARGET_DIR=str(PARENT / 'cargo-target'), M2RC1_PYTHON='C:/Python314/python.exe',
               M2RC1_SRC_ROOT=str(SOURCE / 'src'),
               PYTHONUSERBASE='C:/Users/49745/AppData/Roaming/Python', PYTHONDONTWRITEBYTECODE='1')
    for key in ('APPDATA', 'LOCALAPPDATA', 'TEMP', 'TMP'):
        path = ROOT / ('environment-' + label) / key
        path.mkdir(parents=True, exist_ok=True)
        env[key] = str(path)
    return env


def setup_and_pin():
    assert git('rev-parse', 'HEAD', cwd=REPO) == BASE
    assert not git('diff', '--cached', '--name-only', cwd=REPO)
    if not SOURCE.exists():
        subprocess.run(['git', 'clone', '--no-hardlinks', '--branch', 'codex/clean-source-snapshot',
                        str(PARENT / 'source-export-r4'), str(SOURCE)], check=True)
        subprocess.run(['git', '-C', str(SOURCE), 'remote', 'remove', 'origin'], check=True)
        subprocess.run(['git', '-C', str(SOURCE), 'branch', '-m', 'codex/git-clean-publication-diag-1'], check=True)
        subprocess.run(['git', '-C', str(SOURCE), 'config', 'gc.auto', '0'], check=True)
    assert git('rev-parse', 'HEAD') == HEAD and not git('remote')
    subprocess.run(['git', '-C', str(SOURCE), 'config', 'core.autocrlf', 'false'], check=True)
    checks = REPO / 'verification/GIT-CLEAN-PUBLICATION-1/core-checks-r2.json'
    meta = json.loads(checks.read_text(encoding='utf-8'))
    base = Path(next(a.split('=', 1)[1] for a in meta['argv'] if a.startswith('--basetemp=')))
    databases = sorted(base.glob('test_export_hook_effective_opt[012]/data/library.db'))
    assert len(databases) == 3, databases
    records = []
    for db in databases:
        before = sha(db)
        companions = [p for p in (Path(str(db)+'-wal'), Path(str(db)+'-shm')) if p.exists()]
        dest = ROOT / 'core-r2-source-pins' / db.parent.parent.name / db.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        assert all(p.stat().st_size == 0 for p in companions if p.name.endswith('-wal')), 'nonempty WAL requires coherent DB/WAL freeze'
        originals = [db]
        hashes = {str(p): sha(p) for p in originals}
        for original in originals:
            target = dest.parent / original.name
            if not target.exists():
                shutil.copyfile(original, target)
            assert sha(target) == hashes[str(original)] == sha(original)
        # All source WALs are empty; immutable reads the checkpointed DB without creating SHM.
        with sqlite3.connect(dest.as_uri() + '?mode=ro&immutable=1', uri=True) as conn:
            conn.row_factory = sqlite3.Row
            rows = [dict(r) for r in conn.execute("SELECT * FROM plugin_events WHERE event_type='plugin_error' ORDER BY rowid")]
        assert any('cannot grant sandbox access to python.exe' in str(r) for r in rows)
        records.append(dict(original_path=str(db), frozen_path=str(dest), sha256=before,
                            bytes=db.stat().st_size, plugin_errors=rows,
                            companions=[dict(original_path=str(p), bytes=p.stat().st_size,
                                             disposition='not copied: WAL empty / SHM coordination only; WAL read sharing denied') for p in companions]))
        assert sha(db) == before
        assert all(p.stat().st_size == 0 for p in companions if p.name.endswith('-wal'))
    write(ROOT / 'core-r2-source-pins.json', dict(source_checks=str(checks), checks_sha256=sha(checks),
          source_head=meta['delivery_head'], parent_candidate_head=HEAD,
          query="SELECT * FROM plugin_events WHERE event_type='plugin_error' ORDER BY rowid",
          readonly='stable checkpointed DB copies; WAL size=0 before/after; immutable=1; source hashes unchanged; no source SQLite connection', records=records))
    print('SOURCE_PIN DB snapshots:', len(records), flush=True)


def frontend():
    cwd = SOURCE / 'apps/desktop/frontend'
    env = rust_env('frontend')
    run('npm-ci', ['E:/Program Files/nodejs/npm.cmd', 'ci', '--offline', '--ignore-scripts',
        '--no-audit', '--no-fund', '--cache', 'C:/Users/49745/AppData/Local/npm-cache'], cwd, env)
    run('frontend-build', ['E:/Program Files/nodejs/npm.cmd', 'run', 'build'], cwd, env)


def default_parallel():
    subprocess.run(['git', '-C', str(SOURCE), 'diff', '--exit-code', 'HEAD'], check=True, stdout=subprocess.DEVNULL)
    run('rust-default-parallel-r2', ['cargo', 'test', '--locked', '--offline', '--', '--skip',
        'packaged_sidecar_tests::'], SOURCE / 'apps/desktop/src-tauri', rust_env('default'),
        unset=('RUST_TEST_THREADS', 'M2RC1_PACKAGED'))


def isolated_registry():
    tests = ['ac1_consecutive_lock_timeouts_keep_the_handle_and_the_holder_registers_it',
             'ac4_unreaped_worker_registry_tracks_and_reaps_finite_lifecycle',
             'ac2_saturated_registry_answers_boundedly_and_never_loses_the_handle',
             'ac4_unreaped_worker_registry_capacity_cap_and_lock_failure_retains_handle']
    for i, test in enumerate(tests):
        run(f'registry-isolated-{i+1}', ['cargo', 'test', '--locked', '--offline',
            'library_bridge::tests::'+test, '--', '--exact', '--nocapture'],
            SOURCE / 'apps/desktop/src-tauri', rust_env('isolated'),
            unset=('RUST_TEST_THREADS', 'M2RC1_PACKAGED'))


def packaged():
    checkout = ROOT / 'packaged-source'
    assert not checkout.exists(), 'use a new attempt directory rather than overwrite'
    subprocess.run(['git', '-c', 'core.autocrlf=false', 'clone', '--no-hardlinks',
                    str(PARENT/'source-export-r4'), str(checkout)], check=True)
    subprocess.run(['git', '-C', str(checkout), 'remote', 'remove', 'origin'], check=True)
    subprocess.run(['git', '-C', str(checkout), 'branch', '-m', 'codex/publication-packaged-validation'], check=True)
    subprocess.run(['git', '-C', str(checkout), 'config', 'core.autocrlf', 'false'], check=True)
    assert git('rev-parse', 'HEAD', cwd=checkout) == HEAD
    build_python = 'G:/CODEX/New Manga.task-envs/m2ac5-build/Scripts/python.exe'
    version = subprocess.check_output([build_python, '-I', '-c',
        'import sys,PyInstaller,json; print(json.dumps(dict(version=sys.version,base_prefix=sys.base_prefix,pyinstaller=PyInstaller.__version__)))'], text=True)
    write(ROOT/'packaged-build-inputs.json', dict(head=HEAD, checkout=str(checkout),
        files=[dict(path=p, sha256=sha(checkout/p)) for p in git('ls-files', cwd=checkout).splitlines()],
        build_interpreter=build_python, interpreter_sha256=sha(build_python), tools=json.loads(version),
        weights='SkipWeights: no model validation, no installer/release claim'))
    env = rust_env('packaged-build')
    env['PYTHONUSERBASE'] = 'C:/Users/49745/AppData/Roaming/Python'
    build = run('packaged-build', ['pwsh', '-NoProfile', '-File',
        str(checkout/'packaging/m2ac5/build_sidecar.ps1'), '-PythonExe', build_python, '-SkipWeights'], checkout, env)
    if build['exit'] != 0:
        return
    bundle = checkout/'apps/desktop/src-tauri/target/core-sidecar/core-sidecar'
    files = [dict(path=p.relative_to(bundle).as_posix(), bytes=p.stat().st_size, sha256=sha(p))
             for p in sorted(bundle.rglob('*')) if p.is_file()]
    assert all(any(p['path']==name for p in files) for name in ('core_service.exe','host_bridge.exe','catalog_loader.exe'))
    write(ROOT/'packaged-sidecar-frozen.json', dict(head=HEAD, source_inputs_sha256=sha(ROOT/'packaged-build-inputs.json'),
        build_log_sha256=build['log_sha256'], bundle=str(bundle), files=files,
        frozen_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), weights='NOT_BUNDLED'))
    # Every byte is pinned before the tests; neither source Python nor a borrowed bundle is allowed.
    shutil.copytree(SOURCE/'apps/desktop/frontend/dist', checkout/'apps/desktop/frontend/dist')
    testenv = rust_env('packaged-tests')
    testenv['M2RC1_PACKAGED'] = '1'
    testenv.pop('M2RC1_SRC_ROOT'); testenv.pop('M2RC1_PYTHON')
    result = run('packaged-tests', ['cargo','test','--locked','--offline','packaged_sidecar_tests::','--','--nocapture'],
        checkout/'apps/desktop/src-tauri', testenv,
        unset=('M2RC1_SRC_ROOT','M2RC1_PYTHON','RUST_TEST_THREADS'))
    assert all(sha(bundle/p['path'])==p['sha256'] for p in files), 'bundle changed during tests'
    write(ROOT/'packaged-postcheck.json', dict(exit=result['exit'], frozen_sha256=sha(ROOT/'packaged-sidecar-frozen.json'),
        all_files_unchanged=True, files=len(files)))


if __name__ == '__main__':
    {'setup': setup_and_pin, 'frontend': frontend, 'parallel': default_parallel,
     'isolated': isolated_registry, 'packaged': packaged}[sys.argv[1]]()
