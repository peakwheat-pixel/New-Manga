## P04 提案只读范围/验收审查（static only）

**审查对象**：`codex/P04-scope-freeze` @ `018023e8129ee9e34f441e39b30ab0c22786eccc`，base `88579622d85ff6d0dfd509c6f21931bd91d0881b`。
HEAD 一致性已通过只读 Git 元数据确认：`.git/worktrees/P04-scope-freeze/HEAD` → `refs/heads/codex/P04-scope-freeze` → `018023e8…`；`.git/worktrees/P04-scope-freeze/logs/HEAD:3` 显示 `88579622 → 018023e8`，消息为 `docs: define P04 validation scope`。

---

# Verdict: changes requested

提案主体方向正确：`status: proposed` 如实、Owner/Reviewer 分离清楚、无越权授权、无"未运行写成 PASS"。但存在 **1 个 P1（测试命令前置缺失，静态可证）** 与 **3 个 P2（AC1 判别力、AC3 终态/循环、checkpoint 恢复信息滞后）**，需在释放前做最小修订。

**P0/P1/P2/P3 = 0/1/3/6**

---

## P1

### P1-1：AC1/AC2 计划 `cargo test` 的编译前置（受信 sidecar bundle 及其 provenance/Gate）未登记，且其生成途径落在 P02 Hard Build Barrier 禁止项内

- 证据：
  - `apps/desktop/src-tauri/build.rs:18-29`：build script 在 `tauri_build::try_build` 之前 fail-closed 检查 `target/core-sidecar/core-sidecar`，缺失即 `panic!`（missing sidecar bundle）。
  - `apps/desktop/src-tauri/target` 目录在本 worktree **不存在**（`glob` 对 `apps/desktop/src-tauri/target` 返回 OS error 2），即任何 `cargo test` 都会先撞该 panic，而不是运行 AC1/AC2 测试。
  - 唯一生成途径是 `packaging/m2ac5/build_sidecar.ps1`（build.rs:25 自述），属 sidecar build；P02 屏障明文禁止 sidecar build（`verification/P02/codex-checkpoint-after-r6-dsh-review.md:12`）。
  - `verification/P02/codex-scratch-build-plan.md:9` 明确 root 的 `src-tauri/target/core-sidecar` 是忽略的既有输出、provenance 未核实、**不得复制/覆盖/作为构建输入**。
  - `doc/tasks/P04.md:58-59` 前提只写 "P02 Build Gate=`PASS`；测试范围与运行环境经 Codex 确认 / 确定性 test sidecar"，未登记该编译前置与其来源 Gate。
- 影响：P02 Build Gate 一旦 PASS，Owner 按 P04 命令执行会先得到 build.rs `panic`（可能被误读为"测试失败"或"环境问题"）；若 Owner 为消除 panic 自行运行 `build_sidecar.ps1`，则直接触碰受禁的 sidecar build，或引入未核实的构建输入。P04 的"确定性诊断"因此在当前授权模型下不可执行。
- 最小修正：在 `doc/tasks/P04.md:58-60` 前提栏与"依赖、风险与阻塞"补一行硬前置：`cargo` 编译要求**已由 Codex 在受信隔离环境产出并绑定 commit/Gate 的 core-sidecar bundle**，并写明 `build_sidecar.ps1`/sidecar build 不得由本 Task Owner 运行；把该 Gate 证据路径（P02 scratch build 记录）作为引用。

---

## P2

### P2-1：AC1 未要求任何"等长错替换判别力"证据，实现者可用自指断言"形式上满足"

- 位置：`doc/tasks/P04.md:32`。
- 事实：AC1 首句（精确断言恰为 `list_chapters`、`list_chapter_pages`、无重复）字面上确实能覆盖等长替换；但第二句"确认两项仍在生产面且不出现在 probe/AC1 面"可被写成**引用同一常量**的循环断言（`for c in PAGE_NAV_PRODUCTION_ONLY_COMMANDS { assert!(!probe.contains(c)) }`），等长替换后仍全绿。我已静态复现现有测试的真实漏检路径：把常量替换为其他 production-only 族成员（如 `list_regions` / `rerender_page`）时，`main.rs:1050-1089`、`1094-1132`、`1134-1161` 的长度与成员断言全部通过，而 `list_chapters`/`list_chapter_pages` 会泄漏进 probe/ac1 面。
- 影响：AC1 可能"看起来满足"却未带判别力，重演仓库既有教训（测试声称的行为必须带判别断言）。
- 最小修正：AC1 增加一句证据要求——交付时在任务/评审记录中登记一次**临时等长错替换使新测试 FAIL 的反推证据**（该替换不入库），或在 AC 中显式要求 `assert_eq!` 精确成员断言作为最低实现形态。

