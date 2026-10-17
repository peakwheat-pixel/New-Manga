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
- [x] **AC2**：请求校验、写入验证、协议版本提前拒绝和错误 channel 拒绝的响应均不回显路径片段；路径型 `request_id` 与验证消息封闭投影。
- [x] **AC3 反例测试**：合成绝对路径覆盖 `settings_get` 与 `settings_update_section`、13 个 section、OS 路径形式、路径字段、section key、request ID、非法协议版本、错误 channel 和错误。
- [x] **AC4 不回归**：Core、Rust source、packaged、前端均与本 worktree 基线不回归；前端 Task 记录 278，但基线实测为 285，修复前后均 285。
- [x] **AC5 交付**：实现 commit 与 Handoff 已固定；本 Task 为 `in_review`，Canonical Evidence `complete`，按 BL-15/16/17/18/19 记录。
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

以下 `sha256` 按当前 worktree 的磁盘字节计算。19 条证据均通过 `git cat-file -e 022f4d73773a2d9bdafa04f16d4cca96af5c37ad:<path>` 验证包含性；`class` 仅用 `CANONICAL`。没有声称其他 checkout 的磁盘字节已独立复核。

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| SEC-FIX-PATH-ECHO-1-E1 | AC1/AC2 Core 投影实现 | `src/bootstrap/core_service.py` | `022f4d73773a2d9bdafa04f16d4cca96af5c37ad` | `d51b60db4cc38ed795502b907789f821bd18d834b8640accbff81ab2680ca80d` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E2 | AC3 反例测试 | `tests/core/test_core_service_settings.py` | `022f4d73773a2d9bdafa04f16d4cca96af5c37ad` | `9c39bb81b1317298bafd424e0b62808864848c08c9e1becdf151ee580e8721ee` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E3 | AC6 等价复现脚本 | `verification/SEC-FIX-PATH-ECHO-1/repro_settings_path_projection.py` | `022f4d73773a2d9bdafa04f16d4cca96af5c37ad` | `03f20d4cbc42371d3a05533103a965a72c2a9a76a95a76ef4114a46a0592e879` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E4 | AC6 基线复现输出 | `verification/SEC-FIX-PATH-ECHO-1/baseline/repro-before.log` | `022f4d73773a2d9bdafa04f16d4cca96af5c37ad` | `55422c216533c9b745c03d7a506c684b9d4ba8a41ef368f12c10e9d4c7bca163` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E5 | AC6 修复后复现输出 | `verification/SEC-FIX-PATH-ECHO-1/repro-after.log` | `022f4d73773a2d9bdafa04f16d4cca96af5c37ad` | `5088955da6dde1ce63b75383f44c7d46d3d81ee2eb02fb5e10a3787d554cfbac` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E6 | AC4 Core 基线 | `verification/SEC-FIX-PATH-ECHO-1/baseline/core-pytest.log` | `022f4d73773a2d9bdafa04f16d4cca96af5c37ad` | `af8a62695fe8ec86c38dd0adb6e17744875be22c63180be619b29948516d81c2` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E7 | AC4 Core 交付 | `verification/SEC-FIX-PATH-ECHO-1/core-pytest.log` | `022f4d73773a2d9bdafa04f16d4cca96af5c37ad` | `4d5818eca7d3545b55d511377c2b27db237587750413f172af90b22663a55744` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E8 | AC3 修复前反例输出 | `verification/SEC-FIX-PATH-ECHO-1/baseline/counterexample-before.log` | `022f4d73773a2d9bdafa04f16d4cca96af5c37ad` | `0c2328de431b2329f80cc9de5670465dd99ee0f6bbdc4be34471c225e327f3c3` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E9 | AC3 修复后反例输出 | `verification/SEC-FIX-PATH-ECHO-1/counterexample.log` | `022f4d73773a2d9bdafa04f16d4cca96af5c37ad` | `5e005d2dd8c2ec3e27767ff704cbe9065a8c05420baa8f3a9ba8b4409f16a3e1` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E10 | AC4 Rust source 基线 | `verification/SEC-FIX-PATH-ECHO-1/baseline/rust-source.log` | `022f4d73773a2d9bdafa04f16d4cca96af5c37ad` | `dd0dcaccc678eb2f3872af435013e25942311b0f1457572412d3cf826620f164` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E11 | AC4 Rust source 交付 | `verification/SEC-FIX-PATH-ECHO-1/rust-source-tests.log` | `022f4d73773a2d9bdafa04f16d4cca96af5c37ad` | `a1df0678a66abaa03ce336169061b7d33c90a53dcd7d4babfaa8fcad50e54a59` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E12 | AC4 packaged 基线 | `verification/SEC-FIX-PATH-ECHO-1/baseline/rust-packaged.log` | `022f4d73773a2d9bdafa04f16d4cca96af5c37ad` | `4cf8e7fb15b8f9b219e7c69077f4fdfe955405eb036fd9ec9ca64b83e9c40042` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E13 | AC4 packaged 交付 | `verification/SEC-FIX-PATH-ECHO-1/rust-packaged-tests.log` | `022f4d73773a2d9bdafa04f16d4cca96af5c37ad` | `bb903c9f3e96d7c8b56796c04e33ffde6e11171334780e23886c5e8114bd7e27` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E14 | AC4 前端基线 | `verification/SEC-FIX-PATH-ECHO-1/baseline/frontend-vitest.log` | `022f4d73773a2d9bdafa04f16d4cca96af5c37ad` | `eda5f2aa7225156a354588df75b62a4c8ae44d0c1836366e168b650debfaf288` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E15 | AC4 前端交付 | `verification/SEC-FIX-PATH-ECHO-1/frontend-vitest.log` | `022f4d73773a2d9bdafa04f16d4cca96af5c37ad` | `3eea9556bcc6e954931c7266c18709e0e6f9806fe374d9d8d93a71d68c2ed24f` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E16 | AC1–AC6 汇总 | `verification/SEC-FIX-PATH-ECHO-1/ac-results.md` | `022f4d73773a2d9bdafa04f16d4cca96af5c37ad` | `cb8cf929e5a2c647fde6f864481f9f451636ad3550060a2666bd40b95e6e0083` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E17 | AC4 frontend 安装日志 | `verification/SEC-FIX-PATH-ECHO-1/baseline/npm-ci.log` | `022f4d73773a2d9bdafa04f16d4cca96af5c37ad` | `eef6288e00f4a2b3c8a649994b3333bdf47c96f758dd1632de9eb46c7c71cfe0` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E18 | AC4 Rust source 初次阻塞记录 | `verification/SEC-FIX-PATH-ECHO-1/baseline/rust-source-build-blocked.log` | `022f4d73773a2d9bdafa04f16d4cca96af5c37ad` | `fc6cc0413af41e5e14b336873ea718476282d2ecf1dc9066a516989f40cd2962` | CANONICAL |
| SEC-FIX-PATH-ECHO-1-E19 | AC5 Handoff | `doc/handoffs/SEC-FIX-PATH-ECHO-1-c52ce46.md` | `022f4d73773a2d9bdafa04f16d4cca96af5c37ad` | `29e447a2503c0acb2c2d2a0c0c4615e2b2ce2093c274bf50e518427950b0864a` | CANONICAL |

