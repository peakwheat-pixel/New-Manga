"""Freeze the agent visual verdicts for the SFX spot check (AC2).

The visual pass (agent = directional annotator, NOT a formal labeler) read
every preview produced by ``eval_sfx_ogkalu.py`` (100 px grid overlay,
green=prior box, red=ogkalu detection) and recorded per-frame verdicts.
This script hard-codes NOTHING geometric: SFX boxes estimated by eye are
typed here as explicit ``agent_estimate`` entries (anchored to the grid),
C1 evidence boxes are referenced as ``c1_audit`` provenance, and ogkalu
detections are pulled live from ``ogkalu-sfx-frames.json``. Geometric
overlap (best intersection / sfx area) is computed, not asserted.

Verdict enum (per frame, primary SFX instance unless noted):
- detected_hit      : ogkalu box (conf >= 0.5) covers the SFX
- detected_offset   : ogkalu box (conf >= 0.5) covers only part of the SFX
- detected_low_conf : SFX overlapped only in the 0.25-0.5 harvest band
- missed            : no ogkalu box overlaps the SFX even at 0.25
- skipped_*         : candidate unit is NOT SFX (reason recorded)
- supplementary_*   : recorded observation excluded from the primary count

Directional discipline: single AI annotator, no formal SFX GT exists; all
numbers are directional evidence, formal user review = pre-integration
condition (Task contract).

Usage (from the worktree root):

  python experiments/M2-SFX-DETECT/summarize_sfx_verdicts.py \
      --candidates experiments/M2-SFX-DETECT/sfx-sample-candidates.json \
      --detections experiments/M2-SFX-DETECT/ogkalu-sfx-frames.json \
      --out experiments/M2-SFX-DETECT/sfx-spot-check-verdicts.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def coverage(det_box, sfx_box) -> float:
    """intersection / sfx_area — how much of the SFX the box covers."""
    ix0 = max(det_box[0], sfx_box[0])
    iy0 = max(det_box[1], sfx_box[1])
    ix1 = min(det_box[2], sfx_box[2])
    iy1 = min(det_box[3], sfx_box[3])
    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0
    inter = (ix1 - ix0) * (iy1 - iy0)
    area = (sfx_box[2] - sfx_box[0]) * (sfx_box[3] - sfx_box[1])
    return inter / area if area else 0.0


# --- agent visual verdict table (2026-10-01 pass, grid-anchored) ----------
# sfx_instances: list of {desc, box_xyxy (agent estimate), box_provenance}
# extra observations carry their own verdicts and are excluded from the
# primary frame roll-up when the frame's primary verdict already counts it.
VISUAL_VERDICTS: dict[str, dict] = {
    # ---- Stratum A: C1 user-audited SFX frames ----
    "A__B1-U09": {
        "sfx": "저벅저벅（脚步声，两行手写体）",
        "verdict": "detected_hit",
        "rationale": "ogkalu 检出框覆盖 C1 审定框（저벅/저벅 两行，conf/cls 见下方取值行）；C1 盲区 FP 证据一致",
        "extras": [
            {"desc": "걸들（左上）", "box_xyxy": [55, 285, 205, 365], "verdict": "missed"},
            {"desc": "걸들（右上）", "box_xyxy": [530, 265, 680, 390], "verdict": "detected_low_conf", "note": "conf/cls 见自动取值行"},
            {"desc": "?!（大特效符号）", "box_xyxy": [0, 645, 205, 905], "verdict": "missed"},
        ],
    },
    "A__B1-U12": {
        "sfx": "푸흡（喘气声，竖排）",
        "verdict": "detected_hit",
        "rationale": "ogkalu 检出框覆盖竖排 푸흡 全部字母（conf/cls 见取值行）；C1 盲区 FP 证据一致",
        "extras": [],
    },
    "A__B1-U13": {
        "sfx": "하하（笑声）",
        "verdict": "detected_hit",
        "rationale": "ogkalu 检出框覆盖 하하（conf/cls 见取值行）；C1 盲区 FP 证据一致",
        "extras": [
            {"desc": "빠─（旋转声，画面中部）", "box_xyxy": [180, 215, 285, 335], "verdict": "missed"},
        ],
    },
    "A__B2-U12": {
        "sfx": "싸—아（集体喊/泄气声，超大字）",
        "verdict": "detected_hit",
        "rationale": "ogkalu 全宽大框覆盖全部字面（框过松但含 SFX，conf/cls/坐标见取值行）；阈值边缘样本（C4 正式 block 口径 conf=0.5475）",
        "extras": [
            {"desc": "同区域 3 个 text_bubble 收获带框 (0.27-0.29)", "box_xyxy": None, "verdict": "detected_low_conf", "note": "重复检出同一 SFX 区域"},
        ],
    },
    "A__B2-U14": {
        "sfx": "덜컹（撞击声，两字斜排）",
        "verdict": "detected_offset",
        "rationale": "ogkalu 检出框覆盖「덜」（conf/cls 见取值行）；「컹」（约 [430,100,620,310]，见 extras）无任何检出框——整词部分检出；C1 记录「部分字」一致",
        "extras": [],
    },
    "A__B2-U15": {
        "sfx": "뒤적뒤적（翻找声，两行）",
        "verdict": "detected_hit",
        "rationale": "ogkalu 检出框覆盖两行字面（conf/cls 见取值行）；C1 盲区 FP 证据一致",
        "extras": [],
    },
    "A__A1-U06": {
        "sfx": "끌끌..（坏笑声，伪 GT 框内）",
        "verdict": "detected_low_conf",
        "rationale": "C4/C1 口径 (conf 0.5) 零检出；harvest 0.25 下检出（conf/cls 见取值行），框与 C1 审定框几乎重合——低置信带证据；本次运行与 C4 同权重 hash（037930a8）",
        "extras": [
            {"desc": "악ㄹㄹ~（底部手写拟声）", "box_xyxy": [300, 1044, 690, 1179], "verdict": "detected_low_conf", "note": "conf/cls 见自动取值行"},
        ],
    },
    "A__D-U01": {
        "sfx": "빠걸×3（旋转声，三处）",
        "verdict": "detected_low_conf",
        "rationale": "C4/C1 口径零检出；harvest 0.25 下三处全部检出（逐实例 conf 见取值行，均低于主阈）——「零检出」实为阈值/校准问题",
        "sfx_instances": [
            {"desc": "빠걸（左上）", "box_xyxy": [220, 55, 290, 105], "box_provenance": "agent_estimate"},
            {"desc": "빠걸（右上）", "box_xyxy": [410, 80, 475, 135], "box_provenance": "agent_estimate"},
            {"desc": "빠걸（中左）", "box_xyxy": [215, 150, 290, 205], "box_provenance": "agent_estimate"},
        ],
        "extras": [
            {"desc": "拳头幻觉框（无文字）", "box_xyxy": [430, 195, 490, 250], "verdict": "hallucination", "note": "conf/cls 见自动取值行（框落在手部）"},
        ],
    },
    "A__D-U07": {
        "sfx": "빠악（撞击声，超大红字）",
        "verdict": "missed",
        "rationale": "harvest 0.25 仍零检出——真正的硬盲区（与 C1 D-U07 一致）",
        "sfx_instances": [
            {"desc": "빠악", "box_xyxy": [90, 30, 660, 530], "box_provenance": "agent_estimate"}
        ],
        "extras": [],
    },
    "A__D-U08": {
        "sfx": "콰직（粉碎声，手写刮擦体）",
        "verdict": "missed",
        "rationale": "harvest 0.25 仍零检出（与 C1 D-U08 一致）",
        "sfx_instances": [
            {"desc": "콰직", "box_xyxy": [50, 30, 520, 360], "box_provenance": "agent_estimate"}
        ],
        "extras": [],
    },
    "A__D-U09": {
        "sfx": "투두（坠落声，手写体）",
        "verdict": "missed",
        "rationale": "harvest 0.25 仍零检出（与 C1 D-U09 一致）",
        "sfx_instances": [
            {"desc": "투두", "box_xyxy": [20, 40, 170, 260], "box_provenance": "agent_estimate"}
        ],
        "extras": [],
    },
    # ---- Stratum B: unaudited FP-box candidates ----
    "B__K01_R075_d2": {
        "sfx": None,
        "verdict": "skipped_not_sfx",
        "skip_reason": "旁白字幕横幅（黄底「엄무용 미소가…」）——叙事文字非 SFX",
        "sfx_instances": [],
        "extras": [],
    },
    "B__K01_R035_d8": {
        "sfx": None,
        "verdict": "skipped_not_sfx",
        "skip_reason": "画面内海报印刷小字（ART X vol.2 海报 credit 区）",
        "sfx_instances": [],
        "extras": [],
    },
    "B__K01_R047_d1": {
        "sfx": None,
        "verdict": "skipped_not_sfx",
        "skip_reason": "对白小气泡「내일 봐~」（GT 未标注的真实对白，B1-U05 同类）",
        "sfx_instances": [],
        "extras": [],
    },
    "B__K02_R009_d2": {
        "sfx": None,
        "verdict": "skipped_not_sfx",
        "skip_reason": "手写旁注（蓝字「약 과잉섭취는 몸에 안좋아~」）——手写小注非 SFX",
        "sfx_instances": [],
        "extras": [],
    },
    "B__K03_R155_d0": {
        "sfx": None,
        "verdict": "skipped_not_sfx",
        "skip_reason": "画面内大字标题「사망 기억」（显示文字/章节文案，非拟声）",
        "sfx_instances": [],
        "extras": [],
    },
    "B__K03_R155_d1": {
        "sfx": "화——（爆发声，拖长音）",
        "verdict": "detected_hit",
        "rationale": "ogkalu C4 正式 block 层 FP 框覆盖「화」+ 拖长线（conf 见取值行）；速度线+模糊漩涡背景，典型 SFX 版式",
        "sfx_instances": [{"desc": "화——", "box_xyxy": [95, 285, 290, 390], "box_provenance": "ogkalu FP prior (=SFX 字面)"}],
        "extras": [],
    },
    "B__K03_R027_d0": {
        "sfx": None,
        "verdict": "skipped_not_sfx",
        "skip_reason": "话数标题横幅「언덕 위의 제임스」+「146」+「글그림 주당빵」——出版物元文字",
        "sfx_instances": [],
        "extras": [],
    },
    "B__K04_R021_d6": {
        "sfx": None,
        "verdict": "skipped_not_sfx",
        "skip_reason": "对白小气泡「어?」（GT 未标注）",
        "sfx_instances": [],
        "extras": [],
    },
    "B__K05_R034_d0": {
        "sfx": None,
        "verdict": "skipped_not_sfx",
        "skip_reason": "风格化语气词「넴??？」（顶部裁切、对白性质，非拟声；borderline 登记）",
        "sfx_instances": [],
        "extras": [],
    },
    "B__K06_R000_d2": {
        "sfx": None,
        "verdict": "skipped_not_sfx",
        "skip_reason": "章节标题艺术字「최강전설/기억호」+ credit——出版物元文字",
        "sfx_instances": [],
        "extras": [],
    },
    "B__K06_R096_d1": {
        "sfx": "쭈아앙~（拟声拟态词，白色手写体）",
        "verdict": "detected_hit",
        "rationale": "ogkalu 检出框覆盖字面（conf/cls 见取值行）",
        "sfx_instances": [{"desc": "쭈아앙~", "box_xyxy": [25, 355, 195, 440], "box_provenance": "ogkalu FP prior"}],
        "extras": [],
    },
    "B__K07_R051_d1": {
        "sfx": None,
        "verdict": "skipped_not_sfx",
        "skip_reason": "对白（爆裂形气泡内「아나 ㅅㅂ '우리'를!」）",
        "sfx_instances": [],
        "extras": [],
    },
    "B__K07_R097_d2": {
        "sfx": "철컥철컥（金属扣具/快门声，两行）",
        "verdict": "detected_hit",
        "rationale": "ogkalu 检出框覆盖两行字面（conf/cls 见取值行）",
        "sfx_instances": [{"desc": "철컥철컥", "box_xyxy": [20, 255, 160, 400], "box_provenance": "ogkalu FP prior"}],
        "extras": [],
    },
    "B__K07_R121_d2": {
        "sfx": "뒤적뒤적（翻找声，大字）",
        "verdict": "detected_hit",
        "rationale": "ogkalu 检出框覆盖字面（conf/cls 见取值行）",
        "sfx_instances": [{"desc": "뒤적뒤적", "box_xyxy": [470, 335, 635, 575], "box_provenance": "ogkalu FP prior"}],
        "extras": [
            {"desc": "ㅋㅋㅋ（笑声字母）", "box_xyxy": [505, 240, 640, 345], "verdict": "detected_low_conf", "note": "conf/cls 见自动取值行"},
            {"desc": "꼬르륵（腹鸣声，画面左下）", "box_xyxy": [0, 785, 215, 900], "verdict": "missed"},
        ],
    },
    "B__K08_R003_d1": {
        "sfx": None,
        "verdict": "skipped_not_sfx",
        "skip_reason": "省略号沉默气泡「……▪」（非 SFX）",
        "sfx_instances": [],
        "extras": [],
    },
    "B__K09_R098_d0": {
        "sfx": None,
        "verdict": "skipped_hallucination",
        "skip_reason": "ogkalu 0.61 框落在建筑窗户纹理上——无文字（模型幻觉）",
        "sfx_instances": [],
        "extras": [],
    },
    "B__K09_R024_d3": {
        "sfx": None,
        "verdict": "skipped_not_sfx",
        "skip_reason": "对白气泡（「그게 나든 바야」，被帧边裁切）",
        "sfx_instances": [],
        "extras": [],
    },
    "B__K10_R129_d0": {
        "sfx": "RrRrrr（手机振动拟声，白色手写体）",
        "verdict": "detected_low_conf",
        "rationale": "prior 单元本身落在手机屏幕 UI 文字「발신번호 표시제한」（=skip），但画面含振动拟声 Rrrrr：ogkalu 检出低于主阈 0.5（conf 见取值行）——帧作为额外观察纳入主样本（选样方法披露）",
        "sfx_instances": [
            {"desc": "Rrrrr（大）", "box_xyxy": [355, 320, 600, 590], "box_provenance": "agent_estimate"},
            {"desc": "rRrRr+状态栏图标（小）", "box_xyxy": [55, 105, 345, 240], "verdict_extra": True, "box_provenance": "agent_estimate"},
        ],
        "extras": [],
    },
    "B__K10_R073_d2": {
        "sfx": "끼아아악（尖叫，斜排手写体）",
        "verdict": "detected_hit",
        "rationale": "ogkalu 检出框覆盖字面（conf/cls 见取值行；class 见取值行——自由 SFX 字被判 text_bubble 属类间混淆证据）",
        "sfx_instances": [{"desc": "끼아아악", "box_xyxy": [365, 1175, 620, 1390], "box_provenance": "ogkalu FP prior"}],
        "extras": [
            {"desc": "꺘약（中景拟声）", "box_xyxy": [380, 490, 590, 870], "verdict": "missed"},
        ],
    },
    # ---- Stratum C: unaudited zero-detection regions ----
    "C__K01_R069": {
        "sfx": "칼칼（傻笑/得意声变体，粉色圆体字，两处）",
        "verdict": "missed",
        "rationale": "harvest 0.25 仍零检出——C1 抽检之外的新增硬盲区样本",
        "sfx_instances": [
            {"desc": "촬/칼（左）", "box_xyxy": [200, 35, 275, 140], "box_provenance": "agent_estimate"},
            {"desc": "칼（右）", "box_xyxy": [390, 90, 465, 190], "box_provenance": "agent_estimate"},
        ],
        "extras": [],
    },
    "C__K03_R107": {
        "sfx": None,
        "verdict": "skipped_no_text",
        "skip_reason": "画面无任何文字（人物特写）",
        "sfx_instances": [],
        "extras": [],
    },
    "C__K03_R113": {
        "sfx": "뙇×n（坠落撞击声，环形重复字母）",
        "verdict": "detected_offset",
        "rationale": "C4/C1 口径零检出；harvest 0.25 下检出框（conf/cls 见取值行）仅覆盖左弧部分字母（环形排布的大部分字母未检出）",
        "sfx_instances": [{"desc": "뙇 环（整体范围）", "box_xyxy": [55, 20, 610, 520], "box_provenance": "agent_estimate"}],
        "extras": [],
    },
    "C__K05_R011": {
        "sfx": None,
        "verdict": "skipped_no_text",
        "skip_reason": "画面无任何文字（怪物嘴部特写）",
        "sfx_instances": [],
        "extras": [],
    },
    "C__K05_R026": {
        "sfx": None,
        "verdict": "skipped_no_text",
        "skip_reason": "画面无任何文字（背影）",
        "sfx_instances": [],
        "extras": [],
    },
    "C__K06_R038": {
        "sfx": None,
        "verdict": "supplementary_effect_symbol",
        "skip_reason": "「!!」惊讶特效符号（C1 A1-U02 同源）；非拟声词，不入主样本；harvest 0.25 下低置信检出（conf/cls 见取值行，补充观察）",
        "sfx_instances": [],
        "extras": [],
    },
    "C__K07_R103": {
        "sfx": "철컹（坠落巨响，超大字）",
        "verdict": "missed",
        "rationale": "harvest 0.25 下 SFX 本体零检出；唯一检出框（conf 见取值行）落在建筑窗户纹理=幻觉",
        "sfx_instances": [{"desc": "철컹", "box_xyxy": [0, 0, 620, 230], "box_provenance": "agent_estimate"}],
        "extras": [],
    },
    "C__K07_R095": {
        "sfx": None,
        "verdict": "skipped_no_text",
        "skip_reason": "画面无任何文字（塔顶游客）",
        "sfx_instances": [],
        "extras": [],
    },
    "C__K08_R033": {
        "sfx": "수악（打击声，竖排白描边）",
        "verdict": "detected_low_conf",
        "rationale": "C4/C1 口径零检出；harvest 0.25 下检出框覆盖字面（conf/cls 见取值行）",
        "sfx_instances": [{"desc": "수악", "box_xyxy": [230, 100, 380, 580], "box_provenance": "agent_estimate"}],
        "extras": [],
    },
    "C__K08_R019": {
        "sfx": "빠직 + 아（爆裂/尖叫，两处大字）",
        "verdict": "missed",
        "rationale": "harvest 0.25 仍零检出——新增硬盲区样本",
        "sfx_instances": [
            {"desc": "빠직（上）", "box_xyxy": [30, 40, 330, 420], "box_provenance": "agent_estimate"},
            {"desc": "아（下）", "box_xyxy": [60, 950, 330, 1450], "box_provenance": "agent_estimate"},
        ],
        "extras": [],
    },
    "C__K09_R112": {
        "sfx": None,
        "verdict": "supplementary_uncertain",
        "skip_reason": "单字 swoosh 效果线（疑似「휙/슉」残形，不确定是否拟声）；低置信检出（conf/cls 见取值行）——证据不足，不入主样本（补充观察）",
        "sfx_instances": [],
        "extras": [],
    },
    "C__K09_R001": {
        "sfx": "송송 + 삐직삐직（挖土/电子音，两处）",
        "verdict": "missed",
        "rationale": "harvest 0.25 仍零检出——新增硬盲区样本",
        "sfx_instances": [
            {"desc": "송송", "box_xyxy": [100, 640, 280, 840], "box_provenance": "agent_estimate"},
            {"desc": "삐직삐직", "box_xyxy": [0, 1280, 190, 1450], "box_provenance": "agent_estimate"},
        ],
        "extras": [],
    },
    "C__K10_R144": {
        "sfx": None,
        "verdict": "skipped_no_text",
        "skip_reason": "画面无任何文字",
        "sfx_instances": [],
        "extras": [],
    },
    "C__K10_R143": {
        "sfx": None,
        "verdict": "skipped_no_text",
        "skip_reason": "画面无任何文字",
        "sfx_instances": [],
        "extras": [],
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--detections", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    cand = json.loads(args.candidates.read_text(encoding="utf-8"))
    det = json.loads(args.detections.read_text(encoding="utf-8"))
    det_by_region = det["regions"]

    rows = []
    for c in cand["candidates"]:
        vid = c["sample_id"]
        vv = VISUAL_VERDICTS.get(vid)
        if vv is None:
            raise SystemExit(f"missing visual verdict for {vid}")
        region_key = f"{c['case_id']}_R{c['region_index']:03d}"
        region_dets = det_by_region[region_key]["detections"]
        sfx_instances = []
        if vv.get("sfx_instances"):
            sfx_instances = vv["sfx_instances"]
        elif vv.get("sfx") and c.get("sfx_prior_box_xyxy"):
            sfx_instances = [
                {
                    "desc": vv["sfx"],
                    "box_xyxy": c["sfx_prior_box_xyxy"],
                    "box_provenance": c["prior_box_provenance"],
                }
            ]
        # R6 (DSH r1): conf/cls values are NEVER hand-written in prose —
        # they are appended from the committed payload (ogkalu-sfx-frames.json)
        # and the frozen frames-export (C4 block layer) at generation time.
        annotated = []
        for inst in sfx_instances:
            inst = {k: v for k, v in inst.items() if k != "verdict_extra"}  # R14: unused field removed
            best_cov, best_det = 0.0, None
            for d in region_dets:
                cov = coverage(d["box_xyxy"], inst["box_xyxy"])
                if cov > best_cov:
                    best_cov, best_det = cov, d
            annotated.append(
                {
                    **inst,
                    "best_ogkalu_overlap": {
                        "coverage_of_sfx": round(best_cov, 3),
                        "det_box_xyxy": best_det["box_xyxy"] if best_det else None,
                        "conf": best_det["conf"] if best_det else None,
                        "cls": best_det["cls"] if best_det else None,
                    },
                }
            )
        # frame-level auto value line: best-overlap detection over the FIRST
        # primary instance (+ C4 block-layer FP conf for stratum-B priors)
        value_bits = []
        if annotated:
            bo = annotated[0]["best_ogkalu_overlap"]
            if bo["conf"] is not None:
                value_bits.append(
                    f"[payload 取值] ogkalu 最佳重叠检出框 conf={bo['conf']} cls={bo['cls']} "
                    f"coverage={bo['coverage_of_sfx']} box={bo['det_box_xyxy']}"
                )
            else:
                value_bits.append("[payload 取值] ogkalu 对该实例无任何重叠检出框（harvest 0.25）")
        if c.get("fp_conf") is not None:
            value_bits.append(
                f"[frames-export 取值] C4 正式 block 层 FP conf={c['fp_conf']:.4f} cls=merged_block"
            )
        rationale = vv.get("rationale") or vv.get("skip_reason") or ""
        if value_bits:
            rationale = rationale + "｜" + "；".join(value_bits)
        # extras auto value lines (same rule, per extra box)
        extras_out = []
        for ex in vv.get("extras", []):
            ex = dict(ex)
            if ex.get("box_xyxy"):
                bc, bd = 0.0, None
                for d in region_dets:
                    cov = coverage(d["box_xyxy"], ex["box_xyxy"])
                    if cov > bc:
                        bc, bd = cov, d
                ex["best_ogkalu_overlap"] = {
                    "coverage_of_sfx": round(bc, 3),
                    "conf": bd["conf"] if bd else None,
                    "cls": bd["cls"] if bd else None,
                }
            extras_out.append(ex)
        rows.append(
            {
                "sample_id": vid,
                "stratum": c["stratum"],
                "case_id": c["case_id"],
                "region_index": c["region_index"],
                "region_key": region_key,
                "unit_id": c.get("unit_id"),
                "sfx_summary": vv.get("sfx"),
                "frame_verdict": vv["verdict"],
                "rationale": rationale,
                "sfx_instances": annotated,
                "extras": extras_out,
                "ogkalu_detections_all": region_dets,
                "preview": f"ogkalu__{region_key}.png",
            }
        )

    primary = [r for r in rows if r["frame_verdict"] in
               ("detected_hit", "detected_offset", "detected_low_conf", "missed")]
    n_primary = len(primary)
    hit = sum(1 for r in primary if r["frame_verdict"] == "detected_hit")
    offset = sum(1 for r in primary if r["frame_verdict"] == "detected_offset")
    low = sum(1 for r in primary if r["frame_verdict"] == "detected_low_conf")
    missed = sum(1 for r in primary if r["frame_verdict"] == "missed")
    det_at_primary = hit + offset  # frames with >=1 box at conf>=0.5 on SFX
    det_any = n_primary - missed

    payload = {
        "schema": "m2-sfx-detect/sfx-spot-check-verdicts@1",
        "task": "M2-SFX-DETECT-EVAL",
        "evidence_strength": (
            "DIRECTIONAL — single AI annotator (agent visual pass on grid "
            "previews), no formal SFX GT exists; formal user review is a "
            "pre-integration condition (Task contract / C1 precedent)"
        ),
        "sample_method": (
            "stratified candidates (A=C1 user-audited SFX frames, B=unaudited "
            "FP boxes seeded quota, C=unaudited zero-det regions seeded "
            "quota); primary sample = frames where the agent visually "
            "confirmed onomatopoeia SFX; skipped units keep reasons"
        ),
        "inputs": {
            "candidates": str(args.candidates),
            "detections": str(args.detections),
        },
        "summary": {
            "n_candidate_units": len(rows),
            "n_primary_sfx_frames": n_primary,
            "n_skipped_not_sfx": sum(1 for r in rows if r["frame_verdict"].startswith("skipped_")),
            "n_supplementary_excluded": sum(1 for r in rows if r["frame_verdict"].startswith("supplementary_")),
            "frame_verdict_counts": {
                "detected_hit(conf>=0.5_covers_sfx)": hit,
                "detected_offset(conf>=0.5_partial)": offset,
                "detected_low_conf(0.25-0.5_band_only)": low,
                "missed(zero_even_at_0.25)": missed,
            },
            "frame_detection_rate": {
                "at_primary_conf_0.5": {
                    "value": round(det_at_primary / n_primary, 4),
                    "fraction": f"{det_at_primary}/{n_primary}",
                },
                "at_harvest_conf_0.25": {
                    "value": round(det_any / n_primary, 4),
                    "fraction": f"{det_any}/{n_primary}",
                },
            },
            "in_frame_extra_sfx_observations": sum(
                len(r["extras"]) for r in rows if r["extras"]
            ),
        },
        "primary_frames": primary,
        "all_candidate_rows": rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8"
    )
    print(f"primary SFX frames: {n_primary} (hit={hit} offset={offset} "
          f"low_conf={low} missed={missed})")
    print(f"frame detection rate @0.5 = {det_at_primary}/{n_primary} "
          f"= {det_at_primary/n_primary:.3f}; @0.25 = {det_any}/{n_primary} "
          f"= {det_any/n_primary:.3f}")
    print(f"verdicts -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
