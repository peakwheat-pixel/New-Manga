# P09-FU2 Host issuer 待办与测试注入 seam

## Tauri host issuer 待办

本 Task 只实现 Python Core 的授权消费侧。Tauri host issuer 未实现，必须由独立授权 Task 完成：

- 仅在用户显式选择文件或文件夹后签发 ImportSourceRef；引用只含 opaque grant_id 与 host_signature，绝不把路径、URI 或文件 bytes 放入 ImportPages payload。
- 通过可信 host→Core 注册通道提交当前 host session、ImportPages 操作、user-source / read-only scope、精确文件/文件夹及其直接子项集合、签发时来源身份/尺寸/SHA-256、到期时间和签名。不得把注册 seam 暴露给 React/WebView。
- 安全建立 HMAC key 的来源、传输、轮换与进程退出清理；结束 host session、取消选择或撤销 grant 时调用 Core 撤销 seam。当前 Core 注册表按进程内存保存授权状态，重启后所有旧引用均为未知引用。
- 对文件夹只授权 P09 直接子项图片集合，并沿用自然文件名顺序；显式单文件可为 P09 图片或 PDF。

## 测试注入 seam

- CoreServiceServer._register_import_source / _revoke_import_source 是 Core 内部 host 注入 seam，不属于 JSON-RPC command surface。
- tests/core/test_p09_fu2_import_pages.py::_register_source 以测试专用 32-byte key 生成 host HMAC；issue-time facts 通过既有 HandleVerifiedFileReader.capture_facts 从只读 handle 采集。所有测试源均为 tmp_path 下自建图片/PDF。
- 测试可替换 ImportSourceGrantRegistry 的 clock 检查过期，直接 revoke 测撤销；伪造的 current session 用于 host-session 拒绝用例。HMAC key 与签名没有写入证据日志。
- 中断用 CoreServiceServer(import_cancelled=...) 注入纯内存 callback；契约没有定义 ImportPages 取消 command，因此这只验证 P09 importer 的已冻结 pending/已提交语义，不代表 UI/host 取消接线已完成。

## 已验证边界

请求拒绝路径不暴露来源路径、grant 或签名；拒绝测试比较导入前后活动 Page 行与 Managed Storage 文件快照，并比较原始来源 SHA-256。成功图片与 PDF 测试校验 Managed Copy 内容、source/Page hash、真实尺寸和页序。
