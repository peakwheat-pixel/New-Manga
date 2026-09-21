# T1.1.1 作者验证记录（ZCode）

> 作者自验证据，供 Codex 非作者 Review 使用。基线 `1fa5f893649ec3c9f13f0823aca838548d863393`，
> 分支 `agent/zcode/T1.1.1-production-text-detector`。选型依据：
> `doc/research/T1.1.1-detector-evaluation.md`（SELECTED docTR fast_base，
> commit `ed607b7` @ `agent/deepseek/T1.1.1-detector-evaluation`，22/22 评估证据）。

## 1. 环境

| 项 | 值 |
|---|---|
| OS | Windows 11 `10.0.26200` x64 |
| Python | 3.12.3（两个 venv 均同版本） |
| 实现 venv | `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312`：python-doctr 1.1.0、torch 2.14.0+cpu、torchvision 0.29.0 |
| 基线 venv（无 docTR） | `G:/CODEX/New Manga.task-envs/TASK-012-py312`：基线 requirements，无 torch/doctr/numpy |
| 权重文件 | `C:\Users\49745\.cache\doctr\models\fast_base-688a8b34.pt`，65,815,552 B |
| 权重 SHA-256 | `688a8b3489e9f5d0290c476c6272ec3b18de3ee646c8a0dc158203b1a9c62ace`（安装前后均校验，脚本 `verification/T1.1.1/scripts/fetch_doctr_weights.py`） |

## 2. 测试命令与结果（原文口径）

三条命令均在 worktree
`G:\CODEX\New Manga.worktrees\T1.1.1-production-text-detector` 下执行，
`git status` 干净（除本任务文件）。

### 命令 A — T1.1.1 专项（41 项，实现 venv）

```
PYTHONPATH=src "G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" \
  -m pytest tests/providers/test_detection_doctr.py \
            tests/providers/test_detection_doctr_real.py \
            tests/providers/test_detector_assembly.py \
            tests/providers/test_detect_seam_t111.py \
  -q -p no:cacheprovider
```

结果：`41 passed`（16 单元 fail-closed/merge-policy、2 真实 CPU 推理、
1 装配 fail-closed、22 seam 检查）。退出码 0。

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

## 5.1 GPU 结果：BLOCKED（网络）

cu128 wheel（torch ~2.5 GB）四次安装尝试均未成功，全部为环境网络原因，
非代码原因：

1. 官方源 `download.pytorch.org/whl/cu128` 两次下载损坏（pip SHA-256
   校验失败：expected `7c78…3a4c` got `aefa…f7`，另一次类似）；
2. `--no-cache-dir` 第三次仍损坏（expected `7c78…` got `2eb3…d3`）；
3. 清华镜像索引无 cu128 分发（`No matching distribution found`）。

一次性 venv `G:/CODEX/New Manga.task-envs/T1.1.1-gpu-py312` 已建好，
网络可用时执行
`pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cu128`
后即可用 `NEW_MANGA_DOCTR_DEVICE=cuda` 复跑命令 A 完成 GPU 验证。

已验证的设备逻辑：`_resolve_device` 的 cpu/auto/cuda/tpu 分支有单元
覆盖（tpu → `PROVIDER_INPUT`；cuda 请求但不可用 → `PROVIDER_UNAVAILABLE`
为代码路径 review，未运行验证）；GPU 打包决策本属 T3.2.1，
requirements 固定 PyPI CPU 构建不受影响。

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

## 7. 合规摘要（引评估文档，未重复核实网络源）

- `python-doctr==1.1.0`：Apache-2.0（上游 LICENSE 已在评估阶段 fetch 留档）；
- fast_base 权重：docTR 官方静态分发（doctr-static.mindee.com），
  SHA-256 与上游发布一致，见 §1；权重再分发条款随上游模型页核对；
- 运行时零下载：adapter 只加载本地权重文件；缺失即
  `PROVIDER_NOT_CONFIGURED`，SHA 不符即 `PROVIDER_FAILED`，
  无任何网络回退路径（`_build_engine` 不接受 URL）。

## 8. 未验证项 / 已知限制

- GPU 运行验证：BLOCKED（§5.1，网络下载损坏；CPU 全部验证通过，
  GPU 打包决策属 T3.2.1）；
- 真实素材上的检测率为观察记录而非验收阈值（§6）；封面书法体
  艺术字标题未检出（与评估阶段 art-text 边界一致）；
- `detect` 的并发/多线程行为未专项测试（与既有 provider 同假设，
  engine 实例挂装配单例）；
- 长图 tile 化（page 级一次性推理在大图上的显存/耗时）未压测
  （本次最大页 1350×1920 CPU ~740 ms）；
- Python 3.12 / Windows 验证覆盖 impl 与基线两个 venv；其他
  Python 版本不在本任务范围。
