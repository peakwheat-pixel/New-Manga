# ZCode 全权窗口报告（2026-09-19）

**窗口**：T0 = `51a71f3`（授权提交，2026-09-19 01:10:09 +08:00）→ **T1 = 2026-09-19 09:00**（实际收口时刻见 STATUS 台账行）。
**收口方**：Codex（窗口期暂停生产写入；本报告为纯文档收口的一部分）。

> **勘误（收口时发现，入档）**：本次窗口的授权提交是 **`51a71f3`**。用户收口指令与部分窗口内台账行把授权提交写作 `97a69a9`——**`97a69a9` 是 2026-09-17 窗口（T1=09-18 08:50）的授权提交**，与本窗口无关（`51a71f3` 不是 `97a69a9` 的祖先）。窗口内"依据 `97a69a9`「可自建 Task」"的表述应读作"依据 `51a71f3`（本窗口授权第 4 条）"。

## 1. 规模与结果

| 项 | 值 |
|---|---|
| 窗口内提交 | **79**（`git log --oneline 51a71f3..0bb1e6c`） |
| 已集成切片 | **11**：W0 TASK-046、W1 TASK-048、W2 TASK-049、W3 TASK-050、W4 TASK-051、W5 TASK-052、W6 TASK-053、W7 TASK-054、W8 TASK-055、W9 TASK-056、W11 TASK-058（自建） |
| 交付未集成 | **1**：W10 TASK-057（并行 ZCode 会话；分支 `agent/zcode/TASK-057-backup-restore` 冻结于 `50c4b1a`，Handoff `TASK-057-delivery.md` 已在该 worktree） |
| 收口时 master | `0bb1e6c`（若 TASK-057 在其后集成，以实际头为准） |
| 收口验证 | `pytest tests -q -rs`（PowerShell + `TASK-012-py312`、`PYTHONDONTWRITEBYTECODE=1`、`-p no:cacheprovider`、**未设 `QT_QPA_PLATFORM`**）→ **905 passed / 6 skipped / exit 0**（共 **911 collected**；6 条＝既有 `tests/network` `openssl unavailable`：`test_connection_tester.py:106`、`test_transport_tls.py:39/47/62/69/83`）。与用户口径 `911 passed / 0 skipped` **总数一致**（该口径下 openssl 可用），证据 [closure-full-suite.txt](closure-full-suite.txt) |
| 回滚 | **无**：窗口内 11 个 merge 全部保留（本报告不授权任何回滚） |

## 2. 逐切片 disposition

| W | Task | 目标 | base | reviewed_head | integration | Review 定性 | findings | Handoff | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| W0 | TASK-046 | 解码面 overlap=0、rewind 折叠收口 | `fc8f1d9` | `7bf476b` | `2b40085` | **Qoder 非作者 Review `approved`**（用户把 Reviewer 由 DSH 改派 Qoder） | handoff 追记 R-003 | `doc/handoffs/TASK-046-a40e228.md` | `verification/TASK-046/**` |
| W1 | TASK-048 | 跨线程 SQLite（§11 P-1）+ 生产路径端到端测试资产 | `8bf8da3` | `14995b6` | `be558ca` | 独立子对话 `approved_subagent` | — | `doc/handoffs/TASK-048-011ee16.md` | `verification/TASK-048/**` |
| W2 | TASK-049 | 生产区域输入面（§11 P-2） | `8bf8da3` | `ac8f052` | `e94d5af` | 独立子对话 `approved_subagent` | — | `doc/handoffs/TASK-049-a57617f.md` | `verification/TASK-049/**` |
| W3 | TASK-050 | 设置/provider 绑定注入（§11 P-3 非 UI） | `8bf8da3` | `505f52e` | `21b7301` | 独立子对话 `approved_subagent` | — | `doc/handoffs/TASK-050-5027998.md` | `verification/TASK-050/**` |
| W4 | TASK-051 | 工作台三档视图（§11 P-6） | `8bf8da3` | `7299b81` | `65d1e13` | 独立子对话 `approved_subagent` | — | `doc/handoffs/TASK-051-3cc5cf5.md` | `verification/TASK-051/**` |
| W5 | TASK-052 | 命令失败可见化（§11 P-4，provisional） | `8bf8da3` | `d93fa71` | `a1c8171` | 独立子对话 `approved_subagent` | R-001 勘误（provider-binding 用例为等价形状，非真实异常路径） | `doc/handoffs/TASK-052-3afaade.md` | `verification/TASK-052/**` |
| W6 | TASK-053 | TASK-044 R-03/R-04 收口 | `8bf8da3` | `5eeebde` | `cd57ee4` | 首轮 `approved_subagent`（R-001 P2 守卫）→ 修订 → 复审 `approved_subagent` | R-001 P2 | `doc/handoffs/TASK-053-delivery.md` | `verification/TASK-053/**` |
| W7 | TASK-054 | TASK-043 R-02 跨层改名 | `8bf8da3` | `88c1562` | `771dbf7` | 独立子对话 `approved_subagent` | — | `doc/handoffs/TASK-054-56a429e.md` | `verification/TASK-054/**` |
| W8 | TASK-055 | TASK-021 子集① 日志/诊断 | `8bf8da3` | `60d1d55` | `0493ea9` | 首轮 `changes_requested`（**R-001 P1**）→ 修订 → `approved_subagent` | R-001 P1 | `doc/handoffs/TASK-055-7f13e53.md` | `verification/TASK-055/**` |
| W9 | TASK-056 | TASK-021 子集② 缓存·版本·模型清理 | `8bf8da3` | `15f977a` | `11517ac` | 首轮 `approved_subagent`（R-001 P2 守卫）→ 守卫修订 → 复审 `approved_subagent` | R-001 P2 | `doc/handoffs/TASK-056-delivery.md` | `verification/TASK-056/**` |
| W10 | **TASK-057** | TASK-021 子集③ 备份/恢复 | `8bf8da3` | 分支 `50c4b1a` | **未集成** | **未 Review**（Handoff 已交，Task 仍 `ready`） | — | `G:/CODEX/New Manga.worktrees/TASK-057-zcode/doc/handoffs/TASK-057-delivery.md` | 该 worktree 内 `verification/TASK-057/**`（6 份全仓日志） |
| W11 | TASK-058 | 应用退出排空 workbench 运行线程（§11 P-10，**自建切片**） | `726c1bb` | `9c8cd52` | `414a8e1` | 首轮 `changes_requested` → 返修 `ebfc87a` → `approved_subagent` | R-001 | `doc/handoffs/TASK-058-5df4168.md` | `verification/TASK-058/**` |

