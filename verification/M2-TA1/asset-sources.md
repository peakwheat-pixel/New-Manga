# M2-TA1 来源、许可与素材状态

核对日期：2026-09-29。用户同意本机本地测试；该同意不替代数据提供方访问审批或许可，也不允许将受限图像提交 Git。

| 素材 | 当前状态 | 获取/授权说明 | Git / 再分发 |
|---|---|---|---|
| KO Cleaned Webtoon K01–K10 | **READY**：10 cases、80 files、884,913,245 bytes；PNG CRC 与 JSON 校验通过 | 固定 `examples/` 子路径可公开访问；用户授权本机测试 | 底层图像仍受原权利人版权限制，禁止提交/再分发；源卡片将 CC BY-NC 用于注释/metadata。见 [dataset card](https://huggingface.co/datasets/Vasyanator2/cleaned_webtoon_dataset/blob/main/README.md)。 |
| KO Pepper&Carrot 8 页 | **MISSING**：case 和来源 URL 已登记，素材未下载 | 页面 HEAD 可达；页面所示来源为 CC BY 4.0，下载/逐文件核验尚未做 | 许可标注不等于已取得本地文件；当前保守保持 `redistributable=false`。见 [E06 source page](https://www.peppercarrot.com/kr/webcomic-sources/ep06_The-Potion-Contest.html)。 |
| JA Manga109 selected 37 titles | **BLOCKED_BY_ASSET_ACCESS**：本机无获批 ZIP/token；10 个 smoke case 实时报 `MISSING_GATED_ASSET` | 用户已授权本机测试，但 Hugging Face 页面要求单独访问批准；工具只接受用户已取得的官方 ZIP，不自动登录/下载。见 [official gated page](https://huggingface.co/datasets/hal-utokyo/Manga109)、[official API](https://github.com/manga109/manga109api)。 |
| JMangaBench_Mixed | **BLOCKED_BY_ASSET_ACCESS**（可用 benchmark 图像未取得） | 项目仓库公开可达；当前构建路径需另行取得 Manga109-s 图像 | 未下载数据包/图片；不提交受限漫画图像。见 [JMangaBench_Mixed](https://github.com/muscgab/JMangaBench_Mixed)。 |
| COO SFX | **PARTIAL**：公开来源已登记，配套图像未取得 | 公开 annotation 来源不意味着底层 Manga109 原图可用 | 标注与图像许可分别判断；原图 gated。见 [Manga109 public annotations](https://github.com/manga109/public-annotations)。 |
| Manga109Dialog | **PARTIAL**：公开来源已登记，配套图像未取得 | 公开 annotation 来源不意味着底层 Manga109 原图可用 | 标注与图像许可分别判断；原图 gated。见 [Manga109 public annotations](https://github.com/manga109/public-annotations)。 |
| Text Mask | **MISSING**：未下载 | Zenodo 当前记录列两份合计约 19.2 MB 文件；全版本 8.6 GB 统计不是当前文件体积。底层漫画图像权利链未确认。见 [Zenodo record](https://zenodo.org/records/4511796)。 | 不下载、不进入 Git，待明确可用权利依据。 |
| Open Ground Truth / Pepper&Carrot | **MISSING**：8 个 source cases 登记，页面文件未取回 | 公开页面可达；源码图像仍须逐项遵循 CC BY 4.0 条件 | 当前未把页面图像打包进仓库。 |
| AIHub KO | **BLOCKED_BY_ASSET_ACCESS** | 当前 HEAD 返回 HTTP 403；不据此判断账号授权状态 | 未下载。 |

项目资产目录内的 `.gitignore` 排除所有 JA/KO 数据文件；仅保留占位 `.gitkeep`、规则和清单。所有外部 benchmark 的真实运行均为 `NOT_RUN`，直到所需数据以合法方式取得并实际执行。
