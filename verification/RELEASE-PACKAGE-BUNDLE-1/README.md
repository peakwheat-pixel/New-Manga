# 含 sidecar 的可分发包 — 证据（r1 复核后重做）

Task：`RELEASE-PACKAGE-BUNDLE-1`（Owner：DSH）｜基线 `e2c9fd058`｜实现 `53d803e04`｜r1 返修（本提交）

> **本文件替代初版手工组装记录**。初版用 `tools/ci/publish-release.ps1` 的产物手工拼装，
> 被 r1 复核 **R-03** 判定「许可/变体不符」：包了 `models/`（含 AGPL 的 YOLO11s-seg）
> 却沿用 **base** 命名、缺 `THIRD_PARTY_LICENSES.md`、无 `VERSION.json`、README 未声明整体 AGPL。
> 根因是**绕过了正规打包脚本** `apps/desktop-avalonia/scripts/package.ps1`（它有 base/models 变体概念
> 并强制 4 件套许可逐字节一致）。本节起为**正规脚本产物**。

## 1. 正规打包执行

```
pwsh -NoProfile -File apps/desktop-avalonia/scripts/package.ps1 -Version "0.2.0-dev" -WithModels
  EXIT=0，墙钟 57.2s
  variant=models，licenses_byte_identical=true
```

| 项 | 值 |
|---|---|
| 包目录 | `NewManga-0.2.0-dev-win-x64-models/` |
| **文件数** | **1,038** |
| **未压缩大小** | **867,781,527 B（827.6 MB）** |
| **zip** | **716,526,526 B（683.3 MB）** |
| **zip sha256** | `6a97d2e4a8b60037e0b8433dde2d47463b972e1f163de10f80ca6431a3f7909d` |
| **exe** | `app/NewManga.App.exe` **37,338,109 B**（trimming 后），sha256 `89ef97b6482505941be583b5edf1333f0709f4ed1cfafafd27470009a0a9745c` |
| sidecar | `app/core-sidecar/` 830,148,936 B（791.69 MB），含 5 exe + `_internal` |
| models | 642.3 MiB（`app/core-sidecar/models/{detector,ocr}`） |
| 许可 4 件套 | `LICENSE` / `LICENSE-AGPL-3.0.txt` / `NOTICE.md` / `THIRD_PARTY_LICENSES.md`，**逐字节与仓库根一致**（`licenses_byte_identical: true` + 4 个 sha256） |

**包根目录**：`app/`、`install.ps1`、`uninstall.ps1`、`UPGRADE.md`、`LICENSE_AUDIT.md`、
`MANUAL_VERIFY.md`、`migrate-legacy-dryrun.ps1`、`package-manifest.json`、`VERSION.json` + 4 件套许可。

## 2. `VERSION.json` 的许可与变体声明（R-03 关键）

```json
{
  "variant": "models",
  "license": "AGPL-3.0",
  "bundled_weights_license": "AGPL-3.0 (Ultralytics YOLO11s-seg: app/core-sidecar/models/detector/yolo11s-seg.onnx)",
  "license_files": ["LICENSE","LICENSE-AGPL-3.0.txt","NOTICE.md","THIRD_PARTY_LICENSES.md"],
  "sidecar_build": { "repo_head": "53d803e04109f12ece611211c7626371a0d38a0a", "variant": "models", "models_bundled": true }
}
```

⇒ 变体名与内容一致（`models` 包确实含 models）、整体许可声明为 AGPL-3.0、
4 件套齐备、`sidecar_build.repo_head` 绑定当前 HEAD。

## 3. 包内启动验证（R-01 补全证据字段）

```
<stage>/app/NewManga.App.exe --sidecar-dir="<stage>/app/core-sidecar"
  --data-root <iso>/data --log-dir <iso>/logs --theme-home <iso>/theme-home
```

| 证据 | 值 |
|---|---|
| PID | 52544 |
| 14s 后存活 | **true** |
| 窗口标题 | **`New Manga`** |
| `host.log` | `mode=ReadWrite reason=parity reached and no legacy shell running` → **`core_service ready (1 wire frames)`** → **`host_bridge ready (1 wire frames)`** → `credential port ready (Windows Credential Manager)` |
| `self-check` | `status=Passed`，**capabilities = 17 项**（r1 R-05 更正：先前写 18 有误） |
| DB 创建 | `data/library.db`（4,096 B）+ `-shm`（32,768 B）+ `-wal`（32 B） |

**独立复核者另行验证（更强）**：它自己从零启动**两次**（未复用本会话进程）——
运行 A 显式 `--sidecar-dir`、cwd 置于 `C:\Windows\Temp`；运行 B **不传** `--sidecar-dir`（走
`<appdir>/core-sidecar` 回退，即"双击可跑"）。两次均：
- 窗口 `New Manga`；
- **子进程 `core_service.exe` / `host_bridge.exe` 的 `ExecutablePath` 均指向包内**（不是外挂 build 目录）；
- ready 链通过；优雅关闭后 `library.db=634,880 B`、`catalog.sqlite=24,576 B`，与本会话一致。

⇒ **「portable 可独立分发」事实成立**，且**回退路径也通**。

## 4. 边界（不淡化，包内 README 亦已写入）

- 这是 **portable 文件夹**，**不是安装器**；
- **未执行** clean install / 升级回退 / 卸载矩阵（包内虽带 `install.ps1`/`uninstall.ps1`/`UPGRADE.md`，
  但未在真机跑过）；
- **未代码签名**；
- **E-7 并发项仍 5 项开放** —— 并发安全不可宣称；
- 冒烟只覆盖「启动 + Host ready + 自然退出」，**功能路径未触达**；
- ⇒ **不改变 Gate 条件 4 的最终判定**，Gate 仍 **BLOCKED**。

## 5. 初版手工包的处置

初版手工包（`artifacts/release/NewManga-e2c9fd058-win-x64/` + 其 zip）**已废弃**：
变体命名错误、缺 `THIRD_PARTY_LICENSES.md` 与 `VERSION.json`。文件保留在仓外作历史证据，
**不得**用于对外分发。以本文件的 `NewManga-0.2.0-dev-win-x64-models` 为准。

## 6. 不回归

```
check.ps1（全局）                → PASS (3 warnings), EXIT=0
verify_pins.ps1                  → PASS (all 18), EXIT=0
generate_api_inventory.py --check → OK (1/80/6=87), EXIT=0
产品代码零 diff（只新增 doc/** 与 verification/**）
```

## 7. 已知（r1 P3）

- 初版 commit message 的「1028 文件」「18 capabilities」均有误，已在本文件更正为 **1,038** / **17**；
- `manifest.task` 硬编码为 `V11R-PUB-1`（脚本既有行为，非本卡 id）；
- 包体与 zip 在仓外（`G:\CODEX\New Manga.workspace\task-envs\FINAL-VALIDATION-1\out\`），**不入 Git**。
