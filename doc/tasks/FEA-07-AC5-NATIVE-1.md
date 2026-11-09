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
- [ ] **AC-N2（浮动窗口归属）**：Inspector 浮窗置于副屏 → 可见/可操作；主窗与浮窗跨屏拖动不丢屏外；目标屏不支持浮动时安全停靠（回主窗）；快捷键不重复执行。 <<PARTIAL: 主窗跨屏归属/可见/contained 已验；Inspector 浮窗不存在（RegisterSecondary 零生产调用）→ 该子项 NOT_APPLICABLE；中文 IME 组合输入已验（命令面板输入「你好」）；快捷键「不重复执行」未单独断言>>
- [ ] **AC-N3（拔屏/换主屏）**：OS 级禁用副屏（并尽量物理拔线）→ 第二窗口内容回主窗对应页面；未 flush 编辑态 fail-closed 留在主窗缓冲（不丢不覆盖）；换主屏后布局/全屏状态正确。 <<PARTIAL: OS 级拔屏（DisplaySwitch /internal）已验且自动迁移窗口；物理拔屏已执行：拔后主窗被系统最小化（需手动恢复，D-AC5-1）、恢复后回主屏、重插后自动回 4K 原几何；未 flush 编辑态 fail-closed 未执行>>
- [ ] **AC-N4（manifest/PerMonitorV2 与提交恢复）**：发布 manifest 实际启用 PerMonitorV2（读实际 exe manifest 断言，不只看 csproj）；混合 DPI 下窗口位置/大小提交与恢复正确；恢复点（分辨率/缩放/排列/主屏）在结束时逐项还原并校验。 <<PARTIAL: PerMonitorV2（app.manifest + exe 内嵌）与跨 DPI 几何保持已验；换主屏双向 rc=0 且应用存活；重启窗口几何持久化 → NOT_APPLICABLE（产品无实现）；恢复点按用户决定保留原生 2K>>
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
| EV-AC5-02 | AC-N1/N2/N3 | verification/FEA-07-AC5-NATIVE-1/evidence/matrix-summary.json | 0bcdeb9fc | ac328dd8f480f637fc246d24fa15ce8bc72fe374b611f742fa4a0cf510609a80 | CANONICAL |
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

