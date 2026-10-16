# P16-C1 导出目标授权边界记录

**Status:** `RESOLVED_BY_COORDINATOR_ARCHITECTURE_RULING`

**Task:** P16-C1

**Observed:** 2026-10-16

**Branch / base:** `codex/P16-C1-reader-export-ipc-contract` / `ff9633b5b09d8a898f92722a728edd3ff14da2d5`

## 原始阻塞事实

- D04 §37 要求用户选择导出目标并查看/打开所在文件夹；D08 AC-EXPORT-002 要求 ExportHistory 记录输出路径。
- M2-C1 §10 禁止把前端路径本身作为写权限。原有 `ImportSourceRef` 只覆盖 Core 控制的读取引用，没有冻结 Export 写目标。
- 因此 rev 2.0 尚无可用于 `StartExport` 的授权 wire。

## Coordinator 架构裁决

Coordinator 选定**可信 Tauri host 中介**：Tauri host 签发不透明、受限、过期且一次消费的单目标写引用；Core 校验 issuer/signature、scope、expiry/replay 并解析受限 grant；React/WebView 不接收引用或路径。该决定属于实现边界，不构成新的产品取舍，与 `ImportSourceRef` / §10.1–§10.2 同源。

## 解除与落地

本 blocker 已由用户在 2026-10-16 同会话续接中转述的 Coordinator 架构裁决解除。P16-C1 据此冻结了 rev 2.1 的 `ExportTargetRef` 及 §10.3；没有剩余产品决策阻塞。具体签名算法/token 编码由获授权 Runtime Task 在冻结语义内选择，Tauri host issuer 实现不属于本次 Python-only Runtime 授权。

证据：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` §5、§6.3、§10.3、§12；`verification/P16-C1/coverage-matrix.md`；`verification/P16-C1/compatibility-impact.md`。
