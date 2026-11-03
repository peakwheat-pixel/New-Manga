---
id: FEA-08
title: Source/回收站隔离原型（H4/H5/H6 能力矩阵与技术报告）
kind: prototype
governance_version: 3
status: in_review
approval: scope-r2 **approved**（ZCode CLI fresh session，P0=0/P1=0/P2=2；2026-11-03；报告 doc/reviews/FEA-08-scope-r2.md）
suggested_owner: zcode
owner: zcode
reviewer: scope-r2 approved（ZCode）；impl-r1 **changes_requested**（D-9 独立子 agent，P0=0/P1=2/P2=9，报告 doc/reviews/FEA-08-impl-r1.md）；impl-r2 Reviewer 待 DSH Appointment（Codex）
depends_on:
  - FEA-01-FREEZE-1
base_commit: 2870a9fa52b73fdf344cc723e59957d76d60e395（scope-r2 approved head；范围冻结）
branch: main
worktree: G:\CODEX\New Manga
integration_commit: null
delivery_head: 7b176be6a（R2 交付证据 commit；Canonical Evidence re-pin @该 commit）
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

## 路径口径裁定（有意偏差登记，F08R1-003）

- **原型/脚本**：`G:\CODEX\New Manga.workspace\FEA-08\prototype\`（非 Git，控制仓库体积；FEA 线 workspace 根级实践）；Task/证据登记路径与每个脚本 SHA-256（`verification/FEA-08/prototype_hashes.txt`，15 个登记脚本）。
- **报告**：`doc/research/FEA-08-source-capability.md`（研究类，归 research；不写入冻结设计目录）。
- **临时数据**：`G:\CODEX\New Manga.workspace\FEA-08\tmp\`（合成数据；`run_all.py` 运行后实际清理，`tmp_remaining=[]` 入 `results/run_all_log.json`）。
- 与提案 :929 "experiments/ + doc/design/ + workspace/tasks/FEA-08" 的偏差即上述三点，理由：原型非生产资产、报告非设计冻结物、临时数据沿用 FEA 线既有 workspace 根级实践。
- **depends_on**：`FEA-01-FREEZE-1`（已存在 Task）；FEA-00 仅作依据引用，不入 depends_on。
- **Canonical Evidence pin 口径（R2 / F08I1-002，DSH 裁决 + 集成处置）**：pin `sha256` = 被 pin commit 的 **Git blob 字节（LF 规范）**的 SHA-256，复现 `git cat-file -p <commit>:<path>`；工作树 `Get-FileHash` 与之一致。集成处置：`.gitattributes` 已增 `verification/FEA-08/{*.json,**/*.json,**/*.log,**/*.md,**/*.txt}` → `text eol=lf`（DSH 提交 `07724b88d`；该文件不在本 Task allowed_paths，属集成动作，不计入实现写域）。三方一致性（blob/工作树/Task 表）与干净 checkout 复现见 `logs/pin-verify.log`。
- **R2 实施分工**：ZCode R2 session 完成脚本/证据改造（10:08–10:39，额度耗尽中断，未提交）；DSH 以 Integrator 身份收口（字段自洽修正、全链重跑/staging、EV re-pin、门禁、Handoff）。impl-r2 Review 由未参与实现的独立上下文执行。

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

## 验收（scope-r2 冻结；R2 证据收口）

- [x] **AC-1（H4）**：三断言全 measured（10 场景，h4_results.json）。 <<MET>>
  1. digest 取自打开时验证过的**同一句柄/流**；读取前后以句柄级身份（volume serial + file index）与 size/mtime 比对，一致才成立；
  2. 读取中途外部替换/写入的结果只能是 **unavailable 或完整旧 digest**，不得出现混合/部分新内容 digest 的假成功；杜绝 check 后按路径另开文件；
  3. 矩阵场景含"内存映射写"；不可证则该项 LIMITED/UNAVAILABLE。
  - R2 收口：S5a/S5b 字段自洽（classification=undetected_mixed，detail.mixed_digest_risk=true，outcome_protocol=digest_returned，评估 outcome=unavailable，mixed_digest_risk_field_consistent=true）；S2 写者 `blocked(win32=32)` 实测；S5 mtime_changed 由读前/读后真实 FileIdentity 计算；h4 summary 明示 strict-only 生产硬约束（F08I1-003/004）。
- [x] **AC-2（H5）**：判定操作 = 失败/取消/中断后目标仍在原路径（保留），或成功回收时存在于回收站且**还原后 digest 与回收前一致**；覆盖提案 :512–:514 分支（不可回收卷/策略、网络盘限制、路径被替换、结果未知、目录不可回收则保留且不得改调永久 rmdir）；**禁止清空类 API、仅合成路径**；合成 fixture 回收站条目测试后还原并删除（数量/结果入日志）或显式登记保留；"模拟中断"恢复判据 = receipt + 文件系统事实核对，不重发 destructive 操作。 <<MET>>
  - R2 收口：R2/R9 回收站条目有界轮询（`entries_poll`）；`h5_run.py` 期望 PASS 场景 FAIL 时非零退出；`run_all.py` 二次校验 results verdict；R6b destructive 计数 5→5（`no_destructive_reissued=true`）；R5b 类型/属性实测（`current_type=directory`）；R3 "不可回收→保留不 fallback rmdir" 分支经 mock 失败注入（ret=0x79）走通并标 LIMITED(mocked)（F08I1-005/006）。
- [x] **AC-3（H6）**：按 :457/:469 二分"精确匹配/候选"并附判定所用 digest 类型（图片强 digest；文件夹成员身份+digest；容器成员内容 digest/规范解码像素 digest、尺寸、方向、唯一性；重复成员名保持独立 occurrence；感知 hash/OCR 仅候选；GIF 仅首帧；PDF 记录页码与渲染参数）；golden fixtures 与结果报告。 <<MET>>
  - R2 收口：17 场景 measured；**folder_v1/v2 六个成员已入库**（`fixtures/folder_v1|folder_v2/**`，EV 表逐文件 pin）；`h6_results.json` 记录 `fixtures_root=verification/FEA-08/fixtures`（env 来源），M8/M9 可仅凭仓库证据复现；M12/M13/M15 用独立副本/独立密文两路径比较（自读对照显式标 self-consistency）；dhash 阈值邻界 M17（距离 10→candidate）/M18（距离 11→no_match）；AES ZIP 如实标 LIMITED(pyzipper)；`fixtures_manifest` 指针指向实际存在的 `results/fixtures_manifest.json`（F08I1-001/007/011）。
- [x] **AC-4（交付完整）**：能力矩阵为二维结构 = 卷类型（NTFS 本地/USB/SMB/…）× 输入类别（单图/文件夹/ZIP/CBZ/PDF）逐项"现状/需新增"结论；每项标注证据来源 **measured/mocked/inferred**，**mock/推断不得记 PASS（上限 LIMITED(mocked)）**；技术报告含依赖/许可（如加密 ZIP/PDF fixture 需最小新依赖，二选一：登记许可+不进生产闭包，或预生成 fixture+SHA-256）；无生产代码改动。 <<MET>>
  - R2 收口：矩阵逐格含 `current`/`needed`；NTFS 行状态由 h4/h5/h6 结果 JSON 推导/校验（不再硬编码 PASS；推导不满足即降级），H4/H5 未逐格式实测的格标 `LIMITED(inferred: volume-level, format-agnostic)`，ZIP 的 AES 分支标 `LIMITED(pyzipper)`；mock/inferred 无 PASS；Canonical Evidence 51 项 @`7b176be6a` 全量可复现（blob/worktree/Task 表 + 干净 checkout），门禁记录见下与 `logs/gates.log`（F08I1-002/008/009）。

## 交付与证据

- 原型/脚本：`G:\CODEX\New Manga.workspace\FEA-08\prototype\`（非 Git；15 个登记脚本 SHA-256 见 `verification/FEA-08/prototype_hashes.txt`）。
- 报告：`doc/research/FEA-08-source-capability.md`（R2 收口版）。
- 证据：`verification/FEA-08/**`（results 7 件 / logs 8 件 + gates.log / fixtures 33 内容文件 + evidence_manifest.json / prototype_hashes.txt）。
- 复现：`python ...\prototype\run_all.py`（双生成 fixtures → staging 入库 → H4/H5/H6(直接对入库 fixtures，含 M8M9)/矩阵 → results verdict 校验 → 结果/日志 staging → tmp 清理）；`python ...\prototype\h6_run.py --fixtures ...\verification\FEA-08\fixtures`（H6 独立复跑）；`python ...\prototype\pin_selfcheck.py`（`git add` 后 pin 自校验）。
- Handoff：`doc/handoffs/FEA-08-impl.md`（impl-r1）、`doc/handoffs/FEA-08-impl-r2.md`（R2）。

## Canonical Evidence

R2 交付：全部文件 pin @ `7b176be6a`（R2 证据 commit）；`sha256` = Git blob 字节（LF）SHA-256，复现 `git cat-file -p <commit>:<path>`，工作树 `Get-FileHash` 一致（`.gitattributes` eol=lf 规则保证）。`gates.log` 为首见于登记 commit 的文件，按 SHA-256 pin（commit 列 `-`）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-F08-01 | AC-3/AC-4 | verification/FEA-08/fixtures/anim.gif | 7b176be6a | 7dd78b8dcefe5b5adc3bea15b25c9b76e1df59ebf97c5471bf8c4214553ab2fd | SOURCE_PIN |
| EV-F08-02 | AC-3/AC-4 | verification/FEA-08/fixtures/book_dup.zip | 7b176be6a | dcd801c16dda0cc2c30f14b9e7be548dea86f2fe542d4d40af782dc791306397 | SOURCE_PIN |
| EV-F08-03 | AC-3/AC-4 | verification/FEA-08/fixtures/book_dup_copy.zip | 7b176be6a | bfc7b351471da8c3bd2fd3639a0a23407dfdf2cbf161d23cae57bed4d16ebc05 | SOURCE_PIN |
| EV-F08-04 | AC-3/AC-4 | verification/FEA-08/fixtures/book_enc_aes.zip | 7b176be6a | fe4338f1f3250419b5eb351706896f6536d6bab472c7ef0e60e7bf70d62f46d1 | SOURCE_PIN |
| EV-F08-05 | AC-3/AC-4 | verification/FEA-08/fixtures/book_enc_zipcrypto.zip | 7b176be6a | e1da6e144f2a3a27393c3fca1ccea81ab80cd98994a6a40e4a70555e8baaf5bd | SOURCE_PIN |
| EV-F08-06 | AC-3/AC-4 | verification/FEA-08/fixtures/book_enc_zipcrypto_copy.zip | 7b176be6a | 9014175f97ac98cd7cdd4308a4237f15c860c9760f050db817005f4ee43c7ce7 | SOURCE_PIN |
| EV-F08-07 | AC-3/AC-4 | verification/FEA-08/fixtures/book_v1.cbz | 7b176be6a | 4f1503cf0c86d29c970d3eb037d78b4d3bf405096e8b37ae0323ff520f706166 | SOURCE_PIN |
| EV-F08-08 | AC-3/AC-4 | verification/FEA-08/fixtures/book_v1.zip | 7b176be6a | 4f1503cf0c86d29c970d3eb037d78b4d3bf405096e8b37ae0323ff520f706166 | SOURCE_PIN |
| EV-F08-09 | AC-3/AC-4 | verification/FEA-08/fixtures/book_v1_recompressed.zip | 7b176be6a | 313174905b7e7c14626befe171d8ff6c398e1ebff8a723cf091554c46eccd383 | SOURCE_PIN |
| EV-F08-10 | AC-3/AC-4 | verification/FEA-08/fixtures/doc_enc.pdf | 7b176be6a | f7e7694299573e54086dfc6d6d362e3c389c78ded1521b2388609b39f00b4b8d | SOURCE_PIN |
| EV-F08-11 | AC-3/AC-4 | verification/FEA-08/fixtures/doc_enc_copy.pdf | 7b176be6a | d6458d3a3e220ce42efe8f311bb4889a4db3efb272d769a405f83f1720bd4515 | SOURCE_PIN |
| EV-F08-12 | AC-3/AC-4 | verification/FEA-08/fixtures/doc_v1.pdf | 7b176be6a | 84369184d113196e05c3062d83e37352113cac13049348c14b8de594960b3ef4 | SOURCE_PIN |
| EV-F08-13 | AC-3/AC-4 | verification/FEA-08/fixtures/doc_v1_regen.pdf | 7b176be6a | d97714600647593bb89725932bed07d0c62d3d46c237457658370a6a17e35c8d | SOURCE_PIN |
| EV-F08-14 | AC-3/AC-4 | verification/FEA-08/fixtures/evidence_manifest.json | 7b176be6a | a4237c35eaedcd73e0c773b67a0619a0b82c0981e762a5c3176d35005a425b24 | SOURCE_PIN |
| EV-F08-15 | AC-3/AC-4 | verification/FEA-08/fixtures/firstframe_extract.png | 7b176be6a | f411173051663150ef31d5b3d86a9f5ddb9177d9c5cd5ff2b44c35d3b436ae0f | SOURCE_PIN |
| EV-F08-16 | AC-3/AC-4 | verification/FEA-08/fixtures/folder_v1/p1.png | 7b176be6a | 869e410694cd5f808803c2af5f2d6ce95dd651c76e5e44e1baafe66dbffc38fa | SOURCE_PIN |
| EV-F08-17 | AC-3/AC-4 | verification/FEA-08/fixtures/folder_v1/p2.png | 7b176be6a | da0ad99a91ffff15d6fefcb417c9c1adf1a4160a15718cd16ba4bddc202164f1 | SOURCE_PIN |
| EV-F08-18 | AC-3/AC-4 | verification/FEA-08/fixtures/folder_v1/p3.png | 7b176be6a | 796c1b31e4463efed47d54f9bff124d20a17f1a2aafca7259ca5bd90b4449678 | SOURCE_PIN |
| EV-F08-19 | AC-3/AC-4 | verification/FEA-08/fixtures/folder_v2/p1.png | 7b176be6a | 869e410694cd5f808803c2af5f2d6ce95dd651c76e5e44e1baafe66dbffc38fa | SOURCE_PIN |
| EV-F08-20 | AC-3/AC-4 | verification/FEA-08/fixtures/folder_v2/p2renamed.png | 7b176be6a | da0ad99a91ffff15d6fefcb417c9c1adf1a4160a15718cd16ba4bddc202164f1 | SOURCE_PIN |
| EV-F08-21 | AC-3/AC-4 | verification/FEA-08/fixtures/folder_v2/p4.png | 7b176be6a | 869e410694cd5f808803c2af5f2d6ce95dd651c76e5e44e1baafe66dbffc38fa | SOURCE_PIN |
| EV-F08-22 | AC-3/AC-4 | verification/FEA-08/fixtures/img_base.png | 7b176be6a | 869e410694cd5f808803c2af5f2d6ce95dd651c76e5e44e1baafe66dbffc38fa | SOURCE_PIN |
| EV-F08-23 | AC-3/AC-4 | verification/FEA-08/fixtures/img_cmyk.jpg | 7b176be6a | 0d17f9bd7b8e51ed51c237410a77255c31120b7902e50f875da62a926d01199b | SOURCE_PIN |
| EV-F08-24 | AC-3/AC-4 | verification/FEA-08/fixtures/img_copy.png | 7b176be6a | 869e410694cd5f808803c2af5f2d6ce95dd651c76e5e44e1baafe66dbffc38fa | SOURCE_PIN |
| EV-F08-25 | AC-3/AC-4 | verification/FEA-08/fixtures/img_dhash_dist10.png | 7b176be6a | 5ba3df93071ee7a2710e63757fa9d3194a418aca493410530db385928a0c565c | SOURCE_PIN |
| EV-F08-26 | AC-3/AC-4 | verification/FEA-08/fixtures/img_dhash_dist11.png | 7b176be6a | 68b2ce3459521c379291f7e58cd58a74407788ff0a41d0d72a5cb9ede679e4c4 | SOURCE_PIN |
| EV-F08-27 | AC-3/AC-4 | verification/FEA-08/fixtures/img_dhash_ref.png | 7b176be6a | 6d791ee79e1ab53fbdf02aa40e09aa47e55ada861e4062a36c9216282651d03a | SOURCE_PIN |
| EV-F08-28 | AC-3/AC-4 | verification/FEA-08/fixtures/img_exif_o6.png | 7b176be6a | b125c108b081fd0d59c19090a182ed7507f9a739f5079494f2b9e69460e71bff | SOURCE_PIN |
| EV-F08-29 | AC-3/AC-4 | verification/FEA-08/fixtures/img_flipped.png | 7b176be6a | 8c4b9bff2fabe004bbfe159926afdc39bb6d3d5dc351caeb1903900a1dc435c8 | SOURCE_PIN |
| EV-F08-30 | AC-3/AC-4 | verification/FEA-08/fixtures/img_gray.png | 7b176be6a | 34f0b239609575302cc2f1b2e4a57e26ea69d1b27cb984dc0877a7f43f292c2c | SOURCE_PIN |
| EV-F08-31 | AC-3/AC-4 | verification/FEA-08/fixtures/img_gray_as_rgb.png | 7b176be6a | d4723bb228449cd6203c21b665f31ff8c5726aa42ff5644afa1c226a6a67e744 | SOURCE_PIN |
| EV-F08-32 | AC-3/AC-4 | verification/FEA-08/fixtures/img_reenc.jpg | 7b176be6a | 863d49deb2906fac893953e35150b1600bc0cc645baf0d29d4d372037b87012c | SOURCE_PIN |
| EV-F08-33 | AC-3/AC-4 | verification/FEA-08/fixtures/img_rotated_phys.png | 7b176be6a | 3937a0debc3c1bc12f39246ce56257e7b7e2ea446ac0559dce0cf9a33bddd095 | SOURCE_PIN |
| EV-F08-34 | AC-3/AC-4 | verification/FEA-08/fixtures/wrongframe_blue.png | 7b176be6a | b9c21277c74c0f24dbd06c770443b182de40c8a439993e01b08ee84e7ce04b4e | SOURCE_PIN |
| EV-F08-35 | AC-1 | verification/FEA-08/logs/h4_run.log | 7b176be6a | 4a2e8d7af50220cfc7025f348e61b28f7334dd7444f7737d2018c5abe9c72b7c | CANONICAL |
| EV-F08-36 | AC-2 | verification/FEA-08/logs/h5_run.log | 7b176be6a | 5589b33da77857243def405918ac8fa370904e719653a47e36869a17319aa5fd | CANONICAL |
| EV-F08-37 | AC-3 | verification/FEA-08/logs/h6_run.log | 7b176be6a | bd81d2d875c239e12723c5ef85b8789a90a106be75f00faf79476331abfafc31 | CANONICAL |
| EV-F08-38 | AC-3/AC-4 | verification/FEA-08/logs/make_fixtures.log | 7b176be6a | 8171ed89b17322f0d0d32ab0eda082917e6e261e0b83d377eb7c1ec9d40caa33 | CANONICAL |
| EV-F08-39 | AC-3/AC-4 | verification/FEA-08/logs/make_fixtures_regeneration.log | 7b176be6a | 8171ed89b17322f0d0d32ab0eda082917e6e261e0b83d377eb7c1ec9d40caa33 | CANONICAL |
| EV-F08-40 | AC-4 | verification/FEA-08/logs/matrix.log | 7b176be6a | 98ee99d44af2425c0f7da00a5aa908adbb0aef2d1305d408e4421a4009385817 | CANONICAL |
| EV-F08-41 | AC-1..4 | verification/FEA-08/logs/run_all.log | 7b176be6a | 5c951f0064aa4265d746d9d4ab89088e8ce39ee9655f7fb2030d3ac946ce93f0 | CANONICAL |
| EV-F08-42 | AC-3/AC-4 | verification/FEA-08/logs/stage_evidence.log | 7b176be6a | 98678aa0639f374fabe5082da75825223ad6ccdfc6694a3f2d7ac116baba020e | CANONICAL |
| EV-F08-43 | AC-3/AC-4 | verification/FEA-08/prototype_hashes.txt | 7b176be6a | 3336a7b45923af469b094d5aec045250e0a2b8d5152a6203ef2a86c9372cabca | CANONICAL |
| EV-F08-44 | AC-4 | verification/FEA-08/results/capability_matrix.json | 7b176be6a | 1c9ec50eee9497b37510e8b793ae1ecfc60ce69820cec3bb2116b67ebd917fa0 | CANONICAL |
| EV-F08-45 | AC-4 | verification/FEA-08/results/capability_matrix.md | 7b176be6a | 5e10c4fd01c0caa9707ae50ad0537b433f936307af213bfacfdc178d7f132f06 | CANONICAL |
| EV-F08-46 | AC-3 | verification/FEA-08/results/fixtures_manifest.json | 7b176be6a | 0791f4ddc17931bc40d71ffb853f2b2babf8f762f9040e432905344d2b8e21d0 | CANONICAL |
| EV-F08-47 | AC-1 | verification/FEA-08/results/h4_results.json | 7b176be6a | 37c4888841be62cc43ebc9c4b21bdadb4bd17c815cd880fa93743f45fb1293df | CANONICAL |
| EV-F08-48 | AC-2 | verification/FEA-08/results/h5_results.json | 7b176be6a | 51005a013dda69d7976b805e55812a9acd8facd9d423039ec8c156044994c608 | CANONICAL |
| EV-F08-49 | AC-3 | verification/FEA-08/results/h6_results.json | 7b176be6a | 56c43a175a6e148c4c045d3b6cbc4394f2686354731ac6feb36af4eee5f0a12e | CANONICAL |
| EV-F08-50 | AC-1..4 | verification/FEA-08/results/run_all_log.json | 7b176be6a | 981a585aaedaec91c61457176a356ba16c6478e6528737ecd3d480388ad40356 | CANONICAL |
| EV-F08-51 | AC-1..4 | verification/FEA-08/logs/gates.log | - | fd227b34a27093c1498fbe73622bf33ca16661e0f3995cb138635f9911d6f177 | CANONICAL |

## 门禁记录（R2 交付，2026-11-03；原始输出 `logs/gates.log`）

| 门禁 | 命令 | head | EXIT | 结果 |
|---|---|---|---|---|
| build | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | `7b176be6a` | 0 | 0 warning / 0 error |
| 无过滤全量 | `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --nologo` | `7b176be6a` | 0 | **1292 passed / 0 failed / 57 skipped**（逐程序集 21/38/51/253/117/31/128/653；skip 0/0/28/0/0/0/22/7） |
| 治理检查 | `pwsh -NoProfile -File tools\governance\check.ps1` | `7b176be6a` | 0 | PASS(3 warnings) |
| 冻结 pin | `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | `7b176be6a` | 0 | 15/15 PASS |
| 旧 FEA-06 四 PNG | `Get-FileHash verification\FEA-06\screens\*.png -Algorithm SHA256` | `7b176be6a` | — | reader `8533c263…`/settings `fd30b166…`/shelf `307f8f67…`/workbench `d5d878bb…`（与 FEA-06 卡一致，未变） |
| 禁止范围 diff | `git diff --name-only 2870a9fa5..7b176be6a -- src apps experiments tests packaging scripts tools` | `2870a9fa5..7b176be6a` | — | 空（**src_changes=0**；R2 无生产代码改动） |
| Canonical Evidence pin | `python ...\prototype\pin_selfcheck.py`（`git add` 后） | `7b176be6a` | 0 | 51/51 blob==worktree==Task 表 + 干净 checkout 复现（`logs/pin-verify.log`） |
| 安全边界 | 全仓搜索 `SHEmptyRecycleBin|EmptyRecycleBin|SHERB_` 调用；H5 lab 路径核对 | `7b176be6a` | — | 调用=0（仅注释）；G: 回收站 0→0、leftover=0；tmp_remaining=[] |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| prototype（非 Git） | `G:\CODEX\New Manga.workspace\FEA-08\prototype\` | PRESERVE_REFERENCED | 原地（workspace） | `verification/FEA-08/prototype_hashes.txt`（15 脚本 SHA-256） | 复现证据生成所需；被 Task/Handoff/EV 引用 |
| temp（合成） | `G:\CODEX\New Manga.workspace\FEA-08\tmp\` | DELETE_SAFE | 已删除 | `results/run_all_log.json`（tmp_removed/tmp_remaining=[]） | run_all 末尾实际清理；tmp 当前为空 |
| artifact（生成侧） | `G:\CODEX\New Manga.workspace\FEA-08\out\` | DELETE_SAFE | 原地保留（可再生） | 无 pin（入库副本见 verification/FEA-08） | 由 run_all 再生；不作为证据源 |
| agent-output | workspace `FEA-08\{r2-*,impl-*,scope-*}.log/prompt` | PRESERVE_REFERENCED | 原地（workspace） | 无 | 派发/原始日志，非 Canonical |
| 回收站合成条目 | G: `$RECYCLE.BIN`（lab 前缀） | DELETE_SAFE | 已还原并删除 | `results/h5_results.json` restore_log | 5 条还原后删除；G: 0→0、leftover=0；C: 用户条目 2 条未触碰 |
| evidence（仓库） | `verification/FEA-08/**` | NOT_APPLICABLE | 仓库内 | EV 表（51 项） | Canonical Evidence |

## 待 scope-r2 确认

1. 隔离测试 SQLite：**否**（已写入 BLOCKED）。
2. USB/SMB 无硬件：接受 mock/LIMITED(mocked)（已写入 AC-4）。
3. H6 加密格式 fixture：预生成+SHA 或最小依赖（pyzipper MIT）二选一（已写入 AC-4）。

## Closeout Record

- Closeout date / DSH：待 impl-r2 Review 通过 + 集成验证后填写。
- canonical_evidence_status：`complete`（51 项 pin 自校验通过）。
- resource_closeout_status：`pending`（关闭时按上表逐项复核）。
- 删除、迁移、归档数量/字节数：待关闭时填写（预计：tmp 删除、回收站条目 0 残留；无迁移）。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：STATUS / Plan / Task 导航 / rolling checkpoint 待关闭时更新。