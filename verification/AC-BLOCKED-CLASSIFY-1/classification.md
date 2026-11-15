# 72 条 blocked 的可闭性分类

生成于 HEAD `73da5ab40`；总数 **72**

| 分类 | 条数 | 含义 |
|---|---|---|
| ARCHIVE | 15 | 旧架构已退出，不可闭，登记历史存档 |
| HUMAN | 7 | 需物理设备/人眼/外部账号 |
| RERUN | 14 | 需复跑测试/构建 |
| DOC | 2 | 缺文档/登记 |
| IMPL | 2 | 缺测试/实现 |
| OTHER | 32 | 其它 |

## 逐条明细

| # | 卡 | AC | 分类 | 理由（截断） |
|---|---|---|---|---|
| 1 | `V11R-C-2` | ? | **OTHER** | GAP-3「跟随系统强调色」仅作用域生效、不写设置文件、不跨重启保持（verification/V11R-C-2/DEVIATIONS.md GAP-3；AppearanceSectionView.axaml:59 注明 |
| 2 | `CHAPTER-MANUAL-SORT` | AC10 | **RERUN** | App.Tests 955/0/11/966 通过(2026-11-15)；CoreClient 与 Python 套件本轮未跑 |
| 3 | `V11R-D-1` | ? | **ARCHIVE** | DS 侧已验（test:ReducedMotion_* 见原注释；焦点环 2px accent outline；DESIGN_SYSTEM §2.3 对比度断言），但『reduced-motion 生效』在旧壳不成立：旧 |
| 4 | `FEA-04` | AC1 | **OTHER** | 原标 <<PARTIAL: 范围冻结；实现未开始>>；status:done 指范围冻结完成，非实现完成 |
| 5 | `FEA-04` | AC2 | **OTHER** | 原标 <<PARTIAL: 范围冻结；实现未开始>>；status:done 指范围冻结完成，非实现完成 |
| 6 | `FEA-04` | AC3 | **OTHER** | 原标 <<PARTIAL: 范围冻结；实现未开始>>；status:done 指范围冻结完成，非实现完成 |
| 7 | `FEA-04` | AC4 | **OTHER** | 原标 <<PARTIAL: 范围冻结；实现未开始>>；status:done 指范围冻结完成，非实现完成 |
| 8 | `FEA-04` | AC5 | **OTHER** | 原标 <<PARTIAL: 范围冻结；实现未开始>>；status:done 指范围冻结完成，非实现完成 |
| 9 | `FEA-04` | AC6 | **OTHER** | 原标 <<PARTIAL: 范围冻结；实现未开始>>；status:done 指范围冻结完成，非实现完成 |
| 10 | `FEA-04` | AC7 | **OTHER** | 原标 <<PARTIAL: 范围冻结；实现未开始>>；status:done 指范围冻结完成，非实现完成 |
| 11 | `FEA-04` | AC8 | **OTHER** | 原标 <<PARTIAL: 范围冻结；实现未开始>>；status:done 指范围冻结完成，非实现完成 |
| 12 | `V11R-C-1` | ? | **HUMAN** | 屏幕验收面无对象：本卡为 headless 库卡（allowed_paths 仅 NewManga.ThemeEngine + tests，doc/tasks/V11R-C-1.md:20-22），SCREEN_SPEC |
| 13 | `V11R-C-1` | ? | **OTHER** | build.log:22(0 个警告/EXIT=0) 通过；但引擎无 .axaml，AC4 的 DynamicResource/令牌子项无对象，且 BuiltInThemeGenerator.cs:93 有裸色常量 #1 |
| 14 | `V11R-C-1` | ? | **OTHER** | 单测与 dotnet test 绿已核实（dotnet-test-themeengine.log:219=203 通过 0 失败；dotnet-test-full.log:16 App 232 通过 0 失败）；缺「关键 |
| 15 | `V11R-C-1` | ? | **DOC** | 构建/测试日志与偏差/未验证清单齐全（build.log、dotnet-test-full.log、DEVIATIONS.md、README.md:73 §5）；缺「截图」：verification/V11R-C-1 目 |
| 16 | `V11R-B-5` | ? | **OTHER** | SCREEN_SPECS 无导出预检/术语章节（grep '预检/术语'@doc/plan/V11R_SCREEN_SPECS.md 0 命中；FUSION_SPEC.md:98-99 仅跨切面矩阵行），「按对应章节的布 |
| 17 | `V11R-B-5` | ? | **OTHER** | 无空间/模式切换上下文保留证据：V2StudioExportTermsTests 7 例无 VM 复用/选择/滚动断言（ToolsOverlay 仅开关@apps/desktop-avalonia/tests/NewMa |
| 18 | `V11R-B-5` | ? | **OTHER** | 六态证据缺失：仅有 preflight/readonly/history/terms 各自功能证据（V2StudioExportTermsTests.cs:45/:222/:249/:286），无 idle/loadin |
| 19 | `V11R-B-5` | ? | **OTHER** | 本卡无 conformance/design-system-usage 记录；共享 StudioTheme.axaml 裸间距未清零（:267/:288/:328/:387，verification/V11R-B-3/D |
| 20 | `V11R-B-4` | ? | **IMPL** | partial 状态有赋值路径但无验证：StudioBatchRunState.Partial 出现在 enum(StudioBatchViewModel.cs:44)/HasData(:440)/文案(:448)，** |
| 21 | `V11R-B-4` | ? | **OTHER** | 「无裸间距」未清零：StudioTheme.axaml:267(Padding=10,4)/:288(Width=8)/:328(Width=480)/:387(Padding=6,0)（登记 verification/ |
| 22 | `V11R-B-3` | ? | **OTHER** | 「无裸间距」未清零：StudioTheme.axaml:267(Padding=10,4)/:288(Width=8)/:328(Width=480)/:387(Padding=6,0) 为无 Nm.* 令牌的裸值，登记 |
| 23 | `P02` | AC1 | **ARCHIVE** | 旧架构（Tauri/React/WebView2）已退出：AD-002:30 明确移除 Tauri/Rust host/WebView2，AD-002:163 S5 已将旧壳原位冻结为证据、不再参与发布，apps/des |
| 24 | `P02` | AC2 | **ARCHIVE** | 旧架构退出（AD-002:30/:163、apps/desktop/LEGACY_FROZEN.md:5-6）；本卡 closed_with_limitations、不改写为 PASS（P02.md:35），AC1–AC |
| 25 | `P02` | AC3 | **ARCHIVE** | 旧架构退出（AD-002:30/:163、LEGACY_FROZEN.md:5-6；P02.md:35 不改写为 PASS、:58 AC1–AC7=BLOCKED / NOT_RUN）。缺：真实 WebView2 下 3 |
| 26 | `P02` | AC4 | **ARCHIVE** | 旧架构退出（AD-002:30/:163、LEGACY_FROZEN.md:5-6；P02.md:35、:58）。缺：目标架构下 retype/undo/restore 写后刷新观测面（REAL_WEBVIEW_MOCK |
| 27 | `P02` | AC5 | **ARCHIVE** | 旧架构退出（AD-002:30/:163、LEGACY_FROZEN.md:5-6；P02.md:35、:58）。缺：目标架构真实按键/焦点采集面；且新时点记录产品缺口 P-01（Escape 无法关闭确认对话框）仍未关 |
| 28 | `P02` | AC6 | **ARCHIVE** | 旧架构退出（AD-002:30/:163、LEGACY_FROZEN.md:5-6；P02.md:35、:58）。缺：Avalonia 目标架构下 computed foreground/background 与 tok |
| 29 | `P02` | AC7 | **ARCHIVE** | 旧架构退出（AD-002:30/:163、LEGACY_FROZEN.md:5-6；P02.md:35、:58）。缺：目标架构证据面与 finding 处置闭环——产品缺口 P-01/P-02/P-03 与 BC-AC5 |
| 30 | `GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1` | ? | **OTHER** | 缺第 7 类「保护集合回退」负例测试：6 类有测试（test:test_wrong_digest_fails_closed@tools/governance/tests/test_residual_runtime_ide |
| 31 | `GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1` | ? | **OTHER** | 命令与 EXIT 已记录（file:verification/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1/verification-log.txt:17-19 Ran 12 tests/EX |
| 32 | `GATE3-COVERAGE-MATRIX` | AC2 | **OTHER** | 缺 4 格 `测试名 (文件:行)`+断言说明：Region 编辑/阅读偏好/主题外观/整书进度仍只有类名或方法名（doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11- |
| 33 | `GATE3-COVERAGE-MATRIX` | AC3 | **OTHER** | 缺 `[Fact]`（纯逻辑）分类：§2 只给出 `[AvaloniaFact]` 62 文件（doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md:35）与 |
| 34 | `GATE3-COVERAGE-MATRIX` | AC4 | **RERUN** | §3 的 ❌ 格已清零（doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md:160、:257），但 Host/Core 层 100 项 NOT_RUN 的归 |
| 35 | `GOV-PIN-LINEAGE-1` | AC1 | **OTHER** | 原标 <<BLOCKED: r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC>>；本卡 status:closed_with_limitations 指 r27 撤回原方案、r28 停止改造后收口，非 |
| 36 | `GOV-PIN-LINEAGE-1` | AC2 | **OTHER** | 原标 <<BLOCKED: r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC>>；本卡 status:closed_with_limitations 指方案撤回后收口，非 AC 实施完成；tools/ |
| 37 | `GOV-PIN-LINEAGE-1` | AC3 | **RERUN** | 原标 <<BLOCKED: r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC>>；本卡 status:closed_with_limitations 指方案撤回后收口，非 AC 实施完成；6 项 LI |
| 38 | `GOV-PIN-LINEAGE-1` | AC4 | **OTHER** | 原标 <<BLOCKED: r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC>>；本卡 status:closed_with_limitations 指方案撤回后收口，非 AC 实施完成；23 项 M |
| 39 | `GOV-PIN-LINEAGE-1` | AC5 | **OTHER** | 原标 <<BLOCKED: r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC>>；本卡 status:closed_with_limitations 指方案撤回后收口，非 AC 实施完成；六类回归夹具 |
| 40 | `GOV-PIN-LINEAGE-1` | AC6 | **OTHER** | 原标 <<BLOCKED: r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC>>；本卡 status:closed_with_limitations 指方案撤回后收口，非 AC 实施完成；lineag |
| 41 | `V11R-A-3` | ? | **IMPL** | AC4 要求补强 CommandParityContractTests：本卡交付明确未改该文件（verification/V11R-A-3/README.md:95-96 自述『git diff 无这些文件；66→76  |
| 42 | `V11R-C-3` | ? | **OTHER** | tag 已存在（git tag -l v11r-pre-retire → annotated，指向 df883f2ce；verification/V11R-C-3/R1-tag.txt:7），但两项未满足：①未用 rol |
| 43 | `M2-REGION-RETYPE-CORE` | ? | **ARCHIVE** | 旧架构（Tauri/Rust host）已退出：AD-002:30 明确移除 Rust host，AD-002:163 S5 将旧壳原位冻结为证据、不再参与发布，apps/desktop/LEGACY_FROZEN.md |
| 44 | `M2-REGION-RETYPE-CORE` | ? | **RERUN** | 11 断言用例在树内（tests/editing/test_region_retype.py:75/102/129/158/197/237/263/421/496/522 + tests/providers/test_r |
| 45 | `M2-REGION-RETYPE-CORE` | ? | **ARCHIVE** | PROTOCOL_MINOR=3 已落（grep:PROTOCOL_MINOR = 3@src/bootstrap/core_service.py:324），但 AC5 的「M2-AC5 GATE 25/25 重跑 PA |
| 46 | `M2-REGION-RETYPE-CORE` | ? | **ARCHIVE** | 回归含 cargo + vitest（旧 Rust/React 面，已冻结：apps/desktop/LEGACY_FROZEN.md:5-6、AD-002:30），pytest 三套件与 m2_acceptance 本 |
| 47 | `RUN-IPC-1` | AC4 | **RERUN** | AC4-2 未满足：缺每条命令的成功路径测试，也缺 ControlRun 非法 action 返回 INVALID_REQUEST、StartRun 幂等键复用返回 IDEMPOTENCY_KEY_REUSED 等 ho |
| 48 | `RELEASE-PACKAGE-1` | AC6 | **DOC** | 缺 Handoff：doc/handoffs 无 RELEASE-PACKAGE-1-*.md（分支 task/RELEASE-PACKAGE-1 与 worktree 亦无）；check.ps1 -TaskPath、s |
| 49 | `M2-SFX-CORRECTION-EXPORTER` | ? | **OTHER** | T1b（批量数据生产）产物尚不存在，「与 T1b 产物同构、训练侧零适配」无法验证（Lead 裁决：w7 报告 §需裁决 5）；已核实的只是 T1a 格式面：test:test_manifest_files_are_t1 |
| 50 | `TASK-056` | ? | **RERUN** | 实现与用例在树内（grep:def is_safe_relative_path@src/application/maintenance/cleanup.py:229 + grep:_safe_targets@src/ap |
| 51 | `TASK-056` | ? | **RERUN** | 实现与用例在树内（grep:def preview@src/application/maintenance/cleanup.py:127 + grep:def to_dict@src/application/mainte |
| 52 | `TASK-056` | ? | **RERUN** | 实现与用例在树内（grep:class WebtoonTileCacheSweeper@src/infrastructure/imaging/tile_cache_sweep.py:22；test:test_lists_ |
| 53 | `TASK-056` | ? | **RERUN** | 实现与用例在树内（grep:def retry_pending_cleanups@src/application/maintenance/cleanup.py:160 + grep:def pending_cleanup |
| 54 | `TASK-056` | ? | **ARCHIVE** | 5 次逐次记录存在（file:verification/TASK-056/full-suite-run1.log … run5.log，各 900 passed），但「全仓 passed 不减少」须当轮全仓套件复算；旧  |
| 55 | `TASK-056` | ? | **RERUN** | Handoff/verification/Review/集成俱在（file:doc/handoffs/TASK-056-delivery.md + file:verification/TASK-056/ + file:d |
| 56 | `V11R-C-RESEARCH-1` | ? | **OTHER** | 文档声明『V1 不引入任何第三方 UI/主题框架依赖』(RESEARCH_V1.md:8)；但『不修改生产代码』该卡无 commit 字段，无法独立验证 |
| 57 | `MICA-FIX-1` | AC1 | **HUMAN** | **独立复核 P1-01 判定证据不成立**：titlebar-solid.png（2560×1440，sha256 7ce9ed83…）实为 ChatGPT 桌面应用全屏窗口，画面内无 NewManga 窗口；two- |
| 58 | `MICA-FIX-1` | AC2 | **RERUN** | **独立复核 P2-08**：AC2 唯一证据是 two-wallpapers.json 内的 diagnostics_log 字符串（material=Mica; actual=Mica），无原始启动日志或 --dia |
| 59 | `MICA-FIX-1` | AC3 | **HUMAN** | 缺 Win10/不支持环境真机核对：「不得出现黑边/透明穿透」为 NOT_RUN——卡面测试要求表 :59 记 AC3/AC4 NOT_RUN；Review :88「AC3 PARTIAL：Win10 真机不可得（NOT |
| 60 | `MICA-FIX-1` | AC4 | **ARCHIVE** | 缺可复核的回归日志：verification/MICA-FIX-1 下实测仅 3 个文件（mica/titlebar-solid.png、mica/titlebar-pattern.png、mica/two-wallpa |
| 61 | `MICA-FIX-1` | AC5 | **RERUN** | 部分满足：证据 pin 3/3 已实算 sha256 与卡面登记逐一 MATCH 且均为 64-hex（titlebar-solid.png/titlebar-pattern.png/two-wallpapers.jso |
| 62 | `P19` | AC1 | **ARCHIVE** | 缺 ② CDP 端点证明 与 ③ 四页 DOM 级断言：verification/P19/dplus-status-r3.md:6 实测 CDP 不可用（设 WEBVIEW2_ADDITIONAL_BROWSER_ARG |
| 63 | `P19` | AC3 | **ARCHIVE** | PARTIAL：请求/返回/事件/错误四处全域无泄露未闭环——verification/P19/codex-review-r4.md:21 判 AC3 FAIL（已并入的 58 命令扫描实际复现合成 Windows 路径 |
| 64 | `P19` | AC4 | **OTHER** | 部分满足且末次 E2E 未闭环：verification/P19/d-run-20261018-0056/run-metadata.txt:10-12 = checks=24 / fails=9 / exit_code= |
| 65 | `FEA-07-AC5-NATIVE-1` | AC-N1 | **HUMAN** | 原标 <<PARTIAL: 7/15 混合 DPI 组合已执行（4K 100/125/150/175/200 × 2K 100/125/150 子集），DPI 切换与屏幕内 containment 全部通过；其余组合与「 |
| 66 | `FEA-07-AC5-NATIVE-1` | AC-N2 | **OTHER** | 原标 <<PARTIAL: 主窗跨屏归属/可见/contained 已验；Inspector 浮窗不存在（RegisterSecondary 零生产调用）→ 该子项 NOT_APPLICABLE；中文 IME 组合输入已 |
| 67 | `FEA-07-AC5-NATIVE-1` | AC-N3 | **HUMAN** | 原标 <<PARTIAL: OS 级拔屏（DisplaySwitch /internal）已验且自动迁移窗口；物理拔屏已执行：拔后主窗被系统最小化（需手动恢复，D-AC5-1）、恢复后回主屏、重插后自动回 4K 原几何； |
| 68 | `FEA-07-AC5-NATIVE-1` | AC-N4 | **HUMAN** | 原标 <<PARTIAL: PerMonitorV2（app.manifest + exe 内嵌）与跨 DPI 几何保持已验；换主屏双向 rc=0 且应用存活；重启窗口几何持久化 → NOT_APPLICABLE（产品无 |
| 69 | `FEA-07-AC5-NATIVE-1` | AC-N5 | **OTHER** | 原标 <<PARTIAL: 证据/工具齐；r1 Review changes_requested 已处置，r2 复审未完成>>；卡面 L142 复判「PARTIAL」、L147 记 AC5 行保持 NOT_APPLICA |
| 70 | `P20-MEM-OPT-1` | ? | **HUMAN** | 正文阈值 ≤350 MB 未达成：实测空闲稳态 443.3 MB（卡面 :28「超 26%」）；本卡执行结果 :93-95 记「AC2 —— 经用户裁决后无需实施」，用户 2026-10-18 把 P20 的 AC3 阈 |
| 71 | `P20-MEM-OPT-1` | ? | **RERUN** | 未执行：卡面 :107-109 明记「AC3/AC4 —— 随 AC2 目标消解而不再适用；未执行」；无 P20 AC2 冷启动（≤2.0 s / Core ≤3.5 s）与 AC4（交互 ≤50 ms、60 FPS）的 |
| 72 | `P20-MEM-OPT-1` | ? | **RERUN** | 未执行：卡面 :107-109 明列未执行；缺四页可达复测、bundle 与 resources 的 core_service.exe SHA-256 相等复核、启动 smoke 窗口可达证据（verification/ |

