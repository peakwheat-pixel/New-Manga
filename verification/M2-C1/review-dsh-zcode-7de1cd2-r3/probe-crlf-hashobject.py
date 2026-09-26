"""Independent probe: does the Owner's blob-equivalence command set have
discriminating power in THIS checkout (core.autocrlf=true)?

Owner 03-blob-equivalence.md lists:
  git hash-object doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md
and claims the Owner file / draft blob SHA-1 are both
4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3.
"""
import subprocess
import hashlib
import os

F = 'doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md'


def run(args, **kw):
    return subprocess.run(args, capture_output=True, **kw)


print('cwd =', os.getcwd())
print('core.autocrlf =', run(['git', 'config', '--get', 'core.autocrlf']).stdout.decode().strip())
print()
print('[1] git hash-object <worktree-path>        ->',
      run(['git', 'hash-object', F]).stdout.decode().strip())
print('[2] git hash-object --no-filters <path>    ->',
      run(['git', 'hash-object', '--no-filters', F]).stdout.decode().strip())
print('[3] git hash-object --path=<path> <path>   ->',
      run(['git', 'hash-object', '--path=' + F, F]).stdout.decode().strip())
print('[4] git rev-parse HEAD:<path>              ->',
      run(['git', 'rev-parse', 'HEAD:' + F]).stdout.decode().strip())
print('[5] git rev-parse :<path> (index)          ->',
      run(['git', 'rev-parse', ':' + F]).stdout.decode().strip())
print()
raw = open(F, 'rb').read()
lf = raw.replace(b'\r\n', b'\n')
print('worktree bytes =', len(raw), ' CRLF =', raw.count(b'\r\n'))
print('LF-normalized bytes =', len(lf))
print('sha1(LF-normalized) via git hash-object --stdin ->',
      run(['git', 'hash-object', '--stdin'], input=lf).stdout.decode().strip())
print()
print('python hashlib.sha256(raw worktree bytes)  ->', hashlib.sha256(raw).hexdigest())
print('python hashlib.sha256(LF-normalized bytes) ->', hashlib.sha256(lf).hexdigest())
print()
print('git check-attr -a ->', run(['git', 'check-attr', '-a', '--', F]).stdout.decode().strip() or '(none)')
print('.gitattributes exists ->', os.path.exists('.gitattributes'))
print()
print('Owner-claimed blob SHA-1  = 4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3')
print('Owner-claimed SHA-256     = c04b5af59c1c36ecaf862c9b63e8e410219966ea3d1e526e711ea19904b6f0d8')
