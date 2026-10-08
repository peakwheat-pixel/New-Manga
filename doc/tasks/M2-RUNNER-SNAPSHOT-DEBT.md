---
id: M2-RUNNER-SNAPSHOT-DEBT
title: 修复验收 runner 协议与生产命令快照漂移
kind: maintenance
status: blocked
approval: user_authorized_release_20261008
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness（非作者）
integrator: Codex
depends_on: [M2-DERIVED-GC-2]
base_commit: 968c8f34601b72667831f1fd15bb20cd2c8f3cb7
branch: codex/M2-RUNNER-SNAPSHOT-DEBT
worktree: G:/CODEX/New Manga.worktrees/RUNNER-SNAPSHOT-DEBT-codex
previous_status: in_progress
blocker: packaged_ac1_QtGui_DLL_import_failure
integration_commit: null
---

# M2-RUNNER-SNAPSHOT-DEBT：runner 快照债务

2026-10-08 用户明确授权 Codex 认领并实施；TaskStatus=in_progress，
ExecutionState=ACTIVE。Codex 已核对分配工作区、固定release与纯治理追加差量。非作者 Reviewer=DeepSeek Harness，
Integrator=Codex；作者不得自己批准实现。唯一 Active Task 为本 Task。

## 来源、实际证据与冻结目标

- doc/STATUS.md 的 GC-2 集成 checkpoint；GC-2 done@cea610ed，祖先关系实测成立。
- verification/M2-DERIVED-GC-2/g1-g7-matrix.md §G6，raw/dev-runner-m2rc2.log，
  raw/packaged-ac5-run/tenth-round-build-and-run.log、build-chain.md。
- packaging/m2ac5/run_clean_start_e2e.py:504，CS-L1-packaged-core-ping 仍断言
  protocol_version={major:1,minor:3}；src/bootstrap/core_service.py:168 当前 minor=6。
- verification/M2-RC2/run_e2e.py:309 的 PRODUCTION_EXPECTED 仅9条；
  apps/desktop/src-tauri/src/main.rs:53 的 PRODUCTION_COMMANDS 当前15条。
  缺 list_region_revisions、restore_region_revision、rerender_page、
  resolve_page_resource、list_chapters、list_chapter_pages，按真实冻结顺序核对。

只修复这两处验收期望及必要的注释、输出隔离、最小判别回归；
不修改产品以迎合过时 runner，不从被测回包动态生成期望以掩盖漂移。
先复用已有常量/断言模式，不建通用 registry、快照框架或新依赖。
minor-3 请求若原意为兼容测试，保留并说明；严格核对服务端声明 minor=6，
不把向后兼容请求误判成产品 wire 变更。probe 7条及场景覆盖保持冻结。

旧 FAIL 历史原文不可改写。只有本 Task 新 fixed-head 验收通过、非作者 Review
和 Codex 集成后检查闭合，才在当前状态登记这两个债务闭合；不追认旧 FAIL 为 PASS，
不扩大成干净机/全产品发布批准，不改变 GC-2 G7 分发迁移阻断边界。

## Acceptance Criteria（本轮实际结果见末尾/Handoff）

- [x] AC1 两处漂移在固定 base 上可复核；旧失败、当前契约/代码、期望差量有证据。
- [x] AC2 CS-L1 严格核对当前协议1.6；生产命令完整15条且顺序/内容与冻结面相符，
      probe7条及 fail-closed 行为不变。不得放宽成长度/包含关系/接受任意 minor。
- [x] AC3 最小判别检查：旧minor/缺命令/额外命令/错误顺序或probe混入仍失败；
      正确期望通过；对比独立冻结来源，不能将实现原样复制成无判别测试。
- [ ] AC4 真实dev M2-RC2 runner probe/production全Gate通过，真实packaged m2ac5
      全Gate通过含CS-L1；fresh构建与固定代码head/installer SHA256/执行日志相互绑定。
      依赖缺失记BLOCKED/NOT_RUN，不使用旧产品PASS替代本次验收。
- [x] AC5 旧报告/日志/冻结probe原字节保持，运行输出只入本Task隔离目录；无生产/
      wire/Schema/依赖差量；语法、diff检查和受影响测试通过。
- [ ] AC6 代码head、日志、Handoff固定后真实DSH非作者Review；条件闭合，Codex集成
      后受影响检查才done。作者不得自己批准，产品测试未跑不伪造PASS。

## allowed_paths

- packaging/m2ac5/run_clean_start_e2e.py
- verification/M2-RC2/run_e2e.py
  （以上仅快照/相关说明/为保护历史证据所需的输出与自有lab隔离参数；不改场景阈值）
