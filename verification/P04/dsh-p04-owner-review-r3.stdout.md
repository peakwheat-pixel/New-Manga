以下为**R3 完整最终 Review 报告**（本会话上一轮只完成了证据收集、未产出 verdict，故此处为首次完整结论，并已针对本轮固定 HEAD 重新核查全部被审文件）。

---

# Review：P04 生产命令族与同通道桥接并发定向验证（实现 R3 复审）

## 元信息

| 项 | 值 |
|---|---|
| task_id | `P04` |
| Reviewer | DeepSeek Harness（非作者独立 Reviewer） |
| Author | Antigravity |
| Integrator | Codex |
| 原始 Review base | `9ea4e312fa01470478946a557135791b5a044cb3` |
| 上轮 reviewed HEAD（R2） | `42b87f6bb6314fb42df3592f15a9fcd69866739b` / tree `e642151118cebdbb21cc283afc86121345ee52e0` |
| 本轮 implementation head | `eedbda05ef42d61b35149c4d3d54ac0804b7b80d` |
| 本轮 delivery HEAD | `ec44a4891d624c88e89abfe2c13d9e7e072b9e5e` / tree `864bfdf0368fb912b148021d5352258341fef362`（**hash 未由我独立验证**，见 §6） |
| 被审证据 | `library_bridge.rs`（全文）、`verification/P04/deterministic_concurrent_sidecar.py`（全文）、`doc/tasks/P04.md`、`doc/STATUS.md`、`verification/P04/antigravity-owner-implementation-r1.handoff.md`、`verification/P04/antigravity-owner-revision-r1.handoff.md`、`verification/P04/antigravity-owner-revision-r2.handoff.md`、R1 报告、Codex checkpoints |
| **decision** | **`CHANGES_REQUESTED`**（P0/P1=0；未解决 P2=3、P3=1，其中 2 项属 Owner 可执行小修、2 项属 Codex 侧集成前置） |

> 口径声明：本轮为**只读静态复审**。P02 Build Gate=`BLOCKED`、`build=NOT_AUTHORIZED / NOT_RUN`、Hard Build Barrier=`EFFECTIVE` 不变；AC1/AC2 Cargo 与集成后验证一律 `BLOCKED / NOT_RUN`。**R2-001 的 AC3 负向复现分类不是 P04 完成**：P04 不得标 `done`，Build Barrier 不得解除，本 head 不构成 AC2 通过或集成授权。

## 1. 范围与依据

被审差异范围 `9ea4e312..ec44a489`（Codex 已独立验证该范围仅 `library_bridge.rs`、P04 Task/Handoff、测试 sidecar 变更，`git diff --check` EXIT=0；我无法复跑，见 §6）。本轮实际核查内容：

- 真实 test seam 与时序：`round_trip` `library_bridge.rs:263-324`（stdin 锁 `:283-293`、after-stdin hook `:295-300`、stdout 读锁 `:302-310`、response observer `:316-321`）、seam 定义 `:392-448`、AC2/AC3 测试 `:1082-1311`。
- sidecar `deterministic_concurrent_sidecar.py`（provenance `:68-73`、FIFO 回包 `:120-134`、日志失败 `:33-36`）。
- AC1 证据仍完好：`main.rs:1167-1193`（字面断言 `:1169-1172`、独立字面期望 `:1178`、三面边界 `:1174-1192`）。
- 状态/证据链：`doc/tasks/P04.md`（frontmatter `:5`、测试表 `:58-64`、交付记录 `:74-82`）、`doc/STATUS.md:5`、三份 Handoff。共享契约 `M2-C1` §3–4 与 Task `:29`/`:70` 的 PROPOSAL 限制。

## 2. R2-001..R2-008 逐条复核结论

