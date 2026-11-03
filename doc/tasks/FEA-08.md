---
id: FEA-08
title: Source/回收站隔离原型（H4/H5/H6 能力矩阵与技术报告）
kind: prototype
governance_version: 3
status: in_review
approval: scope-r2 **approved**（ZCode CLI fresh session，P0=0/P1=0/P2=2；2026-11-03；报告 doc/reviews/FEA-08-scope-r2.md）
suggested_owner: zcode
owner: zcode
reviewer: scope-r2 approved（ZCode）；impl Reviewer 待 DSH Appointment
depends_on:
  - FEA-01-FREEZE-1
base_commit: 2870a9fa52b73fdf344cc723e59957d76d60e395（scope-r2 approved head；范围冻结）
branch: main
worktree: G:\CODEX\New Manga
integration_commit: null
delivery_head: c422bf16461309b4b077426cccd0f06a83a3583f
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

## 路径口径裁定（有意偏差登记，F08R1-003）
- **原型/脚本**：`G:\CODEX\New Manga.workspace\FEA-08\prototype\`（非 Git，控制仓库体积；FEA 线 workspace 根级实践）；Task/证据登记路径与每个脚本 SHA-256。
- **报告**：`doc/research/FEA-08-source-capability.md`（研究类，归 research；不写入冻结设计目录）。
- **临时数据**：`G:\CODEX\New Manga.workspace\FEA-08\tmp\`（合成数据，运行后清理并留日志）。
- 与提案 :929 "experiments/ + doc/design/ + workspace/tasks/FEA-08" 的偏差即上述三点，理由：原型非生产资产、报告非设计冻结物、临时数据沿用 FEA 线既有 workspace 根级实践。
- **depends_on**：`FEA-01-FREEZE-1`（已存在 Task）；FEA-00 仅作依据引用，不入 depends_on。

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

## 验收（待 scope-r2 冻结）
- [x] **AC-1（H4）**：三断言全 measured（10 场景，h4_results.json）。 <<MET>>
  1. digest 取自打开时验证过的**同一句柄/流**；读取前后以句柄级身份（volume serial + file index）与 size/mtime 比对，一致才成立；
  2. 读取中途外部替换/写入的结果只能是 **unavailable 或完整旧 digest**，不得出现混合/部分新内容 digest 的假成功；杜绝 check 后按路径另开文件；
  3. 矩阵场景含"内存映射写"；不可证则该项 LIMITED/UNAVAILABLE。
- [x] **AC-2（H5）**：判定操作 = 失败/取消/中断后目标仍在原路径（保留），或成功回收时存在于回收站且**还原后 digest 与回收前一致**；覆盖提案 :512–:514 分支（不可回收卷/策略、网络盘限制、路径被替换、结果未知、目录不可回收则保留且不得改调永久 rmdir）；**禁止清空类 API、仅合成路径**；合成 fixture 回收站条目测试后还原并删除（数量/结果入日志）或显式登记保留；"模拟中断"恢复判据 = receipt + 文件系统事实核对，不重发 destructive 操作。 <<MET>>
- [x] **AC-3（H6）**：按 :457/:469 二分"精确匹配/候选"并附判定所用 digest 类型（图片强 digest；文件夹成员身份+digest；容器成员内容 digest/规范解码像素 digest、尺寸、方向、唯一性；重复成员名保持独立 occurrence；感知 hash/OCR 仅候选；GIF 仅首帧；PDF 记录页码与渲染参数）；golden fixtures 与结果报告。 <<MET>>
- [x] **AC-4（交付完整）**：能力矩阵为二维结构 = 卷类型（NTFS 本地/USB/SMB/…）× 输入类别（单图/文件夹/ZIP/CBZ/PDF）逐项"现状/需新增"结论；每项标注证据来源 **measured/mocked/inferred**，**mock/推断不得记 PASS（上限 LIMITED(mocked)）**；技术报告含依赖/许可（如加密 ZIP/PDF fixture 需最小新依赖，二选一：登记许可+不进生产闭包，或预生成 fixture+SHA-256）；无生产代码改动。 <<MET>>

## 交付与证据
- 原型/脚本：`G:\CODEX\New Manga.workspace\FEA-08\prototype\`（非 Git；hash 登记）。
- 报告：`doc/research/FEA-08-source-capability.md`；证据：`verification/FEA-08/**`（命令/EXIT/日志/矩阵/原型 hash）；Handoff：`doc/handoffs/FEA-08-*.md`。

## Canonical Evidence

impl 交付（2026-11-03）；全部文件 pin @ delivery_head `c422bf164`；sha256 一律为 git blob 哈希（复现：`git cat-file -p <commit>:<path>`）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-F08-01 | AC-3/AC-4 | verification/FEA-08/fixtures/anim.gif | c422bf164 | 7dd78b8dcefe5b5adc3bea15b25c9b76e1df59ebf97c5471bf8c4214553ab2fd | SOURCE_PIN |
| EV-F08-02 | AC-3/AC-4 | verification/FEA-08/fixtures/book_dup.zip | c422bf164 | 478ff64e17f4985c482689131bbda12d5d1ab4696c6ca265b2307cb9978c7ab4 | SOURCE_PIN |
| EV-F08-03 | AC-3/AC-4 | verification/FEA-08/fixtures/book_enc_aes.zip | c422bf164 | ae47692a847007a3451b45e455b487bf4466a77ae0c9391ab85ee927a359c650 | SOURCE_PIN |
| EV-F08-04 | AC-3/AC-4 | verification/FEA-08/fixtures/book_enc_zipcrypto.zip | c422bf164 | 2d1eaf6cad8cb873f9c4095044460c91e6e39cacf8bd81dcb8daa82dcfd383b2 | SOURCE_PIN |
| EV-F08-05 | AC-3/AC-4 | verification/FEA-08/fixtures/book_v1.cbz | c422bf164 | 6fea6b6bdb7f67a39449de0e8355f8380c1bd342f893de26933aa98dd69253c1 | SOURCE_PIN |
| EV-F08-06 | AC-3/AC-4 | verification/FEA-08/fixtures/book_v1.zip | c422bf164 | 6fea6b6bdb7f67a39449de0e8355f8380c1bd342f893de26933aa98dd69253c1 | SOURCE_PIN |
| EV-F08-07 | AC-3/AC-4 | verification/FEA-08/fixtures/book_v1_recompressed.zip | c422bf164 | ad5d56371126e45aeb70994b62f7bfeb50bd0998f36a41b19bf0a41d41179eac | SOURCE_PIN |
| EV-F08-08 | AC-3/AC-4 | verification/FEA-08/fixtures/doc_enc.pdf | c422bf164 | 9da8eff852f646b988d24c1eac5f372df0e228551232781c6f0b4be7ec974432 | SOURCE_PIN |
| EV-F08-09 | AC-3/AC-4 | verification/FEA-08/fixtures/doc_v1.pdf | c422bf164 | 6a4ada60f0dc78a6d3bd9621007c859f653e8b56f02ff449367e0cde1604afe5 | SOURCE_PIN |
| EV-F08-10 | AC-3/AC-4 | verification/FEA-08/fixtures/doc_v1_regen.pdf | c422bf164 | c19f08386335ebd7d9c69e026b67937864e96f73692ec94098f1aad6b7ce8180 | SOURCE_PIN |
| EV-F08-11 | AC-3/AC-4 | verification/FEA-08/fixtures/evidence_manifest.json | c422bf164 | b87a35a44d65487d4d8a1153104ccd571dd325ea7ba021d563fc9c6d73ef3202 | SOURCE_PIN |
| EV-F08-12 | AC-3/AC-4 | verification/FEA-08/fixtures/firstframe_extract.png | c422bf164 | f411173051663150ef31d5b3d86a9f5ddb9177d9c5cd5ff2b44c35d3b436ae0f | SOURCE_PIN |
| EV-F08-13 | AC-3/AC-4 | verification/FEA-08/fixtures/img_base.png | c422bf164 | 869e410694cd5f808803c2af5f2d6ce95dd651c76e5e44e1baafe66dbffc38fa | SOURCE_PIN |
| EV-F08-14 | AC-3/AC-4 | verification/FEA-08/fixtures/img_cmyk.jpg | c422bf164 | 0d17f9bd7b8e51ed51c237410a77255c31120b7902e50f875da62a926d01199b | SOURCE_PIN |
| EV-F08-15 | AC-3/AC-4 | verification/FEA-08/fixtures/img_copy.png | c422bf164 | 869e410694cd5f808803c2af5f2d6ce95dd651c76e5e44e1baafe66dbffc38fa | SOURCE_PIN |
| EV-F08-16 | AC-3/AC-4 | verification/FEA-08/fixtures/img_exif_o6.png | c422bf164 | b125c108b081fd0d59c19090a182ed7507f9a739f5079494f2b9e69460e71bff | SOURCE_PIN |
| EV-F08-17 | AC-3/AC-4 | verification/FEA-08/fixtures/img_flipped.png | c422bf164 | 8c4b9bff2fabe004bbfe159926afdc39bb6d3d5dc351caeb1903900a1dc435c8 | SOURCE_PIN |
| EV-F08-18 | AC-3/AC-4 | verification/FEA-08/fixtures/img_gray.png | c422bf164 | 34f0b239609575302cc2f1b2e4a57e26ea69d1b27cb984dc0877a7f43f292c2c | SOURCE_PIN |
| EV-F08-19 | AC-3/AC-4 | verification/FEA-08/fixtures/img_gray_as_rgb.png | c422bf164 | d4723bb228449cd6203c21b665f31ff8c5726aa42ff5644afa1c226a6a67e744 | SOURCE_PIN |
| EV-F08-20 | AC-3/AC-4 | verification/FEA-08/fixtures/img_reenc.jpg | c422bf164 | 863d49deb2906fac893953e35150b1600bc0cc645baf0d29d4d372037b87012c | SOURCE_PIN |
| EV-F08-21 | AC-3/AC-4 | verification/FEA-08/fixtures/img_rotated_phys.png | c422bf164 | 3937a0debc3c1bc12f39246ce56257e7b7e2ea446ac0559dce0cf9a33bddd095 | SOURCE_PIN |
| EV-F08-22 | AC-3/AC-4 | verification/FEA-08/fixtures/wrongframe_blue.png | c422bf164 | b9c21277c74c0f24dbd06c770443b182de40c8a439993e01b08ee84e7ce04b4e | SOURCE_PIN |
| EV-F08-23 | AC-1 | verification/FEA-08/logs/h4_run.log | c422bf164 | 4a2e8d7af50220cfc7025f348e61b28f7334dd7444f7737d2018c5abe9c72b7c | CANONICAL |
| EV-F08-24 | AC-2 | verification/FEA-08/logs/h5_run.log | c422bf164 | 87807d5fc20e4eadaa0d1f457dfd76c99a8521e6fa239dcc93c1a288ba8690ed | CANONICAL |
| EV-F08-25 | AC-3 | verification/FEA-08/logs/h6_run.log | c422bf164 | 5fd741ce2f662599749d16ea55586cda68280627d71ee4aa2be943b89de3977a | CANONICAL |
| EV-F08-26 | AC-1..4 | verification/FEA-08/logs/make_fixtures.log | c422bf164 | aaa6bd1135f5779a77ad733d085621ad77b5971fb02bcb9d26933bac162fd4db | CANONICAL |
| EV-F08-27 | AC-1..4 | verification/FEA-08/logs/matrix.log | c422bf164 | 5e189f8c1fa17878620b8e5a0b7e4ac40f7c5ddd7701907257c5ad78f031c7dc | CANONICAL |
| EV-F08-28 | AC-1..4 | verification/FEA-08/logs/run_all.log | c422bf164 | 5346f42e6f7f295d2cfb55e36739a09756c943c971da8907936b203800d22203 | CANONICAL |
| EV-F08-29 | AC-3/AC-4 | verification/FEA-08/prototype_hashes.txt | c422bf164 | 8a4a89e7e09785c392bd7b4b46cc900d604f342197fde85fadf83c36f5bc1deb | SOURCE_PIN |
| EV-F08-30 | AC-4 | verification/FEA-08/results/capability_matrix.json | c422bf164 | 2a889d77f7a17ec87988d0e9bb41cb0376911e1e72066e5a573a72af65dfa28e | CANONICAL |
| EV-F08-31 | AC-4 | verification/FEA-08/results/capability_matrix.md | c422bf164 | 77947a4c07a4e4517037b3771ab617a0fe3d7f8b1b7d3e8347331143c67e03bb | CANONICAL |
| EV-F08-32 | AC-3 | verification/FEA-08/results/fixtures_manifest.json | c422bf164 | 9c38e9f2de72ef436df64586ca766a425abca98dd73ae9256df7d7516b38ef01 | CANONICAL |
| EV-F08-33 | AC-1 | verification/FEA-08/results/h4_results.json | c422bf164 | ee167b07602adfd175203b861395369db47e5d25085ae7207b8c979873ce3d03 | CANONICAL |
| EV-F08-34 | AC-2 | verification/FEA-08/results/h5_results.json | c422bf164 | d802dfa5c350e4dcbd6acf3f8668e8b9a7eddd63efe91f3842146fdb08655f84 | CANONICAL |
| EV-F08-35 | AC-3 | verification/FEA-08/results/h6_results.json | c422bf164 | db2d7bfc50d5845ad5fdae197669295a5bbab48ca6dad18db5d3175f86e0cfb7 | CANONICAL |
| EV-F08-36 | AC-1..4 | verification/FEA-08/results/run_all_log.json | c422bf164 | b953d2fdba3b91804dd15d70b9ff15a07f023709b6db8e006ab603ba21e42c9a | CANONICAL |

复现：`python run_all.py`（workspace 原型 14 脚本，SHA-256 见 EV 表 prototype_hashes.txt；tmp 运行后清理）。dotnet build/test 与 check/pins 门禁值见下「门禁记录」。

## 待 scope-r2 确认
1. 隔离测试 SQLite：**否**（已写入 BLOCKED）。
2. USB/SMB 无硬件：接受 mock/LIMITED(mocked)（已写入 AC-4）。
3. H6 加密格式 fixture：预生成+SHA 或最小依赖（pyzipper MIT）二选一（已写入 AC-4）。
