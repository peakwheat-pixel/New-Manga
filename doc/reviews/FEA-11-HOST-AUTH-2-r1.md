# FEA-11-HOST-AUTH-2 Review r1（独立上下文 fresh subagent）

| 项 | 值 |
|---|---|
| 审查者 | 独立上下文 fresh subagent（父会话 `b84cf221…`；**未参与本卡实现**；DSH 落盘） |
| 模式 | 只读 + 临时变异（pristine 副本 → 破坏 → 定向测试 → 逐字节复原 sha256 MATCH），未 commit/push，未改交付 |
| 被审 head | **`f7016d3fb`**（parent `2849001a8`）；工作树 `git diff --exit-code` 全空 |
| 结论 | **`approved`（仅针对已交付实现：AC-F1/F2 + AC-F1c + latent-bug 修复）**；**不构成卡 done 的批准**——AC-F3 NOT MET（架构阻塞）、AC-F4 NOT MET、AC-F5 closeout 面未做 ⇒ 需 DSH 裁决 |
| Findings | **P0=0 / P1=0 / P2=5 / P3=9** |

## 0. 实跑（reviewer 一手）

| 命令 | 结果 |
|---|---|
| `Fea11HostAuthIpcTests` + `NEWMANGA_FEA11_IPC=1` | **2 passed / 0 failed**（两次：11:26、11:40 Rebuild 后） |
| 同 filter 默认（无 env） | 2 skipped（reason 指向 `NEWMANGA_FEA11_IPC=1`） |
| 全量 `NewManga.Host.Tests` | **300 passed / 0 failed / 67 skipped / 367** |
| `Fea11HostAuth2FreshCompletionTests` | **14 passed / 0 failed**（基线 + 变异复原后复跑） |
| `Fea11SourceIpcTests`（gated） | **1 failed**（`FullSyncChain_…`，既存，复现交付 README §6 声明） |
| `check.ps1`（默认 + `-TaskPath`） | PASS（3 warnings） |
| `verify_pins.ps1` | **18/18 PASS**（`C17 = aefa0fa5b17e`，实算文件 SHA-256 相同） |
| `generate_api_inventory.py --check` | EXIT 0 |
| `pytest -q`（独立复跑） | **3390 passed / 10 skipped** |
| 全量 .NET | 未独立复跑；Lead 日志逐程序集 21+38+253+117+31+300+167+778=**1705**、67+24+7=**98**，加总自洽 |

## 1. AC 判定

| AC | 判定 | 关键证据 |
|---|---|---|
| **AC-F1** | **MET** | `Fea11HostAuth2FreshCompletionTests` 14/14：`LastUsedAt` 推进；新 coordinator 读盘证明 fresh 已落盘；`operation_id/request_digest/host_receipt_id` 不变；`authorized_at` 严格变新；`generation=live`、`identity_digest=基线`；`AuthorizationDigest == sha256(canonical(authorizations))` 三方一致；`AcknowledgeAsync_PersistsTheFreshAuthorizationBeforeTheCoreCall` 证明「先落盘后调 Core」；拒绝矩阵 5 例各自 typed + journal 文件字节不变 + state 不变 |
| **AC-F2** | **MET** | gated 2/2 两次实跑：ACK 前 gate 拒绝 → ACK 后 acknowledged/gate 开/新 v2 键；wire `payload.authorization` fresh 且 digest 可复算；二次 ACK 0 新帧；同请求重发同 `commit_digest`、行数不变、源 zip SHA 守恒；错 digest → typed `INVALID_REQUEST`、journal 仍 core-committed、gate 仍 pending；未 ACK 的 core-committed → recovery 成功 + 幂等。reviewer 另从生产 `wire.ndjson` 直读确认 payload = C-17 §5.2:258 六字段平铺 |
| **AC-F3** | **NOT MET（阻塞成立）** | `Fea11HostAuthIpcTests` 仅有 2 个 fact，`CrashPoint_*` 不存在；`crash-ack.ps1` 声称的事实与代码不符；实现者未宣称 MET、未伪造 |
| **AC-F4** | **NOT MET** | `HostOptions.cs` 零 diff；无 `runtime.Commands.InvokeAsync` 全链路用例；README 只写"需 re-home"未具名 |
| **AC-F5** | **NOT MET（门禁面已核，closeout 面未做）** | 门禁面全部满足（见 §0）；`doc/` 零 diff ⇒ HOST-AUTH-1 回填、PLAN、limitation re-home 记录均缺 |

## 2. 正确性核查要点

