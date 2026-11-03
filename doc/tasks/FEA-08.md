---
id: FEA-08
title: Source/回收站隔离原型（H4/H5/H6 能力矩阵与技术报告）
kind: prototype
governance_version: 3
status: in_review
approval: scope-r2 **approved**（ZCode CLI fresh session，P0=0/P1=0/P2=2；2026-11-03；报告 doc/reviews/FEA-08-scope-r2.md）
suggested_owner: zcode
owner: zcode
reviewer: scope-r2 approved（ZCode）；impl-r1 **changes_requested**（D-9 独立子 agent，P0=0/P1=2/P2=9）；impl-r2 **changes_requested**（Codex 独立会话，P0=0/P1=3/P2=4，报告 doc/reviews/FEA-08-impl-r2.md）；impl-r3 **changes_requested**（Codex 独立会话，P0=0/P1=0/P2=5，报告 doc/reviews/FEA-08-impl-r3.md）；impl-r4 **changes_requested**（Codex 独立会话，P0=0/P1=0/P2=5，报告 doc/reviews/FEA-08-impl-r4.md）；impl-r5 **changes_requested**（Codex 独立会话，P0=0/P1=0/P2=4，报告 doc/reviews/FEA-08-impl-r5.md）；impl-r6 Reviewer 待 DSH Appointment（Codex 新独立上下文；R6 finding 全部处置）
depends_on:
  - FEA-01-FREEZE-1
base_commit: 2870a9fa52b73fdf344cc723e59957d76d60e395（scope-r2 approved head；范围冻结）
branch: main
worktree: G:\CODEX\New Manga
integration_commit: null
delivery_head: 2a9e0f882（R6 证据 commit；Canonical Evidence 72 项逐项 pin @该 commit）
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
> R6 返修（2026-11-03）：impl-r5 changes_requested（P0=0/P1=0/P2=4，Codex）处置完成——矩阵补 R6b restored 列表、计数校验拒绝 JSON boolean、backup 移出 OUT 并在失败时保留报告、门禁采集器失败感知汇总（失败即非零退出且结论为 FAIL）；交付说明见 `doc/handoffs/FEA-08-impl-r6.md`。


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
  - R2 收口：R2/R9 回收站条目有界轮询（`entries_poll`）；`h5_run.py` 期望 PASS 场景 FAIL 时非零退出；`run_all.py` 二次校验 results verdict；R6b destructive 计数 5→5（`no_destructive_reissued=true`）；R5b 类型/属性实测（`current_type=directory`）；R3 "不可回收→保留不 fallback rmdir" 分支经 mock 失败注入（ret=0x79）走通并标 LIMITED(mocked)（F08I1-005/006）。\n  - R4 收口（F08I3-001）：`matrix.derive_ntfs` 与 `run_all.verify_results` 增加 **H5 语义门禁**——不只信 verdict：R1/R6b `restored_digest_matches=true` 且 restored 列表全真；矩阵与总驱动**共享同一组** H5 必需事实：R1/R6b 还原 digest 与 restored 列表、R2 成员 digest/restored_count、R3 不可回收分支 `fallback_rmdir_used=false`（不得 fallback 永久 rmdir）、R4 保留+digest 不变、R5/R5b 拒绝且零 destructive、R6a 不重发、**R6b 三个 destructive 计数必须存在且为整数、执行后==恢复后**（缺失 `None` 不再通过）、R9 逐文件还原 digest、R1/R2/R9 entries_poll 合法且未超时。R5 收口（F08I4-001）：矩阵此前只验子集，已补齐全部字段且与 `run_all.verify_results` 逐字段一致。R6 收口（F08I5-001/003）：矩阵补 R6b `restored` 列表逐项断言；计数校验拒绝 JSON boolean（Python `bool` 是 `int` 子类，`isinstance(True,int)` 不得通过）。
