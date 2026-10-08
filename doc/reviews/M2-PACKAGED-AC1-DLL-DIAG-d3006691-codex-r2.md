# Codex 非作者 Review r2：有界修正已核对，诊断Gate仍BLOCKED

base=9063c317937b86bed1f6ff3e2f2c5d224dc10553；reviewed_head=d30066917759b62133840ac6767c7ef67153be06。
Owner=DSH；Reviewer/Integrator=Codex；真实CLI r1/r2 EXIT0，同一会话session-7de56368-5e9b-44ed-9e2d-0c288fdc67ff。
静态核对R1 fail-closed、R2默认不启动原bundle/只运行复制校验的自有副本、R3去掉126推断：已修正。
复制校验失败时Step5被跳过，后续仅静态扫描；不将程序外层退出码当全Gate通过。
Codex实测Owner HEAD/clean/common-dir、git diff --check及src/apps/tests/packaging零差量。
DSH FINAL-r1/r2原文Git内容与实际CLI final.text逐字节一致，未修改原始审查/执行失败证据。

执行限制：DSH pwsh沙箱grantWrite失败，无实际DLL加载、installer复测或机器级探针运行。
Codex本轮只做文件/范围/治理核验，未启动acceptance程序；静态修正不等于运行批准。
PE探针未独立验证，特别延迟导入/候选搜索是手写近似；不能把“missing_union”直接当Loader根因。
本Task AC2运行复现/加载证据仍NOT_RUN；具体DLL/符号/Win32码与安装树完整性UNKNOWN。
后续实跑前应再核对installer与bundle exe固定build-fingerprint、正确fixture/隔离目录和超时；
原Bundle hash仅复制等价不等于固定构建来源。不得把构建树存在性当安装态存在/加载证明。

结论：未批准Task完成或探针的运行验证，TaskStatus=blocked、previous=in_progress，
blocker=dsh_exec_sandbox_and_unverified_dynamic_diagnosis。原runner debt仍blocked，生产修复未释放。
下一步在当前诊断Task补可信隔离执行路径和实际日志，并回DSH修订矩阵后由Codex重审；
不自动创建/释放Qt闭包修复Task。会话精确挂载成功，desktop下次启动可发现，未重启，visibility=unverified。
