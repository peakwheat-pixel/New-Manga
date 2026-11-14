import json
def dump(label, p):
    print("="*50); print(label)
    reqs = {}
    for line in open(p, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line: continue
        try: fr = json.loads(line)
        except Exception: continue
        for side in ("request", "response"):
            val = fr.get(side)
            if isinstance(val, str):
                try: val = json.loads(val)
                except Exception: continue
            if not isinstance(val, dict): continue
            if side == "request":
                reqs[val.get("request_id")] = val.get("command")
            else:
                rid = val.get("request_id")
                cmd = val.get("command") or reqs.get(rid)
                if cmd == "ListBooks":
                    s = json.dumps(val)
                    print("  response for ListBooks:", s[:400])
for label, p in [("PASS", r"G:\CODEX\New Manga.workspace\task-envs\SIDECAR-REBUILD-1\evidence2\host-logs\reader-chapters-list\wire\core-service.ndjson"),
                 ("FAIL", r"G:\CODEX\New Manga.workspace\task-envs\SIDECAR-REBUILD-1\evidence2\host-logs\reader-chapters-concurrent\wire\core-service.ndjson")]:
    dump(label, p)