# 下一步释放准备：ICU隔离修复（未创建/未释放）

- Task：M2-PACKAGED-AC1-ICU-ISOLATION-FIX；目标为安装态Qt不再被不兼容的同名ICU遮蔽，同时保留其它ICU78消费者。
- Owner：Antigravity；非作者Reviewer：DeepSeek Harness；Integrator：Codex。
- 启动条件：Codex创建正式Task、冻结允许路径、实测分配branch/worktree、ready提交并同步后，才可派发实现。
- 硬依赖：M2-PACKAGED-AC1-DLL-DIAG done@merge4431754845fc25795058534f21656705ef701cd6；GC-2 done@cea610ed。
- 新base建议（已实测）：2c8e3e5902c1fbc9d1ad228ec4fc4fe491b7d41e；当前后续追加只有治理文档。新branch/worktree=待Codex创建，不猜路径或复用dirty checkout。
- 固定诊断报告head=229c6c371d34234b65bbdd67fff73f341c60930f；诊断Owner恢复HEAD=c2bde356554c37520bd87d0bc13791a748250133（clean），
  worktree=G:/CODEX/New Manga.worktrees/PACKAGED-AC1-DLL-DIAG-dsh，只读输入，不在此checkout实施修复。原source_head=cfb5d2ee。

## 拟议范围与Gate（需落正式Task冻结）

允许生产修改仅packaging/m2ac5/**；自己的verification、Task、Handoff；Reviewer报告与Codex治理按协议。
禁止src/apps/tests、依赖版本/Schema/公共契约、其它Task历史证据、用户数据/Managed Copy修改；不部署/推送/全局删ICU。
若单靠打包范围不足、必须依赖升级/启动共享代码改动，先停越界部分，交Codex/用户重新冻结。

交付：最小打包修复、普通导入/导出与Loader闭包判别检查、其它ICU78消费者验证、固定提交/Handoff，
fresh Sidecar与NSIS完整构建日志、installer hash/source_head绑定，dev与packaged完整Gate，非作者Review及集成验证。
诊断副本中改名DLL只是因果对照，不能直接作为发行实现，更不能删除用户/已安装目录中的DLL。
先识别哪些实际打包组件需要ICU78，再选择能兼容两类符号需求的最小闭包隔离；不构造通用插件/registry框架。

验收使用已冻结minor1.6响应/15生产命令的runner逻辑。原M2-RUNNER-SNAPSHOT-DEBT仍blocked且实现未合并，
主线两份旧runner仍有陈旧快照；禁止以旧runner的minor3/9项错误作为本次修复结果。
复用固定代码head=2af6b71aa06979b822e543b221aaf3a2d5f01abe里的
packaging/m2ac5/run_clean_start_e2e.py和verification/M2-RC2/run_e2e.py，
在新Task verification内保留精确来源/hash的隔离副本，实测REPO定位，保持26场景/15命令/7probe与所有阈值。
不得回写旧Task/raw；复制只为验证来源，不等于runner debt已集成或关闭。

planned构建：pwsh -NoProfile -File packaging/m2ac5/build_sidecar.ps1 -Force（fresh，不以skip-existing替代）；
在apps/desktop运行既有Tauri build命令；本次实际产物NSIS和5入口来源与head/hash绑定。
planned验收：冻结dev完整10项+probe13项；packaged完整26项（不把外层EXIT0或部分PASS当通过）；
原purged PATH、用户目录零触碰、无残留sidecars、原所有源文件/人工修改/current/pinned保护。
所有新日志带命令/shell/解释器/HEAD/EXIT/耗时，PASS/FAIL/NOT_RUN/skip及原因分列，旧FAIL不回填。

## 可直接转发给Codex的释放指令

在G:/CODEX/New Manga读取AGENTS、Plan/STATUS、诊断Task/REPORT和Codex r3 Review。
以base=2c8e3e5902c1fbc9d1ad228ec4fc4fe491b7d41e核对后续纯治理差量，单独创建并释放M2-PACKAGED-AC1-ICU-ISOLATION-FIX，
Owner=Antigravity，非作者Reviewer=DSH，Integrator=Codex；按上述生产/验证范围落正式Task。
先实测创建唯一branch/worktree并同步实际release commit，不复用其他Agent dirty工作区。
准备自包含Antigravity实施指令，含实际base/head/branch/worktree/allowed_paths/固定报告与测试来源。
正式ready后利用antigravity-dispatch skill自动调用真实外部Agent，取回固定代码/测试/Handoff，交真实非作者DSH。
若涉及依赖升级/共享seam，先交用户选择；未释放前不启动生产实现。
修复Task Gate闭合并集成后，才回M2-RUNNER-SNAPSHOT-DEBT重新完整验收、审查与集成关闭。
