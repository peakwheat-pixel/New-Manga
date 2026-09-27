decision=approved

审查环境声明（影响证据强度，先说明）：本会话 `pwsh` 沙箱在给工作区授权时失败（`SetNamedSecurityInfoW Win32 5: grantWrite`），升级需审批但无审批通道，**无法执行 `git diff/status`、也无法重跑测试**。替代核验方式：以只读方式对比主工作树 `G:\CODEX\New Manga`（`refs/heads/main = 7144e4fa`，其 `app.py` 514 行、`:248` 为 `readerContextChanged.connect(_open_reader_chapter)`，与 FIX-B Review R-01 记录的 base 状态一致）+ mtime 序位 + 日志取证。以下逐项给出结论与证据。

## 一、diff 逐 hunk 核对（等价性证明，非 git 输出）

**`src/bootstrap/app.py`**：交付 532 行 vs 主树 514 行，差 18 行，且**两文件除下列两处插入外逐锚点等同**（锚点行号差在插入点前为 0、之间恒为 +13、之后恒为 +18）：
- hunk A `:250-262`（13 行：7 行注释 + `_close_reader_when_leaving` 定义 + 守卫调用 + `currentPageChanged.connect`），插在 `:248 readerContextChanged.connect` 与 `# TASK-038`（主树 `:250` → 交付 `:263`，+13）之间。
- hunk B `:480-484`（5 行：3 行注释 + `application.aboutToQuit.connect(...)` + 空行），插在 `window = engine.rootObjects()[0]`（主树 `:465` → 交付 `:478`）与 `if options.smoke_test:`（主树 `:467` → 交付 `:485`，+18）之间。
- 其余锚点（`assemble_engine` / `_shutdown_services` / `main` / `_shutdown_services(services)` / `return exit_code`）全部按 +13/+18 精确平移 → **app.py 无任何未披露改动**。

**`tests/core/test_bootstrap.py`**：交付 846 行 vs 主树 811 行 = +35，且 `^def test_` 22→23（仅新增 `:646-679` 一个测试 + 1 空行）、`assert/pytest.raises` 匹配数 96→101（差 5 = 新测试的 5 条断言，`_665/666/671/675/676`）→ **无既有断言被删改、无断言放宽**。插入点后的测试行号全部精确 +35。

**治理/证据**：`doc/tasks/DIAG-READING-EXPORT-001-FIX-C.md` 与主树同名文件（71 行）逐行相同，仅 front-matter `status: ready → in_progress`（claim，属允许范围）。`verification/DIAG-READING-EXPORT-001-FIX-C/` 4 个日志与 Handoff 为主树不存在的新增文件；`**/*FIX-C*` 在工作树内仅 3 个路径（Task/Handoff/该 verification 目录），**无越权新增**。mtime 序位显示测试后所有被写入的非字节码文件仅：`doc/tasks/...FIX-C.md`(2561) → `tests/core/test_bootstrap.py`(2730) → red log(2732) → `src/bootstrap/app.py`(2733) → green log(2735) → targeted-suite.log(2755) → full-suite.log(2905) → Handoff(2906)，其间 170 余条全为 `__pycache__`/`.pyc`。**范围核对：无越权。**

## 二、要求的四项核对

