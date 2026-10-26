# CORE-SLIM-1 Handoff（Core 瘦身）

- Task: `doc/tasks/CORE-SLIM-1.md`（AD-002 §3.5 预算规则）
- Branch: `task/CORE-SLIM-1`；Worktree: `G:/CODEX/New Manga.workspace/worktrees/CORE-SLIM-1`
- Base: `8d0531cfb`（卡字段同步 `a101eeda3`）；Owner: DSH（teammate `core-admin-rca`）；Reviewer: DSH（独立审查另行指定）
- Delivery head: 见本文件所在 commit 的父提交（证据 pin 以 `git log --oneline -1 <evidence-commit>` 为准）
- 未 push（按卡禁止）。

## 1. 交付摘要

| AC | 结论 | 证据 |
|---|---|---|
| AC1 PySide6 移除（口径=打包 Core 闭包零 Qt） | **MET** | `verification/CORE-SLIM-1/ac1/COMPARISON.md`、`ac1/comparison.json` |
| AC2 entry exe 去重 | **MET**（5 个 exe 合计 199.6 → 1.9 MiB；共享 `_internal`） | `verification/CORE-SLIM-1/size-report.md` §2、`ac2/bundle-before.json`/`bundle-after.json` |
| AC3 体积预算 ≤700 MiB（不含模型） | **PARTIAL**：实测 **970.1 MiB**（改前 1067.3 MiB，−97.2 MiB）；差口与取舍证据见 size-report §4 | `verification/CORE-SLIM-1/size-report.md` |
| AC4 回归 | **MET**：pytest `3 failed, 2710 passed, 9 skipped`（失败集合=基线 3 项，无新增）；`scripts/test.ps1` **102/102 passed, 0 skipped**；解码/像素等价 16/16 + PDF 2/2 | `ac4/pytest-after.log`、`ac4/scripts-test-after.log`、`ac1/COMPARISON.md` |
| AC5 门禁 | **MET**（check.ps1 PASS、证据 64-hex pin、Handoff、Record Decision） | 本文件 + 卡片 Canonical Evidence |

冻结闭包能力矩阵（AC2/AC3 前提，真实 sidecar exe）：**7/7 PASS** —— catalog_loader 播种、core_service `core.ping`（protocol 2.3）、acceptance_bridge（seed_fixture 导入 / run_pipeline 渲染 / reader_pages / export_page）、sfx_detect_probe 启动；见 `ac2/capability-smoke.json`。

## 2. 代码与配置改动（`packaging/**` 由 DSH 裁决扩权）

| 文件 | 改动 |
|---|---|
| `src/infrastructure/importing.py` | `QtImageDecoder` → `PillowImageDecoder`（保留同名兼容别名供冻结旧壳 import）；PDF 页 BGRA/BGR→PNG 改 Pillow；MOBI 页图→PNG 改 Pillow（保留 256 MiB 收紧界）；`_ALLOCATION_LIMIT_MIB`/`_ERROR_DETAIL_MAX_CHARS` 语义不变（2047 MiB 声明尺寸预检 → 先判后分配） |
| `src/infrastructure/rendering/pillow_source_style.py`（新） | `PillowSourceStyleAnalyzer`：Qt `PixelSourceStyleAnalyzer` 的行为等价移植（D06 §8 启发式逐字段一致） |
| `src/bootstrap/core_assembly.py` | `page_frame`/`region_crop`/`page_png`/`_render_content_decoder` 由 QImage 改 Pillow（rgb32 = BGRA little-endian + alpha 0xff 字节级一致） |
| `src/bootstrap/core_service.py` | 注入 `PillowImageDecoder` |
| `src/bootstrap/acceptance_bridge.py` | 注入生产同级 Pillow 适配器（解码/字体/排版/合成/风格），删除 QGuiApplication；闭包不再需要 Qt |
| `requirements.txt` | 删 `PySide6_Essentials`/`shiboken6`；新增直接依赖 `pillow==12.3.0` |
| `packaging/m2ac5/core_sidecar.spec` | `EXCLUDED` += `PySide6`/`shiboken6`；每 entry `Analysis(noarchive=True)`（纯 py → 共享 `_internal/*.pyc`，避免 3×65 MiB 重复 PYZ）；closure 断言适配 `_modules_outside_pyz`；docstring 记录 CORE-SLIM-1 事实 |
| `packaging/m2ac5/requirements-build.txt` | 删除 PySide6/shiboken6 pin 与“acceptance 硬依赖 Qt”的过时注释 |
| `tests/library/test_production_adapters.py` | Qt 专用断言改写为 Pillow 语义（MIME fallback / 分配上限先判后分配 / detail 截断），移除 `importorskip("PySide6")` |
| `tests/import_formats/test_decode_format_matrix.py`（新） | PNG/BMP/JPEG/WebP/TIFF/GIF + 多帧 GIF/动画 WebP/多页 TIFF/AVIF/PDF 2 页矩阵 |
| `tests/infrastructure/test_pillow_source_style.py`（新） | Pillow 分析器行为 + 与 Qt 实现逐字段一致 + 模块无 Qt import |

