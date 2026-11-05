# FEA-11-HOST-AUTH-1 Delivery Manifest

生成：2026-11-05（DSH closeout）。终态：`closed_with_limitations`（裁决人 Codex；用户 2026-11-05 委托）。

## 交付坐标

| 项 | 值 |
|---|---|
| Task | `doc/tasks/FEA-11-HOST-AUTH-1.md` |
| base_commit | `7ab9eea87062a44d5b08edbd507538f21443e000` |
| delivery_head | `cbd561b432f73bce3308d68366f79f408cee000a`（r8 reviewed head） |
| integration_commit | `cbd561b432f73bce3308d68366f79f408cee000a`（main 线性集成；无 merge commit） |
| 最终 Review | `doc/reviews/FEA-11-HOST-AUTH-1-r8.md` → **approved**（P0/P1/P2=0，P3=5） |
| 终态裁决 | `doc/reviews/FEA-11-HOST-AUTH-1-codex-adjudication-2026-11-05.md` → **DECISION A** |
| 证据索引 | `verification/FEA-11-HOST-AUTH-1/EV.md` |
| 变更清单 | `verification/FEA-11-HOST-AUTH-1/changed-files.txt`（23 files；A/M） |
| 门禁日志 | `verification/FEA-11-HOST-AUTH-1/logs/gates.log`（r1–r8 + closure） |

## 交付内容（实现）

- `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/CanonicalJson.cs`（canonical-json/1 + sha256；跨实现向量含 non-BMP）。
- `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostAuthorizationMinter.cs`（HostAuthorization 六字段 + Host 铸造 operation_id/host_receipt_id + canonical digest）。
- `apps/desktop-avalonia/src/NewManga.Host/Sources/HostOperationOrchestrator.cs`（Mint → Registry durable Authorize → journal → payload 注入 → Core → MarkCommitted/retry/recover）。
- `apps/desktop-avalonia/src/NewManga.Host/Sources/HostErrorCodes.cs`（C-17 §8 闭集 + retryable 投影）。
- `HostRuntime.cs` / `SourceOperationCoordinator.cs` / `HostCommandDispatcher.cs` 接线；对应测试（Fea11HostAuthTests 24/24，19 方法；Canonical+Min 11/11）。

## 证据与门禁口径

见 `EV.md`「门禁口径」节：必须区分 Host.Tests `105`（r6）与 `107`（r8）、全量 .NET `1395/0/78` 的 r8 独立来源、IPC 首次 `2/3` flake 及后续复跑；不得合并为无波动 PASS。

## 保留限制

10 项 limitation 原文见 r8；closeout 未改写、未标 PASS；AC3 保持 `PARTIAL`；AC4 按 r8 窄口径 `MET（路径层）`，不据此宣称 P0-1 全部技术工作完成。另有 Codex 裁决附加说明（ACK/recovery 使用 journal 原 authorization 的流程缺口）已按附注映射到 limitation 1/2/5/10，不修改原十项文本。

## 终态声明

- 本卡**不是** `done`；不进入 READY DAG；除新授权外不恢复实施。
- 上游 FEA-11 的硬约束（LINEAGE-1 完成前不得消费同步 binding）继续有效。
