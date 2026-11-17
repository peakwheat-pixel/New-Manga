# PACKAGE-VERSION-JSON-DERIVED-1 · 证据（2026-11-17）

# head: a370a1f39（修复提交）
# interpreter: pwsh 7
# command: pwsh -NoProfile -File apps/desktop-avalonia/scripts/package.ps1 -Version 0.1.1 -WithModels -OutputRoot <ws> -SidecarDir <stage core-sidecar>

## AC1 缺口（生成器 vs 护栏）

- `package.ps1:151` 原模板**不含**顶层 `models_bundled` / `models_bundled_bytes`（`models_bundled` 只在 `:95` 的 `sidecar_build` 子对象里）。
- `tools/ci/verify-package-manifest.ps1` 要求顶层字段存在，缺即 `Add-Failure`：
  `FAIL: VERSION.json has no models_bundled field (must be derived from the stage, not omitted)`。
- `build-installer.ps1:152` 对该护栏是 fail-closed ⇒ 干净 `package.ps1` 产物也无法打包。

## AC2 修复

`package.ps1:151` 模板追加两个**由磁盘推导**的字段（复用 `:80-81` 的既有推导，不新增第二套计算）：

```
models_bundled=$modelsBundled;models_bundled_bytes=[int64]$modelsBytes;
```

`Parser::ParseFile` → **PARSE_OK**（无语法错误）。

## AC3 判别力（红）

去掉顶层两字段的同构 stage（`tmp\r23\red-nofield`）跑护栏：

# EXIT=1
verify-package-manifest: FAILED with 3 problem(s)
  FAIL: VERSION.json has no models_bundled field (must be derived from the stage, not omitted)
  FAIL: package-manifest.json bytes mismatch for 1 file(s): VERSION.json (manifest=470 actual=442)
  FAIL: package-manifest.json sha256 mismatch for 1 file(s) (e.g. VERSION.json)

## AC4 端到端（绿）—— **受阻，未完成**

尝试用既有打包产物重跑 `package.ps1`：

# EXIT=1
Exception: ...\package.ps1:51
  sidecar bundle has no build-manifest.json under ...\INSTALLER-MATRIX-1\stage\NewManga-0.1.1-win-x64\app\core-sidecar
  -- it cannot prove which schema it understands. Rebuild it with packaging/m2ac5/build_sidecar.ps1 -Force (that script writes the manifest).

**实测**：该 stage 的 `app/core-sidecar/` 只有 5 个 exe（`acceptance_bridge` / `catalog_loader` / `core_service` / `host_bridge` / `sfx_detect_probe`），
**没有 `build-manifest.json`**（该文件由 `packaging/m2ac5/build_sidecar.ps1:381` 写入 bundle）。
⇒ 想端到端验证本卡，必须先重建 sidecar（`build_sidecar.ps1 -Force`，重活），本轮**未做**。

## AC5 不越界

- 未改 `installer.nsi`；未删/放宽任何护栏检查；未改许可证声明；未改任何 Gate 判定。
- 旧 stage 只读，未覆盖。
