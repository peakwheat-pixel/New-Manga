# Project Rebaseline Plan

## 当前检查点：2026-10-10 P02 R7 exact-head Review CHANGES_REQUESTED；启动保持阻断

P02 仍是唯一 Active 产品验证 Task（`in_progress / ACTIVE`）；P01/P03/P08=`done`，P05=`done`（integration_commit=`bc2b690bc4f66d286bb8f16764269f6681c70b0d`）。P02 scope r1–r4、AC、Owner allowlist 与行为基线冻结；Owner=Antigravity、实现 Reviewer=DeepSeek Harness、Integrator=Codex。Stage A integration=`89413f45a601966eb40d7af7abea65cbdfc754b3`、Gate=`PASS`；hook/cache 静态闭包=`BLOCKED / NOT_VERIFIED`。R6 DSH exact-head Review=`APPROVED`；Smoke admission=`ADMITTED`，限一次尝试。R7 DSH exact-head Review 对 `ab3958e1270084d80f2edb228aebc6e463233602`=`CHANGES_REQUESTED`（P0/P1/P2/P3=`0/0/3/7`），报告见 [R7 response](../verification/P02/dsh-review-p02-smoke-prestart-r7.response.md)。

当前 pre-admission Stage-1=`PRESTART_STAGE_1_PASS`（16/16）；Feature `InstallState=1`，WSB identity/list 与宿主资源阈值通过。固定 non-linked clone `G:\CODEX\P02-scratch-build-source` 已 detached checkout `7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a`，private Git dir、空 remote、无 alternates、object hardlinks `3/3` count=1、clean porcelain 与 source/EOL pins 均通过。R2 递归 manifest 覆盖 r3 Smoke XML 精确 11 个映射；Stage-1 12-root inventory 另含 2 个 Build-only Git 根，未纳入此 manifest。204,419 records：50,356 文件全量哈希、33 个工具链选样、138,947 个文件内容未计算；内部摘要/排序/计数复核=`PASS`，原始 capture process exit 未记录。root protection=`203/203 MATCH`，live root=`main@ceffb7479cb1f79bd3b620afdaf6e9eaa0ae6d50`，candidate overlap=`0`。

R2 admission item 5 的不可能时序已由 R3 erratum 澄清；R7 Review=`CHANGES_REQUESTED`，尤其尚无可执行的 HostFolder manifest 启动前 compare/recheck mode（F-02）。未运行 `wsb start`；Smoke=`NOT_RUN`，完整 preflight=`BLOCKED / INCOMPLETE`，Build Gate=`BLOCKED`，build=`NOT_AUTHORIZED / NOT_RUN`，AC1–AC7=`BLOCKED / NOT_RUN`，Hard Build Barrier=`EFFECTIVE`。见 [R7 review checkpoint](../verification/P02/codex-checkpoint-p02-smoke-prestart-r7-review.md)。P04 继续 proposed；P02 Build Gate 与 Barrier 解除前不释放 P04 或运行 Cargo。

**前次检查点快照（2026-10-09；已由上方 2026-10-10 checkpoint 取代）：**P02 当时为唯一 Active Task（in_progress / ACTIVE），P01=done；scope r1–r4、AC、Owner allowlist 与行为基线保持冻结，不重冻结。Owner Stage A integration_commit=89413f45a601966eb40d7af7abea65cbdfc754b3，tree=f1063c981b8f4164f51248f92b7825fc205dd07d，parent=38959ba99b84f771aba7010b53b9b47ecdc75488。DSH 固定 r8 正式 Review=approved（仅 Stage A），P0/P1/P2/P3=0/0/0/1，open=1：R8-01 为非阻断 P3，Codex 已按 Review 建议登记延期；R7-01 closed，R7-02 deferred (P3)，R6-01..04 closed。Codex r8 exact-head 命令级复核与 Stage A Integration Gate=PASS。隔离 scratch-build 方案与输出边界已独立审查通过，但 Python/Torch/Hugging Face 缓存值、实际 PyInstaller hook/递归导入与子进程写入闭包仍未被证明；Build Gate=`BLOCKED`，build=`NOT_AUTHORIZED / NOT_RUN`，Hard Build Barrier 有效。P02 仍 in_progress，AC1–AC6 保持 BLOCKED。当时下一步只做只读 hook/cache 闭包核验；该项已于 2026-10-09 完成并记录为 BLOCKED / NOT_VERIFIED，后续隔离方案与宿主预检见上方当前 checkpoint。见 [r8 DSH Review](../verification/P02/implementation-stage-a-r8-dsh-review.stdout.md)、[r8 exact-head 复核](../verification/P02/r8-codex-exact-head-review.md)、[Scratch Build Gate](../verification/P02/codex-scratch-build-gate.md) 与 [最新恢复点](../verification/P02/codex-checkpoint-after-scratch-build-gate.md)。本轮未运行产品构建、Vitest、GUI 或真实 WebView。

**上次快照（r6）：P02行为验证基线=`241ff3b70b6fc0490ea238efd486cc707f849031`；Owner转移集成commit=`3f4d16633a18a9ab7aea5b08b67653cd3f6bf8ff`；P08/P03/P01=done、P02=in_progress / ACTIVE；P系列21项：done 3、in_progress 1、proposed 17、ready 0。P01 integration=M0=`13e66ec5bf9a2fc59f4e6c5623feb0bde22884c8`。P02范围r1–r4保持冻结；Owner=Antigravity、Reviewer=DeepSeek Harness、Integrator=Codex。固定Stage A r6=`38672473f93971a4681aef682e5635e64b0bd896` / tree=`2aa967bbf961a0e9e58dd3e1489d74635491e28f` 的DSH正式Review=`approved_with_conditions`（仅Stage A），P0/P1/P2/P3=`0/0/0/4`、open=4；R5-01..06闭合，R6-01..04为P3条件，报告见[`r6 DSH Review`](../verification/P02/implementation-stage-a-r6-dsh-review.md)与[`r6 Codex exact-head Review`](../verification/P02/r6-codex-exact-head-review.md)。r6未集成、`integration_commit: null`；r7已在原Antigravity会话按冻结allowlist修订。当前恢复见[`P02 r6 Review后checkpoint`](../verification/P02/codex-checkpoint-after-r6-dsh-review.md)与[`P02 RESUME`](../verification/P02/RESUME.md)。P03 integration=`552464238a69ad2cea63cff18abe98f412dbae87`；R1/R2/C8历史状态与R2/SYNTH `NOT_VERIFIED`不变。

## 历史检查点：2026-10-09 P02 真实 Workbench WebView 验证 / r6 条件批准

P02真实/Mock边界、AC、Owner allowlist与退出判据由scope r1–r4冻结并释放，不重做。Owner转移已集成于`main` commit `3f4d16633a18a9ab7aea5b08b67653cd3f6bf8ff`。固定Owner Stage A r6=`38672473f93971a4681aef682e5635e64b0bd896` / tree=`2aa967bbf961a0e9e58dd3e1489d74635491e28f`；DSH正式Review=`approved_with_conditions`（仅Stage A），P0/P1/P2/P3=`0/0/0/4`、open=4，R5-01..06闭合，4项新P3条件见[`r6 DSH Review`](../verification/P02/implementation-stage-a-r6-dsh-review.md)。Codex exact replay的TS、ProbeOnly、Full、diff-check均EXIT=0，五项finalized hash全匹配；失败注入也验证 finalizer EXIT=42 与 PowerShell 5.1 异常记录。r6不集成，`integration_commit: null`；r7已在原Antigravity会话按冻结allowlist定向修订R6-01..04：cwd无关的tsc定位、TS machine gate表达真实执行、self-check走生产逻辑、Scenario C如实标为执行/静态。PRE-01..03 exact runner通过不代表运行时AC通过；AC1–AC6保持BLOCKED。Cargo/Tauri/sidecar build、Vitest、真实WebView与产品GUI均未运行。详见[`r6 Review后checkpoint`](../verification/P02/codex-checkpoint-after-r6-dsh-review.md)、[`r6 Codex exact-head复核`](../verification/P02/r6-codex-exact-head-review.md)、[`r6 DSH报告`](../verification/P02/implementation-stage-a-r6-dsh-review.md)及[P02 RESUME](../verification/P02/RESUME.md)。



## 历史检查点：2026-10-09 P02 Owner 转移 / DSH r8 治理 Review 条件批准

DSH r8 固定审查候选 55be5dab7b6d7bebf94c9ad6524f57c023616249，decision=approved_with_conditions，findings P0/P1/P2/P3=0/0/0/2。Codex 已补齐 DSH shell 环境无法执行的 tree、差量、Task digest 与路线 Gate 实测；r8 两个 P3 的精确 head/tree 登记及动态恢复指针已在治理 checkpoint 处置。r7 C-2 对 f18720a 审查版本的首次同步与manifest复核已通过；后续恢复文件更新后须按最新Gate log hash/status再次确认最终版本，快进仍受该条件约束。Live main 快进前 Owner 仍为 ZCode，候选 Task 保持 ready / IDLE。产品实现和产品验收未运行；详见 [P02 RESUME](../verification/P02/RESUME.md) 与 [owner-transfer Gate log](../verification/P02/owner-transfer-r7-gate.log)。

## 历史检查点：2026-10-09 P02 Owner 故障转移 / r6 Review approved；集成于3f4d1663

P02 owner amendment candidate=`codex/P02-owner-amendment@4458b35051dd847ceadad11c332a7e2de3b49512`，base=`4b54f304dc201d129d4ba1c62d0368252e6301b1`。DSH r6 已对该 fixed head 作出有限 `approved`，session=`session-12ea0417-49fa-43ae-9a17-77d60f2bb033`；F-01 要求在 Codex 集成提交同步 Plan/Index 的 Owner 记录，F-02 要求 Codex 复算 Task SHA。报告/prompt/exit/mount 与 Codex 复算正在写入集成证据。Owner=Antigravity、branch=`agent/antigravity/P02-real-webview-harness`、目标 worktree=`G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity`；worktree 尚未创建，Task 仍 `ready / IDLE`，AC1–AC7、构建、Vitest与真实 WebView均 `NOT_RUN`。r2 产品契约及 r4 Codex-only路线校验器治理批准不变。

## 2026-10-09 P01 D3 Review、Codex closeout与main集成完成 / DONE

P01已集成完成：Owner/Integrator=Codex，非作者Reviewer=Antigravity。base=`826bea12a132c5af2ac0cd1244d00e9170093c71`；C9 fixed head=`7645577ab374b581eb7081fd57675c32793249f5`和最终D3=`51bc01fec2652c0e2bc39bb119f8dd7ca3c294cb`均正式approved，D3 tree=`69d9d655cf9aecb1581cf4d3c86c500f265b61ab`、findings=0，report SHA-256=`749c20db44938a5cca9e18995923465e42aba07a960303387483b67ff58fc1ee`。C1=`c28a9e49e684105eebc7f62555086d6cccad75a4` fixed-head Integration Gate通过，D1=`322b757933dce0e7333fc495706cc0d424cccaad`；D5=`cf11183d8185b1b0f78396bd0976b1bbdb42bef0` / tree=`57e275d138e537a62c3f2e9b1ecbef7c1e275e6f`的92-path Codex closeout Gate=`PASS_PRE_FF`。随后M0=`13e66ec5bf9a2fc59f4e6c5623feb0bde22884c8`已fast-forward，D7/root `main@b7ad98b29196e9859cbfbfe187e6822569f79367`的post-FF复核=`PASS`：base..HEAD 92 paths、越界/产品/测试/build路径0；路线validator、base/M0祖先关系、`git diff --check`均通过；root原24项manifest逐项匹配、与差量交集0。C9 P3 `OBS-C9-01`及旧DSH分配文字已处置。C8 `ENV-01`截断事实保留，未补造文本。R2/SYNTH carrier仍`NOT_VERIFIED`，不改来源Task状态或产品裁决；产品测试/build/GUI均`NOT_RUN`（本Task无产品代码差量）。截至该 P01 closeout checkpoint，P02 当时仍为 proposed；后续已在本 Plan 顶部的 P02 release checkpoint 中正式释放。

## 历史检查点：2026-10-09 P01 DSH R2 BLOCKED（由C8 in_review取代）

截至C7历史checkpoint：P01 AC1–AC6与允许的三处来源字段更正已完成，delivery=`9b12493616326af9cdd50a055282426c72516a5a`。DSH R1对`6f24006c21281df485375674d20a1d3b7b48ca63`的`blocked` findings已在P01允许路径修订；C5=`e95ebbf56c9747ad97f2d4e9fa9d1bb10f128364` Codex fixed-head Gate PASS。DSH R2对C6=`3e67d53be6363e0eaabbd1ce038c226b82b8a494`返回`blocked`，报告与C6日志已纳入C7 checkpoint；该状态由C8 `in_review`取代。R1/R2原始报告及DSH `NOT_RUN`事实保留，产品测试仍`NOT_RUN`。

## 历史记录：2026-10-09 P01 正式启动 / IN_PROGRESS

Task=`[P01](tasks/P01.md)`，`status=in_progress`；Owner=Codex，非作者Reviewer=DeepSeek Harness，Integrator=Codex。Task base=`826bea12a132c5af2ac0cd1244d00e9170093c71`；branch=`agent/codex/P01-metadata-audit`；worktree=`G:/CODEX/New Manga.worktrees/P01-metadata-audit-codex`；依赖为空。Reality Check=`RESUME_SAFE`，启动HEAD=`714138de3da06013e3ea35395e0c11b3d15fc371`，P01 worktree clean；root 24项既有dirty/untracked未触碰。当前只核对 GC2/DETECT3 commit 元数据和 R2/SYNTH 独立 Review 载体；只在 Git对象、提交链及交付证据充分时修正来源Task允许的三类frontmatter元数据：GC2集成SHA、DETECT3集成SHA、SYNTH重复integration_commit；禁止改动来源Task状态或产品裁决。R2 challenge 空集/T2 release 保留给用户；缺失的 Review carrier 如实记`NOT_VERIFIED`，不补造批准，不把来源 Task 改`done`。当前恢复指令见[verification/P01/RESUME.md](../verification/P01/RESUME.md)及[下次自动推进提示词](../verification/P01/NEXT-AUTOPROGRESS-PROMPT.md)。

## 2026-10-09 P03 R5/R6 Review 与 Codex 集成关闭 / DONE

P03已完成：Owner=Antigravity、非作者Reviewer=DeepSeek Harness、Integrator=Codex；Task base=`31abde9bf4b73aea2851931dcd48faa0f750b318`，Owner delivery=`85482c5b001d452953c3ed797ce3c4ed64cae4e3`，integration commit=`552464238a69ad2cea63cff18abe98f412dbae87`。DSH R5在fixed head `7677e9c324da2fde618e7cd6fdba2363abeb1f1b`、R6在fixed head `f09100d5b96aea26e4f525fb4c7c10d6d9d9f1cb`均`approved`，未解决P0/P1/P2=0/0/0；Codex非作者复审未发现新P0–P3。集成范围162 paths、零越界、`git diff --check` EXIT=0。16-case snapshot、40/40定向测试和同installer packaged Gate 28/28仍绑定source `d717c049a41544a6d592943a0b0fe1b76a41a050` 与installer SHA `2de124f387bfaf1d0d01b1b0279ad319cd453850d223efa9620b0103ce88a814`；该head至集成commit无产品/runner/test/build差量。报告见[`P03 Codex Integration Gate`](../verification/P03-PACKAGED-SFX-ENTRY/integration/codex-integration-gate.md)。DSH自身shell/Git/tests/Gate为`NOT_RUN`（Win32 5），Web/Desktop visibility=`unverified`；R3-03留作P20风险。

### 历史快照：P03正式释放时状态 / READY

P03「Packaged 第五 SFX 入口验收补齐」已基于live `main@31abde9bf4b73aea2851931dcd48faa0f750b318`建立正式Task并释放 `ready`。Owner=Antigravity，非作者Reviewer=DeepSeek Harness，Integrator=Codex；依赖 `M2-PROD-SFX-PROBE-1@177b356a6453ecc7ae1ec3ae1d5c60f453104007`、`M2-RUNNER-SNAPSHOT-DEBT@73588624b70c337ca4fcb36a4d42e91d3b03f5b0`、`M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD@e7d1f7f8528a6186baec6f642ac8422572103527` 均已done。branch=`agent/antigravity/P03-packaged-sfx-entry`；worktree=`G:/CODEX/New Manga.worktrees/P03-packaged-sfx-entry-antigravity`；allowed_paths=`packaging/m2ac5/run_clean_start_e2e.py`、新增 `tests/packaging/test_packaged_fifth_sfx_entry.py`、`verification/P03-PACKAGED-SFX-ENTRY/**`、P03 Task 与其 Handoff。产品 `src/**`、`apps/**`、IPC/contracts、Schema、依赖、spec/build script 均禁止修改。真实K07页面与v2b权重的外部只读输入SHA、所有AC、构建Hash时序、full Gate、交接和恢复条件见[正式Task](tasks/P03.md)及[恢复点](../verification/P03-PACKAGED-SFX-ENTRY/RESUME.md)。release metadata commit 及Owner初始HEAD由后置 RESUME 记录；fresh installer尚未构建（`NOT_SET`），产品/packaged验收未运行，不能视为通过。

## 历史检查点：2026-10-09 P08集成完成 / P03候选未释放

P08 DSH R7已对base=ecb3b520ce68c2ddcc0c5ec94596e2f50a17f369、reviewed_head=fe222464616152e9c95208e06c248565f2fd86a6批准，session=session-bf5b0be5-bd1e-41b8-83cc-152c28227485，报告SHA256=2D8165B95A702B40607840889208C62A1CEC4E89C4A445D0591BE9ED2A719C03。canonical报告与JSONL final正文逐字节一致。Codex在精确R7 worktree复跑两个validator、fixed-range git diff --check、clean/common-dir及protected path检查均通过。R7-01 P3已由P08 Task-local approval/status映射处置，R7-02已由Codex Gate关闭，R7-03历史字面量已清理。Task status=done；integration_commit=fe222464616152e9c95208e06c248565f2fd86a6，交付直接在main。DSH自身命令因Win32 5为NOT_RUN/NOT_VERIFIED；产品验收仍NOT_RUN。P03的PROBE-1/Runner Debt/Guard前置条件在Plan已记录为满足，但P03未创建或释放；下次需在live main重核并冻结hash/paths后建立正式Task。


2026-10-09 P08状态：P08=done（delivery/reviewed_head=fe222464616152e9c95208e06c248565f2fd86a6；DSH R7 approved；Codex integration Gate通过；integration_commit=fe222464616152e9c95208e06c248565f2fd86a6）；其余20项=proposed / 未释放。P03为下一推荐候选，尚未创建或释放。历史原始审计、台账与验证日志保留。

## 2026-10-08 当前人员裁决：Qoder退出项目

用户明确要求移除Qoder；追加治理范围已先登记于[GOV-001](tasks/GOV-001.md)，变更起点=`main@5b8aed4d`。活跃Agent为Codex、ZCode、DeepSeek Harness、Antigravity；Qoder不再承担Owner/Reviewer/设计或接管。下方当前P02/P07/P08/P12/P14/P15/P17及图、恢复指令已将未来UI/UX责任改为ZCode，DSH优先非作者审查，Codex保留契约/协调/集成。故障转移为ZCode→Antigravity，覆盖共享skill的Qoder默认候选。当前无Active/released产品Task，未启动新实现；历史Task/署名/原Review/台账/未提交内容原样保留。

## 2026-10-08 全项目整体路线（PLAN_ONLY，当前规划覆盖层）

用户要求用 GPT-6.1 Sol high 深读代码和文档、整理全部任务与后续路线、绘中文图并保存额度恢复点。本轮三路审计使用该模型/effort；主协调会话配置保持实际值，不冒充已切换。审计输入=`main@e4242ecd419eb0eea098d2f63b40f709aa5caeea`。本段覆盖下方历史“下一步/ready/blocked”快照的排期解释，**不新增 Active、不释放产品实现、不改变已有产品裁决**。

交付：[报告与能力缺口](../verification/PROJECT-ROADMAP-20261008/REPORT.md)、[中文分层路线图](../verification/PROJECT-ROADMAP-20261008/ROADMAP.md)、[完整 Task 台账](../verification/PROJECT-ROADMAP-20261008/task-inventory.csv)、[额度/中断恢复点](../verification/PROJECT-ROADMAP-20261008/RESUME.md)。详细源码取证见同目录 Core/Desktop/Plan 三份审计；这些文件是证据/派生视图，排期仍以本 Plan 为准，运行仍以 STATUS 为准。

当前：195 个正式 Task 文件＋T1.1.2 历史映射＝196 节点；114 DONE_RECORDED＋48 Legacy VERIFIED_COMPLETE＋5 DOC_ONLY＝167 登记完成/文档交付，另有29个历史 PARTIAL/归档/受限关闭/被取代节点。新架构/治理105节点（其中 M2前缀101）均登记完成，**登记 done 不等于研究质量 PASS、四页全部实现或最终发布通过**。无 Active/released。GC-2实现已done@cea610ed，设计后继 proposed 已被取代；ICU修复、Runner Debt与Guard均已done。旧素材/endpoint/BJ13 blocker不得复活。

实际产品：React目前是 Console↔Workbench，书目与SFX设置是 Console 中的真实IPC小面板；Workbench已接页导航、图像资源、region改标、修订恢复、重渲染。完整四页导航、导入/整条Pipeline启动控制/任务快照/Reader/导出尚未接通。Core里已有业务API，不重写；真实导入适配、异步生命周期与受控IPC需补齐。见报告代码证据。

### 预先定义的任务依赖树与 Gate

以下 P01–P21 中 **P08、P03、P01=done，P02=in_progress / ACTIVE，P05=in_review / ACTIVE（独立文档 Task），其余16项为proposed / 未释放**；P01已完成main fast-forward与post-FF closeout，P02进入正式实现验证；候选任务状态以本表和STATUS为准。

| 候选任务编号 | 状态 | 简单中文描述 | 启动依赖/条件 | 建议责任方；非作者审查 | 完成 Gate / 边界 |
|---|---|---|---|---|---|
| P01 | done | 台账元数据与Review载体取证 | 无Task依赖；固定base=826bea12；最终D3 reviewed head=51bc01fe由Antigravity正式approved（0 findings）；C1 Gate已PASS；integration=`13e66ec5bf9a2fc59f4e6c5623feb0bde22884c8` | Codex；非作者Antigravity | D7 Codex closeout Gate=`PASS`；main=`b7ad98b29196e9859cbfbfe187e6822569f79367`，base..HEAD 92 paths、越界/产品路径0；post-FF manifest 24/24匹配。证据=`verification/P01/integration-gate.md`、`doc/reviews/P01-51bc01fe-antigravity-d3.md`、`verification/P01/closeout-gate.md`与P01 RESUME；R2/SYNTH carrier仍NOT_VERIFIED |
| P02 | in_progress | 真实 Workbench WebView 行为、300ms 刷新与对比度验证 | P08、M2-RESOLVE-DEBOUNCE-1、M2-REGION-DEBOUNCE-1 均已完成；AC/Owner范围 r2及Codex-only validator增量 r4 approved | Antigravity；DeepSeek Harness 非作者审查 | Owner已接单；AC1–AC7真实Tauri/WebView2取证仍待执行；区分mock/Core/JSDOM；300ms quiet-period、retype/undo/restore写后刷新、键盘焦点、F token映射和对比度；build需先过scratch/sidecar隔离Review；独立实现Review与Codex集成Gate后才可done |
| P03 | done | Packaged第五SFX入口验收补齐 | PROBE-1/Runner Debt/Guard已done；DSH R5/R6与Codex集成Gate通过 | Antigravity；DSH | integration=`552464238a69ad2cea63cff18abe98f412dbae87`；Gate evidence绑定source=`d717c049`与固定installer SHA；R3-03留给P20 |
| P04 | proposed / 未释放 | 生产命令族/桥接并发定向验证 | PAGE-NAV done；范围与验收见 [Task](tasks/P04.md)；P02 Build Gate PASS + provenance 固定的隔离 sidecar bundle 后才可执行 Cargo；最新恢复点见 [post-FF checkpoint](../verification/P04/proposal-post-integration-checkpoint-4e6a8cfd.md) | Antigravity；DeepSeek Harness | 字面精确 pin PAGE_NAV 组成员；以确定性 sidecar 诊断同通道并发响应；若复现缺陷则先建独立修复 Task 并阻断 P04；P02 Hard Build Barrier 未解除前不释放、不运行 Cargo |
| P05 | done | category/retryable 契约注记收敛 | M2-CATEGORY-CLARIFY-1、M2-RC4-DOMAIN-COMMANDS、M2-PAGE-RESOURCE-RESOLVE-1 均 done；Task、Owner branch/worktree 与 allowlist 已冻结 | Codex；Antigravity（DSH fallback） | 仅补操作级现状注记与反向链接；不更改冻结错误语义；Review=APPROVED；integration_commit=`bc2b690bc4f66d286bb8f16764269f6681c70b0d`。见 [integration checkpoint](../verification/P05/integration-checkpoint-bc2b690b.md)、[Review report](../verification/P05/antigravity-review-a2569f38.response.md)、[delivery checkpoint](../verification/P05/delivery-checkpoint-a2569f38.md)、[start checkpoint](../verification/P05/start-checkpoint-d36ee3c5.md) |
| P06 | proposed / 未释放 | GC分发迁移安全补证 | GC2 done；受控旧版本/隔离根可用 | ZCode；DSH | G7旧runtime退出/所有入口参与证据；未知保留、迁移不满足BLOCKED；不重做GC2 |
| P07 | proposed / 未释放 | 手输image读取/quiet-window交互修补 | P02证明剩余缺口；REGION-DEBOUNCE已done | ZCode；DSH | 最小实际缺口与判别用例；不重开已闭debounce |
| P08 | done | [完整产品范围与验收冻结准备](tasks/P08.md) | D1–D7已确认；DSH R7对fe222464正式approved；Codex集成Gate通过；delivery直接在main | Codex；非作者Reviewer=DeepSeek Harness | 产品范围/验收矩阵/数据保护/发布边界已冻结；产品实现验收仍NOT_RUN；不扩一级页面 |
| P09 | proposed / 未释放 | 真实导入契约＋Core适配 | P08；先完成AC-DOC-001..003的Architecture Documentation Rebaseline Gate，再冻结来源能力和实施 | Codex契约→Antigravity/ZCode实现；DSH | opaque受限来源、图片/文件夹/PDF/MOBI、真实尺寸、Managed Copy、损坏/逃逸/部分失败；复用Import API与现有decoder |
| P10 | proposed / 未释放 | Provider配置与凭据安全通道 | P08；secret exchange先冻结 | Codex契约→Antigravity实现；DSH | credential引用/存储/脱敏/启动配置与重启持久；secret不进入普通DTO/事件/日志 |
| P11 | proposed / 未释放 | 长任务IPC生命周期契约 | P08；现有PipelineService语义 | Codex；DSH | StartRun快照/控制/恢复/错误/事件策略/有界工作；冻结接受时点；不造第二调度器 |
| P12 | proposed / 未释放 | 书架＋导入的完整用户链 | P09；P08范围确认后另行释放的ZCode页面设计Task通过非作者Review | ZCode；DSH | 建书/章节/选文件/导入报告/导航；React不得传任意路径或直接写DB |
| P13 | proposed / 未释放 | Pipeline后台执行与恢复接线 | P09＋P11；deterministic provider可先验收 | ZCode；DSH | durable accepted、执行/暂停取消重试/崩溃恢复、Lock/current/pinned保护；复用现有API |
| P14 | proposed / 未释放 | 工作台启动/进度/控制/人工编辑闭环 | P13＋P08范围确认后另行释放的ZCode工作台设计Task通过非作者Review；编辑/Lock/Pin/region写命令先冻结 | Codex契约→ZCode/Antigravity Core→ZCode UI；DSH | 替换静态TaskProgress；真实快照查询与失效恢复；译文/Lock/Pin/区域增删几何修改按parity拆切片；expected revision冲突与人工修改保护 |
| P15 | proposed / 未释放 | 完整设置页及所选维护能力 | P10＋P08范围确认后另行释放的ZCode设置设计Task通过非作者Review；备份恢复需P13停写/排空设计 | Codex维护契约→Antigravity Core→ZCode UI；DSH | 使用冻结配置/凭据能力；模型下载、诊断/回收站/TM等现行P0/P1及全库DB＋Managed Copy备份已由P08选入；恢复先停写/连接回收/reassemble/rollback，不冒充全库备份；保留SFX语义 |
| P16 | proposed / 未释放 | 阅读/进度/导出的Core与IPC | P13＋P08正式审查集成（只读旧结果可另评估并行） | Codex契约→ZCode实现；DSH | ReaderProjection/进度/输出授权/lineage/取消；PNG/ZIP/CBZ/PDF/文本分别定格式Gate，PDFComposer现未注入；不把AC1测试模式当production |
| P17 | proposed / 未释放 | 阅读器＋安全导出界面 | P16＋P08范围确认后另行释放的ZCode Reader设计Task通过非作者Review | ZCode；DSH | 真实结果/进度/页序/导出；缩略图、跨页联动非默认范围 |
| P18 | proposed / 未释放 | JA/KO真实质量资格补齐 | P13＋P10；受控素材/模型/endpoint＋P08质量口径；目标架构AC映射须先由Architecture Documentation Rebaseline Task完成 | DSH；Codex或ZCode非作者 | JA自动对齐、无字页F4、K01 terminal/step历史不一致先核验、翻译相似度、修复/源样式质量；真值/阈值/样本/版本可复现，mock不替代；不得以Legacy stack-specific结果作为新架构证据 |
| P19 | proposed / 未释放 | 四页完整E2E与数据安全验收 | P12＋P14＋P15＋P17＋P18；P08已选择四页完整范围 | DSH；Codex非作者 | 用户正常/失败/恢复链；源hash/人工修改/Lock/current/pinned逐项证据；保持D08全部P0/P1和AC-SMOKE完整主流程 |
| P20 | proposed / 未释放 | 最终Windows发布Gate | P19＋P03＋P06；目标环境可用；Architecture Documentation Rebaseline Task先映射目标架构发布/打包/UI要求 | ZCode；DSH；Codex集成 | 新fixed-head/hash安装包；按RG1净化基线验收；Win10单独验证后声明支持；尊重RG1本机裁决，不外推未测环境，不继承PySide6/QML PASS |
| P21 | proposed / 未释放 | Legacy归档/移除（可选） | P20＋独立移除授权 | Codex；非作者DSH | parity＋数据迁移/回退；不继续修Legacy，不作为当前完整产品必做前提 |