| R2 ID | 级别 | R3 独立复核 | 结论 |
|---|---|---|---|
| **R2-001** | P1 | 已按 AC3 定性为"确定性负向诊断/复现器"：docstring `:1085-1092`（明确 "NOT a passing regression gate"、"STATICALLY GUARANTEES response cross-talk mismatch"、`static_expected_behavior = FAIL`、"Cargo test exit 0 … MUST NOT be construed as response ownership PASS"）；artefact 记录 `:1274-1275` 同时含运行期 `behavior` 与静态期望；Handoff `antigravity-owner-revision-r2.handoff.md:44` 状态写 `AC3 REPRODUCER DEFINED (P04 BLOCKED)`，非通过型 CLOSED，且 §5 只请求 R3 复审、未请求集成；runtime 一律 `BLOCKED / NOT_RUN`，`verification/P04/` 下**不存在**任何 `diagnostic_p04_*.jsonl` / 旧 `concurrent_sidecar_diagnostic.jsonl`（已 glob 确认）→ **无伪造 sidecar log**。 | **CLOSED（作为处置）**；其状态落地缺口见 R3-3，复现器启用口径见 R3-1 |
| **R2-002** | P2 | 代码注释 `:1091-1092` 明示 exit 0 ≠ 归属 PASS；`:1257-1266` 只计算 `behavior`、无归属断言；`:1302-1310` FAIL 分支只打印。未新增"错配即 panic"断言，符合 AC3。 | **CLOSED** |
| **R2-003** | P2 | `antigravity-owner-implementation-r1.handoff.md` 已更正：`:25` 记录 `round_trip` 体内 `#[cfg(test)]` hook；`:34` 第 3/4/5 点改为 hook+mpsc 编排、AC3 负向复现器、唯一诊断文件名；全仓 `grep Barrier|严格断言|concurrent_sidecar_diagnostic` 在该 Handoff 内**零命中**（仅历史 response/stdout 工件与 R1 报告保留历史表述，属历史证据）。 | **CLOSED** |
| **R2-004** | P2 | Rust：`:1288-1294` 改为 `.expect("failed to open/create P04 diagnostic verdict log file")` / `.expect("failed to write concurrency verdict record to diagnostic log")`。Python：`:33-36` 捕获后写 stderr 并 `raise RuntimeError(...)`（未捕获→进程失败）。两侧均不再静默吞错。 | **CLOSED** |
| **R2-005** | P3 | `library_bridge.rs` 内 `phase_hook` 零命中（仅历史 prompt/checkpoint 文本保留该符号）；`:1094-1096` 准确描述 `set_test_after_stdin_hook` / `set_test_response_observer` 与 bounded mpsc 编排。 | **CLOSED** |
| **R2-006** | P3 | 两个 mpsc 等待均已 bounded：`:1192-1194`、`:1219-1221`（`recv_timeout(10s).expect(...)`）。但 `:1247-1252` 的两个 `join()` 与 `:307-309` 的 `read_line`（经 `:1203`/`:1232` 调用）仍**无界**，Handoff `revision-r2:49` 的"sidecar 异常挂起仍受 Drop 5 秒 budget 保护"表述不准确 → R3-4。 | **部分关闭**（通道等待已 bounded；剩余限制表述待修正） |
| **R2-007** | P3 | `doc/tasks/P04.md:74-82` 已登记 R1/R2 三份 Handoff 与实现 Review（含 `0/1/3/4`），测试仍 `BLOCKED / NOT_RUN`（`:60-62`、`:81`），无假 PASS。但 `:80` 引用的 `verification/P04/dsh-p04-owner-review-r2.stdout.md` **在本 worktree 与根仓均不存在**（R3-2）；且"P04 保持 blocked"未在权威元数据落地（R3-3）。 | **部分关闭** |
| **R2-008** | P3 | 保留策略已登记（`revision-r2:51`：默认保留、严禁通配符删除、由 Codex 集成阶段轮转）；被审代码/脚本内**无任何删除调用**（sidecar 与测试均无 `remove/unlink/glob delete`），策略与实现一致。 | **CLOSED** |

## 3. R3 Findings

