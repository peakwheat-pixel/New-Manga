继续 P04 R1 返修。你上一轮在 library_bridge.rs 中复制了 round_trip 的写入/读取/解码逻辑，AC2 测试调用的是 round_trip_with_phase_hook，而不是冻结要求的同一个 StdioLibraryChannel::round_trip 方法。因此从 Task 角度 P1-1 仍未闭合；Codex 已在 verification/P04/codex-checkpoint-p04-r1-revision-codex-review-20261010.md 记录此点。

请在当前分支继续：
- 让并发测试线程实际调用 StdioLibraryChannel::round_trip。
- 保留 Alpha 写后暂停、Beta 写后先读、Alpha 后读的确定性编排，且只添加 #[cfg(test)] 的同步钩子/观测设施；不得复制 round_trip 实现，不得改变 release/production behavior。
- 可以在真实 round_trip 内部调用一个仅在 test build 编译的 hook（或通过等价、最小的 test-only seam），确保非 test 编译完全没有新增行为/字段/依赖；不要新增生产协议校验。
- 诊断仍需捕获请求、两条原始 response 线（可用测试专属 observer 或 sidecar 原始输出记录）、caller/token 归属和 behavior=PASS|FAIL；错配只记录，不 panic、不写假 PASS，并遵守 AC3。
- 如果用当前冻结契约无法让实际 round_trip 以确定方式执行这种交错，而需要生产行为改动，请停止代码交付并告知 Codex 采取 AC3 blocked + 独立 seam/修复 Task；不得自行改变产品行为。

其余 R1 项按现状保持：sidecar 缺失 fail-fast、禁止 M2RC1_PYTHON PATH fallback、记录 sys.executable/sys.version、每次独立诊断路径。不得运行 Cargo/Tauri/Rust test/sidecar/build/Sandbox/host inventory 或产品验收；只读分析与 git diff --check 可以运行。

先阅读最近的 Codex checkpoint 与实际 HEAD。只提交允许路径，保留其它工作区文件。更新返修 Handoff 的固定 commit/head；将测试状态保留 BLOCKED / NOT_RUN，不做自我 Review。
