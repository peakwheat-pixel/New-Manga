# P02M11R Codex 非作者 Review：未豁免安全门综合可行性审计

## 对象、基线与角色

- Task=`P02M11R`；被审 Owner/Author=`/root/p02_gate_feasibility`；Reviewer/Integrator=`Codex /root`，不是报告作者。
- Repo=`G:/CODEX/New Manga`；branch=`main`；base/head=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。
- Owner report=`verification/P02/codex-p02-unwaived-gate-feasibility-20261011.md`，`27825 bytes / SHA-256 15736303C3241E0C14106EFCAFB8583DF719A566D1879B7A7144B6D079A04A1F`。
- Owner Agent 没有返回可核验 final handoff，报告记录实际 model/effort=`NOT_VERIFIED / NOT_VERIFIED`。Review 不推定请求配置就是实际配置；handoff/model 缺口在 adjudication 保留。
- Review 决策=`APPROVED_AS_STATIC_FEASIBILITY_REVIEW_WITH_LIMITS`；P0/P1/P2/P3=`0/0/1/0`。这只审查静态报告，不授权 OS/API、profile、registry/WER、Build 或 AC。

## 审查覆盖与独立验证

已阅读完整 Owner report 与当前 P02M11 Task 合同，核对报告目标、唯一 registry waiver、禁止项、逐项 blocker 表、N1–N6 来源、`SUPPORTED_PATH` 与准入的区别、四个依赖推论、风险决策边界、数据 pin 表、命令/错误披露和指定 Review handoff。

独立重算 Owner report 表内 16 个项目文件 pin：12 个当前 SHA/bytes 与表一致；4 个治理文件在 report 生成之后发生了可识别的 Codex 状态更新：`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`、`doc/STATUS.md`、`doc/tasks/P02.md`。没有缺失文件。更新内容属于后续 P02PRE-R0S1/R0S2 的 current-status、分类与恢复指针，不修改 M7/M8/M9/M10 技术合同或 owner waiver。历史未提交版本没有另行快照，因此报告生成时的这 4 个旧文本不能从当前工作区逐字复原；此项作为 P2 限制，不用当前文本冒充旧 pin 对象。12 个稳定技术证据与 review/adjudication pins 均匹配。

已通过 Microsoft Learn 官方页面复核报告的 N1–N6 范围：

- N1 `SetErrorMode`：页面说明 `SEM_NOGPFAULTERRORBOX` 使系统不调用 WER，并说明子进程继承 process error mode；不覆盖启动前或 launcher 自身阶段。
- N2 `Process Creation Flags`：`CREATE_DEFAULT_ERROR_MODE` 让子进程采用默认模式而非继承；报告没有把继承写成不可覆盖保证。
- N3 `SetThreadErrorMode`：页面写的是不显示 WER dialog，且作用于 calling thread；不等同 N1 的 process-wide “system does not invoke WER”。
- N4 `WerAddExcludedApplication`：页面明确 `bAllUsers` 选择 HKLM 或 HKCU hive，并说明需要权限更新 registry list；报告正确将它排除在当前零 registry write 范围外。
- N5 `WerSetFlags`：设置 current-process fault reporting settings；列出的 flags 包括 queue/upload、heap、thread suspension 与 UI 相关内容，不提供全系统无写或 destination closure。
- N6 `Collecting User-Mode Dumps`：LocalDumps 在 HKLM 下配置；可设 per-application override；页面明确 LocalDumps 独立于其他 WER infrastructure。报告因此拒绝把 process error mode 或 UI 变化直接等同于完整 LocalDumps/T0 闭包。

读取的一手来源：

- [SetErrorMode](https://learn.microsoft.com/en-us/windows/win32/api/errhandlingapi/nf-errhandlingapi-seterrormode)
- [Process Creation Flags](https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags)
- [SetThreadErrorMode](https://learn.microsoft.com/en-us/windows/win32/api/errhandlingapi/nf-errhandlingapi-setthreaderrormode)
- [WerAddExcludedApplication](https://learn.microsoft.com/en-us/windows/win32/api/werapi/nf-werapi-weraddexcludedapplication)
- [WerSetFlags](https://learn.microsoft.com/en-us/windows/win32/api/werapi/nf-werapi-wersetflags)
- [Collecting User-Mode Dumps](https://learn.microsoft.com/en-us/windows/win32/wer/collecting-user-mode-dumps)

## Finding

| ID | 级别 | 事实与影响 | 处置 |
|---|---:|---|---|
| M11R-01 | P2 | Owner report 的 16 项来源 pin 中，4 个 mutable governance/Task 文档当前值与旧 pin 不同，因为之后新增了 R0S1/R0S2 current-status updates。旧文本未单独快照，因此不能逐字重建报告的原工作区视图。核心判断依赖的 12 个 M7–M10/研究/Review/adjudication 输入逐字 bytes/SHA 仍匹配；风险 waiver 原值和执行 Gate 当前内容亦一致。 | `ACCEPT_WITH_LIMIT`。将报告作为其当时静态输入集上的 feasibility finding；本 Review 不把四个新状态块视为历史证据。若报告作为当前任务依据，需以 current STATUS/Plan 与本 Review 的 drift 表一同阅读。 |

## 结论与未覆盖项

报告谨慎区分 Microsoft 明文合同、未说明部分与准入推论；没有将局部 `SUPPORTED_PATH`、一般 view 规则、旧候选字符串、用户 registry waiver 或 static review 升级为实机证据/执行授权。核心结论“当前已审材料没有建立满足全部未豁免条件的受支持完整执行链，保持 BLOCKED”受限于其明示的来源范围，表述不过度声称 Windows 永远不存在其他路线。

没有运行 Windows/API/registry/WER/token/profile/path/environment/ACL probe、preflight、Create/Delete、Sandbox、build/Cargo、AC1–AC7；没有修改 Owner report 或其它作者文件。没有运行测试，因该 Task 为静态合同可行性 Review 且禁止目标机运行。Review 未覆盖 Owner 实际模型身份或未交付的聊天 handoff；两者保持 `NOT_VERIFIED`。

本 Review 不代表 private registry technical condition 满足，不解除 Hard Build Barrier，不产生 Gate PASS。建议 Codex 独立 adjudicate M11R-01，并把 P02M11 作为受限静态 feasibility report 关闭；若要继续任何新 runner/API，需先满足独立的精确执行范围与副作用证据。
