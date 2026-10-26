---
id: LEGACY-SHELL-REMOVAL-1
title: S5 旧壳退役 + tile 资源通道切换 + ADR-0002 D4 回归 + 安装包/数据升级
kind: implementation
governance_version: 3
status: blocked
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: antigravity
owner: null
reviewer: dsh
depends_on: [UI-WORKBENCH-READER-1]
base_commit: 55b7f42c6
branch: task/LEGACY-SHELL-REMOVAL-1
worktree: G:/CODEX/New Manga.workspace/worktrees/LEGACY-SHELL-REMOVAL-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/LEGACY-SHELL-REMOVAL-1
allowed_paths:
  - doc/tasks/LEGACY-SHELL-REMOVAL-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - archive/**
  - verification/LEGACY-SHELL-REMOVAL-1/**
  - G:/CODEX/New Manga.workspace/task-envs/LEGACY-SHELL-REMOVAL-1/**
  - G:/CODEX/New Manga.workspace/worktrees/LEGACY-SHELL-REMOVAL-1/**
---

# LEGACY-SHELL-REMOVAL-1：S5 旧壳退役与收口

## 前置（硬，缺一不得动旧壳）

1. **ADR-0002 D4 六项回归全绿**：等长原地重写必拒 / revoke+expiry 生效（含打断 ≤1s 缓存）/ 越界+junction+reparse 拒绝 / 篡改 tile（改字节保尺寸）拒绝 / 身份变化拒绝 / 大页冷加载 ≤60ms 且哈希开销 ≤10%。
2. tile 资源通道在 Host 落地（ADR-0002 D1–D2：Core 出 tile + per-tile digest；替代旧 URL 句柄）。
3. 真机像素 smoke（DPR2 400% 锐利、Mica 真机取色、无控制台、进程工作集峰值 ≤1.5GB）+ IME 实机（微软拼音 20 字）。

## Acceptance Criteria

- [ ] **AC1 D4 回归**：六项安全回归全部通过，证据落 `verification/LEGACY-SHELL-REMOVAL-1/security/`。
- [ ] **AC2 tile 通道**：阅读器/工作台走 tile 通道（per-tile digest 校验）；旧 URL 句柄与 no-store/每请求 SHA-256 机制仅在 D4 通过后退役；性能达 G5（单页 ≤60ms、哈希 ≤10%）。
- [ ] **AC3 旧壳退役**：`apps/desktop/**`（Tauri/React/Rust host/WebView2）→ `archive/history/2026-XX/legacy-tauri-shell/`，完成引用迁移（索引/AGENTS/ADR/检查器/README），**不删除、不 gc/prune**；新旧共存代码移除。
- [ ] **AC4 全量回归**：新壳单命令全绿；pytest 相对基线无新增失败；所有历史 UI 测试（旧壳 60/567）随归档保留说明；`command_allowlist(false,false)` parity 快照重新校验。
- [ ] **AC5 发布件**：单文件安装包（≤150MB 或含模型分离说明）+ 升级路径 + `LICENSE/NOTICE/THIRD_PARTY_LICENSES` 与源码一致；真实运行 smoke（安装→启动→书架→阅读→退出无残留）。
- [ ] **AC6 收口**：`check.ps1` PASS；Handoff；ADR-0002 验收记录；`doc/AD-002` 标记 S0–S5 完成。

## 禁止范围

未过 AC1 不得删除/退役旧机制；不改 Python Core 语义；不 push；不 gc/prune；不随包商业字体。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 六项安全回归脚本 | 无标签副本 | NOT_RUN | 待填 |
| AC2 | tile 通道性能 + digest 篡改 | 同上 | NOT_RUN | 待填 |
| AC3 | 归档 + 引用迁移检查 | 治理检查器 | NOT_RUN | 待填 |
| AC4/AC5 | 全量回归 + 安装 smoke | 干净环境 | NOT_RUN | 待填 |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/LEGACY-SHELL-REMOVAL-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/LEGACY-SHELL-REMOVAL-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
## BLOCKED（2026-10-27，实现方排查 + DSH 裁决）

**阻塞事实（repo 实测，非猜测）**：S5 第 1–2 步依赖的机制**只存在于待退役的旧 Rust 资源通道**（esource_protocol.rs/host_issuer.rs）；新 C# Host 侧 grep 	ile|digest = 0 命中，缺四块能力：① tile 通道与 per-tile SHA-256；② ≤1s 授权缓存 + revoke 失效事件；③ handle 路径重导/containment（越界/junction/reparse）；④ 大页 ≥60ms/哈希 ≤10% 的测量路径。因此 D4 六项无法证明绿，且实机 smoke（Mica 像素/工作集/IME）与安装 smoke 本会话无法诚实产出。

**DSH 裁决**：不跳步、不删旧机制（正确停在安全边界）。拆分为四个 Task 依次释放：
- **S5-A HOST-TILE-CHANNEL-1**（ready，先做）：Host tile 通道 + per-tile digest + ≤1s 授权缓存 + containment；覆盖 D4-2/4（revoke/expiry/篡改保尺寸）。
- **S5-B HOST-RESOURCE-SECURITY-1**：D4-1/3/5/6 安全等价 harness（等长重写/越界+reparse/身份变化/大页性能）。
- **S5-C**：S5-A/B 全绿后归档 pps/desktop/** + 引用迁移。
- **S5-D**：安装包/升级/许可 + 人工实机 smoke（Mica/IME/工作集）。
- S5 本卡保持 blocked 直至 A+B 完成；归档与发布不得提前。
