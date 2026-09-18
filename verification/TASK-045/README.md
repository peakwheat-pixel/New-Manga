# verification/TASK-045 — evidence index

交付 head `1171bc5`（分支 `agent/deepseek/TASK-045-webtoon-display-fixes`；实现两提交 `602cca8` + `1171bc5`）。
环境：PowerShell + `TASK-012-py312`（Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1），
`PYTHONDONTWRITEBYTECODE=1`，全部 `-p no:cacheprovider`。

## 探针（可复跑）

| 文件 | 用途 |
|---|---|
| `memory_and_fixture_probe.py` / `memory-and-fixture-probe.txt` | **AC ⑨** 内存构成：对 400×10000 不可压缩页，比较"单 IDAT / 1000 行分块"两种编码下的常驻源、最大 IDAT 块、带宽与实测额外峰值（单块 24.1MB ≈ 23× 带宽；分块 5.7MB）；并计时 **AC ⑪** 夹具各阶段（96MB 原始构造 0.12s、Qt 编码 0.70s、从 row 12000 起的带状读 18.5s、Qt 载入+切片 0.33s） |
| `rewind_cost_probe.py` / `rewind-cost-probe.txt` | **AC ⑩** rewind 成本：400×20000 全页 25 块扫掠 = 0.94s/**24 次 rewind**；单块回跳 0.015s、回跳到 row 11920 = 0.094s；生产 `overlap=64` 下 1600×8000 Qt 编码页**单块 4.53s → 两块 14.24s**（多出 9.70s 纯重扫） |
| `comment_drift_check.py` / `comment-drift-check.txt` | **F-13/F-14** 注释与实现一致性（可复跑断言）：`src/infrastructure/imaging/**` 内 `setClipRect` 出现 0 次、模块 docstring 已陈述整图根因、`_cache_key` docstring 为内容寻址且确有 `sha256(源字节)` 与格式标记 `v2` |

## 判别力（修前必须失败）

| 文件 | 内容 |
|---|---|
| `pre-fix-tests.txt` | **两棵树**：`git archive 6ea3dd3 src pytest.ini` + 本 worktree 最终 `tests/`，`pytest tests/reading_export tests/core -q -rf` → **10 failed / 120 passed**（完整失败详情） |
| `pre-fix-failure-summary.txt` | 由上式日志机取的「用例 → 失败原因」；含 F-4（`tile 1: file height 864 != declared content_height 800`）、F-5（`3000 != 1200`）、F-11（`requestTiles() takes 3 positional arguments but 4 were given`）、F-14（`stale tile reused after an in-place rewrite`）、AC ⑧ ×2（`zlib.error … incorrect header check`）、F-8（`returnType=void`）、QML ×2 |
| `pre-fix-delegate-diagnosis.txt` | 把基座 QML **仅**补 `objectName: "readerTilesHost"`（其余不动）后单跑 QML 用例 → 仍失败于"第一页瓦片必须被服务" ⇒ 基座**从不创建 delegate**（Repeater 的 `model` 遮蔽），即分块视图渲染空白而非"旧图" |

**守卫（修前也通过，不计入判别力）**：`test_ensure_viewport_rewind_accounting_is_per_tile`、`test_band_read_peak_composition[single-idat|banded-idat]`、`test_qt_encoded_oversized_page_bands_match_qt_pixels`——它们钉住的是本次未改变的行为/覆盖。

## 回归

| 文件 | 内容 |
|---|---|
| `post-fix-reading-core.txt` | `tests/reading_export tests/core` = **130 passed / 0 skipped** |
| `post-fix-qml-contract.txt` | `tests/reading_export/test_qml_contract.py` = **10 passed** |
| `full-suite-runs.log` | **修订切片**：全仓 **5 次连续 830 passed / 6 skipped，逐次 exit 0**；run 6 单独 `-rs` 打印 6 条 skip 逐条原因（本文件在修订提交 `a165aa3` 中按新内容重跑覆盖；上一轮 827/6 的版本见 git 历史 `1171bc5`） |
| `baseline-master-6ea3dd3.txt` | 上一轮基线（主仓库 master `6ea3dd3`）= **813 passed / 6 skipped** |
| `baseline-master-c3d9ed2.txt` | **修订轮基线**（主仓库 master `c3d9ed2`）= **825 passed / 6 skipped** |
| `per-directory-counts.txt` | 逐目录 交付/1171bc5：reading_export 109/100(+9 failed)、core 24/24、ui_shell 46/46、workbench 51/51；AC ⑥ 聚合 **230** |

6 条 skip 全部为既有 `tests/network` `openssl unavailable`（`test_connection_tester.py:106`、`test_transport_tls.py:39/47/62/69/83`）。

## 修订切片（R-001 P1 + R-002..R-005，回应 [doc/reviews/TASK-045-1171bc5.md](../../doc/reviews/TASK-045-1171bc5.md)）

交付 head `a165aa3`（被审 `1171bc5`）。新增证据：

| 文件 | 用途 |
|---|---|
| `revision-reviewer-probe.txt` | **复审者自己的探针** `review-1171bc5/reviewer_probe.py` 在修订树上的复跑：**B1（首个打开）与 B3（`nextPage()` 后）已有瓦片 sources**（原为 `[]`）、section A（F-4）仍 True |
| `revision-pre-fix-tests.txt` / `revision-pre-fix-failure-summary.txt` | R-001 **判别力**（两棵树：`git archive 1171bc5 src pytest.ini` + 本切片 `tests/`）：**8 failed / 125 passed**，全部落在 R-001 轴上（2 个新 QML 用例 + 2 个新 VM 用例 + 4 处按新口径更新的断言） |
| `revbase-full-rerun-3s.txt` | 同一基树的全仓：**8 failed / 822 passed / 6 skipped、exit 1、无崩溃** |
| `revision-baseline-1171bc5-full.txt`、`revbase-workbench-and-full-rerun.txt` | 加固前基树全仓的两次 **access violation**（`tests/workbench/test_ui_responsiveness.py`）原始记录——见下「说明」 |
| `control-pure-1171bc5-full.txt` | 对照：纯 `1171bc5` 树（旧测试）全仓 = **827 passed / 6 skipped、exit 0** |
| `baseline-master-c3d9ed2.txt` | 修订轮主仓库基线 = **825 passed / 6 skipped** |

## 说明

- pytest 的 `-r` 只接受**一组**字符：`-rs -rf` 会让后一个覆盖前一个，故 runs 1–5 只有计数、run 6 单独用 `-rs` 补齐 skip 原因（已在 log 内注明）。
- 探针脚本只读源树；`memory_and_fixture_probe.py` 会在临时目录写入自己的夹具，不触碰仓库数据。
- **基树 access violation 的定位与加固**：把本切片测试放到修前树上时，全仓运行两次在 `tests/workbench/test_ui_responsiveness.py::test_gui_thread_stays_alive_during_run` 崩溃（0xC0000005）。对照实验：纯 `1171bc5` 树全仓 exit 0；`tests/workbench` 单独在基树 51 passed；"QML 契约 + ui_responsiveness" 最小组合无崩溃 ⇒ 需整套顺序。相关性指向修前树上 4 个新用例的**失败路径**各自 `pump_traced(5.0)` 空转（正常路径同步完成、<100ms）。将失败等待收紧到 **3s** 后基树全仓无崩溃，**交付树加固前后各 6 次全仓全绿**。
- 证据文件在提交 `a165aa3` 内；本 README、Handoff 与 Task 记录在随后的文档提交中。
