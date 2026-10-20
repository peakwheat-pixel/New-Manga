# ZCode 独立 Review：PDF-STREAM-FIX-1

- **Reviewer**: ZCode（非作者）
- **日期**: 2026-10-20
- **审查对象**: 分支 `agent/dsh/PDF-STREAM-FIX-1`，HEAD `cbbe0c8d3`（fix=`bb54b6492`，基线=`d58748dee`）
- **审查范围**: `src/infrastructure/export/qt_free.py`（一行修复+注释）、`tests/export/test_pdf_stream_integrity.py`（5 个新测试）、`verification/PDF-STREAM-FIX-1/ac5-regression-baseline-comparison.md`

## 结论

**CHANGES_REQUESTED**

产品代码修复本身正确、最小、证据充分，无异议。唯一阻断项是一个 P1：`test_mupdf_reports_no_zlib_error` 以「声称 AC3、实际零断言、作者自证缺陷下仍绿」的形态留在永久测试套件里，是一个与本 Task 主题（「测试全绿但产品不可用」）同构的假绿信号，应当返修处置（删除或改写，见 P1 的三个选项）。返修只涉及测试文件与文档，不触碰 `src/**`。

**审查环境声明（影响证据等级）**：本会话 Bash 权限客户端故障（`No permission client configured for Bash`，主会话与子代理共 20+ 次探测均失败），一切 python/pytest 执行不可用。本 Review 基于：git 只读取证（可用）、全量源码与测试静态分析、既有 verification 证据交叉验证。运行级复验未做，逐项标注于「明确未核实」；取证环境已在 `%TEMP%/pdfstreamfix-review/` 搭好（回滚版 `src/`、HEAD 原样 `src_fixed/`、`probe.py`，两份 diff 已校验），任何有可用 shell 的会话可直接执行三条命令补齐。

## 逐项判定

### 3.1 修复本身是否正确 —— 通过

- **最小且正确：是。** `git diff d58748dee..cbbe0c8d3` 确认改动仅三个文件（M `qt_free.py` +11/-1、A 测试、A 证据文档）；`qt_free.py` 的改动就是 content stream 一处加 `zlib.compress` + 9 行注释（本会话独立跑通 git diff 核验，与任务书引用一致）。
- **其它调用点核实：作者的假设成立。** `_stream`（qt_free.py:253-255）无条件写入 `/Filter /FlateDecode`，全文件共 6 个调用点：font file（:56）、cidmap（:61）、to_unicode（:62）、SMask alpha（:80）、RGB image（:81）在修复前就已传 `zlib.compress(...)`；content stream（:104-105）是唯一不一致的调用点。修复后 6/6 一致。`/Length` 由 `str(len(payload))` 自动适配压缩后长度，无需另改。
- **两个正确性细节，均无问题**：压缩引入二进制字节不违反 PDF 格式（文件头本就带二进制注释行 `%\xe2\xe3\xcf\xd3`，qt_free.py:259）；`.encode("ascii")` 在修复前后同样安全（content 行仅含坐标数字与 hex 字符串，`_cid_text` 产出 hex）。
- **`_stream` 契约是否应该改：本次不应该，后续建议改。** 加 `compressed: bool` 参数只是把「忘压缩」换成「传错布尔」，没有消灭错误面。真正有防御性的方向是把 `zlib.compress` 收进 helper（调用点不再自己压缩，「忘压缩」在调用点不可表达），见 P2-1。这属于共享 helper 的契约重构，超出本 Task 最小修复范围，维持现状是正确裁量。

### 3.2 测试是否真的能抓缺陷 —— 通过（高置信，非运行级）

作者声称回滚修复后 `3 failed, 2 passed`。本会话无法复跑，但该声称与两条独立证据线完全吻合：

