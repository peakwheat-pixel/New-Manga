---
id: M2-TA3-B2
title: "TA3-B 阶段二：20-case 正式质量 qualification run（翻译=DeepSeek remote，用户裁决 (a) 2026-10-01）"
kind: qualification
status: in_review  # owner 完成 @3c8801b7（AC1-AC6 交付，全链 Gate FAIL 如实登记：ja 10/10 OK、ko 9 case 生产域缺口 F1/F2）——待 DSH 非作者 review
delivery_head: 3c8801b7
approval: user_ruling_2026-10-01_option_a_deepseek
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-TA3-B, M2-PROD-DETECT-1, M2-SFX-PROD-1, M2-SFX-SEM-1]
base_commit: 521d0bdd
branch: agent/zcode/M2-TA3-B2
worktree: G:/CODEX/New Manga.worktrees/M2-TA3-B2-zcode
---

# M2-TA3-B2：TA3-B 阶段二——20-case 正式质量 qualification run

## 背景

[M2-TA3-B](M2-TA3-B.md) 阶段一已 `done` @merge `97450992`：六阶段阈值提案、OCR 隔离 venv 双引擎冒烟、20 case 确定性选取（`experiments/M2-TA3-B/case-selection.json`）、阶段二计划（`verification/M2-TA3-B/phase2-plan.md`）。2026-10-01 用户裁决阶段二翻译 endpoint 选 **(a) DeepSeek remote**（OpenAI-compatible：`base_url=https://api.deepseek.com/v1`、`model=deepseek-chat`；连通性已验证 HTTP 200；key 由用户以外部树文件 `task-envs/M2-TA3-B/deepseek.key` 交付——**任何入库产物/日志/provenance 不得含 key 明文**，runner 经环境变量 `TA3B_TRANSLATE_API_KEY` 注入）。

## 交付（AC）

按 [quality-thresholds.md](../verification/M2-TA3-B/quality-thresholds.md)（阶段一冻结提案）与 [phase2-plan.md](../verification/M2-TA3-B/phase2-plan.md)（13 步清单）执行，交付：

1. **AC1 全链 run**：20 case（ja 10 + ko 10）全链 detect→OCR→translate→inpaint→render→export，detect=manga ogkalu 生产 provider（含 SFX chiqui7 并行）、OCR=ja manga-ocr / ko PaddleKoreanOcrProvider+双侧 wrapper（R6 探针已验证，box 物化 Python list）、translate=DeepSeek（SfxPolicy 默认 SKIP 口径）、inpaint/render/export 生产链；逐 case 结果登记，region 策略默认取消 `max_regions=40` 截断（`--max-regions` 逃生阀使用时必须置 `truncated: true`）。
2. **AC2 自动评测**：G1 CER（ja：J46/J47 SVG 文本层；ko：K11/K19 present-but-unaligned 需人工对齐登记——按 r2 N1 在阈值文档补披露后按登记口径执行）、SFX translation non-fail 统计（n<15 只登记分布）、region_count=0 豁免、失败分类 typed。
3. **AC3 渲染确定性**：固定 3 case（BJ02/K01/K11）复跑 export 哈希一致。
4. **AC4 对白可读性预填工作表**：5 分制三维（忠实/流畅/风格）AI 预填 n≥30 region（含 BJ06/BJ10 SFX 示例），产出 CSV/JSON 工作表待用户审核——**用户审核步骤不属于本 Task 关闭条件**（C1 先例：AI 预判+用户审核），登记为后续步骤。
5. **AC5 文档精修落地**：DSH r2 N1（ko G1 present-but-unaligned 贯通到 thresholds 的 G1 行/G3/Gate 4 注）、N4（`core_assembly.py:763-772` 行号错引→`484-498`、裸 UPDATE→`save_settings_section` 或补 `with conn:`、`credential_ref` 裸名→`make_credential_ref`、`SAKURA_DEFAULT_BASE_URL` 归属句更正）、N6（取消截断后估时回看、选项表凭证口径与 §3(a) 一致）、N2/N5（handoff/Task 旧口径同步、engine_factory 注入点名 re-register 机制）。
6. **AC6 第 0 步探针**：r2 闭合清单第 7 条——同一 core 上 profile 写入（settings upsert+commit）→ `save_provider_binding` → re-assemble → readiness READY → 1 真实 region DeepSeek 翻译探针（`TA3B_TRANSLATE_API_KEY` env resolver 注册路径），失败即停。

