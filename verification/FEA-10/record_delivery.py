"""Read-only inventory of allowed changes/resources; writes only FEA-10 evidence."""
from pathlib import Path
from datetime import datetime, timezone
import fnmatch
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / 'verification/FEA-10'


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], encoding='utf-8').strip()


def sha(path):
    return hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()


def main():
    for name in ('changed-files.txt', 'DELIVERY-MANIFEST.json', 'RESOURCE-MANIFEST.json', 'logs/scope.log'):
        (EVIDENCE / name).touch(exist_ok=True)
    task = (ROOT / 'doc/tasks/FEA-10.md').read_text(encoding='utf-8')
    block = task.split('allowed_paths:\n', 1)[1].split('out_of_scope:', 1)[0]
    allowed = [line.strip()[2:] for line in block.splitlines() if line.strip().startswith('- ')]
    tracked = git('diff', '--name-only').splitlines()
    untracked = git('ls-files', '--others', '--exclude-standard').splitlines()
    changed = sorted(set(tracked + untracked))
    outside = [path for path in changed if not any(fnmatch.fnmatchcase(path, pattern) for pattern in allowed)]
    fea09 = git('diff', '--name-only', '--', 'verification/FEA-09')
    scope = ['DataRoot=N/A (read-only Git scope); fixtures=G:/CODEX/New Manga.workspace/FEA-10/fixtures/',
             'COMMAND=git diff --name-only', *tracked,
             'COMMAND=git ls-files --others --exclude-standard', *untracked,
             'COMMAND=compare all changed/untracked paths against doc/tasks/FEA-10.md allowed_paths',
             'OUT_OF_SCOPE=' + json.dumps(outside),
             'FEA09_DIFF=' + ('EMPTY' if not fea09 else fea09),
             'EXIT=' + ('1' if outside or fea09 else '0')]
    (EVIDENCE / 'logs/scope.log').write_text('\n'.join(scope) + '\n', encoding='utf-8')
    (EVIDENCE / 'changed-files.txt').write_text('\n'.join(changed) + '\n', encoding='utf-8')
    fixture_root = ROOT.parent / 'New Manga.workspace/FEA-10/fixtures'
    cases = []
    for case in sorted(fixture_root.iterdir()):
        if not case.is_dir():
            continue
        values = []
        errors = []
        for path in sorted(case.rglob('*')):
            if not path.is_file():
                continue
            try:
                values.append({'path': path.relative_to(case).as_posix(), 'bytes': path.stat().st_size, 'sha256': sha(path)})
            except OSError as error:
                errors.append({'path': path.relative_to(case).as_posix(), 'error_type': type(error).__name__})
        cases.append({'case': case.name, 'file_count': len(values), 'bytes': sum(row['bytes'] for row in values),
                      'aggregate_sha256': hashlib.sha256(json.dumps(values, sort_keys=True).encode()).hexdigest(),
                      'unreadable': errors, 'disposition': 'PRESERVE_REFERENCED'})
    resources = {'fixture_root': str(fixture_root), 'cases': cases, 'cleanup_performed': False,
                 'early_system_temp': {'disposition': 'PRESERVE_UNKNOWN', 'scanned': False, 'cleanup_performed': False},
                 'new_worktree': None, 'new_dependency_or_model': None,
                 'build_artifacts': {'source': 'apps/desktop-avalonia/**/bin, obj', 'disposition': 'PRESERVE_REFERENCED'}}
    (EVIDENCE / 'RESOURCE-MANIFEST.json').write_text(json.dumps(resources, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    entries = []
    excluded_docs = [relative for relative in changed if relative.startswith('doc/')]
    for relative in changed:
        if relative == 'verification/FEA-10/DELIVERY-MANIFEST.json' or relative.startswith('doc/'):
            continue
        path = ROOT / relative
        if path.is_file():
            entries.append({'path': relative, 'bytes': path.stat().st_size, 'sha256': sha(path)})
    delivery = {'head': git('rev-parse', 'HEAD'), 'branch': git('branch', '--show-current'),
                'excluded_docs': excluded_docs,
                'created_at': datetime.now(timezone.utc).isoformat(), 'uncommitted': True,
                'self_hash_excluded': True, 'files': entries, 'out_of_scope': outside}
    (EVIDENCE / 'DELIVERY-MANIFEST.json').write_text(json.dumps(delivery, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('changed_files=' + str(len(changed)))
    print('out_of_scope=' + json.dumps(outside))
    print('FEA09_DIFF=' + ('EMPTY' if not fea09 else fea09))
    return 1 if outside or fea09 else 0


if __name__ == '__main__':
    raise SystemExit(main())