历史执行提示（已由2026-10-09 P03关闭与P02 release记录取代）：P03已完成DSH R5/R6和Codex非作者复核；P02已由Codex冻结范围并释放给ZCode，当前状态见本计划顶部、STATUS与P02 RESUME。

保留：Manga109永久取消；BJ13维持0.90、手工改标＋skip，补标/补画不释放；Reader范围：仅跨页联动/页缩略图继续延期；基础Reader已由D1解冻，P16/P17实施仍未释放。LaMa/AOT/BrushNet/FLUX learned inpaint没有production实现，不默认投入；SimpleFill/EdgeBleed已在现有链路，是否足够由P08/P18质量证据决定。GC长会话总磁盘有界没有承诺，不为了漂亮路线图扩大删除能力。

历史步骤（截至C7，已被C8/C9取代）：P01 R1 findings已修订；C5固定范围31 paths Gate PASS。DSH R2对C6=`3e67d53be6363e0eaabbd1ce038c226b82b8a494`返回`blocked`；R2报告、prompt、exit、session metadata及C6 Gate日志进入C7 checkpoint。当时计划寻找可执行的临时Review镜像；C8后实际采用固定差量只读Review。C8 fixed head `91ab1ef8ddaa1d00b0b34880a103937b4831590d` 的正式decision=`changes_requested`，C9修订和复审为当前步骤。R2/SYNTH carrier仍`NOT_VERIFIED`，不改用户裁决或来源Task状态。当前恢复以页首和P01 RESUME最新checkpoint为准。

## 2026-10-08 完成：M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD

[M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD](tasks/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD.md) 已完成，关闭 Runner DSH r4 deferred R-001。Owner=Antigravity，非作者 Reviewer=DeepSeek Harness，Integrator=Codex；依赖 `M2-RUNNER-SNAPSHOT-DEBT done@73588624`。实现基线=`e9b66455356c56e0fe6720d658b46bdbdbeb53b5`；release/start head=`d12ebc7a0bbd5617e7a376e00f45c9ee114c8c10`；code delivery=`e167e72351d6f725653d1f16b210a54f435e621f`；reviewed head=`8b867e0208246e2e478a2906a2198c60c7d88aa6`。DSH r1 `changes_requested` 已修订；DSH r2 `approved`（0 P0/P1/P2），报告见 [DSH r2 Review](reviews/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-8b867e02-dsh-r2.md)。Codex integration merge=`e7d1f7f8528a6186baec6f642ac8422572103527`。集成验证：Python 3.14/3.12 各 8 passed；两个 runner 缺省 CLI 均 exit 2；snapshot oracle 16 项 PASS；历史 raw 61/61 SHA-256 一致；Owner 17 路径中 4 个实现/测试路径均在允许范围；证据见 [集成验证记录](../verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/integration-validation.log)。R-06 剩余模块加载复杂度 deferred；完整 Dev/Packaged Gate、Sidecar、NSIS 按 Task 范围 `NOT_RUN`。R-003（第五入口 packaged 覆盖）仍未释放；当前无 Active/released Task。

## 2026-10-08 完成：M2-RUNNER-SNAPSHOT-DEBT @integration `73588624`

ICU 修复 Task 已 done@`65ba30144048a0b8daae22205c01f8049b44b8a7`；fresh Sidecar/NSIS 与 packaged AC1、完整 26/26 Gate 均绑定 source=`4499217d7b2249da16d5dbf27a3219a43876aac7` 和 installer SHA，满足 Runner Debt 原 blocker 的解除条件。集成后未重跑 ICU Gate，production 差量为零。

Task=`[M2-RUNNER-SNAPSHOT-DEBT](tasks/M2-RUNNER-SNAPSHOT-DEBT.md)` 已 `done`；Owner=Codex、非作者 Reviewer=DeepSeek Harness、Integrator=Codex。reviewed head=`5c2d047804eb4a802c04e53b5e8e5e5459570b24`，AC4 实际代码/测试 head=`3d532c1f99e49da703d2076bd67d46b710866637`，integration fast-forward=`73588624b70c337ca4fcb36a4d42e91d3b03f5b0`。Fresh Sidecar/NSIS/Dev/Packaged 与 snapshot oracle 均 PASS；Packaged 26/26，installer SHA=`ef617573ab39c0469079203489f4db4af78ae4e3437f8d97d87a3565bb40fa75`。DSH r4=`approved`、0 P0/P1；集成后核验与 snapshot 16 项 PASS 见 [integration-validation.log](../verification/M2-RUNNER-SNAPSHOT-DEBT/integration-validation.log)。R-001/R-003 为非阻断 deferred，未自动创建后续 Task。

当前无 Active/released Task。R-003（Packaged Gate 覆盖第五入口）仍是未释放候选；下方 ICU/Runner 旧 release、blocked 与 changes_requested 段落仅为历史 checkpoint。

ICU 集成证据：[integration-validation.log](../verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/integration-validation.log)；[DSH r2 Review](reviews/M2-PACKAGED-AC1-ICU-ISOLATION-FIX-4499217d-dsh-r2.md)。

## 历史 DSH Review r1：M2-PACKAGED-AC1-ICU-ISOLATION-FIX changes_requested

