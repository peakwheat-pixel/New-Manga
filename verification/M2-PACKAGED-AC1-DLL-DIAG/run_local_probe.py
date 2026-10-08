"""Run the frozen DSH probe with pinned inputs and isolated child data."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

root = Path(__file__).resolve().parents[2]
task = Path(__file__).resolve().parent
meta = json.loads((root / "verification/M2-RUNNER-SNAPSHOT-DEBT/build-fingerprint.json").read_text(encoding="utf-8"))
# The NSIS installer is under target/release/bundle/nsis; the bundle is under target/core-sidecar.
bundle = Path(meta["installer"]).parents[3] / "core-sidecar/core-sidecar"
mode = sys.argv[1]
assert mode in ("static", "copy")
run_id = mode + "-" + uuid.uuid4().hex[:10]
lab = task / "lab" / run_id
lab.mkdir(parents=True)
raw = task / "raw"
raw.mkdir(exist_ok=True)

def sha(path):
    with Path(path).open("rb") as fh:
        return hashlib.file_digest(fh, "sha256").hexdigest()

assert sha(meta["installer"]) == meta["installer_sha256"]
actual = {name: sha(bundle / name) for name in meta["sidecar_exes"]}
assert actual == meta["sidecar_exes"]
head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
cmd = [r"C:/Program Files/PowerShell/7/pwsh.exe", "-NoProfile", "-File", str(task / "probe/run_dll_diag_probe.ps1")]
install = json.loads((root / "verification/M2-RUNNER-SNAPSHOT-DEBT/raw/packaged/cleanstart-gate.json").read_text(encoding="utf-8"))["install_dir"]
cmd += ["-InstallDir", install]
if mode == "copy":
    cmd.append("-CopyBundle")
win = os.environ.get("SystemRoot", r"C:/Windows")
env = {"SystemRoot": win, "WINDIR": win, "ComSpec": win + r"/System32/cmd.exe", "PATH": win + r"/System32;" + win, "PATHEXT": ".COM;.EXE;.BAT;.CMD"}
for key, sub in [("APPDATA", "roaming"), ("LOCALAPPDATA", "local"), ("TEMP", "temp"), ("TMP", "temp"), ("NEWMANGA_DATA_ROOT", "data")]:
    dest = lab / sub
    dest.mkdir(exist_ok=True)
    env[key] = str(dest)
log = raw / (run_id + ".log")
start = time.monotonic()
with log.open("wb") as out:
    out.write(("HEAD=" + head + "\nCOMMAND=" + json.dumps(cmd) + "\nSTDIN=EOF; CHILD_ENV=" + json.dumps(env) + "\nINPUT_SHA256=" + json.dumps(actual) + "\n").encode("utf-8"))
    out.flush()
    proc = subprocess.Popen(cmd, cwd=lab, env=env, stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT)
    timed_out = False
    try:
        code = proc.wait(timeout=120)
    except subprocess.TimeoutExpired:
        timed_out = True
        subprocess.run([win + r"/System32/taskkill.exe", "/PID", str(proc.pid), "/T", "/F"], stdout=out, stderr=subprocess.STDOUT)
        code = proc.wait(timeout=10)
    out.write(("\nEXIT=" + str(code) + "; TIMEOUT=" + str(timed_out) + "; ELAPSED=" + str(round(time.monotonic() - start, 2)) + "s\n").encode("utf-8"))
print("LOG=" + str(log) + "; EXIT=" + str(code))
sys.exit(124 if timed_out else code)
