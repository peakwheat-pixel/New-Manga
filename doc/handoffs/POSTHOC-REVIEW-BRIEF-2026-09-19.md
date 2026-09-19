# 交接包：ZCode 全权窗口（2026-09-19）的三方 post-hoc 复审

**委托方**：Codex（窗口收口方）。**Reviewer**：**DeepSeek Harness + Qoder + Codex**（三方可独立复审；Codex 为收口方与集成责任人，其复审结论不得作为唯一依据）。
**窗口**：T0 = `51a71f3`（授权提交，2026-09-19 01:10:09）→ T1 = 2026-09-19 09:00。
**复审对象**：`51a71f3..<收口时 master>`（收口时为 `0bb1e6c`；**逐切片以各 Task 的 `integration_commit` 为准**）。

> **为何必须复审**：窗口内 11 个集成的 Review 定性**除 W0 外全部是 `approved_subagent`（同体审查）**——按 [协作协议](../09_COLLABORATION.md) §1，它**不是**独立批准；窗口条款明确"T1 后由三方 post-hoc 复审，**可推翻**"。前两个窗口的先例：[POSTHOC-WINDOW-2026-09-17](../reviews/POSTHOC-WINDOW-2026-09-17.md)（Codex）、[POSTHOC-WINDOW-DSH-2026-09-18](../reviews/POSTHOC-WINDOW-DSH-2026-09-18.md)（DSH）——**两份都在复审中修正过结论**。

## 1. 被审切片（逐切片固定对象）

| W | Task | base | reviewed_head | integration | Review 定性 | 证据入口 |
|---|---|---|---|---|---|---|
| W0 | TASK-046 | `fc8f1d9` | `7bf476b` | `2b40085` | Qoder `approved`（用户改派，非 `approved_subagent`） | `doc/handoffs/TASK-046-a40e228.md`、`verification/TASK-046/**` |
| W1 | TASK-048 | `8bf8da3` | `14995b6` | `be558ca` | `approved_subagent` | `doc/handoffs/TASK-048-011ee16.md`、`verification/TASK-048/**` |
| W2 | TASK-049 | `8bf8da3` | `ac8f052` | `e94d5af` | `approved_subagent` | `doc/handoffs/TASK-049-a57617f.md`、`verification/TASK-049/**` |
| W3 | TASK-050 | `8bf8da3` | `505f52e` | `21b7301` | `approved_subagent` | `doc/handoffs/TASK-050-5027998.md`、`verification/TASK-050/**` |
| W4 | TASK-051 | `8bf8da3` | `7299b81` | `65d1e13` | `approved_subagent` | `doc/handoffs/TASK-051-3cc5cf5.md`、`verification/TASK-051/**` |
| W5 | TASK-052 | `8bf8da3` | `d93fa71` | `a1c8171` | `approved_subagent`（provisional，待 TASK-047 设计收敛） | `doc/handoffs/TASK-052-3afaade.md`、`verification/TASK-052/**` |
| W6 | TASK-053 | `8bf8da3` | `5eeebde` | `cd57ee4` | 首轮 R-001 P2 守卫 → 复审 `approved_subagent` | `doc/handoffs/TASK-053-delivery.md`、`verification/TASK-053/**` |
| W7 | TASK-054 | `8bf8da3` | `88c1562` | `771dbf7` | `approved_subagent` | `doc/handoffs/TASK-054-56a429e.md`、`verification/TASK-054/**` |
| W8 | TASK-055 | `8bf8da3` | `60d1d55` | `0493ea9` | 首轮 **R-001 P1** → 修订 → `approved_subagent` | `doc/handoffs/TASK-055-7f13e53.md`、`verification/TASK-055/**` |
| W9 | TASK-056 | `8bf8da3` | `15f977a` | `11517ac` | 首轮 R-001 P2 → 守卫修订 → 复审 `approved_subagent` | `doc/handoffs/TASK-056-delivery.md`、`verification/TASK-056/**` |
| W11 | TASK-058 | `726c1bb` | `9c8cd52` | `414a8e1` | 首轮 `changes_requested` → 返修 `ebfc87a` → `approved_subagent` | `doc/handoffs/TASK-058-5df4168.md`、`verification/TASK-058/**` |
| W10 | **TASK-057** | `8bf8da3` | 分支 `50c4b1a` | **未集成** | **未 Review** | `…worktrees/TASK-057-zcode/doc/handoffs/TASK-057-delivery.md` |

