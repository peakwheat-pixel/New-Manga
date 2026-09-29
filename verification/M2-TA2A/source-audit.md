# M2-TA2A 来源实物、许可与可运行性审计

审计日期：2026-09-29。核对官方来源页面/仓库、其文件清单与许可说明；本机文件是否存在和完整性以 `manifests/local_asset_inventory.json` 为准。`READY` 仅代表本地文件完整，不代表应用 Pipeline 已验证。

| 来源 | 官方公开内容实际类型 | License / 原图再分发与访问 | 本机结果与可用范围 |
|---|---|---|---|
| Pepper&Carrot E04 Japanese sources | 日语页面图像、Inkscape SVG language pack；官网页面列 8 页和 source ZIP。选中的 E04 SVG 页没有可抽取的非空日语文字节点，不含检测框或 mask。 | 官网标示作品为 CC BY 4.0；需署名作者。图像按该许可可再分发，本仓库仍将原图与归档保持在 Git ignore 下。 | 3 JPEG + 1 ZIP，15,940,323 bytes，逐文件 SHA-256 已记；文件 `READY`，E04 本身不提供机器可读日文 transcription。来源是法国原创 webcomic 的日语本地化版本。 |
| Pepper&Carrot E20 Japanese sources | 日语页面图像、SVG language pack；官网页面列 7 页和 source ZIP。所选 SVG 的 E20P06/P07 有部分非空日文文本层；不含完整对白 transcription、检测框或 mask。 | CC BY 4.0，按官网作者/译者信息署名；原图和 ZIP 不进 Git。 | 7 JPEG + 1 ZIP，24,344,545 bytes，逐文件 SHA-256 已记；文件 `READY`，`Open Ground Truth` 整体仍仅 `PARTIAL`。法国原创 webcomic 日语本地化，不是日本原创 Manga。 |
| Manga109-v2026 | Manga 图像及配套基础标注。 | 官方项目通过 access request 发放；授权用途依版本/卷册区分，页面说明原 Manga109 为学术非商业，Manga109-s 的 87 卷另获商业用途许可。当前无官方归档或本地页图。 | 0 文件，`BLOCKED_BY_ASSET_ACCESS`。不尝试镜像或非官方下载。 |
| Manga109 public annotations / COO | XML annotation，包含日语拟声词转录文本、页码尺寸 metadata 与 polygon 坐标；不含漫画图像。 | Aizawa Yamakata Matsui Lab 按 CC BY 4.0 发布 annotations；该许可不覆盖底层 Manga109 图像。 | 37 XML + license，3,333,257 bytes；全部 XML 可解析。`PARTIAL`：可做 annotation 解析/静态对照；没有配对图像，视觉 SFX/OCR 不可运行。 |
| Manga109 public annotations / Manga109Dialog | XML annotation，内容是 `speaker_id` 到 `text_id` 的关系；不是对白文本 transcription，也不含漫画图像。 | Aizawa Yamakata Matsui Lab 按 CC BY 4.0 发布 annotations；底层页图许可独立。 | 37 XML + license，3,406,525 bytes；全部 XML 可解析。`PARTIAL`：可解析说话人与文本 ID 关系；需要 Manga109 基础文本标注和图像才能做完整 speaker attribution。 |
| JMangaBench_Mixed | GPL-3.0-only 项目代码；构建 recipes、metadata、hashes/evaluator 与公开 rendering layers。规范组成 1,286 个依 Manga109-s 图像本地重建的真实 crops + 2,000 个合成样本；公开仓库不再分发 Manga109-s 页图像像素。 | Manga109-s 必须由使用者单独从官方渠道取得并遵守其访问条款；本地构建物含 Manga109-s 派生像素且不允许再分发。 | 本项目未复制 benchmark 仓库或其构建物，0 本地文件；`BLOCKED_BY_ASSET_ACCESS`，不是可运行图像集。 |
| Text Mask（Zenodo 10.5281/zenodo.4511796） | 记录列出预处理 ZIP 7.9 MB、后处理 ZIP 11.3 MB；说明数据为 450 张 Manga109 来源图像的文字分割数据，含文本 mask / segmentation。 | Zenodo record 的 Rights/License 字段为空；说明查看原漫画图像需要另行取得 Manga109 access。无法从记录确认 mask/嵌入像素的再分发权。 | 未下载，0 本地文件；`BLOCKED_BY_ASSET_ACCESS`。 |
| OpenMantra | 官方仓库包含 5 部日本漫画的原图和 annotation JSON；每个对白项包含 bbox、日文原文及英文/中文译文。 | 仓库许可证为 CC BY-NC 4.0。当前项目使用范围没有被界定为非商业，故未复制或纳入可运行集；用户任务授权不改变上游 license 条款。 | 0 本地文件；`MISSING`（许可范围不匹配/未确认），不计 runnable。 |
| 其他当前 manifest 登记的 JA 来源 | Manga109 代表作 Case 均依赖 Manga109-v2026 图像；本轮未发现另一份已经登记、许可清晰且可独立配对图像与 Ground Truth 的 JA 资产。 | 逐项受上述 Manga109、annotation 或来源许可边界约束。 | 保留 manifest 状态，不把目录定义计入实际 runnable 覆盖。 |

## 下载和完整性事实

- 本地新增开放页面为 10 JPEG + 2 ZIP，共 40,284,868 bytes；JPEG 为 5,482,647 bytes，language-pack ZIP 为 34,802,221 bytes。
- COO 与 Manga109Dialog 合计 74 XML + 2 个 CC BY 4.0 license 文件，共 6,739,782 bytes。两份 license 文件只去除了上游文件末尾多余的空白行，许可正文未改；inventory 同时保存原始 `source_sha256` 和本地 `sha256`。
- 88 个本地文件逐项记录 `source`、`license`、图像再分发状态、local path、文件数、字节数、SHA-256、ground-truth 类型、可检查 Pipeline 和执行状态；没有虚构 source-group checksum。JPEG、ZIP、SVG 成员和 XML 均做了相应格式/CRC/解析验证。`verify`、`list`、`missing` 每次都校验 inventory；缺少图像等可选媒体会计入 missing，缺少 annotation/license 或 SHA-256/大小不匹配会使命令失败。

## 官方来源

- [Pepper&Carrot E04 sources](https://www.peppercarrot.com/ja/webcomic/ep04_Stroke-of-genius__sources.html)
- [Pepper&Carrot E20 sources](https://www.peppercarrot.com/ja/webcomic/ep20_The-Picnic__sources.html)
- [Pepper&Carrot about/license](https://www.peppercarrot.com/ja/about/index.html)
- [Manga109 public annotations](https://github.com/manga109/public-annotations)
- [JMangaBench_Mixed](https://github.com/muscgab/JMangaBench_Mixed)
- [Text Mask Zenodo record](https://zenodo.org/records/4511796)
- [OpenMantra dataset](https://github.com/mantra-inc/open-mantra-dataset)
- [Manga109 access information](https://manga109.github.io/manga109-project-website/en/)
