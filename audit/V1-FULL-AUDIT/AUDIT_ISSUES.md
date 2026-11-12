# 问题台账

## AUDIT-11-INC-001 — 私有素材可能随 main 历史传播

- 状态：`INVESTIGATE`（传播风险证据已记录；远端现状及补救未核验/未执行）
- 级别：待 AUDIT-11 深查后定级；当前不将推论写成已完成的安全结论。
- 证据：段 B 范围裁决 [ZCODE-SCOPE-ADJUDICATION-2026-11-12](reports/ZCODE-SCOPE-ADJUDICATION-2026-11-12.md) 与 [阶段 0 日志](logs/stage0-resume-verification-20261112.log)。本地 reflog 记录 2026-10-30 `origin/main` 三次 push；材料对象提交、审计基线、push 目标与当前 HEAD 的祖先关系均 EXIT 0；既有材料报告记载 `.tmp.driveupload` 内含 169 张 JPEG 的压缩对象。
- 影响：仓库文档记录“素材不传播”及“只推干净源码快照”，而本地 Git 证据支持这些对象曾进入公开仓库 main 历史的高置信推论。
- 未知：本轮未实测 GitHub 当前可见性或外部 fetch；未核实当时执行者的完整授权语境；远端缓存/对象状态未知。
- 处置：不 push、不删除、不改写历史、不 GC/prune、不尝试远端补救。记录并继续本地 AUDIT-11；任何需要远端处置的方案另行裁决。

## SEG-B-PROBES-001 — directory junction 下 managed publication 越界写

- 状态：`TRIAGED`
- 级别：`Medium` / confidence `High`（ZCode 只读源码核对与隔离 probe 证据；未独立复现）
- 证据：`reports/PROBE-TRIAGE-SEGMENT-B-2026-11-12.md`、`reports/PROBES-RESULT-SEGMENT-B.md`、对应 log/evidence JSON。`test_managed_publish_follows_directory_junction` 在隔离 `tmp_path` 内实测 `publish_wrote_outside_managed=true`。
- 影响范围：需外部行为者在 managed root 内创建 junction；产品写出受限于生成的 revision bytes，现有外部文件受 `final_path.exists()` 保护。证据未覆盖真实用户目录、GC/归档或其他未测入口。
- 处置：不修改产品代码；修复须另开实现 Task。建议给 `publish` 增加 containment/reparse 防线。已映射至 AUDIT-03（窄面文件管理证据）和 AUDIT-11（路径/写入安全 FAIL）；这不表示任一专项全部完成。

## SEG-B-PROBES-002 — nmbak 磁盘写失败后数据库变更且缺少回滚标识

- 状态：`TRIAGED`
- 级别：`Medium` / confidence `High`（ZCode 只读源码核对与隔离 probe 证据；未独立复现）
- 证据：`reports/PROBE-TRIAGE-SEGMENT-B-2026-11-12.md`、`reports/PROBES-RESULT-SEGMENT-B.md` 与对应 log/evidence JSON。`test_nmbak_restore_disk_failure_leaves_changed_database_without_rollback_id` 实测 `database_changed=true`、`typed_error=false`、`rollback_id_in_error=false`，且 pre_restore 包已创建。
- 影响范围：可恢复性由 pre_restore 包保留；缺陷为裸 I/O 错误缺少 typed error 和 rollback 指引。多文件部分写中间态仅为静态推断，probe 未演示。上层 Core/wire 映射、真实磁盘故障与用户数据影响未验证。
- 处置：不修改产品代码；修复须另开实现 Task。建议把 I/O 错误包装为带 pre_restore `backup_id` 的 `BACKUP_RESTORE_INCOMPLETE`。已映射至 AUDIT-08（窄面恢复证据）和 AUDIT-11（磁盘写失败/恢复 FAIL）；这不表示任一专项全部完成。

## NM-AUD-0001 — sidecar 启动取消与释放未执行显式进程停止

