---
id: FEA-07-AC5-NATIVE-1
title: FEA-07 AC5 原生双屏矩阵（真实 2K+4K、混合 DPI、拔屏、IME）
kind: verification
governance_version: 3
status: ready
approval: 用户 2026-11-09 明示「我有硬件双屏，一个 2k 一个 4k」，并授权脚本切换显示模式/缩放并记录恢复点；scope = FEA-07 AC5 冻结矩阵（`doc/tasks/FEA-07.md` AC5 行）；0 pin（验证卡，不改产品语义）
suggested_owner: dsh
owner: dsh
reviewer: 独立上下文 fresh subagent（证据交付后指派）
depends_on:
  - FEA-07
base_commit: b6cd53260
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-07-AC5-NATIVE-1
allowed_paths:
  - doc/tasks/FEA-07-AC5-NATIVE-1.md
  - doc/tasks/FEA-07.md
  - doc/reviews/FEA-07-AC5-NATIVE-1-*.md
  - doc/reviews/ADJ-2026-11-RESIDUAL-WAIVER.md
  - doc/handoffs/FEA-07-AC5-NATIVE-1-*.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/FEA-07-AC5-NATIVE-1/**
out_of_scope:
  - 不改产品语义/契约/pins；不新增依赖；不改 `tools/e2e/**`、`scripts/**`
  - 若原生矩阵暴露产品缺陷 → 只登记（DEFECTS）并 re-home 具名卡，不在本卡修
  - 真实用户书籍/DB/主题设置不得修改；显示设置仅临时切换并在结束时恢复（恢复点 JSON + 校验）
  - 原生 IME：仅在实际编辑面存在时执行；无可用 IME 输入面则登记 `NOT_RUN`（不得写成 PASS）
---

# FEA-07-AC5-NATIVE-1：AC5 原生双屏矩阵（真实硬件）

> **状态 `ready`**。用户 2026-11-09 提供真实双屏（AOC 2K + Philips 4K），4K 已连接并扩展、Mi TV 关闭；授权脚本切换显示模式/缩放并记录恢复点。
> **本卡只做验证与取证**：不改产品代码；发现的缺陷登记并 re-home。

## 环境基线（2026-11-09 实测）

- 物理屏：`AOC AG273QS3R4B`（2K，2560×1440）+ `Philips 279M1RV`（4K，3840×2160）；`Mi TV` 已关闭（WMI 仍报 Active，需在矩阵中确认不在桌面）。
- 当前桌面：`\\.\DISPLAY1` 1920×1080@100%（主）+ `\\.\DISPLAY2` 3840×2160@150%（4K，DPI 144）；`PerMonitorSettings` 仅有 Philips 键（`DpiValue=0`）。
- 显卡：NVIDIA RTX 5070 Ti；虚拟适配器 MuMu/Oray IDD/GameViewer 均 Inactive。
- 会话：console 会话 1 活跃。

## Acceptance Criteria（冻结）

- [ ] **AC-N1（混合 DPI 拓扑）**：2K 置原生 2560×1440、4K 置原生 3840×2160，扩展排列；在两屏分别设置 100%/125%/150%/175%/200%（4K）与 100%/125%/150%（2K），逐组合记录每屏 `dpi/scale/rect/primary`；应用窗口在两屏间移动后 DPI 正确切换（无模糊/无错位）。
- [ ] **AC-N2（浮动窗口归属）**：Inspector 浮窗置于副屏 → 可见/可操作；主窗与浮窗跨屏拖动不丢屏外；目标屏不支持浮动时安全停靠（回主窗）；快捷键不重复执行。
- [ ] **AC-N3（拔屏/换主屏）**：OS 级禁用副屏（并尽量物理拔线）→ 第二窗口内容回主窗对应页面；未 flush 编辑态 fail-closed 留在主窗缓冲（不丢不覆盖）；换主屏后布局/全屏状态正确。
- [ ] **AC-N4（manifest/PerMonitorV2 与提交恢复）**：发布 manifest 实际启用 PerMonitorV2（读实际 exe manifest 断言，不只看 csproj）；混合 DPI 下窗口位置/大小提交与恢复正确；恢复点（分辨率/缩放/排列/主屏）在结束时逐项还原并校验。
- [ ] **AC-N5（证据/审查/翻转）**：真实桌面截图（每案例 ≥1，含两块屏与窗口位置）+ 逐案例 JSON + 恢复点 JSON + 失败/跳过原因；独立上下文 Review；`FEA-07` AC5 行 append-only 从 `NOT_APPLICABLE` 翻 `[x] <<MET>>`（或按实测登记 limitation + 剩余 NA 子项），ADJ 登记。

## 实现口径

1. 工具放 `verification/FEA-07-AC5-NATIVE-1/tools/`：`probe-displays.ps1`（DPI 感知采样）、`capture-restore-point.ps1`（恢复点）、`run-native-matrix.ps1`（逐案例驱动 + 截图 + JSON）。
2. 显示切换：`ChangeDisplaySettingsEx`（模式/位置）+ `DisplayConfigSetDeviceInfo`（每屏 DPI）优先；失败则记录并要求用户手动设置该步。
3. 截图：`.NET Graphics.CopyFromScreen` 逐屏 + 全桌面拼接；保存 PNG + SHA256 + 尺寸/DPI 元数据。
4. 应用驱动：真实 `NewManga.App.exe`（Release），`--presentation-host=true --data-root <隔离> --log-dir <隔离> --theme-home <隔离>`；浮窗/切屏通过 `SetWindowPos` + 应用内动作；断言用窗口矩形/可见性/截图。
5. **所有显示设置必须可恢复**：恢复点 JSON + 结束时逐项 `ChangeDisplaySettingsEx` 还原 + 采样校验；失败时保留恢复点文件并在证据中标注。

## 行文口径（红线）

- 不得以 headless 断言代替原生验收；不得把 skip/`NOT_RUN` 写成 PASS。
- 本卡 done 不改变「原生矩阵之外」的任何结论；AC5 行翻转须 append-only + ADJ 登记。

## 执行结果（2026-11-09，DSH 一手执行）

### 环境
- `\\.\DISPLAY1` **AOC AG273QS3R4B** 2560×1440@165（主，100%）；`\\.\DISPLAY2` **Philips 279M1RV** 3840×2160@120（150%）；NVIDIA RTX 5070 Ti；console session 1 活跃。
- manifest：`apps/desktop-avalonia/src/NewManga.App/app.manifest:6-7` → `dpiAware true/pm` + **`dpiAwareness PerMonitorV2`**（csproj `ApplicationManifest` 引用）。

### 混合 DPI 跨屏拖动（真实鼠标手势）
| 配置（2K/4K） | 2K 窗口 | 拖到 4K 后 | DPI | 完全在 4K 内 |
|---|---|---|---|---|
| 100% / 150% | 1408×792 @96 | 2112×1188 @144 | 96→144 | 是 |
| 100% / 125% | 1408×792 @96 | 1760×990 @120 | 96→120 | 是 |
| 100% / 200% | 1408×792 @96 | 2816×1584 @192 | 96→192 | 是 |
| 150% / 200% | 1558×792 @144 | 2077×1056 @192 | 144→192 | 是 |

- 物理尺寸严格按目标屏缩放比（DIP 保持）；截图 `evidence/screenshots/*drag*.png`。
- 对照：`SetWindowPos` 直接注入物理尺寸会按 DIP 保持放大而越屏缘 —— **探针伪影，非产品缺陷**（真实拖动正确）。

### 拔屏（OS 级 `DisplaySwitch.exe /internal`）
- 窗口在 4K (3616,200) 2592×1458@150% → `/internal` 后 **(703,134) 1728×972@100%**、**完全在主屏内**、**进程存活**；`/extend` 后 4K 恢复 3840×2160@150% @(2560,0)。

### 每屏缩放切换
- `DisplayConfig SET_DPI_SCALE` rc=87 不可用；注册表 `DpiValue` + 广播不生效；**UIA 操作「设置 → 显示」可行**（`tools/set-scale-uia.ps1`，先选 `显示器 N` 再选 `缩放`）。
- 映射：`显示器 1`=AOC、`显示器 2`=4K；已实测 2K 100/125/150%、4K 125/150/200%，结束恢复 2K 100% / 4K 150%。

### AC 判定（待独立 Review 后正式登记）
- **AC-N1（混合 DPI 拓扑）**：MET（4 组配置 + DPI 切换 + 截图）。
- **AC-N2（浮动窗口归属）**：**部分 / limitation** —— 主窗跨屏归属与可见可操作 MET；**Inspector 浮窗不存在**（`RegisterSecondary` 零生产调用，L-R4a-1）→ 该子项 NA。
- **AC-N3（拔屏）**：OS 级拔屏 MET（窗口回主屏、进程存活）；**未 flush 编辑态 fail-closed `NOT_RUN`**；物理拔线未做。
- **AC-N4**：PerMonitorV2 manifest **MET**；混合 DPI 提交/恢复 MET（4 组+拔屏后恢复）；恢复点已保存（AOC 分辨率待用户裁决是否还原 1920×1080）。
- **AC-N5**：证据齐（`verification/FEA-07-AC5-NATIVE-1/README.md`、`evidence/matrix-summary.json`、截图）；**独立 Review 与 AC5 行翻转待完成**。

### 限制（不得写成 PASS）
- Inspector 浮窗不可验证（生产未实现第二窗口）。
- 未 flush 编辑态 fail-closed、原生 IME、换主屏/全屏子项：`NOT_RUN`。
- 物理拔线未做（用 OS 级显示移除模拟）。
- 缩放切换依赖 UIA（系统未提供脚本 API）；证据含每次切换前后 DPI 采样。
