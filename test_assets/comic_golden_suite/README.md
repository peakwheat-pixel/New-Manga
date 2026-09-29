# 漫画统一测试资产

本目录是独立于生产用户数据的 JA/KO 测试 case catalog。当前由附件清单整理出 55 个 case：10 个韩漫长条、8 个 Pepper&Carrot 韩文来源页、37 个 Manga109 选定作品。L0 Smoke 为 KO 10 + JA 10；L1 当前只有 55 个定义，低于 100–150 的目标；L2 还依赖外部 benchmark，不会由日常命令自动运行或下载。

## 目录和数据边界

- `manifests/cases.json` 是统一 JSON 清单和困难类型 taxonomy；所有路径均为相对本目录的 Windows 兼容路径。
- `韩漫_KO/`、`日漫_JA/` 是本机素材目录。其 `.gitignore` 默认排除图片、归档和其他数据文件。
- `tools/assets.py` 使用 Python 标准库；命令为 `download`、`verify`、`list`、`missing`，支持 `--language ja|ko`、`--level smoke|regression|full`。
- `READY` 表示完整的预期文件集合可用：KO Webtoon 要有 8 个文件；Manga109 导入还要求数字 JPG 页名与官方 annotation XML `page@index` 对应。`verify` 检查 PNG chunk CRC、`info.json` JSON、Manga109 JPEG/XML；不等同于人工逐页标注审查。

## 获取状态（2026-09-29）

| 来源 | 清单状态 | 本机素材 | 许可 / 边界 |
|---|---|---|---|
| KO Cleaned Webtoon 固定 10 case | READY（case 定义和 URL） | READY：10 case、80 文件、合计 884,913,245 bytes（约 844 MiB）；已通过本地结构验证 | 用户声明授权本地测试；源卡片将 CC BY-NC-4.0 用于作者注释/metadata，原画仍由权利人持有。`redistributable=false`，禁止提交 Git。 |
| KO Pepper&Carrot 8 个来源页 | READY（case 定义和来源链接） | MISSING；需逐案下载并核对文件 | 来源页标记 CC BY 4.0；当前清单保守设 `redistributable=false`，素材逐文件核验后再调整。 |
| JA Manga109 37 个选定作品 | READY（case 定义） | `MISSING_GATED_ASSET`；当前环境未发现 Hugging Face 凭据 | 按官方流程取得 gated ZIP 后，用 `download --language ja --level smoke --archive <path>` 只导入所选作品；不绕过 gated，不把原图提交 Git。用户授权已记录，但不会替代平台访问控制。 |
| JMangaBench | 外部来源已登记 | BLOCKED_BY_ASSET_ACCESS | 项目源可达；可运行 benchmark 仍需另行取得 Manga109-s 图像。 |
| COO / Manga109Dialog | 外部来源已登记 | PARTIAL（公开标注来源已登记；图片 gated） | 标注可公开取得不代表 Manga109 图像可公开再分发。 |
| Text Mask | 外部来源已登记 | MISSING（本机未下载） | 当前 Zenodo 记录列出两份合计约 19.2 MB 的 ZIP；底层图像来源与再分发许可未确认，因此不下载。 |
| AIHub KO 数据 | 外部来源已登记 | BLOCKED_BY_ASSET_ACCESS（当前环境 HTTP 403） | 403 只记录本次环境结果，不推断账号授权状态。 |

清单里 `asset_status` 是初始快照；CLI 根据本地文件实时计算状态。公开源的可达性检查不表示素材已经下载或通过内容校验。用户 2026-09-29 明确授权本机测试使用；本地使用仍按各来源条款限定，不改变 `redistributable` 字段。

## 使用

在仓库根目录运行：

```powershell
python test_assets/comic_golden_suite/tools/assets.py list --level smoke
python test_assets/comic_golden_suite/tools/assets.py missing --level smoke
python test_assets/comic_golden_suite/tools/assets.py verify --language ko --level smoke
python test_assets/comic_golden_suite/tools/assets.py download --language ko --level smoke
python test_assets/comic_golden_suite/tools/assets.py download --language ja --level smoke --archive "$env:USERPROFILE/Downloads/Manga109_released_2026_05_21.zip"
```

`download --language ko --level smoke` 是显式联网命令，只抓取这 10 个固定 case；每个文件须符合响应 `Content-Length` 和 PNG/JSON 格式校验后才会原子写入，已存在文件不覆盖。KO smoke 样本从官方 dataset `examples/` 路径取得。Pepper&Carrot 来源页列为 `MANUAL_SOURCE_REQUIRED`，尚未下载。

Manga109 不会由工具自动下载约 4.07 GB 的全量归档。先通过官方 gated 页面取得 ZIP，再用上面的 `--archive` 参数交给工具；它只导入当前 level 选择的书目，并验证 ZIP CRC、路径、JPG 和页数 annotation，拒绝路径穿越。无本地 ZIP 时报告 `BLOCKED_BY_ASSET_ACCESS`；部分导入的书目报告 `PARTIAL`，不会误报 `READY`。
