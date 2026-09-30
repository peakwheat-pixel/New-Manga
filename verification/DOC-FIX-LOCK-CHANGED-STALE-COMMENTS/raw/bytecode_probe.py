"""AC2 bytecode probe (reproducible evidence version, DSH review P2-2).

Compiles the BASE and WORKTREE versions of the two touched files and
recursively compares the ``co_code`` (executable instruction stream) of
every code object. Comments and docstrings never enter ``co_code``.

Claim scope (DSH review P2-2): this probe proves **instruction-stream
(co_code) equality only**. It deliberately does NOT compare ``co_consts``
(where this task's docstring change legitimately lives), ``co_names``,
``co_varnames``, ``co_freevars``/``co_cellvars``,
``co_linetable``/``co_firstlineno`` (both files net +2 lines), or
exception tables. The task's full zero-logic-change proof is
AC1's human-readable diff (comment-only hunks) TOGETHER with this probe.

Usage (repo worktree root, TASK-012-py312 venv):
    python verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/raw/bytecode_probe.py
Exit 0 iff every code object's co_code is EQUAL across all files.
"""
import subprocess
import sys
import types

BASE = "4ed3c044"  # release commit: pre-change blobs
FILES = [
    "src/bootstrap/acceptance_bridge.py",
    "experiments/M2-TA3-A/run_smoke.py",
]


def code_objects(code: types.CodeType, prefix=""):
    yield (prefix + code.co_name, code.co_code)
    for const in code.co_consts:
        if isinstance(const, types.CodeType):
            yield from code_objects(const, prefix + code.co_name + ".")


def main() -> int:
    overall = True
    for rel in FILES:
        base_src = subprocess.run(
            ["git", "show", f"{BASE}:{rel}"], capture_output=True, check=True
        ).stdout.decode("utf-8")
        with open(rel, encoding="utf-8") as handle:
            new_src = handle.read()
        compile(base_src, rel, "exec")  # py_compile equivalence (AC2-1)
        compile(new_src, rel, "exec")
        base_map = dict(code_objects(compile(base_src, rel, "exec")))
        new_map = dict(code_objects(compile(new_src, rel, "exec")))
        if set(base_map) != set(new_map):
            print(f"[{rel}] code-object set changed: "
                  f"{set(base_map) ^ set(new_map)}")
            overall = False
            continue
        diffs = [name for name in base_map if base_map[name] != new_map[name]]
        status = "EQUAL" if not diffs else f"DIFFER: {diffs}"
        print(f"[{rel}] objects={len(base_map)} co_code={status} "
              f"(py_compile OK both)")
        overall = overall and not diffs
    print("BYTECODE-PROBE:",
          "ALL-EQUAL (instruction stream unchanged)" if overall else "MISMATCH")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