- **静态机制推理**（对每条测试逐一判定）：
  - `test_every_declared_flate_stream_actually_inflates`（AC2）**必 FAIL**：缺陷下 content 流是明文 `q 40 0 0 ...`，首字节 `0x71`；zlib 流的 CMF 低 4 位必须是 8（`0x78` 系），`zlib.decompress` 对 `0x71` 必然抛 `incorrect header check`。该断言与渲染器行为无关，是**规范级、引擎无关**的判别。
  - `test_rendered_page_is_not_blank`（AC4）**必 FAIL**：依赖 MuPDF 遇坏流跳过渲染 → 全白。此行为已有同机实测背书（`verification/SEC-FMT-IMPL-1/BUG-pdf-content-stream-deflate.md` §3.3：纯红页 5400 像素 0 非白）。
  - `test_searchable_pdf_also_renders`（R1）**必 FAIL**：同 AC4 机制，同一条 content 流。
  - `test_declared_length_matches_actual_bytes` **必 PASS**：缺陷下 `/Length` 声明的是明文长度，与实际自洽（本缺陷不产生长度失配）。
  - `test_mupdf_reports_no_zlib_error`（AC3）**必 PASS**：测试体只有渲染 + `capfd.readouterr()`，零断言（test_pdf_stream_integrity.py:114-115 自己注释 `recorded, not asserted`）。
- **交叉验证**：commit `bb54b6492` 的 message 与测试 docstring（:92-96）记录了同样的实测结果；修复后全量 `2294 passed`（cbbe0c8d3 证据文档）包含这 5 个测试全绿，与上述判定自洽。

**「测试全绿但功能不存在」的残余面**：修复后的防线是三层——AC2 inflate 断言（引擎无关的规范级）、AC4/R1 MuPDF 像素断言（第二引擎）、既有 `tests/core/test_p16_reader_export.py:580-590` PDFium 端到端像素断言（第三道，真实生产链路）。我没有找到这三层同时假绿的合理路径。两个小盲区登记于 P2-4（`_streams` 正则/`find(b"endstream")` 定界的理论假红面），概率可忽略。

**诚实性**：AC3 测试的 docstring 把「自己不工作、缺陷下仍绿、原因未查明」写得很清楚（:91-105），`recorded, not asserted` 直白标注。诚实。但「诚实标注」不等于「应当保留」，见 P1。

### 3.3 `test_mupdf_reports_no_zlib_error` 为什么无效 —— 应处置，且 AC3 并非不可测

- **是否应该删除而不是保留并标注：是（或等效改写）。** 保留的代价是永久性的：测试名 `test_mupdf_reports_no_zlib_error` 本身就是一个声称——CI 绿名单、测试计数、未来 grep「AC3」的人都会读到「MuPDF 无 zlib error 已有防线」，而事实是没有。docstring 只对打开文件的人可见。作者保留它的理由是「作为真实陷阱的文档」，但陷阱文档的正确载体是 verification 文档或任务文档，不是一个名字撒谎的活测试。这与本 Task 要修的东西（「测试全绿但产品不可用」）是同一类病。
- **有没有可靠捕获 MuPDF stderr 的方式：有一个高概率候选，未验证。** 子进程隔离：`subprocess.run([sys.executable, "-c", <渲染代码>], capture_output=True)`，在 OS 层用管道重定向 fd 2，绕开 pytest 进程内 capture（capsys/capfd）的全部怪异——无论 MuPDF 走 CRT `fprintf(stderr)` 还是自有 callback，只要最终写到标准错误句柄，管道就能收到。探针脚本已就绪：`%TEMP%/pdfstreamfix-review/probe.py`（对回滚版/修复版 PDF 各跑一次子进程渲染并检查 stderr），本会话因 Bash 故障未能运行。
- **「AC3 集成级 MuPDF 不报错」是否本身不可测：不是。** 两点：(i) 即便 stderr 文本真的不可机器捕获，**AC4 在逻辑上蕴含 AC3 的实质**——渲染出非白像素 ⟹ content 流被成功 inflate 执行 ⟹ 不存在 zlib error；AC4 绿则 AC3 实质成立，AC 不会失去保护。(ii) 子进程方案大概率可测（见上）。所以「不可测」目前只在「pytest 进程内 capture」这一层成立，不应升级为「AC 本身不可测」的结论。

### 3.4 回归证据是否站得住 —— 通过

