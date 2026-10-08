# 可直接转发：DSH 接手 M2-PACKAGED-AC1-DLL-DIAG

在 `G:/CODEX/New Manga.worktrees/PACKAGED-AC1-DLL-DIAG-dsh` 工作。唯一仓库 `G:/CODEX/New Manga`，
Task=M2-PACKAGED-AC1-DLL-DIAG；Owner=DeepSeek Harness；非作者Reviewer=Codex；Integrator=Codex。
该Task已正式ready释放，本指令尚未通过CLI派发；开始前先完成Reality Check并由Codex串行登记认领，
再由Owner在分配分支将Task ready→in_progress。不要自行改Plan/STATUS/总索引，不启动未释放修复。

读取本checkout AGENTS.md、doc/REBASELINE_PLAN.md、doc/STATUS.md、doc/00_INDEX.md、
doc/09_COLLABORATION.md、doc/tasks/M2-PACKAGED-AC1-DLL-DIAG.md，
以及主仓库 `G:/CODEX/New Manga/verification/M2-PACKAGED-AC1-DLL-DIAG/release.md` 和本指令。
branch=agent/deepseek/M2-PACKAGED-AC1-DLL-DIAG；base=9063c317937b86bed1f6ff3e2f2c5d224dc10553；release/synced HEAD=4330b792479c7d251b6dd2389aefa4b1a1b7fe6f；
common-dir必须实测为 `G:/CODEX/New Manga/.git`。主仓库在release后仅追加恢复证据，
不要追随main或复用其他Agent dirty checkout；HEAD/输入漂移时停下相关操作，交Codex核对。

冻结诊断输入：构建source_head=cfb5d2eecc4d8ab7a3159cdbb1d5812547bb5cd2；
runner证据head=15cd788f10e83f6a1a215e71538bfa175b435785；
只读证据工作区 `G:/CODEX/New Manga.worktrees/RUNNER-SNAPSHOT-DEBT-codex`。
installer=`G:/CODEX/New Manga.worktrees/RUNNER-SNAPSHOT-DEBT-codex/apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe`；
SHA256=1cecca95d25439fca682cbe4336123d3b3352db229dd58c4e7d724b4d6c6ccb8；589904619 bytes。
释放时已复测匹配，接手仍须复测；缺失或不匹配记BLOCKED/UNKNOWN，不能用其他installer替代。
硬依赖GC-2 done@cea610ed已满足；runner debt仍blocked，仅作固定证据来源。

阅读 verification/M2-RUNNER-SNAPSHOT-DEBT/build-fingerprint.json、result-summary.json，
raw/packaged/cleanstart-ac1-run1-stdout.log、cleanstart-gate.json及sidecar-build/weights-retry/nsis原始日志。
已知CS-L1 PASS，完整26项=20PASS/1FAIL/5NOT_RUN；AC1 run1 QtGui ImportError，
具体DLL/导出符号与单次退出时间线UNKNOWN。只读追踪新架构Tauri packaged acceptance调用、
src/bootstrap/acceptance_bridge.py:173、packaging/m2ac5/core_sidecar.spec与build_sidecar.ps1，
研究真实DLL依赖/加载路径/构建环境差量。Qt只属于此验收入口，不开展Legacy UI诊断。
先读已有证据和现有工具，再做最小加载复现；在本Task自有lab复制/解包固定二进制，
不能在原证据worktree写输出，也不能用本checkout未修快照runner产生旧minor失败混淆诊断。

允许写：doc/tasks/M2-PACKAGED-AC1-DLL-DIAG.md；verification/M2-PACKAGED-AC1-DLL-DIAG/**；doc/handoffs/M2-PACKAGED-AC1-DLL-DIAG-*.md。
禁止写：src/**、apps/**、tests/**、packaging/**、依赖/Schema/wire/ACL、模型/共享环境、历史日志、
用户数据/Managed Copy/其他Agent工作区；不部署/push/合并main/reset/clean/stash。
不改系统PATH或安装开发Qt绕过原purged PATH Gate，不修改spec/源码验证猜想。
隔离子进程诊断对照须记录原环境和差量，不作为原Gate PASS。只管理自己创建的fixture/进程。
需要修复或越界时只提出新范围建议，不实施。具体DLL不存在证据时写UNKNOWN，不能从QtGui模块名猜DLL。

交付 verification/M2-PACKAGED-AC1-DLL-DIAG/REPORT.md、候选DLL/closure矩阵、原始日志及固定提交；
用doc/templates/HANDOFF.md写Handoff，引用固定delivery_head后追加；送非作者Codex审查。
矩阵逐项PROVEN/REJECTED/UNKNOWN，给出置信度/未覆盖项、最小拟议修复allowed_paths和后续fresh完整Gate。
每个运行日志带shell/解释器/版本/HEAD/命令/EXIT/耗时，PASS/FAIL/BLOCKED/NOT_RUN分列；
工具或沙箱不允许执行时明确NOT_RUN，静态扫描/文件存在不等于加载验证。

~~~powershell
Set-Location 'G:/CODEX/New Manga.worktrees/PACKAGED-AC1-DLL-DIAG-dsh'
git status --short --branch
git rev-parse HEAD
git rev-parse --path-format=absolute --git-common-dir
Get-FileHash -Algorithm SHA256 -LiteralPath 'G:/CODEX/New Manga.worktrees/RUNNER-SNAPSHOT-DEBT-codex/apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe'
git diff --check
git diff 9063c317937b86bed1f6ff3e2f2c5d224dc10553 HEAD -- src apps tests packaging
~~~

诊断探针尚未创建，具体命令由实际执行后入日志；不伪造产品测试PASS。
完成Gate=AC1-AC5证据齐备、allowed_paths逐项核对、Codex非作者Review和文档集成后验证。
诊断done不等于DLL修好，不自动解除runner debt；其解除仍需另行授权修复、fixed-head fresh构建，
完整26项Gate通过，再经非作者Review与Codex集成验证。无需在本Task引入新抽象或测试框架。
