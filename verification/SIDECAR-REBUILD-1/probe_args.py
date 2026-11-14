import json, os, shutil, sqlite3, subprocess, sys
EXE = r"G:\CODEX\New Manga\apps\desktop-avalonia\build\sidecar\core-sidecar\core-sidecar\core_service.exe"
FIX = r"G:\CODEX\New Manga.workspace\task-envs\BOOK-FIXTURE-1\isolated-data"
WORK = r"G:\CODEX\New Manga.workspace\task-envs\SIDECAR-REBUILD-1\fixture-probe2"
COPY = os.path.join(WORK, "data"); LOGS = os.path.join(WORK, "logs")
if os.path.isdir(COPY): shutil.rmtree(COPY)
shutil.copytree(FIX, COPY); os.makedirs(LOGS, exist_ok=True)
def call(p, rid, cmd, payload, minor=3):
    p.stdin.write(json.dumps({"protocol":"new-manga.core","version":{"major":2,"minor":minor},"request_id":rid,"command":cmd,"payload":payload})+"\n"); p.stdin.flush()
    return p.stdout.readline()
for label, args in [("space form", ["--data-root", COPY, "--log-dir", LOGS]),
                    ("equals form", [f"--data-root={COPY}", f"--log-dir={LOGS}"])]:
    if os.path.isdir(COPY): shutil.rmtree(COPY)
    shutil.copytree(FIX, COPY); os.makedirs(LOGS, exist_ok=True)
    p = subprocess.Popen([EXE]+args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    try:
        out = call(p, "r2", "ListBooks", {})
        n = 0
        try:
            n = len(json.loads(out).get("result") or [])
        except Exception: pass
        print(f"[{label}] books returned =", n, "| raw:", out[:160])
    finally:
        try: p.stdin.close()
        except Exception: pass
        try: p.wait(timeout=20)
        except Exception: p.kill()
        err = p.stderr.read()
        line = [l for l in err.splitlines() if "core.schema" in l]
        print("   schema line:", line[0] if line else "(none)")