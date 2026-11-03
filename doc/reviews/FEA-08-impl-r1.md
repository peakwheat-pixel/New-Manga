---
task_id: FEA-08
reviewer: DSH 独立子 agent（实现上下文外；未参与 FEA-08 实现、scope 起草/修订或返修）
reviewer_kind: subagent
author: ZCode CLI impl session（实现 c422bf164；DSH 登记 42de98812）
base_commit: 2870a9fa52b73fdf344cc723e59957d76d60e395
reviewed_head: 0a2a069a809f4f6f2fa6fc8543f03bdc7b88fe62
implementation_head: c422bf16461309b4b077426cccd0f06a83a3583f
task_card_head: 42de988123b4ad980659c0940931153382bbf064
decision: changes_requested
verdict: changes_requested
p0: 0
p1: 2
p2: 9
provenance:
  agent: DSH 独立子 agent（本会话；未参与实现/返修；只读仓库与 workspace 原型）
  mode: read_only_except_this_report
  head_delta: '42de98812..0a2a069a8 仅 doc/TASK_LEDGER.md + doc/checkpoints/GOAL-PROGRESS-2026-11-02.md（DSH 治理记录）；实现体、证据与 Task 卡未变'
  implementation_commit: c422bf164（交付 36 文件）；登记 commit 42de98812
  scope_base: 2870a9fa5（scope-r2 approved head；范围冻结）
  governance: 'check.ps1 PASS(3 warnings)；verify_pins 15/15；未 push；本报告为唯一仓库写入'
---

# Review：FEA-08（impl-r1）

## 0. 结论

**verdict = `changes_requested`（P0=0 / P1=2 / P2=9）。**

技术结论大体成立：H4 strict lease 在 NTFS 上以同一句柄/流 + 句柄级身份得到可证明的一致读取；H5 合成回收/还原/失败保留链路与零清空 API 约束成立；H6 exact/candidate 二分、digest 类型、GIF 首帧、PDF 页码/参数、重复成员名 occurrence 均有实测结果；AC-4 60 格矩阵无 mock/inferred PASS；无生产代码改动；build/test/check/pins 与旧 FEA-06 四 PNG 门禁通过。

但存在两个 P1 阻断项：

1. **AC-3 文件夹 golden fixtures 未入库**：`M8M9` 使用的 `folder_v1/folder_v2` 只存在于非 Git 的 workspace `tmp`，未进入 `verification/FEA-08/fixtures`、`fixtures_manifest.json` 或 Canonical Evidence；从入库证据独立复跑 H6 会在 M8M9 处以 `FileNotFoundError` 失败，必须从 workspace `tmp` 补拷目录后才能复现。AC-3“golden fixtures 与结果报告”对五类输入之一不完整。
2. **9/36 Canonical Evidence pin 不能按 Task 卡声称的 `git cat-file` 方法复现**：Task 卡写“sha256 一律为 git blob 哈希（复现：`git cat-file -p <commit>:<path>`）”，但 EV-F08-11/28/30/31/32/33/34/35/36 的登记值是 CRLF 工作树字节的 SHA-256；原始 Git blob（LF）的 SHA-256 不同，实测 27/36 才与 `git cat-file` 一致。证据内容本身在库，但 pin 的复现口径不成立；`.gitattributes` 只有 `doc/tasks/*.md text eol=lf` 等既有规则，未覆盖 `verification/FEA-08/**`。

因此 **AC-3 判 PARTIAL、AC-4 判 PARTIAL**，Task 卡 `AC-3/AC-4 <<MET>>` 不能按现状维持；AC-1/AC-2 可判 MET，但附 P2 条件（明细见表）。建议 DSH 派一次聚焦证据收口，不改变技术结论、不扩大产品范围。

## 1. 审查范围与依据

- **固定点**：`reviewed_head = 0a2a069a8`（审查结束时的当前 HEAD）；实现体 `c422bf164`；Task 卡 pin `42de98812`；scope 冻结 `2870a9fa5`。审查开始时 HEAD 为 `42de98812`，审查期间 DSH 新增 `e69f8164c`/`0a2a069a8` 两个治理记录 commit；`42de98812..0a2a069a8` 实测仅 `doc/TASK_LEDGER.md` 与 `doc/checkpoints/GOAL-PROGRESS-2026-11-02.md`（6+6 行），实现体、`verification/FEA-08/**` 与 Task 卡均未变。本报告按当前 HEAD 固定，但审查对象仍是同一实现体。
- **被审对象**：`doc/tasks/FEA-08.md`（AC 冻结、Canonical Evidence 36 项）、`doc/research/FEA-08-source-capability.md`、`doc/handoffs/FEA-08-impl.md`、`verification/FEA-08/**`、workspace `G:\CODEX\New Manga.workspace\FEA-08\prototype\**` 与 `out\**`。
- **依据**：提案 `:457/:465/:469/:512–:514/:794–:796/:929`；[ADJ-001](../contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md)；[AD-003](../AD-003_REFERENCED_SOURCE_ARCHITECTURE.md)；[Task FEA-08](../tasks/FEA-08.md) 冻结 AC；[scope-r2](FEA-08-scope-r2.md)；[REVIEW 模板](../templates/REVIEW.md)。
- **范围边界**：只审实现交付与证据，不重新冻结 scope，不替 DSH 做终裁；不修改源码/Task/证据；不 push。
- **未覆盖**：USB/SMB/云占位真机行为（无硬件）；IFileOperation per-item sink/flags 实跑；真实用户回收站/真实库；SQLite/DB（Task BLOCKED 明确排除）。

