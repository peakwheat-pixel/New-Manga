# Codex Dispatch Adjudication — P02PRE-R1F / R1F-R7 cohort #8 (fixreview7)

更新时间=`2026-10-11`；Repo=`G:/CODEX/New Manga`；branch=`main`；基线 HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；Task=`P02PRE-R1F`。

## 结果

`NOT_DISPATCHED / NOT_REVIEWED`。本轮没有 DeepSeek Harness session、没有 DSH CLI exit、没有 Review verdict。不得把本次启动错误解释成 Review finding、测试失败或审核通过。

## 证据与根因

- Codex 已按 manifest 创建 prompt=`6332 bytes / 0C89498657B242D4A3F63EB21574D5BA582EB1BD382A751564635986412E1306`。
- 外层 Python `subprocess.run(['dsh','headless',...], cwd='G:/CODEX/New Manga', ...)` 在创建子进程前返回 `FileNotFoundError: [WinError 2]`；因此 DSH 未启动，也没有 DSH CLI exit code。Codex 随后以 `CreateNew` 在登记的 `.exit` 路径写入清晰的派发状态标记 `NOT_STARTED: WinError 2 before process creation\r\n`（49 bytes / `5F9C0A8B9509DDAF4910151DB3883AE591A33445149CAAB59E1CB7B93F0FD94F`）；它不是命令 exit 或 Review 结果。
- wrapper 以独占创建方式落下的 cohort #8 stdout 和 stderr 两个目标均为 `0 bytes / E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`。两文件仅证明启动器在进程创建前创建了空目标，不是 DSH 输出；原始 exit 目标不存在，以上工件均保留，不覆盖、不删除、不填造退出码。
- 根因为 Python 子进程环境 PATH 未解析本机 npm shim。随后在 PowerShell 7 中只读检查到 `dsh.ps1`、`dsh.cmd`、`dsh` shim，且 `dsh --version` 返回 `0.2.0-rc.2`。因此 DSH CLI 可从 PowerShell 调用；下一轮将通过 PowerShell shim 执行同一只读 Review，并为每个输出使用全新 `CreateNew` 精确路径。

## Codex 处置与边界

cohort #8 的 Review 不完成，Task acceptance criterion 保持未勾选。prompt、空 stdout/stderr 和本 adjudication 均作为本次未启动证据冻结；已存在的 #8 exit target 不可复用或覆盖。Codex 先在 Task、唯一 DAG、STATUS、manifest 与 checkpoint 登记 cohort #9/fixreview8 五个新精确路径，再派发全新 DeepSeek Harness session。Reviewer 只读、不写仓库；Codex 为 Author/Integrator/Adjudicator。

此次启动失败没有执行 getter、脚本、Git、host API、profile、registry、ACL、capture、Build/Cargo 或 AC1–AC7。

Gate 原值保持：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；原文=`technical condition unmet; user explicitly accepted residual risk`。Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。
