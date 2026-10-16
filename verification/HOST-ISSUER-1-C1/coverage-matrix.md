# HOST-ISSUER-1-C1 覆盖对照

基线：`6a5051dcafa549f200730a4f9824d83d187f07a2`；契约修订：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` rev 2.3；范围为契约与本 Task 证据，不含 runtime。

## HOST-ISSUER-1 AC1–AC7

| 来源条款 | rev 2.3 承载点 | 覆盖结论与剩余 Gate |
|---|---|---|
| AC1 导入来源签发 | §5.7 `RegisterImportSource` 接收 `user-source` / `ImportPages` / `read-only`、选中源、直接子项 facts、绝对 expiry、signing key 与签名；回 `{registered:true}`。host 使用 `grant_id` + 相同签名组成 §10.4 既有 `ImportSourceRef`。 | 足以让 host 在 Core registry 建立与单一来源 ref 严格对应的 grant。OS 选择/UI 仍由 HOST-ISSUER-1 自身实现；多选策略不由本契约决定。 |
| AC2 导出目标签发 | §5.7 `RegisterExportTarget` 接收精确 `target_path`、既有 `ExportFormat`、replace 权限、expiry、签名材料；host 使用同一 grant ID/signature 产生 §10.3 既有 `ExportTargetRef`。 | 足以注入单目标、单次 `StartExport` grant；scope、300 秒绝对 TTL、消费规则仍由 §10.3 定义。 |
| AC3 HMAC key 与 host session 生命周期 | HostControl 首次握手与每次请求携带 host session credential；请求同时绑定 Core 进程 `core_session_id`。grant 注册继续携带 P09/P16 seam 已要求的 `signing_key`/`signature`；凭据与签名 key 分离，均不得进入 WebView。关闭 session 撤销其 grants；Core restart 丢弃内存 registry；轮换以新 Core session 建立。 | 生命周期与 host→Core 注入通道已冻结。key 的 host 侧生成/安全存储策略仍须在 HOST-ISSUER-1 按现有 AC3 实现和验证；本 Task 不发明密码算法或持久化。 |
| AC4 host→Core 注入（不经 WebView） | §5.7 独立 `HostControl` envelope 走 Tauri `StdioLibraryChannel` 直接持有的 live-Core stdio；附 session credential/Core session 校验；普通 JSON-RPC 对保留操作返回 `HOST_ONLY_REQUIRED`。不新增 Tauri command/React callable route，也不借用 `core_bridge.rs` resource sidecar。 | 结构上只有受信 host 可发起。HOST-ISSUER-1 仍须提供实现级负向证据，证明 ref、路径、credential、签名 key 不进入 WebView。 |
| AC5 ACL / capability 与宿主同步纪律 | 本 wire 是 Core 内部 HostControl command，不是 Tauri command，不扩大 `command_allowlist`、`generate_handler!`、build app-manifest 或 capabilities。 | 本契约不要求任何 ACL 增项。HOST-ISSUER-1 若另需 WebView-facing 的用户动作命令，仍须按其 AC5 在同一 commit 同步既有 Tauri 面并测试；不得把注册/撤销操作暴露给 WebView。 |
| AC6 契约一致性 | §5.7 将请求中同一 `grant_id` / 签名映射为 §10.3/§10.4 refs；§10.3/§10.4 的字段、scope、过期、消费、revoke 与 `REF_*` 语义原样保留。 | 足以承载既有 refs；不增字段、不改签名输入或错误含义。实现仍须逐字段测试。 |
| AC7 安全 | Host-only credential/session 检查、scope/expiry/signature 校验、重复 ID 拒绝、原子 revoke 与拒绝零副作用见 §5.7。路径/key/refs 仅在可信 host/Core 边界。 | wire 已给出 fail-closed 行为；HOST-ISSUER-1 需以真实 Rust/Core 联调证明伪造、越 scope、过期、revoke 拒绝及零文件/SQLite 副作用。 |

## 相关冻结条款

| 来源 | 对照 |
|---|---|
| §10.3 `ExportTargetRef` | ref 仍是既有单目标一次性写授权，300 秒绝对过期；Core session ID 仅作为进程内注册上下文，不进入 ref 或签名对象。Host 通过 `RegisterExportTarget` 传入原有 private-seam grant facts；`RevokeExportTarget` 停止之后的解析/消费。 |
| §10.4 `ImportSourceRef` | ref 仍为 `{grant_id, host_signature}`；只读 scope、P09 直接子项/格式/事实、滑动 TTL、撤销与已打开 handle 语义均未改变。Core session ID 不进入 ref 或签名对象。 |
| §5.6 `ImportPages` | `ImportPages.sources[]` 仍仅收现有 `ImportSourceRef[]`；host 可在同一 live Core session 中逐条登记对应 grant，再按原 §5.6 payload 注入。所有引用仍须在首次读取前完整校验，拒绝不得产生 DB/temp/Managed Copy 写入。新 control channel 不改变导入、重复检测、取消、报告或多选产品策略。 |

## 依赖证据与结论

- Owner blocker assessment：`G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1/verification/HOST-ISSUER-1/blocker-assessment.md`（文件在来源 worktree 的 commit `bacf151b7` 中；本 C1 worktree 不含该目录）。其记录 live `CoreServiceServer` 私有注册 seam、缺失 dispatcher 路由、Core 实例内存 registry，以及现有 `host_bridge` 不持有 grant registry。
- P09-FU2：`verification/P09-FU2/host-issuer-and-test-seam.md`、`verification/P09-FU2/logs/ac1-importpages-stdio.txt`、`ac2-ref-rejections-zero-side-effects.txt`、`ac4-user-source-scope.txt`。已交付 Core 注入 seam；测试覆盖签名/host session/scope/expiry/revoke 与零副作用，但不实现 host issuer。
- P16：`verification/P16/host-issuer-todo.md`、`verification/P16/ac3-target-ref-matrix.md`。已交付 `ExportTargetRef` Core 校验、原子消费与写前拒绝；host 注入仍未实现。
- 只读现状：`src/bootstrap/core_service.py:1491-1558` 定义私有注册/撤销方法；dispatcher 分别处理 `ImportPages` 与 Reader/Export，没有 host grant 命令。`src/bootstrap/core_assembly.py:1204,1260` 为 live Core 实例构造内存注册表。

**覆盖结论：可以承载 HOST-ISSUER-1 AC1–AC7 的 host→live-Core 签发与注入实现。** 此结论仅指 wire 足够且没有破坏冻结面；HOST-ISSUER-1 的 runtime、Tauri host 实现、AC4/AC7 负向测试和构建仍须独立完成，不能据此标为实现 PASS。未发现必须先做的 grant 数量上限或多来源选择产品裁决。
