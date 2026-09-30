---
task_id: M2-TA2B
author: ZCode
recipient: Codex（集成）/ DeepSeek Harness（Review）
base_commit: 9db2dca892e7fe1db5bf89c0a35501df014e653e
delivery_head: 704df9bc（实现）；本 Handoff 随交付 commit 入库
status: delivered_in_review
review_r1: approved_with_conditions (DSH, tip 4d0e9db8)
repair_head: 118b4df3
---

# Handoff：M2-TA2B（JA/KO 开放素材池）

## 交付结果

按重写版 Task（用户裁决 2026-09-30）完成 AC1–AC8 全部范围，交付分支 `agent/zcode/M2-TA2B-OPEN-ASSETS`：

1. **提交列表**
   - `f1be5d2a` chore(M2-TA2B): claim task - set in_progress and pin base_commit 9db2dca8
   - `704df9bc` feat(M2-TA2B): open asset pool - official free BJ volumes, P&C additions, Manga109 cancellation
   - 交付 commit（本 Handoff + Task 回填）：见分支头部

2. **变更路径**（全部在允许范围内）
   - `test_assets/comic_golden_suite/tools/fetch_bj.py`（新增：BJ 官方免费卷下载/校验/渲染工具，标准库 + 可选 pypdfium2/Pillow，复用 assets.py 的 `zip_parts`/`COPY_BLOCK`）
   - `test_assets/comic_golden_suite/tools/assets.py`（`SOURCE_URL_HOSTS` 增加 `densho810.com`，注释更新）
   - `test_assets/comic_golden_suite/manifests/cases.json`（97 case：+12 BJ01–BJ12、+5 J48–J52、+12 K14–K25；37 个 Manga109 case + 3 个 source 加 `removed_from_scope_2026-09-30: true`；levels 计数与 notes 更新；既有 case/source 字段值零变化，已与 HEAD 程序化对比验证）
   - `test_assets/comic_golden_suite/manifests/local_asset_inventory.json`（+18 个媒体条目逐文件 SHA256；路径为 suite 相对形态，checked=110 missing=0 failures=0）
   - `test_assets/comic_golden_suite/README.md`（97 定义总览、BJ 资产表行、白名单说明、`fetch_bj.py` 用法、《ブラックジャックによろしく》署名与许可义务小节、官方来源链接）
   - `test_assets/comic_golden_suite/日漫_JA/.gitignore`（显式忽略 `01_black_jack_official/`、`99_optional_openmantra/`）
   - `tests/m2_test_assets/test_catalog.py`（68→97 断言更新；新增 BJ 注册、Manga109 取消、OpenMantra 隔离、P&C 补充、densho810 白名单 5 个测试）
   - `verification/M2-TA2B/`（densho810-report-draft.txt + raw/ 下 7 份命令日志（r1 时点））

3. **素材本体（全部 gitignored，零入库）**：BJ 第 1/3/5 卷 ZIP+PDF+12 张渲染 PNG（`日漫_JA/01_black_jack_official/vol*/`）；17 张 P&C 新页 + ep20 kr ZIP（`日漫_JA/02_open_ground_truth_peppercarrot/ep04/`、`韩漫_KO/02_public_ground_truth_peppercarrot/ep04|ep20/`）；OpenMantra annotation/LICENSE/README + 10 张样本页（`日漫_JA/99_optional_openmantra/`，2,341,834 bytes）。

4. **BJ 下载摘要（SHA256 见 `vol*/bj_download_manifest.json`）**
   - vol01：`001bj.zip` 343,497,422 B，sha256 `ec7bbb4ce4f719536a2d58f29eb2c665d19b0769303efe009b4d98cccad699e1`；PDF 209 页
   - vol03：`003bj.zip` 338,764,008 B，sha256 `73aaf85c894554df2f68da5b1ea614c859a815f2bb12cb3fe8e973ac3d5b5750`；PDF 221 页
   - vol05：`005bj.zip` 386,575,185 B，sha256 `df25c0111cc520eb7acbb43372c3a2066a5ea9c77f99aad54fe731d4365278e9`；PDF 243 页
   - 12 个渲染页 SHA256 记录于各卷 `bj_pages_manifest.json` 与 cases.json `page_sha256` 字段。

