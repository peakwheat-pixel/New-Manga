---
task_id: FEA-15-DIAG-ACL-1
reviewer: Codex Reviewer /root/fea15_diag_acl_review
reviewer_kind: subagent
author: Codex diagnosis author session
base_commit: 1e4542a047e991a5f10b0b213ca5a96eafe919a4
delivery_head: daeb6dcccbf970facd2272c00645255ae6bdfb87
reviewed_head: 610839af8348f8b1f36e18a623e9fc40882051b5
decision: approved
---

# Review：FEA-15-DIAG-ACL-1 r1

## 审查范围与独立性

审查来源为独立子任务 `/root/fea15_diag_acl_review`，未参与实现或返修。本结论只接受固定版本的诊断与证据交付，不代替主 Agent 的阶段裁决、终态门禁或 Task 关闭。

开始及结束检查均确认：

- 分支 `main`，HEAD 精确等于 `reviewed_head`。
- `git status --porcelain` 无输出，工作树干净。
- Git common directory 为 `G:/CODEX/New Manga/.git`。
- 未修改文件，未执行 ACL/profile/fixture 操作，未运行产品测试，未 push。

## Architecture

基线至被审 HEAD 的差异仅涉及 Task、状态、DAG、台账和诊断证据；`src/`、`apps/`、`tests/` 无变更。交付没有修改契约、Schema、依赖或 Host/Core 边界，符合当前 Windows / Avalonia / Python Core / SQLite 架构范围。

资源建议保持未知 ACL、profile、共享 fixture 原位保留，没有从测试失败推导清理授权。

## Verification

核对 Task、STATUS、PLAN、README、manifest、appointment、checkpoint、全部本轮探针日志，以及引用的 ACCEPT 原始日志和相关源码。

实测结果与矩阵一致：

- Python 全量：3515 passed、16 failed、12 skipped，EXIT 1。
- 主树定向：4 passed、15 failed，EXIT 1；export audit 断言为预期 2、实际 0。
- venv sandbox 对照：6 passed、10 failed，EXIT 1。
- Host 全量：198 passed、123 failed、74 skipped；8 项目中 2 项失败。
- Host archive 代表对照：1 passed、1 failed，EXIT 1，失败堆栈包含 `SetSecurityInfo` 与 `SourceSecurity.PrivateDirectory`。
- fixture 清单逐行计数为 62。
- v7 探针缺少 `custom_rank`；完整 v14 迁移探针记录缺失章节查询返回空结果。

5 条 CANONICAL 与 10 条 SOURCE_PIN 均满足：

1. 所列 commit 包含对应文件；
2. SHA-256 与当前工作树原始字节一致；
3. 当前内容与所列 commit 的内容在归一 LF/CRLF 后逐字一致。

其中 EV-02–05、SRC-02–05、SRC-07–08、SRC-10 的登记 SHA 与 Git blob SHA 不同，差异仅为行尾。`tools/governance/check.ps1:692–695` 明确允许工作树或 committed blob 两种 basis；依据协作协议 §4.4，不能把该观察直接认定为 pin 损坏。跨平台原始字节复核仍存在 EOL 可移植性限制，应留给既定专项任务。

`gates-review.log:1–39` 记录的执行 HEAD 为 `80edff3fcaf36e7f429dd68500a76472d38321b6`，两个治理检查各 EXIT 0、3 warnings，18 pins 审计 EXIT 0，整体 EXIT 0。其 HEAD、命令和 EXIT 记录自洽。该日志没有证明当前 `reviewed_head` 的门禁通过；README 已明确这一边界。本 Reviewer 未重新执行门禁，也无法仅凭持久日志独立证明历史命令确曾运行。

## AC1–AC5

| AC | 判断 | 依据与边界 |
|---|---|---|
| AC1 sandbox/export | PARTIAL，诊断交付可接受 | 跨主树、clean-tree、venv 的失败可复核；调用链符合 `service.py:346–378` 和 `sandbox.py:250–338`。现有日志不足以定位具体失败操作及原始错误，README 未强行归因于系统 Python ACL。venv 对照不是完整独立解释器，也没有被表述成完整独立对照。 |
| AC2 Host ACL | PARTIAL，诊断交付可接受 | 原始堆栈支持失败落在安全描述符写入路径；`SourceSecurity.cs` 的 owner、受保护 DACL、当前 SID FullControl 与报告相符。NTFS 能力和 PowerShell 成功不能证明 Host 原方法成功，报告已保留此限制。 |
| AC3 资源影响 | PARTIAL，保留建议成立 | ACE 48/24 行来自运行后快照，没有前置快照；profile 创建或复用机制存在，但归属未证实。全部 `PRESERVE_UNKNOWN` 合理，不能据此撤销授权或删除 profile。 |
| AC4 fixture | MET | 原始清单含 62 项时间窗候选；时间戳和用例名不足以证明唯一归属。原位保留、零清理的建议与证据一致。 |
| AC5 建议与交付 | PARTIAL | 矩阵、资源建议、v7 测试债、pins、历史 gate 和 NOT_RUN 已交付；本 Review 提供独立结论，最终门禁与阶段裁决仍未完成。不得提前改为全部 MET。 |

v7 测试债的界限恰当：`schema.py:930–932` 确认 `custom_rank` 在 v12 引入；v7 构造与当前查询不匹配得到支持，但正向内存探针没有证明真实旧库迁移、业务完整性或回退安全。

## Findings

未发现要求 `changes_requested` 的实质性问题；P0=0、P1=0。

以下为非阻断性收口提醒：

- `doc/STATUS.md:7`、Task:47 仍保留 ZCode Review/裁决措辞；appointment:10 仍引用较早 delivery evidence head。最新 appointment 和 Task reviewer 已明确本独立子任务，审查对象没有歧义；最终回填应统一当前指针。
- README 原先将 `SandboxError` 转换概括为 `PLUGIN_HOOK_UNAVAILABLE`；`service.py:374–377` 对 output exceeded 另映射为 `PLUGIN_HOOK_FAILED`。这不改变本次初始化/启动失败诊断，但本次收口已补全该例外。
- PowerShell ACL 探针没有完整脚本，不能独立复现全部参数；README 已披露，不可提升其证明力。

## NOT_RUN 与残余限制

保留以下未执行项：

- 精确 `SourceSecurity.PrivateDirectory` 原方法探针。
- 新的 sandbox/export 重跑。
- 系统 ACL/profile 归属与增量调查。
- fixture 清理、迁移。
- 真实用户库迁移、回退或数据操作。
- Review 后最终版本门禁。

原方法 `NOT_RUN` 没有被包装成成功结果，证据表达诚实。自动审批额度耗尽属于作者记录的未执行原因；本 Reviewer 没有审批服务原始记录，不能独立认证该原因，但未发现与现有证据矛盾的运行结果。

## 阶段建议与下一步

可以建议主 Agent 在最终门禁通过并回填当前指针后裁决 `closed_with_limitations`，同时保留 AC1–AC3、AC5 的未完成状态及上述限制。该状态只表示本诊断阶段收口，不表示根因已查明、回归已通过或产品可发布。

推荐下一步：主 Agent 保存本独立 Review、统一 reviewer/交付指针、在最终文档版本运行并留存治理检查与 pins 审计，再签发阶段结论。`FEA-15-PIN-EOL-GOV-1` 仍为 `proposed`、当前 READY 为空，本 Review 不释放该任务，也不授权 ACL/profile/fixture 处置。
