# 剩余24项：最小裁决与继续边界

2026-10-21 / Codex。当前99本地分支/137注册工作树；原19条未合并支线tip逐条与boundary-adjudication相同。没有重新扫描其当前dirty/占用，不把旧快照当删除依据。main仍为唯一开发/集成主线，尚未达到只剩main。父任务blocked，STATUS/r212禁令及原保护保持有效。

配置Task独审85a393dc4、集成9d21f8fb8（32→30）；六行格式Task独审/集成2573375dc（30→24）。这两次批准不覆盖余24项。

| 组 | 数量及具体对象 | 当前裁定 | 最小下一步/所需裁决 |
|---|---|---|---|
| 广域根 | 12错误=6条source/destination成对记录、5个唯一根；SEC-FIX-PATH-ECHO-1及WORKSPACE-CONSOLIDATION-1：workspace本身、task-envs、worktrees、review-scratch、temp | 原广域保护/阻断全部保留，不能为清零缩小到“看似相关”子目录 | 需要显式选择：保持广域整体保留，还是逐项核实后只保护已证明的具体资源。推荐整体保留；若用户选择此方向，Codex另冻结精确保全映射设计/测试/独审，不改旧记录，也不批准任何删除。不能由本汇总擅自写入例外或清理。 |
| 历史身份/枚举 | 7错误；P19 Task 3项（worktrees/P19-AC3-1及两个TEMP）；ENV-BUNDLE-1-FU1的CLEANED_BY_OWNER 1项；P19-UI-FIX-1的Same目标1项和APPDATA源2项 | 原身份UNKNOWN/用户数据保留；同一个用户源根的两条record不算两个用户源 | 需要原运行上下文或直接证据确认绝对路径/同源目标/实际状态；不能用当前TEMP/APPDATA或用户猜测替代。事实未证实继续BLOCKED。可单独冻结只读取证，不授权修改原JSON/Task。 |
| 冻结Review模板 | 2错误；codex-closeout-p19-view-r12.md中内嵌Task模板的条件枚举/说明路径 | 原Review和pin不动；它不是已冻结真实资源处置记录 | Codex可提出限定精确路径/raw SHA/具体行范围的当前解释方案，另冻工具范围、正反例及独审；必须仍读取真实声明，不能忽略整个Review/verification或重写旧Review。本汇总不批准实现。 |
| NUL快照 | 3错误；P14 owner-initiated-dsh-self-review-r1/r2（各byte286一个NUL）；P22未跟踪codex-p22-task-r4-malformed-snapshot-7ebd7d40.md（2 NUL，偏移见facts） | 原始字节/pin/未提交归属全部保留，不能作为独立Review或当普通文本通过 | 可另冻只读语义/精确身份研究；任何新的当前解释机制须明确来源、保留原bytes和负例测试、独立Review。禁止删NUL/转码/重签/提交P22原文件。 |

逐项原始错误code/file/locator/message、原R编号/实际定位、9源raw SHA/status/NUL偏移及19条支线tip见decision-facts.json。九源SHA均与已独审32矩阵一致，不更改其原始record；locator为解析器表内相对定位，actual_locator是原取证的真实位置。17不等价/2等价是父盘点阶段分类，本汇总只核19tip不重算patch或价值。

## 集中裁决范围

1. 可先仅裁定“5个广域根继续整体保留，允许Codex另冻保全解释方案”。这不会解除保护或清理禁令，不能直接把12项标PASS。选择收窄则必须先拿出逐资源/引用证据和影响，不能整批授权。
2. 对7历史身份错误，需要真实来源证据；没有证据时保留BLOCKED，不要求用户凭记忆编造路径。其余5个冻结/损坏证据项只有只读研究可继续，未获实现批准。
3. Git收敛的独立裁决：原19支线全部保持现状；P14/P22仅是新架构只读评估候选，其余历史/Legacy/等价分支路线见父boundary-adjudication。对需要用户作产品取舍的独有变更，必须先提交具体差异/测试评估；不能现在批量批准merge或丢弃。用户原“不得强删/不得GC/prune”和r212禁令不变；未合并引用不能用update-ref等旁路规避。现阶段不请求删除窗口。

原all-refs-56272e40b.bundle仅覆盖旧Git基线，恢复位置G:/CODEX/New Manga.workspace/archive/git-backups/GIT-MAINLINE-CONVERGENCE-1/；不覆盖后续治理、dirty/untracked/ignored/会话等，不是当前完整恢复备份。所有本轮证据/审查/派生输出在workspace/agent-output/codex各Task目录保留。没有对任何真实资源执行删除/迁移/归档/GC/prune/push。

## 推荐下一步与门槛

推荐由用户先裁定上述广域根“继续整体保留”方向；Codex据此另冻精确保全解释设计，DeepSeek独审。7项历史身份先提供或恢复原运行证据；缺失项保留。模板/NUL或P14/P22只读研究可在Codex另冻范围后推进，但不是删除前置条件的替代品。本Task不释放这些实现、不给历史资产重新背书。

验证只读全审计exit2/24、九源SHA与状态前后相等、19tip一致、99/137、真实EV注册/治理check。产品/构建、工具109回归、占用释放及恢复演练NOT_RUN；没有代码变更。需要真实授权和保护解除才能继续实际资源退出，不能为“唯一main”更改统计口径。