## 按分类展开

### ARCHIVE（15 条）

- `V11R-D-1` ? L51：DS 侧已验（test:ReducedMotion_* 见原注释；焦点环 2px accent outline；DESIGN_SYSTEM §2.3 对比度断言），但『reduced-motion 生效』在旧壳不成立：旧 AppStyles.axaml 的 Transitions（Border.nm-bookcard 0.12s 等）为固定值且 app.axaml:20 仍 include 该样式
- `P02` AC1 L247：旧架构（Tauri/React/WebView2）已退出：AD-002:30 明确移除 Tauri/Rust host/WebView2，AD-002:163 S5 已将旧壳原位冻结为证据、不再参与发布，apps/desktop/LEGACY_FROZEN.md:5-6 不再构建/发布/修复；本卡以 closed_with_limitations 收口且明示不改写为 PASS（doc/tasks/
- `P02` AC2 L248：旧架构退出（AD-002:30/:163、apps/desktop/LEGACY_FROZEN.md:5-6）；本卡 closed_with_limitations、不改写为 PASS（P02.md:35），AC1–AC7 历史为 BLOCKED / NOT_RUN（P02.md:58）。缺：真实 WebView2 鼠标/键盘操作与 Console/Workbench 导航操作面——React 前
- `P02` AC3 L249：旧架构退出（AD-002:30/:163、LEGACY_FROZEN.md:5-6；P02.md:35 不改写为 PASS、:58 AC1–AC7=BLOCKED / NOT_RUN）。缺：真实 WebView2 下 300ms quiet-period 与失效窗口观测面；新时点 AC3 PASS 仅为旧壳 I1 沿用（doc/tasks/P02-NEW-TIME-X6-AC1-AC7.md:53
- `P02` AC4 L250：旧架构退出（AD-002:30/:163、LEGACY_FROZEN.md:5-6；P02.md:35、:58）。缺：目标架构下 retype/undo/restore 写后刷新观测面（REAL_WEBVIEW_MOCK_IPC 边界随旧壳冻结）；新时点 AC4 PASS 属旧壳 synthetic 场景（P02-NEW-TIME-X6-AC1-AC7.md:53），且本 AC 明写三项缺一即 B
- `P02` AC5 L251：旧架构退出（AD-002:30/:163、LEGACY_FROZEN.md:5-6；P02.md:35、:58）。缺：目标架构真实按键/焦点采集面；且新时点记录产品缺口 P-01（Escape 无法关闭确认对话框）仍未关闭（P02-NEW-TIME-X6-AC1-AC7.md:190）。
- `P02` AC6 L252：旧架构退出（AD-002:30/:163、LEGACY_FROZEN.md:5-6；P02.md:35、:58）。缺：Avalonia 目标架构下 computed foreground/background 与 token 映射采样面；旧壳实测 token_mapping 0 mapped / 10 unmapped、page-id-input 对比度无样本（P02-NEW-TIME-X6-AC
- `P02` AC7 L253：旧架构退出（AD-002:30/:163、LEGACY_FROZEN.md:5-6；P02.md:35、:58）。缺：目标架构证据面与 finding 处置闭环——产品缺口 P-01/P-02/P-03 与 BC-AC5=PARTIAL 均按原样保留（P02-NEW-TIME-X6-AC1-AC7.md:190；P02.md:35），未闭合为 done。
- `M2-REGION-RETYPE-CORE` ? L28：旧架构（Tauri/Rust host）已退出：AD-002:30 明确移除 Rust host，AD-002:163 S5 将旧壳原位冻结为证据、不再参与发布，apps/desktop/LEGACY_FROZEN.md:5-6 不再构建/发布/修复；Rust command/allowlist 三视图仅存于冻结证据（grep:set_region_type@apps/desktop/src-ta
- `M2-REGION-RETYPE-CORE` ? L31：PROTOCOL_MINOR=3 已落（grep:PROTOCOL_MINOR = 3@src/bootstrap/core_service.py:324），但 AC5 的「M2-AC5 GATE 25/25 重跑 PASS」属旧 Tauri clean-start 打包面（sidecar 构建已迁 Avalonia：apps/desktop/LEGACY_FROZEN.md:23；raw 证据见
- `M2-REGION-RETYPE-CORE` ? L32：回归含 cargo + vitest（旧 Rust/React 面，已冻结：apps/desktop/LEGACY_FROZEN.md:5-6、AD-002:30），pytest 三套件与 m2_acceptance 本轮禁跑（BRIEF §4）；历史值只见 verification/M2-REGION-RETYPE-CORE/verification.md:59（650+1sk / cargo 
- `TASK-056` ? L33：5 次逐次记录存在（file:verification/TASK-056/full-suite-run1.log … run5.log，各 900 passed），但「全仓 passed 不减少」须当轮全仓套件复算；旧 PySide6/QML 壳（QT_QPA_PLATFORM 口径）测试已归档（apps/desktop/LEGACY_FROZEN.md:25），且 pytest 本轮禁跑（BRI
- `MICA-FIX-1` AC4 L42：缺可复核的回归日志：verification/MICA-FIX-1 下实测仅 3 个文件（mica/titlebar-solid.png、mica/titlebar-pattern.png、mica/two-wallpapers.json），无 scripts/test.ps1、旧壳 vitest 60/567、pytest 3F/2739P/9S 的原始日志与退出码；这些结论目前只出现在卡面 R
- `P19` AC1 L36：缺 ② CDP 端点证明 与 ③ 四页 DOM 级断言：verification/P19/dplus-status-r3.md:6 实测 CDP 不可用（设 WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS=--remote-debugging-port=9222 后所有 msedgewebview2.exe 命令行均不含该参数、9222 无监听，被 Tauri 覆盖），
- `P19` AC3 L38：PARTIAL：请求/返回/事件/错误四处全域无泄露未闭环——verification/P19/codex-review-r4.md:21 判 AC3 FAIL（已并入的 58 命令扫描实际复现合成 Windows 路径经设置接口回显）；设置路径回显后续由 SEC-FIX-PATH-ECHO-1 修复（doc/handoffs/P19-dsh.md:16），但剩余为框架/设计层限制：Tauri 2

