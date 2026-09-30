## 审阅结论

**verdict: approved_with_conditions**

核验方式声明（先说限制，再下结论）：本会话**无法执行任何命令**——沙箱在启动前即失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\M2-TA3-A-E2E-SMOKE-zcode)`），提权到 `danger-full-access` 被拒（"no approval channel is available"）。因此 `git diff / git check-ignore / pytest 复跑 / 任意文件 sha256` **均未执行**，以下全部是静态核验 + 日志一致性复核，并用主仓库 checkout（仍处 base，`tests/m2_test_assets/test_catalog.py:45` 为原始断言）做**独立对照**。凡我无法独立复算的项，均在下文显式标注，不做臆测。

---

### 复核结论（对照 6 个核对点）

| 核对点 | 结论 | 独立证据 |
|---|---|---|
| 1. 只调生产 seam、无 planner 重实现、diff 无 src/apps/packaging | 成立（含残余风险） | `experiments/M2-TA3-A/run_smoke.py:278-283,331-336,402-424` 只调 `application/tasks/service.py:213/272/733` 的 `create_run/plan_run/execute_run`；detect 前插是生产逻辑 `service.py:346-358`；`PipelineScope` 字符串强转 `domain/tasks/models.py:166-168`。base 与 worktree 对 `service.py`（1083 行、7 处行号锚点全同）、`core_assembly.py`（903 行、detector 分支逐字同）、`inpaint_routes.py`（13 处匹配同）逐一相同 |
| 2. 数字一致性 | 基本成立，**1 处不符** | region 33/57/15/7/24、run2 33/40/15/7/24（BJ06 `truncated:true`）、export 大小 8736076/8771537/20408981/5984018/3036455 在 `raw/ac1-smoke-all-cases.log`、`summaries/smoke-report.json`、5 份 case 摘要三处一致；**K11 wall_s：摘要/报告 100.76 vs Task/Handoff 表 113.0**（且 5.15+95.54 已排除 113.0） |
| 3. 回填严格限 5 case；test_catalog 仅一条断言 | **完全成立** | 独立证明见下 |
| 4. 冲突记录处置的最小性与理由 | 成立（2 处表述瑕疵） | base `test_catalog.py` 465 行、worktree 476 行（净 +11 = ac4 的 12+/1-）；base:30-45 与 worktree:30-44 逐行相同，base:48→wt:59、base:458→wt:469、base:465→wt:476 全为 +11 位移 ⇒ 单一连续 hunk；理由（AC 要求回填但快照断言锁全 NOT_RUN）与 Task §冲突记录一致。授权本身按要求不审 |
| 5. 像素零入库 | 成立 | `verification/M2-TA3-A/artifacts/.gitignore:3` `*.png`；ac5 提交清单 20 项无 PNG；盘上 5 份 PNG 仅为工作区文件 |
| 6. AC2 provider 边界 | 成立 | `run_smoke.py:96,494-500`、Task §AC2、`summaries/smoke-report.json:6-12` 全部标注 mock；`mock_local.py:38-39` 定义 `MOCK-OCR-SOURCE-TEXT`/`MOCK-TRANSLATED-TEXT`；inpaint 为生产 `inpaint-simple-fill`（`ports/inpaint/ports.py:26`、`infrastructure/providers/inpaint_routes.py:144-147`）；L-5 明确把排版质量推给 TA3-B |

**核对点 3 的独立证明（不依赖作者日志）**：主仓库 base `cases.json` 与 worktree `cases.json` **都是 6155 行**；base 全文件 `"PASS"` 出现 **0 次**，worktree **恰好 33 次**，且全部落在 K01(443-453)/K02(521-531)/K11(4340-4342)/BJ02(4572-4581)/BJ06(4854-4863) 的 `pipeline_status` 块内；`FAIL/BLOCKED_*` 两份文件均为同 5 处且都在 `benchmark_sources.status`（58/79/133/258/316），无一处是 `pipeline_status` 值。⇒ 回填 diff 严格等于「5 case × executed 键 = 33 个 NOT_RUN→PASS」，无结构/格式漂移（ac4 的 8 类计数之和 33 亦吻合，K01/K02 无 `manga_page_render` 键、K11 仅 3 键可解释 40→33）。

**唯一一次像素级复算**：`read_image` 对盘上 `K11-translated.png` 返回 **sha256 = c451815727ec24b64bfd7656fd7fe574879de4d9dc1d79013456f89cee22b7a2、3036455 bytes、1200×1660**，与 `summaries/smoke-K11.json:530-531` 及 Task 第 67 行逐位一致。BJ02/BJ06 因超尺寸被工具**降采样重编码为 webp**（返回 783216/842448 B，而盘上为 8.7 MB），其返回值**不是源 PNG 哈希**，故不能用于比对——这是工具限制，**不是哈希不符**，K01/K02 同理无法复算。

---

### 问题清单

**P1-1 证据链未锚定交付版本；artifact-samples 的原始输入已不可再生**
- 位置：`verification/M2-TA3-A/raw/{ac2,ac3,ac4,ac5}*.log:3`（均 `HEAD=b94ebe87…`）、`ac1-smoke-all-cases.log:3`（`HEAD=1328a766… claim`，并注明 run_smoke.py 当时为 untracked）；`experiments/M2-TA3-A/probe_artifacts.py:11-17` 硬编码 5 个临时目录。
- 事实：交付 head 为 `dc2b9aca`，但没有任何 raw 日志指向该 commit（Task 第 127 行称 319a3036 仅"日志头对齐交付 head 重生成"，实际头部仍是 b94ebe87，与其自述不符）；日志未记录 `run_smoke.py` 的哈希，"被提交的脚本 == 产出证据的脚本"只能靠作者声明；`C:/Users/49745/AppData/Local/Temp/m2-ta3a-*/library.sqlite` 已被清理（定向 glob 返回 No files found），`artifact-samples.json`（OCR/译文/inpaint/render 身份的唯一来源）无法再生成或第三方复算。
- 影响：AC4「证据」的可审计性被削弱；若 JSON 被质疑，盘上无任何可比对物。AC 本身仍成立（step 计数可与摘要 `run2.per_region` 条数互证：BJ02 34=1+33、BJ06 41=1+40、K01 16=1+15、K02 8=1+7、K11 25=1+24；mock 身份另有 `mock_local.py:38-39` 代码佐证）。
- 建议：不改代码的前提下，追加一份 `verification/M2-TA3-A/raw/00-provenance.txt`，记录 `HEAD=dc2b9aca`、`sha256(run_smoke.py/probe_artifacts.py)`、5 份 summary 与 5 份 PNG 的 sha256 清单（PNG 哈希已在摘要中，可直接引用），并在 Task §遗留 登记「scratch db 为临时目录、probe 不可复跑」；下一轮把 scratch 根指到 `verification/M2-TA3-A/` 下 gitignored 目录。

**P2-1 K11 wall_s 在交付文档中失真（113.0 vs 100.76）**
- 位置：`doc/tasks/M2-TA3-A.md:64`（K11 行 wall_s=113.0）、`doc/handoffs/M2-TA3-A-1328a76.md:33`（同）。
- 事实：`summaries/smoke-K11.json:9,541-542` = started 03:36:55 / finished 03:38:36 / wall_s 100.76；`smoke-report.json:62` = 100.76；run1 5.15 + run2 95.54（`smoke-K11.json:38,47`）亦排除 113.0。其余 4 case 的 wall_s 全对（668.61/820.64/1041.61/137.32）。
- 影响：Task 自身结果总表与它引用的摘要不一致，"数字一致性"核对点因此不能整表通过；集成方若以表格为准会记录错误耗时。
- 建议：把 Task/Handoff 两处 K11 wall_s 改为 100.76，并在 Task 注明该值以 `summaries/smoke-K11.json` 为准（纯文档改动，不需重跑）。

**P2-2 AC2 表述"整页链"与真实执行范围不符，易被误读为 Run1 覆盖全部 region**
- 位置：`doc/tasks/M2-TA3-A.md:49,60-64`（"整页 9 步链…一段式执行"、"Run1 整页链"）。
- 事实：生产 `application/tasks/service.py:939-942` 明确「多 Region 页面的 pipeline steps 仍只对第一个 Region（reading_order 1）执行，扇出是后续调度切片」；`artifact-samples.json` 的 step 计数也证明 Run1 只产生 1 份 region 级步骤（ocr 总数 = 1 + run2 次数）。Run2 才是逐 region 覆盖。
- 影响：证据本身无误（Run2 逐 region 覆盖 + 累计 render 后导出），但"整页链"的措辞会让集成方高估 Run1 的覆盖面。
- 建议：在该句后补一句「Run1 的 region 级步骤按生产 backfill 语义作用于 primary region，其余 region 由 Run2 逐个覆盖；cap 40 见 L-4」。

**P3-1 断言数与事实差 2：应为 92，不是 94**
- 位置：`doc/tasks/M2-TA3-A.md:82`、`doc/handoffs/M2-TA3-A-1328a76.md:44`。
- 事实：`tests/m2_test_assets/test_catalog.py:33` 锁 97 case，抽走 5 个 TA3-A case 后为 **92**。处置的实质（其余 case 仍强制全 NOT_RUN）由我独立验证成立，仅数字错。
- 建议：94 → 92（这两处 + Task §冲突记录结语）。

**P3-2 新断言的判别力在 5 个 TA3-A case 上弱于原快照**
- 位置：`tests/m2_test_assets/test_catalog.py:52-56`。
- 事实：`set(pipeline_status)==set(expected_pipeline)`（第 54 行）已被 `tools/assets.py:88-91` 的 schema 强制（键集相等 + 值域 5 值）；因此第 56 行 `passed <= set(expected_pipeline)` 在该等式之后恒真（死断言）；且新写法放任 5 case 的**非 PASS 值**取 FAIL/其它，原快照是精确全 NOT_RUN。92 case 的 fail-closed（第 48-51 行）确实完好。
- 影响：轻度降低"锁定交付状态"的能力（未来若某 TA3-A 段变 FAIL，测试仍绿），非 AC 回归。
- 建议：对 5 case 改为显式字面快照（如 `EXPECTED_TA3A = {"BJ02": {...}, ...}` 后 `assert case["pipeline_status"] == EXPECTED_TA3A[case_id]`），保留 92 case 的现有 fail-closed；两条断言均可写入 §冲突记录 的同一 hunk。

**P3-3 其他登记/表述瑕疵（不阻断）**
- `run_smoke.py:273` 遗留注释 `(real detect; ocr hits the known gap)` 与本轮结论（缺口未复现，`L-1`）矛盾，易误导后续读者。
- `run_smoke.py:489-502` 的 `report["generated_at_utc"]` 实为**运行开始**时间（02:52:27Z = BJ02 `started_at_utc`），而最后 case 结束于 03:38:36Z；字段语义误导（我初次比对即被判为异常）。建议改名 `run_started_at_utc` 或同时记录 `report_written_at_utc`。
- `run_smoke.py:464` 的 `--keep-scratch` 是 no-op（`tempfile.mkdtemp` 从不清理，无删除分支），而 `probe_artifacts.py` 正依赖这些目录；`probe_artifacts.py:26-29` 的 `LIMIT SAMPLES_PER_STEP*4` 再切 `[:SAMPLES_PER_STEP]` 为无效放大。
- L-2 登记不全：`README.md` 的失实句不止第 7 行——`test_assets/comic_golden_suite/README.md:7`、`26`、`27`、`28`、`29` 均仍写「应用 Pipeline `NOT_RUN`」。建议把 L-2 扩为「README:7,26-29」。
- 产物观感如实性：K11/BJ02/BJ06 的导出图内为**白色占位框 + 虚线行**（未见 `MOCK-TRANSLATED-TEXT` 字形），与 L-5 的 offscreen Qt 字体告警一致；建议在 Task 明确一句「导出图为真实 PNG，文字排版为占位/缺字形渲染，可读性属 TA3-B」，避免"真实产物"被读成"译文可见"。

---

### 未复核项（供集成方按需补足）
`git diff --name-status bebcfcde..HEAD`（仅能引用 `raw/ac5-scope-proof.log` 的自报清单 + 我抽样的 3 个生产文件比对）；`git check-ignore`；`pytest ... = 82 passed`（`raw/ac3-pytest-regression.log` 的 72+10 点计数自洽，但未复跑）；K01/K02/BJ02/BJ06 盘上 PNG 的 sha256（工具降采样，无法复算）；cases.json 未抽样区域的逐字节比对（已用总行数 + PASS/FAIL 全量计数覆盖）。

---

### 可直接转发的下一步指令

**@ZCode（同一分支，仅文档/证据头，禁止触碰 src/**、apps/**、packaging/**，不必重跑 46 分钟 smoke）**
1. `doc/tasks/M2-TA3-A.md`：第 64 行 K11 `wall_s` 113.0 → **100.76**（与 `verification/M2-TA3-A/summaries/smoke-K11.json` 一致）；§冲突记录与结语中的「94 case」→ **92 case**；§AC2 第 49 行补「Run1 region 级步骤按生产 backfill 语义作用于 primary region，其余 region 由 Run2 逐个覆盖」；§遗留 L-2 扩为「README:7,26-29 失实」；新增遗留条目「scratch db 为 `%TEMP%` 临时目录、`probe_artifacts.py` 已不可复跑」。
2. `doc/handoffs/M2-TA3-A-1328a76.md`：第 33 行 K11 `wall_s` 113.0 → 100.76；第 44 行「94 case」→ 92 case。
3. 新增 `verification/M2-TA3-A/raw/00-provenance.txt`：记录 `HEAD=dc2b9aca`、`base=bebcfcde`、`run_smoke.py`/`probe_artifacts.py`/`backfill_pipeline_status.py` 的 sha256、5 份 `smoke-*.json` 与 `artifact-samples.json`/`smoke-report.json` 的 sha256、5 份 PNG 的 sha256（可直接从摘要复抄，K11 已由本 Review 复算确认）。**不要**改动已入库的 5 份 raw 日志正文（保留原始捕获），provenance 用新文件承载。
4. （可选、建议）`tests/m2_test_assets/test_catalog.py:52-56` 改为 5 case 的显式字面快照；仍只动这一个 hunk，并在 §冲突记录 补一行说明。
5. 完成后回 `dc2b9aca` 之后的**新 head**，把 amend 轨迹与「本次仅 doc/verification 改动、cases.json 与代码零变化」写进 Task §交付与运行记录。

**@Codex（集成）**：待上述 amend 落地后，只需核对 `git diff dc2b9aca..新head --name-status` **只含 doc/** 与 `verification/M2-TA3-A/raw/00-provenance.txt`（我因沙箱限制无法代跑），确认非 doc 零 delta 即可把本 Task 转 `done` 并置 `integration_commit`；其余 5 核对点已由本 Review 独立确认，无需重跑 E2E。TA3-B（20-case 质量 qualification）维持 `proposed/暂缓`，待检测器与真实 OCR/翻译 Provider 稳定后另行释放。
