# AC7 — credential、签名与 scope

## Session key 管理

- Host 在创建 session 时通过 `OsRng` 生成独立的 32-byte `host_session_credential`、随机 `host_session_id` 和 32-byte HMAC-SHA256 signing key。Credential 与 signing key 不复用。
- Credential 与 signing key 仅保存在 Rust `StdioLibraryChannel` 的 `HostSession` 内存态；没有写入文件、环境变量、WebView command 参数或返回 DTO。Core 注册 grant 时经同一受信 child stdio 接收所需的签名材料。
- 每条已认证 HostControl envelope 都同时带 `core_session_id`、`host_session_id` 和 credential。Core 对 credential 失效、session 关闭和 core session 不匹配分别拒绝。
- 正常 host channel drop 时发送 `CloseHostSession`，随后关闭 `bootstrap.core_service` 子进程；Core session 关闭会撤销其 grants。进程轮换会建立新 child、新 session 与新 key；Core 不允许同一进程重新打开已关闭的 host session。Import/Export grants 使用契约规定的绝对 300 秒过期。
- 本实现不做持久化 key “加载”：key 生命周期限制在一个 Core child/session 内。当前没有跨进程恢复 session 的功能或 wire。

## 伪造与越 scope

- HMAC-SHA256 实现通过 RFC 4231 vector；Import signature 与 Core canonical JSON vector 一致；Export signature 与 Core NUL-joined vector 一致。对应单测在 `cargo-test-host-unit.txt` 中通过。
- Import ref 仅含 `grant_id`、`host_signature`；Export ref 使用冻结的 `etref1.<grant_id>.<signature>` 格式。Rust 不扩展 ref wire。
- Import 只接受图片或 PDF 文件；目录只取直接子项图片，不递归；路径必须绝对、无 `.`/`..`，拒绝 reparse/symlink。Export 先按 Core 的 `StartExport` 字段集合与 format/options 校验，再将 picker 选出的单一目标绑定到 grant。
- Core 侧伪造/越 scope、超期、撤销的零副作用拒绝沿用 `verification/P09-FU2/logs/ac2-ref-rejections-zero-side-effects.txt` 与 `verification/P16/ac3-target-ref-matrix.md`；这些是 Core consumer 既有证据，不代表本 Task 已进行打包产品 E2E。