该历史 checkpoint 的 Active Task 为 changes_requested：Owner=Antigravity，非作者Reviewer=DeepSeek Harness，Integrator=Codex。实现当时尚未集成；其最终完成状态见本 Plan 首段与当前 STATUS。
固定原始实现 head=aa099f2a013408bf53c3466ab8361bc028289743；DSH审查报告=verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/review-dsh-r1.md，decision=changes_requested，DSH session=session-4655cd71-226a-4eec-91a7-78dad7e84fab（已挂载到 New Manga workspace；桌面可见性待用户下次启动核对）。
R-001 P1：packaged Gate 实测 installer SHA a17a9708… 与 fingerprint/交付包 f76b91d6… 不同；R-002 P1：构建/Gate 日志 HEAD=df824182，无法证明输入字节等同声明提交 aa099f2a。R-003 P2 缺 PE 扫描原始证据；R-004 P2 spec 按名称整包移除 ICU，违背未知引用保留/禁止全局删除；R-005/R-006/R-007 为断言、报告口径、System32 ICU 运行依赖记录问题。
现有 packaged 26/26 PASS 仅适用于日志记录的 a17a9708… installer，不能记作最终指纹 f76b91d6… 已验收。Dev 10/10+13/13 与 Sidecar/NSIS EXIT 0 也仅是提交内日志，DSH未现场重跑。
Owner恢复点：branch=agent/antigravity/M2-PACKAGED-AC1-ICU-ISOLATION-FIX；worktree=G:/CODEX/New Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity；HEAD=46f50a097d25a1893dd1f43b0a38479952242161，clean、common-dir正确。修订从该实际HEAD继续，Task原始基线仍为 5a72db9e3c5778ce4700b7d404250853e474c5de。
Codex已准备 R1修订指令；生产允许路径仍仅 packaging/m2ac5/**。fresh build、hash绑定、AC-1 artefact及新的非作者DSH复审通过前不集成。M2-RUNNER-SNAPSHOT-DEBT仍blocked。

用户授权“下一步”；Codex串行登记唯一Active Task=[ICU隔离修复](tasks/M2-PACKAGED-AC1-ICU-ISOLATION-FIX.md)，Owner=Antigravity，非作者Reviewer=DSH，Integrator=Codex。
真实agy CLI=1.3.1；探测EXIT0/SUCCESS。实际派发start_head=df824182e813fc6d9045872da51d263f28db87f0，
conversation=d0af5e1f-1da8-4842-a5e6-ededa3b2d651；状态CASCADE_RUN_STATUS_RUNNING，最终EXIT/交付待返回。
[自动派发恢复记录](../verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/dispatch.md)；禁止重复派发同worktree写入。
base=5a72db9e3c5778ce4700b7d404250853e474c5de；branch=agent/antigravity/M2-PACKAGED-AC1-ICU-ISOLATION-FIX；
worktree=G:/CODEX/New Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity；生产仅packaging/m2ac5/**，其余范围/Gate按正式Task冻结不变。
Owner开工将Task ready改in_progress；此处是Codex串行认领授权。产品测试目前NOT_RUN。
真实外部Agent实施后必须固定提交/测试/Handoff，再交真实非作者DSH；不提前称修复完成。
原runner debt保持blocked。下方ready / IDLE等均为历史恢复点。

## 2026-10-08 M2-PACKAGED-AC1-ICU-ISOLATION-FIX ready / IDLE

用户单独释放[ICU隔离修复](tasks/M2-PACKAGED-AC1-ICU-ISOLATION-FIX.md)：Owner=Antigravity，非作者Reviewer=DeepSeek Harness，Integrator=Codex。
唯一ready Task；无运行中Task，本轮未派发实施。硬依赖诊断done@44317548与GC-2 done@cea610ed均已集成。
release/synced_head=3d6d8743f662cb850e570e1fa248b96258fee714（Owner clean，未启动）；
base=5a72db9e3c5778ce4700b7d404250853e474c5de；branch=agent/antigravity/M2-PACKAGED-AC1-ICU-ISOLATION-FIX；
worktree=G:/CODEX/New Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity，新分配初始clean，共享唯一Git common-dir。
生产允许仅packaging/m2ac5/**；先核实ICU78消费者；禁止src/apps/tests/Schema/依赖变更或全局删ICU。
完整fresh五入口/NSIS、dev10+probe13、packaged26项Gate及真实DSH审查/集成后验证为done条件；本轮产品测试NOT_RUN。
固定runner来源2af6b71a仅本Task隔离验证复用，原M2-RUNNER-SNAPSHOT-DEBT仍blocked、未集成/关闭。
[释放恢复点与可转发指令](../verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/release.md)由Codex追加。
下方旧ready/in_progress或“无ready”均为历史checkpoint，不覆盖本段。

## 2026-10-08 M2-PACKAGED-AC1-DLL-DIAG done @merge 44317548

诊断Task=[M2-PACKAGED-AC1-DLL-DIAG](tasks/M2-PACKAGED-AC1-DLL-DIAG.md) done；Owner=DSH，非作者Reviewer/Integrator=Codex。
DSH固定报告head=229c6c371d34234b65bbdd67fff73f341c60930f；Codex r3 approved；integration_commit=4431754845fc25795058534f21656705ef701cd6。
Codex实际隔离复现：同hash bridge原副本EXIT1/QtGui错误，仅自有副本改名保留icuuc后初始化EXIT0。
包内ICU78无Qt所需20个无后缀符号，同名遮蔽系统ICU；native错误127及系统ICU加载对照支撑因果。
范围仅本固定产物/本机；没有生产修复，完整26项Gate未重跑，其它ICU78依赖需求未核实，禁止全局删除。
集成后独立证据检查EXIT0、syntax/diff PASS、批准报告字节一致，src/apps/tests/packaging零差量。
[REPORT](../verification/M2-PACKAGED-AC1-DLL-DIAG/REPORT.md)；[Review r3](reviews/M2-PACKAGED-AC1-DLL-DIAG-229c6c37-codex-r3.md)；
[集成验证](../verification/M2-PACKAGED-AC1-DLL-DIAG/raw/post-merge-validation.log)。
当前无运行中/ready Task；M2-RUNNER-SNAPSHOT-DEBT保持blocked。下一步候选M2-PACKAGED-AC1-ICU-ISOLATION-FIX，
Owner=Antigravity，非作者Reviewer=DSH，Integrator=Codex；未创建/释放，须单独冻结修复范围与分配工作区。
[下一Task完整释放准备](../verification/M2-PACKAGED-AC1-DLL-DIAG/NEXT_IMPLEMENTATION.md)。
下方in_progress/blocked为历史checkpoint，不覆盖本段。


## 2026-10-08 恢复隔离实测：M2-PACKAGED-AC1-DLL-DIAG in_progress

用户授权“下一步”；Codex串行恢复本Task in_progress / ACTIVE，Owner=DSH，Reviewer/Integrator=Codex。
Codex提供本机独立验证执行支持，冻结允许范围在Task末尾；原probe代码head=d3006691，Owner恢复db65b6cf。
先固定installer/bundle hash、隔离环境/自有lab、stdin EOF和自身进程超时，再实跑DSH探针、回传DSH更新报告。
src/apps/tests/packaging/依赖/Schema仍只读；生产修复未释放，原runner debt保持blocked。
下方blocked是历史checkpoint，根因在取得新证据前继续UNKNOWN。

## 2026-10-08 DSH自动诊断返回：M2-PACKAGED-AC1-DLL-DIAG blocked

当前Task=[M2-PACKAGED-AC1-DLL-DIAG](tasks/M2-PACKAGED-AC1-DLL-DIAG.md)，Owner=DeepSeek Harness，非作者Reviewer/Integrator=Codex。
TaskStatus=blocked，previous=in_progress，ExecutionState=CHECKPOINTED。真实dsh CLI两轮EXIT0；
session=session-7de56368-5e9b-44ed-9e2d-0c288fdc67ff，已精确挂载，桌面下次启动可发现；当前可见性未验证。
Owner分支agent/deepseek/M2-PACKAGED-AC1-DLL-DIAG；worktree=G:/CODEX/New Manga.worktrees/PACKAGED-AC1-DLL-DIAG-dsh。
固定返修head=d30066917759b62133840ac6767c7ef67153be06；原start_head=24e0ec6e5c6d64a35daad006565919818616b317；base=9063c317。
DSH交付报告/矩阵/最小probe，运行被pwsh沙箱Win32 5阻塞，实际加载仍NOT_RUN，具体DLL/符号/错误码UNKNOWN。
Codex r1发现安全/证据问题，已自动回传DSH；r2有界静态核对通过，不能替代动态验证或完成批准。
[REPORT](../verification/M2-PACKAGED-AC1-DLL-DIAG/REPORT.md)；[Codex r2](reviews/M2-PACKAGED-AC1-DLL-DIAG-d3006691-codex-r2.md)。
主线只同步治理/报告/Review，probe留在Owner分支待执行核验；src/apps/tests/packaging零差量。
下一步同Task补可信隔离运行和实际加载证据，再回DSH更新矩阵并由Codex重审；生产修复未释放。
M2-RUNNER-SNAPSHOT-DEBT继续blocked，完整packaged Gate未通过。下方in_progress/ready为历史checkpoint。


## 2026-10-08 自动派发：M2-PACKAGED-AC1-DLL-DIAG in_progress / DSH

唯一Active Task=[M2-PACKAGED-AC1-DLL-DIAG](tasks/M2-PACKAGED-AC1-DLL-DIAG.md)，TaskStatus=in_progress，ExecutionState=ACTIVE。
Owner=DeepSeek Harness，非作者Reviewer=Codex，Integrator=Codex。用户授权自动调用外部Agent；Codex已串行登记认领，只读诊断，真实DSH CLI派发中。
硬依赖M2-DERIVED-GC-2 done@cea610ed；M2-RUNNER-SNAPSHOT-DEBT只是固定失败证据来源，仍blocked、暂停恢复。
base=9063c317937b86bed1f6ff3e2f2c5d224dc10553；branch=agent/deepseek/M2-PACKAGED-AC1-DLL-DIAG；
worktree=G:/CODEX/New Manga.worktrees/PACKAGED-AC1-DLL-DIAG-dsh，已分配clean/common-dir=G:/CODEX/New Manga/.git。
冻结范围：诊断Task、自有verification与Handoff；产品/src/apps/tests/packaging/spec/依赖只读，
不启动Legacy诊断、不绕过purged PATH Gate、不实施修复。原installer SHA已重新实测匹配，诊断测试NOT_RUN。
原构建source_head=cfb5d2eecc4d8ab7a3159cdbb1d5812547bb5cd2；证据head=15cd788f10e83f6a1a215e71538bfa175b435785。
交付失败DLL/闭包/环境证据或UNKNOWN、最小修复范围建议；Codex非作者Review后才集成诊断文档。
[输入参数](../verification/M2-PACKAGED-AC1-DLL-DIAG/input-manifest.json)；正式release/synced HEAD=4330b792479c7d251b6dd2389aefa4b1a1b7fe6f，clean/common-dir复核通过。
[实际恢复点](../verification/M2-PACKAGED-AC1-DLL-DIAG/release.md)；[完整DSH指令](../verification/M2-PACKAGED-AC1-DLL-DIAG/DSH_INSTRUCTION.md)。
下方runner debt的“唯一Active”及未释放诊断描述为历史checkpoint，不覆盖本段；它的FAIL/BLOCKED不变。


## 历史 checkpoint：M2-RUNNER-SNAPSHOT-DEBT blocked（DSH r3后）

唯一Active Task=[M2-RUNNER-SNAPSHOT-DEBT](tasks/M2-RUNNER-SNAPSHOT-DEBT.md)，Owner=Codex，
非作者Reviewer=DeepSeek Harness，Integrator=Codex。TaskStatus=blocked，
previous_status=in_progress，ExecutionState=CHECKPOINTED。两处runner快照修复留在Owner分支，未集成。
固定构建源码head=cfb5d2eecc4d8ab7a3159cdbb1d5812547bb5cd2；
DSH r3 reviewed_code_head=2af6b71aa06979b822e543b221aaf3a2d5f01abe；
evidence_commit=653a00628e484ecb8ae023f2594b80233bce4e9a；
Owner恢复HEAD=15cd788f10e83f6a1a215e71538bfa175b435785，clean；worktree=
G:/CODEX/New Manga.worktrees/RUNNER-SNAPSHOT-DEBT-codex，common-dir=G:/CODEX/New Manga/.git。
最小16用例PASS；dev Gate10/10+probe13/13 PASS；packaged CS-L1 PASS，完整26项为
20 PASS / 1 FAIL / 5 NOT_RUN。AC1 run1 acceptance_bridge.exe报QtGui DLL导入失败，
精确退出时间线UNKNOWN；不把整个runner耗时当单次timeout证据。
DSH r3静态有界代码批准，零重跑，0P0/P1、4个非阻断P2已补证据/指针；
[原始Review](reviews/M2-RUNNER-SNAPSHOT-DEBT-2af6b71a-dsh-r3.md)。AC4=FAIL/BLOCKED，AC6未集成，Task不能done。
主线只同步治理/原始Review/自有verification证据；此处判别脚本作为审计产物，运行须使用Owner工作区，
主线两个runner仍为未集成版本。没有产品/src/apps/tests/依赖/Schema修改，历史FAIL不追认PASS。
[Handoff及完整转发指令](handoffs/M2-RUNNER-SNAPSHOT-DEBT-codex-cfb5d2ee.md)；
[恢复与同步](../verification/M2-RUNNER-SNAPSHOT-DEBT/closeout-recovery.md)。
下一步建议Codex单独冻结并释放M2-PACKAGED-AC1-DLL-DIAG，Owner=DSH，非作者Reviewer=Codex，
仅诊断新架构packaged acceptance构建环境；候选尚未创建/释放，不能自行开始范围外修复。
解除阻塞需新固定head fresh构建完整Gate通过，再经非作者审查与Codex集成验证。
下方ready/in_progress/历史checkpoint不覆盖本段。


## 历史正式释放：M2-RUNNER-SNAPSHOT-DEBT in_progress

唯一 Active Task=[M2-RUNNER-SNAPSHOT-DEBT](tasks/M2-RUNNER-SNAPSHOT-DEBT.md)，
TaskStatus=in_progress，ExecutionState=ACTIVE。用户明确释放，
Owner=Codex，非作者Reviewer=DeepSeek Harness，Integrator=Codex。
依赖M2-DERIVED-GC-2 done@cea610ed；base=968c8f34601b72667831f1fd15bb20cd2c8f3cb7。
branch=codex/M2-RUNNER-SNAPSHOT-DEBT；
worktree=G:/CODEX/New Manga.worktrees/RUNNER-SNAPSHOT-DEBT-codex。
只修m2ac5协议ping快照与M2-RC2生产命令快照及最小判别/证据隔离；
允许路径与Gate冻结在Task，不改生产/wire/Schema/依赖、不弱化验收。
用户已授权Codex认领实施；先修复快照和输出隔离，再执行定向/dev/packaged验收。旧两个FAIL保持到新Gate闭合，当前验收NOT_RUN。
[实际释放恢复点](../verification/M2-RUNNER-SNAPSHOT-DEBT/release.md)。
下方GC-2记录及无Active/未释放debt描述是历史checkpoint，不覆盖本段。


正式 release/synced Owner HEAD=5896db8c64b90b53b015eb9c46c7dab6ab29210b，clean/common-dir已核验；主仓库后续仅追加本恢复证据，Owner 固定留在 release，不需追随最新 main。
## 2026-10-07 GC-2设计集成与后继准备

[M2-DERIVED-GC-2-DESIGN](tasks/M2-DERIVED-GC-2-DESIGN.md) **done** @merge ad75fadc2944983b4322f353176ba70cf0b0b7ae；Codex/真实DSH/Codex。DSH r4固定e4c0967f approve_with_conditions，0P0-P3；设计判据闭合，两个P4写入指令，治理/实际恢复点准备完成。只交设计，生产代码/Schema/依赖/用户数据零写入；实际回收/native Gate全部NOT_RUN。

[M2-DERIVED-GC-2](tasks/M2-DERIVED-GC-2.md) **done @merge `cea610ed`**（2026-10-08 集成收口；用户 /goal 完全授权，ZCode 代行 Integrator）：Owner=ZCode / 非作者 Reviewer=Codex（用户指示变更，原冻结 DSH）/ Integrator=Codex。11 轮非作者 Review 收敛 r11 approve（0 findings）@基准 258ca6fe、Owner 终 tip=0fadc330；AC1-AC6 与 G1-G7 判别测试全入库（G7 分发迁移 Gate 保持阻断条款登记，CS-L1 快照漂移交独立 debt 候选 M2-RUNNER-SNAPSHOT-DEBT 保持 FAIL 记录）。集成后 main@cea610ed 三套件等量全绿：pytest 1941+1sk / cargo 62+1ign / vitest 140。branch/worktree 留存。无 Active、无 released；下方无Active/190节点等数量是固定历史快照，不覆盖本段。

## 2026-10-07 全面 REBASELINE 覆盖层（审计输入 main@32f9b932）

本次全量审计与下一步分配见 [审计报告](../verification/REBASELINE-20261007/REPORT.md)，全部 **189 个 Task 文件 + T1.1.2 Roadmap 映射，共 190 个节点**见 [任务台账与分组流程图](../verification/REBASELINE-20261007/TASK_GRAPH.md)，机器可复核参数与 Git/worktree 证据见 [inventory](../verification/REBASELINE-20261007/inventory.json)。本段为当前规划覆盖层，下面各日期段落保留历史证据。

数量：已登记完成 **161**（108 DONE_RECORDED + 48 历史 VERIFIED_COMPLETE + 5 DOC_ONLY），历史 PARTIAL **9**、Legacy 归档未完成 **13**、closed_with_limitations **1**、被取代 **6**；当前已登记进行中 **0**、已释放 **0**。这些数字不表示本次复跑全部测试或重做 161 次独立 Review。Legacy 不再生成实施队列。

旧待办校正：TA3-B 阶段二已由 B2 / KO-RERUN / B3 后继任务完成，不再等待用户提供翻译 endpoint；Manga109 永久取消；BJ13/0.90 裁决已确认。ANNOTATE-R2 与 SYNTH-BG-AUTO 原页头落后于 main 集成和 Plan 完成记录，原状态保留并在台账标 STATE_CONFLICT；原独立 Review 报告当前 tracked 树未定位，载体核验 NOT_VERIFIED，不追加虚构批准。

**推荐下一 Task：M2-DERIVED-GC-2-DESIGN（建议 ID，PLANNED_PLACEHOLDER，尚未创建/释放）**。Owner 建议 Codex，非作者 Reviewer 建议 DeepSeek Harness；先追踪旧 preview 的 page/current/pinned/grant 引用，冻结安全回收判据，设计 Gate 后由 ZCode 实现、DSH Review、Codex 集成。允许/禁止路径、固定审计 base/head、worktree 待创建说明及可直接转发指令见审计报告。不得直接启动未释放实现；不扩大 Reader/BJ13 产品范围。

Status: **ACTIVE DEVELOPMENT BASELINE — 2026-10-07 refresh @main `0cb15092`；A/B/C、M2-RC4-DOMAIN-COMMANDS、test_catalog 漂移清算、ui_shell 环境敏感处置、M2-PAGE-RESOURCE-RESOLVE-1、M2-PAGE-NAV-PROJECTION-1、M2-DERIVED-GC-1、M2-CATEGORY-CLARIFY-1、M2-RESOLVE-DEBOUNCE-1 与 M2-REGION-DEBOUNCE-1 全闭环；main 全量基线=1886 passed+1 skipped+0 failed（vitest 140）；无 Active、无已释放。当前运行状态见 STATUS，历史快照不具释放效力。**

Audit date: 2026-10-07 (Asia/Shanghai)，[本次证据](../verification/M2-RC4-DOMAIN-COMMANDS/rebaseline-20261007.md)。

Initial rebaseline code audit: `master` @ `ce21ff9ea5738970bbda9a86079b673918c76048`

Legacy closure checkpoint (2026-09-26): T3.2.1 is `closed_with_limitations` / `SUPERSEDED_BY_M2` under the user-confirmed React + TypeScript + Tauri + Python Core target. The prior integration at `6519125` remains valid historical evidence: fixed input `08f9bd8` was not rebuilt; AC3 remains `PASS（本机模拟路线；非干净机覆盖）`; AC6/AC8/AC9 remain `PARTIAL`; clean Windows/no-Python, Windows 10, real docTR-weight success and true cold-start remain `NOT_RUN`. This is not a Legacy Release approval. Detailed AC/Finding disposition: [closure audit](../verification/T3.2.1/legacy-closure-audit-20260926.md); live execution state: [STATUS.md](STATUS.md).

This file is the sole source of truth for sequencing. `doc/STATUS.md` is the
only live execution checkpoint. `doc/tasks/`, `doc/handoffs/`, `doc/reviews/`
and `verification/` are historical evidence unless this file explicitly
releases a task.

## 2026-10-07 当前释放与业务裁决

A/B/C 已全部集成、收口，不重新打开。阈值 0.90 保持；BJ13 用手动改标 + skip，补标/补画扩展暂不释放。**[M2-RC4-DOMAIN-COMMANDS](tasks/M2-RC4-DOMAIN-COMMANDS.md) 已于 2026-10-07 全链闭环 done @merge `0a7e0d5b`**（Owner=Codex Executor / Reviewer=DeepSeek Harness r1+r2 / Integrator=Codex；[契约](contracts/M2-RC4_DOMAIN_COMMANDS.md) rev 1.6；AC1-AC5 全 PASS；详见 STATUS checkpoint）。历史表述中的释放/进行中状态只记录当时状态，不覆盖本段与 STATUS。

RC-4 done 后 Codex 按最新实测缺口选择下一最高优先任务，无需逐步申请授权；候选包括真实 UI 交互覆盖、页导航/资源投影、token 对比度、test_catalog 断言漂移，均须先单独 Task 冻结范围与 Gate。不重新释放已完成研究、Legacy 或无新证据 BJ13 扩展。**[M2-PAGE-RESOURCE-RESOLVE-1](tasks/M2-PAGE-RESOURCE-RESOLVE-1.md) 已于 2026-10-07 全链闭环 done @merge `9e242b0c`**（Owner=Codex Executor / ZCode 代行，Reviewer=DeepSeek Harness r1+r2，Integrator=Codex / ZCode 代行；契约 M2-C1 rev 1.7、协议 minor 5；DSH r1 changes_requested→rework→r2 approve_with_conditions 全条件闭合；详见 STATUS checkpoint）。**[M2-PAGE-NAV-PROJECTION-1](tasks/M2-PAGE-NAV-PROJECTION-1.md) 已于 2026-10-07 全链闭环 done @merge `657af2e3`**（Owner=Codex Executor / ZCode 代行，Reviewer=DeepSeek Harness r1+r2，Integrator=Codex / ZCode 代行；契约 M2-C1 rev 1.8、协议 minor 6；DSH r1 approve_with_conditions→rework `14f4b1e6`→r2 approve→hardening `00538a14`；详见 STATUS checkpoint）。**[M2-DERIVED-GC-1](tasks/M2-DERIVED-GC-1.md) 已于 2026-10-07 全链闭环 done @merge `44859014`**（Owner=Codex Executor / ZCode 代行，Reviewer=DeepSeek Harness r1+r2，Integrator=Codex / ZCode 代行；零 wire/零 schema/零 React+Rust；RC4-12=**PARTIAL mitigation**——orphan/死行子集闭合、轮换增长路径保持 open；DSH r1 approve_with_conditions→rework `4edec70a`→r2 approve→polish `9c9c7e55`；详见 STATUS checkpoint）。**[M2-CATEGORY-CLARIFY-1](tasks/M2-CATEGORY-CLARIFY-1.md) 已于 2026-10-07 全链闭环 done @merge `21865f7d`**（Owner=Codex Executor / ZCode 代行，Reviewer=DeepSeek Harness r1+r2，Integrator=Codex / ZCode 代行；RC4-10 澄清非修订——MISSING_REQUIRED_INPUT envelope category→unavailable，M2-C1 §5 RerenderPage 注记；DSH r1 approve_with_conditions→docs-only 返修 `e0ab0444`→r2 approve；详见 STATUS checkpoint）。**[M2-RESOLVE-DEBOUNCE-1](tasks/M2-RESOLVE-DEBOUNCE-1.md) 已于 2026-10-07 全链闭环 done @merge `65d500e6`**（Owner=Codex Executor / ZCode 代行，Reviewer=DeepSeek Harness r1+r2，Integrator=Codex / ZCode 代行；PAGE-RESOLVE PR-10 闭合——resolve 300ms 逐键 debounce，零 Python/Rust/契约；DSH r1 approve_with_conditions→返修 `acc3a578`→r2 approve；详见 STATUS checkpoint）。**[M2-REGION-DEBOUNCE-1](tasks/M2-REGION-DEBOUNCE-1.md) 已于 2026-10-07 全链闭环 done @merge `0cb15092`**（Owner=Codex Executor / ZCode 代行，Reviewer=DeepSeek Harness r1+r2，Integrator=Codex / ZCode 代行；RESOLVE-DEBOUNCE r1 C-1 残留闭合——region 300ms 逐键 debounce，写后刷新即时；零 Python/Rust/契约；DSH r1 a_w_c→路径 B 返修 `2cfa7e6f`→r2 a_w_c→N-01 按 r2 option 2 收口承载 `80db177d`；详见 STATUS checkpoint）。

## Architecture decision and future migration registration

[AD-001 Target Desktop Architecture](AD-001_TARGET_DESKTOP_ARCHITECTURE.md) records the user's accepted formal target: React + TypeScript presentation, Tauri/Rust desktop shell and IPC, headless Python Core business/persistence authority, and SQLite as persistent source of truth. M2 first wave M2-I1, M2-I2, M2-R1 and M2-UI1 is complete and integrated. The existing PySide6/QML application may remain operational during migration, but its PyInstaller Windows Release Gate is historical and no longer defines future formal product release acceptance.

**New-architecture-only directive（2026-09-28；用户裁决）**：后续 Task、问题诊断、修复与验收只在 React + TypeScript + Tauri + Python Core + SQLite 新架构上登记和执行。PySide6/QML 代码、测试、Task 与 verification 只保留为历史证据，不再释放 Legacy 实现、诊断或修复工作；旧架构问题若仍对应目标产品行为，必须改写为 M2 新架构需求，并在新架构路径复现、解决和验收。此前仅为 planning recommendation 的 `DIAG-LEGACY-QML-IMPORT-ENTRY-001` 已撤销，未曾释放。

### 2026-09-29 用户授权 Task：M2-TA1

[M2-TA1](tasks/M2-TA1.md)「日漫 / 韩漫统一测试素材基础设施」由用户本次请求授权，依赖已完成的 M2-RG1；独立 Review=`approved`，Codex 已于 `1ef8fe7e7e66044869f8c59646d28bfca7692bbe` 集成并通过定向集成验证，Task=`done`。实现交付=`00df8f1dd4d480d4e4432c833981481f2c01dd3e`；范围只含独立 case manifest、素材 CLI、下载数据忽略规则、工具专用测试及文档；生产 Schema/Pipeline/Provider/依赖零改动。用户授权本地测试，已取得固定 10 个 KO smoke case（主仓库 80 files / 884,913,245 bytes）；受版权限制原图不入库；Manga109 仍 gated 且当前无获批归档。L1 扩到 100–150 暂缓，先补真实可运行 JA 资产。

### 2026-09-29 用户授权阶段：M2-TA2A / M2-TA2B / M2-TA3

[M2-TA2A](tasks/M2-TA2A.md)「JA Public Assets Bootstrap」已完成并由 Codex 集成于 `ef13a77bedf8bb06ee222113da186c7bfff09714`（delivery=`f8ef48c4079e03e57a7ed0da1e9b79c05e90979c`）；Owner=Codex Desktop，Reviewer=DeepSeek Harness（非作者），Integrator=Codex Desktop。实际取得 10 张 Pepper&Carrot 日语本地化页面图像与 2 个官方 SVG language-pack ZIP，以及 74 个 COO/Manga109Dialog XML 和 2 个 license 文件；JA inventory 为 88 文件 / 47,024,650 bytes。图像与归档留在本地 ignored 路径。该结果提供 10 个可枚举的 JA Smoke Case，但并非日本原创 Manga；E20P06/P07 仅有部分机器可读日文文字层，Open Ground Truth 仍为 `PARTIAL`。Manga109 图像仍为 0，L1 保持 65 个定义 / `PARTIAL`。

~~原文（2026-09-30 用户裁决永久取消）：[M2-TA2B](tasks/M2-TA2B.md)「Manga109 Authorized Import」保留为 gated follow-up~~。**2026-09-30 用户裁决：Manga109/Manga109-s 前置永久取消**；[M2-TA2B](tasks/M2-TA2B.md)「JA/KO 开放素材池」**`done` @integration `fae0d8f6`**（2026-09-30；densho810 BJ 官方免费 1/3/5 卷避 JASRAC、BJ01-BJ12 + P&C 17 页 + Manga109 取消标注 + OpenMantra 隔离 optional；DSH r1 approved_with_conditions → r2 approved，0×P0/P1/P2；交付链 tip=`98766fdc`；densho810 利用报告邮件已于 2026-09-30 发送至 info@densho810.com（1 个月报告义务履行完毕））。

### 2026-09-29 用户授权 Task：M2-TA2C No-HF JA/KO Asset Migration

[M2-TA2C](tasks/M2-TA2C.md) 在已完成 M2-TA1/TA2A 的同一个 `comic_golden_suite` 上迁移附件来源方案；基线=`d4d3977907bc64177ef85c61da4c95901f135fc6`，Owner=Codex Desktop，非作者 Reviewer=DeepSeek Harness，实现作者交付后由用户指示 ZCode 代行 Codex 集成；**已 `done` @integration `a4cd513d0f7ca6a50e1ae018629b3042612be3bb`**（r2 `approved` @`8cb3a135`，session=`ca1ae6af`）。附件无实物数据，脚本存在自动依赖安装、下载先发布后验哈希、无许可过滤的重打包风险，故不直接运行（静态审计见 `verification/M2-TA2C/attachment-audit.md`）。公开来源按官方访问与许可逐项核定，Manga109 不再是 JA L0/L1 的硬前置。集成后实际覆盖：L0 20/20 READY（JA 10 + KO 10）、L1/L2 68 定义中 23 READY / 8 MISSING / 37 MISSING_GATED_ASSET，inventory 92 文件 / 63,317,229 bytes；KO 新增 Pepper&Carrot E04P02/P03/P07 + language-pack（4 文件 / 16,292,579 bytes，ignored 本地）；应用级 Pipeline 检查仍全部 `NOT_RUN`。**2026-09-30 用户裁决拆阶段**：[M2-TA3-A](tasks/M2-TA3-A.md) **`done` @integration `5dc69d16`**（5 case=BJ02/BJ06/K01/K02/K11 全链 COMPLETED pipeline_failures=0，真 docTR detect+mock OCR/translate+生产 inpaint/render/export，pytest 82 passed，DSH r1→r2 条件全闭；已知 LOCK_CHANGED 缺口真检测下未复现=L-1 候选；TA3-B 维持暂缓）；M2-TA3-B **阶段一已 `done` @merge `97450992`**（集成 `81cf5125`，DSH r1 changes_requested→返修 `cad45622`→r2 `approved` 0×P0/P1/P2，2026-10-01；阈值提案/OCR 冒烟/20-case 选取/阶段二计划四件交付，R6 端到端探针 PASS，运行时清单见 `verification/M2-TA3-B/integration.md`）；**阶段二（正式 run）BLOCKED_ON_USER：翻译 endpoint 二选一**（(a) 用户 OpenAI-compatible endpoint+key / (b) 授权 Sakura 本地部署），用户裁决后另行释放。

### 2026-09-28 任务盘点（当日快照；当前执行状态见 STATUS）

Live Git=`main@f6f22b67`（2026-09-29 REBASELINE 审计基线，未 push）。已登记并闭环的 Task 共 28 个（GOV-001；M2 首波 D1/I1/I2/R1/UI1；契约与资源通道 C1/S1/S2/C2/S3/RC1/RC2；验收 AC1/AC2/AC3/AC4；DIAG-M2-REGIONLESS-LOCK-CHANGED-001、M2-P1、M2-IPC1；Legacy 诊断家族 DIAG-READING-EXPORT-001/FIX-A/FIX-B/FIX-C；FIX-STUB-DECODER、FIX-EXPORT-LINEAGE、FIX-LISTBOOKS-PAGECOUNT-UNKNOWN、FIX-F02-RESOURCE-CHANNEL-FLAKY），全部 `done` 且集成 main；最新集成=`aa2f99b8`（F02 资源通道安全缺口修复）。**GOAL（G1-G5）已于 2026-09-29 03:4x 达成（停止条件 3）**；随后用户批准释放的 [M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF](tasks/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF.md) 已于 2026-09-29 完整走通 release→implement→review→integrate 链并 `done`（integration=`bc2529f0`，DSH r1 `approved_with_conditions` 0×P0/P1/P2）。验收面终态：m2_acceptance 35 passed 0 xfailed 全绿、tests/core 77 passed、cargo 34 passed、vitest 31 tests；历届 Owner branch/worktree 全保留。未完成仅剩：BLOCKED 待用户资源的 Real docTR、前置未满足的 M2 Release Gate（可测对象已由 M2-AC5 就位），与散落 P3 遗留清单（见下表末列与 STATUS Goal completion checkpoint，新增 DIGEST-PERF P3-5 `SetFilePointer` 2 GiB 既有隐患、M2-AC5 fresh-checkout 构建顺序/beforeBuildCommand 候选）。

| 已完成 Task | Owner | 非作者 Reviewer / Integrator | Integration |
|---|---|---|---|
| GOV-001 | Codex | DeepSeek Harness / Codex | `969f7a5e` |
| M2-D1 | DeepSeek Harness | Codex / Codex | `100abfbb` |
| M2-I1 | ZCode | DeepSeek Harness / Codex | `cff1e0a8` |
| M2-I2 | Antigravity | Codex / Codex | `7e2da6b8` |
| M2-R1 | DeepSeek Harness | Codex / Codex | `5803bd7b` |
| M2-UI1 | Qoder | Antigravity / Codex | `5242f648` |
| M2-C1 | ZCode | Qoder + DeepSeek Harness / Codex | `c1765aa2` |
| M2-S1 | DeepSeek Harness | Codex / Codex | `4103493f` |
| M2-S2 | ZCode | Antigravity / Codex | `bf1d1230` |
| M2-C2 | ZCode | DeepSeek Harness / Codex | `d574ec1e` |
| M2-S3 | ZCode | DeepSeek Harness / Codex | `6799c73a` |
| M2-RC1 | ZCode | DeepSeek Harness / Codex | `3a246840` |
| M2-RC2 | ZCode | DeepSeek Harness / Codex | `88f972fe` |
| M2-AC1 | ZCode | DeepSeek Harness / Codex | `f162193b` |
| M2-RG1 | ZCode | DeepSeek Harness / Codex（ZCode 代行） | `b796bed3` |
| M2-TA1 | Codex | Codex（独立 reviewer subagent）/ Codex | `1ef8fe7e` |
| M2-TA2A | Codex Desktop | DeepSeek Harness / Codex Desktop | `ef13a77b` |
| M2-TA2C | Codex Desktop（续接/集成=ZCode 代行） | DeepSeek Harness / ZCode（代行 Codex） | `a4cd513d` |
| DIAG-M2-REGIONLESS-LOCK-CHANGED-001 | DeepSeek Harness（静态交付，执行由集成方代采） | Antigravity / Codex（代行） | `b5ac097f` |
| M2-P1 | Antigravity | DeepSeek Harness / Codex（代行） | `a174fb9c` |
| M2-IPC1 | Antigravity | DeepSeek Harness / Codex（代行） | `04c1394a` |
| M2-AC2 | ZCode | DeepSeek Harness / Codex（代行） | `9d3c1db5` |
| M2-AC3 | ZCode | DeepSeek Harness / Codex（代行） | `cac37485` |
| M2-AC4 | ZCode | DeepSeek Harness / Codex（代行） | `fc991821` |
| M2-FIX-STUB-DECODER | ZCode | DeepSeek Harness / Codex（代行） | `121a281c` |
| M2-FIX-EXPORT-LINEAGE | ZCode | DeepSeek Harness / Codex（代行） | `d71883ec` |
| M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN | ZCode | DeepSeek Harness / Codex（代行） | `69961029` |
| M2-FIX-F02-RESOURCE-CHANNEL-FLAKY | ZCode | DeepSeek Harness / Codex（代行） | `aa2f99b8` |
| M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF | ZCode | DeepSeek Harness / Codex（代行） | `bc2529f0` |
| M2-AC5 | ZCode | DeepSeek Harness / Codex（代行） | `9db08dc7` |
| M2-FIX-DIGEST-SEEK-2GIB | ZCode | DeepSeek Harness / Codex（代行） | `a0ffc4f3` |
| M2-AC5-BUILD-FRESH-CHECKOUT | ZCode | DeepSeek Harness / Codex（代行） | `1a96f536` |
| M2-TA2C-TOOLING-GAPS | ZCode | DeepSeek Harness / Codex（代行） | `04165c76` |
| M2-DOCTR-QUAL-PREFLIGHT | ZCode | DeepSeek Harness / Codex（代行） | `51229d49` |
| M2-DOCTR-QUAL-RUN | ZCode | DeepSeek Harness / Codex（代行） | `e8c9c120`（正式结论 FAIL） |
| M2-TA2B | ZCode | DeepSeek Harness / Codex（代行） | `fae0d8f6` |
| M2-TA3-A | ZCode | DeepSeek Harness / Codex（代行） | `5dc69d16` |
| DIAG-M2-LOCK-CHANGED-REPRO-002 | ZCode | DeepSeek Harness / Codex（代行） | `1faf6c1b`（收口 `56edc335`） |
| DOC-FIX-LOCK-CHANGED-STALE-COMMENTS | ZCode | DeepSeek Harness / Codex（代行） | `1970512d`（集成修正 `e81b4220`） |
| M2-DOCTR-QUAL-C4 | ZCode | DeepSeek Harness / Codex（代行） | `d5b1831d`（**Gate 全 PASS**：Recall 0.9618 / MeanCov 0.9965 / severe 0.0；fine-tune 主线不投入；C1 缩减为抽检） |
| M2-DOCTR-QUAL-C1 | ZCode（判定=用户本人） | DeepSeek Harness / Codex（代行） | `316abf16`（0 真实对白漏检、Precision 方向性下界 25 盲区+4 幻觉、D 层盲区 5/10 全 SFX；Gate PASS=保守下界） |
| M2-PROD-DETECT-1 | ZCode | DeepSeek Harness / Codex（代行） | `056617e4`（manga 域 RT-DETR-v2 生产 provider+backend 选择默认 manga 可切回；CPU 315.6ms/页；DSH r1 条件闭合→r2 approved） |
| M2-PROD-DETECT-2 | ZCode | DeepSeek Harness / Codex（代行） | `9e44fb21`（发布形态 ML 栈进闭包+权重随包，NSIS 438.86MiB；GATE 25/25+探针 6/6；AC5=PARTIAL→「IPC1 命令面扩展+frozen detect」slice 登记；DSH r1 changes_requested→r2 approved） |
| M2-PROD-DETECT-3 | ZCode | DeepSeek Harness / Codex（代行） | `8fe5199c`（core.detect 命令面协议 1.1+frozen 真实 detect 端到端；DETECT-2 AC5 转 RUN；§8 脱敏+§10 契约例外+torchvision 缺口修复；DSH r1 条件→集成方全闭） |
| M2-MANGA-WEIGHTS-SOP | ZCode | DeepSeek Harness / Codex（代行） | `853fc911`（fetch/verify 脚本+SOP；DSH r1 条件→r2 approved；错 pin 反证 PASS） |
| M2-FIX-REGISTRY-READINESS-ENV | ZCode | DeepSeek Harness / Codex（代行） | `52b07438`（环境断言条件化；三套件 0 failed 基线确立） |
| M2-SFX-DETECT-EVAL | ZCode | DeepSeek Harness / Codex（代行） | `cf4e55ec`（SFX 评估：chiqui7 唯一 sfx 类候选；自比修正方向反转 ogkalu 非自比 7/18；DSH r1→r2 approved） |
| M2-SFX-PROD-1 | ZCode | DeepSeek Harness / Codex（代行） | `0a505bab`（SFX 生产集成：chiqui7 ONNX provider+权重随包 NSIS 479.93MiB；conf≥0.50 冻结；DSH r1 条件→集成方全闭+重建绑定） |

| 已闭环 Task（原「未完成 / 下一阶段」表；新行随收口追加） | 状态 | 建议 Owner / Reviewer | 说明 |
|---|---|---|---|
| [M2-P1](tasks/M2-P1.md) Regionless Detection Fan-out and Guard Rebinding | **done**（integration=`a174fb9c`） | Antigravity / DeepSeek Harness（`approved_with_conditions`，P2 已处置） | fixed base=`33826641`、tip=`59acb340`；修复=诊断报告 §5.4 单函数 + R0–R5/N1–N7 全落测；[release evidence](../verification/M2-P1/release-33826641.md)、[集成记录](../verification/M2-P1/integration-record/integration.md)。 |
| [M2-IPC1](tasks/M2-IPC1.md) Production Core Lifecycle + Read-only Library Vertical Slice | **done**（integration=`04c1394a`） | Antigravity / DeepSeek Harness（r1 changes_requested → r2 approved_with_conditions，裁决已实施） | tip=`5556fc8e`；seam 冻结全落地（含方案 B 冻结面保持）；[release evidence](../verification/M2-IPC1/release-a54bb8c9.md)、[集成记录](../verification/M2-IPC1/integration-record/integration.md)。 |
| [M2-AC2](tasks/M2-AC2.md) Data Integrity Acceptance | **done**（integration=`9d3c1db5`） | ZCode / DeepSeek Harness（r1 changes_requested → r2 approved_with_conditions，C1-C3 已闭） | fixed base=`61f9db9b`、tip=`c3ee8dbe`（11 场景）；纯验收（产品代码零改动）：source hash、Managed Copy、人工修改、Lock、current/pinned Revision + 端到端恢复全 PASS；[release evidence](../verification/M2-AC2/release-61f9db9b.md)、[集成记录](../verification/M2-AC2/integration-c3ee8dbe/integration.md)。 |
| [M2-AC3](tasks/M2-AC3.md) Provider Fail-closed Acceptance | **done**（integration=`cac374855b6e6a4310f557ae362d34d0572cd649`；DSH r1 `approved_with_conditions`，C1-C5 已关闭） | ZCode / DeepSeek Harness | fixed base=`319c5e4b`、tip=`a63d3372`（8 场景）；纯验收（产品代码零改动）：Provider 未配置/网络失败/部分失败时命令计划与页面的 fail-closed 语义（不产出半成品、typed 错误可诊断、可恢复、源文件零风险）全 PASS；[release evidence](../verification/M2-AC3/release-319c5e4b.md)、[集成记录](../verification/M2-AC3/integration-a63d3372/integration.md)。 |
| [M2-FIX-STUB-DECODER](tasks/M2-FIX-STUB-DECODER.md) core_service stub decoder signature fix | **done**（integration=`121a281cbf65f62c57b177efc44fa4649b11c9ae`；DSH r1 `approved_with_conditions` 0×P0/P1/P2，C1 tip 复跑、C2 范围复算、P3-4 回滚红证均已闭） | ZCode / DeepSeek Harness | base=`f5d91425`、delivery=`5cacebfa`、终 tip=`69250a39`；`core_service.py` +3/-1 签名修正 + `tests/core/test_stub_decoder.py` 先红后绿；集成 head 复跑 2/76/32 passed 全绿；遗留 P3-2（mime_type 断言）、P3-6（同族 stub：font_catalog/layout_engine/compositor=object()）留 planning；[集成记录](../verification/M2-FIX-STUB-DECODER/integration-69250a39/integration.md)。 |
| [M2-AC4](tasks/M2-AC4.md) Reader Export Lineage + Library Page-count/Unknown Semantics Acceptance | **done**（integration=`fc99182147bccc89d9bd9124dd17d15b1d428e21`；DSH r1 `approved_with_conditions`，P1-1..P1-3 集成方修正、P2 裁决落字；F-1/F-2 缺陷证据 accepted） | ZCode / DeepSeek Harness | fixed base=`a5529181`、tip=`890f0c74`（11 场景 = 9 passed + 2 xfailed，回归 32 passed + 2 xfailed）；纯验收（产品代码零改动）：缺陷 F-1（export history 无 included_stale/missing ids）、F-2（page_count 无 unknown/已知度通道，定性收窄）以 xfail(strict)+探针固化，AC1/AC4 判 FAIL(部分)、AC2 PASS(a,c)/部分不满足(b)、AC3 PASS、AC5 PASS；[release evidence](../verification/M2-AC4/release-a5529181.md)、[集成记录](../verification/M2-AC4/integration-890f0c74/integration.md)。 |
| [M2-FIX-EXPORT-LINEAGE](tasks/M2-FIX-EXPORT-LINEAGE.md) Export history 补 included_stale/missing page ids（F-1 修复） | **done**（integration=`d71883ec9a6c6fccb14b62908c02790bb3beb99c`；DSH r1 `approved_with_conditions` → r2 `approved`，C1-C6 已关闭；F-1 关闭、xfail 移除，套件现 34 passed+1 xfailed 仅剩 F-2） | ZCode / DeepSeek Harness | fixed base=`8b0d9040`、delivery=`297c9655`（r2 amend 自 0ec1f052，最终 tip=`d395ef70`）；方案 A：`scope_snapshot_json` 加 included_stale/missing 两键（数据源=ExportResult 同源），`schema.py`/`reading_export.py` 零改动；legacy 三通道兼容场景新增；P3-7 并发评估采信未修（候选留 planning）；[release evidence](../verification/M2-FIX-EXPORT-LINEAGE/release-8b0d9040.md)、[集成记录](../verification/M2-FIX-EXPORT-LINEAGE/integration-d395ef70/integration.md)。 |
| [M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN](tasks/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN.md) ListBooks page_count unknown/已知度通道（F-2 修复候选） | **done**（integration=`699610291f1536a1a1dbda62ba73f2587def1d91`；DSH r1 `approved_with_conditions` → r2 `approved_with_conditions`（C1=通过 C2=通过，C3/C4/C5 集成关闭，双轮报告已归档 doc/reviews/）；F-2 关闭、xfail 移除，m2_acceptance 全绿 **35 passed, 0 xfailed**） | ZCode / DeepSeek Harness | fixed base=`6199df48`、delivery=`852a92ae`（r2 amend 自 `f4f77808`→`c3f8bb3a`→最终 tip=`b6cb1af2`）；None 通道三侧（Python `int \| None`+handler `get(book_id)` SQL 零改动、Rust `Option<u32>`+serde 测试、TS `number \| null`+`LibraryPanel ?? "—"`）；known-0 与 null 三侧对称锁定（含 r2 TS 正向用例+`??`→`||` 变异红证）；契约 rev 1.2（§5 widening+§3.2 授权例外指针）；f02 默认线程三连 1 失败 2 绿+单线程对照绿 → 既有资源通道潜伏 flake 另立 flaky Task 建议（不计本 Task 回归）；[release evidence](../verification/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN/release-6199df48.md)、[集成记录](../verification/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN/integration-b6cb1af2/integration.md)。 |
| [M2-FIX-F02-RESOURCE-CHANNEL-FLAKY](tasks/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY.md) Resource channel 等长重写拒检并发缺口（f02 flaky 诊断+修复） | **done**（integration=`aa2f99b8170de4205ccd0be23acb10c7fa367fc1`；DSH r1 `approved_with_conditions` 0×P0/P1，C1 final-tip 绑定复跑闭合、C2 选(b) 集成落字；f02 重新定性为真实产品安全缺口并修复） | ZCode / DeepSeek Harness | base=`2b81f91c`、delivery=`fd31a7ad`、最终 tip=`3cef4831`（claim=`6a404c19`）；诊断 3/3 捕获（dump 铁证 NTFS mtime 同 tick 碰撞 `mtime_delta_100ns=0` → `verified_mtime` 短路放行等长重写）；修复=移除 mtime 短路每请求 `stream_digest` 全量重验 + `CachedGrant` 状态字段清理 + `f02_equal_size_rewrite_stability_loop` 50 轮（集成红证：回退旧代码 loop FAILED=101 判别力实证）；性能 342µs→18424µs/request（1 MiB warm debug，~50x 冻结接受，release NOT_RUN）；集成复跑全绿（cargo 34 passed×3+loop+单线程+pytest 35/77，postmerge 同）；dead-code（`CachedGrant.grant`）显式接受并登记 follow-up；[DSH r1](reviews/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY-fd31a7ad-dsh-r1.md)、[集成记录](../verification/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY/integration-3cef4831/integration.md)。 |
| [M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF](tasks/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF.md) Resource channel digest 重验成本优化（单趟 hash+capture / per-chunk digest）与 GrantCache 死结构收敛 | **done**（integration=`bc2529f02dfbd3c378d5e9cd4c9f7ac2ecfe4f15`；DSH r1 `approved_with_conditions` 0×P0/P1/P2，C1-C4 集成方闭合；f02 断言逐字保持、判别力红证保持） | ZCode / DeepSeek Harness | fixed base=`956e6c3a`、delivery=`5d7cff11`、终 tip=`510202ac`；单趟 hash+capture 消除三读+TOCTOU 残留、GrantCache 删净、测试更名、loop 守卫；release perf −14.6%/−24.4%/−17.9%（闭合 F02 P3-9）；per-chunk 不实施（`host_bridge.py` 禁止路径，书面留痕）；集成 head 复跑 cargo 34+loop+pytest 35+vitest 31 全绿；[release evidence](../verification/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF/release-956e6c3a.md)、[集成记录](../verification/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF/integration-510202ac/integration.md)。 |
| [M2-AC5](tasks/M2-AC5.md) Windows Packaging & Clean-start Acceptance | **done**（integration=`9db08dc7548b70e8f4ee1d42e70e2e0c15838e63`；DSH r1 `approved_with_conditions` 5×P2 → 返修 → r2 `approved` 0×P0/P1/P2；剩余 P3 集成落字/候选） | ZCode / DeepSeek Harness | fixed base=`6f79c040`、delivery=`e3740b25`、终 tip=`0541b86b`；NSIS + onedir 四入口自包含 sidecar；clean-start GATE PASS 25/25（宿主 %APPDATA% 零触碰）；fail-closed 无 python 回落；cargo 38+1/pytest 35/vitest 31 全绿；fresh checkout 须先 build_sidecar.ps1（根治候选）；[release evidence](../verification/M2-AC5/release-6f79c040.md)、[集成记录](../verification/M2-AC5/integration-0541b86b/integration.md)。 |
| Real docTR qualification | 前置 `done`（`51229d49`，DSH r5 `approved`）；用户口径裁决 2026-09-30（coverage 主判定/生产 pad 正式+抵消附报/Precision 下界不作 Gate）→ 正式 run [M2-DOCTR-QUAL-RUN](tasks/M2-DOCTR-QUAL-RUN.md) **`done` @`e8c9c120`——Formal Result: FAIL**（block_coverage Recall 0.4776 < 0.92；MeanCov 0.7531 / severe 0.0385 PASS；Precision 0.1250=非 Gate 下界；DSH r1 APPROVED_WITH_MINOR_ISSUES）；候选流程 C1-C5 已产出（C1 GT 盲区人工校准 First、C3 DBNet Hold、C4 manga 域检测器为唯一可能逼近 Gate 的候选类），实施须另行释放 | ZCode（Owner）/ DeepSeek Harness（Review） | 正式结论已出；调参/换模型属新 Task。 |
| [M2-FIX-DIGEST-SEEK-2GIB](tasks/M2-FIX-DIGEST-SEEK-2GIB.md) Resource channel read_through 64 位 seek（DIGEST-PERF P3-5 清算，Goal 2026-09-30 T1） | **done**（integration=`a0ffc4f342d50c7b7cf2fb7f682c1717120c1a86`；DSH r1 `approved_with_conditions` → r2 返修 → r2 定点复审（仅余 C4）→ r3 关闭 → 集成放行；post-merge 44 passed EXIT=0；release=`d1a4b406`、delivery=`9fa92475`→`8a1bc1e8`；[集成记录](../verification/M2-FIX-DIGEST-SEEK-2GIB/integration-record/integration.md)） | ZCode / DeepSeek Harness | base=`d1a4b406`（release，parent 915cea99）；SetFilePointerEx 64 位 + fail-closed；256 MiB 内行为零变化（DSH 行级重建证实）。 |
| [M2-AC5-BUILD-FRESH-CHECKOUT](tasks/M2-AC5-BUILD-FRESH-CHECKOUT.md) fresh checkout 构建链根治（build.rs 可诊断 sidecar 缺失 + build_sidecar.ps1 增量短路；Goal 2026-09-30 T2） | **done**（integration=`1a96f536d75d7525d51a3da453be1497ad978d78`；DSH r1 `approved_with_conditions`（AC1-AC5 全 PASS 附证据条件）→ r2 证据返修（热态实验实证确定性触发）→ r2 定点复审（仅余机制句，集成落字改正）；post-merge 44 passed EXIT=0；[集成记录](../verification/M2-AC5-BUILD-FRESH-CHECKOUT/integration-record/integration.md)） | ZCode / DeepSeek Harness | base=`251f7425`；不加 beforeBuildCommand（理由记录 README）；tauri.conf.json 零改动。 |
| [M2-TA2C-TOOLING-GAPS](tasks/M2-TA2C-TOOLING-GAPS.md) comic_golden_suite 工具清算（TA2C P3-6 source_url 白名单与目录命名 + P3-10 checksum_inventory 运行时消费与断言覆盖；Goal 2026-09-30 T3） | **done**（integration=`04165c76fab939e4a106f4a87f5045d674e8dac3`；DSH r1 `approved` 一次通过（0×P0/P1/P2）；post-merge 34 passed EXIT=0；7×P3 登记候选；[集成记录](../verification/M2-TA2C-TOOLING-GAPS/integration-record/integration.md)） | ZCode / DeepSeek Harness | base=`f3d684eb`；素材零改动、目录未重命名（受管快照断言替代）。 |
| [M2-RG1](tasks/M2-RG1.md) M2 Release Gate（Windows 本机口径） | **done**（integration=`b796bed3cb3d79b2d4208b29f3e53c956a018dee`；DSH r1 `approved_with_conditions` 1×P1/3×P2 → gate v2 返修 → r2 `changes_requested` → 纯文字收口；两轮条件全闭） | ZCode / DeepSeek Harness | fixed base=`875eb818`、release=`79510a8b`、delivery=`e752ba39`、终 tip=`8e0100ba`；用户裁决"把本机视为干净widows环境。若本机通过，则视为pass"=干净机基座；**GATE PASS 25/25**：AC2 console policy（PE Subsystem=2 + `CREATE_NO_WINDOW`×4 + CW0 阳性对照真命中）/ AC3 冷启动测录（app 46.9/49.9/160.2 ms 等，无阈值）/ AC4 四入口 stdio 闭环 + warn 审查 + M2-AC5 回归 25/25 / AC5 Win11 已验证、Win10 NOT_RUN；集成复跑 cargo 38+1 / pytest 35 / vitest 31 / diff-check 全绿；[release evidence](../verification/M2-RG1/release-875eb818.md)、[集成记录](../verification/M2-RG1/integration-b796bed3/integration.md)。 |
| [M2-DOCTR-QUAL-PREFLIGHT](tasks/M2-DOCTR-QUAL-PREFLIGHT.md) docTR qualification 三项前置（受控权重 / 隔离环境 / 评测基座） | **done**（integration=`51229d49`；DSH 五轮 r5 `approved` 定点 6/6 closed；确定性复现） | ZCode / DeepSeek Harness | release=`480f12a2`、base=`14720230`；fast_base 生产 pin + db_resnet50 对照权重快照、隔离 GPU 环境 Py3.12+cu128 实测、KO webtoon 10 case 511 regions 评测基座三层判定口径；首跑基线 FAIL 稳健（Recall 0.4776）；[handoff](handoffs/M2-DOCTR-QUAL-PREFLIGHT-baseline.md)。 |
| [M2-TA2B](tasks/M2-TA2B.md) JA/KO 开放素材池（2026-09-30 裁决：Manga109 前置永久取消） | **done**（integration=`fae0d8f6`；DSH r1 `approved_with_conditions` → r2 `approved` 0×P0/P1/P2） | ZCode / DeepSeek Harness | tip=`98766fdc`；densho810 BJ 官方免费 1/3/5 卷（避 JASRAC 乐曲页）+ BJ01-BJ12 case + P&C +17 页 + Manga109 取消标注 + OpenMantra 隔离 optional；pytest 47 passed；**densho810 利用报告义务已履行（2026-09-30 用户经其 Gmail 发送至 info@densho810.com；原「Agent 不代发」约束经用户本人明确指令授权代发解除）**。 |
| [M2-TA3-A](tasks/M2-TA3-A.md) 应用级 E2E Smoke（5 case=BJ02/BJ06/K01/K02/K11） | **done**（integration=`5dc69d16`；DSH r1→r2 条件全闭 approved） | ZCode / DeepSeek Harness | 5 case 全链 COMPLETED pipeline_failures=0（真 docTR detect + mock OCR/translate + 生产 inpaint/render/export）、export 哈希双向复算一致、pytest 82 passed；真 docTR 下 LOCK_CHANGED 未复现=L-1 候选（已由 DIAG-002 核实关闭）；TA3-B 维持暂缓。 |
| [DIAG-M2-LOCK-CHANGED-REPRO-002](tasks/DIAG-M2-LOCK-CHANGED-REPRO-002.md) M2-TA3-A L-1 缺口核实（mock detect 复现） | **done**（integration=`1faf6c1b`、收口 `56edc335`；DSH r1→r2 `approved_with_conditions` 0×P0/P1/P2） | ZCode / DeepSeek Harness | S2 @`d268a170` 复现 LOCK_CHANGED（DIAG-001 §3 四项预测全对齐）→ 终局结论=缺口真实存在过、已由 M2-P1 修复（S1 HEAD 全链绿）、retry 自愈实证；**L-1 不再保留缺陷候选**；Owner worktree 保留 @`2c13530b`。 |
| [DOC-FIX-LOCK-CHANGED-STALE-COMMENTS](tasks/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS.md) 两处过时「known planner gap」注释最小修正 | **done**（integration=`1970512d`、集成修正=`e81b4220`；DSH r1 `approved_with_conditions` → r2 `approved`） | ZCode / DeepSeek Harness | 零指令流（co_code）变化+注释-only diff 证明、test_acceptance_loop 4 passed；L-7 ④⑤ 行号换算登记；M2-TA3-A manifest tip 上 14/15 属预期（字节级 15/15 须在其交付 worktree 复算）；Owner worktree 保留 @`8ab9045b`。 |
| [M2-TA3-B](tasks/M2-TA3-B.md) 20-case 端到端质量验收·阶段一（阈值定义+OCR 冒烟+case 选取+阶段二计划） | **done**（integration=`81cf5125`、merge=`97450992`；DSH r1 `changes_requested` 7×P2 → 返修 `cad45622` R1-R18 全 closed → r2 `approved` 0×P0/P1/P2） | ZCode / DeepSeek Harness | base=`c4039415`、branch_base=`53fdfcc6`、delivery=`b057ec69`、被复核 tip=`cad45622`；阈值提案六阶段（OCR CER 三层 GT/translate SFX≥70% n≥15/对白三维 5 分制/inpaint 无数值 Gate/渲染确定性）、OCR 隔离 venv 双引擎冒烟 OK（paddle 3.x bytes 静默忽略=修复候选）、20 case 确定性选取（SHA256 实算 20/20、TA3-A 超集）、阶段二计划（真实 API 序列）；R6 探针 PASS（生产 adapter+wrapper 单 region conf 0.998）；运行时清单 1-6 全闭；**阶段二 BLOCKED_ON_USER 翻译 endpoint 二选一**；main 490+1skipped 0 failed；[DSH r1](reviews/M2-TA3-B-dsh-r1.md)/[r2](reviews/M2-TA3-B-dsh-r2.md)、[集成记录](../verification/M2-TA3-B/integration.md)。 |
| [M2-TA3-B2](tasks/M2-TA3-B2.md) 20-case 端到端质量验收·阶段二（正式 qualification run，DeepSeek remote） | **done**（integration=`952e8ddb`、merge=`228b70c5`；DSH r1 `changes_requested` 1×P1（R1 确定性根因链，集成方定案 export=Run1 渲染复制）→ Owner 返修 R1-R15 → r2 收敛 N1 → 集成闭合） | ZCode / DeepSeek Harness | base=`521d0bdd`、release=`69137837`、delivery=`3c8801b7`、被复核 tip=`7922a3fc`；**正式结论=诚实 Gate FAIL（pipeline_failures=10）**：ja 10/10 全链 OK、ko 9 case 生产域缺口（F1 ogkalu webtoon 0 候选 ×6 / F2 Qt 256MB ×3）、ko G1 CER 0.0556≤0.20 PASS（directional n=6 下偏）、ja G1 NOT_AUTOMATED（O-3 实证）、确定性语义修正+F5 裁决移交、AC4 工作表 n=26 待用户终审；~100 请求 key 零明文；[quality-report](../verification/M2-TA3-B/quality-report.md)、[集成记录](../verification/M2-TA3-B/integration-phase2.md)、[DSH r1](reviews/M2-TA3-B2-81e5ad81-dsh-r1.md)/[r2](reviews/M2-TA3-B2-7922a3fc-dsh-r2.md)；裁决移交：建议 A/B、F5 重定义、SFX→translate 入口。 |
| [M2-DETECT-WEBTOON-DIAG](tasks/M2-DETECT-WEBTOON-DIAG.md) webtoon 长条漫 ogkalu 0 候选适配器级诊断（建议 A 第一步） | **done**（integration=`e1d939fa`、merge=`29942c30`；DSH r1 `changes_requested` → 返修 R1-R11 含探针 schema v2 重跑 → r2 `approved`） | ZCode / DeepSeek Harness | base=`8996ca55`、被审头=`b311f52f`/返修 tip=`a867ff49`；**根因=整页无 letterbox 各向异性重缩放**（640×640 垂直压缩 ~97×；决定性证据=同页同权重仅改分辨率块级 0→193 合并前文本框，NMS 数据 30/33 重叠带+IoU mean 0.848）；修法 A tiling 推荐（契约零变更）、B 路由 docTR 基线、C 排除；修复 Task 释放口径已定（5 张 webtoon_long_strip/生产 region Gate/K19 归 F4/CPU 预算）；[diagnosis](../verification/M2-DETECT-WEBTOON-DIAG/diagnosis.md)、[DSH r2](reviews/M2-DETECT-WEBTOON-DIAG-a867ff49-dsh-r2.md)。 |
| [M2-IMPORT-ALLOC-LIMIT](tasks/M2-IMPORT-ALLOC-LIMIT.md) 大图导入 QImageReader allocation limit（建议 B） | **done**（integration=`499a3da7`、merge=`f9c15e45`；DSH r1 `approved_with_conditions` → 条件返修 R1-R10 全 closed → r2 `approved` 0×新 P0/P1/P2） | ZCode / DeepSeek Harness | fork=`8996ca55`（授权基线 8e0de8d0）、delivery=`a5c8adf1`、返修 tip=`400046ef`；修复=setAllocationLimit(2047MiB) 每 decode 断言（域实测 345.6MiB ×5.9 余量）+MOBI render 重收紧 256MiB+typed 错误（errorString 300+3 字符）；机制锁定用例（同输入仅限值不同）+红态归档 4F/1P；K07/K09/K10 生产通道真图 PASS+对照组（256 拒/2047 过，native_stderr 原文归档）=**TA3-B2 F2 升级一级证据**；五套件含 import_formats 550+1sk（post-merge main 537+1sk 0 failed）；[集成记录](../verification/M2-IMPORT-ALLOC-LIMIT/integration.md)、[DSH r2](reviews/M2-IMPORT-ALLOC-LIMIT-400046ef-dsh-r2.md)。 |
| [M2-QUAL-DETERM-CALIB](tasks/M2-QUAL-DETERM-CALIB.md) F5 确定性 Gate 重定义校准 | **done**（integration=`7a0286ef`、merge=`20e17d52`；DSH r1 `approved_with_conditions` 4×P2 → R1-R14 全 closed 复跑逐值一致 → r2 `approved`） | ZCode / DeepSeek Harness | 双轨 Gate（remote=相似度 median≥0.95/min≥0.70 normalized+覆盖前置+NO_DATA 豁免；mock=字节逐位；`--determinism-track` fail-closed）；校准=K11/BJ02 复跑对（浮动带 [0.75,0.875]）+合成漂移；[集成记录](../verification/M2-QUAL-DETERM-CALIB/integration.md)、[DSH r2](reviews/M2-QUAL-DETERM-CALIB-8926f49c-dsh-r2.md)。 |
| [M2-DETECT-WEBTOON-TILING](tasks/M2-DETECT-WEBTOON-TILING.md) webtoon 长条漫 tiling 检测修复（建议 A 第二步） | **done**（integration=`e1c040bf`+companion、merge=`061fbb60`；DSH r1 **PASS 零阻塞**，9×P3/P4 登记紧邻 follow-up） | ZCode / DeepSeek Harness | fork=`f99a6c55`、delivery=`29a7f5b5`；tiling+坐标回映落 `detection_manga.py`（触发 h/w>4.0、env `NEWMANGA_DETECTOR_TILING_*` 默认 4.0/1024/128/0.5 fail-fast）；qualification **GATE PASS 5/5**（K01 180 region/193 框逐值复现 DIAG、20.1s≤25s；K02/K04/K05/K08 全 >0；阈值曲线+690×690 对照+K19/BJ02 零变化）；+45 测试红 44F→73P；[DSH r1](reviews/M2-DETECT-WEBTOON-TILING-29a7f5b5-dsh-r1.md)、[qualification](../verification/M2-DETECT-WEBTOON-TILING/qualification-report.md)。 |
| [M2-TASKS-BACKFILL-MULTIREGION](tasks/M2-TASKS-BACKFILL-MULTIREGION.md) executor backfill 逐 region 跟进 | **done**（integration=`27701679`、merge=`fd452f37`；DSH r1 有条件通过 → 返修 R1-R7 全 closed → r2 `approved`） | ZCode / DeepSeek Harness | backfill 逐 region fan-out（与恢复路径同 `_plan_region` 语义；SFX gate plan 层 per-region 生效）；R1 terminal 账目同步（断言红态 terminal 12≠17 独立验证）；R4/R5 证据归档；**R2 裁决请求=单 region SFX 页 primary 重决策**（违反 D06 §85 反例已登记）；主 venv 双侧 530+1sk/575+1sk 0 failed；[DSH r2](reviews/M2-TASKS-BACKFILL-MULTIREGION-95469952-dsh-r2.md)。 |
| [M2-SETTINGS-UI-SFX-POLICY](tasks/M2-SETTINGS-UI-SFX-POLICY.md) 设置页 SFX 策略键接入 | **blocked_on_contract**（UI/测试已交付 @`efad4b71`：SettingsPanel+SettingsClient+17 新测试 vitest 48 全绿；IPC 勘察=产品无设置页且无任何 settings 通道，触 M2-C1 冻结契约即停） | ZCode / DeepSeek Harness | 解除前提=settings IPC 通道 slice（`settings_get`/`settings_update_section`，形状已 pin handoff）；通道契约裁决待用户确认；[handoff](handoffs/M2-SETTINGS-UI-SFX-POLICY-8c798aed.md)。 |
| [M2-TASKS-PRIMARY-SFX-GATE](tasks/M2-TASKS-PRIMARY-SFX-GATE.md) primary region 重决策（裁决②） | **done**（integration=`0820d3d5`、merge=`16eb80ce`；DSH r1 有条件通过 0×P0/P1，2×P2 文档/口径级条件闭合） | ZCode / DeepSeek Harness | fork=`1c3ac590`、delivery=`19bf234a`；primary 与 secondaries 统一 `_plan_region` live-Region 重决策（页级决策链退役、SFX 门全域生效 D06 §85、terminal 账目统一 progress 1.0）；DSH 反例红态固化（SFX primary+manual ⇒ RUN≠SKIP_POLICY）；等价性护栏（非 SFX step-for-step 全等）；双侧 627+1sk/630+1sk 精确复现；post-merge 576+1sk；follow-ups：except 收窄/translate-primary 覆盖；[DSH r1](reviews/M2-TASKS-PRIMARY-SFX-GATE-19bf234a-dsh-r1.md)。 |
| [M2-TA3-B2-KO-RERUN](tasks/M2-TA3-B2-KO-RERUN.md) TA3-B2 ko qualification 重跑（裁决③） | **进行中**（第二波释放；前置=PRIMARY-SFX-GATE 集成已满足） | ZCode / DeepSeek Harness | ko 10 case 重跑（TILING 解锁 F1+ALLOC 解锁 F2）；成本受控（先单 case 试算）；K19/F4 维持登记；[Task](tasks/M2-TA3-B2-KO-RERUN.md)。 |
| [M2-SFX-E2E-MATERIAL](tasks/M2-SFX-E2E-MATERIAL.md) SFX 端到端验证+素材扩展（裁决④全权授权） | **done**（merge=`68b351ad`；DSH r1 有条件通过 1×P1 → 返修 R1-R10 全 closed → r2 `approved`） | ZCode / DeepSeek Harness | **SFX 翻译链端到端闭环实证**（BJ06：gate 放行 8/8/译文落库 8/8 非空/ハチン→啪 文化对等/speech 零扰动）；素材许可先行（densho810 vol03 三条 JASRAC 清单复证）+3 页入池（cases.json 97→100）；**检测段=真实瓶颈**（chiqui7 BJ 毛笔竖排 0 命中+误路由 speech 乱译进渲染损害形态=域扩展优先级输入）；成本 68 请求 40.7k est token；[sfx-e2e-report](../verification/M2-SFX-E2E-MATERIAL/sfx-e2e-report.md)、[DSH r2](reviews/M2-SFX-E2E-MATERIAL-f53dd445-dsh-r2.md)。 |
| [M2-DETECTION-HYGIENE](tasks/M2-DETECTION-HYGIENE.md) 检测/调度面 hygiene 一揽子 | **done**（merge=`45bae782`；r1 有条件 5×P2 → 返修 → **r2 抓 P0**（R1 lazy split 被红态归档 checkout-恢复抹除——BACKFILL R9 同款第二次）→ 修复+事故登记+流程修正 → r3 P0 closed） | ZCode（主会话直接实现，周配额约束） / DeepSeek Harness | TILING R1/R3（`_tiling_trigger_ratio` eager+几何旋钮 lazy 于 tiled 分支=普通页零变化恢复；空/空白 env typed 拒绝 +10 用例红→绿+行为级红态归档）；BACKFILL N1（except 收窄白名单+commit 路径包护+桩测试按 DSH 配方重建钉 post-R3 语义含 DB_FAILED 码弱点登记）；SETTINGS-IPC R7/R8 集成方闭合；三套件 **611+1sk**/cargo 46+1ig/vitest 49；[DSH r2](reviews/M2-DETECTION-HYGIENE-02b6d2a2-dsh-r2.md)、[r3](reviews/M2-DETECTION-HYGIENE-52585b64-dsh-r3.md)、[集成记录](../verification/M2-DETECTION-HYGIENE/integration.md)。 |
| [M2-TA3-B3-KO-FULLRUN](tasks/M2-TA3-B3-KO-FULLRUN.md) ko 全量补跑（裁决①②③⑥⑦） | **done @merge `0f872d1b`**（DSH r2 approved；8/8 全链 export OK；F1/F2 关闭；预算 950,954/220 万=43.2%；相似度 known-limitation 落 §5；invalid-env+双 driver 事故登记） | ZCode / DeepSeek Harness | [报告](verification/M2-TA3-B/ko-fullrun-report.md)、[Task](tasks/M2-TA3-B3-KO-FULLRUN.md)。 |
| [M2-SETTINGS-IPC-CHANNEL](tasks/M2-SETTINGS-IPC-CHANNEL.md) settings IPC 通道（裁决①） | **进行中**（Owner 执行中：M2-C1 rev+Rust 两命令+core 桥+前端接通） | ZCode / DeepSeek Harness | 解除 SFX-UI blocked_on_contract；写入端前置校验（SFX-ENTRY R4 教训）；[Task](tasks/M2-SETTINGS-IPC-CHANNEL.md)。 |
| [M2-TA3-B2-KO-RERUN](tasks/M2-TA3-B2-KO-RERUN.md) TA3-B2 ko qualification 重跑（裁决③） | **done**（交付 @`60a04ba3`；DSH r1 `approved` 有条件 0×P0/P1——纯文档返修 R1-R11 全 closed @`0ba046b8`） | ZCode / DeepSeek Harness | **事件驱动停跑**：K02 试算实证 F1 解锁（93 region 全链 export OK、93/93 译文）；外推 63.2-209 万 est token 超停跑口径→7 case 停等 §7 裁决（实际 ≈347 请求 ≈20.4 万）；CER 0.0556 6/6 逐位复现；K11 相似度 Gate 自然 FAIL（min 0.4615=CALIB 局限 8 首测）；sfx.policy=translate 语义验证（素材缺口）；DeepSeek 故障窗 115 分钟 typed fail-closed 韧性实证；三控件落地（--determinism-track/--sfx-policy/--meter-translation）；**§7 七项裁决移交用户**（含 50 万红线追认 §7.5）；[ko-rerun-report](../verification/M2-TA3-B/ko-rerun-report.md)、[DSH r1](reviews/M2-TA3-B2-KO-RERUN-36971e97-dsh-r1.md)。 |
| [M2-SETTINGS-UI-SFX-POLICY](tasks/M2-SETTINGS-UI-SFX-POLICY.md) 设置页 SFX 策略键接入 | **done**（blocked_on_contract 已解除：通道集成 @`fab3ca56` 连带本 Task 入 main；UI 在 SETTINGS-IPC 分支内完成接通（AC4），连带 DSH r1 review 覆盖） | ZCode / DeepSeek Harness | SettingsPanel（三值 select+保存+作用域提示）+SettingsClient+types；17 新测试 vitest 48→49（47 既有零修改=pin 零漂移）；SSR 快照登记；[handoff](handoffs/M2-SETTINGS-UI-SFX-POLICY-8c798aed.md)。 |
| [M2-SETTINGS-IPC-CHANNEL](tasks/M2-SETTINGS-IPC-CHANNEL.md) settings IPC 通道（裁决①） | **done**（integration merge=`fab3ca56`；DSH r1 `approved_with_conditions` 0×P0/P1，R1 旁路同步/R2/R3/R10 集成闭合+**M2-AC5 GATE 重跑 PASS 25/25**） | ZCode / DeepSeek Harness | M2-C1 rev 1.2→1.3（§5.3 两命令 wire shape，错误码零新码）；stdio 既有桥 envelope minor 1→2（DETECT-3 先例）；Python handler+写入端 typed fail-closed（sfx.policy enum 门）；Rust production-only 两命令+allowlist 三视图同步；前端零漂移接通；测试 pytest 602+1sk/cargo 46+1ig（含真实 sidecar e2e）/vitest 49；旁路同步=packaging 门 CS-L1 minor 2+RC2 EXPECTED 5→7+frozen-probe 历史证据标注；[DSH r1](reviews/…)、[handoff](handoffs/M2-SETTINGS-IPC-CHANNEL-45e15524.md)。 |
| [M2-SFX-TRANSLATE-ENTRY](tasks/M2-SFX-TRANSLATE-ENTRY.md) SFX 翻译策略可配置入口（裁决④） | **done**（integration=`e0ba396a`、merge=`1eccc99d`；DSH r1 `approved_with_conditions` 0×P0/P1，条件由集成方闭合） | ZCode / DeepSeek Harness | `settings["sfx"]["policy"]`（skip/translate/manual，默认 SKIP 零变化+非法值 fail-fast）；缺环修复=装配闭包向 create_region 传参（translate 门生产可达）；**作用域=仅新建 region**（r1 R1 登记）；21 新增测试；post-merge 530+1sk 0 failed；后续=React 设置页（Qoder）/region 级策略入口/backfill 调度片；[集成记录](../verification/M2-SFX-TRANSLATE-ENTRY/integration.md)、[DSH r1](reviews/M2-SFX-TRANSLATE-ENTRY-a377a25a-dsh-r1.md)。 |
| [M2-OCR-PADDLE3X-1](tasks/M2-OCR-PADDLE3X-1.md) 生产 ocr_local.py PaddleOCR 3.x 适配修复 | **done**（integration=`53326278`、merge=`96cdb297`；DSH r1 `approved_with_conditions` 1×P2+5×P3+3×P4 条件全闭） | ZCode / DeepSeek Harness | base=`69137837`（release `19adf0e0`）、delivery=`15ef29ab`、集成 tip=`53326278`；诊断=**ALWAYS_EMPTY**（bytes 输入校验层拒绝，错误文本风险面不存在）；修复=bytes→BGR ndarray+`enable_mkldnn=False`+双形状解析（numpy box 物化）；R3 fail-closed 收紧+2 回归测试（ocr_local 19 例）；红绿判别 9/9（声称 10/7 实跑 9/8 差异已如实登记）；探针复跑逐位一致；main 509+1skipped 0 failed；遗留台账（TA3-B2 wrapper 适配/mkldnn 性能对照/2.x 实测/det 孤立 crop）见 [integration.md](../verification/M2-OCR-PADDLE3X-1/integration.md)、[DSH r1](reviews/M2-OCR-PADDLE3X-1-15ef29ab-dsh-r1.md)。 |
| [M2-SFX-SEM-1](tasks/M2-SFX-SEM-1.md) SFX 翻译语义第一刀：拟声词文化对等转换 | **done**（integration=`abf30a1a`、集成修正=`0349be25`+`da780b7d`；DSH r1 `approved_with_conditions` 0×P0/P1，条件由集成方闭合） | ZCode / DeepSeek Harness | `RegionInput.region_type` widening（默认 speech+枚举 fail-closed）、prompt SFX 特化段（≤6 字符禁直译）、user_text 携带类型、TASK-002 契约 rev 1.1；根因=region_type 在 bundle→provider 请求间丢失；跨层 REGION_TYPE_VALUES 断言落地前抓到集成方自身类型 bug；SFX OCR/重绘 out of scope。 |
| [M2-SFX-DETECT-DOMAIN-EXT-DIAG](tasks/M2-SFX-DETECT-DOMAIN-EXT-DIAG.md) SFX 检测域扩展诊断（BJ 域缺口+五方案） | **done @merge `7dd5e5ff`**（零 src；双 DSH r1 交叉验证；根因=域外+结构性发现=无重叠仲裁；排序⑤＞③＞①＞④＞②移交三件裁决；**裁决回执 2026-10-04：①维持现状+UI 缓解 / ②fine-tune 暂不投入 / ③重叠仲裁授权**） | ZCode / DeepSeek Harness | [报告](verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/diagnosis-and-options.md)、[Task](tasks/M2-SFX-DETECT-DOMAIN-EXT-DIAG.md)。 |
| [M2-REGION-OVERLAP-ARBITRATION](tasks/M2-REGION-OVERLAP-ARBITRATION.md) region 创建跨 provider 重叠仲裁（裁决③） | **done @merge `38e4e487`**（DSH r1 changes_requested 3×P1→编排裁决 (a) 修订 AC2→r2 approved_with_conditions，4 项文本条件集成方闭合；composite 层 sfx 驱动定向改标 IoU 0.90 保守域+`NEWMANGA_SFX_ARBITRATION[_IOU]` typed 旋钮；**结构性定案（双独立复算确认）=纯几何重叠反向不可分离**（域内 0.8865 vs BJ13 误路由 0.490/0.550）→BJ13 自动闭合挂召回恢复依赖链（此前 no-op）；KO 10 case off/on 逐位一致（最高 IoU 0.1325）+BJ06 逐位一致；三套件 627+1sk） | ZCode / DeepSeek Harness | [报告](verification/M2-REGION-OVERLAP-ARBITRATION/arbitration-report.md)、[Task](tasks/M2-REGION-OVERLAP-ARBITRATION.md)、[r1](reviews/M2-REGION-OVERLAP-ARBITRATION-b27c826f-dsh-r1.md)/[r2](reviews/M2-REGION-OVERLAP-ARBITRATION-e43cc5db-dsh-r2.md)。 |
| [M2-SFX-MISROUTE-UI-MITIGATION](tasks/M2-SFX-MISROUTE-UI-MITIGATION.md) SFX 误路由缓解 UI 设计切片（裁决①） | **done @merge `4d77a778`**（用户改派 Qoder→ZCode @`fb5d56c6`；DSH r1 approved_with_conditions 4×P2+6×P3+7×P4→18 条全闭合 @`42be3c11`→r2 approved_with_conditions（N-1..N-4 集成方闭合）；E1-E4 视觉+不对称状态机+D1-D10 数据缺口表（RC-1..RC-5 登记零 widening）+13 断言；零产品代码；**产品实现 blocked_on Workbench React 页+region 通道**） | ZCode / DeepSeek Harness | [设计](doc/design/M2-SFX-MISROUTE-UI-MITIGATION/design.md)、[Task](tasks/M2-SFX-MISROUTE-UI-MITIGATION.md)、[r1](reviews/M2-SFX-MISROUTE-UI-MITIGATION-c92eaddd-dsh-r1.md)/[r2](reviews/M2-SFX-MISROUTE-UI-MITIGATION-3f589a0b-dsh-r2.md)。 |
| [M2-SFX-FINETUNE-PREFLIGHT](tasks/M2-SFX-FINETUNE-PREFLIGHT.md) SFX 微调 V1 技术预检（T0） | **done @merge `dedb97b2`**（DSH r1 approved_with_conditions→r2 approved_with_conditions 12/12 闭合；**关键实证：chiqui7 无 .pt 训练权重，续训受阻**（五端点 raw+usedStorage 全 revision 排除）；**编排裁决=采纳 A′**：Ultralytics 官方 yolo11s-seg.pt 基座+四类全标+合成数据；显存实测 b8=7488MiB/67 img/s；导出链冒烟 EXIT=0；四类监督选项3 不可行定案） | ZCode / DeepSeek Harness | 训练线第一环收官；T1b 标注轮待释放（schema 已由 T1a 冻结）。 |
| [M2-SFX-DATA-INFRA](tasks/M2-SFX-DATA-INFRA.md) 训练数据基础设施（T1a） | **done @merge `71a9a84e`**（2026-10-04；schema 冻结+分组隔离 pinned+双去重+可恢复+合成渲染 24 样本精确 GT 1.71e-13px+导入 58；DSH r1/r2 changes_requested→r3 approved_with_conditions→r4 条件闭合，报告入 doc/reviews/；38 tests） | ZCode / DeepSeek Harness | 数据线地基；批量生成=T1b（弱负样本策略/竖排/底图来源输入已备）。 |
| [M2-SFX-SYNTH-BG-AUTO](tasks/M2-SFX-SYNTH-BG-AUTO.md) SFX 合成底图自动 provider | **done**（2026-10-04 全 AC 闭合含真实冒烟留证；全自动内嵌=Playwright 持久登录态+缺口自动触发+fail-closed；DSH r1/r2 changes_requested→r3 approved_with_conditions→r4 docfix） | ZCode / DeepSeek Harness | T1a 底图来源工具化；端到端样册=T1b 输入。 |
| [M2-REGION-RETYPE-CONTRACT](tasks/M2-REGION-RETYPE-CONTRACT.md) Region 改标契约冻结（T5a） | **done @merge `b4b995ab`**（DSH r1 changes_requested P1-1+3×P2→返修 7f390ca6→r2 **approved** 12/12 闭合零新发现；SetRegionType wire+RegionListSummary 读取 DTO+C1-C7 并发/P1-P4 持久化 11 条断言+「忽略」RULED 处理动作/EV-8 RULED 按全局配置重快照；零新错误语义；**runtime 未实现，T5b 另行释放**；EV-8 转 CLOSED 集成注记已落设计稿） | ZCode / DeepSeek Harness | T5 线第一环收官；T5b Core 实现/T5c 样本导出器就绪待释放。 |
| [M2-SFX-ANNOTATE-R1](tasks/M2-SFX-ANNOTATE-R1.md) SFX 标注轮 R1（T1b 两阶段） | **done**（2026-10-04 @merge 6bfa1cde；DSH r1+r2 approved_with_conditions；AI 代审 413 单元=共识 397（96.1%）+仲裁 16 残留 0；三集+合成 324+YOLO 导出；**BJ 域正集 0=A′ 输入条件未满足，§8.1 对照表+T2 处置选项交裁决**） | ZCode+用户 / DeepSeek Harness | 下游 T2 训练（释放待用户裁决，BJ 正集 0 前置）。 |
| [M2-SFX-ANNOTATE-R2](tasks/M2-SFX-ANNOTATE-R2.md) SFX 标注轮 R2（T1b-R2 扩标轮） | **done**（2026-10-04 @merge 84f952b3；DSH r1 approved_with_conditions 条件全闭；素材 KO+5/BJ+10 入池 25/25+15/15 达标；扩审 19 单元双 AI；三集 train 345/571；**BJ 正集 0→5 页 11 框毛笔竖排首批正样本**；challenge 空集明许分支） | ZCode / DeepSeek Harness | T2 训练释放待用户裁决（challenge 空集处置+量级确认）。 |
| [M2-SFX-TRAIN-V1](tasks/M2-SFX-TRAIN-V1.md) SFX 训练 V1（T2） | **done**（2026-10-04 @merge 35cb3db0；DSH r1 approved_with_conditions 条件全闭+运行级验证 5/5；管线验证达成（训练/导出/冒烟全通）；模型全面欠拟合如实登记（BJ 0/5·KO 0/56）；T3/T4 裁决材料已呈报） | ZCode / DeepSeek Harness | 用户裁决 SFX 线下一步（R3 扩标/V2 调参/暂停）。 |
| [M2-SFX-TRAIN-V2](tasks/M2-SFX-TRAIN-V2.md) SFX 训练 V2（T2-V2） | **done**（2026-10-05 @merge 784e585b；DSH r1 approved_with_conditions 条件全闭；own-manga 558 页接入→train 901/2304；**BJ 考卷 V1 0/5→V2B 5/5 零误检**；结构性发现=KO 长条页 letterbox 口径瓶颈（三方全 0/56）归 T3） | ZCode / DeepSeek Harness | 用户裁决：T3 释放（含 KO 口径实验）/T4 条件/暂停。 |
| [M2-KO-TILE-CALIB](tasks/M2-KO-TILE-CALIB.md) KO 长条页推理口径校准（T3 前置） | **done**（2026-10-05 @merge f84b56b7；DSH r1→r2 定点复审→返修全闭；四组矩阵 letterbox 全 0/56 vs tile chiqui7 56/56（同源复现口径）/v2b 35/56——**口径瓶颈确证**；KO Gate 提案冻结 tile_ov128+非派生 GT 裁决项） | ZCode / DeepSeek Harness | T3 Gate 采信（非派生 KO GT 裁决前置）。 |
| [M2-SFX-ANNOTATE-R3](tasks/M2-SFX-ANNOTATE-R3.md) SFX 标注轮 R3（T1b-R3） | **done**（2026-10-05 @merge 5efa052e；DSH r1 approved_with_conditions C1 落框+C2 先例更正全闭；BJ26-37 入池；22 单元双 AI；**BJ 正集 8 页 18 框全部有效**；train-v3 904/2311 考卷不动） | ZCode / DeepSeek Harness | T3 备数据完成；R3-MISS 补画立项建议。 |
| [M2-SFX-GATE-T3](tasks/M2-SFX-GATE-T3.md) SFX 正式评测门（T3） | **done**（2026-10-05 @merge 27817412；DSH r1 approved_with_conditions 12/12 条件闭+r2 建议集成；Gate 定义冻结 v1.0+v1.1 追加；R3-MISS BJ32-35 15 框 ai-direct 首例；KO 非派生 GT 135 框；36 格评测 ALL CELLS 复算 PASS；**G1/G2 v2a 双 FAIL 丧失资格、v2b 全定资格硬门 PASS（考卷 5/5 P1.0+KO 非派生 0.3556≥0.3037）+G8 license 审计 PASS——T4 切换等用户裁决**；零 src） | ZCode / DeepSeek Harness | T4 生产切换材料终稿已呈报（tile 化 17-81s/页性能预算+G7 补证前置）。 |
| [M2-SFX-T4-SWITCH](tasks/M2-SFX-T4-SWITCH.md) SFX 生产切换 V2B（T4） | **done**（2026-10-06 @用户裁决「三件都同意」；DSH r1 approved_with_conditions 0×P0/P1/P2 条件闭 @bd23eaa8；AC1-AC5 全 PASS @merge `cff4923e`——G7 补证 PASS 部署就绪+pin 944e8114 切换+SHA 门反向验证+回退实测+回归锚迁移基线一致；NSIS NOT_RUN=授权面外） | ZCode / DeepSeek Harness | ~~闭环后 T5-TILE 解锁~~ **T5-TILE 已解锁**。 |
| [M2-SFX-T5-TILE-KO](tasks/M2-SFX-T5-TILE-KO.md) SFX KO tile 化生产分支（T5-TILE） | **done**（2026-10-06；DSH r1 approved_with_conditions 0×P0/P1/P2 条件闭 @306f5040；AC1-AC5 全 PASS @merge `5e70af4e`——tile 路由+逐位复现 35/56+48/135 硬证据+性能双档呈报+T4 承接 r1 P3-2 闭合） | ZCode / DeepSeek Harness | ~~部署形态呈报用户终选~~ **已呈报等终选**（CPU 10.46s/页 vs GPU DML 1.08s/页；GPU 启用需新 Task）。 |
| [M2-SFX-GPU-EP-1](tasks/M2-SFX-GPU-EP-1.md) SFX 推理 EP 切换 GPU/DML | **done**（2026-10-06；DSH r1 changes_requested P1-1 返修闭+r2 approved_with_conditions 建议集成 @merge `931a6d03`——directml 1.24.4+EP 配置化默认 dml+回退三键审计（get_providers 读回反推）+GPU/CPU 漂移≤2e-06 门零翻转+KO 页 1.1s/页≈10×+GATE 25/25 NSIS +50.06MiB） | ZCode / DeepSeek Harness | ~~完成后 SFX 线 KO 域生产时延 ~1.1s/页~~ **已达成**。 |
| [M2-SFX-TILE-WIDTH-CALIB-1](tasks/M2-SFX-TILE-WIDTH-CALIB-1.md) tile 路由宽≠600/690 逐宽校准（批准进行2 候选③） | **done**（2026-10-06 @merge `14b5ec03`；DSH r1 approved_with_conditions 0×P0/P1，P2 docs-only 集成闭 @ea6fbc2c——真实素材零「宽≠600/690 长条页」→重采样+合成两条授权路径 10 档 14 页；结论 **(a) 维持现状**：域内重采样档召回与原生 690 档同量级、letterbox 面 10 档×双 conf 全零、原生锚点逐页复现 T5 parity；零 src、deploy-report §3① 缺口关闭） | ZCode / DeepSeek Harness | §3④ GPU 档 ms/tile 16.3-18.4ms（≈6.5-12×）补强登记；上限侧 700-1024 tile 未测（「提高宽上限」类提案须另开 Task）。 |
| [M2-SFX-EPFAIL-AUDIT-1](tasks/M2-SFX-EPFAIL-AUDIT-1.md) SFX run-time EPFail 通道审计（批准进行2 候选①） | **done**（2026-10-06 @merge `9a29e742`；DSH r1 changes_requested→返修→r2 approved 建议集成 0×新 P0-P3，P4×4 集成顺笔闭——每 detect get_providers() 读回（0.03μs）+`sfx_ep_runtime_check` 条件透传至生产 provenance（**r1 P1-1 抓到 composite 装配面丢弃**，透传修复+composite 用例+形态 2 钉子）；回归 1828+1sk+1 failed 等量递增） | ZCode / DeepSeek Harness | 实机真实 EPFail NOT_RUN（wrapper 重放+stub 覆盖）；GPU-EP-1 INIT 三键仍不在生产 composite provenance（device 同名冲突，遗留候选）。 |
| [M2-PROD-SFX-PROBE-1](tasks/M2-PROD-SFX-PROBE-1.md) packaged sfx-detect 探针（批准进行2 候选②） | **done**（2026-10-06 @merge `177b356a`；DSH r1 approved_with_conditions（0×P0/1×P1/3×P2/5×P3）→集成顺笔返修→r2 **approved_with_conditions 实质通过** 0×P0/0×P1（C3 判据代码面+重跑证据双闭合；P3-3 特别裁决认可集成方实测登记——r1「range check 应为空」预期被实测推翻）→残留 R-1/R-2/R-3+P4×8 顺笔闭合——第五 frozen 入口 `sfx_detect_probe.exe`（catalog_loader 先例形 additive 零契约修订）；安装后 frozen 进程内 DML 真实推理候选=1、conf=0.9046692252159119 与 v2b 锚点同源同页（页文件 sha256 逐位一致、conf 差 1.79e-7 在 GPU↔CPU 漂移窗口 ≤2e-06 内）、三键 dml/dml/null；GATE 25/25；NSIS 553.65MiB=+64.72MiB（**第二份 torch/transformers 闭包**非 onnxruntime 面——DSH P2-1 归属更正，取舍三选一登记选 (a) 接受）；r1fix 终态判据（frozen is True+权重 pin+三键在场）真实安装态重跑 4/4 PASS） | ZCode / DeepSeek Harness | 闭合语义=**闭包面**（≠core_service 进程内 detect 可达≠manga slice，禁把命令面扩展当收敛条件）；main.rs 四入口注释/CS-Z3 名单留 src-tauri 下次开面（P4-1）；PROD-DETECT-2 裁决⑥ NOT_RUN sfx slice 由此闭合。 |
| [M2-WORKBENCH-REACT-1](tasks/M2-WORKBENCH-REACT-1.md) Workbench React 页第一刀+region 通道（用户释放三件·候选 A） | **done @merge `108bf113`**（2026-10-06 释放 @`630c3f51`；依赖已就绪侦察实证：region 两命令契约 rev1.4 §5.4+runtime PROTOCOL_MINOR=3+Tauri 9 命令 allowlist 全在位，唯一硬缺口=D5 几何读取面——本 Task 含 additive 契约修订裁量+React 页壳读取面闭环+commandSurface pin deferral 闭合；交付即解除 IMPL-1 派发阻塞） | ZCode / DeepSeek Harness（Qoder 非 author UI/UX 复审可选） | E1-E4 视觉/改标交互属 IMPL-1；VM 24 方法全量对等/RC-1/RC-4/RC-5 不在范围。 |
| [M2-SFX-MISROUTE-UI-IMPL-1](tasks/M2-SFX-MISROUTE-UI-IMPL-1.md) SFX 误路由缓解 UI 产品实现（用户释放三件·候选 B） | **done** @merge `b355757c`，2026-10-06 释放 @`630c3f51`（设计契约 M2-SFX-MISROUTE-UI-MITIGATION FROZEN §4.1 不对称状态机+E1-E4 的实现切片；RC-1 suspect 字段归本 Task 裁量含或登记 NOT_IN_SCOPE） | ZCode / DeepSeek Harness（Qoder 非 author UI/UX 复审可选） | Reader 页级提示条不实现（Reader React 页不存在）；派发时序=真依赖非配额）；**2026-10-07 全链闭环 done @merge `b355757c`（收口 commit）**：Owner=编排接管（子 agent 配额耗尽）；DSH r1 changes_requested（P1-1 错误呈现不可达）→r1fix 全闭→r2 approved_with_conditions（条件文档级）→r2fix 全闭；AC1/AC4=PARTIAL 如实登记（undo 禁用/零 DOM 环境）/AC2=PASS（RC-1 裁定不含经 DSH 核验）/AC3/AC5=PASS；vitest 77→105+build EXIT=0+pytest 1847 等量；遗留=RC-4 域命令面 Task（三禁用入口）|
| [M2-RC4-DOMAIN-COMMANDS](tasks/M2-RC4-DOMAIN-COMMANDS.md) 撤销、重渲染与修订历史 Core 域命令面（RC-4） | **done @merge `0a7e0d5b`**（2026-10-07；base=`44421008` 契约 rev 1.6 envelope minor 3→4；Core/Rust 37110749+58b3706d 三命令 `list_region_revisions`/`restore_region_revision`/`rerender_page`+preview 轮换 fail-closed；React a27b3443→6f3544a2 三入口解禁+10 秒 undo；组合 Gate→DSH r1 approved_with_conditions（0×P0/P1）→r1 返修 Core e495910f+React 7021d34c→组合 Gate 绑 7c9d3a32→DSH r2 **approved_with_conditions 0×P0/P1/P2、r1 三 blocking 全闭**→r2 条件 N-1..N-5 全闭（N-1 core_bridge.rs test-only 注入面追认、N-2/N-5 五条 git 原始日志、N-3 SKIPPED 原行、N-4 注释 6a7b4c3d）→main fast-forward `0a7e0d5b`；post-merge pytest 1859+1sk+3 failed（catalog 既有+ui_shell 两例 main 基线同样失败）/cargo 53+1ign/vitest 118+build 全绿；报告 doc/reviews/M2-RC4-DOMAIN-COMMANDS-{5954bb4b-dsh-r1,1e6b58b9-dsh-r2}.md） | Codex Executor / DeepSeek Harness / Codex（本次 ZCode 代行收口） | AC1-AC5 全 PASS；test-only Rust 注入面追认先例（N-1）；遗留候选=derived 预览 GC（RC4-12）、MISSING_REQUIRED_INPUT category 澄清（RC4-10）、ui_shell QML 环境敏感失败核实。 |
| [M2-TEST-CATALOG-DRIFT-CLEAR-1](tasks/M2-TEST-CATALOG-DRIFT-CLEAR-1.md) test_catalog 断言漂移清算（exact snapshot 反模式修复） | **done @`8412ccfd`**（2026-10-07；test-debt 轻量 Task 直落 main；漂移事实=三次授权素材 Task append-only 追加 97→100 `40a8ceec`/→110 `9b9916af`/→122 `579af8a5`，agy 非作者 Review approve 独立验证前缀不变性；修复=exact-total pin 改唯一性不变量+`>=100` M2 契约冻结下界+BJ13/14/15 真实留态例外集；终结 2026-10-01 起每轮 BASELINE_FAILURE 单列负担；全量 1860+1sk+2 failed） | Codex Executor / Antigravity（非作者） / Codex（代行收口） | manifest 零改动；后继素材 Task 直接 append-only，测试不再 pin 总数。 |
| [M2-UI-SHELL-ENV-1](tasks/M2-UI-SHELL-ENV-1.md) ui_shell QML 事件投递环境敏感失败定性+Quick 后端固定 | **done @`195995bb`**（2026-10-07；test-debt 轻量 Task 直落 main；决定性对照=默认 RHI 2 failed / software 5 passed / offscreen 5 passed（会话窗口 surface 非交互时合成鼠标投递丢失），测试/QML/PySide6 pin 零漂移核实；处置=tests/ui_shell/conftest.py 固定 `QT_QUICK_BACKEND=software`（保留 Windows 平台+字体库），零 src/ui/QML/契约改动；agy 非作者 Review approve 0×P0-P3；全量 **1862+1sk+0 failed 基线 failed 清零**） | Codex Executor / Antigravity（非作者） / Codex（代行收口） | Legacy 产品边界保持（只动测试基础设施）；根因子"锁屏/断连"子定性为会话状态假设，处置正确性由 RHI↔software 对照独立支撑。 |
| [M2-PAGE-RESOURCE-RESOLVE-1](tasks/M2-PAGE-RESOURCE-RESOLVE-1.md) 页→资源解析 wire 命令 resolve_page_resource（Workbench 页图自动加载第一刀） | **done @merge `9e242b0c`**（2026-10-07；契约 M2-C1 rev 1.7/协议 minor 5；确定性键 `page-original-{page_id}`+derived 只读根发布+产物存活自愈+suffix 门共用解码面权威；Rust 13 命令面+ACL 生成物补入库；React resolve effect 自动喂图+pageIdRef 复检；DSH r1 changes_requested→rework `1620d0b7`→r2 approve_with_conditions；focused 417/cargo 54+1ign/vitest 124/全量 **1871+1sk+0 failed**） | Codex Executor（ZCode 代行） / DeepSeek Harness（非作者 r1+r2） / Codex（ZCode 代行收口） | 手输 resource id 降级调试后备保留；页导航列表（list_pages/list_chapters）保持「明确不做」，为下一候选的冻结依据。 |
| [M2-PAGE-NAV-PROJECTION-1](tasks/M2-PAGE-NAV-PROJECTION-1.md) 页导航投影命令 list_chapters/list_chapter_pages（Workbench 页列表三级下钻第一刀） | **done @merge `657af2e3`**（2026-10-07；契约 M2-C1 rev 1.8/协议 minor 6；零新错误码未知父 id 空数组 fail-soft；repository 透传不加新查询方法；Rust 15 命令面+PAGE_NAV 生产-only 组+ACL 生成物随交付入库；React PageListPanel 三级下钻 page 点击驱动 resolve→image 链+手输保留；DSH r1 approve_with_conditions→rework `14f4b1e6`（PR-01..10 fixed）→r2 approve→hardening `00538a14`（N-01..05）；focused 422/cargo 55+1ign/vitest 136/全量 **1876+1sk+0 failed**） | Codex Executor（ZCode 代行） / DeepSeek Harness（非作者 r1+r2） / Codex（ZCode 代行收口） | GetReaderProjection/跨页联动/页缩略图保持「明确不做」；生产-only 族常量成员独立加固（PR-11 deferred）登记为技术债候选。 |
| [M2-DERIVED-GC-1](tasks/M2-DERIVED-GC-1.md) derived 只读根 orphan/死行启动清理第一刀（RC4-12 PARTIAL mitigation） | **done @merge `44859014`**（2026-10-07；零 wire/零 schema/零 React+Rust；orphan 文件+死行两类失败类等价回收+双层逃逸检查+装配 fail-soft；RC4-12 轮换增长主路径保持 open=后续候选；DSH r1 approve_with_conditions→rework `4edec70a`（C-1..C-3）→r2 approve→polish `9c9c7e55`（N-01/02/04）；focused 430/full **1884+1sk+0 failed**/cargo 55+1ign/vitest 136） | Codex Executor（ZCode 代行） / DeepSeek Harness（非作者 r1+r2） / Codex（ZCode 代行收口） | 按引用回收旧 preview 需 page 关联或 grant 联动，设计空间较大须谨慎冻结。 |
| [M2-CATEGORY-CLARIFY-1](tasks/M2-CATEGORY-CLARIFY-1.md) MISSING_REQUIRED_INPUT envelope category 澄清为 unavailable（RC4-10，非修订） | **done @merge `21865f7d`**（2026-10-07；映射拆分一处+2 用例+M2-C1 §5 RerenderPage 注记；code/message/retryable 零变化；DSH r1 approve_with_conditions→docs-only 返修 `e0ab0444`（零代码改动 git 级证据）→r2 approve；focused 432/full **1886+1sk+0 failed**/cargo 55+1ign/vitest 136） | Codex Executor（ZCode 代行） / DeepSeek Harness（非作者 r1+r2） / Codex（ZCode 代行收口） | PR-02/03/05（§8 反向指针/unavailable 语义注记/RC4-08 category 分叉）登记下一轮契约澄清候选。 |
| [M2-RESOLVE-DEBOUNCE-1](tasks/M2-RESOLVE-DEBOUNCE-1.md) Workbench 页资源解析逐键 debounce（PAGE-RESOLVE PR-10 闭合） | **done @merge `65d500e6`**（2026-10-07；`resolveDebounceMs` prop 产品默认 300/测试注入 0；cleanup 双层取消+stillCurrent 复检；零 Python/Rust/契约；DSH r1 approve_with_conditions→返修 `acc3a578`（C-1 措辞/C-2 绑定日志/PR-02 busy 断言）→r2 approve；vitest **138**/build 0/full **1886+1sk+0 failed**/cargo 55+1ign） | Codex Executor（ZCode 代行） / DeepSeek Harness（非作者 r1+r2） / Codex（ZCode 代行收口） | region 读循环逐键 invoke=deferred 后续候选（r1 C-1）。 |
| [M2-REGION-DEBOUNCE-1](tasks/M2-REGION-DEBOUNCE-1.md) Workbench region 读循环逐键 debounce（RESOLVE-DEBOUNCE r1 C-1 残留闭合） | **done @merge `0cb15092`**（2026-10-07；`regionDebounceMs` prop 产品默认 300/测试注入 0；refreshRegions 函数本体零改动=写后刷新即时；零 Python/Rust/契约；DSH r1 a_w_c（PR-01 P2 判别力）→路径 B 返修 `2cfa7e6f`→r2 a_w_c（N-01）→按 r2 option 2 收口承载 `80db177d`；vitest **140**/build 0/full **1886+1sk+0 failed**/cargo 55+1ign） | Codex Executor（ZCode 代行） / DeepSeek Harness（非作者 r1+r2） / Codex（ZCode 代行收口） | 残留登记：手工 resource 输入逐键 image 读取/quiet-window busy/300ms 写后刷新独立判别用例（均 P4 小件）。 |
| [M2-SFX-BJ13-RECALL-1](tasks/M2-SFX-BJ13-RECALL-1.md) BJ13 召回恢复链（用户释放三件·候选 C） | **done @merge `ec460508`**（2026-10-06 释放 @`630c3f51`；合同锚点=ARBITRATION Task :60 依赖链注记+arbitration-report :56 重审条件——v2b 生产链 BJ13/14/15 sfx 召回实测（探针零 src，BJ13 从未进任何评测集=「召回恢复是否已发生」无登记证据）→恢复则仲裁阈值域重审切片（提案不自行改冻结域）/未恢复则剩余选项（补标翻案/补画扩展/维持现状）登记交裁决）；**2026-10-06 全链闭环 done @merge `ec460508`（收口 commit）**：DSH r1 approved_with_conditions→r1fix 全闭+同形态逐位互证→r2 approved 0×新 P0/P1/P2；BJ13 部分恢复仅信号面（4.4x/42x+类别翻转 text→sfx；conf≥0.5 参照框召回 0/2=Slipknot 假阳性）/BJ14、15 未恢复/BJ06 对照 5/8 逐框 <0.5px 锚；**呈报用户：AC2 提案维持 0.90+AC3 推荐序 ③②①** | ZCode / DeepSeek Harness | BJ13 走 letterbox 路径（2946×4167 非 tile 口径）；零 src 或最小 src；冻结回归锚 BJ06 8 region+KO parity+三套件基线。 |
| [M2-REGION-RETYPE-CORE](tasks/M2-REGION-RETYPE-CORE.md) Region 改标 Core 实现（T5b） | **done @merge `d8019810`**（DSH r1 approved_with_conditions（Q1 追认 runner 同步）→返修 `0f88cbcd`→r2 **approved** 12/12；rev 1.4 全链+11 断言两层红绿+real-sidecar 测试+PROTOCOL_MINOR 2→3 旁路追认+GATE 25/25 重跑（M2-AC5/raw 还原+自有 raw 副本 retype-m2ac5-*）；五目录 793 passed；test_catalog 100vs97 pre-existing 实证转登记） | ZCode / DeepSeek Harness | Workbench UI 实现前置就绪；test_catalog 断言更新小切片登记。 |
| [M2-SFX-CORRECTION-EXPORTER](tasks/M2-SFX-CORRECTION-EXPORTER.md) 纠错样本导出器（T5c） | **done @merge `66871d5d`**（DSH r1 changes_requested（P1-1 bbox xywh 误读静默产错框，被测试钉死）→返修 `669146a1`（T1a helper 修复+rgO 判别+判别力数值验证）→r2 approved_with_conditions 条件全闭；scanner 按 rev 1.4 语义+资格判定+双形态导出+--yolo-scope；50 tests 红绿；真库冒烟 CORRECTIONS_EMPTY=expected 补跑） | ZCode / DeepSeek Harness | 纠错积累链采集端就绪；T5 线全收官（契约+Core+导出器）。 |

