---
id: M2-SFX-DETECT-DOMAIN-EXT-DIAG
title: "SFX 检测域扩展第一步：BJ 域缺口诊断与扩展方案评估（误路由损害形态=优先级输入；只评估不实施）"
kind: diagnosis
status: in_progress
owner_claim: 2026-10-03T23:12+08:00 by zcode subagent @497621df
delivery_head: 87a8bc34
reviewed_head: 待 Review 后回填（Reviewer=DeepSeek Harness 非作者）
completion_note: 2026-10-03 AC1-AC4 全部交付（只评估不实施）；三假设 DETERMINED：(a) 域外=成立主根因 (b) 类映射分层（text 捡走成立/阈值救否定） (c) 预处理=不成立；实验 L1/L2/L3 跑成（BJ06 对照+BJ13/14/15，sfx 通道 0.0000-0.0109 vs 域内 0.72-0.94）；结构性发现=region 创建无跨 provider 重叠仲裁，召回修复不闭合误路由损害；status 保持 in_progress 待 Review+集成流转
approval: orchestrator_next_release_2026-10-02_priority_input_registered
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-SFX-E2E-MATERIAL, M2-SFX-DETECT-EVAL]
base_commit: 24a89d7d
branch: agent/zcode/M2-SFX-DETECT-DOMAIN-EXT-DIAG
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-DETECT-DOMAIN-EXT-DIAG-zcode
---

# M2-SFX-DETECT-DOMAIN-EXT-DIAG：BJ 域 SFX 检测缺口诊断与扩展方案评估

## 背景（M2-SFX-E2E-MATERIAL 检测段瓶颈+误路由损害形态=DETECT-EVAL §4.4 优先级输入）

SFX-E2E 实证：①chiqui7 sfx 类对 BJ 大型毛笔竖排 SFX **0 命中**（BJ13/14/15 七目检实例）；②**误路由损害形态**——SFX 被检出为 speech/text 类→对话链乱译→错误译文排版进渲染成品页（与 SfxPolicy 无关，BJ13 region#1/#3 实证「哎呀——」/「Ｗｉｆｉｘ」）；③同位置存在 text 类框（conf 0.744/0.844，IoU 0.452/0.544）与整页 panel 大框——归属未定。翻译链已全部就绪（SFX-SEM/ENTRY/PRIMARY 闭环），瓶颈纯在检测段。

## 交付（AC）

1. **AC1 证据汇总与根因分层**：汇总 SFX-E2E 诊断 JSON（相交框枚举）+KO-RERUN/SFX-PROD 既有评估——BJ 域缺口的根因假设分层：(a) chiqui7 训练域不含 BJ 毛笔竖排形态（域外）；(b) 类别映射歧义（sfx 被判 text/panel）；(c) 预处理（分辨率/letterbox）对大型竖排字不利。每假设给可判定证据或标记不可判定。
2. **AC2 扩展方案评估（只评估不实施）**：沿 DETECT-EVAL §4.4 裁决清单+新证据对比——①后分类器（对 text/panel 检出框跑 SFX 二分类小模型，成本/精度估计）；②类敏感阈值（sfx/text 类差异化 conf，评估误路由风险变化）；③chiqui7 fine-tune（BJ 域标注成本——沿 C4 条件式先例评估）；④路由（BJ 家族 detect 走 docTR+后处理，粒度语义成本）；⑤维持现状+产品侧缓解（误路由损害的产品处置：sfx 疑似框的 speech 译文标记）。各方案列：改动面/成本/预期收益/风险/与 SfxPolicy 语义的交互。
3. **AC3 裁决建议**：方案排序+推荐（含「不实施」选项），移交用户/编排裁决；实施另行释放。
4. **AC4 零 src 改动**：诊断/评估全在 experiments（复用 diagnose_sfx_detect.py 先例与 golden suite 素材——BJ13/14/15 已入池）。

## 允许修改面

