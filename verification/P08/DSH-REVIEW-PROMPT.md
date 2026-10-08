# P08 DSH正式Review指令（草案，尚未派发）

Task：P08「完整产品范围与验收冻结准备」。只读独立非作者审查。Owner=Codex；建议Reviewer=DeepSeek Harness（未认领）。Codex子代理预审不能记作DSH正式Review，也不能替代批准。

用户D1–D7已全部确认。base_commit=ab2f813c0ce311a6712002cafd852b9e7a258380；reviewed_head=490f9bd9637de0812a3ef3d9bbfa754868d5c15f；仓库G:/CODEX/New Manga，交付branch=main；Review worktree待Codex创建。固定交付见[Handoff](../../doc/handoffs/P08-490f9bd9.md)。恢复核Live Git；后续checkpoint文档提交不能替代本固定被审材料。

阅读：`doc/tasks/P08.md`、`verification/P08/SCOPE_DRAFT.md`、`AC_COVERAGE.md`、`preliminary-review.md`、D01/D04/D05/D07/D08、AD-001、M2-C1、当前Plan/Status、Core/Desktop审计及对应代码。

逐项审查：D08全部编号AC、AC-SMOKE、§68–79总Gate是否映射完整；P0/P1、Backup/Restore、clean Windows和AC-SMOKE现行要求是否全部保留且与用户决策一致；模型下载、建书Core写入口、PDF/MOBI及Plugin/Hook/字体/Sakura是否按已确认D1–D7有清晰实现Owner；MOBI/CBZ/PDF/文本新增验收是否完整；所有数据保护、Secret和失败/恢复Gate是否覆盖；表格区分实现Owner/验证Owner；P09–P20依赖、路径、Owner、非作者Review是否符合当前协议（Qoder退出、ZCode UI主责）。

输出逐条P0/P1/P2 findings、精确路径/段落、最小修订建议及实际测试命令/环境；未运行写NOT_RUN。固定reviewed_head；Review不扩Task范围，不释放P09–P20。只有用户裁决已记录（已完成）、Review findings闭合、Codex集成验证通过才可建议P08 done。

本文件是交接准备，尚未向DSH派发。
