# INSTALLER-METADATA-CONSISTENCY-1 · 证据（2026-11-17）

# head: 7f59ae461（收口前 HEAD）
# interpreter: pwsh 7 + python 3
# command: pwsh -NoProfile -File tools/ci/verify-package-manifest.ps1 -StageDir <stage>

## AC1 复现（旧 stage 的元数据互相矛盾）

> **2026-11-17 更正（reviewer-imc F-01）**：本文件初版把「`VERSION.json` 无 `models_bundled` 字段」写成了结论 —— **那是错的**。
> 该文件实际含 `models_bundled=true`、`models_bundled_bytes=632552582`，与实物一致。原因是采集脚本硬编码了结论。
> 下面是**重新生成**的实测（`ac1-inconsistency.json/.log`，全部取自文件本体）。

`<stage>` = `G:\CODEX\New Manga.workspace\task-envs\INSTALLER-MATRIX-1\stage\NewManga-0.1.1-win-x64`

| 项 | 实测 |
|---|---|
| `VERSION.json` | 2,518 B，sha256 `c8459587974b028f30bcdd8048764b00fbdd734159a1e03a96f292de6eb78fd9` |
| `app/VERSION.json` | sha256 `5a8c6abf4330f57d4ecb34f74a92e2c259971e058c0a76710d7fcdee3f7fce67`（**与根不同**；脚本本应逐字节复制） |
| `package-manifest.json` | 381,448 B，sha256 `68752b31fdc7ca62edf0cd8708dc70ac6c4f74040185fa0695e85ea4a8744b1c`，**mtime 2026-10-28 13:16:59** |
| stage 文件 mtime 分布 | 2026-10-27: 9 个；2026-10-28: 11 个；**2026-11-15: 1,017 个** |
| 实物 .onnx | **3 个 / 632,552,582 B**；`VERSION.json` 的 `models_bundled=true`、`models_bundled_bytes=632552582` 与实物**一致** |

| 字段 | `VERSION.json` | `package-manifest.json` | 判定 |
|---|---|---|---|
| version | 0.1.1 | 0.1.0 | **MISMATCH** |
| variant | base | base | MATCH |
| models_bundled | true | false | **MISMATCH** |
| models_bytes | 632,552,582 | 0 | **MISMATCH** |
| file_count | 1,036（排除 manifest 自身） | 1,968 | **MISMATCH** |

- manifest 列出但 stage 不存在：**1,041** 条；stage 存在但 manifest 未列：**109** 条；
- manifest 里含 `app/core-sidecar/python/` 的条目：**1,010** 条（当前 stage 没有该目录）。

**结论**：`VERSION.json` 自身与实物**一致**；不一致的是 **`package-manifest.json`（2026-10-28 旧文件，未被重新生成）**，
它描述的是另一套含 `app/core-sidecar/python/*` 的布局；根/`app` 两份 `VERSION.json` 哈希不同说明有人改过其中一份。

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
5. `manifest.files` 数量与 stage 实际文件数一致（**排除 manifest 自身** —— `package.ps1:157` 先枚举、`:160` 后写 manifest）
6. 文件集**集合相等**（双向：列出的必须存在、存在的必须列出）—— reviewer-imc F-06 加严
7. 每个条目的 `bytes` 与 `sha256` 与实物**逐文件**一致 —— reviewer-imc F-05 加严
8. 重复条目检测 —— F-06 加严
9. `-StageDir` 末尾分隔符归一化 —— F-04 修正

**修复形态说明（F-08）**：不是改 `package.ps1` 内的断言，而是**发布护栏**；该校验器由 `build-installer.ps1:152`（不是 `:151`）以
「refusing to build the installer」方式调用，所以新检查会**在打包前阻断**。生成器本身的字段缺口见限制 2。

## AC4 判别力（红）：旧 stage 现在**失败**

# command: pwsh -NoProfile -File tools/ci/verify-package-manifest.ps1 -StageDir <旧 stage>
# EXIT=1
verify-package-manifest: FAILED with 8 problem(s)
  FAIL: package-manifest.json version mismatch: manifest=0.1.0 VERSION.json=0.1.1
  FAIL: package-manifest.json models_bundled mismatch: manifest=False actual=True (3 onnx files)
  FAIL: package-manifest.json models_bytes mismatch: manifest=0 actual=632552582
  FAIL: package-manifest.json lists 1968 file(s) but the stage holds 1036 (excluding the manifest itself)
  FAIL: package-manifest.json lists 1041 file(s) that are not in the stage (e.g. app/core-sidecar/python/...)
  FAIL: package-manifest.json does not list 109 file(s) present in the stage (e.g. app/core-sidecar/_internal/...)
  FAIL: package-manifest.json bytes mismatch …（逐文件）
  FAIL: package-manifest.json sha256 mismatch …（逐文件）

**微测（新增检查各自的判别力）**：
- F-05 同尺寸改内容：把 `core_service.exe` 首字节取反（大小不变）→ `package-manifest.json sha256 mismatch for 1 file(s)`（见 `ac4c-f05-sha256-swap.log`）；
- F-06 重复条目：manifest 里重复一条 → `repeats 1 path(s)` + 数量不符（见 `ac4d-f06-duplicate-entry.log`）；
- F-04 路径归一化：`-StageDir` 带尾部反斜杠时，一致 stage 仍 `OK / EXIT=0`（见 `ac5-green-consistent-stage.log`，该次即带尾部 `\`）。

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

## F-02（reviewer-imc，P1）：生成器与护栏的字段不闭合

`package.ps1:141-151` 写 `VERSION.json` 时**不写顶层 `models_bundled` / `models_bundled_bytes`**（只在 `:95` 的 `sidecar_build` 里）；
而护栏要求顶层字段存在，缺了就 FAIL，且 `build-installer.ps1:152` 是 fail-closed、CI（`build-release.yml:104→112`）串联无补字段步骤。
⇒ **干净 `package.ps1` 产物即使 manifest 完全自洽，也会被护栏拒绝**。所以 AC5 的「重建后通过」在现码下不可达。
已开后续卡 `PACKAGE-VERSION-JSON-DERIVED-1` 处理（让 `package.ps1` 由磁盘推导写出这两个顶层字段）。
- 未改 `packaging/nsis/installer.nsi`。
- 未改许可证声明（属 `L-IM-7`，另需书面裁决）。
- 未改变任何 Gate 判定。