## 3. 体积（测量口径：整树 − `models/`）

| 项 | before | after |
|---|---|---|
| 整树 | 1269.8 MiB | 1172.6 MiB |
| 5 个 entry exe | 199.6 MiB | **1.9 MiB**（每个 ~0.38 MiB，纯引导器） |
| `_internal` | 825.8 MiB | 926.3 MiB（+100.5：`.pyc` 未压缩化，但去掉了 3 份重复 PYZ） |
| 闭包内 Qt | PySide6 61.2 MiB | **0** |
| **Core 运行时（不含模型）** | 1067.3 MiB | **970.1 MiB（−97.2）** |

- 去重机制：`noarchive=True` → `_internal` 下 8767 个共享 `.pyc`（164.1 MiB），5 entry 同一路径只留一份。
- AC3 未达 700 MiB 的原因（不伪造、不改口径）：剩余体积由**能力必需**的 ML 栈构成（torch 365 / cv2 112 / scipy 70 / onnxruntime 63 / transformers 39 MiB）。build venv 实测 `import doctr,torch,torchvision,transformers,onnxruntime,cv2` 后 `cv2/scipy/h5py/shapely` 已在 `sys.modules`（硬依赖，排除即删能力）；即便强排 cv2+scipy 也只能到 ~788 MiB。达标需把检测链改为 ONNX 化/裁剪 torch 的独立能力裁决。

## 4. 回归证据

- `python -m pytest -q -p no:warnings`：`3 failed, 2710 passed, 9 skipped in 210.59s`（基线 3F/2691P/9S；新失败=0，新增 19 个 AC1 用例；另 1 个基线 flaky 本次通过）。
- `apps/desktop-avalonia/scripts/test.ps1 -SidecarDirectory <新构建无标签副本>`：`TEST PASS (Debug): 102/102 passed, 0 skipped`（真实 sidecar 集成；AC11 Low-IL 影响用无标签副本规避）。
- 解码/像素等价：`ac1/COMPARISON.md` —— 解码矩阵 11/12（唯一差异 = AVIF 能力**增益**，Qt 闭包无 AVIF 插件）；`page_frame` 字节级相等；page/crop/bridge PNG 与 PDF 2 页**逐像素相等**（PNG 字节差异仅来自编码器，已在报告解释）。

## 5. Record Decision

1. **解码器替代方案**：Pillow 12.3 + pypdfium2 取代 Qt 图像插件族。理由：闭包 −61 MiB、去掉 LGPL Qt 运行时、能力不减（HEIC/HEIF 两侧均不支持；AVIF 反而变为可用）；像素等价已有证据；失败语义（typed error、300 字符 detail 上限、2047 MiB 声明尺寸预检、MOBI 256 MiB 收紧）逐条保留。
2. **打包策略**：`noarchive=True`（共享 `_internal/.pyc`）而不是合并入口。理由：不改 sidecar 启动姿势/argv/协议（卡禁止），同时消除 3 份重复 PYZ（−197.7 MiB exe）；代价是 `.pyc` 未压缩（`_internal` +100.5 MiB），净收益 −97.2 MiB。**不采用** cv2/scipy 等 excludes：实测为导入期硬依赖，排除即删能力；且全排后仍 >700 MiB。
3. **legacy QML**：`src/bootstrap/app.py`、`src/ui/**` 与 ~45 个旧测试**原位冻结、不打包、不改**（与 S5-C 口径一致）；`QtImageDecoder` 名保留为 Pillow 实现的兼容别名，避免破坏冻结旧壳的 import 与 pytest 计数。
4. **AC3 判 PARTIAL**：按卡规则（允许 excludes 但不得删能力）实测 970.1 MiB、缺口 270.1 MiB 全部由能力必需的 ML 栈构成，故如实记 PARTIAL 并留证据，未改预算口径。

## 6. 遗留 / 后续

- **AC3 达标**属于新的能力/架构决策（检测链 ONNX 化或 torch 依赖裁剪），建议另开 Task（例：`CORE-SLIM-2`）并由 DSH 裁决预算优先级。
- 构建 venv `G:\CODEX\New Manga.task-envs\m2ac5-build` 仍装有 PySide6（历史遗留）；`requirements-build.txt` 已移除 pin，下一次干净建 venv 即自然消失。闭包已实测 0 Qt。
- 新 bundle 目前只在 worktree 构建产物与 `G:/CODEX/New Manga.workspace/task-envs/CORE-SLIM-1/sidecar-copy`；主检出的 `target/release/resources/core-sidecar` 仍是旧 Qt bundle，集成时需以本 Task 的构建命令重建（`packaging/m2ac5/build_sidecar.ps1 -Force`）。
- `apps/desktop/src-tauri/tauri.conf.json` 未改（旧壳 S5 已冻结，仅资源路径依赖不变）。
- 卡片 `allowed_paths` 未含 `doc/handoffs/**`，但 AC5 要求 Handoff 落在 `doc/handoffs/CORE-SLIM-1-handoff.md`；本文件按 AC5 落位，建议 DSH 在卡上补该路径（或改指 `verification/CORE-SLIM-1/HANDOFF.md`）。