1. **离开读者页触发条件正确**（`app.py:257-261`）：`NavigationService.enter_reader` 置 `current_page=READER`（`application/navigation/service.py:129-134`）→ `enterReader` 发出的 page 必为 `"reader"`，守卫 `page != "reader"` 永不误关（AC2 成立）；`navigate("reader")`（PrimaryNavigationRail.qml:32 的真实入口）同样为 `"reader"`，不误触发。无章节安全：`hasChapter`（`reader/viewmodel.py:162-165`，`progress is not None`）双重守卫 + `closeReader`→`settleReadingTime` 的 `progress is None` 早退（`:461-463`）+ `ReadingService.close()` 的 `progress is not None` 守卫（`application/reading/service.py:158-161`）→ 三重安全，无需异常路径。
2. **aboutToQuit 时序正确**：Qt 在 `QCoreApplication::exec()` 的 cleanup 阶段（`execCleanup`）发射 `aboutToQuit`，即 **exec 返回之前**；`_shutdown_services(services)`（`app.py:525`）在 exec 返回之后调用 → flush 时连接必然存活，符合 Handoff §1.2 声明。全仓 `aboutToQuit` 仅此一处 connect，无重复接线；`assemble_engine` 失败的 except 分支不接线且此前不可能有打开章节，无遗漏。
3. **红→绿证据有效**：red log 的失败点 `tests\core\test_bootstrap.py:671` 与交付文件 `:671`（心跳断言）**行号/源码完全一致** → red 与 green 使用的是同一份最终测试；mtime 序位 red(2732) < app.py(2733) < green(2735)。full-suite `1318 passed, 5 skipped` 与 5 条 skip 明细（`test_detect_seam_t111`/`test_detection_doctr_real` docTR、`test_detection_doctr` numpy×1/torch×2）逐条可查，`EXIT=0`；targeted `210 passed` `EXIT=0`。**结论：红→绿成立**（证据溯源的残余保留意见见第四节 R-3）。
4. **aboutToQuit 无自动化测试的取舍：可接受**。理由：接线为一行标准 `connect`，且该行在既有 `test_smoke_startup_loads_qml_and_exits_zero` / `test_smoke_assembles_real_stack_in_data_root` / `test_missing_qml_returns_nonzero_with_path`（子进程跑 `main()`）中**被真实执行**（full-suite 绿即无槽异常/崩溃），缺的只是"退出后心跳已停"的断言；为一行 connect 引入 `application` 注入 seam 属过度设计，与 Handoff §4.1 判断一致。**裁决：接受披露，不加测试**（但请把"退出路径仅由 smoke 间接覆盖"写进残余边界，Handoff 已写）。

## 三、findings

**F-1 [Minor，集成前须由 Codex 处置] `doc/tasks/DIAG-READING-EXPORT-001-FIX-C.md:43`（AC1）与 `tests/core/test_bootstrap.py:669-671` 不一致**
- 触发/事实：AC1 字面要求 `services.reader.hasChapter is False`，但同一 Task 的设计约束与禁止范围又冻结了"不改 reading service/`ReaderViewModel` 语义"，而 `closeReader` 语义（`viewmodel.py:117-122`，FIX-B 既定）只 flush + 停心跳，`hasChapter` 永留 True。交付测试断言的是心跳停 + 幂等重进，并在 `:669-670` 注明契约。
- 影响：AC1 字面未达成（Task 勾选项应保持未勾选）；若按字面判 PASS 即等于静默放宽 `hasChapter` 子句。
- 建议：**裁决为"AC 文本缺陷，非实现缺陷"**（AC 由 R0 释放文本带入，主树同文，作者无从改）。请 Codex 在集成时把 AC1 修订为"心跳停 + 进度 flush（`hasChapter` 按 `ReadingService.close()` 既有语义保留）"，或明确标注豁免；本 Review 按真实语义核验通过。若 Codex 视字面为合同，则本项升级为 `changes_requested`。

**F-2 [Minor] `tests/core/test_bootstrap.py:646-679`：AC1 的"进度已持久化"无断言**
- 触发：离开读者页后仅断言 `_heartbeat.isActive() is False`。
- 影响：若将来 `closeReader` 退化为"只停心跳不 flush"（或 `ReadingService.close` 被改坏），本测试仍绿 → 该 AC 子句无覆盖。
- 建议（低成本、在允许范围）：navigate 后追加持久化断言，例如经 `services.reading`/`services.conn` 读 `reading_progress` 的 `updated_at`/`last_read_at` 已更新（或 `total_read_seconds` 非负变化），使其与 AC1 文字对齐。

**F-3 [Minor] `tests/core/test_bootstrap.py:677-678`：新测试的 `finally` 未收口心跳，与邻居测试的既定纪律相反**
- 触发：`:674-676` 重新 `enterReader` 使心跳重新 active，随后 `finally` 直接 `services.conn.close()`（第 678 行），未调用 `closeReader()`。
- 影响：正是 FIX-B 的 DIAG 症状 B 形态（连接关闭后仍有 5 s 定时器）；本例实际风险被两点限住——该 `ReaderViewModel` 无 parent，测试帧退出即引用计数归零（连同 `navigation` 上持有 `reader` 的闭包）被销毁；即便触发一次，`settleReadingTime` 的 `sqlite3.Error` 捕获会停表并记录 `heartbeat_error`。但若该测试日后迁到会话级 fixture/`qapp` 事件循环中，即变成真泄漏。
- 建议：`finally` 改为 `services.reader.closeReader(); services.conn.close()`（与本文件 `:642-643` 邻居测试一致）。

