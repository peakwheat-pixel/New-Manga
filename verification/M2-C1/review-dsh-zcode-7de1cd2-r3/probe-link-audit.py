"""Independent relative-link resolution audit over the M2-C1 reviewed_head tree.

Only reads. Resolves every Markdown inline link and every backticked repo path
reference found in the Owner delivery files, against the reviewed_head tree
(= HEAD of this review checkout) and, where absent, against the frozen adopted
object ac38dede.

Scope: the 8 paths added by 7478f72..b237728 plus the Qoder review artefacts
(read from their own commit). The Qoder artefacts are NOT part of reviewed_head
and are reported separately.
"""
import re
import subprocess

HEAD = 'b2377288680569dbee4e2299fd7dfae4de067c54'
AC38 = 'ac38dede84ff22290c9b9d579c1372c8184a7bd5'
QODER = '0d73983a5e1f37f104c76d8bd4c70c6f98fa36f5'

OWNER_FILES = [
    'doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md',
    'doc/handoffs/M2-C1-zcode-7de1cd2.md',
    'verification/M2-C1/zcode-owner/00-environment.md',
    'verification/M2-C1/zcode-owner/01-source-trace-owner-base.md',
    'verification/M2-C1/zcode-owner/02-decision-log.md',
    'verification/M2-C1/zcode-owner/03-blob-equivalence.md',
    'verification/M2-C1/zcode-owner/04-git-scope-check.md',
    'verification/M2-C1/zcode-owner/05-drift-and-links.md',
]


def blob(rev, path):
    r = subprocess.run(['git', 'cat-file', '-e', f'{rev}:{path}'],
                       capture_output=True)
    return r.returncode == 0


def show(rev, path):
    return subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True,
                          text=True, encoding='utf-8').stdout


def resolve(rel_from_file, target):
    """Resolve a relative link target in POSIX form against the file dir."""
    base = rel_from_file.rsplit('/', 1)[0] if '/' in rel_from_file else ''
    parts = base.split('/') if base else []
    for seg in target.split('/'):
        if seg in ('', '.'):
            continue
        if seg == '..':
            if parts:
                parts.pop()
        else:
            parts.append(seg)
    return '/'.join(parts)


LINK_RE = re.compile(r'\[[^\]]*\]\(([^)\s]+)\)')
CODE_PATH_RE = re.compile(r'`((?:doc|src|tests|verification|packaging)/[A-Za-z0-9_./\-]+\.(?:md|py|log|txt|json|qml|ps1))`')

report = []

for f in OWNER_FILES:
    text = show(HEAD, f)
    print(f'### {f}')
    for kind, rx in (('md-link', LINK_RE), ('code-path', CODE_PATH_RE)):
        for m in rx.finditer(text):
            raw = m.group(1)
            line_no = text[:m.start()].count('\n') + 1
            if raw.startswith(('http://', 'https://', '#')):
                continue
            target = raw.split('#')[0]
            if not target:
                continue
            if kind == 'md-link':
                if not raw.startswith(('..', '.')):
                    resolved = target  # repo-root style link
                else:
                    resolved = resolve(f, target)
            else:
                resolved = target
            at_head = blob(HEAD, resolved)
            at_ac38 = blob(AC38, resolved)
            status = 'RESOLVES@HEAD' if at_head else ('MISSING@HEAD/BROKEN' if not at_ac38
                                                     else 'MISSING@HEAD (present@ac38)')
            print(f'  L{line_no:<4} [{kind:9}] {raw}')
            print(f'        resolved={resolved} -> {status}')
            report.append((f, line_no, kind, raw, resolved, status))
    print()

print('=== SUMMARY of non-resolving references inside reviewed_head ===')
bad = [r for r in report if r[5] != 'RESOLVES@HEAD']
for f, ln, kind, raw, resolved, status in bad:
    print(f'  {f}:{ln} [{kind}] {raw} -> {resolved} :: {status}')
print(f'  total references checked = {len(report)}; non-resolving = {len(bad)}')

print()
print('=== Qoder review artefacts (NOT in reviewed_head) link check ===')
qfiles = subprocess.run(['git', 'ls-tree', '-r', '--name-only', QODER,
                         '--', 'doc/reviews/', 'verification/M2-C1/'],
                        capture_output=True, text=True, encoding='utf-8').stdout.split()
for f in qfiles:
    if not f.endswith('.md'):
        continue
    text = show(QODER, f)
    for m in LINK_RE.finditer(text):
        raw = m.group(1)
        line_no = text[:m.start()].count('\n') + 1
        if raw.startswith(('http://', 'https://', '#')):
            continue
        target = raw.split('#')[0]
        resolved = resolve(f, target) if raw.startswith(('..', '.')) else target
        at_q = blob(QODER, resolved)
        at_head = blob(HEAD, resolved)
        at_ac38 = blob(AC38, resolved)
        print(f'  {f}:{line_no} {raw} -> {resolved} :: @qoder={at_q} @reviewed_head={at_head} @ac38={at_ac38}')
