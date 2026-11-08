# FEA-11-HOST-AUTH-2 Canonical Evidence（Host ACK/recovery fresh 授权；0 pin）

> **结论先行**：本卡把 `FEA-11-HOST-AUTH-1` 的 C-17 §3.2 fresh 授权缺口修掉（ACK/recovery 不再发送 apply 时落盘的 authorization），并在修复过程中发现并修掉一个**既存 latent bug**：ACK/recovery 的 payload writer 多写一层对象，与 `SendHostControlAsync` 的 `payload` 信封冲突 ⇒ **生产 coordinator 路径此前从未发出过一帧**（真实 wire 必抛 `InvalidOperationException`）。修复后 wire `payload` = C-17 §5.2:258 六字段平铺。
> **AC 状态**：AC-F1 / AC-F2 / AC-F5 **MET**；AC-F3（真实进程 kill 崩溃点）与 AC-F4（HostRuntime 全链路 e2e）**NOT_APPLICABLE + re-home**（→ `FEA-11-HOST-AUTH-3` / `FEA-11-HOST-AUTH-5`），**不写成 MET**。
> **零契约/wire/命令集/错误码/journal 格式/Core 改动；18 pins 不变。**

| 项 | 值 |
|---|---|
| task | `FEA-11-HOST-AUTH-2`（冻结卡 `doc/tasks/FEA-11-HOST-AUTH-2.md`；scope review `doc/reviews/FEA-11-HOST-AUTH-2-scope-r1.md`，**READY-TO-FREEZE**） |
| Owner | `host-auth-2-impl`（DSH Agent Teams teammate，fresh） |
| Review | 独立上下文 fresh subagent（未参与实现）；报告 `doc/reviews/FEA-11-HOST-AUTH-2-r1.md`；**approved（P0=0/P1=0/P2=5/P3=9）**，仅针对已交付实现 |
| base | `2849001a8`（卡面 base `4070f0043`） |
| 实现 + 测试 commit | **`f7016d3fb`**（8 文件，+1557/−37） |
| 契约 | C-17 `:160/:161/:169/:258/:260/:264`（**冻结字节**，pin `aefa0fa5…`；遵守型修复，0 pin） |
| 依赖 | 零新增 |

## 1. 门禁实测（Lead DSH 一手）

| Gate | Before（`2849001a8`） | After（`f7016d3fb`） | 结果 |
|---|---|---|---|
| build | — | 0 warning / 0 error | PASS |
| 全量 .NET | 1691 passed / 0 failed / 96 skipped | **1705 passed / 0 failed / 98 skipped（总 1803）**（+14 passed、+2 skipped=2 个新 gated fact） | PASS |
| 全量 pytest | 3390 / 10 | **3390 passed / 10 skipped**（271.98 s） | PASS（不降） |
| Host 定向 | 286 / 0 / 65 | **300 / 0 / 67**（reviewer 独立复跑一致） | PASS |
| gated 真实 IPC | — | **2 passed / 0 failed**（`NEWMANGA_FEA11_IPC=1`；reviewer 两次实跑） | PASS |
| pins | 18/18 | **18/18** | PASS |
| check（默认 + `-TaskPath`） | PASS | **PASS(3w) ×2** | PASS |
| API inventory | OK | **EXIT 0** | PASS |
| scope ⊆ allowed_paths | — | 8 文件全部命中；`doc/`、`src/**`、CoreClient、HostErrorCodes、HostOptions、Support 零 diff | PASS |

`verification/FEA-09/logs/wire-redacted.ndjson` 在每次全量 .NET 后被重写（既有副作用），均以 `git checkout -- verification/FEA-09` 恢复。

## 2. 判别性（独立 Review 实跑 7 组变异）

| 变异 | 破坏点 | RED | 复原 |
|---|---|---|---|
| M1 | 删 live `Authorize` | 2 failed | sha256 MATCH → 14/14 |
| M2 | 复用 apply 时 authorization | 2 failed | MATCH → 14/14 |
| M3 | 删 receipt 字段核对 | 6 failed | MATCH → 14/14 |
| M4 | 删 `RequestDigest` 守卫 | **0（存活，P3-2）** | MATCH → 14/14 |
| M5 | 删 baseline generation 守卫 | 1 failed | MATCH → 14/14 |
| M6 | 删 Prepare 锁内 state 守卫 | **0（存活，P3-3）** | MATCH → 14/14 |
| M8 | 还原 parent 嵌套 payload writer | gated 2 failed（`InvalidOperationException`） | MATCH → Rebuild 后 2/2 |

## 3. 未完成项（re-home，非 MET）

- **AC-F3**（真实进程 kill 崩溃点）→ `FEA-11-HOST-AUTH-3`：Core source-read grant **仅进程内存**（`src/infrastructure/resource_channel/source_read_refs.py:106-121`），C-17 **§5.2:258 / §5.3:276** 禁止省略 `grant_ids` ⇒ 整树 kill 后新 Core 无 grant，`_verify_fresh` 必拒。
- **AC-F4**（HostRuntime 全链路 e2e）→ `FEA-11-HOST-AUTH-5`：需 `HostOptions` Core 覆盖 seam（打包 sidecar 早于 C-17 v1.0）。
- limitation 3/4（C-17 UNFREEZE 类）→ `FEA-11-HOST-AUTH-3`；limitation 6/7/8/9 + Review P3-1…8/10 → `FEA-11-HOST-AUTH-4`。

## 4. 不构成什么

- 不构成「FEA-11-HOST-AUTH-1 完全实现」「C-17 §3.3 完全实现」「10 项 limitation 全部关闭」。
- 不构成可发布：`Technical Gate=NOT_SATISFIED` 不变。
- 崩溃点/全链路 e2e 均为 `NOT_RUN`，不得写成 PASS。
