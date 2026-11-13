# New Manga V1 全项目审计报告

**报告状态：** P7 交付已由 Codex 七轮 fresh-context 独立 Review 裁决（首轮 `d92859c9a`、复审 `226eb048`、第三轮 `42810143b`、第四轮 `6350081a`、第五轮 `1ae79bb99`、第六轮 `c2f5bc827`、第七轮 `9bd7264ca`；最新 `reports/CODEX-FINAL6-REVIEW-2026-11-13.md`）。七轮结论均为 **REJECT**，属交付文档收敛要求；本报告的 finding 计数、候选状态与后续已按裁决更新；产品 Release Gate 仍 BLOCKED。
**产品基线：** 10e4ee013835605800d3830fb960ae8d3aa04167。
**审计执行分支：** main。
**产品发布准入：** BLOCKED。

## 执行摘要

本轮审计对段 B 当前产品基线完成 AUDIT-00–14 的阶段性检查。专项有 PASS / FAIL / PARTIAL / BLOCKED 结果及具名限制；未把合成测试、编译成功、历史包或未执行项目当作真实产品验收。

全项目质量目前**无法评为通过**：Codex 裁决后共有 7 项开放 finding（3 项原 triaged：两项 Medium / High confidence 与 `NM-AUD-0001` P2；4 项新裁：`AUDIT-07-CAND-001` P2、`AUDIT-09-CAND-001` P3、`AUDIT-12-CAND-001` P3 交付工具、`AUDIT-14-CAND-001` 非产品文档）；完整 Python pytest 有 16 个失败；Avalonia TestHost 未进入测试用例；若干真实 UI、模型、API 与安装流程未验证。Release Gate 为 BLOCKED。此结论独立于审计文档返修进度。

11 个候选与 `AUDIT-11-INC-001` 已由 Codex 独立裁决：4 项 finding、4 项 INVESTIGATE、1 项 accepted limitation、2 项 close；`AUDIT-11-INC-001` 维持 INVESTIGATE 且不计 P0–P3/finding。产品 P0=0、P1=0、P2=2、P3=2；P0/P1 为当前已分配数量，不表示已证明不存在。

## 范围与方法

- 冻结产品审计基线：10e4ee013835605800d3830fb960ae8d3aa04167。
- 段 A 历史状态保持原样；本报告只总结段 B 新证据，不追溯改写旧 PASS。
- 使用仓库原始审计清单、任务矩阵、专项报告、隔离 synthetic fixtures、真实 Windows UI 空态会话、定向 pytest、构建与静态检查。
- 未改产品源码、原有测试、契约、Schema、依赖、真实用户数据或远端；没有安装旧包、发布、push、清理 Git 历史或调用付费 API。
- 全部范围、命令、generated HEAD、EXIT、日志/JSON 和截图由 audit/V1-FULL-AUDIT/AUDIT_EVIDENCE_INDEX.md 索引。

## AUDIT-00–14 总览

| 专项 | 状态 | 结论摘要 |
|---|---|---|
| 00 基线 / 盘点 | limited PASS | 当前 Git/environment/source inventory 有限完成；外部模型字节、运行行为不在该项 PASS 中。 |
| 01 架构 / 生命周期 | FAIL | helper 通过真实 SidecarProcess API 复现取消 / dispose 返回后子进程仍存活，NM-AUD-0001，P2。 |
| 02 源码质量扫描 | BLOCKED | AST / project graph / build 有证据；whitespace EXIT 2、1,556 项诊断；多类工具未安装、analyzers 关闭、语义扫描未完成。 |
| 03 导入 / 项目路径 | FAIL | Core 87、ReferencedSource 77 passed；junction 下 ManagedFileStorage.publish 越出 managed root，SEG-B-PROBES-001。 |
| 04 OCR / detection | PARTIAL | provider / Core 合成回归 175 + 40 passed；无真实权重、GT、准确率或 CPU inference。 |
| 05 SFX | PARTIAL | 定向合成组 247 passed / 3 deselected；AUDIT-05-CAND-001 已由 Codex 裁为 INVESTIGATE；真实权重、GT、UI 未测。 |
| 06 翻译 | PARTIAL | 合成上下文组 84 passed；真实 API / 费用 / 取消未测；两个候选已由 Codex 裁为 INVESTIGATE。 |
| 07 修复 / 排版 / 导出 | PARTIAL | 多组定向测试通过；Core/rerender/export 127 passed、3 failed、EXIT 1；视觉质量、真实模型与字体许可未测。 |
| 08 数据库 / 恢复 | FAIL | 合成 DB 284 passed；restore 磁盘写失败复现确认 SEG-B-PROBES-002。 |
| 09 UI/UX | PARTIAL | Legacy 与 V2 空态、设置、Reader fallback/快捷键有实际观察；Fluent Host 115.344s 未 ready；大量交互 NOT_RUN。 |
| 10 性能 / 稳定性 | PARTIAL | 四项 720×1080 synthetic Core microbench；无 I/O、模型/API、soak 或产品阈值。 |
| 11 安全 | FAIL（静态阶段） | SEG-B-PROBES-001/002 共用既有 findings；私有素材传播风险待调查；其余多项 PARTIAL / NOT_TESTED。 |
| 12 Windows 交付 | PARTIAL | Release build EXIT 0；仅找到不绑定当前基线的历史包；本 Task 未安装、发布或卸载。 |
| 13 E2E | PARTIAL | 三个 production Core acceptance 文件 31 passed、0 skipped；A/D/E/G/H 部分 synthetic 覆盖，B/C/F 与完整桌面链未测。 |
| 14 V1 完整性 | PARTIAL | 有 MainWindow 接线及 V2 NOT_WIRED 静态观察；缺权威逐项 commitment manifest，完成率 NOT_COUNTABLE。 |

