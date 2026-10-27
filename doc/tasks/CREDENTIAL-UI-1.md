---
id: CREDENTIAL-UI-1
title: 设置页凭据 UI（安全输入 → credential_put / clear）
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-27_goal_auto_except_recommended
suggested_owner: saber-ui-spec
owner: saber-ui-spec
reviewer: dsh
depends_on: []
base_commit: 6f6e4a678
branch: task/CREDENTIAL-UI-1
worktree: G:/CODEX/New Manga.workspace/worktrees/CREDENTIAL-UI-1
integration_commit: dde7f50ee
delivery_head: 5b5d67fc5a248f1081cab4dca49faa2d85d71f97
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/CREDENTIAL-UI-1
allowed_paths:
  - doc/tasks/CREDENTIAL-UI-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/CREDENTIAL-UI-1/**
  - G:/CODEX/New Manga.workspace/task-envs/CREDENTIAL-UI-1/**
  - G:/CODEX/New Manga.workspace/worktrees/CREDENTIAL-UI-1/**
---

# CREDENTIAL-UI-1：设置页凭据 UI（安全输入 → credential_put / clear）

> 交付状态：**ready-for-integration**（实现 `5b5d67fc5` + 证据 + Handoff 已完成；待 DSH 复核/集成；Owner 不自审）。

## 背景

CREDENTIAL-PORT-1 已交付 `credential_put`/`credential_clear` 命令面 + Windows vault 端口（parity 66/0），但 App UI 未接线：Avalonia 设置页没有凭据输入/清除控件。

## Acceptance Criteria

- [x] **AC1 安全输入**：设置页新增「凭据」区块——provider/proxy 目标选择 + 密码框（掩码、不可复制明文、关闭窗口即清空）；提交调 `credential_put`，清除调 `credential_clear`；成功/失败 typed 提示。→ **MET**：`CredentialSection` + `SecretTextBox`（PasswordChar 掩码、无 context menu、Ctrl+C/X/Insert 拦截）；target 来自 P15 profile list（configured/missing）；put(create/replace)/clear 走既有 HostLocal 命令；typed 结果（`CREDENTIAL_CONFLICT`/`CREDENTIAL_STORE_UNAVAILABLE`/`INVALID_ARGUMENTS`/`CREDENTIAL_NOT_FOUND`/`HOST_NOT_READY`）。证据：`credential-ui/put-create.json`、`credential-ui/clear.json`、`credential-ui/payload-contract.json`。
- [x] **AC2 状态显示**：列表显示各目标 `configured / missing`（不显示 secret）；冲突（`CREDENTIAL_CONFLICT`）给明确 UI 提示（替换需二次确认）。→ **MET**：目标行显示 `Provider API Key · <name> · configured/missing`；冲突行 +「确认替换/取消」，确认前零调用。证据：`credential-ui/conflict-replace.json`、`credential-ui/configured-target-confirm.json`、`credential-ui/settings-wiring.json`。
- [x] **AC3 安全**：secret 不进日志/不落 DB/不进 UI 自动化树（PasswordBox 掩码或等价）；关闭后内存中不留明文引用。→ **MET**：自定义 automation peer 无 `IValueProvider`/value（真机 UIA 只见固定名称）；关闭/提交/清除/切换目标/取消清空明文与待确认 secret；253 文件扫描 0 命中（marker 仅 sha256）。证据：`real-app-uia-observation.txt`、`security-scan.json`、`credential-ui/window-close-clears.json`。
- [x] **AC4 测试**：Headless 覆盖「输入→put 调用参数正确（fake store）」「清除→clear」「冲突提示」；真机截图一次（掩码状态）。→ **MET**：9 项 headless（put 参数、clear、冲突二次确认、已配置先确认/取消、复制策略、payload 契约、HostLocal 路由、接线、关闭清空、掩码可见性）；真机 `real-app-masked.png`（22 圆点掩码 + UIA 观察）。证据：`credential-ui/*.json`、`real-app-masked.png`。
- [x] **AC5 回归/门禁**：`scripts/test.ps1` 全绿（≥189）；vitest 60/567；pytest 无新增失败；`check.ps1 -TaskPath` PASS；64-hex pin；Handoff。→ **MET**：test.ps1 **198/198, 0 skipped**（61/53/84）；vitest **60/567**；pytest **3F/2772P/9S**（同一组 3 失败，0 新增）；check PASS；18 条 pin；Handoff 含 Record Decision。

## Record Decision（摘要，完整版在 Handoff / REPORT）

| 项 | 决定 |
|---|---|
| 输入控件 | 自定义 `SecretTextBox : TextBox`（PasswordChar 掩码 + 自定义 automation peer + 复制快捷键拦截），禁止明文 TextBox |
| 真机发现 | 派生控件缺 `StyleKeyOverride => typeof(TextBox)` → 解析不到控件主题、测量 0×0 不可见；已修复并由 headless 可见性测试回归 |
| intent 策略 | missing → `create`；configured → 二次确认后 `replace`；Host 独立校验，冲突 typed `CREDENTIAL_CONFLICT` |
| 状态来源 | 复用 `settings_provider_profiles_list`/`settings_network_profiles_list` 的 `credential_state`（不新增 Host 命令） |
| secret 生命周期 | 仅掩码框 Text（提交瞬间清空）、一次 dispatcher payload、替换确认期间 `_pendingSecret`；关闭/取消/切换目标清理；不写日志/证据/自动化 |
| 测试边界 | UI 用 fake 凭据端口，不写真实 Windows 凭据库；真实 vault 由 CREDENTIAL-PORT-1 的 Host 测试覆盖；真机截图不点保存 |

## 实现摘要（全部 `apps/desktop-avalonia/**`）

- `Services/CredentialUiContracts.cs`（新）：target/result 契约、`credential_put`/`credential_clear` payload 构造、typed 映射。
- `Services/IHostController.cs` / `HostController.cs` / `NullHostController.cs`：新增 `ListCredentialTargetsAsync` / `PutCredentialAsync` / `ClearCredentialAsync` 接线（label 读取 P15 profile list；put/clear 走既有 HostLocal 命令；从不抛进 UI）。
- `Views/SecretTextBox.cs`（新）：掩码-only 输入控件 + 无 value 的 automation peer。
- `Views/CredentialSection.cs`（新）：目标选择、状态行、保存/清除/刷新、冲突二次确认、secret 清理。
- `Views/Pages.cs`：`SettingsPage` 注入 `IHostController` 并嵌入凭据卡；`RefreshCredentialsAsync` / `ClearCredentialSecrets`。
- `Views/MainWindow.axaml.cs`：Host 就绪与进入设置页时刷新状态；`OnClosed` 清空掩码明文。
- `tests/NewManga.App.Tests/CredentialUiTests.cs`（新，9 项）+ `FakeHostController` 扩展。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class |
|---|---|---|---|---|---|
| CU-TEST-SUMMARY | AC5 | verification/CREDENTIAL-UI-1/test/summary.json | 5b5d67fc5a248f1081cab4dca49faa2d85d71f97 | 7717fa702025c7ced6458c5989b04c34300eab4623b4ff6f08fb6c284a4dfd0e | CANONICAL |
| CU-TEST-LOG | AC5 | verification/CREDENTIAL-UI-1/test/dotnet-test-Debug.log | 5b5d67fc5a248f1081cab4dca49faa2d85d71f97 | 3364ed99c8afe328345b53b6bb88ad3c8995994e32195d19c6cf98978a987d5d | CANONICAL |
| CU-VITEST | AC5 | verification/CREDENTIAL-UI-1/test/vitest.log | 5b5d67fc5a248f1081cab4dca49faa2d85d71f97 | aa79f06972b0ec62a898d4df3287abccc63099811d0118f5b449d3b6013d37b7 | CANONICAL |
| CU-PYTEST | AC5 | verification/CREDENTIAL-UI-1/test/pytest.log | 5b5d67fc5a248f1081cab4dca49faa2d85d71f97 | 83e9642a9586b58638378b20028f9e46a0b984564a95f651b06602b137c26ec9 | CANONICAL |
| CU-TEST-PS1-LOG | AC5 | verification/CREDENTIAL-UI-1/test/test.ps1-final.log | 5b5d67fc5a248f1081cab4dca49faa2d85d71f97 | 19ae135e26be7b62a759c3c4d9221d48d9f96ed877660fccd2b94f369fb53111 | CANONICAL |
| CU-PUT-CREATE | AC1/AC4 | verification/CREDENTIAL-UI-1/credential-ui/put-create.json | 5b5d67fc5a248f1081cab4dca49faa2d85d71f97 | 3d3ea1a8e567ed54a71440e35936261ff1e63b12931e7843c34cd64194abfea4 | CANONICAL |
| CU-CLEAR | AC1/AC4 | verification/CREDENTIAL-UI-1/credential-ui/clear.json | 5b5d67fc5a248f1081cab4dca49faa2d85d71f97 | e2290e2d0fe85048e2a458f6f41a758b578910a561fef61d70cf5d388a67bb7d | CANONICAL |
| CU-CONFLICT | AC2/AC4 | verification/CREDENTIAL-UI-1/credential-ui/conflict-replace.json | 5b5d67fc5a248f1081cab4dca49faa2d85d71f97 | 6f226e5a25ec828b8719ec199ec2e194f5f1349529c1570b4a0c33c20aa6faa7 | CANONICAL |
| CU-CONFIGURED-CONFIRM | AC2/AC4 | verification/CREDENTIAL-UI-1/credential-ui/configured-target-confirm.json | 5b5d67fc5a248f1081cab4dca49faa2d85d71f97 | a3fc95840bfb150fc9deaf46cc07f08f73369edbda658eb13cd14f76089f1cf9 | CANONICAL |
| CU-PAYLOAD-CONTRACT | AC1/AC3 | verification/CREDENTIAL-UI-1/credential-ui/payload-contract.json | 5b5d67fc5a248f1081cab4dca49faa2d85d71f97 | 1e3262d5e449531ac5fa2f3698a8e9baebaae6eb0dd9da3757c753f1c6b2245d | CANONICAL |
| CU-SETTINGS-WIRING | AC1/AC4 | verification/CREDENTIAL-UI-1/credential-ui/settings-wiring.json | 5b5d67fc5a248f1081cab4dca49faa2d85d71f97 | 20e4bbc0a60debe08cc6c72e6638c9a3b0bbe65c9ae3bb5fca553283b9368c42 | CANONICAL |
| CU-WINDOW-CLOSE | AC3/AC4 | verification/CREDENTIAL-UI-1/credential-ui/window-close-clears.json | 5b5d67fc5a248f1081cab4dca49faa2d85d71f97 | b2476b03a8471a1f9e842d9ead023c7e2175f84ccb944825cc5620459eaafbf8 | CANONICAL |
| CU-MASKED-VISIBLE | AC3/AC4 | verification/CREDENTIAL-UI-1/credential-ui/masked-input-visible.json | 5b5d67fc5a248f1081cab4dca49faa2d85d71f97 | 197039b711d91b04e26335bbc63730f6fafdb2b9a9b151171c9ff85a5e9c6603 | CANONICAL |
| CU-SECURITY-SCAN | AC3 | verification/CREDENTIAL-UI-1/security-scan.json | 5b5d67fc5a248f1081cab4dca49faa2d85d71f97 | 8697d85e23992e2227aa57ea30801ab8646a14d6dbbc7e2439b292db576610ca | CANONICAL |
| CU-REAL-SCREENSHOT | AC4 | verification/CREDENTIAL-UI-1/real-app-masked.png | 5b5d67fc5a248f1081cab4dca49faa2d85d71f97 | 79b19c1d59c4b66a25019bec59cd68b7559d9386bc71dbd938ebd3e927d22a33 | CANONICAL |
| CU-REAL-SCREENSHOT-META | AC4 | verification/CREDENTIAL-UI-1/real-app-screenshot.json | 5b5d67fc5a248f1081cab4dca49faa2d85d71f97 | 05876aa3ca690fad228084f145811745c20bdc803943ca866fc49b983fb2e08e | CANONICAL |
| CU-REAL-UIA | AC3/AC4 | verification/CREDENTIAL-UI-1/real-app-uia-observation.txt | 5b5d67fc5a248f1081cab4dca49faa2d85d71f97 | aafdf6460d78988ecf2e0bd98a339719ba46c075d547fef785a11afeed50010d | CANONICAL |
| CU-REPORT | AC5 | verification/CREDENTIAL-UI-1/REPORT.md | 5b5d67fc5a248f1081cab4dca49faa2d85d71f97 | 7e34d9f60a873f5ee951545040793a77da7d60a4e0b5847319ee7650c8a5618c | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/CREDENTIAL-UI-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/CREDENTIAL-UI-1 | `evidence/`（test/credential-ui/logs）+ `screenshot-root/`（隔离数据根） | 2026-10-27 收口时存在；`credential-ui/*.json` 与 `test/summary.json` 引用其路径；未移动/未删除；关闭时由 DSH 复核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写（owner 交付 `5b5d67fc5`，待 DSH 集成验证与独立 Review）。
- canonical_evidence_status：`complete`（18 条 CANONICAL pin，指向 delivery_head）。
- resource_closeout_status：`pending`（task-env + 隔离截图数据根保留引用）。
- 删除、迁移、归档数量/字节数：0（本任务未删除任何文件；真实 vault/真实 `%APPDATA%` 未触碰）。
- 未关闭项及保留原因：真实 vault 提交未在 UI 层真机执行（卡面禁令，由 CREDENTIAL-PORT-1 Host 测试覆盖）；真机截图时 Host 未就绪故目标列表为空（掩码与安全属性已验证）；profile 创建/编辑 UI 属后续 Task；需独立 Review。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。

## Review（DSH 集成复核，2026-10-27）— PASS

- 设置页「凭据 · Credential」卡：目标下拉（configured/missing）+ 掩码 SecretTextBox + 保存/清除/刷新 + typed 状态 + CREDENTIAL_CONFLICT 二次确认（确认前零调用）。
- 安全：无明文 TextBox；复制快捷键/右键禁用；automation peer 无 value；提交/清除/切换/取消/关闭均清空；253 文件扫描 secret 0 命中。
- 真机截图揪出并修复真实缺陷：派生 TextBox 缺 `StyleKeyOverride` → 0×0 不可见（已加可见性回归测试）。
- 回归：DSH 复跑 test.ps1 见执行记录（实现方报 198/198）；vitest 60/567；pytest 3F/2772P/9S（0 新增）；check.ps1 -TaskPath PASS；18 条 pin。
- 遗留：UI 未真机写入真实 vault（Host 链已由 CREDENTIAL-PORT-1 覆盖）；真机截图时 Host 未就绪故目标列表为空；profile 创建/编辑 UI 另属 SETTINGS-PROFILE-UI-1。
- 集成：dde7f50ee。


