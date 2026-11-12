# ZCode Review：AUDIT-01/02 阶段

- 日期：2026-11-12
- Reviewer：ZCode（fresh independent context，`reviewer_kind=agent`）
- session：`sess_0f75abbb-b6c5-4aee-b015-b89c5085201c`
- turn：`turn_7990edb9-a081-452d-9998-540e29d7da2d`
- trace：`20f9cd88-0d83-48a0-9575-051ec950da50`
- reviewed HEAD：`beaa13406438fab46ef56fa5a8852bf04ce7133d`（`main`）
CLI：`node zcode.cjs --prompt <read-only audit review> --cwd "G:\CODEX\New Manga" --mode plan --json --locale zh-CN`；CLI EXIT 0。

## Verdict

**`ACCEPT`**：0 个 P0/P1/P2 Review findings；2 条 P3 observation，不阻塞本阶段接受。该结论只覆盖 reviewed HEAD 上 AUDIT-01/02 阶段报告与 `NM-AUD-0001`，不代表全审完成、最终 Release Gate 通过或 Task 关闭。

## 核验结论

- `SidecarProcess.StartAsync` 在子进程已 spawn 后的取消检查没有清理收口；`DisposeAsync` 先设置 `_disposed` 再调用 `StopAsync`，而后者在 `_disposed` 时立即返回，因此直接释放路径没有关闭 stdin、等待退出或 kill。正式隔离 helper probe 的存活结果与该控制流吻合。
- `HostBridgeClient.DisposeAsync` 未先调用 `StopAsync`，因此受该缺陷影响。`CoreServiceClient.DisposeAsync` 显式先 `StopAsync` 再 `DisposeAsync`，报告与台账正确区分。
- ZCode 核对正式 run `20261112T143133097703Z` 两个 child 均在调用返回后存活；`cleanup_killed_child=true` 是 probe 随后终止 helper，不代表产品清理成功。旧 PID marker replay `20261112T142759897356Z` 被正确排除。未发现报告把真实 sidecar 或 UI 写成已验证。
- ZCode 同意 `NM-AUD-0001` 的异步取消/进程资源生命周期分类及 P2 candidate 定级；真实生产 sidecar 行为、发生概率和用户可见影响仍未核实。若后续实测真实 sidecar 在应用正常退出后仍存活，建议重新评估为 P1。
- AUDIT-01 `FAIL`、AUDIT-02 `BLOCKED` 与阶段报告对 TestHost、真实 sidecar/UI、格式扫描和完整静态质量扫描限制的表述成立。

## P3 observations 与处置

| ID | 位置 | observation | 后续动作 |
|---|---|---|---|
| N-1 | `SidecarProcess.cs:153,158`；`HostBridgeClient.cs:121,146` | 相同清理短路还影响 `StartAsync` integrity-fail 清理及 HostBridge ping 失败后的 `client.DisposeAsync()` 路径；根因描述和幂等 stop/cleanup 建议已覆盖根本问题，但影响路径枚举不全。 | 已补充至 `AUDIT_ISSUES.md` 的 `NM-AUD-0001` 复核注记；产品修复需另行释放实现 Task。 |
| N-2 | `HostRuntime.cs:1111-1115` | HostRuntime 关闭顺序对 HostBridge 未先 `ShutdownAsync` 后再 dispose；未来实现设计应显式说明受控退出顺序。 | 已补充至 `AUDIT_ISSUES.md` 的 `NM-AUD-0001` 复核注记；不在本审计 Task 修改产品代码。 |

Reviewer 未复算 BLOB SHA-256，未运行测试/命令；pin 复核基于路径、commit 和内容交叉检查。完整原始 CLI JSON 位于 `evidence/zcode-audit01-02-review-20261112.json`，派发/退出信息位于 `logs/zcode-audit01-02-review-dispatch-20261112.log`。