### P2-2：AC3 未规定"复现缺陷时"测试产物与 P04 终态的处置，存在与 AC4/集成 Gate 互锁的循环风险

- 位置：`doc/tasks/P04.md:33-35`、`:51`。
- 事实：AC2 以"归属正确"为断言时，若复现错配，该测试必然 FAIL；AC4 又要求"测试 Gate 满足后集成"。AC3 只说"保留证据 + 由 Codex 拆独立修复 Task"，未说明：复现测试是 `#[ignore]` 后随交付入库、还是只留 `verification/P04/**` 证据、还是 P04 转 BLOCKED 等修复后重跑。AC3 同时禁止"降低 AC"，因此删除断言或改期望值也缺授权。
- 影响：要么交付出一个失败测试无法通过 Gate，要么为通过 Gate 而弱化断言（与 AC3 冲突），修复 Task 与 P04 之间可能出现循环卡死；`##[ignore]` 之外的选项都缺明文授权。
- 最小修正：在 AC3 明示三选一处置与 P04 终态（建议：复现证据仅落 `verification/P04/**`；复现测试以 `#[ignore]` + 原因注释入库并登记为"由修复 Task 解除"；修复 Task 完成前 P04 保持 `blocked`/`in_review` 而非 `done`），并声明该处置不需要"降低 AC"。

### P2-3：checkpoint 相对 reviewed head 已过时，却被 Task 表述为"当前"checkpoint，恢复信息与事实冲突

- 位置：`doc/tasks/P04.md:75`；`verification/P04/proposal-checkpoint-20261010.md:7,21,27-28`。
- 事实：checkpoint `:7` 的 "last verified HEAD=`88579622`"、`:21` "Documentation/route checks: pending"、`:27-28` "Next exact step: … commit only the P04 proposal files on this scope branch, then … fast-forward integration" —— 而 reflog 显示该 commit 已于 `018023e8` 完成，且 `doc/STATUS.md:3`、`doc/00_INDEX.md:3` 都已把 Task 与 checkpoint 表述为"已建立"。checkpoint 未记录 `018023e8` 的 HEAD/tree、变更路径集、route/link/diff 结果。
- 影响：按 P04.md:75 从该 checkpoint 恢复的人会重复执行已完成的提交步骤，并把 `018023e8` 的文档路由校验状态误读为"未做"或"已做"；这是本审查重点 5 的直接命中。
- 最小修正：追加一份绑定 `018023e8` 的 checkpoint（或就地追加节），记录 reviewed HEAD、变更路径集、`git diff --check` / route validator / Markdown link 结果，并把 `:27-28` 的 Next exact step 更新为"等待 P1-1 前置满足"；同时明确原 checkpoint 为提案前历史快照。

---

## P3

