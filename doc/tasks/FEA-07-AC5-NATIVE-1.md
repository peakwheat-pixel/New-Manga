---
id: FEA-07-AC5-NATIVE-1
title: FEA-07 AC5 原生双屏矩阵（真实 2K+4K、混合 DPI、拔屏、IME）
kind: verification
governance_version: 3
status: closed_with_limitations
approval: 用户 2026-11-09 明示「我有硬件双屏，一个 2k 一个 4k」，并授权脚本切换显示模式/缩放并记录恢复点；scope = FEA-07 AC5 冻结矩阵（`doc/tasks/FEA-07.md` AC5 行）；0 pin（验证卡，不改产品语义）
suggested_owner: dsh
owner: dsh
reviewer: 独立上下文 fresh subagent（证据交付后指派）
depends_on:
  - FEA-07
base_commit: b6cd53260
branch: null
worktree: null
integration_commit: 0bcdeb9fc
delivery_head: 0bcdeb9fc
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [ ] **AC-N1（混合 DPI 拓扑）**：2K 置原生 2560×1440、4K 置原生 3840×2160，扩展排列；在两屏分别设置 100%/125%/150%/175%/200%（4K）与 100%/125%/150%（2K），逐组合记录每屏 `dpi/scale/rect/primary`；应用窗口在两屏间移动后 DPI 正确切换（无模糊/无错位）。 <<PARTIAL: 7/15 混合 DPI 组合已执行（4K 100/125/150/175/200 × 2K 100/125/150 子集），DPI 切换与屏幕内 containment 全部通过；其余组合与「无模糊/无错位」客观断言未做>>
- [ ] **AC-N2（浮动窗口归属）**：Inspector 浮窗置于副屏 → 可见/可操作；主窗与浮窗跨屏拖动不丢屏外；目标屏不支持浮动时安全停靠（回主窗）；快捷键不重复执行。 <<PARTIAL: 主窗跨屏归属/可见/contained 已验；Inspector 浮窗不存在（RegisterSecondary 零生产调用）→ 该子项 NOT_APPLICABLE；可操作性与快捷键未执行>>
- [ ] **AC-N3（拔屏/换主屏）**：OS 级禁用副屏（并尽量物理拔线）→ 第二窗口内容回主窗对应页面；未 flush 编辑态 fail-closed 留在主窗缓冲（不丢不覆盖）；换主屏后布局/全屏状态正确。 <<PARTIAL: OS 级拔屏（DisplaySwitch /internal）已验且自动迁移窗口；物理拔屏已执行：拔后主窗被系统最小化（需手动恢复，D-AC5-1）、恢复后回主屏、重插后自动回 4K 原几何；未 flush 编辑态 fail-closed 未执行>>
- [ ] **AC-N4（manifest/PerMonitorV2 与提交恢复）**：发布 manifest 实际启用 PerMonitorV2（读实际 exe manifest 断言，不只看 csproj）；混合 DPI 下窗口位置/大小提交与恢复正确；恢复点（分辨率/缩放/排列/主屏）在结束时逐项还原并校验。 <<PARTIAL: PerMonitorV2（app.manifest + exe 内嵌）与跨 DPI 几何保持已验；重启窗口几何持久化 → NOT_APPLICABLE（产品无实现）；恢复点按用户决定保留原生 2K>>
- [ ] **AC-N5（证据/审查/翻转）**：真实桌面截图（每案例 ≥1，含两块屏与窗口位置）+ 逐案例 JSON + 恢复点 JSON + 失败/跳过原因；独立上下文 Review；`FEA-07` AC5 行 append-only 从 `NOT_APPLICABLE` 翻 `[x] <<PARTIAL: 证据/工具齐；r1 Review changes_requested 已处置，r2 复审未完成>>

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
## 覆盖补齐与复判（2026-11-09，r1 Review 后）

### 混合 DPI 矩阵（7 组，真实 OS 鼠标拖动）
| 2K / 4K 缩放 | 2K 窗口 | 拖到 4K 后 | DPI | contained |
|---|---|---|---|---|
| 100 / 150 | 1408×792 | 2112×1188 | 96→144 | 是 |
| 100 / 125 | 1408×792 | 1760×990 | 96→120 | 是 |
| 100 / 200 | 1408×792 | 2816×1584 | 96→192 | 是 |
| 150 / 200 | 1558×792 | 2077×1056 | 144→192 | 是 |
| 100 / 175 | 1408×792 | 2464×1386 | 96→168 | 是 |
| 100 / 100 | 1408×792 | 1408×792 | 96→96 | 是 |
| 125 / 150 | 1408×792 | 1690×950 | 120→144 | 是 |

- 覆盖 4K 100/125/150/175/200 与 2K 100/125/150 的组合子集（7/15）；未做组合记 `NOT_RUN`，不写 MET。
- 证据：`evidence/matrix-summary.json`、`evidence/screenshots/*drag*.png`。

### 拔屏（OS 级）
- 第 1 次 `/internal` 3.5s 内未生效（`undock-os-20261109-093255.json`：仍有 2 屏、窗口未回主屏）→ **如实保留失败**；第 2 次成功（`...093322.json`）：窗口 (703,134) 1728×972@100%、完全在主屏内、进程存活。
- 物理拔线未做（`NOT_RUN`）；未 flush 编辑态 fail-closed 未做（`NOT_RUN`）。

### 窗口几何持久化（P1-03 处置）
- `evidence/window-persistence-20261109-101115.json`：移到 4K (3600,300) 2700×1500 → 关闭 → 重开，窗口未恢复（默认 (208,208) 1116×799）。
- 全仓无窗口几何持久化实现 ⇒ 该子项 `NOT_APPLICABLE: 产品未实现窗口几何持久化`；跨 DPI 几何保持已由 7 组拖动覆盖。

### 实际 exe manifest（P2-01 处置）
- `evidence/exe-manifest.txt`：exe sha256 `1bfd0f40…`，内嵌 manifest 含 `dpiAware true/pm` + `dpiAwareness PerMonitorV2`。

### 恢复点（P1-04 处置）
- 用户 2026-11-09 决定**保留 AOC 原生 2560×1440**；缩放已恢复 2K 100% / 4K 150%；原始状态 JSON 保留可回滚。

### AC 复判（不写成 MET 的子项）
- **AC-N1**：`PARTIAL` —— 7/15 组合 + DPI 切换 + contained；「无模糊/无错位」无客观断言。
- **AC-N2**：`PARTIAL/NA` —— 主窗归属/可见/contained 已验；Inspector 浮窗不存在（`RegisterSecondary` 零生产调用）→ 子项 NA；可操作性/快捷键 `NOT_RUN`。
- **AC-N3**：`PARTIAL` —— OS 级拔屏已验；物理拔线、未 flush 编辑 fail-closed `NOT_RUN`。
- **AC-N4**：`PARTIAL/NA` —— PerMonitorV2（源码+exe）与跨 DPI 几何 MET；重启窗口持久化 NA；恢复点按用户决定保留原生 2K。
- **AC-N5**：`PARTIAL` —— 证据齐；r1 changes_requested 处置已落，r2 待审。

### 限制
- Inspector 浮窗不存在；未 flush 编辑态、原生 IME、换主屏、全屏、物理拔线：`NOT_RUN`。
- 缩放切换依赖 Windows 设置 UI 自动化（`SET_DPI_SCALE` rc=87；注册表广播无效）。
- 本卡 `closed_with_limitations`：**不宣称 AC5 完全实现**；`FEA-07` AC5 行保持 `[x] <<NOT_APPLICABLE: ...>>`，理由按 ADJ §7.17 收窄。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-AC5-02 | AC-N1/N2/N3 | verification/FEA-07-AC5-NATIVE-1/evidence/matrix-summary.json | 0bcdeb9fc | 886d86e2b7920a797f5436d658e0d52def222d0737edc4810da8750dfd9b264a | CANONICAL |
| EV-AC5-03 | AC-N3 | verification/FEA-07-AC5-NATIVE-1/evidence/undock-os-20261109-093322.json | 0bcdeb9fc | 03b829e1c32629a8552080406f83ef245133e42750f5bd1d1ac1f6efe150f5b2 | CANONICAL |
| EV-AC5-04 | AC-N4 | verification/FEA-07-AC5-NATIVE-1/evidence/exe-manifest.txt | - | 6585d60816068d1f0f89be7fce6f868d87c7233fa08013b51e7cd87a14dc158a | CANONICAL |
| EV-AC5-05 | AC-N4 | verification/FEA-07-AC5-NATIVE-1/evidence/window-persistence-20261109-101115.json | - | 49465a71c57713c5c97ed1be934f610760524f48d2991a8298bc3af8d42e3556 | CANONICAL |
| EV-AC5-06 | AC-N5 | verification/FEA-07-AC5-NATIVE-1/README.md | 0bcdeb9fc | 4aec163ec936e192d7a7989634da03e3d6224bcf4d4bd52d0c155aafcea3f15e | CANONICAL |

| EV-AC5-P01 | 过程记录 | verification/FEA-07-AC5-NATIVE-1/evidence/display-state-before-native-20261109-084020.json | - | 2482237f8a64d272fbd29ecec127011f6851d0c50ffab562a07a94cd2d5b626c | CANONICAL |
| EV-AC5-P02 | 过程记录 | verification/FEA-07-AC5-NATIVE-1/evidence/display-state-after-aoc-native-20261109-084031.json | - | b38d7962e0412e3f66229eb67a903efd9a4a58ca511ab26821ee823335064b34 | CANONICAL |
| EV-AC5-P03 | 过程记录 | verification/FEA-07-AC5-NATIVE-1/evidence/display-state-truth-check-20261109-092900.json | - | 81251e2ebd306103593d08cc04b41458f8acc3cc435e008726527a26c0b53697 | CANONICAL |
| EV-AC5-P04 | 过程记录 | verification/FEA-07-AC5-NATIVE-1/evidence/display-state-after-100-20261109-092913.json | - | 5690e89461c6a26a42da2f56453ece9f08211cd89098ff6ce6b5daa4441ac5be | CANONICAL |
| EV-AC5-P05 | 过程记录 | verification/FEA-07-AC5-NATIVE-1/evidence/display-state-after-undock-20261109-093308.json | - | 8fcfc0cd821171f4e420ad54785fe73c5c9595edbcc841b50737f183c9d22bce | CANONICAL |
| EV-AC5-P06 | 过程记录 | verification/FEA-07-AC5-NATIVE-1/evidence/display-state-after-undock2-20261109-093337.json | - | 8e8dfcac5320f3114123436e67be1b4bc3c00dd8724f586004d9b6fc71df1a2d | CANONICAL |
| EV-AC5-P07 | 过程记录 | verification/FEA-07-AC5-NATIVE-1/evidence/displays-after-uia-125-20261109-092837.json | - | 88a68a3c033634e521d6942f109068a86761e4b80c115d974cc95df801c6401c | CANONICAL |
| EV-AC5-P08 | 过程记录 | verification/FEA-07-AC5-NATIVE-1/evidence/displays-baseline-20261109-083908.json | - | c8d2847354640e21b8b9fb9d75ec763af88e35b43cc1f4d9f4838da1ad764476 | CANONICAL |

| EV-AC5-P01 | AC-N3（物理拔屏） | verification/FEA-07-AC5-NATIVE-1/evidence/physical-state-after-physical-unplug-20261109-102803.json | - | f313a2b72f7dac8d35bfabb7af5f2765fc7a0e7042db28fa45d8445c569a319e | CANONICAL |
| EV-AC5-P02 | AC-N3（物理拔屏） | verification/FEA-07-AC5-NATIVE-1/evidence/physical-state-after-replug-20261109-103127.json | - | 2ae901ca671f84fb33fa8b923e8ffb2213ee826a8114f51a5c5115df414c01a3 | CANONICAL |
| EV-AC5-P03 | AC-N3（物理拔屏） | verification/FEA-07-AC5-NATIVE-1/evidence/physical-state-after-unplug-restored-window-20261109-102834.json | - | 7d6a2cc54a701ba52386c1443253f7ba6df50d40b052712748ea6c9a5e1c5677 | CANONICAL |
| EV-AC5-P04 | AC-N3 / 缺陷 | verification/FEA-07-AC5-NATIVE-1/evidence/physical-unplug-before.log | - | 17b14460587876746b4d179272fb310a9f97a536b8f3ae1c403103fc19dd5c02 | CANONICAL |
| EV-AC5-P05 | AC-N3 / 缺陷 | verification/FEA-07-AC5-NATIVE-1/DEFECTS.md | - | 0713df0828b05dd54d36eb2048b525a4158e7dd8e7d83d19d1d1e0031facf886 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main；base `b6cd53260`） | NOT_APPLICABLE | — | — | 未创建 worktree |
| temp | `%TEMP%\nm-fea07-*`（应用隔离根/截图中转） | NOT_APPLICABLE | — | — | 关闭应用后由 OS 清理；不触真实书籍/DB |
| display-settings | 2K/4K 模式与缩放（临时切换） | NOT_APPLICABLE | 2K 100% / 4K 150%；AOC 保留原生 2560×1440（用户决定） | NOT_APPLICABLE | 每次切换有 before/after DPI 采样；恢复点 `verification/FEA-07-AC5-NATIVE-1/evidence/display-state-before-native-20261109-084020.json` 保留 |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 应用均用隔离 `--data-root` |
| tracked-side-effect | 无 | NOT_APPLICABLE | — | — | 无 |

## 物理拔屏与重插（2026-11-09，用户手动拔 4K 线）

| 阶段 | 拓扑 | 主窗 | 判定 |
|---|---|---|---|
| 拔屏前 | AOC 2K(主) + 4K | 4K 上 (3616,200) 2592×1458@150% | 就位 |
| 拔掉 4K | AOC 2K(主) + Mi TV 1080p | **最小化**（iconic，-32000,-32000），进程存活 | 未自动迁移（D-AC5-1） |
| 手动恢复 | 同上 | 主屏 (703,134) 1728×972@100%，完全在主屏内 | 可恢复、可用 |
| 插回 4K | AOC 2K(主) + 4K | 自动回到 4K 原几何 (3616,200) 2592×1458@150% | 恢复正确 |

- 证据：`evidence/physical-state-*.json`（4 份）、`evidence/physical-unplug-before.log`、`evidence/screenshots/*phys*.png`。
- 缺陷登记：`DEFECTS.md` **D-AC5-1**（物理移除事件下主窗被最小化而非自动迁移；OS 级 `/internal` 会自动迁移 → 产品缺口/limitation，建议 re-home 窗口管理卡）。
- 过程说明：首次 `physical-unplug-probe.ps1` 因用户拔线晚于脚本 240s 等待窗口而超时（未产出 JSON，失败日志保留）；随后用 `capture-physical-state.ps1` 直接抓取状态完成取证。
