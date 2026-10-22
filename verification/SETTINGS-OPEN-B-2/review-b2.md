# SETTINGS-OPEN-B-2 首次独立 Review（缓存/Revision 清理操作面）

- Reviewer：`reviewer-settings-a`（非实现者）
- 审查头：**`0e2e6233aa54363e49e992ba2353a00c665c3de0`**（B-2 实现 commit）
- 父 commit：**`81f822127f6c98a16b5456bf0595ef29bdd437f8`**
- 后续 HEAD：`d263c8e74`（B-1 r3 文档/证据提交）；`git diff 0e2e6233 HEAD -- apps/desktop/frontend/src/settings apps/desktop/src-tauri src/bootstrap src/application/maintenance tests/core/test_core_cleanup_wire.py` **为空**，本 Review 的 B-2 产品代码结论对当前 HEAD 仍有效。
- 审查方式：读 B-2 完整 diff；独立重跑 Core/Rust/frontend；核对 Tauri 五处清单、probe/ac1 冻结、Core 投影与安全边界；核验 GUI 截图与 canonical evidence；检查 Task/Handoff/报告 base/pins。

## 结论

**changes_requested**。产品实现（Core AC1、Tauri AC2、前端 AC3、测试 AC4）通过独立验证，代码本身没有 P0/P1 缺陷；但 **AC5 证据/pins 自相矛盾**（base 写错、wire/ui report 仍称“未提交工作区/GUI NOT_RUN”而 gui-smoke 已 PASS）、存在一个失败明细泄露 OS 绝对路径的 P2 安全/隐私问题，以及 evidence hash 行尾口径问题。修正证据/文档后应可复审通过，无需重做产品实现。

## 1. AC 状态

| AC | 状态 | 说明 |
|---|---|---|
| AC1 Core 操作面 | **PASS** | 三命令为 application-channel，不在 `_HOST_CONTROL_COMMANDS`；投影、CORE_UNAVAILABLE、payload 校验均成立；28 个 wire 测试全绿 |
| AC2 Tauri 命令面 | **PASS** | `PRODUCTION_COMMANDS` 57、`CLEANUP_PRODUCTION_ONLY_COMMANDS`、allowlist、`generate_handler!`、capabilities/build.rs/生成物一致；probe/ac1 仍 7/6 冻结；cargo 152 passed |
| AC3 前端面板 | **PASS** | 真实预览/清理/重试、空态/错误态、防重复、失败投影；41 files/406 tests、tsc 0 |
| AC4 测试 | **PASS** | 752 Core + 152 Rust + 406 frontend 全绿（独立重跑一致）；安全前缀/pending 重试测试存在 |
| AC5 证据 | **FAIL/PARTIAL** | base commit 与报告事实错误；GUI NOT_RUN/PASS 矛盾；pending/restart 烟测未做；canonical_evidence_status 仍 pending |

## 2. Findings

### P1-1（证据/范围，必须修）— `base_commit` 与 wire/ui report 仍写 `7d19164`/“未提交工作区”，实际父 commit 是 `81f8221`

- `doc/tasks/SETTINGS-OPEN-B-2.md:12`：`base_commit: 7d19164f...`；`doc/handoffs/SETTINGS-OPEN-B-2-0e2e623.md:5` 同样写 `7d19164`。
- `verification/SETTINGS-OPEN-B-2/wire-report.md:5-6`：基线 `7d19164`，并声明“本报告对应**未提交**工作区”；`ui-report.md:4,22,151` 同样声明 `7d19164`、未 commit。
- 实际 `git rev-parse 0e2e6233^` = **`81f82212...`**（用户给出的 parent），B-2 实现 diff 是 `81f8221..0e2e6233`；报告却按 `7d19164`/未提交工作区描述，使 Review/证据范围与 canonical commit 不一致。
- 影响：Review 模板要求 Review 只对固定 `base_commit`/`reviewed_head` 有效；Task/Handoff/两份报告三处 base 错误会让后续 Owner 或集成者审查到错误范围，也无法从报告复现“提交后”的证据。
- 建议：将 Task/Handoff/report 的 base 统一为 `81f8221`；把 wire/ui report 的“未提交工作区”改为 `0e2e6233` 已提交状态，并刷新对应 evidence hash/commit pin；Task `integration_commit/delivery_head` 保持 `0e2e6233`。

### P1-2（AC5 证据，必须修）— `ui-report` 称 GUI NOT_RUN，`gui-smoke` 却给出 PASS；AC5 未勾选，pending/restart 未测

