# 漫画统一测试资产

本目录维护 JA/KO 共用的独立测试 Case Catalog，不接入生产用户作品数据。`manifests/cases.json` 当前有 68 个定义：10 个 KO Webtoon、8 个待取得的 KO Pepper&Carrot 来源页、3 个本次取得的 KO Pepper&Carrot 页面、37 个可选 Manga109 作品、10 个已取得的日语本地化页面。L0 Smoke 仍为 KO 10 + JA 10，20 个资产均本地可用；L1/L2 68 个定义中仅 23 个已取得完整 Case 文件。L1 目标仍为 100–150 个固定困难 Case，但不为数量扩充空目录。Manga109 是可选来源，不再是 JA Smoke/L1 硬前置。

## READY 的含义

Case 的 `READY` 只表示预期本地文件存在且通过完整性验证。它不表示 OCR、Text Detection、Translation、Inpainting、Typesetting、Reading Order、SFX、Speaker Attribution 或 Webtoon 切片/重组已经通过。`pipeline_status` 按每个 Case 的 `expected_pipeline` 独立记录；当前所有应用 Pipeline 都是 `NOT_RUN`。资产 READY 与 Pipeline Verified 是不同门槛。

## 路径与工具

- `manifests/cases.json` 是 JA/KO 统一清单和困难标签 taxonomy；Case 路径相对本目录，适用于 Windows。每个 Case 共用 `source_name`、`asset_type`、`image_available`、`annotation_available`、`source_url`、`license`、`ground_truth_types`、`pipeline_status` 等字段。`image_available` / `annotation_available` 是本次本机文件快照，实时状态仍须由 CLI 复算。
- `cases.json` 中的 `status` / `asset_status` 是维护清单时的快照；每次运行时以 CLI 根据当前本地文件、inventory checksum 和格式检查计算出的状态为准。
- `manifests/local_asset_inventory.json` 记录已取得的 JA 资源及本次 KO Pepper&Carrot 页的许可、内容类型、文件数、字节数、逐文件 SHA-256、GT 能力和 Pipeline 状态；`verify`、`list`、`missing` 均重新计算 inventory 文件的哈希。必需 XML / license 缺失或任一文件哈希不符会返回失败；缺失的图像会在状态与 `missing` 输出中显示。
- 继承自 M2-TA1 的 80 个 KO Webtoon 资产未纳入运行时 SHA inventory；其 `READY` 表示所需 PNG/JSON 文件存在、PNG chunk CRC 与结构有效、JSON 可解析。本次将 80 个文件的 SHA-256 固定记录在 `../../verification/M2-TA2C/ko-webtoon-audit.json` 供外部复核；当前 CLI 不据此拒绝另一个结构正确的 PNG。
- `../../verification/M2-TA2A/source-audit.md` 记录来源实物类型、许可/访问边界和本次不下载原因；只有注释而无图像的来源不会记为可运行资产。
- `韩漫_KO/` 与 `日漫_JA/` 是本地原始素材位置。原始图像和归档默认忽略；只有 `日漫_JA/02_public_annotations/` 下明确标为 CC BY 4.0 的选定 XML 标注及相应许可文本进入 Git。该注释目录通过 `.gitattributes` 保留源字节，避免 Windows 行尾转换影响哈希。
- `tools/assets.py` 使用 Python 标准库，提供 `download`、`verify`、`list`、`missing`；支持 `--language ja|ko`、`--level smoke|regression|full` 和重复传入的 `--case-id`。新增公共 JA/KO 页面只接受 HTTPS `www.peppercarrot.com`，校验 URL/重定向、响应大小、JPEG、ZIP 路径、CRC 和对应语言 SVG/XML 成员，原子发布且不覆盖有效文件。保留旧 KO Webtoon 下载入口供显式恢复；日常 L0/L1 已有本地文件无需 HF 账号或重新下载。

## 资产状态（M2-TA2C，2026-09-29）

