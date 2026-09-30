# 漫画统一测试资产

本目录维护 JA/KO 共用的独立测试 Case Catalog，不接入生产用户作品数据。`manifests/cases.json` 当前有 97 个定义：10 个 KO Webtoon、8 个待取得的 KO Pepper&Carrot 来源页（O01–O08）、15 个 KO Pepper&Carrot 本地化页面（K11–K25）、15 个 JA Pepper&Carrot 本地化页面（J38–J52）、12 个《ブラックジャックによろしく》官方免费页（BJ01–BJ12）、37 个已取消的 Manga109 作品定义（`removed_from_scope_2026-09-30: true`，仅作历史证据保留，不再等待授权或导入）。L0 Smoke 仍为 KO 10 + JA 10，20 个资产均本地可用。Manga109 前置已按用户裁决（2026-09-30）永久取消；JA 真实漫画覆盖改由官方免费《ブラックジャックによろしく》页面承担。

## READY 的含义

Case 的 `READY` 只表示预期本地文件存在且通过完整性验证。它不表示 OCR、Text Detection、Translation、Inpainting、Typesetting、Reading Order、SFX、Speaker Attribution 或 Webtoon 切片/重组已经通过。`pipeline_status` 按每个 Case 的 `expected_pipeline` 独立记录；当前所有应用 Pipeline 都是 `NOT_RUN`。资产 READY 与 Pipeline Verified 是不同门槛。

## 路径与工具

- `manifests/cases.json` 是 JA/KO 统一清单和困难标签 taxonomy；Case 路径相对本目录，适用于 Windows。每个 Case 共用 `source_name`、`asset_type`、`image_available`、`annotation_available`、`source_url`、`license`、`ground_truth_types`、`pipeline_status` 等字段。`image_available` / `annotation_available` 是本次本机文件快照，实时状态仍须由 CLI 复算。`load_manifest` 会对每个 Case 的 `source_url` 施加 HTTPS 主机白名单（`www.peppercarrot.com`、`huggingface.co`、`densho810.com`，与清单实际出现的 host 集合一致）；非白名单 host、非 HTTPS 或带凭据/非常规端口的 URL 会被 `ValueError` 拒绝（fail-closed）。
- M2-TA2B（2026-09-30）：Manga109 / Manga109-s 前置按用户裁决永久取消，37 个 J01–J37 定义与 `manga109_selected_or_full` / `jmangabench` / `text_mask` 三个 source 均带 `removed_from_scope_2026-09-30: true` 标注（其余字段不动，仅作历史证据）。
- `benchmark_sources[*].checksum_inventory` 的非空路径以仓库根目录为基准；`null` 表示本地没有可校验的对应文件。`verify`、`list`、`missing` 均在运行时消费该字段：非空路径会做存在性校验，`local_asset_inventory.json` 条目沿用既有逐文件 SHA-256 复核，其他审计清单（如 KO Cleaned Webtoon 审计）按存在性消费；缺失会以 `INVALID_BENCHMARK_INVENTORY` 报告并使命令失败。来源层 `READY` 只覆盖该条目注明的已取得范围（KO Cleaned Webtoon 为固定 10 Case），不表示原图再分发许可或应用 Pipeline 通过。
- `cases.json` 中的 `status` / `asset_status` 是维护清单时的快照；每次运行时以 CLI 根据当前本地文件、inventory checksum 和格式检查计算出的状态为准。
- `manifests/local_asset_inventory.json` 记录已取得的 JA 资源及本次 KO Pepper&Carrot 页的许可、内容类型、文件数、字节数、逐文件 SHA-256、GT 能力和 Pipeline 状态；`verify`、`list`、`missing` 均重新计算 inventory 文件的哈希。必需 XML / license 缺失或任一文件哈希不符会返回失败；缺失的图像会在状态与 `missing` 输出中显示。
- 继承自 M2-TA1 的 80 个 KO Webtoon 资产未纳入运行时 SHA inventory；其 `READY` 表示所需 PNG/JSON 文件存在、PNG chunk CRC 与结构有效、JSON 可解析。本次将 80 个文件的 SHA-256 固定记录在 `../../verification/M2-TA2C/ko-webtoon-audit.json` 供外部复核；当前 CLI 不据此拒绝另一个结构正确的 PNG。
- `../../verification/M2-TA2A/source-audit.md` 记录来源实物类型、许可/访问边界和本次不下载原因；只有注释而无图像的来源不会记为可运行资产。
- `韩漫_KO/` 与 `日漫_JA/` 是本地原始素材位置。原始图像和归档默认忽略；只有 `日漫_JA/02_public_annotations/` 下明确标为 CC BY 4.0 的选定 XML 标注及相应许可文本进入 Git。该注释目录通过 `.gitattributes` 保留源字节，避免 Windows 行尾转换影响哈希。
- KO Pepper&Carrot 两族目录前缀不同（O01–O08 用 `02_open_ground_truth_peppercarrot`，K11–K13 用 `02_public_ground_truth_peppercarrot`）是已知命名观察（TA2C P3-6）；为保证本地素材路径稳定性不改盘上目录，差异已作为受管事实记录在相关 Case 的 `naming_note` 字段并由 `tests/m2_test_assets/test_catalog.py` 的快照断言锁定，统一留待后续 Task。
- `tools/assets.py` 使用 Python 标准库，提供 `download`、`verify`、`list`、`missing`；支持 `--language ja|ko`、`--level smoke|regression|full` 和重复传入的 `--case-id`。新增公共 JA/KO 页面只接受 HTTPS `www.peppercarrot.com`，校验 URL/重定向、响应大小、JPEG、ZIP 路径、CRC 和对应语言 SVG/XML 成员，原子发布且不覆盖有效文件。保留旧 KO Webtoon 下载入口供显式恢复；日常 L0/L1 已有本地文件无需 HF 账号或重新下载。