- `verification/SETTINGS-OPEN-B-2/ui-report.md:9`：“GUI 烟测为 **NOT_RUN**”；`:159` 再次写 GUI NOT_RUN、建议 Lead 集成阶段执行。
- 但 `verification/SETTINGS-OPEN-B-2/gui-smoke.md` 记录 Lead 在 dev preview 已实际执行 preview/clean/empty，截图 `01..03` 与结果（3 文件/6.0 KB → 成功 3/失败 0/跳过 0 → 归零）可核对；Task `:88` 也写“GUI 烟测 PASS（gui-smoke.md）”。
- `doc/tasks/SETTINGS-OPEN-B-2.md:56` 的 **AC5 仍未勾选**；`canonical_evidence_status: pending`（`:17`）；`gui-smoke.md:20` 明确“重启后 pending 一致”未制造失败场景、未做，pending 重试仅由 Core 测试覆盖。
- 影响：同一 canonical evidence 集合同时声明 GUI PASS 与 NOT_RUN，且 AC5 无法判定；用户重点“(5) GUI 证据是否支持真实可用”只能支持 preview/clean/empty，不能支持 pending/restart。
- 建议：把 AC5 拆清为 **preview/clean/empty = PASS**、**pending/restart = NOT_RUN（或补做）**；更新 `ui-report` 的 GUI 段和 Task AC5；在证据表把 `EV-B2-GUI-SMOKE` 标注覆盖范围；验证后再把 `canonical_evidence_status` 从 pending 改为完成。

### P2-1（安全/隐私）— 失败明细原样透传 `OSError` 文本，可把 OS 绝对路径送到 WebView 并渲染

- `src/application/maintenance/cleanup.py:151-152`（run）与 `:181-182`（retry）对 `OSError` 使用 `str(error)` 作为 `CleanupItemResult("failed", ...)` 的 `reason`；`src/bootstrap/core_service.py:483-493` 把 `items` 原样投影；`apps/desktop/frontend/src/settings/CacheRevisionPanel.tsx:326-329` 把 `detail` 渲染到 DOM。
- 独立 probe（`CleanupService` + 抛含绝对路径的 `OSError`）返回：
  ```
  {"cache/webtoon-tiles/tile-x.png": {"status": "failed",
    "reason": "[WinError 32] ... 'C:\\managed\\cache\\webtoon-tiles\\tile-x.png'"}}
  ```
  真实 Windows 文件被占用/权限失败时，`ManagedFileStorage.remove_managed` 的 `OSError` 通常也包含绝对路径（`absolute.unlink()` 的异常文本）。
- 影响：违反项目“React/WebView 不直接接触任意 OS 路径”的边界，也让 wire-report §6「投影不含 OS 路径」在失败分支不成立；缓存路径虽非用户源文件，仍是宿主路径。
- 建议：失败 `reason` 使用固定短句或脱敏（只保留错误类别/相对路径），不要把 `str(error)` 直接下发；补一个 `OSError` 含绝对路径的 wire test，断言 `_no_absolute_paths(result)`。

### P2-2（证据 hash 口径）— canonical sha256 是工作区 CRLF 字节，不是 commit blob

- B-2 的 14 条 canonical 中，8 条文本日志/报告的 sha256 与工作区文件一致，但与 `git show a5bdb30:<path>` 的 blob 哈希不同（例如 `ui-test-frontend.log`、`wire-cargo-test-serial.log`；其余截图/报告因 LF/二进制一致）。`check.ps1` 同时接受 worktree 与 blob hash（`check.ps1:365-375`），所以本地 PASS；用 `git archive`/autocrlf=false 的 clean 快照复核会不一致。
- 建议：明确约定优先 pin commit blob hash，或对 evidence 文本加 `.gitattributes` 固定行尾；在本 Task 记录口径，否则会重复 r2 式证据争议。

### P2-3（文档/契约同步）— 新 production 命令未记入 typed IPC contract

- `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` 是 B-2 allowed path，但提交未增加 `cleanup.preview/run/retry_pending` 与三条 Tauri production-only 命令的记录；Task AC2 只要求命令清单同步，未明确 contract 条目。
- 影响：新命令的 wire 形状/错误语义已由 Task/design §4.3 冻结，但 contract 目录仍只描述 settings；后续以 contract 为准的集成者会缺一条事实源。
- 建议：补 contract 注记（应用层命令、payload `{}`、投影、CORE_UNAVAILABLE/INVALID_REQUEST、production-only）或在本 Task 明确记录“不纳入 typed IPC contract 的理由”。

## 3. 独立验证

### 3.1 Core / CleanupService

- `_CLEANUP_COMMANDS`（`core_service.py:257-260`）与 `_HOST_CONTROL_COMMANDS`（`:242-245`，仅 6 个 host 命令）无交集；dispatch 在 application 分支（`:3820-3905`），非 host-control；`test_cleanup_commands_are_not_accepted_on_the_frozen_host_control_envelope` 通过。
- 投影：preview `{targets,total_bytes,pending_cleanups}`；run/retry `{items:{relpath:{status,reason}},removed,failed,skipped}`；与前端 `client.ts` 解析一致。
- `CleanupService` 复用 `WebtoonTileCacheSweeper` + `ManagedFileStorage.remove_managed` + 同一 `_JsonTrashManifest`，只处理 `cache/` 安全前缀；`core_assembly.py:947-963` 与 `cleanup.py:127-205` 未新增删除路径；pending 账本 key 与 trash 的 `pending_purges` 分离，未见跨面丢弃。
- 测试：`pytest tests/core/test_core_cleanup_wire.py -q` → **28 passed**；`pytest tests/core -q` → **752 passed, 1 warning, 43.48s，EXIT 0**；安全前缀/重试/缺注入/request_id 脱敏均覆盖。
- 问题：P2-1 失败 reason 路径；`CleanupService` 只 catch `OSError`，若 `ManagedFileStorage` 抛 `ImmutablePathViolation`（RuntimeError）会由 dispatcher 返回 generic UNKNOWN（不会删除文件，但整次操作失败、不形成 pending）；属边界 P2，建议在 P2-1 修复时一并考虑按项 fail-closed 或固定错误。

