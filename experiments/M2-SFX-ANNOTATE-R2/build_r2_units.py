"""M2-SFX-ANNOTATE-R2：扩审单元清单合并提取 + 分批（只提取，不判定）。

三部分来源（编排合同）：
  ① part=bj_lowconf（AC2）  R1 残留 user-residual.json 中 domain=bj 且
                            conf∈[0.2,0.5) 的全部单元；
  ② part=replay（AC3）      R1 残留中回放页（BJ06+J38/J41/J43/J51）全部单元；
  ③ part=bj_new（AC4）      R2 targeted 预标注（stage1_preannotate_bj_new.py）
                            worksheet-bj-new.json 中 conf≥0.2 的全部单元
                            （BJ16-25 新页候选全部入本轮，BJ 正集为主目标）。

合并去重（unit_id 唯一；同单元跨部分时 replay 优先），写：
  training_data/sfx-v1/annotate-r2/judgments/units.json           （全量清单）
  training_data/sfx-v1/annotate-r2/judgments/batch-list/batch-N.json（≤20 单元/批）

批次单元字段固定：id / preview（可解析绝对路径）/ conf / source / ai_pred / part。
dev venv 可跑（无 GPU 依赖）。
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

R1_WORKTREE = Path(r"G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R1-zcode")
R1_ANNOTATE = R1_WORKTREE / "training_data" / "sfx-v1" / "annotate-r1"
R2_ANNOTATE = REPO_ROOT / "training_data" / "sfx-v1" / "annotate-r2"

RESIDUAL_JSON = R1_ANNOTATE / "judgments" / "user-residual.json"
R1_WORKSHEET_JSON = R1_ANNOTATE / "worksheet" / "worksheet.json"
R2_WORKSHEET_JSON = R2_ANNOTATE / "worksheet" / "worksheet-bj-new.json"

UNITS_JSON = R2_ANNOTATE / "judgments" / "units.json"
BATCH_DIR = R2_ANNOTATE / "judgments" / "batch-list"

REPLAY_CASES = {"BJ06", "J38", "J41", "J43", "J51"}  # 合同 AC2 域内回放 5 页
BATCH_SIZE = 20


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def conf_tier(conf) -> str:
    if not isinstance(conf, (int, float)):
        return "ref_no_conf"
    if conf >= 0.5:
        return "conf_ge_0.5"
    if conf >= 0.2:
        return "conf_0.2_to_0.5"
    return "conf_lt_0.2"


def main() -> int:
    residual = json.loads(RESIDUAL_JSON.read_text(encoding="utf-8"))
    r1_ws = {u["unit_id"]: u for u in
             json.loads(R1_WORKSHEET_JSON.read_text(encoding="utf-8"))["units"]}
    r2_ws = json.loads(R2_WORKSHEET_JSON.read_text(encoding="utf-8"))["units"]
    stamp = now_iso()

    units: dict[str, dict] = {}
    dup_dropped: list[str] = []

    def add(u: dict, part: str, priority: int):
        uid = u["unit_id"]
        if uid in units:
            dup_dropped.append(f"{uid} (kept={units[uid]['part']}, dropped={part})")
            return
        preview_rel = u["preview_file"]  # 相对所属 annotate-r*/ 目录（previews/…）
        preview_abs = (R1_ANNOTATE / preview_rel) if uid.startswith("R1-") else (R2_ANNOTATE / preview_rel)
        if not preview_abs.is_file():
            raise FileNotFoundError(f"{uid} 预览图不在盘: {preview_abs}")
        ws = r1_ws.get(uid, {})
        sources = u.get("sources") or []
        units[uid] = {
            "id": uid,
            "part": part,
            "domain": u.get("domain"),
            "case_id": u.get("case_id"),
            "conf": u.get("conf"),
            "review_tier": u.get("review_tier") or conf_tier(u.get("conf")),
            "xyxy": u.get("xyxy"),
            "source": "/".join(sources) if sources else None,
            "ai_pred": ws.get("ai_text"),
            "preview": str(preview_abs).replace("\\", "/"),
            "_priority": priority,
        }

    # ① AC2：R1 残留 BJ 域 conf∈[0.2,0.5)
    for u in residual["units"]:
        c = u.get("conf")
        if u["domain"] == "bj" and isinstance(c, (int, float)) and 0.2 <= c < 0.5:
            add(u, "bj_lowconf", priority=0)

    # ② AC3：R1 残留回放页（BJ06+J38/J41/J43/J51）全部单元
    for u in residual["units"]:
        if u.get("case_id") in REPLAY_CASES:
            add(u, "replay", priority=1)

    # ③ AC4：R2 BJ 新页（BJ16-25）conf≥0.2 全部候选
    for u in r2_ws:
        c = u.get("ai_conf")
        if isinstance(c, (int, float)) and c >= 0.2:
            add(
                {
                    "unit_id": u["unit_id"],
                    "domain": u["domain"],
                    "case_id": u["case_id"],
                    "conf": c,
                    "review_tier": conf_tier(c),
                    "xyxy": u["xyxy"],
                    "preview_file": u["preview_file"],
                    "sources": u.get("sources", []),
                },
                "bj_new",
                priority=2,
            )

    ordered = sorted(units.values(), key=lambda x: (x["_priority"], x["id"]))
    for u in ordered:
        del u["_priority"]

    by_part = {"bj_lowconf": 0, "replay": 0, "bj_new": 0}
    for u in ordered:
        by_part[u["part"]] += 1

    doc = {
        "purpose": "M2-SFX-ANNOTATE-R2 扩审单元全量清单（①AC2 BJ 低置信层 conf∈[0.2,0.5) + ②AC3 回放页 BJ06/J38/J41/J43/J51 + ③AC4 BJ 新页 BJ16-25 conf≥0.2）；只提取分批，不判定",
        "generated_at_utc": stamp,
        "tool": "experiments/M2-SFX-ANNOTATE-R2/build_r2_units.py",
        "inputs": {
            "r1_residual": str(RESIDUAL_JSON),
            "r1_worksheet": str(R1_WORKSHEET_JSON),
            "r2_worksheet_bj_new": str(R2_WORKSHEET_JSON),
            "r2_preannotate_bj_new": str(R2_ANNOTATE / "preannotate" / "manifest-bj-new.json"),
        },
        "counts": {"total": len(ordered), "byPart": by_part},
        "notes": {
            "bj_lowconf": "R1 残留 393 单元中 BJ 域 11 个（ref_no_conf 7 + conf_lt_0.2 4），conf∈[0.2,0.5) 为 0——AC2 部分为空集，如实登记",
            "replay": "回放页单元保持 pseudo、不入训练集（R1 合同），本轮扩审补判定",
            "bj_new": "BJ16-25 = material-selection.json bj_selected rank1-10；候选单源 chiqui7-scan（整页 letterbox，与素材采集员 density-scan-material.json 密度逐页一致）；仅取 conf≥0.2，低置信候选保留在 worksheet-bj-new.json 不入本轮",
            "ai_pred": "AI 预判文字（R1 worksheet ai_text join；本轮单元均无文字预判=null）",
            "preview": "绝对路径；R1 单元 preview 在 R1 worktree（跨 worktree 引用原路径，不复制）",
            "dedup_dropped": dup_dropped,
        },
        "units": ordered,
    }
    UNITS_JSON.parent.mkdir(parents=True, exist_ok=True)
    UNITS_JSON.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")

    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    for old in BATCH_DIR.glob("batch-*.json"):
        old.unlink()
    batches = [ordered[i:i + BATCH_SIZE] for i in range(0, len(ordered), BATCH_SIZE)]
    for n, batch in enumerate(batches, start=1):
        payload = {
            "units": [
                {k: u[k] for k in ("id", "preview", "conf", "source", "ai_pred", "part")}
                for u in batch
            ]
        }
        (BATCH_DIR / f"batch-{n}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8"
        )

    print(f"units: {len(ordered)} | byPart: {by_part} | batches: {len(batches)} (batch_size<={BATCH_SIZE})")
    print(f"dup_dropped: {dup_dropped or 'none'}")
    print(f"wrote {UNITS_JSON}")
    for n in range(1, len(batches) + 1):
        print(f"wrote {BATCH_DIR / f'batch-{n}.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