### HUMAN（7 条）

- `V11R-C-1` ? L31：屏幕验收面无对象：本卡为 headless 库卡（allowed_paths 仅 NewManga.ThemeEngine + tests，doc/tasks/V11R-C-1.md:20-22），SCREEN_SPECS §1–§6 无引擎章节；模块级 10 子系统实现/测试见 file:verification/V11R-C-1/README.md:34(§3 对照表)
- `MICA-FIX-1` AC1 L39：**独立复核 P1-01 判定证据不成立**：titlebar-solid.png（2560×1440，sha256 7ce9ed83…）实为 ChatGPT 桌面应用全屏窗口，画面内无 NewManga 窗口；two-wallpapers.json 的 titlebar_pixel=-1（取色失败）与硬编码 hex 不能证明 Mica。缺：真实 NewManga 窗口「纯色壁纸 vs 图案壁纸」
- `MICA-FIX-1` AC3 L41：缺 Win10/不支持环境真机核对：「不得出现黑边/透明穿透」为 NOT_RUN——卡面测试要求表 :59 记 AC3/AC4 NOT_RUN；Review :88「AC3 PARTIAL：Win10 真机不可得（NOT_RUN）」；已核实部分 = test:WindowMaterial.Choose@apps/desktop-avalonia/tests/NewManga.App.Tests/T
- `FEA-07-AC5-NATIVE-1` AC-N1 L52：原标 <<PARTIAL: 7/15 混合 DPI 组合已执行（4K 100/125/150/175/200 × 2K 100/125/150 子集），DPI 切换与屏幕内 containment 全部通过；其余组合与「无模糊/无错位」客观断言未做>>；卡面 L138 复判「AC-N1: PARTIAL」、L120 记未做组合为 NOT_RUN，故未达成本卡验收
- `FEA-07-AC5-NATIVE-1` AC-N3 L54：原标 <<PARTIAL: OS 级拔屏（DisplaySwitch /internal）已验且自动迁移窗口；物理拔屏已执行：拔后主窗被系统最小化（需手动恢复，D-AC5-1）、恢复后回主屏、重插后自动回 4K 原几何；未 flush 编辑态 fail-closed 未执行>>；卡面 L140 复判「PARTIAL」、L125 记 physical/未 flush 子项 NOT_RUN，故未达成本
- `FEA-07-AC5-NATIVE-1` AC-N4 L55：原标 <<PARTIAL: PerMonitorV2（app.manifest + exe 内嵌）与跨 DPI 几何保持已验；换主屏双向 rc=0 且应用存活；重启窗口几何持久化 → NOT_APPLICABLE（产品无实现）；恢复点按用户决定保留原生 2K>>；卡面 L141 复判「PARTIAL/NA」、L135 记恢复点未逐项还原，故未达成本卡验收
- `P20-MEM-OPT-1` ? L38：正文阈值 ≤350 MB 未达成：实测空闲稳态 443.3 MB（卡面 :28「超 26%」）；本卡执行结果 :93-95 记「AC2 —— 经用户裁决后无需实施」，用户 2026-10-18 把 P20 的 AC3 阈值改为 480 MB（AC 正文 350 MB 未被改写，故按正文判未达成）；且缺「优化前后对照的多轮采样（含 CSV 时序）」——verification/P20-MEM-OPT

