# 代码增量审计

只读 Explorer `code_delta_1010`；读盘主线 HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`。本报告由主协调保存子代理的定界发现，未修改程序或运行测试。

## 主线比较

`git diff --name-status 549a6544f0be1eec66c09ece393fd1a409f10bf3..HEAD -- src apps tests packaging` 为空。四页、书架导入、进度、Reader/生产导出在该比较窗口没有程序实现增量。沿用上次已审查的当前能力事实：Console↔Workbench；Library/Settings 子面板；TaskProgressPanel static；core_service decoder 1×1；现有 PipelineService 未连接生产 StartRun。

## P04 候选

- review base=`9ea4e312fa01470478946a557135791b5a044cb3`；implementation=`eedbda05ef42d61b35149c4d3d54ac0804b7b80d`；delivery=`ec44a4891d624c88e89abfe2c13d9e7e072b9e5e`。
- 候选源代码只变 `apps/desktop/src-tauri/src/library_bridge.rs`、`main.rs`；是 cfg(test) 同步 hooks、AC2 诊断测试与 AC1 精确常量检查，没有生产根因修复。
- 主协调核对 `git merge-base --is-ancestor ec44a489… HEAD` 返回 exit=1，候选不在主线祖先链。

## 生产错配调用链

| 源码位置（当前主线） | 事实 |
|---|---|
| `library_bridge.rs:83–115` | decode_response 解 JSON/error/result，不核对 request_id |
| `library_bridge.rs:117` | LibraryChannel trait 允许共享并发 |
| `library_bridge.rs:263–310` | round_trip 生成 request_id，stdin mutex 写请求后释放，再独立取 stdout mutex 读取下一行 |
| `main.rs:162–170` | AppState 持 Box<dyn LibraryChannel> |
| `main.rs:369–395` | list_chapters/list_chapter_pages 等生产调用委托该 channel |

请求写序与读锁顺序可以不同；FIFO 回包会到错误调用方。P04 测试通过显式同步推导出反序读取，静态预期 FAIL；Cargo/sidecar 未运行，不能写 runtime FAIL。

P22 当前 proposed，base/branch/worktree/production patch 未建立。拟以最小 per-channel transaction lock 覆盖一次 request write→matching response read，加真实 round_trip 的确定性两调用方回归；不改 wire shape/request_id 语义。

## 限制

不重复全仓代码地图，复用不变区间的旧审计；不验证 AppContainer 可行性、不运行产品测试。读取中暂停 checkpoint 一度尚未落盘，随后主协调已读到，最终不列为缺失。

## 10-10 第二次盘点增量

- 主线仍为 `main@cddff58469b56e181019a8ddfeade80684bc7eb9`；自上次 10-10 盘点以来 `src/apps/tests/packaging` 没有差量。本轮没有生产代码修改，也没有运行 Build/Cargo/Vitest/GUI/WebView。
- P04 R3 final 对固定 base=`9ea4e312fa01470478946a557135791b5a044cb3` → delivery=`ec44a4891d624c88e89abfe2c13d9e7e072b9e5e` 给出 `CHANGES_REQUESTED`，P0/P1/P2/P3=`0/0/3/1`。Codex 核验 tree、24 paths、`git diff --check` EXIT 0；这些静态核验不代表 Cargo 或 AC runtime 通过。
- 最新 P04 worktree HEAD=`5ea8304ae1670e079b7a496e08fbdea6f656156f`；从 delivery 只增加 R2 Review 归档文件。R3 report SHA-256=`e15fce703e65c9ce1403ebe21254bb2b0c42a2348b1753cf4f9a5f810c13cd4d` 仍是 untracked evidence，候选 Task 声称已归档与 `git status` 不符。
- R3-2（R2 报告引用）和 R3-3（P04 blocked 状态）在较新的 P04 Task/worktree 记录已有处置；R3-1（默认测试需 `#[ignore]` 的裁决落地）与 R3-4（修正 Handoff 的挂起保护说法）待 Owner R4。Plan/Status 顶部仍写 R3 final pending，应登记为治理状态漂移。
- P22 锁住 write→matching read 后，原 AC3 负向测试中 Alpha 等 Beta、Beta 又在锁外等待会死锁。修复测试必须用正向、确定性两调用方回归验证锁下响应归属，并清除/重推导 `static_expected_behavior: FAIL`；保持 wire protocol/request_id 语义不变。
