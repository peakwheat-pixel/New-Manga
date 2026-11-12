# 问题台账

## AUDIT-05-CAND-001 — 重叠仲裁保留同几何双 Region

- 状态：`REVIEW_PENDING`（候选观察；未由审计作者确定 severity 或正式 finding）
- 证据：`reports/AUDIT-05-06-SFX-TRANSLATION-2026-11-13.md`、`tests/test_audit05_sfx_regression.py`、`logs/audit05-06-targeted-20261113.log`。合成 same-geometry primary `manga-1` + SFX `sfx-1` 仲裁后保留两个相同 polygon，且二者均映射为 SFX；生产 handler 对每候选创建 Region。
- 影响/限制：`skip` 默认策略避免自动翻译；显式 `translate` 时两个 Region 各自进入单 Region step。未测真实模型重复框概率与用户可见影响；既有仲裁 Task 已列该副作用为已知取舍/去重候选。
- 待裁决：请 ZCode 判断是否为正式 finding、严重级别及是否已由既有 Task/产品语义接受；本审计不授权修复。

## AUDIT-06-CAND-001 — 缺少账单级 spend cap 与 provider idempotency key

- 状态：`REVIEW_PENDING`（候选观察；远端计费影响未知）
- 证据：`reports/AUDIT-05-06-SFX-TRANSLATION-2026-11-13.md`；单 Run 有 StepRun 数上限，provider retry 有上限，但配置/transport 未提供货币预算或 provider 级 idempotency key。
- 影响/限制：超时重试可能使客户端重复发送相同 payload；本轮未调用 API，未验证服务端处理、重放或计费，不能声称发生重复扣费。
- 待裁决：请 ZCode 对照审计范围判断风险定级/是否为产品要求缺口；修复需另行释放 Task。

## AUDIT-06-CAND-002 — glossary 词条优先级未由生产路径强制

- 状态：`REVIEW_PENDING`（候选观察；需需求/语义裁决）
- 证据：`reports/AUDIT-05-06-SFX-TRANSLATION-2026-11-13.md` 与对应 production request seam 测试；glossary 以 source→target 字典进入请求，但 system prompt 和生产响应校验未强制 glossary term match。
- 影响/限制：未调用真实模型，不能推断翻译会违反术语；现有文档/用户预期是否要求强制术语优先级尚待核对。
- 待裁决：请 ZCode 对照原始审计清单、契约及既有 glossary 语义确认；本审计不授权改 prompt 或 response validation。

## AUDIT-14-CAND-001 — V1 承诺与未来规划缺少统一逐项总账

- 状态：`REVIEW_PENDING`（审计治理观察；未判为产品 finding 或分级）。
- 证据：`reports/AUDIT-14-V1-INTEGRITY-2026-11-13.md` §2、§4；`doc/00_INDEX.md:46,87`、`README.md:11,21-34,80-120`、`doc/V11R_PROGRAM.md:3`、`doc/STATUS.md:6`。
- 复现条件/实际：在文档声明的权威来源与当前产品说明中对照，README 说根目录不存在而文件实际存在；README 的存储与版本文案、V11R 计划状态与当前决策有漂移。没有独立 V1/未来逐项承诺总账，因此不能可靠计算数量或完成率。
- 影响/限制：可能导致规划项被误当作 V1 缺陷或反之；目前未发现由此直接导致的运行故障。范围限于本轮查阅的当前文档，不声称扫描了所有历史文件。
- 建议：另开授权文档 Task，固定 V1 manifest、未来规划边界和各产品说明的有效日期；本审计不改现有产品文档。

## AUDIT-14-CAND-002 — V2 Studio 有明确 NOT_WIRED 的可见能力

