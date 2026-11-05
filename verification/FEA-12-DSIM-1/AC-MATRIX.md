# FEA-12-DSIM-1 — AC Matrix

- 时间：2026-11-05（Asia/Shanghai）
- 仓库：`G:\CODEX\New Manga`（`main`）；base_commit `37f84bb895c9ef9b64e3865f3a92b245f2e28a7c`
- 实现 commits：`94a12e93f`（协议/模拟件/测试）、`3d0d325f7`（目录指纹 junction 拒绝 + normcase）
- 交付 docs commit：见 Handoff（`doc/handoffs/FEA-12-DSIM-1-3d0d325f7.md`）
- 门禁总日志：`logs/gates.log`；隔离/静态/哨兵细节：`ISOLATION-EVIDENCE.md`；环境：`ENVIRONMENT.md`

| AC | 结论 | 证据 | 说明 |
|---|---|---|---|
| **AC1 协议与生产默认实现** | **MET** | `tests/fea12/test_recycle_gateway_sim.py::test_protocol_is_structural_and_the_typed_vocabulary_is_closed`、`::test_production_default_is_typed_unavailable_with_zero_side_effects`、`::test_no_production_file_references_the_d_flow_port`；`logs/sentinel-probe.log` run 3 | `OriginalFileRecycleGateway.move_to_recyclebin(entries, *, journal)` 协议（`journal` keyword-only 必填，SC-34 seam）；逐项 typed 结果 `moved`/`failed`/`not_started` + 封闭 reason 词表（构造期拒绝未知码）；`UnavailableOriginalFileRecycleGateway` 任何调用 → 全部 `not_started + gateway_unavailable`、`operation_id=""`、**零文件/journal/DB 操作**；`src/**`/`apps/**` 对端口零引用（无 Host/UI 接线）；application 模块不 import `infrastructure` |
| **AC2 模拟实现** | **MET** | `::test_simulated_move_is_auditable_and_keeps_original_path_semantics`、`::test_empty_selection_is_an_empty_typed_outcome`、`::test_simulated_bin_refuses_non_isolated_roots`；`logs/sentinel-probe.log` run 1；`ISOLATION-EVIDENCE.md` §2 | `SimulatedRecycleBin` 构造期拒绝文件系统根 / 不存在 / 非目录 / `*recycle.bin` 根；条目路径经"绝对路径→拒绝 `..`/`.`/空段→未解析基线包含检查→未解析逐段 reparse 拒绝→解析后包含复查"；只在隔离根内 `os.replace`（逐项原子）+ 移动后 kind/size/SHA-256 复核（失败回滚）；manifest（`simulated-recyclebin/recyclebin-manifest.json`）记录 request_id/原路径/bin 内路径/kind/size/sha256/moved_at，可审计；JSONL journal 记录 attempt（含确切路径）+ receipt；全部写入都在隔离根内 |
| **AC3 失败语义** | **MET** | `::test_failure_injection_keeps_original_bytes_and_never_deletes`、`::test_missing_selection_is_a_typed_failure_without_side_effects`、`::test_d_failure_cannot_degrade_to_permanent_delete__static_ast`；`logs/static-scan.log` §AC3；`logs/sentinel-probe.log` run 2 | 注入拒绝（`in_use`）下：原文件仍在原位且**字节相同**、全树快照仅"被移动项"离开原位、失败项**不进 manifest**、journal receipt 带 typed reason；失败项永不转永久删除：两个模块 AST 扫描零破坏性调用（`unlink`/`rmtree`/`rmdir`/`remove`）、零 `sqlite`/`subprocess`/`ctypes` 导入、application 模块零变更型调用；"D 失败不得降级 C"由 `test_d_failure_cannot_degrade_to_permanent_delete__static_ast` 静态断言 + 上述运行时断言共同覆盖 |
| **AC4 隔离与禁令** | **MET** | `logs/static-scan.log`（766 files / 0 API hits；2 test files / 0 path literals；2 modules / 0 fallback）；`::test_static_scan_finds_no_windows_recycle_bin_api`、`::test_test_sources_reference_no_real_path_literals`；`::test_paths_outside_the_isolated_root_are_refused`、`::test_runtime_sentinel_outside_isolated_root_never_changes`；`logs/sentinel-probe.log` | `src/**` + `apps/**` 全量静态扫描（766 files，排除构建产物/第三方 vendored）Windows 回收站 API **0 命中**；`tests/fea12/**` 无 `%APPDATA%`/`%LOCALAPPDATA%`/`%USERPROFILE%`/`$env:APPDATA`/`$Recycle.Bin`/盘符路径字面量（检测器用片段拼接并对合成样本做非空证明）；隔离根外路径 → typed `failed + outside_isolated_root` 且零效果；运行时哨兵在成功 + 失败 + 生产默认三次运行后，隔离根外路径集合与逐文件 size/SHA-256 **完全不变**（探针 `PASS`，pytest 等价断言通过） |
| **AC5 交付件与门禁** | **MET** | `logs/gates.log`；`logs/gates.log` G2/G3/G5/G6/G7；Task 卡 + Handoff + `verification/FEA-12-DSIM-1/**`；Canonical Evidence 表 | pytest fea12 **13 passed**（EXIT 0）；全量 pytest **3093 passed / 10 skipped**（EXIT 0；基线 3073/10 → +20 = 本卡 13 + 并发已提交 FEA-11-LINEAGE-1 r3 的 7）；全量 .NET **失败 0 / 通过 1403 / 跳过 79**（8 assemblies，稳定树复跑）；`verify_pins.ps1` **PASS 18/18**；`check.ps1 -TaskPath` 结果见 `logs/check-final.log`；无 Python 生产接线 / 无 .NET 改动，.NET 数字与 PREREQ-1 绿跑一致 |

## 说明：本卡 ≠ D 流程完成

- 本卡只交付**模拟切片**：`SimulatedRecycleBin` 是测试替身，**不是**生产适配器；生产默认实现是 typed 不可用的 `UnavailableOriginalFileRecycleGateway`（fail-closed）。
- **真实 Windows 回收站行为未实现、未验证（`NOT_RUN`）**：零 OS API 调用、零真实回收站路径、零真实用户数据/AppData/外部卷操作；真实 OS 验证需用户另行专门授权。
- 崩溃恢复（SC-34 "先核对 OS 事实再决定是否重发"）未实现；journal/receipt 形状已建立，属真实 Host 桥任务。
- 无 Host/UI 接线、无 `IHostController`/C-07 冻结面改动、无 schema/migration/DB 改动、无新依赖、无 push。

## 并发工作树说明

- 全量 pytest / .NET 数字是在本卡交付时的**共享工作树**实测（同时含 FEA-11-LINEAGE-1 r3 已提交改动与 FEA-12-PREREQ-1 r2 已提交 docs）。
- 全量 .NET 首跑与第二次复跑各出现 **1 failed**（`FluentResidual2VisualEvidenceTests.Captures_Residual2_Visual_Inventory_Only_When_Opted_In`：断言运行期间 `git status --porcelain -- verification` 不变，被并发 teammate 写入 `verification/FEA-11-LINEAGE-1/logs/**`/重写 `verification/FEA-09` 命中窗口；日志 `dotnet-full-1.log`、`dotnet-full-2.log`）。稳定工作树复跑 **0 failed**（`dotnet-full-3.log`），失败与该测试自身断言窗口有关，与本卡 `src/**` 无 Python 改动无关。
- 首跑后 `verification/FEA-09/logs/wire-redacted.ndjson` 被 .NET 测试重写，已按卡要求 `git checkout -- verification/FEA-09` 恢复（EXIT 0）。
