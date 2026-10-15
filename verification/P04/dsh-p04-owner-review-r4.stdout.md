我已完成全部可执行的静态核验。以下是 R4 exact-head 复审报告。

---

# Review：P04 Owner R4 修正（R3-1 / R3-4）exact-head 复审

## 元信息

| 项 | 值 |
|---|---|
| task_id | `P04` |
| Owner | Antigravity |
| Reviewer | DeepSeek Harness（非作者独立 Reviewer） |
| Integrator | Codex |
| 修正基线（父） | `5ea8304ae1670e079b7a496e08fbdea6f656156f` |
| 唯一待审 commit | `faea1a2c9e19f4817fd792290e91324f047529f9` |
| 声称 tree | `eb0cc832531005a40d7a7294daf12cd0baa30a3d`（**我无法独立核验**，见 §1） |
| 分支 / worktree | `agent/antigravity/P04-prod-command-concurrency` / `G:/CODEX/New Manga.worktrees/P04-prod-command-concurrency-antigravity` |
| R3 原报告 | `verification/P04/dsh-p04-owner-review-r3.stdout.md`（`CHANGES_REQUESTED`，未解决 `0/0/3/1`） |
| 审查性质 | **只读静态审查**；未运行 Cargo / Rust / Tauri / sidecar / GUI / Sandbox / 宿主写权限探测；未创建或修改任何文件 |
| decision | **APPROVED**（范围限定见 §7） |

---

## 1. Git / 文件绑定能力与实际核验结果

**能力现状（重要限制）**：本会话 `pwsh` 通路整体不可用——沙箱在启动时即失败：`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\P04-prod-command-concurrency-antigravity)`，连 `echo hello` 都无法执行；对同一只读 git 操作尝试一次性提升到 `danger-full-access` 返回 `requires approval, but no approval channel is available`，故**未获得任何 Git 执行能力**。这与 R3 报告 §5 记录的同一环境限制一致。

| 绑定项 | 是否独立核验 | 实际得到的证据 |
|---|---|---|
| HEAD 分支 | **是** | worktree gitdir `HEAD` = `ref: refs/heads/agent/antigravity/P04-prod-command-concurrency` |
| 分支当前指向 | **是** | `.git/refs/heads/agent/antigravity/P04-prod-command-concurrency` = `faea1a2c9e19f4817fd792290e91324f047529f9` |
| 待审 commit 存在 + 父提交 | **是（reflog 级）** | worktree `logs/HEAD` 末行：`5ea8304ae1670e079b7a496e08fbdea6f656156f faea1a2c9e19f4817fd792290e91324f047529f9 … commit: test(P04): ignore AC3 negative reproducer and clarify timeout boundaries for R3 review` |
| commit message 主题 | **是** | 同上 reflog 记录，与 R4 授权范围（ignore + timeout 边界说明）一致 |
| commit `tree` = `eb0cc832…` | **NOT_VERIFIED** | 无 git 能力，无法解析/校验 commit 对象；`tree` 仅来自 Owner 声明与 Codex 复核 |
| 工作树内容 == `faea1a2c` 内容 | **NOT_VERIFIED** | 无 `git status` / `git diff`；只能确认"我读到的文件内容"自洽 |
| base..HEAD 差异路径穷举 | **NOT_VERIFIED（独立）/ 与 Codex 声明一致（交叉）** | 无法复跑 `git diff --stat`、`git diff --check`；采信用户给定的 "Codex 复核唯一差异路径" 并结合静态一致性证据（§2/§4） |

诚信声明：以上"是"的部分来自**直读 worktree 的 Git 元数据文本文件**（reflog / ref / HEAD），不是 Owner 或 Codex 的转述；**未**把任何静态审查说成运行验证，也**未**假称核验过 `tree`。附加事实：本次派发的宿主日志 `verification/P04/codex-dsh-owner-r4-review.{stdout.json,stderr.log}` 已存在于磁盘，属 Codex 侧派发工件，不在 Owner R4 授权路径内。

---

## 2. R3-1 核查：AC3 负向复现器是否被准确 `#[ignore]` 并移出默认集合

**代码事实（`apps/desktop/src-tauri/src/library_bridge.rs`）**

- `:1103-1105`：
  ```rust
  #[test]
  #[ignore = "P04 AC3 reproducer: deterministic negative diagnostic, run explicitly via cargo test -- --ignored"]
  fn same_channel_concurrent_round_trips_keep_response_ownership() {
  ```
  属性紧跟 `#[test]`、函数名与 R3 指定目标测试完全一致，且 `#[ignore]` 带明确原因字符串（优于 `main.rs` 既有裸 `#[ignore]` 先例）。