```mermaid
flowchart TD
  %% ✓ = done（已集成 main）；O = Owner；R = 非作者 Reviewer（均为 DSH 除非另注）；虚线 = 候选/后续，未释放不实施
  GOV["GOV-001 治理基线 · O:Codex ✓"] --> D1["M2-D1 耦合审计 · O:DSH ✓"]
  D1 --> I1["M2-I1 核心装配缝 · O:ZCode ✓"]
  D1 --> I2["M2-I2 Qt-free 逻辑抽取 · O:AGY ✓"]
  D1 --> R1["M2-R1 Qt 运行时验证 · O:DSH ✓"]
  D1 --> UI1["M2-UI1 React 视觉契约 · O:Qoder ✓"]
  I1 --> C1["M2-C1 Typed IPC 契约 1.0 · O:ZCode ✓"]
  I2 --> C1
  R1 --> C1
  UI1 --> C1
  C1 --> S1["M2-S1 大媒体可行性 · O:DSH ✓"]
  S1 --> S2["M2-S2 安全验证原型 · O:ZCode ✓"]
  S2 --> C2["M2-C2 契约 1.1（T1-T7） · O:ZCode ✓"]
  C2 --> S3["M2-S3 Tauri 协议探针 · O:ZCode ✓"]
  S3 --> RC1["M2-RC1 资源通道 runtime · O:ZCode ✓"]
  RC1 --> RC2["M2-RC2 命令面/sidecar 加固 · O:ZCode ✓"]
  RC2 --> AC1["M2-AC1 端到端验收 · O:ZCode ✓"]
  AC1 --> DGR["DIAG-REGIONLESS 诊断 · O:DSH ✓"]
  DGR --> P1["M2-P1 regionless 重绑修复 · O:AGY ✓"]
  P1 --> IPC1["M2-IPC1 生产 IPC 竖切 · O:AGY ✓"]
  IPC1 --> AC2["M2-AC2 数据完整性验收 · O:ZCode ✓"]
  AC2 --> AC3["M2-AC3 Provider fail-closed 验收 · O:ZCode ✓"]
  AC3 --> AC4["M2-AC4 导出谱系/页数语义验收 · O:ZCode ✓"]
  AC4 -->|"发现 F-1"| FXE["FIX-EXPORT-LINEAGE · O:ZCode ✓"]
  AC4 -->|"发现 F-2"| FXL["FIX-LISTBOOKS-PAGECOUNT · O:ZCode ✓"]
  IPC1 --> FXS["FIX-STUB-DECODER · O:ZCode ✓"]
  FXL --> FXF["FIX-F02 资源通道安全缺口 · O:ZCode ✓"]
  GOV -. 独立 Legacy 诊断支线 .-> DIO["DIAG-READING-EXPORT-001 · O:DSH ✓"]
  DIO --> FXA["FIX-A 等待语义 · O:ZCode ✓"]
  FXA --> FXB["FIX-B 心跳生命周期 · O:ZCode ✓"]
  FXB --> FXC["FIX-C 生产接线 · O:ZCode ✓"]

  FXF --> PKG["M2-AC5 打包/clean-start · O:ZCode ✓"]
  PKG --> RG["M2-RG1 Release Gate（本机口径） · O:ZCode ✓"]
  FXF -.-> DP["DIGEST-PERF digest 性能优化 · O:ZCode ✓"]

  %% Goal「M2 遗留技术债清算」（2026-09-30 达成：T1/T2/T3）
  DP -.-> T1["FIX-DIGEST-SEEK-2GIB 64 位 seek（T1） · O:ZCode ✓"]
  PKG -.-> T2["AC5-BUILD-FRESH-CHECKOUT 构建链根治（T2） · O:ZCode ✓"]
  TA2C -.-> T3["TA2C-TOOLING-GAPS 工具清算（T3） · O:ZCode ✓"]

  %% 测试素材家族（2026-09-29 用户授权；2026-09-30 裁决后 T-D2/T-D3 闭环）
  RG --> TA1["M2-TA1 素材基础设施 · O:Codex ✓"]
  TA1 --> TA2A["M2-TA2A JA 公开素材 · O:Codex ✓"]
  TA2A --> TA2C["M2-TA2C No-HF 素材迁移 · O:Codex ✓（集成=ZCode 代行）"]
  TA1 -.-> TA2B["M2-TA2B 开放素材池（T-D2） · O:ZCode ✓"]
  TA2C -.-> TA3A["M2-TA3-A E2E Smoke 5 case（T-D3） · O:ZCode ✓"]
  TA3A -.-> TA3B["M2-TA3-B 20-case 质量 qualification 阶段一 · O:ZCode ✓（阈值/冒烟/选样/计划）"]
  TA3B -.-> TA3B2["M2-TA3-B2 阶段二 20-case run · O:ZCode ✓（诚实 Gate FAIL：ko 缺口 F1/F2；ko G1 CER 0.0556 PASS directional）"]
  TA3B -.-> OCRFIX["M2-OCR-PADDLE3X-1 PaddleOCR 3.x 生产适配修复 · O:ZCode ✓"]
  TA3B -.-> WDIAG["M2-DETECT-WEBTOON-DIAG webtoon 检测诊断 · O:ZCode ✓（根因=整页各向异性重缩放；tiling 可行性实测）"]
  TA3B -.-> ALLOC["M2-IMPORT-ALLOC-LIMIT 大图导入上限 · O:ZCode ✓（2047MiB+MOBI 收紧；F2 升一级证据）"]
  TA3B -.-> CALIB["M2-QUAL-DETERM-CALIB F5 确定性校准 · O:ZCode ✓（双轨 Gate：remote=相似度/mock=字节）"]
  TA3B -.-> SFXE2["M2-SFX-TRANSLATE-ENTRY SFX 翻译入口 · O:ZCode ✓（sfx.policy 可配置；默认 SKIP 零变化）"]
  TA3B -.-> TIL["M2-DETECT-WEBTOON-TILING tiling 检测修复 · O:ZCode ✓（GATE PASS 5/5；ko 检测解锁）"]
  TA3B -.-> BKF["M2-TASKS-BACKFILL-MULTIREGION backfill 逐 region · O:ZCode ✓"]
  TA3B -.-> SUI["M2-SETTINGS-UI-SFX-POLICY 设置页接入 · O:ZCode ✓（通道集成后解除，UI wired）"]
  TA3B -.-> PSG["M2-TASKS-PRIMARY-SFX-GATE primary 重决策 · O:ZCode ✓（裁决②；SFX 门全域）"]
  TA3B -.-> KOR["M2-TA3-B2-KO-RERUN ko 重跑 · O:ZCode ✓（F1 解锁实证 K02；7 case 停等 §7 裁决；CER 0.0556 复现）"]
  TA3B -.-> SIP["M2-SETTINGS-IPC-CHANNEL settings 通道 · O:ZCode ✓（M2-C1 1.3；GATE 重跑 PASS 25/25）"]
  TA3B --> FULL["M2-TA3-B3-KO-FULLRUN ko 全量补跑 · done @0f872d1b（8/8 全链 export OK；F1/F2 关闭；950954/2.2M）"]
  TA3B -.-> HYG["M2-DETECTION-HYGIENE hygiene 一揽子 · O:ZCode ✓（r2 抓 P0 checkout-restore 抹除；事故登记+流程修正）"]
  TA3B -.-> SMAT["M2-SFX-E2E-MATERIAL SFX 端到端+素材 · O:ZCode ✓（BJ06 8/8 闭环；检测盲区=域扩展优先级输入）"]
  SFXE -.-> DEXT["M2-SFX-DETECT-DOMAIN-EXT-DIAG BJ 域缺口诊断+方案评估 · done @7dd5e5ff（域外=主根因；裁决回执 10-04）"]
  SMAT -.-> DEXT
  DEXT -.-> ARBIT["M2-REGION-OVERLAP-ARBITRATION 重叠仲裁 · done @38e4e487（裁决③；几何反向不可分离定案；BJ13 闭合挂召回恢复链）"]
  DEXT -.-> UIM["M2-SFX-MISROUTE-UI-MITIGATION 缓解 UI 设计 · done @4d77a778（设计契约；实现 blocked_on Workbench）"]
  DEXT -.-> T0["M2-SFX-FINETUNE-PREFLIGHT 技术预检 · done @dedb97b2（A′ 裁决：官方基座+四类全标）"]
  DEXT -.-> T1A["M2-SFX-DATA-INFRA 数据基础设施 · done @71a9a84e（T1a 并行）"]
  UIM -.-> T5A["M2-REGION-RETYPE-CONTRACT 改标契约 · done @b4b995ab（rev1.4 冻结；T5b/T5c 待释放）"]
  T0 -.-> T1B["M2-SFX-ANNOTATE-R1 标注轮 R1 · done @6bfa1cde（AI 代审 413 单元）"]
  T1B -.-> T1BR2["M2-SFX-ANNOTATE-R2 扩标轮 · done @84f952b3（BJ 正集 0→5 页 11 框；challenge 空集交裁决）"]
  T1BR2 -.-> T2["M2-SFX-TRAIN-V1 训练 · done @35cb3db0（管线验证达成；模型欠拟合如实；V2 杠杆已呈报）"]
  T2 -.-> T2V2["M2-SFX-TRAIN-V2 · done @784e585b（BJ 考卷 0/5→5/5；KO 口径瓶颈发现归 T3）"]
  T2V2 -.-> KOCAL["M2-KO-TILE-CALIB 口径校准 · ready（tile vs letterbox 对照）"]
  T2V2 -.-> T1BR3["M2-SFX-ANNOTATE-R3 扩标轮 · ready（BJ 正集 6 框→几十框）"]
  KOCAL -.-> T3["M2-SFX-GATE-T3 正式评测门 · done @27817412（v2b 唯一全硬门通过；T4 等用户裁决）"]
  T1BR3 -.-> T3
  T3 -.-> T4SW["M2-SFX-T4-SWITCH 生产切换 V2B · done @cff4923e（G7 补证 PASS+pin 944e8114 切换+回退实测）"]
  T4SW -.-> T5TILE["M2-SFX-T5-TILE-KO tile 化分支 · done @5e70af4e（逐位复现硬证据+性能双档呈报）"]
  T5TILE -.-> GPUEP["M2-SFX-GPU-EP-1 EP 切换 GPU/DML · done @931a6d03（@用户裁决 GPU；KO 页 ≈10×）"]
  GPUEP -.-> TILEW["M2-SFX-TILE-WIDTH-CALIB-1 宽≠600/690 逐宽校准 · done @14b5ec03（结论=(a) 维持现状零 src；§3① 关闭）"]
  GPUEP -.-> EPFAUD["M2-SFX-EPFAIL-AUDIT-1 run-time EPFail 审计 · done @9a29e742（读回+sfx_ep_runtime_check 透传 provenance）"]
  GPUEP -.-> PROBE["M2-PROD-SFX-PROBE-1 packaged sfx-detect 探针 · done @177b356a（第五 frozen 入口；NOT_RUN sfx slice 闭包面闭合）"]
  UIM -.-> WBReact["M2-WORKBENCH-REACT-1 Workbench React 页第一刀+region 通道 · done @108bf113（D5 闭合 rev1.5；已解除 IMPL 阻塞）"]
  WBReact -.-> IMPL["M2-SFX-MISROUTE-UI-IMPL-1 缓解 UI 产品实现 · done @b355757c（E1-E4+状态机；undo/rerender 禁用待 RC-4 域命令面）"]
  ARBIT -.-> BJ13R["M2-SFX-BJ13-RECALL-1 BJ13 召回恢复链 · done @ec460508（先实测再重审；提案维持 0.90+③②① 交用户；旋钮已预留）"]
  T5A -.-> T5B["M2-REGION-RETYPE-CORE 改标 Core 实现 · done @d8019810（rev1.4 全链+GATE 25/25）"]
  T5A -.-> T5C["M2-SFX-CORRECTION-EXPORTER 纠错导出器 · done @66871d5d（scanner+双形态导出）"]

  %% docTR qualification 主线（2026-09-30 口径裁决后闭环，正式结论 FAIL）
  TA1 -.-> PRE["DOCTR-QUAL-PREFLIGHT 权重/环境/评测基座 · O:ZCode ✓"]
  PRE --> QRUN["DOCTR-QUAL-RUN 正式 qualification（T-D1） · O:ZCode ✓（正式结果 FAIL）"]
  QRUN --> C4["DOCTR-QUAL-C4 manga 域检测器评估 · O:ZCode ✓（Gate 全 PASS 0.9618）"]
  C4 --> C1SPOT["C1 抽检型校准审计 · O:ZCode+用户 ✓（0 真实漏检；Gate PASS=保守下界）"]
  C4 --> PRODINT["M2-PROD-DETECT-1 docTR→manga 域生产集成 · O:ZCode ✓（manga 默认/可切回 doctr；CPU 315.6ms/页）"]
  PRODINT --> DET2["M2-PROD-DETECT-2 发布形态运行时/权重分发 · O:ZCode ✓（ML 栈进闭包+权重随包；NSIS 438.86MiB；AC5 PARTIAL→IPC1 slice）"]
  DET2 --> DET3["M2-PROD-DETECT-3 core.detect 命令面+frozen 端到端 · O:ZCode ✓（协议 1.1；AC5 NOT_RUN 转 RUN；torchvision 缺口修复）"]
  DET3 --> SFXE["M2-SFX-DETECT-EVAL SFX 检测评估 · O:ZCode+用户裁决 ✓（chiqui7 唯一 sfx 类候选；自比修正方向反转）"]
  SFXE --> SFXP["M2-SFX-PROD-1 SFX 生产集成 · O:ZCode ✓（onnxruntime 轻量栈；权重随包 NSIS 479.93MiB；发布形态开箱可用）"]
  SFXP --> SEM1["M2-SFX-SEM-1 SFX 语义第一刀 · O:ZCode ✓（region_type widening+拟声词文化对等；TASK-002 rev 1.1）"]

  %% L-1 缺口核实支线（TA3-A 遗留 → DIAG-002 → DOC-FIX-STALE 全闭）
  TA3A -.-> DG2["DIAG-LOCK-CHANGED-REPRO-002 L-1 核实=已由 M2-P1 修复 · O:ZCode ✓"]
  DG2 -.-> DOCF["DOC-FIX-STALE 过时注释修正 · O:ZCode ✓"]

  classDef done fill:#d7f5df,stroke:#237a3b,color:#123;
  classDef proposed fill:#fff0b3,stroke:#8a6d00,color:#123;
  class DEXT,ARBIT,UIM done;
  class T5A proposed;
  class T1A done;
  class T0 done;


  
  class GOV,D1,I1,I2,R1,UI1,C1,S1,S2,C2,S3,RC1,RC2,AC1,DGR,P1,IPC1,AC2,AC3,AC4,FXE,FXL,FXS,FXF,DIO,FXA,FXB,FXC,DP,PKG,RG,TA1,TA2A,TA2C,TA2B,TA3A,T1,T2,T3,PRE,QRUN,DG2,DOCF,C4,C1SPOT,PRODINT,DET2,DET3,SFXE,SFXP,TA3B,OCRFIX,TA3B2,WDIAG,ALLOC,CALIB,SFXE2,TIL,BKF,PSG,SIP,SUI,KOR,SMAT,HYG,FULL,SEM1 done;
  
```

