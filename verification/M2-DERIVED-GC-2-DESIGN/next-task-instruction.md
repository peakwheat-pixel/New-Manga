# 指令二：仅准备，先由Codex正式释放，再给ZCode

Task=M2-DERIVED-GC-2；Owner=ZCode；非作者Reviewer=DeepSeek Harness；Integrator=Codex。唯一仓库G:/CODEX/New Manga；设计merge/base=ad75fadc2944983b4322f353176ba70cf0b0b7ae，设计批准head=e4c0967f83a08d9b9e2d84605d17923e81a844b6。依赖GC-1@44859014、RC4@0a7e0d5b及本设计集成。

恢复点已实测：branch=agent/zcode/M2-DERIVED-GC-2；worktree=G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode；base=ad75fadc2944983b4322f353176ba70cf0b0b7ae；allocated HEAD=e093f0106bf62476c640dbcf8bb47448c8cc644c，clean，common-dir=G:/CODEX/New Manga/.git。此head含proposed准备文件，不是ready/release，尚未开工。Task状态proposed，当前无生产实施授权。

~~~mermaid
flowchart LR
  D["设计 · Codex / DSH<br/>已集成 ad75fadc"] --> P["GC-2 · ZCode<br/>proposed，未实施"]
  P --> R["Codex<br/>正式ready + 同步恢复点"]
  R --> I["ZCode实现<br/>G1–G7实际证据"]
  I --> V["非作者DSH<br/>新fixed-head Review"]
  V --> M["Codex<br/>集成 + 集成后检查"]
  I --> B["G7未知/无法证明<br/>两sweep禁用 · BLOCKED"]
~~~

## 发给Codex的释放指令

~~~text
在G:/CODEX/New Manga读取AGENTS、Plan、STATUS、doc/tasks/M2-DERIVED-GC-2.md、已集成设计及DSH r4原报告。
只释放已有proposed M2-DERIVED-GC-2，不扩大范围。实测main/分配worktree的HEAD、branch、common-dir、dirty；确认base ad75fadc之后只有已知治理差量，生产漂移须重核。核对三个依赖done、Owner=ZCode/Reviewer=DSH/Integrator=Codex、Task冻结的完整allowed_paths及辅助catalog Schema/内部trusted seam。
在Plan/STATUS串行登记唯一Active，把Task proposed→ready，提交正式release；由Codex在干净的本Task工作区快进到该固定release，再填最新base/head/恢复点，不让ZCode自行猜路径或改proposed。
没有进一步产品裁决的已冻范围可按正常Gate推进；真正范围外改动或G7证据不足记BLOCKED/不启两sweep，不放宽判据。最后把下面ZCode指令与实际release hash一起转发；不要启动其他Task或复用他人dirty checkout。
~~~

## 正式释放后转发给ZCode