## 允许修改面

`experiments/M2-TA3-B/**`、`verification/M2-TA3-B/**`、`doc/tasks/M2-TA3-B2.md`、`doc/handoffs/M2-TA3-B2-*.md`、`doc/tasks/M2-TA3-B.md`（仅阶段二指针/状态行回填）。

## 禁改面

`src/**`、`tests/**`、`requirements.txt`、`packaging/**`、`apps/**`、`doc/contracts/**`、`experiments/M2-TA3-A/**`（只读复用）、`doc/STATUS.md`（Owner 不得写结论叙述，仅集成方收敛）、mock/生产 provider 语义。

## 纪律

- key 零明文入库（含 git diff、日志、provenance、handoff）；key 文件只存外部树 task-envs。
- 翻译质量 directional 口径：DeepSeek 首次接入，全部数字为 directional，不外推生产结论。
- 成本控制：单 region 单请求、无重试风暴（fail-closed typed，重试只走生产 retry 语义）；预估 ≤ 数万 token 量级，超预期即停并登记。
- Not 验收的：ja G1 CER 阈值判定若 FAIL，如实登记数字与方向，修复属后续 Task（本 Task 是 qualification 不是 gate 强制）。
- worktree 独立分支；Owner 完成后 handoff → DSH 非作者 review → 编排会话集成。

## 阶段二交付证据（owner 回填 2026-10-01，delivery_head=`3c8801b7`）

| AC | 结果 | 证据 |
|---|---|---|
| AC1 全链 run | 执行完成；**全链 Gate FAIL 如实登记**：ja 10/10 全链 completed+export OK（56 region、48 翻译=56−8 SFX、无截断；r1 R6 数字勘误：原写 53 无法由任何口径复原）；ko 9/10 fail-closed 于两条生产域缺口（F1 ogkalu 对 webtoon 长条漫 0 候选、F2 Qt 256MB 解码上限拒 K07/K09/K10 导入）；K11 修复后 export OK 但 run2 携带 2 个 typed data 失败；pipeline_failures=10（构成附表见 quality-report §1.1a） | [quality-report.md](../verification/M2-TA3-B/quality-report.md) §1 + `phase2/summaries/`（20 summary+report） |
| AC2 自动评测 | ko G1 自动子集 n=6 median **0.0556**（提案 ≤0.20 → PASS，directional，对齐抽验 4/4）；ja G1 **NOT_AUTOMATED**（SVG credits 与 detect region 文本族不重合）；SFX n=0<15 只登记分布；G2 待审 50 行 | quality-report §2 + `phase2/ocr/cer-*` + `svg-gt-*` |
| AC3 渲染确定性 | BJ02 PASS（逐位一致）；K11 FAIL——根因=remote endpoint 译文非逐位确定（OCR 0/13 差异、译文 7/13 浮动，渲染器忠实）；K01 无产物 NOT_ACHIEVABLE；独立复算 11/11 哈希一致 | quality-report §5 + `phase2/summaries/rerun-compare.json` + `phase2/export/export-hash-recompute.json` |
| AC4 对白可读性预填 | 工作表 n=26（ja15+ko11，ko 池受 F1 级联限制，缺口如实登记）；**对 AC4 字面要求的双缺口（r1 R12 并列挂账）：n=26<30 + BJ06/BJ10 SFX 示例=0（生产 SfxPolicy 默认 SKIP，SFX→translate 通路未满足前置）**；DeepSeek 自评 ai_draft + owner 6-crop 抽检校准；用户终审=后续步骤（非本 Task 关闭条件） | `phase2/translate/dialogue-readability-worksheet.*` |
| AC5 文档精修 | r2 N1/N2/N4/N5/N6 落地 | commit `b7806dac` |
| AC6 第 0 步探针 | PASS：profile 写入（save_settings_section+make_credential_ref）→binding→同 db re-assemble（vault 通路如实落地 MISSING_CREDENTIAL）→env resolver re-register+invalidate→readiness ready→1 真实 region 翻译 0.45s；零 key 泄漏 | `phase2/translate-probe.json` + `experiments/M2-TA3-B/translate_probe.py` |

后续步骤（非本 Task 关闭条件）：用户审核三份工作表（对白 n=26 / OCR 抽检骨架 n=28 / inpaint n=8）+ G2 GT 50 行；F1/F2 修复 Task 建议 A/B 与 F4/F5 口径修订交 Codex 裁决（quality-report §8/§9）。
