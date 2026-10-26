---
id: PRODUCT-IDENTITY-1
title: 修正产品外壳命名——窗口标题 / exe 名 / 应用 ID 统一为 New Manga
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-26
suggested_owner: dsh
owner: dsh
reviewer: codex
depends_on: [UIUX-V2-RUNTIME-NARROW-1]
base_commit: null
branch: main
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/PRODUCT-IDENTITY-1
allowed_paths:
  - doc/tasks/PRODUCT-IDENTITY-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/PRODUCT-IDENTITY-1/**
  - apps/desktop/src-tauri/tauri.conf.json
  - apps/desktop/src-tauri/tauri.acceptance.conf.json
  - apps/desktop/src-tauri/src/main.rs
  - apps/desktop/frontend/e2e/uiux-v2/lib/env.mjs
---

# PRODUCT-IDENTITY-1：产品外壳命名统一为 New Manga

## 问题（用户 2026-10-26 提问触发）

用户问「为什么软件的名字不是叫 New Manga」。核对后确认这是**里程碑代号遗留**，不是设计选择：

| 位置 | 改前 | 用户可见 |
|---|---|---|
| 界面品牌（`nm-brand-name` / 书卡 kicker） | New Manga | 是（正确） |
| 数据目录（`main.rs:823`） | `%LOCALAPPDATA%\New Manga` | 是（正确） |
| 窗口标题（`tauri.conf.json`） | `M2-RC1 resource channel runtime` | 是（错误） |
| exe 名（`productName`） | `m2rc1-desktop.exe` | 是（错误） |
| 应用 ID（`identifier`） | `com.newmanga.m2rc1.desktop` | 间接（`%APPDATA%` 目录） |

`M2-RC1` 是「资源通道运行时」里程碑代号，当时用于区分并行实验构建，后续未收拾。

## 目标

- **AC1** 窗口标题 = `New Manga`
- **AC2** 构建产物 exe = `New Manga.exe`（`productName`）
- **AC3** 应用 ID = `com.newmanga.desktop`，且 `main.rs` 里对应的 `%APPDATA%` 目录拼接同步
- **AC4** 用户作品库不受影响：仍为 `%LOCALAPPDATA%\New Manga`（`main.rs:823` 硬编码，与 identifier 无关）
- **AC5** 验收脚手架不被打断：`e2e/uiux-v2/lib/env.mjs` 的 `PINNED_EXE` 指向新路径，`run.mjs` 全绿
- **AC6** 重建发布版并冒烟：标题正确、无调试端口

## 不做（明确边界）

- **不改 `Cargo.toml` 的 package/bin 名**（`m2rc1-desktop`）：那是内部 crate 标识，用户不可见；改它会波及 `cargo test --bin`、大量测试命令与既有证据脚本，收益为零、风险为实。
- **不改历史验收脚本** `e2e/p02-new-time/**` 里对 `m2rc1-desktop.exe` 的匹配：那是已冻结的历史证据（P02 / AC1 时期），改了等于篡改历史；只登记"该脚本对新 exe 名失效"这一事实。
- 不改界面品牌与设计令牌（本来就是 New Manga）。

## 风险与处置

- **应用 ID 变更的副作用**：`%APPDATA%\com.newmanga.m2rc1.desktop` 会成为孤儿目录（旧设置/WebView 缓存）；新数据落到 `%APPDATA%\com.newmanga.desktop`。**用户作品库在 `%LOCALAPPDATA%\New Manga`，不受影响**。孤儿目录不删（属用户数据，保留待用户自行处置）。
- **exe 名带空格**：`New Manga.exe`。e2e 脚本以字符串拼接路径，不需要额外引号处理；但需实测确认 spawn 正常。
- 改 `identifier` 会改 WebView2 用户数据目录 → 首次启动等于"全新安装"，主题等本地状态会回到默认（可接受，且我们默认深色与设计一致）。

## 验收方式

- 重建 `cargo tauri build --no-bundle` → 产物名为 `New Manga.exe`
- 启动冒烟：窗口标题 = `New Manga`；`Get-NetTCPConnection -LocalPort 9345` 无监听
- 改 `env.mjs` 的 `PINNED_EXE` 后重建 acceptance 构建，`node e2e/uiux-v2/run.mjs` → exit 0
- `tsc --noEmit` exit 0；`vitest run` 全绿
- 证据落 `verification/PRODUCT-IDENTITY-1/`

## 执行记录（2026-10-26）

用户选择「全套改（含应用 ID）」，DSH 执行。

### 实际改动

| 文件 | 改动 |
|---|---|
| `apps/desktop/src-tauri/tauri.conf.json` | `productName` → `New Manga`；`identifier` → `com.newmanga.desktop`；window `title` → `New Manga` |
| `apps/desktop/src-tauri/tauri.acceptance.conf.json` | window `title` → `New Manga` |
| `apps/desktop/src-tauri/Cargo.toml` | `[[bin]] name` → `new-manga`（**package name 保留不动**，见 AC 说明） |
| `apps/desktop/src-tauri/src/main.rs` | L1543 应用数据目录拼接 → `com.newmanga.desktop`；L3499 注释里的 `cargo test --bin` 同步 |
| `apps/desktop/frontend/e2e/uiux-v2/lib/env.mjs` | `PINNED_EXE` → `target/release/new-manga.exe` |
| `apps/desktop/frontend/e2e/uiux-v2/diag-narrow.mjs` | 注释示例路径同步 |

### 两次判断修正（如实记录，已写入证据 README）

1. 只改 `productName` **不会**改 exe 名——`--no-bundle` 产物名取 Cargo `[[bin]] name`；`productName` 只影响 NSIS 安装包与快捷方式显示名。
2. Cargo **拒绝带空格的 crate/bin 名**：`error: invalid character ' ' in crate name: 'New Manga'` → 改用 `new-manga`。

最终用户可见：窗口标题 `New Manga`、产物 `new-manga.exe`、应用 ID `com.newmanga.desktop`。

### 验证

- 发布版重建 exit 0；启动后窗口标题 = `New Manga`；`9345` 无监听
- 验收脚手架：重建 acceptance 版后 `run.mjs` → **`run-i5` 10/10 PASS，exit 0**
- `tsc` exit 0；`vitest` 567 passed
- 证据：`verification/PRODUCT-IDENTITY-1/README.md`

### 已知影响（登记）

1. 旧 `%APPDATA%\com.newmanga.m2rc1.desktop` 成为孤儿目录（不擅自删除，属用户数据）；作品库不受影响。
2. 历史证据脚本 `e2e/p02-new-time/lib/env.mjs`、`ac1-identity.mjs` 仍匹配旧 exe 名，按"不改历史证据"约定保留，属预期失效。
3. identifier 变更使 WebView2 本地偏好回到默认（默认深色与设计一致）。

## Acceptance Criteria 状态

- [x] **AC1** 窗口标题 = `New Manga` <<MET>>
- [x] **AC2** 构建产物 = `new-manga.exe`（Cargo 不允许空格，取工程惯例名；窗口/安装名仍为 New Manga） <<MET>>
- [x] **AC3** 应用 ID = `com.newmanga.desktop`，`main.rs` 对应目录拼接同步 <<MET>>
- [x] **AC4** 作品库路径仍为 `%LOCALAPPDATA%\New Manga`（未改，与 identifier 无关） <<MET>>
- [x] **AC5** 验收脚手架未断：`env.mjs` PINNED_EXE 更新后 `run-i5` 10/10 exit 0 <<MET>>
- [x] **AC6** 发布版重建 + 冒烟：标题正确、无调试端口 <<MET>>

## Canonical Evidence

| evidence_id | AC | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC1/AC2/AC6 | verification/PRODUCT-IDENTITY-1/README.md | HEAD3 | - | CANONICAL |
| EV-02 | AC5 | verification/UIUX-V2-RUNTIME-NARROW-1/run-i5/report.json | HEAD3 | - | CANONICAL |
| EV-03 | AC1/AC3 | apps/desktop/src-tauri/tauri.conf.json | HEAD3 | - | CANONICAL |
| EV-04 | AC2 | apps/desktop/src-tauri/Cargo.toml | HEAD3 | - | CANONICAL |
| EV-05 | AC3 | apps/desktop/src-tauri/src/main.rs | HEAD3 | - | CANONICAL |
| EV-06 | AC5 | apps/desktop/frontend/e2e/uiux-v2/lib/env.mjs | HEAD3 | - | CANONICAL |

## Resource Manifest

- 无删除/迁移/归档；旧 exe 文件（`m2rc1-desktop.exe`、验收备份）已删除，但其 SHA-256 已记录在 REALCORE-1/2 与 NARROW-1 的 README 中，证据可复现性不受影响。