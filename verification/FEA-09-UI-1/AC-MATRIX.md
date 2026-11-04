# FEA-09-UI-1 AC 证据矩阵（返修 r1 + DSH 集成，2026-11-04）

状态口径：`MET` = 本矩阵命令在最终返修工作树实际运行且全绿；不得把 fake/进程内证据拼成 AC-4。本表为 Task 进入 `in_review`（复审）的逐 AC 证据；最终 `done` 以全新上下文 Codex 复审 + DSH 集成验证为准。

## 门禁（返修工作树，base `7f4f4d3cd`；DSH 复跑）

| 命令 | 实际结果 |
|---|---|
| `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **0 warning / 0 error** |
| `dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build` | **1317 passed / 0 failed / 74 skipped**（8 程序集；基准 1300/0 不减少，+17 新测试） |
| 真实 IPC：`Fea09UiImportIpcProductionTests`（`NEWMANGA_FEA09_IPC=1`） | **11/11 passed**（`HostController(HostOptions)` + 真实 `ImportDockViewModel` + HostRuntime + Python Core stdio） |
| 真实 IPC：`Fea09UiImportIpcTests`（下层 coordinator，`NEWMANGA_FEA09_IPC=1`） | **5/5 passed** |
| `python tools/generate_api_inventory.py --check` | **PASS**（C-07 冻结清单 54 方法未变；无 UNFREEZE） |
| `pwsh tools/governance/check.ps1` | **PASS**（3 warnings） |
| `pwsh tools/governance/verify_pins.ps1` | **17/17 PASS** |
| `git diff --name-only` | 全部在 allowed_paths（PLAN/STATUS/TASK_LEDGER/VERIFICATION 为 DSH 集成文件） |
| DSH 原始成功记录 | `logs/dsh/build.log`（命令头+EXIT=0）、`logs/dsh/full-test.log`（8 个项目逐命令+EXIT=0）+ `logs/dsh/trx/dsh-full-<project>.trx`（8 个唯一 TRX）、`logs/dsh/ipc-test.log`（EXIT=0，16/16）+`logs/dsh/trx/dsh-ipc.trx` |
| FEA-09 canonical 证据 | 测试复跑污染已 `git checkout` 恢复原字节；工作树无 `verification/FEA-09/**` 改动 |

## AC 结论

| AC | 判别与证据 | 结果 | 状态 |
|---|---|---|---|
| **AC-1** plan 预览/确认/取消 + 源变化拒绝 | 真实闭环：`production-ui-import-ipc.json` case `ordinary`/`host-folder`/`changed-before-confirm`：plan→confirm→receipt 成功 2 页；确认前改源→本次 confirm **逐文件追加帧**含 `FILE_IDENTITY_CHANGED` typed 拒绝，receipt 行 `OutcomeText` 同码、0 页（不使用 Snapshot.LastError 兜底）；取消→已提交页保留、未提交不出现。VM/View 13+4 例补充状态/按钮。 | 真实 HostController+VM+IPC 验证 | **MET** |
| **AC-2** 密码重试 + 零泄漏 + AES typed unsupported | `C_SingleEncryptedSourceWrongPasswordThenRetry`（错密 typed 失败 0 页→正确密码 completed 2 页）；`B_AesTypedUnsupported`；`Z_Audit...` 对 request+response wire（逐例）、stdout/stderr/host 日志、Registry 原始持久化字节（opaque/DPAPI，不冒充 List() 明文视图）、UI 错误、失败结果、Task evidence 扫描密码字面量/hex/base64：**0 命中**；Secret-G 失败清理 G/H/I/J 四例（capability/register/start/replan）通过且 token 文件 0 残留；>1 加密源 typed `SOURCE_PASSWORD_REQUIRED` 拒绝。 | 真实 IPC + 静态/动态审计 | **MET** |
| **AC-3** 取消/已提交守恒/重试不重复/计数一致 | `D_CancelAfterOneCommitThenRetryConservesPages`：提交 1 页后 VM cancel→receipt 终态已提交 1 页、未提交 0；重试后总 3 页无重复；`A_OrdinarySuccessAndWholeSourceSkip` 计数/receipt 一致；R2 暂时失败恢复轮询→取消两例通过。 | 真实 IPC + VM 状态机 | **MET** |
| **AC-4** 隔离 fixture + production adapter 真实 UI 可观察证据（非 fake） | `Fea09ProductionFixture` 隔离 workspace + 真 Python Core stdio；`HostController` 生产 App adapter + `ImportDockViewModel` 真实 VM；11/11 真实 IPC 通过；证据 `ipc/production-ui-import-ipc.json`、`.wire.ndjson`（case/计数/状态/原因）；旧 coordinator 5 例仅作下层证据，不冒充。 | 真实闭环 | **MET** |
| **AC-5** 旧 managed 路径/PNG/用户数据/全量/未 push | 旧 `ImportPages` 路径回归在 1317/0 全量内；FEA-06 四 PNG 对照 `4/4 UNCHANGED`；隔离 fixture 无真实用户数据；全量不减少；未 commit/push（提交由 DSH 完成）。 | 全量 + 审计 | **MET** |

## 限制与已知事项（如实登记）

1. **FEA-09 canonical 证据可被常规测试复跑重写**（既有债务候选）：`Fea09RealIpcTests` 写 `verification/FEA-09/ipc/*`，`NewManga.CoreClient.Tests/WireLogSourceRedactionTests`（默认门）写 `verification/FEA-09/logs/wire-redacted.ndjson`；DSH 复跑后已恢复原字节并复算 pin。建议后续 Task 改为写 workspace。
2. **folder 引用导入**：App 不递归/排序/授权，目录路径 + `sourceKind="folder"` 交 Host `IssueAsync`（Host EnumerateFolder：自然排序/隐藏系统过滤/reparse 拒绝/预算）；真实 IPC `F_FolderUsesHostEnumerationAndOrdering` 验证 2 页（隐藏文件排除）；自然顺序未单列断言。
3. **多加密源**：同一 plan 含 >1 encrypted 源时 App 层 typed 拒绝（一次仅支持一个加密源，请分别确认），未扩展 Core wire；逐源独立确认/token 为后续体验演进。
4. **生产 fixture** 使用测试内 C# launcher 包装真实 Python Core（带故障注入钩子），HostRuntime/生产 adapter/VM 未替换；属真实 stdio 闭环。
5. **UI 自动化**：真实控件文本由 App.Tests 的真实 Avalonia 控件断言；未做整窗口视觉/E2E 录制（本 Task 最小接线范围）。receipt 行布局（N2）已补 RowDefinitions=Auto,Auto。
6. **Registry 审计**：只扫描原始持久化字节（opaque/DPAPI）；未解密调用 Registry.List()，不宣称该明文视图已验证。
