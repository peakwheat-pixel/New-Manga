---
id: SETTINGS-PROFILE-UI-1
title: 设置页 profile 管理 UI（provider / network profile 表单）
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-27_goal_auto_except_recommended
suggested_owner: saber-ui-spec
owner: saber-ui-spec
reviewer: dsh
depends_on: []
base_commit: 327aa8526
branch: task/SETTINGS-PROFILE-UI-1
worktree: G:/CODEX/New Manga.workspace/worktrees/SETTINGS-PROFILE-UI-1
integration_commit: 31cf7f1ce
delivery_head: f2cf8734325c2597d46c064e36b7824bb4cfe2ec
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/SETTINGS-PROFILE-UI-1
allowed_paths:
  - doc/tasks/SETTINGS-PROFILE-UI-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/SETTINGS-PROFILE-UI-1/**
  - G:/CODEX/New Manga.workspace/task-envs/SETTINGS-PROFILE-UI-1/**
  - G:/CODEX/New Manga.workspace/worktrees/SETTINGS-PROFILE-UI-1/**
---

# SETTINGS-PROFILE-UI-1：设置页 profile 管理 UI

> 交付状态：**ready-for-integration**（实现 `f2cf87343` + 证据 + Handoff 已完成；待 DSH 复核/集成；Owner 不自审）。
> 说明：卡面 base 记 `dde7f50ee`；按 DSH 指令分支从当前 HEAD **`327aa8526`** 创建。

## 背景

命令面已 66/0；凭据 UI 已就绪（CREDENTIAL-UI-1），但真实用户无法在 UI 内创建 provider/network profile 目标。相关命令均已实现但无 UI 入口。

## Acceptance Criteria

- [x] **AC1 provider profile 表单**：列表 + 新建/编辑/删除（名称/类型/base_url/model 等字段按 P15 profile schema），成功/失败 typed 提示。→ **MET**：「Provider Profile 管理」卡（display_name/provider_id/capabilities/endpoint/model/network_profile/enabled；新建/保存修改/删除/刷新；空态；typed `SETTINGS_*` 提示）。证据：`settings-profile-ui/provider-create.json`、`provider-update-delete.json`、`provider-error-feedback.json`。
- [x] **AC2 network profile 表单**：列表 + 新建/编辑/删除 + `test`（显示诊断结果）+ `resolve`（显示解析结果）。→ **MET**：「Network Profile 管理」卡（Direct/System/HTTP/HTTPS/SOCKS5；proxy_endpoint 规则；verify_tls/确认关闭 TLS/fallback；设为默认/清除默认；测试网络显示 Core 6 段真实诊断；解析网络显示 network_profile_id/mode/source；不可用显示「不可用」不伪造）。证据：`settings-profile-ui/network-create.json`、`network-test-resolve.json`、`network-tls-confirmation.json`、`network-default-delete.json`。
- [x] **AC3 绑定/默认**：profile 绑定到 slot（bindings set/clear）、设默认 network profile。→ **MET**：「Provider 绑定（slot）」卡（scope global/book/chapter + capability + provider profile → bindings set/clear/resolve）；Network 卡内 default set/clear。证据：`settings-profile-ui/bindings-set-clear.json`、`network-default-delete.json`。
- [x] **AC4 测试**：Headless 覆盖 CRUD 调用参数、错误提示、空态；真机截图一次。→ **MET**：10 项 headless（CRUD 精确参数、typed 错误、空态、test/resolve 渲染、TLS 确认、bindings scope、页面接线、payload 契约）；真机截图 2 张（provider/network 卡片，含 ScrollViewer 修复）。证据：`settings-profile-ui/*.json`、`real-app-provider-profile.png`、`real-app-network-profile.png`。
- [x] **AC5 回归/门禁**：test.ps1 全绿（≥198）；vitest 60/567；pytest 无新增失败；check.ps1 -TaskPath PASS；64-hex pin；Handoff。→ **MET**：test.ps1 **210/210**（61/55/94，0 skipped）；vitest **60/567**；pytest **3F/2772P/9S**（同一组 3 失败，0 新增）；check PASS；19 条 pin；Handoff 含 Record Decision。

## Record Decision（摘要，完整版在 Handoff / REPORT）

| 项 | 决定 |
|---|---|
| schema | 严格按 P15：capabilities ∈ CAPABILITY_NAMES；mode ∈ Direct/System/HTTP/HTTPS/SOCKS5；provider update 不带 provider_id；network create 可选 verify_tls/fallback，update 必填，关闭 TLS 需 confirm |
| payload | App `SettingsProfilePayload` 显式构造，键与 dispatcher 完全一致（NULL 显式、scope 只含 kind[/book_id|chapter_id]）；headless 契约测试钉住 |
| 空态/不可用 | 空列表显示空态文案；test/resolve 在无结果时显示「不可用」，**绝不伪造 passed** |
| typed 错误 | SETTINGS_ITEM_NOT_FOUND / SETTINGS_CONFLICT / SETTINGS_INVALID_INPUT / TLS_CONFIRMATION_REQUIRED / SETTINGS_UNAVAILABLE → 中文可操作提示 |
| 页面可达性 | 新增卡片后设置页超窗口高度 → 内容行改 `ScrollViewer`（真机截图发现并修复） |
| 测试边界 | 用 FakeHostController 记录参数，不污染真实 `%APPDATA%`；真实 Core 链路由既有 NS-WIRE-B2 冻结 sidecar 测试覆盖 |

## 实现摘要（全部 `apps/desktop-avalonia/**`）

- `Services/SettingsProfileContracts.cs`（新）：capability/mode 常量、profile 记录、scope、typed result、15 条命令 payload 构造、`SETTINGS_*` 映射。
- `Services/IHostController.cs` / `HostController.cs` / `NullHostController.cs`：新增 12 个 profile/binding/default/test/resolve seam 实现（list 解析 profiles[]/credential_state/tls_verification_state；错误映射 typed）。
- `Views/ProfileSections.cs`（新）：ProviderProfileSection / NetworkProfileSection / ProviderBindingsSection（列表/表单/空态/诊断/错误）。
- `Views/Pages.cs`：SettingsPage 嵌入三卡 + `RefreshProfilesAsync()`；内容行改 ScrollViewer。
- `Views/MainWindow.axaml.cs`：Host 就绪/进入设置页刷新 profile 列表。
- `tests/NewManga.App.Tests/SettingsProfileUiTests.cs`（新，10 项）+ `FakeHostController` 扩展。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| SP-TEST-SUMMARY | AC5 | verification/SETTINGS-PROFILE-UI-1/test/summary.json | f2cf8734325c2597d46c064e36b7824bb4cfe2ec | a2050faaab4233900b7d5bac8421b021dd0f59abcca87b50704286c0453a64b2 | CANONICAL |
| SP-TEST-LOG | AC5 | verification/SETTINGS-PROFILE-UI-1/test/dotnet-test-Debug.log | f2cf8734325c2597d46c064e36b7824bb4cfe2ec | 9e1462d7b67f6c8661db5d6a7bb638b38004eb5c7eeed7ddfb28e5dccf64fa14 | CANONICAL |
| SP-VITEST | AC5 | verification/SETTINGS-PROFILE-UI-1/test/vitest.log | f2cf8734325c2597d46c064e36b7824bb4cfe2ec | 22894c49d2e8d7d0b9754994d60fb29c786d513cf3eb30f8c25ed108efa6a075 | CANONICAL |
| SP-PYTEST | AC5 | verification/SETTINGS-PROFILE-UI-1/test/pytest.log | f2cf8734325c2597d46c064e36b7824bb4cfe2ec | 1e007d04c540ccf740433cd1f3669adc7d9cd47dee12a63f0f06366d7df1c8e3 | CANONICAL |
| SP-TEST-PS1-LOG | AC5 | verification/SETTINGS-PROFILE-UI-1/test/test.ps1-final.log | f2cf8734325c2597d46c064e36b7824bb4cfe2ec | 59ca519701cf400130d7686b6c9b87a711226012961432ddefa9895885eed7b4 | CANONICAL |
| SP-PROVIDER-CREATE | AC1/AC4 | verification/SETTINGS-PROFILE-UI-1/settings-profile-ui/provider-create.json | f2cf8734325c2597d46c064e36b7824bb4cfe2ec | 1ea0ff6ecc28fbb480f56b1eb85c78308b9fac1c3e0e8f30a1e73dedd442ea1f | CANONICAL |
| SP-PROVIDER-UPDATE-DELETE | AC1/AC4 | verification/SETTINGS-PROFILE-UI-1/settings-profile-ui/provider-update-delete.json | f2cf8734325c2597d46c064e36b7824bb4cfe2ec | 87f030ef879c12bf9fe5d0fffee0df23bc08590d23141865638216bcead6eaf0 | CANONICAL |
| SP-PROVIDER-ERROR | AC1/AC4 | verification/SETTINGS-PROFILE-UI-1/settings-profile-ui/provider-error-feedback.json | f2cf8734325c2597d46c064e36b7824bb4cfe2ec | a6f3bb9ad80180fde4761c9884c010c5f97f981908274ee9dd9cbe6200bdb436 | CANONICAL |
| SP-NETWORK-CREATE | AC2/AC4 | verification/SETTINGS-PROFILE-UI-1/settings-profile-ui/network-create.json | f2cf8734325c2597d46c064e36b7824bb4cfe2ec | 1071913ce0edaf3799045960b9cf863995af526dcf63dc7b871ec84685cfe2fb | CANONICAL |
| SP-NETWORK-TEST-RESOLVE | AC2/AC4 | verification/SETTINGS-PROFILE-UI-1/settings-profile-ui/network-test-resolve.json | f2cf8734325c2597d46c064e36b7824bb4cfe2ec | f6abab106cbc481001f71f9e17d17920466a745c1826f7d3a2baee6cdc737311 | CANONICAL |
| SP-NETWORK-TLS | AC2/AC4 | verification/SETTINGS-PROFILE-UI-1/settings-profile-ui/network-tls-confirmation.json | f2cf8734325c2597d46c064e36b7824bb4cfe2ec | c76266823372c976724b829a5b82449d68ee91b412a30ec96e7c75299336d6ae | CANONICAL |
| SP-NETWORK-DEFAULT-DELETE | AC2/AC3/AC4 | verification/SETTINGS-PROFILE-UI-1/settings-profile-ui/network-default-delete.json | f2cf8734325c2597d46c064e36b7824bb4cfe2ec | 4d98a56501b3c1b80a9124c535dd0796baa4b6bd7ccea1cf22990f44669b2b43 | CANONICAL |
| SP-BINDINGS | AC3/AC4 | verification/SETTINGS-PROFILE-UI-1/settings-profile-ui/bindings-set-clear.json | f2cf8734325c2597d46c064e36b7824bb4cfe2ec | 12bd6ae06e76565fe48c6cbf8eef73dfb3328dc6ef34c8ecdcc95f997dccc708 | CANONICAL |
| SP-SETTINGS-WIRING | AC4 | verification/SETTINGS-PROFILE-UI-1/settings-profile-ui/settings-wiring.json | f2cf8734325c2597d46c064e36b7824bb4cfe2ec | e3a404702b601231d068015b41ea589fbe2f7a126175079dd1035063eb6f7ffd | CANONICAL |
| SP-PAYLOAD-CONTRACT | AC4 | verification/SETTINGS-PROFILE-UI-1/settings-profile-ui/payload-contract.json | f2cf8734325c2597d46c064e36b7824bb4cfe2ec | 7d6f535b9a1502695e92945f123c46af9d5f0b7e7a8375b61ebb682c6b644b96 | CANONICAL |
| SP-REAL-PROVIDER-PNG | AC4 | verification/SETTINGS-PROFILE-UI-1/real-app-provider-profile.png | f2cf8734325c2597d46c064e36b7824bb4cfe2ec | e2a46f3344451456fc3ea15be7fae9ff1ae001dade7105e609dc95f178c06e40 | CANONICAL |
| SP-REAL-NETWORK-PNG | AC4 | verification/SETTINGS-PROFILE-UI-1/real-app-network-profile.png | f2cf8734325c2597d46c064e36b7824bb4cfe2ec | 0d3cb2f86f0efa479e3e98d084e3b3ba8862fdd7f5e44ccedab82002ba2f397b | CANONICAL |
| SP-REAL-META | AC4 | verification/SETTINGS-PROFILE-UI-1/real-app-screenshots.json | f2cf8734325c2597d46c064e36b7824bb4cfe2ec | f9c6a9ccd83ee599a8b0c49ac3ea7ce9f38053017b995682920f0e53d1284cf2 | CANONICAL |
| SP-REPORT | AC5 | verification/SETTINGS-PROFILE-UI-1/REPORT.md | f2cf8734325c2597d46c064e36b7824bb4cfe2ec | fbe67d082c69e9cf64268eac92503f6601bb0f75fa11bef6135f7bfc6540c03a | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/SETTINGS-PROFILE-UI-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/SETTINGS-PROFILE-UI-1 | `evidence/`（test/settings-profile-ui/logs）+ `screenshot-root/`（隔离数据根） | 2026-10-27 收口时存在；`settings-profile-ui/*.json` 与 `test/summary.json` 引用其路径；未移动/未删除；关闭时由 DSH 复核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写（owner 交付 `f2cf87343`，待 DSH 集成验证与独立 Review）。
- canonical_evidence_status：`complete`（19 条 CANONICAL pin，指向 delivery_head）。
- resource_closeout_status：`pending`（task-env + 隔离截图数据根保留引用）。
- 删除、迁移、归档数量/字节数：0（本任务未删除任何文件；真实 `%APPDATA%` 未触碰）。
- 未关闭项及保留原因：真实 Host 全链由既有冻结 sidecar 测试覆盖（本卡 UI 用 fake）；真机截图时 Host 未就绪故列表为空态；provider_id/endpoint/model 为自由文本、无建议列表；book/chapter scope 的 id 为文本框（未接选择器）；App.Tests 既有 evidence 并发写 flake 已记录；需独立 Review。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
## Review（DSH 集成复核，2026-10-27）— PASS

- 三卡：Provider Profile 管理（CRUD + 空态 + typed）、Network Profile 管理（CRUD + test 真实六段诊断 + resolve + 默认切换）、Provider 绑定 slot（scope global/book/chapter + capability + set/clear/resolve）。
- 真机发现并修复：设置页内容行改 ScrollViewer（新卡被窗口裁切）。
- 证据：10 项 headless（CRUD 精确参数、typed 错误 0 调用、空态、test/resolve、TLS_CONFIRMATION_REQUIRED、15 条 payload 键集契约）+ 真机 2 张截图。
- 回归：DSH 复跑 test.ps1 见执行记录（实现方报 210/210：61/55/94）；vitest 60/567；pytest 3F/2772P/9S（0 新增）。
- 遗留：book/chapter scope 仍手填 id（需选择器）；provider_id/endpoint 自由文本无建议；截图时 Host 未就绪列表空态。
- 集成：31cf7f1ce。