| EV-AC5-EX01 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/extra-fullscreen-20261109-103425.json | - | 8dc8fa4c68555eacb8f09e954b4eae9d722debbdc1273e202011bd5873a1c6a9 | CANONICAL |
| EV-AC5-EX02 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/extra-fullscreen-20261109-103453.json | - | 6038a0ddbae43f0176bc31a8720654e6221ca1d284028f4cde06271cf64bb165 | CANONICAL |
| EV-AC5-EX03 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/extra-ime-20261109-103532.json | - | f03c60cdf40f50e1be371ff3a1b5bbceba0d672cc9b957bfb15cd315acbae543 | CANONICAL |
| EV-AC5-EX04 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/extra-primary-switch-20261109-103517.json | - | 5055c17af7b6121be303f6ca5982e0f4a525911395d3a5ddecd7b27d179fd5f6 | CANONICAL |
| EV-AC5-EX05 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/extra-theme-draft-unplug-20261109-103548.json | - | 031e32886b305813f79aad5b104ead4c251c5cb98666e654058bd6719cdbb2e1 | CANONICAL |
| EV-AC5-EX06 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/unsaved-edit-unplug-20261109-103628.json | - | 62bc95591d880eb61e7a775a10bbdca3440535a9f88ddb8ddfc51f245f78d324 | CANONICAL |
| EV-AC5-EX07 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/unsaved-edit-unplug-20261109-103656.json | - | b9cf4a1aefc50260b9f6b43eaf2c01877f5a2144975e2bd1c92851f4858c9c8e | CANONICAL |
| EV-AC5-EX08 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/unsaved-edit-unplug-20261109-103718.json | - | d30462a62dd9ab3afa88bc2dd0407af8ec774d732f3e6b2b3f84919df6fe1c08 | CANONICAL |
| EV-AC5-EX09 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/unsaved-edit-unplug-20261109-103745.json | - | cd4fac4740ff9f92650ebf30ce73ddff7d3f1539824d390775cf3f87d0a28bce | CANONICAL |
| EV-AC5-EX10 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-085421-mon1-back.png | - | 0e0f681aaa0f9db7cc239416f7164365d19297de06bac7ef775528821da0b03e | CANONICAL |
| EV-AC5-EX11 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-085421-mon1-before.png | - | 885d7016c5126075c99be0808c9b813d629c89820cb033f9b9d46fc8a78a4b9f | CANONICAL |
| EV-AC5-EX12 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-085421-mon1-placed.png | - | 4e1cadab36ab96af14b6d75cc02fc9d1fcca0ec6eecf7e560f86236f0893e98d | CANONICAL |
| EV-AC5-EX13 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-085421-mon2-placed.png | - | 2c549ba00b01a07de78fc1085dd4f307d8d92d2671de47bea72d4cf16f97e85f | CANONICAL |
| EV-AC5-EX14 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-085421-straddle.png | - | 293bb07348888049e68a2472bc43d6159aa0da25605417f940a7f92197832fb9 | CANONICAL |
| EV-AC5-EX15 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-085525-drag-mon1.png | - | 1769bd646a8a767267e591bd23da831d82baf1728f6364227314fb865ca57c0e | CANONICAL |
| EV-AC5-EX16 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-085525-drag-mon2.png | - | d16dc103df2c088647ee72c311fc8914317d2415cc443a0489c93b73868690f9 | CANONICAL |
| EV-AC5-EX17 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-093107-drag-mon1.png | - | 786c84b9847bf7251ff3deb45c28f0a0bbf330a74c34b10f574609457a275348 | CANONICAL |
| EV-AC5-EX18 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-093107-drag-mon2.png | - | 7a2a61a5d4470b40a6077d9f56c5ce29f8fad9524c04d38b9959de95b98699b1 | CANONICAL |
| EV-AC5-EX19 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-093132-drag-mon1.png | - | 15bed2b88c103666d5c86da9c18b8c95273754b0c98b2aaf621ecdb9c2240c61 | CANONICAL |
| EV-AC5-EX20 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-093132-drag-mon2.png | - | 4b469c67f8a549fd1293a5a3aaa823941ce22536f83e80d4c40eb9c558503db5 | CANONICAL |
| EV-AC5-EX21 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-093156-drag-mon1.png | - | cfd15509fcefa374699994c76ce1e9138279577135089e710cdeeefb3a70e4da | CANONICAL |
| EV-AC5-EX22 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-093156-drag-mon2.png | - | d313c23e3a7141bcb70c1f67a66068b1220942840fad70a309e7abda7b203ce7 | CANONICAL |
| EV-AC5-EX23 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-093255-undock-after.png | - | 5047d1d64a3ffe27b89cb0a92316abf8553ef812ee7c53f857567ccff41591f4 | CANONICAL |
| EV-AC5-EX24 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-093255-undock-before.png | - | 783950b92fb876f309c7aa2f394ff65e5975440e620053b1e7d4719671fc9a08 | CANONICAL |
| EV-AC5-EX25 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-093255-undock-restored.png | - | b9c8ae1a2a63d73c90ecd84694711ef0a8346aa97f5d24cff2d1834b1a8d50fd | CANONICAL |
| EV-AC5-EX26 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-093322-undock-after.png | - | 8c3f9ae7a4542a177a87940c55aa5588a7e0905e893d087b1337367c91e3bbbd | CANONICAL |
| EV-AC5-EX27 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-093322-undock-before.png | - | 742c71435b24d065b6fc681d44a30a5efb89b3395eda01c2db9df59b8973e4e1 | CANONICAL |
| EV-AC5-EX28 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-093322-undock-restored.png | - | 73bc3051e7892c6159559b6442d349a443493fc52a24679080b441f255a33a9a | CANONICAL |
| EV-AC5-EX29 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-100407-drag-mon1.png | - | 3e953d8457c17c572fb8191a0214b39e6bfeb577d91ede70373ab9d6c18a867b | CANONICAL |
| EV-AC5-EX30 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-100932-drag-mon1.png | - | c72d1b58b081251a30188831e562b8853e3a1ecfca10444c6adcf12ec59eba12 | CANONICAL |
| EV-AC5-EX31 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-100932-drag-mon2.png | - | d2d562b9c956959a1707c0794606fe15a47f5c86c720d15bc94ad1907bb4537c | CANONICAL |
| EV-AC5-EX32 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-100958-drag-mon1.png | - | d4f3b5f237fba4f0eac3d0555f2d8482a082026410265f33343a71faad2f40ab | CANONICAL |
| EV-AC5-EX33 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-100958-drag-mon2.png | - | 9483be596b4b3fdb6e1fe643a106cc20a3d020c3b21ac731f014af8b84d7ecf2 | CANONICAL |
| EV-AC5-EX34 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-101032-drag-mon1.png | - | 26aa4fefb96b00d7683f7ac6fc76484da010afbb7d779b7c75ebf79fe01e00ac | CANONICAL |
| EV-AC5-EX35 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-101032-drag-mon2.png | - | fa1a7975d5395f52b5dd32fabb13c98e6772eb9c6a52d0153a04bf7da2cca6ad | CANONICAL |
| EV-AC5-EX36 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-101630-mon1-back.png | - | 50c385f172705c39901e37f98f7caf3c65e0ae09913a4b8cca9a2c8777aee432 | CANONICAL |
| EV-AC5-EX37 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-101630-mon1-before.png | - | be6cc96ca475f7acf667a1f19e67a517e5140ebe1aab55548697e702f99ba0a2 | CANONICAL |
| EV-AC5-EX38 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-101630-mon1-placed.png | - | eeb99db52ee437d42a1779764af5ab16b75b0852d6685a99dade3b6b5cb3696c | CANONICAL |
| EV-AC5-EX39 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-101630-mon2-placed.png | - | 424dee0183a8a165ec959a205cd463fb7be6a36203199b4a1b58d75166ecf33a | CANONICAL |
| EV-AC5-EX40 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-101630-straddle.png | - | 74ff51d3b9a6607e3d5c68e8e75ab36b12499be395372cc1cb61eec9e2dc0e63 | CANONICAL |
| EV-AC5-EX41 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-102130-phys-on4k.png | - | 4588c52b8e9e039996723a8e83425f55ec2640489178a083712e1448cd3d7370 | CANONICAL |
| EV-AC5-EX42 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-102803-after-physical-unplug.png | - | f7615e01b22ae2a83eb63d54dd5c405ffb191e023ab6cf71a8031926168636e2 | CANONICAL |
| EV-AC5-EX43 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-102834-after-unplug-restored-window.png | - | a3b4eece709f468c0570e9e88a6759cb9b427feb0d77e1837684ea5651a0afbc | CANONICAL |
| EV-AC5-EX44 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-103127-after-replug.png | - | e8d88694df436ab94882950bfa269083c5198f7ba92931e0ea212744dd988e8b | CANONICAL |
| EV-AC5-EX45 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-103425-fullscreen-f11.png | - | b7e89f53ca59bc151f5644f151d894390a60b98b0c59754486f6038df6ac7779 | CANONICAL |
| EV-AC5-EX46 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-103425-fullscreen-max.png | - | b7e89f53ca59bc151f5644f151d894390a60b98b0c59754486f6038df6ac7779 | CANONICAL |
| EV-AC5-EX47 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-103453-fullscreen-esc.png | - | bc1f606ca307a73817d1a03a438c4edcad007726043c2f38f23ea118abaf4291 | CANONICAL |
| EV-AC5-EX48 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-103453-fullscreen-fkey.png | - | 73b4319fe5c6ba32da0f74afdd440014baa88958eaae1143c2269ae8757d16ed | CANONICAL |
| EV-AC5-EX49 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-103453-fullscreen-max.png | - | b7e89f53ca59bc151f5644f151d894390a60b98b0c59754486f6038df6ac7779 | CANONICAL |
| EV-AC5-EX50 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-103517-primary-switch-after.png | - | 0c5507f728d82d1854f3dd03189f7d1c4c8e52444f88db90a1746ed400fd71de | CANONICAL |
| EV-AC5-EX51 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-103517-primary-switch-before.png | - | 71664376dbbb0b28c958bff23887ba5631265193aad0f24e8d93de367a493ab7 | CANONICAL |
| EV-AC5-EX52 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-103532-ime-palette.png | - | 5a8fd6918233d1f125965e8ace712d6758bf1e7f31ffdce9172e94381418a033 | CANONICAL |
| EV-AC5-EX53 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-103532-ime-typed.png | - | 4ec517ad6522e45260ed37a2c54f1827908d6c095809d0f5d8f10400a9d2673f | CANONICAL |
| EV-AC5-EX54 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-103548-theme-draft-unplug-after-unplug.png | - | 417954d12197c61bb510fda39b9cb0af9a62c74e09d8f3539456ca1c07938ed0 | CANONICAL |
| EV-AC5-EX55 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-103548-theme-draft-unplug-draft.png | - | b23ab2b3a459b0c87ced2eb31639cdc1ae444cd96908aa4cceef4885169da0ba | CANONICAL |
| EV-AC5-EX56 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-103548-theme-draft-unplug-studio.png | - | 9d17f62fbf1a78cfe0aa0330dd70981868233499b3bbfb65917cc64cb0fc1268 | CANONICAL |
| EV-AC5-EX57 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-103628-unsaved-after-restore.png | - | 4d4112110f165bbfd0dc6547e649df786e4b8d72293c935630c7934622016a05 | CANONICAL |
| EV-AC5-EX58 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-103628-unsaved-after-unplug.png | - | 14dff23b6a25435a3f0933537bfe545c041eefa77920e3fa9d807f8002729a7d | CANONICAL |
| EV-AC5-EX59 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-103628-unsaved-before.png | - | 779154e1c6e064ca5cd84945d54317378e5fab501ea4134bebee33d48dddd89e | CANONICAL |
| EV-AC5-EX60 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-103656-unsaved-after-restore.png | - | 3d53122bc2f98a23003160ca3c85581cb7c89f1cef9db716b1e40f0cb3b787d0 | CANONICAL |
| EV-AC5-EX61 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-103656-unsaved-after-unplug.png | - | 492c05181433d199dd8991586360337cc1b4cd99d2e2f528b0542ea6de0764ed | CANONICAL |
| EV-AC5-EX62 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-103656-unsaved-before.png | - | 185bcbfce09e067532529518a9bdd15a894d3bb8dcf4f2684da1c96289bf557c | CANONICAL |
| EV-AC5-EX63 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-103718-unsaved-after-restore.png | - | 48409871523893a103c5facf440ec215c02e61464e624b4e2dbef274c05f2abe | CANONICAL |
| EV-AC5-EX64 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-103718-unsaved-after-unplug.png | - | cbea929a6e3fbdc89c45021c4824ed2b9ec432e65a778c033002d02ea62882f5 | CANONICAL |
| EV-AC5-EX65 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-103718-unsaved-before.png | - | 48aed862ded92fe9dde463e34714ee743430f325d3b79310564935e9307dcf7f | CANONICAL |
| EV-AC5-EX66 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-103745-unsaved-after-restore.png | - | b1b8b1e17ead502deb59d940c5dab365ca9a8d44ad4ec24fd69c3f4eb8239878 | CANONICAL |
| EV-AC5-EX67 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-103745-unsaved-after-unplug.png | - | b1812c6320c6282b41320249ff6e14d8f2e4109703040b4761cdb4e8de92857a | CANONICAL |
| EV-AC5-EX68 | 追加原生子项 | verification/FEA-07-AC5-NATIVE-1/evidence/screenshots/20261109-103745-unsaved-before.png | - | f96cc778419fa92e3a7527c45f31d03e30b8a30e22ebe523a911fc3b0e057bc6 | CANONICAL |

