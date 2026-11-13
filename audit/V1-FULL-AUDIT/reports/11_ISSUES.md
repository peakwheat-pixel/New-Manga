# 11 去重问题台账（Codex 裁决后版本）

**审计基线：** 10e4ee013835605800d3830fb960ae8d3aa04167
**裁决来源：** Codex 全新上下文的最终独立 Review，`reviewed_head=d92859c9ac8a4d3122d6cabfe4d44af980574104`，session `01a1d4ce-6b79-7b43-939d-834e3cdc21a9`，EXIT 0；原始报告 `reports/CODEX-FINAL-REVIEW-2026-11-13.md`。该 Review 结论为 **REJECT**（要求返修交付文档），但已逐项处置 11 个候选与 `AUDIT-11-INC-001`；产品 Release Gate 维持 BLOCKED。
**历史说明：** 原 P7 初版（审计作者不重定级、候选 `REVIEW_PENDING` 待 ZCode）保存在 Git 历史与 `AUDIT_RESUME.md` 的历史检查点中；本文件反映 Codex 裁决后的当前台账。

## 汇总

| 类别 | 数量 | 说明 |
|---|---:|---|
| 原已 triage 产品 finding | 3 | `SEG-B-PROBES-001`、`SEG-B-PROBES-002`（Medium / High confidence）；`NM-AUD-0001`（P2） |
| 本次 Codex 裁为 finding 的候选 | 4 | `AUDIT-07-CAND-001`（P2）、`AUDIT-09-CAND-001`（P3）、`AUDIT-12-CAND-001`（P3，交付工具）、`AUDIT-14-CAND-001`（P3 优先级，非产品 P0–P3 计数） |
| 维持 INVESTIGATE 的候选 | 4 | `AUDIT-05-CAND-001`、`AUDIT-06-CAND-001`、`AUDIT-06-CAND-002`、`AUDIT-14-CAND-002` |
| accepted limitation | 1 | `AUDIT-07-CAND-002` |
| close | 2 | `AUDIT-14-CAND-003`（关闭“当前 release 会失败”断言）、`AUDIT-14-CAND-004` |
| 未决调查风险 | 1 | `AUDIT-11-INC-001`；维持 INVESTIGATE，不分配 severity，不计 P0–P3 或 finding 数 |
| 已披露关闭的非产品观察 | 1 | `AUDIT11-REV-001`，P3；不是产品 finding |
| 产品 P0 / P1 / P2 / P3 | 0 / 0 / 2 / 2 | P0、P1 为当前已分配数量，不表示已证明不存在；SEG-B findings 不映射 P 级 |
| 开放 finding 总数 | 7 | 3 原 finding + 4 新增；其中 4 项产品 P 级、2 项 SEG-B 未映射 P 级、1 项非产品文档 finding |

## 开放 finding

| ID | 状态 / 等级 | 裁决与依据 | 后续 |
|---|---|---|---|
| SEG-B-PROBES-001 | TRIAGED；Medium / High confidence | junction 下 `ManagedFileStorage.publish` 可在 managed root 外写入 revision bytes；probe 已复现，未映射 P 级。 | 独立实现 Task 增加 containment/reparse 防线；隔离回归。 |
| SEG-B-PROBES-002 | TRIAGED；Medium / High confidence | restore 磁盘写失败后数据库已变更、裸 I/O 错误无 rollback ID；pre_restore 包保留。 | 独立实现 Task 收敛 typed error 与 rollback ID；故障注入回归。 |
| NM-AUD-0001 | TRIAGED；P2 | sidecar 取消/dispose 后忽略 EOF 的 helper 子进程仍存活；受控 helper 经真实 API 复现。 | R2 独立实现 Task：幂等 stop/cleanup、spawn 后取消清理、Host shutdown 顺序。 |
| AUDIT-07-CAND-001 | finding；P2 | 定向测试 127 passed / 3 failed：ZIP `store`、JSON text override、空 options 的 hook audit events 不符预期；不涉及排版像素质量。 | 独立实现 Task 修正 options/hook 行为并跑 export 回归组。 |
| AUDIT-09-CAND-001 | finding；P3 | 合成空章节路径下界面显示已选作品/章节，Retry 却提示先选择；单一已记录用户可见不一致，根因与普遍性未知。 | 隔离 Host/UI fixture 复现选中/未选中/零页/切换路径后修正提示与状态。 |
| AUDIT-12-CAND-001 | finding；P3（交付工具） | `publish.ps1` 默认输出到仓库 `artifacts/win-x64-single` 并递归清理；违反产物应放在相邻 workspace 的规则；脚本未运行，无已误删证据。 | 新 Task 将默认输出移出仓库并用 disposable 目录验证清理仅限专用目录。 |
| AUDIT-14-CAND-001 | finding；P3 优先级（非产品 P0–P3 计数） | README 存储默认表述与 AD-003 不一致；AD-003 实现清单过期；缺可逐项核验的 V1 承诺总账，完成率不可计数。 | 独立文档 Task 建立有日期/版本的 V1 manifest 并对齐 README/AD-003/STATUS/索引。 |

