---
id: M2-TA2B
title: Manga109 Authorized Import
kind: dataset_import
status: done
approval: pending_official_manga109_access
suggested_owner: ZCode
owner: null
reviewer: DeepSeek Harness
depends_on: [M2-TA1]
base_commit: null
branch: null
worktree: null
integration_commit: fae0d8f6f4e2009595993c284f1c3f436c2f12f8
---

# M2-TA2B：Manga109 Authorized Import

## 状态与启动门

`BLOCKED_BY_ASSET_ACCESS`，本 Task 已登记但**未 release、不得在未满足门槛时开工**。启动条件是本机存在用户依法取得的 Manga109-v2026 官方归档，且归档来源/版本可核验；不要求用户把 gated 凭据交给 Agent。

## 目标

正式满足启动门后，使用项目已有 Manga109 安全 importer 向 `test_assets/comic_golden_suite/日漫_JA/` 导入选定官方图像，从既有代表作品池固定约 80–120 个 Golden Pages。覆盖 normal/dense/tiny、vertical/horizontal/rotated/curved、fragmented SFX、overlap、complex background、low contrast、narration、multi-speaker、unusual balloon、action 和 screentone。`READY` 只表示图像、标注和完整性检查通过。

## 禁止项与前置条件

- 不绕过 gated access；不使用非官方镜像或盗版站。
- 不把 Manga109 原图或归档提交 Git；仅在本地 ignored assets 保存。
- 不因 annotation public/CC BY 推导原图许可；不把全部 21k+ 页面加入普通回归。
- 真实授权归档取得前只维护本 Task 和范围计划；实际下载/导入、Golden Page 确认和执行态必须保持 `BLOCKED_BY_ASSET_ACCESS` / `NOT_RUN`。
- Task 必须由 Codex 在授权条件满足后重新登记 base、branch、worktree 和 allowed paths，再转为 `ready`。

---

# 方案变更存档（2026-09-30 用户裁决，本文件历史部分至此保留为证据）

> 2026-09-30 用户裁决：**永久取消 Manga109 / Manga109-s 前置**（不再等待人工申请），改为无需申请、可脚本自动下载的开放素材池。上述 Manga109 方案整体归档为历史证据；现行方案见新 Task 文件（重写版，如下）。`BLOCKED_BY_ASSET_ACCESS` 解除。

---
id: M2-TA2B
title: "JA/KO 开放素材池（用户方案变更 2026-09-30）：ブラックジャックによろしく官方免费全卷 + Pepper&Carrot 补充；永久取消 Manga109 前置"
kind: asset
status: done
approval: user_ruling_2026-09-30
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者静态：r1 approved_with_conditions → r2 approved）
depends_on: []
base_commit: 9db2dca892e7fe1db5bf89c0a35501df014e653e
branch: agent/zcode/M2-TA2B-OPEN-ASSETS
worktree: G:/CODEX/New Manga.worktrees/M2-TA2B-OPEN-ASSETS-zcode
integration_commit: null
---

# M2-TA2B（重写版）：开放素材池（自动下载、校验、manifest、case 接入）

## 来源与目标（用户裁决 2026-09-30）

- **永久取消** Manga109 / Manga109-s 前置，不再等待人工申请；解除 `BLOCKED_BY_ASSET_ACCESS`。
- 改为**无需申请、可脚本自动下载的开放素材池**，自动完成：下载、完整性检查、SHA256、去重、许可登记、manifest、PDF/Page 转换、case 选取与测试接入。
- 主素材：官方《ブラックジャックによろしく》日文版。补充：Pepper&Carrot 日语/可用韩语素材。
- OpenMantra：隔离 optional benchmark（CC BY-NC）；**不作生产许可基线**。
- 素材特性需覆盖：真实黑白日漫、RTL 分页、竖排/横排对白、气泡、拟声词、复杂背景、小字/大字，支撑检测/OCR/inpaint/翻译/嵌字/分页与长条 E2E 的测试需求。
- 能自动处理的不得要求人工操作。

## 事实核查（2026-09-30，编排会话 WebSearch+WebFetch 实证）

- **主素材渠道成立**：`https://densho810.com/free/`（電書バト，有限会社佐藤漫画制作所=作者佐藤秀峰的公司运营）提供**全 13 卷**《ブラックジャックによろしく》日语版+英语版 ZIP（内含无 DRM PDF）**直链免费下载**（如 `dl/001bj.zip`），无需注册/付费。
- **许可**（作者授权声明）：商用/非商用自由、无需事先许可、允许翻译与二次创作；**署名义务**：须标明作品名《ブラックジャックによろしく》与作者名"佐藤秀峰"；**事后报告义务**：公开利用后 1 个月内邮件报告 info@densho810.com；禁止 Kindle 上架；第 2/7/11 卷部分页面含 JASRAC 管理乐曲（选取时避开或登记）。
- 原作者官网 mangaonweb.com 已下线（域名停放）——電書バト为现行官方分发渠道。

