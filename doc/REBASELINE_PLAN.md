# Project Rebaseline Plan — 唯一 DAG

运行以 [STATUS](STATUS.md) 为准；目标架构 [AD-001](AD-001_TARGET_DESKTOP_ARCHITECTURE.md)。

## 当前 DAG

|节点/目标|依赖|状态|
|---|---|---|
|GIT-CLEAN-RUST-CAPACITY-DESIGN-1|—|ready（ZCode 仅设计；base1829a38；Reviewer=Antigravity）|
|GIT-CLEAN-RUST-ISOLATION-1|—|in_review（1829a38；并发双过，饱和0/32；DSH r2 blocked；Reviewer=Antigravity）|
|GIT-CLEAN-CORE-ENV-2|—|proposed（V2–V5与无ACL写入环境未定义）|
|GIT-CLEAN-PUBLICATION-DIAG-1|—|approved（DSH r1；仅fed诊断；不集成/不done）|
|GIT-CLEAN-PUBLICATION-1|—|in_review（root e34a90d00；DSH r1 blocked；push-gate approved；已推新分支）|
|NEW-MANGA-V1-FULL-AUDIT|—|blocked（素材不传播；resume=in_progress，其他审计AC未完成）|
|GOV-RESIDUAL-RUNTIME-IDENTITY-1|GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1|done（r2 approved 8e31aaa1d；集成同点；只读取证，7项错误与保护不变）|
|GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1|GOV-RESIDUAL-RUNTIME-IDENTITY-1|done（Antigravity approved 3264e0b61；7错→0，保护根+APPDATA 三根）|
|GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1|GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1|done（R2 b8c51b038；集成457485207；正式12→7，无清理）|
|GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1|GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1、GOV-BROAD-ROOT-PRESERVATION-IMPL-1|done（R2 e6f400101；集成20dff6381；仅设计，正式12不变）|
|GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1|GOV-BROAD-ROOT-PRESERVATION-IMPL-1|done（R2 49942377b；集成fec50696a；研究，正式12不变）|
|GOV-BROAD-ROOT-PRESERVATION-IMPL-1|GOV-BROAD-ROOT-PRESERVATION-DESIGN-1|done（R4 d5d21ff9f；集成a3bba87ce；正式24→12，不清理）|
|GOV-BROAD-ROOT-PRESERVATION-DESIGN-1|GOV-RESIDUAL-24-DECISION-1|done（R3 232e3a589；整体保护设计，未实现）|
|GOV-RESIDUAL-24-DECISION-1|GOV-NONRESOURCE-MANIFEST-FORMAT-1|done（d1ad7e525；只读汇总；广域根裁决见设计Task）|
|GOV-NONRESOURCE-MANIFEST-FORMAT-1|GOV-NDJSON-EXCEPTION-CONFIG-1|done（独审2573375dc；正式30→24，保护+2）|
|GOV-NDJSON-EXCEPTION-CONFIG-1|GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1、GOV-NDJSON-NONDECL-IDENTITY-1|done（独审85a393dc4；集成9d21f8fb8；正式32→30）|
|GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1|GOV-NDJSON-NONDECL-IDENTITY-1|done（edbd1a492；51pin实际保护恢复）|
|GOV-NDJSON-NONDECL-IDENTITY-1|GOV-DECLARATION-RESIDUAL-32-AUDIT-1|done（54cfbadad；身份研究，不登记例外）|
|GOV-DECLARATION-RESIDUAL-32-AUDIT-1|GOV-PATH-HEADER-COMPAT-1|done（927e06f8b；只读取证，原32错误保留）|
|GOV-PATH-HEADER-COMPAT-1|WORKSPACE-DECLARATION-REMEDIATION-1|done（9cae94142；单一固定别名，无资源处置授权）|
|GIT-MAINLINE-CONVERGENCE-1|—|done（r3 approved 6997733bf；refs/heads 仅 main、worktree 1、21 条归档、2.6GiB 可恢复）|
|V1-RELEASE-SIGNING-1|P09-MANAGED-READ-ROOT-TRUST-1、WORKSPACE-CLEANUP-TOOL-HARDENING-1|in_review（接受未签名；待发布签核；当前无执行）|
|GOV-DIRECTORY-CLEANUP-1|—|done（r1 approved 40acf35b7；五根 171 项，2 项归档后删除、净释放 426.3 MiB）|
|SETTINGS-OPEN-A-1|P15、P15-C1|done（批次 A：OCR/翻译参数/图片修复/排版样式；r1 changes_requested → r2 approved，集成 6a303a9）|
|SETTINGS-OPEN-B-1|SETTINGS-OPEN-A-1|done（批次 B-1：模型/GPU + 任务/并发；review r1/r2/r3 与 follow-up approved，集成 b521ad27）|
|SETTINGS-OPEN-B-2|SETTINGS-OPEN-B-1|done（批次 B-2：缓存/Revision 清理操作面；review approved，集成 0e2e623；GUI 烟测 PASS）|
|SETTINGS-OPEN-C-1-DESIGN|SETTINGS-OPEN-B-2|done（批次 C 契约设计：三节冻结 + 决策清单 D1–D11；用户裁决全部接受推荐值）|
|SETTINGS-OPEN-C-1-RECYCLE|SETTINGS-OPEN-C-1-DESIGN|done（回收站查看+清空；实现 `6d6c085..893c00fc`；独立 Review r1 changes_requested → r2 approved）|
|SETTINGS-OPEN-C-2-BACKUP|SETTINGS-OPEN-C-1-RECYCLE|done（`.nmbak` v1 + Core/Tauri/前端；Review r3 approved `657c18d4`）|
|SETTINGS-OPEN-C-3-PLUGIN|SETTINGS-OPEN-C-2-BACKUP|done（Plugin/Hooks 只读面；Review r2 approved `85128cd2`）|
|PLUGIN-RUNTIME-1|SETTINGS-OPEN-C-3-PLUGIN|done（本地插件运行时；用户 2026-10-23 授权 D1–D6；Review approved 2026-10-23，`992225d5`）|
|PLUGIN-RUNTIME-2|PLUGIN-RUNTIME-1|done（r3 approved 2ea97edd6；集成 eb5e821f3；111 passed；资源原位保留）|
|GUI-PLUGIN-SANDBOX-SMOKE-1|PLUGIN-RUNTIME-PACKAGED-PYTHON-1|done（手工 GUI 冒烟由 TOOL-SOFTWARE-SMOKE-1 替代；工具全量 PASS 24 项/23.6s）|
|PLUGIN-RUNTIME-PACKAGED-PYTHON-1|PLUGIN-RUNTIME-CAPABILITY-1|done（approved `a1f05450`；证据重钉 `6e3ce06f9`）|
|TOOL-SOFTWARE-SMOKE-1|PLUGIN-RUNTIME-PACKAGED-PYTHON-1|done（r2 approved `c680434ea`；分层软件检查工具；15 tests；证据 `7b2abfa00`）|
|PLUGIN-RUNTIME-CAPABILITY-1|PLUGIN-RUNTIME-SANDBOX-2|done（capability 接线：network 可强制；Review r1 approved `0d3bbe49`）|
|PLUGIN-RUNTIME-SANDBOX-2|PLUGIN-RUNTIME-SANDBOX-1|done（per-plugin AppContainer profile；Review r1 approved `127c5111`）|
|PLUGIN-RUNTIME-SANDBOX-1|PLUGIN-RUNTIME-1|done（OS 级插件沙箱；用户 2026-10-23 选择候选 1；Review r2 approved `41d7abeb`）|
|P07 / P21|P02 / P20+另授权|proposed（可选；未释放）|

