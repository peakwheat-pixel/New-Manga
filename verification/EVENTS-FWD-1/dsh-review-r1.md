# EVENTS-FWD-1 独立 Review（R1）

| 项 | 值 |
|---|---|
| Task | EVENTS-FWD-1（host→WebView 事件转发面，解 G17 / P14 前置） |
| Owner | antigravity |
| Reviewer | dsh（epoch 6；独立于 Owner） |
| 交付 commit | 分支 HEAD 实测 `5c02eecfcf9e109eb152185521f75180a238745e`（实现 `18462441c`，经两次 amend） |
| 基线 | `6c28a02e9` |
| 结论 | **approved**（`changes_requested` 的 1 项 I1 已于 `6229e230f` 收敛并复核通过，见 §5） |

## 1. 已独立验证且成立的部分

| # | 验证项 | 方法 | 结果 |
|---|---|---|---|
| V1 | 交付范围 | `git diff --name-only 6c28a02e9..HEAD` | 契约、`library_bridge.rs`、`main.rs`、`capabilities`、`gen/schemas/capabilities.json`、`frontend/src/events.{ts,test.ts}`、`packaged_sidecar_tests.rs`、Task/Handoff/verification —— **全在允许范围**；worktree clean |
| V2 | **无新增命令面** | 解析 `PRODUCTION_COMMANDS` 条目数 | **仍为 18** ✓（转发不新增命令，符合 AC1/AC5） |
| V3 | 契约内容合规 | 逐条比对 §6.4 | 六类已冻结事件逐条给 `core:*` 名与投影；**明令禁止路径/引用/密钥/字节**；事件须重查快照；**明确排除** `CoreAvailabilityChanged`(G16)/`ImportProgressChanged`(G26) 且未知事件 **fail-closed**；未改 §6.2 既有字段 |
| V4 | 安全投影 | 读 `project_forwarded_event` | **白名单式逐字段重建**，缺必填/类型不符返回 `None`，并校验取值（如 `RunPaused` 必须 `status=="paused"`）→ 无法意外泄露路径/引用 |
| V5 | 读路径重构 | 读 reader 线程 + `dispatch_stdout_line` | 设计正确：按 `event_type`/`request_id` 分流；**EOF 或读错时 `drain` 全部 pending 并以 `CORE_UNAVAILABLE` 唤醒**（不会挂死）；**单个 pending 时回退路由**，保留旧的"下一行即响应"语义；`impl Drop`（L935）在 L962 `handle.join()` → 读线程干净退出 |
| V6 | 既有不变式 | 读 `exchange` | 仍为**无超时阻塞等待**（与旧内联 `read_line` 相同）→ **未引入新的挂起语义**；stdin 写失败会移除 pending 并返回 typed 错误 |
| V7 | 四类定向测试 | `cargo-tests.log` | `test_events_fwd_all_six_frozen_events_projected` / `..._strips_forbidden_paths_and_opaque_references` / `..._fail_closed_on_unfrozen_events` / `..._dispatch_stdout_line_interleaved_with_responses` **全部 ok**；并发回归 `same_channel_concurrent_round_trips` 1 passed |
| V8 | 权限最小化 | `capabilities` diff | **只加** `core:event:allow-listen`/`allow-unlisten`，**刻意不加 `allow-emit`** → WebView 不能伪造事件 |
| V9 | 前端接线 | `events.ts` + `events.test.ts`；`frontend-tests.log` | 6 类 typed listener；**17 files / 177 tests passed**；`frontend-build.log` build 成功 |
| V10 | frozen bundle | `packaged-sidecar-tests.log` | **7 passed / 0 failed**（含新增的 `real_library_sidecar_event_sink_registration_and_lifecycle`） |
| V11 | 未弱化 FU1 测试 | `git diff 6c28a02e9..HEAD -- packaged_sidecar_tests.rs` | **纯新增 +24 行，删除 0 行** ✓ |
| V12 | 工作树卫生（我在前几轮登记的契约） | `git status` + diff 名单 | **`verification/P04` 的测试诊断未入库** ✓；**27 个 CRLF 噪音已恢复**（worktree clean）✓ |
| V13 | Python 套件 | `python-tests.log` | **395 passed** ✓ |

## 2. I1（必须返修，bounded，仅契约文档结构）

**finding**：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` 现含 **两个 h1 标题**（L9 与 L28），并**并存两条互相矛盾的"当前修订范围"**：

- L11/L13：`当前修订范围：EVENTS-FWD-1 rev 2.4`、`状态：rev 2.4 … minor 4`
- L30/L32：**`当前修订范围：HOST-ISSUER-1-C1 rev 2.3`**、`状态：rev 2.3 … minor 3`

owner 把新头部**插在原头部之前**而非替换，导致：重复 h1、**冲突的当前版本声明**、revision history 两套并行（`2.3` 同时在两处；`2.0/1.8/1.7/1.6` 在两处反复出现），且第一套 history **缺少 2.2/2.1**。

**为什么不只是观感问题**：本项目的每个 Task 都靠**契约修订号**精确 pin（"以契约为准"）。文档同时声明 rev 2.4 与 rev 2.3，会让后续 Task（尤其 P14）**引用错误的当前修订**。

**返修要求（bounded）**：

1. **恰好一个 `# M2-C1 — Typed IPC Contract` h1**；
2. **恰好一个当前修订/状态块**，声明 `rev 2.4`（EVENTS-FWD-1）与 `major 2 / minor 4`；
3. **恰好一套连贯的 Revision history**，按版本降序包含既有全部条目（至少 2.4/2.3/2.2/2.1/2.0/1.8/1.7/1.6 …），**不得丢历史条目**；
4. **不得**修改 §6.4 的规范内容、任何既有冻结字段/语义、其他章节、代码或证据；**不得**顺手重排无关章节；
5. 修完重新提交，并把 Handoff/Task 的 `delivery_head` 更新为**最终 HEAD**（见 §3 N-b），**不得**让该字段指向被 amend 掉的提交。

