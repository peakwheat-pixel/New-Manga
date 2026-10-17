---
id: SEC-FIX-PATH-ECHO-1
title: 修复设置命令回显绝对路径（settings_get / settings_update_section）
kind: bugfix
governance_version: 2
status: in_review
approval: coordinator_release_20261017_from_P19_AC3_1_finding
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [P15-HOST-2, P15-CORE-1C]
base_commit: f4bbc59c9e5cf9864ab0ab0e97277b826b9a0a5f
branch: codex/SEC-FIX-PATH-ECHO-1
worktree: G:/CODEX/New Manga.workspace/worktrees/SEC-FIX-PATH-ECHO-1
integration_commit: null
delivery_head: c52ce4695802a06fde8f4e08f2d96a8cecfd855d
canonical_evidence_status: in_progress
resource_closeout_status: accounted_with_preserved_residuals
evidence_dir: verification/SEC-FIX-PATH-ECHO-1
---

# SEC-FIX-PATH-ECHO-1：设置命令回显绝对路径（P1 安全）

## 来源（P19-AC3-1 的真实发现，已复现）
`verification/P19-AC3-1/repro_settings_path_roundtrip.py` + `raw/settings-path-roundtrip.*`：
```
REPRO settings.update_section({section:'ocr', values:{path, api_secret}})
WRITE_RESPONSE={"result":{"settings":{"ocr":{...
READ_RESPONSE={... {"ocr":{"path":"C...
OBSERVED path_value_returned=true  synthetic_secret_returned=false  file_io_attempted=false
REPRO_RESULT=PASS (the forbidden OS-path echo was reproduced; secret key was dropped)
```
→ `settings_get` 与 `settings_update_section` **原样返回 Core 通用 settings projection**，其中 `ocr.path` 含**绝对 OS 路径**。用户已多次强调"永不暴露路径"，且 P19 的 AC3 要求四处均不得出现路径。

## Acceptance Criteria
- [x] **AC1**：Core 响应投影对路径型值脱敏，不回显绝对路径、盘符、UNC 或用户目录片段。
- [x] **AC2**：请求校验、写入验证和协议版本提前拒绝的错误响应均不回显路径片段；路径型 `request_id` 与验证消息封闭投影。
- [x] **AC3 反例测试**：合成绝对路径覆盖 `settings_get` 与 `settings_update_section`、13 个 section、OS 路径形式、路径字段、section key、request ID、非法协议版本和错误。
- [x] **AC4 不回归**：Core、Rust source、packaged、前端均与本 worktree 基线不回归；前端 Task 记录 278，但基线实测为 285，修复前后均 285。
- [ ] **AC5 交付**：实现 commit 与 Handoff 已固定；Canonical Evidence pins 将针对最终 delivery head 更新，完成前不交 Reviewer。
- [x] **AC6**：等价复现脚本修复前后运行，修复后 `path_value_returned=false`。

## 允许 / 禁止
- 允许：`src/**`（Core 投影修复为主）、必要处 `apps/desktop/src-tauri/**`、`tests/**`、本 Task、Handoff、`verification/SEC-FIX-PATH-ECHO-1/**`。
- 禁止：改契约（若需改 projection 定义 → **停下上报**）；Schema/迁移/依赖；改 STATUS/PLAN；碰用户 19 项 dirty；**不得**用"前端不再显示"掩盖（必须在 **Core/host 投影层**修复）。

## 依赖、风险与阻塞
- 前置：P15-HOST-2、P15-CORE-1C。**被阻塞方**：P19 的 AC3。
- 风险：涉及设置投影语义 → 需保持既有 `settings_update_section` 写入能力不变。

## 交付与运行记录
- 2026-10-17 Coordinator 释放（dsh, epoch 6），依据 P19-AC3-1 复现。
- 2026-10-17 开始实施：本轮用户指定 Owner=Codex、base=`f4bbc59c9e5cf9864ab0ab0e97277b826b9a0a5f`；实际分支为 `codex/SEC-FIX-PATH-ECHO-1`。
- 基线事实差异：本 worktree 的 `doc/STATUS.md` 当前仍指向 `ARCH-DOC-REBASELINE`，而 Plan 将本 Task 列为 READY；按本 Task 禁令不改 STATUS/PLAN，记录供 Coordinator 核对。用户本轮明确指定本 Task Owner 与 worktree，故按该指令实施。
- 复现源路径检查：只读主仓 `verification/P19-AC3-1/repro_settings_path_roundtrip.py` 与 `raw/` 在当前主仓 checkout 不存在；Task 的复现记录仍载明 `path_value_returned=true`。AC6 已由同基线等价脚本前后复跑并留档。
- 实现提交：`cd78a333577365466726e1f32d3ef95be22d7324`（Core 输出投影）、`5b9f6c422df5cdb601522c91cb447702a2e78efc`（保留非字符串路径键值）及 `c52ce4695802a06fde8f4e08f2d96a8cecfd855d`（协议提前拒绝时也投影路径型 request ID 和错误消息）。`delivery_head` 使用最后提交的完整 `git rev-parse HEAD` 值；Task/Handoff 之后续文档提交追加。
- 修复位置：`src/bootstrap/core_service.py:340-379` 新增 Core settings 输出投影；`handle_settings_get`、`handle_settings_update_section` 调用投影（`:1250-1309`）；通用 dispatcher 在协议校验前脱敏 settings 命令的 request ID（`:2644-2655`），协议错误及 settings IPC 错误/成功 envelope 使用安全 ID（`:2726-2743`、`:3014-3061`），settings 校验消息也走脱敏投影（`:3030`）。Tauri `main.rs:519-550` 与 `library_bridge.rs:1665-1685` 是 Core 透传，未改。
- 反例测试：`tests/core/test_core_service_settings.py::test_settings_commands_redact_paths_in_every_section`。
- 复现及套件原始输出：`verification/SEC-FIX-PATH-ECHO-1/{baseline,repro-after.log,*-tests.log,*-pytest.log,*-vitest.log}`；汇总见 `verification/SEC-FIX-PATH-ECHO-1/ac-results.md`。
- Handoff：`doc/handoffs/SEC-FIX-PATH-ECHO-1-c52ce46.md`。
- 原始产物中保留四个由 Rust source 测试生成的 `verification/P04/diagnostic_p22_*.jsonl` 与 Task 临时目录，均未纳入提交。资源状态为 `accounted_with_preserved_residuals`。

## Canonical Evidence

Evidence pins are being regenerated against the final delivery commit and Handoff commit. Keep this Task in in_review and do not route it to the Reviewer until the final pin table is complete.
