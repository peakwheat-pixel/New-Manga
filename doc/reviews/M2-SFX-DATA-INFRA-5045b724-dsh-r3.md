证据收集完成。以下是 r3 终审复核结论。

---

## 取证基线与限制（请先读）

本轮 **pwsh 完全不可用**：沙箱在初始化 workspace-write 时 ACL 授予失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)`），重试 3 次均同错；按沙箱升级路径申请 `danger-full-access` 时返回「requires approval, but no approval channel is available」。因此**本轮无法独立复跑 pytest / pipeline / 复算 sha256**，改用**只读静态取证 + 交付产物交叉核对**。可核对项已全部核对，结论如下；数字型声明凡我无法复算者，标注为「未复算」。

已完成的**独立**交叉核对（非引用 Owner 自述）：

| 核对项 | 方法 | 结果 |
|---|---|---|
| HEAD | `.git/refs/heads/agent/zcode/M2-SFX-DATA-INFRA` | `5045b7240099c40aae4b04169ee9a4aff5cd2cea` ✓ |
| r3 提交链 | `.git/worktrees/.../logs/HEAD` reflog | `2838d690 → 89872c03 → (amend) 5045b724` |
| 37 tests | `grep '^def test_'` 计数（5+12+6+7+2+5） | **37** ✓ |
| 拆分数 | `manifest.full.json` 内 `"split": "train"` 匹配数 | **63** ✓（pipeline-run.log 同值） |
| 负样本数 | `"negative": true` 匹配数 | **11** ✓；`original_classes: []` 亦 **11** ✓ |
| 遮挡落地 | `"occluded": true` 匹配数 | **8** ✓（P1-4） |
| 合成样本 | `annotation_status: synthetic` × 24，全部 `group: synthetic/poc` | ✓ |
| train manifest 隔离 | `manifest.train.json` = `sample_count 61`，`"split": "test"/"challenge"` **0**、`"negative": true` **0** | ✓（AC2/AC3 产物层成立） |
| lock 形状 | `manifest.full.json:13882-13890` 键集 = seed/method/pinned_groups/fingerprint/frozen_at/challenge_single_bucket | ✓ 与 pipeline/split 写者一致 |
| 单次跑签名 | `lock.frozen_at` == `summary.generated_at` == `2026-10-04T03:38:17Z` | ✓ 证明 pipeline 后**无子命令回写**官方树（cmd_dedup/cmd_split 会刷新 frozen_at） |
| 摘要↔lock | `split_lock.fingerprint` == lock `fingerprint` == `de3787c6…` | ✓ |
| sha256 a48d616e/e0d2981a | 需 shell 复算 | **未复算**（见下） |

---

## 1. r2 问题逐条核对表

| 编号 | 结论 | 证据 |
|---|---|---|
| **新-1(P1) 摘要覆写降级 + sha 自引证** | **部分** | **修到的**：`cmd_summary` 确已从盘重算——`cli.py:493` 调 `step_dedup`、`:494` 调 `step_build_train`、`:497-500` 重算 import 计数；r2 污染根因在新旧日志中同时留证：`subcommands-r2-run.log:2,12` 摘要两次写 `experiments\M2-SFX-DATA-INFRA\manifest_summary.json`（Git 内），`subcommands-r3-run.log:4` 改成 `%TEMP%\summary.bypass.json` ✓。**未修到**：① `cmd_summary` 仍产出**降级摘要**——只传 `{"imported": N}`（`cli.py:497-500`），而 `build_summary` 的 `import_assets` 含 `boxes`/`assets_copied`（`cli.py:321-328`，pipeline 侧实测 182/47，见 `pipeline-run.log:2`），子命令路径下这两键**丢失**；`synthetic_poc.gt_roundtrip_max_err_px` 变 `null`（`cli.py:496` 只传 synth_count）；`summary` 子命令默认输出仍是 Git 内文件（`cli.py:541`）且无任何护栏 → 降级覆写隐患由代码降级为「仅靠流程纪律」。② `smoke` 只断言 `imported==58`（`test_cli_pipeline_smoke.py:66-68`），**未覆盖**上述三字段。③ 自引证措辞**未删除**：`data-infra-report.md:28-29`「（与 manifest_summary.json 逐字节核对一致）」、`handoff:170`「逐字节核对一致」，与 `handoff:153` 自称「删除自引证措辞」自相矛盾——该 sha 由同一次 pipeline 经 `fsha`（`cli.py:300-304`）写入摘要，报告再引摘要值＝循环引证。④ 报告头版 AC 表仍以 r1 值为现行证据：`:14` fingerprint `a02fed3d…`、`:16` GT err `2.27e-13`；`handoff:88`「数据 Hash」仍为 r1 期 `095a3c59…`/`17129854…`（无轮次标注，最终值为 `a48d616e…`/`e0d2981a…`）。 |
| **新-2(P2-13) 字体绝对路径** | **通过** | `cli.py:337` `Path(...).name`；`manifest_summary.json:55-57` = `["TanukiMagic.ttf"]`，无分隔符；`test_cli_pipeline_smoke.py:70-71` 断言无 `\`/`/` ✓ |
| **新-3(P3) `import os as _os`** | **通过** | 全包 `grep '_os'` 0 命中；`importers.py:15` 用 `os`，`:72-73` 真消费（`os.environ`/`os.pathsep`）✓ |
| **新-4(P3) importers 空 pass + `det.get('cls')`** | **通过** | 全包空 `pass` 仅剩 `atomicio.py:118`（`OSError` 处理器，合法）；`importers.py:210` `det.get("cls")` ✓。微瑕：`:233` `d.get("cls","")` 可注入空串（本批数据未出现，见 `manifest.full.json:1546-1554`） |
| **新-5(P3) 字体可复现** | **部分** | **通过项**：`fetch_fonts.py` 存在，zip sha pin fail-closed（`:56-61`）；`_BRUSHY_NAME_HINTS=("tanuki","brush","fude","kouzan")`（`synth.py:46`），pen/hand/magic 已去且注释说明了误命中原因 ✓。**不通过项**：① 声明「LICENSE-NOTE.txt 落字体目录」**不成立**——`glob training_data/sfx-v1/fonts/*` 仅返回 `TanukiMagic.ttf`，LICENSE-NOTE.txt 不存在（而 `handoff:157`、`report:33` 均声称已落）。② 「zip+**ttf** 双 sha256 pin 校验」**夸大**：`FONT_SHA256`（`fetch_fonts.py:25`）只在「已存在」快路径（`:45`）被查；**下载安装路径 `:62-64` 从不校验解出的 TTF**，直接把 `zip.extract` 结果 `copy2` 落位。③ 全仓无 `fetch-fonts` 执行日志、报告/日志未记录该字体 sha 校验 → 在盘 `TanukiMagic.ttf` 与 pin 的关系**从未被验证**，新-5 想关的「可复现性」实为「代码通道存在但未走通」。④ LICENSE-NOTE 正文仅断言 OFL，无许可全文/URL。 |
| **新-6(P3) lock 形状漂移** | **通过** | 三写者键集实测一致：pipeline `cli.py:389-396`、split `cli.py:441-445`、dedup 透传 `cli.py:456-466`；盘上 `manifest.full.json:13882-13890` 键集相符；`cmd_dedup` 真丢弃时以 kept 集重算（`:459`）；`cleanup_stale_tmp` docstring 明示 `.bak` **不**清理（`atomicio.py:109`）且 glob 模式只含 `.tmp`（`:112`）✓。残留见 §2 新-5/新-6。 |
| **新-7(P3) `.gitignore *.bak`** | **部分** | 修复本身正确且已收窄到 `experiments/M2-SFX-DATA-INFRA/*.bak`（`.gitignore:16`），不再是裸 `*.bak` ✓。但 `.gitignore` **仍在本 Task 允许修改范围之外**（合同允许范围＝`experiments/M2-SFX-DATA-INFRA/**`、`verification/...`、Task/Handoff），这是继承认 P2-1 之后的第 2 处越界，仍需集成方追认——属**集成 Gate 前置条件**，未闭合。 |
| **新-8(P3) 溯源** | **部分** | `r2_head: 2838d690` ✓ 已填。但 **`r3_head: 89872c03` ≠ 实际 tip `5045b724`**（`handoff:8` vs `.git/refs/.../M2-SFX-DATA-INFRA`；reflog 证明 89872c03 已被 `--amend` 重写为 5045b724）——handoff 自称「当前 tip」，且 §5.1 的 recovery point 就是这组 hash，指向一个**不在分支上的悬空对象**。评审任务书称「r3_head=5045b724 已填」与文件实际内容不符。另：Task 仍 `status: ready` / `delivery_head ecb39e67` / `base_commit: 74fa71e9`（handoff 作 `4c12e8af`），Task 正文与 r1/r2 报告入 `doc/reviews/`（`glob doc/reviews/M2-SFX-DATA-INFRA*` 无命中）——**均已登记**为集成收口执行，本轮不作缺陷计。 |
| **新-9(P3) 登记 + red 替代 + build_summary 容错** | **通过（附证据质量 P3）** | ① `build_summary` 中间态容错已落地：`cli.py:300-304` 返回 `{"sha256": None, "bytes": None, "note": "not_written_yet"}`；② 「test 4 中 1 空框」登记（`report:42`）经我独立复算成立：负样本共 11 个（`manifest.full.json` 11 处 `negative: true`），builder 排除 10 个（`manifest_summary.json:87-98`），challenge 7 个全为 l3 `partial` 不含 ogkalu → 第 11 个必在 test（test 恰 4 样本）✓；③ red 替代证明 `red-evidence-r2-tests.log` 存在，但只有裸 `0` 计数、无命令行与原始输出，属**断言而非证据**（P3，见 §2 新-7）。 |

---

## 2. 新引入问题

无 P0、无 P1。r3 增量未破坏任何 AC 级事实（82 样本 / 7-63-8-4 / fingerprint `de3787c6…` / lock 六键 / 负样本与 test-challenge 隔离，均经产物独立核对成立）。

| 编号 | 级别 | 问题 | 位置 |
|---|---|---|---|
| 新-1 | **P2** | `summary` 子命令仍产降级摘要：`import_assets.boxes`、`import_assets.assets_copied` 丢失，`gt_roundtrip_max_err_px→null`；默认 `--summary-out` 仍指向 Git 内 `manifest_summary.json` 且无护栏；测试未覆盖这三字段。（未修正的 r2 新-1 残项） | `cli.py:483-511,541,321-328`；`test_cli_pipeline_smoke.py:65-68` |
| 新-2 | **P2** | 「已删除自引证措辞」与实际不符：报告/handoff 仍以「与 manifest_summary.json 逐字节核对一致」承载 sha 可信度（循环引证）；报告 AC 表与 handoff 附录仍以 r1 旧值（`a02fed3d`/`2.27e-13`/`095a3c59`/`17129854`）充当现行证据 | `data-infra-report.md:14,16,28-29`；`handoff:88,153,170` |
| 新-3 | **P2** | 新-5 的「LICENSE-NOTE.txt 已落」为虚假声明（目录仅 `TanukiMagic.ttf`）；`FONT_SHA256` 在安装路径从不校验，实际在盘字体 sha 未被任何证据验证；无 fetch-fonts 执行留证 | `fetch_fonts.py:25,45,62-64`；`training_data/sfx-v1/fonts/`；`handoff:157`；`report:32-33` |
| 新-4 | **P3** | handoff frontmatter `r3_head` 指向 amend 前的悬空 commit，recovery point 不可解析 | `handoff:8` vs refs/reflog |
| 新-5 | **P3** | 冻结常量双份真源：`cli.CHALLENGE_IDS` 与 `splits.CHALLENGE_CASE_IDS` 各自定义同一 challenge 清单，存在漂移位 | `cli.py:58`；`splits.py:32` |
| 新-6 | **P3** | 新-6 的「真丢弃时重算 fingerprint」无有效回归：smoke 的 dedup 丢弃数为 0（断言恒真、不可区分重算与不重算）；`test_dedup` 只直调 `drop_duplicates`，不经 `cmd_dedup` | `test_cli_pipeline_smoke.py:75-79`；`test_dedup.py:76-77`；`pipeline-run.log:5` |
| 新-7 | **P3** | `red-evidence-r2-tests.log` 只记裸 `0`，无命令/原始输出，作为 red 证据不可复现 | `verification/.../red-evidence-r2-tests.log:4-15` |
| 新-8 | **P3** | 面向操作者的 README 未提 `fetch_fonts.py`/`fetch-fonts`（仍只写手工放字体），可复现通道未入门文档 | `README.md:36-39`；`cli.py:543-545` |
| 新-9 | **P3** | `subcommands-r3-run.log:12`「bypass assertions OK」无驱动脚本入库，断言内容不可核 | `verification/.../subcommands-r3-run.log:12` |

**未复算声明**：`manifest_summary.json:107,111` 的 `a48d616e…`/`e0d2981a…` 与 `bytes 253363/216280`、以及 `FONT_SHA256`/`FONT_ZIP_SHA256` 的 pin 值，本轮因沙箱不可用**未能独立复算**；我仅验证了其**内部一致性**（摘要值 == 报告/handoff r3 节引用值；`frozen_at==generated_at` 排除事后回写）。这一项需集成方在可执行环境补一次 `sha256sum` 独立取证。

---

## 3. Verdict

**approved_with_conditions** — 交付实质（AC1-AC6 与全部产物级事实）经独立静态核对成立，无 P0/P1；但存在 1 个 P2 代码残项、2 个 P2 虚假/循环声明与 1 个失效 recovery point，须在集成收口时闭环。

**集成前须闭合的最小条件**（均廉价）：
- **C1**（Owner，代码）：`cmd_summary` 补齐 `import_assets.boxes`/`assets_copied` 重算，或让 `summary` 拒绝覆写已有更丰富摘要 / 默认输出改非受控路径；smoke 增补对应断言。
- **C2**（Owner，文档）：删除「与 manifest_summary.json 逐字节核对一致」自引证表述；把报告 AC 表与 handoff 附录的 r1 旧值改为最终值或显式标注「r1 历史」。
- **C3**（Owner）：执行 `fetch-fonts` 生成 LICENSE-NOTE.txt 并记录字体 sha 校验，或在安装路径补 `sha256_file(dst) == FONT_SHA256` 断言；否则撤回该声明。
- **C4**（Owner）：handoff frontmatter `r3_head` 改为集成时实际 tip。
- **C5**（集成方）：`.gitignore:16` 追认；另请补一次独立 `sha256sum` 取证（本会话沙箱不可用）。

**推荐下一步**：把本报告与 C1-C5 转给 **Codex（集成方）**——先由 ZCode Owner 落 C1-C4 一个返修 commit（仅 `experiments/M2-SFX-DATA-INFRA/**`、`verification/M2-SFX-DATA-INFRA/**`、Handoff），再由 Codex 执行 `merge + doc/reviews/ 入库 + Task/STATUS/PLAN 收口` 并同步追认 C5；随后按 Plan 释放 T1b（批量数据生产：竖排 + 真实底图 + 字体源），T1b 起手前必须先关闭 C1。