- [x] **AC-3（H6）**：按 :457/:469 二分"精确匹配/候选"并附判定所用 digest 类型（图片强 digest；文件夹成员身份+digest；容器成员内容 digest/规范解码像素 digest、尺寸、方向、唯一性；重复成员名保持独立 occurrence；感知 hash/OCR 仅候选；GIF 仅首帧；PDF 记录页码与渲染参数）；golden fixtures 与结果报告。 <<MET>>
  - R3 收口：**19 场景 measured**；`folder_v1/v2` 六个成员入库（EV 逐文件 pin），H6 直接对入库 fixtures 运行（`fixtures_root` 记录）；**规范像素 digest 绑定尺寸**（`sha256("WxH\0"+RGB)`，F08I2-002；M19 为 2×6 vs 3×4 同像素字节反例 → 仅 `candidate`，`exact_blocked_by_size_mismatch=true`）；**容器 exact 要求成员身份唯一一对一定位**（重复同图但成员名不同 → `needs_confirmation`，M20；F08I2-003）；M12/M13/M15 独立副本/独立密文两路径比较（自读对照标 self-consistency）；dhash 阈值邻界 M17（10→candidate）/M18（11→no_match）；AES ZIP 如实标 LIMITED(pyzipper)；`fixtures_manifest` 指针指向实际存在的 `results/fixtures_manifest.json`（F08I1-001/007/011）。\n  - R4 收口（F08I3-004）：容器唯一映射判据升级——**按 occurrence 构建“内容 → 成员名多重集”映射**：唯一内容可跨名唯一对应（M21 唯二内容改名/换位 → exact）；重复内容需相同 name/ordinal 锚（M22 → exact）；锚不一致才 needs_confirmation（M20）；重复名不同内容仍 candidate（M12）。R5 收口（F08I4-003）：重复成员名在**两侧**独立核验——任一侧存在重复名即 candidate，新增 M23 非对称反例并断言左右互换均为 candidate。共 **22 场景 measured**（M21/M22 正例 + M23 非对称反例）。
- [x] **AC-4（交付完整）**：能力矩阵为二维结构 = 卷类型（NTFS 本地/USB/SMB/…）× 输入类别（单图/文件夹/ZIP/CBZ/PDF）逐项"现状/需新增"结论；每项标注证据来源 **measured/mocked/inferred**，**mock/推断不得记 PASS（上限 LIMITED(mocked)）**；技术报告含依赖/许可（如加密 ZIP/PDF fixture 需最小新依赖，二选一：登记许可+不进生产闭包，或预生成 fixture+SHA-256）；无生产代码改动。 <<MET>>
  - R3 收口：矩阵逐格含 `current`/`needed`，且**每个卷分支显式赋值 H4/H5/H6 各自 evidence**（非 NTFS 卷不再继承上一轮 NTFS 的 measured，F08I2-004）；NTFS 行状态由 h4/h5/h6 结果**及语义断言**推导（strict 拦截断言、GIF 蓝帧反证、尺寸绑定、容器唯一映射、回收分支计数；任一项被破坏即降级，不写 PASS——F08I2-005），H4/H5 未逐格式实测的格标 `LIMITED(inferred: volume-level, format-agnostic)`，ZIP 的 AES 分支标 `LIMITED(pyzipper)`；mock/inferred 无 PASS；**R4 收口（F08I3-002/003/005）**：`run_all` 晋升改为事务化（新内容先写临时文件、旧文件登记 journal 后才移动；任一步失败逐项恢复并核对；全部晋升成功后才提交 journal/发布成功日志，失败不冒充 EXIT=0），空输出/耗时/环境写入门禁原始日志；**R5 收口（F08I4-002/004/005）**：晋升前先对旧 Canonical 集做 hash 树/文件快照，失败恢复后必须**完整核对旧集 hash** 才报 `rolled_back=true`（未恢复 backup 明确列出）；门禁原始日志重采集与摘要口径修正（7 份 raw，command/EXIT/cwd/shell/elapsed 齐全）；`gates_capture.py` 实际 SHA 已与 `prototype_hashes.txt` 一致；**R6 收口（F08I5-002/004）**：晋升 backup 目录移出 `out/`（避免下次启动清空），失败时保留并报告 `backup_dir_kept`；门禁采集器按实际结果汇总（任一 build/test/pins/PNG/禁止 diff/安全项失败即非零退出、结论为 FAIL，不再无条件“全部通过”）；Canonical Evidence **72 项**（69 文件逐行 commit-blob/worktree/index-blob/干净 checkout 四方校验 + `pin-verify.log` 自身 SHA-256 pin），门禁原始日志与 57 项 skip 来源入库（F08I1-002/008/009、F08I2-004/005/007、F08I3-002/003/005）。

