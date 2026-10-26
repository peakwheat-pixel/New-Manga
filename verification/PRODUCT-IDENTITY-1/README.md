# PRODUCT-IDENTITY-1 — 证据

日期：2026-10-26
触发：用户问「为什么软件的名字不是叫 New Manga」
授权：用户选择「全套改（含应用 ID）」

## 改前 / 改后

| 位置 | 改前 | 改后 | 用户可见 |
|---|---|---|---|
| 界面品牌（`nm-brand-name`、书卡 kicker） | New Manga | New Manga（未动） | 是 |
| 作品库目录（`main.rs:823` 硬编码） | `%LOCALAPPDATA%\New Manga` | **未动** | 是 |
| 窗口标题（`tauri.conf.json`） | `M2-RC1 resource channel runtime` | **`New Manga`** | 是 |
| 构建产物 exe | `m2rc1-desktop.exe` | **`new-manga.exe`** | 是 |
| 应用 ID（`identifier`） | `com.newmanga.m2rc1.desktop` | **`com.newmanga.desktop`** | 间接（`%APPDATA%`） |
| 应用数据目录拼接（`main.rs:1543`） | `com.newmanga.m2rc1.desktop` | **`com.newmanga.desktop`** | 间接 |
| Rust crate 名（`Cargo.toml [package]`） | `m2rc1-desktop` | **未改**（内部标识，用户不可见） | 否 |

## 过程中的两次判断修正（如实记录）

1. **改 `productName` 不会改 exe 名。** 第一次只改 `tauri.conf.json` 的 `productName` 为 `New Manga`，重建后产物**仍是** `m2rc1-desktop.exe`——Tauri 的 `--no-bundle` 产物名取的是 Cargo `[[bin]] name`，不是 `productName`（`productName` 影响的是 NSIS 安装包名与快捷方式显示名）。
2. **Cargo 拒绝带空格的 bin 名。** 把 `[[bin]] name` 设为 `New Manga` 后编译报错：
   `error: invalid character ' ' in crate name: 'New Manga'`
   改用工程惯例 `new-manga` → 产物 `new-manga.exe`。

用户的可见面因此是：**窗口标题 = New Manga**、**安装后快捷方式/安装包 = New Manga**、**exe 文件名 = new-manga.exe**（无空格，工程安全）。

## 验证结果（全部实测）

| 项 | 命令/方法 | 结果 |
|---|---|---|
| 发布版产物 | `cargo tauri build --no-bundle` | exit 0，产物 `new-manga.exe`（11.50 MB） |
| 窗口标题 | 启动后读窗口标题 | **`New Manga`**（截图 `after-rename.png`） |
| 无调试端口 | `Get-NetTCPConnection -LocalPort 9345` | 无监听（干净发布版） |
| 应用 ID | `tauri.conf.json` | `com.newmanga.desktop` |
| 验收脚手架未断 | 重建 acceptance 版 + `node e2e/uiux-v2/run.mjs` | **`run-i5` 10/10 场景 PASS，exit 0** |
| 类型检查 | `tsc --noEmit` | exit 0 |
| 单元测试 | `npx vitest run` | **567 passed / 60 files** |

## 已知影响（登记，不阻塞）

1. **孤儿数据目录**：旧的 `%APPDATA%\com.newmanga.m2rc1.desktop`（旧设置 / WebView 缓存）不会被自动迁移或删除。新数据落到 `%APPDATA%\com.newmanga.desktop`。**作品库不受影响**（在 `%LOCALAPPDATA%\New Manga`，与 identifier 无关）。孤儿目录属用户数据，按项目规则不擅自删除。
2. **历史证据脚本失效**：`e2e/p02-new-time/lib/env.mjs`、`e2e/p02-new-time/ac1-identity.mjs` 里仍匹配 `m2rc1-desktop.exe`。它们是 P02 / AC1 时期的**冻结证据**，按本卡约定**不改**——因此这些脚本对新产物名不再适用，属预期而不是回归。
3. **首次启动状态重置**：identifier 变更后 WebView2 用户数据目录更换，主题等本地偏好回到默认（默认深色，与设计一致）。

## 截图

- `G:/CODEX/New Manga.workspace/publish/identity-smoke/after-rename.png`（标题栏 = New Manga，Core 在线）