- 状态：`TRIAGED`（静态控制流已确认；隔离 helper 通过真实 `SidecarProcess` API 复现存活；真实 sidecar / 用户可见影响尚未验证；ZCode 阶段 Review 已接受此范围）
- 级别：`P2`（ZCode 对 `beaa13406438fab46ef56fa5a8852bf04ce7133d` 的独立阶段 Review 维持 P2；真实生产 sidecar 的存活行为仍未验证）
- 分类：异步取消 / 进程资源生命周期。
- 位置：`apps/desktop-avalonia/src/NewManga.CoreClient/Transport/SidecarProcess.cs:81-169,299-360`；调用路径 `apps/desktop-avalonia/src/NewManga.CoreClient/Bridge/HostBridgeClient.cs:238-264`、`apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs:258-285,1100-1120,1188-1219`。
- 复现条件（已执行）：隔离 helper 在启动时把自身 PID 写入 workspace 标记文件后忽略 stdin EOF 并 sleep 60 秒；分别使用已取消 token 调 `SidecarProcess.StartAsync`，以及正常启动后直接调用 `DisposeAsync`。
- 预期：启动取消或释放时，sidecar 的 stdin 被关闭、退出被等待；超过宽限期时执行进程树 kill。
- 实际：代码控制流符合上项描述；正式 audit runner probe `20261112T143133097703Z` 实测 pre-cancel 后 `OperationCanceledException` 被调用方观察到，新 helper child 仍存活；direct-dispose 用例中 `DisposeAsync` 约 2,011 ms 返回后，新 helper child 仍存活。两项 helper 随后都由 probe 显式终止，`cleanup_killed_child=true`。未声称生产 Python sidecar 会忽略 EOF。
- 证据：`tests/sidecar_lifecycle_probe.ps1`、`logs/sidecar-lifecycle-probe-20261112T143133097703Z.log`、`evidence/sidecar-lifecycle-probe-20261112T143133097703Z.json`、`logs/sidecar-lifecycle-invalid-run-investigation-20261112.log`、`reports/AUDIT-01-02-ARCHITECTURE-STATIC-2026-11-12.md`、`logs/dotnet-build-audit01-02-20261112.log`、`reports/DOTNET-RESULT-SEGMENT-B-2026-11-12.md`。Avalonia TestHost 仍在测试用例前退出；该 probe 单独验证生命周期，不替代 unit suite。中间 runner run `20261112T142759897356Z` 复用了旧 PID 标记，读取旧 PID 后未跟踪当轮 helper；其 bounded 60 秒 helper 后续自然结束，14:36Z 检查无匹配存活进程。该次日志和 JSON 保留以供追溯，但不作为 finding 证据。
- 影响范围与未知：已证明 pre-cancel 路径与直接 dispose 路径可使忽略 EOF 的子进程在调用返回后继续运行；`HostBridgeClient.DisposeAsync` 不先调用 `StopAsync`。真实 Core/Bridge 对 EOF 的退出行为、真实产品启动取消窗口发生概率、进程继续持有资源的时间及用户可见影响仍未测；不据此推断数据损坏或安全边界绕过。
- 根因/假设：同一 `_disposed` 标记同时阻止重复释放和底层 stop；`DisposeAsync` 设置标记的顺序使其自身 stop 调用短路。取消检查未纳入创建后的 try/finally cleanup。
- 推荐修复方案：另建幂等 stop/cleanup 路径，使 dispose 能实际关闭、等待并按超时终止；把 spawn 后所有失败与取消收口到有所有权的清理逻辑；让 HostBridge shutdown/dispose 覆盖受控进程退出。修复仅可在单独释放的实现 Task 中进行。
- 对应回归测试：使用可控 helper child 覆盖 pre-cancel、spawn 后取消、正常 EOF 退出、忽略 EOF 并超过 grace period；断言子进程及其子树在 dispose 返回后均已退出，并验证 shutdown 错误仍可收敛。
- 处置：本审计不修改产品代码；请 ZCode 对 severity / 分类 / 影响边界作独立复核，后续实现须另开 Task。
- ZCode 阶段 Review：`ACCEPT`，维持 P2（0 个 P0/P1/P2 findings）；原始回执见 `reports/ZCODE-AUDIT-01-02-REVIEW-2026-11-12.md`。P3 observation N-1 补充两条受同一清理短路影响的路径：`SidecarProcess.StartAsync` integrity-fail 清理与 `HostBridgeClient` ping 失败后的 `client.DisposeAsync()`；N-2 要求未来实现设计明确 `HostRuntime` 退出时 HostBridge 的受控 shutdown 顺序。二者不改变严重度和边界，也不授权本 Task 修改产品代码。