窗口报告（含队列偏离、未完成项与原因）：[verification/ZCODE-WINDOW-2026-09-19/window-report.md](../../verification/ZCODE-WINDOW-2026-09-19/window-report.md)；收口验证：[closure-full-suite.txt](../../verification/ZCODE-WINDOW-2026-09-19/closure-full-suite.txt)。

## 2. 优先复核靶点（按风险排序）

1. **W1 TASK-048（§11 P-1，P0）**：跨线程 SQLite 的修复是否**真**让生产路径跑通（不是"绕过断言"）：独立复跑"真实 `assemble_services` + 真实 SQLite + 真实 `RunController`(QThread) + 完整命令"；核对并发控制方案（不是仅 `check_same_thread=False`）；核对 `recover_running_runs()` 接入启动路径的时序影响。
2. **W2/W3（P-2/P-3）**：页级 `ocr` 是否不再因"无 Region"失败；`detect` handler 在**无检测器**时是否 typed fail-closed（不得静默）；provider 绑定注入是否**复用**既有 settings 形状（`_load_pipeline_settings`）且默认路径与修前一致。
3. **W6 TASK-053**：删除/级联是否**枚举过 `sqlite_master` 的 TRIGGER**（TASK-044 的教训）；孤儿文件清单是否真的可重试；无 target run 的保留/清理策略是否有据。
4. **W9/W10（清理面）**："永不清理"边界（用户源文件、current/pinned revision、Lock 保护对象）是否真的不可达；瓦片缓存跨代回收是否只碰 `tile-*.png`。
5. **W5 TASK-052（provisional）**：QML 是否只加了工作台页面内的最小元素；错误文本是否脱敏且含可执行诊断；与 TASK-047 设计产出的冲突面。
6. **W0 TASK-046 的 Review 定性偏差**：`approved`（Qoder，用户改派）与窗口条款的 `approved_subagent` 口径差异是否需要更正入档。
7. **各切片的"判别力"证据**：逐条核对"新用例对修前失败/对照矩阵"，**不得以 `N passed` 代替**；核对全仓运行是否遵守口径（同 shell/venv、不设 `QT_QPA_PLATFORM`）。
8. **W10 TASK-057 的冻结状态**：`50c4b1a` 是否可安全集成（Review 尚未发生）；其 Handoff 声称的 AC 是否有证据。

## 3. 边界与交付

- **只读**：不得修改 `src/**`、`tests/**`；不得改各 Task 既入档 Review 正文与 `doc/10_CURRENT_STATE_AND_GAPS.md`；不得回滚窗口内任何 merge。
- 交付到 `doc/reviews/POSTHOC-WINDOW-2026-09-19-<reviewer>.md`（如 `POSTHOC-WINDOW-2026-09-19-DSH.md`、`-Qoder.md`、`-Codex.md`）+ 证据 `verification/POSTHOC-WINDOW-2026-09-19/<reviewer>/**`。
- 结论口径：**`uphold`（维持 done）/ `uphold_with_findings`（维持 + 另开切片）/ `overturn`（推翻，须带可复现反例与 P0/P1 依据）**；推翻项由 Codex 处置（重开 Task 或回滚相关集成的**后续修正**，但**不删除已入档历史**）。
- 验证口径：同一 shell + 同一 venv、`PYTHONDONTWRITEBYTECODE=1`、`-p no:cacheprovider`、**不设 `QT_QPA_PLATFORM`**；退出码 + passed/skipped 分列 + skip 原因；**总数必须对得上**（收口时：本机 905 passed / 6 skipped = 911 collected；openssl 可用口径为 911 passed / 0 skipped）。
- 报告中必须分列"**独立复跑**"与"**复用窗口内证据**"。
