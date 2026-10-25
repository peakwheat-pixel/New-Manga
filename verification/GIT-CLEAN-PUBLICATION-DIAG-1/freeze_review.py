"""Freeze a supplementary local-only review package, retaining every original byte."""
from pathlib import Path
import json
import shutil
import sys

from diagnose import REPO, ROOT, PARENT, HEAD, sha, write

EVIDENCE = REPO / 'verification/GIT-CLEAN-PUBLICATION-1'
PACKAGE = PARENT / 'review-package-r2'


def collect_runs(value):
    if isinstance(value, dict):
        if 'log' in value and 'exit' in value:
            yield value
        for child in value.values():
            yield from collect_runs(child)
    elif isinstance(value, list):
        for child in value:
            yield from collect_runs(child)


def freeze():
    assert not PACKAGE.exists(), 'new package required; old freezes must not be overwritten'
    PACKAGE.mkdir()
    metadata = {}
    for path in sorted(EVIDENCE.iterdir()):
        if path.is_file() and path.suffix in ('.json', '.log', '.py', '.md'):
            shutil.copyfile(path, PACKAGE / path.name)
            if path.suffix == '.json':
                for run in collect_runs(json.loads(path.read_text(encoding='utf-8'))):
                    name = Path(run['log']).name
                    assert (EVIDENCE / name).is_file(), f'missing referenced log: {name}'
                    metadata.setdefault(name, []).append((path.name, run))
    logs = sorted(EVIDENCE.glob('*.log'))
    assert len(logs) == 19
    for log in logs:
        assert log.name in metadata, f'no machine exit metadata: {log.name}'
        records = metadata[log.name]
        assert len({run['exit'] for _, run in records}) == 1, log.name
        source, run = records[0]
        header = dict(provenance='RETROSPECTIVE_ENVELOPE_FROM_EXISTING_CHECKS_NOT_ORIGINAL_RUN_HEADER',
                      raw_log=log.name, raw_sha256=sha(log), metadata=source,
                      metadata_sha256=sha(EVIDENCE/source), argv=run['argv'], cwd=run['cwd'],
                      shell=run.get('shell', 'UNRECORDED'), venv='UNRECORDED',
                      env=run.get('env_overrides', {k:v for k,v in run.items() if k in
                          ('PYTHONPATH','PYTHONUSERBASE','isolation_root')}),
                      env_completeness='only what original metadata recorded; missing fields UNRECORDED')
        target = PACKAGE/'log-envelopes'/log.name
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(('RUN_HEADER '+json.dumps(header, ensure_ascii=False)+'\n'
                            +f"EXIT={run['exit']} (reported by original checks; not a rerun)\n").encode()
                           +log.read_bytes())
    disposition = REPO/'audit/V1-FULL-AUDIT/evidence/push-material-disposition.json'
    objects = json.loads(disposition.read_text(encoding='utf-8'))['objects']
    summary = [dict(outer_object=r['outer_object'], embedded_git_object=r['embedded_git_object'],
                    payload_sha256=r['payload_sha256']) for r in objects]
    assert len(summary)==169 and len({r[k] for r in summary for k in ('outer_object','embedded_git_object')})==338
    write(PACKAGE/'forbidden-object-fingerprints.json', dict(source_path=str(disposition),
          source_sha256=sha(disposition), disposition='LOCAL_ONLY_NO_UPLOAD', objects=summary))
    dbs = json.loads((ROOT/'core-r2-source-pins.json').read_text(encoding='utf-8'))
    shutil.copyfile(ROOT/'core-r2-source-pins.json', PACKAGE/'core-r2-source-pins.json')
    for row in dbs['records']:
        target = PACKAGE/'core-db'/Path(row['frozen_path']).parent.name/'library.db'
        target.parent.mkdir(parents=True)
        shutil.copyfile(row['frozen_path'], target)
        assert sha(target)==row['sha256']
    clarified = json.loads((EVIDENCE/'checks-r4.json').read_text(encoding='utf-8'))
    for row in clarified:
        if row['name'].startswith('rust'):
            row['filtered_tests_reason']='12 packaged_sidecar_tests require a separately built and SHA-frozen sidecar; original run did not build one'
    write(PACKAGE/'checks-r4-clarified.json', dict(derived_from_sha256=sha(EVIDENCE/'checks-r4.json'),
          note='supplement only, original checks-r4.json unchanged', runs=clarified))
    write(PACKAGE/'PACKAGE_MANIFEST.json', dict(candidate_head=HEAD, local_only=True,
        delivery='candidate Git objects only; never zip/copy the live working directory or this evidence package',
        historical_logs='raw 19 logs unchanged; retrospective envelopes are explicitly labelled',
        files=[dict(path=p.relative_to(PACKAGE).as_posix(), sha256=sha(p), bytes=p.stat().st_size)
               for p in sorted(PACKAGE.rglob('*')) if p.is_file()]))
    verify()


def verify():
    manifest = json.loads((PACKAGE/'PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
    assert all(sha(PACKAGE/r['path'])==r['sha256'] for r in manifest['files'])
    for file in PACKAGE.glob('*.json'):
        for run in collect_runs(json.loads(file.read_text(encoding='utf-8'))):
            assert (PACKAGE/Path(run['log']).name).is_file(), run['log']
    for file in (PACKAGE/'log-envelopes').glob('*.log'):
        assert b'EXIT=' in file.read_bytes() and b'RETROSPECTIVE_ENVELOPE' in file.read_bytes()
    print('Frozen package verified:', len(manifest['files']), 'files; 19 labelled envelopes; 338 forbidden IDs')


if __name__=='__main__':
    {'freeze':freeze, 'verify':verify}[sys.argv[1]]()
