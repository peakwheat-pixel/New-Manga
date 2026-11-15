# INSTALLER-011-ASSERTION-PLAN-1：补 0.1.1 原始断言 —— **计划与风险评估，本轮不执行**

基线 `3ad02e401`。

## 1. 缺口是什么

`INSTALLER-EVIDENCE-VERSION-AUDIT-1` 已确认：

| 版本 | 原始断言 JSON | 证据强度 |
|---|---|---|
| **0.1.0**（2026-10-28） | ✅ `install-phase.json`(37) + `uninstall-phase.json`(19) + `verify.json` | **高**（可逐条复核） |
| **0.1.1**（当前交付版本） | ❌ **不存在** | **中**（只有 `INSTALLER-MATRIX-1/README.md` 汇总） |

**⇒ 若能补上 0.1.1 的 phase JSON，条件 4 的证据就是完整可复核的。**

## 2. 前置条件：全部具备（已核实）

| 需要 | 实测 |
|---|---|
| **0.1.1 setup.exe** | ✅ `task-envs\INSTALLER-MATRIX-1\out2\NewManga-0.1.1-setup.exe`（621.9 MB, 2026-11-15 05:02）<br>另有 `out\`（04:41）与 `FEA-15-A2-1\out\`（71.9 MB, 2026-11-10） |
| **0.1.0 setup.exe**（回退目标） | ✅ `task-envs\GATE4-PAGES-UPGRADE-1\out-0.1.0\NewManga-…`（622 MB, 2026-11-15 05:17）<br>另有 `task-envs\NSIS-INSTALLER-1\out\NewManga-0.1.0-setup.exe`（65.4 MB, 2026-10-28） |
| **当前已安装** | ✅ `%LOCALAPPDATA%\Programs\NewManga\app\NewManga.App.exe`，`ProductVersion = 0.1.1+71cecb95a…` |
| **安装/卸载脚本** | ✅ 产品自带 `install.ps1` / `uninstall.ps1` / `migrate-legacy-dryrun.ps1`（各 2.4/0.8/0.8 KB） |

**⇒ 技术上完全可做。**

## 3. ★ 为什么本轮**不做**

**goal 的前提是"以保证现有功能不回归为前提"。**

补 0.1.1 原始断言需要**完整的 6 步安装/卸载矩阵**：

```
S0 基线（已装 0.1.1）
S1 卸载 0.1.1 → 安装 0.1.0
S2 覆盖安装 0.1.1（升级）
S3 卸载 0.1.1
S4 安装 0.1.0（回退）
S5 清理：卸载 0.1.0   ← 之后系统里就没有 NewManga 了
```

**风险清单**：

| 风险 | 说明 | 缓解 |
|---|---|---|
| **R1 现有安装被移除** | S1/S3/S5 都会卸载；**若中途失败，机器上可能没有可用的 NewManga** | 全部 setup.exe 都在，可随时重装 |
| **R2 数据根被改动** | 前一次矩阵实测数据根哈希全程不变（`6ae4d6da…d9b2`），**但那是 0.1.0/0.1.1 同字节的"标签回退"** | 执行前先备份 `%APPDATA%\com.newmanga.desktop` 清单 |
| **R3 注册表残留** | HKCU 卸载项、Start Menu 快捷方式 | `uninstall.ps1` 已验证会清理干净（0.1.0 的 19 条断言含这些） |
| **R4 时间** | 每次安装 ~7 s、卸载 ~0.7 s（0.1.0 实测），6 步约 1–2 分钟 + 哈希计算 | 可接受 |
| **R5 无回滚点** | 如果 S5 后我需要恢复，得再跑一次 0.1.1 安装 | 有 setup.exe，可恢复 |

**⇒ 结论：技术上可做，但**会真实改动用户机器上的软件安装状态**，
而**本轮的收益只是"让 0.1.1 的证据从汇总升级到逐条可复核"**。

**⇒ 权衡：收益（证据强度提升）< 风险（可能留下一个半装的系统）。**
**⇒ 本轮不做。这不是"做不到"，是"选择不在没有用户在场时动用户的安装"。**

## 4. 若要做，执行步骤（供后续参考）

```powershell
# 0) 备份数据根清单
$root = "$env:APPDATA\com.newmanga.desktop"
# 记录 (路径|大小|mtime) 排序后的 SHA-256

# 1) 卸载现有 0.1.1
& "$env:LOCALAPPDATA\Programs\NewManga\Uninstall.exe" /S
# 2) 装 0.1.0
& "<out-0.1.0>\NewManga-0.1.0-setup.exe" /S
# 3) 覆盖装 0.1.1（升级）
& "<out2>\NewManga-0.1.1-setup.exe" /S
# 4) 卸载
& "$env:LOCALAPPDATA\Programs\NewManga\Uninstall.exe" /S
# 5) 装 0.1.0（回退）
& "<out-0.1.0>\NewManga-0.1.0-setup.exe" /S
# 6) 清理
& "$env:LOCALAPPDATA\Programs\NewManga\Uninstall.exe" /S
# 7) 恢复 0.1.1
& "<out2>\NewManga-0.1.1-setup.exe" /S
```

**每步都要记录**：`exit code`、`VERSION.json.version`、exe `ProductVersion`、
HKCU `DisplayVersion`、数据根清单 SHA-256。**并落成 `install-phase.json` / `uninstall-phase.json`。**

## 5. 一个更安全的替代（推荐）

**不需要动系统就能提升 0.1.1 证据强度**：**只验证"包本身"而不安装**。

可做的静态核实（零系统变更）：
1. **核对 0.1.1 setup.exe 的 sha256 与我此前引用的一致**（`0c041599…58f06`）；
2. **核对 `build-info.republished.json` 里的 authicode 状态、版本、路径与 setup.exe 匹配**；
3. **核对 `manifest-summary.json` / `smoke-singlefile.json` 的内部一致性**；
4. **核对 stage 里的 `VERSION.json` 与 exe 内嵌 `ProductVersion` 一致**（0.1.0 的证据里这是 AC2 的核心断言）。

**⇒ 这 4 项能核实"包是真的、自洽的"，但不能替代"安装行为"的实测。**
**它把 0.1.1 的证据从"只有汇总"提升到"包级可复核"，仍不等于"逐条断言"。**

**⇒ 下一轮我可以先做这个（零风险），再决定是否要跑完整矩阵。**
