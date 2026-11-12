# ZCode 原始审计范围恢复裁决

日期：2026-11-12
裁决上下文：ZCode CLI 全新只读会话
裁决时 HEAD：`033c3cf1af0e00e34172224c37a6c841277333bb`
外层 CLI：session=`sess_a2d20ca9-eaa7-49f8-95bf-2e67edbf8824`；turn=`turn_1a64fded-8e70-42b5-8f49-7fab16e23712`；trace=`422fc57e-18d3-48ef-927a-c580d3eed95a`；CLI EXIT=0。

## 结论

原始用户审计附件已从 Codex 会话恢复，包含 AUDIT-00–14 的逐项定义、审计授权与边界、结果分类、问题分级、交付物及完成条件。原 `BLOCKED-ORIGINAL-CHECKLIST-MISSING` 前提已消失。AUDIT-01–14 应恢复为 `NOT_TESTED`，不得因此标记为 PASS；AUDIT-00 保持段 B 已完成基线盘点范围内的 limited PASS，同时补齐原始 AUDIT-00 要求的项目清单；Release Gate 维持 `BLOCKED`，Task 维持 `in_progress`。

原件路径：`audit/V1-FULL-AUDIT/source/ORIGINAL-USER-AUDIT-INSTRUCTIONS-2026-10-24.txt`。本次独立复核结果：文件 SHA-256=`3EA8E623AE7EC6E492385005828DC43368563A78E4A91C9CAF8BB75DBB399EAF`；`git hash-object --no-filters` 与 `HEAD:<path>` 均为 `b775b8663c3827ed4a75d6b64ff2236b92151038`，三者字节一致。

## 状态与范围裁决

- AUDIT-01–14：逐项从 `BLOCKED-ORIGINAL-CHECKLIST-MISSING` 改为 `NOT_TESTED`。既有 pytest、probes、.NET、smoke、governance 结果只作为各专项的背景证据，不可由 suite 结果推导专项 PASS。
- AUDIT-00：当前 Git/environment/source baseline 结论仍有效；启动入口、66-command 面、数据库 schema、模型资源 pin 和结构/模块索引仍须补齐至 `01_PROJECT_INVENTORY.md`。
- 旧“等待用户提供清单或接受 `closed_with_limitations`”分支由附件恢复事实取代。生命周期更正报告中关于永久限制接受的等待语义不再适用；任务继续执行，不关闭、不转 `in_review`。
- ZCode 给出的可执行顺序：裁决落盘与状态重置；AUDIT-00 项目盘点；AUDIT-02 静态扫描与 AUDIT-01 架构审阅；既有 suite 结果按专项映射；AUDIT-11 安全静态审阅；AUDIT-08 隔离数据库异常模拟和 AUDIT-05/06 契约核对；AUDIT-14 功能覆盖/债务盘点；合成 fixture 和隔离场景；最后形成问题、整改计划、Release Gate 与正式报告。
- 继续遵循 Task `allowed_paths`、原始审计授权和现行素材边界。任何产品源码、原有测试、契约、Schema、依赖或治理范围外改动均停止；真实 GUI、TestHost、沙箱 grant、干净 Windows、真实付费 API、真实素材内容等证据缺口使用各自具名 `BLOCKED`/`NOT_RUN`，不得用静态分析、mock 或合成样本冒充实测。

## 裁决来源及证据限制

原始 ZCode CLI 输出保存在仓外：`G:\CODEX\New Manga.workspace\agent-output\codex\NEW-MANGA-V1-FULL-AUDIT\zcode-original-scope-readjudication-20261112.log`，SHA-256=`5A0DE1E20FFE9B573138488A447439856BE778FA9B11738BB98E8357119EA18F`，CLI EXIT=0。原始输出正文称其交互会话无派发 ID，但外层 CLI JSON envelope 实际记录了本报告开头列出的 session/turn/trace ID；本报告按外层机器记录披露两者，不隐去不一致。

ZCode 在 plan mode 中尝试的 shell 调用被策略拦截（“Plan mode only allows read-only, non-destructive tools”），该尝试未执行且没有 shell EXIT。其对原件哈希、Git pin 和既有治理门禁的判断依赖仓库已有证据。本报告单独记录本轮 Codex 对原件 SHA-256、blob 与当前 HEAD blob 的复算；没有把既有门禁写成此次复跑。

本裁决不等于全审 PASS、AC 完成、Task 关闭或软件发布准入通过。