- 全 `apps/desktop/src-tauri/src` 范围 `#[ignore` 命中 **仅 2 处**：`library_bridge.rs:1104`（本轮目标）与 `main.rs:1484`（既有的 `perf_chunk_request_digest_cost`，其 `:1478-1479` 注释即"measured explicitly, never in the default suite … -- --ignored"）。**未误 ignore 其他测试。**
- `library_bridge.rs` 内 `#[cfg(test)]` 命中 **8 处**，行号恰为 R3 报告记录的 `295/316/392/403/422/430/440/737`；`#[test]` **12 处**（`742…1103`），与 R3 报告隐含集合一致 → 未新增 test seam。
- `#[ignore]` 之外的测试函数体与 R3 审阅时**逐行同构**：R3 引用 `:1288-1294`（`.expect` 链）现值 `:1289-1295`、`:1274-1275`（verdict 记录）现值 `:1275-1276`、`:1302-1310`（FAIL 分支）现值 `:1303-1311`、`:1247-1252`（`join`）现值 `:1248-1253`、`:1192-1194`/`:1219-1221`（`recv_timeout`）现值 `:1193-1195`/`:1220-1222`——**统一 +1 偏移**，与"在第 1104 行插入一行属性"完全吻合。
- 未引入 watchdog：grep `watchdog|kill_for_test` 在 `library_bridge.rs` 内仅命中 `:393` 既有定义，**测试体内无 `kill_for_test()` 调用**；生产 `round_trip`（`:263-324`，stdin 锁 / after-stdin hook / stdout `read_line` / observer）与 `Drop`（`:466-483`，`wait_timeout_or_kill(5s)`）内容与 R3 描述一致，且其行号（`< 1103`）**未发生任何偏移** → 生产面零改动的静态证据成立。
- 硬前置仍保留（`:1110-1112` `M2RC1_PYTHON` expect、`:1125-1129` 脚本存在断言、`:1140` 写 `verification/P04/**`）——这正是"显式运行时才可能失败/产生产物"的设计，加 `#[ignore]` 后不再污染默认套件。
- Handoff 侧口径登记完整：`antigravity-owner-revision-r2.handoff.md:28` 记录了 `#[ignore]` 与字符串原文（与代码逐字符一致），`:66` 的 AC2 行登记"不再进入默认 Cargo 测试套件；仅在 P02 批准隔离环境且具备 `M2RC1_PYTHON` 时通过明确 `-- --ignored` 有意运行"。

**R3-1 disposition：FIXED（静态）**。`#[ignore]` 从默认 Cargo 集合排除属 Rust 标准属性语义，本报告仅作**静态判断**，运行期未验证（`BLOCKED / NOT_RUN`）。

---

## 3. R3-4 核查：Handoff 超时/挂起边界表述

`antigravity-owner-revision-r2.handoff.md:50`（原 `:49`）现文本准确覆盖 R3-4 要求的全部三点：

1. "`recv_timeout` 仅限制 mpsc 通道等待" ✓
2. "子线程内的 `read_line` 会阻塞在 stdout 锁或读操作，导致主线程 `handle_alpha.join()` / `handle_beta.join()` 仍可能无界等待" ✓
3. "测试函数无法返回，通道实例无法被 drop，因此 `Drop` 机制的 5 秒 budget 根本不可达，并不能保护该挂起路径" ✓
4. "此为已知架构限制，不增加 watchdog 或产品代码范围" ✓

未发现任何地方把该问题说成"已修复"或"受 Drop 保护"：全 `verification/P04/**` 检索 `5 秒 budget|Drop 机制|Drop 保护|受 Drop`，仅剩 `:50` 这一处**否定性**正确表述、以及记录该修正本身的派发日志工件。代码侧未新增 watchdog/`kill_for_test`（§2），未扩大产品范围。`P04.md:78`（worktree，Codex 维护）也一致记录"`recv_timeout` 只覆盖 mpsc 等待，`read_line`/`join` 仍可能无界，本轮不加入 watchdog"。

**R3-4 disposition：FIXED（静态，仅文档事实描述）**。

---

## 4. 范围、状态与 Gate 核查