## 许可义务登记（合规边界）

- **用户待办（外部发送，Agent 不代发）**：素材公开用于测试后 1 个月内由用户向 info@densho810.com 发报告邮件（形式不限）。Task 交付物须生成报告草稿文本供用户发送。
- 署名落地：manifest 每个 BJ case 与 suite README 携带"ブラックジャックによろしく © 佐藤秀峰（電書バト densho810.com 经由、二次利用フリー）"。
- 版权像素**不入 Git**（同 KO 惯例）：下载/转换产物全部在 gitignored 目录，Git 只入 manifest、SHA256、许可文本与报告草稿。

## Acceptance Criteria

- [x] AC1（下载与完整性）：脚本化下载 BJ 日语版至少 3 卷（第 1 卷必选；避开第 2/7/11 卷 JASRAC 卷或选取时登记），逐文件 SHA256 记录；ZIP→PDF 校验（页数>0、无 DRM 解码成功）。
- [x] AC2（PDF/Page 转换）：用 pypdfium2（生产既有依赖）将所选卷渲染为页面图像（PNG，DPI≥150），选取覆盖特性矩阵的 case 页（黑白、RTL、竖排/横排对白、气泡、SFX、复杂背景、小字/大字），每卷至少 3 个 case 页；产物入 gitignored 目录并在 manifest 登记路径+SHA256。
- [x] AC3（去重与登记）：页面级去重（哈希）；cases.json 新增 BJ case（case_id `BJ01`..，language=ja、特性 tags、license_class=commercial_use_permitted_attribution、source_url=densho810.com/free/、署名字段）；suite README 署名与许可义务小节；**用户报告邮件草稿** `verification/M2-TA2B/densho810-report-draft.txt`。
- [x] AC4（Pepper&Carrot 补充）：下载 ja/kr 可用补充页（ep04/ep20 语言包内未入库页），同流程登记（若无可补页则如实记录）。
- [x] AC5（OpenMantra optional 隔离）：尝试脚本获取 OpenMantra 公开仓库素材至 `test_assets/comic_golden_suite/日漫_JA/99_optional_openmantra/`（gitignored），manifest 标注 `optional_noncommercial_baseline_excluded: true`；获取失败则如实记 BLOCKED-OPTIONAL（不阻塞 Task）。
- [x] AC6（Manga109 取消落地）：cases.json 中 37 个 Manga109 case 与 Manga109/JMangaBench/TextMask 相关 source 标注 `removed_from_scope_2026-09-30`（保留历史定义）；tests 相应断言更新；README 资产表更新。
- [x] AC7（测试接入与回归）：`tests/m2_test_assets` 更新（BJ case 注册、Manga109 取消断言、白名单 host 增加 densho810.com）全绿；`assets.py verify/list` EXIT=0；`git diff --check` EXIT=0。
- [x] AC8（范围纪律）：素材产物零入库（gitignored）；diff 仅触及允许路径。

## 允许修改范围

- `test_assets/comic_golden_suite/manifests/cases.json`（新 case/标注/取消标注）
- `test_assets/comic_golden_suite/README.md`、`test_assets/comic_golden_suite/tools/assets.py`（白名单+新下载入口函数）
- `tests/m2_test_assets/**`、`.gitignore`（新增素材产物 ignore 规则）
- `verification/M2-TA2B/**`、本 Task、Handoff

## 禁止范围

