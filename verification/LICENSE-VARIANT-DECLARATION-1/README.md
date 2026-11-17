# LICENSE-VARIANT-DECLARATION-1 · 证据（2026-11-17，方向 A）

# head: 4ca94f0df（收口前 HEAD）
# interpreter: pwsh 7 / python 3 / makensis v3.13
# 裁定来源: doc/reviews/ZCODE-RULING-INSTALLER-LICENSE-2026-11-17.md（第二次调用：DECISION = A）

## 决定

ZCode 第二次调用（不带 `--json`，正文未截断）：

```
DECISION: A
REASON: 项目边界已明文预设「集成 AGPL-3.0 组件（如 Ultralytics）则整体按 AGPL-3.0 声明」，
        且权重随包开箱可用是既有产品裁决（NSIS 438MiB 先例），移除权重属功能倒退。
NEXT: 先在 THIRD_PARTY_LICENSES.md 把三项权重「[待核实]」核实落定为 AGPL-3.0（A 的事实前提），
      随后改 installer.nsi:60/:72/:73/:103 四处硬编码文案。
```

DSH 采纳方向 A。**但「核实落定为 AGPL-3.0」这一步 DSH 不做**：三项权重的上游许可客观上未一手核实，
把它写成「已核实 AGPL-3.0」会是伪造事实。改按同一裁定书 R4 的**保守出口**执行：随包权重未全部核实 ⇒ 整包声明 AGPL-3.0，
并在文档里如实标注「上游许可待核实」。这是**过度声明（安全方向）**，不是虚假声明。

## AC2/AC3 改动（方向 A）

| 文件 | 改动 |
|---|---|
| `NOTICE.md` | models 变体的权重清单改为**实际 3 个 ONNX**（rtdetr-v2-fixed / manga-ocr encoder / decoder，含字节与 sha256 前 16 位）；说明按保守策略整包 AGPL；标注此前「yolo11s-seg」的描述错误并更正 |
| `apps/desktop-avalonia/docs/LICENSE_AUDIT.md` | 变体表与 §3 权重表按实物重写；标注三项「待核实」与保守 AGPL 结论；附「名为 base 实际装 632 MB 权重却声明 GPL」的更正说明 |
| `THIRD_PARTY_LICENSES.md` | §3 增加「整包许可结论（保守策略）」段：3 项待核实 + yolo11s-seg 当前不在包内 ⇒ models 整包 AGPL-3.0，GPL 只适用无权重 base |
| `packaging/nsis/installer.nsi` | 4 处硬编码（`LegalCopyright` / `MUI_WELCOMEPAGE_TEXT` / `MUI_LICENSEPAGE_TEXT_TOP` / 安装日志）改为读取 `${VARIANT_NAME}` `${VARIANT_LICENSE}`；内容短语由 `${VARIANT_NAME}` 在脚本内推导（中文不走命令行，避免乱码） |
| `apps/desktop-avalonia/scripts/build-installer.ps1` | 从 stage 的 `VERSION.json` 取 variant/license 传给 makensis；**权重存在但 license≠AGPL-3.0 直接 throw**（fail-closed）；`build-info.json` 的 `variant`/`stage.version_json.license` 改为按实际 stage 记录 |
| `apps/desktop-avalonia/scripts/package.ps1` | `package-manifest.json` 的 `models_bytes` 改为 onnx 口径（+ `models_dir_bytes` 保留全量）；`bundled_weights_license` 由**实际文件列表**生成（此前硬编码 yolo11s-seg） |

## AC3 绿（models 变体端到端）

`package.ps1 -Version 0.1.1 -WithModels -SidecarDir <fixture>` → `PKG_EXIT=0`；产出：

```
version=0.1.1  variant=models  license=AGPL-3.0
models_bundled=True  models_bundled_bytes=632,552,582  models_dir_bytes=632,662,260
app_build={exe_sha256=…; exe_bytes=…; repo_head=<exe 内嵌 40-hex>}
bundled_weights_license=AGPL-3.0 (conservative: models/detector/rtdetr-v2-fixed.onnx,
  models/ocr/manga-ocr-onnx/decoder_model.onnx, models/ocr/manga-ocr-onnx/encoder_model.onnx)
```

护栏：**`OK (exe, core_service, 3 onnx / 632552582 B all match VERSION.json)` / EXIT=0**。

安装器（同一 stage）：`build-installer.ps1` → `INST_EXIT=0`；
makensis 收到 `VARIANT_NAME=models` / `VARIANT_LICENSE=AGPL-3.0`（见 `ac3-nsis-variant-defines.log`）；
`build-info.json`：`variant=models`、`stage.version_json.license=AGPL-3.0`、
`installer = 652,157,341 B / sha256 a4b11458690f38f7b0cb245dd5c5eb74f830dff835489d64af0581fa459e2fba / authenticode=NotSigned`。

## AC4 判别力：旧 stage 仍被拒

对 `INSTALLER-MATRIX-1` 的旧 stage（名为 base、实装 632,552,582 B 权重、声明 GPL-3.0-or-later）跑护栏：**EXIT=1**（8 条 FAIL，见 `ac4-old-stage-still-rejected.log`）。
⇒ 「旧的不合规包会被挡住、新的合规包能通过」两侧都有实测。

## 边界与未覆盖

- **不做**权重上游许可的「核实认定」：三项仍为「待核实」，只是**保守按 AGPL 声明**。
- 未验证安装向导的**实际渲染**（中文文案在 NSIS 里压缩存储，无法用字符串搜索确证；已通过 makensis 编译 + 变体定义核对）。
- `setup.exe` **未签名**（`authenticode=NotSigned`），Release Gate 条件 4 仍需真证书。
- 未改动旧 stage 任何字节。
