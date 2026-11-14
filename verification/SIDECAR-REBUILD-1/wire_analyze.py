import json, sys, collections
for label, p in [("PASS", r"G:\CODEX\New Manga.workspace\task-envs\SIDECAR-REBUILD-1\evidence2\host-logs\reader-chapters-list\wire\core-service.ndjson"),
                 ("FAIL", r"G:\CODEX\New Manga.workspace\task-envs\SIDECAR-REBUILD-1\evidence2\host-logs\reader-chapters-concurrent\wire\core-service.ndjson")]:
    print("="*60); print(label, p.split("\\")[-3])
    cmds = collections.Counter()
    errs = collections.Counter()
    n = 0
    samples = {}
    for line in open(p, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line: continue
        n += 1
        try: fr = json.loads(line)
        except Exception: continue
        # frame may have request/response shapes
        for side in ("request", "response"):
            val = fr.get(side)
            if isinstance(val, str):
                try: val = json.loads(val)
                except Exception: val = {"_raw": val[:120]}
            if isinstance(val, dict):
                c = val.get("command")
                if c: cmds[(side, c)] += 1
                e = val.get("error")
                if e: errs[(side, json.dumps(e)[:110])] += 1
                if c == "ListBooks" and side == "response" and "ListBooks" not in samples:
                    samples["ListBooks"] = json.dumps(val)[:300]
    print("frames:", n)
    print("commands:", dict(cmds))
    print("errors:", dict(errs))
    if "ListBooks" in samples: print("first ListBooks response:", samples["ListBooks"])