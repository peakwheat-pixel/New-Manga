# R1处理记录

R1 reviewed_head 3879cb936，changes_requested；原Review完整保留review-dsh-r1.md。

|项|修订|实测/限制|
|---|---|---|
|P1诊断承载|每record source/destination各一条DECL_BROAD_ROOT_PRESERVED，沿用add_warning四字段，无新diagnostics schema；6×2=12warnings|内存拷贝实际调用add_warning12次并复算，warning恰+12；真实guard仍24，未实施loader|
|P1激活来源|policy存在但untracked=POLICY_UNTRACKED fatal；tracked缺失=MISSING fatal；Git查询失败fatal|冻结T14/T18，运行负例PLANNED/NOT_RUN；tracked不是固定commit独审替代|
|P2相邻断言|只断言新增五根没有命中，不要求repo原evaluate为空|15模型覆盖重算PASS|
|P2原子/计数|独立容器与独立scanned，原index容器不写穿；全部登记/warning/计数成功才最终返回新快照；任一异常丢弃暂存、原快照+fatal|T01/T12注入第1/6/12登记、warning/计数阶段失败；真实异常测试PLANNED/NOT_RUN|
|P2非Gitfixture|未安装保持原行为仅限有效Git RepoFixture；nonGit scanner继续fatal；直接ProtectionIndex/model不触发Git|无noGit旁路，未来T14覆盖|

两原源、7只读输入、69例外、运行工具及scope不变。用户只裁定整体保护与设计，仍不授权实现/清理。下一固定head DeepSeek R2复审，不能延用R1批准。
