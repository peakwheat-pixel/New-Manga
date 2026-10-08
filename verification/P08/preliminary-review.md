# P08 草案独立预审意见

类型：Codex Reviewer 子代理的只读预审；审查者未撰写原草案。本意见不是项目指定DSH正式Review，也不批准产品范围。审查head=`f7d4a947`。产品测试未运行。

## P1：修订后再提交正式Review

1. AC_COVERAGE原193项只覆盖编号AC；漏D08 §53发布主流程、§68–77自动化/视觉/Benchmark/安全/发布清单/READY，以及§79收口。D08 §73要求Backup/Restore PASS、P0/P1 100%。原草案建议延期备份恢复，不能同时声称完成当前发布Gate。将总Gate纳入覆盖，并将是否保留D08作为显式用户决定。
2. 模型下载进度与中断恢复属于产品能力，原映射仅P18实验/P20打包，没有实现Owner。要求D6明确决定；若纳入建议P15负责Core/设置链，若延期需用户批准改D08 P0/P1/READY要求。
3. 空库建Book/Chapter需要生产Core写入口。原P09导入适配/P12前端范围缺契约/Core/Host负责人。建议P09列CreateBook/CreateChapter契约与Library Core/Host路径，P12由ZCode接UI。
4. Plugin/Hook、字体上传、Sakura分别存在D01目标和D08 §78 AC；“Plugin Agent”不覆盖上述功能。要求逐项成为用户选项。
5. D08平台、性能、容量表归属混淆实现与验证；P02是观察验证任务，不能隐含改生产。将候选实现Owner与DSH/Codex验收责任分列；发现缺口另行立项。

## P2：恢复材料

初始恢复点未记录提交后的head。补充初交付head=`f7d4a947`和这次实际修订/验证head，记录dirty原作者文件并保留漂移检查。

## 已核实准确项

正式production import decoder是1×1 passthrough；main.rs命令面没有完整Import/CreateBook/StartRun/ReaderProgress/Export；TaskProgressPanel明确静态；production export assembly未注入PDF composer。Qoder已退出，ZCode UI主责，Reader仍保持待裁决；草案未擅自解冻。

## 结论

修订AC-SMOKE/总Gate、D08冲突、实现责任与用户选择后，草案可再送指定非作者DSH正式Review。此预审只帮助准备，不是批准或验收。