上图中绿色节点全部为 `done` 且已集成 main。M2-TA3-B 阶段一（阈值/冒烟/选样/计划）已 done；其阶段二（正式 qualification run）BLOCKED_ON_USER 翻译 endpoint 二选一，用户裁决后另行释放阶段二 Task。C1-C5 检测器候选流程已收官（C4 评估 done、C1 抽检 done、C2/C3/C5 经 C4 裁定无需运行），生产集成 M2-PROD-DETECT-1 已 done。Legacy TASK-001～065 的详细分类仍在本文件后文保存：`VERIFIED_COMPLETE`、`PARTIAL`、`SUPERSEDED`、`DOC_ONLY` 均为历史迁移盘点，不再生成旧架构工作。

**M2 — Desktop Architecture Migration: FIRST_WAVE_RELEASED / BOUNDED_IMPLEMENTATION.** User authorization on 2026-09-25 releases only the four Tasks below from the verified local `master` base `6a68fdeb92d8a1c7903166a8076d6260bf8fa79a`. [M2-D1 Headless & Qt Coupling Audit](tasks/M2-D1.md) is `done` after Codex non-author [Review](reviews/M2-D1-0a27a54.md) `approved` and integration `100abfb`. Its [report](research/M2-D1_HEADLESS_QT_COUPLING_AUDIT.md) supplies the first-wave evidence. AD-001 remains the fixed React + TypeScript / Tauri / Python Core / SQLite target. Migration is incremental; the existing PySide6/QML application may remain operational during transition, but its PyInstaller Release Gate is retired as the future formal release gate.

