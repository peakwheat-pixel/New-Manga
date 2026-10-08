# P03 formal non-author review request — R3

请作为 P03 的非作者正式 Reviewer，对下列固定 Git 范围独立审查。只读，不修改、格式化或生成任何仓库文件，不把未提交文件计入 reviewed diff。

## 固定身份与范围

- Repository: `G:/CODEX/New Manga`
- Review worktree: `G:/CODEX/New Manga.worktrees/P03-review-prep-85482c5b`
- Task: `doc/tasks/P03.md`; status=`in_review`
- Author/Owner: Antigravity
- Reviewer: DeepSeek Harness（必须非作者）
- Integrator: Codex
- Fixed `base_commit`: `31abde9bf4b73aea2851931dcd48faa0f750b318`
- Fixed `reviewed_head`: `423ea5f196e6276f007bd3f96e381fa893985eb9`
- Review exactly `base..reviewed_head`; do not substitute current refs, root `main`, old DSH reports, or untracked files.

请先核对 `git rev-parse HEAD`、branch/worktree/common-dir、`git diff --name-only base..head` 和 `git diff --check base..head`（若沙箱不能执行，明确写 `NOT_RUN` 并说明；不要声称已运行）。对本次 exact head 的 Codex trace=`verification/P03-PACKAGED-SFX-ENTRY/integration/build-logs/17-final-review-head-scope-diff-check.log`（122 paths、out-of-scope=0、diff-check EXIT=0），两份只读 normalization trace=`build-logs/18-final-review-head-normalization.log`；历史 checkpoint traces 为 `build-logs/11–16`。准确区分 DSH 自行运行与复核 Codex 保存的日志。未提交日志仅作验证证据，不纳入固定 Git diff。

## 必须核阅

读取 `AGENTS.md`、`doc/09_COLLABORATION.md` §6、`doc/templates/REVIEW.md`、`doc/tasks/P03.md`、对应 RESUME/Handoff、Task 范围内全部代码/测试/验证证据。审查两个必需视角：**Architecture** 和 **Verification**。不要求 Standards 视角；Spec 按 AC1–AC5 逐项对照。

重点核实：

1. `packaging/m2ac5/run_clean_start_e2e.py` 和 `tests/packaging/test_packaged_fifth_sfx_entry.py` 的第五入口断言、冻结/错误/候选数/权重 pin/path 判别及 `install_dir` 缺省 fail-closed 修复；调用者和回归用例是否与实现一致。
2. fixed diff 是否只触及 Task allowed paths 与明确由 Codex 维护的六个导航治理文件（见 Task）；`src/**`、`apps/**`、contracts、Schema、运行时依赖、build spec/script 是否零差量。
3. R-001–R-006 和独立 Codex finding C-001 的 disposition 是否证据充分、准确；特别检查 R-003 修复后 fresh sidecar、NSIS installer 与 Gate 的 source/hash 绑定，而非仅凭摘要接受。
4. AC1–AC4 的真实证据以及 AC5 仍需 Codex 完成集成检查的边界。核对 Gate 的 28/28、exit、installer SHA、S1/S2 结构化结果和零触碰证据；40 项定向测试、16 项 snapshot oracle、构建 trace、raw/canonical 日志双向可逆证据。
5. 输出/文档有无新 P0–P3 问题、错误的 PASS/DONE 声明、遗漏的验收或数据保护风险。

## 已登记的历史 Review findings（请独立核实，不预设关闭）

- R-001 P2：Owner 与新 Codex installer 指纹已分列，初始 `d21e89b6…` 标为被替代；Codex installer=`2de124f387bfaf1d0d01b1b0279ad319cd453850d223efa9620b0103ce88a814`。
- R-002 P2：提交的 `build-logs/11-fixed-head-diff-check.log` 是 candidate `2d114480…` 的完整 trace；对本次 exact `fb5782c5…` 的复验在 `build-logs/12-final-fixed-head-scope-diff-check.log`，请检查两者绑定与范围。
- R-003 P2：`db2c1e93…` 使 success predicate 无论调用者是否提供 `install_dir` 都要求证明权重位于安装目录，40 项定向测试包含缺省值的有效 payload 负例。
- R-004 P3：Codex 标记 `deferred/non-blocking`；AC2 有 probe JSON SHA pin、bundle 来源、安装目录内路径和固定 installer，但 Task 未要求独立重哈希 ONNX。请判断此 deferred 是否合理/应保留风险。
- R-005 P3：Handoff token count 已从 6,704 修为 6,702。
- R-006 P3：build logs 记录各阶段 HEAD/clean status；NSIS 构建绑定 `a3aaf229…`。
- C-001 P2：P03 RESUME 的 Handoff 相对链接已修正为 `../../doc/handoffs/P03-PACKAGED-SFX-ENTRY-140a6686-r3.md`。
- C-002 P2 (Codex independent review) — fixed in commit `41be59e9d4e3c55ac87cf0868f89077b4d03978e`: success-negative cases now have a valid install directory and internal weights path, assert that the unmodified baseline passes, and then apply one negative condition; the separate omitted-install_dir fail-closed assertion remains. The targeted suite passed 40/40.
- C-003 P3 — fixed: installer table states the same-installer Gate completed 28/28 PASS; current RESUME names the current task state.

Codex host 验证证据（Reviewer 不应将其写成 DSH 自己运行）：

- Python 3.14.6 定向 pytest：40 passed，0 skipped，EXIT=0；`integration/build-logs/01-targeted-tests.log`。
- C-002 sensitivity repair rerun: same 40 tests passed, 0 skipped, EXIT=0; `integration/build-logs/14-targeted-regression-tests.log`.
- Runner snapshot oracle：16 actual-predicate cases PASS，EXIT=0；`integration/build-logs/02-snapshot-check.log`。
- npm install/build、fresh Sidecar、Tauri/NSIS build：各 EXIT=0；`integration/build-logs/03–06`。
- Installer SHA=`2de124f3…`，size=579,537,342；manifest 在 Gate 前固定。
- 同一 installer 上完整 packaged Gate：28/28 PASS、GATE PASS、EXIT=0；`integration/run-2de124f3-py314/`。安装目录和 host APPDATA 零变更，用户源文件字节未变，五个 sidecar 零存活。
- raw auxiliary logs 原始字节保存在 ZIP；规范化/逆变换 SHA 验证 6/6 PASS；`build-logs/07–08`。
- 当前 fixed-head range `31abde9…423ea5f1…`: 122 paths、out-of-scope=0、`git diff --check` EXIT=0；`build-logs/17`。两份只读 normalization verifier EXIT=0；`build-logs/18`。

## 报告要求

请返回可归档的中文 Review，头部包括 `task_id=P03`、`reviewer=DeepSeek Harness`、`author=Antigravity`、精确 base/head，以及 `decision=approved` 或 `changes_requested`。分别给出 Architecture 与 Verification 判定；按 ID/等级/文件行/触发影响/最小建议/状态列 findings；AC1–AC5 逐项说明；列明 P0/P1 unresolved 数、实际执行命令和 `NOT_RUN` 项、环境限制与残余风险。只有你独立确认无未解决 P0/P1 且验收边界准确时才可批准；不要替 Codex 标记 Task `done`，也不要把本 Review 当成 Codex integration Gate。
