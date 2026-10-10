#!/usr/bin/env python3
"""Validate the committed P02 current-prestart R5 repair package."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

BASE = "4183e7f7cf366c27aa8ad8a0bc7300af48783470"
ALLOWED_FILES = {"doc/00_INDEX.md", "doc/REBASELINE_PLAN.md", "doc/STATUS.md", "doc/tasks/P02.md"}
DOCS = [*sorted(ALLOWED_FILES), "verification/P02/codex-checkpoint-p02-smoke-prestart-r5-followup-package.md"]
REQUIRED = ["Build Gate=BLOCKED", "build=NOT_AUTHORIZED / NOT_RUN", "AC1–AC7=BLOCKED / NOT_RUN", "Hard Build Barrier=EFFECTIVE", "wsb start=NOT_RUN"]


def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()


def blob(path, rev="HEAD"):
    return subprocess.check_output(["git", "cat-file", "blob", f"{rev}:{path}"])


def normalized(text):
    return text.replace("`", "")


def has_hook_cache_state(text):
    return re.search(r"hook/cache(?:\s+\S+)?=BLOCKED / NOT_VERIFIED", normalized(text)) is not None


def allowed(path):
    return path in ALLOWED_FILES or path.startswith("verification/P02/")


def self_check():
    assert allowed("doc/00_INDEX.md")
    assert allowed("verification/P02/example.log")
    assert not allowed("apps/desktop/src-tauri/src/lib.rs")
    assert has_hook_cache_state("hook/cache=BLOCKED / NOT_VERIFIED")
    assert has_hook_cache_state("hook/cache 静态闭包=BLOCKED / NOT_VERIFIED")
    assert not has_hook_cache_state("hook/cache=PASS")
    print("validator self-check: PASS (scope + bare/descriptive hook-cache forms)")


def main():
    self_check()
    head, tree = git("rev-parse", "HEAD"), git("rev-parse", "HEAD^{tree}")
    paths = git("diff", "--name-only", BASE, "HEAD").splitlines()
    outside = [path for path in paths if not allowed(path)]
    print(f"HEAD: {head}")
    print(f"Tree: {tree}")
    print(f"Complete diff path count: {len(paths)}")
    print(f"Out-of-scope path count: {len(outside)}")
    assert not outside, outside

    for name in DOCS:
        text = normalized(Path(name).read_text(encoding="utf-8"))
        missing = [phrase for phrase in REQUIRED if phrase not in text]
        assert not missing, (name, missing)
        assert has_hook_cache_state(text), name
        print(f"{name}: required Gate states=6/6 PASS")

    pointer = "codex-checkpoint-p02-smoke-prestart-r5-followup-package.md"
    for name in ["doc/00_INDEX.md", "doc/REBASELINE_PLAN.md", "doc/STATUS.md"]:
        assert pointer in Path(name).read_text(encoding="utf-8"), name
        print(f"{name}: current recovery pointer PASS")

    status = Path("doc/STATUS.md").read_text(encoding="utf-8")
    assert "当前恢复见 verification/P02/codex-checkpoint-p02-smoke-prestart-r4-review.md" not in status
    print("R5-01: stale R4 current recovery pointer absent")

    for path in [
        "verification/P02/r9f-current-prestart-route-validator-r9.stdout.log",
        "verification/P02/r9f-current-prestart-diff-check-r9.exit",
        "verification/P02/r9f-current-prestart-parent-diff-check-r9.exit",
        "verification/P02/r9f-current-prestart-scope-assertions-r9.stdout.log",
    ]:
        subprocess.check_call(["git", "cat-file", "-e", f"HEAD:{path}"])
    print("R5-02: D13 route/diff/scope run records committed")

    errata = Path("verification/P02/codex-checkpoint-p02-review-response-sha256-eol-errata-r1.md").read_text(encoding="utf-8")
    assert "r9f-current-prestart-scope-assertions-r4.stdout.log" in errata
    assert "r9f-current-prestart-scope-assertions-r5.stdout.log" in errata
    print("R5-03: R2/R3 historical hash-label logs both named")

    assert "hook/cache=BLOCKED / NOT_VERIFIED" in normalized(Path("doc/00_INDEX.md").read_text(encoding="utf-8"))
    print("R5-04: Index hook/cache state present")

    r4 = json.loads(Path("verification/P02/dsh-review-p02-current-prestart-r4.session.json").read_text(encoding="utf-8"))
    assert "3f243b1993dc577ea98aa8130c1a822ac57763a4" in r4["response_sha256_basis"]
    print("R5-05: R4 Git blob hash basis names source commit")

    pairs = [
        ("r2", "9869F229DADD4A173C74B737321270AEF504C5266B2AA2A100CF999B41696612"),
        ("r3", "A07E7DE8DA8C2F1466763EDC037227C39E7E2C5900E616122B19CC3FB5D1A565"),
        ("r4", "A2F962B6494579C162F1D0FD36EE8985819108860967E189A3EA25B3BD04B3B4"),
        ("r5", "A55411B9C664BA5FF407E06CA8C608559B36FEF27CF59040DC21B3D58746297C"),
    ]
    for round_id, expected in pairs:
        path = f"verification/P02/dsh-review-p02-current-prestart-{round_id}.response.md"
        actual = hashlib.sha256(blob(path)).hexdigest().upper()
        assert actual == expected, (round_id, actual, expected)
        print(f"{round_id.upper()} committed response blob SHA: PASS ({actual})")

    for round_id, expected_phrase in [
        ("r6", "hard_build_barrier_preserved: False"),
        ("r7", "doc/00_INDEX.md|wsb start=NOT_RUN|False"),
    ]:
        log = blob(f"verification/P02/r9f-current-prestart-scope-assertions-{round_id}.stdout.log").decode("utf-8-sig")
        code = blob(f"verification/P02/r9f-current-prestart-scope-assertions-{round_id}.exit").decode("utf-8-sig").strip()
        assert expected_phrase in log and code == "1", (round_id, code)
    print("R6/R7 original EXIT=1 records: preserved")


if __name__ == "__main__":
    main()