### RERUN（14 条）

- `CHAPTER-MANUAL-SORT` AC10 L85：App.Tests 955/0/11/966 通过(2026-11-15)；CoreClient 与 Python 套件本轮未跑
- `GATE3-COVERAGE-MATRIX` AC4 L56：§3 的 ❌ 格已清零（doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md:160、:257），但 Host/Core 层 100 项 NOT_RUN 的归因仍是未核实的类名推断：§4.2 表头自认「未逐条核实」（同文:94）、§4.4 自认无法可靠切分 E-2 子集（:153-154）、§7 自认逐类归属未逐条核实 attribut
- `GOV-PIN-LINEAGE-1` AC3 L85：原标 <<BLOCKED: r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC>>；本卡 status:closed_with_limitations 指方案撤回后收口，非 AC 实施完成；6 项 LINE_ENDING pin 的 pinned-blob 验证与 LF 诊断复核未执行（doc/tasks/GOV-PIN-LINEAGE-1.md:287-292）
- `M2-REGION-RETYPE-CORE` ? L29：11 断言用例在树内（tests/editing/test_region_retype.py:75/102/129/158/197/237/263/421/496/522 + tests/providers/test_retype_redetect_persistence.py:184 + tests/pipeline/test_retype_candidate_persistence.py:11
- `RUN-IPC-1` AC4 L65：AC4-2 未满足：缺每条命令的成功路径测试，也缺 ControlRun 非法 action 返回 INVALID_REQUEST、StartRun 幂等键复用返回 IDEMPOTENCY_KEY_REUSED 等 host 层 typed 拒绝单测（现仅 frozen 2.3 域级 5x TARGET_NOT_FOUND + 1x INVALID_REQUEST）；AC4-3 的成功 Run 真
- `TASK-056` ? L29：实现与用例在树内（grep:def is_safe_relative_path@src/application/maintenance/cleanup.py:229 + grep:_safe_targets@src/application/maintenance/cleanup.py:193；test:test_paths_outside_safe_prefixes_are_skipped_and
- `TASK-056` ? L30：实现与用例在树内（grep:def preview@src/application/maintenance/cleanup.py:127 + grep:def to_dict@src/application/maintenance/cleanup.py:67,:107；test:test_preview_reports_targets_and_total_bytes@tests/maintenan
- `TASK-056` ? L31：实现与用例在树内（grep:class WebtoonTileCacheSweeper@src/infrastructure/imaging/tile_cache_sweep.py:22；test:test_lists_every_generation_relative_to_managed_root@tests/maintenance/test_cleanup.py:90 + test_miss
- `TASK-056` ? L32：实现与用例在树内（grep:def retry_pending_cleanups@src/application/maintenance/cleanup.py:160 + grep:def pending_cleanup_count@src/application/maintenance/cleanup.py:188 + test:test_run_is_idempotent@tests/main
- `TASK-056` ? L34：Handoff/verification/Review/集成俱在（file:doc/handoffs/TASK-056-delivery.md + file:verification/TASK-056/ + file:doc/reviews/TASK-056-15f977a.md + 集成 commit 11517ac 可解析），但缺 STATUS 台账行：doc/STATUS.md 与 doc/
- `MICA-FIX-1` AC2 L40：**独立复核 P2-08**：AC2 唯一证据是 two-wallpapers.json 内的 diagnostics_log 字符串（material=Mica; actual=Mica），无原始启动日志或 --diagnostics 输出文件；卡面 L58 记 AC2 NOT_RUN；且同轮采集（AC1）已证明截图不可信。实现存在仍成立：grep:ActualTransparencyLevel
- `MICA-FIX-1` AC5 L43：部分满足：证据 pin 3/3 已实算 sha256 与卡面登记逐一 MATCH 且均为 64-hex（titlebar-solid.png/titlebar-pattern.png/two-wallpapers.json），Handoff doc/handoffs/MICA-FIX-1-handoff.md 存在（:8 集成 93aaaeb8c）；但 check.ps1 -TaskPath 无入
- `P20-MEM-OPT-1` ? L39：未执行：卡面 :107-109 明记「AC3/AC4 —— 随 AC2 目标消解而不再适用；未执行」；无 P20 AC2 冷启动（≤2.0 s / Core ≤3.5 s）与 AC4（交互 ≤50 ms、60 FPS）的同方法复测对照数据入库
- `P20-MEM-OPT-1` ? L40：未执行：卡面 :107-109 明列未执行；缺四页可达复测、bundle 与 resources 的 core_service.exe SHA-256 相等复核、启动 smoke 窗口可达证据（verification/P20-MEM-OPT-1 仅 5 个 pin：process-tree.json、probe-trace.log、probe-process-tree.ps1、experimen