- `PrepareCompletion`（`SourceOperationCoordinator.cs:191-301`）顺序与 C-17:160/:169 **逐项对齐**：锁内读 + state 校验 → 解析基线（registry_id/generation/identity_digest）→ receipt 字段核对 → live `Authorize`（锁后重读 + root 物理 identity 重验）→ `Mint`（live generation + 基线 identity + 原 op/request/receipt、`authorized_at` 严格后移）→ `RequestDigest` 守卫 → 锁内重读 state 未变 → **先落盘** fresh → 返回；之后才发 Core 帧。
- ACK/Recovery 成功后均**锁内重读** state 才写终态（防 `MarkFailed` 竞争）。
- **latent bug 判定：属实**。parent 版本 ACK/recovery payload lambda 以 `WriteStartObject()` 开头，而 `SendHostControlAsync:585-589` 已开 `payload` 对象 ⇒ 首个 `WriteStartObject` 落在"期望属性名"位置 → 必抛 `InvalidOperationException`（reviewer 用同 token 序列独立复现；变异 M8 还原后 gated 2 例同样以该异常 RED）。精确边界：**生产 coordinator 路径从未发出过一帧**；Core 侧是否曾被手工帧跑通不作绝对断言。修复后 wire 形状 = 契约六字段。
- `AuthorizationDigest` 双口径：`Authorize()/RetryFailed()` 写 JSON 信封 sha256，`PrepareCompletion` 写 wire 摘要（C-17:264）；无生产读取方，不影响契约，登记 P3 待统一。

## 3. AC-F3 阻塞判定（reviewer 结论）

**成立（在本卡冻结 AC 与现有 stdio 架构下不可完成）**，且非永久：需后续卡。证据：
1. Core grant 仅进程内存：`src/infrastructure/resource_channel/source_read_refs.py:106-121`（`SourceReadGrantRegistry(_grants: dict)`，`register` 要求 `expires_at ≤ now+300`，`:178-180`）。⚠ 实现者引用的 `ports.py:28-31` **行号错误**（该处是 `build_source_sync_stack` 参数）。
2. C-17 不允许省略 `grant_ids`：正确锚点是 **§5.2:258**（六字段必填）与 **§5.3:276**（非缺失源不能为空）+ Core `runtime.py:220-260`；实现者/脚本引用的 §3.2:169/:248 **均不是**该禁令锚点（结论对、引用错）。
3. 整树 kill 必杀 Core → 新进程必新 Core → 内存 grant 全失 → `SOURCE_GRANT_EXPIRED`；补救（Core grant 持久化 / recovery 重发 grant + journal 扩展 / 外部托管 Core）均在本卡 out_of_scope 或需契约/格式变更；`reattest.py` 不发放 sync grant。

## 4. 判别性变异实测（reviewer 自拟 M1–M8，实跑 7 组）

pristine sha256 `a4213091…bfdb`；每组：单点替换（断言锚点唯一）→ 定向测试 → 逐字节复原 → `Get-FileHash` + `git diff --exit-code` 双证。

| 变异 | 破坏点 | 实测 RED | 复原/复绿 |
|---|---|---|---|
| M1 | 删 `accessRegistry.Authorize(...)` | **2 failed**（LastUsedAt / 拒绝矩阵） | MATCH → 14/14 |
| M2 | 复用 `entry.AuthorizationJson`（不重签） | **2 failed** | MATCH → 14/14 |
| M3 | 删 `VerifyOperationReceipt` | **6 failed** | MATCH → 14/14 |
| M4 | 删 `minted.RequestDigest == entry.RequestDigest` 守卫 | **0 failed（存活）** | MATCH → 14/14 |
| M5 | 删 baseline generation 守卫 | **1 failed** | MATCH → 14/14 |
| M6 | 删 PrepareCompletion 锁内 state 守卫 | **0 failed（存活）** | MATCH → 14/14 |
| M8 | 还原 parent 嵌套 payload writer | **gated 2 failed**（`InvalidOperationException`） | MATCH → Rebuild 后 2/2、14/14 |

方法论诚实记录：`Copy-Item` 复原保留旧 mtime，首次"复原复绿"误用变异二进制（异常签名与 M8 一致，被识别）；`dotnet build -t:Rebuild` 后复绿为真。

## 5. 超范围与契约

- diff ⊆ allowed_paths ✓（8 文件全部命中卡面）；`doc/`、`src/**`、`NewManga.CoreClient/**`、`HostOperationOrchestrator.cs`、`HostErrorCodes.cs`、`HostOptions.cs`、`Tests/Support/**` **零 diff**；wire/命令集/错误码/journal 格式零变更；pins 18/18。

## 6. Findings

**P0=0。P1=0。**

