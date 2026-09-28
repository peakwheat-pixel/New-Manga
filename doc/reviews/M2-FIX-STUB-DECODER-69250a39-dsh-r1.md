approved_with_conditions

## 0. 审查对象与证据边界

| 项 | 值 | 来源 |
|---|---|---|
| 被审交付实现 head（delivery） | `5cacebfa25ef17ea3a487ac4fcb11a4590636661` | worktree reflog `logs/HEAD:5`（amend 结果）+ `verification/M2-FIX-STUB-DECODER/raw/06-scope-self-check.log:3` |
| 被审最终 tip / worktree HEAD | `69250a39ac3ff48c13c28cfd34241eb9fb78a494` | `.git/refs/heads/agent/zcode/M2-FIX-STUB-DECODER`（我直接只读读取，非 Owner 日志） |
| base / release | `f5d91425` / `fc419905c6a5b151f089d9fd78f7fccea97efb7b` | Task frontmatter:14-15、reflog `logs/HEAD:1-3` |
| ledger | claim `0f4f881a3cb8…` → accept `550b4269fe21…` → amend `5cacebfa25ef…` → task 回填 `69250a39ac3f…` | reflog `logs/HEAD:3-6`（与 Owner 声称的三 commit + amend 轨迹逐字吻合） |
| 审查方式 | **纯静态只读**：read/grep/glob + 只读读取 `.git/refs`、`logs/HEAD` 文本；未执行任何命令、未修改任何文件 | — |

- **verified-by-reading**：全部源码/测试/文档/日志内容、git 引用与 reflog 文本、以 grep 做的反向核查（尾部空白、`DecodedImage(` 构造点、`def test_` 计数）。
- **not_verified**：任何需要解释器/git 命令产出的运行面结论（§3），按协议归 Integrator。
- 该 Review 仅对上述两个固定 head 有效。

---

## 1. 分级问题清单

### P0 — 无

### P1 — 无

### P2 — 无

### P3（6 条，均为可读性/登记项，不阻塞集成）

**P3-1｜交付描述在"行级"不精确（非事实错误）**
- `src/bootstrap/core_service.py:54-56`：实际改动 = 2 行注释（`:54-55`）+ 1 行代码（`:56`），即 **+3/-1**；`raw/03-green-after-fix.log:5-6` 的 `git diff --stat` 亦为 `1 file changed, 3 insertions(+), 1 deletion(-)`。
- 而 `doc/handoffs/M2-FIX-STUB-DECODER-owner-delivery.md:14` 写"一行注释"，`verification/M2-FIX-STUB-DECODER/verification-results.md:13` 写"附一行注释"。
- 理由：Task `doc/tasks/M2-FIX-STUB-DECODER.md:35` 的 AC1 原文含"（注释注明取值理由）"，注释是 AC 要求项，故**不构成 scope creep，也不构成 AC 违背**；仅"一行"措辞与 +3/-1 不符。建议 Integrator 在集成记录中直接写 `+3/-1`，无需 Owner 返修。

**P3-2｜AC1 的 `mime_type` 取值在测试中未承重**
- `tests/core/test_stub_decoder.py:43-44`（`isinstance(img.mime_type, str)` + `!= ""`）与 `:58`（`!= ""`）均未锁定具体值 `"image/rgb"` → 若实现被改成 `mime_type="image/jpeg"` 或任意非空串，测试仍绿。
- 但缺陷类（字段名错误/必填字段缺失）已被完整锁定；且我 grep 确认 `DecodedImage.mime_type` 在 src 中**无消费者**——`src/application/importing/images/service.py:107-108` 只取 `decoded.width/height`，落库的 `mime_type` 属 artifacts/渲染域（`src/infrastructure/sqlite/schema.py:84`、`src/infrastructure/sqlite/artifacts.py:237`），与本 stub 无交集。故该值当前是惰性的，AC1"语义合理"由注释（`:54-55`）+ Handoff §实现发现 4（`owner-delivery.md:46`）以人审承担。
- 说明：`owner-delivery.md:46` 已主动声明 `image/rgb` 非 IANA 注册类型、以"非空 str + 保留原 rgb 语义"为判据，属**如实披露而非掩盖**。可选加固：收紧为 `== "image/rgb"`；不阻塞。

