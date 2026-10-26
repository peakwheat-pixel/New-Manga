# UIUX-V2-RUNTIME-NARROW-1 — 证据与结论

修复 900×700（DPR 2）窄窗横向溢出（`documentElement.scrollWidth=1024 > clientWidth=900`），
并把 S10 的 KNOWN_DEFECT 升级为硬断言。

## 根因（实测，非推测）

**撑宽元素：`.nm-app`（运行时根容器，`data-testid="app-root"`）。**

- 规则：`apps/desktop/frontend/src/ui/ui.css:18`（修复前）——
  `.nm-app { width: 100%; min-width: 1024px; ... }`
- 机制：视口 900 时 `#root`/body 均为 900（`width:100%`，无 min-width），而 `.nm-app`
  的 `min-width: 1024px` 把根盒强制撑到 1024；根盒溢出 `#root`，body 的
  `overflow: hidden`（base.css）把溢出裁剪并把 1024 报告为视口滚动区域，
  即 `documentElement.scrollWidth = 1024`。
- 实测证据（改前，`diag/before-fix-diag.json`，改前 exe =
  REALCORE-2 冻结构建 `E58CFE59…`）：
  - 900×700 DPR2 四页全部 `doc.scrollWidth=1024 / clientWidth=900`，
    `.nm-app` rect.width=1024、computed `min-width: 1024px`；
  - 溢出元素扫描（rect.right > 900）显示全部 offender 都是 `.nm-app`
    及其沿 1024 容器铺开的子孙（nm-titlebar / nm-window-buttons /
    nm-shelf__main / nm-detail / nm-settings__content 等），无第二个独立撑宽源；
  - 1280×800 DPR2 四页 `1280/1280` 无溢出（1280 > 1024，min-width 不触发），
    与缺陷只在 <1024 视口出现一致。
- 旁证：全前端 CSS 中除该行外不存在其它 ≥1024 的宽度下限
  （唯一非零大 min-width 就是这一条）。

## 修法

1. **`src/ui/ui.css`**：删除 `.nm-app` 的 `min-width: 1024px`（保留 `min-height: 680px`，
   本卡只涉宽度）。窄窗几何由页面自身断点承接，不靠根容器硬撑。
2. **`src/pages/pages.css`**：新增 `@media (max-width: 1023px)` 窄断点——
   `.nm-book-grid` 从固定 `repeat(5, 168px)`（最小宽 904px）改为
   `repeat(auto-fill, minmax(150px, 1fr))`，`.nm-book-card` 配套 `width: auto`。
   原因：去掉根容器 min-width 后，900 视口下库区只剩约 512px，固定 5 列的
   904px 最小宽度会让库区内部横向滚动；自适应列把同样的卡片排满库区。
   ≥1024px 视口不命中该断点，固定 5 列布局不变。
3. 标题栏 `minmax(150px,1fr) auto minmax(360px,1fr)` **未改**：实测三段
   min-content = 150 + 326（tabs）+ 360 + 间距 48 = 884 < 900，900 视口下
   本就放得下（改后实测 brand 166 / tabs 326 / actions 360，actions.right=892），
   窗口按钮完整可见。
4. **`e2e/uiux-v2/run.mjs` S10 升级**：`knownDefect("窄窗横向溢出…")` 改为硬断言
   `check("900×700 书架无横向溢出（scrollWidth===clientWidth）")`；新增
   900×700 与 1280×800 两档 × 四页（书架/工作台/阅读器/设置）逐页
   `scrollWidth === clientWidth === innerWidth` 断言与截图（report 字段
   `narrowViewportMatrix`，共 8 行）。
5. **`e2e/uiux-v2/lib/env.mjs`**：隔离根与 canonical 证据目录从 REALCORE-2
   改指本卡（`task-envs/UIUX-V2-RUNTIME-NARROW-1` 与本目录），
   `run.mjs` 的 `TASK_ID`/`RUN_ID` 同步改为 NARROW-1——满足任务卡硬约束 1
   （本卡运行不得写 REALCORE-2 证据树）。
6. 新增诊断脚本 `e2e/uiux-v2/diag-narrow.mjs`（两档四页宽度构成 + 溢出元素
   扫描 + 截图，改前/改后各跑一次）。

