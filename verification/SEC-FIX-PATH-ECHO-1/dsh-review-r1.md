---
task_id: SEC-FIX-PATH-ECHO-1
reviewer: DeepSeek Harness (dsh)
author: Codex
base_commit: f4bbc59c9e5cf9864ab0ab0e97277b826b9a0a5f
reviewed_head: 6f27cf72aaf1a71de2c6df9fdd041757e6ef2ebe
decision: approved
---

# Review：SEC-FIX-PATH-ECHO-1

## 独立性与范围

- 被审对象：分支 `codex/SEC-FIX-PATH-ECHO-1`（8 提交，tip `6f27cf72a`）；worktree `G:/CODEX/New Manga.workspace/worktrees/SEC-FIX-PATH-ECHO-1`。
- 固定基线 `base_commit = f4bbc59c9`（= 审查时 main HEAD）；固定 `reviewed_head = 6f27cf72a`（= 审查时分支 tip）。
- **独立性**：`.orchestrator/tasks/SEC-FIX-PATH-ECHO-1-role.json` 记录 `owner=codex`、`contributors=[]`、`repair_participants=[]`；Reviewer（dsh）未参与该 Task 的 implementation/repair，符合 `reviewer != owner` 且非 contributor。Review 全程只读，未修改实现、契约、Schema、依赖、STATUS、PLAN 或用户 dirty 内容。
- 依据：Task AC1–AC6 与其允许/禁止范围、`doc/templates/REVIEW.md`、`AGENTS.md` 产品边界（AD-001：React/WebView 不直接访问任意 OS 路径，须经 Tauri IPC 与 Core 冻结契约）。
- 未审到：Tauri/Rust 侧运行时行为（本次未重跑 Rust 套件，采用 Owner 日志 + 数字核对，见 F-note）；前端设置页对 `[redacted]` 的交互（记为 F2）。

## Architecture（结论：PASS）

- **修复位置正确**：改动落在 Python Core 投影层 `src/bootstrap/core_service.py`（+63 行），**非**前端掩盖，满足 Task 禁止项"不得用'前端不再显示'掩盖（必须在 Core/host 投影层修复）"。
- 新增 `_project_settings_value()` 递归投影与 `_SETTINGS_OS_PATH` 正则；覆盖 `handle_settings_get`（全量 + 分节）、`handle_settings_update_section`（写后返回）、以及协议版本不支持 / `E_INVALID_REQUEST` / `E_UNKNOWN` 三类错误 envelope 的 `request_id` 与 `message`，并覆盖 host-control 分支的 `request_id`。
- **写入语义未变**：投影只作用于 IPC 响应，`handle_settings_update_section` 仍持久化原始值；Tauri `main.rs` / `library_bridge.rs` 保持透传、无 host 改动 → 冻结契约未被修改。
- **误伤面受控**：`_settings_path_field` 仅在值为字符串或非空 dict/list 时整体遮蔽，布尔/数值（如 `file: false`）不受影响。
- 分层与依赖：未引入新模块、依赖或 Schema 迁移。

## Verification（结论：PASS，全部独立复跑）

| 场景 | 命令或步骤 | 环境 / commit | 结果 | 证据 |
|---|---|---|---|---|
| AC6 修复前复现 | `python verification/SEC-FIX-PATH-ECHO-1/repro_settings_path_projection.py` | 基线 `f4bbc59c9` | `path_value_returned=true` / `REPRO_RESULT=FAIL` / `EXIT_CODE=1` | `baseline/repro-before.log` |
| AC6 修复后复现（**本次独立实跑**） | 同上 | tip `6f27cf72a`，Python 3.14.6 | `path_value_returned=false` / `REPRO_RESULT=PASS` / `EXIT=0` | 本次实跑输出；`repro-after.log` |
| AC3 反例（应对旧码失败） | `pytest tests/core/test_core_service_settings.py::test_settings_commands_redact_paths_in_every_section -q -p no:cacheprovider` | 基线 | `1 failed` / `EXIT_CODE=1` | `baseline/counterexample-before.log` |
| AC3 反例（修复后） | 同上 | tip | `1 passed` / `EXIT_CODE=0` | `counterexample.log` |
| AC4 Core（**本次独立实跑**） | `python -m pytest tests/core -q -p no:cacheprovider` | tip `6f27cf72a`，Python 3.14.6 | **`536 passed, 1 warning in 38.99s` / `EXIT=0`** | 本次实跑输出 |
| AC4 Core 基线/交付日志对照 | 同命令 | 基线 / 交付 | `535 passed` / `536 passed`，均 `EXIT_CODE=0` | `baseline/core-pytest.log`、`core-pytest.log` |
| AC4 Rust source（日志+数字核对） | `M2RC1_PYTHON` 显式设置后 `cargo test ... -- --skip packaged_sidecar_tests` | 基线 / 交付 | 两次均 `107 passed; 0 failed; 1 ignored` | `baseline/rust-source.log`、`rust-source-tests.log` |
| AC4 packaged（日志+数字核对） | `M2RC1_PACKAGED=1` + `packaged_sidecar_tests` | 基线 / 交付 | 两次均 `12 passed; 0 failed` | `baseline/rust-packaged.log`、`rust-packaged-tests.log` |
| AC4 前端（日志+数字核对） | `npm test -- --reporter=dot` | 基线 / 交付 | 两次均 `285 passed (285)` / 28 files | `baseline/frontend-vitest.log`、`frontend-vitest.log` |
| 证据完整性（**本次独立核算**） | `Get-FileHash -Algorithm SHA256` × 19 条 | tip 磁盘字节 | **19/19 与 Task Canonical Evidence 表逐条一致** | 本次实跑比对 |
| 范围合规（**本次独立核算**） | `git diff --stat main...codex/SEC-FIX-PATH-ECHO-1` | — | 仅 `src/bootstrap/core_service.py`、`tests/core/test_core_service_settings.py`、Task/Handoff/`verification/SEC-FIX-PATH-ECHO-1/**`；**未触碰**用户 43 项 dirty，未改 STATUS/PLAN/契约 | 本次实跑 |