## 交付与证据

- 原型/脚本：`G:\CODEX\New Manga.workspace\FEA-08\prototype\`（非 Git；16 个登记脚本 SHA-256 见 `verification/FEA-08/prototype_hashes.txt`）。
- 报告：`doc/research/FEA-08-source-capability.md`（R4 收口版）。
- 证据：`verification/FEA-08/**`（fixtures 目录 **44 文件 = 43 内容文件 + `evidence_manifest.json`**；results 7 件；logs 8 件 + `gates.log` + `test-skip-inventory.md`（57 项逐项来源）+ `gates-raw/` 原始输出（build/test/pins/四 PNG/禁止 diff/安全搜索/check + manifest + phase1 values）+ `pin-verify.log`；`prototype_hashes.txt`；共 **72 文件**，EV 表逐文件登记）。
- 复现：`python ...\prototype\run_all.py`（双生成 fixtures → 原子 staging → stage_evidence → H4/H5/H6(直接对入库 fixtures，含 M8M9/M19/M20)/矩阵 → results 双层校验 → 结果/日志原子晋升 → tmp 清理；失败回滚旧 Canonical 集）；`python ...\prototype\h6_run.py --fixtures ...\verification\FEA-08\fixtures`（H6 独立复跑）；`python ...\prototype\gates_capture.py --phase1/--phase2`（门禁原始日志 + 57 项 skip 清单）；`python ...\prototype\pin_selfcheck.py`（`git add` 后四方 pin 自校验）。
- Handoff：`doc/handoffs/FEA-08-impl.md`（impl-r1）、`...-impl-r2.md`（R2）、`...-impl-r3.md`（R3）、`...-impl-r4.md`（R4）、`...-impl-r5.md`（R5）、`...-impl-r6.md`（R6）。

## Canonical Evidence

R6 交付：全部文件 pin @ R6 证据 commit（见 git log 与下表 commit 列）；`sha256` = Git blob 字节（LF）SHA-256，复现 `git cat-file -p <commit>:<path>`，工作树 `Get-FileHash` 一致；`pin_selfcheck.py` **逐行读取登记 commit 复核**（F08I2-001）+ stage-index blob + 干净 checkout 四方校验，结果见 `logs/pin-verify.log`。仅 `pin-verify.log` 以 SHA-256 pin（commit 列 `-`；自校验脚本自身输出，自引用无收敛解，理由见 gates.log 说明）；其余 69 文件均有 commit pin。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-F08-01 | AC-3/AC-4 | verification/FEA-08/fixtures/anim.gif | 2a9e0f882 | 7dd78b8dcefe5b5adc3bea15b25c9b76e1df59ebf97c5471bf8c4214553ab2fd | SOURCE_PIN |
| EV-F08-02 | AC-3/AC-4 | verification/FEA-08/fixtures/book_asym_left.zip | 2a9e0f882 | 85a050227446fb2655ab8dc21599b95acd5bbc7922d4f6bf812a3f2a460c6c96 | SOURCE_PIN |
| EV-F08-03 | AC-3/AC-4 | verification/FEA-08/fixtures/book_asym_right.zip | 2a9e0f882 | 58a25933aecd28d7228384c5f2a518ebf0cc9fd048f9c26d249ad8d2efacbc74 | SOURCE_PIN |
| EV-F08-04 | AC-3/AC-4 | verification/FEA-08/fixtures/book_dup.zip | 2a9e0f882 | 58a25933aecd28d7228384c5f2a518ebf0cc9fd048f9c26d249ad8d2efacbc74 | SOURCE_PIN |
| EV-F08-05 | AC-3/AC-4 | verification/FEA-08/fixtures/book_dup_copy.zip | 2a9e0f882 | bfc7b351471da8c3bd2fd3639a0a23407dfdf2cbf161d23cae57bed4d16ebc05 | SOURCE_PIN |
| EV-F08-06 | AC-3/AC-4 | verification/FEA-08/fixtures/book_dupanchor_left.zip | 2a9e0f882 | 0a7aadf6d4212acc706cfc5281270beb8b6352d9e12e7a9e2d827219f66bffd5 | SOURCE_PIN |
| EV-F08-07 | AC-3/AC-4 | verification/FEA-08/fixtures/book_dupanchor_right.zip | 2a9e0f882 | b9b4314df56f66187de5bab58bd9fac23ed83bb8ae6ab5adcf04e685f48e2290 | SOURCE_PIN |
| EV-F08-08 | AC-3/AC-4 | verification/FEA-08/fixtures/book_dupcontent_a.zip | 2a9e0f882 | e3accd905431bd7ae4ec5cd4e0dd600ca42a69d5a7b725e8033caaac58499634 | SOURCE_PIN |
| EV-F08-09 | AC-3/AC-4 | verification/FEA-08/fixtures/book_dupcontent_b.zip | 2a9e0f882 | 869deaf3c875c3ff446533409e03141df461e5a6f4c6ed04858fe8219b4be5b7 | SOURCE_PIN |
| EV-F08-10 | AC-3/AC-4 | verification/FEA-08/fixtures/book_enc_aes.zip | 2a9e0f882 | 296173b73c60003878c649df4ef4e528edb583d01b71ccec99bae26f33eb4d4c | SOURCE_PIN |
| EV-F08-11 | AC-3/AC-4 | verification/FEA-08/fixtures/book_enc_zipcrypto.zip | 2a9e0f882 | db575588895d2c07b6c35c829114f9ee5dc615f11fafe394bcb943014c38d39e | SOURCE_PIN |
| EV-F08-12 | AC-3/AC-4 | verification/FEA-08/fixtures/book_enc_zipcrypto_copy.zip | 2a9e0f882 | aadb73c757d4fb962a33fef9f90fbd1d911a5d3e0af53b5e6ecc5c708d793c31 | SOURCE_PIN |
| EV-F08-13 | AC-3/AC-4 | verification/FEA-08/fixtures/book_renamed_left.zip | 2a9e0f882 | 85a050227446fb2655ab8dc21599b95acd5bbc7922d4f6bf812a3f2a460c6c96 | SOURCE_PIN |
| EV-F08-14 | AC-3/AC-4 | verification/FEA-08/fixtures/book_renamed_right.zip | 2a9e0f882 | d734303cc4649c3aa2a5a6d4361dce840ff2c840d3ee165955ad53aae1e96d1d | SOURCE_PIN |
| EV-F08-15 | AC-3/AC-4 | verification/FEA-08/fixtures/book_v1.cbz | 2a9e0f882 | 930202f29e1e4530386136ad9444f8bda85ea716d1f4d48c58dcf1fe400dcbf8 | SOURCE_PIN |
| EV-F08-16 | AC-3/AC-4 | verification/FEA-08/fixtures/book_v1.zip | 2a9e0f882 | 930202f29e1e4530386136ad9444f8bda85ea716d1f4d48c58dcf1fe400dcbf8 | SOURCE_PIN |
| EV-F08-17 | AC-3/AC-4 | verification/FEA-08/fixtures/book_v1_recompressed.zip | 2a9e0f882 | 41f40e715b62da37fb85fc5499f0c1b508addedb7429b4724a7fc478acf247ec | SOURCE_PIN |
| EV-F08-18 | AC-3/AC-4 | verification/FEA-08/fixtures/doc_enc.pdf | 2a9e0f882 | 717935b12e5506033d87810829775c924ee6d1edb7df15620d163d6bd3489c23 | SOURCE_PIN |
| EV-F08-19 | AC-3/AC-4 | verification/FEA-08/fixtures/doc_enc_copy.pdf | 2a9e0f882 | b1354540cc41dc8d96907eece6e170ea9cc943604e41a00b92617b1f28047975 | SOURCE_PIN |
| EV-F08-20 | AC-3/AC-4 | verification/FEA-08/fixtures/doc_v1.pdf | 2a9e0f882 | 81ba7bfdfc962150af1d118d7ffac7b2d7d33ed0c6a0bfbf4c60f9d3c890c7d6 | SOURCE_PIN |
| EV-F08-21 | AC-3/AC-4 | verification/FEA-08/fixtures/doc_v1_regen.pdf | 2a9e0f882 | a4ba9de189e52a0b39348839b0904875e90c79e65c34b9876afd1a187292276c | SOURCE_PIN |
| EV-F08-22 | AC-3/AC-4 | verification/FEA-08/fixtures/evidence_manifest.json | 2a9e0f882 | 7eb3d0ef485f56bc2580cd1a5f58af1b6593be4a8340420488969ecf0c0b2b15 | SOURCE_PIN |
| EV-F08-23 | AC-3/AC-4 | verification/FEA-08/fixtures/firstframe_extract.png | 2a9e0f882 | f411173051663150ef31d5b3d86a9f5ddb9177d9c5cd5ff2b44c35d3b436ae0f | SOURCE_PIN |
| EV-F08-24 | AC-3/AC-4 | verification/FEA-08/fixtures/folder_v1/p1.png | 2a9e0f882 | 869e410694cd5f808803c2af5f2d6ce95dd651c76e5e44e1baafe66dbffc38fa | SOURCE_PIN |
| EV-F08-25 | AC-3/AC-4 | verification/FEA-08/fixtures/folder_v1/p2.png | 2a9e0f882 | da0ad99a91ffff15d6fefcb417c9c1adf1a4160a15718cd16ba4bddc202164f1 | SOURCE_PIN |
| EV-F08-26 | AC-3/AC-4 | verification/FEA-08/fixtures/folder_v1/p3.png | 2a9e0f882 | 796c1b31e4463efed47d54f9bff124d20a17f1a2aafca7259ca5bd90b4449678 | SOURCE_PIN |
| EV-F08-27 | AC-3/AC-4 | verification/FEA-08/fixtures/folder_v2/p1.png | 2a9e0f882 | 869e410694cd5f808803c2af5f2d6ce95dd651c76e5e44e1baafe66dbffc38fa | SOURCE_PIN |
| EV-F08-28 | AC-3/AC-4 | verification/FEA-08/fixtures/folder_v2/p2renamed.png | 2a9e0f882 | da0ad99a91ffff15d6fefcb417c9c1adf1a4160a15718cd16ba4bddc202164f1 | SOURCE_PIN |
| EV-F08-29 | AC-3/AC-4 | verification/FEA-08/fixtures/folder_v2/p4.png | 2a9e0f882 | 869e410694cd5f808803c2af5f2d6ce95dd651c76e5e44e1baafe66dbffc38fa | SOURCE_PIN |
| EV-F08-30 | AC-3/AC-4 | verification/FEA-08/fixtures/img_base.png | 2a9e0f882 | 869e410694cd5f808803c2af5f2d6ce95dd651c76e5e44e1baafe66dbffc38fa | SOURCE_PIN |
| EV-F08-31 | AC-3/AC-4 | verification/FEA-08/fixtures/img_cmyk.jpg | 2a9e0f882 | 0d17f9bd7b8e51ed51c237410a77255c31120b7902e50f875da62a926d01199b | SOURCE_PIN |
| EV-F08-32 | AC-3/AC-4 | verification/FEA-08/fixtures/img_copy.png | 2a9e0f882 | 869e410694cd5f808803c2af5f2d6ce95dd651c76e5e44e1baafe66dbffc38fa | SOURCE_PIN |
| EV-F08-33 | AC-3/AC-4 | verification/FEA-08/fixtures/img_dhash_dist10.png | 2a9e0f882 | 5ba3df93071ee7a2710e63757fa9d3194a418aca493410530db385928a0c565c | SOURCE_PIN |
| EV-F08-34 | AC-3/AC-4 | verification/FEA-08/fixtures/img_dhash_dist11.png | 2a9e0f882 | 68b2ce3459521c379291f7e58cd58a74407788ff0a41d0d72a5cb9ede679e4c4 | SOURCE_PIN |
| EV-F08-35 | AC-3/AC-4 | verification/FEA-08/fixtures/img_dhash_ref.png | 2a9e0f882 | 6d791ee79e1ab53fbdf02aa40e09aa47e55ada861e4062a36c9216282651d03a | SOURCE_PIN |
| EV-F08-36 | AC-3/AC-4 | verification/FEA-08/fixtures/img_dims_a.png | 2a9e0f882 | 4b6c236c544ccc21e68b653d03a8cc51b8f4cafa07857c8ca713ec1f2492a0c2 | SOURCE_PIN |
| EV-F08-37 | AC-3/AC-4 | verification/FEA-08/fixtures/img_dims_b.png | 2a9e0f882 | 13180946b6a81a2009889ac3946ae26c234e85c8df6d4fece86e5cdbe0227342 | SOURCE_PIN |
| EV-F08-38 | AC-3/AC-4 | verification/FEA-08/fixtures/img_exif_o6.png | 2a9e0f882 | b125c108b081fd0d59c19090a182ed7507f9a739f5079494f2b9e69460e71bff | SOURCE_PIN |
| EV-F08-39 | AC-3/AC-4 | verification/FEA-08/fixtures/img_flipped.png | 2a9e0f882 | 8c4b9bff2fabe004bbfe159926afdc39bb6d3d5dc351caeb1903900a1dc435c8 | SOURCE_PIN |
| EV-F08-40 | AC-3/AC-4 | verification/FEA-08/fixtures/img_gray.png | 2a9e0f882 | 34f0b239609575302cc2f1b2e4a57e26ea69d1b27cb984dc0877a7f43f292c2c | SOURCE_PIN |
| EV-F08-41 | AC-3/AC-4 | verification/FEA-08/fixtures/img_gray_as_rgb.png | 2a9e0f882 | d4723bb228449cd6203c21b665f31ff8c5726aa42ff5644afa1c226a6a67e744 | SOURCE_PIN |
| EV-F08-42 | AC-3/AC-4 | verification/FEA-08/fixtures/img_reenc.jpg | 2a9e0f882 | 863d49deb2906fac893953e35150b1600bc0cc645baf0d29d4d372037b87012c | SOURCE_PIN |
| EV-F08-43 | AC-3/AC-4 | verification/FEA-08/fixtures/img_rotated_phys.png | 2a9e0f882 | 3937a0debc3c1bc12f39246ce56257e7b7e2ea446ac0559dce0cf9a33bddd095 | SOURCE_PIN |
| EV-F08-44 | AC-3/AC-4 | verification/FEA-08/fixtures/wrongframe_blue.png | 2a9e0f882 | b9c21277c74c0f24dbd06c770443b182de40c8a439993e01b08ee84e7ce04b4e | SOURCE_PIN |
| EV-F08-45 | AC-1..4 | verification/FEA-08/logs/gates-raw/01-build.log | 2a9e0f882 | 41868b6d19d0b1eeda246ed05c70e7846552f1ea635dd94d5186f54403f0b97e | CANONICAL |
| EV-F08-46 | AC-1..4 | verification/FEA-08/logs/gates-raw/02-test.log | 2a9e0f882 | 2e1db9f3377f54a0c84c6da60b85242c1e1d13c1a3513c9a999acdec99ef6fae | CANONICAL |
| EV-F08-47 | AC-1..4 | verification/FEA-08/logs/gates-raw/03-check.log | 2a9e0f882 | 561089b21ab2272dfa2981449624b6e457649a5c11b50bee1a2abe697452b58e | CANONICAL |
| EV-F08-48 | AC-1..4 | verification/FEA-08/logs/gates-raw/04-freeze-pins.log | 2a9e0f882 | f80f1ec95329b71f91dcd6983fb0afe07714acad3c1f228631758e7a7f79e0f2 | CANONICAL |
| EV-F08-49 | AC-1..4 | verification/FEA-08/logs/gates-raw/05-fea06-png.log | 2a9e0f882 | c548630329b1c9ef25880344f08e33ebf65c206eea9cf90d8e9dc318675a068e | CANONICAL |
| EV-F08-50 | AC-1..4 | verification/FEA-08/logs/gates-raw/06-forbidden-diff.log | 2a9e0f882 | 3a4686cc81c118966eb6df21a546aa101afd7a466509a528defa64341568da69 | CANONICAL |
| EV-F08-51 | AC-1..4 | verification/FEA-08/logs/gates-raw/07-clearing-api-search.log | 2a9e0f882 | 4183caa4ae0c2f4068a91e31b2c169d1131ffa83ea32aec326d93bdca58138ed | CANONICAL |
| EV-F08-52 | AC-1..4 | verification/FEA-08/logs/gates-raw/gates-raw-manifest.json | 2a9e0f882 | b184c87f3c9d50dee01ed64290aae48bf0646a66dcea4eb2e1122a7ccfde63ac | CANONICAL |
| EV-F08-53 | AC-1..4 | verification/FEA-08/logs/gates-raw/phase1-values.json | 2a9e0f882 | 118faa0b56cb8ca8750ff3defe471c196b21063db13a5669b48f5f0cab6a1f86 | CANONICAL |
| EV-F08-54 | AC-1..4 | verification/FEA-08/logs/gates.log | 2a9e0f882 | a480e537665a13e86ebae71b378987953984c5b05f1b387a43f17422b9544825 | CANONICAL |
| EV-F08-55 | AC-1 | verification/FEA-08/logs/h4_run.log | 2a9e0f882 | 4a2e8d7af50220cfc7025f348e61b28f7334dd7444f7737d2018c5abe9c72b7c | CANONICAL |
| EV-F08-56 | AC-2 | verification/FEA-08/logs/h5_run.log | 2a9e0f882 | 5589b33da77857243def405918ac8fa370904e719653a47e36869a17319aa5fd | CANONICAL |
| EV-F08-57 | AC-3 | verification/FEA-08/logs/h6_run.log | 2a9e0f882 | 1707f3db7021d59dd9dafc739927e2e2bd51f7f4a260d1e239d52993950dffc6 | CANONICAL |
| EV-F08-58 | AC-1..4 | verification/FEA-08/logs/make_fixtures.log | 2a9e0f882 | de9113023032d42429261130473b20200f871447c9c329606ba43214edaeda4d | CANONICAL |
| EV-F08-59 | AC-1..4 | verification/FEA-08/logs/make_fixtures_regeneration.log | 2a9e0f882 | de9113023032d42429261130473b20200f871447c9c329606ba43214edaeda4d | CANONICAL |
| EV-F08-60 | AC-4 | verification/FEA-08/logs/matrix.log | 2a9e0f882 | 98ee99d44af2425c0f7da00a5aa908adbb0aef2d1305d408e4421a4009385817 | CANONICAL |
| EV-F08-61 | AC-1..4 | verification/FEA-08/logs/run_all.log | 2a9e0f882 | 1adac129f039009f69148a6a6403caf6eec186c0af449aa54d192af3715a6372 | CANONICAL |
| EV-F08-62 | AC-1..4 | verification/FEA-08/logs/stage_evidence.log | 2a9e0f882 | abead797f8bfdde752df60d2a6c00fec93ad37c38767700f12a6fafe271cf6bc | CANONICAL |
| EV-F08-63 | AC-1..4 | verification/FEA-08/logs/test-skip-inventory.md | 2a9e0f882 | a60853c274ddcce905f2fc7818e1b5ee04bca89247588dd057f4bb0d84e59b4b | CANONICAL |
| EV-F08-64 | AC-3/AC-4 | verification/FEA-08/prototype_hashes.txt | 2a9e0f882 | 421e4c5c945725477fd271e6f3958356c9480e47b755e3dff07bb0469694444b | CANONICAL |
| EV-F08-65 | AC-4 | verification/FEA-08/results/capability_matrix.json | 2a9e0f882 | 0fdca8deaa9e43455276b15d4aecba3b7521a473d7de543158f6b8730ab9e1ac | CANONICAL |
| EV-F08-66 | AC-4 | verification/FEA-08/results/capability_matrix.md | 2a9e0f882 | b0061009e4bb3f0851cde642e2efb98944b9659a939203d0b1b3a91aa4688997 | CANONICAL |
| EV-F08-67 | AC-3 | verification/FEA-08/results/fixtures_manifest.json | 2a9e0f882 | be18d0f4d0d7df3c80c33dca8a2d6f87774dde50b5cd6b2e389601c21db3609b | CANONICAL |
| EV-F08-68 | AC-1 | verification/FEA-08/results/h4_results.json | 2a9e0f882 | 40e5d4bcbbb126dbe8ef75ed52fe5261417b3866b2732b9ab57830eb8b588127 | CANONICAL |
| EV-F08-69 | AC-2 | verification/FEA-08/results/h5_results.json | 2a9e0f882 | 5dede5702c41750b3fd3c94f5b5d175f4c4a318d6ce39fbca42b6d4c83d49053 | CANONICAL |
| EV-F08-70 | AC-3 | verification/FEA-08/results/h6_results.json | 2a9e0f882 | a3827c5c263b19b9864a123c5d956b4f3532e2ab1147e934462e62c7c3806b66 | CANONICAL |
| EV-F08-71 | AC-1..4 | verification/FEA-08/results/run_all_log.json | 2a9e0f882 | 276008896b0c7539b7158d4a1d7ceabea177acedbb1cd6ba7880d47e2d9cc0c3 | CANONICAL |
| EV-F08-72 | AC-1..4 | verification/FEA-08/logs/pin-verify.log | - | 9efd0187f26413a0ae710f374d55054dc977171eddd5113c7cf0fd88a3c391df | CANONICAL |

## 门禁记录（R5 交付，2026-11-03；原始输出 `logs/gates-raw/**`（7 份，含 command/EXIT/cwd/shell/elapsed），摘要 `logs/gates.log`）

| 门禁 | 命令 | head | EXIT | 结果 |
|---|---|---|---|---|
| build | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | `b44d4a748` + R6 工作树 | 0 | 0 warning / 0 error（`gates-raw/01-build.log`） |
| 无过滤全量 | `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --nologo` | 同上 | 0 | **1292 passed / 0 failed / 57 skipped**（逐程序集 21/38/51/253/117/31/128/653；skip 0/0/28/0/0/0/22/7；本轮一次通过，原始输出 `gates-raw/02-test.log`） |
| 治理检查 | `pwsh -NoProfile -File tools\governance\check.ps1` | 同上 | 0 | PASS(3 warnings)，elapsed 1.3s（`gates-raw/03-check.log` 含命令/EXIT/cwd/shell/elapsed/env） |
| 冻结 pin | `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | 同上 | 0 | 15/15 PASS（`gates-raw/04-freeze-pins.log`） |
| 旧 FEA-06 四 PNG | `Get-FileHash verification\FEA-06\screens\*.png -Algorithm SHA256` | 同上 | 0 | reader `8533c263…`/settings `fd30b166…`/shelf `307f8f67…`/workbench `d5d878bb…`（与 FEA-06 卡一致，未变；`gates-raw/05-fea06-png.log`） |
| 禁止范围 diff | `git diff --name-only 2870a9fa5..HEAD -- src apps experiments tests packaging scripts tools`；+ `git status --porcelain` 同范围 | 同上 | 0 | 空（**src_changes=0**；R6 无生产代码改动；`gates-raw/06-forbidden-diff.log`） |
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
