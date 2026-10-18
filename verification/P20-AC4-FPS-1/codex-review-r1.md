---
task_id: P20-AC4-FPS-1
reviewer: Codex
author: ZCode
base_commit: a04e4ea78d5b33a0f91efcdc06b396391c4b165e
reviewed_head: 01129315100928751546c9608456868f5085fa8c
decision: changes_requested
---

# 独立 Review

## 结论与范围

审查实现提交 01129315100928751546c9608456868f5085fa8c；文档 Task/Handoff commit 为 b3612908000438d290bf65efcee0249b86f5c648。Task 中 8 个 Canonical Evidence SHA-256 均与磁盘字节一致，且对应完整 40 位 commit 确实包含该路径。AC4 原延迟证据没有被该实现提交覆盖。治理检查 tools/governance/check.ps1 返回 PASS（3 warnings），其中一项指出本 Review 文件尚未登记为 Canonical Evidence；本轮硬约束只允许写 Review 文件，因此没有改 Task pin。

钩子默认关闭、样本计算和单元级测试实现基本符合冻结口径；但测量 runner 存在 AppData 数据根回退、全局结束其他 sidecar 进程、失败仍返回成功，以及统计排除可能掩盖前台长停顿等问题。

## Findings

| ID | 级别 | 状态 | file:line 依据 | 最小修法 |
|---|---|---|---|---|
| FPS-R1-01 | P1 | FAIL | verification/P20-AC4-FPS-1/run-ac4-fps.ps1:70-75 只设置 NEWMANGA_DATA_ROOT。apps/desktop/src-tauri/src/main.rs:1249-1267 在没有 M2RC1_SRC_ROOT 且 packaged sidecar 存在时自动走 packaged_user_root；:1321-1347 会分别把未显式指定的 derived、managed、catalog 路径回退到 %APPDATA%/com.newmanga.m2rc1.desktop。runner 没有设置 M2RC1_DERIVED_ROOT、M2RC1_MANAGED_ROOT、M2RC2_CATALOG_DB，因此隔离根不完整，可能把测量库、managed 文件或 catalog 写入用户 AppData。 | 在启动 exe 前将这三个路径都显式指向新建的 %TEMP% 隔离根，并在缺少路径配置时 fail closed；若跑 dev 模式，也显式设置并核对 M2RC1_SRC_ROOT。 |
| FPS-R1-02 | P1 | FAIL | verification/P20-AC4-FPS-1/run-ac4-fps.ps1:219-223 通过进程名直接 Stop-Process 所有 core_service、host_bridge 实例，没有核验其 PID 是否为本轮启动的后代；若用户另有正在运行的实例，正常收尾会强制终止它。启动后早退路径（:101-102、:219 之后未到达的 exit）也没有统一 finally 清理。 | 记录本轮 app PID 及其后代 PID，只等待/结束这些进程；用 finally 处理正常、失败和人工中止，并再次确认本轮进程退出。 |
| FPS-R1-03 | P1 | FAIL | verification/P20-AC4-FPS-1/run-ac4-fps.ps1:162-180 对 UIA CSV/JSON 读取失败只写日志；:185-202 对缺 CSV 只记 SUMMARY missing csv，对 avg 超限只输出 ASSERT FAIL；主流程 :214-216 忽略 CaptureRound 失败后的整体结果，最终 :237 无条件 exit 0。因而没有样本、抓取失败或 avg > 50 ms 都能让 runner 返回成功。 | 累积每轮 capture、复算和阈值结果；任一 required artifact 缺失或断言失败时返回非零，只有单页与 Webtoon 都完整测量且 avg 判定通过时才返回 0。 |
| FPS-R1-04 | P2 | PARTIAL | apps/desktop/frontend/src/perf/FpsRecorderPanel.tsx:26-43、:107-115 只创建 Blob URL 并触发 anchor.download，代码没有接收 OutDir、调用显式文件保存 API 或设置下载路径。WebView2 的 DefaultDownloadFolderPath 默认是用户系统下载目录；用户可在 Save As 中覆盖。当前实现不能证明每次都由调用方指定 OutDir，也不能排除按默认下载位置保存。参见 [Microsoft WebView2 默认下载目录](https://learn.microsoft.com/en-us/dotnet/api/microsoft.web.webview2.core.corewebview2profile.defaultdownloadfolderpath) 与 [DownloadStarting 路径控制](https://learn.microsoft.com/en-us/microsoft-edge/webview2/reference/win32/icorewebview2downloadstartingeventargs)。 | 使用显式 Save As/文件保存选择流程，将选定目录作为当前导出目标；取消时不写默认位置。保留当前无直接路径写入的前端边界。 |
| FPS-R1-05 | P2 | PARTIAL | apps/desktop/frontend/src/perf/fpsRecorder.ts:190-205 对所有 delta ≥1000 ms 无条件标记 raf_gap_ge_1000ms；:209-230 只对未排除样本计算 kept avg/max/p95。verification/P20-AC4-FPS-1/run-ac4-fps.ps1:187-200 也只按 excluded=0 复算。页面隐藏/系统休眠以外的前台主线程停顿超过 1 秒会被同样排除；CSV 虽保留行，但汇总 max 与 avgWithinThreshold 可以不反映此长尖峰。 | 仅在采样确认页面不可见/系统挂起时从 kept 指标排除；否则保留尖峰参与统计。至少同时报告全样本 max 与被排除样本的最大间隔，避免 PASS 隐去观测到的停顿。 |

## AC 逐项状态

| AC | 状态 | 核验依据 |
|---|---|---|
| AC1：默认关闭、无 rAF 注册与样本数组 | PASS | main.tsx:11-12 仅在 readFpsRecorderRequest 为 true 时调用 startFpsRecorder；fpsRecorder.ts:165、:234-240 只在 start 分配 samples 并首次注册 rAF，:178-206 的后续注册仅发生在帧回调中。关闭态单元测试覆盖默认导入无注册/无 recorder，默认 DOM 无面板。本轮 npm test 复跑 32 files / 319 tests，exit 0。 |
| AC2：OutDir 落盘、无 AppData 直接写入、无默认落盘 | PARTIAL | fpsRecorder.ts 与 FpsRecorderPanel.tsx 不直接访问文件系统或 AppData；导出只在用户点击后触发 Blob download。但前端未把用户选定路径传进代码或固定 OutDir，下载路径受 WebView2 默认目录/Save As 行为控制；测量 runner 的应用数据根也未完整隔离，见 FPS-R1-01、FPS-R1-04。 |
| AC3：真实桌面单页与 Webtoon 测量 | NOT_RUN | 本轮没有启动 GUI；没有样本级 CSV 或现场汇总。Owner 标记 NOT_RUN 正确，不能记 PASS。脚本与指南存在 FPS-R1-01、02、03 所列问题，修正并由 Coordinator 在真实桌面执行后才能验收。 |
| AC4：允许的排除项、逐样本留痕、不可配置 avg 门槛、p95/max | PARTIAL | 排除原因只有 raf_gap_ge_1000ms 与 non_positive_delta，excluded 行保留在 CSV（fpsRecorder.ts:31-33、:190-205、:264-270）；avg 门槛是常量 50（:25-30），nearest-rank p95 与 kept max 都由汇总输出（:146-159）。但 >=1 s 前台停顿也会排除并不参与汇总，见 FPS-R1-05，故不能确认无尖峰遮蔽可能。 |
| AC5：撕裂只记限制、不声称已验证 | PASS | run-ac4-fps.ps1:18-19、:225-234 与 MEASUREMENT-GUIDE.md:34-37 明确记录 NOT_VERIFIED_BY_RULING；本报告不把撕裂记为 PASS。 |
| AC6：前端回归与 AC4 既有延迟不退化/不覆盖 | PASS | 本轮 npm test：32 files / 319 tests，exit 0；npx tsc --noEmit：exit 0。旧证据 verification/P20/ac4-20261018-0720/ac4-metadata.txt:3-8 仍记录 20/20 有效样本、avg 36 ms、p95/max 62.4 ms、FPS NOT_MEASURED；ac4-trace.log:27-29 保留同一结论。该实现 commit 不包含 verification/P20/** 的覆盖修改。 |
| AC7：不改 P20 其他 AC 实现/阈值 | PASS | 实现提交的文件范围是 frontend/src/main.tsx、frontend/src/perf/**、verification/P20-AC4-FPS-1/**；未改 IPC、契约、Schema、ACL、依赖或 src-tauri。 |

### 本轮验证记录

| 项 | 命令 | 环境与退出码 |
|---|---|---|
| 前端测试 | npm test | PowerShell 7.6.6、Node v24.15.0、npm 12.0.1；32 files / 319 tests；exit 0。日志位于 C:\Users\49745\AppData\Local\Temp\codex-p20-review-aa95e4a226814ea998336172bf91c73b。 |
| TypeScript | npx tsc --noEmit | 同一隔离验证环境；exit 0，无诊断。 |
| PowerShell parser | [System.Management.Automation.Language.Parser]::ParseFile 对 run-ac4-fps.ps1 | 0 parse errors；这只证明语法可解析，不代表真实桌面运行通过。 |

## 未能验证项

1. AC3 单页和 Webtoon 真实交互桌面测量及 CSV/JSON 产物；按任务分工由 Coordinator 执行。
2. WebView2 下载 UI 是否在目标版本上每次都要求用户选择路径。本轮按源码与 Microsoft API 文档判为 OutDir 保证不足，未启动窗口验证。
3. runner 对本轮实际 app/sidecar PID 的清理行为；没有运行测量脚本，避免启动 GUI、写用户/验证数据或结束其他同名进程。
4. Tearing 依用户裁决保持 NOT_VERIFIED_BY_RULING。

## 集成建议

**不可批准集成。** FPS-R1-01/02 涉及用户数据隔离和进程所有权，FPS-R1-03 可能把失败测量报成成功；AC3 也仍是 NOT_RUN。修正 runner 与统计口径后，再由 Coordinator 执行单页和 Webtoon 的真实桌面测量，并把产物与 exact build/head 关联后重新 Review。