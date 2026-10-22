# P02PRE-R0S5 Codex integration verification

## 范围与结论

本文件核验 R0S5 静态文档闭环、Review 记录、Live Git 与风险/Gate 状态。没有运行 P02PRE host/OS/Registry/WER/profile/token/ACL/path/environment/hash query；没有执行产品 build、Cargo 或 AC1–AC7。静态 Review/文档集成完成，但 R0S5 overall=`blocked / NOT_SAFE_FOR_R0`，因为当前 runner/getter 仍无可审查的无副作用证据。

## Independent Review 与裁决证据

| 阶段 | Agent / 命令 | 结果 | 限制 |
|---|---|---|---|
| Round 1 | DeepSeek Harness；`dsh headless` | exit `0`；session=`session-fe73b6c6-4296-4259-bf90-b5363bd15a7a`；`changes_requested`，P0/P1/P2/P3=`0/0/2/4` | 静态文档审查；不核验 hashes、Live Git 或 host；报告 hash=`A059009D3783F88F9D77D27392B0577D5C516A7452E61AECFB5BAA9B212042DC`。 |
| Round 2 | DeepSeek Harness；`dsh headless` | exit `0`；session=`session-9295f595-2e84-4162-bf28-780dc7ce4604`；`changes_requested`，`0/0/1/4` | 静态文档审查；报告 hash=`88AF93CA3B1D7D11A7B45C059201C06DE6DB1BA9D4250FCB9FC26DC36D0508A5`。 |
| Round 3 | DeepSeek Harness；`dsh headless` | exit `0`；session=`session-f78b23bc-9619-47b8-83b8-84507d9b74ef`；`approved`，`0/0/0/1`；报告=`verification/P02/dsh-p02pre-r0s5-review-r3-20261011.md`，`10056 bytes / SHA-256 02AB67DD56CD3D5E8F33364909B6D769A5BA8EB72B67D51FEBC3DF4E36F5FD98` | 只审静态文本；Reviewer 未验证 hashes/Git/host，也未独立证明本轮零查询。唯一非阻断 P3 已由 Codex 做措辞修正，未改变对象、路径或授权范围。 |

R3 stdout=`4967 bytes / SHA-256 39B5DD9275522A94AFE7647A7689CB634DFDCD6476D36A14BE9C6F442244FB60`；R3 prompt=`2801 bytes / SHA-256 C2657874D44DC1980E8B065E1DD97036D8E9EEFFF81DC6640E624381D860156A`。实际 mount 命令为 `py -3 C:/Users/49745/.agents/skills/dsh-dispatch/scripts/mount_session.py --latest`；命令输出确认 R3 session 已挂载到 `New Manga` workspace，但 numeric exit 没有单独保存。

Round 3 的唯一 P3 是 Task L55 把 12 个只读输入根放进 “scratch” 句式。Codex 已改成将“12 个只读输入根、13 个 scratch 输出 leaf、3 个以 r6 scratch root 为根的 canary leaf”并列描述。该措辞修改不改变候选集合、绝对路径、读取权限或执行授权；无需重开对象集 Review。逐项 findings disposition 见 `codex-p02pre-r0s5-adjudication-20261011.md`。

## Live Git 核验

执行前后只读采集得到：

- root=`G:/CODEX/New Manga`；branch=`main`；HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`；common-dir=`.git`。
- 使用与 R0S4 checkpoint 相同参数：`git --no-optional-locks -c core.fsmonitor=false -c core.quotepath=false status --porcelain=v1 -z --untracked-files=all --no-renames --ignore-submodules=none`。通过 .NET `Process` 读取原始 stdout bytes；exit=`0`，588 NUL records，37250 bytes，stderr empty，SHA-256=`0E20722F5A97717F05356548AF29662A34403221F2A213421E40FE722708A98E`。
- `.git/index` 在 status 前后 SHA-256 均=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`；未观察到 index bytes 变化。
- `git --no-optional-locks -c core.fsmonitor=false worktree list --porcelain` 计数=`361`；未 prune worktree。
- 与 R0S4 同参数 status 从 569 records 增至 588 records（+19）；这是整体 status 计数差，不将所有变化归因于本 Task。初始及最终 Git 记录均显示工作区包含大量已有修改/未跟踪文件。本轮不 reset、clean、stash、覆盖、删除或 commit；无法确认的既有文件原作者归属不推断。