5. **AC 对照**：AC1–AC8 全部 PASS（逐项证据见 Task 测试表与下表）；无 BLOCKED、无 NOT_RUN 交付项。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 下载 3 卷 | `python test_assets/comic_golden_suite/tools/fetch_bj.py fetch --volumes 1 3 5`（vol05 修复后 `fetch --volumes 5`） | Windows + Python 3.14.6，HEAD f1be5d2a | PASS（首次 vol05 因 ZIP 内 `__MACOSX/._005bj.pdf` 元数据成员失败，修复提取规则后复用已下载 ZIP 重跑 EXIT=0） | `verification/M2-TA2B/raw/ac1-fetch-bj-volumes.log`、`ac1-fetch-bj-vol05-retry.log` |
| AC2 渲染 | `fetch_bj.py render --volumes 1 3 5` + 12 页人工目检 | pypdfium2==5.13.0（生产 pin）、Pillow 12.3.0 | PASS：12 PNG（DPI 150，2946x4167），去重 0 | `verification/M2-TA2B/raw/ac2-render-bj-pages.log` |
| AC3 manifest/署名/草稿 | cases.json 编辑 + README + 草稿生成 | 704df9bc | PASS | `manifests/cases.json`、`verification/M2-TA2B/densho810-report-draft.txt` |
| AC4 P&C 补充 | `assets.py download --level full --case-id J48…K25`（17 个 case） | f1be5d2a | PASS：downloaded=18 existing=16 failures=0 | `verification/M2-TA2B/raw/ac4-download-pc-additions.log` |
| AC5 OpenMantra | curl raw.githubusercontent.com（annotation/LICENSE/README + 5 部作品各 2 页） | f1be5d2a | PASS（READY_OPTIONAL_ISOLATED，`optional_noncommercial_baseline_excluded: true`） | `verification/M2-TA2B/raw/ac5-openmantra-optional-download.log` |
| AC6 取消标注 | 与 HEAD 程序化对比 + 断言测试 | 704df9bc | PASS：37 case + 3 source 标注，其他字段值零变化 | `tests/m2_test_assets/test_catalog.py::test_manga109_scope_is_cancelled_by_user_ruling_2026_09_30` |
| AC7 pytest | `python -m pytest tests/m2_test_assets -q` | 704df9bc | PASS：39 passed，EXIT=0 | `verification/M2-TA2B/raw/ac7-pytest-m2-test-assets.log` |
| AC7 verify | `assets.py verify --language ja --level full`、`--language ko --level full` | 704df9bc（素材已从主仓库只读复制至 worktree） | PASS：ja EXIT=0（gated=37/PARTIAL=12/READY=15）；ko EXIT=0（MISSING=8 既有 O01–O08/READY=25） | `verification/M2-TA2B/raw/ac7-verify-ja-ko-full.log` |
| AC8 范围 | `git status`、`git check-ignore`、`git diff --check` | 704df9bc | PASS：素材零入库，diff 仅允许路径，EXIT=0 | git 输出 |

未运行项：BJ 全 13 卷、OpenMantra 全量 214 页、应用级 Pipeline（ocr/detection/…）均属可选扩展或后续 Task，未纳入本次范围。

## 接收方式

