decision=approved

# DSH 非作者复核（第二轮 / R2）：DIAG-READING-EXPORT-001-FIX-A

- 被审交付：`agent/zcode/DIAG-READING-EXPORT-001-FIX-A-terminal-wait-semantics`，worktree HEAD 经 `.git/refs/heads/agent/zcode/...` 与 `.git/worktrees/DIAG-FIX-A-zcode/logs/HEAD`（第 6/7 行）核实 = **`6fe7bd86`**（R2 实现 `db5ee918` → Handoff `6fe7bd86`），与送审声明一致。
- 会话限制（先披露）：本会话 `pwsh` 沙箱在初始化阶段即失败（`Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\DIAG-FIX-A-zcode)`，连 `echo` 都不执行；换 workdir 同样失败），独立子代理复现同一错误，且提权通道不可用。**因此无法执行 `git diff/status` 原文**；我改用等价静态核验：①`.git` refs + reflog 核实 head 与提交链；②以主仓库工作树（`.git/logs/HEAD` 第 555-556 行证明 `main = 32ef1dd6` + 单条发布文档提交 `878bf2a5`）作为 base 快照，与 R2 文件逐行比对；③用工作区 mtime 全量清单（glob 落盘 2877 条，按时间升序）做范围核验。本会话未修改任何文件。

## 一、上轮 6 条 findings 逐条处置核对

| ID | 级别 | 上轮诉求 | 处置核对 | 结论 |
|---|---|---|---|---|
| F1 | P2 | `test_export_outcome_wait_...` 的 `assert snapshots` 消费排队投递列表而谓词无终态等待；"其余 6 处无暴露面"表述失真且进入文件头注释 | `tests/reading_export/test_viewmodels.py:349`、`:377` 谓词已改为 `not vm.running and snapshots`（选择器改动共 6 处：284/299/349/377/440/456）；文件头 `:63-76` 已重写为"程序顺序 ≠ 跨线程可观察顺序 + **信号列表消费者**才需终态等待"，`:73-75` 明确把 `:456` 标为一致性改动 | 通过 |
| F2 | P3 | 阶段 B misses 对新谓词数学恒 0；verdict 未校验 completed；`main` 恒 `return 0` | `probe-terminal-wait-discrimination.py:219/228` 判定加 `completed == iterations`，`:238` 用 `detected_failures == iterations and iterations > 0`，负判定在 `:227/:237/:245` 置 `exit_code = 1`，`:248` 返回；`probe-r2.log:29` 的 B 行文本含 `(completed=200/200)`（R1 日志 `:29` 无此后缀）→ hunk 方向可证；Handoff `:55` 已把 AC1 依据改为 completed+misses 双条件 | 通过 |
| F3 | P3 | 探针 `pump_until` 为逐字副本，证据非真实测试函数执行 | Task `:46` 确有"探针只读，不编辑/monkeypatch 产品或测试文件"约束，副本为合规做法；Handoff `:60` 已披露证据强度口径（证明同款谓词模式，非测试函数本身） | 通过（accepted + 披露） |
| F4 | P3 | 定向 15 passed 无日志归档 | `verification/DIAG-READING-EXPORT-001-FIX-A/targeted-suite.log` 存在：命令/解释器/CWD 齐全，`15 passed in 0.42s`，`EXIT=0`；Handoff `:63` 引用（小瑕疵见 O4） | 通过 |
| F5 | P3 | STATUS 仍记 FIX-A proposed（不在 Owner 写集合） | `doc/STATUS.md:7`、`:45` 仍为 `proposed / NOT_RELEASED`；该文件不在 Task `:53-58` 允许修改范围，工作区 mtime 亦停留在检出期（未改），处置为 Integrator 集成时同步，合理 | 通过（集成侧待办） |
| F6 | P3 | `:442` 空页路径为主线程同步 `_fail`，改动惰性 | Handoff `:45` 表项与文件头 `:73-75` 均标注"一致性改动，非竞态点"，且与 `src/ui/viewmodels/export/viewmodel.py:262-264`（`request is None` → 主线程同步 `_fail`）事实一致 | 通过（accepted + 披露） |

## 二、R2 是否引入新问题