| EV-AC5-AT01 | 全屏尝试记录 | verification/FEA-07-AC5-NATIVE-1/evidence/attempts/seed2.log | - | 757c1f4fd40778210a0619e701858dbc31a91cecb61dad3194c66e397851ffd0 | CANONICAL |
| EV-AC5-AT02 | 全屏尝试记录 | verification/FEA-07-AC5-NATIVE-1/evidence/attempts/seed2.log.err | - | d2ea1a7a4c3f1ad3d6f9643545b44cc46c127b80495bd61b124457b08e452b39 | CANONICAL |
| EV-AC5-AT03 | 全屏尝试记录 | verification/FEA-07-AC5-NATIVE-1/evidence/attempts/seed3.log | - | 3c72196f1a8a8bb6c689360538e07cd44e6f3b87c53bc90606e32d42ac6bea7a | CANONICAL |
| EV-AC5-AT04 | 全屏尝试记录 | verification/FEA-07-AC5-NATIVE-1/evidence/attempts/seed3.log.err | - | d2ea1a7a4c3f1ad3d6f9643545b44cc46c127b80495bd61b124457b08e452b39 | CANONICAL |

| EV-AC5-FS01 | 全屏/导入尝试 | verification/FEA-07-AC5-NATIVE-1/evidence/probe-f11-20261109-112323.json | - | ac4acfc73849bbcfb6a41e8d2d3aa45f70d082060e849556afdee6e2751a8919 | CANONICAL |
| EV-AC5-FS02 | 全屏/导入尝试 | verification/FEA-07-AC5-NATIVE-1/evidence/open-immersive-20261109-111201.json | - | 48601f503603ca2f910342b41139d5848d6d1ec55634637099053d03a2781fda | CANONICAL |
| EV-AC5-FS03 | 全屏/导入尝试 | verification/FEA-07-AC5-NATIVE-1/evidence/open-immersive-20261109-111244.json | - | 984d975ac5b4c1d92e249ee620f298d5932bb7447cdaf861474e744fffbec334 | CANONICAL |
| EV-AC5-FS04 | 全屏/导入尝试 | verification/FEA-07-AC5-NATIVE-1/evidence/reader-fullscreen-20261109-111005.json | - | cb015416bb8410638d82820dbc4c2485554440d0ecf7e95c215cf3a49124ce54 | CANONICAL |
| EV-AC5-FS05 | 全屏/导入尝试 | verification/FEA-07-AC5-NATIVE-1/evidence/finish-import-20261109-110424.json | - | f7b684588ff8afb1d0cdea45c7d351aedea2858ea582fd27706291e7a05b9b9e | CANONICAL |
| EV-AC5-FS06 | 全屏/导入尝试 | verification/FEA-07-AC5-NATIVE-1/evidence/import-dialog-uia-20261109-110259.json | - | b0a79e902e64566ab9fdb5b23c9a9a048165856756a49900f43e9c2587872153 | CANONICAL |

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