- 素材像素/文件入 Git；删除或改写既有 KO/JA 素材与既有 case 字段值（取消标注除外）
- `src/**`、`apps/**`、`packaging/**`
- 向外部发送任何内容（densho810 报告邮件=用户待办）
- 生产许可基线引入 NC 素材（OpenMantra 隔离）

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 下载 | `python test_assets/comic_golden_suite/tools/fetch_bj.py fetch --volumes 1 3 5` | 网络 | PASS：vol01/03/05 ZIP=343,497,422 / 338,764,008 / 386,575,185 bytes，PDF 页数 209/221/243，逐文件 SHA256 入 `bj_download_manifest.json`；vol05 首次因 `__MACOSX/._005bj.pdf` 成员报 expected-one-PDF 失败，修复（跳过 macOS 元数据成员）后复用已下载 ZIP 重跑 EXIT=0 | `verification/M2-TA2B/raw/ac1-fetch-bj-volumes.log`、`ac1-fetch-bj-vol05-retry.log` |
| AC2 转换 | `python test_assets/comic_golden_suite/tools/fetch_bj.py render --volumes 1 3 5` | pypdfium2==5.13.0 + Pillow | PASS：12 页 PNG（DPI 150，2946x4167），卷内去重 0，页级 SHA256 入 `bj_pages_manifest.json`；12 页全部人工目检并按 taxonomy 标注 tags | `verification/M2-TA2B/raw/ac2-render-bj-pages.log` |
| AC3 manifest | cases.json 更新 + `assets.py verify` | — | PASS：BJ01–BJ12 注册（ja、RTL、署名字段、license_class、页 SHA256）；README 署名/许可小节；邮件草稿已生成（用户待发送） | `test_assets/comic_golden_suite/manifests/cases.json`、`verification/M2-TA2B/densho810-report-draft.txt` |
| AC4 P&C | `assets.py download --level full --case-id J48..K25` | 网络 | PASS：17 个新页（ja E04×5、kr E04×5、kr E20×7）+1 个 ep20 kr ZIP 下载成功 failures=0；inventory 更新后 checked=110 missing=0 failures=0 | `verification/M2-TA2B/raw/ac4-download-pc-additions.log`、`ac7-verify-ja-ko-full.log` |
| AC5 OpenMantra | curl raw.githubusercontent.com（mantra-inc/open-mantra-dataset） | 网络 | PASS（OPTIONAL 隔离）：annotation.json + LICENSE.md + README.md + 10 张样本页（5 部作品 × 2 页，2,341,834 bytes）入 gitignored `99_optional_openmantra/`；source 标注 `optional_noncommercial_baseline_excluded: true`、`READY_OPTIONAL_ISOLATED` | `verification/M2-TA2B/raw/ac5-openmantra-optional-download.log` |
| AC6 取消 | cases.json 标注 | — | PASS：37 个 Manga109 case + 3 个 source 带 `removed_from_scope_2026-09-30: true`；与 HEAD 程序化对比确认无其他字段值变化 | `tests/m2_test_assets/test_catalog.py::test_manga109_scope_is_cancelled_by_user_ruling_2026_09_30` |
| AC6/AC7 测试 | `python -m pytest tests/m2_test_assets -q` | 标准 pytest | PASS：39 passed，EXIT=0 | `verification/M2-TA2B/raw/ac7-pytest-m2-test-assets.log` |
| AC7 verify | `assets.py verify --language ja|ko --level full` | 本地素材 | PASS：ja SUMMARY MISSING_GATED_ASSET=37 PARTIAL=12 READY=15 EXIT=0；ko SUMMARY MISSING=8（既有 O01–O08 未取得） READY=25 EXIT=0 | `verification/M2-TA2B/raw/ac7-verify-ja-ko-full.log` |
| AC8 范围 | `git status` / `git diff --check` | — | PASS：素材目录被 `.gitignore` 显式规则忽略（`日漫_JA/01_black_jack_official/`、`99_optional_openmantra/`）；diff 仅触及允许路径；EXIT=0 | git status 输出 |

## 依赖、风险与阻塞

- 风险 1：BJ ZIP 体积大（高分辨率）——逐卷下载、抽样 3 卷而非全量；全量 13 卷登记为可选扩展（不阻塞）。【实现后确认：3 卷共约 1 GiB，预算内】
- 风险 2：densho810 直链形态或限速变化——脚本带重试与 User-Agent；失败则如实 BLOCKED 并报告（不换非官方源）。【实现后确认：直链 `dl/00Nbj.zip` 形态稳定；vol05 ZIP 含 `__MACOSX/._005bj.pdf` 元数据成员，脚本已按安全规则跳过】
- 风险 3：PDF 页提取方向/RTL 语义——转换脚本保序记录页码，RTL 断言由 case tags 登记。【实现后确认：12 页人工目检，RTL+竖排成立】
- 阻塞：无。

## 交付与运行记录

