`approved_with_conditions`

---

## 一、评审方式声明

**未复跑任何命令。** 本 worktree 的 shell 通道被沙箱拒绝：每一次 `pwsh`（`git rev-parse HEAD`、`Write-Output` 探针等）均返回 `Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)`，因此 `python -m pytest tests/m2_test_assets -q`、`assets.py verify`、`fetch_bj.py fetch/render`、`git diff --name-status / status / check-ignore / diff --check` 全部未执行。以下结论来自静态核验 + 只读旁证。

**静态核验并已确认的内容**

1. 7 份 `verification/M2-TA2B/raw/*.log` 的头行（`shell/cwd/HEAD/date/cmd`）与 `# EXIT=` 尾行齐备（ac1 vol=EXIT=1、retry/2/4/5/7×2=EXIT=0）。
2. **证据时序自洽性**：从链接 worktree reflog（`G:/CODEX/New Manga/.git/worktrees/M2-TA2B-OPEN-ASSETS-zcode/logs/HEAD`）取得提交时间——`f1be5d2a`=2026-09-30T00:29:13Z、`704df9bc`=01:04:23Z、`4d0e9db8`=01:08:05Z。7 份日志 `date=` 均为**真 UTC**（与脚本自写的 `bj_download_manifest.json::downloaded_at_utc` 交叉印证：vol01 manifest 00:36:12Z vs ac1 头 00:35:46Z、vol05 manifest 00:40:06Z vs retry 头 00:40:04Z）。ac1/ac1-retry/ac2/ac4/ac7-verify/ac7-pytest 均落在 claim 与实现提交之间 → `HEAD=f1be5d2a` 正常；**不止 ac7，全部 7 份都是实现 commit 之前的工作区态**。唯一例外见 P3-1（ac5）。
3. **base 复现**：主仓库 `G:/CODEX/New Manga` 的 reflog 尾行即 `9db2dca8`（master tip == base），故主仓库工作区的 `cases.json`（4380 行）== base 版本。以此做了 base↔worktree 的逐值对比（见 AC6 行）。
4. **git index 只读检索**：`.git/worktrees/.../index` 中不存在任何含 `black_jack` 的路径，也不存在 `99_optional_openmantra` 路径（方法自校验：同一 index 能命中 `02_public_annotations`、`ac5-openmantra-...log`）。→ 素材像素未入库。
5. **实体文件**：`日漫_JA/01_black_jack_official/vol01|03|05` 的 ZIP/PDF/`bj_download_manifest.json`/`bj_pages_manifest.json`/各 4 张 PNG 均在盘；`99_optional_openmantra` 恰 13 个文件（annotation/LICENSE/README + 10 张 jpg）；三卷 `page_sha256` 与 cases.json 对应 case 的 `page_sha256` 逐值相同（已核对 BJ01 ff3365…、BJ07 cba84c…、BJ08 4e02cb…、BJ10 4bc8d4…）。
6. **图像目检复核（3/12 页）**：BJ07=`vol03_p0111` 确为近空白心电图纸页（tags=[]、`unlabeled_or_absent`，与 `feature_notes` 一致）；BJ06=`vol03_p0056` 确有电话铃声拟声词、竖排对白、夜间街景、多人对话、小字；BJ10=`vol05_p0061` 确有夜间救护车、框内时间旁白、警报 SFX、多人对话。作者「人工目检」自述可信。
7. **外部一手来源复核**：`densho810.com/free/` 官方利用规约逐条验证（商用非商用自由、署名「ブラックジャックによろしく　佐藤秀峰」且不可变更、FAQ 明确 © 非必需、JASRAC 为 **2 卷 p35/54/150/151/153、7 卷 p192、11 卷 p77**、Kindle 禁、电子书商店 ≥1 円、公开后 1 个月内邮件报告）——README/draft 的相关表述均准确。
8. **测试计数核对**：`test_catalog.py` 23 个测试函数（2 处 parametrize：2 + 4）→ 27 item；`test_public_assets.py` 12 个 → 合计 **39**，与 ac7 日志 `39 passed` 精确吻合。

**未复跑**：pytest、assets.py verify/list/missing、fetch_bj.py、git 全系命令（含 `git diff --name-status 9db2dca8..4d0e9db8`）、SHA256 原位重算（`read_image` 只给出规范化副本哈希，不能替代原文件哈希）。

---

## 二、问题清单（P0/P1/P2/P3）