**不做**：不得借返修改实现、增删事件、改权限面或产品代码。

## 3. 已接受的信息性记录（非返修项，由 Coordinator 在 closeout 处理）

- **N-a（AC4 判定）**：owner 如实登记 `BLOCKED_ON_TRIGGER_COMMAND` 并给出四层分层证据（安全投影过滤 / stdio 多路复用旁路无干扰 / 真实 bundle 运行时 / 前端类型解包）。**符合 AC4 允许的"分层证据 + 如实 BLOCKED"路径**，接受。
  **值得记录的独立佐证**：owner 独立发现"生产命令面没有任何命令能启动 Pipeline Run"——这与 Coordinator 在同一时段只读发现并释放的 [RUN-IPC-1](../RUN-IPC-1.md) **完全一致**，是对该缺口真实性的第三方确认。
- **N-b（delivery_head 不一致，BL-7 类）**：Handoff 与 Task 记录的 `delivery_head=5c1695757342…`，而**分支 HEAD 实为 `5c02eecfcf…`**（reflog：`18462441c` → `5c1695757` → `5c02eecfc`，两次 amend）。两者内容差异**仅限** `doc/handoffs/EVENTS-FWD-1-fwd1.md` 与 `doc/tasks/EVENTS-FWD-1.md` 自身（代码与全部证据 tree **完全一致**），故**不影响证据有效性**；但记录必须冻结为最终 HEAD。按既有 BL-7 处置（closeout 一律以 `git rev-parse HEAD` 冻结实际值），**由 Coordinator 在集成/关闭阶段修正**，不计为 Owner 返修项。
- **N-c（声称不精确）**：Handoff 写"既有 Rust 测试 **80 passed**"，而归档日志 `cargo-tests.log` 实为 **79 passed + 1 ignored**（另 8 filtered）。应以日志为准；Review 采用 79 passed + 1 ignored。
- **N-d（窄残余风险，接受并记录）**：当**并发 ≥2 个未决请求**且 Core 返回一行既非事件、`request_id` 又不匹配任何 pending 时，该行会被丢弃、等待者可能持续阻塞。旧实现会把它当响应解码并返回解码错误。实际 Core 总是回显 `request_id`，且单并发时 fallback 会兜住，因此**风险很低**；记录以便后续硬化。

## 4. 收敛计划

`I1 返修（Owner=antigravity，仅契约文档结构） → Reviewer 复核 h1=1 / 单一 rev 2.4 声明 / 历史完整 + 确认 §6.4 与全部证据未变 → 集成（注意与 EXPORT-REVEAL-1 在 main.rs/library_bridge.rs 的冲突，按会话集成计划处理） → closeout（Coordinator 冻结实际 HEAD、修正 delivery_head）`。

## 5. I1 收敛记录（Reviewer 有界复核，结论：CONVERGED）

返修 commit `6229e230f`（契约结构修复）+ `5f1d9870e`（Handoff/Task 记录更新）。Reviewer 逐项复核：

| # | I1 返修要求 | 复核结果 |
|---|---|---|
| 1 | 恰好一个 h1 | **PASS**：`^# M2-C1` 计数 = **1** |
| 2 | 恰好一个当前修订/状态块，声明 rev 2.4 | **PASS**：`当前修订范围` = 1（L11，`EVENTS-FWD-1 rev 2.4`）；`^状态：rev` = 1（L13，`rev 2.4` / major 2、minor 4） |
| 3 | 一套连贯历史、无丢失 | **PASS**：`2.4 2.3 2.2 2.1 2.0 1.8 1.7 1.6` **各恰好出现一次**（此前第一套 history 缺 2.2/2.1 的问题已消除） |
| 4 | 不得改 §6.4 规范内容、既有冻结字段、其他章节、代码或证据 | **PASS**：契约 diff 为 **0 insertions / 18 deletions**（纯删重复头部块）；对 §6.4/事件名/权限行的 grep **零命中**；`verification/**` 与 `apps/desktop/**` 在 I1 中**零改动** |
| 5 | delivery_head 指向最终 HEAD | **部分达标**：由 `5c1695757` 更新为 `6229e230f`，但**真实 HEAD 已推进到 `5f1d9870e`**（记录后又追加了文档提交）→ 同一自引用模式第三次出现。按 BL-7 既有处置，**由 Coordinator 在 closeout 以 `git rev-parse HEAD` 冻结实际值**，不计为 Owner 返修项（已登记 BL-15） |
| 6 | （建议项）精确化 Rust 测试计数 | **PASS**：Handoff 已改为 `79 passed + 1 ignored (8 filtered) + 1 concurrent passed + 7 packaged passed`，与 `cargo-tests.log` 一致 |

**I1 CONVERGED，无需 I2。** 全 Task 最终判定 **approved**（可 `done`）。

