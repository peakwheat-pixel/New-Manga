# P02 Tauri 构建源码树副作用调查 r1

- 时间：2026-10-09 UTC
- 类型：只读代码/配置调查
- 调查者：Codex 使用只读 Explorer Agent；该调查不是 P02 Owner 交付或 Review。
- 状态：未运行构建、产品测试或真实 WebView。

## 发现

`apps/desktop/src-tauri/build.rs` 调用 `tauri_build::try_build`。当前锁定的 `tauri-build 2.7.0` 会生成 command permission 文件和 `gen/schemas/**`，写入位置位于源码树。被调用的 `tauri-utils` `write_if_changed` 按字节完全一致才跳过写入；因此生成内容的 LF 与 Windows Git checkout 的 CRLF 不同也会触发重写。全局 `core.autocrlf=true`，仓库没有适用于这些路径的 `.gitattributes` 覆盖规则。已有 Antigravity 中断现场的 24 个 tracked 差异是 2 个 schema JSON 与 22 个自动生成 TOML；忽略行尾空白后无差异，但这些文件仍受保护。

`CARGO_TARGET_DIR` 只移动 Cargo 编译产物，不能重定向 Tauri 对源码树的生成写入。`build.rs` 另检查固定源码路径 `apps/desktop/src-tauri/target/core-sidecar/core-sidecar`；Tauri 配置还从 `../frontend/dist` 读取前端资源。不得假定这些输入与当前提交匹配或可安全覆盖。

## 评估与限制

在新、独立、clean worktree 中用 `git -c core.autocrlf=false worktree add` 检出 LF，可能避免已观察到的行尾重写；本调查没有创建此 worktree或运行构建验证该假设。因此这是候选缓解措施，不是安全证明。旧 ZCode 命名 owner worktree 中的 24 个差异、Cargo 产物和 `cdp_probe.py` 保持原位并排除于任何后续交付。真实构建/WebView Gate 保持 `NOT_RUN`。

## 检查依据

- `apps/desktop/src-tauri/build.rs`：sidecar 前置检查与 `tauri_build::try_build` 调用。
- `apps/desktop/src-tauri/tauri.conf.json`：frontend dist 和 sidecar 资源输入。
- Cargo.lock 确定的 `tauri-build 2.7.0` / `tauri-utils 2.9.3` 源码：生成调用和逐字节写入判定。
- [`antigravity-dispatch-r1.interruption.md`](antigravity-dispatch-r1.interruption.md)：受影响路径和现场保护证据。

调查未验证 build/cache side effect beyond observed source-tree paths；不据此声称新 worktree build-safe。