## 未决调查风险

| ID | 状态 | 风险陈述与边界 | 处置 |
|---|---|---|---|
| AUDIT-11-INC-001 | INVESTIGATE；不分配 severity，不计 P0–P3/finding | 本地 reflog 与提交祖先关系支持私有素材对象可能曾随历史 main push 进入公开仓库的高置信推论；**当前远端是否可见、可下载或可 fetch 仍未知**，远端缓存/对象状态与当时授权语境也未知。不得写成已公开或已消除。 | R1 独立、授权范围冻结的只读 Task 核验远端可见性并记录目标/时间/结果；任何删除、改写历史或补救另行裁决。 |

## 已裁为其他状态的候选

| ID | 状态 | 依据 |
|---|---|---|
| AUDIT-05-CAND-001 | INVESTIGATE | 合成 same-geometry 产生双 SFX Region；既有仲裁任务已记录副作用，但产品去重语义未确定。先定义相同/近似区域、人工修改、`skip`/`translate` 规则。 |
| AUDIT-06-CAND-001 | INVESTIGATE | 有 StepRun 与 provider 重试上限，无账单级预算；未调用付费 API，无重复计费证据；费用上限是否内建需需求裁决。 |
| AUDIT-06-CAND-002 | INVESTIGATE | glossary 进入请求但无严格输出校验；原始需求未证实要求逐项强制匹配，真实模型未测。 |
| AUDIT-07-CAND-002 | accepted limitation | `license_note` 仅为备注；仓库 tracked font assets=0，FEA-14-FONT-1 明确默认不随包分发字体；无未授权分发证据。 |
| AUDIT-14-CAND-002 | INVESTIGATE | V2 Studio 有静态 `NOT_WIRED` 能力，但 V1 归属未知、真实 GUI 未运行；先映射权威 V1 manifest 再决定实现。 |
| AUDIT-14-CAND-003 | close | workflow 不传 `IconPath`，installer 仅在旧图标存在时选用；未证明缺图标会失败或当前 release 依赖旧路径。旧辅助路径如清理归 R4 维护 Task 并先核实调用者。 |
| AUDIT-14-CAND-004 | close | 多 shell 是架构观察，无具体运行故障证据；后续真实 UI 验证记录 shell × page 矩阵即可。 |

## 计数校验

- 候选总数 11：05（1）+ 06（2）+ 07（2）+ 09（1）+ 12（1）+ 14（4）= 11，无重复计数。
- 产品 P 级：P2 = `NM-AUD-0001` + `AUDIT-07-CAND-001`；P3 = `AUDIT-09-CAND-001` + `AUDIT-12-CAND-001`。
- 非产品：`AUDIT-14-CAND-001` 为 P3 优先级文档 finding，不并入产品 P0–P3。
- 开放 finding 7 = 3 原 triaged + 4 新增；SEG-B 两项保持独立量表。
- `AUDIT-11-INC-001` 与 `AUDIT11-REV-001` 均不计入开放 finding。
