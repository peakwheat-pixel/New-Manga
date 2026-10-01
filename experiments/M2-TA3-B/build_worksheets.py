"""M2-TA3-B2 phase-2: build the human-review worksheets from run details.

Outputs (CSV into ``verification/M2-TA3-B/phase2/translate/`` and
``phase2/ocr/``, JSON twins next to them):

  1. ``dialogue-readability-worksheet.csv``  - AC4: n>=30 speech/narration
     regions (ja 15 + ko 15, layered per thresholds §2.5), three 1-5
     dimensions (faithfulness / fluency / register, region score = mean of
     the three).  The ``ai_draft`` column is pre-filled here by a DeepSeek
     SELF-evaluation of each translation (the only reviewer is the USER -
     C1 precedent: AI pre-fill + user audit; the worksheet is not a
     verdict until the user fills the verdict columns).
  2. ``sfx-semantic-worksheet.csv``          - thresholds §3.1 score sheet
     skeleton (expected empty this run: production SfxPolicy default SKIP).
  3. ``ocr-spot-check-worksheet.csv``        - thresholds §2.5 n=30 layered
     OCR audit skeleton (crop paths + OCR output; ``ai_draft`` verdict
     column pre-filled in a separate pass, user verdict columns empty).

Credential discipline: the DeepSeek self-evaluation reads the key from the
environment (``TA3B_TRANSLATE_API_KEY``) and never logs or persists it.
This evaluation traffic is separate from the translation chain and tiny
(30 short requests).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PHASE2 = REPO_ROOT / "verification" / "M2-TA3-B" / "phase2"
PIXEL_ROOT = Path(r"G:/CODEX/New Manga.task-envs/M2-TA3-B/phase2-pixels")
ENV_KEY_NAME = "TA3B_TRANSLATE_API_KEY"
BASE_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-chat"

TINY_TAG_CASES = {"BJ02", "BJ06", "BJ10", "J47", "K02"}
VERTICAL_TAG_CASES = {"BJ02", "BJ03", "BJ04", "BJ05", "BJ06", "BJ08", "BJ10", "BJ11"}
COMPLEX_TAG_CASES = {"BJ02", "BJ03", "BJ05", "BJ06", "BJ10", "K05", "K09"}
SFX_CASES = {"BJ06", "BJ10"}


def layer_of(case_id: str, region_type: str) -> str:
    if region_type == "sfx" or case_id in SFX_CASES and region_type in {"other", "title"}:
        return "sfx_or_decoration"
    if case_id in TINY_TAG_CASES:
        return "tiny_text"
    if case_id in VERTICAL_TAG_CASES and region_type == "speech":
        return "vertical_speech"
    if case_id in COMPLEX_TAG_CASES:
        return "complex_background"
    return "dialogue"


def csv_escape(value) -> str:
    text = "" if value is None else str(value)
    return '"' + text.replace('"', '""') + '"'


def write_csv(path: Path, cols: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        fh.write(",".join(cols) + "\n")
        for row in rows:
            fh.write(",".join(csv_escape(row.get(c, "")) for c in cols) + "\n")


def deepseek_self_evaluate(pairs: list[dict]) -> list[dict]:
    """One short JSON request per pair; en-key from env; typed failure path."""
    key = os.environ.get(ENV_KEY_NAME)
    if not key:
        raise RuntimeError(f"{ENV_KEY_NAME} not set")
    system = (
        "你是漫画翻译质量评审。对每条「源文本→中文译文」按三个维度独立打 1-5 分："
        "faithfulness（忠实度：译文语义与原文一致，无增删反转）、fluency（流畅度：中文自然可读）、"
        "register（语境适切：符合漫画语境与说话人语气）。"
        "锚点：5=专业出版级（该维无可挑剔）；4=少量瑕疵不影响理解；3=可读但有明显生硬或轻微不准；"
        "2=多处错误影响理解；1=不可用。三维独立打分。"
        '只输出 JSON 对象：{"scores":[{"faithfulness":n,"fluency":n,"register":n,"rationale":"中文，40字内"}]}'
        "，scores 数组与输入顺序一一对应，不要输出其他内容。"
    )
    body = {
        "model": MODEL,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "items": [
                            {"index": i, "source": p["source_text"], "translation": p["translated_text"]}
                            for i, p in enumerate(pairs)
                        ]
                    },
                    ensure_ascii=False,
                ),
            },
        ],
    }
    request = urllib.request.Request(
        BASE_URL,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = json.loads(response.read().decode("utf-8"))
    elapsed = round(time.perf_counter() - started, 2)
    content = payload["choices"][0]["message"]["content"]
    scores = json.loads(content)["scores"]
    return scores, elapsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summaries-dir", default=str(PHASE2 / "summaries"))
    parser.add_argument("--n-per-lang", type=int, default=15)
    parser.add_argument("--skip-ai-prefill", action="store_true")
    args = parser.parse_args()

    summaries_dir = Path(args.summaries_dir)
    summaries = []
    for path in sorted(summaries_dir.glob("qual-*.json")):
        if ".rerun" in path.name or path.name.startswith("qual-report"):
            continue
        summaries.append(json.loads(path.read_text(encoding="utf-8")))
    if not summaries:
        print("FATAL: no summaries", file=sys.stderr)
        return 2

    # ---- 1. dialogue readability worksheet (AC4) --------------------------
    pool: dict[str, list[dict]] = {"ja": [], "ko": []}
    for summary in summaries:
        for detail in summary.get("translate_details", []):
            if detail.get("region_type") not in {"speech", "narration"}:
                continue
            if not (detail.get("translated_text") or "").strip():
                continue
            pool.setdefault(summary["language"], []).append(
                {
                    "case_id": summary["case_id"],
                    "region_id": detail["region_id"],
                    "region_type": detail["region_type"],
                    "layer": layer_of(summary["case_id"], detail["region_type"]),
                    "source_text": detail.get("source_text", ""),
                    "translated_text": detail.get("translated_text", ""),
                }
            )

    def stratified_take(items: list[dict], n: int) -> list[dict]:
        by_layer: dict[str, list[dict]] = {}
        for item in items:
            by_layer.setdefault(item["layer"], []).append(item)
        quota = {"dialogue": None, "vertical_speech": 6, "tiny_text": 2, "complex_background": 2}
        taken: list[dict] = []
        for layer, cap in quota.items():
            if cap is None:
                continue
            taken.extend(by_layer.get(layer, [])[:cap])
        for layer, items_left in sorted(by_layer.items()):
            while len(taken) < n and items_left:
                candidate = items_left.pop(0)
                if candidate not in taken:
                    taken.append(candidate)
        return taken[:n]

    worksheet_rows: list[dict] = []
    for language in ("ja", "ko"):
        selected = stratified_take(pool.get(language, []), args.n_per_lang)
        for item in selected:
            worksheet_rows.append(
                {
                    "unit_id": f"{item['case_id']}:{item['region_id'][:8]}",
                    "language": language,
                    "case_id": item["case_id"],
                    "region_id": item["region_id"],
                    "layer": item["layer"],
                    "source_text": item["source_text"],
                    "translated_text": item["translated_text"],
                    "faithfulness": "",
                    "fluency": "",
                    "register": "",
                    "region_score": "",
                    "ai_draft": "",
                    "ai_rationale": "",
                    "user_verdict": "",
                    "rationale": "",
                }
            )

    if not args.skip_ai_prefill and worksheet_rows:
        print(f"AI self-evaluating {len(worksheet_rows)} translations ...")
        batch = 10
        for start in range(0, len(worksheet_rows), batch):
            chunk = worksheet_rows[start : start + batch]
            scores, elapsed = deepseek_self_evaluate(chunk)
            for row, score in zip(chunk, scores):
                mean = (score["faithfulness"] + score["fluency"] + score["register"]) / 3
                row["ai_draft"] = f"f={score['faithfulness']},fl={score['fluency']},r={score['register']},mean={mean:.1f}"
                row["ai_rationale"] = score.get("rationale", "")
            print(f"  batch {start}-{start + len(chunk) - 1} done in {elapsed}s")
        print("NOTE: ai_draft is a DeepSeek SELF-evaluation pre-fill; the user audit is the only verdict (C1 precedent).")

    cols = [
        "unit_id", "language", "case_id", "region_id", "layer", "source_text",
        "translated_text", "faithfulness", "fluency", "register", "region_score",
        "ai_draft", "ai_rationale", "user_verdict", "rationale",
    ]
    write_csv(PHASE2 / "translate" / "dialogue-readability-worksheet.csv", cols, worksheet_rows)
    (PHASE2 / "translate" / "dialogue-readability-worksheet.json").write_text(
        json.dumps(
            {
                "task": "M2-TA3-B2",
                "worksheet": "dialogue readability (thresholds §3.2)",
                "anchor": "5=professional/4=minor flaws/3=readable-but-rough/2=multiple errors/1=unusable; per-dimension; region score = mean",
                "gate_proposal": "median >= 3.5 AND share(score>=3) >= 80% (USER to rule; directional)",
                "ai_prefill": "DeepSeek self-evaluation (self-anchoring risk declared); user audit = only verdict",
                "n": len(worksheet_rows),
                "per_language": {
                    lang: sum(1 for r in worksheet_rows if r["language"] == lang)
                    for lang in ("ja", "ko")
                },
                "pool_sizes": {lang: len(v) for lang, v in pool.items()},
                "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
            ensure_ascii=False, indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    # ---- 2. SFX semantic worksheet skeleton (§3.1) -------------------------
    sfx_rows: list[dict] = []
    for summary in summaries:
        for detail in summary.get("translate_details", []):
            if detail.get("region_type") != "sfx":
                continue
            sfx_rows.append(
                {
                    "sfx_id": f"{summary['case_id']}:{detail['region_id'][:8]}",
                    "case_id": summary["case_id"],
                    "region_id": detail["region_id"],
                    "source_text": detail.get("source_text", ""),
                    "translated_text": detail.get("translated_text", ""),
                    "verdict": "",
                    "fail_mode": "",
                    "rationale": "production SfxPolicy default SKIP - no automatic SFX translation this run (n=0 < 15, R13: distribution only)",
                }
            )
    write_csv(
        PHASE2 / "translate" / "sfx-semantic-worksheet.csv",
        ["sfx_id", "case_id", "region_id", "source_text", "translated_text", "verdict", "fail_mode", "rationale"],
        sfx_rows,
    )

    # ---- 3. OCR n=30 layered spot-check skeleton (§2.5) --------------------
    ocr_pool: dict[str, list[dict]] = {"ja": [], "ko": []}
    for summary in summaries:
        for detail in summary.get("ocr_details", []):
            ocr_pool.setdefault(summary["language"], []).append(
                {
                    "case_id": summary["case_id"],
                    "region_id": detail["region_id"],
                    "region_type": detail.get("region_type", ""),
                    "layer": layer_of(summary["case_id"], detail.get("region_type", "")),
                    "ocr_text": detail.get("ocr_text", ""),
                    "crop": str(PIXEL_ROOT / "ocr" / "crops" / summary["case_id"] / f"{detail['region_id']}.png"),
                }
            )
    ocr_rows: list[dict] = []
    for language in ("ja", "ko"):
        for item in stratified_take(ocr_pool.get(language, []), args.n_per_lang):
            ocr_rows.append(
                {
                    "unit_id": f"{item['case_id']}:{item['region_id'][:8]}",
                    "language": language,
                    "case_id": item["case_id"],
                    "region_id": item["region_id"],
                    "layer": item["layer"],
                    "crop_preview_file": item["crop"],
                    "ocr_output": item["ocr_text"],
                    "verdict": "",
                    "ai_draft": "",
                    "rationale": "",
                }
            )
    write_csv(
        PHASE2 / "ocr" / "ocr-spot-check-worksheet.csv",
        ["unit_id", "language", "case_id", "region_id", "layer", "crop_preview_file", "ocr_output", "verdict", "ai_draft", "rationale"],
        ocr_rows,
    )

    # ---- 4. inpaint qualitative spot-check skeleton (§4, 10 regions) -------
    # SimpleFillProvider = basic fill; this sheet audits EXECUTION correctness
    # (region processed, artifact renders), never de-texting quality.
    inpaint_rows: list[dict] = []
    complex_cases = {"BJ02", "BJ03", "BJ05", "BJ06", "BJ10", "K05", "K09"}
    plain_quota, complex_quota = 5, 3
    for summary in summaries:
        export_info = summary.get("export", {})
        if export_info.get("status") != "OK":
            continue
        for detail in summary.get("ocr_details", []):
            layer = (
                "complex_background"
                if summary["case_id"] in complex_cases
                else "plain_balloon"
            )
            cap = complex_quota if layer == "complex_background" else plain_quota
            current = sum(1 for r in inpaint_rows if r["layer"] == layer)
            if current >= cap:
                continue
            inpaint_rows.append(
                {
                    "unit_id": f"{summary['case_id']}:{detail['region_id'][:8]}",
                    "case_id": summary["case_id"],
                    "region_id": detail["region_id"],
                    "layer": layer,
                    "exported_png_path": export_info.get("pixel_path", ""),
                    "bbox_in_export": json.dumps(detail.get("bbox", {}), ensure_ascii=False),
                    "residue_visible": "",  # user: no / slight / yes
                    "rationale": "",
                }
            )
    write_csv(
        PHASE2 / "inpaint" / "inpaint-spot-check-worksheet.csv",
        ["unit_id", "case_id", "region_id", "layer", "exported_png_path", "bbox_in_export", "residue_visible", "rationale"],
        inpaint_rows,
    )
    (PHASE2 / "inpaint" / "inpaint-spot-check-note.json").write_text(
        json.dumps(
            {
                "task": "M2-TA3-B2",
                "note": "SimpleFillProvider = basic fill; this audit checks execution correctness only (region processed, artifact renders) - de-texting quality is OUT of scope by provider selection (thresholds §4, no numeric gate)",
                "sfx_layer": "not sampled: production SfxPolicy default SKIP means SFX regions have no automatic inpaint artifact this run (honest registration)",
                "n": len(inpaint_rows),
            },
            ensure_ascii=False, indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    print(f"inpaint spot-check skeleton: n={len(inpaint_rows)} -> inpaint/inpaint-spot-check-worksheet.csv")
    print(f"ocr spot-check skeleton: n={len(ocr_rows)} -> ocr/ocr-spot-check-worksheet.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