## 资产状态（M2-TA2C，2026-09-29）

| 来源 | 本机内容 | 许可与图像边界 | 资产状态 |
|---|---|---|---|
| KO Cleaned Webtoon 固定 10 Case | 80 个文件，884,913,245 bytes（约 844 MiB） | 用户已授权本机测试；源页面将 CC BY-NC 4.0 用于作者注释/metadata，底层漫画图像仍由权利人持有。不得进 Git。 | `READY`：文件完整性已验证；应用 Pipeline `NOT_RUN` |
| 《ブラックジャックによろしく》官方免费页（BJ01–BJ12） | 第 1/3/5 卷官方 ZIP（3 个，共 1,068,836,615 bytes）+ DRM-free PDF 3 个 + pypdfium2 渲染 PNG 12 页（DPI 150，2946x4167）；逐文件 SHA-256 见 `日漫_JA/01_black_jack_official/vol*/bj_download_manifest.json` 与 `bj_pages_manifest.json` | 作者（佐藤秀峰/佐藤漫画制作所）官方免费渠道 densho810.com：商用/非商用自由、署名义务（作品名+作者名）、公开利用后 1 个月内邮件报告 info@densho810.com、禁 Kindle 上架；避开含 JASRAC 乐曲的第 2/7/11 卷。像素不入 Git。 | `READY`：ZIP/PDF/页 PNG 完整性已验证；应用 Pipeline `NOT_RUN` |
| Pepper&Carrot 日语本地化页面 | 15 张 JPEG + 2 个 SVG language-pack ZIP；逐文件大小与 SHA-256 见 inventory | 官方页面标为 CC BY 4.0，需保留作者及译者署名。内容是法国原创 webcomic 的日语本地化，不是日本原创 Manga。E20P06/E20P07 有部分机器可读日文文字层；没有对白转录全集、检测框或 mask。原图虽可依许可再分发，仍默认不提交 Git。 | 15 个 Case（J38–J52）资产 `READY`；Open Ground Truth 能力整体 `PARTIAL`；应用 Pipeline `NOT_RUN` |
| Pepper&Carrot 韩语本地化页面 | E04 5 张 + E20 7 张新增 JPEG（K14–K25），加既有 E04P02/P03/P07（K11–K13），共 15 张 JPEG + 2 个官方 SVG language-pack ZIP（E04 + E20）；逐文件 SHA-256 见 inventory | 同一上游，CC BY 4.0 署名条件。配对 SVG 含韩文文本层，但没有完整检测框或 mask；法国原创韩语本地化，不计原生韩漫。 | 15 个 Case 资产 `READY`，仅列入 L1/L2；应用 Pipeline `NOT_RUN` |
| Manga109 37 个已选作品（已取消） | 0 张漫画图像 | 用户裁决（2026-09-30）永久取消 Manga109/Manga109-s 前置；定义保留为历史证据，不再取得或导入。 | `removed_from_scope_2026-09-30` |
| COO | 37 份 XML 标注 + CC BY 4.0 许可文本；无配对图像 | 标注可再分发；Manga109 图像不在此源中。 | `PARTIAL`：标注已本地解析，图像视觉验证未执行 |
| Manga109Dialog | 37 份 XML + CC BY 4.0 许可文本；无配对图像或独立对白转录 | 数据是 speaker/text ID 关联；基础文本及图像仍需 Manga109 资源。 | `PARTIAL` |
| JMangaBench_Mixed | 本机无 benchmark 图像 | 公共仓库含 GPL-3.0-only 代码、recipe、metadata、hash/evaluator 与 rendering layers；完整图像集依赖 Manga109-s。 | `BLOCKED_BY_ASSET_ACCESS` |
| Text Mask | 0 个文件 | Zenodo 列出 Manga109 派生的 450 份预/后处理分割数据；原始页图受 gated access 约束，记录未声明 license。 | `BLOCKED_BY_ASSET_ACCESS` |
| OpenMantra（隔离 optional） | 13 个文件（annotation/LICENSE/README + 10 张样本 ja 页，2,341,834 bytes），存于 gitignored `日漫_JA/99_optional_openmantra/` | 官方仓库 mantra-inc/open-mantra-dataset；许可 CC BY-NC 4.0——仅作隔离的非商业基线（`optional_noncommercial_baseline_excluded`），不进入生产许可基线、smoke/regression/full levels 或 Git；逐文件 SHA-256 见 `verification/M2-TA2B/raw/ac5b-openmantra-verification.log`。 | `READY_OPTIONAL_ISOLATED`（不计可运行覆盖） |
| eBDtheque | 0 个文件 | 官方要求学术邮箱人工注册并接受条款后下载；提供图像和 panel/balloon/text/reading-order GT。 | `BLOCKED_BY_ASSET_ACCESS`，不得计入可运行 |
| Artificial Manga Panel Dataset | 0 个生成页面 | 公开仓库是 MIT 代码和配方；生成依赖另外来源的文本、字体和图像材料。 | `MISSING`，`SYNTHETIC_STRESS_TEST` 候选；不计真实漫画覆盖 |
| Public Domain Japan | 0 个文件 | Japan Search/NDL 是检索入口，每件图像单独核对权利；规划 `public_domain/`、`licensed_open/`、`historical_scan/` 三类，不批量爬取。 | `MISSING_MANUAL_SELECTION` |
| AIHub KO optional | 0 个文件 | 访问与再分发条件未落实。 | `BLOCKED_BY_ASSET_ACCESS`，可选 |
| 其他 KO 来源 | AIHub 本次请求返回 HTTP 403；KO Pepper&Carrot 8 个来源页未下载 | 不从 403 推断账号授权；按各自来源许可处理。 | `BLOCKED_BY_ASSET_ACCESS` / `MISSING`，详见 manifest |

