---
id: CREDENTIAL-PORT-1
title: Host 凭据管理器端口（解除 credential_put/clear BLOCKED）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_goal_auto_except_recommended
suggested_owner: core-admin-rca
owner: null
reviewer: dsh
depends_on: []
base_commit: e30149258
branch: task/CREDENTIAL-PORT-1
worktree: G:/CODEX/New Manga.workspace/worktrees/CREDENTIAL-PORT-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/CREDENTIAL-PORT-1
allowed_paths:
  - doc/tasks/CREDENTIAL-PORT-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/CREDENTIAL-PORT-1/**
  - G:/CODEX/New Manga.workspace/task-envs/CREDENTIAL-PORT-1/**
  - G:/CODEX/New Manga.workspace/worktrees/CREDENTIAL-PORT-1/**
---

# CREDENTIAL-PORT-1：Host 凭据管理器端口

## 背景

NS-WIRE-B2 中 `credential_put`/`credential_clear` **BLOCKED**：Core 只有 `BindProfileCredential`/`ClearProfileCredential` 绑定面；旧壳是「Host OS 凭据存储（Windows Credential Manager）+ 交互输入」两段式；Avalonia Host 无凭据端口（旧实现 `settings_bridge.rs:288-350`）。

## Acceptance Criteria

- [x] **AC1 端口设计**：定义 Host 凭据端口（ICredentialStore 抽象 + Windows 实现：Win32 CredWrite/CredRead/CredDelete 或 DPAPI），记录与 Core `Bind/ClearProfileCredential` 的两段式协议。→ **MET**：`ICredentialStore`（Exists/Store/Read/Delete/Enumerate）+ `WindowsCredentialStore`（advapi32 CredReadW/CredWriteW/CredDeleteW/CredEnumerateW；CRED_TYPE_GENERIC + PERSIST_LOCAL_MACHINE + UTF-16LE，与冻结 Core `infrastructure.credentials.windows` 字节兼容）+ `ICoreCredentialBridge`（profiles list 冲突检查 + Bind/Clear minor 7）；两段式协议见 REPORT §1。
- [x] **AC2 接线**：`credential_put`/`credential_clear` 接线：写入 OS 凭据存储 → Core 绑定 ref；清除时清理两端；失败 typed 且不留孤儿凭据。→ **MET**：put 校验 target/intent/secret → Core 侧 create/replace 冲突判定 → 铸造 `NewManga/{provider|proxy}/{owner}/{32hex}`（与 Core `make_credential_ref` 同格式）→ vault 写入 → `BindProfileCredential`；**bind 失败删除 vault 条目（无孤儿）**。clear 走 `ClearProfileCredential`（Core 清 ref 并删 vault）+ Host 前缀清扫残留（`orphans_removed`）；两条均 **HostLocal IMPLEMENTED**（registry 66/0），失败全部 typed。
- [x] **AC3 安全**：不落明文到日志/DB；凭据不出进程（Core 只拿 ref）；错误信息不泄露 secret。→ **MET**：secret 仅存在于命令 payload 与 OS vault；Core 只收到 `credential_ref`；secret 上限 4096；证据只记 operation/target_kind/owner_hash(16)/state/orphans_removed；集成测试扫描 Host 日志 + 单元/集成全证据目录 + 提交前 verification 全目录均 **0 命中**；错误码不含 payload。
- [x] **AC4 真机/单测**：真实写入→读取→绑定→清除全链；单测覆盖（fake store）；对冻结 sidecar 真实执行断言。→ **MET**：`CredentialPortTests` 7 项：6 个 fake store/bridge 单测（ref 格式、intent 冲突、bind 失败清理、clear 清扫、非法参数、前缀与 Core 一致、secret 不泄漏）+ 1 个 `[HostSidecarFact]` 真实冻结 sidecar + **真实 Windows Credential Manager** 全链：put→vault 可读回 marker（UTF-16LE 字节兼容）→ Core 列表 configured→重复 create `CREDENTIAL_CONFLICT`→clear→vault 0 条 + Core 列表 missing→unknown profile `CREDENTIAL_NOT_FOUND` 且无孤儿；证据 `evidence/credential-port.json`。
- [x] **AC5 回归/门禁**：test.ps1 全绿；pytest 无新增失败；check.ps1 -TaskPath PASS；64-hex pin；Handoff。→ **MET**：test.ps1 **189/189**（基线 182 + 7 新测试）；pytest **4F/2771P/9S**：3 个既有 flaky + `test_plugin_sandbox.py::test_sandbox_job_kills_grandchildren`（并发重负载计时 flake，单独重跑 **PASS**）→ **0 新增失败**；`extract-command-surface.py --check` PASS（66 命令零漂移）；check.ps1 PASS；pin 见下表；Handoff 已交付。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/CREDENTIAL-PORT-1/**`、workspace。

## 禁止范围

不改 Python Core 语义/协议/旧壳、不 push、不 gc/prune；不得把 secret 写日志/DB/测试快照；不得伪造成功。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| E-CP-REPORT | AC1–AC5 | `verification/CREDENTIAL-PORT-1/REPORT.md` | `e414673a3` | `3af576b7821be24754aba36b0ea58e7cd0c40c8d58e25d1a4090d2fb30de63a6` | CANONICAL |
| E-CP-CHECK | AC5 | `verification/CREDENTIAL-PORT-1/parity-check.log` | `e414673a3` | `820f6d456abeab98d52599b5fffdfa051b58369b8a108e8860b1fde4f6db82fe` | CANONICAL |
| E-CP-CONTRACT | AC2/AC5 | `verification/CREDENTIAL-PORT-1/evidence/parity-contract.json` | `e414673a3` | `87dc2cef2ca615d65720af40005707ffb474e2aff1a9a12651c9d439bc8c0963` | CANONICAL |
| E-CP-CRED | AC4 | `verification/CREDENTIAL-PORT-1/evidence/credential-port.json` | `e414673a3` | `275f265dca9f80ba22d3cc6c112888759c324fcded12ab133b0f3323b24dc70d` | CANONICAL |
| E-CP-TYPED | AC2 | `verification/CREDENTIAL-PORT-1/evidence/not-supported-typed-errors.json` | `e414673a3` | `92ab32df0f918ffd1161521f12e3f3d49a8039b3d8063732bbd4c6f7ee214e85` | CANONICAL |
| E-CP-DOMAINS | AC2 | `verification/CREDENTIAL-PORT-1/evidence/domain-services.json` | `e414673a3` | `b41c2f3e901131e2adf32851f51f29e26b1bb6d83b8b05611e56ee98424862af` | CANONICAL |
| E-CP-DOTNET | AC5 | `verification/CREDENTIAL-PORT-1/dotnet-all.log` | `e414673a3` | `19e73aa672548089cbb0c62893cc541a4e81ea6f18a0c03d010e30fb0bf3a04b` | CANONICAL |
| E-CP-PYTEST | AC5 | `verification/CREDENTIAL-PORT-1/pytest.log` | `e414673a3` | `00e661dc51e6945c245e1aeffffbf1b92b440b34498baa1278e23e447e031c30` | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/CREDENTIAL-PORT-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/CREDENTIAL-PORT-1 | `evidence/`（test.ps1 私有证据）、`evidence-dev/`（定向开发证据） | 证据已复制到 `verification/CREDENTIAL-PORT-1/`；无真实 secret；关闭时按裁决保留/清理 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
