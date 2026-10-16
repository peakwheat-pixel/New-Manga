# P14 WebView 边界核验

核验依据：Coordinator 2026-10-16 裁决 A、M2-C1 §6.4 与 §10，以及 P14 生产工作台调用链。这里的 `m2res` 例外只覆盖 Viewer 页图读取。

| 边界面 | 核对位置 | 结果 |
|---|---|---|
| 请求 | `library/client.ts`、`workbench/client.ts`、`WorkbenchPage.tsx` | 工作台命令传业务 ID、选择范围和格式选项。导入请求仅带 `chapterId` / 重复策略；导出请求不带路径或目标引用。导入和导出目标由 Tauri host 的系统选择器处理。 |
| 返回 | `library/client.ts`、`workbench/client.ts`、`workbench/client.test.ts` | 页资源解析仅给出资源 catalog ID / revision；资源发行返回短期 `m2res` URL / opaque ID / 尺寸。导出快照与历史经 allowlist 投影，路径和 target/grant 字段不会进入 Workbench DTO；测试以带路径和 `target_ref` 的输入验证投影。 |
| 事件 | `events.ts`、`WorkbenchPage.tsx` | 六类冻结事件只携带业务 ID、状态、错误码或计数；Workbench 收到事件后重查快照。未发现 `m2res` URL、文件路径、grant 或会话凭据进入事件 payload。 |
| 错误 | `workbench/client.ts`、`bookshelf/error.ts`、`WorkbenchPage.tsx` | 工作台错误通过大写稳定错误码校验；导入错误按 `code` 映射本地化文案。原始 message 不展示；无路径或凭据回显。 |
| 媒体读取、生命周期 | `workbench/pageImage.ts`、`WorkbenchPage.tsx`、`resourceChannel/client.ts` | 只有 Viewer 页图链路使用解析出的资源 ID / revision 发行 `m2res` 短期映射、分块取回 Blob 并生成 `blob:` 展示 URL；旧 Blob URL 会撤销。`m2res` URL 不进 storage、应用日志或事件 payload，也不授权写操作。 |

P14 生产工作台未将媒体 URL 用于其他业务。仓库中既有的 `App.tsx` / `ac1/driver.ts` 通道探针与 `*.test.ts(x)` 是验证资源协议的测试路径；它们不持久化完整 URL、不将 URL 写进事件或应用日志。该验证用途不改变 P14 运行时边界。

未发现文件系统路径（绝对、相对或 UNC）、`ExportTargetRef` / `ImportSourceRef` / `ResourceRef` grant 材料、`host_session_credential` / `core_session_id` 或可解码出路径的字段进入 P14 请求、返回投影、事件 payload 或用户可见错误。

