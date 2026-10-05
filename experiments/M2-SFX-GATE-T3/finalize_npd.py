"""M2-SFX-GATE-T3 AC3 npd 定稿：分歧仲裁回写 + npd-gt.json + 派生 GT 交集/差集统计。

仲裁者=入册会话独立标准（逐单元叠框预览+原页实看），判据四条（不引用任何既有 GT 坐标）：
  ①字形艺术化/效果字形态（vs 规整印刷+语法句）
  ②容器语义内容（对白气泡/解说带/物件）→ 非 SFX
  ③画面线稿/动作线（无字形结构）→ 非 SFX
  ④实例粒度（连续紧贴字串=一实例；一框多独立实例=粒度错误）
处置枚举：
  keep            单方候选指向真实 SFX，框入册
  keep-merged     与对方单元同目标 IoU<0.5 配对失败（小框敏感/粒度差），定稿框入册
                  （定稿框=union 或 correct 指定框），对方记 delete-duplicate
  delete-duplicate 同目标冗余（对方框/合并框已承接）
  delete          非 SFX（判据①②③）或框内无字形
  correct         是 SFX 但框需修（定稿框=修正框）
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
NPJ = REPO / "training_data" / "sfx-v1" / "gate-t3" / "npd-judgments"
GT_OUT = REPO / "training_data" / "sfx-v1" / "gate-t3" / "npd-gt.json"
R3M = Path(r"G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R3-zcode/training_data/sfx-v1/annotate-r3/preannotate/manifest.r3.json")
IOU_MATCH = 0.5

# ---------------------------------------------------------------------------
# 仲裁终裁表（逐单元；rationale 全文在 arbiter/batch-1.json judgments 内）
# ---------------------------------------------------------------------------
VERDICTS: dict[str, dict] = {
    # ---- pre-k01（21）----
    "R4-pre-k01-D00": {"verdict": "keep-merged", "final_xyxy": [563.0, 3639.0, 625.0, 3699.0]},
    "R4-pre-k01-D08": {"verdict": "delete-duplicate"},
    "R4-pre-k01-D01": {"verdict": "keep-merged", "final_xyxy": [25.0, 4168.0, 155.0, 4310.0]},
    "R4-pre-k01-D10": {"verdict": "delete-duplicate"},
    "R4-pre-k01-D02": {"verdict": "keep-merged", "final_xyxy": [490.0, 7913.0, 560.0, 7972.0]},
    "R4-pre-k01-D11": {"verdict": "delete-duplicate"},
    "R4-pre-k01-D03": {"verdict": "keep", "final_xyxy": [210.0, 13534.0, 307.0, 13617.0]},
    "R4-pre-k01-D12": {"verdict": "delete-duplicate"},
    "R4-pre-k01-D04": {"verdict": "keep-merged", "final_xyxy": [214.0, 29848.0, 267.0, 29937.0]},
    "R4-pre-k01-D13": {"verdict": "delete-duplicate"},
    "R4-pre-k01-D05": {"verdict": "delete"},
    "R4-pre-k01-D14": {"verdict": "keep", "final_xyxy": [172.0, 35913.0, 234.0, 35962.0]},
    "R4-pre-k01-D06": {"verdict": "delete"},
    "R4-pre-k01-D15": {"verdict": "delete"},
    "R4-pre-k01-D16": {"verdict": "delete"},
    "R4-pre-k01-D07": {"verdict": "keep", "final_xyxy": [144.0, 45503.0, 234.0, 45640.0]},
    "R4-pre-k01-D17": {"verdict": "keep", "final_xyxy": [121.0, 45696.0, 236.0, 45842.0]},
    "R4-pre-k01-D09": {"verdict": "keep", "final_xyxy": [292.0, 4103.0, 340.0, 4136.0]},
    "R4-pre-k01-D18": {"verdict": "keep", "final_xyxy": [427.0, 49845.0, 486.0, 49915.0]},
    "R4-pre-k01-D19": {"verdict": "keep", "final_xyxy": [351.0, 49851.0, 398.0, 49903.0]},
    "R4-pre-k01-D20": {"verdict": "keep", "final_xyxy": [265.0, 50015.0, 335.0, 50105.0]},
    # ---- pre-k02（6；三对同目标小框 IoU 配对失败）----
    "R4-pre-k02-D00": {"verdict": "keep-merged", "final_xyxy": [232.0, 1042.0, 272.0, 1092.0]},
    "R4-pre-k02-D03": {"verdict": "delete-duplicate"},
    "R4-pre-k02-D01": {"verdict": "keep-merged", "final_xyxy": [251.0, 1938.0, 314.0, 1990.0]},
    "R4-pre-k02-D04": {"verdict": "delete-duplicate"},
    "R4-pre-k02-D02": {"verdict": "keep-merged", "final_xyxy": [312.0, 5953.0, 357.0, 5994.0]},
    "R4-pre-k02-D05": {"verdict": "delete-duplicate"},
    # ---- pre-k08（8）----
    "R4-pre-k08-D00": {"verdict": "keep-merged", "final_xyxy": [235.0, 6048.0, 326.0, 6300.0]},
    "R4-pre-k08-D03": {"verdict": "delete-duplicate"},
    "R4-pre-k08-D01": {"verdict": "keep", "final_xyxy": [107.0, 31745.0, 375.0, 32070.0]},
    "R4-pre-k08-D02": {"verdict": "keep", "final_xyxy": [425.0, 31972.0, 702.0, 32315.0]},
    "R4-pre-k08-D06": {"verdict": "delete"},
    "R4-pre-k08-D04": {"verdict": "delete"},
    "R4-pre-k08-D05": {"verdict": "correct", "final_xyxy": [220.0, 28298.0, 520.0, 28430.0]},
    "R4-pre-k08-D07": {"verdict": "keep", "final_xyxy": [610.0, 44120.0, 648.0, 44218.0]},
    # ---- pre-k09（16）----
    "R4-pre-k09-D00": {"verdict": "keep-merged", "final_xyxy": [422.0, 8520.0, 690.0, 9110.0]},
    "R4-pre-k09-D09": {"verdict": "delete-duplicate"},
    "R4-pre-k09-D01": {"verdict": "keep", "final_xyxy": [91.0, 10921.0, 243.0, 11217.0]},
    "R4-pre-k09-D11": {"verdict": "delete-duplicate"},
    "R4-pre-k09-D12": {"verdict": "delete-duplicate"},
    "R4-pre-k09-D02": {"verdict": "keep", "final_xyxy": [167.0, 34064.0, 473.0, 34175.0]},
    "R4-pre-k09-D13": {"verdict": "delete-duplicate"},
    "R4-pre-k09-D03": {"verdict": "keep", "final_xyxy": [373.0, 49635.0, 555.0, 49772.0]},
    "R4-pre-k09-D04": {"verdict": "keep", "final_xyxy": [363.0, 50765.0, 522.0, 50881.0]},
    "R4-pre-k09-D05": {"verdict": "delete"},
    "R4-pre-k09-D06": {"verdict": "keep", "final_xyxy": [298.0, 56455.0, 400.0, 56615.0]},
    "R4-pre-k09-D15": {"verdict": "delete-duplicate"},
    "R4-pre-k09-D07": {"verdict": "keep", "final_xyxy": [333.0, 68360.0, 395.0, 68420.0]},
    "R4-pre-k09-D08": {"verdict": "keep", "final_xyxy": [25.0, 7492.0, 305.0, 8030.0]},
    "R4-pre-k09-D10": {"verdict": "keep", "final_xyxy": [187.0, 10200.0, 268.0, 10312.0]},
    "R4-pre-k09-D14": {"verdict": "delete"},
}

RATIONALES: dict[str, str] = {
    "R4-pre-k01-D00": "实看 sheet+rationale：绿底右上灰色「호호/후훗」笑声小字独立无气泡，a/b 双方各框（563-625/584-620 同区），字 40px 级小框 IoU 0.38 配对失败——同目标 keep-merge，定稿=union。",
    "R4-pre-k01-D08": "与 D00 同目标（对方框已由合并框承接），delete-duplicate。",
    "R4-pre-k01-D01": "实看 sheet：粉底放射集中线上「오호호」蓝白描边大字斜排+星光装饰，笑声效果字无气泡。a/b 双框同目标（IoU 0.25，字斜排致框差大），keep-merge 定稿=union（含三字+描边出血）。",
    "R4-pre-k01-D10": "与 D01 同目标（对方框已由合并框承接），delete-duplicate。",
    "R4-pre-k01-D02": "实看 sheet：绿底「딸기..」黑色手写小字+粉圆点（草莓嘟哝拟态），效果字无容器。a/b 双框同目标 IoU 0.46 差 0.04 配对失败，keep-merge 定稿=union。",
    "R4-pre-k01-D11": "与 D02 同目标（对方框已由合并框承接），delete-duplicate。",
    "R4-pre-k01-D03": "实看高清叠框（k01_D03_D12_hires.png 4x）：粉墙白字蓝描边「달까」二字分列黑竖线两侧，字群实际 y≈13530-13600；a 框基本套准（右下少量空白），b 框偏上 50px 仅套字顶。字形带描边装饰、独立无容器，按 KO 域效果字口径 keep=a 框。",
    "R4-pre-k01-D12": "与 D03 同目标，b 框偏上未套准字形（高清图实证），delete-duplicate。",
    "R4-pre-k01-D04": "实看 sheet：深蓝底粉白描边竖排「울/올느」抽泣效果字无气泡。a/b 双框同目标（b⊂a），keep-merge 定稿=a 框（b 完全包含于 a）。",
    "R4-pre-k01-D13": "与 D04 同目标（合并框=a 框已承接），delete-duplicate。",
    "R4-pre-k01-D05": "实看高清叠框（k01_D05_D14_hires.png 2x）：a 框 [357,35910,470,36000] 区域为大气泡「왕유리는 없냐? 왕유리??」右下半+空白，「아」「하」字均在框外——框内主体是对白气泡无独立字形，delete。",
    "R4-pre-k01-D14": "实看高清叠框：b 框恰好套住左「아」白字红描边（叹声效果字，无气泡独立于画面），keep=b 框。",
    "R4-pre-k01-D06": "实看 sheet（D15/D16 同区）：橙色横贯解说带「뚜두구 뚜뚜뚜-기상음악 나이베 어~」——「기상음악 나이베어~」（起床音乐响了）为陈述句旁白解说，横幅=画面容器，按 R2-BJ17-B02 容器判例其内文字=容器语义内容非画面空间效果音，delete。",
    "R4-pre-k01-D15": "同一解说带左段（뚜뚜루 뚜뚜뚜 喇叭声段）：虽为拟声形态，但与右侧陈述句连排构成完整解说带容器内容，一体 delete（判据②容器语义）。",
    "R4-pre-k01-D16": "同一解说带右段（기상음악 나이베에~ 歌词/解说），delete（判据②）。",
    "R4-pre-k01-D07": "实看 sheet：蓝底白字橙描边竖排「걸걸」潦草艺术字（厚脸皮笑声）独立无气泡，keep=a 框。",
    "R4-pre-k01-D17": "实看 sheet：蓝底白字橙描边「끝끝」竖排斜列（得意拟态）效果字，与 D07 同域异位（y45696 vs 45503 无重叠），keep=b 框。",
    "R4-pre-k01-D09": "实看 sheet：紫底「냬엠☆」粉紫描边小字+星形装饰（哈欠拟态），效果字，keep=b 框。",
    "R4-pre-k01-D18": "实看 sheet：浅蓝字竖排「개웃겨」（爆笑感叹效果字）+描边装饰，KO 域反应感叹效果字惯例（彩色描边、无容器、字形装饰化），keep=b 框。",
    "R4-pre-k01-D19": "实看 sheet：斜排「ㅋㅋ」浅蓝描边小字（笑声）散置群像间，keep=b 框。",
    "R4-pre-k01-D20": "实看 sheet：白字粉描边小字群散布（群像笑闹效果字群，b 读 ㅋ 群），与同区共识效果字群同域，keep=b 框。",
    "R4-pre-k02-D00": "实看 sheet：窗前蓝灰描边竖排小拟声字（a 读 푸훕/b 读 푸덕），男角色嘴旁无气泡。字仅 30x48px，a/b 框 10px 偏移 IoU 0.29 配对失败——同目标 keep-merge 定稿=union。",
    "R4-pre-k02-D03": "与 D00 同目标（合并框承接），delete-duplicate。",
    "R4-pre-k02-D01": "实看 sheet：棕色描边小字「콜록/쾅쾅」（咳嗽/砰砰拟声）+黄点装饰，a 框偏左含纸巾边、b 框套准字。同目标 keep-merge 定稿=union。",
    "R4-pre-k02-D04": "与 D01 同目标（合并框承接），delete-duplicate。",
    "R4-pre-k02-D02": "实看 sheet：橙色手写小字「웅기?」样+问号（女角色旁拟态小字），无气泡。a/b 双框同目标 IoU 0.35 配对失败，keep-merge 定稿=union。",
    "R4-pre-k02-D05": "与 D02 同目标（合并框承接），delete-duplicate。",
    "R4-pre-k08-D00": "实看 sheet：小拳面板左上棕红描边竖排变形字「드르륵/쿵직类」（a/b 读法异、目标同）。a 框紧套字形，b 框左扩 130px 含面板空白——keep-merge 定稿=a 框（correct：弃 b 框过宽部分）。",
    "R4-pre-k08-D03": "与 D00 同目标（b 框过宽未采用），delete-duplicate。",
    "R4-pre-k08-D01": "实看 sheet：红色巨型变形冲击字左簇（벅，双环部件）+集中线，keep=a 框。",
    "R4-pre-k08-D02": "实看 sheet：红色巨型变形冲击字右簇（컥，圆+长笔画）——a 按词拆排两簇分框符合实例粒度，keep=a 框（框稍大含集中线下部可接受）。",
    "R4-pre-k08-D06": "实看 sheet：b 框一框套「벅+컥」两簇独立实例（中间隔人物）——一框多实例粒度错误，两实例已由 D01/D02 承接，delete。",
    "R4-pre-k08-D04": "实看 sheet：白色圆角气泡容器内规整印刷体「ㅋㅋㅋ」——气泡对白（笑声文字化）非画面空间效果音，b 自述「不确定照标」；按 BJ36 仲裁同判据（容器+规整字形+语法语义）delete。",
    "R4-pre-k08-D05": "实看 sheet：黑色几何粗直笔画连写「크크크크类」（连击/笑声拟声变形字）无气泡——是 SFX；但 b 框右下 30% 含人物头发/脸。correct 收窄至字带 [220,28298,520,28430]（x2 598→520 去人物、y2 28472→28430 去脸缘）。",
    "R4-pre-k08-D07": "实看 sheet：白底棕色斜排小字「훗」形（冷笑拟声）字形结构清晰非线稿，keep=b 框。",
    "R4-pre-k09-D00": "实看 sheet：深蓝速度线背景斜排草书细笔画大字+底部双圆圈（坠落拟声 쿵/옴）。a/b 双框同目标 IoU 0.44 配对失败，keep-merge 定稿=union。",
    "R4-pre-k09-D09": "与 D00 同目标（合并框承接），delete-duplicate。",
    "R4-pre-k09-D01": "实看 sheet：深色手写斜排「퍽퍽!」两枚字块上下紧贴（间隙≈8px）构成连续拟声串——连续紧贴字串按一实例计，keep=a 组合框；b 拆分双框记 delete-duplicate。",
    "R4-pre-k09-D11": "与 D01 同目标上枚（连续字串由组合框承接），delete-duplicate。",
    "R4-pre-k09-D12": "与 D01 同目标下枚（连续字串由组合框承接），delete-duplicate。",
    "R4-pre-k09-D02": "实看 sheet：白字描边「✱너무신남✱」横排效果字+两侧十字爆花/金星装饰（兴奋拟态）。a 框套准字带+装饰，keep=a 框。",
    "R4-pre-k09-D13": "与 D02 同目标（b 框下延至 y34312 含人物头部），delete-duplicate。",
    "R4-pre-k09-D03": "实看 sheet：矩形效果音框（尖角、无尾）内大号手写艺术字「디동」（瘫倒拟声）——与对白气泡的区别在字形艺术化+框形（KO webtoon 效果音框惯例），keep=a 框。",
    "R4-pre-k09-D04": "实看 sheet：矩形效果音框内手写粗笔「벅격」（撞击拟声）艺术字，同 D03 判据，keep=a 框。",
    "R4-pre-k09-D05": "实看 sheet：浅黄纸上单笔 ㄱ 形锯齿钩笔画——无字形结构（非文字，判据③动作线/爪痕），delete。",
    "R4-pre-k09-D06": "实看 sheet：浅黄纸上锯齿锋利笔画字「탁类」（抓取拟声）字形结构可辨，keep=a 框。",
    "R4-pre-k09-D15": "实看 sheet：b 大框 [156,56440,452,56645] 套整个黄纸区（含手部+弧线+多处字迹）——粒度粗含非文字区域，字迹已由 D06 承接，delete-duplicate。",
    "R4-pre-k09-D07": "实看 sheet：白底黑手写小字「쿰~」+波浪符（蹭头拟声），keep=a 框。",
    "R4-pre-k09-D08": "实看 sheet：深蓝背景竖长排布尖锐笔画组合变形字（쿵쿵落地声变形，笔画群有字块结构非平行速度线），keep=b 框。",
    "R4-pre-k09-D10": "实看 sheet：黑色毛笔字「탁」斜排+右下白色冲击箭头，字清晰，框含箭头可接受（冲击一体呈现），keep=b 框。",
    "R4-pre-k09-D14": "实看 sheet：白底规整印刷体粗黑「뭐?！」——完全规整字形（无任何艺术化变形）+疑问句语法语义+无容器压画面的台词强调，非以声音拟形的效果音（b 自述「照标」），按判据①delete。",
}

# keep-merged 配对表（定稿框并入方 ← 被承接方）
MERGE_PAIRS = [
    ("R4-pre-k01-D00", "R4-pre-k01-D08"), ("R4-pre-k01-D01", "R4-pre-k01-D10"),
    ("R4-pre-k01-D02", "R4-pre-k01-D11"), ("R4-pre-k01-D04", "R4-pre-k01-D13"),
    ("R4-pre-k02-D00", "R4-pre-k02-D03"), ("R4-pre-k02-D01", "R4-pre-k02-D04"),
    ("R4-pre-k02-D02", "R4-pre-k02-D05"), ("R4-pre-k08-D00", "R4-pre-k08-D03"),
    ("R4-pre-k09-D00", "R4-pre-k09-D09"),
]


def iou(a, b) -> float:
    ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
    ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua


def main() -> int:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    div = json.loads((NPJ / "divergence.json").read_text(encoding="utf-8"))
    cons = json.loads((NPJ / "consensus.json").read_text(encoding="utf-8"))

    # 1) 断言：仲裁表覆盖全部分歧单元且 ID 无重号
    ids = [u["id"] for u in div["divergence"]]
    assert len(set(ids)) == len(ids), "divergence ID 重号"
    assert set(VERDICTS) == set(ids), (
        f"仲裁表与分歧单元失配: 缺 {set(ids)-set(VERDICTS)} 多 {set(VERDICTS)-set(ids)}")
    for pair in MERGE_PAIRS:
        assert VERDICTS[pair[0]]["verdict"] == "keep-merged"
        assert VERDICTS[pair[1]]["verdict"] == "delete-duplicate"

    # 2) 回写 divergence 状态 + 仲裁 rationale
    for u in div["divergence"]:
        v = VERDICTS[u["id"]]
        u["status"] = "arbiter-" + v["verdict"]
        u["arbiter_rationale"] = RATIONALES[u["id"]]
        if "final_xyxy" in v:
            u["final_xyxy"] = v["final_xyxy"]
    div["n_arbitrated"] = len(VERDICTS)
    div["arbiter"] = ("入册会话独立标准（逐单元叠框预览/高清复核+原页实看；判据=字形艺术化/"
                      "容器语义/画面线稿/实例粒度四条，不引用任何既有 GT 坐标；"
                      "R3 仲裁先例容器判例沿用）；arbiter/batch-1.json")
    div["arbitrated_at_utc"] = now
    (NPJ / "divergence.json").write_text(
        json.dumps(div, ensure_ascii=False, indent=1), encoding="utf-8")

    # 3) npd-gt.json：共识 union 框 + 分歧定稿框（keep/keep-merged/correct）
    pages: dict[str, dict] = {}
    for c in cons["consensus"]:
        pg = pages.setdefault(c["page"], {"boxes": []})
        pg["boxes"].append({
            "xyxy": c["union_xyxy"],
            "rationale": f"consensus IoU={c['iou_ab']}｜a: {c['rationale_codex']}｜b: {c['rationale_agy']}",
            "chain": f"{c['id']}=keep-union",
        })
    for u in div["divergence"]:
        if u["status"] in ("arbiter-keep", "arbiter-keep-merged", "arbiter-correct"):
            pg = pages.setdefault(u["page"], {"boxes": []})
            pg["boxes"].append({
                "xyxy": VERDICTS[u["id"]]["final_xyxy"],
                "rationale": (f"divergence({u['proposer']})｜{RATIONALES[u['id']]}"),
                "chain": f"{u['id']}={u['status']}",
            })
    dist = Counter(u["status"] for u in div["divergence"])

    # 4) 派生 GT 交集/差集统计（IoU>=0.5 同页贪心）
    m3 = json.loads(R3M.read_text(encoding="utf-8"))
    by_sid = {s["sample_id"]: s for s in m3}
    stats: dict[str, dict] = {}
    tot = Counter()
    for pg, d in sorted(pages.items()):
        s = by_sid[pg]
        assert s["annotation_status"] == "complete" and s["provenance"]["type"] == "asset_case"
        derived = [[b["polygon"][0][0], b["polygon"][0][1],
                    b["polygon"][2][0], b["polygon"][2][1]] for b in s["boxes"]]
        npd = [b["xyxy"] for b in d["boxes"]]
        pairs, only_der, only_npd = _match(derived, npd)
        stats[pg] = {
            "page_wh": [s["image"]["width"], s["image"]["height"]],
            "derived_gt": len(derived), "npd_gt": len(npd),
            "matched_iou05": len(pairs),
            "derived_only": len(only_der), "npd_only": len(npd) - len(pairs),
            "matched_iou_mean": round(sum(p[0] for p in pairs) / len(pairs), 4) if pairs else 0.0,
            "matched_pairs": [{"iou": round(v, 4), "derived_xyxy": dv, "npd_xyxy": nv}
                              for v, dv, nv in pairs],
            "derived_only_xyxy": [dv for _v, dv in only_der],
            "npd_only_xyxy": [nv for _v, nv in only_npd],
        }
        tot["derived"] += len(derived)
        tot["npd"] += len(npd)
        tot["matched"] += len(pairs)
    summary = {
        "derived_total": tot["derived"], "npd_total": tot["npd"],
        "matched": tot["matched"],
        "derived_only": tot["derived"] - tot["matched"],
        "npd_only": tot["npd"] - tot["matched"],
        "note": ("交集=双方各自独立标注在同一视觉目标上命中（IoU>=0.5）；"
                 "差集两向=GT 偏差度量（derived_only=AI 直接标注发现派生 GT 之外的目标 "
                 "或派生检出粒度/定位差；npd_only 同理反向）"),
    }

    gt_doc = {
        "kind": "sfx-gate-t3/npd-gt@1",
        "purpose": ("AC3 KO 非派生 GT 切片定稿：双 AI 独立整页标注（隔离纪律：任务书零既有"
                    "坐标，无模型输出/预标注/既有 GT 引用）→IoU>=0.5 比对→分歧第三方仲裁"
                    "（重看图）→本文件为唯一非派生 GT 事实源"),
        "generated_at_utc": now,
        "tool": "experiments/M2-SFX-GATE-T3/{compare_judgments.py,finalize_npd.py}",
        "isolation_discipline": {
            "task_brief_leak_check": "PASS（标注任务书不含任何既有框坐标）",
            "arbiter_independence": "仲裁判据四条不含既有 GT 坐标引用（见 tool docstring）",
            "coincidence_evidence": ("pre-k08 D00=a 框 [235,6048,326,6300] 与 R2 confirm 派生框 "
                                     "[233.4,6046.4,330.9,6301.1] 独立重合、pre-k08 D07=b 框与派生框 "
                                     "[609.4,44114,645.9,44213.6] 独立重合——双 AI 独立标注客观性旁证"
                                     "（交集统计自然体现，未参与判定）"),
        },
        "verdict_dist_divergence": dict(sorted(dist.items())),
        "consensus_boxes": cons["n_consensus"],
        "arbitrated_kept": (dist["arbiter-keep"] + dist["arbiter-keep-merged"]
                            + dist["arbiter-correct"]),
        "arbitrated_removed": dist["arbiter-delete"] + dist["arbiter-delete-duplicate"],
        "total_boxes": sum(len(d["boxes"]) for d in pages.values()),
        "pages": dict(sorted(pages.items())),
        "derived_gt_crosscheck": {"per_page": stats, "summary": summary,
                                  "derived_source": "manifest.r3.json pre-k01/02/08/09（chiqui7-scan 采集口径，R2 confirm 判定链）"},
    }
    GT_OUT.write_text(json.dumps(gt_doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[npd-gt] pages={sorted(pages)} boxes/page="
          f"{ {k: len(v['boxes']) for k, v in sorted(pages.items())} } "
          f"total={gt_doc['total_boxes']}")
    print(f"[npd-gt] verdict_dist={dict(sorted(dist.items()))}")
    print(f"[crosscheck] {json.dumps(summary, ensure_ascii=False)}")
    return 0


def _match(a_list, b_list):
    """面积降序贪心（确定性）。返回 (pairs, only_a, only_b)。"""
    pairs, used_a, used_b = [], set(), set()
    cand = [(iou(a, b), (a[2]-a[0])*(a[3]-a[1]), i, j)
            for i, a in enumerate(a_list) for j, b in enumerate(b_list)]
    cand.sort(key=lambda t: (-t[0], -t[1]))
    for v, _ar, i, j in cand:
        if v < IOU_MATCH or i in used_a or j in used_b:
            continue
        used_a.add(i)
        used_b.add(j)
        pairs.append((v, a_list[i], b_list[j]))
    return (pairs, [(iou(a_list[i], [0, 0, 0, 0]), a_list[i]) for i in range(len(a_list)) if i not in used_a],
            [(0.0, b_list[j]) for j in range(len(b_list)) if j not in used_b])


if __name__ == "__main__":
    raise SystemExit(main())