`experiments/M2-SFX-DETECT-DOMAIN-EXT-DIAG/**`、`verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/**`、Task/Handoff。

## 禁改面

`src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、既有 Task 产物（SFX-E2E/KO-RERUN/TILING 只读）、`doc/STATUS.md`。

## 纪律

- directional；方案成本估计为静态分析+既有证据推导（可跑小实验佐证——零 src）。
- 与 M2-TA3-B3-KO-FULLRUN 并行零文件交集（FULLRUN 是 ko 评测面）。

## 交付记录（2026-10-03，Owner=ZCode subagent）

AC1-AC4 全部交付，delivery_head=`87a8bc34`，主报告 `verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/diagnosis-and-options.md`，Handoff `doc/handoffs/M2-SFX-DETECT-DOMAIN-EXT-DIAG-87a8bc34.md`。要点：

- **AC1 三假设全部 DETERMINED**：(a) 域外=**成立（主根因）**——L3 参照框 crop（等效 2.4-3.4× 分辨率）7/7 sfx 分数仅 0.0000-0.0109，域内对照 BJ06 同管线 0.721-0.9355（跨 2-3 个数量级）；(b) 类别映射歧义=**分层**——「SFX 像素被 text 类高 conf 捡走」成立（BJ13 text 0.744/0.844，L3 crop 中 text 0.735/0.9046/0.8707；E2E r1 R2 的「归属未定」收敛为 text，panel 大框全页平凡覆盖 IoU 0.013-0.126 非独立根因），「sfx 信号被 argmax 竞争压制、可差异化阈值救」**否定**（同框 sfx 分数比 text 低 1-2 个数量级，raw pre-NMS 峰值仅 0.0855）；(c) 预处理=**不成立**——L2 tile（1.67×）与 L3 crop 均不恢复 sfx 信号，盲区目标在 letterbox 空间（61-86×135-206px）反而大于域内正例（21-84×25-131px），且等比 letterbox 无 WEBTOON-DIAG 各向异性机理。
- **AC2 五方案**：①后分类器（只救 BJ13/14，BJ15 参照框处无紧贴 text/bubble 载体=结构性救不了）；②类敏感阈值（九档扫描直接否决）；③fine-tune（唯一对症自动化路径，前置=AGPL 衍生权重许可裁决+BJ 域 GT 标注+回归基线，沿 C4 §7.1 条件式形态）；④路由（不推荐独立立项：docTR 无 SFX 类面且 C4 反登记其为 SFX 误检源）；⑤维持现状+产品侧缓解（短期首选，唯一直接处置误路由损害的方案）。
- **AC3 排序**：⑤＞③（条件式）＞①（条件性次优）＞④＞②（否决）；「不实施」合法；移交用户三个裁决问题（是否接受不实施+UI 缓解 / AGPL 衍生许可 / 重叠仲裁契约授权）。
- **结构性新发现**：`src/bootstrap/core_assembly.py` `_create_detected_region` 按候选独立建 region、无跨 provider 重叠仲裁——召回修复（①②③）后 ogkalu speech region 仍并存走对话链，误路由乱译损害不消失；重叠仲裁属共享契约面，须 Codex 范围裁决（DETECT-EVAL §4.4 条件 5 具体化）。
- **AC4 实验**：`experiments/M2-SFX-DETECT-DOMAIN-EXT-DIAG/conf_scan_diag.py`（零 src，只读 import 生产 `_build_engine/_letterbox/_map_back/_nms`）；三层探针 L1 conf 九档扫描（BJ06 对照+BJ13/14/15，全类+4 类分数向量）/L2 60% tile/L3 参照框 crop + raw pre-NMS 干净探针；raw 落 `verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/raw/`；环境 onnxruntime 1.30.0 CPU，权重 pin 校验通过（sha256 `d87389af…`）。禁改面零触碰，逐文件 add，无 `git add -A`。