具体矩阵、证据边界和 NOT_RUN 项见 reports/02_ARCHITECTURE_REVIEW.md 至 reports/10_WINDOWS_RELEASE_REVIEW.md 及各 AUDIT-NN 专项报告。

## Finding 数量与处置

- P0：0 项已被正式分配；这不是“已证明没有 P0”。
- P1：0 项已被正式分配；这不是“已证明没有 P1”。
- P2：2 项，NM-AUD-0001 与 AUDIT-07-CAND-001，均未修复。
- P3：2 项产品 finding，AUDIT-09-CAND-001 与 AUDIT-12-CAND-001；另 AUDIT-14-CAND-001 为 P3 优先级文档 finding，不并入产品 P0–P3 计数。AUDIT11-REV-001 是已披露关闭的非产品 P3 observation。
- 其他量表：SEG-B-PROBES-001 与 SEG-B-PROBES-002 均为 Medium / High confidence，不与 P-level 合并计数。
- 开放 finding 共 7 项；另有 AUDIT-11-INC-001 1 条 INVESTIGATE 风险，不计 finding。
- 11 个候选已由 Codex 裁决：4 finding / 4 INVESTIGATE / 1 accepted limitation / 2 close。

完整去重记录、证据、分类和已裁决问题见 reports/11_ISSUES.md 以及 AUDIT_ISSUES.md。

## 测试结果摘要

- Python Core 全量 pytest：3,519 passed / 16 failed / 10 skipped / 11 warnings，EXIT 1。
- Avalonia TestHost：8/8 runner EXIT 1、TRX 0 tests，BLOCKED-TESTHOST-ACCESS。
- Core/Wire smoke：EXIT 1；Wire 6 PASS、Core 4 PASS / 7 BLOCKED-SANDBOX-GRANT；frontend / packaged SKIP。
- Avalonia Release build：EXIT 0、0 warnings / 0 errors；没有安装或打包当前基线。
- 专项结果按 AUDIT-00–14 状态表分开陈列。pytest / probe EXIT 0 有时代表 fixture 成功复现缺陷，不可一概解释为产品通过。

逐命令原始日志和结果见 reports/08_TEST_RESULTS.md 与 AUDIT_EVIDENCE_INDEX.md。

## 功能完整性与 Windows 发布判断

目前缺少 V1 与未来规划的权威逐项总账，不能计算整体承诺完成率。V2 Studio 静态 inventory 标记多个可见能力 NOT_WIRED，但它们是否属于 V1 承诺已由 Codex 裁为 INVESTIGATE（V1 归属待 manifest）。

Windows build 成功不等于 Windows 发布成功。没有当前基线包 provenance、clean install、升级/回退、安装后四个一级页面验收和卸载证据。历史包未被执行。

## 主要未解决风险与证据缺口

1. managed root junction 越界写、restore I/O failure 无 rollback ID、sidecar 生命周期问题均未修复。
2. 16 个 Python pytest 失败未归因/修复；Avalonia TestHost / sandbox 前置阻断仍在。
3. 真实模型、人工 GT、实际翻译服务/费用、完整页面编辑/导出和长时稳定性未验证。
4. clean Windows 安装、升级/回退、权限/中文路径、当前 installer 与模型资源 provenance 未验证。
5. 当前公开远端对历史私有素材对象的可见性未知；没有远端访问或补救。
6. 11 个候选已由 Codex 裁决；`AUDIT-11-INC-001` 仍为 INVESTIGATE，远端可见性未知。

## 整改路线与发布 Gate

建议路线、依赖、影响文件、验收标准和回归范围见 reports/12_REMEDIATION_PLAN.md。发布结论见 reports/13_RELEASE_GATE.md：BLOCKED，不建议发布，不满足 PASS 或 CONDITIONAL。

## 结论边界与后续

本报告是当前证据的综合摘要，不是产品发布批准。候选分级与最终独立 Review 已由 Codex 作出（结论 REJECT，要求返修）；Task AC 状态、生命周期与最终集成由 DSH 处置。

**直接下一步：** 固定本轮文档收敛后的 clean head，由 DSH 完成集成、Canonical Evidence/资源 closeout 与最终四项门禁；产品实现按 R1–R4 另立 Task。不得修改产品源码、修改冻结契约、发布或 push。
