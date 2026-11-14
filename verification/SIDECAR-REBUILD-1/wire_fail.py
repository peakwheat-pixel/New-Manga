import json
p = r"G:\CODEX\New Manga.workspace\task-envs\SIDECAR-REBUILD-1\evidence4\host-logs\reader-chapters-list\wire\core-service.ndjson"
for i, line in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
    line = line.strip()
    if not line: continue
    try: fr = json.loads(line)
    except Exception: continue
    def side(name):
        v = fr.get(name)
        if isinstance(v, str):
            try: v = json.loads(v)
            except Exception: return v[:100]
        return v
    req, resp = side("request"), side("response")
    print("#", i)
    if isinstance(req, dict):
        print("  REQ ", req.get("command"), req.get("request_id"))
    if isinstance(resp, dict):
        print("  RESP", resp.get("request_id"), "| result:", json.dumps(resp.get("result"))[:180], "| error:", json.dumps(resp.get("error"))[:80])
    else:
        print("  RESP raw:", str(resp)[:160])