- **方法有效性**：`git stash push -u` + `checkout d58748dee` 是否还原干净基线——**是**。本会话核验 `git status`：已跟踪文件零修改（非 `??` 行为 0），即 stash 实际只收纳了 untracked；这些 untracked（`.orchestrator/`、`doc/tasks/` 旧文件等）均不在 pytest 收集路径（`testpaths=tests`）内，也不被 9 个失败文件引用，**不可能影响结果**。
- **「同样 9 个失败」是否足以证明「非本次引入」：是。** 论证：修复后全量失败集合 = 这 9 个（文档记录 `9 failed, 2294 passed, 9 skipped`）；基线上跑同样 9 个文件得到集合相同的 9 个失败。若本次改动引入回归，必然表现为「修复后出现基线上没有的失败」或「修复后掩盖了基线上有的失败」——集合相等排除了两者。加之 diff 与这 9 个文件（providers/workbench）零交集、改动语义（PDF 流压缩）与它们无因果通路，排除是充分的。
- **诚实性良好**：文档明确记录全量不是绿的（§5.1）、9 个失败是真实的环境/状态问题且未修未假装修（§5.2-5.3）、未立 task 的归属交 Codex 裁定（§七）。符合本项目证据纪律。
- 一处复算指南的小缺陷见 P2-3（§六命令块不含 stash 往返，照抄有把 untracked 工作区留在 stash 里的风险）。

### 3.5 缺陷为什么能存活 —— 猜测部分成立，关键处需要修正

作者的猜测「所有测试都在生成后立即用同一套代码读回」**不完全对**。真实结构是三层：

1. **reading_export 层（与猜测一致）**：`tests/reading_export/test_export.py:125-132` 的 PDF 路径用 `StubPdfComposer` 造 `%PDF-STUB` 字节、断言仅前缀/`%%EOF`；`:419-449` 的真 composer 测试测的是 `application.export.pdf_qt.QtImagePdfComposer`（**不是**出缺陷的 `QtFreePdfComposer`），断言也只有字节前缀/页数正则/`startxref`。`QtFreePdfComposer` 在修复前**没有任何直接单测**（`git log -S "QtFreePdfComposer" -- tests/` 为空）。
2. **core P16 层（与猜测相反——独立验证存在）**：`tests/core/test_p16_reader_export.py:580-590`（本 Review 第一手核验）经 `assemble_production_core` → `QtFreePdfComposer()` 的**真实生产链路**导出 PDF，用 `pdfium.PdfDocument(...)` 渲染并断言**精确像素相等**（`(30,30,240)`/`(240,30,30)`，:585-586），searchable PDF 还断言文本抽取（:590）。这不是同构读回——这是货真价实的「独立实现 + 端到端 + 像素级」验证，自 `e2c07fa9b`（2026-10-16）起就存在，而缺陷正是该提交引入的。
3. **但它没响**：缺陷存在期间（10-16 → 10-20）该测试全绿（全量失败仅 9 个且全在 providers/workbench）。推理链封闭：断言是精确像素相等且走此链路 → PDFium 必然渲染出了正确颜色 → **PDFium 对「声明 FlateDecode、内容为明文」的流按容错路径照常渲染**，而 MuPDF 与 Chrome 拒绝。

**所以准确结论是**：缺口不是「没有独立验证」，而是**互操作性押在单一外部实现上，缺陷的可见性由该引擎的容错行为决定**。单引擎验证对「规范违反类」缺陷没有判别力——你抽到的引擎宽容，产品就是坏的而套件全绿。 ZIP/CBZ 侧同病且更彻底：读写两侧都是标准库 `zipfile`（同构读回），唯一独立验证（7z `t`/`l` 子进程）至今只存在于 `verification/SEC-FMT-IMPL-1/probe-ac5-interop.py`，未进 pytest。这确实是测试策略层面的缺口，不只是这一个 bug；本次新测试的 AC2（`zlib.decompress`，引擎无关的规范级断言）正是对的方向，建议按 P2-2 登记后续固化。

## 发现的问题（按严重度）

### P0

无。

### P1

**P1-1：`test_mupdf_reports_no_zlib_error` 应当处置，不应以现状保留。**
测试名声称 AC3（「MuPDF 不报 zlib error」），测试体零断言，作者自证缺陷下仍绿（docstring test_pdf_stream_integrity.py:91-105）。它每跑一次都在产出一条虚假的绿色 CI 信号。处置三选一（按优先序）：