~~~text
ZCode：仅在Codex把M2-DERIVED-GC-2正式ready并提供release hash之后执行；本文件目前proposed，不能直接开工。
唯一仓库G:/CODEX/New Manga，任务branch=agent/zcode/M2-DERIVED-GC-2，任务worktree=G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode；准备基线base=ad75fadc2944983b4322f353176ba70cf0b0b7ae，实际分配head见下方实测记录。先按Codex release恢复点核对git status、HEAD、common-dir、Task依赖/授权；不猜路径、不使用他人dirty checkout。
读AGENTS、doc/REBASELINE_PLAN.md、doc/STATUS.md、doc/09_COLLABORATION.md、正式Task、doc/contracts/M2_DERIVED_PREVIEW_GC_DESIGN.md与doc/reviews/M2-DERIVED-GC-2-DESIGN-e4c0967f-dsh-r4.md。在Task分支认领in_progress，独立Owner=ZCode，Reviewer=DSH，Integrator=Codex。
实现明确origin/retired+受控启动静默窗口，复用artifact repo/publisher/catalog/handle_resolver；保护current/pinned、有效grant、在途流、Managed/source/人工修改/Lock；Unknown一律保留。无TTL/年龄/数量猜删、无在线live-row删除、无未知历史origin回填、无通用GC框架。
allowed_paths只有：
src/infrastructure/resource_channel/{catalog_store.py,handle_resolver.py,catalog_loader.py,render_preview.py,host_bridge.py}，src/bootstrap/core_service.py；
apps/desktop/src-tauri/src/{core_bridge.rs,library_bridge.rs,main.rs}；
tests/core/{test_derived_gc.py,test_rc4_stdio_render_preview.py,test_page_resource_resolve.py}；
tests/m2_resource_channel/{test_catalog_authority.py,test_bridge_and_thresholds.py,test_handle_resolver.py,test_sidecar_isolation.py}，tests/m2_acceptance/test_acceptance_loop.py；
packaging/m2ac5/run_clean_start_e2e.py、packaging/release-gate/run_release_gate.py，仅fixture初始化参数；
verification/M2-RC2/run_e2e.py、verification/M2-AC1/run_e2e.py，仅现行driver首次fixture初始化；
正式Task、已冻设计/ M2-C1内部窄注记、自己的verification/M2-DERIVED-GC-2/**和Handoff；总索引/主线状态只由Codex维护，Review只收非作者原报告。
允许共享变化仅catalog来源/单行namespace元数据、channel窄retired写权限、内部revoke retire_preview位及可信fixture初始化flag。禁止产品Schema/migration/ports/RenderOutcome、其他src/apps/tests、acceptance_bridge.py/ac1_bridge.rs、grant公共语义/reader share flags、React、依赖、packaging spec/build/install/deploy流程、Legacy、用户文件/Managed artifact删除；不部署/push/reset/clean/stash，不改历史SHA冻结probe/报告/原日志。
R4-A1：AC1 fixture先自己建立并核验root/scope/derived；_LoopHarness用同自有根；只有新/空未绑定catalog才显式initialize。run2/已绑定只走正常共享，不重复flag；必须留绑定前拒绝→初始化后可用→run2仍可用对照。旧未知/已有行/冲突不claim。
R4-A2：verification/M2-RC2/review-dsh-*/probe_ttl_nan*.py是SHA冻结历史证据，不改且不列入新Gate；现行driver仅run_e2e.py。
G1-G7逐项真实验证：来源/权限；所有轮换失败分支与零busy mark；双OS进程共享/独占/崩溃释放和完整首次装配入口；current/pin/有效grant/unknown保留对照；人工修改hash/size、junction/身份替换、在途流/sharing、DB busy及各crash点；F05隔离/定向pytest/cargo/固定head dev+packaged构建验收；G7旧runtime退出与全入口受保护证据。G7不能证明则live-preview与orphan/dead-row两sweep恒禁用，记BLOCKED，不借设计批准启用删除。
PowerShell环境Python=G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe(已测3.12.3)，cargo=C:/Users/49745/.cargo/bin/cargo.exe。pytest跑Task所列三个core文件+tests/m2_resource_channel+tests/m2_acceptance；cargo按Task命令设M2RC1_PYTHON并test manifest。native双进程/句柄/DB保护必须实际OS隔离fixture；mock/静态/旧PASS不能代替。产品/模型外部凭证缺失明确BLOCKED，不申请无审批通道提升或伪造PASS。
交付实际固定代码head、完整verification日志（shell/解释器/命令/HEAD/EXIT/passed/skip逐条原因/对照artifact）、逐AC结果与doc/handoffs/M2-DERIVED-GC-2-<head>.md。交真实DSH新fixed-head非作者Review，条件闭合后Codexmerge+集成后验证才done；不审核自己，不合并主线。设计完成不等于回收已实现。
~~~

实测见next-task-allocation.log。正式释放前Codex同步含ready的实际release；本阶段没有派发/启动ZCode。
