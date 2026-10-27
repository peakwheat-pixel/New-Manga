#!/usr/bin/env python
"""RUN-OCR-DIAG-1 AC3: run `core.detect` on every fixture page.

`core.detect` is the verification surface over the SAME detector instance the
pipeline detect step uses, so candidate counts here are the pipeline's counts.
Zero candidates is exactly what the pipeline turns into INVALID_INPUT
("detector returned no candidates for page ...", handlers.py:296).
"""
import base64
import json
import sqlite3
import subprocess
import sys
import threading
import time
from pathlib import Path

TASK_ENV = Path(r"G:\CODEX\New Manga.workspace\task-envs\RUN-OCR-DIAG-1")
SIDECAR = Path(
    r"G:\CODEX\New Manga.workspace\task-envs\FINAL-VALIDATION-1\out"
    r"\NewManga-0.1.0-win-x64-models\app\core-sidecar"
)
DATA_ROOT = TASK_ENV / "data-root-models-book"


def pages_with_files():
    con = sqlite3.connect("file:%s?mode=ro" % str(DATA_ROOT / "library.db").replace("\\", "/"), uri=True)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "select page_id, sort_order, source_filename, width, height, managed_original_ref "
        "from pages order by sort_order")]
    con.close()
    out = []
    for r in rows:
        p = DATA_ROOT / "managed" / r["managed_original_ref"]
        out.append({**r, "path": str(p), "exists": p.exists()})
    return out


class Session:
    def __init__(self):
        env = dict(__import__("os").environ)
        env["NEWMANGA_DATA_ROOT"] = str(DATA_ROOT)
        env["M2RC1_DERIVED_ROOT"] = str(DATA_ROOT / "derived")
        env["M2RC2_CATALOG_DB"] = str(DATA_ROOT / "catalog" / "catalog.sqlite")
        env["M2RC1_MANAGED_ROOT"] = str(DATA_ROOT / "managed")
        self.p = subprocess.Popen([str(SIDECAR / "core_service.exe")], cwd=str(SIDECAR),
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  text=True, encoding="utf-8", errors="replace", bufsize=1, env=env)
        self.stderr = []
        threading.Thread(target=self._pump, daemon=True).start()
        self.i = 0
        self.log = open(TASK_ENV / "logs" / "detect-probe.log", "w", encoding="utf-8")

    def _pump(self):
        for line in self.p.stderr:
            self.stderr.append(line)
            self.log.write("STDERR " + line)
            self.log.flush()

    def send(self, command, payload, timeout=180.0):
        self.i += 1
        rid = "det-%03d" % self.i
        frame = {"protocol": "new-manga.core", "version": {"major": 2, "minor": 3},
                 "request_id": rid, "command": command, "payload": payload}
        self.log.write("REQ " + json.dumps({"command": command}, ensure_ascii=False) + "\n")
        self.p.stdin.write(json.dumps(frame, ensure_ascii=False) + "\n")
        self.p.stdin.flush()
        deadline = time.time() + timeout
        while time.time() < deadline:
            raw = self.p.stdout.readline()
            if not raw:
                return None
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if "event_type" in obj and "request_id" not in obj:
                continue
            if obj.get("request_id") == rid:
                return obj
        return None

    def close(self):
        try:
            self.p.stdin.close()
            self.p.wait(timeout=15)
        except Exception:
            try:
                self.p.kill()
            except Exception:
                pass
        time.sleep(0.2)
        self.log.close()


def main():
    pages = pages_with_files()
    ev = {"ac": "AC3", "sidecar": str(SIDECAR), "data_root": str(DATA_ROOT),
          "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "pages": []}
    s = Session()
    try:
        s.send("core.ping", {})
        for pg in pages:
            rec = {"page_order": pg["sort_order"], "page_id": pg["page_id"],
                   "filename": pg["source_filename"], "db_w": pg["width"], "db_h": pg["height"],
                   "exists": pg["exists"]}
            if not pg["exists"]:
                rec["error"] = "file missing"
                ev["pages"].append(rec)
                continue
            data = Path(pg["path"]).read_bytes()
            rec["bytes"] = len(data)
            from PIL import Image  # only to get exact size, decoded by the Core independently
            with Image.open(pg["path"]) as im:
                rec["w"], rec["h"], rec["format"] = im.size[0], im.size[1], im.format
            t0 = time.time()
            resp = s.send("core.detect", {
                "page": base64.b64encode(data).decode("ascii"),
                "width": rec["w"], "height": rec["h"],
            })
            rec["elapsed_ms"] = round((time.time() - t0) * 1000, 1)
            if resp is None:
                rec["error"] = "no response"
            else:
                err = resp.get("error")
                res = resp.get("result") or {}
                rec["error_code"] = (err or {}).get("code")
                rec["candidates"] = len(res.get("candidates") or []) if isinstance(res, dict) else None
                rec["coordinate_space"] = res.get("coordinate_space") if isinstance(res, dict) else None
                rec["provider_elapsed_ms"] = res.get("elapsed_ms") if isinstance(res, dict) else None
                rec["labels"] = sorted({c.get("provider_label") for c in (res.get("candidates") or [])
                                        if isinstance(c, dict)}) if isinstance(res, dict) else None
            ev["pages"].append(rec)
            print(json.dumps(rec, ensure_ascii=False))
    finally:
        s.close()
    ev["stderr"] = "".join(s.stderr)
    ev["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    out = TASK_ENV / "evidence" / "detect-per-page.json"
    out.write_text(json.dumps(ev, indent=2, ensure_ascii=False), encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