## 追加原生子项（2026-11-09）

| 子项 | 方法 | 结果 |
|---|---|---|
| 中文 IME | 命令面板 Ctrl+K → 激活 `00000804` 布局 → `nihao`+空格 | ✅ 组合出「你好」（`evidence/extra-ime-*.json`） |
| 换主屏 | `CDS_SET_PRIMARY` 切 4K 主屏 → 恢复 AOC | ✅ 双向 rc=0、应用存活、几何/DPI 正确（`evidence/extra-primary-switch-*.json`） |
| 全屏切换 | 最大化按钮 + F11 + F/Esc | ⚠️ **NOT_RUN**：全屏仅 Reader 页（`ReaderWorkbenchPages.cs:2599` / `:2649`），空库无章节；F11 无效果 |
| 未 flush 编辑 + 拔屏 | 命令面板未提交输入 `draft` → `/internal` 移除第二屏 → 重读缓冲 | ✅ 缓冲保留、进程存活（`evidence/unsaved-edit-unplug-*.json`） |

- 证据：`evidence/extra-*.json`、`evidence/unsaved-edit-unplug-*.json`、`evidence/screenshots/*`（含 before/after、palette、typed、unplug）。
- 诚实性：全屏依赖真实章节内容 → `NOT_RUN`，未写 PASS。