### 3.2 Tauri（五处一致 + probe/ac1）

- `apps/desktop/src-tauri/src/main.rs:70-89` 的 `PRODUCTION_COMMANDS` 含三条 cleanup；`:192-193` `CLEANUP_PRODUCTION_ONLY_COMMANDS`；`:288-315` `command_allowlist` 在 probe/ac1 过滤；`:1671-1673` production `generate_handler!`；probe/ac1 的 `generate_handler!` 不含三条。
- `capabilities/m2rc1-commands.json:4,20-22` 声明 64 命令/57 production + 三个 allow；`build.rs:44-85` ACL manifest 同步；`permissions/autogenerated/cleanup_*.toml` 与 `gen/schemas/*` 已提交。
- 独立 `cargo test --locked --skip packaged_sidecar_tests --test-threads=1`（dev overlay + `M2RC1_PYTHON`）：**152 passed; 0 failed; 1 ignored; 12 filtered out; 26.97s，EXIT 0**；`cleanup_commands_are_exact_and_production_only` 通过。默认线程 149+2 个既有 flaky 未复跑，wire-report 已记录为基线问题。
- 结论：AC2 五处一致、probe/ac1 冻结成立。

### 3.3 前端 / GUI

- `npm --prefix apps/desktop/frontend test` → **41 files / 406 tests passed，EXIT 0**；`tsc --noEmit` → **0**。
- 面板自动 preview、空态禁用、结果计数、失败明细、retry、加载错误、防重复均有人测；`SettingsPage` 9 开/3 关；无自动清理天数/Revision 保留控件，只有只读说明（`CacheRevisionPanel.tsx:13-23,254-260`），符合“不开放”。
- 截图核对：`01-cache-preview-3-files.png` 显示“可清理 3 个文件 / 6.0 KB、挂起项 0 个”，`02-cache-cleaned.png` 显示“成功 3 个 · 失败 0 个 · 跳过 0 个”，`03-cache-empty-idle.png` 空态；与 gui-smoke 一致，**支持真实可用（preview/clean/empty）**。
- 未覆盖：pending/restart（见 P1-2）；失败态 GUI 未制造（Core tests 覆盖）。

### 3.4 测试/检查汇总

| 命令 | 结果 | EXIT |
|---|---|---|
| `python -m pytest tests/core -q` | **752 passed, 1 warning, 43.48s** | 0 |
| `python -m pytest tests/core/test_core_cleanup_wire.py -q` | **28 passed, 3.86s** | 0 |
| `cargo test --locked --skip packaged_sidecar_tests --test-threads=1` | **152 passed / 0 failed / 1 ignored / 12 filtered, 26.97s** | 0 |
| `npm --prefix apps/desktop/frontend test` | **41 files / 406 tests passed** | 0 |
| `tsc --noEmit` | 无诊断 | 0 |
| `tools/governance/check.ps1` | **PASS (2 warnings)** | 0 |

## 4. 范围 / 未跑

- 审查范围：B-2 的 Core、Tauri、frontend、tests、verification；B-2 commit 后只有 B-1 r3 docs/evidence，B-2 产品文件无后续修改。
- B-2 Task 的 canonical 14 行、commit a5bdb30 含所 pin 文件；hash 口径见 P2-2。
- **NOT_RUN**：`packaged_sidecar_tests`（无 PyInstaller bundle）；GUI pending/restart；真实失败态 GUI；默认线程 cargo（既有 flaky，串行已过）。
- 未审：B-1 r3（另有 `review-b1-r3.md`）；B-2 后续批次 C。

## 5. 推荐下一步

1. 修 **P1-1**：Task/Handoff/wire-report/ui-report base 统一 `81f8221`，报告改为已提交 `0e2e6233`；重刷 canonical evidence/hash pin。
2. 修 **P1-2**：明确 AC5 GUI 覆盖（preview/clean/empty PASS；pending/restart NOT_RUN 或补烟测），更新 `ui-report`/Task AC5 后再把 `canonical_evidence_status` 收口。
3. 修 **P2-1**：失败 `reason` 脱敏并加“失败含绝对路径”回归；P2-2 统一 hash 行尾口径；P2-3 补 contract 注记。
4. 上述只改证据/文档/错误文本，不需要重做 B-2 产品实现；修正后可快速复审通过。
