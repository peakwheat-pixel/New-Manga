请对项目 G:/CODEX/New Manga 的 P04 提案做一次只读范围/验收审查。

固定候选：branch codex/P04-scope-freeze，reviewed head 018023e8129ee9e34f441e39b30ab0c22786eccc，base 88579622d85ff6d0dfd509c6f21931bd91d0881b。
请直接阅读该固定 head 的 doc/tasks/P04.md、doc/REBASELINE_PLAN.md、doc/STATUS.md、doc/00_INDEX.md、verification/P04/proposal-checkpoint-20261010.md，以及相关源文件 apps/desktop/src-tauri/src/main.rs、apps/desktop/src-tauri/src/library_bridge.rs、apps/desktop/src-tauri/Cargo.toml、doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md、doc/tasks/M2-PAGE-NAV-PROJECTION-1.md。

审查重点：
1. P04 是否保持 proposed，依赖/当前状态是否准确，范围是否最小并有明确的 Owner/Reviewer 分离。
2. AC1 是否真正覆盖 PAGE_NAV_PRODUCTION_ONLY_COMMANDS 的等长错替换；测试命令是否对应当前 bin target。
3. AC2/AC3 是否能作为确定性诊断，是否存在要求含糊、不可实现、会误把未运行写成通过或会导致 P04 与修复任务循环的问题。
4. allowed_paths、禁止事项、P02 Hard Build Barrier 条件是否自洽；是否意外授权修改生产逻辑、协议或运行受禁操作。
5. Plan/STATUS/Index/checkpoint 之间有没有状态冲突、坏链接或遗漏的恢复信息。

请不要修改文件；不要运行 Cargo、Tauri、任何构建/测试、Sandbox、Windows Sandbox Feature 查询/启用、scratch clone，也不要创建/派发其他 Task。仅作静态只读检查。

返回中文 Markdown：先写 verdict（approve / changes requested / blocked），随后列 P0-P3 findings（精确路径与行号、影响、最小修正）；如果没有 finding，写 `P0/P1/P2/P3 = 0/0/0/0` 并说明未运行测试、结论仅限提案静态审查。不要把本审查表述为 P04 实现 Review 或产品 Gate。