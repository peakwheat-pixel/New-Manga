# FEA-12-DSIM-1 — AC Matrix（r2）

- 时间：2026-11-05（Asia/Shanghai）
- 仓库：`G:\CODEX\New Manga`（`main`）；base_commit `37f84bb895c9ef9b64e3865f3a92b245f2e28a7c`
- 实现 commits：`94a12e93f`（协议/模拟件/测试）、`3d0d325f7`（目录指纹 junction 拒绝 + normcase）、**`d5925957b`（r2：R-001 自身写目标加固 + 8 项判别测试）**
- 交付 docs commit：见 Handoff `doc/handoffs/FEA-12-DSIM-1-d5925957b.md`
- 门禁总日志（仓外，Resource Manifest 登记）：`G:\CODEX\New Manga.workspace\agent-output\fea12-dsim-impl\FEA-12-DSIM-1\gates.log`
- 隔离/静态/哨兵细节：`ISOLATION-EVIDENCE.md`；环境与 per-commit scope：`ENVIRONMENT.md`

| AC | 结论 | 证据 | 说明 |
|---|---|---|---|
| **AC1 协议与生产默认实现** | **MET** | `tests/fea12/test_recycle_gateway_sim.py::test_protocol_is_structural_and_the_typed_vocabulary_is_closed`、`::test_production_default_is_typed_unavailable_with_zero_side_effects`、`::test_no_production_file_references_the_d_flow_port`；`logs/sentinel-probe.log` run 3 | 协议 `move_to_recyclebin(entries, *, journal)`（journal keyword-only 必填）；逐项 typed `moved`/`failed`/`not_started` + 封闭 reason 词表；生产默认 typed 不可用、`operation_id=""`、零文件/journal/DB 操作；`src/**`/`apps/**` 对端口零引用；application 不 import infrastructure |
| **AC2 模拟实现（r2 收窄表述）** | **MET（限定）** | `::test_simulated_move_is_auditable_and_keeps_original_path_semantics`、`::test_simulated_bin_refuses_non_isolated_roots`、**R-001 6 项**：`::test_filesystem_root_is_refused`、`::test_root_reached_through_a_junction_is_refused`、`::test_preplanted_bin_dir_junction_is_refused_without_outside_writes`、`::test_preplanted_journal_hardlink_is_refused_without_outside_writes`、`::test_replanted_bin_dir_junction_is_refused_at_write_time`、`::test_replanted_journal_hardlink_is_refused_at_write_time`；`ISOLATION-EVIDENCE.md` §2 | **限定表述**：在**调用者提供的干净隔离根**内，全部写入限定在该根内；且 gateway **自身写目标**（bin 目录/manifest/journal）在构造期与每次读写前做 realpath containment + junction/symlink/硬链接（`st_nlink>1`）拒绝，检测到即 typed `RecycleSafetyError` 且零写入。**不再声称"任何情况下全部写入都在隔离根内"**：校验与写入之间的并发重植窗口（TOCTOU）未消除，属单写者测试替身固有残余风险（见 §残余风险） |
| **AC3 失败语义** | **MET** | `::test_failure_injection_keeps_original_bytes_and_never_deletes`、`::test_missing_selection_is_a_typed_failure_without_side_effects`、`::test_verify_failed_rolls_back_to_the_original`（r2 新增）、`::test_d_failure_cannot_degrade_to_permanent_delete__static_ast`；`logs/static-scan.log` §AC3；`logs/sentinel-probe.log` run 2 | 注入拒绝下原文件字节/集合不变、失败项不进 manifest、receipt 带 typed reason；`verify_failed` 回滚恢复原文件；两模块 AST 零破坏性调用/零 DB/零进程、application 零变更型调用；"D 失败不得降级 C"有静态 + 运行时断言 |
| **AC4 隔离与禁令** | **MET** | `logs/static-scan.log`（766 files / 0 API；2 test files / 0 literals；2 modules **1020 lines** / 0 fallback）；`::test_static_scan_finds_no_windows_recycle_bin_api`、`::test_test_sources_reference_no_real_path_literals`、`::test_paths_outside_the_isolated_root_are_refused`、`::test_runtime_sentinel_outside_isolated_root_never_changes`；`logs/sentinel-probe.log` | 静态 0 命中；测试无 `%APPDATA%`/盘符/`$Recycle.Bin` 字面量；隔离根外路径 typed 拒绝零效果；运行时哨兵三次运行后根外逐文件 size/SHA-256 不变（`outside changes: []`）；**AppData 表述已修正**（OS temp scratch ≠ 用户 AppData 业务数据） |
| **AC5 交付件与门禁** | **MET** | `gates.log`（仓外 agent-output）；Task 卡 + Handoff + `verification/FEA-12-DSIM-1/**`（含 `agent-output-manifest.json`） | pytest fea12 **21 passed**；全量 pytest **3101 passed / 10 skipped**（r1 交付基线 3093/10，+8 = 本卡 r2 新测试）；全量 .NET：r2 尝试 1 次 flaky（1 failed/670/7，归因既有 FEA-09 证据重写与并发 CORE 还原窗口，日志 `dotnet-r2-1.log`），**r2 无 .NET 改动 → 引用 r1 稳定树绿跑 1403/0/79**（`dotnet-full-3.log`）；pins **18/18**；`check.ps1 -TaskPath` PASS **3 warnings、无 evidence_dir 告警**（warnings 均为预存/Lead-owned：13 非终态 Task、STATUS 80% 预算、PLAN 80% 预算；过程日志已迁 agent-output，见 `agent-output-manifest.json`） |

