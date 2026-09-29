# M2-TA2A 实际运行结果

状态口径：`READY` 仅代表本地资产完整性；所有应用级 Pipeline 保持 `NOT_RUN`。本次执行环境为 Windows / PowerShell，Python=`C:\Python314\python.exe`。原始 stdout、stderr 和每条退出码在 `integration-checks.log`。

## 资产状态

| 来源 | 实际本地文件 | 字节数 | 状态 / 可用范围 |
|---|---:|---:|---|
| KO Cleaned Webtoon 固定集 | 80 个资产文件：70 PNG + 10 JSON，覆盖 10/10 Case | 884,913,245 | `READY`（文件完整性）；OCR / Detection / Translation / Inpainting / Typesetting / 切片重组等应用测试 `NOT_RUN` |
| Pepper&Carrot 日语本地化页面 | 10 JPEG + 2 官方 SVG language-pack ZIP | 40,284,868 | 页面素材 `READY`；E20P06/P07 有部分日文 SVG 文本层，Open Ground Truth 整体 `PARTIAL`。法国原创 webcomic 日语本地化，不是日本原创 Manga |
| COO | 37 XML + 1 license | 3,333,257 | `PARTIAL`；日语 SFX 转录/坐标标注可解析，无配对漫画图像 |
| Manga109Dialog | 37 XML + 1 license | 3,406,525 | `PARTIAL`；speaker-to-text ID 关系可解析，不含基础对白转录或配对图像 |
| Manga109 / JMangaBench_Mixed | 0 图像 | 0 本地 | `BLOCKED_BY_ASSET_ACCESS`；JMangaBench 的完整图像集依赖 Manga109-s 衍生像素 |
| Text Mask | 0 文件 | 0 本地 | `BLOCKED_BY_ASSET_ACCESS`；Zenodo 记录未声明许可且依赖 Manga109 图像 |
| OpenMantra | 0 文件 | 0 本地 | `MISSING`；上游为 CC BY-NC 4.0，项目非商业适用范围未确认，因此未取得 |

JA 本地总计 88 个文件 / 47,024,650 bytes（12 个公开漫画媒体文件 + 74 个 annotation XML + 2 个 license 文件）。所有本地文件逐文件记录 byte size 和 SHA-256；详细来源类型、许可、再分发状态、Ground Truth 和 Pipeline 映射见 `source-audit.md` 与 `test_assets/comic_golden_suite/manifests/local_asset_inventory.json`。

## 实际运行命令

| 命令 | 结果 |
|---|---|
| `python -m pytest tests/m2_test_assets -q` | `EXIT 0`；21 passed。 |
| `python test_assets/comic_golden_suite/tools/assets.py verify --language ja --level smoke` | `EXIT 0`；`READY=10`，`INVENTORY checked=88 missing=0 failures=0`。 |
| `python test_assets/comic_golden_suite/tools/assets.py list --language ja --level smoke` | `EXIT 0`；枚举 JA Smoke 10/10，inventory 校验通过。 |
| `python test_assets/comic_golden_suite/tools/assets.py missing --language ja --level smoke` | `EXIT 0`；无缺失 Case，`READY=10`。 |
| `python test_assets/comic_golden_suite/tools/assets.py download --language ja --level smoke`（重复执行） | `EXIT 0`；`downloaded=0 existing=20 gated_cases=0 failures=0`，没有重复生成文件。 |
| `python test_assets/comic_golden_suite/tools/assets.py download --language ja --level regression` | `EXIT 0`；`gated_cases=37 failures=0`，未向 gated 来源发起下载。 |
| `python test_assets/comic_golden_suite/tools/assets.py verify --language ja --level regression` | `EXIT 0`；`MISSING_GATED_ASSET=37 READY=10`，inventory 校验通过。 |
| `python test_assets/comic_golden_suite/tools/assets.py verify --language ko --level smoke` | `EXIT 0`；KO 10/10 `READY`，inventory 校验通过。 |
| 离线 verify（将 `urllib.request.urlopen` 替换为抛错函数后调用同一 CLI） | `EXIT 0`；JA 10/10 `READY`，证明校验不依赖网络。 |

## 完整性与 Git 边界

- 资产审核器重新计算 88 个文件大小与 SHA-256：0 mismatch；74 个 XML 均通过解析；2 个 ZIP 均读取所有成员并通过 CRC；65/65 Case ID 唯一。
- `git ls-files` 审核为 0 个漫画图片/归档被跟踪；12 个 JA JPEG/ZIP 全部被 `git check-ignore --no-index` 忽略。
- 76/76 个进入 Git 的 CC BY 4.0 annotation XML / license index blob 与本地源字节哈希一致（`.gitattributes` 禁止行尾转换）。KO 本地 80 个资产文件保持 ignore。
- `git diff --check` 与 `git diff --cached --check` 均 `EXIT 0`。最终集成时会在主工作区再次核验。

## 基线与未运行项

`tests/m2_acceptance` 已知基线为 `8 failed / 24 passed / 3 skipped`，状态 `BASELINE_FAILURE`；`tests/core` 因缺少 PySide6 无法 collection，状态 `BLOCKED_BY_ENV`。本 Task 未修这些无关问题，也未重跑上述两组。

OCR、Text Detection、Bubble Detection、Region、Reading Order、SFX 应用检测、Speaker Attribution、Translation、Inpainting、Typesetting、页面重新渲染及 Webtoon 临时切片/拼接均为 `NOT_RUN`。`READY` 不代表这些 Pipeline 已验证。

本次运行的原始输出与命令退出码见 `integration-checks.log`；来源实物类型、许可和不可获取原因见 `source-audit.md`。
