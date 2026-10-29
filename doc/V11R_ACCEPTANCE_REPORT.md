# New Manga 全功能整改 + 全新 UI/UX + Theme Studio 重建 · 验收报告

生成时间：2026-10-30（Asia/Shanghai）
Lead / Integrator：DeepSeek Harness（DSH）
仓库：`G:/CODEX/New Manga`；main HEAD：`5e2d60023`（本报告随其后一个提交入库）
授权依据：用户总指令（V11R）；证据/裁定索引见 `doc/V11R_PROGRAM.md` §8（R-01…R-25）、`doc/V11R_PIN_LEDGER.md`。

> 本报告只写**实测**结论。未运行、无证据、环境不允许的项目一律标 `NOT_RUN`/`BLOCKED`，不伪造 PASS。

---

## 1. 总结论

| 范围 | 结论 | 说明 |
|---|---|---|
| V1.1 审计整改（工作流 A） | **PASS_WITH_ISSUES** | A-1/A-2/A-3/A-5/A-6/A-7 完成并集成；66 命令契约 FROZEN 49 / PARTIAL 17 / GAP 0；**追加发现并修复 P0**：发布版默认 `ReadOnlyUntilParity` 导致导入/建书/运行全被拒（A-5）。F0-1 Region 写面 4 轮审查 P1 全关闭、I4 后仅待独立复核（见 §7）。 |
| 全新 UI/UX（工作流 B） | **PASS_WITH_ISSUES** | 新 Avalonia 外壳 + Library/Console/Studio Page/Studio Batch + 导出/术语工作面全部交付；main 已切**新壳为默认入口**（`--shell=legacy` 保留回滚）。独立审查 r1/r2/r3 的 P1 均已关闭；剩余 P2/P3 见 §8。 |
| Theme Studio 重建（工作流 C） | **PASS_WITH_ISSUES** | C-1 新主题引擎 **PASS**；C-2 Theme Studio 7 分区 **PASS_WITH_ISSUES（2×P2）**；C-3 旧主题**退役执行 BLOCKED**（准备包就绪，但回滚安全网 P1 待修）。 |
| 设计系统（工作流 D） | **PASS_WITH_ISSUES** | D-1 独立审查 r2 的 2×P1 已修（真实 App 资源栈全局令牌、徽标合成对比度），DS 82 测试；仍有 6 行/6 对状态色落极端表面未达 4.5:1（已登记组件约束）。 |
| 总体 | **未达 L4 最终验收** | 阻断项：C-3 未执行（旧主题系统仍在）、F0-1 待最终复核、跨项目并行测试偶发、Windows 实机/DPI/IME/Trim 未验证（NOT_RUN）。可交付为 **M2（新壳可用）+ M3（全工作面）候选**。 |

---

## 2. 交付物

### 2.1 架构（保持 AD-002 冻结：C#/.NET 9 + Avalonia 11.3 + Python Core + SQLite + Typed JSON IPC）
- 新增 `NewManga.DesignSystem`（令牌/样式/自定义控件/图标/a11y）与 `NewManga.ThemeEngine`（主题包 Schema/Registry/Validator/Persistence/Preview/Palette/迁移/`IThemeService`）。
- 依赖方向固定：`App → ThemeEngine → DesignSystem`（R-20）；App 不再直接依赖旧主题实现（C-3 完成后旧项目删除）。
- 旧 React/Tauri 壳未成为生产前端（保留为历史证据）。

### 2.2 UI（工作流 B）
- 外壳：三空间（资料柜/工作台/控制台）+ Studio 双模式（Page ⇄ Batch）+ 共享选择模型（R-16）+ 键盘仲裁（R-17）+ Theme Studio 表面栈。
- Library：搜索/排序/筛选、封面网格、驻留详情、多选批量条、导入 Dock（含新建章节）、回收站、阅读浮层。
- Studio Page：画布 + Region 编辑/检查器五页签/胶片条/六态（空/加载/部分/错误/只读/锁定）。
- Studio Batch：动态列矩阵（10/5 列真实投影）、七态符号、计数 Chip、门禁确认、Stop 二次确认、R-22 意图级幂等键、增量刷新保滚动/焦点。
- Console：9 分区（真实 4 项 + 诚实 NOT_WIRED 5 项）、Provider/网络档案/凭据（永不回显）、Run 投影与控制（共享单一 poller，R-24）。
- 导出/术语：导出预检（范围/格式/stale 策略两值真实透传）、进度/取消/历史；术语与约束因 Core 无读写命令，诚实 NOT_WIRED。