- 状态：`REVIEW_PENDING`（是否属于 V1 承诺待 ZCode 裁决；GUI 行为未实测）。
- 证据：`reports/AUDIT-14-V1-INTEGRITY-2026-11-13.md` §3；`apps/desktop-avalonia/src/NewManga.App/Shell/V2/AppShellV2.axaml.cs:53-58`、`ViewModels/V2/Studio/StudioPageViewModel.cs:270-282,1808-1835`、`StudioWorkspaceViewModel.cs:28-33`、`StudioTermsViewModel.cs:45-47,79-82`。
- 复现条件/实际：静态走 `AppShellV2` composition；Studio 仅注入 Host/selection/run tracking，遗漏 run/text/flag source 参数，故 page VM 采用 `NotWired*` 默认值；Final/Split 页资源也被 inventory 固定标为 `NOT_WIRED`。
- 影响/限制：若被纳入当前产品承诺，批量 Run 投影、区域文本/状态与成品页显示不可用；未确认 V1 需求归属、用户可见状态或实际 GUI 结果。
- 建议：由 ZCode 对照版本承诺与当前 V2 设计定级；若纳入当前发布范围，另行释放实现 Task 并为每个入口补真实 Host/GUI 回归。

## AUDIT-14-CAND-003 — Avalonia 发布辅助脚本保留旧 Tauri 路径依赖

- 状态：`REVIEW_PENDING`（发布脆弱性候选；未证明 clean release 会失败）。
- 证据：`reports/AUDIT-14-V1-INTEGRITY-2026-11-13.md` §4；`.github/workflows/build-release.yml` installer 调用处不传 `-IconPath`；`apps/desktop-avalonia/scripts/build-installer.ps1` 的缺省回退检查 `apps/desktop/src-tauri/icons/icon.ico`；`scripts/prepare-sidecar.ps1` 的缺省 Source 指向旧 `src-tauri/target/release/resources/core-sidecar`。
- 影响/限制：当前 CI 依赖该 Tauri icon 文件存在；手动 sidecar helper 在新架构产物目录下可能选错输入。此轮未执行 clean build/installer，未证实失败、发行物损坏或用户影响。
- 建议：若 ZCode 接受此观察，另开发布脚本 Task 明确当前资产来源、在隔离干净环境验证并移除无用旧路径引用。

## AUDIT-14-CAND-004 — 多 Avalonia shell 路由扩大 V2 回归面

- 状态：`REVIEW_PENDING`（架构风险观察，未证明为已发生缺陷）。
- 证据：`reports/AUDIT-14-V1-INTEGRITY-2026-11-13.md` §4；`apps/desktop-avalonia/src/NewManga.App/App.axaml.cs:131-176`、`Views/MainWindow.axaml.cs:94-117`、`Shell/V2/AppShellV2.axaml.cs:53-58`。
- 实际：composition 支持 legacy `MainWindow`、Current V2 和 Fluent frontend 分支；页面结构/能力不同。全审目前没有本 Task 的真实 GUI 对照结果。
- 影响/限制：提高路由、导航与功能 parity 的回归成本；当前没有证据表明用户运行时已遇到具体行为错误。
- 建议：ZCode 判定这是否是当前架构的可接受迁移/回退设计；后续验收按 shell/页面记录可达性与关键操作，不能把单一路径测试外推到所有 shell。

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
- 级别：`Medium` / confidence `High`（ZCode 只读源码核对及两次隔离 probe；2026-11-13 在已提交 audit probe 上复跑确认）
- 证据：`reports/PROBE-TRIAGE-SEGMENT-B-2026-11-12.md`、`reports/PROBES-RESULT-SEGMENT-B.md`、`reports/AUDIT-08-SQLITE-PERSISTENCE-2026-11-13.md` 与对应 log/evidence JSON。`test_nmbak_restore_disk_failure_leaves_changed_database_without_rollback_id` 再次观测 `database_changed=true`、`typed_error=false`、`rollback_id_in_error=false`、`pre_restore_packages=1`；隔离复现测试 EXIT 0 的含义是 finding 被确认。
- 影响范围：可恢复性由 pre_restore 包保留；缺陷为裸 I/O 错误缺少 typed error 和 rollback 指引。多文件部分写中间态仅为静态推断，probe 未演示。上层 Core/wire 映射、真实磁盘故障与用户数据影响未验证。
- 处置：不修改产品代码；修复须另开实现 Task。建议把 I/O 错误包装为带 pre_restore `backup_id` 的 `BACKUP_RESTORE_INCOMPLETE`。已映射至 AUDIT-08（本轮专项 FAIL）和 AUDIT-11（磁盘写失败/恢复 FAIL）；这不表示任一专项全部完成。多文件部分写仍仅为静态推断，未由 probe 演示。

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

