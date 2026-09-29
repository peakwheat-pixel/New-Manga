# M2-TA2C 实施验证（固定实现 `2e9797013dcb73280462a7b34390abcb2be12977`）

环境：Windows PowerShell；Python `C:/Python314/python.exe`；Task branch `agent/codex/M2-TA2C-no-hf-assets`；Git common directory `G:/CODEX/New Manga/.git`。下列 raw log 含实际命令、shell/Python、被测 HEAD 与 EXIT。`READY` 仅表示资产完整性；应用级 Pipeline 全部 `NOT_RUN`。

| 命令/步骤 | EXIT | 结果与 raw log |
|---|---:|---|
| `python -m pytest tests/m2_test_assets -q` | 0 | 25 passed；含 JA/KO 共用 schema、唯一 Case/source ID、Windows 路径、原子/重复/离线/截断下载、ZIP CRC/路径、SHA 漂移测试；[log](pytest-assets.log) |
| `assets.py list --level smoke` | 0 | L0 20 `READY`，JA10 + KO10；inventory 92 checked / 0 missing / 0 failures；[log](asset-cli.log) |
| `assets.py verify --language ja --level smoke` | 0 | JA 10 `READY`；[log](asset-cli.log) |
| `assets.py verify --language ko --level smoke` | 0 | 固定 KO Webtoon 10 `READY`；[log](asset-cli.log) |
| `assets.py verify --language ko --level regression --case-id K11 --case-id K12 --case-id K13` | 0 | 新 KO Pepper&Carrot 3 `READY`；[log](asset-cli.log) |
| `assets.py missing --level regression` | 0 | 68 定义：23 `READY`、8 `MISSING`、37 `MISSING_GATED_ASSET`；报告命令本身正常退出，缺失项不冒充通过；[log](asset-cli.log) |
| `assets.py download --language ko --level regression --case-id K11 --case-id K12 --case-id K13`（重复） | 0 | downloaded=0 / existing=6 / failures=0；第一次真实下载为 4 个文件，因 3 Case 共用 1 ZIP，实际输出未保留 raw log；文件哈希和当前复验可查 inventory；[log](asset-cli.log) |
| `assets.py download --language ja --level smoke`（重复） | 0 | downloaded=0 / existing=20；[log](asset-cli.log) |
| `assets.py download --language ko --level smoke`（重复） | 0 | downloaded=0 / existing=80；未从 HF 重取 844 MiB；[log](asset-cli.log) |
| manifest/local status probe | 0 | 68 唯一 ID；L0 20/20；L1/L2 68 定义、23 READY、8 missing、37 gated；577 个应用 Pipeline 段均 `NOT_RUN`；[log](manifest-status-check.log) |
| `python -m pytest tests/m2_acceptance -q --tb=no` | 1 | `BASELINE_FAILURE`：与 Task claim 前同一组 8 failed / 24 passed / 3 skipped，用例名完全相同；[before](acceptance-baseline.log)、[after](acceptance-implementation.log) |
| `python -m pytest tests/core -q --tb=short` | 2 | `BLOCKED_BY_ENV`：PySide6 缺失造成 4 collection errors、1 skipped；与素材变更无关；[log](core-environment-detail.log) |
| `git ls-files` media filter / `git check-ignore --no-index -v` / `git diff --check HEAD^ HEAD` | 0 / 0 / 0 | tracked media=0；KO/JA 图像与 KO ZIP 均命中 ignore；diff 无空白问题；[log](git-license-check.log) |
| 官方来源 HEAD probe | 0 | 九个官方入口本次均返回 200；仅证明入口可访问，不证明许可或实际数据已取得；[log](source-url-head.log) |

本次新增被忽略的 KO Pepper&Carrot E04P02/P03/P07 三张 JPEG 和一个官方 language-pack ZIP，共 4 个本地文件 / 16,292,579 bytes。SHA-256、来源/许可和 GT 范围见 `../../test_assets/comic_golden_suite/manifests/local_asset_inventory.json`。原有 JA 12 媒体与 KO Webtoon 80 文件均由已完成 Task 的主工作区同步到本 worktree，文件数量与 byte size 一致；未重复网络下载 KO Webtoon。KO Webtoon 每文件 SHA-256 审计清单在 [ko-webtoon-audit.json](ko-webtoon-audit.json)。

OpenMantra 由于 CC BY-NC 使用范围不明保持 `MISSING`；eBDtheque 注册、Manga109、JMangaBench 图像和 TextMasks 配对图像均未取得；Artificial Manga 只有上游代码/配方，Public Domain Japan 待人工选取。L2 全量 Benchmark、应用 OCR/Detection/Translation/Inpainting/Typesetting/Webtoon slice-and-reassembly 均 `NOT_RUN`。