### DOC（2 条）

- `V11R-C-1` ? L37：构建/测试日志与偏差/未验证清单齐全（build.log、dotnet-test-full.log、DEVIATIONS.md、README.md:73 §5）；缺「截图」：verification/V11R-C-1 目录内 0 个 .png
- `RELEASE-PACKAGE-1` AC6 L45：缺 Handoff：doc/handoffs 无 RELEASE-PACKAGE-1-*.md（分支 task/RELEASE-PACKAGE-1 与 worktree 亦无）；check.ps1 -TaskPath、scripts/test.ps1、pytest 均无归档日志（证据目录只有 9 条产物证据；64-hex pin 9/9 已复算一致）：file:verification/RELEA

### IMPL（2 条）

- `V11R-B-4` ? L33：partial 状态有赋值路径但无验证：StudioBatchRunState.Partial 出现在 enum(StudioBatchViewModel.cs:44)/HasData(:440)/文案(:448)，**且 L673 有赋值** `State = Projection is null ? Error : Partial`；但全 VM 无测试断言该状态出现、无就地呈现校验（独立复核 
- `V11R-A-3` ? L36：AC4 要求补强 CommandParityContractTests：本卡交付明确未改该文件（verification/V11R-A-3/README.md:95-96 自述『git diff 无这些文件；66→76 改造归 V11R-F0-1』，CommandContractV11RTests.cs:12-14 同述），改由新增 CommandContractV11RTests 承载；该新类只

