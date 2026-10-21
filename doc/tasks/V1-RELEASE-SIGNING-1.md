---
id: V1-RELEASE-SIGNING-1
title: v1 代码签名与发布签核（等待用户证书）
kind: release
status: in_review
approval: user_authorized_release_20261021
suggested_owner: DeepSeek Harness
owner: dsh-lead
reviewer: Codex
depends_on: [P09-MANAGED-READ-ROOT-TRUST-1, WORKSPACE-CLEANUP-TOOL-HARDENING-1]
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/V1-FINALIZE-20261021
allowed_paths:
  - doc/tasks/V1-RELEASE-SIGNING-1.md
  - verification/V1-FINALIZE-20261021
  - apps/desktop/src-tauri/target/release/bundle/nsis
created: 2026-10-21
---

# V1-RELEASE-SIGNING-1：v1 代码签名与发布签核

## 来源与目标

来源：用户 2026-10-21 裁决“2. 是”（继续 v1 发布流程），并选择“我提供 PFX 路径 + 密码（推荐）”。
目标：对 `m2rc1-desktop_0.1.0_x64-setup.exe` 完成真实代码签名、时间戳与 `signtool verify /pa`，记录 Authenticode 证据，给出“发布就绪/阻塞”的最终签核。

## 当前状态（2026-10-21）

- 安装/卸载：**DONE**。Windows Sandbox 全新环境 `setup.exe /S` exit 0、`uninstall.exe /S` exit 0；证据 `verification/V1-FINALIZE-20261021/clean-install-sandbox/`。
- 签名流水线：**已验证（非真实发布签名）**。自签名测试证书 + DigiCert RFC3161 时间戳在**副本**上 `signtool sign` exit 0、时间戳链验证通过；`verify /pa` 仅因自签名根不受信任失败（预期）。测试证书/副本已清理，源安装包 SHA-256 未变。
- 真实签名：**WAIVED（用户 2026-10-21 明确接受未签名 v1）**。本机无 Code Signing EKU 证书；安装包 `NotSigned`；按用户决定不再采购/等待证书。
- 记录：`verification/V1-FINALIZE-20261021/release-readiness.md`、`signing-pipeline-test.log`。

## 阻塞解除记录

用户 2026-10-21 明确回复“接受未签名 v1”。真实签名从 `BLOCKED` 转为 **WAIVED**；发布按未签名自用/内测版收口。

## Acceptance Criteria

- [ ] AC1 使用**真实**证书对安装包执行 `signtool sign`，exit 0，且 `/fd SHA256 /td SHA256 /tr <RFC3161>` 时间戳成功；不得使用自签名测试证书替代。 <<NOT_APPLICABLE: 用户 2026-10-21 接受未签名 v1>>
- [ ] AC2 `signtool verify /pa /v` exit 0；`Get-AuthenticodeSignature` 状态 `Valid`，签名者证书链可信。 <<NOT_APPLICABLE: 用户 2026-10-21 接受未签名 v1>>
- [ ] AC3 记录签名前后安装包 SHA-256、签名者 Subject/Thumbprint、时间戳来源、命令与 exit code，写入 `release-readiness.md`。 <<NOT_APPLICABLE: 用户 2026-10-21 接受未签名 v1>>
- [ ] AC4 若用户决定接受未签名发布：必须显式书面裁定并更新 `release-readiness.md`；否则不得发布。 <<MET: 用户明确接受未签名，release-readiness.md 已记录>>

## 允许修改范围

- 本 Task、`verification/V1-FINALIZE-20261021/` 证据目录、`apps/desktop/src-tauri/target/release/bundle/nsis/` 下的签名产物。
- 不修改源码、契约、Schema、依赖、Plan/STATUS（由 Lead/Codex 同步）。

## 禁止范围

- 不得用自签名证书冒充发布签名。
- 不得 push/GC/prune/历史重写。
- 不得在无用户书面同意时发布未签名安装包。

## 证据

- `verification/V1-FINALIZE-20261021/release-readiness.md`
- `verification/V1-FINALIZE-20261021/signing-pipeline-test.log`
- `verification/V1-FINALIZE-20261021/clean-install-sandbox/`

## Closeout Record

- 关闭日期 / 决定：2026-10-21；用户明确接受未签名 v1，Task 改为 `in_review`（发布签核待最终发布动作，不标 done 以保持 STATUS 指针合法）。
- 限制：安装包未签名，Windows SmartScreen 可能显示“未知发布者”；不可宣称已签名发布；证书采购/签名可在后续版本补做。
- 其余发布验证：全新机器安装/卸载 PASS；签名流水线已用自签名测试证书验证（非真实签名）。