### P0
无。JASRAC 纪律成立：仅选第 1/3/5 卷（官方 JASRAC 页位所属卷为 2/7/11），三卷 `bj_download_manifest.json::jasrac_volume=false`，`fetch_bj.py:403-405` 硬拒 2/7/11；manifest 与 Git 中无任何 JASRAC 卷素材。素材像素未入 Git（见上 §一.4/§一.5）。

### P1

**P1-1｜OpenMantra 许可登记与实际状态自相矛盾（NC 素材已落盘，却被 3 处登记为「未取得」）**
- `test_assets/comic_golden_suite/README.md:35`：仍写「0 个文件 … 因此未取得、未计入可运行覆盖。`MISSING`（条件候选）」。
- `test_assets/comic_golden_suite/manifests/local_asset_inventory.json:630-647`：`local_path` 仍为 `日漫_JA/05_openmantra_candidate`（该目录不存在），`status:"MISSING"`、`file_count:0`、`notes:"…no data copied"`。
- `test_assets/comic_golden_suite/manifests/cases.json:207`：同一对象内 `image_redistribution_status` 仍写 "Non-commercial only; **not acquired**…"，而同对象 208-213 行已写 `local_path: 日漫_JA/99_optional_openmantra`、`local_file_count: 13`、`status: READY_OPTIONAL_ISOLATED`。
- 问题：AC5 的唯一价值是「如实登记 + 严格隔离」。技术控制面完好（`optional_noncommercial_baseline_excluded:true`、无 case 引用该目录、`日漫_JA/.gitignore:27` 忽略、`test_catalog.py:94-108` 断言），但**人类可读的许可登记（README 资产表 + checksum inventory）宣称 NC 素材不存在**，而 13 个 CC BY-NC 文件确实在盘上。审计者/后续 Agent 会得出相反结论。
- 建议闭合：同一分支补一个 doc/data commit——README:35 表行改为 `READY_OPTIONAL_ISOLATED`（13 文件 / 2,341,834 B，写入 99_optional_openmantra，禁止进入生产基线/smoke/regression/full/Git）；`local_asset_inventory.json:630-647` 更新 path 与计数（或加显式 `"inventory_tracking":"excluded_optional_noncommercial"` 并同步 file_count）；`cases.json:207` 改写为与 210 行一致的「已获取至 gitignored 隔离目录、非商业基线」表述。

### P2

**P2-1｜BJ01–BJ12 的资产完整性不在任何自动校验路径内，且 `asset_status` 与 CLI 计算语义冲突**
- `cases.json` BJ01-BJ12（如 `:4465`、`:4470`、`:4491-4493`）声明 `asset_status:"READY"`、`asset_profile.kind:"manual_source_page"`。
- `tools/assets.py:162-163`：`manual_source_page` **恒返回 PARTIAL**（`test_catalog.py:367-372` 明确断言「never report ready」）；`tools/assets.py:900-922` 的 verify 循环对 `manual_source_page` 不做任何校验，且 `local_asset_inventory.json` **不含 BJ 文件**（README:42 自述有意如此）。→ 12 张 PNG 即使全部丢失/损坏，`verify` 仍 EXIT=0，CI 全绿；AC2/AC3 的核心产物只有日志与 `bj_pages_manifest.json`（gitignored，不入库）作为证据。
- 建议闭合：任选其一并留证据——(a) 把 BJ 页面纳入 `local_asset_inventory.json`（逐文件 sha256），或 (b) 在 `fetch_bj.py` 增 `verify` 子命令（对照 cases.json `page_sha256` 重算）并在 verification 日志留 EXIT；同时把 BJ 的 `asset_status` 改为与 CLI 口径一致的值或删除该快照字段，避免「清单说 READY、工具说 PARTIAL」。

