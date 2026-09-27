我已完成只读核对（无法执行 shell：DSH 沙箱对 workspace ACL 的 `grantWrite` 被 Win32 拒绝，`pwsh`/`git` 全部不可用，审批通道也不可用），因此改用文件级证据链重建。先说结论，再给逐条核对与限制披露。

**核对基线确认**：`.git/worktrees/DIAG-FIX-C-zcode/HEAD` → `refs/heads/agent/zcode/DIAG-READING-EXPORT-001-FIX-C-quit-and-leave-wiring` → `27dbedda0d190a1717f5b641a69e7197581c8f38`；`logs/HEAD` 显示 `ee30172f → 132aa5e1`（R3 代码：N-1..N-5）`→ 27dbedda`（R3 handoff）。即 `ee30172f..27dbedda` 的代码 hunk 全落在 `132aa5e1`，我被审的工作区快照 = 27dbedda。

---

decision=changes_requested

## 一、逐条核对表

| ID | 级别 | R3 处置声明 | 复核 | 依据（文件:行） |
|---|---|---|---|---|
| N-1 | P2→P3 | 心跳非 active 时重置 `_last_settle`；判别测试断言 `total_read_seconds` 不变 | **不通过（仅验证面）** | 产品修复正确：`src/bootstrap/app.py:243-244` 在幂等守卫之后、章节校验之前重置基线，`viewmodel.py:96,464-466` 的 settle 折叠为 0；正常切章（heartbeat active）不重置，语义不变 ✓。但判别断言 `tests/core/test_bootstrap.py:707-709` 用**严格相等**，其真值取决于"重置读数与 `openChapter` 内首个 settle 读数落在同一时钟 tick"，而非取决于行为 |
| N-2 | P3 | 三重幂等守卫 | **通过** | `app.py:231-236` 三重条件（`hasChapter` ∧ `_reading.chapter_id == get_reader_context().chapter_id` ∧ `_heartbeat.isActive()`）；`navigation/viewmodel.py:81-83,92-102` 显示 `navigate`/`enterReader` 都会 emit `currentPageChanged` 再 emit `readerContextChanged`，故 re-arm 先打开（opens=1，heartbeat 起），随后 enterReader 被守卫跳过；断言 `test_bootstrap.py:706,711` 分别在 re-arm 后、enterReader 后计数，判别力成立（去守卫则 opens=2） |
| N-3 | P3 | re-arm 包 try/except + stderr | **通过** | `app.py:286-289` 与 F-6 `app.py:518-522` 同规格（`except Exception as error  # noqa: BLE001` + `print(..., file=sys.stderr)`）；异常不逃逸 QML 调用点 |
| N-4 | P3 | 以最终测试重取红/绿 | **通过（附文档漂移 T-2）** | `wiring-test-pre-wiring-red.log:1-2` 标注 "R3 final version"，其打印源码（log:12-52）与当前 `test_bootstrap.py:653-685` 一致；`wiring-test-post-wiring-green.log` EXIT=0 为同一文件；`targeted-suite-r3.log:14` 210 passed、`full-suite-r3.log:388-390` 1318 passed/5 skipped/1 warning EXIT=0 |
| N-5 | P3 | 改 closeReader 调用计数 | **通过** | `test_bootstrap.py:673-687` 实例级包装 + `assert closes`；pre-wiring 时 `navigate("bookshelf")` 不触发 `closeReader`（`app.py:277-294` 是接线本体），断言结构性为红。判别力成立（红日志先停在更早的 heartbeat 断言，见 T-4） |
| N-6 | P4 | accepted + 披露 | **通过** | `app.py:237-244` 注释明确以 heartbeat 状态判"离开态"；私有面（`_heartbeat`/`_last_settle`）访问未扩散到 QML/service，公开 pause/resume 面留后续 VM Task 合理 |
| F-1 | Gate | AC1 文本裁决留集成 | **维持** | Task `:43` 字面 `hasChapter is False` 与 `ReadingService.close()`（`application/reading/service.py:158-161` 只 flush）矛盾，仍属集成层裁决 |

**正面确认**：N-1 的守卫位置与顺序正确——它排在 N-2 幂等守卫**之后**，因此 heartbeat active 时既不会误重置基线、也不会误跳过切章结算；`hasChapter=True` + heartbeat active + 同章节时直接 return，不重置 `_last_settle`，符合"阅读中切章保持既有结算语义"。N-2 守卫不阻塞必要重开：离开态（heartbeat 停）时第三条件为假，导入新页后重进仍会重新 `openChapter` 刷新 tiles/pages。

## 二、R3 引入的新问题

**T-1（P3，主阻塞）`tests/core/test_bootstrap.py:707-709` 的判别断言非确定性**

