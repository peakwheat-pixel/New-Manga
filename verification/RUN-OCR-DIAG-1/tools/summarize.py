import json, sys, collections
path = sys.argv[1]
d = json.load(open(path, encoding="utf-8"))
print("tag:", d["tag"], "| terminal:", (d.get("run") or {}).get("terminal_status"))
print("overrides:", (d.get("run") or {}).get("overrides"))
steps = (d.get("db") or {}).get("tables", {}).get("step_runs") or []
print("step_runs:", len(steps))
by = collections.defaultdict(collections.Counter)
det = collections.defaultdict(set)
for s in steps:
    by[s["step_type"]][s["status"]] += 1
    if s.get("error_detail"):
        det[s["step_type"]].add((s.get("error_code"), s["error_detail"][:300]))
for st in sorted(by):
    print("  %-14s %s" % (st, dict(by[st])))
    for code, msg in sorted(det.get(st, ()))[:4]:
        print("      -> %s: %s" % (code, msg))
rows = ((d.get("run") or {}).get("task_projection") or {}).get("rows") or []
print("page rows:")
for r in rows:
    print("   p%s %-52s %-9s %s" % (r.get("page_order"), r.get("filename"), r.get("status"), r.get("error_code")))
print("stderr (last 1200):")
print((d.get("stderr") or "")[-1200:])
print("detect_probe:", (d.get("run") or {}).get("detect_probe"))
