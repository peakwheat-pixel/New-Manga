# M2-PROD-DETECT-2 r1 返修定点复审（DSH，非作者，review round 2）

## Verdict
**approved（可集成）** — R1-R12 全部实质闭合，无 P0/P1/P2 未闭合项；禁改面零回潮。附 6 项非阻塞缺陷（N1-N6，最高 P3）：N1 是新增告警文本的拼接 bug（表现层，不改变语义与 AC 判定）、N2/N4/N6 为文档/证据文本口径、N3 为断言面比 detect 链真实面少一个名字。N1/N3 涉及 `src/**` 与 spec，**建议随下一次必经重建（集成重建或 M2-IPC1 slice）一并落地**，避免为一行 print 触发 353s+516s+GATE+探针的独立整轮重跑。

## R1-R12 逐条复核表

| 项 | 状态 | 一句依据（file:line） |
|---|---|---|
| R1 warn 载体 | **closed** | `core_sidecar.spec:79-98` `_archive_warn_file` 在每个 `Analysis(...)` 返回后立即 copy（调用点 `:154`），**四份归档内容互异即证不是"末次覆盖"**：`warn-host_bridge.txt` 与 `warn-catalog_loader.txt` 同为 blob `fdcc4814`/29 行、`warn-core_service.txt` `aea793ed`/979 行、`warn-acceptance_bridge.txt` `1d622208`/979 行（若四份都在末尾 copy，四份都会等于无 ML 的 catalog_loader 文件）；`warn/CLASSIFICATION.md:12-24` 12 桶逐项加总 = 958 = 脚本自报总数，`:48` unclassified 空；软告警行号 `:41-44` 与 `raw/build-sidecar-console.log:119/157-158/160/163/257/294-295/297/300` 逐一对齐 |
| R2 AC5 口径 | **closed** | `doc/tasks/M2-PROD-DETECT-2.md:57` 判定改 PARTIAL + `:102` NOT_RUN 子项与后续 slice；`packaged-detect-probe-results.json:83` boundary_note；`release-notes.md:49,61` 结论收窄为"运行时+权重随包就绪 + 闭包外等价推理" |
| R3 hiddenimports/断言 | **closed** | `core_sidecar.spec:76` 显式 ML_HIDDENIMPORTS（仅 ML 入口传入，`:144`）+ `:101-118` `_assert_ml_closure` 校验 `analysis.pure`，**时机=core_service Analysis 之后、acceptance_bridge Analysis 之前**（`:155-156`，fail build 提前而非构建末尾）；日志实证 `raw/build-sidecar-console.log:413`；`raw/pyz-core-service-listing.txt:7913-7922` 含 `modeling_rt_detr` 与 rt_detr_v2；机制句更正见 `spec:35-45`/`Handoff:28`/`release-notes:16` |
| R4 doctr detect 断言 | **closed** | `packaged-detect-probe.py:37-48` L4(a) 明示"startup only"；`:490-551` 新增 L4(b) 闭包外 detect，断言 typed `ProviderNotConfigured`+`error_code`（场景 `:504/:542`）；`results:71-80` |
| R5 裸 ValueError | **closed** | `src/bootstrap/core_assembly.py:623-632` 删除 `raise`，改 stderr 一行警告 + 返回默认路径；`bundled_in_release` 参数与代码引用零残留（仅见于文档/注释文字）；`raw/l2-frozen-weights-absent.log:2-3` exit=0/ready；单测 `tests:186-206` 参数化两 backend |
| R6 语义分叉 | **closed** | 两 backend 共用同一 lookup（`core_assembly.py:798-818`），frozen 全缺同一形状：`raw/l2...log:6`（manga）与 `raw/l4-frozen-doctr-startup.log:6`（doctr，权重确实不在包内 `probe:494-508` 反证）；裁决追认 `Task:40,47`；`AC3` 措辞 `:55`；`build_sidecar.ps1:42-47` `-SkipWeights` 注释已按新语义改写 |
| R7 证据重绑定 | **closed** | 构建时 `HEAD=dbad2027a196e6d4ae933dc9401037809bd668f2`（`raw/build-sidecar-console.log:1` 与 `:417` 两处）；新 NSIS sha256 `ed401584…` 由 GATE CS-E2 绑定（`raw/cleanstart-runner-stdout.log:4`），460,175,852B÷1048576=438.86 MiB 与 `raw/tauri-build-console.log:60` 独立自洽；r1 证据归档**内容忠实**（`raw-r1/l2` 保留 `ValueError@core_assembly.py:623` traceback、`raw-r1/cleanstart:4,12` 保留 `6c765ed3…`/5,552、`raw-r1/tauri:286-292` 保留 1m08s/438.87 MiB、`raw-r1/l4-frozen-doctr-startup.log:5` 保留 r1"doctr 无警告"态）；**额外强佐证**：新 `raw/l2:6` 的乱码警告只能由当前 `core_assembly.py:624-632` 源码产生（见 N1）→ 产物确实含本返修代码 |
| R8 README | **closed** | `packaging/m2ac5/README.md:27-40`（ML 五行/裁决 2/体积/权重随包/mobi-pypdfium2）、`:96-102`（权重复制、`-WeightsSource`、`-SkipWeights` 新语义）、`:109-110`（体积口径指向 release-notes） |
| R9 requirements 注释 | **closed** | `requirements-build.txt:30-41` 改为"mobi 不进（lazy import）"+"pypdfium2 由 doctr 传递依赖带入、不手工 pin、风险登记" |
| R10 -WeightsSource | **closed** | `build_sidecar.ps1:35-41` 参数 + `:115`/`:152` 两条路径（增量短路与全量）均传参，注释明示 pin 不放宽 |
| R11 测试增强 | **closed** | `tests:303-320` env-only 装配级；`:244-262` stray 真实落盘（fake interpreter 于 tmp_path）；`:55-68` 反射收敛为 helper；计数 13 def + `:186` 参数化×2 = 14 collected，与 11→14 口径一致 |
| R12 命名/层数 | **closed** | `probe:483` 场景名改 `PK-L4-doctr-starts-without-assembly-error`；`results:5` scenario_count_note；`Task:88`/`Handoff:37` 明示 4 层 6 场景 |

