## 复核环境说明（先声明证据边界）

本会话 `pwsh` 全程不可用（harness 报 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)`，`danger-full-access` 无审批通道）。**我无法执行任何命令**（pytest / git / check-ignore / sha256 全部无法自跑），故本次为**纯静态复核 + 集成方日志交叉核对**：代码事实从源码逐行读，运行结果以 `verification/M2-SFX-DATA-INFRA/*.log` 与 `experiments/M2-SFX-DATA-INFRA/manifest_summary.json` 为二级证据。下列结论已标明哪些项属"代码事实可核"、哪些属"仅日志自证"。

---

# 1. r1 问题逐条核对表

| 编号 | 结论 | 证据（文件:行） |
|---|---|---|
| P1-1 感知去重死代码 | **通过** | `hash.py:48-54` 新增 `box_geometry_hash`（`_box_hash_payload(..., None)` 不含 image sha，docstring 明写 r1 P1-1）；`dedup.py:13,26-28` `_box_set_key` 改用几何哈希；`dedup.py:66-78` perceptual 分支条件 `bkey`（几何）+ 汉明距离，对"sha 不同"可达；回归测试 `test_dedup.py:92-123`（断言 `sha 不同` 前置 + `perceptual_pairs` 非空 + `duplicate_of[p1]=p0`）。exact 分支 `dedup.py:54-63` 仍用 `(sha, bkey)`，判别力未降 |
| P1-2 负样本进训练 | **通过** | `splits.py:177-201`：`exclude_negative: bool = True`、`excluded_negative_ids` 留痕、`exclude_negative=False` 为显式通道；`importers.py:239` `"negative": not boxes`；`cli.py:271-279` 输出 ids。证据：`pipeline-run.log:6` = `{"train":57,"val":4}` + 10 个 id；`manifest_summary.json:41` 记 11 个空框（1 个落 test，见新-9）。测试 `test_splits_derived_same_set.py:175-189` |
| P1-3 合成全落 val | **通过** | `splits.py:86-99,119-136`（`pinned` 从比例切片中剔除）；`cli.py:59-61` `PINNED_GROUPS={"synthetic/poc":"train"}`、`cli.py:243` 传入；`manifest_summary.json:49-51` `by_split={"train":24}`、`:59-61` `pinned_groups` 入 lock；测试 `test_splits_derived_same_set.py:165-172` + 端到端 `test_cli_pipeline_smoke.py:40-43,51` |
| P1-4 occluded 未落地 | **通过** | `cli.py:216` `occluded=p.occlusion is not None`；`schema.py:40,110,137,210` 字段/序列化/反序列化/JSON Schema 四处齐；`synth.py:377-384` `i%3==0` → 8/24；测试 `test_cli_pipeline_smoke.py:16-26`（含 `(False,False)` 阴性对照） |
| P2-1 .gitignore 越界 | **部分** | `.gitignore:12-13` `/training_data/`（Codex 追认范围内 ✅）；但 r2 **又新增** `.gitignore:15-16` `experiments/M2-SFX-DATA-INFRA/*.bak`，超出 r1 追认的"最小必要变更"字面范围 → 见新-7 |
| P2-2 summary KeyError | **通过** | `cli.py:328-329` 改 `.get`（`synth_info or {}`）；`cli.py:475-485` `cmd_summary` 实算 `synth_count`/`seed`；测试 `test_cli_pipeline_smoke.py:58-62`（rc==0）。**但**修复引入了摘要退化，见新-1 |
| P2-3 dedup 回写抹 lock | **通过** | `cli.py:445-456` 回写透传 `seed=container.get("seed")` + `extra={"lock": container["lock"]}`；`subcommands-r2-run.log:4-5` dedup EXIT=0 且后续 split 的 lock 未丢。残留：不重算 fingerprint（新-6/P3） |
| P2-4 force 失效 | **通过** | `splits.py:113-117` force 时先重判 challenge、再把非 challenge 重置 `unassigned` 后重划；测试 `test_splits_derived_same_set.py:147-162`（与"全新样本同 seed 重划"指纹等值）；`subcommands-r2-run.log:6-9` seed 20261005 → `train57/val10/test8` ≠ 20261004 的 `63/8/4`（行为确实变了） |
| P2-5 fingerprint 时机 | **通过** | `cli.py:376-379` 以 `kept` 计算并回填 `split_info`，`:386-393` 写入 lock；端到端断言 `test_cli_pipeline_smoke.py:47-51`（`lock.fingerprint == split_fingerprint(records, seed)`）；`manifest_summary.json:62` = `de3787c6…` 与 handoff:131 一致 |
| P2-6 atomicio 第三态 | **通过** | `atomicio.py:8-11`（正文修正三态表述）、`:84-91`（主路径缺失回退 `.bak`）；测试 `test_atomic_recovery.py:119-131`（含"回退读的是上一完整版"语义断言 `len==1, seed==6`） |
| P2-7 README 分桶描述 | **通过** | `README.md:57-59`"排序后按比例切片（r1 P2-7 更正：是排序切片，非阈值分桶）"；`splits.py:10-12` 同口径 |
| P2-8 report val 组成写错 | **通过**（除 sha 行） | `data-infra-report.md:20-49` r2 修订段以新产物数字覆盖；`:51` 明标"r1 历史数字（被上节覆盖，留证）"。**例外**：`:44` sha 行与交付摘要不符 → 新-1 |
| P2-9 conf 丢弃 | **通过** | `importers.py:199,208-211,238` `det_conf_stats`（conf/cls/conf_ge_primary）写入 provenance，意图留痕（harvest 0.25 vs primary 0.5） |
| P2-10 challenge 破坏组原子性 | **通过** | `splits.py:6-9` 显式登记（challenge 优先于组原子性、同卷泄漏风险、不得用于泛化声明）；`README.md:68-70` 同口径 |
| P2-11 test 集弱 | **通过**（登记精度见新-9） | `README.md:70-71`、`data-infra-report.md:105-106` 登记转 T1b |
| P2-12 AC4 毛笔字体 | **部分** | 接入成立：`synth.py:45` `_BRUSHY_NAME_HINTS`、`:55-92` `discover_fonts(extra_dirs)`；`cli.py:191-198` brushy 独占过滤；`manifest_summary.json:52-54` fonts 仅 1 条 = TanukiMagic ✅；`training_data/sfx-v1/fonts/TanukiMagic.ttf` 在盘。**不通过点**：字体只在 gitignored 区，Git 内无获取脚本/sha256 pin/许可证据文本（仅 `README.md:36-39` 一句 "OFL, tanukifont.com"），跨机器不可复现；且绝对路径入摘要 → 新-2/新-5 |
| P2-13 绝对路径 | **不通过** | `cli.py:310` `data_root_gitignored` 已改相对描述 ✅；但 `cli.py:334` 新增 `"fonts": sorted({s.provenance.get("font_path")...})` 把**本机绝对路径**写进 Git 摘要：`manifest_summary.json:53` = `G:\\CODEX\\New Manga.worktrees\\M2-SFX-DATA-INFRA-zcode\\training_data\\sfx-v1\\fonts\\TanukiMagic.ttf`。同一 r1 项在同一文件内回潮 |
| P3 测试计数 27→37 | **通过** | `README.md:10`、`data-infra-report.md:45`、`green-run-r2.log:4` 均 37；我静态计数 = 7(dedup)+12(splits)+5(atomic)+5(synth)+6(schema)+2(cli smoke) = **37** ✅，其中新增回归 8 个（r1 的 29 + 8） |
| P3 报告 r2 段 | **通过** | `data-infra-report.md:20-49` |
| P3 handoff r2 段 | **通过** | `doc/handoffs/M2-SFX-DATA-INFRA-zcode-delivery-20261004.md:101-140` |
| P3 未用 import（copy/field/image_sha_by_sample） | **部分** | `field` 在用（`dedup.py:19-23`）、`image_sha_by_sample` 全仓不存在（已清）；`copy` 实际在用（`test_synth_gt_roundtrip.py:88,101`）——r1 该条本属误报。**但**新引入未用 import：`cli.py:194` `import os as _os`（全文件无 `_os.` 使用）→ 新-3 |
| P3 loader close | **通过**（生产路径） | `cli.py:254-256`、`importers.py:94` 均 `with Image.open(...)`；`test_dedup.py:74,119` 测试内未用 `with`（P4 级） |
| P3 孤儿 derived 恒 train 登记 | **通过** | `splits.py:16-17`、`README.md:60-61`（`_ranked_group_split` n<4 恒返 train） |
| P3 Task frontmatter 漂移 | **部分（仅登记未修）** | `doc/tasks/M2-SFX-DATA-INFRA.md:12` `status: ready`、`:55` `delivery_head ecb39e67`、`:56` r1 数字（39/31/5、`a02fed3d`）、`:58`"Review：尚无" —— 全文零 r2 记录；handoff:7 `r2_head: 见交付记录 §r2` 也未填实际哈希 → 新-8 |

**核对表结论**：4×P1 全通过（代码事实级可核，非仅日志）；P2 中 11 条通过、P2-1/P2-12 部分、**P2-13 不通过**；P3 中 5 条通过、2 条部分。

**我未能独立复现的项（如实登记）**：`git diff 4c12e8af..HEAD` 禁改面零触碰、`git check-ignore`、pytest 实跑 37 passed、manifest 落盘字节 sha256。

---

# 2. 新引入问题

### 新-1（P1）r2 证据声称与交付物不符；Git 可见摘要被 `summary` 覆写后丢失 P1-2/AC4 证据

- `data-infra-report.md:44-45` 与 `handoff:132` 均声称"manifest.full sha `2f8cdc1f…`、manifest.train sha `3e08c1be…` **与 manifest_summary.json 一致**"。但交付工作区中 `manifest_summary.json:82,86` 记的是 **`872e8aab…`(253295 B) / `ebf71b06…`(216280 B)**；全仓 grep（14 处命中）显示 `2f8cdc1f/3e08c1be` **只出现在这两句声称本身**，没有任何交付物承载它——即该一致性声明在交付态**不可核验（自引证）**。
- 根因（代码事实）：`cli.py:479-485` 的 `cmd_summary` 覆写**同一个** `manifest_summary.json`（默认 `--summary-out` 与 pipeline 相同），且它传入空 `DedupReport()`、`synth_from_disk` 仅含 `synth_count`、`train_info` 仅含一句 note → 摘要退化为 `gt_roundtrip_max_err_px: null`（`manifest_summary.json:46`，AC4 互算 1.705e-13 只剩 `pipeline-run.log:3`）、`excluded_negative_ids` 消失（`:75-79` 只剩 note，P1-2 证据出 Git）、`import_assets` 丢 `imported/boxes/assets_copied`、`dedup` 变成无条件写死 `0/0/0/[]`（`:69-74`，即使真有丢弃也报 0）。运行顺序见 `subcommands-r2-run.log:2,12`——`summary` 是 r2 复核的**最后一条命令**。
- 两种交付态都成立缺陷：若交付 commit 存的是 pipeline 版（2f8cdc1f），则工作区相对 commit 存在**未提交改写**（摘要被复核动作回写），交付即脏；若存的是 `summary` 版（我读到的 872e8aab），则报告/handoff 的数字与"与摘要一致"均为**假陈述**。
- 新增 e2e 测试恰好掩盖了它：`test_cli_pipeline_smoke.py:59-63` 在跑完 `summary` 后只断言 `by_split` 与 `data_root_gitignored`，**不断言** `gt_roundtrip_max_err_px`/`train_builder`/`import_assets` 未被降级。
- 最小修法：摘要单一写者（或 `cmd_summary` 复算并保留 pipeline 字段/把降级如实标注 "degraded"），复核脚本把 `summary` 排在 `pipeline` 之前，重跑后同步更新 report:44-45 与 handoff:132 的数字；并在报告登记"子命令顺序会改写 Git 摘要"。

### 新-2（P2）P2-13 回潮：摘要含本机绝对路径，且 manifest 内路径约定不一致

`cli.py:334` 写 `font_path` 原值（绝对），落 `manifest_summary.json:53`（两份副本 `.bak:53` 同）；而同一 manifest 里 `image.path` 已改为 `assets/...`、`synthetic/...` 相对约定（`cli.py:157,176,213`）。修法一行：写 `Path(font_path).name` 或相对 `fonts/` 约定。

### 新-3（P3）未用 import（与 r1 同类，r2 新引入）

`cli.py:194` `import os as _os`，函数内后续未引用（`:195-197` 只用 `Path` 与 `_BRUSHY_NAME_HINTS`）。

### 新-4（P3）死代码与取值风格不一致

- `importers.py:212-215`：`if not boxes: pass` 空操作分支（唯一内容为注释）——r1 P1-1 的同类问题（咽掉的分支）。
- `importers.py:237` `d["cls"]` 直取，而 `:210` 用 `det.get("cls")`；检测项缺 `cls` 键时导入器会硬崩而非登记。
- 可顺手清：`schema.py:14` 与 `splits.py:35` 的 `SPLIT_CLASSES` 均定义后从未使用（重复常量）；`dedup.py:59-60` `box_exact_pairs` 与 `exact_pairs` 恒同（恒冗余字段）。

### 新-5（P3）毛笔字体的可复现性与启发式风险

- TanukiMagic 只存在于 gitignored `training_data/sfx-v1/fonts/`；Git 内无获取脚本、无 sha256 pin、无许可证据文件（`README.md:36-39` 仅文字声明 OFL/tanukifont.com）。⇒ 换机器/clean checkout 时 `brushy` 为空 → `cli.py:198` 回退系统字体，AC4 的"毛笔体"卖点与"TanukiMagic 独占"结论**只在 Owner 机器成立**（诚实口径：属"环境依赖"，建议登记或补一条 fetch+sha256 校验脚本）。
- `synth.py:45` `_BRUSHY_NAME_HINTS` 含 `"pen"`/`"hand"`/`"magic"` 等宽泛子串：`"pen" in "opensans"` 为真 ⇒ 一旦 `fonts/` 放入 OpenSans 类字体即被误判为毛笔体并**顶掉**真毛笔体优先级。

### 新-6（P3）lock 形状随写者漂移 + 一处 docstring 失真

- `cli.py:438-440`（`cmd_split`）的 lock 只有 `seed/method/pinned_groups/fingerprint/frozen_at`，**缺 `challenge_case_ids`**；`cli.py:386-393`（pipeline）有。交付态 `manifest.full.json` 由 `split(restore)` 最后写入（`subcommands-r2-run.log:8`）⇒ 报告 `:48-49` 描述的 lock 键集与盘上不一致。
- `cli.py:450-455`（`cmd_dedup`）回写透传旧 lock 却**不重算 fingerprint**：若本次真丢弃样本，lock 指纹将指向丢弃前的集合（此次 dropped=0 故未暴露）。
- `atomicio.py:109` docstring 称清理"tmp/bak"，实现 `:112` 只匹配 `*.tmp`（bak 保留是有意设计，docstring 应删"bak"）。

### 新-7（P3）`.gitignore` 二次变更未获追认

`.gitignore:15-16`（r2 新增）不在 r1 追认的"数据本体出 Git"最小必要范围内。规则本身合理（路径受限），但按协作纪律需集成方一并追认或改由 `experiments/**/.gitignore` 局部承担。

### 新-8（P3）交付文档的 r2 溯源缺口

- `handoff:7` `r2_head: 见交付记录 §r2`——§r2（`:101-140`）全段**没有出现任何 commit 哈希**；任务书 `doc/tasks/M2-SFX-DATA-INFRA.md` 零 r2 记录（`:12,55,56,58`）。r2_head=`2838d690` 仅存在于本次复核派单里，**交付物内不可溯源**。
- `doc/reviews/` 下无 `M2-SFX-DATA-INFRA-*-dsh-r1.md`（本 worktree 全仓 glob 无命中）：r1 报告未入库，r2 无法逐字核对 r1 原文（含"12 P2"与编号 P2-1..P2-13 共 13 条的计数口径差）。按惯例（STATUS 中"DSH 报告原字节入库"）应由集成方补入 r1+r2 报告。

### 新-9（P3）登记精度与鲁棒性小项

- `README.md:70-71` / `report:105-106` 登记 test 集为"4 个 ogkalu pseudo 无人工 GT"，但由 `manifest_summary.json:41`(11 空框) 与 `pipeline-run.log:6`(排除 10) 互算可知：**11 个空框负样本中恰有 1 个落在 test**（builder 先按 split 过滤、再判 negative，故 10≠11 自洽）。即 test 集 4 个样本里 1 个**连框都没有**，评估价值比登记所述更低——建议一并登记。
- `cli.py:296,351-352` `build_summary` 无条件对 `manifest.train.json` 取 sha：若在两次 `write_manifest` 之间中断（atomicio 允许的中间态）导致 train 缺失，`summary` 会以 `FileNotFoundError` 崩溃而非 typed/manifest 级错误。
- r2 的 8 个回归测试无 red 留证（`verification/M2-SFX-DATA-INFRA/` 只有 r1 的 `red-run.log`）；静态看这 8 个在 ecb39e67 上前置必然红（无 `pinned`/`exclude_negative` 参数、force 不重置、无 `.bak` 回退、perceptual 死代码），但纪律上缺 red→green 留痕。

### 新-10（P4，仅提示）

测试内重复局部 import（`test_synth_gt_roundtrip.py:90,109` 重复导入模块级已有符号）；`_image_ref` 返回的第二个元素（文件名）恒被丢弃（`importers.py:108,146`）。

---

# 3. verdict

**changes_requested** — r1 的 4×P1 与 11/13×P2 已实修（代码事实级可核，日志一致），但交付态存在 **1×P1（摘要/一致性声明与交付物不符 + 摘要覆写后退化、P1-2 与 AC4 证据出 Git）**、**P2-13 明确回潮（本机绝对路径入摘要）**、以及 7×P3（未用 import/死代码、字体可复现性、lock 形状漂移、.gitignore 二次越界、r2_head 不可溯源、test 集登记精度），需 Owner 返修 r3 后再进集成。

**给 Owner（ZCode）的可转发指令（r3 最小闭合清单）**：
1. 摘要归属定死：`cmd_summary` 不得静默降级 Git 摘要（或复算 `gt_roundtrip_max_err_px`/`train_builder`/`import_assets`/`dedup`，或另写 `--summary-out` 旁路）；重跑后把 `report:44-45` 与 `handoff:132` 的 sha 改为**重跑后实算值**，并删掉"与摘要一致"这类无法被交付物承载的措辞。
2. `cli.py:334` 字体改相对/基名（P2-13 真闭合）。
3. 清 `cli.py:194` `import os as _os`；`importers.py:212-215` 空分支删掉；`d["cls"]`→`det.get("cls")`。
4. 字体补可复现通道（fetch 脚本 + sha256 pin + 许可证据文本），并收窄 `_BRUSHY_NAME_HINTS`（至少去掉 `"pen"`）。
5. `cmd_split` 的 lock 补 `challenge_case_ids`；`cmd_dedup` 重算 fingerprint；`atomicio.py:109` docstring 去"bak"。
6. 文档：handoff frontmatter 填实际 `r2_head`/`r3_head`，Task 正文回填 r2 数字与交付链；`.gitignore:15-16` 请集成方追认；补登记"test 4 中 1 为空框负样本"与"8 个回归测试无 red 留证"。
7. 集成方（Codex 代行）：r1+r2 报告原字节入 `doc/reviews/`，并复算交付摘要与盘上 manifest 的 sha 一致后再 merge。