## 2. Standards（executed）

- **写域（实现 commit）**：`git diff --name-only e8b3aea61..c422bf164` 仅 36 个文件，全部落在 Task `allowed_paths`（`doc/research/FEA-08-*`、`doc/handoffs/FEA-08-*`、`verification/FEA-08/**`）；`git diff --name-only 2870a9fa5..HEAD -- src apps experiments tests packaging scripts tools` 为空。`doc/TASK_LEDGER.md`/checkpoint 的 HEAD 变更是 DSH 治理记录，不是实现夹带。**PASS**。
- **无生产代码改动**：build/test 前后 `git status --porcelain=v1` 为空；产品源码零 diff。**PASS**。
- **证据纪律**：每脚本日志有 `$ python ...`、`EXIT=`；`prototype_hashes.txt` 14/14 与 workspace 脚本 SHA-256 一致；`run_all.log` 有逐步骤输出。**PASS（脚本层）**。但 Canonical Evidence 的 36 项 pin 有 9 项不按 `git cat-file` 复现，属证据纪律缺陷 → **F08I1-002（P1）**。
- **安全边界**：全仓/workspace 搜索 `SHEmptyRecycleBin|EmptyRecycleBin|SHERB_` 的调用=0（命中仅为注释）；H5 所有 destructive 调用经 `recycle_guarded` 白名单断言（仅 lab 前缀）；`find_recycle_entries(VOLUME='G:\\', lab)` 只还原 lab 前缀条目；`C:` 用户回收站 2 条未被触碰；`G:` 0→0；无回收站设置改变。**PASS**。
- **临时数据**：`run_all.py` 运行时有清理逻辑，但当前 workspace `tmp\fixtures` 仍有合成 fixture；报告“tmp 运行后清理”与最终状态不一致 → **F08I1-010（P2）**（仅合成数据，无真实用户数据）。
- **依赖/许可**：报告 §7 登记 Pillow/pypdfium2/PyMuPDF/7-Zip/pywin32；PyMuPDF AGPL 仅研究、不进生产闭包；pdfium BSD/Apache 为生产候选；7-Zip 仅生成 fixture；无新增生产依赖。**PASS**。

## 3. Spec（executed）

### AC-1（H4）— **MET（strict；附 P2）**

- **同一句柄/流**：`lease.py:47-60` 的 `read_digest` 只调用 `fwin.read_handle_all(self.handle)`，不按路径重开；`lease.py:70-84` 的 `diagnostic_reopen_digest`/`diagnostic_unchecked_read` 明确标注为对照，不参与协议输出。`fwin.py:126-143` 为句柄 `ReadFile`。
- **句柄级身份**：`fwin.py:62-95` 的 `FileIdentity` = `volume_serial + file_index + size + mtime_100ns`，`from_handle` 取 `GetFileInformationByHandle`；`read_digest` 读前/读后同句柄比对，不一致抛 `LeaseUnavailable`。
- **场景结果**：S1 基线完整旧 digest；S2 strict 写者/覆盖均 blocked + 完整旧；S3a 覆盖式替换 blocked + 旧 digest；S3b rename-aside + rename-in 后仍完整旧 digest，且路径重开=新内容的反证成立；S4 WriteFile 中途写 → `unavailable`，含混合流对照；S5a/S5b mmap 写两时序 → `undetected_mixed`（盲区），S5c strict 阻止 mmap 写者；S6 删除/S7 重命名 → 完整旧 digest。10 场景均 measured。
- **mmap**：已实测并如实登记 strict 可挡、tolerant 下 mmap 写不更新 mtime 的混合流盲区；报告 §3.3-2 与 matrix `h4_summary` 明确“tolerant 对 mmap 只能判 UNAVAILABLE”。结论方向正确。
- **NTFS/其他卷**：本机 C/D/E/G/H 均为固定 NTFS（`probe_env.py` 实测）；USB/SMB/云在矩阵为 LIMITED(mocked/inferred)，无一 PASS。
- **保留 P2**：S5a/S5b 原始结果仍是 `outcome=digest_returned`、`mixed_digest_risk=false`，矩阵 NTFS H4 状态仍写 `PASS`（note 才写 tolerant+mmap=UNAVAILABLE）；若生产允许 tolerant，AC-1 断言②“不得出现混合 digest 假成功”不成立。见 **F08I1-003**。
- **保留 P2**：S2 `writer_attempts.write_open` 记录为 `blocked(win32=None)`，报告 §3.2 写 `win32=32`；S5a/S5b 的 `mtime_changed` 由不存在的 `identity_before` 计算（恒 false）。见 **F08I1-004**。

