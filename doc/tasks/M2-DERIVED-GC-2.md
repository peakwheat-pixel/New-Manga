---
id: M2-DERIVED-GC-2
title: 轮换退役 preview 引用安全回收实现
kind: feature
status: in_progress
approval: user_authorized_release_20261007
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: Codex
depends_on: [M2-DERIVED-GC-2-DESIGN, M2-DERIVED-GC-1, M2-RC4-DOMAIN-COMMANDS]
base_commit: ad75fadc2944983b4322f353176ba70cf0b0b7ae
branch: agent/zcode/M2-DERIVED-GC-2
worktree: G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode
allocation_state: allocated_clean
allocated_head: e093f0106bf62476c640dbcf8bb47448c8cc644c
integration_commit: null
---

# M2-DERIVED-GC-2：正式释放，待 ZCode 认领

2026-10-07 用户明确授权 Codex 正式释放；Task=ready，ExecutionState=IDLE / AWAITING_OWNER_CLAIM。唯一释放任务为本 Task，Owner=ZCode，非作者 Reviewer=DeepSeek Harness，Integrator=Codex。允许路径、共享 seam、AC/G1-G7 和禁止范围沿用已批准设计及本文件，未扩大产品范围。ZCode 收到实际 release commit 并核对干净恢复点后才认领 in_progress；本轮未派发或启动生产实施。

**2026-10-07 Owner 认领（ZCode）**：恢复点核对通过——worktree `G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode` 分支 `agent/zcode/M2-DERIVED-GC-2`、HEAD=`5896db8c64b90b53b015eb9c46c7dab6ab29210b`（clean）、common-dir=`G:/CODEX/New Manga/.git`、与 release 恢复点一致；主仓库额外 HEAD=`554a9845` 为指令所述治理 commit。Task 依赖（设计@e4c0967f 已批、GC-1@44859014、RC4@0a7e0d5b）核实已集成。Owner=ZCode 本会话认领 in_progress；Reviewer=DeepSeek Harness（非作者）、Integrator=Codex 不变。AC/G1-G7 维持 planned / NOT_RUN。

设计集成=ad75fadc2944983b4322f353176ba70cf0b0b7ae，设计批准 head=e4c0967f83a08d9b9e2d84605d17923e81a844b6，DSH r4 approve_with_conditions（0P0-P3）；两个 P4 已纳入下文。base_commit 保留设计基线，不把治理同步冒充产品基线变化。allocated_head 是初次分配的历史快照；正式释放后的实测 HEAD 以 verification/M2-DERIVED-GC-2/release-recovery.md 为准（释放提交后追加，避免自引用 hash）。初始 main=02ff655b、Owner worktree=e093f010，均 clean、common-dir 正确；ad75fadc 后只有已知治理差量。

本次释放不是实现批准，AC/G1-G7 全部 planned / NOT_RUN。设计完成不等于回收已实现。完整可转发实施指令见 verification/M2-DERIVED-GC-2/zcode-instruction.md。

## 来源与冻结目标

doc/contracts/M2_DERIVED_PREVIEW_GC_DESIGN.md §1–7；独立报告doc/reviews/M2-DERIVED-GC-2-DESIGN-e4c0967f-dsh-r4.md。GC-1 done@44859014仅orphan/dead-row；RC4 done@0a7e0d5b。实现范围为已知origin+明确retired+非current/非pinned、仅在受保护静默窗口删除的preview副本；长会话/每次运行末key/unknown/pinned仍保留，不声称磁盘有界或RC4-12全闭合。

共享冻结仅：专用catalog的preview_lifecycle来源字段（resource_id、producer_root、artifact_id、artifact_revision_id、managed_rel_path、retired）和preview_namespace单行版本/canonical+OS identity绑定；Core唯一创建origin，channel仅更新既有retired；trusted轮换revoke请求内部retire_preview位、CoreChannel窄方法；可信隔离loader的initialize-preview-namespace flag。主产品Schema/ports、WebView wire/ACL/十五条命令表、grant/TTL公共语义、读取share flags、依赖全部不变。

## Acceptance Criteria（实施前全部 planned / NOT_RUN）

- [ ] AC1 origin在本次outcome的artifact_id/revision_no/managed_path逐字唯一匹配后事务登记；旧资源不猜关联、不回填来源；普通loader重绑清掉来源资格。
- [ ] AC2 Windows删除域共享/独占生命周期租约真实双进程成立，store bootstrap hint在锁下重验；全入口/首次fixture initialize→seed→probe/ac1/acceptance可用，绑定前拒绝、run2仍可用；未知/失配禁两个sweep。
- [ ] AC3 current/pinned/Managed/source/人工修改/Lock/有效grant/在途读取保护；同一核验句柄hash/size/identity/目录保护后DELETE，分享冲突/目录逃逸/未知均保留，不用年龄/TTL/数量猜删。
- [ ] AC4 revoke成功才mark、same-key/None/revoke失败/mark异常判别；mark独立零busy连接非致命、不增加第二RPC；启动ping 30s超时自有child/worker/句柄完整退出，不改正常round_trip/Drop行为。
- [ ] AC5 G1-G7判别证据和受影响定向回归入库，失败/崩溃恢复/metadata顺序幂等；旧runtime全退出及所有入口覆盖无法证明则两个sweep恒禁用并BLOCKED，不伪造启用/测试PASS。
- [ ] AC6 固定代码head+Handoff→新fixed-head真实DSH非作者Review→条件闭合→Codexmerge与集成后验证，最后才done；不以设计批准代替实现批准。

