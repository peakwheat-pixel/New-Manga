"""Read-only documentation/scope check; does not execute a collector."""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / 'doc/contracts/M2_DERIVED_PREVIEW_GC_DESIGN.md'
BASE = 'ab4b7c110a7c828f20d2d0787bd71144336d2e44'


def git(*args):
    p = subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
    print('COMMAND=git ' + ' '.join(args))
    print(p.stdout.strip())
    print('EXIT=' + str(p.returncode))
    assert p.returncode == 0, p.stderr
    return p.stdout.strip()


head = git('rev-parse', 'HEAD')
assert git('rev-parse', '--path-format=absolute', '--git-common-dir').replace('\\', '/') == 'G:/CODEX/New Manga/.git'
for dep in ['44859014', '0a7e0d5b']:
    git('merge-base', '--is-ancestor', dep, head)
assert not git('diff', BASE, '--name-only', '--', 'src', 'apps', 'tests', 'requirements.txt', 'packaging')
git('diff', '--check')
git('ls-files', '--others', '--exclude-standard')
text = DESIGN.read_text(encoding='utf-8')
for label in ['D1', 'D2', 'K1', 'K2', 'K3', 'K4', 'K5', 'K6', 'U1', 'U2', 'U3', 'U4', 'U5', 'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7']:
    assert re.search(r'\| ' + label + r'(?: \|| )', text), label
for token in ['NOT_RUN', 'UNKNOWN', 'pinned', 'current', 'retired', '静默', 'Managed', 'revoke', 'FILE_SHARE_READ', 'BLOCKED']:
    assert token in text, token
citations = re.findall(r'`((?:src|apps)/[^` :]+):(\d+)(?:[–-]\d+)?[^`]*`', text)
assert len(citations) >= 8
for name, line in citations:
    source = ROOT / name
    assert source.is_file(), name
    assert 1 <= int(line) <= len(source.read_text(encoding='utf-8-sig').splitlines()), (name, line)
for name in re.findall(r'\| ((?:src|apps|tests)/[^ |]+)', text):
    assert (ROOT / name).exists(), name
print('PASS: dependency ancestry, zero product-tree delta, design matrix/Gate completeness, source paths/line bounds')
print('NOT_RUN: future implementation/runtime/native locks/product regression; design check is not a deletion-safety test')
