"""M2-SFX-ANNOTATE-R3 AC2 后半：双 AI 判定比对 → consensus/divergence + 第三方仲裁。

输入：judgments/{codex,agy}/batch-*.json（双 AI 独立逐图判定，22 单元覆盖经断言）。
动作：
  1. 按 id 比对 → consensus.json（verdict 一致，双方 rationale 全文保留）+
     divergence.json（verdict 不一致，含 preview 绝对路径，沿 R2 同构）。
  2. divergence 3 单元由编排会话仲裁者逐图实看终裁（预览裁切 + 原页上下文复核；
     独立标准=判定效果音的关键在「以声音拟形的艺术化文字」与「依附器件/服饰的
     画面语义」之分，字形比对参照 R2 confirm 判例与 R2-BJ17-B02 仲裁判例），
     终裁结论在 ARBITER_VERDICTS 常量内联登记（rationale 全文含实看证据与采方
     论证），写 judgments/arbiter/batch-1.json（沿 R2 arbiter 格式）。
  3. 断言：判定覆盖 units 全量 22/22；共识∪仲裁=范围全量；arb 判定恰好覆盖
     divergence、无多余。

纪律：只读输入判定；产物落 judgments/（gitignored）；仲裁 rationale 全文留痕。
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
JUDG_DIR = REPO_ROOT / "training_data" / "sfx-v1" / "annotate-r3" / "judgments"
UNITS_JSON = JUDG_DIR / "units.json"

# ---------------------------------------------------------------------------
# 第三方仲裁终裁（逐图实看：预览裁切 + 原页上下文，见各 rationale）
# ---------------------------------------------------------------------------

ARBITER_VERDICTS = [
    {
        "id": "R3-BJ27-B00",
        "verdict": "delete",
        "rationale": (
            "实看预览+原页精确框区（vol05_p0039 [264.8,2225.9,347.7,2329.0] ±边距复核）：框内为青年"
            "衬衫胸口的几何花纹领带局部（黑色方块纹+白色高光线，多面体状误读源于裁切视角），非文字——"
            "codex 报告的「ン/ロ/コ 假名状字块」与领带几何花纹逐块吻合（方框纹=ロ 形、横条纹=ン 形的"
            "偶然相似），无笔画连贯性亦无可读拟声词；agy 的画面物体判断成立。原页为病房对话页，场景"
            "上亦无该处效果音的叙事动机。按判定标准「依附服饰的画面语义≠以声音拟形」终裁 delete，采 agy。"
        ),
    },
    {
        "id": "R2-BJ20-B01",
        "verdict": "delete",
        "rationale": (
            "实看预览+原页右下上下文（vol05_p0052 [2372.9,3900.6,2716.9,4167.0]）：框内圆角矩形牌为"
            "担架/器械尾部的面板显示牌形态（黑色粗边框贴合器件边缘，旁边即担架床沿），牌内潦草弯曲字符"
            "为依附器件的显示/标签内容（心电乱纹/铭牌涂写语义）——字符被牌框物理包住，与书写在画面空间、"
            "独立于物体的效果音有本质区别；R2 confirm 判例（粗毛笔假名无气泡）与 R2-BJ17-B02 仲裁判例"
            "（容器内的规整字=容器语义内容）均指向：器件容器内的文字不按 SFX 计。codex 的标牌判断成立，"
            "agy 的「散写拟态」忽略了牌框的器件容器语义。终裁 delete，采 codex。"
        ),
    },
    {
        "id": "R2-BJ22-B01",
        "verdict": "correct",
        "rationale": (
            "实看预览+原页右上大图（vol01_p0067 [1650,0]-[2946,900] 复核）：候选宽框 [1052.8,0.3,1863.4,"
            "559.0] 圈住手术室场景（医护+器械车），但页面右缘 x≈1840-2100 处有竖长白底椭圆框（右缘出页），"
            "框内为锯齿状潦草粗笔画拟声字（快速手术动作声形态）——与同页左侧规整细笔对白「用意のできた」"
            "字形对比鲜明，满足「以声音拟形的艺术化字形」标准（同 R2-BJ17-B02 仲裁判例的反面情形："
            "该判例 delete 恰因字形完全普通，此处字形高度艺术化），确认为 SFX。但候选框只碰到椭圆左缘"
            "（x1=1863.4 < 椭圆主体 1840-2100 的大部分），需收缩重框至椭圆区域（约 [1840,60,2100,570]）"
            "→ correct（是 SFX 但框需修；坐标修正留 revision 链，沿 R2 stage2r2 correct 语义框保留"
            "原坐标+revision note）。SFX 存在性采 agy，处置按 R2 correct 口径。"
        ),
    },
]


def load_side(who: str, files: list[str]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for f in files:
        d = json.loads((JUDG_DIR / who / f).read_text(encoding="utf-8"))
        for j in d["judgments"]:
            if j["id"] in out:
                raise ValueError(f"{who}/{f}: 重复判定 {j['id']}")
            out[j["id"]] = j
    return out


def main() -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    units = json.loads(UNITS_JSON.read_text(encoding="utf-8"))["units"]
    ids = [u["id"] for u in units]
    id_set = set(ids)

    codex = load_side("codex", ["batch-1.json", "batch-2.json"])
    agy = load_side("agy", ["batch-0.json", "batch-1.json"])
    for name, side in (("codex", codex), ("agy", agy)):
        if set(side) != id_set:
            raise ValueError(f"{name} 判定覆盖不一致: 缺 {sorted(id_set - set(side))} 多 {sorted(set(side) - id_set)}")

    consensus, divergence = [], []
    for uid in ids:
        c, a = codex[uid], agy[uid]
        if c["verdict"] == a["verdict"]:
            consensus.append({
                "id": uid,
                "verdict": c["verdict"],
                "rationale_codex": c["rationale"],
                "rationale_agy": a["rationale"],
            })
        else:
            preview = next(u["preview"] for u in units if u["id"] == uid)
            divergence.append({
                "id": uid,
                "verdict_codex": c["verdict"],
                "verdict_agy": a["verdict"],
                "rationale_codex": c["rationale"],
                "rationale_agy": a["rationale"],
                "preview": preview,
            })

    # 仲裁终裁：必须恰好覆盖 divergence、无多余
    arb_ids = [j["id"] for j in ARBITER_VERDICTS]
    if sorted(arb_ids) != sorted(d["id"] for d in divergence):
        raise ValueError(f"仲裁覆盖不一致: arb={sorted(arb_ids)} vs divergence={sorted(d['id'] for d in divergence)}")

    (JUDG_DIR / "consensus.json").write_text(
        json.dumps({
            "purpose": "M2-SFX-ANNOTATE-R3 双 AI 交叉审核共识（codex+agy verdict 一致；双方 rationale 全文保留）",
            "generated_at_utc": stamp,
            "tool": "experiments/M2-SFX-ANNOTATE-R3/build_r3_judgments.py",
            "inputs": {"codex": "judgments/codex/batch-{1,2}.json", "agy": "judgments/agy/batch-{0,1}.json",
                       "units": "judgments/units.json"},
            "n_consensus": len(consensus),
            "verdict_dist": dict(Counter(c["verdict"] for c in consensus)),
            "consensus": consensus,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
    (JUDG_DIR / "divergence.json").write_text(
        json.dumps({
            "purpose": "M2-SFX-ANNOTATE-R3 双判分歧（codex vs agy verdict 不一致）→ 第三方仲裁输入",
            "generated_at_utc": stamp,
            "tool": "experiments/M2-SFX-ANNOTATE-R3/build_r3_judgments.py",
            "n_divergence": len(divergence),
            "divergence": divergence,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
    arb_dir = JUDG_DIR / "arbiter"
    arb_dir.mkdir(parents=True, exist_ok=True)
    (arb_dir / "batch-1.json").write_text(
        json.dumps({
            "purpose": (f"M2-SFX-ANNOTATE-R3 双判分歧第三方仲裁批次 1/1（分歧 {len(divergence)} 单元逐图终裁；"
                        "仲裁者=编排会话独立标准：以声音拟形的艺术化文字 vs 依附器件/服饰的画面语义；"
                        "字形比对参照 R2 confirm 判例与 R2-BJ17-B02 仲裁判例；预览+原页上下文实看）"),
            "generated_at_utc": stamp,
            "judgments": ARBITER_VERDICTS,
        }, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"consensus: {len(consensus)} {dict(Counter(c['verdict'] for c in consensus))}")
    print(f"divergence: {len(divergence)} -> arbiter batch-1.json "
          f"{dict(Counter(j['verdict'] for j in ARBITER_VERDICTS))}")
    final = {}
    for c in consensus:
        final[c["id"]] = c["verdict"]
    for j in ARBITER_VERDICTS:
        final[j["id"]] = j["verdict"]
    print(f"final: {len(final)} units {dict(Counter(final.values()))}")
    if set(final) != id_set:
        raise ValueError("共识∪仲裁 != units 全量")
    return 0


if __name__ == "__main__":
    sys.exit(main())