| 核查项 | 结果 |
|---|---|
| 修正是否只落在两条授权路径 | `library_bridge.rs` 仅 +1 行 `#[ignore]`（§2 行号锚点证据）；`antigravity-owner-revision-r2.handoff.md` 仅新增 `:28` 一条 + 就地更新 `:66`/`:50` 表述。未发现第三路径痕迹；**路径穷举本身 NOT_VERIFIED（无 git）**，与 Codex 声明的两路径一致 |
| P04 是否仍 `blocked` 且依赖 P22 | **是**：worktree `doc/tasks/P04.md:5-6,14` = `status: blocked`、`blocked_by: [P22]`；主仓 `G:/CODEX/New Manga/doc/tasks/P04.md:5,14` 相同；主仓 `doc/STATUS.md:5` = `P04=BLOCKED、blocked_by:[P22]`，且 `P22=BLOCKED 等待 P04 R4 Review 和写入窗口释放` |
| P02 Hard Build Barrier | **仍 `EFFECTIVE`**：handoff `:59`、R4 response §3 均声明 `EFFECTIVE`；`P02 Build Gate=BLOCKED`、`build=NOT_AUTHORIZED / NOT_RUN` |
| Cargo / sidecar / runtime | **仍 `BLOCKED / NOT_RUN`**：handoff §3 四行（AC1、AC2、AC3、集成后）分别为 `BLOCKED / NOT_RUN`、`BLOCKED / NOT_RUN`、`STATIC READY / NOT_RUN`、`BLOCKED / NOT_RUN`；worktree `P04.md:60-62` 三行皆 `BLOCKED / NOT_RUN`。**本轮我亦未运行任何命令**，无新运行证据 |
| R3 遗留 Codex 侧两项 | R3-2（R2 报告归档）**已解决**：`verification/P04/dsh-p04-owner-review-r2.stdout.md` 现存在；R3-3（状态落地）**主仓已解决**（见上）。worktree 内 `doc/STATUS.md:5` 仍为旧文本"P04 已进入 in_progress" → 见 P3-4 |

---

## 5. Findings 与 disposition

| ID | 级别 | 位置 | 事实 | Disposition |
|---|---|---|---|---|
| R3-1 | P2 | `library_bridge.rs:1103-1105` | 目标 AC3 负向复现器已加 `#[ignore = "…"]`，函数名/字符串准确，全 crate 无第二个新增 ignore，无新增 seam/watchdog，生产面零改动 | **FIXED**（静态） |
| R3-4 | P3 | `antigravity-owner-revision-r2.handoff.md:50` | 已准确区分 mpsc 等待 vs 无界 `read_line`/`join`，明确 `Drop` 5 秒 budget 不可达，未声称已修复，未加 watchdog | **FIXED**（静态） |
| R3-2 | P2 | `verification/P04/dsh-p04-owner-review-r2.stdout.md` | Codex 归档路径现已存在，引用不再是断链 | **CLOSED**（Codex 侧） |
| R3-3 | P2 | 主仓 `doc/tasks/P04.md` + `doc/STATUS.md` | 主仓已落地 `blocked` / `blocked_by:[P22]` | **CLOSED**（Codex 侧；worktree 快照陈旧见 P3-4） |
| P3-1 | P3 | `antigravity-owner-revision-r2.handoff.md` frontmatter / §1 | 该文件已被 R4 就地更新（含 `#[ignore]` 与 timeout 边界修正），但 `status: completed_revision_r2_static_only`、标题与 §1 表述仍只描述 R2 轮次，未标注 R4 修订；R4 授权允许（非必须）另写 `antigravity-owner-revision-r3.handoff.md` | **OPEN（建议性）**，Owner 或 Codex 可在集成前补一行 R4 修订说明/时间戳；不阻断 |
| P3-2 | P3 | 同上 `:115`（§5 转发指令块） | 残留"登记挂起抑制"措辞，与 `:50` 修正后的"挂起不可抑制、Drop 不可达"存在轻微张力；属历史指令副本，无明确错误声称 | **OPEN（建议性）**，建议随 R4 说明一并措辞对齐；不阻断 |
| P3-3 | P3 | `library_bridge.rs:1195` / `:1222` | `.expect("bounded wait timeout …")` 仍把所有 `recv_timeout` 失败（含 sender 断开）描述为 timeout（R3-4 附带的观察项）。R4 授权明确"其他测试不得改动"，故**未修属合规** | **OPEN（移交给 P22/后续修复 Task）**，非 R4 未完成项 |
| P3-4 | P3 | worktree `doc/STATUS.md:5`；主仓 `doc/tasks/P04.md:84` | worktree 内 STATUS 仍写"P04 已进入 in_progress"，与同 worktree `P04.md` frontmatter `blocked` 并存；主仓 P04 仍写 R3 `IN_PROGRESS / final report pending`。Owner 无权改共享状态，Codex 声明限定"主仓已落地" | **OPEN（Codex 侧）**，建议 P22 释放/集成前同步 worktree 与主仓元数据；不影响 Owner R4 判定 |

