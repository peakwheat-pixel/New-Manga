decision=changes_requested

## 0. 复核方法与限制（先说清证据面）

- 本会话 shell 全程不可用：`pwsh` 每次都在沙箱授权阶段失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\DIAG-FIX-B-zcode)`），提权重试被拒（`no approval channel is available`）。因此**无法执行 `git diff 528ba4d4..2a1078b6` / `git diff a8b94df1..2a1078b6`**。
- 替代证据链（可复现）：(1) 读取明文 reflog `G:\CODEX\New Manga\.git\worktrees\DIAG-FIX-B-zcode\logs\HEAD` 重建 commit 链；(2) 对当前工作区（=2a1078b6）逐文件内容级核对，并逐条验证 Handoff 的自述；(3) 用证据日志自身的 UTC 时间戳与 commit 时间对齐，判定哪些证据文件属于 R2。
- 重建的链：`a8b94df1`(base) → `6e37f05d`(claim) → `3ce82240`(实现) → `528ba4d4`(R1 Handoff) → `2a1078b6`(R2，被审 HEAD)。R2 证据（`*-r2.log`，17:44:32/17:45:05 UTC）严格落在 `528ba4d4`(≈17:38) 与 `2a1078b6`(≈17:46:19) 之间 → 确为 R2 新增。
- 未能验证的部分：R2 commit 的**逐 hunk 与完整文件清单**（无 git）。以下 R2 变更面是我用"内容 + commit message + 时间戳"推出的，若有不可见改动（不改变文件内容的权限位等）我无法发现。

## 1. R2 变更核对（内容级）

| R2 声称变更 | 实测 | 判定 |
|---|---|---|
| `src/ui/viewmodels/reader/viewmodel.py` 仅 docstring/注释 | `:51` 信号、`:75-80` 构造注释、`:452-459` `settleReadingTime` docstring 均改为 `heartbeat_error` 属性 + `heartbeatErrorChanged` 信号并注明无 QML 消费者；`import sqlite3`/`try/except sqlite3.Error` 逻辑与 R1 语义一致 | 一致 |
| `tests/reading_export/test_viewmodels.py:162` 补 try/finally | `:165-174` `try: … finally: if vm.hasChapter: vm.closeReader()`，且注释标注 FIX-B/AC3 | 一致 |
| Handoff 修订（AC1 披露、AC3 理由、§4.2/§4.3、§7 处置表） | 均存在（`:53-58`、`:76-77`、`:84-89`、`:107-120`） | 一致 |
| R2 重跑证据 | `targeted-suite-r2.log:16` `163 passed`、`:63 EXIT=0`；`full-suite-r2.log:390` `1317 passed, 5 skipped, 1 warning`、`:392 EXIT=0`；`:385-389` 五条 skip 原因 = 2 docTR + 1 numpy + 2 torch（与 §2 AC5 文字吻合）；`:379-381` 唯一 warning = `imghdr` DeprecationWarning（与 §4.7 吻合）；两个全量日志均无 `Cannot operate on a closed database`（该串只出现在探针日志的 typed error 字段） | 一致 |

## 2. 上轮 6 条 findings 逐条结论

| ID | 结论 | 一句依据 |
|---|---|---|
| R-01 | **通过** | Handoff:55、:76-77 明确"生产终结点接线为零 + bootstrap/QML 属禁止范围 + 已停止实现 + 需 Codex/用户裁决是否另立接线 Task"，满足 Task §已知阻塞"停止并交 Codex 作范围决定"；我全仓核验属实：`closeReader` 仅被 3 个测试文件调用，`src/bootstrap/app.py:248` 只连 `readerContextChanged→openChapter`，全仓 `.qml` 无 `closeReader`/`aboutToQuit` 接线。附条件：AC1 不得据此判 PASS，须由 Codex 出范围裁决。 |
| R-02 | **通过** | `test_viewmodels.py:165-174` 已补 try/finally；`test_webtoon_tiles.py` 三处（`:272`/`:624`/`:752`）不收口的理由成立——三处均为 `JsonProgressDocumentStore`（`src/application/reading/ports.py:73-102`，无 `close()`、无 sqlite 错误面），VM 是测试函数局部对象、`QTimer` parent 为 VM（`viewmodel.py:71`），GC 即销毁，确实无泄漏可观测后果。 |
| R-03 | **通过** | `viewmodel.py:75-80`、`:452-459` 已改为 `heartbeat_error` 属性 + `heartbeatErrorChanged` 信号并注明无 QML 消费者；全仓 grep 已无 `heartbeatError` Property 引用（仅信号名与属性名）。 |
| R-04 | **通过** | 信号保留（`viewmodel.py:51`）且 Handoff:87-89 注明"供下一个触碰 reader UI 的 Task 消费、Owner 未定、Python 侧为观察者"，归属已落到文档。 |
| R-05 | **不通过** | 只改了 §变更面一行：`Handoff:18` 的"10 文件 = 代码 4 + 证据 4 + 治理 2"仍不实（R2 新增 `targeted-suite-r2.log`、`full-suite-r2.log`，`verification/DIAG-READING-EXPORT-001-FIX-B/` 现有 **6** 个证据文件，改动面 ≥12），且**同一文件 `:61` AC6 仍写"diff 仅上述 8 文件"**，与 §变更面自相矛盾；另 `:38` "（4 处）"与其自身枚举的 5 处不符，`:58` AC3 "覆盖 5 处" 实为 6 处。这正是 R-05 的同一类缺陷未收口。 |
| R-06 | **通过** | `Handoff:84-86` 已增列"stop 之后无重启路径，一次瞬时 `OperationalError`（如 database is locked）也停表、静默累积至下次 `openChapter`；如需区分可恢复错误另立 Task"，捕获范围按裁决保持 `sqlite3.Error`（`viewmodel.py:471`），未收窄。 |

## 3. R2 引入/未收口的新问题（全部 P3，均为文档事实性，代码与测试无问题）

1. **N-01（=R-05 残留）`doc/handoffs/DIAG-READING-EXPORT-001-FIX-B-3ce82240.md:61`**：`diff 仅上述 8 文件` 与本文件 `:18` 的"10 文件"冲突。
   要求：删除"8 文件"，改为与实际改动面一致的口径（见 N-02）。
2. **N-02 `…3ce82240.md:18`**：计数仍不实。证据子项实为 6（`probe-heartbeat-leak-fixed.py`、`probe-heartbeat-leak-fixed.log`、`targeted-suite.log`、`full-suite.log`、`targeted-suite-r2.log`、`full-suite-r2.log`），不是 4 → 正确写法应为"12 文件 = 代码 4 + 证据 6 + 治理 2"（若 Task 文件也在 R2 commit 内改动，请按 git 实际结果修正为 12/13，并在 §7 末尾列出 R2 的 5 个改动文件）。**不要再用手写汇总数覆盖 git 事实**。
3. **N-03 `…3ce82240.md:60`、`:69`、`:70` 与 `:120`**：§7 声称"重跑定向与全仓见 §3 更新"，但 §2 AC5 与 §3 表格链接的是 R1 日志（`targeted-suite.log` / `full-suite.log`，17:35/17:36 UTC），R2 重跑证据 `targeted-suite-r2.log` / `full-suite-r2.log` 在全文**零引用**（grep 无 `-r2`）。
   要求：把 R2 断言链接指向 `-r2.log`（或 §3 增列 R1/R2 两行并显式标注归属）。数值两轮相同，无需重跑，只改指针。
4. **N-04 `…3ce82240.md:6` 与 `:17`**：frontmatter `owner_head: 3ce82240` 与 Commit 链（停在"→ 本 Handoff"）均未记录 `528ba4d4`(R1 Handoff) 与被审 HEAD `2a1078b6`，被审固定点无法从 Handoff 自证。
   要求：补 `reviewed_head: 2a1078b6`（或等价字段），链改为 `a8b94df1 → 6e37f05d → 3ce82240 → 528ba4d4 → 2a1078b6`。
5. **N-05 `…3ce82240.md:38` 与 `:58`**（同族计数）：`:38` 写"（4 处）"但同一括号内枚举了 5 处（`reader` fixture + 3 个 qml fixture + `test_bootstrap.py:636` finally）；`:58` 写"覆盖 5 处（§1.2 的 4 处 + :162）"而实际 teardown 落点为 6 处。
   要求：统一为枚举得出的数字（6 处），或改为"按文件列点"避免汇总数。

## 4. 结论与推荐下一步

- 实体结论：**代码与测试面通过**——`viewmodel.py:469-475` 的类型化 stop-on-error、`:162` teardown 补口、三处 teardown 面、探针 7/7 与 R2 双套件证据均经内容核对一致；R-01/R-02 两条 P2 的处置（披露式升级 + 有理由的不收口）我判定可接受。**R-05 未彻底收口，并新增 N-03/N-04 两处追溯性缺口**，故本轮为 `changes_requested`，且修复仅限文档、**无需重跑测试**。
- 推荐下一步：① Owner（ZCode）按 §3 的 N-01～N-05 修订 Handoff（可并入同一 commit，提交信息注明 `R3 docs-only per DSH re-review`）后重交复核；② 交 Codex 裁决 AC1 范围缺口——是否另立"生产装配/QML 离开读者页接线 `closeReader`/`aboutToQuit`"的续作 Task，并决定本 Task 在 AC1 部分未达的情况下可否进入 `done`；③ 集成核验前需 Codex 追认 Integrator 身份与三方核验（scope/`diff --check`/合并历史），本 Task 现状 `status: in_progress`、AC 全未勾选，与"评审中"一致。