**P2-2｜source 级登记陈旧且不完整：与 inventory/README 表直接矛盾，且新来源缺登记**
- `cases.json:189-190`（`peppercarrot_japanese_localized_pages`：`local_file_count:12` / `byte_size:40284868`）与 `:225-228`（`peppercarrot_korean_localized_pages`：`local_file_count:4`/`local_image_file_count:3`/`byte_size:16292579`）**与 base 完全相同**，未随 AC4 更新；`cases.json:338-339`（`sources.peppercarrot.ja_local_page_count:10` / `ko_local_page_count:3`）同样陈旧。而 inventory 现为 ja ep04=9 文件/8 图、ko ep04=9/8、ko ep20=8/7，README:28-29 自己也写 15/15 张。
- 另：`benchmark_sources` 中**没有** KO ep20 族条目，也**没有** densho810/BJ 来源条目（而 `license_class`、署名、再分发状态、本地计数目前只存在于 case 级字段）——套件既有的 11 个来源都有该条目，`test_catalog.py:132-146` 也建立在「来源登记完整」的假设上。
- 建议闭合：更新上述计数（ja: 15 图/17 文件、ko: 15 图/17 文件，byte_size 按 inventory 求和）；为 `peppercarrot_korean_localized_pages_ep20` 与 `black_jack_official_free`（densho810）各加一条 `benchmark_sources`（license_class=`commercial_use_permitted_attribution`、attribution 串、`image_redistribution_status`、`checksum_inventory`、本地计数），必要处补断言。

**P2-3｜12 个新 KO case 的溯源页 URL 用 `/ko/`，与实际韩语页 `/kr/` 及既有同类不一致**
- `cases.json:5505,5555,5605,5655,5705,5755,5805,5855,5905,5955,6005,6055` 的 `"source"`/`"source_url"` 溯源页为 `https://www.peppercarrot.com/ko/webcomic/...`，而既有 `K11–K13`（`:4271,4324,4377`）与 `local_asset_inventory.json:651` 用 `/kr/`。
- 实测（HTTP 200）该 `/ko/` 页返回「**Oops! There is no translation available yet for this episode**」并回退英文页；语言列表中韩语（한글）对应的是 `/kr/`。下载/校验不受影响（真实下载走 `/0_sources/...`，已过 host 白名单；`transcript_member` 用 `lang/kr/` 正确），但 12 处许可溯源链接指向非韩语桩页。
- 建议闭合：统一改为 `/kr/`（与 K11–K13、inventory 一致）。

**P2-4｜新增网络工具 `tools/fetch_bj.py`（412 行）零测试覆盖**
- `tests/m2_test_assets/` 两个文件中没有任何 `fetch_bj` 引用（已 grep 全仓 `*.py`）。其安全边界——host/path 白名单（`fetch_bj.py:61-71`）、重定向守卫（`:74-81`）、Content-Length 上限与流式超限（`:122-137`）、原子发布 `.part→` 硬链接（`:146-156`）、`__MACOSX`/AppleDouble 跳过（`:173-176`）、JASRAC 卷拒收（`:403-405`）——全部只靠一次人工运行日志背书。对比 `assets.py` 同族能力有 `test_public_assets.py:157-180` 的正/反例断言。
- 建议闭合：补 4–6 个离线单测（monkeypatch `urlopen`）：跨 host 重定向必须拒绝且不发布、`Content-Length` 缺失/超 600MB 拒绝、非 ZIP 载荷不发布、`__MACOSX/._x.pdf` 与真 PDF 共存时命中唯一成员、`--volumes 2/7/11` 返回 2、失败后无 `.part` 残留。

**P2-5｜AC6「既有字段零变化」与 AC8「diff 仅允许路径」缺少归档证据**
- `verification/M2-TA2B/raw/` 只有 7 份日志，**没有** AC6 的程序化对比产物，也**没有** AC8 的 `git status`/`git diff --check`/`git diff --name-status` 日志；Task 测试表（`doc/tasks/M2-TA2B.md:114,117`）的「证据」一栏分别只写测试函数名与「git 输出」。对照 `verification/M2-TA2C-TOOLING-GAPS/raw/07-ac5-diff-check-and-scope-proof.log`，本仓已有此惯例。
- 影响：这两条恰恰是最需要**可复核**的两条（"零变化"与"禁改路径零命中"），目前只能靠 reviewer 侧旁证（我做的 base↔worktree 静态对比与 index 检索）。禁改路径（`src/**`、`apps/**`、`packaging/**`）零命中**无法从交付物确认**。
- 建议闭合：补 `verification/M2-TA2B/raw/ac6-zero-change-diff.log`（base↔HEAD 的 cases.json 逐字段对比输出）与 `ac8-scope-proof.log`（`git status --short`、`git diff --name-status 9db2dca8..HEAD`、`git check-ignore -v` 三条，EXIT 行齐备）。