| 来源 | 本机内容 | 许可与图像边界 | 资产状态 |
|---|---|---|---|
| KO Cleaned Webtoon 固定 10 Case | 80 个文件，884,913,245 bytes（约 844 MiB） | 用户已授权本机测试；源页面将 CC BY-NC 4.0 用于作者注释/metadata，底层漫画图像仍由权利人持有。不得进 Git。 | `READY`：文件完整性已验证；应用 Pipeline `NOT_RUN` |
| Pepper&Carrot 日语本地化页面 | 10 张 JPEG + 2 个 SVG language-pack ZIP，共 12 个媒体文件 / 40,284,868 bytes；逐文件大小与 SHA-256 见 inventory | 官方页面标为 CC BY 4.0，需保留作者及译者署名。内容是法国原创 webcomic 的日语本地化，不是日本原创 Manga。E20P06/E20P07 有部分机器可读日文文字层；没有对白转录全集、检测框或 mask。原图虽可依许可再分发，仍默认不提交 Git。 | `READY`：页面与配对 ZIP/member 完整性已验证；Open Ground Truth 能力整体 `PARTIAL`；应用 Pipeline `NOT_RUN` |
| Pepper&Carrot 韩语本地化页面 | E04P02/P03/P07 三张 JPEG + 共用 1 个官方 SVG language-pack ZIP，4 个本地文件 / 16,292,579 bytes；逐文件 SHA-256 见 inventory | 同一上游，无第二次全仓克隆；CC BY 4.0 署名条件。三个配对 SVG 含韩文文本层，但没有完整检测框或 mask；法国原创韩语本地化，不计原生韩漫。 | 3 个新增 Case 的资产 `READY`，仅列入 L1/L2；应用 Pipeline `NOT_RUN` |
| Manga109 37 个已选作品 | 0 张漫画图像 | Manga109-v2026 官方 gated 数据；用户授权记录不替代平台访问条件。不得用镜像或提交原图。 | `BLOCKED_BY_ASSET_ACCESS` |
| COO | 37 份 XML 标注 + CC BY 4.0 许可文本；无配对图像 | 标注可再分发；Manga109 图像不在此源中。 | `PARTIAL`：标注已本地解析，图像视觉验证未执行 |
| Manga109Dialog | 37 份 XML + CC BY 4.0 许可文本；无配对图像或独立对白转录 | 数据是 speaker/text ID 关联；基础文本及图像仍需 Manga109 资源。 | `PARTIAL` |
| JMangaBench_Mixed | 本机无 benchmark 图像 | 公共仓库含 GPL-3.0-only 代码、recipe、metadata、hash/evaluator 与 rendering layers；完整图像集依赖 Manga109-s。 | `BLOCKED_BY_ASSET_ACCESS` |
| Text Mask | 0 个文件 | Zenodo 列出 Manga109 派生的 450 份预/后处理分割数据；原始页图受 gated access 约束，记录未声明 license。 | `BLOCKED_BY_ASSET_ACCESS` |
| OpenMantra 候选 | 0 个文件 | 官方仓库描述含日文页图、原文/译文和框；许可为 CC BY-NC 4.0，非商业用途限定与本产品测试范围未能确认兼容，因此未取得、未计入可运行覆盖。 | `MISSING`（条件候选） |
| eBDtheque | 0 个文件 | 官方要求学术邮箱人工注册并接受条款后下载；提供图像和 panel/balloon/text/reading-order GT。 | `BLOCKED_BY_ASSET_ACCESS`，不得计入可运行 |
| Artificial Manga Panel Dataset | 0 个生成页面 | 公开仓库是 MIT 代码和配方；生成依赖另外来源的文本、字体和图像材料。 | `MISSING`，`SYNTHETIC_STRESS_TEST` 候选；不计真实漫画覆盖 |
| Public Domain Japan | 0 个文件 | Japan Search/NDL 是检索入口，每件图像单独核对权利；规划 `public_domain/`、`licensed_open/`、`historical_scan/` 三类，不批量爬取。 | `MISSING_MANUAL_SELECTION` |
| AIHub KO optional | 0 个文件 | 访问与再分发条件未落实。 | `BLOCKED_BY_ASSET_ACCESS`，可选 |
| 其他 KO 来源 | AIHub 本次请求返回 HTTP 403；KO Pepper&Carrot 8 个来源页未下载 | 不从 403 推断账号授权；按各自来源许可处理。 | `BLOCKED_BY_ASSET_ACCESS` / `MISSING`，详见 manifest |

