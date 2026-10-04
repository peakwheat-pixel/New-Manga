"""M2-SFX-ANNOTATE-R2 AC1：KO 域 K11-K25 候选页下载（15 页全量候选）。

从 cases.json 既有登记 K11-K25（peppercarrot.com 韩文版，CC-BY-4.0）下载
low-res 页图到 gitignored 数据树候选目录，PIL 验证可开并转 RGB PNG。
正式入池 5 页由 material_scan_density.py 密度排序后另行落位
（韩漫_KO/02_public_ground_truth_peppercarrot/epXX/<source_id>.png）。

候选页 = 选取池（SFX 密集 top-5 裁量的证据），全部留在候选目录作扩标池。
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
CASES_JSON = REPO_ROOT / "test_assets" / "comic_golden_suite" / "manifests" / "cases.json"
CAND_DIR = REPO_ROOT / "training_data" / "sfx-v1" / "annotate-r2" / "ko-candidates"
USER_AGENT = "NewManga-TestAssets/1.0"
TIMEOUT = 60


def main() -> int:
    manifest = json.loads(CASES_JSON.read_text(encoding="utf-8"))
    cases = [c for c in manifest["cases"] if c["case_id"].startswith("K") and c["case_id"] >= "K11"]
    print(f"candidates: {len(cases)} cases (K11-K25)")
    CAND_DIR.mkdir(parents=True, exist_ok=True)
    failures = 0
    for case in cases:
        cid = case["case_id"]
        url = case.get("asset_profile", {}).get("image_url") or case.get("source_url")
        out = CAND_DIR / f"{cid}_{case['source_id']}.png"
        if out.is_file():
            print(f"{cid}\tSKIP\t{out.name} already present")
            continue
        if not url:
            print(f"{cid}\tFAILED\tno image_url in cases.json", file=sys.stderr)
            failures += 1
            continue
        payload = None
        last_error: Exception | None = None
        for attempt in (1, 2, 3):
            try:
                request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                    payload = response.read()
                break
            except (OSError, urllib.error.URLError) as exc:
                last_error = exc
                if attempt < 3:
                    time.sleep(2 * attempt)
        if payload is None:
            print(f"{cid}\tFAILED\t{type(last_error).__name__}: {last_error} ({url})", file=sys.stderr)
            failures += 1
            continue
        with Image.open(__import__("io").BytesIO(payload)) as im:
            rgb = im.convert("RGB")
            rgb.save(out, format="PNG")
            size = rgb.size
        print(f"{cid}\tOK\t{size[0]}x{size[1]} <- {url}")
    print(f"SUMMARY\tcommand=fetch_ko cases={len(cases)} failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
