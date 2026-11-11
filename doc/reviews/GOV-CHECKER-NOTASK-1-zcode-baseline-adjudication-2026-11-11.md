---
task_id: GOV-CHECKER-NOTASK-1
adjudicator: ZCode CLI 独立只读会话
session_id: sess_3018f37e-e987-4c51-a1c8-0a9935530d04
input_head: ca7f6f31b740cd09d6853e63683983c4826daf60
decision: BASELINE_SUFFICIENT_IMPLEMENTATION_AUTHORIZED_V2
---

# 基线与空窗语法裁决

2026-11-11，ZCode 独立会话核验 §4.4 前置，认为影响全集分区、12 个基线场景、目标错误断言及隔离恢复证据足够，可实施。首轮裁决的括号注释语法未排除路径；经指出与释放条件冲突，同一 session 在 `turn_aafd8f02-5da1-4d4c-8e50-304f57136d5d` 修订为本 v2。两轮 CLI 均 EXIT 0；本记录由 Codex 根据返回整理。

## 冻结语义

现行活动指针正则先行且不变，匹配成功则按现有路径、状态与 Task 全套检查；未匹配且未显式指定 `-TaskPath` 时，才按单行白名单识别空窗：

1. `^-\s*当前 Task：无[ \t]*$`；或
2. `^-\s*当前 Task：无（[^）]*）[。]?[ \t]*$`。

匹配行若包含大小写不敏感的 `tasks/` 或 `tasks\` 路径形态，拒绝作为空窗。空窗成立仅发一条 warning，跳过当前 Task 检查；其他全局检查仍执行。两者均未成立时维持原有两条 FAIL。显式 `-TaskPath` 不评估空窗且不发空窗 warning。

空窗行与合法活动指针并存时沿用指针、无新 warning；空窗行与终态指针并存仍按终态指针失败；多活动指针继续首个匹配；多个空窗行只发一条 warning。空窗注释不做自然语言语义判断，结构或路径形态不匹配则不能作为空窗。具体边界：`无效`、`无。`、半角冒号、未闭合全角括号、`无，但是正在执行某任务`、嵌套全角括号、全角注释中的 `tasks/`、`TASKS/` 或 `tasks\` 均须失败；藏在半角括号的 `tasks/FOO.md` 按现有指针路径检查。允许无路径形态的 `无（GOV-CHECKER-NOTASK-1 已收口）`。

## 实施后验证要求

- T1 空窗行加终态指针须出现终态错误；T2 空窗加显式 done/pending `-TaskPath` 须出现 integration_commit 错误且无空窗 warning。
- T3 覆盖上述非法和合法边界，断言目标错误，不只看 EXIT；T4 裸 `无` 成功；T5 双空窗只发一条 warning。
- T6 复跑 12 个原基线场景，只有明确空窗由两项失败变为成功，其余 EXIT 与目标错误一致；重复空窗加活动指针继续按活动指针。
- T7 在隔离副本分别注入“任意解析失败均放行”和“去掉路径排除”变异，证明缺失行及全角注释中 `tasks/FOO.md` 分别错误变绿；逐字节还原并记录 SHA，复测反例失败、正例成功。
- T8 收口时空窗 default、本卡 `-TaskPath`、18 pins 与 API inventory 均 EXIT 0。实现与证据分开提交；按原释放裁决进行独立 Review，最终由另一个独立 ZCode 会话裁决；禁止 push。

终态基线有历史证据字节和缺失 pyc 噪音，done/pending 构造有 closeout 噪音；判别必须核查指定错误行。隔离副本和诊断材料保留。
