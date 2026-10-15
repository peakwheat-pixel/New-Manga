# P04 Owner 实现 R1 独立只读 Review

## 结论：**CHANGES_REQUESTED**

范围合规、AC1 与数据安全面**通过**，无 P0。但 AC2 的"确定性/可复现归属结论"存在一项 P1 实质缺口（`round_trip` 的写序与读锁序不受测试控制，归属判定仍由调度决定，存在漏检与不可复现），另有 P2 两项（脚本缺失时静默降级为 inline sidecar、`M2RC1_PYTHON` provenance 未强制/未记录）。AC2 的 Cargo 测试仍为 `BLOCKED / NOT_RUN`，本文所有结论均为**静态审查推断**，不是运行验证。

---

## 1. 审查对象核对

| 项 | 值 |
|---|---|
| HEAD | `751abae2277e975eddacc385a423bcd796334f97` ✅ 与期望一致 |
| HEAD tree hash | `7db544b75b6f694e4a510f5dbd5d917c47b26b7b` |
| 基线 9ea4e312 | `9ea4e312fa01470478946a557135791b5a044cb3`（tree `599c18f3a4d03e5741551c0a0480301470e8e3d8`） |
| 审查差异 | `9ea4e312..751abae2`，含 2 个提交：`9d00ed40`（测试实现，tree `e14ddc9ba44ac913549cfe50db6a72501d3642c7`）+ `751abae2`（Handoff） |
| 工作区 | 干净；仅 3 个未跟踪文件 `dsh-p04-owner-review-r1.{prompt.md,stdout.md,stderr.log}`，经核对是**本次派发产物**，不属于 Owner 差异 |
| `git diff --check` | exit 0，无空白错误 |

变更 7 文件，**全部为纯新增**（`--numstat`：149/0、32/0、101/0、24/0、0/0、0/0、137/0），无任何行被删改。

**范围合规（逐条核对，通过）**
- `library_bridge.rs` 新增行全部落在 `#[cfg(test)] mod tests`（模块起始 `library_bridge.rs:695`）内；`main.rs` 新增行在 `main.rs:1167-1193`，位于既有 `mod tests` 内。
- 未触碰 `Cargo.toml`、`tauri.conf.json`、capabilities、IPC/Schema、依赖、Python Core、frontend；`doc/**` 零改动（Owner 未动共享 Plan/Status/Index，符合 Task L44）。
- 未新增依赖：仅用 `std`（`Arc`/`Barrier`/`thread`）与已在用的 `serde_json`；`LibraryError` 有 `Debug`（`library_bridge.rs:41`），`expect` 可编译。
- `list_chapters` / `list_chapter_pages` 的冻结依据与 [M2-C1 rev 1.8 §5](../../doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md) L140-141 一致（probe/AC1 冻结面零变化，option-B 先例）。
- Handoff 与 Task 测试表**无任何假 PASS**：三行均为 `BLOCKED / NOT_RUN`，与 P02 Build Gate 状态一致。

---

## 2. Findings

### P1-1 AC2 的交错顺序不受控：归属结论不可复现，存在漏检/假通过

**位置**
- `apps/desktop/src-tauri/src/library_bridge.rs:1047`（新测试）、`:1139`（`Barrier::new(2)`）、`:1146` / `:1154`（两条并发 `round_trip`）
- `apps/desktop/src-tauri/src/library_bridge.rs:263-310`（`round_trip`）：`:283-293` 持 **stdin** 锁写完即释放；`:296-303` 持 **stdout** 锁跨 `read_line` 阻塞持有
- `verification/P04/deterministic_concurrent_sidecar.py:112-125`：仅在收到 **2 条** `test.concurrent_*` 后，按**接收顺序**回包

**影响**
归属是否正确，取决于"stdin 写入顺序"与"stdout 锁获取顺序"是否一致，而这两个顺序之间**没有任何确定性约束**（`Barrier` 只同步起跑瞬时）：

- 一致 → 各自读到自己的响应 → PASS；
- 不一致（后写者先取得 stdout 锁）→ 读到对方的响应 → 断言 panic → FAIL。

因此同一份代码可能一次 PASS、一次 FAIL（flaky）；且在典型调度下，先写完 stdin 的线程随即执行 `lock()` 并阻塞持有 stdout 锁，写序与锁序**倾向一致**，测试可能恒为 PASS —— 若并发错配缺陷真实存在也会被漏掉。这与 AC2 要求的"**可复现的**响应归属结论"直接冲突：AC2 的 PASS/FAIL 结果无法作为集成 Gate 依据。

**触发条件**：调度使后写者先取得 stdout 锁（情形"alpha 先写 stdin、beta 先锁 stdout"或其镜像）。

**最小建议（二选一，需 Integrator 裁决）**
1. 给出不改生产代码的确定性控制手段（例如用测试可访问的 `stdout` 私有字段与共享标志，使两条 `round_trip` 的交错顺序在测试内被**确定性地**确立）；或
2. 若确认在"必须经 `round_trip` 且生产代码零改动"的约束下无法确定性构造，则按 **AC3 备选路径**处置：P04 置 `blocked`（previous=`in_progress`），由 Codex 另立测试 seam Task，本测试**不得**作为"同通道归属正确"的证据。

