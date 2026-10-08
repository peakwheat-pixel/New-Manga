# M2-RUNNER-SNAPSHOT-DEBT：Codex blocked Handoff

2026-10-08；Owner=Codex；非作者 Reviewer=DeepSeek Harness；Integrator=Codex。
TaskStatus=blocked / previous=in_progress；ExecutionState=CHECKPOINTED。
本交付是待审查的实现与阻塞证据，不是独立批准或主线集成。

## 固定恢复点与结果

唯一仓库G:/CODEX/New Manga。
base=968c8f34601b72667831f1fd15bb20cd2c8f3cb7。
branch=codex/M2-RUNNER-SNAPSHOT-DEBT；
worktree=G:/CODEX/New Manga.worktrees/RUNNER-SNAPSHOT-DEBT-codex；
common-dir=G:/CODEX/New Manga/.git。
release=1ac7aa83；claim=b3860981；实现代码=d1c279db45904c6009dbc696d95a0b4a63ebd837；
含日志harness的固定构建/测试head=cfb5d2eecc4d8ab7a3159cdbb1d5812547bb5cd2。
后续只提交文档/日志；待审查head由实际git rev-parse记录，不猜自身hash。

两处快照修复完成：安装态ping响应严格1.6，minor3请求保留兼容探针；
生产命令15条严格ordered equality，probe7条冻结。
output-dir隔离产物；RC2 fresh lab，packaged本次自有lab/install，
避免复用/清理共享安装目录；无产品Schema/wire/ACL/依赖变动。

**dev Gate PASS；packaged CS-L1 PASS；完整packaged Gate FAIL/BLOCKED**。
真实安装态acceptance_bridge.exe导入QtGui失败：
ImportError: DLL load failed while importing QtGui。
AC1 run1无结果，既有240秒上限超时退出；未改timeout或场景阈值。
本轮不修禁止范围spec/依赖/acceptance_bridge，不合并两处runner实现到main。

## AC 与真实验证

| AC | 结果 | 证据（verification/M2-RUNNER-SNAPSHOT-DEBT/） |
|---|---|---|
| AC1 基线漂移 | PASS | baseline-evidence.md，旧GC-2报告保持原文 |
| AC2 两处快照 | PASS | 实现diff，actual CS-L1 PASS，dev production15条 |
| AC3 判别 | PASS | check_snapshots.py；raw/check-snapshots.log：12实际谓词用例 |
| AC4 全Gate | FAIL / BLOCKED | dev10/10+probe13/13 PASS；packaged20 PASS+1 FAIL，后续AC1五项NOT_RUN |
| AC5 保护/范围 | PASS | history-index-before.txt、范围检查；旧raw/报告/probe零差量，syntax/diff通过 |
| AC6 Review/集成 | PENDING | 真实DSH审查待执行；没有实现集成/done |

PowerShell；Python3.12.3（T1.1.1 venv）、cargo1.98.1、rustc1.98.1、
node24.15.0、npm12.0.1；真实环境记录见raw/dev-r2/e2e-environment.json。
没有全仓pytest/vitest复跑声称，没有干净Windows机/分发迁移保证。
最小检查负向样本打印FAIL是期望的拒绝结果，整体assert检查EXIT0，不是运行时Gate失败。

- npm-ci/frontend-build EXIT0：raw/npm-ci.log、frontend-build.log。
- 初次dev EXIT1：fresh checkout没有sidecar bundle，raw/dev-runner.log及raw/dev/保留。
- fresh PyInstaller完成所有入口，但原PowerShell5脚本weights阶段Get-FileHash解析失败，
  整条命令EXIT1：raw/sidecar-build.log。
- 用PowerShell7运行同一未改脚本，复用本次fresh bundle完成两组模型哈希校验与复制，
  EXIT0：raw/sidecar-weights-retry.log。没有SkipWeights，没有旧bundle拷贝。
- dev重跑完整Gate10/10+probe13/13、无missing/unexpected/non-PASS，EXIT0：
  raw/dev-runner-r2.log、raw/dev-r2/e2e-gate.json。
- fresh NSIS构建EXIT0：raw/nsis-build.log。
- installer SHA256=1cecca95d25439fca682cbe4336123d3b3352db229dd58c4e7d724b4d6c6ccb8，
  source_head=cfb5d2ee；build-fingerprint.json与cleanstart-gate.json SHA实测相等。
- packaged实际运行EXIT1：raw/packaged-runner.log、raw/packaged/cleanstart-gate.json；
  CS-L1 PASS；唯一已报告FAIL=CS-A1-run1-completed；run2/restart/saved/reader/export
  五项NOT_RUN。QtGui原始失败日志=raw/packaged/cleanstart-ac1-run1-stdout.log。
- production、zero-touch和no-surviving-sidecars均PASS；没有清理用户目录/他人进程。

所有命令/HEAD/EXIT/原始输出在run_step日志头尾，无摘要代替真实执行。
Tauri生成文件仅LF/CRLF变化；在本Task独占checkout断言内容等价后恢复换行，
build-generated-normalization.json记路径；不是产品修复，最终src/apps/tests零差量。

## 风险、停止条件及下一步

QtGui失败的具体DLL/构建环境原因仍UNKNOWN；本轮没有证明是产品源码回归、
安装路径问题或哪个DLL缺失。禁止靠purged PATH增加开发Python/Qt路径绕过验收。
当前两处快照修复仅在Owner分支，主线保留旧FAIL，Task不能done。

下一接收者=真实DSH非作者，固定本次证据head，审查代码/判别力/FAIL及范围；
Review批准代码不替代AC4，也不能据此合并或放宽Gate。

推荐Codex下一步释放只读诊断候选M2-PACKAGED-AC1-DLL-DIAG，Owner=DeepSeek Harness，
非作者Reviewer=Codex，Integrator=Codex；尚未创建/释放，branch/worktree待Codex实测分配。
诊断只针对新架构Tauri packaged acceptance入口与构建环境，不开启Legacy UI修复。

可直接转发给Codex：
在G:/CODEX/New Manga读取本Handoff、正式Task及packaged失败原始日志。
先冻结并释放M2-PACKAGED-AC1-DLL-DIAG，只读跟踪安装态acceptance_bridge的QtGui导入/
DLL解析、PyInstaller closure和与已知PASS构建环境的差量；Owner=DSH、Reviewer=Codex。
固定输入source head=cfb5d2ee、installer SHA如上；现有证据worktree如上，诊断branch/worktree
待Codex创建，不复用他人dirty checkout。只写诊断Task/自己的verification/Handoff，
生产/spec/依赖只读；使用自有隔离fixture，不改PATH放宽原Gate，不删用户文件。
交付具体失败DLL/环境证据或UNKNOWN、最小修复范围建议；修复须另行冻结授权。
解除本Task阻塞需fixed-head fresh构建+AC1/完整packaged Gate通过，随后真实非作者审查、
Codex集成后检查；不得将本轮20项PASS当整个Gate通过。
