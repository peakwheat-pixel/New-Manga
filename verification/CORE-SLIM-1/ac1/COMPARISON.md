# AC1 — Qt 参考 vs Pillow 替代：解码/像素等价报告

采集方式：`tools/capture_decode_paths.py --impl qt`（改前，PySide6 实现）与 `--impl pillow`（改后，Pillow 实现）跑同一批确定性 fixtures，再由 `--compare` 逐项比较；原始数据见 `qt/results.json`、`pillow/results.json`、`comparison.json`，输入指纹见 `fixtures-manifest.json`。

## 汇总

| 维度 | 结果 |
|---|---|
| 解码矩阵（尺寸/MIME/成败） | **11/12** |
| 像素产物（frame 原始字节 + page/crop/bridge PNG） | **16/16** |
| PDF 光栅页（2 页逐像素） | **2/2** |

## 解码矩阵（`QtImageDecoder` → `PillowImageDecoder`）

| fixture | 期望 | Qt | Pillow | 判定 |
|---|---|---|---|---|
| `basic.png` | — | OK 11x7 image/png | OK 11x7 image/png | 一致 |
| `plain.bmp` | — | OK 20x10 image/bmp | OK 20x10 image/bmp | 一致 |
| `photo.jpg` | — | OK 64x48 image/jpeg | OK 64x48 image/jpeg | 一致 |
| `palette.png` | — | OK 24x16 image/png | OK 24x16 image/png | 一致 |
| `alpha.png` | — | OK 40x30 image/png | OK 40x30 image/png | 一致 |
| `multi.tiff` | — | OK 40x30 image/tiff | OK 40x30 image/tiff | 一致 |
| `still.webp` | — | OK 64x48 image/webp | OK 64x48 image/webp | 一致 |
| `anim.webp` | — | OK 32x24 image/webp | OK 32x24 image/webp | 一致 |
| `anim.gif` | — | OK 48x32 image/gif | OK 48x32 image/gif | 一致 |
| `still.avif` | — | FAIL Unsupported image format | OK 32x24 image/avif | **差异（见备注）** |
| `long.png` | — | OK 690x4000 image/png | OK 690x4000 image/png | 一致 |
| `declared-huge.png` | — | FAIL Unable to read image data | FAIL image declares 8192x65536 = 2048.0 MiB decoded, above th | 一致 |

**唯一差异（能力增益，非回归）**：`still.avif` 在 Qt 闭包里无 AVIF 插件，改前是“已声明后缀但解码失败”；Pillow 12.3 自带 AVIF 解码，改后成功。`heic/heif` 两侧都不支持（Pillow 需 pillow-heif，非依赖）——即**没有任何解码能力被删除**。

## 像素路径（逐像素相等，字节差异仅来自 PNG 编码器）

| 样例 | `page_frame`（rgb32 原始字节） | `page_png` | `region_crop` | `_render_content_decoder` |
|---|---|---|---|---|
| `basic.png` | ✅ 像素相等 | ✅ 像素相等（字节不同） | ✅ 像素相等（字节不同） | ✅ 像素相等（字节不同） |
| `photo.jpg` | ✅ 像素相等 | ✅ 像素相等（字节不同） | ✅ 像素相等（字节不同） | ✅ 像素相等（字节不同） |
| `alpha.png` | ✅ 像素相等 | ✅ 像素相等（字节不同） | ✅ 像素相等（字节不同） | ✅ 像素相等（字节不同） |
| `palette.png` | ✅ 像素相等 | ✅ 像素相等（字节不同） | ✅ 像素相等（字节不同） | ✅ 像素相等（字节不同） |

`page_frame` 是字节级完全相等（`Format_RGB32` 的 BGRA little-endian 内存布局，alpha 固定 0xff）；`page_png`/`region_crop`/`_render_content_decoder` 的 PNG **字节**不同是编码器实现差异（Qt vs libpng/zlib 设置），**解码后像素逐字节相等**。下游只消费像素或把 PNG 作为自产 Managed Copy 保存，不跨版本比对 PNG 字节，因此无兼容性影响。

## PDF 光栅（真实 pypdfium2 渲染 → PNG）

| 页 | 尺寸 | 像素 | 字节 |
|---|---|---|---|
| page0 | 1224x1584 | ✅ 相等 | 不同（编码器） |
| page1 | 1224x1584 | ✅ 相等 | 不同（编码器） |

## SourceStyle 分析器等价（`PixelSourceStyleAnalyzer` → `PillowSourceStyleAnalyzer`）

以 `tests/infrastructure/test_pillow_source_style.py` 锁定：同一 crop 上 `detected_source_font_size` / `source_font_size_confidence` / `text_color` / `background_color` / `direction_hint` 与 Qt 实现逐字段相等（该测试在 Qt 可用的开发环境运行；打包闭包内不再需要 Qt）。

