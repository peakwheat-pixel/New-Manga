import io, subprocess, sys
from pathlib import Path
REPO = Path(r"G:\CODEX\New Manga")
CS = REPO / "src" / "bootstrap" / "core_service.py"
PROBE = REPO / "verification" / "P09-PREVIEW-LIFECYCLE-RECLAIM-1" / "ac4-leak-assert-probe.py"
orig = io.open(CS, encoding="utf-8").read()
A = "preview_resource_ids=preview_resource_ids,"      # 直接传参
B = "{book_id: preview_resource_ids},"                # manifest 存储
assert orig.count(A) == 1 and orig.count(B) == 1, (orig.count(A), orig.count(B))

def run(tag):
    r = subprocess.run([sys.executable, str(PROBE)], capture_output=True, text=True)
    leak_lines = [l for l in r.stdout.splitlines() if l.startswith("LEAK")]
    # R2 Finding 4: the exit code alone is not enough.  An unrelated crash also exits
    # non-zero, so a check that only compares codes can call an exception "discriminating".
    # Parse the leak counts and require them to be a real, non-zero leak.
    leaked_rows = None
    if leak_lines:
        try:
            leaked_rows = int(leak_lines[0].split()[1])
        except (IndexError, ValueError):
            leaked_rows = None
    print("%-34s exit=%d  leak_rows=%s  %s" % (tag, r.returncode, leaked_rows, leak_lines))
    return r.returncode, leaked_rows

r0, leak0 = run("A) 基线")

io.open(CS, "w", encoding="utf-8", newline="").write(orig.replace(A, "preview_resource_ids=[],", 1))
try:
    r1, leak1 = run("B) 只切直接传参")
finally:
    io.open(CS, "w", encoding="utf-8", newline="").write(orig)

both = orig.replace(A, "preview_resource_ids=[],", 1).replace(B, "dict(),", 1)
io.open(CS, "w", encoding="utf-8", newline="").write(both)
try:
    r2, leak2 = run("C) 同时切两处")
finally:
    io.open(CS, "w", encoding="utf-8", newline="").write(orig)
    print("   已还原")

print()
# All four must hold, and B must be green too: it demonstrates that one supply path alone
# is sufficient, which is the redundancy claim this check exists to support.
checks = {
    "A baseline is green": r0 == 0 and leak0 == 0,
    "A produced no leak": leak0 == 0,
    "B (one path cut) still green": r1 == 0 and leak1 == 0,
    "C (both cut) fails": r2 != 0,
    "C reports a real leak": isinstance(leak2, int) and leak2 > 0,
}
for name, ok in checks.items():
    print("  %-32s %s" % (name, "ok" if ok else "FAILED"))

if all(checks.values()):
    print()
    print("判别力 = CONFIRMED")
    sys.exit(0)

print()
print("判别力 = NOT CONFIRMED（以上任一未成立）")
sys.exit(1)