静态自洽复核（第 4 项要求）：warn 四文件 + CLASSIFICATION 逐桶可数（12 桶合计 958 ✓，unclassified=0 ✓，979 行与 diff `@@ -0,0 +1,979 @@` 一致 ✓）；PYZ listing 含 rt_detr 11 条 ✓（含 `modeling_rt_detr`），transformers 2320 条 ✓（grep 报 "250 of 2320"）；探针 6 场景与 `raw/l1/l2/l3/l4-frozen-doctr-startup/l4-doctr-detect` 对齐 ✓（L2-recovery 无独立 raw 日志，见 NOT_VERIFIED#5）；NSIS sha256 在 GATE 日志绑定 ✓；构建 HEAD=dbad2027 日志实证 ✓。半成品合入（第 3 项）：装配段全分支覆盖（override/data-root/frozen-hit/frozen-miss/non-frozen），`bundled_in_release` 残留零，代码与 Task/Handoff/release-notes 叙述除 N2 所列两行外自洽。

## 回潮与新问题
**回潮：无。** 返修 diff 36 文件全落允许路径（`doc/tasks`、`doc/handoffs`、`packaging/m2ac5` 四件、`src/bootstrap/core_assembly.py`、`tests/**`、`verification/M2-PROD-DETECT-2/**`）；禁改面（`apps/**`、`tauri.conf.json`、`run_clean_start_e2e.py`、`ports/**`、两个 provider、`requirements.txt`、`experiments/**`）在 35 个 `+++ b/` 目标中零出现；`console=True` 未动（`core_sidecar.spec:168-173`，diff 中仅注释级引用）；无 deleted file；`verification/M2-AC5/**` 零出现。

