---
id: M2-SFX-DETECT-DOMAIN-EXT-DIAG
title: "SFX 检测域扩展第一步：BJ 域缺口诊断与扩展方案评估（误路由损害形态=优先级输入；只评估不实施）"
kind: diagnosis
status: ready
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