**P3-3｜测试耦合私有名/私有属性（经核对符合仓库既有惯例，登记即可）**
- `tests/core/test_stub_decoder.py:21-27` 导入私有类 `_PassthroughImageDecoder`、`:37` 经 `core.importer._decoder` 取实例。
- 反证非问题：`tests/core/test_core_assembly.py:225` 既有断言就是 `core.importer._decoder is decoder`；`tests/core/test_transport_credential_assembly.py:18`、`tests/core/test_shutdown_drain.py:54` 均直接导入 `_credential_resolver`/`_shutdown_services` 等私有名。测试注释（`:22-24`）已说明选择理由。
- 另注：该测试未做 identity 断言（装配若换成别的 decoder 仍会通过），该缺口由 `test_core_assembly.py:225` 的 identity 断言覆盖。

**P3-4｜红/绿证据不绑定 commit，判别力靠日志内嵌 diff 自证**
- `raw/02-red-before-fix.log:4` HEAD=`0f4f881a…`（claim），`raw/03-green-after-fix.log:4` HEAD 同为 `0f4f881a…` → 红/绿都产自"claim commit + 未提交工作树"（新增测试文件当时未入库）。
- 判别力仍然成立且可核对：红点源码行就是被修行（`raw/02:40`、`:62` 显示 `return DecodedImage(width=1, height=1, format="rgb")`，位置 `raw/02:44`、`:66` = `src\bootstrap\core_service.py:54`），异常 `TypeError: DecodedImage.__init__() got an unexpected keyword argument 'format'`（`:42`、`:64`）；绿日志内嵌 stat 证明当时工作树只有 `core_service.py` 一处 +3/-1（`raw/03:5-6`）。
- `owner-delivery.md:44` 主动声明"临时回滚再证红步骤省略"，属诚实披露；建议 Integrator 在最终 tip 补一次回滚再证红（命令见 §3），把该 P3 关闭为集成侧证据。

**P3-5｜交付 tip hash 未落 frontmatter（协议已声明由 Integrator 回填）**
- `doc/tasks/M2-FIX-STUB-DECODER.md:17` `delivery_head: null`；`doc/handoffs/M2-FIX-STUB-DECODER-owner-delivery.md` 无 YAML frontmatter；hash 只出现在 Task 正文 `:69` 与回填 commit message（reflog `logs/HEAD:6` 逐字含 "delivery tip=5cacebfa"）。
- 不构成闭环空引用（M2-AC3 review r1 P1-2 的那类问题）：hash 有两处落地且相互一致；且 `raw/06:8` 证明 handoff 文件本身就在 `5cacebfa` 的 diff 内，与"本文件即在该 commit 内"相符。与 M2-AC4 review r1 P3-5 同类，按模板 `doc/templates/HANDOFF.md:14` 由 Integrator 回填可接受。

**P3-6｜范围外同类 stub 使本 Task 目标只部分达成（Task 已明示，非本交付缺陷）**
- `src/bootstrap/core_service.py:84-86` `font_catalog/layout_engine/compositor=object()`，Task `:60`/`:70` 已登记为范围外观察项。
- 静态评估：image import 链现在真的走通——`image_decoder` 注入 `ImportImagesUseCase`（`src/bootstrap/core_assembly.py:627-631`），`copy_store`/`sink` 均为真实 adapter（`core_assembly.py:626, 630`）；但生产装配下渲染/排版类命令仍会因 `object()` 失败。建议另立 Task（或并入 ImportPages 扩面前的 check list）。

---

## 2. verified-by-reading（按四轴）