| First-wave Task | Status / Owner / Reviewer | Write authority and boundary |
|---|---|---|
| [M2-I1 Core Assembly Seam](tasks/M2-I1.md) | `done` / ZCode / DeepSeek Harness; R3 Delivery `09ad43a`, Handoff `8dab0ab`, [R3 Review](reviews/M2-I1-09ad43a-deepseek.md) `approved`, integration `cff1e0a8658f57a2e9caf774a9de0961e8f65da3`; post-integration verification passed | `src/bootstrap/**` and its assigned tests; split Core from Legacy Qt assembly, injectable adapters. |
| [M2-I2 Qt-free Logic Extraction](tasks/M2-I2.md) | `done` / Antigravity / Codex; Delivery `e359da7`, Revised HEAD `0d6acc7`, [Codex Review](reviews/M2-I2-0d6acc7.md) `approved`, integration `7e2da6b8eb55e437d36fa3fa11cbf3e976a834c9` | Two named UI logic modules, frozen application destinations, named consumers/tests; no Domain Contract change. |
| [M2-R1 Qt Runtime Feasibility Spike](tasks/M2-R1.md) | `done` / DeepSeek Harness / Codex; Delivery `5e2800b`, Handoff `052f99c`, Review `79b1a77` `approved`, integration `5803bd7` | Research/verification only. M2D1-22 is measured with platform limits on Windows 11; QML/`QQuickWindow` and production entry remain `UNVERIFIED`/`NOT_RUN`. No implementation authorization. |
| [M2-UI1 React Feature Parity & Visual Contract](tasks/M2-UI1.md) | `done` / Qoder / Antigravity; Delivery `23a5ac0`, Handoff `784ce18`, [independent Review](reviews/M2-UI1-23a5ac0.md) `APPROVED` at `83a795b`, integration `5242f64` | Design, verification and Handoff only; no React/QML product implementation. Page-level blocked mapping remains an explicit user/contract decision. |

