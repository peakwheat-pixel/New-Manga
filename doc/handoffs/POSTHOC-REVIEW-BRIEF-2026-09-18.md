---
kind: posthoc-review-brief
recipient: Codex（Lead）+ DeepSeek Harness（独立外部复审者；ZCode 回避）
from: ZCode（两轮窗口的作者/集成者，本包仅为交接材料）
issued: 2026-09-18 08:45（T1=08:50 前，最后一笔入库）
base: 417a23a
scope: 2026-09-17 23:12:28 两轮窗口内全部 approved_subagent 集成交付
---

# Post-hoc 复审任务包（两轮窗口集成清单，供 Codex/DSH 直接执行）

窗口条款：[STATUS](../STATUS.md)「ZCode 全权窗口授权（2026-09-17）【生效中】」＋第二轮指令包 [ZCODE-WINDOW-2026-09-17-round2.md](ZCODE-WINDOW-2026-09-17-round2.md)。**复审可推翻窗口内任何 `done`**；作者（ZCode）对本复审回避。

## 待复审集成清单（7 项，全部 approved_subagent）

| # | integration | Task | reviewed_head | 窗口内 Review | 复审建议重点 |
|---|---|---|---|---|---|
| 1 | `372c3bf` | TASK-037 flaky 修复 | `7b96e72` | `7c35277` approved_subagent | ①`:224` 式等价更新是否成立（TASK-038 又改过同文件，注意两轮叠加后的最终态）；②修复只加强未放宽（对照 `7b96e72` diff） |
| 2 | `4d0f932` | TASK-033 完整链收口 | `933819f` | `401d6d7` approved_subagent | 单一写者 P0（`revision_updates={}` ＋ RenderService CAS）；AC-RFULL-001=BLOCKED 未 PASS；R-001 P2 的"白名单外未修"处置 |
| 3 | `b738200` | TASK-020 Webtoon 分块 | `b337f71`（首轮 `7833604` changes_requested→修订） | `a9b4141` + 复审 `79ec0d2` approved_subagent | R-001 P1 修订闭环；oversize BLOCKED（Qt PNG ≳300MB 限制）未记 PASS；夹具高页化是"前提修复"非放宽 |
| 4 | `ba7d560` | TASK-023 PDF 导入 | `7fa9118` | `c87f21c` approved_subagent | pypdfium2 依赖留证（前后全仓对照）；MOBI BLOCKED 未伪造 |
| 5 | `f835ac9` | TASK-038 生产装配 | `317f33e` | `fcf791f` approved_subagent | export 双路径注册名对应关系；`:224` 二次更新（TASK-038 再次前提变化）；装配契约测试覆盖 |
| 6 | `c8024fe` | TASK-039 planner 修复 | `38fbde4` | `18c9834` approved_subagent | probe=None 与修前逐字节等价；AC③ 泛化口径（复审 R-004 accepted 的裁定是否成立）；生产注入点白名单外未实现 |
| 7 | `5bc17f8` + `b940497` | TASK-021 trash 子集 | `887e0d6` + 修订 `0fe634f` | `a9b4141` + 复审 `79ec0d2` approved_subagent（R-001 fixed 复现+终态 7/7） | R-001 修订闭环；同毫秒合并缺陷加固；manifest 崩溃窗口声明的如实性 |

## 每项复审的统一输入

- 集成 merge 的两个 parent 即「当时 master ＋ 分支 head」；Review 报告在 `doc/reviews/TASK-0xx-<head>.md`（含窗口内子 agent 的 findings 与 disposition——外部复审可对照其是否漏判）。
- 全部全仓证据在各 `verification/TASK-0xx/full-suite-runs.log`。
- **口径注意**：第一轮 W5-W7/插队数字为 `powershell.exe`（Git Bash 会话启动，PATH 继承含 openssl）＋TASK-012-py312 → N passed/0 skipped；第二轮同口径。纯系统 PATH PowerShell 口径为 N-6 passed/6 skipped（6 条 `tests/network` TLS skip↔pass）。两口径收集总数一致，**不要把口径差读成"skip 被消除"**（round2 指令包已明确该教训）。

## 复审后裁决清单（三项，STATUS 已登记等待）

1. **TASK-039 `clean_probe` 的生产注入切片**：修复逻辑已集成（`PipelineService.clean_probe` 可选参数），但 bootstrap 注入在 TASK-039 白名单外未实现——未注入前生产 render-only 命令保持既有 BLOCKED 行为（不比修前差）。需 Codex 立 scope 明确的小切片（`src/bootstrap/app.py` 一行注入 + 装配断言）。
2. **TASK-021 R-001（P2）**：已在本窗口修订收口（`0fe634f`，复审 `79ec0d2` approved_subagent、复现+终态 7/7 PASS）——外部复审核对该复审即可；若推翻需重开 TASK-021。
3. **排期裁决**：TASK-021 三个 frozen 子集（备份/恢复、缓存/版本/模型清理、日志/诊断包）＋两项用户待决（MOBI 解析依赖、超大 webtoon 像素解码的流式解码依赖）。

## 作者声明的诚实边界（供外部复审对照核验）

- 全部窗口 Review 均为 approved_subagent（同体审查）；本包作者（ZCode）对上述 7 项皆为作者兼集成者。
- 三处 BLOCKED 未记 PASS：TASK-020 超大 webtoon 像素解码、TASK-023 MOBI 光栅化、TASK-033 AC-RFULL-001（真实能力仍缺）。
- 一处修前树异常未定性：TASK-037 修前对照中 1 次全仓 96% 处进程异常终止（无 summary、EXIT=127，复跑未再现）——已如实登记，非测试失败。
- 两轮新增测试以各自 Handoff 数字为准（全仓口径演进 770→772→780→786→787，每步差值＝对应切片新增数）；无依赖清单变更（pypdfium2 为 TASK-023 用户批准项并留证）。
