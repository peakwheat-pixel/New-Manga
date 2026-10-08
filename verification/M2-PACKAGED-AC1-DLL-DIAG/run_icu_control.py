"""Counterfactual on an owned copy; preserve the original ICU bytes by renaming."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import uuid

root = Path(__file__).resolve().parents[2]
task = Path(__file__).resolve().parent
source = task / "lab/20261008-100953/core-sidecar"
assert source.resolve().is_relative_to((task / "lab").resolve())
lab = task / "lab" / ("icu-control-" + uuid.uuid4().hex[:8])
lab.mkdir()
bundle = lab / "core-sidecar"
shutil.copytree(source, bundle)
meta = json.loads((root / "verification/M2-RUNNER-SNAPSHOT-DEBT/build-fingerprint.json").read_text(encoding="utf-8"))
exe = bundle / "acceptance_bridge.exe"
assert hashlib.sha256(exe.read_bytes()).hexdigest() == meta["sidecar_exes"]["acceptance_bridge.exe"]
icu = bundle / "_internal/icuuc.dll"
assert hashlib.sha256(icu.read_bytes()).hexdigest() == hashlib.sha256((source / "_internal/icuuc.dll").read_bytes()).hexdigest()
win = os.environ["SystemRoot"]
env = {"SystemRoot": win, "WINDIR": win, "PATH": win + "/System32;" + win, "PATHEXT": ".EXE;.COM", "M2AC1_TEST_MODE": "1", "QT_QPA_PLATFORM": "offscreen"}
for key, name in [("APPDATA", "roaming"), ("LOCALAPPDATA", "local"), ("TEMP", "temp"), ("TMP", "temp"), ("NEWMANGA_DATA_ROOT", "data")]:
    dest = lab / name
    dest.mkdir(exist_ok=True)
    env[key] = str(dest)
head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
rows = []
for case in ["original", "owned_icu_renamed"]:
    if case != "original":
        renamed = icu.with_name("icuuc.dll.diagnostic-preserved")
        assert not renamed.exists()
        icu.rename(renamed)
    start = time.monotonic()
    r = subprocess.run([str(exe)], cwd=bundle, env=env, stdin=subprocess.DEVNULL, capture_output=True, timeout=20)
    log = task / "raw" / ("icu-control-" + case + ".log")
    log.write_bytes(("HEAD=" + head + "\nCOMMAND=" + json.dumps([str(exe)]) + "\nENV=" + json.dumps(env) + "\nSTDIN=EOF; CASE=" + case + "\n").encode() + r.stdout + r.stderr + ("\nEXIT=" + str(r.returncode) + "; ELAPSED=" + str(round(time.monotonic()-start,2)) + "s\n").encode())
    rows.append({"case": case, "exit": r.returncode, "log": str(log), "qtgui_import_error": b"importing QtGui" in r.stderr})
print(json.dumps(rows))
(task / "raw/icu-control-result.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