**P2-6｜AC2 特性矩阵缺「横排对白」，且测试只锁定 11 个 tag 子集**
- 12 个 BJ case 的 tags 并集 = {huge_text, vertical_text, complex_background, rotated_text, normal_dialogue, multi_speaker, narration, low_contrast, dense_dialogue, tiny_text, fragmented_sfx}，**无 `horizontal_text`**（全仓 `horizontal_text` 仅出现在既有 J41/J47 一类的 P&C case，`:4169,4224`）。AC2 明确要求覆盖「竖排/横排对白」，`curved_text`/`overlapping_text`/`unusual_balloon`/`extreme_size` 亦缺。`test_catalog.py:72-77` 的断言集合刻意不含 `horizontal_text`。
- 可闭合方式（择一，需 Codex 作为 AC owner 认可）：BJ04 的 `feature_notes`（`cases.json:4699`）本就写「vertical title + **horizontal small labels**」，若目检属实即补 `horizontal_text` tag（并同步断言集合）；或由 Codex 明确把横排覆盖划归既有 P&C case 并在 Task/README 写明豁免。

### P3

- **P3-1｜日志可复现性小瑕**：`ac1-fetch-bj-volumes.log:1` 的 `cmd=` 为 `… fetch_bj.py fetch`，缺 `--volumes 1 3 5`（Task 表 `:109` 写的是带参形式；语义等价，因 `DEFAULT_VOLUMES=(1,3,5)`，`fetch_bj.py:400`），而 ac2 同族头行带参——建议统一记录真实命令行。`ac5-openmantra-optional-download.log:1` 的 `cmd=` 是**手写散文**而非命令行，且其 `date=…01:05:00Z` 落在实现 commit `704df9bc`(=01:04:23Z) 之后 37 s 却仍记 `HEAD=f1be5d2a`；AC5 目前无法被他人一键复现（无入库脚本）。
- **P3-2｜日志份数自述不符**：`doc/tasks/M2-TA2B.md:128` 写「5 份 verification 日志」、`doc/handoffs/M2-TA2B-704df9b.md:29` 写「6 份命令日志」，实际 `raw/` 为 **7** 份。
- **P3-3｜README 数值错误**：`README.md:29` 写 KO 侧「3 个官方 SVG language-pack ZIP」，inventory 全表仅 4 个 zip（ja ep04/ep20 + ko ep04/ep20 → KO 为 **2** 个）；`:28` 的 JA「2 个」正确。
- **P3-4｜署名字串与官方规定格式有偏差**：官方要求逐作品明示「ブラックジャックによろしく　佐藤秀峰」（FAQ 明确「© をつける必要はありません」，且该两项内容不可变更）。本套件统一串为 `ブラックジャックによろしく © 佐藤秀峰（densho810.com 经由、二次利用フリー）`（`cases.json` 12 处、README:73、`fetch_bj.py:54`、两份 vol manifest），其中「经由」为简体中文。建议以规定格式原样为主串，来源/许可说明另列，降低"变更署名内容"的解释风险。
- **P3-5｜`fetch_bj.py` 输入校验与死代码**：`fetch_bj.py:252-253` 的 `raise ValueError` 不在 `:255` 的 try 内，`--volumes 0`/负数/`>999` 会以未捕获 traceback 退出而非干净 CLI 错误；`:298-303` `sample_page_indices` 中 `picks` 恒 ≤4 元素，`picks[:count] if len(picks) > count else picks` 分支为死代码。
- **P3-6｜取消语义只落在标注层**：37 个 Manga109 case 仍保留 `levels:["regression","full"]`（如 `cases.json:1558-1561`），`removed_from_scope_2026-09-30` 不参与 `selected()`，故 `verify --level full` 永远计 37 个 `MISSING_GATED_ASSET`；`levels.smoke.notes`（`:37`）未随取消更新；`generated_at` 仍为 `2026-09-29`（`:5`）而文件实际改于 09-30。若「保留历史定义」即最终语义，建议在 README/Task 一句话显式声明「取消 = 仅标注、不参与可运行计数、不改变 levels」。
- **P3-7｜边界未说明**：`coo_and_manga109_dialog`（source=`github.com/manga109/public-annotations`，本机 76 文件、`PARTIAL`）同样与 Manga109 相关却未打取消标注，README:12 只列了三个 source，未说明该条为何豁免（推测因其为已取得的 CC BY 4.0 标注资产）——补一句即闭合。
- **P3-8（信息性）**：渲染产物 2946×4167 @ `dpi=150` 意味着源 PDF 页面框≈1414×2000 pt（≈19.6×27.8 in），"DPI 150" 是相对页面框的渲染比例而非扫描密度；不影响 AC2 判据，仅提示体积/性能口径。
- **P3-9（越界，非本次改动）**：`assets.py:643` 的 `download_webtoon_case` 用裸 `urlopen`，未像 `download_public_file` 那样校验重定向后的 host（`:561`）。属既有代码，建议另立任务，不计入本次交付。