## 3. 队列偏离与插队记录（3 条，均有依据或如实登记）

1. **W0 的 Reviewer 改派**：原定 DSH，2026-09-19 经**用户指示**改派 Qoder（Qoder 非本切片作者）⇒ 其 Review 定性为 `approved`（而非窗口条款要求的 `approved_subagent`）。这是**更强**的第三方独立审查，但与窗口"DSH 与 Qoder 窗口期不参与"的表述不一致——**以用户指示为准**，如实登记供 post-hoc 复核。
2. **W11 自建 TASK-058**：依据 `51a71f3` 窗口授权第 4 条（可自建 Task）——属**豁免内的插队**，无需申请；其目标（§11 P-10 退出不排空运行中的 run）来自同一 §11 结论集。
3. **W10 由并行会话承担**：TASK-057 由**另一个 ZCode 会话**实施（同一 Owner、不同会话），窗口内未集成 ⇒ 按章程**冻结在当前 commit**，不回滚、不补集（避免双写）。

## 4. 未完成项与原因

| 项 | 状态 | 原因 |
|---|---|---|
| **TASK-057**（W10） | 交付未集成（`50c4b1a`） | 并行会话交付完成但未集成；T1 到点按章程冻结 |
| **TASK-022** | `BLOCKED（前置未达成）` | 需 TASK-021 三子集（W8/W9 已 done、**W10 未集成**）+ **TASK-047 设计门（Qoder，窗口外）** + W3 绑定写入面 |
| **TASK-025** | `BLOCKED` | 需 TASK-022 |
| **TASK-026** | `BLOCKED` | 需 TASK-022/025，且**须非作者** |
| **TASK-027** | `BLOCKED` | 需 TASK-026 + 用户发布审核 |
| **§11 P-5**（书架导入入口） | 未修 | 静态成立；运行期需**真实 GUI 会话**确证 |
| **§11 P-7 / P-8**（PDF/MOBI 无 UI 入口 / 设置页空壳） | 未修 | 与 **TASK-047**（设计门）及 TASK-022 范围重叠，需设计先冻结 |
| **§11 P-9**（导出面） | 未修 | 需**产品裁决**导出落点 |
| **§11 P-7～P-10 的独立复核** | **未执行** | Codex 窗口期侧线（只读）本轮未完成，**列入 09:00 后复审工作** |

## 5. 纪律与口径（复核要点）

- **证据口径**：窗口内全程 PowerShell + `TASK-012-py312`、`PYTHONDONTWRITEBYTECODE=1`、`-p no:cacheprovider`、**不设 `QT_QPA_PLATFORM`**（E-1 已入 STATUS flaky/环境节）；每切片留 ≥5 次全仓逐次记录 + 判别力证据。
- **Review 定性**：除 W0（Qoder `approved`，用户指示）外全部为 `approved_subagent`（同体审查），**均可被 T1 后三方 post-hoc 复审推翻**。
- **每切片均有 STATUS 台账行**（窗口内唯一状态写入方式），逐行含 base / reviewed_head / integration / Review 定性 / findings。
- **不回滚**：窗口内 11 个 merge 保留；本报告与收口提交不改任何既有 Review 正文、不改 `doc/10_CURRENT_STATE_AND_GAPS.md`。

## 6. 收口动作（Codex，纯文档）

1. STATUS 登记实际 T1 时间并把「ZCode 全权窗口授权（2026-09-19）」小节标注失效；窗口台账行已就位。
2. 移除三处临时条款：`doc/STATUS.md` 小节效力、`AGENTS.md` 临时条款、`doc/09_COLLABORATION.md` §8。
3. `doc/00_INDEX.md` 第 5 行补写**第三窗口进展段**（W0–W11）。
4. 本报告 + 三方 post-hoc 复审交接包 `doc/handoffs/POSTHOC-REVIEW-BRIEF-2026-09-19.md`。
5. 收口验证（见 §1）；未跑项如实登记（见 §4）。