| ID | 级别 | 位置 | 问题 | 建议（DSH 处置） |
|---|---|---|---|---|
| R1-P2-1 | P2 | 卡 AC-F3 / README §5 | AC-F3 NOT MET 且卡面无 re-home 条款 ⇒ 不可 done | **DSH：re-home 到 `FEA-11-HOST-AUTH-3`**（并在卡面按 NOT_APPLICABLE + 具名卡登记） |
| R1-P2-2 | P2 | AC-F4；`HostOptions.cs` 零 diff | AC-F4 未实现，README 未具名 | **DSH：re-home 到 `FEA-11-HOST-AUTH-5`**（HostRuntime 全链路 e2e；打包 sidecar 腿单列 NOT_RUN） |
| R1-P2-3 | P2 | `verification/…/tools/crash-ack.ps1:14,21,55,64,107` | 脚本声称的 `CrashPoint_Park/Recover` fact **不存在**；引用锚点错误 | **DSH：本轮把脚本标注为「未实现骨架（随 HOST-AUTH-3）」并纠正锚点**（§5.2:258 / §5.3:276） |
| R1-P2-4 | P2 | 卡面五条 AC 行尾均带 `<<MET>>`（**base 即存在**，冻结卡作者问题） | closeout 照抄会产生 F3/F4 假 MET | **DSH：closeout 逐条改写**（F1/F2/F5 MET；F3/F4 `NOT_APPLICABLE` + 具名 re-home） |
| R1-P2-5 | P2 | AC-F5 / `doc/` 零 diff | closeout 面未做 | **DSH：本轮完成 closeout** |
| R1-P3-1 | P3 | `:143`/`:492` vs `:286` | `AuthorizationDigest` 双口径 | 登记后续卡（HOST-AUTH-4）统一 |
| R1-P3-2 | P3 | `:265-268` | `RequestDigest` 守卫无判别测试（M4 存活） | 登记 HOST-AUTH-4 |
| R1-P3-3 | P3 | `:276-279`、`:350-353` | 两处 state 竞争守卫无测试 | 登记 HOST-AUTH-4 |
| R1-P3-4 | P3 | `Fea11HostAuthTests.cs:743-767` | receipt 矩阵缺 `plan_digest`/`commit.*` | 登记 HOST-AUTH-4 |
| R1-P3-5 | P3 | `Fea11HostAuthIpcTests.cs:113-120` | 重发只断 `commit_digest/state`，未断 receipt 整体 | 登记 HOST-AUTH-4 |
| R1-P3-6 | P3 | `:604-618` | `AuthorizationAfter` 亚毫秒窗口 | 登记 HOST-AUTH-4 |
| R1-P3-7 | P3 | `:234` | 「generation > baseline」分支当前不可达（C-15 registry 语义） | 卡面/注释标注，登记 HOST-AUTH-4 |
| R1-P3-8 | P3 | `Fea11HostAuthIpcTests.cs:504-527` | gated 质量：无超时/不清理/`Wire.Count` 隐含假设/固定 python 路径 | 登记 HOST-AUTH-4 |
| R1-P3-9 | P3 | `README.md:32,5`；`crash-ack.ps1:21` | `wifi`→`wire`；grant_ids 禁令与内存 registry 的锚点错误 | **本轮修正**（P2-3 同批） |
| R1-P3-10 | P3 | `Fea11HostAuthIpcTests.cs:143-154` | 错 digest 由 fixture 直接发帧，未覆盖 coordinator journal 交互 | 登记 HOST-AUTH-4 |

## 7. 未核实（reviewer 自陈）

全量 .NET 未独立复跑（计数加总自洽）；基线 1691/0/96 未在 `2849001a8` 实跑；`crash-ack.ps1` 未执行；AC-F4 全链路未验证；并发竞争/亚毫秒窗口/generation 分支未实测；`HostOptions` seam 的打包/trim 影响未验。

---

## DSH findings 处置（2026-11-08，裁决人=DSH）

| Finding | 处置 |
|---|---|
| P2-1（AC-F3） | **re-home 到 `FEA-11-HOST-AUTH-3`**（含 limitation 3/4 的 C-17 UNFREEZE 类项）；卡面 AC-F3 改 `NOT_APPLICABLE: 架构阻塞+re-home`，不写 MET |
| P2-2（AC-F4） | **re-home 到 `FEA-11-HOST-AUTH-5`**（HostRuntime 全链路 e2e）；卡面 AC-F4 改 `NOT_APPLICABLE: re-home` |
| P2-3/P3-9（脚本/锚点） | **本轮修正** `crash-ack.ps1` 标注与锚点；README 的 `wifi` 错字与锚点同步修正 |
| P2-4（AC 全 MET 标记） | **本轮改写卡面 AC 行**：F1/F2/F5 → `[x] <<MET>>`；F3/F4 → `[x] <<NOT_APPLICABLE: …re-home…>>` |
| P2-5（closeout 面） | **本轮完成**：卡 done + 证据 + `FEA-11-HOST-AUTH-1` append-only（AC3 判定与 re-home）+ PLAN/STATUS/ledger + handoff §30 |
| P3-1…P3-8/P3-10 | 全部登记到 `FEA-11-HOST-AUTH-4`（Host 完成语义收尾） |