**F-4 [Nit] `tests/core/test_bootstrap.py:650`：docstring 与红日志事实不符**
- 事实：docstring 写"Pre-wiring this failed on `hasChapter is False`"，但 red log `:37-39,45` 显示修前实际失败在 `:671` 的心跳断言（`hasChapter` 在 navigate 前后都为 True）。
- 影响：误导后续审计（且恰好暗示存在过一次"改断言"的历史，虽然 red/green 同一版本已由行号证明）。
- 建议：改为"Pre-wiring this failed on the heartbeat-stopped assertion"。

**F-5 [Minor，行为回退；建议 Codex 判是否另立小 Task] `src/bootstrap/app.py:257-261` 未覆盖"经导航栏重返读者页"路径**
- 触发：生产 QML 导航栏渲染全部四页（`PrimaryNavigationRail.qml:21-32`，`pages` 来自 `_PAGE_LABELS`），点击"阅读器"→ `navigate("reader")`。序列：读书中 → 点"书架"（closeReader：心跳停、`hasChapter` 留 True）→ 点"阅读器" → `currentPageChanged("reader")` 被守卫正确忽略，但**不发射 `readerContextChanged`**（`viewmodel.py:80-83` 只在 `navigate` 发 page 信号），故 `_open_reader_chapter`→`openChapter`（唯一 `_heartbeat.start()` 处，`:113`）不执行，`ReaderView` 显示着已加载章节而心跳**保持停止**。
- 影响：该会话内阅读时长失去"5 s 崩溃粒度"（仍会在下一次 `nextPage`/离开/退出等 settle 点被整段补记，故非永久丢失）；同时形成"页面有章节、会话已 close"的不一致态。修前该路径心跳一直在跑，故属本次接线引入的小幅回退。
- 建议：在 `src/bootstrap/**`（无需动 QML/VM/service）即可闭合——`reader_context` 经 `navigate` 不会被清（AC-NAV-003），故可在同一 handler 的 `page == "reader"` 分支复用 `_open_reader_chapter()` 作 re-arm（需接受"重新 `openChapter`（重读进度、重建瓦片）"的语义）；若判为超范围，请立后续 Task 并写入残余边界。

**F-6 [Minor] `src/bootstrap/app.py:483`：退出期 flush 与活跃 workbench 写者争锁，而 `closeReader` 的 `_reading.close()` 无保护**
- 触发：pipeline 运行中退出工作台 → `aboutToQuit` 先于 `_shutdown_services` 的 drain 执行 → `settleReadingTime`→`add_time` 经 `SqliteReadingProgressStore.write`（`with self._conn:` 事务写，`PRAGMA busy_timeout=5000`、WAL，`connection.py:57,318-320`）与工作线程争写锁；前者已被 `except sqlite3.Error` 捕获（`viewmodel.py:469-475`），但紧接着的 `self._reading.close()`→`_touch`→`_persist()`（`service.py:158-161,367-380`）**无 try/except**，`database is locked` 会从 `aboutToQuit` 槽逃逸。
- 影响：进度最后一次 flush 失败 + traceback 噪音；异常在 Qt 从 C++ 调用槽的上下文里逃逸可能打断退出清理（`_shutdown_services` 不执行，靠 WAL 恢复，代码内已有该情形的既定兜底）。属 FIX-B 遗留的 `closeReader` 设计，但本次接线首次把它放到"工作线程可能正在写"的退出路径上。
- 建议：在 bootstrap 侧包一层（允许范围、3 行，沿用 `_shutdown_services` 的"stderr 报告而非静默"惯例）：
  `def _close_reader_on_quit(): try: services.reader.closeReader() except Exception as e: print(f"reader flush on quit failed: {e}", file=sys.stderr)`；或明确接受并写入 Handoff 残余边界。

## 四、设计取舍裁决（Handoff §4 三项）