- **P3-1（术语歧义）** `doc/tasks/P04.md:32` 的"probe/AC1 面"指 M2-AC1 test-mode 面（`command_allowlist(false,true)`，`main.rs:94`），与 P04 自身的"AC1"编号同名，易误读。建议写作"probe/M2-AC1 面"。
- **P3-2（记录落点含糊）** `doc/tasks/P04.md:33` 要求"记录请求/响应的 protocol、version、request_id 字段"，但 `library_bridge.rs:263-310` 的 `round_trip` 只返回 `decode_response` 后的 `result`，这些字段被丢弃，只能经测试 sidecar 侧旁录。建议写明证据落点（`verification/P04/**`）以及"记录 ≠ PASS、不断言 version 语义（依 `M2-C1_TYPED_IPC_CONTRACT.md:64,111` 的 PROPOSAL 状态）"。
- **P3-3（工作区产物未区分）** `verification/P04/` 下存在 `dsh-availability-probe.*`、`dsh-proposal-review.prompt.md`、`dsh-proposal-review.stderr.log`，均为 reviewed head 之后由派发链路写入的工作区文件（`dsh-proposal-review.stderr.log` 含审查推理文本，属实时 stderr 镜像，不应作为验证证据签入）。checkpoint 未登记也未区分"已提交/未提交"。建议在 checkpoint 或 Task 中登记派发产物清单与"不入库"口径。
- **P3-4（命令未显式固定 target）** `Cargo.toml:6-8` 当前只有单个 bin target `m2rc1-desktop`，故 `doc/tasks/P04.md:58-59` 的 `cargo test <filter>` 有效；但未写 `--bin m2rc1-desktop`，未来新增 lib/bin target 时 filter 可能命中歧义。建议显式加 `--bin`。
- **P3-5（cfg(test) 限定）** `doc/tasks/P04.md:40` 的"确定性测试同步设施"未显式绑定 `#[cfg(test)]`。建议改写为"仅 `#[cfg(test)]` 范围内的测试/helper/同步设施；生产代码零改动"，避免被解释为可在非 cfg(test) 区加测试原语。
- **P3-6（机器可读阻塞缺失）** `doc/tasks/P04.md:12-13` 的 `depends_on` 只有已 done 的 `M2-PAGE-NAV-PROJECTION-1`，硬执行前提（P02 Build Gate）仅在正文 `:67`。Plan `:75` 有条件文字但无结构字段，依赖图/validator 层看不到该阻塞。建议在 front-matter 增 `blocked_by`（或等效字段）并在 Plan 表中单列"启动条件"，与 `:67` 保持一致。

---

## 已核实为无问题的点

- **proposed 与状态一致**：`doc/tasks/P04.md:5` `status: proposed`，`owner/reviewer: null`；`REBASELINE_PLAN.md:68,75`、`STATUS.md:3`、`00_INDEX.md:3` 三处口径一致（P04=proposed / 未释放，P02 唯一 Active）。依赖 `M2-PAGE-NAV-PROJECTION-1` 确为 `status: done`（`M2-PAGE-NAV-PROJECTION-1.md:5`，integration=`657af2e3`）。
- **Owner/Reviewer 分离**：建议 Owner=Antigravity、Reviewer=DeepSeek Harness、Integrator=Codex（`P04.md:7-11,45,35`），未自审、无 Qoder 恢复；与 `AGENTS.md` 角色一致。
- **无越权授权**：`P04.md:39-43` 仅测试代码 + `verification/P04/**` + 本 Task 文档；未授权改契约/协议/生产逻辑/依赖/ACL。`:49-52` 与 P02 屏障（禁止 Cargo/Tauri/sidecar/frontend build、Sandbox Feature 查询/启用、scratch clone）逐项自洽。
- **无"未运行写成 PASS"**：`P04.md:58-60` 实测列、`:62` 与 checkpoint `:19-23` 均如实 `BLOCKED / NOT_RUN`、Feature=`UNKNOWN`。
- **链接无坏链**：`P04.md:24,28,75` 的三个相对链接、`STATUS.md:3` / `00_INDEX.md:3` 的 P04 链接、checkpoint `:30` 引用的 `verification/P02/codex-scratch-build-preflight-r1.md` 均存在。

---

## 审查限制（必须随本结论保留）

- 未运行任何构建、测试、Cargo/Tauri、Sandbox、Windows Sandbox Feature 查询/启用、scratch clone，也未创建/派发任何 Task。
- 只读 `git` 命令因本机 DSH 沙箱 ACL 失败（`SetNamedSecurityInfoW failed (Win32 5)`）无法执行；HEAD/base 由 `.git` worktree 元数据与 reflog 只读确认，因此**无法逐文件核对 `018023e8` 的确切变更路径集**。
- 本文档**不是** P04 实现 Review，也**不是**产品/发布 Gate；它只是提案的静态范围/验收审查。

## 推荐下一步

建议由 Codex（唯一能改共享状态文件的角色）在**不释放 P04、不派发实施、不运行 Cargo**的前提下执行最小修订：先补 `doc/tasks/P04.md:58-60` 的 sidecar bundle 前置（P1-1），再处置 AC1 判别力证据（P2-1）与 AC3 终态（P2-2），最后追加一份绑定 `018023e8` 的 checkpoint 并刷新 `P04.md:75`（P2-3）；随后固定新 head，重新发起一次同口径只读审查。除上述文档修订外，**无需下一步操作**。
