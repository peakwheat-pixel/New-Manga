# P19-AC3-1 WebView 访问面证明

## 前端实际 API 使用

- React/TypeScript 代码中唯一 `@tauri-apps/api` 导入为 event listener；唯一 app bridge 调用面为 `window.__TAURI__.core.invoke`。实际代码引用：
  - `apps/desktop/frontend/src/App.tsx:25 __TAURI__?: { core?: { invoke: InvokeFn } };`
  - `apps/desktop/frontend/src/App.tsx:27 const invoke = globalWindow.__TAURI__?.core?.invoke;`
  - `apps/desktop/frontend/src/events.ts:77 ? (window as unknown as { __TAURI__?: { event?: { listen: ListenFn } } })`
  - `apps/desktop/frontend/src/events.ts:79 if (globalWindow?.__TAURI__?.event?.listen) {`
  - `apps/desktop/frontend/src/events.ts:80 return globalWindow.__TAURI__.event.listen;`
  - `apps/desktop/frontend/src/events.ts:83 const tauriEvent = await import("@tauri-apps/api/event");`
  - `apps/desktop/frontend/src/library/client.ts:14 ? (window as unknown as { __TAURI__?: { core?: { invoke: InvokeFn } } })`
  - `apps/desktop/frontend/src/library/client.ts:16 const invoke = globalWindow?.__TAURI__?.core?.invoke;`
  - `apps/desktop/frontend/src/reader/client.ts:20 ? (window as unknown as { __TAURI__?: { core?: { invoke: InvokeFn } } })`
  - `apps/desktop/frontend/src/reader/client.ts:22 const invoke = globalWindow?.__TAURI__?.core?.invoke;`
  - `apps/desktop/frontend/src/reader/ReaderPage.tsx:40 const defaultInvoke = typeof window !== "undefined" ? (window as unknown as { __TAURI__?: { core?: { invoke: InvokeFn } } }).__TAURI__?.core?.invoke : undefined;`
  - `apps/desktop/frontend/src/region/client.ts:31 ? (window as unknown as { __TAURI__?: { core?: { invoke: InvokeFn } } })`
  - `apps/desktop/frontend/src/region/client.ts:33 const invoke = globalWindow?.__TAURI__?.core?.invoke;`
  - `apps/desktop/frontend/src/settings/client.ts:45 ? (window as unknown as { __TAURI__?: { core?: { invoke: InvokeFn } } })`
  - `apps/desktop/frontend/src/settings/client.ts:47 const invoke = globalWindow?.__TAURI__?.core?.invoke;`
  - `apps/desktop/frontend/src/workbench/WorkbenchPage.tsx:246 __TAURI__?: { core?: { invoke: InvokeFn } };`
  - `apps/desktop/frontend/src/workbench/WorkbenchPage.tsx:248 const found = globalWindow.__TAURI__?.core?.invoke;`
- frontend/package.json runtime dependencies：`@tauri-apps/api`, `react`, `react-dom`；没有 SQLite driver、filesystem plugin、SQL plugin 或模型 runtime。
- Rust direct plugin dependencies：dialog, opener（dialog/opener 由 Rust 调用）；没有 fs/sql plugin dependency。`withGlobalTauri=true`，因此 WebView 有 Tauri JS bridge 对象，但 IPC 权限仍由以下 Capability 限制。
- Capability `m2rc1-command-surface` 只匹配 window `main`，列出 58 个 app command 权限；另外只有 `core:event:allow-listen, core:event:allow-unlisten`。未授予 `dialog:*`、`opener:*`、`core:path:*`、`fs:*`、`sql:*`。清单：`apps/desktop/src-tauri/capabilities/m2rc1-commands.json:1-70`。
- `tauri.conf.json` 关闭 asset protocol 且 scope 为空：`apps/desktop/src-tauri/tauri.conf.json:10-15`。WebView 不能借 asset protocol 读取 path。
- 应用 ACL 只授权列出的 58 个命令，其他命令由 ACL 拒绝：`apps/desktop/src-tauri/build.rs:31-53`；production invoke handler 不包含 probe/AC1 面：`apps/desktop/src-tauri/src/main.rs:1482-1538`；host-only operations 不在 WebView command set：`apps/desktop/src-tauri/src/main.rs:2506-2522`。

## 越权反例（静态 ACL 自检）

`raw/scan.stdout.txt` 内 `NEGATIVE_ACL` 记录逐项断言下列调用没有 capability permission / app handler，并打印 `DENIED_BY_CAPABILITY`。这是基于已构建 app ACL 清单和运行时注册面的静态反例；本 Task 没有启动桌面应用或伪装成 live WebView invocation。

| 反例调用 | 检查结果 |
|---|---|
| `register_catalog` | DENIED_BY_CAPABILITY |
| `OpenHostSession` | DENIED_BY_CAPABILITY |
| `BindProfileCredential` | DENIED_BY_CAPABILITY |
| `plugin:fs|read_text_file` | DENIED_BY_CAPABILITY |
| `plugin:sql|select` | DENIED_BY_CAPABILITY |
| `plugin:dialog|open` | DENIED_BY_CAPABILITY |
| `plugin:opener|open_path` | DENIED_BY_CAPABILITY |
| `plugin:path|resolve_directory` | DENIED_BY_CAPABILITY |

`fs`/`sql` 未注册；dialog/opener 虽在 Rust 初始化，但 Capability 没有授予对应 plugin permission。`core:path` permission 同样未授予。产品实际对外唯一 native data/mutation 路径是 ACL 白名单内的 Tauri invoke command；业务 IPC 的 Core 返回细节见命令矩阵。

边界结论限定于当前源码/锁定依赖的静态配置。Live GUI 的 CUA/UIA 或进程级 runtime injection 未执行。
