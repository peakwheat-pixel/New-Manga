---
task_id: FEA-15-DIAG-ACL-1
author: Codex primary Agent
recipient: 项目后续 Owner；ZCode 负责 proposed successor 的范围复核
base_commit: 1e4542a047e991a5f10b0b213ca5a96eafe919a4
delivery_head: 610839af8348f8b1f36e18a623e9fc40882051b5
status: closed_with_limitations
---

# Handoff：FEA-15-DIAG-ACL-1

## 交付结果

完成只读测试失败与资源影响诊断。没有改生产代码、测试、依赖、Schema 或冻结契约；没有修改系统 ACL、枚举/删除 profile、清理 fixture、访问真实用户库或 push。

| AC | 结果 |
|---|---|
| AC1 sandbox/export | `PARTIAL`：跨主树、clean-tree 与 venv 失败已记录；失败操作和底层原始错误未定位。 |
| AC2 Host ACL | `PARTIAL`：异常链指向 `SetSecurityInfo` / `SourceSecurity.PrivateDirectory`；精确原方法探针 `NOT_RUN`。 |
| AC3 资源影响 | `PARTIAL`：Python ACL 与 profile 缺少运行前快照，归属未知；按 `PRESERVE_UNKNOWN` 保留。 |
| AC4 fixture | `MET`：62 个时间窗候选均保留原位，零清理、零迁移。 |
| AC5 建议与交付 | `MET`：诊断矩阵、v7 测试构造债、限制和 NOT_RUN 已留证；独立 Review `approved`，P0/P1=0；最终治理门禁见 `gates-terminal.log`。 |

