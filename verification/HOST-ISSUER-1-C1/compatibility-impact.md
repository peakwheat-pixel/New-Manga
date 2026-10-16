# HOST-ISSUER-1-C1 兼容性与破坏性影响

## 修订范围

- 契约从 rev 2.2 / protocol `2.2` 增至 rev 2.3 / protocol `2.3`，minor `2→3`，major 不变；按 §3.2 仅新增 host-control wire。
- 新增 §5.7 `OpenHostSession`、`RegisterImportSource`、`RevokeImportSource`、`RegisterExportTarget`、`RevokeExportTarget`、`CloseHostSession`。
- 明确既有 §10.3/§10.4 grant 同时受 host session 与 live Core process session 约束；新增 `core_session_id` 和 `host_session_credential` 仅位于 host-control envelope / Core 内存控制状态。
- 明确 §11 仅将 host grant registration/revoke 的授权握手从 `UNKNOWN / NOT_IN_SCOPE` 冻结为 `FROZEN`。序列化库、产品 Tauri command names 与 process supervision 仍按原状态保留为 `UNKNOWN / NOT_IN_SCOPE`。
- §12 授权范围只新增 `src/bootstrap/core_service.py` 与 `tests/core/**`。没有授权或修改 runtime。

## Host-only 边界表达与拒绝

1. Tauri host 直接 spawn 并持有 `bootstrap.core_service` 子进程的既有 stdio JSON-lines channel（`StdioLibraryChannel`）；HostControl 使用独立 envelope 走同一条 host-owned 进程通道，不新增监听器或 sidecar，也不经 `core_bridge.rs` resource sidecar。不得监听网络/公开 socket、不得转交 WebView。HostControl 不属于普通 §3 application command surface。
2. 首次 `OpenHostSession` 由 Tauri host 在向 WebView 暴露普通 Core 操作前通过该私有通道发送，host 创建并私有保存 32-byte CSPRNG credential。Core 返回当前进程 `core_session_id`；之后每个 HostControl 请求必须携带 `host_session_id`、`host_session_credential` 与 `core_session_id`。
3. Core 只在当前 live Core、当前唯一活动 host session、credential 恒时比较成功时进入既有 `_register_*` / `_revoke_*` seam。普通 application JSON-RPC 对这些操作返回 `HOST_ONLY_REQUIRED`；错误 credential/已关闭 host session 返回 `HOST_SESSION_INVALID`，旧 Core session 请求返回 `CORE_SESSION_MISMATCH`。所有拒绝都在注册或文件/数据库副作用前完成。
4. React/WebView 不接收上述 credential、session、路径、签名 key 或 ref，也没有任一 Tauri command/allowlist/capability 可调用 HostControl 注册/撤销方法；Rust 内部 bridge 不得提供 raw-Core passthrough。若后续 host Task 增加 UI-facing 用户动作命令，仍须遵守 HOST-ISSUER-1 AC5 的 Tauri 同步和测试纪律，但该命令不得代理注册/撤销 API。

该边界是契约要求，不是已运行的安全证明。Core handler、Rust host 接线、WebView 负向扫描与真实拒绝测试尚未运行。

## 对既有消费者的兼容影响

| 面 | 影响 |
|---|---|
| §3 `Request<T>` / `Response<T>` | 现有字段和成功/错误 envelope 不变。只新增一个独立 HostControl envelope。 |
| §5.6 `ImportPages` | command、payload、result、错误、导入顺序和副作用语义不变；仍只接收现有 `ImportSourceRef[]`。新的注册动作只填充同一个 live Core 实例的内存 registry。 |
| §10.4 `ImportSourceRef` | 保持 `{grant_id, host_signature}`；不新增 Core session、credential、路径或其它 ref 字段；既有 `REF_*` 不重新解释。 |
| §5 `StartExport` / §10.3 `ExportTargetRef` | `target_ref` 与导出 payload 不变；单目标、一次消费、格式/replace 限制、300 秒绝对 expiry 与现有 `REF_*` 保持。 |
| P13 / P16 / P12 冻结 wire | 本次未修改 P11、P13-C1、P16-C1、P12-C1 的行为或字段。 |
| 老版本 | rev 2.2 及更早客户端/ Core 不支持 HostControl；不得回退到公开 JSON-RPC、WebView command、路径字段或旧 sidecar。新 host issuer 必须与 rev 2.3 Core 配对；不具备 HostControl 时 fail-closed。 |

## 破坏性变更与风险

- **既有 WebView/Core 产品 wire：无破坏性字段变更。** 现有冻结 command/payload/result/error/ref shape 均不变。
- **新 host-control 能力：需双方升级配对。** rev 2.2 Core 无注册通道，不能支撑 HOST-ISSUER-1；rev 2.3 契约本身不表示 runtime 可用。版本协商与自动迁移仍未实现。
- **session 生命周期约束：一个 host session 对应一个 Core process。** `CloseHostSession`/通道断开即撤销当前 session grant；该进程不接受第二个 host session，host 轮换时须重启 Core。Core 重启后旧内存 grant 消失，新 Core session 不接受旧 ref。
- **原子撤销边界：** 成功 revoke 响应后开始的后续 grant resolve/consume 立即拒绝；已经完成原子消费的导入读取/导出任务沿 §10.3/§10.4 既有语义完成，不回滚已提交结果或新增取消行为。
- **兼容性风险：** 如果实现把 HostControl credential、control command 或签名/路径数据传给 WebView，或在注册拒绝前修改 registry/写文件/SQLite，即违反本契约；HOST-ISSUER-1 必须以实现级负向证据关闭此风险。

## 验证界限

本 Task 只修订契约。未跑 Core/Tauri/WebView runtime、构建或测试；未新增产品命令、Schema/migration、依赖或实现代码。以上为静态契约/既有 seam 对照，不是运行通过结论。