## 输出文件核验

Codex 重新计算以下最终工作区文件的 bytes/SHA-256。R3 Reviewer 自己明确不验证这些 pins；这些 pins 绑定工作区文本，不是 Git commit。

| 文件 | bytes | SHA-256 |
|---|---:|---|
| `doc/tasks/P02PRE-R0S5.md` | 9183 | `2F2D8D3FF6159FEA14237BAA7D52C820E919F40948D29B9A0B3A31F91F2FCB00` |
| `verification/P02/p02-readonly-preflight-r0s5-manifest-20261011.md` | 10471 | `043F9D58FB77D8A79DBD2C67C490735040243B5A93149BB6A0B1169685C63D9B` |
| `verification/P02/codex-p02pre-r0s5-delivery-20261011.md` | 6889 | `3C7CF0232454EF531740A15C614CD763F44F844599FF8F5B5EF48B67E0D51A0D` |
| `verification/P02/dsh-p02pre-r0s5-review-20261011.md` | 17644 | `A059009D3783F88F9D77D27392B0577D5C516A7452E61AECFB5BAA9B212042DC` |
| `verification/P02/dsh-p02pre-r0s5-review-r2-20261011.md` | 14531 | `88AF93CA3B1D7D11A7B45C059201C06DE6DB1BA9D4250FCB9FC26DC36D0508A5` |
| `verification/P02/dsh-p02pre-r0s5-review-r3-20261011.md` | 10056 | `02AB67DD56CD3D5E8F33364909B6D769A5BA8EB72B67D51FEBC3DF4E36F5FD98` |
| `verification/P02/dsh-p02pre-r0s5-review-r3-20261011.prompt.md` | 2801 | `C2657874D44DC1980E8B065E1DD97036D8E9EEFFF81DC6640E624381D860156A` |
| `verification/P02/dsh-p02pre-r0s5-review-r3-20261011.stdout.md` | 4967 | `39B5DD9275522A94AFE7647A7689CB634DFDCD6476D36A14BE9C6F442244FB60` |
| `verification/P02/codex-p02pre-r0s5-adjudication-20261011.md` | 6611 | `922811400183421700D33EF084052F6C2E2FA918A584B93909E7CB7D86BA5583` |
| `verification/P02/codex-checkpoint-p02pre-r0s5-20261011.md` | 4308 | `AF08035BC363F4DBFCB522D65D94E6DEA583A090F90F7BD75D48EE0947269DE2` |

P02PRE-R0S5 Task 的最终状态字段=`blocked`；AC1–AC7 没有因文档 Review 被判通过。

## 未运行项与 Gate

当前 `exec_command`/PowerShell executable/version、完整 argv、startup/profile/module/provider、cache/history/wrapper/temp/log、子进程/runner 边界未证明无副作用。manifest 没有任何当前 getter 清除；因此没有运行本地主机查询、注册表或 WER getter、路径/ACL/env/hash query、profile API、权限 canary 或 host capture。未运行不是 `FAILED`。

`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。P02PRE/Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。没有查询、安装、启用或启动 Windows Sandbox。

本轮只修改了授权治理范围内的 Task、delivery、adjudication、verification/checkpoint 与 Plan/STATUS/Index/P02 摘要；不涉及产品代码，无需运行代码测试。曾尝试删除 Round 1 dispatch 生成的 `verification/P02/dsh-p02pre-r0s5-review-20261011.stderr.log`，automatic approval review 拒绝该删除；文件保持原状，本轮未绕过或重试。