- verification/M2-RUNNER-SNAPSHOT-DEBT/**（最小可运行判别检查、计划、checkpoint、日志）
- doc/tasks/M2-RUNNER-SNAPSHOT-DEBT.md
- doc/handoffs/M2-RUNNER-SNAPSHOT-DEBT-*.md
- doc/reviews/M2-RUNNER-SNAPSHOT-DEBT-*.md（只收非作者原始报告）
- Codex治理：doc/REBASELINE_PLAN.md、doc/STATUS.md、doc/00_INDEX.md、doc/tasks/README.md

共享接口/Schema/依赖授权：无。read-only 来源包括当前契约、Core、Rust命令表、
既有测试、打包spec/build scripts、GC-2证据；不允许改产品常量来让runner通过。

## 禁止与停止条件

禁止修改src/**、apps/**、tests/**、依赖、Schema、公共IPC/wire/ACL、GC语义、
probe集合、打包spec/build/install/deploy流程及Legacy；禁止修改历史报告/raw/probe，
禁止覆盖用户/其他Agent文件、源文件或Managed Copy；不push/部署/reset/clean/stash。
允许在自有隔离lab安装和运行测试installer，不属于产品部署。
fresh构建仅写本Task checkout 的ignored target，runner输出不得落旧tracked raw。
如需范围外修复、无法建立输出隔离/可信构建绑定，先BLOCKED交Codex冻结新范围。

## 验证计划（planned；本次释放不执行产品验收）

PowerShell；Python=G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe；
packager=G:/CODEX/New Manga.task-envs/m2ac5-build/Scripts/python.exe；
cargo=C:/Users/49745/.cargo/bin/cargo.exe。开始时实测解释器/依赖/WebView2，
不能把原任务环境记录当本轮已通过。

~~~powershell
Set-Location 'G:/CODEX/New Manga.worktrees/RUNNER-SNAPSHOT-DEBT-codex'
git status --short --branch
git rev-parse HEAD
git rev-parse --path-format=absolute --git-common-dir
& 'G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe' verification/M2-RC2/run_e2e.py
powershell -NoProfile -File packaging/m2ac5/build_sidecar.ps1 -Force
# 在 apps/desktop 目录执行既有构建命令：
npx --yes @tauri-apps/cli@2 build
# 回任务根目录，用本次实际生成的installer（不猜旧路径）：
& 'G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe' packaging/m2ac5/run_clean_start_e2e.py --installer '<本次构建的实际installer路径>'
git diff --check
~~~

上面runner命令在实施前先完成自有output/lab隔离；若增加输出参数，记录实际参数。
拟议最小检查 verification/M2-RUNNER-SNAPSHOT-DEBT/check_snapshots.py 在实现阶段创建，
无现成实现，不声明已PASS。语法检查采用内存compile或自有缓存避免污染历史目录。
每份日志记shell/解释器/命令/HEAD/EXIT/场景总数/PASS/FAIL/skip及原因；
打包日志还需sidecar来源head、installer SHA256与gate产物互证。
本地host simulation不等于真正干净Windows机；未验证的分发边界继续登记。

## 恢复、交付与下一步

base=968c8f34601b72667831f1fd15bb20cd2c8f3cb7；实际branch/worktree见frontmatter。
释放commit后的恢复点由主仓库追加到verification/M2-RUNNER-SNAPSHOT-DEBT/release.md，
避免自引用hash。Owner开始前核对ready、固定release/head、common-dir与clean。

交付fixed代码head、verification/M2-RUNNER-SNAPSHOT-DEBT/证据、
doc/handoffs/M2-RUNNER-SNAPSHOT-DEBT-<head>.md；下一接收者真实DeepSeek Harness，
随后Codex集成。非作者Review尚未派发，产品/runner测试NOT_RUN。

可直接给Codex：在上述分配worktree核对release.md的实际HEAD，认领in_progress，
按本Task冻结范围修复两处runner快照并做最小判别检查；保留历史FAIL，fresh构建并真实
复跑dev+packaged Gate，保存独立证据和固定代码head/Handoff；交真实DSH非作者审核，
批准与条件闭合后由Codex集成验证，最后更新done。不可改产品或弱化Gate。

## 2026-10-08 实施结果与阻塞（Codex）

代码head=d1c279db45904c6009dbc696d95a0b4a63ebd837；含日志harness固定head=
cfb5d2eecc4d8ab7a3159cdbb1d5812547bb5cd2。两处快照、output-dir、自有lab已实现。
12个实际谓词检查PASS，frontend构建PASS；dev全Gate10/10、probe13/13 PASS。
fresh PyInstaller成功但PowerShell5 weights复制EXIT1（Get-FileHash不可用）；
PowerShell7按既有脚本恢复hash校验复制EXIT0；fresh NSIS EXIT0。
packaged CS-L1 PASS，但AC1 run1的acceptance_bridge.exe导入QtGui时DLL失败，
未生成结果且返回1，精确run_app退出时间线UNKNOWN，完整Gate FAIL/EXIT1。不是旧minor3快照失败，不宣称新AC4 PASS。

TaskStatus=blocked，previous_status=in_progress，ExecutionState=CHECKPOINTED。
禁止范围外spec/依赖/acceptance_bridge修复；主线不集成两处runner实现，
先保存证据并交真实非作者DSH审查。解除条件：单独授权的打包/入口诊断或修复Task，
固定head新构建后AC1及完整packaged Gate通过，再回本Task完成AC4/AC6。
AC1/AC2/AC3/AC5已执行证据见Handoff；AC4=FAIL/BLOCKED、AC6=PENDING。
旧日志/报告原字节保留；源src/apps/tests/依赖没有提交差量。

packaged实际结果=20 PASS / 1 FAIL；AC1 run1失败后的run2/restart/saved/reader/export五项NOT_RUN，不计PASS。详细计数见result-summary.json。

## DSH r1 有界修正（Task仍blocked）

reviewed_head=7556cb2d；DSH真实CLI EXIT0，session=session-dbe4f574-2377-4302-885a-1f4cba2ae9f9，
原始报告doc/reviews/M2-RUNNER-SNAPSHOT-DEBT-7556cb2d-dsh-r1.md。
代码approve_with_conditions（0P0/P1/P2），整个Task blocked，不豁免AC4。
C1落实际git diff与head绑定；C2最小检查改独立固定15条oracle，加capability/error/status负向；
C3只改usage说明/PS7 skip记录，并把未落时间线明确UNKNOWN；C4清理DSH自己误写的scratch。
原报告出现F-17/F-07编号载体不完整，以及完整21/21表述，原文不改；应验收26个完整场景，
当前21个已报告=20PASS+1FAIL，后续5项NOT_RUN，不以21/21替代完整Gate。
下一固定head需真实DSH复核；包装DLL诊断/修复候选未释放。
