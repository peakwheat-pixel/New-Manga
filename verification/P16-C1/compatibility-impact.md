# P16-C1 rev 2.1 兼容性与破坏性影响

**契约：** `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`

**基线：** rev 2.0 / protocol `new-manga.core` major 2, minor 0

**目标：** rev 2.1 / protocol major 2, minor 1

## 版本变化与影响

- 协议 **minor `0→1`，major 保持 `2`**。本次只新增冻结命令 `GetReaderProjection`、`SaveReadingProgress`、`StartExport`、`CancelExport`、`GetExportSnapshot`、`GetExportHistory`，以及 `ReadingProgressChanged`、`ExportProgressChanged`；不删除、改名、改变类型/必填性或重解释任何既有冻结字段、命令、状态、错误或事件。
- rev 2.0 中 Reader 命令仍为 PROPOSAL，Export IPC 未实现，Export progress event 为 UNKNOWN/PROPOSAL。因此本次冻结不改变既有已发布 wire 的行为，也没有一个已冻结 Reader/Export consumer 要迁移。**P13 Run wire 不变**：`StartRun`、Run 控制/查询命令、§5.5、§6.1 投影和四类 Run 事件逐字语义保留。
- minor widening 不是新能力的向后实现：rev 2.0 客户端不能调用新增 Reader/Export 命令。要使用新面，客户端和 Core 必须按 rev 2.1 配对。契约没有版本协商或自动迁移，也不承诺 Core 同时服务不同 minor；未知 event/status 仍按 §3 显式保留/处理为 `UNKNOWN`。
- 破坏性影响限于**能力/部署配对**：旧客户端没有 Reader/Export 命令，不能获得该能力；请求 rev 2.1 命令的客户端不能连接只实现 rev 2.0 的 Core。既有冻结命令的旧消费者不因本修订改变 payload/result/error 语义。实现状态为 `NOT_IMPLEMENTED`，本文件不宣称生产兼容性已经实测。

## 授权边界影响

P16 Python IPC Runtime 仅可在 §12 列出的 allowlist 内实现 Reader/Export command handlers、snapshot/event、`ExportTargetRef` Core-side grant validation/resolution 与 ExportHistory；不得改 React/WebView、Tauri/Rust、QML、Schema/migration、依赖、其他产品行为或授权外模块。Tauri host issuer 的实现仍须其自身获授权的 Task；这是实现分工，不改变本次冻结的 issuer/scope/expiry/replay wire 语义。

## 写引用兼容与安全影响

- `StartExport` 不接受任意目标路径字符串，只接受 Tauri host 签发的 `ExportTargetRef`。它绑定当前 host session、一个精确输出文件、一个 `format`、host 的替换授权和 300 秒绝对 TTL；一次调用消费且不滑动续期。Python Core 必须验证 issuer 签名与 scope 后经 Core-side grant resolver 解析，非 host、过期、撤销、重放或越 scope 一律拒绝。
- React/WebView 从不接收 token 或目标路径。Core 的输出路径仅在可信 Core↔Tauri 面供 ExportHistory 使用；host 不把它转发到 WebView。该约束与 `ImportSourceRef` / §10.1–§10.2 同源：同为 host 授权、opaque、scoped、expiring、Core-resolved；import 是只读且可续期，export 是一次性写目标。
- Export 仅写授权输出、该目标下的临时 staging 和 ExportHistory。输入 source、Managed Copy、译图 artifact 及 current/pinned Revision 均零写；失败/取消清理未发布临时文件。已原子发布的输出不因之后的取消被删除。

## 验收状态

本文件和 [覆盖对照表](coverage-matrix.md) 只证明契约设计覆盖；没有运行 runtime、迁移、导出格式、安全专项、外部阅读器、性能或 Windows smoke 测试。下游实现/验收仍须按 P16/P17 正式 Task 和 AC 门槛执行。
