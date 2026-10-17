---
id: SEC-FIX-PATH-ECHO-1
title: 修复设置命令回显绝对路径（settings_get / settings_update_section）
kind: bugfix
governance_version: 2
status: ready
approval: coordinator_release_20261017_from_P19_AC3_1_finding
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [P15-HOST-2, P15-CORE-1C]
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
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
- [ ] **AC1**：两条命令的**响应**只包含契约允许字段；**路径类设置值必须以脱敏/占位形式返回**（如仅 basename 或 opaque id），**不得**返回绝对路径、盘符、UNC 或用户目录片段。
- [ ] **AC2**：**失败/错误**路径同样不得包含路径片段（封闭投影）。
- [ ] **AC3 反例测试**：以合成绝对路径复现原缺陷并断言**不再回显**；覆盖 `settings_get` 与 `settings_update_section`（含各 section）。
- [ ] **AC4 不回归**：Core pytest **535**、Rust source **107/0/1**（须设 `M2RC1_PYTHON`）、packaged **12/0**、前端 **278** 全不回归。
- [ ] **AC5 交付**：commit + Handoff（必须）+ Canonical Evidence（`status: in_review`；BL-15/17/19/16/18）。
- [ ] **AC6**：交付须**复跑** `verification/P19-AC3-1/repro_settings_path_roundtrip.py` 或等价脚本，证明 `path_value_returned=false`。

## 允许 / 禁止
- 允许：`src/**`（Core 投影修复为主）、必要处 `apps/desktop/src-tauri/**`、`tests/**`、本 Task、Handoff、`verification/SEC-FIX-PATH-ECHO-1/**`。
- 禁止：改契约（若需改 projection 定义 → **停下上报**）；Schema/迁移/依赖；改 STATUS/PLAN；碰用户 19 项 dirty；**不得**用"前端不再显示"掩盖（必须在 **Core/host 投影层**修复）。

## 依赖、风险与阻塞
- 前置：P15-HOST-2、P15-CORE-1C。**被阻塞方**：P19 的 AC3。
- 风险：涉及设置投影语义 → 需保持既有 `settings_update_section` 写入能力不变。

## 交付与运行记录
- 2026-10-17 Coordinator 释放（dsh, epoch 6），依据 P19-AC3-1 复现。