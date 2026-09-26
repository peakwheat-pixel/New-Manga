"""Independent recount of Contract-cited source facts at fixed base 7478f72.

Checks (not inherited from the Owner or r2 conclusions):
  A. src/application/tasks/projection.py -> TaskProjection dataclass field count = 23
  B. src/application/tasks/service.py    -> control_run / recover_running_runs /
     retry_failed_targets / TARGET_NOT_FOUND line numbers
  C. src/application/editing/service.py  -> list_revisions definitions = 0,
     restore_revision / set_revision_pinned present
  D. git grep CredentialRef in src/ at fixed base -> zero hits
  E. Contract §5.1 wire enum vs CommandType members at fixed base
"""
import re
import subprocess
import sys

BASE = '7478f72fe6f9872cae29f4fa12888b5e1f2380f1'


def show(path):
    r = subprocess.run(['git', 'show', f'{BASE}:{path}'],
                       capture_output=True, text=True, encoding='utf-8')
    if r.returncode != 0:
        print('FAILED to read', path, r.stderr)
        sys.exit(1)
    return r.stdout


def grep_lines(text, pattern):
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        if re.search(pattern, line):
            out.append((i, line.rstrip()))
    return out


print('=== A. TaskProjection field count ===')
proj = show('src/application/tasks/projection.py')
lines = proj.splitlines()
start = None
for i, line in enumerate(lines, 1):
    if re.match(r'class TaskProjection\b', line):
        start = i
        break
print('class TaskProjection at line', start)
fields = []
i = start
while i < len(lines):
    line = lines[i]
    if line.strip() and not line.startswith((' ', '\t')) and i > start:
        break
    m = re.match(r'\s{4}(\w+)\s*:', line)
    if m:
        fields.append((i + 1, m.group(1)))
    i += 1
print('field count =', len(fields))
for ln, name in fields:
    print(f'  {ln}: {name}')

print()
print('=== B. service.py control/lifecycle line numbers ===')
svc = show('src/application/tasks/service.py')
for pat in [r'def control_run', r'def recover_running_runs', r'def retry_failed_targets',
            r'TARGET_NOT_FOUND', r'pause_requested', r'INVALID_RUN_TRANSITION']:
    hits = grep_lines(svc, pat)
    print(f'{pat!r}: ' + ', '.join(f':{ln}' for ln, _ in hits[:6]) + (f' (total {len(hits)})' if len(hits) > 6 else ''))
    if pat in (r'def control_run', r'def recover_running_runs', r'def retry_failed_targets'):
        for ln, text in hits:
            print(f'      {ln}: {text.strip()}')

print()
print('=== C. editing/service.py revision API ===')
esvc = show('src/application/editing/service.py')
print('def list_revisions hits:', len(grep_lines(esvc, r'def list_revisions')))
for pat in [r'def restore_revision', r'def set_revision_pinned', r'\.list_revisions\(']:
    for ln, text in grep_lines(esvc, pat):
        print(f'  {pat!r} {ln}: {text.strip()}')

print()
print('=== D. CredentialRef in src/ at fixed base ===')
r = subprocess.run(['git', 'grep', '-c', 'CredentialRef', BASE, '--', 'src/'],
                   capture_output=True, text=True)
print('exit =', r.returncode, '(1 == zero hits)')
print('stdout:', r.stdout.strip() or '(empty)')

print()
print('=== E. CommandType members vs Contract §5.1 enum list ===')
models = show('src/domain/tasks/models.py')
m = re.search(r'class CommandType\(str, Enum\):(.*?)(?=\nclass |\Z)', models, re.S)
members = re.findall(r'^\s{4}(\w+)\s*=\s*"([^"]+)"', m.group(1), re.M)
wire = [v for _, v in members]
print('CommandType member count =', len(wire))
print('values:', wire)

contract = open('doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md', encoding='utf-8').read()
s51 = contract.split('### 5.1 Task command types')[1].split('`PipelineScope`')[0]
listed = re.findall(r'`([a-z_]+)`', s51)
print('Contract §5.1 listed count =', len(listed))
print('listed:', listed)
print('SET EQUAL =', set(listed) == set(wire))
print('missing from contract:', sorted(set(wire) - set(listed)))
print('extra in contract   :', sorted(set(listed) - set(wire)))