当前 SHA inventory 共 110 个文件 / （92 个既有 + M2-TA2B 新增 18 个媒体：5 张 ja 页、12 张 kr 页、1 个 ep20 kr language-pack ZIP）；每个文件均记录大小和 SHA-256。另有 KO Cleaned Webtoon 80 个文件 / 884,913,245 bytes，运行时做格式/CRC 校验，逐文件 SHA-256 另存审计清单。BJ 的 ZIP/PDF 逐文件 SHA-256 与渲染页 SHA-256 记录在 `日漫_JA/01_black_jack_official/vol01..05/bj_download_manifest.json` 与 `bj_pages_manifest.json`（素材目录 gitignored，不入运行时 inventory）；BJ 渲染页的自动完整性校验走 `python test_assets/comic_golden_suite/tools/fetch_bj.py verify`（对照 cases.json 的 `page_sha256` 逐页重算，12/12 为绿色门槛）。上述 `READY` 只表示资产文件状态。实际页面的应用级 Smoke/Regression 仍需后续独立运行。Manga109 公开 annotation 与 Manga109 原图许可相互独立；只有 annotation 的资源不标为完整视觉测试资产。Manga109 取消语义（用户裁决 2026-09-30）= 仅在 case/source 上标注 `removed_from_scope_2026-09-30`、不参与可运行计数与选取，`levels` 历史定义保持不变（故 `verify --level full` 仍如实报告 37 个 `MISSING_GATED_ASSET`）。`coo_and_manga109_dialog`（COO/Manga109Dialog 标注）未打取消标注：它们是已取得的 CC BY 4.0 标注资产，不依赖 Manga109 像素访问，保持 PARTIAL 可用。

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

