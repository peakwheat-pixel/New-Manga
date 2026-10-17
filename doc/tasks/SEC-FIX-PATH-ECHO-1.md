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
delivery_head: 5b9f6c422df5cdb601522c91cb447702a2e78efc
canonical_evidence_status: complete
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
- [x] **AC2**：请求校验错误、写入验证错误和路径型 `request_id` 均不回显路径片段。
- [x] **AC3 反例测试**：合成绝对路径覆盖 `settings_get` 与 `settings_update_section`、13 个 section、OS 路径形式、路径字段、section key、request ID 和错误。
- [x] **AC4 不回归**：Core、Rust source、packaged、前端均与本 worktree 基线不回归；前端 Task 记录 278，但基线实测为 285，修复前后均 285。
- [x] **AC5 交付**：实现 commits 与 Handoff 已固定；本 Task 为 `in_review`，Canonical Evidence `complete`，按 BL-15/16/17/18/19 记录。
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
- 实现提交：`cd78a333577365466726e1f32d3ef95be22d7324`（Core 投影与初始证据）及 `5b9f6c422df5cdb601522c91cb447702a2e78efc`（路径字段的非字符串值保持原样；更新代码、测试和最终测试日志）。`delivery_head` 使用后者完整 `git rev-parse HEAD` 值；Task/Handoff 之后续文档提交追加。
- 修复位置：`src/bootstrap/core_service.py:340-379` 新增 Core settings 输出投影；`handle_settings_get`、`handle_settings_update_section` 调用投影（`:1250-1309`），settings IPC envelope 的 `request_id` 经同一投影（`:3008-3055`）。Tauri `main.rs:519-550` 与 `library_bridge.rs:1665-1685` 是 Core 透传，未改。
- 反例测试：`tests/core/test_core_service_settings.py::test_settings_commands_redact_paths_in_every_section`。
- 复现及套件原始输出：`verification/SEC-FIX-PATH-ECHO-1/{baseline,repro-after.log,*-tests.log,*-pytest.log,*-vitest.log}`；汇总见 `verification/SEC-FIX-PATH-ECHO-1/ac-results.md`。
- Handoff：`doc/handoffs/SEC-FIX-PATH-ECHO-1-5b9f6c4.md`。
- 原始产物中保留三个由 Rust source 测试生成的 `verification/P04/diagnostic_p22_*.jsonl` 与 Task 临时目录，均未纳入提交。资源状态为 `accounted_with_preserved_residuals`。

## Canonical Evidence