无 P0/P1/P2 未解决项；未发现伪造运行证据、把 `BLOCKED / NOT_RUN` 写成 `PASS`、或生产/IPC/Schema/依赖/capabilities/Python Core/frontend/共享规划文档改动。

---

## 6. 覆盖、未覆盖与剩余风险

- **已覆盖（直读）**：`library_bridge.rs` 生产 `round_trip` `:263-324`、test seam `:392-448`、`Drop` `:466-483`、测试区 `:1082-1312` 全文；`main.rs` AC1 测试 `:1163-1193` 与既有 ignore 先例 `:1477-1485`；`antigravity-owner-revision-r2.handoff.md` 全文；worktree `doc/tasks/P04.md`、`doc/STATUS.md`；主仓 `doc/tasks/P04.md`、`doc/STATUS.md`；`dsh-p04-owner-review-r3.stdout.md`；R4 派发 prompt/response；`deterministic_concurrent_sidecar.py` 关键符号检索；`verification/P04/**` 相关文本检索。
- **未覆盖 / 不可验证**：① `tree=eb0cc832…`、工作树与 `faea1a2c` 的一致性、差异路径穷举、`git diff --check` 全部 `NOT_VERIFIED`（无 Git 执行能力，无审批通道）；② 未编译——`#[ignore]` 与 `recv_timeout` API 用法仅静态推理；③ 运行期行为、sidecar provenance、`behavior` 实际取值未运行；④ 若在 `:1103` 之前存在"等行数内容替换"，本方法无法检测（但 R3 引用锚点与 `#[cfg(test)]`/`#[test]` 计数均吻合，风险低）。
- **剩余风险**：AC2 归属错配本体仍未修复（由 P22 承接）；`static_expected_behavior: "FAIL"` 为硬编码静态期望，修复集成后会陈旧（R3 §6 已记）；挂起面仍存在（R3-4 已如实记录，非本轮授权范围）。

---

## 7. 判定

**decision = APPROVED**

**P0 / P1 / P2 / P3 未解决数 = 0 / 0 / 0 / 4**（4 项均为建议性 P3，见 §5；其中 2 项归属 Codex，1 项移交 P22，2 项为 Owner/Codex 可选措辞改进）。

**限定语义（必须遵守）**：本 `APPROVED` 仅针对 **`faea1a2c` 对 R3-1 与 R3-4 的修正范围**（静态）。它**不**代表 P04 完成、**不**代表 AC1/AC2 通过、**不**代表可解除 Build Barrier 或可集成：P04 整体仍 `blocked`、`blocked_by: [P22]`，P02 Hard Build Barrier 仍 `EFFECTIVE`，AC1/AC2 Cargo 与集成后验证仍 `BLOCKED / NOT_RUN`。

**推荐下一步**（基于当前仓库状态）：
1. **Codex**：把本 R4 报告归档为 `verification/P04/dsh-p04-owner-review-r4.stdout.md`，并把 P04 交付/Review 记录（worktree `doc/tasks/P04.md`）更新为 R4 `APPROVED`（含 §6 限制），同时处理 P3-4 的 worktree/主仓元数据同步。
2. **Codex**：按既有计划推进 P22（唯一修复通道并发错配），其输入证据即本轮 AC3 负向复现器与 R3 静态推导；P22 完成后恢复 P04，补入/启用回归测试并在 P02 批准环境中以 `-- --ignored` 复跑 AC2。
3. **Owner（Antigravity）**：无必须动作；如需闭环 P3-1/P3-2，可在同一 handoff 内补 R4 修订说明并对齐 §5 措辞（不新增 watchdog、不改生产代码）。
4. 纪律不变：不得运行 Cargo/Tauri/sidecar/build/Sandbox/宿主写权限探测，不得把 `BLOCKED / NOT_RUN` 写成 `PASS`。

（本报告未创建或修改任何文件；本轮宿主日志 `verification/P04/codex-dsh-owner-r4-review.*` 由 Codex 派发通道生成，非我写入。）