**数字口径**：Core 修复前 **535**（基线）、修复后 **536**（新增 1 个反例测试）——差值 +1 由本 Task 新增测试解释，非既有用例变化。前端 Task 记载 **278**、实测基线 **285**（差 +7 在本次修复前已存在，本 Task 未改前端）→ 属文档口径滞后，非回归。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| F1 | P2（记账） | `doc/handoffs/SEC-FIX-PATH-ECHO-1-c52ce46.md:66`、Task `delivery_head` | Handoff §"接收方式"声明"Review 时固定 `reviewed_head` 为实现提交；文档提交只追加 Task/Handoff/Canonical Evidence，**不修改实现**"，但其后提交 `022f4d737`（`test(settings): cover pre-validation path echoes`）**实际修改了测试代码**与 `core-pytest.log`（535→536）。`delivery_head=c52ce4695` 落后于分支 tip `6f27cf72a`。影响：交付记账不精确，可能导致集成点取错 commit 而漏掉测试与证据更新 | `git log --oneline --name-status main..codex/SEC-FIX-PATH-ECHO-1` | 集成时 `integration_commit` 必须取 **tip `6f27cf72a`**；closeout 如实记录 `reviewed_head=6f27cf72a` 与真实测试数 536 | open |
| F2 | P2（产品观察，非阻塞） | `apps/desktop/frontend/src/settings/SettingsPanel.test.tsx:110` | 前端将 `settings_get` 返回值渲染为"当前值"。路径类字段现返回 `[redacted]`；若将来开放含 path 字段的设置分区（如 OCR 路径），表单可能显示占位符，且存在把 `[redacted]` 回写的理论风险 | 静态审阅 + 复现脚本显示 `ocr.path → "[redacted]"` | 当前唯一已开放分区 `sfx.policy` 为枚举值、无 path 字段，**无实际影响**。建议在 P19 AC3 或后续设置 UI Task 显式验证"占位值不参与回写" | open（deferred） |
| F3 | P2（信息，范围外） | `src/bootstrap/core_service.py:2644-2655` | 路径型 `request_id` 投影仅对 `settings.get` / `settings.update_section` 生效；其他命令的错误响应仍可能原样回显含路径的 `request_id` | Task AC1/AC2 仅约束 settings 两条命令；`safe_request_id` 条件分支 | 超出本 Task AC 范围，不阻塞批准。交 Coordinator 决定是否建立 follow-up Task | open |

无 P0/P1 发现。F1 不影响实现正确性（`src/bootstrap/core_service.py` 在 `c52ce4695` 之后**未再改变**，实现 head 仍准确）。

## 结论与复审

- **decision: approved**（fixed `reviewed_head = 6f27cf72a`，fixed `base_commit = f4bbc59c9`）。
- 理由：AC1–AC6 全部满足且经独立复跑验证；19/19 SHA-256 逐条一致；修复位于 Core 投影层且未改契约；四套件无回归；范围合规、未触碰用户 dirty。P0/P1 未解决 0 项，关键验证缺失 0 项。
- 集成要求：`integration_commit` 取分支 tip `6f27cf72a`；合并后**在主仓复跑 Core pytest 必须得 536**（若得 535 说明测试未随合并进入，须停下核查）。
- 剩余风险：F2（未来 path 类设置分区的回填语义）、F3（非 settings 命令的 request_id 路径回显）。
- 复审规则：head 变更或出现新 Review 后本文件自动转为历史记录，不得覆盖或继续当作当前批准。
