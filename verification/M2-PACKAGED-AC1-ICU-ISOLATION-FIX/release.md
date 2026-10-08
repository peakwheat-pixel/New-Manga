# ICU隔离修复：实际释放恢复点与实施指令

## 2026-10-08 Codex释放记录

- Task=M2-PACKAGED-AC1-ICU-ISOLATION-FIX；TaskStatus=ready；ExecutionState=IDLE；尚未认领/派发/实现。
- Owner=Antigravity；非作者Reviewer=DeepSeek Harness；Integrator=Codex。
- 唯一仓库=G:/CODEX/New Manga；common-dir=G:/CODEX/New Manga/.git。
- base=5a72db9e3c5778ce4700b7d404250853e474c5de；release_commit=3d6d8743f662cb850e570e1fa248b96258fee714。
- branch=agent/antigravity/M2-PACKAGED-AC1-ICU-ISOLATION-FIX；实际worktree=G:/CODEX/New Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity。
- 实际synced HEAD=3d6d8743f662cb850e570e1fa248b96258fee714；FF前clean/初始HEAD=base；FF后clean、branch/common-dir正确、git diff --check EXIT0。
- 释放提交仅Task/Plan/STATUS/两个索引，共5文件；src/apps/tests/packaging/依赖生产差量为零。
- 主线Qoder未提交report.json和canvas文件保留，没有stage/修改/清理；主线并非clean。
- 产品测试全部NOT_RUN；本轮没有构建、安装、实际loader验证或生产改动；不声称修复成功。
- 下一Exact Step：Codex串行登记本Task认领及STATUS ACTIVE，再通过antigravity-dispatch真实外部CLI发送下段；禁止尚未登记就开工。
- 后续主线追加本记录仅治理差量；Owner恢复点固定上述release，不要求盲目追主线新HEAD。

## 固定验证输入

- `2af6b71aa06979b822e543b221aaf3a2d5f01abe:packaging/m2ac5/run_clean_start_e2e.py` SHA256=`9c8fff9d55936b9b872405d8fc12dad0af0005e5fe0b8b4688dfe2d21bec8216`（Git blob原始字节）。
- `2af6b71aa06979b822e543b221aaf3a2d5f01abe:verification/M2-RC2/run_e2e.py` SHA256=`7e0a4ce503a1c4a980b236a2497ee511b495fa708573aa5c78aa39aa59a2112b`（Git blob原始字节）。

诊断报告head=229c6c371d34234b65bbdd67fff73f341c60930f；诊断merge=4431754845fc25795058534f21656705ef701cd6。
原构建source_head=cfb5d2eecc4d8ab7a3159cdbb1d5812547bb5cd2；原installer SHA256=1cecca95d25439fca682cbe4336123d3b3352db229dd58c4e7d724b4d6c6ccb8，589904619 bytes。
诊断只证明固定产物本机同名ICU遮蔽因果；原GateWin32错误、其它ICU78消费者仍UNKNOWN。初始pefile8192截断造成的64项QtGui符号误报已撤回，不能当修复依据。

## 可直接转发给Antigravity的完整指令（待串行登记后派发）

