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
    result = subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8")
    if args and args[0] == "show":
        print("SOURCE_CONTENT_BYTES_SHA256=" + hashlib.sha256(result.stdout.encode("utf-8")).hexdigest())
    else:
        print(result.stdout, end="")
    print(result.stderr, end="")
    print("EXIT=" + str(result.returncode))
    assert result.returncode == 0
    return result.stdout.strip()


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