---

## 三、AC1–AC8 逐项裁定

| AC | 裁定 | 判据（入库日志/实体文件，非 commit 自述） |
|---|---|---|
| AC1 下载与完整性 | **PASS** | `ac1-fetch-bj-volumes.log`（vol01/03 OK、vol05 `__MACOSX/._005bj.pdf` 致 expected-one-PDF 失败、EXIT=1）+ `ac1-fetch-bj-vol05-retry.log`（`reused`、EXIT=0）；盘上 `vol01/03/05` ZIP+PDF+`bj_download_manifest.json` 齐备，ZIP sha256/字节数与 Task/Handoff 声明一致（343,497,422/338,764,008/386,575,185），PDF 209/221/243 页且 `drm_checked:true`；manifest `downloaded_at_utc` 与日志时间互证；`fetch_bj.py:403-405` 拒 2/7/11。小瑕 P3-1。 |
| AC2 PDF/Page 转换 | **PASS（覆盖有缺口 → P2-6）** | `ac2-render-bj-pages.log` EXIT=0、12 页 DPI150 2946×4167、卷内 `duplicates=0`；`bj_pages_manifest.json` 逐页 sha256 与 cases.json `page_sha256` 逐值相同（已核 BJ01/BJ07/BJ08/BJ10）；每卷 4 个 case 页（≥3 满足）；目检抽查 3 页与 `feature_notes` 相符；但无 `horizontal_text` 等标签，AC 括号内「横排对白」未由新 case 覆盖。 |
| AC3 去重与登记 | **PASS** | cases.json BJ01–BJ12（`:4428-5251`）逐项具备 `language=ja`、tags、`license_class=commercial_use_permitted_attribution`、`source_url=https://densho810.com/free/`（白名单内）、`attribution`、`page_sha256`、`volume`、`pdf_page_number`、`page_file`、`render_dpi`；README:70-76 署名字节与许可义务四要素齐全（已对照官方规约逐条验证）；`densho810-report-draft.txt:5` 明确「Agent は送信しない／ユーザーが送付」→ 发送动作留给用户，符合禁止项。小瑕 P3-4。 |
| AC4 Pepper&Carrot 补充 | **PASS** | `ac4-download-pc-additions.log` EXIT=0（`downloaded=18 existing=16 failures=0`，逐 case 行自洽：17 新页 + 1 ep20 zip）；J48–J52/K14–K25 的 `source_id` 无重复且与 inventory 的 8/8/7 页集合完全对应（ja E04 新增 P00/P01/P04/P07/P08；ko E04 新增 P00/P01/P04/P06/P08；ko E20 新增 P01–P07）；盘上文件存在；`ac7-verify` 的 `INVENTORY checked=110 missing=0 failures=0` 反证 18 个新条目哈希与盘上一致。缺陷见 P2-2/P2-3/P3-3。 |
| AC5 OpenMantra 隔离 | **PASS（登记不一致 → P1-1）** | `ac5-…log` 13 文件/2,341,834 B 与盘上 13 个文件、`cases.json:198-230` 完全一致；`optional_noncommercial_baseline_excluded:true`；无任何 case 引用该目录（`local_path` 全表已核）；`日漫_JA/.gitignore:27` 忽略；index 中无该路径 → 未入 Git；且未计入 smoke/regression/full。技术隔离成立，但 README/inventory/同对象 `image_redistribution_status` 三处仍称「未取得」→ P1-1；无入库脚本 → P3-1。 |
| AC6 Manga109 取消落地 | **PASS（证据缺档 → P2-5）** | 逐值计数确认 37 个 `asset_type=manga109_title` 全部带 `removed_from_scope_2026-09-30:true`（1587…3747，步长 60 恰为「块 +1 行」），3 个 source（74/106/147）亦带；base↔worktree 静态对比：68 个既有 case 的 `local_path` 序列逐值相同，J38 与 K11 块与 base **逐行逐值一致**（48/53 行全等），J01–J37 每块仅 +1 行（flag）而 J38–J47/K11–K13 步长不变，未发现其他既有字段被改动的迹象；`test_catalog.py:80-91` 断言存在。未见 AC6 的程序化 diff 归档。 |
| AC7 测试接入与回归 | **PASS** | `ac7-pytest-m2-test-assets.log` `39 passed` EXIT=0，且 39 与交付测试文件可精确复算（catalog 27 item + public_assets 12）；`ac7-verify-ja-ko-full.log` ja `MISSING_GATED_ASSET=37 PARTIAL=12 READY=15` EXIT=0、ko `MISSING=8 READY=25` EXIT=0，`INVENTORY checked=110 missing=0 failures=0`、`BENCHMARK_INVENTORY checked=4 failures=0`；`SOURCE_URL_HOSTS` 已含 `densho810.com`（`assets.py:43`）且有 lookalike/http/非常规端口反例断言（`test_catalog.py:173-187`）。缺 `fetch_bj.py` 测试（P2-4）、无 `git diff --check` 归档（P2-5）、`list` 未留证据。 |
| AC8 范围纪律 | **PASS（素材零入库）／NOT_RUN（diff 路径边界）** | 零入库：`日漫_JA/.gitignore:26-27` 显式忽略 `01_black_jack_official/`、`99_optional_openmantra/`，`韩漫_KO/.gitignore:1` `/*` 覆盖新 ep20；git index 无 `black_jack`/`99_optional_openmantra` 路径；素材仅存在于 gitignored 目录。diff 边界（仅允许路径、`src/**`、`apps/**`、`packaging/**` 零命中）：沙箱禁止 git + 无归档日志 → **NOT_RUN**，须由 Codex 用 `git diff --name-status 9db2dca8..4d0e9db8` 复核。 |