### AC-2（H5）— **MET（with P2）**

- **判定操作**：R1 单文件回收 + 还原 digest 一致；R2 非空目录回收 + 逐成员 digest；R3 空目录回收；R4 占用失败保留 + digest 不变；R5 计划/执行间路径替换 → identity 不匹配拒绝、零 destructive；R5b 同名目录顶替 → 拒绝；R6a 执行前崩溃 → 事实判定 retained、不重发；R6b 执行后结果未知 → 事实判定 completed + 还原 digest；R9 批量 1/3 占用 → 逐项事实核对（a 回收、b/c 保留），还原后三项 digest 全一致。9 个 measured PASS；R7/R8 为 LIMITED(mocked)。
- **零清空 API / 仅合成路径**：`fwin.py` 不封装清空类 API；`h5_run.py` 的 `recycle_guarded` 对每个 path 断言 `lab.lab` 前缀；`find_recycle_entries` 只匹配 lab 前缀。全仓/原型搜索清空类调用=0。**PASS**。
- **回收站条目处置**：`restore_log` 5 条（page_001、vol01、empty_dir、crash_after、batch_a），`bin_baseline=0`、`bin_final=0`、`leftover=0`；本次独立复跑 G: 也保持 0→0；C: 用户条目 2 条未触碰。
- **保留 P2**：首轮独立复跑 R2 FAIL（`recycle_entry_found=false`、`restored_count=0`），随后 7 次 PASS（2 次手工 + 5 次循环）；`h5_run.py:146` 在 `SHFileOperationW` 返回后立即枚举 `$RECYCLE.BIN`，没有等待/轮询，存在时序窗口；且 `h5_run.py` 不因 `verdict=FAIL` 非零退出，`run_all.py:28-30` 只检查进程返回码。见 **F08I1-005**。
- **保留 P2**：R6b 的 `no_reissue` 只是 `decision == completed`，不是 destructive 调用计数；R5b 的 `refused=True`/`identity_match=False` 为硬编码；R3 的 `fallback_rmdir_used` 从未置 true 且 verdict 无条件 PASS；目录不可回收分支实际未触发；R7/R8 仍为 inferred(mocked)。见 **F08I1-006**。

### AC-3（H6）— **PARTIAL**

- **判定口径**：`h6_run.py` 实现 bytes 强 digest → 规范像素 digest（`exif_transpose` → RGB8 → 原始尺寸）→ dhash 候选（≤10 仅候选）；文件夹 `folder_membership+bytes_sha256`；容器 `member_content_sha256`（ZipInfo 逐 occurrence）；PDF `rendered_pixel_sha256` + 页码 + `pdfium_info/dpi/scale/colorspace`；GIF 仅帧 0。M1–M16 结果均有 `result` + `digest_type`。
- **实测覆盖**：未变图片 exact；JPEG 重编码/CMYK/物理旋转候选；翻转 no_match；EXIF 方向、灰度/RGB exact；文件夹 diff `needs_confirmation` + 重命名候选 + 重复同图独立 occurrence；ZIP/CBZ 重编码 exact；重复成员名 candidate + ordinal 0/1；ZipCrypto 带密 exact、无密 needs_password、AES 标准库 `NotImplementedError` 如实登记；PDF 重生成 exact + 2 页页码/参数；GIF 首帧 exact + 蓝帧反证。**逻辑与结果类型成立**。
- **P1 缺口**：`M8M9` 使用的 `folder_v1/folder_v2` 未入库 `verification/FEA-08/fixtures`；`results/fixtures_manifest.json` 21 项无 folder；`make_fixtures.py:117-125` 创建文件夹但未 `reg()` 登记。独立从 evidence fixtures 复跑 H6 时 M8M9 直接 `FileNotFoundError`，补拷 workspace `tmp\fixtures\folder_v1|v2` 后才得到同样的 `folder_membership+bytes_sha256`/`needs_confirmation`。**AC-3 不能算完整 MET** → **F08I1-001（P1）**。
- **P2 缺口**：M12/M13/M15 均为同一 fixture 对自身比较（`h6_run.py:253,257-261,283-284`），exact 判定是平凡成立；AES ZIP 实际不可读但矩阵 ZIP H6 仍 PASS；dhash 候选边界只有 0/5/36，无 10/11 邻界 fixture。见 **F08I1-007**。
- **P2 缺口**：`h6_results.json:5` 的 `fixtures_manifest` 指向不存在的 `fixtures/fixtures_manifest.json`，实际为 `results/fixtures_manifest.json`。见 **F08I1-011**。

