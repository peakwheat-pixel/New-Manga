"""SIDECAR-REBUILD-1 / E2-FALLOUT-TRIAGE-1: probe the rebuilt sidecar directly.

Sends core.ping then ListBooks over the NDJSON stdin/stdout channel and prints the raw
responses, so we can see WHY the C# client reports "ListBooks result is not an array".
"""
import json
import subprocess
import sys
import tempfile
import os

EXE = r"G:\CODEX\New Manga\apps\desktop-avalonia\build\sidecar\core-sidecar\core-sidecar\core_service.exe"
WORK = r"G:\CODEX\New Manga.workspace\task-envs\SIDECAR-REBUILD-1\probe-run"
os.makedirs(WORK, exist_ok=True)
root = os.path.join(WORK, "data")
logs = os.path.join(WORK, "logs")
os.makedirs(root, exist_ok=True)
os.makedirs(logs, exist_ok=True)


def send(proc, request_id, command, payload, minor=3):
    frame = {
        "protocol": "new-manga.core",
        "version": {"major": 2, "minor": minor},
        "request_id": request_id,
        "command": command,
        "payload": payload,
    }
    proc.stdin.write(json.dumps(frame) + "\n")
    proc.stdin.flush()
    line = proc.stdout.readline()
    return line


proc = subprocess.Popen(
    [EXE, f"--data-root={root}", f"--log-dir={logs}"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    encoding="utf-8",
    errors="replace",
)
try:
    ping = send(proc, "req-1", "core.ping", {})
    print("=== core.ping ===")
    print(ping[:600])

    books = send(proc, "req-2", "ListBooks", {})
    print("=== ListBooks (minor=3) ===")
    print(books[:800])
finally:
    try:
        proc.stdin.close()
    except Exception:
        pass
    try:
        proc.wait(timeout=15)
    except Exception:
        proc.kill()
    err = proc.stderr.read()
    if err:
        print("=== stderr (tail) ===")
        print(err[-1500:])

