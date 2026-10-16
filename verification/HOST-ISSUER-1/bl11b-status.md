# BL-11b 与本次 Cargo 测试口径

已知主仓/旧 worktree 基线见只读治理记录 `G:/CODEX/New Manga/.orchestrator/BL11-ENV-EVIDENCE.md`：旧 `cargo test --locked` 记录为 `58 passed / 6 failed / 1 ignored`，主仓对照相同；六项依赖打包 sidecar 的测试因协议 2.3 源码与旧 bundle 不匹配报 `PROTOCOL_VERSION_UNSUPPORTED` / `CORE_UNAVAILABLE`。这仍是 BL-11b，未由本 Task 重建 bundle。

本 worktree 本次测试使用 `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe`（Python 3.12.3，含 Pillow），并显式设置 `M2RC1_SRC_ROOT` 指向当前 worktree `src`。在同步旧 Rust 测试中的协议断言至 `2.3` 后，`cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml` 结果为 `76 passed / 0 failed / 1 ignored`，exit `0`；原始日志是 `cargo-test-full-python312.txt`。

两组结果口径不同：本次 full suite 的真实 Core 调用直接运行当前 Python 源码；没有重建或验证已知过期的打包 sidecar，也没有新增针对 HostControl 六操作的 live packaged E2E。因此本次通过证明 Rust build、Host issuer 单测和对当前源码 sidecar 的既有测试通过；不证明 packaged host issuer 已端到端可用。已知 BL-11b 的六项失败仍须由重建 bundle 的独立债务处理。