## allowed_paths（本次 ready 释放后生效）

生产落点：

- src/infrastructure/resource_channel/catalog_store.py
- src/infrastructure/resource_channel/handle_resolver.py
- src/infrastructure/resource_channel/catalog_loader.py
- src/infrastructure/resource_channel/render_preview.py
- src/infrastructure/resource_channel/host_bridge.py
- src/bootstrap/core_service.py
- apps/desktop/src-tauri/src/core_bridge.rs
- apps/desktop/src-tauri/src/library_bridge.rs
- apps/desktop/src-tauri/src/main.rs

已有测试，仅相关fixture与判别断言：

- tests/core/test_derived_gc.py
- tests/core/test_rc4_stdio_render_preview.py
- tests/core/test_page_resource_resolve.py
- tests/m2_resource_channel/test_catalog_authority.py
- tests/m2_resource_channel/test_bridge_and_thresholds.py（:memory:，不做file-backed初始化）
- tests/m2_resource_channel/test_handle_resolver.py
- tests/m2_resource_channel/test_sidecar_isolation.py
- tests/m2_acceptance/test_acceptance_loop.py

唯一步骤接线例外，不改部署/build/spec/验收阈值：

- packaging/m2ac5/run_clean_start_e2e.py（仅seed fixture的初始化flag/root传参）
- packaging/release-gate/run_release_gate.py（同上）
- verification/M2-RC2/run_e2e.py（仅现行driver的首次新fixture初始化）
- verification/M2-AC1/run_e2e.py（同上；先建自有derived根，run2不重复init）

文档/证据：

- doc/tasks/M2-DERIVED-GC-2.md
- doc/contracts/M2_DERIVED_PREVIEW_GC_DESIGN.md（必须随真实实施差量与新Review，不延用旧设计批准）
- doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md（仅内部生命周期窄注记，不变public wire）
- verification/M2-DERIVED-GC-2/**
- doc/handoffs/M2-DERIVED-GC-2-*.md
- doc/reviews/M2-DERIVED-GC-2-*.md（非作者报告原字节；不得作者代写批准）
- Codex元数据维护：doc/REBASELINE_PLAN.md、doc/STATUS.md、doc/00_INDEX.md、doc/tasks/README.md

## 禁止与停止条件

其他src/apps/tests、产品schema/migration/ArtifactRepositoryPort/RenderOutcome、acceptance_bridge.py/ac1_bridge.rs、ResourceChannelService公共语义、resource_protocol读取share flags、React/UI、依赖、packaging spec/build/install/deploy流程、Legacy、源文件/Managed artifact/用户数据库/模型；不部署/push，不reset/clean/stash或覆盖他人checkout。

禁止改SHA冻结历史probe_ttl_nan*.py、历史报告/原日志；M2-RC2旧verify.ps1及冻结probe不是本Task Gate。不得在线删live-row preview、不按TTL/年龄/数量或UUID猜引用、不把初始化namespace当G7启用许可。发现范围外入口/共享修改先BLOCKED交Codex，不靠补一个未来承诺绕过。

## R4-A1/A2必须吸收的精度

AC1 launcher在initialize之前由fixture创建并核验root/scope/derived；_LoopHarness使用同自有根。initialize只对自有新/空且未绑定catalog调用；run2/已绑定使用普通共享路径，缺失/冲突/旧未知状态拒绝，不重复flag。G3含绑定前红→初始化后绿→run2仍绿。

verification/M2-RC2/review-dsh-a8fb17ca/probe_ttl_nan.py与review-dsh-eac5cb3e/probe_ttl_nan_independent.py是SHA冻结历史证据，不改，不在新Gate集；现行driver仅run_e2e.py。新增SQLite URI范围仅本设计seam，不扩张到其他SQL连接实现。

## Verification 与交付

G1–G7逐项照设计§6执行；当前全部NOT_RUN。环境实测可用：PowerShell，Python=G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe（3.12.3），cargo=C:/Users/49745/.cargo/bin/cargo.exe。下列是计划命令，不能抄作已PASS：

~~~powershell
git status --short --branch
git rev-parse --path-format=absolute --git-common-dir
git rev-parse HEAD
& 'G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe' -m pytest -q tests/core/test_derived_gc.py tests/core/test_rc4_stdio_render_preview.py tests/core/test_page_resource_resolve.py tests/m2_resource_channel tests/m2_acceptance
$env:M2RC1_PYTHON = 'G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe'
cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml
git diff --check
~~~

native共享/独占、句柄删除、双DB保护/崩溃恢复必须真实隔离OS进程/自有fixture，mock不代替。受影响dev/packaged入口以固定head构建+runner验收，缺环境BLOCKED；不改其通过阈值，不使用旧PASS。每次日志有shell/解释器/命令/HEAD/EXIT/收集总数/passed与skip及逐条原因；判别矩阵对照必须有可复核artifact。

交付代码commit、verification/M2-DERIVED-GC-2/完整证据、doc/handoffs/M2-DERIVED-GC-2-<head>.md，逐AC实际结果和G7残留。下一接收者=真实DSH非作者，之后Codex；ready 后经恢复点核对才可认领。完整可转发指令见verification/M2-DERIVED-GC-2/zcode-instruction.md。