- 分支 `agent/zcode/M2-TA2B-OPEN-ASSETS`（worktree `G:/CODEX/New Manga.worktrees/M2-TA2B-OPEN-ASSETS-zcode`），base `9db2dca8`，实现 head `704df9bc`。
- 复现：`python test_assets/comic_golden_suite/tools/fetch_bj.py fetch --volumes 1 3 5 && python … render --volumes 1 3 5`（需 `pip install pypdfium2==5.13.0`，tuna 镜像无 wheel 时用 `--index-url https://pypi.org/simple`）；`python -m pytest tests/m2_test_assets -q`；`python test_assets/comic_golden_suite/tools/assets.py verify --language ja --level full`。
- 前置条件：本机素材目录含 BJ/P&C/OpenMantra 产物（Reviewer 若无网络可只跑 pytest 与 verify）；Reviewer 的 worktree 若无素材，verify 的媒体缺失不致 FAIL（missing 媒体不计数），但 READY 数会不同。
- Reviewer 检查建议：1) cases.json 中 BJ12 个 case 的 tags 与 `feature_notes` 是否与页面实况一致（可对照 `vol*/pages/*.png`）；2) `removed_from_scope_2026-09-30` 标注是否满足取消语义；3) `fetch_bj.py` 的安全边界（host/path 白名单、Content-Length、原子发布）；4) README 署名小节与邮件草稿的合规表述。

## 下一任务建议（必填）

