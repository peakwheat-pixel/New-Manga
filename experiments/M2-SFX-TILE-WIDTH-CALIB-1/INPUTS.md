# M2-SFX-TILE-WIDTH-CALIB-1 素材盘点登记（先盘点再动手）

- Task: [M2-SFX-TILE-WIDTH-CALIB-1](../../doc/tasks/M2-SFX-TILE-WIDTH-CALIB-1.md)
- 盘点日期: 2026-10-04，Owner=ZCode
- 盘点范围: `G:/CODEX/New Manga.task-envs/` 下 own-manga / train-v2 / KO 域素材树（教训「先盘点再动手」的登记面）

## 1. 盘点结论（逐树）

| 树 | 内容 | 宽≠600/690 且 aspect≥8.0 的页 |
|---|---|---|
| `sfx-synth-exp/own-manga/{1,2,3}`（6 卷：Gemu obu Famiria v15/v16、Uragirareta v12/v13、Goshujinsama v01/v02s） | 2018 张用户自有普通漫画页 | **0 页**（全部 1350x1920 / 1167x1618 / 964-987x1400 等普通宽页，aspect ~1.4） |
| `sfx-synth-exp/own-manga-candidates/` | own-manga SFX 标注链（v1 harvest 口径 2017 框 → 四层过滤 final pool 1738 框 → 558 页级样本入册 `own-manga-ingest/own_manga_manifest_records.json`） | 0 页（页图同上树；partial 140 页 / pseudo 418 页分级见 ingest_notes.md） |
| `M2-TA2B-OPEN-ASSETS-zcode/test_assets/comic_golden_suite/韩漫_KO/01_real_webtoon_cleaned_dataset`（K01-K10 × 7 个处理阶段变体 = 70 图） | KO 域全部已知长条 webtoon 页 | **0 页**——全部恰为 690 或 600 宽（690x62133~131289、600x18401），与 T5 deploy-report §3①「已知 KO case GT 页只有 600/690 宽」一致 |
| `M2-SFX-TRAIN-V2-zcode/training_data/sfx-v1/train-v2` manifest.train-v2.json（909 样本 / 2367 框；annotation_status: pseudo 418 / synthetic 324 / partial 140 / complete 27） | V2 训练集全量标注 | 0 页——aspect≥8.0 的仅 pre-k01~k10 十页，宽全部 690/600；其余 887 样本为普通宽页或 synth-r1 小尺寸切片（199-456px 宽、aspect<2） |
| `M2-DETECT-WEBTOON-DIAG` / `M2-DETECT-WEBTOON-TILING` | DSH 诊断报告/日志 | 无页图素材 |

**盘点硬结论**：真实素材中不存在「宽≠600/690 且 aspect≥8.0」的 KO/webtoon 域原生页。本 Task 价值恰在「其他宽度」，AC1 补样只能走 Task 合同两条已授权路径：①已知真值页（pre-k08/k09/k02）等比重采样合成变体；②程序生成合成页（外部树，矩形/文字块模拟 SFX）。

## 2. 评测集选样（每宽度档页数 + GT 类型登记）

| 宽度档 | 来源 | 页数 | GT 类型 | GT 框数 |
|---|---|---|---|---|
| W690 | 原生 pre-k08 + pre-k09（R2 final val，sha 对 manifest 断言） | 2 | **真实 GT**（R2 final 派生框） | 27+24=51 |
| W600 | 原生 pre-k02（R2 final test） | 1 | **真实 GT** | 3 |
| W640 | pre-k08/k09 等比 LANCZOS 缩放（640/690≈0.9275） | 2 | 重采样派生 GT（框坐标×scale 精确相似变换；像素插值损失声明） | 51 |
| W480 | pre-k08/k09 等比（480/690≈0.6957） | 2 | 重采样派生 GT | 51 |
| W320 | pre-k08/k09 等比（320/690≈0.4638） | 2 | 重采样派生 GT | 51 |
| SYNTH-384 | 程序合成长条页（外部树） | 1 | **合成精确 GT**（绘制时坐标） | ~50 |
| SYNTH-560 | 程序合成 | 1 | 合成精确 GT | ~50 |
| SYNTH-680 | 程序合成 | 1 | 合成精确 GT | ~50 |
| W800 | pre-k08 等比放大（800/690≈1.1594，域外档：宽>690 路由 letterbox） | 1 | 重采样派生 GT | 27 |
| W1024 | pre-k08 等比放大（1024/690≈1.4841，域外档） | 1 | 重采样派生 GT | 27 |

选样裁量：k08/k09 为 GT 框数最多两页（51/56 框）；k02 是唯一 600 宽原生页（3 框，页数少如实登记）。宽 640/480/320 覆盖冻结路由上限 690 以下三档（接近上限/中距/窄幅）；合成 384/560/680 三档补非重采样原生分辨率证据；800/1024 测路由边界另一侧（§3④ 跨域面）。

## 3. 自锚风险逐来源声明（directional）

1. **重采样派生 GT**：等比缩放为精确相似变换，框坐标本身无标注误差引入；但 LANCZOS 像素重采样会改变 SFX 字形边缘与相对字号（同 tile 1024 输入下，窄页 SFX 被放大更多：320 宽 tile 的 letterbox 放大倍率 3.2× vs 690 宽的 1.48×），表现变化混合「宽度档」与「有效分辨率」两个因素——本 Task 只做 directional 归因，不声称单变量因果。
2. **合成精确 GT**：矩形文字块（韩文拟声词+拉丁拟声词混排、描边+填充）与真实 KO 手写/艺术字 SFX 视觉域不同，检测器对其的绝对 conf/召回不可外推到真实页；仅用于同页 tile vs letterbox 的机械行为对照与耗时实测。字形域偏移为常量、宽度为变量，宽度轴上的相对对比仍 directional 有效。
3. **真实 GT**（W690/W600）为 R2 final 派生框（AI 审链 partial/pseudo 性质，T5 同口径），非人工逐框核实；本 Task 沿用其作为 KO 域相对参照（锚点档），登记同样的 GT 性质限制。
4. 页数少（多数档 2 页、W600 仅 1 页 3 框）：统计功效低，结论全部 directional，禁「显著」措辞。

## 4. 权重与环境

- 权重=v2b 生产 pin 原样：`G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights-v2b/yolo11s-seg.onnx`，sha256 先验断言 `944e8114…`（本 Task 无权重变更，不引入 chiqui7 对照）。
- venv=`T1.1.1-impl-py312`（Python 3.12.3 + onnxruntime-directml 1.24.4，DmlExecutionProvider，GPU 默认）；禁 CPU 跑 tile（~10s/页量级）。
- 外部树（不入 Git）：`G:/CODEX/New Manga.task-envs/M2-SFX-TILE-WIDTH-CALIB-1/`（pages + prepared manifest）。