- 2026-09-30 ZCode 实现：claim `f1be5d2a`（base=9db2dca8）、实现 `704df9bc`。交付物：`tools/fetch_bj.py`、BJ01–BJ12 + J48–J52 + K14–K25 case、`removed_from_scope_2026-09-30` 标注、README 署名/许可小节、邮件草稿、7 份 verification 日志、OpenMantra 隔离条目。素材本体（BJ ZIP/PDF/PNG、P&C 新页、OpenMantra 样本）全部 gitignored 未入库。遗留：densho810 报告邮件=用户待办（草稿已备）；BJ 全 13 卷与 OpenMantra 全量页为可选扩展（未纳入）；vol05 ZIP 含 macOS `__MACOSX` 成员已由脚本跳过；worktree 缺失的 gitignored 既有素材已从主仓库只读复制（KO webtoon 845MB、P&C 既有页）用于 verify。
- Handoff：`doc/handoffs/M2-TA2B-704df9b.md`。实际测试：见上表与 `verification/M2-TA2B/raw/`。
- 2026-09-30 DeepSeek Harness 静态 Review r1（被审 tip `4d0e9db8`）：**`approved_with_conditions`**——P0=0、P1×1（OpenMantra 三处登记与实际状态矛盾）、P2×6（BJ 校验路径缺失/来源计数陈旧/KO URL /ko/、fetch_bj 零测试/AC6+AC8 归档缺失/horizontal_text 覆盖缺口）、P3×9。DSH 以官方一手页面逐条复核了 densho810 许可事实（含 JASRAC 页位 2 卷 p35/54/150/151/153、7 卷 p192、11 卷 p77），确认署名/报告/Kindle 禁令表述准确、报告邮件发送动作留给用户。
- 2026-09-30 ZCode 返修 commit `118b4df3`（amend 自 `a93a61f3`，仅修 ac6 日志尾随空格与元数据，轨迹如实披露）：闭合 P1-1（README/inventory/cases.json 三处 OpenMantra 登记同步，inventory 加 `inventory_tracking: excluded_optional_noncommercial_checksums`）、P2-1（`fetch_bj.py verify` 子命令对照 cases.json `page_sha256` 重算 12/12 OK + README 登记为绿色门槛）、P2-2（ja/ko source 计数 15 图/17 文件 + byte_size 按 inventory 求和 + 新增 `black_jack_official_free` benchmark_source 18 文件/2,251,373,940 B）、P2-3（K14–K25 溯源 URL 12 处 /ko/→/kr/）、P2-4（新增 `test_fetch_bj.py` 离线单测，最终 8 个：跨 host 重定向拒（r2 N-3 补 RedirectGuard 直接驱动判别用例）/Content-Length 缺失与超限拒（r2 N-3 强化：缩小上限使仅 size-cap 守卫可拒绝）/非 ZIP 不发布/原子发布/__MACOSX 跳过/JASRAC 拒收）、P2-5（`ac6-zero-change-diff.log` 零变化证明 + `ac8-scope-proof.log` 范围审计：diff 仅允许路径、禁改路径零命中、素材 check-ignore 生效、diff --check EXIT=0）、P2-6（BJ04 补 `horizontal_text`，编排侧目检确认「GIVE MY REGARDS TO BLACK JACK」横排标签与横排副题；断言集合同步）、P3-3/P3-4/P3-5/P3-6/P3-7 落字（KO ZIP 3→2、官方署名格式「ブラックジャックによろしく　佐藤秀峰」+attribution_note 另列、fetch --volumes 校验进 try + 死分支删除、README 取消语义与 COO 豁免说明）、P3-1（`ac5b-openmantra-verification.log` 13 文件 SHA-256 复验补齐可复现证据）。P3-2 计数勘误（7 份）。P3-8/P3-9 信息性/越界不处理（P3-9 登记候选任务）。回归：pytest 46 passed（39+7；r2 收口后 47）、fetch_bj verify 12/12、assets verify ja/ko EXIT=0。
- 2026-09-30 DeepSeek Harness 限定复核 r2（被审 tip `31dcbde0`/返修 `118b4df3`）：**`approved`**——r1 全部条件 closed（独立复算字节求和/哈希/映射），0×P0/P1/P2，新增 8 项 P3 记录（N-1 草稿署名串、N-2 naming_note 范围、N-3 判别力措辞、N-4/N-5/N-8 代码候选、N-6 快照口径说明、N-7 报告归档）。集成收口：N-1/N-2/N-3/N-6 已随 r2 收口 commit 闭合，N-4/N-5/N-8 登记候选，N-7 归档随集成 commit。
- 2026-09-30 ZCode（代行 Codex）集成：merge `fae0d8f6`（base `9db2dca8`，分支 tip `98766fdc`；交付链 f1be5d2a→704df9bc→4d0e9db8→118b4df3→31dcbde0→98766fdc）。r1/r2 报告归档 `doc/reviews/M2-TA2B-4d0e9db8-dsh-r1.md`（sha256 前 16 `26372181214ecc33`）、`doc/reviews/M2-TA2B-31dcbde0-dsh-r2.md`（`dff840c005038a09`）。post-merge 复跑（main @`fae0d8f6`）：pytest tests/m2_test_assets 47 passed、git diff --check EXIT=0；素材在盘门槛（fetch_bj verify 12/12、assets verify ja/ko full EXIT=0、INVENTORY checked=110 missing=0）以交付链内日志 `raw/ac7b`/`ac7d` 为准（素材本体 gitignored，仅存在于 Owner worktree）。**Task done。**
