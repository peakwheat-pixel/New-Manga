# T1.1.1 作者验证记录（ZCode）

> 作者自验证据，供 Codex 非作者 Review 使用。基线 `1fa5f893649ec3c9f13f0823aca838548d863393`，
> 分支 `agent/zcode/T1.1.1-production-text-detector`。选型依据：
> `doc/research/T1.1.1-detector-evaluation.md`（SELECTED docTR fast_base，
> commit `ed607b7` @ `agent/deepseek/T1.1.1-detector-evaluation`，22/22 评估证据）。
>
> **修订轮（R2）**：本文件在首轮交付（delivery head `4a1ed6ca`，Handoff
> `doc/handoffs/T1.1.1-zcode-handoff-865074f.md`）之后，按 Codex Review 的
> 6 个 blocker 修订。修订内容与对应验证见 §9；§1–§8 中已更新的数字以
> 本轮复测为准。

## 1. 环境

| 项 | 值 |
|---|---|
| OS | Windows 11 `10.0.26200` x64 |
| Python | 3.12.3（两个 venv 均同版本） |
| 实现 venv | `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312`：python-doctr 1.1.0、torch 2.14.0+cpu、torchvision 0.29.0 |
| 基线 venv（无 docTR） | `G:/CODEX/New Manga.task-envs/TASK-012-py312`：基线 requirements，无 torch/doctr/numpy |
| GPU venv | `G:/CODEX/New Manga.task-envs/T1.1.1-gpu-py312`：torch 2.11.0+cu128、torchvision 0.26.0+cu128、python-doctr 1.1.0、PySide6_Essentials 6.11.2（RTX 5070 Ti） |
| 权重文件 | `C:\Users\49745\.cache\doctr\models\fast_base-688a8b34.pt`，65,814,772 B（R2 更正：首轮误记 65,815,552 B；以 SHA-256 与 pin 匹配时的实测字节数为准） |
| 权重 SHA-256 | `688a8b3489e9f5d0290c476c6272ec3b18de3ee646c8a0dc158203b1a9c62ace`（安装前后均校验，脚本 `verification/T1.1.1/scripts/fetch_doctr_weights.py`） |

## 2. 测试命令与结果（原文口径）

三条命令均在 worktree
`G:\CODEX\New Manga.worktrees\T1.1.1-production-text-detector` 下执行，
`git status` 干净（除本任务文件）。

### 命令 A — T1.1.1 专项（R2：46 项，实现 venv）

```
PYTHONPATH=src "G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" \
  -m pytest tests/providers/test_detection_doctr.py \
            tests/providers/test_detection_doctr_real.py \
            tests/providers/test_detector_assembly.py \
            tests/providers/test_detect_seam_t111.py \
  -q -p no:cacheprovider
```

结果（R2 复测）：`46 passed`（21 单元 fail-closed/merge-policy/clipping、
2 真实 CPU 推理、1 装配 fail-closed、22 seam 检查）。退出码 0。
相对首轮 +5：水平/垂直阈值判别、padding 增长、pad 后页界 clip、
detect 路径页界 clip（§9 blocker 1/2/6）。

### 命令 B — 全量（实现 venv，含 docTR）

```
PYTHONPATH=src "G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" \
  -m pytest tests -q -p no:cacheprovider
```

结果：`1 failed, 1071 passed`。唯一失败
`tests/providers/test_registry_readiness.py::test_no_model_runtime_is_installed_in_this_environment`
—— 该测试断言*当前环境没有 torch/numpy*（TASK-019 BLOCKED 分类的环境证据），
在装了 docTR 的实现 venv 中必然失败。这是预期的环境差异，不是回归；
该断言在基线环境中仍成立（见命令 C）。

### 命令 C — 全量（基线 venv，无 docTR）

```
PYTHONPATH=src "G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe" \
  -m pytest tests -q -p no:cacheprovider
```

