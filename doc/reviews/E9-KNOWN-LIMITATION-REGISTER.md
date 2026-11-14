# E-9 已知限制登记（非冻结契约）

**状态：已由 ZCode 裁决采纳（2026-11-15）；本文件是登记入口，不是契约本体。**

## 为什么单独建文件而不是改 C-17

`doc/plan/FEA-CONTRACT-FROZEN-C17.md` 是**冻结契约且被 pin 覆盖**
（其附录 §"v1.2 UNFREEZE 重冻记录" 写明 `verify_pins` 三指纹与 `truth 17 OK + C17 OK = 18/18`，
工作树字节 `cdeee4872e29b56c7d67de65dabd6ca9b31006eecde61d99b83e29fe5a4fc96c`，58134 bytes）。

**改它需要走正式 UNFREEZE 流程**（新载体 + 独立字节复核 + 三指纹重算），
而本限制**不需要改契约语义**：契约定义的是"恢复需要容器路径"，产品只是**暂时无法提供该路径**。
故登记于此，并在 C-17 与 E-9 finding 之间建立引用。

## 限制本体（按 ZCode 核实的真实口径）

**非 folder 来源（`zip` / `cbz` / `pdf` / `image`）的 source **sync 完成链不可用**。**

具体：
- `SourceOperationCoordinator.AcknowledgeAsync` 与 `RecoverAsync` **都走同一次 fresh re-mint**；
- 该 re-mint 需要容器路径，而 **journal / plan materialization / apply payload 六个入口全都没有它**
  （证据：`verification/E9-PATH-AVAILABILITY-1/README.md`）；
- 因此 Host **typed 拒绝**，错误码 **`SOURCE_PLAN_UNAVAILABLE`**；
- 后果：ACK 失败 → gate 停 pending（`source_sync.py:150`）→ **新 binding 不可读**。

**`sourceKind == "folder"` 不受影响**（root 目录恰好就是容器）。

### 表述纪律

**不得**写成"仅崩溃恢复不可用" —— 那**低估**了影响面：**正常 ACK 同样不可用**。
ZCode 明确核实过 `AcknowledgeAsync:468` 与 `RecoverAsync:581` 是同一路径。

## 数据安全边界（ZCode 保留给用户的第二点）

**只挡"读门打开"，无业务数据损坏**：apply 阶段已 `core-committed`，
源文件、旧 binding 的 `verified_digest`、旧 entry digest 均不变（由
`E9-KNOWN-LIMITATION-TESTS-1` 的三条新增断言固定住）。

## 解锁条件

实现 **mint-time 路径映射**（ZCode 登记的后续 Task 候选）：

- 在 `SourceReadCoordinator.IssueLockedAsync` 处（它**手中已有真实容器路径**）持久化
  **Host 侧 DPAPI 映射** `registry_id → container_path`；
- 恢复时取候选路径，**身份仍经 `IssueAsync` 的全量物理 facts 验证**（路径失效 = typed 失败，fail-closed 保留）；
- **不动 wire / Python Core / apply payload**；但属**新增持久授权材料**，需契约小节 + 安全审查；
- 落地后**回退本限制**（并新增"非 folder 恢复成功"的正向测试）。

## 被这条限制挡住的测试

`Fea11Residual4AIpcTests.ProductionDispatcherFullSyncChain_NewKeyOldDigestConserved`
（opt-in `NEWMANGA_FEA11_IPC=1`）—— 已按裁决改为断言 typed 拒绝，标记
`KNOWN-LIMITATION-E9`；**不得**静默改绿，回退限制时须还原为成功断言。

## 引用

- 产品裁决：`doc/reviews/E9-PRODUCT-ADJUDICATION-zcode-2026-11-15.md`
- 缺陷登记：`doc/reviews/MAINT-1-EXISTING-FINDINGS-2026-11-14.md` 的 **E-9**
- 路径不可得证据：`verification/E9-PATH-AVAILABILITY-1/README.md`
- 测试口径证据：`verification/E9-KNOWN-LIMITATION-TESTS-1/README.md`
