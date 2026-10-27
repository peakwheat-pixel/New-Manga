import json, sqlite3
from pathlib import Path
from PIL import Image
import numpy as np
root = Path(r"G:\CODEX\New Manga.workspace\task-envs\RUN-OCR-DIAG-1\data-root-models-book")
con = sqlite3.connect("file:%s?mode=ro" % str(root / "library.db").replace("\\","/"), uri=True)
con.row_factory = sqlite3.Row
rows = [dict(r) for r in con.execute("select page_id, sort_order, source_filename, width, height, managed_original_ref from pages order by sort_order")]
out = []
print("%-3s %-44s %-11s %-9s %-6s %-6s %-8s %-7s %-7s %s" % ("#","filename","size","mode","mean","std","darkFrac","uniqPct","edge","run_result"))
for r in rows:
    p = root / "managed" / r["managed_original_ref"]
    info = {"page_order": r["sort_order"], "filename": r["source_filename"], "db_w": r["width"], "db_h": r["height"]}
    if p.exists():
        info["bytes"] = p.stat().st_size
        im = Image.open(p); info.update(format=im.format, mode=im.mode, w=im.size[0], h=im.size[1])
        a = np.asarray(im.convert("L"), dtype=np.uint8)
        info.update(mean=round(float(a.mean()),1), std=round(float(a.std()),1),
                    darkFrac=round(float((a<100).mean()),4),
                    uniqPct=round(len(np.unique(a))/256.0,3),
                    edge=round(float((np.abs(np.diff(a.astype(np.int16),axis=1)).mean()+np.abs(np.diff(a.astype(np.int16),axis=0)).mean())/2),2))
        # colourfulness: fraction of pixels with saturated colour (manga splash pages often full colour)
        rgb = np.asarray(im.convert("RGB"), dtype=np.uint8).astype(np.int16)
        info["colorFrac"] = round(float(((rgb.max(2)-rgb.min(2))>40).mean()),4)
    info["run_result"] = "INVALID_INPUT(detect)" if r["sort_order"] >= 4 else "PROVIDER_NOT_CONFIGURED(ocr)"
    out.append(info)
    print("%-3s %-44s %-11s %-9s %-6s %-6s %-8s %-7s %-7s %s" % (
        info["page_order"], info["filename"][:44], "%sx%s" % (info.get("w"), info.get("h")), info.get("mode"),
        info.get("mean"), info.get("std"), info.get("darkFrac"), info.get("uniqPct"), info.get("edge"), info["run_result"]))
json.dump(out, open(r"G:\CODEX\New Manga.workspace\task-envs\RUN-OCR-DIAG-1\evidence\page-features.json","w",encoding="utf-8"), indent=2, ensure_ascii=False)