```python
assert services.reading.progress.total_read_seconds == total_before_return
```

- N-1 的重置与 `openChapter()` 内首个 `settleReadingTime()`（`viewmodel.py:96`）之间隔着 `navigation.get_reader_context()`、`core.library.get_chapter()`、`core.page_catalog.list_pages()`（`app.py:248-258`）。
- 该断言为真**当且仅当**两次 `time.monotonic()` 返回同一个值。两种可能都不稳：
  - 时钟粒度粗（Windows/py312 路径为 `GetTickCount64`，≈15.625 ms）：只要中间耗时跨越一个 tick，`elapsed = 0.015625 > 0` → `add_time` 生效 → 断言红。这**不是理论推测**：green 日志能通过本身就反证了当前时钟是 tick 粒度（若为 QPC 级高分辨率，几微秒间隔即 `elapsed > 0`，断言必红）。
  - 时钟切到 QPC（docs.python.org 3.14 已列 Windows 走 `QueryPerformanceCounter`）：`elapsed` 恒 > 0 → 断言恒红，环境升级即炸。
- 对照同仓库既有写法：`tests/reading_export/test_viewmodels.py:180-184` 对同类墙钟累计用 `>= 2.0` 容忍断言；`tests/reading_export/test_reading.py` 的严格相等都针对显式传入值而非墙钟。本断言是首个对墙钟派生量做严格相等的新例。
- 影响面正是本 Task 的 Gate 1（红→绿证据）：偶发红会被误读为 R3 回归，并污染集成 head 的全仓证据。

**T-2（P4）R3 套件证据引用未更新**：`doc/handoffs/DIAG-READING-EXPORT-001-FIX-C-de0bf175.md:21,54,55,67,68` 仍指向 R1 的 `targeted-suite.log` / `full-suite.log`；R3 实际证据是 `targeted-suite-r3.log` / `full-suite-r3.log`（仅在 `:120` §7 提及）。按 §3 表格链接取到的是旧版本日志，无法支撑 R3 代码面。

**T-3（nit，非阻塞）**：`src/bootstrap/app.py:33-34` 插入 `import time` 后顺序为 `sys, time, tempfile`，与仓库惯例（`tests/core/test_bootstrap.py:12-19` 的字母序混排）不一致；仓库无 ruff/isort 配置与 lint Gate，故仅风格。

**T-4（观察，非阻塞）**：`wiring-test-pre-wiring-red.log:50-58` 的失败点是 heartbeat 断言（`:685`），line 687/707/711 在 pre-wiring 下不可达，故 N-1/N-5 的"红"是结构性推断而非日志直接证据；另 `app.py:243` 以"心跳非 active"等同于"离开态"，在 FIX-B 存储故障停跳（`viewmodel.py:471-475`）时也会重置基线（该段时长本已写不入库，无实质损失）。建议注释一句话说明，或并入后续 VM Task。

## 三、changes_requested 的具体修复要求

1. `tests/core/test_bootstrap.py:707-709`：把严格相等换成保留判别力的容忍式，例如
   `assert services.reading.progress.total_read_seconds - total_before_return < 1.0`（无 N-1 时增量 ≈600，判别力不变）；或 monkeypatch `ui.viewmodels.reader.viewmodel.time.monotonic` 做确定性注入。修复后以最终测试重取 red/green 两个日志（保持红绿同版本）。
   - 若 Owner 质疑 tick 粒度前提，可在 `TASK-012-py312` 下自证：`python -c "import time;print(time.get_clock_info('monotonic'))"`——无论 `resolution` 是 0.015625 还是 1e-07，结论相同：严格相等都不是稳定判别式。
2. `doc/handoffs/DIAG-READING-EXPORT-001-FIX-C-de0bf175.md:21,54-55,67-68`：链接与数字来源改为 `-r3.log`（R1/R2 日志保留为历史证据即可）。
3. `src/bootstrap/app.py:33-34`（可选）：`import time` 移到 `import tempfile` 之后，恢复字母序惯例。

**未发现**新的产品逻辑缺陷、越界修改或禁止面触碰：改动点（`src/bootstrap/app.py`、`tests/core/test_bootstrap.py`、`verification/DIAG-READING-EXPORT-001-FIX-C/**`、handoff）均在 Task `:50-54` 允许范围内，`src/application/**`、`src/ui/**`、QML、Schema 未见 R3 痕迹。

**推荐下一步**：由 ZCode（Owner）按上表第 1-2 项做 docs+test 单行返修并重取红/绿与两套件日志（新文件名 `-r4`），随后由 DeepSeek Harness 做 R4 定点复核（只核 `tests/core/test_bootstrap.py:707`、handoff §3 引用与两次日志 EXIT）；产品接线本身无需再改。
