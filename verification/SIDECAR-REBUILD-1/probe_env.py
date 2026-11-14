import json, os, shutil, subprocess
EXE = r"G:\CODEX\New Manga\apps\desktop-avalonia\build\sidecar\core-sidecar\core-sidecar\core_service.exe"
FIX = r"G:\CODEX\New Manga.workspace\task-envs\BOOK-FIXTURE-1\isolated-data"
WORK = r"G:\CODEX\New Manga.workspace\task-envs\SIDECAR-REBUILD-1\fixture-probe3"
COPY = os.path.join(WORK, "data"); LOGS = os.path.join(WORK, "logs")
if os.path.isdir(WORK): shutil.rmtree(WORK)
shutil.copytree(FIX, COPY); os.makedirs(LOGS, exist_ok=True)
env = dict(os.environ); env["NEWMANGA_DATA_ROOT"] = COPY
p = subprocess.Popen([EXE, "--log-dir", LOGS], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", env=env)
def call(rid, cmd, payload):
    p.stdin.write(json.dumps({"protocol":"new-manga.core","version":{"major":2,"minor":3},"request_id":rid,"command":cmd,"payload":payload})+"\n"); p.stdin.flush()
    return p.stdout.readline()
try:
    out = call("r2", "ListBooks", {})
    try: n = len(json.loads(out).get("result") or [])
    except Exception: n = -1
    print("NEWMANGA_DATA_ROOT -> books returned =", n)
    print("raw:", out[:200])
finally:
    try: p.stdin.close()
    except Exception: pass
    try: p.wait(timeout=20)
    except Exception: p.kill()
    err = p.stderr.read()
    for l in err.splitlines():
        if "core.schema" in l or "core.namespace" in l: print("  ", l[:150])