无论结果如何，该测试输出只能记为"单次调度相关观察"，不得据此记录行为 `PASS`。

### P2-1 sidecar 脚本缺失时静默降级为 inline 变体，掩盖证据来源

**位置**：`library_bridge.rs:1067-1068`（`if script_path.is_file(){ cmd.arg(&script_path); } else { … }`）、`:1070-1107`（`INLINE_SIDECAR`）。

**影响**：Handoff §1.2/§2 声明 AC2 使用 `verification/P04/deterministic_concurrent_sidecar.py`；但脚本不存在时测试会改用行为不完全等价的 inline 变体并继续运行（甚至 PASS），运行时无法区分，"证据来自交付脚本"这一声明在运行时无保证。两者差异示例：inline 的日志写入为 `except Exception: pass`（静默），文件脚本写 stderr（`:33-35`）。

**触发条件**：`repo_root` 推导失效、仓库布局变化或脚本被移动。

**最小建议**：删除 fallback，改为 `assert!(script_path.is_file(), "P04 test sidecar missing: {script_path:?}")`；至少让缺脚本时测试失败而非静默换源。

### P2-2 `M2RC1_PYTHON` provenance 未强制、未记录

**位置**：`library_bridge.rs:1051`（`unwrap_or_else(|_| "python".into())`）；sidecar 未记录 `sys.executable` / `sys.version`；Handoff L47 仅列前提。

**影响**：Task AC2 明确要求"`M2RC1_PYTHON` 路径与版本须来自 P02 批准环境并记录到证据"。当前测试静默回退到 PATH 上的 `python` 且不告警，诊断 jsonl 只旁录 `protocol`/`version`/`request_id`，不含解释器身份。注：该回退与既有 `real_*` / `startup_ping_deadline_*` 测试同风格（`library_bridge.rs:950/972/1011`，M2-IPC1 review P3-5 已记录该非 hermetic 模式），因此**不是新引入缺陷**，但与本轮 AC2 的显式要求有落差。

**触发条件**：未设置 `M2RC1_PYTHON` 时运行。

**最小建议**：让 sidecar 把 `sys.executable` + `sys.version` 写入诊断 jsonl；或在测试中断言该 env 存在（若 Gate 保证提供）；至少在 Handoff 中写明回退行为。

### P3-1 测试运行副作用写死仓库存根路径且不清理

**位置**：`library_bridge.rs:1061-1065`、`:1110`；`deterministic_concurrent_sidecar.py:62-65`。

每次运行会向 `verification/P04/concurrent_sidecar_diagnostic.jsonl` **append** 未跟踪产物，无清理、无上限；多次/并发运行会累积。写入失败被吞掉（不影响断言，这点是稳健的，符合 Task"旁录不代表 PASS"）。建议改用 `CARGO_TARGET_TMPDIR` 或带时间戳/唯一文件名，或在测试结束时清理。

### P3-2 两个 0 字节文件作为证据提交

`verification/P04/antigravity-owner-implementation-r1.stdout.json` 与 `.stderr.log` 均为 **0 字符**（已用 `git show` 核对）。`stdout.json` 是空文件而非合法 JSON，无证据价值，且与同目录 `antigravity-availability-probe-r1.stdout.json`（263 字节）形成误导性对比。建议删除，或在 Handoff 说明为空的原因。

### P3-3 Handoff 的 `delivery_head` 与本次审查 HEAD 语义不一致

`handoff.md:9` 记 `delivery_head: 9d00ed408ca69964fd15e6aa42170d8368221248`（= 实现提交，tree `e14ddc9b…`），而审查对象是 `751abae2`（含 Handoff 自身的提交，tree `7db544b7…`）。这不构成错误（Handoff 无法自引用其所在提交），但字段名会让集成者取不到包含 Handoff 的提交。建议改名 `implementation_head`，或补 `reviewed_head` 一行。

### P3-4 无超时保护（既有模式）

AC2 测试的两次 `round_trip` 无超时（`library_bridge.rs:1157-1165`）。正常路径下 `Drop`（`:424-441`）会写 `core.shutdown` 并 `wait_timeout_or_kill`（≤5 s），sidecar 在 `:103-105` `return 0`，清理完整。异常情况下（sidecar 收到 1 条请求后不再回包，例如 spawn 后对端异常）`read_line` 会永久阻塞，测试挂起而非失败。与既有测试风格一致，风险低；可选加测试侧超时。

### 未发现的问题（明确写"无"）
- 无 P0；未发现生产逻辑、IPC/Schema、依赖、capabilities、Python Core 改动。
- **死锁**：结论为不会死锁 —— stdin 写受锁保护不会交错；两行写完后 sidecar 必然回包（脚本 `:115`），两个 `read_line` 都能满足；管道缓冲不足以阻塞 2 行写入。
- **假 PASS 声明**：无；Task/Handoff 对 NOT_RUN 的表述诚实。
- **数据安全**：测试不 spawn 生产 Core、不设 `NEWMANGA_DATA_ROOT`、不触碰用户数据；sidecar 只做 JSON 往返。

