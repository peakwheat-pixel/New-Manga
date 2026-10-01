# Handoff：M2-IMPORT-ALLOC-LIMIT — 大图导入 QImageReader allocation limit 修复（TA3-B2 F2）

- owner：ZCode · 交付头：`a5c8adf1` · 分支 `agent/zcode/M2-IMPORT-ALLOC-LIMIT`（Task 授权基线 `8e0de8d0`；分支实际 fork 自 release `8996ca55`）· worktree `G:/CODEX/New Manga.worktrees/M2-IMPORT-ALLOC-LIMIT-zcode`
- Task：[M2-IMPORT-ALLOC-LIMIT](../tasks/M2-IMPORT-ALLOC-LIMIT.md)（status=in_review）
- commit 拓扑（dsh r1 R5 改正）：`8996ca55`(fork=release，续接熔断半成品所在工作区) → `a5c8adf1`(implement: 修复+红绿测试+K07 真图验证+证据) → `02f306ea`(docs/handoff) → 本返修 commit
- Review：DeepSeek Harness r1=approved_with_conditions（返回修：本文档「r1 返修记录」节）

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

- **非 0**：`setAllocationLimit(0)` 在 Qt 语义中是**完全关闭检查**，损坏/声明超大 header 可 OOM 进程；本值是**有界 fail-closed 上限**，锚在下方域实测上。
- **域覆盖**：产品域实测最大页 K07 690×131289 解码 ≈345.6MiB，2047 留 **~5.9× 余量**；即使取无实测出处的假设外推 690×~350k px×4B ≈ **921MiB**（≈966MB，r1 R6 统一 MiB 口径；~350k px 为假设上尾，域内无实测样本），仍留 ~2.2× 余量。
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
  - K07 `690×131289`（盘上 57,012,442 B，解码 ≈345.6 MiB）→ imported OK，宽高/managed ref 登记
  - K09 `690×100480`（46,128,749 B）→ imported OK
  - K10 `690×100674`（40,141,409 B）→ imported OK
  - 三例 zero failed → **verdict: PASS**
- **对照组**（F2 一级证据）：刻意绕开修复后的 decoder（其前置断言会恢复 2047），用原始 `QImageReader` 读法在 Qt 默认 256 MiB 下重放三例：**全部拒绝**，`errorString='Unable to read image data'`；Qt 的 limit 拒绝原因不进 errorString，但 stderr 分类日志逐例输出 `QImageIOHandler: Rejecting image as it exceeds the current allocation limit of 256 megabytes`——**该日志原文已按 case 以 OS 级 fd2 捕获归档进 JSON**（r1 R2，此前 handoff 声称已归档而 JSON 实际未含，属证据声明超出工件，本次返修正名），JSON 另含 env 段（python/platform/pyside6/qt）与 per-case decoded MiB / 对照臂 header-declared MiB。TA3-B2 quality-report 中 F2 的「推断」口径自此升级为一级证据。
- **正向臂**（r1 R3）：对照组每例附 @2047 MiB **同一 reader 读法、同一字节**的成功解码记录——对照组内部 256 拒/2047 过，限值为唯一变量。
- K07 尺寸 690×131289 与 TA3-B2 case-selection 记录一致（交叉核实通过）。

## 5. 复现命令

```bash
cd "G:/CODEX/New Manga.worktrees/M2-IMPORT-ALLOC-LIMIT-zcode"
PY="G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe"

# 全量四套件（期望 521 passed, 1 skipped）
PYTHONPATH=src "$PY" -m pytest tests/library/test_production_adapters.py tests/providers tests/core tests/m2_acceptance -q

# K07/K09/K10 真图验证（期望 verdict: PASS；r1 R10：补 --out 使命令可复现证据工件）
PYTHONPATH=src "$PY" experiments/M2-IMPORT-ALLOC-LIMIT/verify_k07.py --out verification/M2-IMPORT-ALLOC-LIMIT/verify-k07.json
```

## 6. 边界与已知保留