### 轴 1｜AC1 最小性：**PASS（verified-by-reading）**
- 修复点 `src/bootstrap/core_service.py:51-56` 仅 `_PassthroughImageDecoder.decode` 类体；`:57` 起的 `_StubStyleAnalyzer`、`:59-62`、`:65-89` `assemble_production_core` 其他注入均为原文（`:83-87` 与 `owner-delivery.md:45` 的"范围外观察"描述一致）。
- 契约零改动：`src/application/importing/images/ports.py:11-17` 仍是 `@dataclass(frozen=True)` 的 `width/height/mime_type` 三个必填字段、无默认值 → 修复后调用同时消除"多余 `format=`"与"缺失 `mime_type`"双重缺陷（先红日志只显示前者，因为 Python 先报未知关键字；后者为潜在第二重，与 Task `:29` 描述一致）。
- 全仓反向核查：`DecodedImage(` 构造点共 7 处（src 2 处：`core_service.py:56`、`src/infrastructure/importing.py:61`；测试 4 处；`verification/M2-AC4/raw/probe_export_semantics.py:52`），**全部用 `mime_type=`，无 `format=` 残留** → 该类缺陷无第二实例。
- 取值语义：`"image/rgb"` 非 IANA 注册类型，但（a）满足契约唯一约束 `str`；（b）无任何下游校验/落盘消费该值（见 P3-2 的反向核查）；（c）保留 stub 原 `rgb` 语义且注释在位 → 作为占位 stub 判定"合理"，与 Task AC1 措辞一致。

### 轴 2｜AC2 判别力：**PASS（verified-by-reading）**
- 走 production 装配路径（非"等价替代"）：`tests/core/test_stub_decoder.py:33` 调用 `assemble_production_core`（即 `main()` 用的同一函数，`core_service.py:366`），`:37` 经 `core.importer._decoder` 取实例；该属性链已逐跳核对：`core_assembly.py:627-628` 组装 `ImportImagesUseCase(image_decoder, …)` → `src/application/importing/images/service.py:46` `self._decoder = decoder`。Handoff `:43` 关于"`CoreServices` 无 `image_decoder`"的语义发现**属实**。
- 断言承重：`:40-44` 断言 `isinstance(DecodedImage)` + `width==1` + `height==1` + `mime_type` 非空 str；第二条场景 `:53-58` 用 4 种 payload（含 `b""`、非图像字节）覆盖 passthrough 全不抛。红点（`raw/02:38-44`）与绿（`raw/03:16-17`）仅差被修一行。
- 红点=被修复行：`raw/02:40/62` 源码行 + `:44/66` `src\bootstrap\core_service.py:54` 逐字对应 Task `:36` 与 `verification-results.md:19-22` 声称，无偏移。
- 附核：先红运行同时证明装配本身可用（异常发生在 `test:38` 的 `decode`，而非 `assemble_production_core`），故 `tmp_path/"data"` 用法与既有 `tests/core/test_core_service.py:61-63` 一致（`data_root = tmp_path / "data"`）。

### 轴 3｜范围与证据纪律：**PASS（verified-by-reading；执行面归 Integrator）**
- 允许路径：`raw/06:20-29` owner-only diff（`fc419905..5cacebfa`）共 9 个文件，全部落在 Task `:41-43` 允许范围内；`tests/` 侧只有 **A** `tests/core/test_stub_decoder.py`（`raw/06:24`），**无既有测试被修改**（与 AC 及禁令 `:47` 相符）；`src/` 侧只有 `M src/bootstrap/core_service.py`（`raw/06:23`）。
- 归属正确性：`raw/06:7` 的 `M doc/STATUS.md` 与 `:16` 的 `A verification/…/release-f5d91425.md` 属释放 commit——我以 reflog 独立佐证：`logs/HEAD:1-2` 显示 worktree 起于 `fc419905`，该两文件在 claim 之前已在分支上；`doc/STATUS.md:29` 内容确为 release checkpoint。
- 日志带头带尾：`raw/02:1-5`+`:71 EXIT=1`；`raw/03:1-7`+`:20 EXIT=0`；`raw/04:1-5`+`:55 EXIT=0`；`raw/05:1-5`+`:9 EXIT=0`；`raw/06:1-4` + 分段 `EXIT=0`（`:18`、`:30`）+ `DIFF_CHECK_EXIT=0`（`:33`）。头含 shell/解释器/HEAD/ISO 时间戳，齐备。
- 数字一致性：Task `:55`、Handoff `:19-20`、`verification-results.md:32-33` 与 `raw/04:9`（76 passed）、`raw/05:8`（32 passed, 2 xfailed）完全一致。
- **独立交叉验证（我做的，非 Owner 日志）**：对 `tests/core` grep `^\s*def test_` 得 **76** 命中，且该目录内无 `parametrize`、无 `skip`（只有 `test_bootstrap.py:31` 与 `test_core_assembly.py:239` 的 PySide6 `importorskip`），而 `raw/04:9` 报 `76 passed` 且无 skipped → "76 = 既有 74 + 新增 2、无静默取消/跳过"成立。
- 空白纪律：对 `src/bootstrap/core_service.py`、`tests/core/test_stub_decoder.py`、`verification/M2-FIX-STUB-DECODER/**` grep `[ \t]+$` 零命中，与 `raw/06:33` 的 `DIFF_CHECK_EXIT=0` 相容；amend 轨迹（`550b4269`→`5cacebfa`，whitespace-only）由 reflog `logs/HEAD:4-5` 独立证实，Handoff `:56` 的披露属实。
- NOT_RUN 如实：`owner-delivery.md:49-52`、`verification-results.md:60-63` 明示端到端 `import_files` 全链未跑（M2-IPC1 命令面无 import）、无 BLOCKED。判定：**如实，且与 `core_service.py:16-19` 冻结命令面（ping/ListBooks/shutdown）相符**。

