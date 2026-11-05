# FEA-12-PREREQ-1 — AC Matrix

- 时间：2026-11-05（Asia/Shanghai）；**r2 返修后（r1 Review = changes_requested，P1 R-001 已修）**
- 基线：`base_commit = 035468a81e43e8d70fb711536824cdf613a7a0c4`
- 实现 head / 交付 commit：见 `doc/handoffs/FEA-12-PREREQ-1-035468a81.md`
- 门禁总日志：`logs/gates.log`（r2 处置见 G10；R-001 判别性见 G8）

| AC | 结论 | 证据 | 说明 |
|---|---|---|---|
| AC1 M2-C1 rev 2.13 additive 文本 | **MET（r2 修复 R-001 后）** | `logs/rev213-diff-audit.log`（PASS）、`logs/rev213-diff-audit-r2-before.log`（旧 head FAIL 判别性）、`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` | **166 insertions / 2 removed**（仅文档状态行 + §11 policy 行，均被 ADJ §D2/rev 管理授权）；§5.11.3 表 **2 个新码各一行齐备**（R-001：`BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE` 已补，表 code 集合 ⊇ 两个 ErrorView 集合，审计断言通过；旧 head 该断言 FAIL 证明判别力）；§5.11.1a/§5.11.5/§5.13/§5.14/§3.2/§11/§12/Revision history 完整登记；文档 rev=2.13；`PROTOCOL_MINOR` 仍 3、delete per-command minor 仍 10 |
| AC2 Host 投影 additive | **MET** | `REGISTRATION-COMPARISON.md`、`logs/dotnet-full-2.log`（CoreClient 165/0/23）、`logs/gates.log` G5/G6 | registry 5 新命令（preview minor 11、trash minor 13）+ 3 capability 常量/映射 + 20 码白名单；dispatcher closed-shape + additive digest 透传 + `ProjectDeleteTrashError`；CoreServiceClient 常量化；既有命令 wire/映射零语义改动；sidecar 回归 B1/B2 通过（r1 与 r2 各 3/3） |
| AC3 负向对照 | **MET** | `logs/baseline-negative-control-base-035468a81.log`、`logs/baseline-negative-control.log`、`test-evidence/commands/fea12-old-core-negative-control.json`、B1/B2 负向对照单测 | 基线：5 新码→`category=unknown` 且 code 原文保留；新命令 typed `UNKNOWN_COMMAND`；旧 Core 对 preview(2.11)/MoveToTrash(2.13) 返回 typed `UNKNOWN_COMMAND`（不静默丢弃）；对 delete 追加 `inventory_digest` 返回 `INVALID_REQUEST`（closed-shape fail-closed）。注册后新码投影为冻结 category/retryable（单测）。R-005：单测为「新投影器减 5 码」的重建集合；真实基线机制由基线脚本（ProjectRunError + run 白名单）演示，**结论不变** |
| AC4 治理门禁 | **MET** | `logs/gates.log` G1–G9 + Handoff（最终 `check.ps1`） | pins 18/18；`check.ps1` PASS（最终警告数见 Handoff；R-003 已把自指日志移出 evidence_dir）；全量 .NET 首跑 1 flaky（既有测试债务，单测复跑 1/1 通过）→ 恢复 FEA-09 后复跑 **1403 passed / 0 failed / 79 skipped**；pytest 3073 passed / 10 skipped（本卡无 Python 改动，r2 未重跑并已说明）；r2 命令治理测试复跑 135/0/15、live 负向对照复跑 3/3 |
| AC5 交付件 | **MET** | 本文件、`logs/`、`REGISTRATION-COMPARISON.md`、`ENVIRONMENT.md`、Task/Handoff、Canonical Evidence 表 | 无"未跑冒充实测"：每条结论对应日志/命令/EXIT；Handoff 记录交付 commit、r1 findings 处置与 r2 就绪声明 |

## 说明

- 全量 .NET 首跑唯一失败 `FluentResidual2VisualEvidenceTests.Captures_Residual2_Visual_Inventory_Only_When_Opted_In`
  与实现无关：该测试断言运行前后 `git status --porcelain -- verification` 不变，而同一 solution 运行的
  `NewManga.CoreClient.Tests.WireLogSourceRedactionTests` 会重写 tracked 证据
  `verification/FEA-09/logs/wire-redacted.ndjson`（既有行为）。单独复跑 1/1 通过；恢复 tracked 证据后
  全量复跑 0 fail。详见 `logs/gates.log` G3。r2 无产品代码改动，全量未重跑（`logs/gates.log` G3/G4/G10）。
- 本卡无 Python 产品改动；pytest 3073/10 为基线数字（与 FEA-11 r2 门禁 3073/10 一致）。
- **r2 处置摘要**：R-001 已修（P1，契约 + 判别性审计断言）；R-002 defer CORE（Handoff/卡内登记二选一集成要求）；
  R-003/R-004/R-005/R-006 已修或注明（P3）；r1 Review 报告 `doc/reviews/FEA-12-PREREQ-1-r1.md`（reviewed_head `5a7c7e028`）。