## 说明：本卡 ≠ D 流程完成

- 只交付**模拟切片**：`SimulatedRecycleBin` 是测试替身，生产默认是 typed 不可用（fail-closed）。
- **真实 Windows 回收站行为未实现、未验证（`NOT_RUN`）**，需用户另行专门授权；不得据此声称 D 流程完成。
- 崩溃恢复（SC-34）、真实 OS 桥、Host/UI 接线、schema/依赖变更均不在本卡。

## r2 处置（Review r1 findings）

| ID | 级别 | 处置 |
|---|---|---|
| **R-001** | P2 | **已修复**：bin/manifest/journal 在构造期 + 每次读写前 realpath containment + reparse/hardlink 拒绝，typed `RecycleSafetyError` 零写入；新增 6 项判别测试（真实 `mklink /J` junction + `os.link` 硬链接）；AC2/ISOLATION 表述收窄并登记 TOCTOU 残余风险 |
| **R-002** | P2 | **已修复**：`logs/gates.log`、`logs/check-final.log` 迁至 `G:\CODEX\New Manga.workspace\agent-output\fea12-dsim-impl\FEA-12-DSIM-1\`；新增 `verification/FEA-12-DSIM-1/agent-output-manifest.json`（EV-19）登记 bytes/sha256；Resource Manifest 更新为 PRESERVE_REFERENCED；`check.ps1` PASS **3 warnings、无 evidence_dir 告警** |
| R-003 | P3 | **已修复**：ENVIRONMENT 引用改为 r2 Handoff `FEA-12-DSIM-1-d5925957b.md` 并补列 fix commit |
| R-004 | P3 | **已修复**：ISOLATION-EVIDENCE 行数改为 r2 实测 **1020 lines**（`logs/static-scan.log`） |
| R-005 | P3 | **已补**：ENVIRONMENT 增加 per-commit scope 证明（本卡 4 个自有 commit 文件集；range 含其他任务 commit 的说明） |
| R-006 | P3 | **已修正**：.NET 首跑归因改为实测 diff（`verification/FEA-12-PREREQ-1/tools/rev213-diff-audit…` → `…/logs/…` 的并发 PREREQ-1 证据写入，见 `dotnet-full-1.log` 原样输出），Handoff/G3 同步 |
| R-007 | P3 | **已补**：fs-root 拒绝、真实 junction（`mklink /J`）、`verify_failed` 回滚、`already_in_bin` 均入库（8 项新测试）；manifest 写失败/损坏与 journal 目录/符号链接未补（见残余风险） |
| R-008 | P3 | **已修正**：`ISOLATION-EVIDENCE.md` §4 改为"OS temp scratch（物理位于 AppData\Local\Temp）≠ 用户 AppData 业务数据"，不再使用"AppData 零操作"字面 |
| R-009 | P3 | **已补**：全部 raw log 前加 provenance 头（command / shell+python / head / captured / EXIT / summary），见 `logs/*.log` 首行块 |

## 残余风险（r2 更新）

1. **模拟 ≠ 真实 D**：真实 Windows 回收站 `NOT_RUN`，需另行授权。
2. **TOCTOU**：自身写目标校验与写入之间是两次独立系统调用，并发重植窗口未消除；模拟件单写者，真实桥需绑定句柄。AC2 已按此收窄，不再声称无条件隔离。
3. **全量 .NET flaky（外部窗口）**：`FluentResidual2VisualEvidenceTests` 断言运行期间 `verification` git status 不变；r1 首跑/二次与 r2 尝试均命中并发写入窗口（r2 实测 diff：`M verification/FEA-12-DSIM-1/logs/...` vs `M verification/FEA-09/logs/wire-redacted...`）。**本卡无 .NET 改动**，r1 稳定树复跑 1403/0/79 可引用。
4. **manifest 写失败/损坏**：移动成功但 manifest/receipt 写失败时不回滚（异常上抛，journal 只有 attempt），属崩溃恢复残余风险。
5. **目录内 junction/symlink**：代码拒绝为 `unsupported_entry`，但选中文件夹内的 junction 无 OS 级测试（真实桥需覆盖）。
6. **pytest 数字含并发改动**：共享工作树含 FEA-12-CORE 未提交改动与已提交的其他任务测试；本卡只新增 `tests/fea12/**`。