### 轴 4｜回归风险（静态评估）：**低，无发现**
- 被改行只存在于一个仅在 `assemble_production_core` 内被实例化（`core_service.py:83`）的私有 stub 中；`tests/core` 其余测试不经过 `decode`（grep `_decoder` 仅 `test_core_assembly.py:218/225/248` 的 identity 断言，与被改行无因果关系）。
- strict xfail 未受影响：`raw/05:8` 实测仍 `2 xfailed` 而非 XPASS。逐条核对为本 Task 无关缺陷：
  - F-1 = export lineage 缺 `included_stale/missing_page_ids`，`tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py:545-556`，登记于 `doc/tasks/M2-AC4.md:49-50`；
  - F-2 = `handle_list_books` unknown/已知度通道缺失，同文件 `:750-760`，登记于 `doc/tasks/M2-AC4.md:52`、遗留转 `M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN`（`M2-AC4.md:87`）。
  - **注意点（已闭合）**：F-2 的 xfail reason 直接指向 `core_service.py` 的 `handle_list_books`（`:_fetch_page_counts`，`:169-185`）——与本次改动**同文件**，理论上存在"改一处误伤 xfail"的风险；静态上两处代码路径不相交（decoder 类体 vs SQL 计数），且 `raw/05` 实测未翻 XPASS → 判定受控。
- `m2_acceptance` 中的自备 decoder（`test_data_integrity.py:54`、`test_provider_fail_closed.py:65`、`test_reader_export_lineage_library_pagecount.py:91` 均为 `mime_type="image/png"`）不经 stub，不受影响。

---

## 3. not_verified（需集成方代跑；建议原样记录 EXIT）

环境（Owner/Task 口径）：`$py="G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe"`，`wt="G:/CODEX/New Manga.worktrees/M2-FIX-STUB-DECODER-zcode"`，Git Bash（win32）。

1. **固定 head 复跑（关闭 C1）**
   ```bash
   cd "$wt"
   git rev-parse HEAD            # 期望 69250a39ac3ff48c13c28cfd34241eb9fb78a494
   "$py" -m pytest tests/core/test_stub_decoder.py -v            # 期望 2 passed, EXIT=0
   "$py" -m pytest tests/core/ -q                                # 期望 76 passed, EXIT=0（74 既有 + 2 新增）
   "$py" -m pytest tests/m2_acceptance -q                        # 期望 32 passed, 2 xfailed, EXIT=0
   ```
