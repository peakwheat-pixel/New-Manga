# 72 条 blocked 的可闭性分类（r1 复核后重做，逐条人工判定）

生成于 HEAD `73da5ab40`；**总数 72**（与 `verify_final.py` 的 `blocked=72` 一致）。

分类口径（r1 复核要求）：**`ARCHIVE` 只允许「AC 对象在当前架构不存在」**；当前架构的 live gap 必须落到可操作类（`IMPL`/`RERUN`/`DOC`）。

| 分类 | 条数 | 能否由 Agent 闭合 |
|---|---:|---|
| `ARCHIVE` | 15 | 否（对象已退役，历史存档） |
| `WITHDRAWN` | 6 | 否（方案撤回/已裁决） |
| `HUMAN` | 5 | 否（需人眼/物理设备） |
| `RERUN` | 10 | **是**（当前架构复跑/复算） |
| `DOC` | 9 | **是**（补文档/证据/登记） |
| `IMPL` | 22 | **是**（写代码/测试；工作量见各条） |
| `MECHANISM_NA` | 5 | 否（要求本身不适用，建议改判 NA） |

**可由 Agent 闭合合计：RERUN + DOC + IMPL = 41 条。**

## 逐条明细（含判定依据）

| # | 卡 | 行 | AC | 分类 | 判定依据 |
|---|---|---:|---|---|---|
| 1 | `V11R-C-2` | 39 | AC6 | **MECHANISM_NA** | GAP-3 跟随系统强调色在 V1 未接入（DEVIATIONS 已登记为已知限制） |
| 2 | `CHAPTER-MANUAL-SORT` | 85 | AC10 | **RERUN** | CoreClient 与 Python 套件本轮未跑，可在当前架构复跑 |
| 3 | `V11R-D-1` | 51 | AC8 | **IMPL** | **当前树 live gap**：app.axaml:20 仍 include 旧 AppStyles.axaml（固定 Transitions），需退役旧样式或改 Transitions，非旧架构存档 |
| 4 | `FEA-04` | 90 | AC1 | **IMPL** | 范围冻结完成、实现未开始（8 条同源），实现需另立卡 |
| 5 | `FEA-04` | 91 | AC2 | **IMPL** | 同上 |
| 6 | `FEA-04` | 92 | AC3 | **IMPL** | 同上 |
| 7 | `FEA-04` | 93 | AC4 | **IMPL** | 同上 |
| 8 | `FEA-04` | 94 | AC5 | **IMPL** | 同上 |
| 9 | `FEA-04` | 95 | AC6 | **IMPL** | 同上 |
| 10 | `FEA-04` | 96 | AC7 | **IMPL** | 同上 |
| 11 | `FEA-04` | 97 | AC8 | **IMPL** | 同上 |
| 12 | `V11R-C-1` | 31 | AC1 | **MECHANISM_NA** | headless 库卡，SCREEN_SPECS 无引擎章节；屏幕验收面无对象（同卡 AC2/3/5 已判 NA） |
| 13 | `V11R-C-1` | 34 | AC4 | **IMPL** | BuiltInThemeGenerator.cs:93 裸色常量待清（另有「子项无对象」部分→NA） |
| 14 | `V11R-C-1` | 36 | AC6 | **MECHANISM_NA** | 同上：headless 库卡无「关键屏」，截图要求无对象 |
| 15 | `V11R-C-1` | 37 | AC7 | **MECHANISM_NA** | 同上 |
| 16 | `V11R-B-5` | 31 | AC1 | **DOC** | SCREEN_SPECS 缺导出预检/术语章节，属文档缺口 |
| 17 | `V11R-B-5` | 32 | AC2 | **IMPL** | 缺上下文保留断言，需补测试 |
| 18 | `V11R-B-5` | 33 | AC3 | **IMPL** | 缺六态枚举/触发/呈现，需补实现与测试 |
| 19 | `V11R-B-5` | 34 | AC4 | **IMPL** | StudioTheme.axaml 裸间距未清零（:267/:288/:328/:387） |
| 20 | `V11R-B-4` | 33 | AC3 | **IMPL** | Partial 状态无断言（赋值点 :673 存在），需补测试 |
| 21 | `V11R-B-4` | 34 | AC4 | **IMPL** | 裸间距未清零 |
| 22 | `V11R-B-3` | 34 | AC4 | **IMPL** | 裸间距未清零 |
| 23 | `P02` | 247 | AC1 | **ARCHIVE** | Tauri/React/WebView2 已由 AD-002:30/:163 退役，旧壳冻结为证据 |
| 24 | `P02` | 248 | AC2 | **ARCHIVE** | 同上（WebView2 操作面已冻结） |
| 25 | `P02` | 249 | AC3 | **ARCHIVE** | 同上（WebView2 quiet-period 观测面不存在） |
| 26 | `P02` | 250 | AC4 | **ARCHIVE** | 同上（REAL_WEBVIEW_MOCK_IPC 随旧壳冻结） |
| 27 | `P02` | 251 | AC5 | **ARCHIVE** | 同上（真实按键/焦点采集面在旧壳） |
| 28 | `P02` | 252 | AC6 | **ARCHIVE** | 同上（旧壳 computed token 采样面） |
| 29 | `P02` | 253 | AC7 | **ARCHIVE** | 同上（旧壳证据面与 finding 闭环） |
| 30 | `GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1` | 51 | AC6 | **IMPL** | 缺第 7 类「保护集合回退」负例测试 |
| 31 | `GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1` | 52 | AC7 | **DOC** | 卡面指向的 integration/ 目录不存在，需补集成复验证据 |
| 32 | `GATE3-COVERAGE-MATRIX` | 52 | AC2 | **DOC** | 缺 4 格「测试名 (文件:行)」+ 断言说明，属矩阵文档补齐 |
| 33 | `GATE3-COVERAGE-MATRIX` | 54 | AC3 | **DOC** | 缺 [Fact] 分类统计，属矩阵文档补齐 |
| 34 | `GATE3-COVERAGE-MATRIX` | 56 | AC4 | **DOC** | NOT_RUN 归因未逐条核实，属矩阵文档补齐 |
| 35 | `GOV-PIN-LINEAGE-1` | 77 | AC1 | **WITHDRAWN** | r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC（卡 :208-209） |
| 36 | `GOV-PIN-LINEAGE-1` | 81 | AC2 | **WITHDRAWN** | 同上（check.ps1 未修改，卡 :287-292） |
| 37 | `GOV-PIN-LINEAGE-1` | 85 | AC3 | **WITHDRAWN** | 同上（r1 复核指出 AC3 与其余 5 条同根因，不应拆到 RERUN） |
| 38 | `GOV-PIN-LINEAGE-1` | 88 | AC4 | **WITHDRAWN** | 同上 |
| 39 | `GOV-PIN-LINEAGE-1` | 92 | AC5 | **WITHDRAWN** | 同上 |
| 40 | `GOV-PIN-LINEAGE-1` | 96 | AC6 | **WITHDRAWN** | 同上 |
| 41 | `V11R-A-3` | 36 | AC4 | **IMPL** | 契约测试未补断言（口径待 Lead 裁决后落实现） |
| 42 | `V11R-C-3` | 41 | ? | **IMPL** | 缺 tag 存在后的 -DryRun 证据，可补跑 |
| 43 | `M2-REGION-RETYPE-CORE` | 28 | AC2 | **ARCHIVE** | Rust command/allowlist 三视图仅存于冻结的 apps/desktop（LEGACY_FROZEN:5-6） |
| 44 | `M2-REGION-RETYPE-CORE` | 29 | AC3 | **RERUN** | 11 断言用例在树内（tests/editing/*），缺本轮复跑 |
| 45 | `M2-REGION-RETYPE-CORE` | 31 | AC5 | **ARCHIVE** | M2-AC5 GATE 25/25 属旧 Tauri clean-start 打包面（LEGACY_FROZEN:23） |
| 46 | `M2-REGION-RETYPE-CORE` | 32 | AC6 | **RERUN** | pytest 三套件本轮禁跑；cargo/vitest 部分属旧壳（另计 ARCHIVE） |
| 47 | `RUN-IPC-1` | 65 | AC4 | **IMPL** | 缺 typed 拒绝单测（r1 复核指出理由主体是缺测试） |
| 48 | `RELEASE-PACKAGE-1` | 45 | AC6 | **DOC** | 缺 Handoff 文件，可补写 |
| 49 | `M2-SFX-CORRECTION-EXPORTER` | 35 | AC4 | **IMPL** | T1b 批量产物尚不存在，需先生产 |
| 50 | `TASK-056` | 29 | ① | **RERUN** | 实现与用例在树内；缺产品面接线 + 本轮复跑 |
| 51 | `TASK-056` | 30 | ② | **RERUN** | 同上 |
| 52 | `TASK-056` | 31 | ③ | **RERUN** | 同上 |
| 53 | `TASK-056` | 32 | ④ | **RERUN** | 同上 |
| 54 | `TASK-056` | 33 | ⑤ | **RERUN** | 缺当前可复算的全仓基线与 5 次复跑 |
| 55 | `TASK-056` | 34 | ⑥ | **MECHANISM_NA** | 「STATUS 台账行」为历史模板要求：STATUS 预算 3200 bytes 只列当前 Task，TASK_LEDGER 按状态汇总；r1 复核补充：历史 commit 曾满足，现要求已不可满足 → 建议 not-applicable（需裁决） |
| 56 | `V11R-C-RESEARCH-1` | 40 | AC5 | **DOC** | 卡有 delivery_head: ba59a6c0d，git show --stat 可证 0 生产文件 → 补核验记录即可（r1 复核指出原判「无法验证」错误） |
| 57 | `MICA-FIX-1` | 39 | AC1 | **HUMAN** | 需真实 NewManga 窗口的纯色/图案壁纸 A/B 截图 + 窗口句柄/进程证明（现证据实为 ChatGPT 窗口，复核 P1-01 已判不成立） |
| 58 | `MICA-FIX-1` | 40 | AC2 | **RERUN** | 需重跑 --diagnostics 留下原始日志（现仅 JSON 内字符串） |
| 59 | `MICA-FIX-1` | 41 | AC3 | **HUMAN** | 需 Win10/不支持环境的真机黑边核对（AC3 NOT_RUN） |
| 60 | `MICA-FIX-1` | 42 | AC4 | **RERUN** | 缺 scripts/test.ps1 回归日志与退出码，可重跑归档 |
| 61 | `MICA-FIX-1` | 43 | AC5 | **DOC** | pin 3/3 已 MATCH；缺 check -TaskPath 入库记录与 Record Decision 段，可补 |
| 62 | `P19` | 36 | AC1 | **ARCHIVE** | CDP/WebView2 DOM 断言面随旧壳退役；用户已裁决接受 UIA 替代 |
| 63 | `P19` | 38 | AC3 | **ARCHIVE** | Tauri 2.12 不校验顶层未知键属旧壳框架限制 |
| 64 | `P19` | 39 | AC4 | **ARCHIVE** | 旧壳 E2E（msedgewebview2 分区断言）已冻结 |
| 65 | `FEA-07-AC5-NATIVE-1` | 52 | AC-N1 | **HUMAN** | 剩余 8 组混合 DPI 组合 + 「无模糊/无错位」主观视觉断言，需真实多屏 |
| 66 | `FEA-07-AC5-NATIVE-1` | 53 | AC-N2 | **IMPL** | Inspector 浮窗子项 NA；「快捷键不重复执行」需补断言 |
| 67 | `FEA-07-AC5-NATIVE-1` | 54 | AC-N3 | **HUMAN** | 物理拔屏 + 未 flush 编辑态 fail-closed，需真实设备拔插 |
| 68 | `FEA-07-AC5-NATIVE-1` | 55 | AC-N4 | **HUMAN** | 恢复点逐项还原校验（卡面 :135 记未逐项还原），需真机操作 |
| 69 | `FEA-07-AC5-NATIVE-1` | 56 | AC-N5 | **DOC** | r2 复审未闭环，需补独立 Review |
| 70 | `P20-MEM-OPT-1` | 38 | AC2 | **ARCHIVE** | 旧 Tauri/WebView2 卡（allowed_paths 含 Tauri 侧、证据为 m2rc1-desktop/msedgewebview2）；AD-002 已退役该壳 |
| 71 | `P20-MEM-OPT-1` | 39 | AC3 | **ARCHIVE** | 同上；卡面 :107-109 明记 AC3/AC4 随 AC2 目标消解不再适用 |
| 72 | `P20-MEM-OPT-1` | 40 | AC4 | **ARCHIVE** | 同上 |

## 原 blocked 理由（完整，供核对）

### 1. `V11R-C-2` L39 AC6 → **MECHANISM_NA**

> GAP-3「跟随系统强调色」仅作用域生效、不写设置文件、不跨重启保持（verification/V11R-C-2/DEVIATIONS.md GAP-3；AppearanceSectionView.axaml:59 注明 V1 未接入 OS 取色）；其余子项有 test:AppearanceSettings_ApplyImmediately_AndPersist@apps/desktop-avalonia/tests/NewManga.App.Tests/V2ThemeStudioTests.cs:776

### 2. `CHAPTER-MANUAL-SORT` L85 AC10 → **RERUN**

> App.Tests 955/0/11/966 通过(2026-11-15)；CoreClient 与 Python 套件本轮未跑

### 3. `V11R-D-1` L51 AC8 → **IMPL**

> DS 侧已验（test:ReducedMotion_* 见原注释；焦点环 2px accent outline；DESIGN_SYSTEM §2.3 对比度断言），但『reduced-motion 生效』在旧壳不成立：旧 AppStyles.axaml 的 Transitions（Border.nm-bookcard 0.12s 等）为固定值且 app.axaml:20 仍 include 该样式（verification/V11R-D-1/DEVIATIONS.md D-12）→ 全应用 reduced-motion 未达

### 4. `FEA-04` L90 AC1 → **IMPL**

> 原标 <<PARTIAL: 范围冻结；实现未开始>>；status:done 指范围冻结完成，非实现完成

### 5. `FEA-04` L91 AC2 → **IMPL**

> 原标 <<PARTIAL: 范围冻结；实现未开始>>；status:done 指范围冻结完成，非实现完成

### 6. `FEA-04` L92 AC3 → **IMPL**

> 原标 <<PARTIAL: 范围冻结；实现未开始>>；status:done 指范围冻结完成，非实现完成

### 7. `FEA-04` L93 AC4 → **IMPL**

> 原标 <<PARTIAL: 范围冻结；实现未开始>>；status:done 指范围冻结完成，非实现完成

### 8. `FEA-04` L94 AC5 → **IMPL**

> 原标 <<PARTIAL: 范围冻结；实现未开始>>；status:done 指范围冻结完成，非实现完成

### 9. `FEA-04` L95 AC6 → **IMPL**

> 原标 <<PARTIAL: 范围冻结；实现未开始>>；status:done 指范围冻结完成，非实现完成

### 10. `FEA-04` L96 AC7 → **IMPL**

> 原标 <<PARTIAL: 范围冻结；实现未开始>>；status:done 指范围冻结完成，非实现完成

### 11. `FEA-04` L97 AC8 → **IMPL**

> 原标 <<PARTIAL: 范围冻结；实现未开始>>；status:done 指范围冻结完成，非实现完成

### 12. `V11R-C-1` L31 AC1 → **MECHANISM_NA**

> 屏幕验收面无对象：本卡为 headless 库卡（allowed_paths 仅 NewManga.ThemeEngine + tests，doc/tasks/V11R-C-1.md:20-22），SCREEN_SPECS §1–§6 无引擎章节；模块级 10 子系统实现/测试见 file:verification/V11R-C-1/README.md:34(§3 对照表)

### 13. `V11R-C-1` L34 AC4 → **IMPL**

> build.log:22(0 个警告/EXIT=0) 通过；但引擎无 .axaml，AC4 的 DynamicResource/令牌子项无对象，且 BuiltInThemeGenerator.cs:93 有裸色常量 #1F1F1F；无 conformance 扫描记录

### 14. `V11R-C-1` L36 AC6 → **MECHANISM_NA**

> 单测与 dotnet test 绿已核实（dotnet-test-themeengine.log:219=203 通过 0 失败；dotnet-test-full.log:16 App 232 通过 0 失败）；缺「关键屏截图证据」：verification/V11R-C-1 下 0 个 .png

### 15. `V11R-C-1` L37 AC7 → **MECHANISM_NA**

> 构建/测试日志与偏差/未验证清单齐全（build.log、dotnet-test-full.log、DEVIATIONS.md、README.md:73 §5）；缺「截图」：verification/V11R-C-1 目录内 0 个 .png

### 16. `V11R-B-5` L31 AC1 → **DOC**

> SCREEN_SPECS 无导出预检/术语章节（grep '预检|术语'@doc/plan/V11R_SCREEN_SPECS.md 0 命中；FUSION_SPEC.md:98-99 仅跨切面矩阵行），「按对应章节的布局/组件/状态」无法核对；数据源与非 Mock 诚实有 file:verification/V11R-B-5/preflight.json + file:verification/V11R-B-5/terms.json

### 17. `V11R-B-5` L32 AC2 → **IMPL**

> 无空间/模式切换上下文保留证据：V2StudioExportTermsTests 7 例无 VM 复用/选择/滚动断言（ToolsOverlay 仅开关@apps/desktop-avalonia/tests/NewManga.App.Tests/V2StudioExportTermsTests.cs:342）；evidence_dir 无 context/scroll JSON

### 18. `V11R-B-5` L33 AC3 → **IMPL**

> 六态证据缺失：仅有 preflight/readonly/history/terms 各自功能证据（V2StudioExportTermsTests.cs:45/:222/:249/:286），无 idle/loading/empty/error/partial 的枚举、触发或就地呈现记录

### 19. `V11R-B-5` L34 AC4 → **IMPL**

> 本卡无 conformance/design-system-usage 记录；共享 StudioTheme.axaml 裸间距未清零（:267/:288/:328/:387，verification/V11R-B-3/DEVIATIONS.md:14）；build.log:18 0 warning 已通过

### 20. `V11R-B-4` L33 AC3 → **IMPL**

> partial 状态有赋值路径但无验证：StudioBatchRunState.Partial 出现在 enum(StudioBatchViewModel.cs:44)/HasData(:440)/文案(:448)，**且 L673 有赋值** `State = Projection is null ? Error : Partial`；但全 VM 无测试断言该状态出现、无就地呈现校验（独立复核 P2-06 纠正：原注释称「无赋值点」有误）。loading 仅赋值点 :1166 无断言。已测 NoRun@V2StudioBatchTests.cs:429、Error@:619、Ready@:442

### 21. `V11R-B-4` L34 AC4 → **IMPL**

> 「无裸间距」未清零：StudioTheme.axaml:267(Padding=10,4)/:288(Width=8)/:328(Width=480)/:387(Padding=6,0)（登记 verification/V11R-B-3/DEVIATIONS.md:14）；build.log:15 0 warning 与 V2Xaml_UsesNoRawDesignValues_AndNoForbiddenEffects 已通过

### 22. `V11R-B-3` L34 AC4 → **IMPL**

> 「无裸间距」未清零：StudioTheme.axaml:267(Padding=10,4)/:288(Width=8)/:328(Width=480)/:387(Padding=6,0) 为无 Nm.* 令牌的裸值，登记于 verification/V11R-B-3/DEVIATIONS.md:14 与 V2StudioConformanceTests.spacingAllowlist；build.log:15 0 warning 与 V2Xaml_UsesNoRawDesignValues_AndNoForbiddenEffects 已通过

### 23. `P02` L247 AC1 → **ARCHIVE**

> 旧架构（Tauri/React/WebView2）已退出：AD-002:30 明确移除 Tauri/Rust host/WebView2，AD-002:163 S5 已将旧壳原位冻结为证据、不再参与发布，apps/desktop/LEGACY_FROZEN.md:5-6 不再构建/发布/修复；本卡以 closed_with_limitations 收口且明示不改写为 PASS（doc/tasks/P02.md:35），历史各时点 AC1–AC7=BLOCKED / NOT_RUN（P02.md:58）。缺：目标架构下可执行的 Tauri/WebView2 启动与 harness 验收面。

### 24. `P02` L248 AC2 → **ARCHIVE**

> 旧架构退出（AD-002:30/:163、apps/desktop/LEGACY_FROZEN.md:5-6）；本卡 closed_with_limitations、不改写为 PASS（P02.md:35），AC1–AC7 历史为 BLOCKED / NOT_RUN（P02.md:58）。缺：真实 WebView2 鼠标/键盘操作与 Console/Workbench 导航操作面——React 前端已冻结，AD-002 无对应验收面。

### 25. `P02` L249 AC3 → **ARCHIVE**

> 旧架构退出（AD-002:30/:163、LEGACY_FROZEN.md:5-6；P02.md:35 不改写为 PASS、:58 AC1–AC7=BLOCKED / NOT_RUN）。缺：真实 WebView2 下 300ms quiet-period 与失效窗口观测面；新时点 AC3 PASS 仅为旧壳 I1 沿用（doc/tasks/P02-NEW-TIME-X6-AC1-AC7.md:53），非目标架构验收。

### 26. `P02` L250 AC4 → **ARCHIVE**

> 旧架构退出（AD-002:30/:163、LEGACY_FROZEN.md:5-6；P02.md:35、:58）。缺：目标架构下 retype/undo/restore 写后刷新观测面（REAL_WEBVIEW_MOCK_IPC 边界随旧壳冻结）；新时点 AC4 PASS 属旧壳 synthetic 场景（P02-NEW-TIME-X6-AC1-AC7.md:53），且本 AC 明写三项缺一即 BLOCKED。

### 27. `P02` L251 AC5 → **ARCHIVE**

> 旧架构退出（AD-002:30/:163、LEGACY_FROZEN.md:5-6；P02.md:35、:58）。缺：目标架构真实按键/焦点采集面；且新时点记录产品缺口 P-01（Escape 无法关闭确认对话框）仍未关闭（P02-NEW-TIME-X6-AC1-AC7.md:190）。

### 28. `P02` L252 AC6 → **ARCHIVE**

> 旧架构退出（AD-002:30/:163、LEGACY_FROZEN.md:5-6；P02.md:35、:58）。缺：Avalonia 目标架构下 computed foreground/background 与 token 映射采样面；旧壳实测 token_mapping 0 mapped / 10 unmapped、page-id-input 对比度无样本（P02-NEW-TIME-X6-AC1-AC7.md:53），P-02 token 缺口未关闭（同卡:190）。

### 29. `P02` L253 AC7 → **ARCHIVE**

> 旧架构退出（AD-002:30/:163、LEGACY_FROZEN.md:5-6；P02.md:35、:58）。缺：目标架构证据面与 finding 处置闭环——产品缺口 P-01/P-02/P-03 与 BC-AC5=PARTIAL 均按原样保留（P02-NEW-TIME-X6-AC1-AC7.md:190；P02.md:35），未闭合为 done。

### 30. `GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1` L51 AC6 → **IMPL**

> 缺第 7 类「保护集合回退」负例测试：6 类有测试（test:test_wrong_digest_fails_closed@tools/governance/tests/test_residual_runtime_identity.py:182、tampered_policy_body:220、origin_drift:187、present_absent_target:194、missing_preserve_target:200、unbound_error:206），但代码 PROTECTION_REGRESSION 守卫（tools/governance/clean_workspace.py:2191-2195）只被 test:test_protection_set_did_not_shrink@tools/governance/tests/test_residual_runtime_identity.py:149 以「生产集合未缩小」正面断言，未构造回退触发 fail-closed 的用例；审查报告 §3.3 也只列 6 类负例

### 31. `GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1` L52 AC7 → **DOC**

> 命令与 EXIT 已记录（file:verification/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1/verification-log.txt:17-19 Ran 12 tests/EXIT 0、:80-81 check.ps1 PASS 2 warnings/EXIT 0、:84 git diff --check EXIT 0）+ 独立 Review approved（file:doc/reviews/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1-3264e0b61-antigravity-r1.md:7-8），但缺「集成复验」独立证据：卡面 :124 指向的 verification/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1/integration/ 不存在（git ls-files 该目录 0 文件、Test-Path False），1945 保护根/0 errors/EXIT 0 仅见卡面 Closeout 与审查报告 §3.2

### 32. `GATE3-COVERAGE-MATRIX` L52 AC2 → **DOC**

> 缺 4 格 `测试名 (文件:行)`+断言说明：Region 编辑/阅读偏好/主题外观/整书进度仍只有类名或方法名（doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md:66-70）；矩阵 §7 自认仅 12 格逐行核对断言、其余为类摘要+方法名（同文:190）；r3 复核 R3-008 判「AC2 仍未满足」（doc/reviews/GATE3-COVERAGE-MATRIX-review-r3.md:62）；任务卡自认「部分修」（doc/tasks/GATE3-COVERAGE-MATRIX.md:118）

### 33. `GATE3-COVERAGE-MATRIX` L54 AC3 → **DOC**

> 缺 `[Fact]`（纯逻辑）分类：§2 只给出 `[AvaloniaFact]` 62 文件（doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md:35）与 4 类 sidecar gate 7 个（同文:36），全库无 [Fact] 计数/分类（grep:纯逻辑 0 命中），且未逐格标 gate 属性；r1 复核 AC3 判 PARTIAL（doc/reviews/GATE3-COVERAGE-MATRIX-review-r1.md:47），r2 R-007 仍 PARTIAL/OPEN（doc/reviews/GATE3-COVERAGE-MATRIX-review-r2.md:46）

### 34. `GATE3-COVERAGE-MATRIX` L56 AC4 → **DOC**

> §3 的 ❌ 格已清零（doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md:160、:257），但 Host/Core 层 100 项 NOT_RUN 的归因仍是未核实的类名推断：§4.2 表头自认「未逐条核实」（同文:94）、§4.4 自认无法可靠切分 E-2 子集（:153-154）、§7 自认逐类归属未逐条核实 attribute（:194）；r3 复核 R3-006 指出 3 处性质错标（GrantIssuer/StartupSelfCheck/Fea11Watch 实为 [HostSidecarFact]，doc/reviews/GATE3-COVERAGE-MATRIX-review-r3.md:60），末版矩阵未改

### 35. `GOV-PIN-LINEAGE-1` L77 AC1 → **WITHDRAWN**

> 原标 <<BLOCKED: r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC>>；本卡 status:closed_with_limitations 指 r27 撤回原方案、r28 停止改造后收口，非 AC 实施完成（doc/tasks/GOV-PIN-LINEAGE-1.md:208-209）；63 个 TIME_BASED + 6 个 LINE_ENDING 的逐条 pinned-blob 核验记录未产出（诊断侧仅见 verification/GOV-PIN-LINEAGE-1/ac1-pin-only-verification.json）

### 36. `GOV-PIN-LINEAGE-1` L81 AC2 → **WITHDRAWN**

> 原标 <<BLOCKED: r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC>>；本卡 status:closed_with_limitations 指方案撤回后收口，非 AC 实施完成；tools/governance/check.ps1 未修改（doc/tasks/GOV-PIN-LINEAGE-1.md:287-292「明确未做」），历史 blob 校验语义与工作区漂移诊断均未实施

### 37. `GOV-PIN-LINEAGE-1` L85 AC3 → **WITHDRAWN**

> 原标 <<BLOCKED: r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC>>；本卡 status:closed_with_limitations 指方案撤回后收口，非 AC 实施完成；6 项 LINE_ENDING pin 的 pinned-blob 验证与 LF 诊断复核未执行（doc/tasks/GOV-PIN-LINEAGE-1.md:287-292）

### 38. `GOV-PIN-LINEAGE-1` L88 AC4 → **WITHDRAWN**

> 原标 <<BLOCKED: r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC>>；本卡 status:closed_with_limitations 指方案撤回后收口，非 AC 实施完成；23 项 MISSING_FILE 的 commit/路径/blob 状态与 hash 对照及来源链核对未按 AC 交付（doc/tasks/GOV-PIN-LINEAGE-1.md:287-292）

### 39. `GOV-PIN-LINEAGE-1` L92 AC5 → **WITHDRAWN**

> 原标 <<BLOCKED: r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC>>；本卡 status:closed_with_limitations 指方案撤回后收口，非 AC 实施完成；六类回归夹具未建立，checker 既有夹具与 v3 AC gate、Resource Manifest 门禁未被专门回归（doc/tasks/GOV-PIN-LINEAGE-1.md:287-292）

### 40. `GOV-PIN-LINEAGE-1` L96 AC6 → **WITHDRAWN**

> 原标 <<BLOCKED: r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC>>；本卡 status:closed_with_limitations 指方案撤回后收口，非 AC 实施完成；lineage registry、最小 checker diff、测试证据、Handoff 与独立 Review 均未交付（doc/reviews 无 GOV-PIN-LINEAGE-1 审查报告；doc/tasks/GOV-PIN-LINEAGE-1.md:205-221 收口记录）

### 41. `V11R-A-3` L36 AC4 → **IMPL**

> AC4 要求补强 CommandParityContractTests：本卡交付明确未改该文件（verification/V11R-A-3/README.md:95-96 自述『git diff 无这些文件；66→76 改造归 V11R-F0-1』，CommandContractV11RTests.cs:12-14 同述），改由新增 CommandContractV11RTests 承载；该新类只断言 channel/minor/证据列，ContractRow(:199-206) 无 params 字段 ⇒ 『参数特判』无断言。HEAD 的 CommandParityContractTests 由 V11R-F0-1 改造（同文件 :13-16），非本卡交付。口径待 Lead 裁决

### 42. `V11R-C-3` L41 ? → **IMPL**

> tag 已存在（git tag -l v11r-pre-retire → annotated，指向 df883f2ce；verification/V11R-C-3/R1-tag.txt:7），但两项未满足：①未用 rollback-theme-retire.ps1 -CreateTag，改用直接 git tag（R1-tag.txt:10-13 自述脚本会继续 checkout）；②缺『tag 存在后的 -DryRun』证据——唯一 dry-run 是 tag 创建前的 READY 包 verification/V11R-C-3-READY/rollback-dry-run.log:9（tag exists=False），tag 创建于 2026-10-30T03:18:13 晚于该日志；doc/reviews/V11R-THEME-L3-r1-independent.md:79,125 明确要求补一次 tag 存在的 DryRun

### 43. `M2-REGION-RETYPE-CORE` L28 AC2 → **ARCHIVE**

> 旧架构（Tauri/Rust host）已退出：AD-002:30 明确移除 Rust host，AD-002:163 S5 将旧壳原位冻结为证据、不再参与发布，apps/desktop/LEGACY_FROZEN.md:5-6 不再构建/发布/修复；Rust command/allowlist 三视图仅存于冻结证据（grep:set_region_type@apps/desktop/src-tauri/src/library_bridge.rs:836，:4217/:4821）。缺：AD-002 下等效 command/allowlist 验收面。

### 44. `M2-REGION-RETYPE-CORE` L29 AC3 → **RERUN**

> 11 断言用例在树内（tests/editing/test_region_retype.py:75/102/129/158/197/237/263/421/496/522 + tests/providers/test_retype_redetect_persistence.py:184 + tests/pipeline/test_retype_candidate_persistence.py:119），但「先红后绿」只有历史记录（verification/M2-REGION-RETYPE-CORE/verification.md:22），pytest 本轮禁跑（BRIEF §4）。缺：本轮两层断言（service guard 返回 + 管线候选持久化）复跑证据。

### 45. `M2-REGION-RETYPE-CORE` L31 AC5 → **ARCHIVE**

> PROTOCOL_MINOR=3 已落（grep:PROTOCOL_MINOR = 3@src/bootstrap/core_service.py:324），但 AC5 的「M2-AC5 GATE 25/25 重跑 PASS」属旧 Tauri clean-start 打包面（sidecar 构建已迁 Avalonia：apps/desktop/LEGACY_FROZEN.md:23；raw 证据见 verification/M2-REGION-RETYPE-CORE/raw/retype-m2ac5-cleanstart-gate.json）。缺：目标架构下协议 minor 旁路同步与 GATE 25/25 复跑证据。

### 46. `M2-REGION-RETYPE-CORE` L32 AC6 → **RERUN**

> 回归含 cargo + vitest（旧 Rust/React 面，已冻结：apps/desktop/LEGACY_FROZEN.md:5-6、AD-002:30），pytest 三套件与 m2_acceptance 本轮禁跑（BRIEF §4）；历史值只见 verification/M2-REGION-RETYPE-CORE/verification.md:59（650+1sk / cargo 47+1ig / vitest 49 / m2_acceptance 35）。缺：本轮三套件 + cargo + vitest 复跑。

### 47. `RUN-IPC-1` L65 AC4 → **IMPL**

> AC4-2 未满足：缺每条命令的成功路径测试，也缺 ControlRun 非法 action 返回 INVALID_REQUEST、StartRun 幂等键复用返回 IDEMPOTENCY_KEY_REUSED 等 host 层 typed 拒绝单测（现仅 frozen 2.3 域级 5x TARGET_NOT_FOUND + 1x INVALID_REQUEST）；AC4-3 的成功 Run 真实往返为 NOT_RUN（无 book/chapter/page 与 Provider 夹具，见 evidence-layering.md 层3 诚实缺口）：file:verification/RUN-IPC-1/evidence-layering.md + file:verification/RUN-IPC-1/rust-packaged-tests.log

### 48. `RELEASE-PACKAGE-1` L45 AC6 → **DOC**

> 缺 Handoff：doc/handoffs 无 RELEASE-PACKAGE-1-*.md（分支 task/RELEASE-PACKAGE-1 与 worktree 亦无）；check.ps1 -TaskPath、scripts/test.ps1、pytest 均无归档日志（证据目录只有 9 条产物证据；64-hex pin 9/9 已复算一致）：file:verification/RELEASE-PACKAGE-1/package-summary.json

### 49. `M2-SFX-CORRECTION-EXPORTER` L35 AC4 → **IMPL**

> T1b（批量数据生产）产物尚不存在，「与 T1b 产物同构、训练侧零适配」无法验证（Lead 裁决：w7 报告 §需裁决 5）；已核实的只是 T1a 格式面：test:test_manifest_files_are_t1a_format@experiments/M2-SFX-CORRECTION-EXPORTER/tests/test_export.py:42 + test:test_yolo_seg_labels@experiments/M2-SFX-CORRECTION-EXPORTER/tests/test_export.py:56 + grep:/training_data/@.gitignore:13

### 50. `TASK-056` L29 ① → **RERUN**

> 实现与用例在树内（grep:def is_safe_relative_path@src/application/maintenance/cleanup.py:229 + grep:_safe_targets@src/application/maintenance/cleanup.py:193；test:test_paths_outside_safe_prefixes_are_skipped_and_survive@tests/maintenance/test_cleanup.py:141 + test:test_user_source_outside_managed_root_is_never_addressed@tests/maintenance/test_cleanup.py:189），但卡面收口自述「装配接线与模型目录 NOT_RUN」（doc/tasks/TASK-056.md:49），且 pytest 本轮禁跑（BRIEF §4）。缺：产品面接线证据 + 本轮复跑。

### 51. `TASK-056` L30 ② → **RERUN**

> 实现与用例在树内（grep:def preview@src/application/maintenance/cleanup.py:127 + grep:def to_dict@src/application/maintenance/cleanup.py:67,:107；test:test_preview_reports_targets_and_total_bytes@tests/maintenance/test_cleanup.py:109 + test_run_removes_all_generations_with_structured_result@:117），但装配接线与模型目录 NOT_RUN（TASK-056.md:48）且 pytest 本轮禁跑（BRIEF §4）。缺：预览/结构化结果的产品面接线 + 本轮复跑。

### 52. `TASK-056` L31 ③ → **RERUN**

> 实现与用例在树内（grep:class WebtoonTileCacheSweeper@src/infrastructure/imaging/tile_cache_sweep.py:22；test:test_lists_every_generation_relative_to_managed_root@tests/maintenance/test_cleanup.py:90 + test_missing_cache_dir_is_empty@:101），但装配接线 NOT_RUN（TASK-056.md:48）且 pytest 本轮禁跑。缺：瓦片缓存跨代回收的接线证据 + 本轮用例复跑。

### 53. `TASK-056` L32 ④ → **RERUN**

> 实现与用例在树内（grep:def retry_pending_cleanups@src/application/maintenance/cleanup.py:160 + grep:def pending_cleanup_count@src/application/maintenance/cleanup.py:188 + test:test_run_is_idempotent@tests/maintenance/test_cleanup.py:132 + test:test_failure_persists_pending_and_retry_clears_it@tests/maintenance/test_cleanup.py:203），但装配接线 NOT_RUN（doc/tasks/TASK-056.md:48）且 pytest 本轮禁跑。缺：幂等/失败可诊断可重试的本轮复跑。

### 54. `TASK-056` L33 ⑤ → **RERUN**

> 5 次逐次记录存在（file:verification/TASK-056/full-suite-run1.log … run5.log，各 900 passed），但「全仓 passed 不减少」须当轮全仓套件复算；旧 PySide6/QML 壳（QT_QPA_PLATFORM 口径）测试已归档（apps/desktop/LEGACY_FROZEN.md:25），且 pytest 本轮禁跑（BRIEF §4）。缺：当前可复算的全仓基线与 5 次复跑。

### 55. `TASK-056` L34 ⑥ → **MECHANISM_NA**

> Handoff/verification/Review/集成俱在（file:doc/handoffs/TASK-056-delivery.md + file:verification/TASK-056/ + file:doc/reviews/TASK-056-15f977a.md + 集成 commit 11517ac 可解析），但缺 STATUS 台账行：doc/STATUS.md 与 doc/TASK_LEDGER.md 均无 TASK-056 行（grep 0 命中）；另卡面 48 行保留「装配接线与模型目录 NOT_RUN」。

### 56. `V11R-C-RESEARCH-1` L40 AC5 → **DOC**

> 文档声明『V1 不引入任何第三方 UI/主题框架依赖』(RESEARCH_V1.md:8)；但『不修改生产代码』该卡无 commit 字段，无法独立验证

### 57. `MICA-FIX-1` L39 AC1 → **HUMAN**

> **独立复核 P1-01 判定证据不成立**：titlebar-solid.png（2560×1440，sha256 7ce9ed83…）实为 ChatGPT 桌面应用全屏窗口，画面内无 NewManga 窗口；two-wallpapers.json 的 titlebar_pixel=-1（取色失败）与硬编码 hex 不能证明 Mica。缺：真实 NewManga 窗口「纯色壁纸 vs 图案壁纸」A/B 截图 + 窗口句柄/进程证明。对照裁剪图 reviews/titlebar-solid-crop.png

### 58. `MICA-FIX-1` L40 AC2 → **RERUN**

> **独立复核 P2-08**：AC2 唯一证据是 two-wallpapers.json 内的 diagnostics_log 字符串（material=Mica; actual=Mica），无原始启动日志或 --diagnostics 输出文件；卡面 L58 记 AC2 NOT_RUN；且同轮采集（AC1）已证明截图不可信。实现存在仍成立：grep:ActualTransparencyLevel@apps/desktop-avalonia/src/NewManga.App/Views/MainWindow.axaml.cs:1032；缺：原始日志/重跑证据

### 59. `MICA-FIX-1` L41 AC3 → **HUMAN**

> 缺 Win10/不支持环境真机核对：「不得出现黑边/透明穿透」为 NOT_RUN——卡面测试要求表 :59 记 AC3/AC4 NOT_RUN；Review :88「AC3 PARTIAL：Win10 真机不可得（NOT_RUN）」；已核实部分 = test:WindowMaterial.Choose@apps/desktop-avalonia/tests/NewManga.App.Tests/ThemeRetirementR4Tests.cs:77（OpaqueFallback 分支单测）+ grep:MicaFallback@apps/desktop-avalonia/src/NewManga.App/Views/MainWindow.axaml.cs:134（回退背景不透明）

### 60. `MICA-FIX-1` L42 AC4 → **RERUN**

> 缺可复核的回归日志：verification/MICA-FIX-1 下实测仅 3 个文件（mica/titlebar-solid.png、mica/titlebar-pattern.png、mica/two-wallpapers.json），无 scripts/test.ps1、旧壳 vitest 60/567、pytest 3F/2739P/9S 的原始日志与退出码；这些结论目前只出现在卡面 Review :89 与 doc/handoffs/MICA-FIX-1-handoff.md:7 的自述中，按卡面自述不构成证据

### 61. `MICA-FIX-1` L43 AC5 → **DOC**

> 部分满足：证据 pin 3/3 已实算 sha256 与卡面登记逐一 MATCH 且均为 64-hex（titlebar-solid.png/titlebar-pattern.png/two-wallpapers.json），Handoff doc/handoffs/MICA-FIX-1-handoff.md 存在（:8 集成 93aaaeb8c）；但 check.ps1 -TaskPath 无入库实测记录（本轮 Lead 仅实测全仓 check.ps1 = PASS 3 warnings，未覆盖 -TaskPath 变体），且无独立「Record Decision（透明策略/回退策略/取色方法）」段落，handoff :3-6 只有零散叙述

### 62. `P19` L36 AC1 → **ARCHIVE**

> 缺 ② CDP 端点证明 与 ③ 四页 DOM 级断言：verification/P19/dplus-status-r3.md:6 实测 CDP 不可用（设 WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS=--remote-debugging-port=9222 后所有 msedgewebview2.exe 命令行均不含该参数、9222 无监听，被 Tauri 覆盖），实际通道降为真实 WebView2 + UIA 语义（doc/handoffs/P19-dsh.md:7），用户裁决 A 接受 D 替代（verification/P19/codex-review-r2.md:22）；已有 = ①构建产物 hash verification/P19/ac2-main-20261018-0128/run-metadata.txt:6 exe_sha256；④CUA 截图+UIA 转储；⑤禁用态 DOM 断言亦被 UIA 语义替代

### 63. `P19` L38 AC3 → **ARCHIVE**

> PARTIAL：请求/返回/事件/错误四处全域无泄露未闭环——verification/P19/codex-review-r4.md:21 判 AC3 FAIL（已并入的 58 命令扫描实际复现合成 Windows 路径经设置接口回显）；设置路径回显后续由 SEC-FIX-PATH-ECHO-1 修复（doc/handoffs/P19-dsh.md:16），但剩余为框架/设计层限制：Tauri 2.12 不校验顶层未知键 58/58、错误面仅送 error.code（doc/tasks/P19.md:122 与 doc/handoffs/P19-dsh.md:18）

### 64. `P19` L39 AC4 → **ARCHIVE**

> 部分满足且末次 E2E 未闭环：verification/P19/d-run-20261018-0056/run-metadata.txt:10-12 = checks=24 / fails=9 / exit_code=1；trace.log:46-63 显示 9 个分区 en=False + invoke=failed（禁用态原始数据在），但 ASSERT FAIL disabled-not-invokable:* 因 PAGE_CHANGED 判据误判（panes=[] 空致误判）；doc/handoffs/P19-dsh.md:34 明记「已改为 en/invoke 判定，但未按其重跑」→「可见但不可操作且有可理解原因」的整套断言未以有效判据通过

### 65. `FEA-07-AC5-NATIVE-1` L52 AC-N1 → **HUMAN**

> 原标 <<PARTIAL: 7/15 混合 DPI 组合已执行（4K 100/125/150/175/200 × 2K 100/125/150 子集），DPI 切换与屏幕内 containment 全部通过；其余组合与「无模糊/无错位」客观断言未做>>；卡面 L138 复判「AC-N1: PARTIAL」、L120 记未做组合为 NOT_RUN，故未达成本卡验收

### 66. `FEA-07-AC5-NATIVE-1` L53 AC-N2 → **IMPL**

> 原标 <<PARTIAL: 主窗跨屏归属/可见/contained 已验；Inspector 浮窗不存在（RegisterSecondary 零生产调用）→ 该子项 NOT_APPLICABLE；中文 IME 组合输入已验（命令面板输入「你好」）；快捷键「不重复执行」未单独断言>>；卡面 L139 复判「PARTIAL/NA」、L145 记 Inspector 浮窗不存在，故未达成本卡验收

### 67. `FEA-07-AC5-NATIVE-1` L54 AC-N3 → **HUMAN**

> 原标 <<PARTIAL: OS 级拔屏（DisplaySwitch /internal）已验且自动迁移窗口；物理拔屏已执行：拔后主窗被系统最小化（需手动恢复，D-AC5-1）、恢复后回主屏、重插后自动回 4K 原几何；未 flush 编辑态 fail-closed 未执行>>；卡面 L140 复判「PARTIAL」、L125 记 physical/未 flush 子项 NOT_RUN，故未达成本卡验收

### 68. `FEA-07-AC5-NATIVE-1` L55 AC-N4 → **HUMAN**

> 原标 <<PARTIAL: PerMonitorV2（app.manifest + exe 内嵌）与跨 DPI 几何保持已验；换主屏双向 rc=0 且应用存活；重启窗口几何持久化 → NOT_APPLICABLE（产品无实现）；恢复点按用户决定保留原生 2K>>；卡面 L141 复判「PARTIAL/NA」、L135 记恢复点未逐项还原，故未达成本卡验收

### 69. `FEA-07-AC5-NATIVE-1` L56 AC-N5 → **DOC**

> 原标 <<PARTIAL: 证据/工具齐；r1 Review changes_requested 已处置，r2 复审未完成>>；卡面 L142 复判「PARTIAL」、L147 记 AC5 行保持 NOT_APPLICABLE，独立 Review 未闭环，故未达成本卡验收

### 70. `P20-MEM-OPT-1` L38 AC2 → **ARCHIVE**

> 正文阈值 ≤350 MB 未达成：实测空闲稳态 443.3 MB（卡面 :28「超 26%」）；本卡执行结果 :93-95 记「AC2 —— 经用户裁决后无需实施」，用户 2026-10-18 把 P20 的 AC3 阈值改为 480 MB（AC 正文 350 MB 未被改写，故按正文判未达成）；且缺「优化前后对照的多轮采样（含 CSV 时序）」——verification/P20-MEM-OPT-1 实测仅有单轮 ac1-probe-20261018-072149 快照（process-tree.json/probe-trace.log），无优化后时序 CSV；EmptyWorkingSet 方案因指标操纵被拦截回退（:97-105）

### 71. `P20-MEM-OPT-1` L39 AC3 → **ARCHIVE**

> 未执行：卡面 :107-109 明记「AC3/AC4 —— 随 AC2 目标消解而不再适用；未执行」；无 P20 AC2 冷启动（≤2.0 s / Core ≤3.5 s）与 AC4（交互 ≤50 ms、60 FPS）的同方法复测对照数据入库

### 72. `P20-MEM-OPT-1` L40 AC4 → **ARCHIVE**

> 未执行：卡面 :107-109 明列未执行；缺四页可达复测、bundle 与 resources 的 core_service.exe SHA-256 相等复核、启动 smoke 窗口可达证据（verification/P20-MEM-OPT-1 仅 5 个 pin：process-tree.json、probe-trace.log、probe-process-tree.ps1、experiment-steady-after-trim.ps1、test-interaction-and-pages.ps1，脚本存在但无本次运行产物）
