"""E2-FALLOUT-TRIAGE-1: open a COPY of the book fixture with the rebuilt sidecar.

If ListBooks returns [] here while the fixture has a library.db with books, the root cause is a
schema/version mismatch between the fixture data and the rebuilt sidecar (schema v14) -- i.e. a
data-layer incompatibility, not a test-harness path problem.
"""
import json
import os
import shutil
import sqlite3
import subprocess
import sys

EXE = r"G:\CODEX\New Manga\apps\desktop-avalonia\build\sidecar\core-sidecar\core-sidecar\core_service.exe"
FIXTURE = r"G:\CODEX\New Manga.workspace\task-envs\BOOK-FIXTURE-1\isolated-data"
WORK = r"G:\CODEX\New Manga.workspace\task-envs\SIDECAR-REBUILD-1\fixture-probe"
COPY = os.path.join(WORK, "data")
LOGS = os.path.join(WORK, "logs")

print("=== fixture source ===")
print("exists:", os.path.isdir(FIXTURE))
db = os.path.join(FIXTURE, "library.db")
print("library.db exists:", os.path.isfile(db))
if os.path.isfile(db):
    try:
        conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [r[0] for r in cur.fetchall()]
        print("tables:", tables[:20])
        for t in ("books", "chapters", "pages"):
            if t in tables:
                cur.execute(f"SELECT COUNT(*) FROM {t}")
                print(f"  count({t}) =", cur.fetchone()[0])
        for probe in ("schema_version", "meta", "settings"):
            if probe in tables:
                cur.execute(f"SELECT * FROM {probe} LIMIT 5")
                print(f"  rows({probe}) =", cur.fetchall()[:5])
        cur.execute("PRAGMA user_version")
        print("PRAGMA user_version =", cur.fetchone()[0])
        conn.close()
    except Exception as exc:
        print("sqlite error:", exc)

if os.path.isdir(COPY):
    shutil.rmtree(COPY)
shutil.copytree(FIXTURE, COPY)
os.makedirs(LOGS, exist_ok=True)
print("copied fixture ->", COPY)


def call(proc, rid, command, payload, minor=3):
    frame = {
        "protocol": "new-manga.core",
        "version": {"major": 2, "minor": minor},
        "request_id": rid,
        "command": command,
        "payload": payload,
    }
    proc.stdin.write(json.dumps(frame) + "\n")
    proc.stdin.flush()
    return proc.stdout.readline()


proc = subprocess.Popen(
    [EXE, f"--data-root={COPY}", f"--log-dir={LOGS}"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    text=True, encoding="utf-8", errors="replace",
)
try:
    print("=== ping ===")
    print(call(proc, "r1", "core.ping", {})[:300])
    print("=== ListBooks on fixture copy ===")
    out = call(proc, "r2", "ListBooks", {})
    print(out[:800])
finally:
    try:
        proc.stdin.close()
    except Exception:
        pass
    try:
        proc.wait(timeout=20)
    except Exception:
        proc.kill()
    err = proc.stderr.read()
    if err:
        print("=== stderr (tail) ===")
        print(err[-2000:])
