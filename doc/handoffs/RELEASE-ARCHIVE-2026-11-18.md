# 发布产物归档记录（2026-11-18，DSH）

## 结论：最终产品现在在这里

**`G:\CODEX\New Manga.workspace\artifacts\release\v0.1.1-2026-11-18-GPL\`**

| 文件 | 字节 | sha256 |
|---|---|---|
| `NewManga-0.1.1-setup.exe` | 652,081,157 | `3c9984b21d663a9ec9a8890387e5800df7d85a3005ed66f0231c67653751df05` |
| `NewManga-0.1.1-win-x64-models.zip` | 680,542,141 | `b9adfe9f2e3627977514f05b945caf8ee08f3dbbb2d07e5869a0d074a40333e4` |
| `SHA256SUMS` | 193 | — |
| `RELEASE-MANIFEST.json` | 1,530 | — |

`RELEASE-MANIFEST.json` 记录：`version=0.1.1`、`variant=models`、`license=GPL-3.0-or-later`、
`signed=false`、`authenticode=NotSigned`、`models_bundled_bytes=632,552,582`、
`app_exe`（37,344,576 B + sha256）、两个文件的字节与 sha256、`gate_status`
（`Technical Gate=NOT_SATISFIED`、`Release Gate=BLOCKED`、`condition_4=closed_with_limitations`）。

## 归档方式（只新增，不删除）

1. **复制**（非移动）—— `tmp\r28\inst\` 与 `tmp\r28\pkg\` 的原件**保留在原位**，证据日志里的引用仍然有效。
2. **逐字节校验复制件**：两个文件的 `bytes` 与 `sha256` 均与源一致（`same=True`）。
3. **旧产物标注**：`artifacts\release\SUPERSEDED.md` —— 指明 2026-10-30 那批（`NewManga-0.1.1-win-x64/`、
   `...-portable.zip`、`...-setup.exe`、旧 `RELEASE-MANIFEST.json`/`SHA256SUMS`）**已作废**，
   原因是它们早于许可裁定与 `app_build`/manifest 口径修复，**过不了** `tools/ci/verify-package-manifest.ps1`。
4. **中间产物标注**：`tmp\VOID-INSTALLERS.md` —— 列出 r24/r25/r26/r27/r30 六个作废安装包及其作废原因，
   **未删除任何文件**。

## 为什么这个包是"合规的"（依据，不是自称）

- 它是 Gate 条件 4 矩阵的被测产物：`verification/RELEASE-GATE4-SIGNED-MATRIX-1/ac3-installer-build-info.json` 记录同一 sha256。
- 包内 6 份许可文件与仓库根**逐字节相同**（`ac3-clean-package-verify.log`，`RESIDUAL: none`）。
- 静默安装实测 `ExitCode=0`，装出的 `app\NewManga.App.exe` 与 stage 内**逐字节相同**（`ac3-clean-install.log`）。
- 从安装后 exe 可达四个一级页面（4 张实拍，`ac4-*.jpg`）。
- 卸载后用户数据根逐文件 sha256 **零变化**（`ac6-uninstall.log`）。
- 两轮独立复核：`doc/reviews/RELEASE-GATE4-MATRIX-REVIEW-2026-11-18.md`（首轮 `ACCEPTED_WITH_FINDINGS`，复检两条 P1 均 CLOSED）。

## 边界（必须一起读）

- **未签名**（用户 2026-11-18 裁决「本项目不需要证书」）；SmartScreen 会提示，这是设计现状，不是缺陷。
- **不代表 Release Gate 通过**：`Release Gate=BLOCKED`、`Technical Gate=NOT_SATISFIED` 未变。
- 条件 5 为 `LIMITATION_ACCEPTED`（无代表性质量基线，**不宣称准确率**）。
- 条件 2 已按 Owner 裁决「A 保持现状」关闭 —— **风险是接受，不是消除**：历史中的 `.tmp.driveupload` 与素材对象仍可被匿名枚举。
- 三项随包 ONNX 的 Apache-2.0 是**上游声明**，本仓库不做法律认定；本地 ONNX 无可读许可元数据。

## 回滚/取用

- 需要重装：直接运行归档目录里的 `setup.exe`（静默 `/S`）。
- 需要免安装：解压 `NewManga-0.1.1-win-x64-models.zip`，运行 `app\NewManga.App.exe`。
- 需要重建：`apps/desktop-avalonia/scripts/package.ps1 -Version 0.1.1 -WithModels …` 后接
  `build-installer.ps1 -StageDir <stage>`，并用 `tools/ci/verify-package-manifest.ps1` 过闸。
