你是 DeepSeek Harness，受邀作为 P04 Task 的独立非作者 Reviewer。请只做只读审查，不要修改、创建、格式化、暂存或提交任何文件，也不要运行 Cargo、Rust 测试、Tauri、Python sidecar、Sandbox 或任何构建/执行命令。

## 固定审查对象
- 仓库：当前工作目录（这是 detached review worktree）。
- 期望 HEAD：751abae2277e975eddacc385a423bcd796334f97；若 HEAD 不匹配，立即报告 BLOCKED，不要继续。
- 审查实现差异：9ea4e312fa01470478946a557135791b5a044cb3..751abae2277e975eddacc385a423bcd796334f97。
- 独立核对 frozen contract：doc/tasks/P04.md；Owner=Antigravity，Reviewer=你，Codex=Integrator。也检查相关 contracts 与实际调用上下文。
- Owner Handoff：verification/P04/antigravity-owner-implementation-r1.handoff.md。

## 审查目标
按任务范围、AC1–AC4、数据安全/测试副作用和正确性评审；只报告有代码/文档证据的问题。
1. AC1：是否真的执行字面期望 `assert_eq!(PAGE_NAV_PRODUCTION_ONLY_COMMANDS, &["list_chapters", "list_chapter_pages"]);`；是否验证 production/probe/AC1 面，并避免期望由被测常量推导。
2. AC2：确定性 sidecar 与同步是否真实保证至少两个同一 `StdioLibraryChannel` 实例并发 `round_trip`；检查是否可能死锁、漏测、假通过，调用方归属是否校验了可区分响应。Task 规定不得只用 sleeps/概率循环，不新增生产协议逻辑。
3. 仅允许测试代码与 verification/P04、Task/Handoff/Review 文档；确认生产逻辑、IPC/Schema、依赖、capabilities、Python Core 未变。
4. 检查脚本和测试的副作用路径、子进程生命周期/清理、失败行为，以及 Handoff 对实现和 NOT_RUN 测试状态的表述。
5. Cargo/Tauri 测试因 P02 Gate 保持 BLOCKED/NOT_RUN，静态审查不得把运行结果写成 PASS。

## 比较范围与报告
- 只评审 9ea4e312..751abae2 的 Owner 实现差异；忽略祖先里的 D24/D25 治理变化，但检查它们在 Task 中冻结的约束。
- 输出中文 Review，首先给结论：APPROVED / CHANGES_REQUESTED / BLOCKED。
- 每项 finding 用 P0/P1/P2/P3，给出文件与行号、具体影响、触发条件、最小建议。确认没有 findings 时明确写无。
- 单独说明 AC1/AC2/AC3/AC4 的证据状态及任何无法静态证明的部分；测试仍是 NOT_RUN。
- 明确说你没有运行测试/构建，也没有修改文件。不要把静态推断称作运行验证。
- 对照本次审查精确 HEAD 和 tree hash。