### 全屏（Reader-only）尝试与结论

- 全屏只在 Reader 页：`ReaderWorkbenchPages.cs:2599`（`WindowState.FullScreen`）+ 热键 `Key.F:2649`；主窗 `F11` 实测无效。
- 需真实章节内容；已尝试「导入文件夹」UIA 自动化灌入合成漫画（ASCII 路径、2 话×3 页），文件夹对话框自动化多次未稳定完成（`evidence/attempts/seed*.log`）。
- 结论：**`NOT_RUN`**，不写 PASS；补齐条件 = 人工导入一个漫画文件夹（两次点击）或提供已导入库。

### 全屏（沉浸 ReaderWindow）实测结果 —— `NOT_RUN` + 缺陷候选 D-AC5-2

- 实现事实：沉浸窗口为独立 `ReaderWindow`（`ReaderWorkbenchPages.cs:2576-2602`：`SystemDecorations.None` + `WindowState.FullScreen`），入口为 Reader 页按钮/双击或应用级 `F11`（`MainWindow.TryHandleGlobalKey` → `ToggleImmersiveAsync` → `OpenImmersiveReader`）。
- 已导入真实内容（169 页）并打开 Reader 页（封面/第 1 页可见），随后尝试：
  1. **用户手动 F11**（点击画面后）→ 无窗口出现；
  2. 自动化 `SendKeys(F11)`（焦点在按钮，确认非文本框、`GetForegroundWindow` 为应用）→ 6s×200ms 轮询内无新顶层窗口；
  3. 双击页面图像 → 无沉浸窗口；
  4. 对照实验：`SendKeys(RIGHT)` 翻页后 **wire 无新 `resolve_page_resource`** ⇒ 键盘事件未送达 Reader（本会话输入路由异常）。
- wire 旁证：11:22:04–05 出现 `resolve_page_resource` + `SaveReadingProgress`（`ReaderWindow.Closed` 才 flush）⇒ 说明 F11 路径**部分执行过**（窗口创建/关闭），但未在桌面保持可见。
- 结论：**`NOT_RUN`**，不写 PASS；登记 **D-AC5-2**（沉浸全屏在本会话无法出现，疑似 `OpenImmersiveReader` 在本会话抛异常或输入未送达；需在**本地控制台会话**复现确认是环境还是产品缺陷）。
- 判定材料：`evidence/probe-f11-*.json`、`evidence/open-immersive-*.json`、`evidence/reader-fullscreen*.json`；截图含用户漫画内容，仅存仓外 `G:\CODEX\New Manga.workspace\FEA-07-AC5-NATIVE-1\ac5-fullscreen\`（哈希已记录）。