当前 SHA inventory 共 92 个文件 / 63,317,229 bytes（JA 12 个媒体、KO Pepper&Carrot 4 个媒体、76 个 annotation XML / license 文件）；每个文件均记录大小和 SHA-256。另有 KO Cleaned Webtoon 80 个文件 / 884,913,245 bytes，运行时做格式/CRC 校验，逐文件 SHA-256 另存审计清单。上述 `READY` 只表示资产文件状态。实际页面的应用级 Smoke/Regression 仍需后续独立运行。Manga109 公开 annotation 与 Manga109 原图许可相互独立；只有 annotation 的资源不标为完整视觉测试资产。

附件 `漫画素材包_无HF方案_日漫韩漫.zip` 没有实际图像或 GT，且下载/校验/重打包脚本不能安全替换现有 CLI；静态审计见 `../../verification/M2-TA2C/attachment-audit.md`，官方来源审计见 `../../verification/M2-TA2C/source-audit.md`。OpenMantra 的 CC BY-NC 范围、TextMasks 的空白许可栏、JMangaBench 对 Manga109-s 像素的依赖均如实保持不可运行状态。

## 使用

在仓库根目录运行：

```powershell
python test_assets/comic_golden_suite/tools/assets.py list --level smoke
python test_assets/comic_golden_suite/tools/assets.py missing --level smoke
python test_assets/comic_golden_suite/tools/assets.py verify --language ja --level smoke
python test_assets/comic_golden_suite/tools/assets.py download --language ja --level smoke
python test_assets/comic_golden_suite/tools/assets.py verify --language ko --level smoke
python test_assets/comic_golden_suite/tools/assets.py download --language ko --level smoke
python test_assets/comic_golden_suite/tools/assets.py list --language ko --level regression --case-id K11 --case-id K12 --case-id K13
python test_assets/comic_golden_suite/tools/assets.py verify --language ko --level regression --case-id K11 --case-id K12 --case-id K13
```

日常 JA smoke 使用已实际取得的 10 个 Pepper&Carrot 日语页面，不枚举缺图的 Manga109 Case。正式通过 Manga109 官方流程取得归档后，才使用：

```powershell
python test_assets/comic_golden_suite/tools/assets.py download --language ja --level regression --archive "$env:USERPROFILE/Downloads/Manga109_released_2026_05_21.zip"
```

`download` 不会自动抓取全量 Manga109/Manga109-s 或 Text Mask 数据。已有文件损坏时校验会报错且不会静默覆盖。无网络时 `verify` 只读取本地文件。

## 注释数据署名与许可

- COO 标注归属 Aizawa Yamakata Matsui Lab，按 CC BY 4.0 发布。再分发时保留来源和许可，并引用 Baek、Matsui、Aizawa 的 ECCV 2022 论文《COO: Comic Onomatopoeia Dataset for Recognizing Arbitrary or Truncated Texts》。
- Manga109Dialog 标注归属 Aizawa Yamakata Matsui Lab，按 CC BY 4.0 发布。再分发时保留来源和许可，并引用 Li、Aizawa、Matsui 的 ICME 2024 论文《Manga109Dialog: A Large-scale Dialogue Dataset for Comics Speaker Detection》。对应许可文本随选定 XML 一同提供。
- 许可只覆盖上述标注，不改变底层 Manga109 漫画页的访问与再分发限制。

## 官方来源

- [Pepper&Carrot E04 Japanese source page](https://www.peppercarrot.com/ja/webcomic/ep04_Stroke-of-genius__sources.html)
- [Pepper&Carrot E20 Japanese source page](https://www.peppercarrot.com/ja/webcomic/ep20_The-Picnic__sources.html)
- [Manga109 public annotations](https://github.com/manga109/public-annotations)
- [JMangaBench_Mixed](https://github.com/muscgab/JMangaBench_Mixed)
- [Manga109 official project and access terms](https://manga109.github.io/manga109-project-website/en/)