### 2.3 Theme Studio（工作流 C）
- C-1 引擎：10 子系统 + 203–229 测试；Part B Avalonia 适配器（`DesignSystemThemeLayerSink`，59 键白名单、原子替换、失败保持原状、不重建窗口、画布像素差=0）；K-21 Scrim 全局不变量。
- C-2 页面：7 分区全部可用（主题库/预览/我的主题/编辑/外观/导入导出/恢复默认），真实生产服务（非 STUB），24 帧渲染证据 + 应用/取消/回滚真断言。
- C-3 准备：依赖图（631 引用/68 文件）、迁移门 26 测试、删除批次 A/B/C + R1–R6、回滚脚本、对比度矩阵。

### 2.4 服务层与 Core（工作流 A）
A-1 `CreateChapterAsync`；A-2 `IRunController`（暂停/继续/停止/重试，R-08 幂等键纪律）；A-3 66 命令契约 + 派生 parity 测试；A-4 同 SHA CI + 干净克隆可重建；A-5 **P0 写入策略**（默认可写 + 三重护栏 + 首次备份）；A-6 启动自检（协议/能力不匹配降级只读）；A-7 导出 `stale_policy` 透传。

---

## 3. 测试与门禁（L1–L4）

| 层级 | 内容 | 结果 |
|---|---|---|
| L1 任务级 | 各任务 build `-warnaserror` + 聚焦测试 | PASS（证据各 `verification/<TASK>/`） |
| L2 功能级 | 全量 `dotnet test`（5 项目）+ `pytest` | **PASS（最后一次干净运行 ×2）**：DS 82 / ThemeEngine 229 / Host 49(+28 skip) / CoreClient 45(+22 skip) / App 305(+7 skip) = **710 通过 / 57 环境性跳过 / 0 失败**；Python **2727 passed / 10 skipped / 0 failed**（F0 分支） |
| L3 里程碑 | 独立 Reviewer（≠ Owner）对 UI/主题/DS 的固定 pin 审查 | UI r3：`PASS_WITH_ISSUES`（P1 后已修）；主题域：C-1 PASS、C-2 PASS_WITH_ISSUES、C-3-READY FAIL；DS r2 FAIL→I2 已修待终审；F0 4 轮审查 P1 全关闭 |
| L4 发布验收 | Windows 实机 / DPI / IME / Trim / AOT / 真 sidecar E2E | **NOT_RUN**（环境限制，见 §9）；新壳在**真实窗口**已启动并截图取证（`verification/V11R-INT-1/v2-shell-default-first-run.png`） |

> 注：全量解决方案运行时偶发 1 个 CoreClient 测试失败（单项目独立运行 0 失败，连续 2 次复跑通过）；已登记测试基础设施 follow-up（A-6 runsettings 串行化已落地）。

---

## 4. P0 发现（超出原审计，必须在总报告强调）

发布版 GUI 默认 `ReadOnlyUntilParity`（`AppOptions/HostOptions ParityReached=false`，NSIS 快捷方式无参数），导致用户侧**导入、建书、建章、运行全部被 `HOST_READ_ONLY` 拒绝**。A-5 已修：默认 ReadWrite + 三重护栏（旧 Tauri 壳在运行 / `--parity=false` / Host 未就绪）+ 首次运行备份 + `HostViewSnapshot.ReadOnlyReason`，并有真实备份产物与四象限证据。

---

## 5. 独立审查记录

