# Handoff：M2-IMPORT-ALLOC-LIMIT — 大图导入 QImageReader allocation limit 修复（TA3-B2 F2）

- owner：ZCode · 交付头：`a5c8adf1` · 分支 `agent/zcode/M2-IMPORT-ALLOC-LIMIT`（base `8e0de8d0`）· worktree `G:/CODEX/New Manga.worktrees/M2-IMPORT-ALLOC-LIMIT-zcode`
- Task：[M2-IMPORT-ALLOC-LIMIT](../tasks/M2-IMPORT-ALLOC-LIMIT.md)（status=in_review）
- commit 拓扑：`8e0de8d0`(base) → `a5c8adf1`(implement: 修复+红绿测试+K07 真图验证+证据) → 本 handoff commit
- Review：待派发 DeepSeek Harness（非作者静态）

## 0. 续接声明（熔断半成品处置）

本 Task 续接前一个熔断 agent 留在 8996ca55 工作区的半成品（未提交）。回填 owner 先读 diff 核实方向再实跑，处置如下：

| 半成品内容 | 处置 | 说明 |
|---|---|---|
| `importing.py`：`_ALLOCATION_LIMIT_MIB=2047` + 论证注释 + `_reader_error_detail()`（errorString 截 300 字符） | **采纳，零修改** | 方向与任务书 AC1/r1 R4 完全一致 |
| `helpers.py`：`make_thin_png`（手写 IHDR/IDAT 伪大尺寸头） | **采纳 + 修正** | 原 `zlib.compress(row * height)` 工厂内一次性分配 `width*height*4` 量级中间对象（8192×65536 case ≈2GB），与自身注释「No full-size allocation happens in the factory」矛盾；改为 compressobj 流式 ~8MiB 批量压缩 |
| `test_production_adapters.py`：4 个新测试 + autouse fixture + `UnknownFormatReader` 补 `setAllocationLimit` | **采纳 + 修正** | ①`LongErrorReader` fake 缺 `setAllocationLimit` staticmethod，decode() 新增的前置断言在它上面直接 AttributeError（实跑红证实）→补齐；②fail-closed 测试改 `make_thin_png(8192, 65536, rows=1)`：Qt 按声明 IHDR 尺寸在分配前拒绝（实测 0.01s，stderr 分类日志证实），单行 IDAT 即可触发真实 2048>2047 拒绝，无需压缩 2GB 数据（6.9s→<0.01s） |

## 1. 方案

`src/infrastructure/importing.py`（产品唯一 QImageReader 使用点）：

1. `QtImageDecoder.decode()` 在每次 read 前调用 `QImageReader.setAllocationLimit(_ALLOCATION_LIMIT_MIB)`（模块常量 **2047** MiB）。静态 setter 是进程全局；每次 decode 幂等重断言代价可忽略，且在无关代码改写全局值后仍保持正确。当前 import 跑在应用线程；并发最坏情形是同一值的幂等重复写。
2. decode 失败路径 detail 改走 `_reader_error_detail(reader)`：携带 `reader.errorString()` 原文（strip；空则回退 `bytes are not a decodable image`；超 300 字符截断加 `...`），闭合 r1 R4「per-file detail 为空串不可诊断」，同时为 UI/日志面保持有界。
3. fail-closed 语义不放宽：超上限仍 raise `ImageDecodeError`（typed），只是上限更合理 + 错误可诊断。

## 2. 上限论证（为何 2047 安全）

- **非 0**：`setAllocationLimit(0)` 在 Qt 语义中是**完全关闭检查**，损坏/声明超大 header 可 OOM 进程；fail-closed 纪律要求硬上界。
- **域覆盖**：产品域实测最大页 K07 690×131289 解码 ≈345.6MiB；外推最坏 690×~350k px×4B ≈965MiB；2047 仍留 ~2.1× 余量。
- **参数边界**：2047 在 Qt `int` MB 参数内；单次 decode 远低于现实 64 位桌面内存预算。
- **非预分配**：Qt 在分配**前**检查该界，因此它是单次 decode 的上界，从不预占内存。
- **settings 可配置化不做**：任务书 AC1 为「方案自选并留痕」；静态模块常量 + 幂等断言以最小面闭合 F2，settings 通道留待真实需求（避免为本 Task 扩 settings 契约面）。

## 3. 红绿数字

测试环境：主实现 venv `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312`（PySide6 6.11.2，Qt 6.5+ API 具备），`PYTHONPATH=src`。