结果：`1046 passed, 4 skipped`，退出码 0。相对基线 1031：无回归。
- +14 单元 + 1 装配测试通过：装配后 app 仍可启动，detect fail-closed 为
  `PROVIDER_NOT_CONFIGURED`（与 `detector=None` 同缺口），不发明 Region；
- 4 skipped：`test_detection_doctr_real.py` 与 `test_detect_seam_t111.py`
  整模块 skip（`importorskip("doctr")`），以及 2 个位于 torch 探测之后的
  fail-closed rung 单元测试（`importorskip("torch")`）。

### 命令 D — T1.1.1 专项（GPU venv，CUDA）

与命令 A 同四文件，venv 换 GPU venv 并设 `NEW_MANGA_DOCTR_DEVICE=cuda`
（命令原文见 §5.1）。结果：**41 passed**，退出码 0。

## 3. Seam 检查矩阵（22 项）

`tests/providers/t111_support.py::SEAM_CHECK_MATRIX`，四样本
（jp-horizontal / jp-vertical / la-horizontal / no-text，与评估 harness
同几何、SHA 记录于评估文档）× 每样本 7 项，加 1 项 no-text typed failure：

真实 SQLite + 生产 pipeline（`assemble_services` 装配的真实 handler、
`RegionEditingService.create_region` + `RegionOrigin.MACHINE`）路径上验证：
候选 Region 数与持久化、reading_order 连续、polygon 在页界内、
GT 气泡中心命中、provenance 记录 provider/model/device、
源 PNG SHA-256 前后一致、no-text 页 `INVALID_INPUT` typed failure。

## 4. 生产帧契约说明（重要）

`bootstrap.app` 的 `page_frame` 返回 **raw 像素**（`rgb32`，QImage
Format_RGB32 小端 BGRA），`handle_detect` 原样传入
`DetectionRequest.image_bytes`；`ports/detection/ports.py` 的 docstring
"encoded bytes" 与生产实现不符（该文件属本任务禁改清单，未修改）。
adapter 按 raw 帧处理：rgb32（BGRA→RGB）/ rgb24 双模式，字节长度不匹配
即 typed `PROVIDER_INPUT`，绝不猜测。seam 支撑类
`ManagedPngPageImageSource` 与生产同样产出 rgb32。

## 5. GPU 验证

见 §5.1（cu128 wheel 单独安装于一次性 venv
`G:/CODEX/New Manga.task-envs/T1.1.1-gpu-py312`，不改实现 venv 的
CPU pin；requirements 保持 PyPI CPU 构建，GPU 打包决策属 T3.2.1）。

## 5.1 GPU 结果：PASS

一次性 venv `G:/CODEX/New Manga.task-envs/T1.1.1-gpu-py312`
（torch 2.11.0+cu128、torchvision 0.26.0+cu128、python-doctr 1.1.0、
PySide6_Essentials 6.11.2、Py 3.12.3）。cu128 wheel 由 curl 断点续传
下载后本地安装（pip 24.0 一次性下载三次损坏；断点续传一次成功）。
GPU：NVIDIA GeForce RTX 5070 Ti，`torch.cuda.is_available()` = True。

命令（同 §2 命令 A，venv 与设备换为 GPU）：

```
PYTHONPATH=src NEW_MANGA_DOCTR_DEVICE=cuda \
"G:/CODEX/New Manga.task-envs/T1.1.1-gpu-py312/Scripts/python.exe" \
  -m pytest tests/providers/test_detection_doctr.py \
            tests/providers/test_detection_doctr_real.py \
            tests/providers/test_detector_assembly.py \
            tests/providers/test_detect_seam_t111.py \
  -q -p no:cacheprovider
```

结果：**41 passed**（22 项 seam 检查以 CUDA 推理运行）。