M2 首波四项任务已集成。M2-C1 固定 base=`7478f72fe6f9872cae29f4fa12888b5e1f2380f1`、Owner Delivery=`7de1cd27e22037d4b76b235c9f11399b0cea9463`、Handoff/reviewed_head=`b2377288680569dbee4e2299fd7dfae4de067c54`、Contract blob=`4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3`。Qoder Review=`0d73983a5e1f37f104c76d8bd4c70c6f98fa36f5`、DSH r3 Review=`96666bf063c8a514b3f8a58f78453a397dd93f75` 均 `APPROVED`，同一 reviewed_head，Gate=`PASSED`；原始提交已并入共享历史，M2-C1=`done`。先前对象缺失系 SHA 字符转置误报，见 [Gate 核验](../verification/M2-C1/integration-gate-readiness-96666bf.md)。M2-S1 研究已释放，产品实现未释放。

**M2-S1 研究完成（2026-09-26）**：[M2-S1 Large-Media Resource Channel Feasibility Spike](tasks/M2-S1.md) 固定 base=`85a2aa7fd07a2dca843bf5cea3ec34070b63bdbc`，Owner=DeepSeek Harness；初审 `changes_requested`（`f709e39c`）后，修订 reviewed_head=`64c87d13faa3889c749096dedeacf5afbe8dda16` 由非作者 Codex [复审](reviews/M2-S1-64c87d1.md) `APPROVED`（`8984b4b3`）。Owner 原始提交经 Git bundle/fetch 保留 SHA，tip=`9f5eb1d51cb4283eb670085410ea9596d1f7b0d2` 并入 merge=`4103493fd63c0133f62a659390d0367d1c2a98ab`；集成后[核验](../verification/M2-S1/integration-4103493.md)通过，研究 Task=`done`。A/B 通道仅为条件性 `PROPOSAL`，S1-B1–B12 与 7 项用户阈值仍未解决；IPC runtime 与产品实现均未授权。历史[范围登记](../verification/M2-S1/scheduler-registration-0c2e202.md)与[释放证据](../verification/M2-S1/release-85a2aa7.md)分别保存。

**§7 产品阈值裁决与 M2-S2 释放（2026-09-26；用户授权代行治理）**：因 Codex 额度耗尽，用户指示 ZCode 会话代行 Codex 角色完成两项治理：① [M2-S1 报告 §7](tasks/../research/M2-S1_RESOURCE_CHANNEL_SPIKE.md) 的 7 项产品阈值已裁决于 [product-thresholds-ruling-67c3d56.md](../verification/M2-S1/product-thresholds-ruling-67c3d56.md)（T1 单资源 256 MiB 上限；T2 ≥32 活跃引用/≥16 订阅者；T3 首帧热缓存 200 ms/冷缓存 1 s 目标；T4 禁 Base64 物化 + 有界缓冲；T5 分层信任——WebView 永不接触 OS 路径、选映射 ID 保密；T6 300 s 滑动 TTL + revision 绑定立即撤销；T7 模型权重独立通道）。裁决可被用户逐项推翻，不修改 M2-S1 报告与任何 Contract。② [M2-S2](tasks/M2-S2.md) Resource Channel Security Verification Spike 登记并释放 `ready / SECURITY_VERIFICATION_RELEASED`：Owner=ZCode、Reviewer=Antigravity（非作者），base=`67c3d56e`，branch=`agent/zcode/M2-S2-resource-channel-security`，worktree=`G:/CODEX/New Manga.worktrees/M2-S2-zcode`，释放证据 [release-67c3d56.md](../verification/M2-S2/release-67c3d56.md)。M2-S2 验证 S1-B11（TOCTOU open-then-verify-from-handle）与 S1-B12（映射 ID 保密）；不实现产品通道，runtime 实现继续 NOT_RELEASED。

**M2-S2 完成与集成（2026-09-26）**：[M2-S2](tasks/M2-S2.md) `done`。Owner ZCode delivery=`d502aa5a`、Handoff head=`fbdf1bc2`（隔离原型 + 探针 24/24 PASS、复跑一致：TOCTOU 16 场景 + 映射 ID 8 场景）；Antigravity 非作者 [Review](reviews/M2-S2-fbdf1bc2.md)（`ea11d109`）`approved`（6/6 AC PASS、P0/P1=0、唯一 P2 R-001 GBK 控制台编码项 deferred 并附规避）；Codex 集成 merge=`bf1d12309bee19cccf665fb2d5bb5c9d4dee7e66`（parents `7671f0c1`+`ea11d109`；唯一 add/add 冲突 `doc/tasks/M2-S2.md` 按 M2-S1 先例取 Owner 版），[集成后核验](../verification/M2-S2/integration-bf1d1230.md)：32 路径全授权、禁改路径零改动、`diff --check` exit 0、9 链接 0 断链。原型层关闭 S1-B11/S1-B12 验证缺口；产品级保证保留 `UNVERIFIED/NOT_RUN`（§7 报告：11 NOT_RUN + 3 UNVERIFIED）；结果作为 Contract 修订（T1–T7 落约）与后续 runtime Task 的输入。

**M2-C2 契约修订释放（2026-09-26；用户批准首选方案）**：用户批准登记并释放 [M2-C2](tasks/M2-C2.md) Typed IPC Contract Revision（Resource Channel Thresholds and Security Conclusions）：把阈值裁决 T1–T7 与 M2-S2 的句柄校验/映射 ID 结论落入 [M2-C1 Contract](contracts/M2-C1_TYPED_IPC_CONTRACT.md) 原位修订版（`1.0`→`1.1`，§10 增补、§11 large-media 行部分解除、版本与修订记录），解除「裁决悬在治理文档、契约未更新」的漂移，作为大媒体 runtime Task 的需求基线。Owner=ZCode（按用户采纳的改派选项自 Codex 改派——Codex 额度耗尽且 M2-C1 原始 Owner 亦为 ZCode），Reviewer=DeepSeek Harness（非作者），Codex Integrator。base=`3f468e6e`，branch=`agent/zcode/M2-C2-typed-ipc-contract-revision`，worktree=`G:/CODEX/New Manga.worktrees/M2-C2-zcode`（已创建、干净），释放证据 [release-3f468e6e.md](../verification/M2-C2/release-3f468e6e.md)。修订不得放松既有 §10 保护语义、不得宣称已实现、不授权 runtime 实现。

**M2-C2 完成与集成（2026-09-26）**：[M2-C2](tasks/M2-C2.md) `done`。Owner ZCode delivery=`67f814ff`、Handoff/reviewed_head=`c18f273a`（Contract `1.0`→`1.1`，blob `4b503a17…`→`fc359138…`）；DeepSeek Harness 非作者 [Review](reviews/M2-C2-c18f273a.md) `approved`（0×P0/P1/P2，4×P3 advisory F-01..F-04 为标签/措辞精确性，deferred 至下次触碰 Contract 的 Task）。DSH headless 审查（沙箱内 git 不可用、报告以 untracked 交付）：集成方以 import 提交 `0bbe78f3` 原字节入库报告与派发记录（SHA-256 记录于集成核验），Owner 分支 tip 不动；三命令复核由集成方补跑（范围 7 授权路径、`diff --check` exit 0、blob `fc359138` 三点一致）。Codex 集成 merge=`d574ec1ec42bade5da98ec955d02284d1451f04a`（parents `0bbe78f3`+`c18f273a`；唯一 add/add 冲突 `doc/tasks/M2-C2.md` 按「master 为基 + Owner 回填」解决、blob 等价验证），[集成后核验](../verification/M2-C2/integration-d574ec1e.md)：15 路径全授权、禁改路径零改动、`diff --check` exit 0、8 文件 30 链接 0 断链、集成后 blob=`fc359138` 不变。Contract `1.1` 以设计要求口径承载 T1–T7 与安全语义（产品级保证按来源保留 UNVERIFIED）；runtime 实现继续 NOT_RELEASED。
**M2-S3 释放（2026-09-26）**：[M2-S3](tasks/M2-S3.md) Tauri Asset Protocol Feasibility Probe 已登记并释放 `ready / TAURI_ASSET_PROTOCOL_PROBE_RELEASED`，固定 base=`90c3e45962733799d43e3aefacf4fea99f662a2c`；Owner=DeepSeek Harness、Reviewer=ZCode（非作者），branch=`agent/deepseek/M2-S3-tauri-asset-protocol-probe`，worktree=`G:/CODEX/New Manga.worktrees/M2-S3-deepseek`，范围仅限隔离实验/报告/证据，不改产品代码或 Contract；释放证据 [release-90c3e459](../verification/M2-S3/release-90c3e459.md)。先解 S1-B1（真实 Tauri/WebView asset protocol 权限、缓存、生命周期）；S1-B6 待 runtime 通道存在后测量。大媒体 runtime 仍未释放，待 M2-S3 Review 与 Codex 集成裁决。

**M2-S3 改派 checkpoint（2026-09-26；按用户要求，后由完成记录 supersede）**：Owner 改为 ZCode，非作者 Reviewer 改为 DeepSeek Harness；固定 base=`90c3e45962733799d43e3aefacf4fea99f662a2c`、验收标准与 `ready` 状态不变。改派时的 Owner branch/worktree=`agent/zcode/M2-S3-tauri-asset-protocol-probe` / `G:/CODEX/New Manga.worktrees/M2-S3-zcode` 在固定 base 创建并保持干净。初始分配给 DeepSeek Harness 的 branch/worktree=`agent/deepseek/M2-S3-tauri-asset-protocol-probe` / `G:/CODEX/New Manga.worktrees/M2-S3-deepseek` 留存于同一 base，不再获本 Task 写授权；不清理或删除。改派证据：[reassignment-9b2d40c2](../verification/M2-S3/reassignment-9b2d40c2.md)。

**M2-S3 完成与集成（2026-09-26）**：[M2-S3](tasks/M2-S3.md) `done`，Owner=ZCode delivery tip=`bcef79e775bf4a5b4a4eceb4c3e63ac630aa6de9`；DeepSeek Harness 非作者 Review `approved`，固定于 `233d0901e1de817a8357be7047346de7d8c49f23`（0×P0/P1、5×P2、5×P3）。DSH shell 不可用；Codex 独立核对后续差异至 bcef，并在 Windows/WebView2 实际复跑。merge=`6799c73a75c16252602ac85f4454a5ac1b45b8d2`（parents `a006acb9` + `bcef79e7`；唯一 add/add 冲突为 Task，按 master 为基 + Owner 回填解决）；[集成核验](../verification/M2-S3/integration-bcef79e7/integration.md) 记录授权范围 27 路径、禁改路径零改动、三次 Codex 探针均 16/16 PASS、`diff --check` exit 0。S1-B1=`PASS` 仅限单宿主、Rust 模拟映射表、一次性 body、非打包探针；S1-B3/B5/B6/B8 与产品级安全/IPC 仍未验证，runtime 继续 `NOT_RELEASED`。M2-C2 的 4×P3 advisory 仍 deferred 至下一次实际触碰 Contract 的 Task。

**M2-RC1 大媒体 runtime 释放（2026-09-27；用户明确授权）**：[M2-RC1](tasks/M2-RC1.md) `ready / LARGE_MEDIA_RESOURCE_CHANNEL_RUNTIME_RELEASED`；Owner=ZCode，Reviewer=DeepSeek Harness（非作者），Integrator=Codex；release commit=`fb87414af906348666ffd7d001a276e86c4cd5bc`。固定实现 base=`2dca20cd971e3c2ae1a3ab8134ac0acdf98c45f1`，branch=`agent/zcode/M2-RC1-large-media-resource-channel-runtime`，worktree=`G:/CODEX/New Manga.worktrees/M2-RC1-zcode`。依赖 M2-C1/S1/S2/C2/S3 均 `done`；Contract 1.1 固定 blob=`fc35913801297ee1876ea395f9c5041a16226f20`。Task 以受限 `m2res` opaque-ID URL 为 WebView 入口，限定新 React/Tauri app 与 resource-channel Core 路径；共享 Contract、Legacy QML、Schema、根依赖和打包发布不在授权范围。S1-B3/B8 未关闭前不得宣称产品级安全或打包就绪；S1-B6 冷缓存目标须如实标记。释放证据：[release-2dca20cd](../verification/M2-RC1/release-2dca20cd.md)。Owner worktree 从固定 base 起步；释放提交只提供 Task 文件，不能混入 Owner 实现历史。
**M2-RC1 完成与集成（2026-09-27）**：[M2-RC1](tasks/M2-RC1.md) `done`，Codex merge=`3a24684007fd5a5e855f324077ad996841300f27`（parents `cb6e6d51` + `ce3c3771`）。DSH round-4 Review=`approve` @`2f6a31cd67e983e789c02cb4e33c194f0e012f23`；Codex 在 Owner tip `ce3c3771` 独立复跑 pytest 43、Cargo 12、Vitest 8、WebView2 E2E 10/10 ×2，均 exit 0。62 路径 reviewed delta 已核对；Contract 1.1 blob=`fc35913801297ee1876ea395f9c5041a16226f20` 未变。F-03/F-05 accepted deferrals were assigned to [M2-RC2](tasks/M2-RC2.md), now done at merge `88f972fe`. S1-B3/B5/B6/B8 仍属 `UNVERIFIED/NOT_RUN` 边界；本集成不作产品级安全或打包就绪声明。证据：[integration](../verification/M2-RC1/integration-2f6a31cd/integration.md)。

**M2-RC2 完成与集成（2026-09-27）**：[M2-RC2](tasks/M2-RC2.md) done；固定 Task base=22a2c2bf9a70d8c3b81edcdbe0e1ef146db556e5，FIX head=eac5cb3ed56b4531106cfa98ec6d4ea11ce8d51b，Owner docs head=dc8e5c95c31ccc0dd96fa2287b44aa962c70153d。DeepSeek Harness 对 FIX head 的独立 Review approved；R3-01 文案已在集成时修正。Codex merge=88f972fed921c7d7a010bef38a734de2601d9ca5（parents 6a68fdeb + dc8e5c95；未改写 Owner 历史），报告与两轮复核原始证据逐字节导入，SHA256 清单及集成复跑转录见 [集成核验](../verification/M2-RC2/integration-88f972fe/integration.md)。Codex 复跑 pytest 66、Cargo 20、Vitest 15、WebView2 E2E GATE 10/10 / probe 13/13 与 TTL 探针，全部 EXIT=0；Contract 1.1 blob=fc35913801297ee1876ea395f9c5041a16226f20 未变。S1-B3/B6/B8 保持 NOT_RUN、S1-B5 保持 UNVERIFIED；bundle.active=false；不作产品级安全、安装或打包就绪声明。集成时尚无 M2 successor；随后单独登记并释放 [M2-AC1](tasks/M2-AC1.md)，范围仅为下方 Backlog 首行。

**M2-AC1 完成与集成（2026-09-28）**：[M2-AC1 end-to-end acceptance on the M2 baseline](tasks/M2-AC1.md) `done`。Owner=ZCode，DeepSeek Harness 非作者 Review r4=`approved`（静态 Review）@`d102bf70`；Codex merge=`f162193b5255f06bcbbfc0d1820f38cd81f89d32`，parents=`1347a67c` + Owner tip=`51f70ed1`。固定实现 base=`7db0e7b6ef77b5d403e3d485dc1378d4c786bc7d`；Owner branch/worktree 保留于 `agent/zcode/M2-AC1-end-to-end-acceptance` / `G:/CODEX/New Manga.worktrees/M2-AC1-zcode`。Codex 在合并 head 独立复跑 Core 4、Cargo 26、Vitest 19、E2E 45/45 均通过；全仓 pytest=`1316 passed, 11 skipped, EXIT 0`（docTR 2、OpenSSL 6、NumPy 1、Torch 2，逐项见日志）。E2E 双样本、真实进程重启、Reader 与 PNG 像素摘要一致；全仓 Owner 先前披露的两项 Legacy QML 失败在 Codex 本次运行未复现，仍不视为已查根因。Codex 对 F-008 追认恰好 9 个 Tauri ACL 机制文件，production command surface 不扩张；无 M2 Contract、SQLite schema/migration、依赖锁、Legacy QML 或 packaging 改动。集成记录：[integration-51f70ed1](../verification/M2-AC1/integration-51f70ed1/integration.md)；释放记录：[release-7db0e7b6](../verification/M2-AC1/release-7db0e7b6.md)。其他 M2 Acceptance Backlog 行仍未登记。

