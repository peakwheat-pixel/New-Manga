# INSTALLER-METADATA-CONSISTENCY-1 · 证据（2026-11-17）

# head: 7f59ae461（收口前 HEAD）
# interpreter: pwsh 7 + python 3
# command: pwsh -NoProfile -File tools/ci/verify-package-manifest.ps1 -StageDir <stage>

## AC1 复现（旧 stage 的元数据互相矛盾）

`<stage>` = `G:\CODEX\New Manga.workspace\task-envs\INSTALLER-MATRIX-1\stage\NewManga-0.1.1-win-x64`

| 项 | 实测 |
|---|---|
| `VERSION.json` | 2,518 B，sha256 `c8459587974b028f30bcdd8048764b00fbdd734159a1e03a96f292de6eb78fd9` |
| `package-manifest.json` | 381,448 B，sha256 `68752b31fdc7ca62edf0cd8708dc70ac6c4f74040185fa0695e85ea4a8744b1c` |
| manifest mtime | **2026-10-28 13:16:59** |
| stage 其余文件 mtime | **2026-11-15**（`VERSION.json` 04:57:47、`NewManga.App.exe` 04:56:57） |
| 根 `VERSION.json` vs `app/VERSION.json` | **哈希不同**（`c8459587…` vs `5a8c6abf…`）——脚本本应逐字节复制 |

| 字段 | `VERSION.json` | `package-manifest.json` | 判定 |
|---|---|---|---|
| version | **0.1.1** | **0.1.0** | MISMATCH |
| variant | base | base | ok |
| models | 文本声明 BUNDLED（603.2 MB） | `models_bundled: false`、`models_bytes: 0` | MISMATCH |
| 实物 | 3 个 .onnx / **632,552,582 B** | 0 | MISMATCH |
| files | — | 1,968 | 实物 1,037 |

**结论**：这个 stage **不是 `package.ps1` 的干净输出** —— manifest 是 10-28 的旧文件（未被重新生成），根/`app` 两个 `VERSION.json` 不一致（说明被手工改过），
且旧 manifest 甚至描述了一个**包含 `app/core-sidecar/python/*`** 的包（当前 stage 没有这些文件）。

## AC2 根因（`apps/desktop-avalonia/scripts/package.ps1`）

| 行 | 事实 |
|---|---|
| 3 | `[string]$Version='0.1.0'` —— 版本是**参数默认值**，不参与「与实际产物对账」 |
| 17-18 | `$variant`/`$stageName` 都由 `$WithModels`/`$Version` 推导，**没有校验 stage 目录的既有内容** |
| 73 | `if(-not $WithModels){$roboArgs+=@('/XD', models)}` —— 不带 `-WithModels` 时**不复制** models，但**不清除**已存在的 models 目录 |
| 80-81 | `$modelsBundled=(Test-Path .../models)` / `$modelsBytes=...` —— 由**磁盘现状**推导（这点是对的） |
| 157-160 | manifest 在阶段末尾由 `Get-ChildItem $stage -Recurse -File` 生成 —— **不校验 stage 是否残留旧 build** |
| 护栏缺口 | `tools/ci/verify-package-manifest.ps1` 原本**只校验 `VERSION.json`**，对 `package-manifest.json` 完全没检查（实测旧 stage 原版校验器 `OK / EXIT=0`） |

## AC3 修复（只加严，不放宽）

`tools/ci/verify-package-manifest.ps1` 增加 `package-manifest.json` 交叉校验（每条都是 **failure**，不是 warning）：

1. `manifest.version == VERSION.version`
2. `manifest.variant == VERSION.variant`
3. `manifest.models_bundled == (stage 内 .onnx 数量 > 0)`
4. `manifest.models_bytes == 实测 .onnx 总字节`
5. `manifest.files` 的数量与 stage 实际文件数一致（**排除 manifest 自身** —— `package.ps1` 在写 manifest 之前枚举，这是生成器的既定语义）
6. `manifest.files` 列出的每个路径都**真实存在于 stage**

## AC4 判别力（红）：旧 stage 现在**失败**

# command: pwsh -NoProfile -File tools/ci/verify-package-manifest.ps1 -StageDir <旧 stage>
# EXIT=1
verify-package-manifest: FAILED with 5 problem(s)
  FAIL: package-manifest.json version mismatch: manifest=0.1.0 VERSION.json=0.1.1
  FAIL: package-manifest.json models_bundled mismatch: manifest=False actual=True (3 onnx files)
  FAIL: package-manifest.json models_bytes mismatch: manifest=0 actual=632552582
  FAIL: package-manifest.json lists 1968 file(s) but the stage holds 1036 (excluding the manifest itself)
  FAIL: package-manifest.json lists 1041 file(s) that are not in the stage (e.g. app/core-sidecar/python/plugin-python.sha256, ...)

> 注：原版校验器对同一 stage 输出 `OK … EXIT=0`（见上 AC2「护栏缺口」），所以这不是既有失败，而是**新增的判别力**。

## AC5 绿例（元数据一致时必须通过，证明不误报）

用**真实 exe**（发布产物，`ProductVersion` 内嵌 head `1f5832b50…`）+ 真实 `core_service.exe` 组一个 stage，
元数据按实际内容生成（version/variant/models_bundled/models_bytes/files 全部自洽）：

# command: pwsh -NoProfile -File tools/ci/verify-package-manifest.ps1 -StageDir <一致 stage>
# EXIT=0
verify-package-manifest: OK (exe, core_service, 0 onnx / 0 B all match VERSION.json)

**边界**：这是「一致元数据」的绿例，**不是** `package.ps1` 的完整重跑（完整重跑需要 clean worktree + ~1.4 GB sidecar 复制 + 800 MB zip，本轮未做）。

## AC6 不越界

- **未覆盖** `INSTALLER-MATRIX-1` 的 stage / `setup.exe` / 任何 `verification/**` 既有字节（旧 stage 只读）。
- 未改 `packaging/nsis/installer.nsi`。
- 未改许可证声明（属 `L-IM-7`，另需书面裁决）。
- 未改变任何 Gate 判定。
