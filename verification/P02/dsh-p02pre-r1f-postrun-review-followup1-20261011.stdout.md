---
task_id: P02PRE-R1F-POSTRUN-20261011
reviewer: DeepSeek Harness
author: Codex /root
base_commit: cddff58469b56e181019a8ddfeade80684bc7eb9
reviewed_head: cddff58469b56e181019a8ddfeade80684bc7eb9
decision: CHANGES_REQUESTED
---

# Review：P02PRE-R1F post-run evidence（非作者只读）

## 范围与依据

审查对象：R1F 唯一一次冻结 capture 及其全部 pin。范围=`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/00_INDEX.md`、`doc/09_COLLABORATION.md`、`doc/tasks/P02PRE-R1F.md`、`p02pre-r1f-manifest-20261011.md`、`p02pre-r1f-capture.ps1`（ps1）、R8 parser JSON、rolling checkpoint、evidence JSON、capture stdout/stderr/exit；外加 `doc/templates/REVIEW.md` 与 09_COLLABORATION §5.1/§6。按原请求给定 pins 使用；本次无执行权限，**未复算任何 bytes/SHA-256**，pin 一致性仅由文档间交叉核对（checkpoint:38–41 与请求 pins 逐项一致；R8 `expectedSourceSha256` = ps1 pin）。未读取 `.tmp.driveupload` 内容/元数据。

## Architecture 结论

执行契约被遵守：冻结 executor=`…\v1.0\powershell.exe` 5.1（编排父 shell 才为 PS 7.6.6）；失败关闭（fail-closed）设计生效——首阻断即停止、仍以唯一 `CreateNew` 写出 JSON、随后 `ps1:912` throw，未产生任何伪 PASS（stdout 0B、exit=1）。一次性/不可变契约由 `ps1:15` 的 target-exists 守卫与 `CreateNew` 保护，本次 JSON 为新建而非覆盖。缺陷在候选的**依赖前置条件缺失**：首个哈希依赖 `Get-FileHash` 无任何 engine 能力预检，单个命令不可解析即耗尽整次 one-shot，得到零新增 inventory；`stopReason` 粒度不足以区分 R1 的策略停止与本轮命令解析失败；证据不绑定实际 argv（`command` 为 `ps1:24` 硬编码）与被执行源码字节（脚本不自哈希，inventory 未到达）；状态文档未随运行更新。

## 验证

| 检查 | 证据 | 状态 |
|---|---|---|
| 是真实 capture 而非 parse-only | evidence JSON 有 t0/process/identity/whoami；exit=1；R8 另件 `captureScriptInvoked=false` | PASS |
| 实际运行器 | `process.executablePath=…WindowsPowerShell\v1.0\powershell.exe`、`5.1.26100.9549`、`ConsoleHost` | PASS（自报；限制见 R1F-POST-04） |
| 首个阻断条件 | `state=GIT_INDEX_PREHASH_INVALID`、`errorOperation=Get-FileRecord(.git/index)`、`firstBlockingPath=G:\CODEX\New Manga\.git\index`、`errorType=System.Management.Automation.CommandNotFoundException`、error=「无法将“Get-FileHash”项识别为…」；对应 `ps1:254–261/333–334` | PASS |
| 失败关闭一致 | stdout=0B；`exit`=`1`；stderr 676B 与 `ps1:912` throw 文本逐一对应 | PASS |
| 下游是否运行 | JSON 中 `commands={}`、`fileInventory=[]`、`gitMetadata=[]`、`environment={}`、`paths={}`、`wer={}`、`protectedHashes={}`，无 scratch 键、无 summary/homeEnvironmentCheck；仅 whoami.exe（exit 0）与 Get-Item/.NET 身份查询执行 | PASS：Git inventory/hash、scratch、路径/ACL、TEMP/cache、WER/registry、Build/Cargo、AC 均未到达 |
| Get-FileHash 缺失根因 / PS7 不兼容 | 无 PSModulePath/LanguageMode/模块清单记录；同一子进程 Get-Item 成功，故非全量模块发现失效 | NOT_RUN（根因 UNPROVABLE）；**现有文件不能证明 PS7 不兼容**（PS7 未执行该脚本） |
| Plan/STATUS/Task 实际状态 | PLAN:13/32/73/74/101、STATUS:5、Task:36/40/115 仍写 Capture=`BLOCKED / NOT_RUN` | FAIL（陈旧） |
| pin 复算、重跑 capture | 审查禁止执行 | NOT_RUN |
| Gate/Build/AC | 未运行 | NOT_RUN |