独立 Review 报告：[`FEA-15-DIAG-ACL-1-r1.md`](../reviews/FEA-15-DIAG-ACL-1-r1.md)。审查者为新上下文子 Agent `/root/fea15_diag_acl_review`，只读审查固定 HEAD `610839af8348f8b1f36e18a623e9fc40882051b5`。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 Python 全量 | `python -m pytest -q -rs` | Task clean-tree，HEAD `d63d735a712dbe47100db2e72b4d59a73dfd1f62` | 3515 passed / 16 failed / 12 skipped，EXIT 1 | `verification/FEA-15-ACCEPT-1/pytest-full-retry.log` |
| AC1 sandbox/export 定向 | `python -m pytest -q -rs tests/infrastructure/test_plugin_sandbox.py tests/core/test_p16_reader_export.py::test_export_hook_effective_options_match_content_and_history` | 主树隔离环境，HEAD `d63d735a712dbe47100db2e72b4d59a73dfd1f62` | 4 passed / 15 failed，EXIT 1；export audit 预期 2、实测 0 | `verification/FEA-15-ACCEPT-1/pytest-main-targeted.log` |
| AC1 venv 对照 | `venv-python -m pytest tests/infrastructure/test_plugin_sandbox.py -q -rs` | 专用 venv，fixture source `d63d735a712dbe47100db2e72b4d59a73dfd1f62` | 6 passed / 10 failed，EXIT 1；非完整独立解释器 | `verification/FEA-15-ACCEPT-1/plugin-control.log` |
| AC2 .NET 全量 | `dotnet test each project -c Release --no-build --nologo -v normal` | Task clean-tree，HEAD `d63d735a712dbe47100db2e72b4d59a73dfd1f62` | Host 198 passed / 123 failed / 74 skipped；8 项目中 2 项失败；EXIT 1 | `verification/FEA-15-ACCEPT-1/dotnet-full.log` |
| AC2 Host 代表对照 | `dotnet test Host.Tests -c Release --filter FullyQualifiedName~Fea11SourceIpcTests.FailureRecordHostControlPayloadStaysFlat|FullyQualifiedName~RunGrantRenewalTests.HostWiring_ManagedOnlyRun_StartsNoRenewal` | Host archive fixture，HEAD `8cad6d68c1e455c087a20346c9b1c0217bef129e` | 1 passed / 1 failed，EXIT 1；失败堆栈含 `SetSecurityInfo` | `verification/FEA-15-ACCEPT-1/dotnet-host-control.log` |
| AC3/AC4 资源边界 | 只读核对观测日志与 62 项 fixture 清单；不执行清理 | Task-owned workspace / shared FEA-11 fixture path | ACL/profile 与 fixture 归属不可判定；全部保留 | `resource-manifest.json`、`../FEA-15-ACCEPT-1/python-acl-observation.log`、`fixture-observation.log` |
| AC5 Review | 新上下文 Reviewer 只读审查固定交付 HEAD | Reviewer `/root/fea15_diag_acl_review`；reviewed head `610839af8348f8b1f36e18a623e9fc40882051b5` | `approved`，P0=0/P1=0 | `doc/reviews/FEA-15-DIAG-ACL-1-r1.md` |
| AC5 终态治理门禁 | `pwsh -NoProfile -File tools/governance/check.ps1`；`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-15-DIAG-ACL-1.md`；`pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 干净 `main`，HEAD `05b22084828bff3ad27a96093652beff92dbe108`；完成时点、完整输出与 EXIT 见 `gates-terminal.log` | default PASS（3 warnings，EXIT 0）；TaskPath PASS（5 warnings，EXIT 0）；pins 18/18 PASS（EXIT 0） | `verification/FEA-15-DIAG-ACL-1/gates-terminal.log` |

本 Task 收口后没有重跑产品测试；上表产品测试是被引用的历史实测，不代表当前 HEAD PASS。NOT_RUN 仍包括精确 Host 方法探针、sandbox/export 新重跑、ACL/profile 归属调查、fixture 清理/迁移和真实用户库操作。

## 接收方式

- 仓库：`G:/CODEX/New Manga`；分支：`main`；固定诊断交付及 Reviewer head：`610839af8348f8b1f36e18a623e9fc40882051b5`。
- 收口提交只包含文档与证据；`integration_commit` 保持 `null`，因为没有生产实现集成。
- 本 Task 的未知资源继续原位保留。不要从本诊断推导 ACL 恢复、profile 删除、fixture 清理或真实用户库操作授权。

## 下一任务建议

- Task ID / 标题：`FEA-15-PIN-EOL-GOV-1` / 证据 pin 行尾与跨 checkout 可复现性治理。
- 推荐 Agent / Reviewer：ZCode 先做范围复核与 release adjudication；如卡片释放后由 Codex 实施，另派独立上下文 Reviewer。
- 推荐原因与前置依赖：本次 Review 记录 pin 的工作区字节与 Git blob 行尾差异；候选卡仍是 `proposed` / `pending_scope_review`，须先重盘影响全集并冻结范围。
- Recovery point：仓库 `G:/CODEX/New Manga`，branch `main`；诊断 evidence base `1e4542a047e991a5f10b0b213ca5a96eafe919a4`、reviewed head `610839af8348f8b1f36e18a623e9fc40882051b5`。新 Task worktree 尚未创建，待范围冻结后由其 Owner 建立。
- 允许修改路径：只按 [`FEA-15-PIN-EOL-GOV-1.md`](../tasks/FEA-15-PIN-EOL-GOV-1.md) 在 release 时冻结的 `allowed_paths`。
- 禁止范围：未单独冻结前不得实施；不得修改 `.gitattributes`、检查语义、历史证据或冻结契约。
- 交付物：按候选卡产出当前 pin 全集、跨 checkout 口径矩阵、历史差异证据、授权方案及独立 Review。
- 验证命令、环境与完成 Gate：按 release 后的卡面；保存每次命令的环境、HEAD、时间与 EXIT，先完成影响全集核验，再进行任何口径/迁移裁决。
- 可直接转发给 Agent 的指令：

> ZCode：请先复核并裁决 `doc/tasks/FEA-15-PIN-EOL-GOV-1.md` 的 Task 范围与依赖。该卡当前为 `proposed` / `pending_scope_review`，本 Handoff 不授权实施。若批准 release，请先冻结影响全集、base、branch/worktree、Owner、独立 Reviewer、`allowed_paths`、证据目录与逐项验收 Gate，再把卡置为 `ready` 并更新 STATUS/Plan；不得在 release 前改 `.gitattributes`、检查语义、历史证据或冻结契约。

目前没有已释放的后续实施 Task；上述 successor 仅待范围复核，不应自动开始。

## 风险与遗留

- Host ACL 的具体拒绝条件未知；Python ACE 和 AppContainer profile 的来源、增量未知；62 个共享 fixture 候选没有证明唯一归属。
- v7 fixture 与 v12 起的 `chapters.custom_rank` schema 不匹配；v14 内存探针不证明真实用户库迁移/回退安全。
- 所有遗留资源均保留原位；没有清理、迁移、归档或外部 push。