## 改前 / 改后实测数字（documentElement.scrollWidth / clientWidth）

| 视口 | 页面 | 改前 | 改后 |
|---|---|---|---|
| 900×700 DPR2 | 书架 | **1024 / 900（溢出 124px）** | 900 / 900 |
| 900×700 DPR2 | 工作台 | 1024 / 900 | 900 / 900 |
| 900×700 DPR2 | 阅读器 | 1024 / 900 | 900 / 900 |
| 900×700 DPR2 | 设置 | 1024 / 900 | 900 / 900 |
| 1280×800 DPR2 | 四页 | 1280 / 1280 | 1280 / 1280 |

- 改前数据：`diag/before-fix-diag.json`（另见 REALCORE-2
  `verification/UIUX-V2-RUNTIME-REALCORE-2/run-i34/report.json` S10：
  `docWidth:1024, clientWidth:900`）。
- 改后数据：`diag/after-fix-diag.json` 与 `run-i3/report.json`
  （`narrowViewportMatrix`，S10 内含 S6 创建的真实书卡）。
- 1280×800 不退化：改前/改后诊断的 1280 档四页布局数值逐项比对
  **完全一致**（`.nm-app` 1280、titlebar 轨道 453/326/453、库区 892、详情 340）。
- S10 原有通过项全部保持：标题栏三段不重叠、书架内容区与详情区不重叠、
  `blurLayers=2`（≤2）、状态条可见（width 868、位于视口内）。

## 复现命令

```powershell
cd "G:/CODEX/New Manga/apps/desktop/frontend"; npm run build
cd ../src-tauri; cargo tauri build --no-bundle --config tauri.acceptance.conf.json
cd ../frontend; $env:UIUX_E2E_EXE='G:/CODEX/New Manga/apps/desktop/src-tauri/target/release/m2rc1-desktop.exe'; node e2e/uiux-v2/run.mjs
# 诊断（可选）：node e2e/uiux-v2/diag-narrow.mjs
node node_modules/typescript/bin/tsc --noEmit
npx vitest run
```

## 验收结果（2026-10-26，exe SHA256 = C1AB2749EAEE5E1BD793EEC1FCA59158B76E44CF741349A0962B76AC11DFA8BD）

| 项 | 结果 | 证据 |
|---|---|---|
| `node e2e/uiux-v2/run.mjs` exit 0，S1..S10 全 PASS，S10 无 KNOWN_DEFECT | **PASS**（exit=0；S10 15 checks 全 PASS，knownDefects=0） | `run-i3/report.json` |
| 900×700 四页 `scrollWidth===clientWidth` + 截图 | **PASS**（四页 900/900） | `run-i3-shots/11-900x700-dpr2-{shelf,workbench,reader,settings}.png`、`11-shelf-900x700-dpr2.png` |
| 1280×800 四页 `scrollWidth===clientWidth` + 截图 | **PASS**（四页 1280/1280） | `run-i3-shots/12-1280x800-dpr2-*.png` |
| `tsc --noEmit` | **PASS**（exit=0） | 本 README 复现命令 |
| `vitest run` | **PASS**（60 files / 567 tests，与基线一致） | 同上 |
| 隔离数据根 | 全部写读在 `task-envs/UIUX-V2-RUNTIME-NARROW-1/run-i{1,2,3}`，未触碰用户 %APPDATA% | `run-i3/report.json` envManifest |

## 证据清单

- `diag/before-fix-diag.json` — 改前两档四页诊断（含 offenders 扫描，根因实锤）
- `diag/after-fix-diag.json` — 改后两档四页诊断
- `diag/shots-before/`、`diag/shots-after/` — 各 8 张（两档四页）
- `run-i3/report.json` — 完整 S1..S10 验收报告（真实 packaged EXE + 真实 Core）
- `run-i3-shots/` — S10 两档四页截图 9 张（含书架详查 1 张）
- 原始运行环境（task-env，不入库）：`G:/CODEX/New Manga.workspace/task-envs/UIUX-V2-RUNTIME-NARROW-1/run-i{1,2,3}/`（logs / stdout / stderr / fixtures / library.db）
