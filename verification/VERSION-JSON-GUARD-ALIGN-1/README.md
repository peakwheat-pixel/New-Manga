# VERSION-JSON-GUARD-ALIGN-1 · 证据（2026-11-17）

# head: 45e25b9bb（收口前 HEAD）
# interpreter: pwsh 7
# command: pwsh -NoProfile -File apps/desktop-avalonia/scripts/package.ps1 -Version 0.1.1 -OutputRoot <ws> -SidecarDir <fixture> -NoTrim

## AC1 复现两处缺口（reviewer-pvd 实测 + 本卡复跑）

1. **缺 `app_build`**：改动前 `package.ps1` 的 `VERSION.json` 模板不含 `app_build`；护栏 `:63` 缺即 FAIL。
   本卡复跑（删掉 `app_build` 的同构 stage）：`FAILED with 3 problem(s)`，首条 `VERSION.json has no app_build section`（见 `ac4-red-missing-app-build.log`）。
2. **models 字节口径**：`package.ps1:81` 的 `$modelsBytes` 统计 `models/` **全部文件**（0.1.1 sidecar 实测 632,662,260 B），
   护栏只累加 `*.onnx`（632,552,582 B），差 **109,678 B**（config/vocab 等，`build_sidecar.ps1:147-169` 会复制）。

## AC2/AC3 修复

`apps/desktop-avalonia/scripts/package.ps1`：

- 新增 `$appExe` / `$appExeSha` / `$appExeBytes` / `$appHead`：
  head 取自 **exe `ProductVersion` 内嵌的 40-hex**（与护栏 `:3` 的验证口径一致），取不到才回退 `git rev-parse HEAD`；
- `VERSION.json` 模板新增 `app_build=@{exe_sha256=…;exe_bytes=…;repo_head=…}`；
- `models_bundled_bytes` 改为 **`$modelsOnnxBytes`**（只算 `*.onnx`，与护栏同口径），另存 `models_dir_bytes` 保留目录全量口径（透明、不丢信息）。

`Parser::ParseFile` → **PARSE_OK**（无语法错误）。

> 期间踩坑：第一版把模板分隔写成 `|`，被 PowerShell 当成管道符 → `package.ps1` 在写 VERSION.json 时抛
> `术语 'sidecar=bundled: …' 不会被识别为 cmdlet`。已改回 `;` 并重跑通过。

## AC4 判别力（红/绿）

**绿（base 变体，端到端）**：用 fixture sidecar（5 个 exe + `build-manifest.json` schema v14，非真实 sidecar 构建）跑 `package.ps1`：
- `PKG_EXIT=0`；产出 `VERSION.json`：`version=0.1.1`、`variant=base`、`models_bundled=false`、`models_bundled_bytes=0`、`models_dir_bytes=0`、
  `app_build={exe_sha256=3b4d2578…e895; exe_bytes=82,912,672; repo_head=45e25b9bb…}`（head 为 exe 内嵌值）；
- 护栏：**`OK (exe, core_service, 0 onnx / 0 B all match VERSION.json)` / EXIT=0**（见 `ac4-green-base-guard.log`、`ac4-green-base-version.json`）。

**红**：把同一 stage 的 `app_build` 删掉 → 护栏 `FAILED with 3 problem(s)`（首条 `no app_build section`）/ EXIT=1。

## AC5 不越界

- 未改护栏的检查集合（只对齐生成器口径）；未改 `installer.nsi`；未改许可证声明；未改任何 Gate 判定。
- 旧 stage（INSTALLER-MATRIX-1）只读，未覆盖。

## 未覆盖

- **models 变体的端到端未跑**：需要把 632 MB 权重复制进 sidecar 并打包（重活）。`models_bundled_bytes` 的口径已与护栏一致（只算 onnx），
  但「含权重的包能过闸」只有口径推导 + 微测（`models_bundled_bytes mismatch: json=1071 actual=1000` 的反例已由 reviewer-pvd 记录）。
- `repo_head` 的「可验证性」依赖 exe 内嵌 40-hex；若某次发布未内嵌，回退 `git rev-parse HEAD` 可能与 exe 不符（护栏会因此 FAIL，属 fail-closed）。