## AUDIT11-REV-001 — 扫描器源文件自指纹差异

- 状态：`CLOSED_BY_DISCLOSURE`（P3 observation；非产品 finding）。
- 发现：ZCode 对 `e10fd1ee7e326255ffebb4ca529ecee5dfa477d9` 的独立 AUDIT-11 Review `ACCEPT`，记录 0 个 P0/P1/P2 阻断项和 1 个 P3 observation。扫描日志中的源 SHA-256 为 `4BFDDE17DC29EF7619D3A385F010E0877DC6527865C6FC8B5DFD34660F6BD456`，最终 pin 的 SHA-256 为 `8D71732C7DB12CD14711E7AE9E83CCF2F2D753DD3EAEE526B5E446B1463476D8`。
- 复核：重建行 37 末尾含一个 ASCII 空格的 6,193-byte 版本，SHA-256 精确匹配扫描时 hash；提交版 6,192 bytes。差异来自 `git diff --cached --check` 后移除该尾随空格，仅为空白变化，不改变 Python tokens/扫描逻辑。详见 `logs/audit-11-scanner-source-hash-drift-20261112.log`。
- 边界：扫描结果 JSON SHA-256 与记录统计未变；本次没有重跑 scanner，不能声称新扫描 PASS。review 报告、原始回执及 dispatch 日志见 `reports/ZCODE-AUDIT-11-REVIEW-2026-11-12.md`、`evidence/zcode-audit11-review-20261112.json`、`logs/zcode-audit11-review-dispatch-20261112.log`。


## AUDIT-07-CAND-001 — P16 reader export hook options test failures

- 状态：`REVIEW_PENDING`（候选观察；不由审计作者分配 severity 或正式 finding）。
- 证据：`reports/AUDIT-07-REPAIR-TYPESET-EXPORT-2026-11-13.md`、`logs/audit07-core-rerender-export-20261112T205159956924Z.log`。三个参数化 case 中 ZIP compression override 未生效、text representation override 未生效，且空 override case 未产生预期的 hook audit events；测试组 127 passed / 3 failed / EXIT 1。
- 边界：该测试覆盖 reader export plugin hook/options 与 history，不测排版像素或真实导出视觉质量；当前尚未重复运行或单独归因到产品缺陷。
- 待裁决：请 ZCode 判断是否属于 AUDIT-07 或既有 export scope，是否构成正式 finding 及严重度；本审计不授权修复。

## AUDIT-07-CAND-002 — 用户字体许可证备注不是授权验证

- 状态：`REVIEW_PENDING`（范围/风险待裁决；不宣称存在未授权分发）。
- 证据：`src/application/fonts/service.py` 接受可选 `license_note` 并原样保存；FEA-14-FONT-1 要求不随包分发字体且把字体渲染消费留给 FONT-2；静态捕获显示仓库 tracked font assets=0。
- 边界：本轮没有读取用户字体、核验外部许可或观察随包/发布；`license_note` 只能作为用户备注，不能证明许可。用户字体许可检查 `NOT_RUN`。
- 待裁决：请 ZCode 判断备注/许可边界是否已由 FEA-14-FONT-1 limitation 接受，或需要独立产品要求/Task；不在本审计内改变字体导入语义。

## AUDIT-09-CAND-001 — V2 Reader Retry 提示与可见选择不一致

- 状态：`REVIEW_PENDING`（候选观察；审计作者不分配 severity，也不确定为正式 finding）。
- 证据：`reports/AUDIT-09-UI-UX-2026-11-13.md`、`screenshots/audit09-v2-reader-retry-banner-20261113.jpg`、`logs/audit09-ui-v2-capture-20261112T220906Z.log` 及对应 JSON。隔离 V2 Library 选择了合成 book/chapter（章节 0 页）；Reader Retry 后仍提示“请先在资料柜选择作品与章节”。
- 边界：仅在合成空章节路径观察；没有真实页图或操作数据，未验证状态根因、真实用户影响或其他导航路径；不据此推断数据丢失。
- 待裁决：请 ZCode 判断提示是否构成 UI finding、severity 与需求归属；本审计不授权修复。