真实素材 GPU 批跑（`real_material_check.py --device cuda`，
数值证据 `real-material/results-gpu.json`，SHA-256
`df1f18a8cb4a8a958789a9c6964b70ad7ce4a165a76b40b40a53256174d97fa9`）：

| 项 | CPU（impl venv） | GPU（RTX 5070 Ti） |
|---|---|---|
| 169 页总耗时 | 124.4 s | **13.2 s**（页均 ~78 ms） |
| 候选块总数 | 4,333 | 4,336 |
| 页均置信度 | 0.6271 | 0.6270 |
| 零候选页 | 091、155 | 091、155（相同） |
| 块数不一致页 | — | 仅 2 页差 1–2 块（070、081，浮点阈值边界） |

单页（1350×1920）显存峰值：522.6 MiB allocated / 830.0 MiB reserved
（`torch.cuda.max_memory_*`，页 168），16 GB 卡余量充足。

CPU 与 GPU 结果一致性良好；差异均为检测阈值边界的浮点效应，符合预期。

## 6. 真实漫画质量验证

素材：用户提供的商业日漫单行本卷册 `G:\CODEX\New Manga\material\17`
（169 页 JPG，1350×1920，含灰度页）。**只读访问**；带框标注图写在仓库外
（`G:\CODEX\New Manga.task-envs\T1.1.1-work\t111-real-material\`，9 张），
版权像素不入库；入库证据只有数值 JSON
（`verification/T1.1.1/real-material/results.json`）。

命令：

```
PYTHONPATH=src "G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" \
  verification/T1.1.1/scripts/real_material_check.py \
  --material "G:/CODEX/New Manga/material/17" \
  --out verification/T1.1.1/real-material/results.json --device cpu
