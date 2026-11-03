---
id: FEA-08
title: Source/回收站隔离原型（H4/H5/H6 能力矩阵与技术报告）
kind: prototype
governance_version: 3
status: in_review
approval: scope-r2 **approved**（ZCode CLI fresh session，P0=0/P1=0/P2=2；2026-11-03；报告 doc/reviews/FEA-08-scope-r2.md）
suggested_owner: zcode
owner: zcode
reviewer: scope-r2 approved（ZCode）；impl-r1 **changes_requested**（D-9 独立子 agent，P0=0/P1=2/P2=9）；impl-r2 **changes_requested**（Codex 独立会话，P0=0/P1=3/P2=4，报告 doc/reviews/FEA-08-impl-r2.md）；impl-r3 **changes_requested**（Codex 独立会话，P0=0/P1=0/P2=5，报告 doc/reviews/FEA-08-impl-r3.md）；impl-r4 **changes_requested**（Codex 独立会话，P0=0/P1=0/P2=5，报告 doc/reviews/FEA-08-impl-r4.md）；impl-r5 Reviewer 待 DSH Appointment（Codex 新独立上下文；R5 finding 全部处置）
depends_on:
  - FEA-01-FREEZE-1
base_commit: 2870a9fa52b73fdf344cc723e59957d76d60e395（scope-r2 approved head；范围冻结）
branch: main
worktree: G:\CODEX\New Manga
integration_commit: null
delivery_head: f015108ad（R5 证据 commit；Canonical Evidence 72 项逐项 pin @该 commit）
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/FEA-08
allowed_paths:
  - doc/tasks/FEA-08.md
  - doc/research/FEA-08-*.md
  - doc/handoffs/FEA-08-*.md
  - doc/reviews/FEA-08-*.md
  - verification/FEA-08/**
---

# FEA-08：Source/回收站隔离原型

> 依据：`doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md` S3 FEA-08 行、H4/H5/H6 表（:794–:796）、§15.4 出口定义（:929）、精确匹配口径（:457/:469）、回收站语义（:512–:514）；`doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md`；`doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md`；`G-CONTRACT`/`G-DELETE-CONTRACT` 已 CLOSED（2026-11-01，AD-003 §5/STATUS；提案内 "OPEN" 为冻结时快照，字节不动）。
> 范围已由 scope-r2 approved 冻结（2026-11-03）；`ready` 可实施；workspace 派发 prompt 已按冻结 AC 同步。
> R2 返修（2026-11-03）：impl-r1 changes_requested（P1=2/P2=9）处置完成；证据全链重出并 re-pin @ `7b176be6a`；交付说明见 `doc/handoffs/FEA-08-impl-r2.md`。
> R3 返修（2026-11-03）：impl-r2 changes_requested（P1=3/P2=4，Codex）处置完成——H6 规范像素 digest 绑定尺寸、容器成员身份唯一映射、pin 自校验按登记 commit 逐行复现、矩阵逐卷 evidence/语义断言、run_all 原子 staging（失败回滚不污染 Canonical）、门禁原始日志与 57 项 skip 来源入库；交付说明见 `doc/handoffs/FEA-08-impl-r3.md`。
> R4 返修（2026-11-03）：impl-r3 changes_requested（P0=0/P1=0/P2=5，Codex）处置完成——H5 语义门禁（还原 digest/类型拒绝/无永久 fallback/计数必须为整数）、事务化晋升（先写新内容再换、逐项回滚并核对）、容器唯一内容映射正例（M21/M22）、check 原始日志耗时/环境、fixtures 计数勘误；交付说明见 `doc/handoffs/FEA-08-impl-r4.md`。
> R5 返修（2026-11-03）：impl-r4 changes_requested（P0=0/P1=0/P2=5，Codex）处置完成——矩阵补齐全部 H5 语义事实、晋升事务升级为「旧集 hash 快照 + 逐项登记/恢复 + 恢复完整核对才报 rolled_back」、重复成员名双侧对称核验（M23）、门禁原始日志与摘要口径修正、gates_capture 实际 SHA 登记；交付说明见 `doc/handoffs/FEA-08-impl-r5.md`。


## 路径口径裁定（有意偏差登记，F08R1-003）

- **原型/脚本**：`G:\CODEX\New Manga.workspace\FEA-08\prototype\`（非 Git，控制仓库体积；FEA 线 workspace 根级实践）；Task/证据登记路径与每个脚本 SHA-256（`verification/FEA-08/prototype_hashes.txt`，16 个登记脚本）。
- **报告**：`doc/research/FEA-08-source-capability.md`（研究类，归 research；不写入冻结设计目录）。
- **临时数据**：`G:\CODEX\New Manga.workspace\FEA-08\tmp\`（合成数据；`run_all.py` 运行后实际清理，`tmp_remaining=[]` 入 `results/run_all_log.json`）。
- 与提案 :929 "experiments/ + doc/design/ + workspace/tasks/FEA-08" 的偏差即上述三点，理由：原型非生产资产、报告非设计冻结物、临时数据沿用 FEA 线既有 workspace 根级实践。
- **depends_on**：`FEA-01-FREEZE-1`（已存在 Task）；FEA-00 仅作依据引用，不入 depends_on。
- **Canonical Evidence pin 口径（R4 / F08I1-002 + F08I2-001，DSH 裁决 + 集成处置）**：pin `sha256` = 被 pin commit 的 **Git blob 字节（LF 规范）**的 SHA-256，复现 `git cat-file -p <commit>:<path>`；工作树 `Get-FileHash` 与之一致。**`pin_selfcheck.py` 逐行读取 Task 表登记的 commit 复核**（不再只信 index：R2 曾把已变更文件的旧 commit 当通过，F08I2-001），并做 stage-index blob 与干净 checkout（`git checkout-index`）四方校验；仅 `pin-verify.log`（自校验脚本自身输出，自引用无收敛解）以 SHA-256 pin（commit 列 `-`），其余 69 文件均有 commit pin。集成处置：`.gitattributes` 已增 `verification/FEA-08/{*.json,**/*.json,**/*.log,**/*.md,**/*.txt}` → `text eol=lf`（DSH 提交 `07724b88d`；该文件不在本 Task allowed_paths，属集成动作，不计入实现写域）。
- **R2/R3/R4 实施分工**：ZCode R2 session 完成脚本/证据改造（10:08–10:39 额度耗尽中断，未提交）；DSH 以 Integrator 身份完成 R2 收口与全部 R3/R4 返修（H6 判据、矩阵、事务化 staging、门禁原始日志、H5 语义门禁）。impl-r2/impl-r3 均由 Codex 新独立上下文复核（未参与实现）；impl-r4 待 Codex 新独立上下文复核（DSH 不自审）。

## 目标（原型，不产出生产实现）

隔离环境（synthetic 非真实资料、临时卷/目录）验证并交付：
- **H4 稳定源 lease**：读取期间检测外部替换/重命名/删除/断连/共享写/内存映射写；同一已验证句柄/流一致读取并计算 digest；不可保证返回 unavailable。
- **H5 Windows 回收站**：IFileOperation/SHFileOperation 仅对合成路径操作；失败/取消/部分失败/中断不永久删除；receipt/恢复核对；负向原型。
- **H6 精确页面匹配**：按 :457/:469 口径的 golden fixtures（PDF 重生成、ZIP/CBZ 重编码/重复名、GIF 首帧、色彩/方向、加密格式）；无法唯一精确匹配只给候选。

## OUT

- 生产 Source/导入实现、Host `SourceAccessRegistry`/grant、Core schema/DB、UI 集成（FEA-09+）。
- 真实用户文件/真实库/AppData 写入；改变文件系统或回收站设置；对非合成路径发起回收。
- **禁止 `SHEmptyRecycleBin` 等清空类 API**（避免清空用户真实回收站）。
- 无证据的 PASS；承诺覆盖所有卷/格式。

## BLOCKED / 限制登记

- 无硬件的卷类型/云盘行为：LIMITED/UNAVAILABLE，交产品裁决。
- **测试 SQLite/DB 文件行为不在本卡范围**（H4/H5/H6 为文件系统/OS 层验证；Source DDL 未冻，耦合未冻结 schema 会污染结论）。
- H6 新格式：登记候选策略，不扩大自动匹配。
- 原生 200% DPI/a11y 与本卡无关（FEA-07 residual，D-1）。

## 验收（scope-r2 冻结；R3 证据收口）

- [x] **AC-1（H4）**：三断言全 measured（10 场景，h4_results.json）。 <<MET>>
  1. digest 取自打开时验证过的**同一句柄/流**；读取前后以句柄级身份（volume serial + file index）与 size/mtime 比对，一致才成立；
  2. 读取中途外部替换/写入的结果只能是 **unavailable 或完整旧 digest**，不得出现混合/部分新内容 digest 的假成功；杜绝 check 后按路径另开文件；
  3. 矩阵场景含"内存映射写"；不可证则该项 LIMITED/UNAVAILABLE。
  - R2 收口：S5a/S5b 字段自洽（classification=undetected_mixed，detail.mixed_digest_risk=true，outcome_protocol=digest_returned，评估 outcome=unavailable，mixed_digest_risk_field_consistent=true）；S2 写者 `blocked(win32=32)` 实测；S5 mtime_changed 由读前/读后真实 FileIdentity 计算；h4 summary 明示 strict-only 生产硬约束（F08I1-003/004）。
- [x] **AC-2（H5）**：判定操作 = 失败/取消/中断后目标仍在原路径（保留），或成功回收时存在于回收站且**还原后 digest 与回收前一致**；覆盖提案 :512–:514 分支（不可回收卷/策略、网络盘限制、路径被替换、结果未知、目录不可回收则保留且不得改调永久 rmdir）；**禁止清空类 API、仅合成路径**；合成 fixture 回收站条目测试后还原并删除（数量/结果入日志）或显式登记保留；"模拟中断"恢复判据 = receipt + 文件系统事实核对，不重发 destructive 操作。 <<MET>>
  - R2 收口：R2/R9 回收站条目有界轮询（`entries_poll`）；`h5_run.py` 期望 PASS 场景 FAIL 时非零退出；`run_all.py` 二次校验 results verdict；R6b destructive 计数 5→5（`no_destructive_reissued=true`）；R5b 类型/属性实测（`current_type=directory`）；R3 "不可回收→保留不 fallback rmdir" 分支经 mock 失败注入（ret=0x79）走通并标 LIMITED(mocked)（F08I1-005/006）。\n  - R4 收口（F08I3-001）：`matrix.derive_ntfs` 与 `run_all.verify_results` 增加 **H5 语义门禁**——不只信 verdict：R1/R6b `restored_digest_matches=true` 且 restored 列表全真；矩阵与总驱动**共享同一组** H5 必需事实：R1/R6b 还原 digest 与 restored 列表、R2 成员 digest/restored_count、R3 不可回收分支 `fallback_rmdir_used=false`（不得 fallback 永久 rmdir）、R4 保留+digest 不变、R5/R5b 拒绝且零 destructive、R6a 不重发、**R6b 三个 destructive 计数必须存在且为整数、执行后==恢复后**（缺失 `None` 不再通过）、R9 逐文件还原 digest、R1/R2/R9 entries_poll 合法且未超时。R5 收口（F08I4-001）：矩阵此前只验子集，已补齐全部字段且与 `run_all.verify_results` 逐字段一致。
- [x] **AC-3（H6）**：按 :457/:469 二分"精确匹配/候选"并附判定所用 digest 类型（图片强 digest；文件夹成员身份+digest；容器成员内容 digest/规范解码像素 digest、尺寸、方向、唯一性；重复成员名保持独立 occurrence；感知 hash/OCR 仅候选；GIF 仅首帧；PDF 记录页码与渲染参数）；golden fixtures 与结果报告。 <<MET>>
  - R3 收口：**19 场景 measured**；`folder_v1/v2` 六个成员入库（EV 逐文件 pin），H6 直接对入库 fixtures 运行（`fixtures_root` 记录）；**规范像素 digest 绑定尺寸**（`sha256("WxH\0"+RGB)`，F08I2-002；M19 为 2×6 vs 3×4 同像素字节反例 → 仅 `candidate`，`exact_blocked_by_size_mismatch=true`）；**容器 exact 要求成员身份唯一一对一定位**（重复同图但成员名不同 → `needs_confirmation`，M20；F08I2-003）；M12/M13/M15 独立副本/独立密文两路径比较（自读对照标 self-consistency）；dhash 阈值邻界 M17（10→candidate）/M18（11→no_match）；AES ZIP 如实标 LIMITED(pyzipper)；`fixtures_manifest` 指针指向实际存在的 `results/fixtures_manifest.json`（F08I1-001/007/011）。\n  - R4 收口（F08I3-004）：容器唯一映射判据升级——**按 occurrence 构建“内容 → 成员名多重集”映射**：唯一内容可跨名唯一对应（M21 唯二内容改名/换位 → exact）；重复内容需相同 name/ordinal 锚（M22 → exact）；锚不一致才 needs_confirmation（M20）；重复名不同内容仍 candidate（M12）。R5 收口（F08I4-003）：重复成员名在**两侧**独立核验——任一侧存在重复名即 candidate，新增 M23 非对称反例并断言左右互换均为 candidate。共 **22 场景 measured**（M21/M22 正例 + M23 非对称反例）。
- [x] **AC-4（交付完整）**：能力矩阵为二维结构 = 卷类型（NTFS 本地/USB/SMB/…）× 输入类别（单图/文件夹/ZIP/CBZ/PDF）逐项"现状/需新增"结论；每项标注证据来源 **measured/mocked/inferred**，**mock/推断不得记 PASS（上限 LIMITED(mocked)）**；技术报告含依赖/许可（如加密 ZIP/PDF fixture 需最小新依赖，二选一：登记许可+不进生产闭包，或预生成 fixture+SHA-256）；无生产代码改动。 <<MET>>
  - R3 收口：矩阵逐格含 `current`/`needed`，且**每个卷分支显式赋值 H4/H5/H6 各自 evidence**（非 NTFS 卷不再继承上一轮 NTFS 的 measured，F08I2-004）；NTFS 行状态由 h4/h5/h6 结果**及语义断言**推导（strict 拦截断言、GIF 蓝帧反证、尺寸绑定、容器唯一映射、回收分支计数；任一项被破坏即降级，不写 PASS——F08I2-005），H4/H5 未逐格式实测的格标 `LIMITED(inferred: volume-level, format-agnostic)`，ZIP 的 AES 分支标 `LIMITED(pyzipper)`；mock/inferred 无 PASS；**R4 收口（F08I3-002/003/005）**：`run_all` 晋升改为事务化（新内容先写临时文件、旧文件登记 journal 后才移动；任一步失败逐项恢复并核对；全部晋升成功后才提交 journal/发布成功日志，失败不冒充 EXIT=0），空输出/耗时/环境写入门禁原始日志；**R5 收口（F08I4-002/004/005）**：晋升前先对旧 Canonical 集做 hash 树/文件快照，失败恢复后必须**完整核对旧集 hash** 才报 `rolled_back=true`（未恢复 backup 明确列出）；门禁原始日志重采集与摘要口径修正（7 份 raw，command/EXIT/cwd/shell/elapsed 齐全）；`gates_capture.py` 实际 SHA 已与 `prototype_hashes.txt` 一致；Canonical Evidence **72 项**（69 文件逐行 commit-blob/worktree/index-blob/干净 checkout 四方校验 + `pin-verify.log` 自身 SHA-256 pin），门禁原始日志与 57 项 skip 来源入库（F08I1-002/008/009、F08I2-004/005/007、F08I3-002/003/005）。

## 交付与证据

- 原型/脚本：`G:\CODEX\New Manga.workspace\FEA-08\prototype\`（非 Git；16 个登记脚本 SHA-256 见 `verification/FEA-08/prototype_hashes.txt`）。
- 报告：`doc/research/FEA-08-source-capability.md`（R4 收口版）。
- 证据：`verification/FEA-08/**`（fixtures 目录 **44 文件 = 43 内容文件 + `evidence_manifest.json`**；results 7 件；logs 8 件 + `gates.log` + `test-skip-inventory.md`（57 项逐项来源）+ `gates-raw/` 原始输出（build/test/pins/四 PNG/禁止 diff/安全搜索/check + manifest + phase1 values）+ `pin-verify.log`；`prototype_hashes.txt`；共 **72 文件**，EV 表逐文件登记）。
- 复现：`python ...\prototype\run_all.py`（双生成 fixtures → 原子 staging → stage_evidence → H4/H5/H6(直接对入库 fixtures，含 M8M9/M19/M20)/矩阵 → results 双层校验 → 结果/日志原子晋升 → tmp 清理；失败回滚旧 Canonical 集）；`python ...\prototype\h6_run.py --fixtures ...\verification\FEA-08\fixtures`（H6 独立复跑）；`python ...\prototype\gates_capture.py --phase1/--phase2`（门禁原始日志 + 57 项 skip 清单）；`python ...\prototype\pin_selfcheck.py`（`git add` 后四方 pin 自校验）。
- Handoff：`doc/handoffs/FEA-08-impl.md`（impl-r1）、`...-impl-r2.md`（R2）、`...-impl-r3.md`（R3）、`...-impl-r4.md`（R4）、`...-impl-r5.md`（R5）。

## Canonical Evidence

R5 交付：全部文件 pin @ R5 证据 commit（见 git log 与下表 commit 列）；`sha256` = Git blob 字节（LF）SHA-256，复现 `git cat-file -p <commit>:<path>`，工作树 `Get-FileHash` 一致；`pin_selfcheck.py` **逐行读取登记 commit 复核**（F08I2-001）+ stage-index blob + 干净 checkout 四方校验，结果见 `logs/pin-verify.log`。仅 `pin-verify.log` 以 SHA-256 pin（commit 列 `-`；自校验脚本自身输出，自引用无收敛解，理由见 gates.log 说明）；其余 69 文件均有 commit pin。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-F08-01 | AC-3/AC-4 | verification/FEA-08/fixtures/anim.gif | f015108ad | 7dd78b8dcefe5b5adc3bea15b25c9b76e1df59ebf97c5471bf8c4214553ab2fd | SOURCE_PIN |
| EV-F08-02 | AC-3/AC-4 | verification/FEA-08/fixtures/book_asym_left.zip | f015108ad | 75884802f4956f38528f184018481e783b5704d7c1bd858e09c4c0a371a47d6e | SOURCE_PIN |
| EV-F08-03 | AC-3/AC-4 | verification/FEA-08/fixtures/book_asym_right.zip | f015108ad | 910af583119c76b2994c97d8fde8df34be7c2b0be9f8eaed4ef65e9b67ebb5e8 | SOURCE_PIN |
| EV-F08-04 | AC-3/AC-4 | verification/FEA-08/fixtures/book_dup.zip | f015108ad | 910af583119c76b2994c97d8fde8df34be7c2b0be9f8eaed4ef65e9b67ebb5e8 | SOURCE_PIN |
| EV-F08-05 | AC-3/AC-4 | verification/FEA-08/fixtures/book_dup_copy.zip | f015108ad | bfc7b351471da8c3bd2fd3639a0a23407dfdf2cbf161d23cae57bed4d16ebc05 | SOURCE_PIN |
| EV-F08-06 | AC-3/AC-4 | verification/FEA-08/fixtures/book_dupanchor_left.zip | f015108ad | 293ecd0bf7503ae5ec7573c43a5b0cf603fe8d102a6f28408721e9dfbdd7258d | SOURCE_PIN |
| EV-F08-07 | AC-3/AC-4 | verification/FEA-08/fixtures/book_dupanchor_right.zip | f015108ad | ba0d39970de787f449e9fc57132129118d73e26134791f21838e8691542fae49 | SOURCE_PIN |
| EV-F08-08 | AC-3/AC-4 | verification/FEA-08/fixtures/book_dupcontent_a.zip | f015108ad | 90e79c90caa454567f33a5f188d8f379ed244c51e87d54b59d4c44b4bcfeb626 | SOURCE_PIN |
| EV-F08-09 | AC-3/AC-4 | verification/FEA-08/fixtures/book_dupcontent_b.zip | f015108ad | 7a7f099cf6634cc9175adca6cba56155c3369c6a104170bc7abb841a55631dd7 | SOURCE_PIN |
| EV-F08-10 | AC-3/AC-4 | verification/FEA-08/fixtures/book_enc_aes.zip | f015108ad | a11cc8a33ef4867bda88abd74957357d920902e0673a365670b6e8710009db6b | SOURCE_PIN |
| EV-F08-11 | AC-3/AC-4 | verification/FEA-08/fixtures/book_enc_zipcrypto.zip | f015108ad | 94753e8e50d4225f4a7970a6d321d1e9744bcd70dc37e851f4c2fc3d72bf7656 | SOURCE_PIN |
| EV-F08-12 | AC-3/AC-4 | verification/FEA-08/fixtures/book_enc_zipcrypto_copy.zip | f015108ad | 15adce99eb20efe7470350b4aa472208ea74456ef3b6b327cbce135ecbe43f92 | SOURCE_PIN |
| EV-F08-13 | AC-3/AC-4 | verification/FEA-08/fixtures/book_renamed_left.zip | f015108ad | 75884802f4956f38528f184018481e783b5704d7c1bd858e09c4c0a371a47d6e | SOURCE_PIN |
| EV-F08-14 | AC-3/AC-4 | verification/FEA-08/fixtures/book_renamed_right.zip | f015108ad | edd0bc5167046db379c69ebb512c6a318355cc9757c64fe50052d5f95d24323e | SOURCE_PIN |
| EV-F08-15 | AC-3/AC-4 | verification/FEA-08/fixtures/book_v1.cbz | f015108ad | bf11f920e6203c14a80745eedc6e2f653f34be004b48bb0d6dd54150f094aeee | SOURCE_PIN |
| EV-F08-16 | AC-3/AC-4 | verification/FEA-08/fixtures/book_v1.zip | f015108ad | bf11f920e6203c14a80745eedc6e2f653f34be004b48bb0d6dd54150f094aeee | SOURCE_PIN |
| EV-F08-17 | AC-3/AC-4 | verification/FEA-08/fixtures/book_v1_recompressed.zip | f015108ad | e241737b6b0b34f8d079d7fcc0ea16777148125c04f644cd589d46e2b30b7268 | SOURCE_PIN |
| EV-F08-18 | AC-3/AC-4 | verification/FEA-08/fixtures/doc_enc.pdf | f015108ad | 89adee6fa0a99e98bd46352563d9b3b661f9db29c372aed8431cf32206fab6f5 | SOURCE_PIN |
| EV-F08-19 | AC-3/AC-4 | verification/FEA-08/fixtures/doc_enc_copy.pdf | f015108ad | df4dcac585b419742844080bae139d86419d591caa47fa2e226215b99d446b49 | SOURCE_PIN |
| EV-F08-20 | AC-3/AC-4 | verification/FEA-08/fixtures/doc_v1.pdf | f015108ad | e6e77604a955224e15f3b2840c2d47106ba5e88fb794a5b484c1629d9ab9d6c3 | SOURCE_PIN |
| EV-F08-21 | AC-3/AC-4 | verification/FEA-08/fixtures/doc_v1_regen.pdf | f015108ad | 07bce0293aafdfe4c3da496613b9652de48e38867694a2a74d77fcd0c2563c21 | SOURCE_PIN |
| EV-F08-22 | AC-3/AC-4 | verification/FEA-08/fixtures/evidence_manifest.json | f015108ad | 7e3fb8b573e0748785f4a0ecc93ce5d5ae4543fe55dbdd8bf59590dcc0001346 | SOURCE_PIN |
| EV-F08-23 | AC-3/AC-4 | verification/FEA-08/fixtures/firstframe_extract.png | f015108ad | f411173051663150ef31d5b3d86a9f5ddb9177d9c5cd5ff2b44c35d3b436ae0f | SOURCE_PIN |
| EV-F08-24 | AC-3/AC-4 | verification/FEA-08/fixtures/folder_v1/p1.png | f015108ad | 869e410694cd5f808803c2af5f2d6ce95dd651c76e5e44e1baafe66dbffc38fa | SOURCE_PIN |
| EV-F08-25 | AC-3/AC-4 | verification/FEA-08/fixtures/folder_v1/p2.png | f015108ad | da0ad99a91ffff15d6fefcb417c9c1adf1a4160a15718cd16ba4bddc202164f1 | SOURCE_PIN |
| EV-F08-26 | AC-3/AC-4 | verification/FEA-08/fixtures/folder_v1/p3.png | f015108ad | 796c1b31e4463efed47d54f9bff124d20a17f1a2aafca7259ca5bd90b4449678 | SOURCE_PIN |
| EV-F08-27 | AC-3/AC-4 | verification/FEA-08/fixtures/folder_v2/p1.png | f015108ad | 869e410694cd5f808803c2af5f2d6ce95dd651c76e5e44e1baafe66dbffc38fa | SOURCE_PIN |
| EV-F08-28 | AC-3/AC-4 | verification/FEA-08/fixtures/folder_v2/p2renamed.png | f015108ad | da0ad99a91ffff15d6fefcb417c9c1adf1a4160a15718cd16ba4bddc202164f1 | SOURCE_PIN |
| EV-F08-29 | AC-3/AC-4 | verification/FEA-08/fixtures/folder_v2/p4.png | f015108ad | 869e410694cd5f808803c2af5f2d6ce95dd651c76e5e44e1baafe66dbffc38fa | SOURCE_PIN |
| EV-F08-30 | AC-3/AC-4 | verification/FEA-08/fixtures/img_base.png | f015108ad | 869e410694cd5f808803c2af5f2d6ce95dd651c76e5e44e1baafe66dbffc38fa | SOURCE_PIN |
| EV-F08-31 | AC-3/AC-4 | verification/FEA-08/fixtures/img_cmyk.jpg | f015108ad | 0d17f9bd7b8e51ed51c237410a77255c31120b7902e50f875da62a926d01199b | SOURCE_PIN |
| EV-F08-32 | AC-3/AC-4 | verification/FEA-08/fixtures/img_copy.png | f015108ad | 869e410694cd5f808803c2af5f2d6ce95dd651c76e5e44e1baafe66dbffc38fa | SOURCE_PIN |
| EV-F08-33 | AC-3/AC-4 | verification/FEA-08/fixtures/img_dhash_dist10.png | f015108ad | 5ba3df93071ee7a2710e63757fa9d3194a418aca493410530db385928a0c565c | SOURCE_PIN |
| EV-F08-34 | AC-3/AC-4 | verification/FEA-08/fixtures/img_dhash_dist11.png | f015108ad | 68b2ce3459521c379291f7e58cd58a74407788ff0a41d0d72a5cb9ede679e4c4 | SOURCE_PIN |
| EV-F08-35 | AC-3/AC-4 | verification/FEA-08/fixtures/img_dhash_ref.png | f015108ad | 6d791ee79e1ab53fbdf02aa40e09aa47e55ada861e4062a36c9216282651d03a | SOURCE_PIN |
| EV-F08-36 | AC-3/AC-4 | verification/FEA-08/fixtures/img_dims_a.png | f015108ad | 4b6c236c544ccc21e68b653d03a8cc51b8f4cafa07857c8ca713ec1f2492a0c2 | SOURCE_PIN |
| EV-F08-37 | AC-3/AC-4 | verification/FEA-08/fixtures/img_dims_b.png | f015108ad | 13180946b6a81a2009889ac3946ae26c234e85c8df6d4fece86e5cdbe0227342 | SOURCE_PIN |
| EV-F08-38 | AC-3/AC-4 | verification/FEA-08/fixtures/img_exif_o6.png | f015108ad | b125c108b081fd0d59c19090a182ed7507f9a739f5079494f2b9e69460e71bff | SOURCE_PIN |
| EV-F08-39 | AC-3/AC-4 | verification/FEA-08/fixtures/img_flipped.png | f015108ad | 8c4b9bff2fabe004bbfe159926afdc39bb6d3d5dc351caeb1903900a1dc435c8 | SOURCE_PIN |
| EV-F08-40 | AC-3/AC-4 | verification/FEA-08/fixtures/img_gray.png | f015108ad | 34f0b239609575302cc2f1b2e4a57e26ea69d1b27cb984dc0877a7f43f292c2c | SOURCE_PIN |
| EV-F08-41 | AC-3/AC-4 | verification/FEA-08/fixtures/img_gray_as_rgb.png | f015108ad | d4723bb228449cd6203c21b665f31ff8c5726aa42ff5644afa1c226a6a67e744 | SOURCE_PIN |
| EV-F08-42 | AC-3/AC-4 | verification/FEA-08/fixtures/img_reenc.jpg | f015108ad | 863d49deb2906fac893953e35150b1600bc0cc645baf0d29d4d372037b87012c | SOURCE_PIN |
| EV-F08-43 | AC-3/AC-4 | verification/FEA-08/fixtures/img_rotated_phys.png | f015108ad | 3937a0debc3c1bc12f39246ce56257e7b7e2ea446ac0559dce0cf9a33bddd095 | SOURCE_PIN |
| EV-F08-44 | AC-3/AC-4 | verification/FEA-08/fixtures/wrongframe_blue.png | f015108ad | b9c21277c74c0f24dbd06c770443b182de40c8a439993e01b08ee84e7ce04b4e | SOURCE_PIN |
| EV-F08-45 | AC-1..4 | verification/FEA-08/logs/gates-raw/01-build.log | f015108ad | a096efc7be165145da4d9e798e864545ed28635d115944cac6d3228e200f831e | CANONICAL |
| EV-F08-46 | AC-1..4 | verification/FEA-08/logs/gates-raw/02-test.log | f015108ad | 118d468c8613bcaa5843a1dd55c911adfa3e12ed0a3173cac8d1f5342e28f413 | CANONICAL |
| EV-F08-47 | AC-1..4 | verification/FEA-08/logs/gates-raw/03-check.log | f015108ad | bbc479b3e4057ff40b4e306a8bd7638604b3de7c91230f298a826846da7df405 | CANONICAL |
| EV-F08-48 | AC-1..4 | verification/FEA-08/logs/gates-raw/04-freeze-pins.log | f015108ad | f92880d1b3e9547bb82344b10e47992639304bd1d95aa3d5930c5004abfc4a71 | CANONICAL |
| EV-F08-49 | AC-1..4 | verification/FEA-08/logs/gates-raw/05-fea06-png.log | f015108ad | ca4067ccecd0482e3574464079a682baf8d12b7abd4e39ebb318ebce4330e94e | CANONICAL |
| EV-F08-50 | AC-1..4 | verification/FEA-08/logs/gates-raw/06-forbidden-diff.log | f015108ad | be11bbcdec00008669899d5237420a3521b7a0db6a990d40920657d28335e8ed | CANONICAL |
| EV-F08-51 | AC-1..4 | verification/FEA-08/logs/gates-raw/07-clearing-api-search.log | f015108ad | 06b79584bdbad3874283828e9ec32ee6c02ad1bd7ba7422ebbda52b30bed39be | CANONICAL |
| EV-F08-52 | AC-1..4 | verification/FEA-08/logs/gates-raw/gates-raw-manifest.json | f015108ad | 322ab2eb2868f7a0c62c8964f103c2e61a73ba9e6ff052deac3664ac2a4c5396 | CANONICAL |
| EV-F08-53 | AC-1..4 | verification/FEA-08/logs/gates-raw/phase1-values.json | f015108ad | 66fc80a312a6de97c404a157c065f9b75f7736169623be080a1f00095812da84 | CANONICAL |
| EV-F08-54 | AC-1..4 | verification/FEA-08/logs/gates.log | f015108ad | aa72dbc9b6863b1b58c995a5055f89eef2e5657fb940ebe8c59047a3ed2e162a | CANONICAL |
| EV-F08-55 | AC-1 | verification/FEA-08/logs/h4_run.log | f015108ad | 4a2e8d7af50220cfc7025f348e61b28f7334dd7444f7737d2018c5abe9c72b7c | CANONICAL |
| EV-F08-56 | AC-2 | verification/FEA-08/logs/h5_run.log | f015108ad | 5589b33da77857243def405918ac8fa370904e719653a47e36869a17319aa5fd | CANONICAL |
| EV-F08-57 | AC-3 | verification/FEA-08/logs/h6_run.log | f015108ad | 1707f3db7021d59dd9dafc739927e2e2bd51f7f4a260d1e239d52993950dffc6 | CANONICAL |
| EV-F08-58 | AC-1..4 | verification/FEA-08/logs/make_fixtures.log | f015108ad | de9113023032d42429261130473b20200f871447c9c329606ba43214edaeda4d | CANONICAL |
| EV-F08-59 | AC-1..4 | verification/FEA-08/logs/make_fixtures_regeneration.log | f015108ad | de9113023032d42429261130473b20200f871447c9c329606ba43214edaeda4d | CANONICAL |
| EV-F08-60 | AC-4 | verification/FEA-08/logs/matrix.log | f015108ad | 98ee99d44af2425c0f7da00a5aa908adbb0aef2d1305d408e4421a4009385817 | CANONICAL |
| EV-F08-61 | AC-1..4 | verification/FEA-08/logs/run_all.log | f015108ad | 44c5be84e9035243bb34f42a93906c4853dd5f7f92b434048eb06bad586d63fc | CANONICAL |
| EV-F08-62 | AC-1..4 | verification/FEA-08/logs/stage_evidence.log | f015108ad | 1f6fdcae7e7e371e373382d7f26b22477bb49a726f6bc2ec2e82954e71866744 | CANONICAL |
| EV-F08-63 | AC-1..4 | verification/FEA-08/logs/test-skip-inventory.md | f015108ad | 1cbd2c13ed612ae05f51af937ee3eee38e22e79c13c2a21065c6c89244ad9403 | CANONICAL |
| EV-F08-64 | AC-3/AC-4 | verification/FEA-08/prototype_hashes.txt | f015108ad | 55f0068175e08a5181e401ebc00da7c6f9421a69891e25622570ec6949f5c274 | CANONICAL |
| EV-F08-65 | AC-4 | verification/FEA-08/results/capability_matrix.json | f015108ad | 0fdca8deaa9e43455276b15d4aecba3b7521a473d7de543158f6b8730ab9e1ac | CANONICAL |
| EV-F08-66 | AC-4 | verification/FEA-08/results/capability_matrix.md | f015108ad | b0061009e4bb3f0851cde642e2efb98944b9659a939203d0b1b3a91aa4688997 | CANONICAL |
| EV-F08-67 | AC-3 | verification/FEA-08/results/fixtures_manifest.json | f015108ad | 28c81ad98ef0296d01a99920190ae8762f0c7f798a890cd118f4cee32c52dcca | CANONICAL |
| EV-F08-68 | AC-1 | verification/FEA-08/results/h4_results.json | f015108ad | b3fa0ec95d38b6f15fe795a14846a7b65a7ed22fce89688108a394265d8f3ad0 | CANONICAL |
| EV-F08-69 | AC-2 | verification/FEA-08/results/h5_results.json | f015108ad | d2abd890b36ac4f471cdc5661ee0c67a50880f02926a5d45c4eadee403d06bd6 | CANONICAL |
| EV-F08-70 | AC-3 | verification/FEA-08/results/h6_results.json | f015108ad | 2660b2351bfca22f64dd88082be61dc8be7e94a47c6b2e1fd741781fabeab7a0 | CANONICAL |
| EV-F08-71 | AC-1..4 | verification/FEA-08/results/run_all_log.json | f015108ad | 276008896b0c7539b7158d4a1d7ceabea177acedbb1cd6ba7880d47e2d9cc0c3 | CANONICAL |
| EV-F08-72 | AC-1..4 | verification/FEA-08/logs/pin-verify.log | - | 9efd0187f26413a0ae710f374d55054dc977171eddd5113c7cf0fd88a3c391df | CANONICAL |

## 门禁记录（R5 交付，2026-11-03；原始输出 `logs/gates-raw/**`（7 份，含 command/EXIT/cwd/shell/elapsed），摘要 `logs/gates.log`）

| 门禁 | 命令 | head | EXIT | 结果 |
|---|---|---|---|---|
| build | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | `8609c6591` + R5 工作树 | 0 | 0 warning / 0 error（`gates-raw/01-build.log`） |
| 无过滤全量 | `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --nologo` | 同上 | 0 | **1292 passed / 0 failed / 57 skipped**（逐程序集 21/38/51/253/117/31/128/653；skip 0/0/28/0/0/0/22/7；本轮一次通过，原始输出 `gates-raw/02-test.log`） |
| 治理检查 | `pwsh -NoProfile -File tools\governance\check.ps1` | 同上 | 0 | PASS(3 warnings)，elapsed 1.2s（`gates-raw/03-check.log` 含命令/EXIT/cwd/shell/elapsed/env） |
| 冻结 pin | `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | 同上 | 0 | 15/15 PASS（`gates-raw/04-freeze-pins.log`） |
| 旧 FEA-06 四 PNG | `Get-FileHash verification\FEA-06\screens\*.png -Algorithm SHA256` | 同上 | 0 | reader `8533c263…`/settings `fd30b166…`/shelf `307f8f67…`/workbench `d5d878bb…`（与 FEA-06 卡一致，未变；`gates-raw/05-fea06-png.log`） |
| 禁止范围 diff | `git diff --name-only 2870a9fa5..HEAD -- src apps experiments tests packaging scripts tools`；+ `git status --porcelain` 同范围 | 同上 | 0 | 空（**src_changes=0**；R5 无生产代码改动；`gates-raw/06-forbidden-diff.log`） |
| 安全边界 | `git grep -n -E "SHEmptyRecycleBin|EmptyRecycleBin|SHERB_" -- src apps experiments tests packaging scripts tools` | 同上 | 0 | NO_MATCHES（代码路径调用=0；`gates-raw/07-clearing-api-search.log`） |
| 57 skip 来源 | `python ...\prototype\gates_capture.py --phase1` | 同上 | 0 | `logs/test-skip-inventory.md` **57/57** 逐项（测试标识、源文件:行、属性、原因） |
| Canonical Evidence pin | `python ...\prototype\pin_selfcheck.py`（`git add` 后） | 同上 | 0 | **71/71 文件**四方一致（登记 commit blob / 工作树 / index blob / 干净 checkout）+ `pin-verify.log` 自身 SHA-256 pin（共 72 项；`logs/pin-verify.log`） |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| prototype（非 Git） | `G:\CODEX\New Manga.workspace\FEA-08\prototype\` | PRESERVE_REFERENCED | 原地（workspace） | `verification/FEA-08/prototype_hashes.txt`（16 脚本 SHA-256） | 复现证据生成所需；被 Task/Handoff/EV 引用 |
| temp（合成） | `G:\CODEX\New Manga.workspace\FEA-08\tmp\` | DELETE_SAFE | 已删除 | `results/run_all_log.json`（tmp_removed/tmp_remaining=[]） | run_all 末尾实际清理（含失败路径 finally）；tmp 当前为空 |
| artifact（生成侧） | `G:\CODEX\New Manga.workspace\FEA-08\out\` | DELETE_SAFE | 原地保留（可再生） | 无 pin（入库副本见 verification/FEA-08） | 由 run_all 再生；不作为证据源；失败时 `run_all_failure.json` 只留 workspace |
| agent-output | workspace `FEA-08\{r2-*,r3-*,impl-*,scope-*}.log/prompt` | PRESERVE_REFERENCED | 原地（workspace） | 无 | 派发/原始日志，非 Canonical |
| 回收站合成条目 | G: `$RECYCLE.BIN`（lab 前缀） | DELETE_SAFE | 已还原并删除 | `results/h5_results.json` restore_log | 5 条还原后删除；G: 0→0、leftover=0；C: 用户条目 2 条未触碰 |
| evidence（仓库） | `verification/FEA-08/**` | NOT_APPLICABLE | 仓库内 | EV 表（72 项） | Canonical Evidence |
| 门禁原始日志（仓库） | `verification/FEA-08/logs/gates-raw/**` | NOT_APPLICABLE | 仓库内 | EV 表 + `gates-raw-manifest.json` | 版本化原始输出（命令/EXIT/shell/解释器）供审计（F08I2-007） |

## 待 scope-r2 确认

1. 隔离测试 SQLite：**否**（已写入 BLOCKED）。
2. USB/SMB 无硬件：接受 mock/LIMITED(mocked)（已写入 AC-4）。
3. H6 加密格式 fixture：预生成+SHA 或最小依赖（pyzipper MIT）二选一（已写入 AC-4）。

## Closeout Record

- Closeout date / DSH：待 impl-r3 Review 通过 + 集成验证后填写。
- canonical_evidence_status：`complete`（72 项；71 文件四方 pin + `pin-verify.log` 自身 SHA；impl-r2/r3/r4 findings 已处置）。
- resource_closeout_status：`pending`（关闭时按上表逐项复核）。
- 删除、迁移、归档数量/字节数：待关闭时填写（预计：tmp 删除、回收站条目 0 残留；无迁移）。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：STATUS / Plan / Task 导航 / rolling checkpoint 待关闭时更新。