**Separate Legacy reliability diagnostic (2026-09-27 released; 2026-09-28 integrated):** [DIAG-READING-EXPORT-001](tasks/DIAG-READING-EXPORT-001.md) is `done`. Owner=DeepSeek Harness delivered `8b36e98e` / tip `77c661b0` from fixed base=`83de13dfe0521125715c2e26da75b96a63103938` (branch=`agent/deepseek/DIAG-READING-EXPORT-001-reading-export-flaky-diagnosis`, worktree preserved). With Codex quota unavailable, the user directed a ZCode session to act as Codex proxy for the non-author Review and integration: proxy non-author [Review](reviews/DIAG-READING-EXPORT-001-77c661b0.md) `approved` @`77c661b0` (commit `c90b8b27`; 0×P0/P1; R-001 P2 §4.1-amplifier wording corrected at integration with U3 kept open; R-002 P3 accepted); integration merge=`e0a0e784498fc339a4d666dd931cc67cfb65bbdb` (parents `c90b8b27`+`77c661b0`; sole Task conflict resolved to the Owner-delivered version; Owner history unrewritten). Result: **15/15 matrix `NOT_REPRODUCED`** (run-01's 11 environment skips disclosed individually), both historical mechanisms reproduced by the two allowed read-only probes (terminal-signal queued-delivery race; reader-heartbeat writes closed SQLite). **NOT_REPRODUCED is not a fix.** Follow-ups [DIAG-READING-EXPORT-001-FIX-A](tasks/DIAG-READING-EXPORT-001-FIX-A.md) and [DIAG-READING-EXPORT-001-FIX-B](tasks/DIAG-READING-EXPORT-001-FIX-B.md) are `done` (FIX-A integration [a8b94df1](../verification/DIAG-READING-EXPORT-001-FIX-A/integration-a8b94df1/integration.md); FIX-B integration [9c9c9087](../verification/DIAG-READING-EXPORT-001-FIX-B/integration-9c9c9087/integration.md)); the former `proposed / NOT_RELEASED` wording was stale. Diagnostic integration verification: [integration-e0a0e784](../verification/DIAG-READING-EXPORT-001/integration-e0a0e784/integration.md). Release record: [release-83de13df](../verification/DIAG-READING-EXPORT-001/release-83de13df.md). This separate Legacy diagnostic is distinct from the M2 successor [M2-AC1](tasks/M2-AC1.md).

**Legacy closure:** [T3.2.1](tasks/T3.2.1.md) is terminal `closed_with_limitations`, disposition `CLOSED_WITH_LIMITATIONS / SUPERSEDED_BY_M2`. It retains all historical AC states: AC1/2/3/4/5/7/10 remain PASS within their documented scopes; AC6=`PARTIAL (11/12)`, AC8=`PARTIAL`, AC9=`PARTIAL`; clean-machine, Windows 10 x64, real-weight success and true cold-start items remain `NOT_RUN`. The old Release Gate is not a future release gate and its unfinished ACs do not block M2. REPAIR-15/16/17 remain `proposed / NOT_RELEASED` with `SUPERSEDED / DO_NOT_RELEASE`; no Legacy repair will be prepared or released.

### M2 Acceptance Backlog (planning rows and explicit releases)

These are requirements carried forward for M2 acceptance planning. Only a row linked to a separately released Task grants implementation scope; all unlinked rows remain unregistered. M2-C1 remains limited to its existing typed IPC contract.

| Future acceptance requirement | Classification | Placement |
|---|---|---|
| Deterministic successful Mock/Local pipeline, saved result, restart recovery, Reader verification and export verification | `MIGRATE_TO_M2_ACCEPTANCE` | Completed by [M2-AC1](tasks/M2-AC1.md), fixed base `7db0e7b6`; deterministic provider remains separate from real docTR claims and does not satisfy other rows. |
| Source hash integrity, Managed Copy, user edits, Lock and current/pinned Revision integrity | `CORE_REQUIREMENT` | Python Core/data safety acceptance and end-to-end recovery checks. |
| Missing Provider fails closed with durable, diagnosable status | `CORE_REQUIREMENT` | Python Core/Pipeline acceptance. |
| Reader export lineage and Library page-count/unknown semantics | `MIGRATE_TO_M2_ACCEPTANCE` | Reader/Export and Library parity acceptance. |
| Tauri + Python Core clean installation/start, no system Python dependency, migrated AC6/AC8 workflow/path/exit behavior | `MIGRATE_TO_M2_ACCEPTANCE` | Future target-package acceptance, scoped by a later authorized release task. |
| Real docTR-weight success qualification | `CORE_REQUIREMENT` | Deferred execution until controlled weights, environment and quality criteria are available. |
| Cold-start metrics, target Windows support matrix, GUI console policy and packaged dependency closure | `DEFERRED` | Decide and verify in a future M2 Release Gate/D08; do not inherit the Legacy results. |

### Released M2 diagnostic

This is an independent new-architecture diagnosis from the M2-AC1 Review, **not** a row in the M2 Acceptance Backlog and not a product-code authorization.

| Task | Scope and evidence | Owner / Reviewer |
|---|---|---|
| [DIAG-M2-REGIONLESS-LOCK-CHANGED-001](tasks/DIAG-M2-REGIONLESS-LOCK-CHANGED-001.md) | `done`（integration=`b5ac097f`）；fixed base=`5789b30b`、delivery=`7a03ac5f`。根因已定位并可复现：`_backfill_detected_regions` 只重绑 `region_id` 未重绑 `target_id` ⇒ OCR 守卫以 `None` 比对 Region current revision ⇒ `LOCK_CHANGED`。只诊断；修复须另立 Task（M2-P1 候选）。 | DeepSeek Harness（静态交付，执行由集成方代采）/ Antigravity（`approved`）；Integrator=Codex（代行）。 |

释放证据：[release-5789b30b](../verification/DIAG-M2-REGIONLESS-LOCK-CHANGED-001/release-5789b30b.md)。Task 已冻结 base、branch、worktree、allowed/forbidden paths、AC 与验证命令；产品代码仍未获授权。

The detailed AC and Qoder finding matrix is in the [Legacy Closure Audit](../verification/T3.2.1/legacy-closure-audit-20260926.md).

Historical REPAIR-13/14 completion facts follow for traceability; they do not reopen T3.2.1 or block M2. Child [REPAIR-13](tasks/T3.2.1-REPAIR-13.md) is `done`: fixed base=`8738c41`, product delivery=`aed0094`, final Handoff/evidence head=`13ae23f`, independent Review=`ccd26a4` (`APPROVE_WITH_CONDITIONS`, C1/C2 satisfied), Codex integration=`6fe7455`. Integration used only the 62-path fixed task delta; the full author branch was not merged because its ancestry includes unrelated REPAIR-9–12 candidate history. Post-integration focused suite: 162 passed, exit 0. C2 cleanup cleared all trailing whitespace; Codex recount found 13 pre-cleanup diagnostics vs 12 stated in the supplement, recorded in the integration report. At that historical checkpoint the Parent Full Gate was OPEN and AC3 was `BLOCKED`; this child completion did not change them. The former Sandbox attempts remain historical evidence; the parent clean-Windows/Sandbox Gate is unchanged. [REPAIR-14](tasks/T3.2.1-REPAIR-14.md) for F-13-3 is `done`: fixed base=`4ab6f58c06cb0691413e2630cb48a145c18c383a`, delivery=`43b24ee`, Handoff tip=`2f0d266`, DeepSeek Harness Review=`f616175e` (`approved`), Codex integration=`296131b`. R14-008 records the accepted fixture-seeding deviation and unrun GUI-native creation substep; R14-010 path counts are corrected in the integration record. Parent Gate remained OPEN / AC3 BLOCKED at that historical integration checkpoint; current closure and preserved AC statuses are recorded in the closure audit.

## Historical Legacy implemented-state audit — no scheduling authority

### Verified complete on the integrated product baseline

- SQLite v2 schema, migrations, region/revision persistence, connection
  ownership and managed-copy safety boundaries.
- Local image, PDF and picture-MOBI import paths, with typed failure behavior.
- Scheduler/executor, pause/stop/retry/recovery state, render/export adapters,
  Webtoon tiled reading and diagnostics wiring.
- Four top-level QML routes and the existing Bookshelf/Workbench/Reader shell.
- Backup/restore service and restore admission/latch tests; production backup
  UI/bootstrap exposure is not part of this verified list.
- T1.1.2 Region Canvas & Creator: rectangle/polygon creation, canonical page
  coordinate conversion, real SQLite persistence, deletion, Inspector sync and
  production `region_creator`/`region_deleter` wiring.
- T1.1.1 Production Text Detector: docTR local detector and production bootstrap
  injection are integrated at `f56f441`; focused detector tests, bootstrap to
  SQLite, real-material detection and source protection passed. Its full suite
  was `1077 collected = 1070 passed + 6 skipped + 1 known environment failure`,
  exit 1; see [integration evidence](../verification/T1.1.1/integration-f56f441.md).
- Earlier T1.1.2 integration verification: `1031 collected = 1025 passed + 6
  skipped`, exit 0; smoke test exit 0. The six skips were existing
  OpenSSL-unavailable TLS cases.

### Partial, blocked or missing

- **T1.2.1 verified complete:** Settings UI/ViewModel, provider/network
  persistence, fail-closed policy, production bootstrap credential injection,
  and authenticated proxy path are integrated and independently verified.
  See the [R5 review](../verification/T1.2.1/review-e5716ac.md) and
  [integration evidence](../verification/T1.2.1/integration-9a14310.md).
- **T2.1.1 gap:** the selected F · Graphite Atelier design is documented, but
  production QML still uses the pre-F hard-coded palette and has no shared
  token/theme layer.
- **T3.1.1 verified complete:** reading progress and export history now use the
  SQLite v4 adapters with non-destructive one-time legacy import; P2 follow-ups
  are recorded in the Task and integration evidence.
- **T3.2.1 Legacy closure:** `closed_with_limitations / SUPERSEDED_BY_M2`; unfinished Legacy ACs remain at their recorded statuses and no longer block M2. See [closure evidence](../verification/T3.2.1/legacy-closure-audit-20260926.md).
- Real provider quality and external endpoint behavior are not proven by the
  unit suite; adapters and fail-closed paths are not production quality claims.

## Historical Task audit

Classification is based on current source, current tests, fixed integration
commits and review evidence. It does not copy the old `status: done` field.
Historical files are not rewritten merely to change this classification.

| Classification | Tasks | Audit reason |
|---|---|---|
| `VERIFIED_COMPLETE` | TASK-005–015, TASK-029–032, TASK-034–046, TASK-049–065 | Integrated implementation or contract has current code and reproducible review/test evidence. TASK-013 is complete for its original progress/workbench scope; the canvas gap is a later slice. TASK-059 is a verified design deliverable, not production QML implementation. |
| `IMPLEMENTED_NOT_VERIFIED` | none | No current Task remains in this state; historical TASK-001–065 classifications are retained separately from the current roadmap. |
| `PARTIAL` | TASK-004, TASK-016–021, TASK-023, TASK-033 | The bounded slice exists, but its own evidence records a clean-machine gate, model/endpoint quality limitation, large-page limitation, deferred sub-slices, deferred MOBI history, or missing real-provider capability. |
| `BLOCKED` | none | No historical task is promoted to blocked when a bounded delivered slice exists; the current blockers are represented as gaps in the new roadmap. |
| `NOT_STARTED` | none | Former proposed tasks were replaced or retained in the new roadmap rather than left as an unowned queue. |
| `SUPERSEDED` | TASK-022, TASK-025–027, TASK-047, TASK-048 | Replaced by T1.2.1/T2.1.1/T2.2.1/T3.2.1 or by the later connection-ownership implementation. TASK-047 was explicitly rejected. |
| `DUPLICATE` | none | No additional independent delivery was found to be a pure duplicate. |
| `OBSOLETE` | none | Retired scope is recorded as superseded so its history remains traceable. |
| `DOC_ONLY` | TASK-001–003, TASK-024, TASK-028 | These are intentionally document/contract/design deliverables; their completion does not imply product implementation. |

The old task ledgers remain in place for traceability. T3.2.1 closure does not rewrite its historic Review, Handoff, integration or verification records.
historical metadata, not a second scheduling source of truth.

## Historical Legacy dependency graph — no scheduling authority

```text
T1.1.2 Region Canvas & Creator
  requires: TASK-008/TASK-049 region service and current Workbench VM seam
  writes:  QML workbench overlay, Workbench VM creator slot, interaction tests
  serial integration: src/bootstrap/app.py region_creator injection

T1.1.1 Production Text Detector
  requires: detector choice and provider contract decision
  writes: selected DetectionProvider adapter + bootstrap wiring + E2E test
  must not: use MangaOCR as a detector or silently fall back

T1.2.1 Settings UI & ViewModel
  requires: existing TASK-009/TASK-050 settings/credential services
  R4 writes: bounded registry/runtime/VM/bootstrap repair and focused tests
  gate: five R3 findings, new Handoff, non-author re-review, Codex integration

T2.1.1 Graphite Atelier QML
  requires: T1.1.2 and T1.2.1 contracts stable
  -> T2.2.1 Reader/Workbench polish

T3.1.1 SQLite progress/export history
  requires: TASK-057 backup/recovery slice; recommended after T2 stabilization
  -> T3.2.1 PyInstaller packaging and clean-machine Release Gate (historical downstream; closed with limitations / superseded by M2)
```

No downstream task is released before its prerequisite is integrated. Product
code, shared contracts, `src/bootstrap/app.py`, SQLite migrations and top-level
QML shell changes are serialized through Codex.

## Historical migration execution record — superseded by the 2026-09-28 flow above

| Order | Task | State | Owner / reviewer | Acceptance boundary |
|---:|---|---|---|---|
| 1 | **T1.1.2 Region Canvas & Creator** | **VERIFIED_COMPLETE** | Qoder implementation / Codex non-author review and integration; base `b985d9c`, integrated `5b91745` | Draw a rectangle/polygon on the original page; inspector updates; matching `regions` and `region_revisions` rows are created; no source-file write. |
| 2 | T1.1.1 Production Text Detector | **VERIFIED_COMPLETE**; integrated `f56f441` | ZCode implementation / Codex non-author review and integration | A page without regions creates a persisted candidate Region through a selected real detector; configured path no longer fails as `PROVIDER_NOT_CONFIGURED`. |
| 3 | [T1.2.1 Settings UI & ViewModel](tasks/T1.2.1.md) | **VERIFIED_COMPLETE**; integrated `9a14310`, evidence `e92c414` | ZCode implementation / Codex non-author review and integration | Provider, credential, endpoint and proxy settings survive restart, feed the pipeline and never enter logs/diagnostics; B-003 production credential path verified. |
| 4 | [T2.1.1 Apply Design F to QML](tasks/T2.1.1.md) | **VERIFIED_COMPLETE**; product code integrated at `5da1cf6` | Qoder / Codex non-author review and integration; base `7f34135` | Shared F tokens use `pragma Singleton` + `qmldir`; all four pages consume them; 158px bookshelf geometry, accepted/completed-state contrast, and a discriminating hard-code guard are verified without business-logic changes. Review/integration evidence: [`review-bc49ef9`](../verification/T2.1.1/review-bc49ef9.md), [`integration-5da1cf6`](../verification/T2.1.1/integration-5da1cf6.md). |
| 5 | [T2.2.1 Reader & Workbench Polish](tasks/T2.2.1.md) | **VERIFIED_COMPLETE**; integrated `fe9fca0` | ZCode functional implementation + Qoder QML/UI/UX / Codex non-author review and integration | Chapter picker, Workbench empty-state picker, dismissible command-error notification, and webtoon canvas consistency are accessible and tested. Evidence: [`review-0846573`](../verification/T2.2.1/review-0846573.md), [`integration-aad510b`](../verification/T2.2.1/integration-aad510b.md). |
| 6 | [T3.1.1 Unify Storage into SQLite](tasks/T3.1.1.md) | **VERIFIED_COMPLETE**; product integrated `0c70e44` | Antigravity implementation / DeepSeek Harness independent Review; Codex Lead / Architect / Integrator | JSON progress/export stores migrate once into transactional SQLite with rollback, non-destructive legacy import and no data loss. Evidence: [review-899bd3c](../verification/T3.1.1/review-899bd3c.md), [integration-899bd3c](../verification/T3.1.1/integration-899bd3c.md). |
| 7 | [T3.2.1 Windows Packaging & Release Gate](tasks/T3.2.1.md) | CLOSED_WITH_LIMITATIONS / SUPERSEDED_BY_M2; AC states preserved. | Codex governance closure; evidence `verification/T3.2.1/legacy-closure-audit-20260926.md`. | Legacy unfinished ACs are not M2 blockers; REPAIR-15/16/17 are superseded and not released. |
| 8 | [M2-C1 Typed IPC Contract](tasks/M2-C1.md) | `done`；Owner Delivery=`7de1cd27e22037d4b76b235c9f11399b0cea9463`，Handoff/reviewed_head=`b2377288680569dbee4e2299fd7dfae4de067c54`；Qoder 与 DSH r3 Review 均 `APPROVED`；Gate=`PASSED`；集成 merge=`c1765aa2`。 | ZCode Owner；Qoder=`0d73983a5e1f37f104c76d8bd4c70c6f98fa36f5`；DeepSeek Harness r3=`96666bf063c8a514b3f8a58f78453a397dd93f75`；Codex Integrator。 | Owner/Reviewer 原始提交保留；source-trace 断链由 Codex 在集成层补齐。全部旧现场保留；M2-S1 研究单独释放。 |
| 9 | [M2-S1 Large-Media Resource Channel Feasibility Spike](tasks/M2-S1.md) | `done`；base=`85a2aa7`，修订 reviewed_head=`64c87d1`，integration=`4103493`。 | DeepSeek Harness Owner / Codex 非作者 Reviewer；复审 `8984b4b3` `APPROVED`。 | 图片/tile 通道研究与原始实验已集成；A/B 仅为条件性建议，S1-B1–B12 与 7 项产品阈值留待单独 Gate；产品实现未释放。 |
| 10 | [M2-S2 Resource Channel Security Verification Spike](tasks/M2-S2.md) | `done`；base=`67c3d56e`，delivery=`d502aa5a`，reviewed_head=`fbdf1bc2`（Antigravity Review `ea11d109` `approved`），integration=`bf1d1230`。 | ZCode Owner / Antigravity 非作者 Reviewer；Codex Integrator。 | 隔离原型验证 S1-B11（open-then-verify-from-handle TOCTOU 负向探针 16/16）与 S1-B12（Core 侧映射 ID 保密 8/8）；产品级保证保留 UNVERIFIED/NOT_RUN；零产品代码改动；结果作为 Contract 修订与 runtime Task 输入；runtime 实现未释放。 |
| 11 | [M2-C2 Typed IPC Contract Revision](tasks/M2-C2.md) | `done`；base=`3f468e6e`，delivery=`67f814ff`，reviewed_head=`c18f273a`（DSH Review `approved`，报告经 `0bbe78f3` 原字节 import），integration=`d574ec1e`。 | ZCode Owner / DeepSeek Harness 非作者 Reviewer；Codex Integrator。 | Contract 原位修订 `1.0`→`1.1`（blob `4b503a17`→`fc359138`）：§10 落入 T1–T7 阈值与安全语义、§11 large-media 行部分解除；既有保护语义零放松；4×P3 advisory deferred；不授权 runtime 实现。 |
| 12 | [M2-RC1 Contract-Aligned Large-Media Resource Channel Runtime](tasks/M2-RC1.md) | `done`；base=`2dca20cd`，Owner delivery/reviewed head=`2f6a31cd`（DSH round-4 `approve`），Owner evidence tip=`ce3c3771`；integration merge=`3a246840`。 | ZCode Owner / DeepSeek Harness 非作者 Reviewer / Codex Integrator。 | 62 路径交付，四套命令级复跑全通过；Contract blob=`fc359138` 保持不变。F-03/F-05 转入 M2-RC2，现已 done at merge `88f972fe`；S1-B3/B5/B6/B8 的未验证边界与产品级安全/打包限制保持。集成记录 `verification/M2-RC1/integration-2f6a31cd/integration.md`。
| 13 | [M2-RC2 Resource Channel Command Surface and Sidecar Boundary Hardening](tasks/M2-RC2.md) | done；base=22a2c2bf，delivery=a8fb17ca，FIX/reviewed head=eac5cb3e，DSH Review=approved，docs=dc8e5c95，Codex integration=88f972fe。 | ZCode Owner / DeepSeek Harness 非作者 Reviewer / Codex Integrator。 | 命令面与 Core catalog 权威、sidecar 隔离完成；R3-01 证据措辞已修正。集成复跑 66/20/15/GATE 10/10/probe 13/13，全 EXIT=0；Contract blob fc359138 未变。S1-B3/B6/B8=NOT_RUN、S1-B5=UNVERIFIED；不作产品级安全/打包声明。记录：[integration](../verification/M2-RC2/integration-88f972fe/integration.md)。 |
| 14 | [M2-AC1 end-to-end acceptance on the M2 baseline](tasks/M2-AC1.md) | `done`；base=`7db0e7b6`，Owner tip=`51f70ed1`，DeepSeek Harness r4 `approved` @`d102bf70`（静态），Codex integration merge=`f162193b`。 | ZCode / DeepSeek Harness / Codex。 | Backlog 首行闭环完成；Codex 在 integration head 独立复跑 pytest 4、Cargo 26、Vitest 19、E2E 45/45，全仓 1316 passed/11 skipped，均 EXIT 0。F-008 限定追认 9 个 ACL 联动文件；无其他越界。记录：[integration-51f70ed1](../verification/M2-AC1/integration-51f70ed1/integration.md)。 |
| 15 | [DIAG-READING-EXPORT-001 Reading/export completion signal and connection-lifetime flaky diagnosis](tasks/DIAG-READING-EXPORT-001.md) | done；base=83de13df，Owner delivery=8b36e98e，Owner tip=77c661b0（DSH），Codex 代行非作者 Review=c90b8b27 approved @77c661b0，integration=e0a0e784。 | DeepSeek Harness Owner / Codex（ZCode 会话代行）非作者 Reviewer 与 Integrator。 | 15/15 固定矩阵 NOT_REPRODUCED（11 个环境 skip 逐项披露，不计通过）；两个历史机制由恰好 2 个只读探针定位并复现（终态信号排队投递竞态；读者心跳写已关闭 SQLite）。**NOT_REPRODUCED ≠ 已修复**；FIX-A/FIX-B 见第 16/17 行。记录：[integration](../verification/DIAG-READING-EXPORT-001/integration-e0a0e784/integration.md)。 |
| 16 | [DIAG-READING-EXPORT-001-FIX-A Export terminal-state wait/signal-delivery semantics](tasks/DIAG-READING-EXPORT-001-FIX-A.md) | done；base=32ef1dd6，R1 delivery=77a78b25、R2 delivery=db5ee918、Owner tip=6fe7bd86（ZCode，用户全夜指令授权释放），DSH 双轮 Review：R1 changes_requested（1P2+5P3 全处置）→ R2 approved @6fe7bd86；integration=a8b94df1。 | ZCode Owner（代行 Codex 释放/集成，待追认）/ DeepSeek Harness 非作者 Reviewer。 | 纯测试等待语义修复（产品零改动）：6 处终态信号消费者等待信号到达；判别探针旧谓词忙碌主线程 324/400 miss → 新谓词 0 miss + 故障注入 3/3 检出；集成 head 全仓 1316 passed/5 skipped EXIT=0（6 OpenSSL=shell PATH 口径）。DSH R2 的 5×P4 观察 deferred。记录：[integration](../verification/DIAG-READING-EXPORT-001-FIX-A/integration-a8b94df1/integration.md)。 |
| 17 | [DIAG-READING-EXPORT-001-FIX-B Reader heartbeat lifecycle](tasks/DIAG-READING-EXPORT-001-FIX-B.md) | done；base=a8b94df1，交付链 claim=6e37f05d → R1=3ce82240/528ba4d4 → R2=2a1078b6 → R3 docs=f93ea667（Owner tip，ZCode），DSH 三轮 Review：R1 changes_requested（2P2+4P3 全处置）→ R2 复核"代码与测试面通过"（5 条文档缺口）→ R3 approved @f93ea667；integration=9c9c9087。 | ZCode Owner（代行 Codex 释放/集成，待追认）/ DeepSeek Harness 非作者 Reviewer。 | `settleReadingTime` 的 `sqlite3.Error` 类型化处理（停心跳+`heartbeat_error` 属性+信号，不吞异常）+ 测试 teardown 6 处落点 + 真实 SQLite 回归测试（先红后绿）；泄漏探针真实 2 心跳周期 7/7 PASS `LEAK CLOSED`；集成 head 全仓 1317 passed/5 skipped EXIT=0。生产 QML/bootstrap 终结点接线为零（Task 禁止范围）→ 登记 proposed 候选 FIX-C（代行 Codex 裁决，待追认）。记录：[integration](../verification/DIAG-READING-EXPORT-001-FIX-B/integration-9c9c9087/integration.md)。 |
| 18 | [DIAG-READING-EXPORT-001-FIX-C Production reader heartbeat endpoint wiring](tasks/DIAG-READING-EXPORT-001-FIX-C.md) | done；base=0e34c5c3，交付链 claim=b1f4cedf → R1=de0bf175 → R2=e9f61f5b → R3=132aa5e1 → R4=46c7ff5a → R5=5d541bee → R6=0e0e699e（Owner tip，ZCode），DSH 六轮 Review：R1 approved（6 Minor）→ R2..R5 changes_requested 逐轮处置 → R6 approved @0e0e699e；integration=0f2e9e31。 | ZCode Owner（代行 Codex 释放/集成，待追认）/ DeepSeek Harness 非作者 Reviewer。 | 纯 Python bootstrap 接线（零 QML）：离开读者页 `closeReader`（幂等 + 离园时长不计入守卫 + re-arm 重启）与 `aboutToQuit` stderr 守卫；接线测试红→绿（600s 离园判别）；集成 head 全仓 1318 passed/5 skipped EXIT=0。F-1/AC1 文本裁决记录于 Task 集成记录。记录：[integration](../verification/DIAG-READING-EXPORT-001-FIX-C/integration-0f2e9e31/integration.md)。 |

The [formal T1.2.1 Task](tasks/T1.2.1.md), [R5 review](../verification/T1.2.1/review-e5716ac.md)
and [integration evidence](../verification/T1.2.1/integration-9a14310.md) record
the completed Task. T2.1.1 passed its release gate at base `7f34135`, received
non-author review, was integrated at `5da1cf6`, and is now
`VERIFIED_COMPLETE`; its fresh evidence is recorded in
`verification/T2.1.1/`.

The formal [T3.1.1 Task](tasks/T3.1.1.md), its independent
[Release Gate](../verification/T3.1.1/release-gate-e771179.md), DeepSeek Harness
Review, and Codex [integration evidence](../verification/T3.1.1/integration-899bd3c.md)
are complete. The product delivery is integrated at `0c70e44`; R-002 and the
remaining P2 follow-ups are explicitly deferred rather than hidden.

## Historical T3.2.1 Legacy Release Gate record (superseded 2026-09-26)

The formal [T3.2.1 Task](tasks/T3.2.1.md) and
[Release Gate](../verification/T3.2.1/release-gate-c2fcb1c.md) use the product
baseline `c2fcb1c`. The Gate decision is **PASS TO START** only. At the pre-closure checkpoint, the ZCode
continuation input, local host-simulation status, remaining evidence, and no-Sandbox
instruction were recorded in
[checkpoint](../verification/T3.2.1/clean-release-gate-20260926/checkpoint.md)
and [Handoff](handoffs/T3.2.1-zcode-continuation-20260926.md); the older Codex
closeout record remains historical.

Review status is slice-specific: REPAIR-8 (`3cdfdee` / `37d5488`) was approved
for documentation only; REPAIR-9 (`d2bf6a8` / `eeb095e`) remains
`changes_requested` after Review `85f8c59`; REPAIR-10 (`be5200e` / `d7edea5`)
was approved for packaging-test path independence only. REPAIR-11 Delivery
`9622395` / Handoff `941dbc8` received `changes_requested` from independent
Review `4f2f8a0`; the evidence findings were corrected by REPAIR-12 Delivery
`a2f6695` / Handoff `8738c41`, which received slice-only `approved` Review
`a656486`. The new review does not alter the historical REPAIR-11 decision or
approve the full product Gate. At that historical checkpoint AC3's required interactive workflow was
`NOT_RUN`; AC5=`NOT_RUN`, AC6/AC7=`PARTIAL / NOT_RUN`,
AC8/AC9=`NOT_RUN`, and R-014–R-016=`OPEN`. These values are not the later integrated checkpoint or the closure audit's final disposition. Codex's historical closeout records
O-12-2 and keeps the legacy REPAIR-11 Handoff outside the integration candidate.
At that pre-closure checkpoint, no REPAIR-7/9/10/11/12 or related branch was to
be merged to `master` before full Gate closure and final independent Review.

## Project control baseline — 2026-09-22

The detailed modified-V2 audit is [PROJECT-AUDIT-2026-09-22](../verification/PROJECT-AUDIT-2026-09-22.md).
It is evidence and a derived map, not a second planning source. The current
project overview, repository/code architecture map, Task ↔ Code ↔ Test
traceability, module maturity, parallel matrix and Dependency Blocking Chain
are maintained there; this Plan retains the authoritative phase, dependency
and release order. The live dashboard, `TaskStatus`/`ExecutionState`, current
branch/HEAD, dirty-file safety and next actions remain in [STATUS](STATUS.md).

Current successor gate (updated 2026-09-26):

```text
M2-D1 / M2-I1 / M2-I2 / M2-R1 / M2-UI1 = integrated; ancestry verified at base 7478f72fe6f9872cae29f4fa12888b5e1f2380f1
  -> T3.2.1 = closed_with_limitations / SUPERSEDED_BY_M2; unfinished Legacy ACs do not block M2
  -> M2-C1 = done; dual Review APPROVED at the same reviewed_head; Integration Gate PASSED; original commits integrated
  -> Case A = OWNER_ADOPTED_WITHOUT_SEMANTIC_CHANGE; Contract blob equals adopted source blob 4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3
  -> DSH r3 Review commit 96666bf reports APPROVED and is present unchanged in shared history
  -> Codex corrected a transposed SHA in the former blocker check; exact object ancestry, Contract blob and authorized paths passed
  -> M2-S1 research done at merge 4103493; thresholds T1-T7 ruled and recorded through M2-S2 / M2-C2; remaining product verification stays scoped and open
  -> M2-S2 security verification done at merge bf1d1230; prototype conclusions only, product guarantees remain UNVERIFIED/NOT_RUN
  -> M2-C2 Contract 1.1 done at merge d574ec1e; blob fc359138; 4x P3 advisory deferred until next Contract touch
  -> M2-S3 probe done at merge 6799c73a; S1-B1 PASS within documented boundaries; product resource-channel runtime Task separately released as M2-RC1
  -> M2-RC1 done at merge 3a246840; round-4 DSH approve @2f6a31cd; all Codex command-level integration checks passed; Contract blob fc359138 unchanged; product security/packaging claims remain gated
  -> M2-RC2 done at merge 88f972fe; DSH FIX review approved; S1-B3/B6/B8=NOT_RUN, S1-B5=UNVERIFIED
  -> M2-AC1 done at Codex merge f162193b (2026-09-28): fixed base 7db0e7b6; bounded deterministic Mock/Local -> SQLite save -> process restart/recovery -> Reader -> PNG export acceptance
  -> DIAG-M2-REGIONLESS-LOCK-CHANGED-001 ready at fixed base 5789b30b; AWAITING_EXTERNAL_DISPATCH; Legacy QML candidate withdrawn by user directive
  -> Separate Legacy DIAG-READING-EXPORT-001 done at merge e0a0e784 (2026-09-28, proxy Codex review+integration): 15/15 matrix NOT_REPRODUCED, both mechanisms probe-reproduced
  -> DIAG FIX-A done at integration a8b94df1 (2026-09-28, overnight directive): DSH dual-round review r2 approved; test-wait semantics; FIX-B released serially
  -> DIAG FIX-B done at integration 9c9c9087 (2026-09-28, overnight directive): DSH three-round review r3 approved; typed heartbeat-error handling + teardowns; leak probe 7/7 LEAK CLOSED
  -> DIAG FIX-C done at integration 0f2e9e31 (2026-09-28, overnight directive): DSH six-round review r6 approved; production leave/quit wiring (pure Python); family fully closed
```

This is a dependency blocking chain, not a schedule critical path; no reliable
duration model exists. Research-only storage work and knowledge-map refreshes
may be conditional/safe parallel work when their write sets stay isolated.

Audit note: Roadmap ID `T1.1.2` is verified through historical `TASK-013`,
integration `5b91745` and its verification records, but has no dedicated
`doc/tasks/T1.1.2.md`. This is a traceability gap recorded for future document
maintenance; it does not reopen the integrated implementation.

## Directory and document governance

- Keep `src/`, `tests/`, `doc/01–09`, contracts, task/review/handoff evidence
  and verification logs.
- Keep historical tasks in place; archive them logically through the mapping in
  this file instead of moving or deleting them.
- Treat `verification/` as evidence, not generated cache. Do not delete logs
  during this rebaseline.
- `.pytest_cache/` is generated and ignored. The untracked-file inventory in
  the initial audit is historical; refresh `git status` before any edit and
  preserve other agents' material.
- `experiments/TASK-017/README.md` is another agent's uncommitted change;
  preserve it and keep it outside this audit commit.
- The 2026-09-20 worktree inventory is evidence only and must be refreshed
  before any future worktree deletion. No worktree deletion or prune is
  authorized here.

## Recovery checkpoint

```powershell
Set-Location 'G:\CODEX\New Manga'
git status --short --branch
git rev-parse HEAD
Get-Content doc\STATUS.md
git log -8 --oneline --decorate
```

Resume only after confirming the current branch, dirty files, `STATUS.md`,
this plan and the latest verification artifact. Do not infer progress from
chat history.