- Canonical Evidence 状态：`complete`。19/19 条 commit 包含性校验通过。
- BL-18：Codex 仅完成 Owner 自检；独立 Reviewer 为 DeepSeek Harness（非作者；`.orchestrator/tasks/SEC-FIX-PATH-ECHO-1-role.json` 证明其非 owner/contributor），Review 见 `verification/SEC-FIX-PATH-ECHO-1/dsh-review-r1.md`（`decision: approved`，`reviewed_head=6f27cf72a`）。

## 证据行尾规范化与 re-pin 记录（Coordinator dsh, epoch 7；用户 2026-10-17 裁决方案 A）

- **背景**：集成后核验发现本 Task 有 4 条 `sha256` 在**主仓 checkout 下不可复现**。根因是证据目录**缺少行尾约定**：`core.autocrlf=true` 使 `git checkout` 把仓库内 LF blob 检出为 CRLF，而 Owner 计算 pin 时用的是 worktree 的 LF 字节。
- **处置（方案 A：统一 LF）**：
  1. 新增 `verification/SEC-FIX-PATH-ECHO-1/.gitattributes`（`* text eol=lf`），与同批 Task `P19-AC3-1` 的既有约定一致；
  2. 对证据目录执行**字节级 CRLF→LF 规范化**（保留 BOM 与其他字节，不改内容语义）；
  3. Handoff 位于 `doc/handoffs/`（不在证据目录内），故在**根 `.gitattributes`** 追加精确规则 `doc/handoffs/SEC-FIX-PATH-ECHO-1-c52ce46.md text eol=lf`；
  4. 用脚本从**磁盘实测字节**重算 pin 并回写本表（**未人工转录**）。
- **受影响 pin（15 条）**：E4–E15、E17、E18、E19。E1/E2 在 `src/`、`tests/`（未规范化），pin 不变；E3/E16 原本即 LF，pin 不变。
- **E19 附带修正**：原记 `ecc0d82d…` 与磁盘在**两种行尾下都不符**（系 `022f4d737` 改写该 Handoff 后的陈旧 pin），属 **pin 记错**，本次一并修正为实测值 `29e447a2…`。
- **自校验**：重算脚本二次运行报告 `stale=0`（全部与磁盘一致）。
- **不变式**：`sha256` 仍按**磁盘字节**计算（BL-16），只是在新增 `.gitattributes` 之后，任何 checkout（含 fresh clone）都得到同一 LF 字节。