### AC-4（交付完整）— **PARTIAL**

- **矩阵**：4 卷类型 × 5 输入类别 × 3 能力 = 60 格；机械核对 `PASS 15 / LIMITED(mocked) 30 / LIMITED(inferred) 10 / UNAVAILABLE(inferred) 5`；`PASS` 仅出现在 measured 的 NTFS 行，mock/inferred 无 PASS。`needs_new` 7 项、依赖/许可、fixture 生成方式与“无生产代码改动”均有落点。**矩阵与 mock 口径成立**。
- **P1 缺口**：9/36 Canonical Evidence pin 不按 Task 卡声明的 `git cat-file` 复现（见 §5 与 F08I1-002）；Canonical Evidence 的“complete”状态不能按现状证明。
- **P2 缺口**：`matrix.py:69-100` 对 NTFS 行硬编码 `PASS`，`ntfs_row_from_results` 计算出的 `h5v/h6v` 未用于逐格判定；矩阵没有逐格“现状/需新增”字段（仅全局 `needs_new`）；NTFS 的 H4/H5 对五类输入全部标 measured，但 H4 只测了单文件、H5 只测了文件/目录，ZIP/CBZ/PDF 的 H4/H5 属于格式无关推断而非逐类实测。见 **F08I1-008**。
- **报告依赖/许可**：§7 与 `evidence_manifest.json` 记录 PyMuPDF AGPL 仅研究、pdfium 生产候选、7-Zip 仅生成 fixture、pyzipper 未引入；无新增生产闭包。**PASS**。