- (a) `aboutToQuit` 一行 connect 无自动化测试：**接受**（理由见第二节第 4 点；静态核验：唯一 connect、时序先于 drain/关连接、无章节安全、smoke 子进程实跑不炸）。
- (b) `closeReader` 不清 `hasChapter`、契约=心跳停 + 进度 flush：**接受**。`ReadingService.close()` 只 `_touch`、`ReaderViewModel.hasChapter` 由 `progress is not None` 决定，均属 FIX-B 已冻结语义且在本 Task 禁止范围内；测试 `:669-670` 已把契约写死。**但 Task AC1 文本必须相应修订（F-1）。**
- (c) 离开读者页即 flush 进度（提前 flush 无损）：**接受**。校验依据：flush 前置了 `settleReadingTime`（`:119`），而修前心跳每 5 s 也在做同样的 `add_time`+`_touch(now=True)`，故"离开即写一次"总时长口径与修前等价（同类导航下写入次数反而更少，原来是每 5 s 一次）；"离开不保存"属需求变更，Handoff 已如此标注。

## 五、未覆盖风险

- **R-1 本文未取得 `git diff 0e34c5c3..de0bf175` 原始输出**（沙箱不可用）。已用"主树 base 状态等价 + 锚点平移 + 断言计数 + mtime 序位"替代证明；残余不确定性为：若 `0e34c5c3..7144e4fa` 之间主树对这两个代码文件有非锚点级改动且分支另有合并，本次等价性推理会失真（现有证据均不支持该假设）。建议集成核验时由 Codex 补跑 `git diff --check` 与 scope 校验作为最终口径。
- **R-2 未能重跑任何测试**（无法执行 pytest）。红/绿/定向/全仓 4 份日志的内容自洽（行号一致、skip 明细逐条、EXIT 齐备），但均为作者所出，非本会话复算。
- **R-3 红→绿溯源有一处不可查的机械动作**：red 结束 `18:03:02.475` 与 green 开始 `18:03:02.540` 仅隔 65 ms，说明接线是**以程序方式换入/换出**（如临时 checkout base 版 `app.py` 后回拷），而非两次运行之间手工编辑。日志内容（同一测试源码/行号、失败点恰为接线相关断言）与 mtime 序位（red < app.py < green）均支持其真实性，但该换入/换出脚本本身未入库，无法复核"red 用的是原封 base 文件"。
- **R-4 AC3 的运行时证据缺口**：退出路径只被 smoke 子进程间接执行，**无任何断言验证"退出后心跳已停/进度已 flush"**；如日后 `_shutdown_services` 的调用点或 `aboutToQuit` 语义变化，无回归保护网。
- **R-5 读者会话"半开"态的其它未覆盖面**：`closeReader` 后 `hasChapter=True` 且 `reader_context` 仍指向旧章节，`navigate("reader")`（F-5）之外还有 `_open_reader_chapter` 对空页目录 `return`（`app.py:235-238`）时也可能出现"章节已加载但未重新武装心跳"的组合，本次未做穷举；建议随 F-5 的后续 Task 一并盘点。
- **R-6 预存在的时长归因语义**：所有 settle 点（导航离开、翻页、退出）都会把"离开读者页期间的墙钟"计入 `total_read_seconds`/刷新 `last_read_at`（`settleReadingTime` 以 `_last_settle` 差值计入，无前台/可见性判定）。修前因心跳常驻每 5 s 结算，总量口径等价；本次未引入新口径，但若产品要求"离开不计时"，需另立需求（Handoff §4.2 已如此声明）。

## 六、给集成方的建议下一步

FIX-C 的实现范围、触发条件、退出时序、证据与范围约束均经核验成立；请 Codex 在集成时处置 **F-1（修订/豁免 AC1 文本，Task 勾选与 `status` 归属 Codex）**，并考虑把 **F-2（进度持久化断言）+ F-3（finally 收口）+ F-4（docstring）** 作为同一 commit 的 3 行级收尾（属允许范围，不需重新释放 Task），把 **F-5 / F-6** 记为残余边界或另立后续小 Task；随后按 Gate 4 完成 scope/`diff --check`/合并历史三方核验。建议给 ZCode 的可转发指令：`在 agent/zcode/DIAG-READING-EXPORT-001-FIX-C-quit-and-leave-wiring 上补 tests/core/test_bootstrap.py 的持久化断言与 finally closeReader、修正 :650 docstring（不改 src 语义、不新增依赖），重跑 tests/core + tests/reading_export + 全仓并追加 verification 日志，commit 后再交复核。`
