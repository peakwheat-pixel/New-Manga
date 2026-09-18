# TASK-042 集成验证：`ce7b4f9`

## 固定对象

| 项目 | 值 |
|---|---|
| base commit | `904fca185c9900c0b2df297529a58ece831dc0a0` |
| reviewed head（delivery） | `fc6c649` |
| 元数据 / docs head | `49b0608` |
| 分支 head（被集成对象） | `98b38b7`（= 合并 master `f1c6ea0` 后的分支 head） |
| Review 报告 commit | `6e303cf` → [`doc/reviews/TASK-042-fc6c649.md`](../../doc/reviews/TASK-042-fc6c649.md)（Reviewer=Codex，**非作者**；decision=`approved`；四轴均 `executed`、不跨轴排名） |
| implementation merge / integration commit | `ce7b4f916a8155b2c4914eb4f9bfe5d8cf0f4462`（merge，parents `6e303cf` + `98b38b7`） |
| 环境 | Windows `10.0.26200`；`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1）；`PYTHONDONTWRITEBYTECODE=1`；`-p no:cacheprovider` |

## 作者改动范围（已核）

**4 文件 `+712/−81`**：`src/infrastructure/imaging/streaming_png.py`（新增 279）、`src/infrastructure/imaging/webtoon_tiles.py`（±142）、`tests/reading_export/test_streaming_png.py`（新增 296）、`tests/reading_export/test_webtoon_tiles.py`（±76）；docs：`doc/handoffs/TASK-042-fc6c649.md`、`verification/TASK-042/full-suite-runs.log`。
**越界 0；`git diff --diff-filter=D --name-only 904fca1 HEAD` 为空（无删除）；`requirements.txt` 零改动。**

> **澄清（供后续复审避免误判）**：`git diff f1c6ea0 fc6c649` 会列出若干 `D`（含 `doc/tasks/TASK-043.md` 等）——那是**基线产物**：`fc6c649` 的父提交是 `ebe5755`（分支起点线），master 的 `f1c6ea0` 是经 `98b38b7` **合并**进来的。已核实 `f1c6ea0` 是 HEAD 的祖先、所列文件在 HEAD 全部存在。

## 复验结果（master `ce7b4f9`，Reviewer 独立重跑）

| # | 命令 / 方法 | 退出码 | 结果 |
|---:|---|---:|---|
| 1 | `pytest tests/reading_export tests/core tests/providers tests/pipeline -q -p no:cacheprovider -rs` | 0 | **352 passed / 0 skipped** |
| 2 | `pytest -q -p no:cacheprovider -rs -rf`（全仓） | 0 | **792 passed / 6 skipped**；6 条全为既有 `tests/network` 的 `openssl unavailable`（作者声明口径为 `798 passed / 0 skipped`，**总数一致**） |
| 3 | 过滤器正确性（Reviewer 自写正向编码：5 种过滤器 + 逐行混合 + 4 组 bpp + 随机内容 + 多带偏移） | 0 | **逐字节等于原始行** |
| 4 | 与 Qt 一致性（Qt 编码随机 RGBA PNG → 读者带状解码 vs `QImage` 像素） | 0 | **逐像素一致**（多带偏移） |
| 5 | 游标语义 | 0 | 回退请求 → typed `REWIND_REQUIRED`；`rewind()` 后重扫正确 |
| 6 | 成本量化 | — | 扫 20000 行 **0.39 s**；回跳 row 12000（16000 行）**0.156 s**；回跳 row 0（4000 行）**0.219 s**；`visible_tiles` 升序 ⇒ **每调用最多一次 rewind** |
| 7 | 内存构成 | — | 峰值 **≈39.7 MB**（带宽 12.8 MB / 整图 rgb32 64 MB / 压缩源 113 KB）→ 见 R-02 |
| 8 | **损坏载荷（新发现）** | — | 翻转 IDAT 载荷 → **untyped `zlib.error`** 逃出 `except (OSError, ValueError)` → **R-01** |

## 验收结论

- [x] 非作者 Review 绑定固定 base/head，四轴均 `executed`、逐轴小结、**不跨轴排名**；并行偏差按环境结论声明（§6 第 6 条兜底）。
- [x] **AC ① 带状解码 + 内存实测**：PASS（带状解码成功；峰值 ≪ 整图）。
- [x] **AC ② TASK-020 表征钩子按原设计翻转**：PASS，且**更强而非放宽**——`pytest.raises(OSError)` → 成功断言 + 尺寸 + 几何比率 + 记录峰值；TASK-020 的几何断言逐字未动、**测试未删除**。
- [x] **AC ③ fail-closed 矩阵**：PASS（枚举内：NOT_PNG/INTERLACED/16-bit/PALETTED/TRUNCATED 均 typed）；**枚举外**发现 R-01。
- [x] **AC ④ 端到端 + 回退路径不变**：PASS（tile 路径可达；未注入 `tile_factory` 时整图路径行为不变）。
- [x] **AC ⑤ 依赖纪律**：PASS（`requirements.txt` 零改动；pyvips 未启用，stdlib-only 已满足全部 AC）。
- [x] **AC ⑥ 判别力 + 回归**：PASS（新模块在修前不存在 ⇒ 新用例必然失败；钩子翻转的反事实由作者会话留证；**Reviewer 未另行重跑修前树，已如实标注**）。
- [x] **AC ⑦ Review + 集成**：本文件。
- [x] 6 条 skip 全为既有 `openssl unavailable`；**未新增 skip 计数、未放宽既有断言**（新增 1 处模块级 `importorskip("PySide6")`，已披露且在声明 venv 中不生效 → P3 登记）。
- [x] **TASK-020 遗留项②（超大 webtoon 像素解码 `BLOCKED`）关闭**；遗留项①②至此全部关闭。**TASK-042 置 `done`**。
- [x] 未 push；未改 Schema/migration、依赖清单、seam 本体、`AGENTS.md`、`src/ui/**`、其他 Task。

## Findings 处置

| ID | 级别 | 内容 | 处置 |
|---|---|---|---|
| **R-01** | **P3** | `streaming_png.py::_pump` 未捕获 `zlib.error`（MRO `(zlib.error, Exception)`，既非 `OSError` 也非 `ValueError`）→ 损坏但结构完整的载荷逃出 VM 的 `except (OSError, ValueError)`，不再优雅回退。**失败仍是 fail-closed（Adler-32 拦截，不产出错误像素）**，故定 P3 | **open → 并入 [TASK-045](../../doc/tasks/TASK-045.md) AC ⑧** |
| **R-02** | P3 | 内存声明不够精确：峰值 = 压缩源常驻 + ≈3–4× 带宽（非 1× 带）；AC ① 仍成立 | **open → TASK-045 AC ⑨** |
| **R-03** | P3 | rewind 重扫成本未量化；"升序请求 ⇒ 每调用最多一次 rewind"未文档化 | **open → TASK-045 AC ⑩** |
| **R-04** | P3 | 超大页夹具改由测试自写 stdlib 写入器（filter 0）生成 → "真实编码器 × 超大"覆盖缺口 | **open → TASK-045 AC ⑪** |