| 口径 | 命令 | 结果 |
|---|---|---|
| 红态（`git stash` src 后对 8996ca55 基线跑新测试） | `pytest tests/library/test_production_adapters.py -k "allocation_limit or long_strip or truncates_very_long"` | **3 failed**（`imports_webtoon_long_strip_beyond_qt_default_cap`：256 上限拒 690×110000≈289.5MiB；`raises_allocation_limit_above_qt_default`：基线不调用 setter；`truncates_very_long_reader_errors`：5000 字符 detail 不截断）+ 1 新增即绿（`fail_closed_above_limit...`：256 上限同样拒绝 2048MiB，保护性回归测试基线绿符合预期） |
| 绿态（修复后） | 同上 | **4/4 passed**（12 passed 文件级 1.57s，修正前 9.76s） |
| 全量四套件 | `pytest tests/library/test_production_adapters.py tests/providers tests/core tests/m2_acceptance -q` | 基线 `8996ca55`：**517 passed, 1 skipped**；交付头：**521 passed, 1 skipped, 0 failed**（+4 新增，无回归） |

## 4. K07 真图验证（AC3）+ F2 口径升级（AC4）

脚本 `experiments/M2-IMPORT-ALLOC-LIMIT/verify_k07.py`（真图只读，managed 树写 `%TEMP%` 一次性目录），证据 `verification/M2-IMPORT-ALLOC-LIMIT/verify-k07.json`：

- **主通道**（生产 `ImportImagesUseCase` + `QtImageDecoder` + `ManagedCopyStoreAdapter` + 内存 sink，limit=2047）：
  - K07 `690×131289`（盘上 57,012,442 B，解码 ≈345.6 MiB）→ imported OK，宽高/mime/managed ref 登记
  - K09 `690×100480`（46,128,749 B）→ imported OK
  - K10 `690×100674`（40,141,409 B）→ imported OK
  - 三例 zero failed → **verdict: PASS**
- **对照组**（F2 一级证据）：刻意绕开修复后的 decoder（其前置断言会恢复 2047），用原始 `QImageReader` 读法在 Qt 默认 256 MiB 下重放三例：**全部拒绝**，`errorString='Unable to read image data'`；Qt 的 limit 拒绝原因不进 errorString，但 stderr 分类日志逐例输出 `QImageIOHandler: Rejecting image as it exceeds the current allocation limit of 256 megabytes`（已归档进 JSON 附带复现命令）。TA3-B2 quality-report 中 F2 的「推断」口径自此升级为一级证据。
- K07 尺寸 690×131289 与 TA3-B2 case-selection 记录一致（交叉核实通过）。

## 5. 复现命令

```bash
cd "G:/CODEX/New Manga.worktrees/M2-IMPORT-ALLOC-LIMIT-zcode"
PY="G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe"

# 全量四套件（期望 521 passed, 1 skipped）
PYTHONPATH=src "$PY" -m pytest tests/library/test_production_adapters.py tests/providers tests/core tests/m2_acceptance -q

# K07/K09/K10 真图验证（期望 verdict: PASS）
PYTHONPATH=src "$PY" experiments/M2-IMPORT-ALLOC-LIMIT/verify_k07.py
```

## 6. 边界与已知保留

- 禁改面零触碰：`src/ports/**`、importing.py 外 infrastructure、`src/bootstrap/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、TA3-A/B experiments、`doc/STATUS.md` 均未改（自检 porcelain+diff --check 见交付 commit）。
- 真 PNG 的「伪大尺寸头」只用于 IHDR 声明尺寸超限路径（rows=1 时 IDAT 数据不完整，注释已限定「仅用于 Qt 分配前拒绝的路径」）；webtoon 导入绿测试用完整数据真实解码。
- 2047 上限是本 Task 决策值；若未来出现域内更大页或 32 位平台约束，重新评估入口=importing.py 注释块 + 本 handoff §2。
- K01-K10 中 F1 缺口（ogkalu webtoon 0 候选）不在本 Task 范围（M2-DETECT-WEBTOON-DIAG 并行处理）。

## 7. Review 指引（DSH 非作者）

建议重点：①2047 论证链（§2）是否成立、非 0 理由是否充分；②红态证据口径（基线 stash 复现命令可重放）；③`make_thin_png` 流式改造与 `rows=1` 截断的测试有效性（Qt 分配前拒绝的前提已实测）；④对照组绕开 decoder 的设计（§4 NOTE）；⑤禁改面核对。
