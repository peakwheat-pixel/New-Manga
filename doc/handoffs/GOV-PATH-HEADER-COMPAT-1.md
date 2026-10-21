---
task_id: GOV-PATH-HEADER-COMPAT-1
author: Codex
recipient: Codex
base_commit: 93c4eb2ca907a53af500634637582ed7ebeba0eb
delivery_head: 78fc0cba26d0f52f3bb86014076039c0212dd4f0
status: integrated
---

# Handoff：固定模板路径表头兼容

## 交付结果

仅两处归一化识别完整字面量 `path（仓库相对路径或绝对路径）`，重复列同步拒绝；无依赖/Schema/API变更。实现9f59537f9，独审固定78fc0cba2，主线merge 9cae94142a51ee104dea19714568d3fe2b89dad0。AC1/2由5正反例支持；AC3同main数据快照77→32 errors，1280旧保护根全保留+410；AC4为29声明+80安全回归、双事故回放各15拒绝/0删除/0违规及独审；AC5主线复验与保留资源核销。

DSH R1 session-9829cfea-8585-41aa-b985-11d20c90a7e2因linked工作树shell ACL失败未批准。R2 session-90adda56-6155-4d06-95df-667579988499 EXIT0 approved，独审实际核验head/diff/祖先关系；测试与12pin原始字节核对为Codex实测，未写成Reviewer重跑。Review原文在verification/GOV-PATH-HEADER-COMPAT-1/deepseek-review{,-r2}.md。

R2记录项：delivery_head已更正；git log证明EV12属性文件实际最后变更9ea78f1aa，1a958d770仅更新Task，因此原pin来源正确、保持不变。前置模拟1277→1687；增加本Task三个资源根后实际对照1280→1690，两者均+410。集成后另有新增证据根，当前只读审计1702根，不与旧快照绝对值混算。

## 验证证据

Windows / PowerShell / Python -B；原始命令与exit见postintegration-validation.json。主线5测试exit0；git diff --check 93c4eb2ca..HEAD exit0；clean_workspace.py --repo "G:/CODEX/New Manga" --workspace-root "G:/CODEX/New Manga.workspace" --audit-declarations --out <本Task agent-output>/postintegration 返回exit2，32项错误按设计fail-closed，非清理PASS。postintegration-declaration-audit.json记录32错误，旧致命类别仍保留。原始5+29+80日志及双事故回放在本Task证据目录；0skip。资源保留记录resource-closeout.json；全部原有及新增分支/工作树保留，当前98 heads/136 worktrees。无真实资源删除/迁移/归档、无产品代码集成、无远端操作。

## 下一任务建议（未释放）

- Task：父GIT-MAINLINE-CONVERGENCE-1的32项残余声明只读取证切片；创建新Task前先冻结精确source范围。依赖本修复已集成，禁止重开旧Task。
- Agent：Owner Codex，Reviewer DeepSeek Harness；Lead裁定共享保护边界，独立Reviewer复核证据。
- Recovery：G:/CODEX/New Manga，main，固定base/head=9cae94142a51ee104dea19714568d3fe2b89dad0；后续治理文档提交推进属预期，启动须核对实际HEAD/租约。新worktree待Codex创建，本建议不创建。
- Scope：先只读本Task postintegration-declaration-audit.json列出的32 source/locator，读取精确引用；允许路径仅待冻结的新Task、自身verification/Handoff以及STATUS/Plan/台账元数据。历史source/evidence/pin、用户文件、工具源码均禁止改写；不扩大接口/Schema/依赖。涉及历史声明修订需另行精确范围/来源Owner裁定。
- Deliverables：逐项错误/来源/归属/原始引用/保护影响/最小修复建议/需裁决理由矩阵；不提供可执行删除清单。
- Verification：只读前后HEAD/status核对；pwsh -NoProfile -File tools/governance/check.ps1；任何未实测项标NOT_RUN/BLOCKED。须独审和Codex裁定才能关闭切片，不自动解除禁令。
- Forwardable instruction：Codex，请在G:/CODEX/New Manga的main核对实际HEAD与epoch9租约，以9cae94142a51ee104dea19714568d3fe2b89dad0为恢复基点，读取父GIT-MAINLINE-CONVERGENCE-1、边界裁定、此Handoff及postintegration-declaration-audit.json。先建立并冻结一个32项残余声明只读取证Task，Owner Codex/Reviewer DeepSeek；新worktree待Codex创建。只读列出的source/locator和直接引用，逐项输出错误、归属、保护影响、最小建议与用户裁决需求。只修改冻结的新Task/自身verification/Handoff和授权治理元数据；禁止改历史source/pin/用户文件/工具源码，禁止apply/删除/迁移/GC/prune/push/Legacy任务。保留原始错误与HEAD/status前后证据，运行治理check，固定commit独审/Handoff；建议不是释放，先在Plan/STATUS冻结，不自动启动后续实施。

## 风险与遗留

父目标继续blocked，尚未达到只剩main。STATUS/r212禁令、所有证据pin和未提交/ignored内容继续保护。32错误未消解，不适用清理。旧Git bundle截至56272e40b，不涵盖本轮或未提交/ignored/会话。产品测试NOT_RUN（仅治理解析器变更，已跑对应回归）。资源保留不等于已解除占用或可删除。