READY 节点：GIT-CLEAN-RUST-CAPACITY-DESIGN-1。

2026-10-25 DSH 接任 Lead/Architect/Integrator（Codex 降为协作）。仅 ZCode 容量设计释放；Rust r2 与父审查 blocked，Core proposed。目标安全 push：仅干净快照分支，Gate 未过早不推；新 head 新 Appointment。

C-1/C-2/C-3 与插件 OS 级沙箱已完成，不再列为待授权候选。主线收敛已完成并通过独立审查；后续任何清理/删除仍需新的具体授权，不构成解除 r212 或五广域根保护。

## 终态依赖与限制

本 Plan 明确继承[冻结 DAG](../archive/history/2026-10-21/git-mainline-convergence/rebaseline-plan-before.md)中的其余节点状态、依赖 与限制；这是对原图的无损引用，不重开 Task、不增加 READY。完整源为 `fdca2057e:doc/REBASELINE_PLAN.md`，SHA-256 `1d2c83431273512787e58037260f1b27a2a0c3dab01e921e167fd6b51cf16ed7`。

- 已完成节点共 54 项（源图口径）；P09/P18/P19/P20 等限定关闭，未满足 Gate 不变。
- WORKSPACE-CONSOLIDATION-1：closed_with_limitations（r212），18 个受保护资源限制；不得清理/GC/prune。132 worktrees/93 branches 为历史快照。
- WORKSPACE-CLEANUP-TOOL-HARDENING-1：done（368c07809）；WORKSPACE-DECLARATION-REMEDIATION-1：done（bb7887442），残余错误保留 fail-closed；不因工具修复自动获得删除授权。
- P22 已集成；H1/P2-1/13 与 BC-AC5 PARTIAL 保留。无 Legacy 实施/诊断/修复释放。

当前治理主线 `main`；旧主线显式保留规则不变。远端仅允许用户授权的新分支快照 push，不push main。
