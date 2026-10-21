---
task_id: GOV-DECLARATION-RESIDUAL-32-AUDIT-1
author: Codex
recipient: Codex
base_commit: c0a9cb7962669cb4e987af51260f68850f4fe3b0
delivery_head: e2b8d19ed47a5ecde53d53f7fa17be6a2e10c29f
status: in_review
---

# Handoff：32项声明只读取证

32项对应17来源，详见verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/report.md、matrix.json/md、source-facts.json、direct-reference-facts.json。六组错误计数6/12/7/2/2/3，12宽泛根错误仅6声明/5根；未把错误数当资源数。原code/file/locator/message保留，R30/31实际source_path定位另列；作者不明如实UNKNOWN，未提交原件未提交入Git。

验证：17项raw SHA与逐源Git状态不变；只读clean_workspace.py --audit-declarations --out G:/CODEX/New Manga.workspace/agent-output/codex/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/corrected-observation-audit 返回exit2，原32错误多重集合完全相等；98heads/136worktrees；详情preservation-validation.json。初始曾36错误（一份保留失败输出）源于本Task结构化引用4原resource，已只改观察记录为原文字符串；失败输出留agent-output。无source/guard代码变更、无用户数据访问或资源处置；产品/工具回归NOT_RUN。

DeepSeek固定commit独立Review待完成；不得把Owner校验写成Reviewer实测。父Task blocked，STATUS/r212保护/清理禁令有效。原工作树和本Task输出全部保留。基线c0a9cb796，证据交付22bd5e07af5710af2359827a45fdf658186f578d，main文档提交，无新branch/worktree。

## 下一任务建议（尚未释放）

Task：拟议GOV-NDJSON-NONDECL-IDENTITY-1，核验2个P02日志非声明身份；依赖本Task获独审、Codex关闭后，再冻结新Task，不重开旧Task。Owner Codex / Reviewer DeepSeek Harness，理由为共享保护解析契约需Lead负责。

Recovery：G:/CODEX/New Manga，main；固定base/head=22bd5e07af5710af2359827a45fdf658186f578d，后续治理元数据提交需启动实测；不新建工作树，本建议不释放实施。允许范围在新Task冻结前仅只读本报告的R23/R24和两日志固定hash/格式诊断、既有精确path+SHA例外机制；拟写路径仅新Task/自身verification/Handoff和治理元数据。原source/JSON/pin、历史Task、用户文件、Legacy、guard/例外表均禁止改写，若要工具写入另冻allowed_paths与语义。

交付：两项完整NDJSON身份/资源键核验、精确例外适用性及负例/字节漂移拒绝方案、是否需新写范围的裁定；不得提供删除清单。验证：逐source raw SHA/status前后、现行声明审计exit2/原错误身份核对、pwsh -NoProfile -File tools/governance/check.ps1；NOT_RUN/BLOCKED不得写PASS，固定head独审与Handoff后才可关闭。

可直接转发：Codex，请在G:/CODEX/New Manga的main核对实际HEAD/epoch9，以22bd5e07af5710af2359827a45fdf658186f578d为恢复基点读取本Handoff/32项矩阵R23/R24。先冻结拟议GOV-NDJSON-NONDECL-IDENTITY-1（依赖本Task独审关闭，Owner Codex/Reviewer DeepSeek），只读两项日志raw hash、完整NDJSON诊断和精确path+SHA非声明例外机制，提交身份/引用/保护影响和负例/漂移拒绝方案。只写新Task/自身verification/Handoff和冻结治理元数据；不改原始JSON/历史Task/pin/用户文件/guard/例外表，不运行旧collector，不清理/迁移/GC/prune/push，不恢复Legacy。记录真实命令/exit、逐源前后指纹、治理check、固定head独审；建议不等于释放，任何代码/例外表修改另冻精确范围。

风险：原32错误未消解，未证明资源可删除或只剩main；全部保护不变。无需本轮额外产品测试。

R1要求已按文档范围修正：R24 tracked与R23 untracked分清；6/64为总值数、类型计数1/4/1与1/62/1；R30/31同源不同destination；新增完整错误身份与稳定hash，checkpoint将登记SOURCE_PIN。原始source17项不变，旧Review原文保留。

## 最终独审与Codex核销

R2在927e06f8b25563afbc7acbcc25d19fe775d1ded6 approved；DSH session-15d4c9be-21a7-4f1c-afa3-e9cd29af81a1，R1/R2 EXIT0，原文deepseek-review-r1/r2.md保存。P1/P2五项修正已通过复审，10pins独立raw bytes复算PASS。独审未复跑声明审计，Codex收口再跑exit2且原32完整身份多重集合相等；17原字节/status不变。

R2非阻塞格式项为Review原文4处Markdown双空格；仅对本Task两份Review设置-whitespace，保留原文，diff-check exit0，不影响其它文档/源码。无新branch/worktree、0删除/迁移/归档；agent-output原位PRESERVE_REFERENCED，其余派生类NOT_APPLICABLE，详resource-closeout.json/integration-validation.json。文档研究已串行落main，不需要产品分支merge；集成点为R2 reviewed_head，尾部提交仅登记批准/核销。

父收敛仍blocked，当前98heads/136worktrees；全部保护和32errors继续有效。下一Task建议仍为拟议GOV-NDJSON-NONDECL-IDENTITY-1，未释放，不自动开始工具/例外表修改。