```text
在 G:/CODEX/New Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity 工作。
Task=M2-PACKAGED-AC1-ICU-ISOLATION-FIX；Owner=Antigravity；非作者Reviewer=DeepSeek Harness；Integrator=Codex。
branch=agent/antigravity/M2-PACKAGED-AC1-ICU-ISOLATION-FIX；base=5a72db9e3c5778ce4700b7d404250853e474c5de；
release/start_head=3d6d8743f662cb850e570e1fa248b96258fee714；common-dir必须G:/CODEX/New Manga/.git。
先读取AGENTS.md、doc/REBASELINE_PLAN.md、doc/STATUS.md、doc/00_INDEX.md、doc/09_COLLABORATION.md、正式Task，
以及主仓 G:/CODEX/New Manga/verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/release.md。
读诊断Task、verification/M2-PACKAGED-AC1-DLL-DIAG/REPORT.md、local-evidence.md、dll-closure-matrix.json、
raw/symbol-probe-full-exports.json、raw/icu-control-result.json和doc/reviews/M2-PACKAGED-AC1-DLL-DIAG-229c6c37-codex-r3.md。
实测git status --short --branch、git rev-parse --path-format=absolute --git-common-dir、git rev-parse HEAD、git diff --check；
必须branch/head/common-dir匹配、工作区clean；存在漂移先记录并交Codex，禁止覆盖他人修改。
须Codex已串行认领并登记STATUS ACTIVE才改Task为in_progress，保持checkpoint；不得自行修改共享总索引。

硬依赖：诊断done@4431754845fc25795058534f21656705ef701cd6、GC-2 done@cea610ed3f3349f1d76361d151815445e991f7d7。
关联M2-RUNNER-SNAPSHOT-DEBT仍blocked，不当done依赖，不自动合并其修复。
目标：Windows/React/Tauri安装态Qt不被包内不兼容icuuc同名遮蔽，同时保留实际ICU78消费者。
先追踪现有build_sidecar/spec/入口与DLL加载全链路，识别5入口实际ICU78消费者并逐项证据/UNKNOWN，
再选最小打包闭包隔离修复；禁止直接照诊断副本改名动作发行或全局删ICU，不造新通用抽象。

allowed_paths=packaging/m2ac5/**、doc/tasks/M2-PACKAGED-AC1-ICU-ISOLATION-FIX.md、
verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/**、doc/handoffs/M2-PACKAGED-AC1-ICU-ISOLATION-FIX-*.md。
生产仅packaging/m2ac5/**；src/apps/tests只读，禁止依赖清单/版本、Schema、共享IPC/ACL、Legacy改动。
构建仅自有worktree ignored产物/模型/隔离lab、安装fixture；保护源文件、人工修改、Lock、current/pinned Revision、Managed Copy及恢复。
不写旧Task/raw、不改System32/PATH/共享环境或既有安装/用户目录；不部署/推送/合并main/master，
不reset/clean/stash他人工作区；需要依赖升级/共享启动代码时暂停越界部分，Task记录blocked交Codex/用户重新冻结。

主线runner仍旧快照；本Task验证精确复用head=2af6b71aa06979b822e543b221aaf3a2d5f01abe的
packaging/m2ac5/run_clean_start_e2e.py与verification/M2-RC2/run_e2e.py，
用git show原始字节复制到本Task verification根，核对上方SHA256、实测REPO定位，
不修改minor响应/命令集合/场景/阈值；所有--output-dir指向本Task新输出，自有fixture隔离。
复制仅验证来源，不等于runner debt集成。旧probe fixture只读复用；定位不适配交Codex，不静默改验收。

planned：pwsh -NoProfile -File packaging/m2ac5/build_sidecar.ps1 -Force；必须fresh五入口成功，
不能用skip-existing替代。核对既有Tauri构建入口，在apps/desktop构建fresh NSIS，绑定source_head、
5入口/installer路径/SHA256/大小、锁定依赖、shell/解释器、命令、EXIT、耗时和完整日志。
用固定dev runner副本 --exe <本次exe> --skip-build --output-dir <本Task新dev目录>：完整10项Gate+13 probe，15 production/7 probe严格一致。
用固定packaged runner副本 --installer <本次installer> --output-dir <本Task新packaged目录>：完整26项全PASS，
CS-L1响应minor1.6/请求minor3兼容、两轮AC1、重启新PID、summary/reader恢复、PNG digest一致；原purged PATH保持。
再验证普通PE导入/导出+真实loader/bridge、实际ICU78消费者、原失败/修复后对照与运行后无自身sidecar残留。
证据全落本Task verification，PASS/FAIL/NOT_RUN/skip分列及理由，外层EXIT0不等于场景通过；旧FAIL永不回填。

交付最小打包改动和闭包判别检查、固定实现commit、Task逐项AC证据、checkpoint、完整fresh构建/Gate日志、
installer/source_head/hash绑定及doc/templates/HANDOFF.md规范Handoff（实现head后追加文档引用该head）。
交付时再次git status/HEAD/common-dir/diff --check，并验证范围外差量为零；不把未跑产品Gate写PASS。
固定代码head和Handoff后交实际非作者DSH审查；DSH approved后Codex集成及集成后验证才能done。
完成后推荐Codex恢复M2-RUNNER-SNAPSHOT-DEBT重新完整验收/独立审查/集成；不自行释放后续Task。
```
