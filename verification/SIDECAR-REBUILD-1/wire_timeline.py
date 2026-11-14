import json
p = r"G:\CODEX\New Manga.workspace\task-envs\SIDECAR-REBUILD-1\evidence2\host-logs\reader-chapters-concurrent\wire\core-service.ndjson"
print("=== 逐帧时序（request -> response 的 command）===")
for i, line in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
    line = line.strip()
    if not line: continue
    try: fr = json.loads(line)
    except Exception: continue
    def cmd(side):
        v = fr.get(side)
        if isinstance(v, str):
            try: v = json.loads(v)
            except Exception: return None
        if isinstance(v, dict):
            return v.get("command"), v.get("request_id"), (json.dumps(v.get("error"))[:40] if v.get("error") else None)
        return None
    r = cmd("request"); s = cmd("response")
    print(f"{i:3d} REQ={r}  RESP={s}")