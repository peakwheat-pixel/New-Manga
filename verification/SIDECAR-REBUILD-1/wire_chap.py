import json
p = r"G:\CODEX\New Manga.workspace\task-envs\SIDECAR-REBUILD-1\evidence2\host-logs\reader-chapters-concurrent\wire\core-service.ndjson"
reqs = {}
n = 0
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
            if val.get("command") == "list_chapters":
                print("REQ list_chapters payload:", json.dumps(val.get("payload"))[:200])
        else:
            cmd = val.get("command") or reqs.get(val.get("request_id"))
            if cmd == "list_chapters":
                n += 1
                r = val.get("result"); e = val.get("error")
                print(f"RESP#{n} content:", json.dumps(r)[:160], "| error:", json.dumps(e)[:120] if e else None)
print("total list_chapters responses:", n)