| ID | 级别 | 路径/行 | 根因 | 最小修复 | 归属 |
|---|---|---|---|---|---|
| **R3-1** | P2 | `library_bridge.rs:1103-1104`（`#[test]`，无 `#[ignore]`）、`:1109-1111`（`M2RC1_PYTHON` 硬 `expect`）、`:1124-1128`（脚本必须存在）、`:1288-1294`（必须写入 `verification/P04/**`） | 复现器默认启用且带硬前置条件：未设 `M2RC1_PYTHON` 的普通 `cargo test` 会 panic；每次运行都会在仓库内产生 untracked 诊断产物。同文件既有测试用 `unwrap_or_else(\|_\| "python")`（`:992`/`:1014`/`:1053`），本测试是该 crate 首个硬失败前置；Task/三份 Handoff 均未登记"默认测试套件口径已变化"。仓库对 AC3 复现器已有先例：`verification/P04/dsh-proposal-review.stdout.md:45` 建议"复现测试以 `#[ignore]` + 原因注释入库并登记为'由修复 Task 解除'"。 | 二选一：(a) 给该测试加 `#[ignore = "P04 AC3 reproducer: deterministic negative case, run via cargo test -- --ignored"]` 并在 Handoff 写明未 ignore 的理由；或 (b) Codex 明确裁决保持启用，并在 Task/Handoff 登记"默认 `cargo test` 现要求 `M2RC1_PYTHON` 且写入 `verification/P04/**`"。 | Owner（(a)）或 Codex 裁决（(b)） |
| **R3-2** | P2 | `doc/tasks/P04.md:80`、`antigravity-owner-revision-r2.handoff.md:20` | 两份文档都引用 `verification/P04/dsh-p04-owner-review-r2.stdout.md` 作为本次返修依据，但该文件在 worktree 与根仓均不存在（`glob **/dsh-p04-owner-review*` 仅得 `r1.*` 与本轮 `r3.stdout.jsonl/.exit`）→ 证据链断链，后续任何人对"R2 要求了什么"只能依赖聊天记录，违反"引用实际文件与 commit"的仓库纪律。 | Codex 把 R2 报告归档到被引用的确切路径（或修正引用为实际归档路径）；属派发方/Integrator 动作，非 Owner 代码问题。 | Codex |
| **R3-3** | P2 | `doc/tasks/P04.md:5`（`status: in_progress`）、`doc/STATUS.md:5`（"P04 已进入 in_progress"）vs `revision-r2.handoff.md:44`/`:66`、`implementation-r1.handoff.md:35`（均称 "P04 保持 blocked"） | AC3 的 `P04 置为 blocked（previous=in_progress）` 未在任何权威元数据落地；Handoff 反复声明 blocked，而 Task frontmatter 与 STATUS 仍为 `in_progress` → 状态互相矛盾，集成者可能误判 P04 仍在正常推进而非 AC3 阻断。 | Codex 将 P04 置 `blocked`（previous=`in_progress`）并同步 `doc/STATUS.md`；在落地前，Handoff 不应单方面断言"P04 保持 blocked"。 | Codex |
| **R3-4** | P3 | `revision-r2.handoff.md:49`；`library_bridge.rs:1247-1252`、`:307-309` | "若 sidecar 进程异常挂起仍受 Drop 机制 5 秒 budget 保护"仅对"两侧回包后 sidecar 仍存活"成立；若 sidecar 发出第 1 行后挂起，主线程阻塞在 `handle_alpha.join()`，测试函数永不返回，`Drop`（`:466-483`）不可达 → 仍可永久挂起。另 `:1194`/`:1221` 的文案把所有 `recv_timeout` 失败（含 sender 断开）都描述为 timeout。 | 修正 Handoff 表述为"仅覆盖 mpsc 通道等待；`read_line` 阻塞导致 join 无界时 Drop 不可达"；可选（在授权路径内、复用既有 test-only seam）加看门狗线程在 N 秒后调用 `kill_for_test()`（`:392-398`）使阻塞 `read_line` 得到 EOF、测试失败而非挂起。 | Owner |

**在记录范围内未发现的问题（明确写"无"）**：无 P0/P1 未解决项；未发现生产逻辑/IPC/Schema/依赖/capabilities/Python Core/frontend/共享规划文档改动；未发现新增依赖；未发现伪造运行证据或把 `BLOCKED / NOT_RUN` 写成 PASS；未发现测试代码落到 `#[cfg(test)]` 之外（cfg(test) 清单：`:295`/`:316`/`:392`/`:403`/`:422`/`:430`/`:440`/`:737`，与 R2 一致，无新增生产面 seam）；未发现通配符删除既有文件的行为。

## 4. AC 状态

| AC | 静态状态 | 运行状态 |
|---|---|---|
| **AC1** | **静态满足**（`main.rs:1169-1172` 字面断言 + 独立字面期望 `:1178` + production/probe/M2-AC1 三面边界 `:1174-1192`） | `BLOCKED / NOT_RUN` |
| **AC2** | **未达成、且不可记 PASS**：交付已如实改为同类 AC3 复现器；静态推导结论为跨调用方错配（`static_expected_behavior=FAIL`），AC2 要求的"每个调用方拿到自己的结果/错误"无法被该构造证明 | `BLOCKED / NOT_RUN` |
| **AC3** | **已按 AC3 触发并声明**（记录结构化证据、不 panic、不改生产行为、移交独立修复 Task）；但 `P04=blocked` 的状态转换未落地（R3-3），且"最小复现落 `verification/P04/**`"目前由 Handoff §2 与代码注释承载，运行期 artefact 在未运行下不存在 | `BLOCKED / NOT_RUN` |
| **AC4** | R1/R2 已由非作者完成，本文即 R3；集成与集成后定向验证未开始 | `BLOCKED / NOT_RUN` |

## 5. 验证

| 场景 | 命令 | 结果 | 证据 |
|---|---|---|---|
| AC1 allowlist 常量成员 | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop page_nav_production_only_commands_are_exact` | **BLOCKED / NOT_RUN** | 无（Build Gate=`BLOCKED`） |
| AC2 同通道并发响应归属 | `cargo test … same_channel_concurrent_round_trips_keep_response_ownership` | **BLOCKED / NOT_RUN** | 无 |
| P04 集成后定向验证 | 复跑上述两项 + `git diff --check` | **BLOCKED / NOT_RUN** | 无 |
| 本轮变更集/HEAD 绑定核验 | `git rev-parse HEAD`、`git diff --stat 9ea4e312..ec44a489`、`git diff --check` | **BLOCKED / NOT_RUN（环境不允许）** | 沙箱无法为工作区配置写权限（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)`），无审批通道 → `pwsh`/`git` 不可用；改以 `read`/`grep`/`glob` 直读 |