日常 JA smoke 使用已实际取得的 10 个 Pepper&Carrot 日语页面，不枚举缺图的 Manga109 Case。BJ 官方免费卷的获取与渲染使用（默认卷 1/3/5，避开含 JASRAC 乐曲的 2/7/11 卷；需要 pypdfium2==5.13.0）：

```powershell
python test_assets/comic_golden_suite/tools/fetch_bj.py fetch --volumes 1 3 5
python test_assets/comic_golden_suite/tools/fetch_bj.py render --volumes 1 3 5
```

`download` 不会自动抓取全量 Manga109/Manga109-s 或 Text Mask 数据（Manga109 方案已取消，`--archive` 入口保留仅为兼容历史流程）。已有文件损坏时校验会报错且不会静默覆盖。无网络时 `verify` 只读取本地文件。

## 《ブラックジャックによろしく》署名与许可义务（M2-TA2B）

- 来源：作者佐藤秀峰的公司有限会社佐藤漫画制作所（電書バト）在 [densho810.com/free/](https://densho810.com/free/) 提供的无 DRM PDF，明示"二次利用フリー"。
- **署名义务**：每次利用必须明示作品名《ブラックジャックによろしく》与作者名"佐藤秀峰"（英文语境"Give My Regards to Black Jack / SHUHO SATO"），内容不可变更。本套件统一署名字段采用官方规定格式原样：`ブラックジャックによろしく　佐藤秀峰`（作品名+作者名，全角空格分隔，内容不可变更），已写入每个 BJ case 的 `attribution` 字段；来源与许可说明另列于 `attribution_note` 字段（densho810.com 官方免费渠道、二次利用フリー、1 个月内邮件报告义务），不与署名主串混写。
- **事后报告义务**：素材公开用于测试后 1 个月内，须由用户向 info@densho810.com 发送邮件报告（Agent 不代发）；草稿见 `../../verification/M2-TA2B/densho810-report-draft.txt`。
- 其他条款：商用/非商用自由、无需事先许可；禁止 Amazon Kindle 上架；电子书商店分发须 1 円以上有偿；第 2/7/11 卷含 JASRAC 管理乐曲页面（本套件选取卷 1/3/5 规避）。
- 版权像素不入 Git：ZIP、PDF、渲染 PNG 全部位于 gitignored 目录；Git 只保留 manifest 元数据、SHA-256 清单与本说明。

## 注释数据署名与许可

- COO 标注归属 Aizawa Yamakata Matsui Lab，按 CC BY 4.0 发布。再分发时保留来源和许可，并引用 Baek、Matsui、Aizawa 的 ECCV 2022 论文《COO: Comic Onomatopoeia Dataset for Recognizing Arbitrary or Truncated Texts》。
- Manga109Dialog 标注归属 Aizawa Yamakata Matsui Lab，按 CC BY 4.0 发布。再分发时保留来源和许可，并引用 Li、Aizawa、Matsui 的 ICME 2024 论文《Manga109Dialog: A Large-scale Dialogue Dataset for Comics Speaker Detection》。对应许可文本随选定 XML 一同提供。
- 许可只覆盖上述标注，不改变底层 Manga109 漫画页的访问与再分发限制。

## 官方来源

- [《ブラックジャックによろしく》フリーダウンロード（電書バト）](https://densho810.com/free/) — 作者官方免费分发页与利用规约
- [Pepper&Carrot E04 Japanese source page](https://www.peppercarrot.com/ja/webcomic/ep04_Stroke-of-genius__sources.html)
- [Pepper&Carrot E20 Japanese source page](https://www.peppercarrot.com/ja/webcomic/ep20_The-Picnic__sources.html)
- [Manga109 public annotations](https://github.com/manga109/public-annotations)
- [JMangaBench_Mixed](https://github.com/muscgab/JMangaBench_Mixed)
- [Manga109 official project and access terms](https://manga109.github.io/manga109-project-website/en/)