以下 `sha256` 按当前 worktree 的磁盘字节计算；前 18 条均由 `git cat-file -e 5b9f6c422df5cdb601522c91cb447702a2e78efc:<path>` 验证包含性，第 19 条使用 Handoff 文档提交验证。class 仅使用 `CANONICAL`。没有声称其他 checkout 的磁盘字节已独立复核。

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| SEC-FIX-PATH-ECHO-1-E1 | AC1/AC2 Core 投影实现 | `src/bootstrap/core_service.py` | `5b9f6c422df5cdb601522c91cb447702a2e78efc` | `18b3ce6c2eeca10d0a08dceeece511f815a3a1ee66d129f4c94b39f1569f3345` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E2 | AC3 反例测试 | `tests/core/test_core_service_settings.py` | `5b9f6c422df5cdb601522c91cb447702a2e78efc` | `fc86a7377c4a1850ad849dfb2a9bd0d1eaa9d302a224c66493d2d8d4fec1ddda` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E3 | AC6 等价复现脚本 | `verification/SEC-FIX-PATH-ECHO-1/repro_settings_path_projection.py` | `5b9f6c422df5cdb601522c91cb447702a2e78efc` | `03f20d4cbc42371d3a05533103a965a72c2a9a76a95a76ef4114a46a0592e879` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E4 | AC6 基线复现输出 | `verification/SEC-FIX-PATH-ECHO-1/baseline/repro-before.log` | `5b9f6c422df5cdb601522c91cb447702a2e78efc` | `f729bd703e6be159fb4fb3cd5dcdf6360199d906929dc1816270d4f5595cabc2` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E5 | AC6 修复后复现输出 | `verification/SEC-FIX-PATH-ECHO-1/repro-after.log` | `5b9f6c422df5cdb601522c91cb447702a2e78efc` | `7d0905878ac2db075a0d8db2efa6618c8a09bcbc5a786c86d001d275cab67fcc` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E6 | AC4 Core 基线 | `verification/SEC-FIX-PATH-ECHO-1/baseline/core-pytest.log` | `5b9f6c422df5cdb601522c91cb447702a2e78efc` | `fddbf18177ba52512bec53ede16c68d8f98e0c567665da0c77641d9d3337a4b6` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E7 | AC4 Core 交付 | `verification/SEC-FIX-PATH-ECHO-1/core-pytest.log` | `5b9f6c422df5cdb601522c91cb447702a2e78efc` | `060440804b2417ccebbab0b97c8852603ec94137a608f1c9a0686acb3dcfec17` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E8 | AC3 修复前反例输出 | `verification/SEC-FIX-PATH-ECHO-1/baseline/counterexample-before.log` | `5b9f6c422df5cdb601522c91cb447702a2e78efc` | `80f2cde14ab15db4a7d8934fc1e8241ba9dcc04253a9f1827b63075976dc3421` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E9 | AC3 修复后反例输出 | `verification/SEC-FIX-PATH-ECHO-1/counterexample.log` | `5b9f6c422df5cdb601522c91cb447702a2e78efc` | `6742cffb27700c7e050653697b6839e20ad77ebc73e21a3b0b3254c4cb5db498` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E10 | AC4 Rust source 基线 | `verification/SEC-FIX-PATH-ECHO-1/baseline/rust-source.log` | `5b9f6c422df5cdb601522c91cb447702a2e78efc` | `5554938dfc92fd3d2e156be2f8c1f37bb951f40411d92a1e0400d6bdfb4d835e` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E11 | AC4 Rust source 交付 | `verification/SEC-FIX-PATH-ECHO-1/rust-source-tests.log` | `5b9f6c422df5cdb601522c91cb447702a2e78efc` | `8ac9bfb595182337f1f8a83e1a8ca89738397fad063fa97a0c37146002d76658` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E12 | AC4 packaged 基线 | `verification/SEC-FIX-PATH-ECHO-1/baseline/rust-packaged.log` | `5b9f6c422df5cdb601522c91cb447702a2e78efc` | `b2cf7aefa2f6ab0725450e9b9384e1fb553dee27c0fee3ab4ae29153c078a5bd` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E13 | AC4 packaged 交付 | `verification/SEC-FIX-PATH-ECHO-1/rust-packaged-tests.log` | `5b9f6c422df5cdb601522c91cb447702a2e78efc` | `82b16fe868c3ed68fb6527e8c02e0abed2221d75581dd4cdcb2480eb045e395b` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E14 | AC4 前端基线 | `verification/SEC-FIX-PATH-ECHO-1/baseline/frontend-vitest.log` | `5b9f6c422df5cdb601522c91cb447702a2e78efc` | `a71a4e888292c9018b2c5ba3c29e38c7fbeb42db7d3cee5f06fa731c39fe2eb0` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E15 | AC4 前端交付 | `verification/SEC-FIX-PATH-ECHO-1/frontend-vitest.log` | `5b9f6c422df5cdb601522c91cb447702a2e78efc` | `c14c79165e77fa63cf25924f04d887a864590fb6b0e8ef871fd22b5736d929a7` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E16 | AC1–AC6 汇总 | `verification/SEC-FIX-PATH-ECHO-1/ac-results.md` | `5b9f6c422df5cdb601522c91cb447702a2e78efc` | `3f38b15e37ec94aa8e70ca8d7eef291ae23aeca619515590d3c6d834f4b6027a` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E17 | AC4 frontend 安装日志 | `verification/SEC-FIX-PATH-ECHO-1/baseline/npm-ci.log` | `5b9f6c422df5cdb601522c91cb447702a2e78efc` | `90c81132c43d0d67ca152e30c3b5014093dd2d9641cc22b44ec95b9aefc3f281` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E18 | AC4 Rust source 初次阻塞记录 | `verification/SEC-FIX-PATH-ECHO-1/baseline/rust-source-build-blocked.log` | `5b9f6c422df5cdb601522c91cb447702a2e78efc` | `93eca7fc7a735acb6adfa8177eec72e2dd31474c3dbc952e57824e2f6825c857` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E19 | AC5 Handoff | `doc/handoffs/SEC-FIX-PATH-ECHO-1-5b9f6c4.md` | `bc8b57778e17d488b89bc9659ad2db6f43ed6445` | `7ae03284f73eb977d5fd4e94b1e0330ac3622d2c9adf56a33618097e9a659ab6` | CANONICAL |

- Canonical Evidence 状态：`complete`。19/19 条 commit 包含性校验通过；`sha256` 基于本 Task worktree 的磁盘字节。
- BL-18：Codex 仅完成 Owner 自检；独立 Reviewer 为 DeepSeek Harness，尚未产生或冒名记录 Review。
