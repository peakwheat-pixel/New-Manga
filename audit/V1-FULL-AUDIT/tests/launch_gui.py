"""Launch the freshly built current desktop against audit-only data."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / 'audit/V1-FULL-AUDIT'
RUNTIME = ROOT.parent / 'New Manga.workspace/task-env/NEW-MANGA-V1-FULL-AUDIT'
gui = RUNTIME / 'gui'
assert not gui.exists(), 'Use a new attempt directory; do not overwrite a previous session'
env = {k: v for k, v in os.environ.items() if not k.startswith(('M2RC1_', 'M2RC2_', 'M2AC1_', 'NEWMANGA_'))}
pins = {'M2RC1_PYTHON': sys.executable, 'M2RC1_SRC_ROOT': str(ROOT / 'src'),
        'NEWMANGA_DATA_ROOT': str(gui / 'data'), 'M2RC1_DERIVED_ROOT': str(gui / 'derived'),
        'M2RC1_MANAGED_ROOT': str(gui / 'managed'), 'M2RC2_CATALOG_DB': str(gui / 'catalog/catalog.sqlite'),
        'APPDATA': str(gui / 'roaming'), 'LOCALAPPDATA': str(gui / 'local'),
        'TEMP': str(gui / 'temp'), 'TMP': str(gui / 'temp'),
        'WEBVIEW2_USER_DATA_FOLDER': str(gui / 'webview'), 'PYTHONDONTWRITEBYTECODE': '1'}
for key in ['NEWMANGA_DATA_ROOT', 'M2RC1_DERIVED_ROOT', 'M2RC1_MANAGED_ROOT', 'APPDATA', 'LOCALAPPDATA', 'TEMP']:
    Path(pins[key]).mkdir(parents=True, exist_ok=True)
Path(pins['M2RC2_CATALOG_DB']).parent.mkdir(parents=True, exist_ok=True)
env.update(pins)
exe = RUNTIME / 'cargo-target/debug/m2rc1-desktop.exe'
assert exe.is_file()
with (AUDIT / 'logs/gui-stdout.log').open('wb') as out, (AUDIT / 'logs/gui-stderr.log').open('wb') as err:
    start = time.perf_counter()
    process = subprocess.Popen([str(exe)], env=env, cwd=ROOT, stdout=out, stderr=err, creationflags=subprocess.CREATE_NO_WINDOW)
    record = {'pid': process.pid, 'exe': str(exe), 'sha256': hashlib.sha256(exe.read_bytes()).hexdigest(),
              'source_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
              'environment_pins': pins, 'spawn_seconds': round(time.perf_counter() - start, 3),
              'mode': 'fresh debug build / real Python Core / synthetic empty audit data; not installed release'}
    (AUDIT / 'evidence/gui-launch.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    print(json.dumps(record))