| 对象 | 轮次 | 结论 | 处置 |
|---|---|---|---|
| D-1 设计系统 | r1 / r2 | FAIL / FAIL（2×P1） | P1 已修（真实 App 资源栈令牌、徽标合成对比度），P2 八项完成 → 待终审 |
| F0-1 Region 写面 | r1 / r2 / r3 / r4 / I4 | FAIL×4；r4 仅 2×P2 未闭 | I4 已修 3 项，待窄复核 |
| B-1/B-2 | r1 / r2 / r3 | PASS_WITH_ISSUES | I1 关闭 P1；B-2 轮询恢复/状态词表 P2 部分完成 |
| B-3/B-4 | r1 / r2 / r3 | FAIL → PASS_WITH_ISSUES | I1→I3 关闭 P1；DIS 上收/证据/R-25 已修 |
| B-5 | r1 | PASS_WITH_ISSUES | P2 证据重生成 + A-7 后 stale 两值已上收 |
| C-1 / C-2 / C-3-READY | r1 | PASS / PASS_WITH_ISSUES / FAIL | C-2 2×P2、C-3-READY 1×P1+2×P2 待修 |

报告均归档 `doc/reviews/`。

---

## 6. 已知问题（不修项 / 组件约束）

1. **状态色落极端表面**：6 行/6 对（dark/light × `bg.overlay/sunken/raised`）未达 4.5:1；裁决=状态文字只落 `bg.panel/raised`+`statusMuted`，其余为背景用途（`verification/V11R-D-1/contrast-matrix.md`）。
2. **`Nm.Color.Scrim`/`Instant` 为全局不变量**，不入 59 键主题层（R-21）。
3. **系统强调色跟随**仅作用域生效、不持久化（GAP-3，V1 不扩 `IThemeService`；登记 V1.x follow-up）。
4. **术语表/不译表**无 Core 读写命令 → 三页诚实 NOT_WIRED。
5. **过期/待确认计数**无投影口径 → 显示 `—`（follow-up：Core 投影扩展）。
6. **页缩略图网格**需 Host 缩略图命令（follow-up）。
7. **`ImportExportPanels`/`ReaderWorkbenchPages` 本机路径 fallback** 待 owner 清理（verify-clean-clone ALLOW_PENDING）。
8. 主题层行高与绝对行框并存（R-15 已纳入白名单并按主题层派生）。

---

## 7. BLOCKED / 未完成

| 项 | 状态 | 原因 / 解除条件 |
|---|---|---|
| **C-3 旧主题退役执行** | **BLOCKED** | 准备包就绪，但回滚脚本 DryRun 在 tag 校验前 throw（P1，Reviewer 实测 exit=1）+ 对比度计数错误（P2）+ 陈旧数字（P3）。最小修复集已派并给出窄复审要求；修复+窄复审通过后按 R1–R6 执行（先打 `v11r-pre-retire` tag）。 |
| **F0-1 合并** | **BLOCKED（窄复核中）** | 4 轮审查 P1 全关闭，I4 修 3×P2；独立 Reviewer 正在只核这 3 条，通过即整支合入（含 C077 `list_page_region_texts`）。 |
| D-1 终审 | 待审 | I2 已交付（2×P1+P2 全闭），需固定 pin 终审。 |
| C-2 2×P2 | 待修 | ThemeStudio C# 裸几何值 + conformance 排除、AC9 像素探针恒真。 |

---

## 8. 下一步建议（按优先级）

1. **C-3-READY 修复 + 窄复审 → 执行 C-3 退役**（旧主题项目/旧壳主题入口删除，依赖图/迁移门/回滚三件套已就绪）。
2. **F0-1 窄复核通过 → 合入 main**，ui-studio 接 C077 与 Region 写命令（`verification/V11R-F0-1-I1/CONSUMER_GUIDE.md`）。
3. **D-1 终审 + C-2 两个 P2 修复**，合入后冻结 V1 设计/主题契约。
4. **L4 实机验收**：Windows 10/11、DPI 100/150/200、IME、Trim/AOT/单文件发布、真 sidecar E2E（建书→建章→导入→运行→导出→重启持久化）。
5. **测试基础设施**：解决跨项目并行偶发（runsettings 已串行化宿主，仍需定位残余共享状态）。
6. 已知 follow-up：Core 投影计数、Host 缩略图命令、术语读写命令、本机路径 fallback、系统强调色持久化。

---

## 9. 环境限制（NOT_RUN 汇总）

Windows 实机启动 smoke、真实 DPI 多屏、IME、屏幕阅读器、Trim/AOT/单文件发布、GitHub Actions 真实运行、PyInstaller 同 SHA sidecar 集成、真 `%APPDATA%` 生产数据读写 —— 均因当前环境不可执行而 `NOT_RUN`，无伪造。