1. **改写为子进程断言版**（若实验证实可捕获）：测试体内 `subprocess.run([sys.executable, "-c", <渲染该 PDF 的最小代码, 传 PDF 路径>], capture_output=True, text=True)`，断言 `result.returncode == 0` 且 `"zlib error" not in result.stderr`。前置条件：先跑 `%TEMP%/pdfstreamfix-review/probe.py` 确认子进程 stderr 能捕获到回滚版的 `zlib error: incorrect header check` 且修复版为空。
2. **若实验证明子进程也捕获不到**：删除该测试，并在本 Task 文档记录「AC3 的 stderr 文本不可机器断言（机制证据链：pytest 进程内 capture 失败 + 子进程实验失败，见 verification/）；AC3 实质由 AC4 蕴含（渲染非白 ⟹ inflate 成功 ⟹ 无 zlib error）」。
3. **最低限度**：若 1、2 本轮都不可行，改名为 `test_mupdf_opens_and_renders_without_raising`（名字与实际行为一致：它确实验证 `pymupdf.open` + `get_pixmap` 不抛异常，有烟雾价值），docstring 移除对 AC3 的认领，AC3 完成度如实标注为「由 AC4 蕴含，直接断言 NOT_RUN」。

### P2

**P2-1：`_stream` 契约集中化（后续 Task，不阻断本次）。** 把 `zlib.compress` 收进 `_stream`（或更名 `_flate_stream`），使「忘压缩」在调用点不可表达。本次缺陷正是唯一一个绕过约定的调用点；契约靠注释维持就会再犯。

**P2-2：测试策略缺口登记（修正版 §3.5，后续 Task，不阻断本次）。** 两件事值得进 Backlog：(a) PDF 导出的外部验证本次已固化为双引擎（规范级 inflate + MuPDF 渲染），但 CBZ/ZIP 的独立验证（7z）仍在 verification 探针层、未进 pytest；(b) 「单引擎验证对规范违反类缺陷无判别力」应作为本项目导出类测试的选型准则记入验证纪律（P16 的 PDFium 精确像素断言是好的，但正是它单独在场时给了四天假绿）。归属由 Codex 裁定。

**P2-3：回归证据文档 §六复算命令不自包含。** 命令块只有两条 `git checkout`，不含开头的 `git stash push -u` 与结尾的 `git stash pop`。照抄执行的人会把 untracked 工作区留在 stash `pdf-fix-wip` 里。补全往返步骤。

**P2-4：`_streams` 辅助函数的定界健壮性（登记即可）。** `pdf.find(b"endstream", start)`（test_pdf_stream_integrity.py:42）理论上可能被压缩流内碰巧出现的 `endstream` 字节序列截断造成假红；用已解析的 `/Length` 定位流边界更稳。当前输入（40x60/60x90 纯色小图）下概率可忽略。

## 明确未核实的内容

1. **一切运行级验证**（本会话 Bash 权限客户端故障，主会话与子代理均无法执行任何 python/pytest）：
   - 未独立复跑修复后 5 个测试全绿（依据：cbbe0c8d3 证据文档全量 `2294 passed` 含新文件 + 静态核验）；
   - 未独立复跑「回滚后 3 failed, 2 passed」（依据：作者实测记录 + 逐测试机制推理，两条线一致，见 §3.2）;
   - **未运行 MuPDF stderr 子进程捕获实验**——`%TEMP%/pdfstreamfix-review/probe.py` 已就绪未跑，P1-1 选项 1 的前置条件未验证；
   - 未复跑回归基线对照（依据：文档记录 + 方法有效性评估，见 §3.4）。
   取证环境待命：`%TEMP%/pdfstreamfix-review/`（回滚版 `src/`、HEAD 原样 `src_fixed/`、`tests/`、`probe.py`；回滚版与基线 `d58748dee` 的差异已经 diff 校验为仅 content stream 一行）。补齐命令：
   - `cd /g/CODEX/New\ Manga && python -m pytest tests/export -v`
   - `cd %TEMP%/pdfstreamfix-review && PYTHONPATH=src python -m pytest tests/test_pdf_stream_integrity.py -v`
   - `python %TEMP%/pdfstreamfix-review/probe.py`
2. **PDFium 容忍坏流的具体机制**：由「缺陷期 P16 端到端像素断言全绿」反推（推理链封闭），无直接机制实验（如对坏 PDF 单跑 pdfium 观察行为）。
3. **capfd/capsys 捕获不到 MuPDF stderr 的根因**：作者记录「未查明」，本会话未能推进。候选解释（CRT stderr 与 pytest capture 的交互、MuPDF 自有 error callback 的输出路径）均未证实；P1-1 的子进程方案正是为绕开该未定机制设计的。
4. **回归证据中 3 个 workbench 失败的根因**：作者明确记录未深究，本 Review 同样未深究（其目的仅是排除与本次改动的因果，已达成）。
