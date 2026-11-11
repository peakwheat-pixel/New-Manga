---
task_id: GOV-REFINCIDENT-1
adjudicator: ZCode 独立只读 Integrator
session_id: sess_84bc17dc-2b59-4dac-b4ba-46768d80fd97
release_turn_id: turn_4a718b6b-dd49-423d-a6ac-72ae60adc9c2
byte_preservation_turn_id: turn_3d252485-c86f-4463-96d9-4bb4f1f6c991
base_commit: fa5e58e3fdbd2b53453e55104a7b002d4e57d518
decision: RELEASE_GOVERNANCE_INVESTIGATION_WITH_R2
---

# ZCode 释放裁决：Git 引用事故只读调查

2026-11-11，ZCode 独立 plan 会话决定先释放 `GOV-REFINCIDENT-1`，不暂停正常文档证据提交；R-001 为 open P2，basis enforcement 暂不释放。两轮 CLI 均 EXIT 0；本文件由 Codex 根据会话回复整理。Task 为 governance v3，Owner codex，base 为上述 main HEAD；依赖 `GOV-CHECKER-NOTASK-1` 仅表示治理时序与证据目录挂靠，不表示因果关系。生命周期按协作协议使用 `ready → in_progress → in_review → done`，不使用非枚举的 `released`。

## 范围与禁区

仅允许 `doc/tasks/GOV-REFINCIDENT-1.md`、本 Task 的 `doc/reviews/GOV-REFINCIDENT-1-*.md`、`doc/handoffs/GOV-REFINCIDENT-1-*.md`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、由工具生成的 `doc/TASK_LEDGER.md` 和 `verification/GOV-REFINCIDENT-1/**`。仓外新取证输出仅允许写 `G:/CODEX/New Manga.workspace/GOV-CHECKER-NOTASK-1/git-ref-incident-20261111-1824/investigation/`；既有事故文件和副本不得改动、移动或清理。

允许只读复算事故目录既有文件、枚举限定的 Git 环境和 hook 名、查询事发窗口 G: 卷/系统事件及相关进程名、`git count-objects -v`、枚举 dangling 对象类型；原始系统/进程输出仅留仓外，仓内写脱敏摘要与 hash。禁止提权、修改系统配置、修改 Git refs/config/hooks/objects（正常 Task 文档 commit 所需写入除外）、gc/prune/repack/清理/push、改治理工具/模板/历史 pin/契约/源码/Schema/依赖；监测工具和 basis enforcement 仅可建议，不实施。发现原件 hash 不符或活跃持续损坏源时停止并保留现场；权限不足逐项记 NOT_RUN。

## 验收

- AC1：事故原始 `incident.txt` 以原字节仓内副本保全、BLOB SHA 与原件一致；结构化时间线区分原日志声称与独立复核；复算全部既有文件及重点副本，前后两次文件集合及 SHA 一致，无法读取项如实记 NOT_RUN。
- AC2：限定 Git 环境、hook、系统事件、G: USN 与相关进程、dangling 分类逐项执行或记 NOT_RUN、命令/时点/EXIT；NUL 字节模式与 Git loose-ref 写入机制仅作为假设输入。
- AC3：每条假设记录支持/反对证据、可复核性及置信度；允许 `root_cause_unknown_with_evidence`。复发监测建议与已演练的应急路径均标明未实施及恢复前置。
- AC4：Task/STATUS/Plan/Ledger 一致，default、本卡 TaskPath、18 pins、API 四项实际 EXIT 0 并留证；独立上下文 Review 与不同独立 ZCode 终裁；关闭后空窗 default 再实测。R-001 仍 open P2。

## R2：原字节保全与换行

原件为 5702 bytes、8 对 CRLF 和 22 个独立 LF，SHA-256 `72456c6d002a6799e483221c7c1b9df69723a64faa18c9868e355cae86f53970`。默认 clean 过滤会改 BLOB。主选先在隔离仓库验证：一次性 `git -c core.autocrlf=false add`、BLOB 原字节 SHA 一致、默认 status clean、默认 autocrlf 重 add 后 BLOB ID 不变；fresh clone BLOB 不变，工作区字节情况实测登记。任一阻断判据失败，则改为 ZIP 单文件容器保全，解包 SHA 必须等于原件并如实修订 AC1。

不得修改 `.gitattributes` 或 Git 配置；不得对原字节副本执行 renormalize、普通 `git add`、checkout/restore/clean/stash pop 覆盖。仓内证据先提交再按包含该文件的 commit 与 BLOB SHA pin；工作区/fresh-checkout 漂移若发生须记 limitation。

## 限制与后续

ZCode 可直接读取已恢复的 loose ref、reflog、取证目录和日志；未独立运行 Git、门禁或重算六副本 hash，属于调查复核对象。损坏根因当前 UNKNOWN。事故目录、损坏 ref 原件、reflog 副本和隔离仓库 `PRESERVE_REFERENCED`，不清理；若无活跃损坏源，调查关闭后可再裁决 R-001 后续任务。
