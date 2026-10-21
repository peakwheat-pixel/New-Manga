---
task_id: GIT-MAINLINE-CONVERGENCE-1
author: Codex
recipient: Codex
base_commit: fdca2057eec058996f936fc16138cc87e8cdc0bc
delivery_head: c9a1bdd3061300c9c1c633eb8f2279903918e5a2
status: blocked
---

# Handoff：Git 主线收敛（目标尚未完成）

正式 CAS 接管：Codex epoch9；用户已确认原 dsh 停止写入。main 当前承接治理；不重开旧Task。

治理前后本地分支97→97，注册工作树135→135；214 common refs全部保留，0stash。19未合并支线已逐项核对提交/patch/增量归档，未执行产品代码集成。19份旧bundle verify通过；新增全refs bundle 238847964B在空bare恢复214refs全等、135HEAD可读、fsck exit0，SHA256 8128955e47f835989a718b55b3af11754752e893b7f78fe7f337eaef68c0f1a9。备份仅截至56272e40b，不含后续治理提交或未提交/ignored/应用会话。

证据版本：最初盘点 a91e659c3（历史）；修订与LF证据 c615d52b4；19条重签/盘点复审 head c9a1bdd30。DeepSeek session-1b587ef1-3c10-4e81-97b0-17e7d84c0765，R1/R2退出0；R2 approved仅限固定c9非破坏性切片。6项P2已修，N001旧指针在尾部记录提交修正。Review不批准删除/GC/prune/Task done，尾部状态登记不是新实施交付。

## 实测验证

- 19 EV/SRC：raw bytes disk==blob==SHA，19/19，无文本归一化。
- pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GIT-MAINLINE-CONVERGENCE-1.md：c9固定head PASS 3 warnings，EXIT0；日志 verification/GIT-MAINLINE-CONVERGENCE-1/validation-c9a1bdd30.txt，最终记录提交后另验。
- git diff --check：EXIT0。产品测试NOT_RUN（无产品代码变化）。
- 117个其他refs逐项记录保留；相比19分支集合另有110个去重提交，均在记录时Git备份中。

## 当前阻塞

125工作树保护命中，82有dirty/untracked，60有ignored根，77声明错误；集合重叠。旧清理禁令和旧主线显式保留未解除。未提交/ignored未逐文件备份，不对任何工作树执行删除。19未合并branch不能普通-d删除，不能以强删旁路或盲合并绕过用户约束。

完整Task保持blocked，暂停前in_review；没有done/关闭/发布/下一Owner。全部新资源按Task Manifest保留，源数据/原作者未提交内容保留；精确清册和下一裁决见 verification/GIT-MAINLINE-CONVERGENCE-1/{report,branches,worktrees,decision-request}.md。

## 下一任务建议（等待用户裁决，尚未释放）

- Task：GIT-MAINLINE-CONVERGENCE-1后续处置切片，或另建逐项保护声明/路径兼容Task。前提是明确保护与独有工作的处置边界；不把本建议当作READY。
- Owner：Codex；Reviewer：DeepSeek Harness（非本轮修订作者）。原因：Lead掌握保护/契约，独立Reviewer核对语义与数据保全。
- Recovery：G:/CODEX/New Manga，main；固定base为本Handoff delivery_head c9a1bdd30，实际尾部HEAD以git实测；不创建新worktree直到正式释放。若有代码修复，分支codex/<NEW-TASK-ID>，路径G:/CODEX/New Manga.workspace/worktrees/<NEW-TASK-ID>，均待Codex创建。
- 允许：先只读所选source、77错误与原RESIDUAL，冻结Task/Plan/STATUS和自己的verification；任何helper或历史声明改动要另列精确allowed_paths。
- 禁止：用户文件/数据库/模型/原始evidence/pin字节、全局忽略/放宽fail-closed、清理/GC/prune/强删/远端操作；不得恢复Legacy实现。
- 交付：逐项source/HEAD/归属/保护来源/引用/占用/备份恢复矩阵、原始错误与修复前后对照、固定commit、非作者Review和Handoff。删除另需独立授权窗口。
- 验证：现有声明审计/incident replay（如涉及工具）、Task治理check、必要回归；所有命令有环境/EXIT，任何PARTIAL/BLOCKED不写PASS。
- Forwardable instruction：在 G:/CODEX/New Manga 的 main 读取 GIT-MAINLINE-CONVERGENCE-1、R2 reviewed_head=c9a1bdd3061300c9c1c633eb8f2279903918e5a2、checkpoint与decision-request，先核对实际HEAD和唯一Codex租约。确认用户对所选保护资源/独有支线的处置裁决；未获裁决则保持blocked和全部原位保护。获裁决后仅冻结一个最小后续Task，明确Owner Codex/Reviewer DeepSeek、source/HEAD/allowed_paths；代码修复使用待创建的codex任务分支和workspace工作树。交付真实before/after矩阵、必要测试、固定commit、独立Review/Handoff；任何删除需另做备份恢复与精确授权窗口，禁止强删旁路、Legacy盲合并、GC/prune或push。

## 2026-10-21 后续状态（覆盖上文历史计数与77错误的当前含义）

保护处置边界已记录boundary-adjudication.md，全部原资源保留，STATUS/r212禁令有效。工具前置GOV-PATH-HEADER-COMPAT-1独审/集成完成9cae94142；77→32 errors，原保护集合全保留+410。当前98本地分支/136工作树，新增Task资源原位保留，尚未达到只剩main。父Task继续blocked；旧盘点Review范围不扩张。下一建议为32项只读取证，完整启动条件/Owner/Reviewer/base/范围/验证/可转发指令见 [子Task Handoff](GOV-PATH-HEADER-COMPAT-1.md)，尚未释放。
