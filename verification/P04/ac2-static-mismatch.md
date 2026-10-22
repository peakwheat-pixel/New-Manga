# P04 AC2 静态错配结论

日期：2026-10-10（Asia/Shanghai）

## 固定对象

- Task：P04，Owner=Antigravity，非作者 Reviewer=DeepSeek Harness。
- review base=`9ea4e312fa01470478946a557135791b5a044cb3`。
- reviewed HEAD=`42b87f6bb6314fb42df3592f15a9fcd69866739b`，tree=`e642151118cebdbb21cc283afc86121345ee52e0`。
- 独立 Review=`CHANGES_REQUESTED`；P0/P1/P2/P3=`0/1/3/4`。完整分析见 [DSH R2 report](dsh-p04-owner-review-r2.stdout.md)。

## 静态结果

当前 AC2 编排确定地强制 Alpha 先写、Alpha 在写后 hook 等待、Beta 后写；sidecar 按请求接收顺序回包。Alpha 被 hook 阻塞时，Beta 先拿 stdout 锁，因此读取第一个回包（Alpha 的响应）。两方拿到的响应都不属于对应调用方，预期行为=`FAIL`。

这是基于固定源码的静态推导，不是运行证据。Cargo AC1/AC2、sidecar、Tauri/build 均=`BLOCKED / NOT_RUN`；未创建伪造的 sidecar 输出或 verdict artifact。

## 处置

按 P04 AC3，P04 保持 `blocked`。独立修复候选为 [P22](../../doc/tasks/P22.md)，其 hard dependency 不含 P04=`done`；P22 集成后仍须在 P02 Build Gate 解除时运行并通过 AC2，方可解除 P04 阻塞。
