---
id: M2-PACKAGED-AC1-ICU-ISOLATION-FIX
title: 安装态 Qt 与 ICU78 依赖闭包隔离修复
kind: bugfix
status: changes_requested
approval: user_authorized_release_20261008
suggested_owner: Antigravity
owner: Antigravity
reviewer: DeepSeek Harness
integrator: Codex
depends_on: [M2-PACKAGED-AC1-DLL-DIAG, M2-DERIVED-GC-2]
base_commit: 5a72db9e3c5778ce4700b7d404250853e474c5de
branch: agent/antigravity/M2-PACKAGED-AC1-ICU-ISOLATION-FIX
worktree: G:/CODEX/New Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity
allocated_head: 5a72db9e3c5778ce4700b7d404250853e474c5de
start_head: df824182e813fc6d9045872da51d263f28db87f0
implementation_head: aa099f2a013408bf53c3466ab8361bc028289743
evidence_head: 46f50a097d25a1893dd1f43b0a38479952242161
reviewed_head: aa099f2a013408bf53c3466ab8361bc028289743
review_report: ../../verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/review-dsh-r1.md
execution_state: CHECKPOINTED
integration_commit: null
allowed_paths:
  - packaging/m2ac5/**
  - doc/tasks/M2-PACKAGED-AC1-ICU-ISOLATION-FIX.md
  - verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/**
  - doc/handoffs/M2-PACKAGED-AC1-ICU-ISOLATION-FIX-*.md
---

# M2-PACKAGED-AC1-ICU-ISOLATION-FIX：安装态 ICU 隔离修复

## 来源与目标

用户于2026-10-08单独释放；本轮仅治理释放、分配和同步，未派发/开工。
[诊断报告](../../verification/M2-PACKAGED-AC1-DLL-DIAG/REPORT.md)固定被审head=229c6c371d34234b65bbdd67fff73f341c60930f，
[Codex r3](../reviews/M2-PACKAGED-AC1-DLL-DIAG-229c6c37-codex-r3.md) approved，诊断集成4431754845fc25795058534f21656705ef701cd6。
证据仅适用于固定产物/本机：包内icuuc.dll导出ICU78后缀符号，缺Qt6Core普通导入所需20个无后缀符号，
同名遮蔽系统ICU；native加载127、System32加载对照、同hash bridge自有副本改名对照支持因果。
原Gate的Win32错误仍UNKNOWN；其它ICU78消费者尚UNKNOWN；不能把副本对照直接当发行修复。
目标：新架构Windows/Tauri安装态Qt启动正常，同时保持实际ICU78消费者可用。先追踪现有打包/加载链，再做最小修复。
诊断准备见[NEXT_IMPLEMENTATION](../../verification/M2-PACKAGED-AC1-DLL-DIAG/NEXT_IMPLEMENTATION.md)。

## Acceptance Criteria

- [ ] AC-1：列出实际5入口产物的ICU78消费者、普通导入/导出、同名解析和加载闭包矩阵；每项证据或UNKNOWN，未知不得靠全局移除解决。
- [ ] AC-2：仅打包范围内最小修复；新鲜产物在隔离/purged PATH下Qt6Core/Qt6Gui、acceptance_bridge真实加载成功，ICU78实际消费者仍正常；留原失败与修复后对照。
- [ ] AC-3：fresh Sidecar五入口和NSIS构建成功，实际source_head、命令/解释器、产物hash/大小、EXIT/耗时绑定。不能用skip-existing替代fresh构建。
- [ ] AC-4：冻结dev完整10项Gate及13项probe通过；15 production commands、7 probe commands严格核对，不降低阈值。
- [ ] AC-5：新安装副本完整26项packaged Gate全PASS；CS-L1响应minor1.6、请求minor3兼容；两轮AC1完成、重启新PID、summary/reader恢复、PNG digest一致。旧FAIL不回填。
- [ ] AC-6：用户源文件、人工修改、Lock、current/pinned Revision、Managed Copy及恢复能力保护；只写自有隔离fixture/输出，运行后无自身sidecar残留。
- [ ] AC-7：固定实现head、逐项结果及Handoff齐全；真实非作者DSH approved后由Codex集成并验证，才进入done。

## DSH Review r1：changes_requested

固定审查输入：base=5a72db9e3c5778ce4700b7d404250853e474c5de、reviewed_head=aa099f2a013408bf53c3466ab8361bc028289743、证据/Handoff checkpoint=46f50a097d25a1893dd1f43b0a38479952242161。完整报告：[review-dsh-r1.md](../../verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/review-dsh-r1.md)。

- P1 R-001：26项 packaged Gate JSON 的 installer SHA=a17a9708…，与交付 fingerprint SHA=f76b91d6… 不同；后者无完整 Gate 结果日志。
- P1 R-002：构建/Gate 日志记录 HEAD=df824182，修复当时未提交；fingerprint 声明 source_head=aa099f2a，输入字节相同无法由证据确认。
- P2 R-003/R-004：412 PE 扫描没有脚本/原始输出，closure-matrix.json 引用断链；spec 按名称/深度全局删除 ICU，不能证明保留未知消费者。
- P3 R-005/R-006/R-007：spec 断言不可达且文档名称不符；报告数字/CS-E2 hash 比对表述与日志/runner不符；System32 ICU 运行期依赖及OS基线未记录。

Decision=changes_requested；AC-5 对交付 installer 为 BLOCKED，AC-3 来源绑定 FAIL，AC-1 关键扫描 artefact NOT_RUN。现有 PASS 只适用于提交内各自记录的那次运行，DSH未现场重跑。禁止集成或标记Task done；修订仍受原 allowed_paths 限制。


## 允许修改范围

Owner仅上述allowed_paths。生产修改仅packaging/m2ac5/**，不更改已冻结验收口径；本次不借机合并runner debt。
允许读取src/apps/tests相关调用链，使用既有工具/依赖；构建可生成自己worktree内Git ignored产物、隔离模型缓存、安装fixture和lab，不修改跟踪的apps文件。
验证runner复用固定head=2af6b71aa06979b822e543b221aaf3a2d5f01abe的
packaging/m2ac5/run_clean_start_e2e.py、verification/M2-RC2/run_e2e.py：
精确字节副本放本Task verification根（相同深度），记录来源/SHA256、实测REPO定位；新--output-dir仅本Task/自有lab。
必要既有probe fixture只读复用；任何定位不适配先记录并交Codex，不改验收逻辑/场景/阈值。
Codex可维护Plan/STATUS/索引和释放记录；DSH可写doc/reviews/M2-PACKAGED-AC1-ICU-ISOLATION-FIX-*.md及自己的审查证据。

## 禁止范围

禁止跟踪的src/**、apps/**、tests/**、其它verification历史证据、Schema/共享IPC/ACL、依赖清单/版本变更；禁止Legacy修复。
禁止改系统PATH/环境、System32、既有安装目录/用户数据、全局删除ICU；不部署、不推送、不合并main/master，不reset/clean/stash他人工作区。
共享启动代码或依赖升级若不可避免，暂停越界部分、在Task记录blocked原因，交Codex/用户重新冻结；不得先改再补授权。
只使用现成关联/构建机制，不新增通用registry或插件抽象。

## 测试要求

以下均planned / NOT_RUN；本轮不执行生产测试。

| 场景 | planned命令或步骤 | 环境/判据 | 结果 |
|---|---|---|---|
| 构建 | pwsh -NoProfile -File packaging/m2ac5/build_sidecar.ps1 -Force | Owner独立worktree；fresh五入口，完整EXIT/log | NOT_RUN |
| NSIS | 在Owner apps/desktop执行既有Tauri build命令（先核对项目入口与依赖） | 既有锁定依赖；新installer/source_head/hash绑定 | NOT_RUN |
| 闭包 | 本Task最小普通PE导入/导出与实际loader/bridge、ICU78消费者检查 | 自有副本；pefile完整导出计数校验，不能复用8192截断误报 | NOT_RUN |
| dev | 固定runner副本 --exe <本次exe> --skip-build --output-dir <本Task新dev输出> | 完整10项+13 probe，不用主线旧9项快照 | NOT_RUN |
| packaged | 固定runner副本 --installer <本次installer> --output-dir <本Task新packaged输出> | 完整26场景，不用主线旧minor3响应快照 | NOT_RUN |
| 范围 | git status --short --branch；git rev-parse --path-format=absolute --git-common-dir；git rev-parse HEAD；git diff --check；git diff --name-only <base> HEAD | 每次恢复/交付实测，越界为零 | NOT_RUN |

日志落verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/**：命令、shell/解释器、HEAD、EXIT、耗时、PASS/FAIL/NOT_RUN/skip分列及原因；外层EXIT0不替代场景结果。
禁止把规划或旧诊断通过当产品PASS，任何未跑Gate明确BLOCKED/NOT_RUN。

## 依赖、风险与阻塞

硬依赖均已集成且为base祖先：诊断done@4431754845fc25795058534f21656705ef701cd6；
GC-2 done@cea610ed3f3349f1d76361d151815445e991f7d7（以Plan/集成证据为准，历史Task frontmatter integration_commit仍null不单独定性）。
M2-RUNNER-SNAPSHOT-DEBT是关联blocked Task，不是假定done的依赖；其已批准runner代码仅验证复用，不自动集成/关闭。
原构建source_head=cfb5d2eecc4d8ab7a3159cdbb1d5812547bb5cd2；原installer SHA256=1cecca95d25439fca682cbe4336123d3b3352db229dd58c4e7d724b4d6c6ccb8，589904619 bytes。
原packaged20PASS/1FAIL/5NOT_RUN；修复须全新完整26项，不能以启动对照替代。
候选base2c8e3e5902c1fbc9d1ad228ec4fc4fe491b7d41e至实际base只有Plan/STATUS和诊断准备/checkpoint文档差量。
当前阻塞为DSH r1的R-001/R-002 P1及R-003/R-004；消费者需求仍需以可复核artefact澄清。超范围需求停止并交Codex/用户裁决。

## 交付与运行记录

- Handoff：Owner checkpoint=46f50a097d25a1893dd1f43b0a38479952242161，位于指定 Antigravity worktree；引用代码head=aa099f2a013408bf53c3466ab8361bc028289743。
- Review：真实外部 DSH r1=changes_requested；完整报告见 [review-dsh-r1.md](../../verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/review-dsh-r1.md)，session=session-4655cd71-226a-4eec-91a7-78dad7e84fab。
- 实际产品测试：Owner提交内记录 Sidecar/NSIS EXIT 0、Dev 10/10+13/13、packaged 26/26；但 packaged JSON installer hash 与 fingerprint 不同，构建时 HEAD 与 source_head 不一致；不得据此宣称交付产物 Gate 完成。DSH未现场重跑。
- 2026-10-08 Codex复核：Owner分支仍在 46f50a097d25a1893dd1f43b0a38479952242161，clean、common-dir正确；下一修订须从该实际HEAD继续，原 Task base保持不变。
- [实际释放恢复点与完整Owner指令](../../verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/release.md)：由Codex在release提交后追加；Owner读取主仓同路径。
- 当前 changes_requested / CHECKPOINTED；未集成。由Antigravity在同一Task与分支修订，先固定新代码commit，再重建并验证；不得使用未提交输入绑定产物。
- 集成后下一步回M2-RUNNER-SNAPSHOT-DEBT完整fresh验收/独立审查/集成，不能自动把原blocked变done。