分类结论：这是 **capture/runtime 侧失败**（脚本在 main 仓库 baseline 的 `.git/index` pre-hash 处因命令不可解析而 fail-closed），**不是 AC 测试失败**——AC1–AC7、Build/Cargo、测试 harness 从未启动，无任何测试判定。证据亦不足以把 locus 归于脚本逻辑或环境，须记 UNPROVABLE。

## Findings

| ID | 级别 | 文件/行 | 影响 | 证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R1F-POST-01 | P2 | PLAN:13/32/73/74/101、STATUS:5、Task:36/40/115、checkpoint:19/253 | 仓库无任何文档记录 one-shot 已消耗；后继 agent 可能误以为 capture 仍未运行并再次释放 | evidence JSON 存在且 t0=2026-10-11T14:17:31Z、exit=1；上述文档仍写 NOT_RUN/null | Codex post-run adjudication + 状态刷新为 `ONE_SHOT_CONSUMED / GIT_INDEX_PREHASH_INVALID` | open |
| R1F-POST-02 | P2 | ps1:254–261/333–334、manifest:59/65 | 候选缺少 engine 能力预检，一次不可解析命令耗尽 one-shot，零新增 inventory；pre-run 约定的后捕获 inventory SHA 比对不可达成 | `firstBlockingPath=.git\index`、`errorType=CommandNotFoundException`、`fileInventory=[]` | successor Task 增加能力预检（记录 `$PSVersionTable`/PSModulePath/可用模块/LanguageMode/`Get-Command Get-FileHash`） | open |
| R1F-POST-03 | P3 | evidence JSON `classifications`/`errors` | 9 项分类除 hostIdentity 外均为初始化默认值，JSON 无 `captureStatus`、无 reached/not-reached 标记、`errors=[]`，需读者自行重建可达性 | JSON 与 ps1:19–46 初始化逐项相同；仅 hostIdentity=PASS_WITH_EVIDENCE | successor 增加显式未到达标记与更细 stop 子状态 | open |
| R1F-POST-04 | P3 | ps1:24/596–602、manifest:59 | 运行 attestation 仅自报：argv 为硬编码字符串，源码字节未绑定（R8 只证明同 pin 可解析） | stdout 0B；stderr 仅源码行摘录；无 wrapper argv 旁证 | successor 在 evidence 内记录源码 SHA/argv；本次 adjudication 声明该限制 | open |

## 结论与剩余风险

结论：证据内部一致、停止原因记录准确、下游未到达判定正确、one-shot 不可变要求成立；但状态文档陈旧且缺 post-run 记录（P2），候选缺能力预检（P2），故 **CHANGES_REQUESTED**（0/0/2/2）。非 BLOCKED_BY_MISSING_EVIDENCE：决定性事实均可由 pins 复现。**本 Review 不构成任何 Gate/AC 通过。**

保持原值：private_registry_absence=`UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。

剩余风险：①manifest:59/65 的后捕获 governance-path 确认对本次运行记为 UNPROVABLE/FAILED，checkpoint 最终 hash 无法由本次 inventory 提供；②误重跑风险虽被 `ps1:15` fail-closed 拦住，仍可能被误记为授权运行；③无 OS 级监视，写入闭包仍 `UNPROVABLE_NOT_MONITORED_IN_R1F`；④本次未复算 pins。

最小安全后继动作（不实施）：Codex 先出 `verification/P02/p02pre-r1f-postrun-adjudication-20261011.md`（one-shot 已消耗、exit=1、首阻断、根因=UNPROVABLE、下游未到达），刷新 PLAN/STATUS/Task/checkpoint 状态；**禁止重跑 ps1 或覆写 evidence JSON/stdout/stderr/exit**；随后冻结 successor Task（新脚本 + 新 evidence/输出路径 + 能力预检 + 源码/argv 自绑定），经非作者 Review 与 Codex pre-run adjudication 后才可再释放一次 capture。

§5.1 建议（建议≠释放）：Task=「P02PRE-R1F-successor：能力预检 + 证据自绑定」；Owner=Codex，Reviewer=DeepSeek Harness（另一 session）；Recovery point=`G:/CODEX/New Manga`、branch=`main`、base=head=`cddff58469b56e181019a8ddfeade80684bc7eb9`；Scope 限 R1F successor 的 `verification/P02/**` 新路径与 `ps1` 新候选，禁止改动 R1F 既有 artifacts；Verification 要求新 pins 复算 + 单次 capture 五态分类；Gate/barrier 全部保持现状。