## 4. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| F08I1-001 | **P1** | `verification/FEA-08/fixtures/`（无 `folder_v1`/`folder_v2`）；`results/h6_results.json:84-113`；`make_fixtures.py:117-125`；`doc/research/FEA-08-source-capability.md:105,170` | AC-3 文件夹 golden fixtures 未入库：M8M9 使用的 6 个文件夹成员只存在于非 Git workspace `tmp`；`results/fixtures_manifest.json` 21 项无 folder；报告 §10 仍称“21 项预生成原件”。从入库证据无法复现 M8M9，AC-3“golden fixtures 与结果报告”不完整，AC-3 不能维持 `<<MET>>`。 | `Get-ChildItem verification/FEA-08/fixtures -Directory`=0；`fixtures_manifest.json` 无 folder；把 evidence fixtures 复制到临时 `tmp/fixtures` 跑 `h6_run.py` → M8M9 `FileNotFoundError: .../folder_v1/p1.png`；补拷 workspace `tmp/fixtures/folder_v1|v2` 后 15 项 result 类型与证据一致。 | 将 `folder_v1/p1-3`、`folder_v2/p1,p2renamed,p4` 纳入 `verification/FEA-08/fixtures/` 并在 `fixtures_manifest.json`/`evidence_manifest.json`/EV 表登记；或明确把 M8M9 降为 `LIMITED`/`NOT_RUN` 并删除“measured PASS”表述。 | open |
| F08I1-002 | **P1** | `doc/tasks/FEA-08.md:73-112`（EV-F08-11/28/30/31/32/33/34/35/36）；`.gitattributes`（无 `verification/FEA-08/**` eol 规则） | Task 卡声称“sha256 一律为 git blob 哈希（复现：`git cat-file -p <commit>:<path>`）”，但 9/36 的登记值是 CRLF 工作树字节 SHA-256；原始 Git blob（LF）SHA-256 不同。干净 checkout + `core.autocrlf=false`/`git cat-file` 无法复现，25% 的 Canonical Evidence 不能按声明方法验证；这直接影响 AC-4“交付完整”。 | 逐行用 `git cat-file blob <blob>` 原始字节算 SHA-256：27/36 匹配；9 项不匹配（见 §5 表）。工作树 `Get-FileHash` 36/36 匹配。示例：EV-F08-33 h4_results 期望 `ee167b07...`，blob 实际 `be90b375...`。 | 加 `.gitattributes` 规则 `verification/FEA-08/** text eol=lf` 后重新生成/重算 LF pin（该文件不在 Task allowed_paths，需 DSH 扩围或作为集成处置）；或把 EV 表复现命令改为明确的 checkout/CRLF 口径并同步 `sha256` 定义。目标 36/36 可复现。 | open |
| F08I1-003 | P2 | `results/h4_results.json:105-138`（S5a/S5b）；`results/capability_matrix.json:8-12`；报告 §3.3-2 | S5a/S5b 原始记录是 `outcome=digest_returned`、`mixed_digest_risk=false`、`classification=undetected_mixed`；矩阵 NTFS H4 状态仍为 `PASS`，只在 note 写“tolerant+mmap=UNAVAILABLE”。报告 §3.3-2 的“tolerant 只能判 UNAVAILABLE”是建议/结论，不是结果字段。若允许 tolerant 共享，AC-1 断言②“不得出现混合/部分新内容 digest 假成功”直接不成立；strict-only 的生产约束必须显式。 | 读 S5a/S5b JSON；对照报告 §3.2 表与矩阵 note；独立复跑 H4 同样得到 `undetected_mixed`/`digest_returned`。 | 在结果中把 S5a/S5b 标为 `unavailable` 或 `LIMITED(mmap-blind)`，`mixed_digest_risk=true`；矩阵 NTFS H4 改为 `PASS(strict) / UNAVAILABLE(tolerant+mmap)`，避免单值 PASS 被误读；报告把 strict-only 写成硬约束。 | open |
| F08I1-004 | P2 | `results/h4_results.json:35-40`（S2）；`h4_run.py:120-121,235-241`；报告 §3.2 | S2 `write_open` 记录 `blocked(win32=None)`，报告 §3.2 写 `win32=32`；`FileIdentity` 的 mtime 比较只在 S4 的 `unavailable` 分支出现，S5a/S5b 的 `mtime_changed` 由不存在的 `identity_before` 计算，恒 false；`outcome_for` 对所有 `digest_returned` 置 `mixed_digest_risk=false`，与 `undetected_mixed` 分类矛盾。 | 读 `h4_results.json` S2/S5 行；`S5c` 能正确记录 `win32=32`，说明 S2 的 `e.winerror` 用法错误；S5a/b 的 `mtime_changed` 字段无实测来源。 | S2 用 `e.args[0]`/`ctypes.get_last_error()` 记录 32；S5 显式读读前/读后 `FileIdentity` 再算 `mtime_changed`；`undetected_mixed` 时 `mixed_digest_risk=true`；报告数字与 JSON 对齐。 | open |
| F08I1-005 | P2 | `h5_run.py:140-160`（R2 无轮询）；`h5_run.py:99-368`（无 failure exit）；`run_all.py:28-30`（只看进程返回码） | H5 R2 的 `entries_for_lab()` 紧跟 `SHFileOperationW` 枚举 `$RECYCLE.BIN`，shell 尚未把条目落盘时会得到 `recycle_entry_found=false`/`restored_count=0`；首轮独立复跑出现 R2 FAIL 而进程仍 EXIT=0，随后 7 次 PASS。`h5_run.py` 不因场景 `FAIL` 非零退出，`run_all.py` 只看 returncode，因此“run_all EXIT=0”不能证明 9 个 PASS 全部成立。 | 本会话 `review-h5` 首跑：R2 `FAIL`（`recycle_entry_found=false`、`restored_count=0`），EXIT=0；随后 `h5_run.py` 7 次 R2 PASS（2 次手工 + 5 次循环）；`fwin.bin_count('G:\\\\')` 始终 (0,0)。代码检查 R2 无 retry/poll。 | 在 R2/R9 用 `SHQueryRecycleBinW`/`entries_for_lab` 做有界轮询（如 500 ms × N）；`h5_run.py` 对任何 PASS 预期场景 FAIL 时 `sys.exit(1)`；`run_all.py` 同时校验 `results/*.json` 的 verdict，不只 returncode。 | open |
| F08I1-006 | P2 | `h5_run.py:253-305`（R6b）；`:230-249`（R5b）；`:162-182`（R3）；`:334-347`（R7/R8） | AC-2 的若干分支证据强度不足：R6b 的 `no_reissue` 只等于 `decision == completed`，没有 destructive 调用计数（R6a 有）；R5b 的 `refused=True`/`identity_match=False` 是硬编码，实际只捕获“打开目录失败”；R3 的 `fallback_rmdir_used` 从未置 true，verdict 无条件 PASS；“目录不可回收”分支在 Win11+NTFS 未触发；R7/R8 仍为 inferred(mocked)。 | 读 `h5_results.json` R6b（无 `no_destructive_reissued` 字段）与 R5b/R3 行；`h5_run.py` 对应行；`h5_results.json:192-203` 的 R7/R8 `evidence_type: inferred(mocked)`。 | R6b 记录 before/after `destructive_calls`；R5b 用真实 identity/type 检查并记录 `current_identity`；R3 记录实际 `fallback_rmdir_used` 路径或明确标 `LIMITED(mocked)`；目录不可回收分支加 mock 失败注入并标 LIMITED。 | open |
| F08I1-007 | P2 | `h6_run.py:253`（M12）、`:257-261`（M13）、`:283-284`（M15）；`:68`（dhash 阈值）；`results/h6_results.json:137-194,282-288`；`capability_matrix.json:52-56` | M12/M13/M15 都是同一 fixture 对自身比较，`exact_match` 平凡成立，不能证明“另一份同内容加密/重复名 fixture 可精确匹配”；AES ZIP 实测 `NotImplementedError`，但矩阵 ZIP H6 仍 `PASS`（只在 note 提 pyzipper）；候选边界只有 dhash 0/5/36，缺 10/11 邻界。 | 读 `h6_run.py` 与 `h6_results.json`；M15 `bytes_digest_a`/`bytes_digest_b` 相同、`container_bytes_differ=false`；M13 `aes_with_password.result=error`；M2/M5/M3 距离 0/5/36。 | 为 M12/M13/M15 增加独立副本（或从同一密文复制到不同路径，至少证明路径无关），或明确标“self-consistency”而非 exact；AES 在矩阵 ZIP H6 标 `LIMITED(pyzipper)`；补 dhash=10/11 fixture 证明候选边界。 | open |
| F08I1-008 | P2 | `matrix.py:69-100`；`results/capability_matrix.json` 全表；报告 §6 | 矩阵 60 格完整、mock 无 PASS，但 NTFS 行的 H4/H5/H6 状态是硬编码 `PASS`，`ntfs_row_from_results` 的 `h5v/h6v` 未参与逐格判定；没有逐格“现状/需新增”字段（只有全局 `needs_new`）；NTFS 的 H4/H5 对五类输入全部标 `measured`，而 H4 只测单文件、H5 只测文件/目录，ZIP/CBZ/PDF 的 H4/H5 没有逐类实验。 | 读 `matrix.py`：`ntfs_row_from_results` 返回 h5v/h6v 但未使用；矩阵 15 个 NTFS 格均 `PASS`；`h4_results` 无 ZIP/CBZ/PDF 场景；`h5_results` 只有 R1/R2/R3 文件/目录。 | 逐格增加 `current`/`needed`（现状/需新增）字段；对 H4/H5 的格式无关推断显式标 `inferred` 或在 note 说明“volume-level measured, format-agnostic”；矩阵生成器从 `h4/h5/h6` 逐项结果推导/校验，任一底层场景非 PASS 时不得写 PASS。 | open |
| F08I1-009 | P2 | `doc/tasks/FEA-08.md:114`；`doc/handoffs/FEA-08-impl.md:35` | Task 卡写“dotnet build/test 与 check/pins 门禁值见下「门禁记录」”，但文件没有该章节；Handoff 写“见 Task 卡记录”，同样指向不存在的内容。门禁数值只存在于 commit `42de98812` message 与本会话复跑，Canonical Task 卡缺记录，后续集成/关闭无法从卡片核验。 | 逐行读 Task 卡（114 行后直接进入“待 scope-r2 确认”）；`Select-String '门禁记录'` 仅命中引用行；commit message 有 build 0/0、1292/0/57、check PASS(3)、pins 15/15。 | 在 Task 卡增加“门禁记录”表：命令、HEAD/commit、EXIT、0w/0e、1292/0/57、check PASS(3)、pins 15/15、四 PNG SHA、禁止范围 diff=0；Handoff 改指该表。 | open |
| F08I1-010 | P2 | `run_all.py:51-63`；`results/run_all_log.json:25-29`；报告 §2/§10 | `run_all.py` 运行末尾删除 `tmp` 所有项，`run_all_log.json` 记 `tmp_removed=["fixtures","h4_lab"]`/`tmp_remaining=[]`；但审查时 workspace `FEA-08\tmp\fixtures` 仍有 21+ 文件（含 `_enc_src`、`folder_v1/v2`），与报告“tmp 运行后清理”不一致。合成数据无真实用户信息，但 Task 明确要求运行后清理并留日志。 | `Get-ChildItem workspace\FEA-08\tmp` 当前仍见 `fixtures`；`Get-ChildItem tmp\fixtures -Directory` 见 `_enc_src/folder_v1/folder_v2`；`run_all_log.json` 与报告 §10 宣称 cleaned。 | 在最后一步统一清理 `tmp`（含 `_enc_src`/folder）并记录 `tmp_remaining`；若需保留用于复跑，显式登记保留原因/路径，不写“已清理”。 | open |
| F08I1-011 | P2 | `results/h6_results.json:5`；`run_all.py:40-49`；Task 卡 `:114`；报告 §10 | `h6_results.json` 的 `fixtures_manifest` 写 `fixtures/fixtures_manifest.json`，该路径不存在；实际是 `results/fixtures_manifest.json`。Task 卡 `:114` 说“python run_all.py（workspace 原型 14 脚本）”，但 `run_all.py` 只执行 5 个（fixtures/H4/H5/H6/matrix），其余 9 个是诊断/证据 staging；容易把“14 脚本 hash 登记”误解为 run_all 覆盖全部。 | `Test-Path verification/FEA-08/fixtures/fixtures_manifest.json`=False；`Test-Path results/fixtures_manifest.json`=True；`run_all.py` 5 次 `run_step`；`prototype_hashes.txt` 14 行。 | 改指向 `results/fixtures_manifest.json`；Task 卡/报告写清“14 个登记脚本，run_all 执行 5 个核心步骤，stage_evidence 单独生成 manifest”。 | open |