---

## 3. AC 证据状态

| AC | 静态证据状态 | 无法静态证明 / 未决 |
|---|---|---|
| **AC1** | **静态满足**。`main.rs:1169-1172` 为字面 `assert_eq!(PAGE_NAV_PRODUCTION_ONLY_COMMANDS, &["list_chapters","list_chapter_pages"])`；`:1178` 期望值用独立字面常量 `EXPECTED_PAGE_NAV_COMMANDS`，**未从被测常量派生**；`:1174-1192` 验证 production 面包含、probe 与 AC1 面均不含；与常量定义 `main.rs:133-134`、既有 15 项生产面测试 `:1021-1048`、既有排除扫描 `:1135-1161` 一致 | 编译未验证（我做了类型层静态推理：`&[&str]` 与 `&[&str; 2]` 的 `PartialEq` impl 存在于 std，但**未编译**）；测试命令 NOT_RUN |
| **AC2** | **实现存在但目标未达成**。同一 `Arc<StdioLibraryChannel>` 实例（`:1125-1128`）、两条可区分 `round_trip`（`:1146/:1154`）、无 sleep、无概率循环、生产代码零改动、归属用 `caller`+`token` 双字段断言（`:1167-1185`） | "确定性/可复现归属结论"未达成 → **P1-1**；`M2RC1_PYTHON` provenance 未记录 → **P2-2**；运行时交错分布与实际 PASS/FAIL **无法静态证明**；NOT_RUN |
| **AC3** | 规则已写入 Handoff §5；无错配被复现（因未运行）；不修生产、不改生产行为 | 当前测试在错配成立时会直接 panic（FAIL），与 AC3"不提交会失败的测试"存在张力，须在 AC2 **首次运行后**按结果处置（不运行本 Task 无法判定） |
| **AC4** | 本次即 R1 非作者审查 | Handoff §4 指定的落盘文件 `verification/P04/dsh-implementation-review-r1.stdout.md` **未由我创建**（用户指令禁止创建文件），需派发方/Integrator 落盘；修订后需 R2 复审 |

---

## 4. 声明

- 我**没有运行**任何测试或构建：未运行 Cargo、Rust 测试、Tauri、Python sidecar、Sandbox，未执行任何产品验收。所有命令均为只读的 `git`（`rev-parse`/`log`/`diff`/`show`/`status`/`diff --check`）与文件读取。
- 我**没有修改、创建、格式化、暂存或提交任何文件**；本 Review 仅以对话输出呈现。
- 上文全部结论为**静态代码/文档推断**，凡涉及运行时行为的（交错分布、编译通过与否、PASS/FAIL）均已标注为未证明。
- 本次未把任何 `NOT_RUN`/`BLOCKED` 写成 `PASS`。

---

## 5. 推荐下一步

**结论为 CHANGES_REQUESTED，需先裁决 P1-1 的处置路径。**

- **Task ID / 标题**：P04 AC2 确定性处置（R1 findings 修订）
- **推荐 Agent**：Codex（Integrator，先就 P1-1 作路径裁决）→ Antigravity（Owner 修订）
- **前置依赖**：P02 Build Gate 仍 BLOCKED，本步**不得**运行 Cargo/Tauri
- **Recovery Point**：`9ea4e312`；被审 HEAD `751abae2`（tree `7db544b7…`）
- **允许修改路径**：`apps/desktop/src-tauri/src/library_bridge.rs`（仅 `#[cfg(test)]`）、`apps/desktop/src-tauri/src/main.rs`（仅测试）、`verification/P04/**`、P04 Handoff/Review
- **禁止范围**：生产逻辑/IPC/Schema/依赖/capabilities/Python Core 零改动；不运行 Cargo/Tauri/sidecar；不把 NOT_RUN 写成 PASS

**可直接转发给 Codex 的指令**

```markdown
P04 实现 R1 独立 Review 结论为 CHANGES_REQUESTED（HEAD 751abae2，tree 7db544b7…），
静态证据见审查输出。请裁决并分派：

1) 先就 P1-1 裁决路径：(a) 接受 Antigravity 在 production 零改动前提下提出 AC2 确定性
   交错控制方案；或 (b) 确认不可确定性构造，按 P04 Task AC3 备选把 P04 置 blocked
   （previous=in_progress），另立独立测试 seam Task（明确不依赖 P04=done）。
2) 无论哪条路径，要求 Owner 同批处理 P2-1（删除 sidecar 缺失时的 inline 静默降级，
   改为 fail-fast）与 P2-2（把 sys.executable/sys.version 写入 verification/P04 诊断，
   或在测试中强制 M2RC1_PYTHON）。
3) 明确纪律：P02 Build Gate 仍 BLOCKED，本轮不得运行 Cargo/Tauri/sidecar；
   不得把任何 NOT_RUN 记为 PASS；AC2 结果未运行前不得作为归属正确证据。
4) Review 报告落盘 verification/P04/dsh-implementation-review-r1.stdout.md 由你/派发方完成。
```

无需其他并行操作。
