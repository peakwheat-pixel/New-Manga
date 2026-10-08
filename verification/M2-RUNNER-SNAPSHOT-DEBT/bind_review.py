"""Bind a known code/review head before committing only its evidence."""
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
reviewed = sys.argv[1]
source = "cfb5d2eecc4d8ab7a3159cdbb1d5812547bb5cd2"


def git(*args):
    print("COMMAND=" + json.dumps(["git", *args]))
    result = subprocess.run(["git", *args], capture_output=True)
    if args and args[0] == "show":
        print("SOURCE_CONTENT_BYTES_SHA256=" + hashlib.sha256(result.stdout).hexdigest())
    else:
        print(result.stdout.decode("utf-8"), end="")
    print(result.stderr.decode("utf-8"), end="")
    print("EXIT=" + str(result.returncode))
    assert result.returncode == 0
    return result.stdout.decode("utf-8").strip()


git("diff", "--name-only", "6afbd1ba", "653a0062")
git("rev-parse", "653a0062^1")
git("show", "968c8f34601b72667831f1fd15bb20cd2c8f3cb7:apps/desktop/src-tauri/src/main.rs")
assert not git("diff", "--name-only", "968c8f34601b72667831f1fd15bb20cd2c8f3cb7", source, "--", "apps/desktop/src-tauri/src/main.rs")
current = git("rev-parse", "HEAD")
git("merge-base", "--is-ancestor", reviewed, current)
print("ACTUAL_EVIDENCE_PARENT_HEAD=" + current)
git("diff", "--name-only", reviewed, current)
print("FIXED_REVIEWED_CODE_HEAD=" + reviewed)
git("rev-parse", "41d77f98")
git("diff", "--name-only", source, "41d77f98")
git("diff", "--name-only", source, reviewed)
assert not git("diff", "--name-only", source, reviewed, "--", "src", "apps", "tests")
git("diff", "--check", source, reviewed)
for path in ["verification/M2-RC2/run_e2e.py", "packaging/m2ac5/run_clean_start_e2e.py"]:
    old = ast.parse(git("show", source + ":" + path))
    new = ast.parse(git("show", reviewed + ":" + path))
    old.body = old.body[1:]
    new.body = new.body[1:]
    assert ast.dump(old, include_attributes=False) == ast.dump(new, include_attributes=False)
    print("AST_EXCLUDING_DOCSTRING_IDENTICAL=" + path + "; EXIT=0")
for report in Path("doc/reviews").glob("M2-RUNNER-SNAPSHOT-DEBT-*-dsh-r*.md"):
    blob = subprocess.check_output(["git", "show", reviewed + ":" + report.as_posix()])
    print("REPORT_CONTENT_BYTES_SHA256=" + report.name + ":" + hashlib.sha256(blob).hexdigest())
print("BINDING_PASS; raw evidence appended after this fixed code head")
