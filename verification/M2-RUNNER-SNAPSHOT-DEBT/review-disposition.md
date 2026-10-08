# DSH r1 处置（任务仍BLOCKED）
2026-10-08；真实CLI EXIT0；session-dbe4f574-2377-4302-885a-1f4cba2ae9f9。
精确工作区会话挂载EXIT0；desktop下次启动后可发现，本轮未重启，web_visibility=unverified。
报告原文按final.text UTF8入Git；完整blob原字节SHA见review-binding.log。
r1 reviewed_head=7556cb2d；代码approve_with_conditions，0P0/P1/P2；
整个Task blocked / AC4 FAIL / AC6未集成，Code approval不能代替完整Gate。

C1/F04：git diff --name-only cfb5d2ee 7556cb2d、实际rev-parse已落盘，只有文档/证据，
raw构建HEAD=cfb一致；后继RC2只改docstring，AST等价已断言。
C2/F01：改为从释放Task/M2-C1 rev1.8 §5手动固定的独立15条oracle，分别比对Rust与runner，
不能从被测实现/回包动态生成期望；F02 capability/error/status四个负向新增，
最小实际谓词检查现在16项，父侧EXIT0。
F03：probe混入用例只是等值多项拒绝；另有真实probe公告反向校验，声明不夸大。
C3/F05：旧run_app没有单次起止/timeout分支日志，精确退出时间线无法事后重造，改UNKNOWN；
DLL/详细时间线交候选只读诊断，本轮没有伪造超时分支PASS。
F06：明确PS7省略Force，仅走skip-existing路径的模型hash/copy；未重跑PyInstaller。
F07：补RC2 usage/output-dir及fresh lab文档串。
C4：DSH误写scratch违背只读指令，报告主动erratum；确认自有raw路径/唯一marker，
按其作者明确清理说明移除单一scratch，无用户或其他Agent文件删除。
r1报告内部F17编号及21/21完整Gate建议原文保留；实际应为26个完整场景，
当前21个报告=20PASS/1FAIL，另5NOT_RUN，不放宽到21项。
后续r2只复核有界修正，不重复或豁免AC4；Task不合并实现，不done。
