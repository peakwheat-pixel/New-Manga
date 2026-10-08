# 下一步：同Task补动态证据，不释放修复

Task=M2-PACKAGED-AC1-DLL-DIAG；Owner=DSH；Reviewer/Integrator=Codex。
唯一仓库G:/CODEX/New Manga；branch=agent/deepseek/M2-PACKAGED-AC1-DLL-DIAG；worktree=G:/CODEX/New Manga.worktrees/PACKAGED-AC1-DLL-DIAG-dsh。
base=9063c317937b86bed1f6ff3e2f2c5d224dc10553；Owner恢复HEAD=db65b6cfccebf9a9792631b903507ba0313c8109（clean），
待实跑probe固定head=d30066917759b62133840ac6767c7ef67153be06。
Task blocked；启动条件：有可实际执行且日志可信的隔离命令环境；先由Codex核对漂移/冻结执行范围再登记恢复。
不要重复使用DSH当前已报Win32 5的命令沙箱，也不要安装共享依赖或放宽原Gate来消除阻塞。

可直接转发给Codex/DSH：读取Task、checkpoint及Codex r2 Review。核对上述base/head/common-dir和输入。
同Task诊断输入仍为source_head=cfb5d2ee、installer SHA256=1cecca95d25439fca682cbe4336123d3b3352db229dd58c4e7d724b4d6c6ccb8。
先建立可信执行路径，再核对build-fingerprint的bundle exe pin、正确隔离fixture、超时和自身进程管理。
仅写Task、自有verification和Handoff，Reviewer只记录独立验证证据；src/apps/tests/packaging/依赖/Schema/用户数据只读。
先进行静态验证，再按审查后的probe自有lab复制运行；未执行步骤NOT_RUN，PE静态输出不是Loader根因。
将实际命令/环境/HEAD/EXIT/耗时、文件hash和加载结果入库，交DSH更新候选矩阵PROVEN/REJECTED/UNKNOWN，
固定新报告head后由非作者Codex重审。不要自动采用Qt闭包修复建议，修复范围须另Task冻结。
诊断done不解除runner debt；仍需后续授权修复、新fresh installer、完整26项Gate及独立Review/集成。

~~~powershell
Set-Location 'G:/CODEX/New Manga.worktrees/PACKAGED-AC1-DLL-DIAG-dsh'
git status --short --branch
git rev-parse HEAD
git rev-parse --path-format=absolute --git-common-dir
git diff --check
git diff 9063c317 HEAD -- src apps tests packaging
~~~
