# M2-DERIVED-GC-2：给 ZCode 的完整实施指令

ZCode：M2-DERIVED-GC-2 已正式 ready，Owner=ZCode，非作者 Reviewer=DeepSeek Harness，Integrator=Codex。先核对 Codex 提供的固定 release HEAD，再认领 in_progress；本轮 Codex 只完成释放和同步，没有启动实现。
唯一仓库G:/CODEX/New Manga，任务branch=agent/zcode/M2-DERIVED-GC-2，任务worktree=G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode；准备基线base=ad75fadc2944983b4322f353176ba70cf0b0b7ae，正式 release_commit/实测 Owner HEAD=5896db8c64b90b53b015eb9c46c7dab6ab29210b（clean，已快进）；common-dir=G:/CODEX/New Manga/.git；本指令与恢复记录为主仓库提交后追加的纯治理证据，Owner checkout 留在固定 release。设计批准 head=e4c0967f83a08d9b9e2d84605d17923e81a844b6；依赖 GC-1@44859014、RC4@0a7e0d5b、本设计 merge@ad75fadc，均已集成。先按Codex release恢复点核对git status、HEAD、common-dir、Task依赖/授权；不猜路径、不使用他人dirty checkout。
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

## 可复制的定向验证命令（planned / NOT_RUN）

~~~powershell
Set-Location 'G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode'
git status --short --branch
git rev-parse HEAD
git rev-parse --path-format=absolute --git-common-dir
& 'G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe' -m pytest -q tests/core/test_derived_gc.py tests/core/test_rc4_stdio_render_preview.py tests/core/test_page_resource_resolve.py tests/m2_resource_channel tests/m2_acceptance
$env:M2RC1_PYTHON = 'G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe'
& 'C:/Users/49745/.cargo/bin/cargo.exe' test --manifest-path apps/desktop/src-tauri/Cargo.toml
git diff --check
~~~

上述命令不替代 G1-G7、真实 native/双进程/恢复及固定 head dev+packaged Gate。不得把 skip/NOT_RUN/BLOCKED 写成 PASS。