### OTHER（32 条）

- `V11R-C-2` ? L39：GAP-3「跟随系统强调色」仅作用域生效、不写设置文件、不跨重启保持（verification/V11R-C-2/DEVIATIONS.md GAP-3；AppearanceSectionView.axaml:59 注明 V1 未接入 OS 取色）；其余子项有 test:AppearanceSettings_ApplyImmediately_AndPersist@apps/desktop-aval
- `FEA-04` AC1 L90：原标 <<PARTIAL: 范围冻结；实现未开始>>；status:done 指范围冻结完成，非实现完成
- `FEA-04` AC2 L91：原标 <<PARTIAL: 范围冻结；实现未开始>>；status:done 指范围冻结完成，非实现完成
- `FEA-04` AC3 L92：原标 <<PARTIAL: 范围冻结；实现未开始>>；status:done 指范围冻结完成，非实现完成
- `FEA-04` AC4 L93：原标 <<PARTIAL: 范围冻结；实现未开始>>；status:done 指范围冻结完成，非实现完成
- `FEA-04` AC5 L94：原标 <<PARTIAL: 范围冻结；实现未开始>>；status:done 指范围冻结完成，非实现完成
- `FEA-04` AC6 L95：原标 <<PARTIAL: 范围冻结；实现未开始>>；status:done 指范围冻结完成，非实现完成
- `FEA-04` AC7 L96：原标 <<PARTIAL: 范围冻结；实现未开始>>；status:done 指范围冻结完成，非实现完成
- `FEA-04` AC8 L97：原标 <<PARTIAL: 范围冻结；实现未开始>>；status:done 指范围冻结完成，非实现完成
- `V11R-C-1` ? L34：build.log:22(0 个警告/EXIT=0) 通过；但引擎无 .axaml，AC4 的 DynamicResource/令牌子项无对象，且 BuiltInThemeGenerator.cs:93 有裸色常量 #1F1F1F；无 conformance 扫描记录
- `V11R-C-1` ? L36：单测与 dotnet test 绿已核实（dotnet-test-themeengine.log:219=203 通过 0 失败；dotnet-test-full.log:16 App 232 通过 0 失败）；缺「关键屏截图证据」：verification/V11R-C-1 下 0 个 .png
- `V11R-B-5` ? L31：SCREEN_SPECS 无导出预检/术语章节（grep '预检|术语'@doc/plan/V11R_SCREEN_SPECS.md 0 命中；FUSION_SPEC.md:98-99 仅跨切面矩阵行），「按对应章节的布局/组件/状态」无法核对；数据源与非 Mock 诚实有 file:verification/V11R-B-5/preflight.json + file:verification/
- `V11R-B-5` ? L32：无空间/模式切换上下文保留证据：V2StudioExportTermsTests 7 例无 VM 复用/选择/滚动断言（ToolsOverlay 仅开关@apps/desktop-avalonia/tests/NewManga.App.Tests/V2StudioExportTermsTests.cs:342）；evidence_dir 无 context/scroll JSON
- `V11R-B-5` ? L33：六态证据缺失：仅有 preflight/readonly/history/terms 各自功能证据（V2StudioExportTermsTests.cs:45/:222/:249/:286），无 idle/loading/empty/error/partial 的枚举、触发或就地呈现记录
- `V11R-B-5` ? L34：本卡无 conformance/design-system-usage 记录；共享 StudioTheme.axaml 裸间距未清零（:267/:288/:328/:387，verification/V11R-B-3/DEVIATIONS.md:14）；build.log:18 0 warning 已通过
- `V11R-B-4` ? L34：「无裸间距」未清零：StudioTheme.axaml:267(Padding=10,4)/:288(Width=8)/:328(Width=480)/:387(Padding=6,0)（登记 verification/V11R-B-3/DEVIATIONS.md:14）；build.log:15 0 warning 与 V2Xaml_UsesNoRawDesignValues_AndNoForb
- `V11R-B-3` ? L34：「无裸间距」未清零：StudioTheme.axaml:267(Padding=10,4)/:288(Width=8)/:328(Width=480)/:387(Padding=6,0) 为无 Nm.* 令牌的裸值，登记于 verification/V11R-B-3/DEVIATIONS.md:14 与 V2StudioConformanceTests.spacingAllowlist；build
- `GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1` ? L51：缺第 7 类「保护集合回退」负例测试：6 类有测试（test:test_wrong_digest_fails_closed@tools/governance/tests/test_residual_runtime_identity.py:182、tampered_policy_body:220、origin_drift:187、present_absent_target:194、missing_p
- `GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1` ? L52：命令与 EXIT 已记录（file:verification/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1/verification-log.txt:17-19 Ran 12 tests/EXIT 0、:80-81 check.ps1 PASS 2 warnings/EXIT 0、:84 git diff --check EXIT 0）+ 独立 Review appro
- `GATE3-COVERAGE-MATRIX` AC2 L52：缺 4 格 `测试名 (文件:行)`+断言说明：Region 编辑/阅读偏好/主题外观/整书进度仍只有类名或方法名（doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md:66-70）；矩阵 §7 自认仅 12 格逐行核对断言、其余为类摘要+方法名（同文:190）；r3 复核 R3-008 判「AC2 仍未满足」（doc/reviews/
- `GATE3-COVERAGE-MATRIX` AC3 L54：缺 `[Fact]`（纯逻辑）分类：§2 只给出 `[AvaloniaFact]` 62 文件（doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md:35）与 4 类 sidecar gate 7 个（同文:36），全库无 [Fact] 计数/分类（grep:纯逻辑 0 命中），且未逐格标 gate 属性；r1 复核 AC3 判 PAR
- `GOV-PIN-LINEAGE-1` AC1 L77：原标 <<BLOCKED: r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC>>；本卡 status:closed_with_limitations 指 r27 撤回原方案、r28 停止改造后收口，非 AC 实施完成（doc/tasks/GOV-PIN-LINEAGE-1.md:208-209）；63 个 TIME_BASED + 6 个 LINE_ENDING 的逐条 pin
- `GOV-PIN-LINEAGE-1` AC2 L81：原标 <<BLOCKED: r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC>>；本卡 status:closed_with_limitations 指方案撤回后收口，非 AC 实施完成；tools/governance/check.ps1 未修改（doc/tasks/GOV-PIN-LINEAGE-1.md:287-292「明确未做」），历史 blob 校验语义与工作区漂移诊
- `GOV-PIN-LINEAGE-1` AC4 L88：原标 <<BLOCKED: r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC>>；本卡 status:closed_with_limitations 指方案撤回后收口，非 AC 实施完成；23 项 MISSING_FILE 的 commit/路径/blob 状态与 hash 对照及来源链核对未按 AC 交付（doc/tasks/GOV-PIN-LINEAGE-1.md:287-
- `GOV-PIN-LINEAGE-1` AC5 L92：原标 <<BLOCKED: r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC>>；本卡 status:closed_with_limitations 指方案撤回后收口，非 AC 实施完成；六类回归夹具未建立，checker 既有夹具与 v3 AC gate、Resource Manifest 门禁未被专门回归（doc/tasks/GOV-PIN-LINEAGE-1.md:287
- `GOV-PIN-LINEAGE-1` AC6 L96：原标 <<BLOCKED: r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC>>；本卡 status:closed_with_limitations 指方案撤回后收口，非 AC 实施完成；lineage registry、最小 checker diff、测试证据、Handoff 与独立 Review 均未交付（doc/reviews 无 GOV-PIN-LINEAGE-1 审查
- `V11R-C-3` ? L41：tag 已存在（git tag -l v11r-pre-retire → annotated，指向 df883f2ce；verification/V11R-C-3/R1-tag.txt:7），但两项未满足：①未用 rollback-theme-retire.ps1 -CreateTag，改用直接 git tag（R1-tag.txt:10-13 自述脚本会继续 checkout）；②缺『tag 存
- `M2-SFX-CORRECTION-EXPORTER` ? L35：T1b（批量数据生产）产物尚不存在，「与 T1b 产物同构、训练侧零适配」无法验证（Lead 裁决：w7 报告 §需裁决 5）；已核实的只是 T1a 格式面：test:test_manifest_files_are_t1a_format@experiments/M2-SFX-CORRECTION-EXPORTER/tests/test_export.py:42 + test:test_yolo_s
- `V11R-C-RESEARCH-1` ? L40：文档声明『V1 不引入任何第三方 UI/主题框架依赖』(RESEARCH_V1.md:8)；但『不修改生产代码』该卡无 commit 字段，无法独立验证
- `P19` AC4 L39：部分满足且末次 E2E 未闭环：verification/P19/d-run-20261018-0056/run-metadata.txt:10-12 = checks=24 / fails=9 / exit_code=1；trace.log:46-63 显示 9 个分区 en=False + invoke=failed（禁用态原始数据在），但 ASSERT FAIL disabled-not-i
- `FEA-07-AC5-NATIVE-1` AC-N2 L53：原标 <<PARTIAL: 主窗跨屏归属/可见/contained 已验；Inspector 浮窗不存在（RegisterSecondary 零生产调用）→ 该子项 NOT_APPLICABLE；中文 IME 组合输入已验（命令面板输入「你好」）；快捷键「不重复执行」未单独断言>>；卡面 L139 复判「PARTIAL/NA」、L145 记 Inspector 浮窗不存在，故未达成本卡验收
- `FEA-07-AC5-NATIVE-1` AC-N5 L56：原标 <<PARTIAL: 证据/工具齐；r1 Review changes_requested 已处置，r2 复审未完成>>；卡面 L142 复判「PARTIAL」、L147 记 AC5 行保持 NOT_APPLICABLE，独立 Review 未闭环，故未达成本卡验收