## 5. 验证

| 场景 | 命令/步骤 | 环境/head | 结果 | 证据 |
|---|---|---|---|---|
| 固定点/零写入 | `git rev-parse HEAD`；`git status --porcelain=v1` | `0a2a069a8`；实现 `c422bf164` | **PASS**：HEAD 固定；审查开始时 porcelain 为空；本报告为唯一仓库写入 | 命令输出 |
| build | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | Windows 11 / .NET SDK 10.0.401 | **PASS**：0 warning / 0 error，EXIT=0 | workspace `review-build.log`（临时） |
| 无过滤全量 | `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --nologo` | 同上 | **PASS**：**1292 passed / 0 failed / 57 skipped**，EXIT=0；逐程序集 21/38/51/253/117/31/128/653，skip 0/0/28/0/0/0/22/7 | workspace `review-test.log`（临时） |
| 治理检查 | `pwsh -NoProfile -File tools\governance\check.ps1 -TaskPath doc/tasks/FEA-08.md` | 同上 | **PASS**（3 warnings：9 非终态 Task、STATUS/PLAN 预算 80%），EXIT=0 | 命令输出 |
| 冻结 pin | `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | 同上 | **PASS**：15/15，EXIT=0 | 命令输出 |
| 旧 FEA-06 四 PNG | `Get-FileHash verification\FEA-06\screens\*.png -Algorithm SHA256` | 同上 | **PASS**：reader `8533c263…78b2`、settings `fd30b166…a162`、shelf `307f8f67…8b0a`、workbench `d5d878bb…2df5`，与 FEA-06 卡一致 | 命令输出 |
| 禁止范围 diff | `git diff --name-only e8b3aea61..c422bf164`；`git diff --name-only 2870a9fa5..HEAD -- src apps experiments tests packaging scripts tools` | 同上 | **PASS**：实现 commit 36 文件全在 allowed_paths；产品路径零 diff；HEAD 的 `TASK_LEDGER`/checkpoint 为 DSH 治理记录 | 命令输出 |
| 原型脚本 hash | 14 个 `.py` 重算 SHA-256 对照 `prototype_hashes.txt` | workspace prototype | **PASS**：14/14 一致 | 命令输出 |
| Canonical Evidence pin | 36 行逐项 `git cat-file blob <blob>` 原始字节 SHA-256 | `c422bf164` | **FAIL（P1）**：27/36 与登记值一致；9 项不一致（EV-F08-11/28/30/31/32/33/34/35/36）；工作树 `Get-FileHash` 36/36 一致 | 命令输出 |
| H4 独立复跑 | 复制 `fwin.py/lease.py/h4_run.py` 到隔离目录，`python h4_run.py` | workspace 副本 | **PASS（结果类型）**：10 场景分类与证据一致（S4 unavailable、S5a/b undetected_mixed、其余 complete_old_digest）；无进程失败 | 命令输出 |
| H5 独立复跑 | 复制 `fwin.py/h5_run.py` 到隔离目录，`python h5_run.py` ×8（首跑 + 7 次） | workspace 副本 | **PASS with caveat**：首跑 R2 FAIL（`recycle_entry_found=false`、`restored_count=0`，EXIT=0），随后 7 次 PASS；每次 G: 0→0、leftover=0 | 命令输出 |
| H6 独立复跑（入库证据） | 复制 evidence fixtures 到临时 `tmp/fixtures`，`python h6_run.py` | workspace 副本 | **FAIL（P1）**：M8M9 `FileNotFoundError: folder_v1/p1.png`；证明文件夹 golden fixtures 未入库 | 命令输出 |
| H6 独立复跑（补 folder） | 再补拷 workspace `tmp/fixtures/folder_v1|v2`，重跑 | 同上 | **PASS**：15 项 result/digest_type 与证据一致（M1–M16），含 M8M9 needs_confirmation、M14 exact、M16 exact | 命令输出 |
| 安全/合成路径 | 全仓+prototype 搜索 `SHEmptyRecycleBin|EmptyRecycleBin|SHERB_`；读 `h5_run.py`/`fwin.py`；`probe_env.py` | `0a2a069a8` | **PASS**：调用=0（仅注释）；回收只经 `recycle_guarded` lab 前缀；C: 用户回收站 2 条未触；G: 0；无设置改变；`probe_env.py` 显示 C/D/E/G/H 均固定 NTFS | 命令输出 |
| 临时数据 | `Get-ChildItem workspace\FEA-08\tmp`；读 `run_all_log.json` | 同上 | **FAIL（P2）**：`tmp\fixtures` 仍在（含 `_enc_src/folder_v1/v2`），与 `tmp_remaining=[]`/报告“已清理”不一致 | 目录/JSON 对照 |
| 未 push | `git branch -r --contains c422bf164`；`git rev-parse origin/main` | 同上 | **PASS**：无远端 ref 包含交付 commit；`origin/main=b1c1f5a568` | 命令输出 |

## 6. Architecture 结论

**PASS（原型边界内）。** 实现仅新增 workspace 原型脚本、`doc/research/FEA-08-*`、`doc/handoffs/FEA-08-*` 与 `verification/FEA-08/**`；无 Host/Core/DB/schema/UI/共享契约/生产依赖改动。H4 的同一句柄/身份协议、H5 的合成回收/还原/失败保留、H6 的 exact/candidate 与 digest 类型均与 AD-003/ADJ-001 的“隔离原型、不碰真实库、原文件操作独立授权”边界一致。PyMuPDF AGPL 仅研究、pdfium 生产候选、pyzipper 未引入的许可处置正确；无回收站清空 API、无真实用户数据访问。**保留 P2 见 F08I1-003/006/008；P1 见 001/002。**

## 7. Verification 结论

- **门禁/回归层 PASS**：build 0w/0e；全量 1292/0/57；check PASS(3)；pins 15/15；旧 FEA-06 四 PNG 不变；实现 commit 写域仅 allowed_paths；产品源码零 diff；未 push；原型脚本 14/14 hash 匹配；H4/H6 结果类型可复现（H6 需补 folder 目录）。
- **证据完整层 PARTIAL**：P1-001（folder fixtures 未入库）与 P1-002（9/36 pin 不可按声明复现）阻断“Canonical Evidence complete”；P2 的 H4 字段、H5 时序/分支、H6 自比较/AES、矩阵逐格、门禁记录、temp 清理需收口。
- **不得宣称**：AC-3/AC-4 已完整 `<<MET>>`；H5“所有 measured 场景稳定 PASS”；H6“AES ZIP 已覆盖”；“tmp 已清理”。技术结论（strict H4、H5 合成链路、H6 exact/candidate）不受 P1 内容层否定，但交付证据需补。

## 8. 复审与下一步

1. **P1-001**：把 `folder_v1/folder_v2` 纳入 `verification/FEA-08/fixtures/`，登记 `results/fixtures_manifest.json`、`fixtures/evidence_manifest.json` 与 EV 表；或把 M8M9 降为 `LIMITED/NOT_RUN`。建议前者。
2. **P1-002**：为 `verification/FEA-08/**` 加 `text eol=lf`（需 DSH 扩围/集成处置）并重算 9 个 pin，或把 EV 表复现口径改为明确的 checkout/CRLF 方法；目标 36/36。
3. **P2 收口**：H4 字段（F08I1-003/004）、H5 轮询/失败 exit/分支（005/006）、H6 自比较/AES/边界/manifest（007/011）、矩阵逐格（008）、门禁记录（009）、temp 清理（010）。
4. 新 head 后复审只核 P1 闭合 + 无回归；DSH 再做集成验证与关闭。**不 push。**

## 9. 其他观察（不单列 finding）

- `probe_env.py` 的 pypdfium 冒烟用了无参 `PdfDocument()`，在 Pillow/pypdfium2 当前版本会抛 `missing 1 required positional argument`，且 `V_PYPDFIUM2`/`V_PDFIUM` 打印为 `?`；H6 用 `PdfDocument(path)` 实跑正常，`h6_results` 的 pdfium 版本为 153.0.7999.0。该诊断脚本失败不影响 H6 证据，但建议修正以免误读。
- `run_all.py` 只跑 5 个核心脚本；`h4_diag_replace.py`、`h5_diag*.py`、`h5_cleanup_leftovers.py`、`stage_evidence.py` 是诊断/证据 staging，不在 `run_all` 链路；Task 卡/报告的“14 脚本”应写明“14 个登记脚本，5 个核心步骤”。
- `doc/TASK_LEDGER.md` 与 checkpoint 在审查期间随 DSH 新会话交接 commit 前移（`e69f8164c`/`0a2a069a8`），属治理记录；实现体、证据与 Task 卡未变，不改变本报告对 `c422bf164` 的结论。
