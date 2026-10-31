---
task_id: FEA-00-r2-remediation
kind: remediation_handoff_not_a_task
author: Codex
recipient: DeepSeek Harness
base_commit: 1180cdba79e4d610521dde13f0c8a458220f9d90
delivery_head: null
status: pending_independent_review
---

# FEA-00 Codex r2 问题修订交接

## 范围与状态

依据用户“处置报告中的问题”，修订 [Codex r2](../reviews/FEA-00-codex-r2.md) 指出的文档、治理检查器和判别力证据。本交接是修订者的事实记录，**不是独立 Review、DSH adjudication、Task 释放或批准**。`FEA-00-r2-remediation` 是交接标识，不是已创建的 Task；当前 Task 状态、生产代码和冻结 M2-C1 字节未改。所有修改目前仍在 `main` 工作树，未提交、未 push；未覆盖其他已有 dirty/untracked 内容。

| r2 项 | 修订及事实 | 剩余处置 |
|---|---|---|
| R2-01 / P0 | AD-003 §2 与 AD-002 的新增状态横幅均不再声称已证明变更前工作树原始字节；两处均说明去横幅、归一行尾后与 HEAD blob 一致，以及没有变更前工作树字节基线。实际比较通过，原 AD-002 正文未改。 | 无法补出不存在的变更前工作树 hash；请独立审查其三种口径及实际 diff。 |
| R2-02 / P1 | 检查器只从非注释、非 fenced code 的有效行提取唯一且值完整相等的 AD-002/AD-003/INDEX 哨兵；解析 AGENTS 当前架构值及首句真实 ADR 链接；INDEX 必须有唯一、状态正确的当前 ADR/裁定 Markdown 表格行。保留不扫描自由历史正文的边界。 | 新规则是有意收紧的格式约束；后续变更这些字段的格式时要同步规则及回归。请独立复审解析边界。 |
| R2-03 / P1 | 本次改检查器**之前**固定受影响集合与正负例计划，实跑 r2 和 Git HEAD 两个版本的完整 checker fixture 并保存日志；再实施修复和回归。实际 `$staticFiles` 为 HEAD 12、r2 14；当前 scope 15 包括所选 Task。 | DSH 先前修改的过程偏差不能通过本次事后证据追溯消除；若其事前全集证据不可得，保留“无法追溯”，由 DSH 作程序处置。不可把此前证据标为事前完成。 |
| R2-04 / P2 | AD-003 §4 区分 Core 命令、服务层与 Host/V2 接线，链接 ADJ-001 §7；V2 删除、回收站、恢复和永久删除均标 `NOT_WIRED`，运行行为待验证。 | 不把静态对照或治理检查器 PASS 当作 UI 功能验收。 |
| r2 表格 R-01 残余 | ADJ-001 PD-08 和 AD-003 §3.7 明确“只有……”限定于共享引用冲突；`BOOK_BUSY`、目标不存在等其他现行预检失败仍按 M2-C1 处理。 | 共享引用算法、并发与真实删除回归依旧 `NOT_RUN`。 |

## 当前修订指纹

| 文件 | SHA-256 |
|---|---|
| `doc/AD-002_TARGET_DESKTOP_ARCHITECTURE.md` | `00e3025bf654edcb3a2e44ab4175992241bd850c710439a9d879ad353463d0ef` |
| `doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md` | `0940a41bb0f2c14f77a50e66d34d983c83b40e0375230c1e027e98de75bcce15` |
| `doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md` | `9d8c9548dd921f5901464c63a8be63d2fb579e2aa2980b07dd34f29947f0662c` |
| `tools/governance/check.ps1` | `13e08555e4d7f107623f1daaea325bb8c8f776fb88e75b2ec9b87e2e25bde5f5` |
| `tools/governance/tests/test_architecture_assertions.py` | `4d639ba7bc15327ede458709ccb5810987749303f85cc622742b7a9187a63601` |
| 原 `doc/reviews/FEA-00-codex-r2.md` | `632a2a63e8d6e81748db2a7aae723c7e2c5f168495d1cfda3c1e322c0c22d9a9`（未改） |

## 验证与证据

证据目录：`G:/CODEX/New Manga.workspace/agent-output/codex/FEA-00-R2-remediation/`。原始输出是限定范围的治理检查/夹具结果，不是产品功能验收。

| 证据 | SHA-256 | 实测 |
|---|---|---|
| `pre-change-scope.txt` | `6f0ee472732e2ff7859b77079672707784f45c0e4e3ef2bc2afcc23b0774c58d` | 修改 checker 前定义集合、规则与负例；不代表先前 DSH 变更已有事前证据。 |
| `baseline-regression.log` | `51712bf0152548daa0723923d54440a410595cafed15444f4b598a87c9887500` | r2 checker：5 个测试方法，6 个负例未被拒绝；`EXIT=1`，正向当前文档和合法历史说明通过。 |
| `head-regression.log` | `3df163f0d21bb23840f126a8b6c24c3e260c976b01c000bd2e1a0f0411446597` | Git HEAD checker：同组测试 8 个失败；包括合法历史说明被旧正则误报；`EXIT=1`。 |
| `final-regression.log` | `ad7df8b0f7fa6d09d9e7d74108de6af1022aab331382db32c5b42ec0826052a6` | `python -B -m unittest discover -s tools/governance/tests -p test_architecture_assertions.py -v`：8 个测试方法、含多个子场景全部通过，`EXIT=0`；在隔离 workspace 中执行**完整 checker**。新增测试场景在初始基线之后补充，不能伪称全部有事前基线。 |
| `existing-ac-gate.log` | `fdbc5db912aecc1d04610e01d22c989aee6cee98d90a69159be6c988c8cde11a` | `python -B tools/governance/tests/test_ac_gate.py`：12/12 个 AC 门禁样例符合预期，`EXIT=0`。其中部分夹具预期出现其他 DAG/evidence 错误；不是所有检查全局 PASS。 |
| `governance-final.log` | `73f0a77c0ff8b29f6932473dbb1c8654aef15ff8f759d4ddfa9f6a3f04bcd244` | `pwsh -NoProfile -File tools/governance/check.ps1`：`PASS (2 warnings)`、`EXIT=0`；警告为 7 个非终态 Task 和 Plan 行数/体积预算。 |

AD-002 额外核验：去除工作树顶部状态横幅并将 CRLF 归一为 LF 后，与 Git HEAD blob 逐字节一致；HEAD blob SHA-256 `853c95113eca398186b883ebf1e914da3dba349fadea1b013d53e56b71c063ee`。这**不证明**变更前工作树字节。

## 接收与下一步

建议 DSH 接收本交接并安排 Codex 在**不同会话/独立上下文**复审上述固定字节、事前证据与残余程序偏差。可转发：

> 请只读复审 `doc/handoffs/FEA-00-codex-r2-remediation.md` 中固定的文件与证据，逐项核查 R2-01–R2-04 和共享引用残余；独立运行治理检查与隔离回归，核查不误报合法历史、不接受伪造断言。报告实际 reviewer 会话身份，不得以本交接或作者自测代替 Review。不得激活实现 Task、修改生产代码或 push。

实现 Task 无需下一步操作：本轮不创建或释放 Task；其他当前 Gate、审批和集成由 DSH 依项目规则处理。