**`and snapshots` 语义匹配性（重点核查，未见问题）**
- `snapshots` 由 `changed` 驱动（主线程 connect → auto/queued 投递），谓词 = `not vm.running`（工作线程程序序上终态状态与信号已发布）∧ `snapshots` 非空（至少一次排队投递已被处理）。两测试其后的断言只依赖：DirectConnection 在工作线程 emit 内同步填充的 `in_call`、普通属性 `statusMessage`、以及已投递快照——不存在"谓词返回而断言所需数据未就绪"的假绿，也不会因 `changed` 永不发射而死等（该信号必然发射）。
- 合取**严格强于**旧谓词（只会等更久），未放宽断言、未加 sleep/retry/skip，符合 AC5/R-001 口径。
- 全文件 base→R2 差异经逐行比对已完全归账：文件头注释重写（+10 行）、6 处谓词、2 处谓词换行重排（+4 行），无其他内容改动（444 → 458 行逐段偏移一致，含我未抽查过的 100-254 区间）。

**探针 verdict 修改正确性（未见问题）**
- A：`misses > 0 and completed == iterations` 才判正，否则负 + exit 1；B：`misses == 0 and completed == iterations` 才判正；C：`detected_failures == iterations and iterations > 0` 才判正。破伤阶段 `completed` 恒 0（`continue` 早于计数），改用 `detected_failures` 判定等价且更严格。负判定不再以 0 退出 → F2 的实质诉求关闭。

**范围核验（mtime 全量清单）**：工作区最新 7 个文件恰为 R2 交付面——`full-suite.log`(2871)、`test_viewmodels.py`(2872)、`probe-*.py`(2873)、`test_viewmodels *.pyc`(2874)、`targeted-suite.log`(2875)、Handoff(2876)、`probe-r2.log`(2877)；**末尾无任何 `src/**`**，与"产品代码零改动"一致（另：主仓库与 worktree 的 `src/ui/viewmodels/export/viewmodel.py` 418 行逐行一致）。`doc/tasks/...FIX-A.md` 位于 2532（发布时 mtime，非 R2 触碰）；R1 证据 `probe-...log`(2551)、`full-suite.log`(2871) 未被覆盖。未发现 R2 引入 P0–P2 级新问题。

## 三、非阻塞观察（P4，建议集成后择机处理，不构成 changes_requested）

1. `probe-terminal-wait-discrimination.py:210`：阶段 B 的 "MISSES" 行结构性恒 0（谓词含 `state["arrived"]`，`ok=True` 即 arrived=True），标签易被误读；判定已改用 `completed`，结论不受影响。建议该阶段打印 `n/a (structural)`。
2. `probe-...py:238`：当 `broken iters == 0` 时落入负判定并 `exit 1`（文案为"predicate ACCEPTED"），属退化调用的误报；建议入口处 `iters <= 0` 直接报错退出。
3. Handoff `:106` 措辞"verdict A/B/C 均加 `completed==iterations`"与 `:238` 实际（C 用 `detected_failures`）不完全对应，建议改为"completed（A/B）/ detected_failures（C）"。
4. Handoff `:72` §3 行 1 证据列仍写"会话转录（本节文字）"，未改为本轮新增的 `targeted-suite.log`。
5. 全仓回归证据 `full-suite.log` 是 R1 head 的，R2 head 未重跑全仓（Handoff §4 已披露）；R2 变更限于单一测试文件且该文件 R2 定向 15/15 通过。若需以 R2 head 的全仓绿入库，补一次约 72s 即可。

## 四、结论与推荐下一步

`decision=approved`。F1（P2）已实质修复并可对照 base 复核，其余 5 条各自以"修复/接受并披露/集成侧待办"闭合，处置证据（R2 日志、verdict 语义、pending 证据保留）与代码状态自洽；无未披露的范围溢出，无新增正确性风险。

推荐下一步（Integrator = Codex／代行 Codex）：将 `6fe7bd86` 集成入 main（保持 Owner 历史不重写），并同步 `doc/STATUS.md:7/:45` 的 FIX-A 状态；集成核验通过后再按串行规则释放 FIX-B。可直接转发的指令：

> 以 Integrator 身份集成 DIAG-READING-EXPORT-001-FIX-A：将 `agent/zcode/DIAG-READING-EXPORT-001-FIX-A-terminal-wait-semantics@6fe7bd86`（base `32ef1dd6`）集成入 main，执行 scope/`diff --check`/历史完整性核验（Owner 历史不重写），并同步 `doc/STATUS.md`（FIX-A 由 `proposed / NOT_RELEASED` 更新为已释放/已集成，标注 FIX-A 评审结论 `approved`、FIX-B 待串行释放），随后按 §5.1 释放 [DIAG-READING-EXPORT-001-FIX-B](doc/tasks/DIAG-READING-EXPORT-001-FIX-B.md) 并指派 Owner。集成记录须附本 Review 与本 Task 的 verdict。