- Task ID / 标题：M2-TA2B Review（DeepSeek Harness 非作者静态 Review）→ Codex 集成验证
- 推荐 Agent / Reviewer：DeepSeek Harness（静态 Review，非作者）；集成由 Codex
- 推荐原因与前置依赖：Task 交付流程要求独立 Review + Codex 集成验证后才可进入 done；本 Handoff 提供全部证据路径
- Recovery point：仓库 `G:/CODEX/New Manga`，branch `agent/zcode/M2-TA2B-OPEN-ASSETS`，worktree `G:/CODEX/New Manga.worktrees/M2-TA2B-OPEN-ASSETS-zcode`，base `9db2dca8`，delivery head `704df9bc`（工作树保持干净，不 push、不合并）
- 允许修改路径：Review 意见记录（Task/Handoff/verification）；若 Review 要求修改实现，仅限 Task 允许路径（cases.json、README、tools/assets.py、tools/fetch_bj.py、tests/m2_test_assets/**、.gitignore、verification/M2-TA2B/**）
- 禁止范围与新增授权条件：素材像素/文件不得入 Git；不得改 `src/**`、`apps/**`、`packaging/**`；不得修改既有 case 字段值（取消标注除外）；densho810 报告邮件必须由用户本人发送
- 交付物：Review 记录（REVIEW 模板）+ 集成验证结论；通过后 Task 置 done 并由 Codex 决定集成 commit
- 验证命令、环境与完成 Gate：`python -m pytest tests/m2_test_assets -q` EXIT=0；`python test_assets/comic_golden_suite/tools/assets.py verify --language ja --level full` EXIT=0；`git diff --check` EXIT=0
- 可直接转发给 Agent 的指令：

> 在 worktree `G:/CODEX/New Manga.worktrees/M2-TA2B-OPEN-ASSETS-zcode`（分支 agent/zcode/M2-TA2B-OPEN-ASSETS，head 704df9bc）对 M2-TA2B 做非作者静态 Review：读 `doc/tasks/M2-TA2B.md`（重写版）、`doc/handoffs/M2-TA2B-704df9b.md`、`verification/M2-TA2B/raw/` 日志与 `test_assets/comic_golden_suite/README.md` 署名小节；运行 `python -m pytest tests/m2_test_assets -q` 与 `python test_assets/comic_golden_suite/tools/assets.py verify --language ja --level full`；核对 BJ01–BJ12 的 attribution/tags、37+3 个 `removed_from_scope_2026-09-30` 标注、OpenMantra `optional_noncommercial_baseline_excluded` 隔离与素材 gitignore。产出 REVIEW 模板记录，不修改实现，不合并。

## Review 轨迹与返修（2026-09-30）

- **DSH r1（被审 tip `4d0e9db8`）：`approved_with_conditions`**——P0=0、P1×1 + P2×6 + P3×9；判据为入库日志/实体文件（非 commit 自述），并逐条复核 densho810 官方利用规约。
- **返修 commit `118b4df3`**（amend 自 `a93a61f3`：仅 ac6 日志尾随空格与元数据，轨迹披露）：P1-1（OpenMantra 三处登记同步 + inventory_tracking 标记）、P2-1（`fetch_bj.py verify` 12/12 + README 绿色门槛）、P2-2（source 计数按 inventory 求和 + `black_jack_official_free` 条目）、P2-3（12 处 /ko/→/kr/）、P2-4（`test_fetch_bj.py` 离线单测，r2 收口后 8 个）、P2-5（ac6 零变化日志 + ac8 范围审计日志，禁改路径零命中、diff --check EXIT=0）、P2-6（BJ04 补 horizontal_text，编排侧目检确认）、P3-1/3/4/5/6/7 落字（ac5b 复验日志、KO ZIP 3→2、官方署名格式+attribution_note、输入校验进 try+死分支删除、取消语义与 COO 豁免说明）。
- **与 DSH 建议的偏差**：P2-2 的 ko ep20 未单列新 benchmark_source，而是把既有 `peppercarrot_korean_localized_pages` 条目对齐为与 ja 侧一致的跨 episode 合并口径（E04+E20，2 archives）——与既有 ja 条目结构对称，理由登记于此。
- **DSH r2（限定复核，tip `31dcbde0`）：`approved`**——r1 条件全 closed（独立复算），0×P0/P1/P2，8 项 P3 记录；N-1/N-2/N-3/N-6 已随 r2 收口 commit 闭合，N-4/N-5/N-8 登记候选，N-7 随集成归档。
- **最终回归**：pytest 47 passed、fetch_bj verify 12/12 EXIT=0、assets verify ja/ko full EXIT=0、`fetch_bj.py verify` 12/12 EXIT=0、`assets.py verify` ja/ko full EXIT=0（INVENTORY checked=110 missing=0）；日志 `raw/ac6-zero-change-diff.log`、`ac7b-fetch-bj-verify.log`、`ac7c-pytest-after-fix.log`、`ac7d-verify-after-fix.log`、`ac5b-openmantra-verification.log`、`ac8-scope-proof.log`。

## 风险与遗留

- **用户待办**：素材公开用于测试后 1 个月内，须由用户向 info@densho810.com 发送报告邮件（草稿 `verification/M2-TA2B/densho810-report-draft.txt`，Agent 不代发）。
- vol05 ZIP 内含 macOS `__MACOSX/._005bj.pdf` 元数据成员（上游打包产物）；`fetch_bj.py` 已显式跳过此类成员，属预期行为。
- BJ 首次下载 vol05 时曾因该成员报 `expected exactly one PDF member` 失败并留下 3 个 `.part` 硬链接残留（成功路径缺清理）；已修复为 finally 清理并删除残留文件。修复前的失败日志如实保留在 `raw/ac1-fetch-bj-volumes.log`。
- worktree 原本缺失全部 gitignored 素材；为使 verify 可运行，已从主仓库只读复制 KO webtoon（845MB）与既有 P&C 页（未修改主仓库）。主仓库 verify 基线不受影响。
- 可选扩展（不阻塞）：BJ 其余 10 卷（第 2/7/11 卷含 JASRAC 乐曲页需登记处理）、OpenMantra 全量 214 页、BJ case 的应用级 Pipeline 首跑。
- OpenMantra 为 CC BY-NC 4.0：仅限隔离的非商业基线使用（`optional_noncommercial_baseline_excluded: true`），不得进入生产许可基线、smoke/regression/full levels 或 Git。
- pypdfium2 安装注意：本机默认 tuna 镜像对 Python 3.14 无 wheel（`from versions: none`），需 `--index-url https://pypi.org/simple`。
