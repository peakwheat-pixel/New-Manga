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
    leak = [l for l in r.stdout.splitlines() if l.startswith("LEAK")]
    print("%-34s exit=%d  %s" % (tag, r.returncode, leak))
    return r.returncode

r0 = run("A) 基线")

io.open(CS, "w", encoding="utf-8", newline="").write(orig.replace(A, "preview_resource_ids=[],", 1))
try:
    r1 = run("B) 只切直接传参")
finally:
    io.open(CS, "w", encoding="utf-8", newline="").write(orig)

both = orig.replace(A, "preview_resource_ids=[],", 1).replace(B, "dict(),", 1)
io.open(CS, "w", encoding="utf-8", newline="").write(both)
try:
    r2 = run("C) 同时切两处")
finally:
    io.open(CS, "w", encoding="utf-8", newline="").write(orig)
    print("   已还原")

print()
if r0 == 0 and r2 != 0:
    print("判别力 = CONFIRMED（基线绿，两条供给路径都断则红）")
elif r0 == 0 and r1 == 0 and r2 == 0:
    print("判别力 = NOT CONFIRMED（三处皆绿 = 还有第三条供给路径）")
else:
    print("判别力 = 部分（baseline=%d, one=%d, both=%d）" % (r0, r1, r2))
