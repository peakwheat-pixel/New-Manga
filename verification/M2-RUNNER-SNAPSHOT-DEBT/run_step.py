"""Capture exact command/head/exit without truncating build evidence."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

root = Path(__file__).resolve().parents[2]
log = root / "verification/M2-RUNNER-SNAPSHOT-DEBT" / sys.argv[1]
log.parent.mkdir(parents=True, exist_ok=True)
command = sys.argv[2:]
with log.open("w", encoding="utf-8") as output:
    output.write(f"HOST=Windows; HARNESS_PYTHON={sys.executable}; CWD={os.getcwd()}\n")
    output.write("HEAD=" + subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip() + "\n")
    output.write("COMMAND=" + json.dumps(command, ensure_ascii=False) + "\n")
    output.flush()
    start = time.monotonic()
    result = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT)
    output.write(f"\nEXIT={result.returncode}; ELAPSED={time.monotonic()-start:.1f}s\n")
print(f"LOG={log}; EXIT={result.returncode}")
sys.exit(result.returncode)
