# M2-TA2C 官方来源与许可审计

2026-09-29 复核。此表区分“官方可访问”与“本机可运行”。`READY` 仅针对资产完整性；所有应用级 Pipeline `NOT_RUN`。新素材下载前检查磁盘空间，原图进入 ignored 本地目录。

| Source | 官方实际内容与使用边界 | 当前处置 |
|---|---|---|
| [OpenMantra](https://github.com/mantra-inc/open-mantra-dataset) | 5 个日本漫画作品的页图、`annotation.json`，含框和 JA/EN/ZH 文本；[LICENSE](https://github.com/mantra-inc/open-mantra-dataset/blob/main/LICENSE.md) 为 CC BY-NC 4.0。项目产品开发用途的非商业适配尚未确证；不能把公开 clone 权推导为无条件测试权或再分发权。 | `MISSING`，0 本机文件；禁止自动 clone，待权利范围明确。不是 L0 硬前置。 |
| [eBDtheque](https://ebdtheque.univ-lr.fr/registration/) | 漫画页与 panel/balloon/text/reading-order 标注；官网要求同意条款并用学术邮箱人工注册，再使用提供的账号下载。 | `BLOCKED_BY_ASSET_ACCESS`；0 配对文件。 |
| [Pepper&Carrot](https://www.peppercarrot.com/en/webcomic-sources/ep04_Stroke-of-genius.html) JA/KO | David Revoy 法国原创作品的日语/韩语本地化；官方 CC BY 4.0，页面和语言 SVG pack 可分别取得。不是日本原创商业 Manga；已有 JA 10 JPEG+2 ZIP，且 E20P06/P07 只有部分可机读日语文本。KO 从同一官方源选择页图，不重复克隆全仓。 | JA 10 页资产 `READY`，GT `PARTIAL`；本次另取得 KO E04P02/P03/P07 3 JPEG + 1 ZIP（16,292,579 bytes），SVG 含韩文的 `flowPara` 节点分别为 34/16/18（P07 另有其他韩文文本块），3 Case 资产 `READY`、Pipeline `NOT_RUN`。署名须保留。 |
| [Artificial Manga Panel Dataset](https://github.com/aasimsani/artificial_manga_panel_dataset) | GitHub 仓是 MIT 代码与配方；生成所需 JESC、Kaggle 图像、字体与 PSD 等材料分别有来源条件。克隆代码不等于拥有合成页面或清晰的复合许可。 | `MISSING`，0 生成图；可做未来 `SYNTHETIC_STRESS_TEST`，不计真实漫画覆盖。 |
| [JMangaBench_Mixed](https://github.com/muscgab/JMangaBench_Mixed) | GPL-3.0-only 代码、recipe、metadata、rendering layers/evaluator；1286 real crops 与 2000 synthetic 样本均在本地构建时读取 Manga109-s 像素。公开仓不含完整可运行图像。 | `requires_Manga109_pixels=BLOCKED_BY_ASSET_ACCESS`；`usable_without_Manga109` 只有代码/配方，不计视觉 READY。 |
| [TextMasks Zenodo](https://zenodo.org/records/4511796) | 450 份 Manga109 来源页的文本分割 mask，两个公开 ZIP 共约 19.2 MB、官方 MD5 可核。Zenodo Rights/License 栏空白，原漫画图像需另行取得 Manga109 权限。mask 与原图不可混为完整 Inpainting GT。 | 许可证不明且无配对像素，当前 `BLOCKED_BY_ASSET_ACCESS`；0 本机文件。不得无条件下载/再分发。 |
| [Japan Search](https://jpsearch.go.jp/) / [NDL](https://www.ndl.go.jp/) | 检索入口，不是统一许可的可批量下载 dataset；每件作品需独立判定公有领域/开放许可。 | `MISSING_MANUAL_SELECTION`；仅保留 `public_domain/`、`licensed_open/`、`historical_scan/` 目录规范，不自动爬取。 |
| [Manga109](https://manga109.github.io/manga109-project-website/en/) | 官方授权的原始漫画页需另行取得；已有 COO/Manga109Dialog 共 74 XML+2 license，均只有 annotation、没有配图。 | Manga109 optional `BLOCKED_BY_ASSET_ACCESS`，COO/Dialog annotation `PARTIAL`；不阻塞 JA L0/L1。 |
| [KO Cleaned Webtoon](https://huggingface.co/datasets/Vasyanator2/cleaned_webtoon_dataset) | 既有固定 10 Case 共 80 文件已本地取得。公开下载入口仍在 HF，但已有资产不需要账号/网络；作者的 CC BY-NC 只覆盖 annotation/metadata，不授予底层商业漫画图像再分发权。 | 仅本地完整性 `READY`；本 Task 不重复下载；应用 Pipeline `NOT_RUN`。 |
| [AIHub](https://www.aihub.or.kr/) | 可选外部数据源，入口访问条件需单独确认；不能把 HTTP 403 推断为授权状态。 | `BLOCKED_BY_ASSET_ACCESS` / optional；0 本机文件。 |

## 判断原则

1. 官方仓库、URL 或下载脚本存在不代表已有可运行图像。
2. 注释许可与底层图像许可分开记录；未有配图时只能 `PARTIAL` 或 `BLOCKED_BY_ASSET_ACCESS`。
3. 目标产品使用范围尚未确认符合 CC BY-NC 时，不把 OpenMantra 或许可不明 TextMasks 自动取得/标 READY。
4. 目录占位与 code-only 不计入 L0、L1、L2 可运行数；`screentone` / `historical_scan` 可作普通标签说明，维持原 16 项 taxonomy。
