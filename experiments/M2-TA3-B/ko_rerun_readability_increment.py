"""M2-TA3-B2-KO-RERUN AC3: ko dialogue-readability worksheet increment.

The first run's worksheet (phase2/translate/dialogue-readability-worksheet.csv,
n=26) had ko n=11 because F1 left K11 as the only ko case with translations.
The rerun unlocks ko webtoon translations (K02 pilot: 93 speech regions), so
this script pre-fills the ko increment (quota 15, thresholds §3.2) from the
ko-rerun summaries: K02 (webtoon domain) 12 + K11 (P&C domain) 3, stratified
over reading_order, then DeepSeek SELF-evaluates on the same 5-point anchors
as build_worksheets.py (batch of 5 -> 3 requests; ai_draft column = pre-fill,
user audit remains the only verdict, C1 precedent).

Standard library only.  The key enters via TA3B_TRANSLATE_API_KEY and is
never printed or persisted.
"""

from __future__ import annotations

import csv
import json
import os
import time
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SUMMARIES = REPO_ROOT / "verification/M2-TA3-B/phase2/ko-rerun/summaries"
OUT = REPO_ROOT / "verification/M2-TA3-B/phase2/ko-rerun/translate/dialogue-readability-ko-increment.csv"

ENV_KEY_NAME = "TA3B_TRANSLATE_API_KEY"
BASE_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-chat"

QUOTA_K02 = 12
QUOTA_K11 = 3
BATCH = 5

SYSTEM = (
    "你是漫画翻译质量评审。对每条「源文本→中文译文」按三个维度独立打 1-5 分："
    "faithfulness（忠实度：译文语义与原文一致，无增删反转）、fluency（流畅度：中文自然可读）、"
    "register（语境适切：符合漫画语境与说话人语气）。"
    "锚点：5=专业出版级（该维无可挑剔）；4=少量瑕疵不影响理解；3=可读但有明显生硬或轻微不准；"
    "2=多处错误影响理解；1=不可用。三维独立打分。"
    '只输出 JSON 对象：{"scores":[{"faithfulness":n,"fluency":n,"register":n,"rationale":"中文，40字内"}]}'
    "，scores 数组与输入顺序一一对应，不要输出其他内容。"
)


def stratified_take(items: list[dict], n: int) -> list[dict]:
    if len(items) <= n:
        return items
    step = len(items) / n
    return [items[min(len(items) - 1, int(i * step))] for i in range(n)]


def self_evaluate(pairs: list[dict]) -> tuple[list[dict], float]:
    key = os.environ[ENV_KEY_NAME]
    body = {
        "model": MODEL,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "items": [
                            {
                                "index": i,
                                "source": p["source_text"],
                                "translation": p["translated_text"],
                            }
                            for i, p in enumerate(pairs)
                        ]
                    },
                    ensure_ascii=False,
                ),
            },
        ],
    }
    req = urllib.request.Request(
        BASE_URL,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    started = time.perf_counter()
    with urllib.request.urlopen(req, timeout=120) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    elapsed = round(time.perf_counter() - started, 2)
    return json.loads(payload["choices"][0]["message"]["content"])["scores"], elapsed


def main() -> int:
    picked: list[dict] = []
    for case_id, quota in (("K02", QUOTA_K02), ("K11", QUOTA_K11)):
        summary = json.loads((SUMMARIES / f"qual-{case_id}.json").read_text(encoding="utf-8"))
        pool = [
            {
                "case_id": case_id,
                "region_id": t["region_id"],
                "source_text": t["source_text"].replace("\n", " ").strip(),
                "translated_text": t["translated_text"].replace("\n", " ").strip(),
            }
            for t in summary["translate_details"]
            if t["region_type"] in ("speech", "narration") and t["translated_text"].strip()
        ]
        take = stratified_take(pool, quota)
        picked.extend(take)
        print(f"{case_id}: pool={len(pool)} take={len(take)}")

    rows: list[dict] = []
    for start in range(0, len(picked), BATCH):
        chunk = picked[start : start + BATCH]
        scores, elapsed = self_evaluate(chunk)
        for pair, score in zip(chunk, scores):
            mean = round(
                (score["faithfulness"] + score["fluency"] + score["register"]) / 3, 1
            )
            rows.append(
                {
                    **pair,
                    "ai_faithfulness": score["faithfulness"],
                    "ai_fluency": score["fluency"],
                    "ai_register": score["register"],
                    "ai_region_score": mean,
                    "ai_rationale": score["rationale"],
                    "user_verdict": "",
                    "rationale": "",
                }
            )
        print(f"batch {start}-{start + len(chunk) - 1}: {elapsed}s")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    cols = [
        "case_id", "region_id", "source_text", "translated_text",
        "ai_faithfulness", "ai_fluency", "ai_register", "ai_region_score",
        "ai_rationale", "user_verdict", "rationale",
    ]
    with OUT.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        writer.writerows(rows)
    means = [r["ai_region_score"] for r in rows]
    print(
        f"rows={len(rows)} ai_mean={round(sum(means) / len(means), 2)} "
        f"(range {min(means)}-{max(means)}); ai_draft is a SELF-evaluation pre-fill, "
        "the user audit is the only verdict"
    )
    print(f"out -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
