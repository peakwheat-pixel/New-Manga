# M2-TA1 仓库与附件审计

日期：2026-09-29。仓库基线：`40ce1f91cc41a8ed13e10e397fe0ddab43d9f5be`。详情按当日 Task worktree 实测记录。

## 仓库现状

- 已阅读根目录 `AGENTS.md`、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`、`doc/STATUS.md`、`doc/09_COLLABORATION.md`、Task/Handoff/Review 模板、`doc/fixtures/MANIFEST.md`、`tests/m2_acceptance` 与 pytest 配置。
- 基线无 `test_assets/`。`doc/fixtures/MANIFEST.md` 管理通用合成/容量 fixture，不包含漫画 case catalog 或漫画素材 loader；因此采用 `test_assets/comic_golden_suite/`，不复制既有 fixture 体系，也不接入生产 Schema、Pipeline 或 UI。
- 新架构验收入口是 `tests/m2_acceptance`。Legacy `tests/core` 仅作环境诊断，不作为本 Task 新架构 Gate。
- Task worktree 仅改测试资产、测试、Task 证据及导航/状态文档；主工作区原有未提交文件保持原样。

## 附件内容核验

- ZIP 清单：144 entries、68 files、31,617 bytes uncompressed。包含 KO 固定 10 case、Pepper&Carrot 8 case、Manga109 37 title 的占位 README，以及 manifests、CSV、`client_import_manifest.json`、README、版权说明和脚本；未包含漫画原图。
- 统一目录/分类计划有价值，但原脚本不直接执行：`download_assets.py` 会自动安装 `huggingface_hub`、将 token 作为 `--hf-token` 参数、对外部 ZIP 使用 `extractall`，缺少有界大小/完整性检查；PowerShell installer 使用 `Copy-Item -Force` 覆盖目标内容；启动器还会绕过 PowerShell execution policy。因而只移植清单意图，改用无依赖安装、显式归档导入、路径/大小/CRC 校验与无覆盖写入的标准库实现。
- 已完整检查 `韩漫_KO`、`日漫_JA`、`manifests`、`tools`、`client_import_manifest.json`、`素材索引.csv`、`来源与版权说明.md`、`README_先看.md`；从未执行附件脚本/安装器。
- Manga109 附件提供 37 个标题，不能按 README 中较小的标题数误写；实际统一 manifest 有 55 个 case：KO 10 Webtoon + 8 Pepper&Carrot + JA 37 Manga109。L0 是 KO 10 + JA 10；L1 仍是 55 个定义，低于 100–150 目标；L2 仅登记外部 benchmark，不进日常运行。
- 独立 Review 发现附件建议代码中的 Manga109 文件名假设不适用于真实归档。官方 API 示例是 `images/ARMS/003.jpg`，2026-05-21 公开布局示例是 `images/ARMS/000.jpg`。导入器按数字页名并以 XML `page@index` 严格匹配，合成 ZIP 测试复现官方命名。来源：[Manga109 API](https://github.com/manga109/manga109api)、[Manga109 layout example](https://huggingface.co/datasets/mayocream/manga109-segmentation/commit/23f4a56758fd5f8a48a3b1ff84338e290e77174e)。

## 附件 URL 检查（2026-09-29，HTTP HEAD）

| 地址 | 结果 | 解释 |
|---|---|---|
| Cleaned Webtoon 固定 case 的 Hugging Face `info.json` | HTTP 200 | 公开文件入口可达；实际 80 个文件下载成功并通过校验。 |
| Manga109 Hugging Face 数据集页 | HTTP 200 | 页面可达不表示获得 gated 原图权限；当前机器没有凭据，仍需官方审批。 |
| Pepper&Carrot E06 source page | HTTP 200 | 公开来源页可达；本次未下载页面/图像。 |
| Manga109 public annotations GitHub ZIP | HTTP 200 | 公开标注代码/包入口可达，不提供 gated 原图访问。 |
| JMangaBench_Mixed GitHub ZIP | HTTP 200 | 项目入口可达；可运行样本仍依赖单独取得的 Manga109-s 图像。 |
| Text Mask Zenodo record | HTTP 200 | 记录可达；关联图像再分发条件未确认，因此不下载。 |
| AIHub 数据页面 | HTTP 403 | 仅记录当前网络环境响应，不推断登录或授权状态。 |

HEAD 检查不代表完整资源已取回、内容已验证或权限已获批。公开归档未解压，避免运行或信任归档中的内容。