- **N1 [P3]｜`src/bootstrap/core_assembly.py:624-632`｜新警告文本被隐式字符串拼接吞掉分隔符，实际输出是乱码。** `"...none exists: " " | ".join(probed)` 在解析上是 `("...none exists:  | ").join(probed)`（相邻字面量先拼接，trailer 再作用于整个原子），故真实 stderr = `<data_root 路径>WARNING: … none exists:  | <bundle 路径>; …`。实证：`raw/l2-frozen-weights-absent.log:6` 与 `raw/l4-frozen-doctr-startup.log:6` 两处同形状乱码（第一候选被顶到行首、冒号后双空格），而 `raw-r1/l2:10`（raise 版）是干净单行——**该乱码本身就是"产物含本返修源码"的指纹**。威慑：两个候选与 `PROVIDER_NOT_CONFIGURED` 指引仍在同一行，L2 门（`probe:370` 子串断言）与 `tests:202-206,:343` 也只做子串断言，故未被发现。修法：把分隔符括起来或先 `probed_str = " | ".join(probed)` 再插值；测试补一条"整行以 WARNING: 开头"的布局断言。不改语义与 AC，但改动在 exe 内，须随重建落地。
- **N2 [P3]｜`doc/tasks/M2-PROD-DETECT-2.md:56`（AC4 内嵌"实测"）与 `:57`（AC5 内嵌延迟）仍是 r1 期数字**（NSIS 460,184,382B / sha256 `6c765ed3…`、onedir 1,116,380,855B、稳态 299ms/页、冷启动 6,542ms），与同一文件测试表 `:87/:88`（460,175,852B / `ed401584…` / 1,116,381,295B / 288ms）及 `release-notes.md:41,57` 直接冲突——正是 r1 R8/R9 那一类"同一交付内两处口径"。另 `:53` 写归档路径 `build/warn/warn-<entry>.txt`，实际为 `pyinstaller-work/<spec>/warn-archive/` → 入库 `verification/M2-PROD-DETECT-2/warn/`。纯文本修正，可立即做。
- **N3 [P4]｜`core_sidecar.spec:76,106`｜断言面比 detect 链真实面少一个名字。** provider 解析的是 `transformers.RTDetrV2ForObjectDetection`（`detection_manga.py:291`），对应 `transformers.models.rt_detr_v2`；`ML_HIDDENIMPORTS`/`_assert_ml_closure` 只钉 `transformers` 与 `transformers.models.rt_detr`。该子树本次确在包内（`raw/pyz-core-service-listing.txt:7920-7922`）且 `classify_warn.py:53-56` 的 HARD_DEP_SUBTREES 已含它，但**构建期 fail-closed 保证少这一格**。建议下一次触碰 spec 时补入（本次日志也显示 rt_detr 的 hiddenimport 未产生独立 "Analyzing hidden import" 行，真实保险来自断言，故更应把三个名字补齐）。
- **N4 [P4]｜`build_sidecar.ps1:23`｜usage 注释未列 `-WeightsSource`**（参数本体 `:35-41` 与 README §2b 已写全）。
- **N5 [P4，表述]｜`release-notes.md:3`/`Handoff:32` 称 r1 证据为 `git mv`**，但所给 diff 中 10 个 `raw-r1/**` 全为 `new file mode`（全 diff 无 rename/相似度头），`raw/**` 为原地改写——归档是一份等价拷贝而非可观察的 rename。内容忠实（见 R7 行），r1 行号锚不失效，仅措辞需改（或下次用 `--find-renames` 出 diff）。
- **N6 [P3，证据载体]｜`release-notes.md:25`（配合 `Handoff:62`、`Task:85`）声称 NSIS 安装后三文件 `Get-FileHash` 实测、并"补齐 r1 NOT_VERIFIED#6"，但全 `verification/M2-PROD-DETECT-2/` 树内检索 `037930a8`/`b6d70793`/`7e9e2245` **只命中 release-notes 的叙述本身**，无任何 hash dump/transcript 文件。结论仍可传递成立（构建期脚本逐文件 pin 校验 + `raw/build-sidecar-console.log:416` "sha256 verified"，且 L3 以安装后包内权重跑通 provider 内部 pin 校验），但"显式 dump 已补"这一声称缺载体。二选一：把 `Get-FileHash` 记录入库，或把措辞降级为"由构建期校验 + L3 provider 内 pin 校验传递成立，未保留独立 dump"。

## NOT_VERIFIED（集成方复跑项）
1. **完整构建重跑**（PyInstaller 353s）：四条 `warn-archive:` + `closure assertion: … (8572 pure modules)`；`classify_warn.py` exit 0 与逐桶归桶只能执行复现（我已独立验证：硬依赖顶层零 missing、958 总数、12 桶加总一致）。
2. **onedir 1,116,381,295 B / 5,550 文件**：无 raw 载体（仅 release-notes/Handoff 叙述）；相对 r1 的 +440 B 无法对算（旧 onedir 已被覆盖）。
3. **NSIS 460,175,852 B（438.86 MiB 有 `raw/tauri-build-console.log:60` 佐证）与 sha256 `ed401584…`**：GATE CS-E2 已静态绑定，须复跑安装与 runner 核验；N6 的安装态 hash dump 缺载体。
4. **GATE 25/25**：我静态计数 25×`[PASS]` + `GATE: PASS` + 安装后 5,552 文件 + CS-E2 sha；runner 未改（diff 零出现）但需实跑。
5. **探针 6/6**：L3（EXIT=0/候选=2/稳态 288ms）与 L4(b)（typed `PROVIDER_NOT_CONFIGURED`）的 payload 只存在 **Owner 产出的 results JSON**，`raw/l3-inference.log`、`raw/l4-doctr-detect.log` 仅含 exit 码/pbar/空 stderr；**L2-recovery（warning_gone）无独立 raw 日志**，仅 results。
6. **pytest 401+1**：`raw/pytest-three-suites-tail.log` 仅 4 行汇总（"1 failed, 401 passed"），289/35/77 套件拆分与 14 个新测 PASS 无 raw 载体；既有环境性失败的 base 同源性需对 base 复现。
7. **cargo 44+1 ignored / vitest 31**：无 raw 产物（Handoff 自述"实测同上轮/本表"）。
8. **git 层**：`git diff --check f79203eb..1c0bc399` EXIT=0、禁改面专项 diff 为空、`git ls-files` 权重零命中、以及 **per-commit 边界**（dbad2027 代码 commit / 6b066a9e 证据 commit / tip 1c0bc399 hygiene；Task frontmatter `delivery_head=6b066a9e` 与 Handoff `delivery_head: dbad2027` 语义不同、均非分支 tip，集成时应以 `1c0bc399` 为准）——只能执行确认。
9. **frozen 进程内 ML import / detect**（AC5 NOT_RUN，结构性）：待 M2-IPC1 命令面扩展后另立验证。

## 推荐下一步
按 approved 接收并把复跑清单 1→5 走完；同时让 Owner（或集成 commit）把 N2/N4/N6 的文本与 N1 的一行 print 修正（附整行布局断言）随集成重建一并落地，N3 的 `rt_detr_v2` 断言留待下一次 spec 触碰。