```

结果（CPU，fast_base 冻结策略）：

| 项 | 值 |
|---|---|
| 推理成功页数 | 169 / 169（0 异常） |
| 候选块总数 / 均值 | 4,333 / 每页 25.64 |
| 整体平均置信度 | 0.6271（页均最低 0.3707，最高 0.8568） |
| 零候选页 | 2 页（091、155，目视为无文字页面） |
| 单页耗时 | 稳态 ~740 ms（首页 4.4 s 含引擎构建） |

目视抽查（git 外标注图）：典型剧情内页的竖排日文对话气泡全部检出且
框与气泡对齐，页码检出，无明显乱框；封面页的英文小字/出版社名/职员表
检出准确，但封面书法体艺术字大标题未检出 —— 与评估阶段 `art-text`
边界的结论一致（本任务不做艺术字专项）。

以上为该冻结策略在真实素材上的**观察记录**，不构成产品准确率验收；
阈值类验收属后续 slice。

`results.json` SHA-256：
`660d7aed919b39e2e906306c8b3828f945bf17c0b2bfca0dc160162111690a6c`
（25,113 B；仅数值与页名，无像素）。

## 7. 合规摘要（R2：原始证据留档于 `verification/T1.1.1/compliance/`）

R2 按 Review blocker 4 将可复核证据 fetch 留档（每份文件附来源 URL、
fetch 日期与 SHA-256，汇总见 `compliance/compliance.md`）：

- `compliance/doctr-v1.1.0-LICENSE`：docTR v1.1.0 上游 LICENSE 全文
  （Apache-2.0）；
- `compliance/doctr-v1.1.0-README.md`：§License 声明；
- `compliance/doctr-v1.1.0-docs-using_models.rst`：官方文档对预训练
  权重的加载/许可说明；
- `compliance/doctr-v1.1.0-docs-datasets.rst`、
  `compliance/doctr-v1.1.0-docs-sharing_models.rst`：数据集与模型
  分发条款的官方表述；
- `compliance/pypi-python-doctr-1.1.0.json`：PyPI 发布元数据
  （license 字段）。

结论边界：上游对仓库整体适用 Apache-2.0，未附单独权重许可文本；
本任务仅消费权重做本地前向推理，不分发数据集；商用许可裁决不在
法务授权范围内，见 `compliance/compliance.md` 的结论与限制节。

运行时零下载不变：adapter 只加载本地权重文件；缺失即
`PROVIDER_NOT_CONFIGURED`，SHA 不符即 `PROVIDER_FAILED`，
无任何网络回退路径（`_build_engine` 不接受 URL）。

## 8. 未验证项 / 已知限制

- 真实素材上的检测率为观察记录而非验收阈值（§6）；封面书法体
  艺术字标题未检出（与评估阶段 art-text 边界一致）；
- GPU 打包（requirements 固定 CUDA wheel）仍属 T3.2.1；本任务在
  一次性 venv 完成了 GPU 运行验证（§5.1），requirements 不变；
- `detect` 的并发/多线程行为未专项测试（与既有 provider 同假设，
  engine 实例挂装配单例）；
- 长图 tile 化未压测（本次最大页 1350×1920：CPU ~740 ms /
  GPU ~55 ms / 显存峰值 523 MiB）；
- Python 3.12 / Windows 验证覆盖 impl、基线、GPU 三个 venv；其他
  Python 版本不在本任务范围。

## 9. R2 修订记录（Codex Review 6 blockers → 修复与证据）

首轮 delivery head `4a1ed6ca` 收到 Codex Review 6 个 blocker，逐项修复：

| # | blocker | 修复 | 证据 |
|---|---|---|---|
| 1 | `MERGE_HORIZONTAL_TOLERANCE_PX` 定义未使用 | `cluster_words_into_blocks` 水平判据改为实际计算 `gap = max(x0_a, x0_b) - min(x1_a, x1_b)` 并与常量 8.0 比较（`h_near`） | `src/infrastructure/providers/detection_doctr.py`；判别测试 `test_horizontal_gap_threshold_is_discriminative`（gap 8.0 合并 / 8.01 分开） |
| 2 | padding 后 polygon 未做页界 clip | pad 后逐顶点 `min(max(p, 0), page_w/h)` clip 到页界；`page_size=None` 保持旧行为（仅单元路径） | `test_padded_polygon_is_clipped_to_the_page`；`TestDetectPathClipping::test_detect_never_returns_polygons_past_the_page`（detect 路径 fake predictor 注入越界归一化框，断言输出 polygon 全在页内） |
| 3 | torch/torchvision 未固定、packaging choice 不明 | `requirements.txt` 追加 `python-doctr==1.1.0`、`torch==2.14.0`、`torchvision==0.29.0`，注释声明 PyPI wheel = CPU 构建为本任务支持配置，CUDA wheel 属 T3.2.1 | `requirements.txt` diff；§5.1 GPU 以一次性 venv 验证，不改 CPU pin |
| 4 | license/权重/训练数据合规证据不可复核 | 新建 `verification/T1.1.1/compliance/`：上游 LICENSE 全文、README §License、using_models/datasets/sharing_models 官方文档、PyPI 元数据，每份附 URL+日期+SHA-256，汇总 `compliance.md` | §7；`compliance/compliance.md` |
| 5 | 权重 fetch 默认路径与 bootstrap 默认查找路径不一致 | `fetch_doctr_weights.py` 目标解析改为：`NEWMANGA_DETECTOR_WEIGHTS` env（与 bootstrap 同一变量，精确文件路径）→ `--dest <dir>` → 默认 `./models/detector/`（与 bootstrap `<data root>/models/detector/` 布局对齐） | 脚本 diff；env 与 `--dest` 两条路径实测 `already fetched and verified`，退出码 0 |
| 6 | 阈值/padding/clip 缺判别测试 | +5 判别测试：水平 gap 8.0/8.01、垂直中心差 14.0/14.1（median 20 → tol 14）、pad +6px 边界、pad 后 clip（有/无 page_size）、detect 路径页界 | `tests/providers/test_detection_doctr.py`；命令 A 41→46 |

垂直阈值判别测试的依据：两词高度 20px，`max(20 * 0.7, 8) = 14.0`，
中心差 14.0 合并、14.1 分开，覆盖 `MERGE_VERTICAL_FACTOR` 与
`MERGE_MIN_TOLERANCE_PX` 的合流点。

## 10. R2 验证记录总表

| 项 | 结果 | 退出码 |
|---|---|---|
| T1.1.1 CPU 专项（命令 A，46 项） | 46 passed | 0 |
| T1.1.1 GPU 专项（命令 D，46 项，CUDA） | 46 passed | 0 |
| `python -m compileall src tests` | 通过 | 0 |
| bootstrap smoke（装配 → detect → SQLite） | `BOOTSTRAP_DETECT_SQLITE_OK rows: 3 provider: local-doctr doctr/fast_base` | 0 |
| `git diff --check`（空白错误） | 干净 | 0 |
| 权重 SHA-256 | `688a8b34…c62ace`，65,814,772 B，与 pin 一致 | 0 |
| production bootstrap → detect → SQLite | 3 Region 落库；provenance provider=`local-doctr`、model=`doctr/fast_base`、coordinate=`page-global`、candidate_count=3 | 0 |
| source protection（素材 169 文件） | aggregate SHA `6038374326eb819d199c897dc008ec3ac8c08b42cbff79cfa0252fd8bc0f03cb`、总字节 100,434,899、newest mtime 978188400（原始时间戳，未触碰） | 0 |
| full pytest（impl venv） | 见 §10.1 | — |
| full pytest（基线 venv TASK-012） | 见 §10.1 | — |

### 10.1 全量结果与一个既有顺序敏感缺陷（base 对照实证）

- 实现 venv 全量（R2 工作树）：`2 failed, 1075 passed`（三次运行均同）。
  失败 1：`tests/providers/test_registry_readiness.py::
  test_no_model_runtime_is_installed_in_this_environment` —— 预期的
  环境证据测试（该 venv 装有 torch，断言必然失败），非回归。
  失败 2：`tests/reading_export/test_viewmodels.py::
  test_start_export_completes_and_updates_history` —— 顺序敏感，见下。
- 基线 venv 全量（R2 工作树）：`1 failed, 1049 passed, 5 skipped`。
  唯一失败仍是同一个 export 测试（该 venv 无 numpy/torch，
  registry_readiness 断言成立故通过；5 skipped = real/seam 整模块 +
  torch 后置 rung + numpy 后置 clip 测试）。
- **base 对照（决定性）**：`git stash` R2 改动后，在首轮 delivery head
  `4a1ed6ca` 的干净工作树上重跑同一命令 →
  `2 failed, 1070 passed`，失败项与 R2 完全相同（含 export 测试）。
  1072 + 5（R2 新增测试）= 1077，项数吻合。**该 export 失败在
  R2 改动之前即存在，与本轮修订无关**；首轮全量的通过是竞态未触发。
- 缩小范围：单独 `pytest tests/reading_export/test_viewmodels.py` →
  `15 passed`（多次）；`pytest tests/providers
  tests/reading_export/test_viewmodels.py` → `234 passed, 1 failed`
  （唯一失败为 registry_readiness 环境断言，export 通过）。

失败机理（R2 全量 traceback，原文）：`running=False`、
`statusMessage='导出完成：…result.zip'`、`history=1` 均已就绪，但
`exportFinished` 信号接收列表为空（`assert 0 == 1`，`len([]) == 1`）——
完成状态已发布而信号未送达，是完成路径上信号投递与
`pump_until` 停止条件之间的时序竞态，属 `tests/reading_export` /
export VM 的既有问题。`tests/reading_export/**` 与 export VM 均不在
R2 授权修改路径内，本任务不修改；建议作为独立缺陷交由该文件责任方
或 Codex 裁决归属。