**Cargo AC1/AC2 未运行对 Review 门槛的影响**：即使全部 finding 关闭，本轮也**不能**把 AC1/AC2 记为 PASS，`REVIEW.md` 门槛要求"关键验证缺失时不可批准"。本报告的"静态可接受"仅指：AC3 复现器定位、seam 设计、证据写法与范围合规；**不等于 P04 完成、AC2 通过或可解除 Build Barrier**。

## 6. 覆盖 / 未覆盖、限制与剩余风险

**已覆盖**：`library_bridge.rs` 全文（生产 `round_trip` 与全部 `#[cfg(test)]` seam、AC2/AC3 测试逐行时序推导）、sidecar 全文、`main.rs` AC1 测试与 allowlist 定义、`doc/tasks/P04.md`、`doc/STATUS.md`、三份 Owner Handoff、R1 报告与 Codex checkpoints、`verification/P04/**` 文件清单（确认无 `diagnostic_p04_*.jsonl`/旧日志名文件）。

**未覆盖/不可验证**：① 无法运行 git，故 `ec44a489`/tree `864bfdf0…`（及 `eedbda05…`）与工作区内容的一致性、变更文件集穷举、`git diff --check` 均为 `BLOCKED / NOT_RUN`（间接证据：worktree branch ref = 交付分支，Handoff 元数据与本轮给定 hash 自洽）；② 编译未验证（`recv_timeout` 调用、`#[cfg(test)]` seam 泛型实例化仅静态推理）；③ 运行时行为、`behavior` 实际取值、sidecar provenance 内容未运行；④ 本轮 `verification/P04/dsh-p04-owner-review-r3.prompt.md` 在该 worktree 不存在，我按本会话给定要求执行（与 R2-007 提及的文件缺失同源，见 R3-2）。

**剩余风险**：① AC2 归属风险仍在（响应按 stdout 读取顺序 FIFO 归属、无 `request_id` 关联），须由独立修复 Task 处置；② `static_expected_behavior: "FAIL"` 是硬编码字面量，修复 Task 集成后该字段会变陈旧，需在回归测试中重新推导或移除；③ 挂起面仍存在（R3-4）；④ 默认 `cargo test` 口径变化与仓库内诊断产物累积（R3-1/R2-008）。

## 7. 集成建议与下一条动作

**不可集成、不得闭环 P04。** 本 head 的静态交付已把 R2-001 正确转为 AC3 负向复现器，剩余 4 项均为 P2/P3 且两项属 Codex 侧；建议如下：

1. **Codex（集成前置，必须）**：把 P04 置 `blocked`（previous=`in_progress`）并同步 `doc/STATUS.md`（R3-3）；把 R2 报告归档到 `verification/P04/dsh-p04-owner-review-r2.stdout.md` 或修正全部引用（R3-2）；就复现器是否 `#[ignore]` 作明确裁决并登记默认测试套件口径变化（R3-1）。
2. **Codex**：按 AC3 建立**不依赖 P04=`done`** 的独立生产修复 Task，把本复现器与该静态推导作为输入证据；修复集成后恢复 P04，补入/启用回归测试并复跑 AC2 取得真实运行证据。
3. **Owner（Antigravity，小修）**：修正 `antigravity-owner-revision-r2.handoff.md:49` 的挂起/Drop 表述（R3-4）；若 Codex 裁决走 `#[ignore]`，同步加注释与运行命令说明（R3-1）。
4. **纪律不变**：P02 Build Gate 保持 `BLOCKED`、Hard Build Barrier `EFFECTIVE`，不得运行 Cargo/Tauri/sidecar/build/Sandbox/host inventory，AC1/AC2 保持 `BLOCKED / NOT_RUN`。

**下一条具体动作**：Codex 先执行第 1 项（状态落地 + R2 报告归档 + 复现器启用裁决），随后把第 3 项的最小修复指令发回 Antigravity 同一 conversation 并请其提交新固定 head；Owner 修订完成后，再派 DeepSeek Harness 对该新 head 作 R4 复审（若第 1、3 项均在集成前完成，R4 可仅做 exact-head 确认）。在此之前，P04 不得 `done`，也不得解除任何 Build Barrier。

（本报告未创建/修改任何文件；请由 Codex 归档为 canonical report `verification/P04/dsh-p04-owner-review-r3.stdout.md`。）