2. **范围与最小性（关闭 C2，替换 Owner 自检）**
   ```bash
   git diff --name-status fc419905..5cacebfa      # 期望仅 Task 允许路径；tests 侧只有 A tests/core/test_stub_decoder.py
   git diff f5d91425..5cacebfa -- src/           # 期望仅 core_service.py：+3/-1（2 注释行 + mime_type 行）
   git diff --check f5d91425..5cacebfa            # 期望 EXIT=0
   git log --format=%H%n%s 0f4f881a..69250a39     # 期望 3 条：accept / amend / task backfill（可复核 delivery tip=5cacebfa）
   ```
3. **判别力加固（关闭 P3-4，可选）**：在最终 tip 上临时把 `src/bootstrap/core_service.py:56` 还原为 `format="rgb"`，跑 `"$py" -m pytest tests/core/test_stub_decoder.py -v`，期望 `2 failed`、Traceback 指向 `core_service.py:54`（还原后行号）、异常为 `unexpected keyword argument 'format'`；随后 `git checkout -- src/bootstrap/core_service.py` 并确认 `git status --porcelain src/` 为空（零残留）。我无法验证"工作树 == 5cacebfa 的 blob"，此项也顺带证明。
4. **尾随空白（我的核查是工作树内容层面）**：`raw/06:33` 的 `DIFF_CHECK_EXIT=0` 是对 commit 的判定；我只能证明当前工作树三个路径无尾随空白。第 2 组命令的 `git diff --check` 直接覆盖该结论。
5. **未读面**：commit object/message 内容（zlib 对象，静态只读无法解压）——仅以 reflog 文本旁证；`tests/m2_acceptance` 与 `tests/core` 的实际收集/参数化情况以复跑为准。

---

## 4. 结论与推荐下一步

**结论（双面）**
- **Architecture 面：PASS**。契约零改动（`ports.py` 未动、frozen dataclass 未扩字段）、无 schema/IPC/依赖变更、无分层新增（测试 `sys.path` 注入与 `tests/core` 既有惯例一致）、改动点单一且语义自洽。
- **Verification 面：PASS（verified-by-reading），执行面 NOT_RUN**。AC1/AC2/AC3 的每项声明我都以源码 + 日志逐行核对，并用 git 引用、reflog、grep 计数做了**三项 Owner 日志之外的独立交叉验证**（tip hash=`69250a39…`、三 commit + amend 轨迹、`tests/core` 76 计数），全部吻合；无 P0/P1/P2。
- 4 轴映射：AC1 最小性 PASS（1 个 src 文件、1 个类体）；AC2 判别力 PASS（真 production 装配 + 具体 width/height 断言 + 红点逐字=被修行）；AC3 证据纪律 PASS（带头带 EXIT、范围仅允许路径、NOT_RUN 如实）；回归风险低（strict xfail 未翻 XPASS，F-1/F-2 与本次改动路径不相交）。

**条件（approved_with_conditions；均属集成侧，不要求 Owner 返修）**
- **C1**：Integrator 在固定 head `69250a39ac3ff48c13c28cfd34241eb9fb78a494` 上复跑 §3 第 1 组四条命令，逐条记录 EXIT 与新日志（带真实 HEAD），核对 `2 passed / 76 passed / 32 passed+2 xfailed`。
- **C2**：以 §3 第 2 组 `git diff` 命令独立复算 AC1 最小性与范围（替代 Owner 自检日志），并把 `delivery_head=5cacebfa25ef17ea3a487ac4fcb11a4590636661` 回填 `doc/tasks/M2-FIX-STUB-DECODER.md:17`（关闭 P3-5）。

**推荐下一步**：本 Review 结论为 `approved_with_conditions`，可作 `doc/reviews/M2-FIX-STUB-DECODER-<tip>-dsh-r1.md` 归档。建议由 **Codex（Integrator，非本 Task 作者）** 在同一 worktree 执行 §3 第 1、2 组命令关闭 C1/C2，同时按 P3-1 在集成记录中把改动记作 `+3/-1`，然后 merge、回填 `delivery_head`/`integration_merge` 并置 `done`；P3-2（mime_type 具体值断言）与 P3-4（回滚再证红）作为可选加固记入集成记录即可；P3-6（`font_catalog/layout_engine/compositor=object()`）另立后续 Task，不在本次范围内扩张。
