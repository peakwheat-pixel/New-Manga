# EVENTS-FWD-1 Compatibility Impact Note

## 1. 修订概述

- **协议版本**：major `2`，minor 从 `3` 提升至 `4`（`rev 2.4`）。
- **修订性质**：仅新增 host→WebView 的事件转发通道名称与 payload 安全投影（覆盖 §6.2 已冻结的六类事件：`TaskFailed`、`RunPaused`、`RunCompleted`、`CurrentPageStepChanged`、`ExportProgressChanged`、`ReadingProgressChanged`）。
- **零破坏性改动**：
  - Core 侧 stdio JSONL wire 格式、事件字段、命令 payload 与结果 DTO 完全不发生任何变更；
  - Tauri 命令面（18 条生产命令）与 ACL 完全不增加任何新命令，不暴露任何 host-only 控制能力；
  - 既有请求/响应多路复用语义不被破坏。

## 2. 兼容性矩阵

| 消费端版本 | Core 版本 | 兼容性评估 | 行为说明 |
|---|---|---|---|
| rev 2.4+ (含事件监听) | rev 2.3/2.4 (支持 §6.2 事件) | **完全兼容** | 消费端实时接收 6 类已冻结事件，收到失效提示后主动重查快照。 |
| rev 2.3 (不监听事件 / 仅轮询) | rev 2.4 | **完全兼容（降级路径畅通）** | 旧消费端不调用事件监听，按既有 `GetRunSnapshot` / `GetTaskProjection` / `GetExportSnapshot` 轮询工作，行为与此前完全一致（P14 轮询降级路径不被阻断）。 |
| rev 2.4+ | 旧 Core (未发事件) | **安全向后兼容** | 消费端未收到事件推送时，仍可依赖快照查询或轮询保障功能可用性。 |

## 3. 安全与隔离纪律

1. **绝对路径与凭据下发禁止**：事件 payload 严格过滤，绝不包含任何操作系统路径、`ExportTargetRef`、`ImportSourceRef`、`ResourceRef`、签名材料或二进制字节（对齐 §10.2 / §10.3 / §10.4）。
2. **事件 ≠ 真值**：事件仅为失效提示，消费方收到后强制重查快照（对齐 §6.2 与 P11 §7.1/§7.3），禁止从事件重建持久状态。
3. **未冻结事件 Fail-Closed**：未冻结的 `CoreAvailabilityChanged`（G16）与 `ImportProgressChanged`（G26）明确排除，host 侧绝不向 WebView 转发。