---

## 四、结论与推荐下一步

实现质量整体扎实：安全边界设计（host/path 正则白名单 + 重定向守卫 + Content-Length 上限 + `.part→final` 硬链接原子发布 + `__MACOSX` 跳过 + 失败清理 + JASRAC 卷硬拒）经代码级核验成立，我未发现可利用的绕过路径；许可事实（含 JASRAC 页位、Kindle 禁、≥1 円、1 个月报告）已用官方一手页面逐条复核，README 与邮件草稿表述准确，报告邮件发送动作明确留给用户；素材确实零入库、JASRAC 卷零涉及、12 张页面哈希链与 base 既有字段均可用只读证据闭合。问题集中在**登记/证据一致性**，不是实现方向错误。

**建议下一步（交 Codex / ZCode）**

1. 请 ZCode 在同一分支补一个 `fix(M2-TA2B)` 小 commit 闭合 **P1-1**（README:35 + `local_asset_inventory.json:630-647` + `cases.json:207` 三处 OpenMantra 状态同步）与 **P2-2/P2-3**（source 级计数与来源条目、KO 溯源 URL 统一 `/kr/`）；**P2-6** 由 Codex 裁决「补 `horizontal_text` tag」或「书面豁免并说明横排由 P&C case 承担」。
2. **P2-1/P2-4** 建议一并处理（BJ 页面纳入可校验路径或新增 `fetch_bj.py verify`；补离线单测 4–6 个），否则 AC2/AC3 的核心产物将持续处于「CI 全绿但无校验」状态。
3. **P2-5** 由 Codex 在集成阶段补齐归档证据：`ac6-zero-change-diff.log`、`ac8-scope-proof.log`，并**必须**执行 `git diff --name-status 9db2dca8..4d0e9db8` 确认禁改路径零命中、素材零入库（这是我作为静态 Reviewer 唯一无法覆盖的门槛）。
4. 复评范围可限定为上述闭合项 + Codex 的 git 范围证据；无需全量重审。
5. 推荐指令（可直接转发）：在 worktree `G:/CODEX/New Manga.worktrees/M2-TA2B-OPEN-ASSETS-zcode`（分支 `agent/zcode/M2-TA2B-OPEN-ASSETS`，HEAD `4d0e9db8`）按 REVIEW 意见处理 P1-1、P2-1…P2-6 与 P3-1…P3-3：更新 OpenMantra 三处登记、source 级计数与新增 source 条目、KO 溯源 URL 改 `/kr/`、BJ 校验路径与 `fetch_bj.py` 单测、补 AC6/AC8 归档日志；不得发送 densho810 报告邮件（用户待办），不得让素材像素入 Git，不得改 `src/**`、`apps/**`、`packaging/**`；完成后回填 Handoff 供 Codex 集成验证。