- 禁改面零触碰：`src/ports/**`、importing.py 外 infrastructure、`src/bootstrap/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、TA3-A/B experiments、`doc/STATUS.md` 均未改（自检 porcelain+diff --check 见交付 commit）。
- 真 PNG 的「伪大尺寸头」只用于 IHDR 声明尺寸超限路径（rows=1 时 IDAT 数据不完整，注释已限定「仅用于 Qt 分配前拒绝的路径」）；webtoon 导入绿测试用完整数据真实解码；限值机制本身由 r1 R1 机制锁定用例固化（同字节 @1MiB 拒 / @2047 过）。
- **MOBI 通道上界不随全局放宽**（r1 R7）：`QtImageDecoder` 抬高的进程全局 2047 MiB 会被 `_MobiDocumentHandle.render_page` 在其自身 `QImage.loadFromData` 前重新收紧回 Qt 内建 256 MiB——MOBI 内嵌图是不可信输入，保持原 fail-closed 上界；`QtImageDecoder` 每次 decode 前重断言 2047，互不干扰。
- 2047 上限是本 Task 决策值；若未来出现域内更大页或 32 位平台约束，重新评估入口=importing.py 注释块 + 本 handoff §2。
- K01-K10 中 F1 缺口（ogkalu webtoon 0 候选）不在本 Task 范围（M2-DETECT-WEBTOON-DIAG 并行处理）。

## 7. Review 指引（DSH 非作者）

建议重点：①2047 论证链（§2）是否成立、非 0 理由是否充分；②红态证据口径（基线 stash 复现命令可重放）；③`make_thin_png` 流式改造与 `rows=1` 截断的测试有效性（Qt 分配前拒绝的前提已实测）；④对照组绕开 decoder 的设计（§4 NOTE）；⑤禁改面核对。

## 8. r1 返修记录（DSH r1 approved_with_conditions，2026-10-01，R1-R10 逐条落点）

DSH r1 评审：`G:/CODEX/New Manga.task-envs/M2-IMPORT-ALLOC-LIMIT/dsh-review-r1.md`。逐条处置：

| # | 级别 | 处置 | 落点 |
|---|---|---|---|
| R1 | P2 | **closed**：新增机制锁定用例 `test_qt_image_decoder_allocation_limit_decides_accept_or_reject`——同一完整合法小图 `make_thin_png(690, 4000)`（~10.5 MiB），生产 limit 必过、`monkeypatch.setattr(importing, "_ALLOCATION_LIMIT_MIB", 1)` 必拒；同输入仅限值不同，限值是决定因素的断言固化。原 fail-closed 测试（rows=1 截断载荷，无法区分限值拒绝与数据截断失败）保留为 typed fail-closed 保护，其机制证明职责移交本用例 | tests/library/test_production_adapters.py |
| R2 | P2 | **closed（补档而非降级）**：verify_k07.py 增强——①OS 级 fd2 捕获 per-case stderr 分类日志原文（实测 `qt.gui.imageio: QImageIOHandler: Rejecting image as it exceeds the current allocation limit of 256 megabytes`）进 JSON `native_stderr`；②新增 `env` 段（python 3.12.3 / Windows-11 / PySide6 6.11.2 / Qt 6.11.2 / limit 2047）；③per-case `decoded_mib`（345.6/264.5/265.0）与对照臂 `declared_mib`；schema v2 并重跑 `--out` 落盘。原 handoff「已归档进 JSON」声明当时超出工件（JSON 实未含 stderr），已在 §4 正名 | experiments/.../verify_k07.py + verification/.../verify-k07.json |
| R3 | P3 | **closed**：对照臂新增正向记录 `at_2047_same_reader_same_bytes`（同一原始 reader 读法、同一字节 @2047 → 成功，三例全 decoded），对照组内部 256 拒/2047 过，限值为唯一变量；verdict 判定同步纳入该臂 | verify_k07.py control 段 |
| R4 | P3 | **closed（删词）**：domain `Page` 无 mime 字段（src/domain/pages/entities.py），Task AC3 行、handoff §4、脚本 docstring 的「mime」表述全部删除，与 JSON 字段对齐（JSON 从未登记 mime） | Task 交付证据表 / handoff §4 / verify_k07.py docstring |
| R5 | P3 | **closed**：commit 拓扑改正为 `8996ca55(fork=release) → a5c8adf1(implement) → 02f306ea(docs)`（DSH 经 reflog 证实 a5c8adf1 父提交是 8996ca55 而非 8e0de8d0）；Task frontmatter `base_commit` 加注「Task 授权基线 8e0de8d0；分支实际 fork 自 release 8996ca55」 | handoff 头部 / Task frontmatter |
| R6 | P3 | **closed**：importing.py 注释数字统一 MiB 口径——965 MiB 实为 ≈966 MB ≈ **921 MiB**（966e6 B / 1048576），余量 2.1×→**2.2×**；~350k px 标注为「无实测出处的假设上尾」；「非 0」论证重心改为「有界 fail-closed 锚在域实测 345.6 MiB × ~5.9× 余量」。handoff §2 同步 | src/infrastructure/importing.py 注释 + handoff §2 |
| R7 | P3 | **closed**：`_MobiDocumentHandle.render_page` 解码前 `QImageReader.setAllocationLimit(256)` 重新收紧（MOBI 内嵌图=不可信输入，保持 Qt 内建 fail-closed 上界，不被 webtoon 抬高的进程全局 2047 波及）；`QtImageDecoder` 每 decode 前重断言 2047，互不干扰。import_formats 28 用例全绿 | src/infrastructure/importing.py + 本 handoff §6 |
| R8 | P4 | **closed**：截断断言收紧为 `detail.endswith("...")` 且 `len(detail) == _ERROR_DETAIL_MAX_CHARS + 3`（300+3，替代宽松的 ≤400） | tests/library/test_production_adapters.py |
| R9 | P4 | **closed**：红态归档 `verification/M2-IMPORT-ALLOC-LIMIT/pre-fix-tests-against-base-src.txt`——基线 blob 写回工作区（git 语义零 diff 溯源 + 模块解析路径行）→ 5 个新用例 `-q -rs -rf` → **4 failed, 1 passed**（fail-closed 保护测试基线绿，与原记录一致）→ HEAD 恢复；用例①加 `@pytest.mark.slow`（真实 289.5 MiB 解码） | verification/.../pre-fix-tests-against-base-src.txt + tests |
| R10 | P4 | **closed**：handoff §5 复现命令补 `--out verification/M2-IMPORT-ALLOC-LIMIT/verify-k07.json`，使命令可复现证据工件 | handoff §5 |

返修后验证（主 venv，PYTHONPATH=src）：

- 五套件 `pytest tests/library/test_production_adapters.py tests/providers tests/core tests/m2_acceptance tests/import_formats -q` → **550 passed, 1 skipped, 0 failed**（四套件口径 522 = 原 521 + R1 新用例；import_formats 28 例补跑全绿，覆盖 R7 MOBI 面回归）。
- K07/K09/K10 真图重跑 → verdict: PASS（schema v2，新增 env/native_stderr/decoded_mib/正向臂）。
- 红态归档：4 failed, 1 passed（见 R9）。
