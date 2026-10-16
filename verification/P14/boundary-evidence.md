# P14 WebView 边界核验

核验依据：Coordinator 2026-10-16 裁决 A、M2-C1 §6.4 与 §10，以及 P14 生产工作台调用链。`m2res` 例外只覆盖生产 Viewer 页图读取；短期随机 URL / opaque handle 是显示句柄，不是写授权。

| 边界面 | 核对位置 | 结果 |
|---|---|---|
| 请求 | `library/client.ts`、`workbench/client.ts`、`WorkbenchPage.tsx` | 工作台命令只传业务 ID、选择范围和格式选项。导入请求仅带 `chapterId` / 重复策略；导出请求不带路径或目标引用。文件选择与导出目标由 Tauri host 系统选择器处理。 |
| 返回 | `library/client.ts`、`workbench/client.ts`、`workbench/client.test.ts` | 页资源解析仅给资源 catalog ID / revision；Viewer 加载时发行短期 `m2res` URL / opaque ID / 尺寸。导出快照与历史经 allowlist 投影；带 `output_path` / `target_ref` 的输入不会进入 Workbench DTO。响应 ID 使用 `isSafeUiId` 校验，包含 `C:` 盘符前缀的返回 ID 会拒绝。 |
| 事件 | `events.ts`、`WorkbenchPage.tsx` | 六类冻结事件只携带业务 ID、状态、错误码或计数；Workbench 收到事件后重查权威快照。事件 payload 不含 `m2res` URL、文件路径、grant 或会话凭据。 |
| 错误 | `workbench/client.ts`、`bookshelf/error.ts`、`WorkbenchError.tsx`、`WorkbenchPage.tsx` | UI 使用稳定错误码映射本地化说明与可重试操作，不显示原始错误 message、路径或凭据；错误码经过格式校验。 |
| 媒体读取、生命周期 | `workbench/pageImage.ts`、`WorkbenchPage.tsx`、`resourceChannel/client.ts` | P14 生产工作台仅 Viewer 页图链路从 `resolve_page_resource` 得到资源 ID / revision，再发行 `m2res` 短期映射、分块读入 Blob 并生成可撤销 `blob:` 展示 URL。URL / opaque ID 不持久化、不写应用日志或事件 payload，不用于其他业务，也不授权任何写操作。 |

生产路径复核：`App.tsx` 的 production interactive deny matrix 已移除 Viewer 之外的 `issue_resource_url` / `m2res` 调用；`App.test.tsx` 对 production startup 断言不调用 `issue_resource_url`。`App.tsx` / `ac1/driver.ts` 中剩余资源通道调用只在 host 明确开启的 probe / AC1 验收模式执行；它们不属于生产工作台显示链路，不写 URL 或 opaque ID 到日志/事件。probe 的 fresh-reference 结果仅记录布尔值。

未发现文件系统路径（绝对、相对或 UNC）、`ExportTargetRef` / `ImportSourceRef` / `ResourceRef` grant 材料、`host_session_credential` / `core_session_id` 等会话凭据或可解码出路径的字段进入 P14 请求、返回投影、事件 payload 或用户可见错误。`m2res` URL 不离开生产 Viewer 媒体显示读取路径。
