# INSTALLER-EVIDENCE-VERSION-AUDIT-1：复原"AC1–AC6 只读汇总表"这一局限，核实原始 JSON

基线 `1f0d95b70`。本卡执行 `RELEASE-GATE-RE-ASSESSMENT` §9 局限 4 的自我修正：
**此前只读了 `verification/INSTALLER-MATRIX-1/README.md` 的汇总表，未逐个复核原始 JSON。**

## 1. 我查了什么

`verification/NSIS-INSTALLER-1/` 下的原始 JSON：
`install-phase.json`（17 KB）、`uninstall-phase.json`（8 KB）、`verify.json`（13 KB）。

## 2. ★ 发现：**两份证据来自不同的 run（版本不同）**

| 来源 | 版本标识 | 包名 |
|---|---|---|
| `NSIS-INSTALLER-1/install-phase.json` | `registry_display_version = **0.1.0**` | `NewManga-0.1.0-setup.exe`（`installer_exists` 断言） |
| `INSTALLER-MATRIX-1/README.md` | **0.1.1** | `NewManga-0.1.1-setup.exe` |

**⇒ 这是两次不同的打包/安装 run，不是同一份证据的两个视图。**

因此：

- `README` 说"用户数据根清单 SHA-256 前后完全一致 `6ae4d6da…`"；
- `uninstall-phase.json`（0.1.0）里的对应断言是 `data_root_durable_unchanged_*` = **`fdf52d87…`**（expected/actual 完全相同，`pass: true`）。

**两个 digest 不同 ≠ 矛盾** —— 它们是**不同版本 run 的不同基线**。
**但如果只读汇总表、把 `6ae4d6da…` 当成"当前证据"，就会引用一个不属于当前证据集的数字。**

**⇒ 我在复评 §2.1b / 交接文档 §2.1b 里引用的 `6ae4d6da…` 是 README（0.1.1）的数字；
而原始 JSON 是 0.1.0。两者都对，但**不能混为一谈**。这一点此前没说清。**

## 3. 原始 JSON 实际证明了什么（0.1.0 run，独立复核）

### 3.1 安装阶段（`install-phase.json`）

- **37 条断言全部 `pass: true`**；
- 关键几条：
  - `install_exit_code` expected `0` / actual `0` ✅
  - `installed_exe_is_gui_subsystem` expected `2 (WINDOWS_GUI)` / actual `2` ✅
  - **四个许可文件 sha256 全部逐位相符**（`LICENSE`、`LICENSE-AGPL-3.0.txt`、`NOTICE.md`、`THIRD_PARTY_LICENSES.md`）✅
  - `start_menu_shortcut_target` = `C:\Users\49745\AppData\Local\Programs\NewManga\app\NewManga.App.exe` ✅
  - `registry_display_version` `0.1.0` ✅、`registry_install_location` ✅、`registry_uninstall_string` `*Uninstall.exe*` ✅、`registry_quiet_uninstall_string` `*/S*` ✅
  - **`data_root_durable_unchanged_after_install` expected == actual `fdf52d87…`** ✅
  - **`data_root_durable_untouched_by_launch` expected == actual `fdf52d87…`** ✅
  - `app_host_ready` = `host.log core_service ready + host_bridge ready`（elapsed 2.48 s）✅
  - `app_main_window` = 非零 handle `19730986`，`title='New Manga'` ✅

### 3.2 卸载阶段（`uninstall-phase.json`）

- **19 条断言全部 `pass: true`**；
- 关键几条：
  - `uninstall_exit_code` `0` ✅
  - `install_dir_removed` / `start_menu_shortcut_removed` / `start_menu_dir_removed` / `uninstall_key_removed` / `app_reg_key_removed` 全部 ✅
  - **`hk_hklm_uninstall_absent_after`** / **`program_files_absent_after`** ✅（未污染机器级位置）
  - `uninstall_log_complete` = `uninstall_complete=1` ✅
  - **`data_root_durable_unchanged_after_uninstall` expected == actual `fdf52d87…`** ✅
  - **`reinstall_exit_code` `0`**、`reinstall_app_sha_matches` `9aeeb5ed…` ✅ —— **重装也验了**
  - **`data_root_durable_unchanged_after_reinstall`** `fdf52d87…` ✅
  - **`final_uninstall_clean`** ✅、**`data_root_durable_unchanged_final`** `fdf52d87…` ✅

**⇒ 独立复核结论：0.1.0 run 的 AC4/AC5/AC6 证据**比汇总表所呈现的更完整** ——
不仅验了安装/卸载，还验了**重装**、以及**机器级位置（HKLM / Program Files）未被污染**。

## 4. 一处必须指出的细节（诚实）

`install-phase.json` 里：

```
data_root_after_install_digest    = 44f2bfed…
data_root_after_launch_digest     = 9de15a8d…
```

**两者不同** —— 说明**应用启动会改动"非 durable"部分**（日志/缓存），
而 **`data_root_durable_*` 全程保持 `fdf52d87…` 不变**。

**⇒ 这正是正确的语义**：durable（用户真实数据）不受影响，易失部分（日志等）可以变。
**我此前引用"用户数据根 SHA-256 前后完全一致"时没有区分这两个层级**，措辞不够精确。

## 5. 对 Gate 的影响

**不改变判定**（条件 4 仍 PARTIAL，AC7 未做），但**提高了该判定的证据强度**：

| 此前 | 现在 |
|---|---|
| 只读汇总表；`6ae4d6da…` 未核实 | 逐个读了原始 JSON；确认 **0.1.0 run 的 56 条断言全 pass**；并**发现两份证据版本不同** |
| 说"用户数据根 SHA-256 前后完全一致" | **精确化**：`data_root_durable` 全程不变；`data_root`（含日志等易失部分）会变 |

## 6. 未做

- **未复核 `INSTALLER-MATRIX-1` 那一轮（0.1.1）的原始 JSON** —— 我只找到 README 与 `build-info.republished.json`、
  `publish-manifest.republished.json`、两个 `.log`，**没有找到对应的 `install-phase.json`/`uninstall-phase.json`**。
  **⇒ 0.1.1 那轮的原始断言数据在仓库里可能不存在**，只有汇总表。
  **这是需要后续确认的缺口**（若只有汇总表而无原始数据，则 0.1.1 的 AC1–AC6 证据强度低于 0.1.0）。
- 未复核 `verify.json`（13 KB）。