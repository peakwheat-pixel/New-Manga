已完成全部独立复核。以下是本次 r2 审查报告。

---

# M2-TA2C 独立非作者 Review（DSH r2，返修复审）

- **reviewer** = DeepSeek Harness（非作者，只读；未修改任何文件）
- **fixed base** = `d4d3977907bc64177ef85c61da4c95901f135fc6`
- **旧审查 head（r1）** = `2c12ba1ec9d302de10a210211dfa46cd490845df`（r1 verdict `changes_requested`）
- **本次 reviewed_head** = `8cb3a135c58d7a7a7b3d07fc5bba75c17aa6deb7`
- **返修实现 head** = `66dc361dac18b02fe3e4b773e9d0091ce6e37f60`
- **本会话** = `session-ca1ae6af-3e74-421c-a4ab-1ec58ec54927`（即外部交接文档所称的 r2b 会话）
- **Verdict = `approved`**：0×P0、0×P1、0×P2；**P2-1 与 P2-2 均判定关闭**；7 项遗留 P3 + 本次新增 3 项 P3，全不阻塞集成

**会话有效性前置说明**：审查期间工作区出现外部会话写入的 untracked `verification/M2-TA2C/checkpoint-handoff-zcode.md`（6039 bytes，22:58:51），声明"M2-TA2C 交接给 ZCode 代行集成"。我据此独立核验：`dsh-review-r2.jsonl` 末条确为 `{"type":"final","text":""}`、`dsh-review-r2.err.log` 确为 `INVALID_REQUEST: 422`，故 **r2 会话无效、不能作为 verdict**，本 r2b 会话为有效复审。该 checkpoint 与 `dsh-review-r2*.{jsonl,err.log}` 均为审查期副产物，**不在固定 diff 内、非作者交付**，我未创建也未改动。

## 1. 交付链与范围（Architecture）

`d4d39779`(base) → `ff2dee6c`(release) → `391faae8`(claim) → `2e979701`(r1 实现) → `2c12ba1e`(r1 handoff) → `93f7b4b4`/`0676865b`/`c6c9c93c`/`66dc361d`(返修) → `8cb3a135`(r2 handoff)。

| 轴 | 结论 | 依据 |
|---|---|---|
| 范围合规 | PASS | `2c12ba1e..8cb3a135` 共 14 文件，全落 Task 允许路径（`test_assets/comic_golden_suite/**`、`tests/m2_test_assets/**`、`doc/tasks|handoffs|reviews/M2-TA2C-*`、`verification/M2-TA2C/**`） |
| 生产零改动 | PASS | 对 `src/`、`apps/`、`requirements*`、`contracts/`、`packaging/`、lock 文件过滤命中为空 |
| 唯一体系 | PASS | 仍只升级 `comic_golden_suite`，未引入第二套 catalog |
| 净代码改动 | PASS | 返修对 `tools/assets.py` **净改动为零**：`93f7b4b4` 引入 `validate_public_profile(profile, case["language"])`，`c6c9c93c` 撤回；blob 比对 `2c12ba1e:assets.py` == `8cb3a135:assets.py`（`7adac8f8…`）**identical=True** |
| 证据链自述一致 | PASS | Handoff/run-results-r2 对 4 个返修 commit 的描述与 `git show --stat` 逐条吻合 |

## 2. Verification（**本次实际运行** vs 沙箱阻塞）

**我实际执行并取得 EXIT 的项**（作者日志不计入）：

| 我的命令 | EXIT | 我的实测结果 |
|---|---:|---|
| `assets.py list --level smoke` | 0 | `READY=20`（JA10+KO10）、`INVENTORY checked=92 missing=0 failures=0` |
| `assets.py missing --level regression` | 0 | `READY=23 / MISSING=8 / MISSING_GATED_ASSET=37` |
| `assets.py verify --language ja --level smoke` | 0 | `READY=10` |
| `assets.py verify --language ko --level smoke` | 0 | `READY=10` |
| `assets.py verify ... --case-id K11 K12 K13` | 0 | `READY=3` |
| `assets.py download ... --case-id K11 K12 K13` | 0 | `downloaded=0 existing=6 failures=0`（幂等、未联网、未写盘） |
| `pytest test_catalog.py -k "manifest_has_unique… or source_registry"` | 0 | `2 passed, 11 deselected`（含本次新增断言） |
| 独立复算 `local_asset_inventory.json` | — | **92 文件 / 63,317,229 bytes / 0 mismatch / 0 missing** |
| 独立复算 `ko-webtoon-audit.json` | — | **10 Case / 80 文件 / 884,913,245 bytes / 0 mismatch** |
| 报告完整性交叉核对 | — | `doc/reviews/M2-TA2C-2c12ba1e-dsh-r1.md` 正文与 `dsh-review-r1.jsonl` 的 `final` 文本**逐字一致**（规范化后 7926==7926）→ r1 报告未被篡改 |
| `git diff --check`（`d4d39779..8cb3a135` 与 `2c12ba1e..8cb3a135`） | 0 / 0 | 无空白/冲突标记错误 |
| `git check-ignore -v` KO 新 4 文件 | — | 全部命中 `韩漫_KO/.gitignore:1:/*` |
| `pytest --collect-only tests/m2_test_assets` | — | `25 tests collected`（与作者 25 passed 的基数一致） |

**沙箱阻塞（BLOCKED_BY_ENV，非作者缺陷）**：

- `pytest tests/m2_test_assets`（全量）：我实测 **3 passed, 22 errors, EXIT=1**，全部为 `_pytest/pathlib.py:175: PermissionError`（`tmp_path` 创建后被拒）。因此作者 `pytest-assets-r2.log` 的 `25 passed` 我**无法在本沙箱复现**，标 `NOT_RUN/BLOCKED_BY_ENV`；r1 的环境根因在 r2b 上完全一致。
- `pytest tests/m2_acceptance -q --tb=no`：我实测 **1 passed, 3 skipped, 31 errors, EXIT=1**（同为 `tmp_path` setup ERROR），因此作者声明的 `8 failed / 24 passed / 3 skipped` **未被我独立复现**。我做的替代核对是文档层比对：`acceptance-baseline.log` 与 `acceptance-r2.log` 的 8 条 FAILED 用例名**逐条完全相同**，计数一致，`BASELINE_FAILURE` 定性在证据层自洽。
- `tests/core`：作者标 `BLOCKED_BY_ENV`（PySide6 缺失），本次返修未重跑；我未复跑。

## 3. 旧 P2 逐项独立复核

### P2-1（KO Cleaned Webtoon 来源状态）→ **已关闭**

| 检查 | 我的实测证据 |
|---|---|
| 来源层状态已对齐 | `cases.json:149` `status="READY"`；`README.md:24` 资产状态列同为 `READY`；K01–K10 `asset_status` 集合 = `['READY']` |
| 判据已写明 | `:166` 新增 `notes`，明确 READY 仅覆盖"固定 10 个本地 Cleaned Webtoon 样例 + 结构/CRC 完整性"，底层再分发仍禁、应用 Pipeline `NOT_RUN`；`README.md:12` 同步限定来源层 READY 的覆盖范围 |
| 状态真实性 | 该源 10 Case × 8 文件 = 80 文件，`local_file_count=80` 与之吻合；我独立复算 80 文件 SHA-256 **全部匹配**，CLI 报 K01–K10 `READY` |
| 许可未被淡化 | `image_redistribution_status` 仍为 `"Raw manga image redistribution not established"`，`license` 仍写 CC BY-NC 仅覆盖 annotation/metadata |

结论：状态冲突已按"对齐事实 + 写明范围与判据"闭合，**不是用改文案掩盖真实不可用资产**。

### P2-2（JA/KO `checksum_inventory` 及路径基准）→ **已关闭**

- `peppercarrot_japanese_localized_pages:192`：`null` → `test_assets/comic_golden_suite/manifests/local_asset_inventory.json`（该清单确含 JA 12 个媒体，我独立复算 92 文件全匹配）。
- 四个非空值**全部为仓库根相对路径且实际存在**：`coo_and_manga109_dialog`、`peppercarrot_japanese_localized_pages`、`peppercarrot_korean_localized_pages` 统一指向同一清单；`ko_sfx_dialogue_cleaned_webtoon:161` 指向 `verification/M2-TA2C/ko-webtoon-audit.json`。基准统一成立。
- 额外改善：`ko_sfx` 原值为带说明后缀的**不可解析字符串**（`"...json (per-file SHA-256; CLI checks PNG CRC and JSON)"`），现为纯路径，实际修掉了 r1 未点名的隐性问题。
- `README.md:12` 明确写出"非空路径以仓库根为基准；`null` 表示本地无可校验文件"，`null` 的 8 个源 `local_file_count` 全为 0，自洽。

## 4. 新增测试 / 语言校验 / 许可与忽略边界

**新增测试**（`tests/m2_test_assets/test_catalog.py`，+5 行，全仓仅此测试文件变更）：新增 `by_id` 索引 + `ko_sfx.status == "READY"` + 三源 `checksum_inventory` 统一断言。断言**真实非空转**，我在沙箱实测该测试 `2 passed` 通过。

**语言校验行为**（r1 P3-2 处置）：作者的选择是**明确不采用**并附红证。我确认语义：`validate_public_profile(profile, language=None)` 的 `language` 分支要求 member 前缀 `lang/kr/`（KO）。若按 r1 建议在 `required_files()` 传 language，则 `status()` 对"member 语言不匹配的 profile"会从 `PARTIAL`（`test_public_assets.py:96` 断言）变成 `ValueError`，即改变既有无效 profile 的失败模式。而 manifest 层语言校验仍由 `load_manifest:83`、`download`、`validate_public_case` 覆盖，**行为无偏差**。作者撤回 + `run-results-r2.md:16` 如实披露 + 保留 `pytest-assets-r2-initial-fail.log` 红证，处置合理，**P3-2 以"不采用"关闭**。

**许可/忽略边界**：KO 新 4 文件（3 JPEG + 1 ZIP，16,292,579 bytes）全部被 `韩漫_KO/.gitignore` 的 `/*` 规则忽略，`git check-ignore -v` 逐文件命中；`日漫_JA` 维持 annotation-XML + license 白名单并显式排除图像/压缩包扩展名；本次 diff 未新增任何 tracked 媒体文件（全仓 245 个 tracked 媒体均在 `verification/**`、`experiments/**` 历史目录，不在 `test_assets/**`）。许可陈述未被削弱。

## 5. Findings（本次 r2）

### P0 / P1 / P2
**无。**

### P3（遗留，已在 r1 登记，作者已说明处置）
- **P3-1 已关闭**：`source-audit.md:9` 已补"SVG 含韩文的 `flowPara` 节点分别为 34/16/18（P07 另有其他韩文文本块）"口径。
- **P3-3 保留**：首次真实下载（4 文件）无 raw log，作者继续如实披露。接受。
- **P3-4 保留**：`acceptance-baseline.log:1` 的 `HEAD=391faae8`（claim）而非固定 base `d4d39779`；作者声明二者仅 Task 元数据不同，未对固定 base 直接取证。
- **P3-5 保留**：`doc/STATUS.md:14/15/17` 仍写 "implementation claim pending"、"worktree is pending creation"、M2-TA2C `ready`；`doc/REBASELINE_PLAN.md:34` 仍写状态 `ready`。作者声明集成时回填，可接受。
- **P3-6 保留**：`manual_source_page` 的 `source_url` 仍只有 `https://` 前缀断言、无主机白名单；`O01–O08`（`韩漫_KO/02_open_ground_truth_peppercarrot/**`）与 `K11–K13`（`…_public_ground_truth_peppercarrot/ep04`）同族目录命名仍不一致。
- **P3-7 保留（交集成方）**：`.dsh-review-tmp/` 我同样遭遇 `Permission denied`（`git status` 每次告警）且无法经策略删除；本会话新增 untracked `dsh-review-r2.jsonl`/`dsh-review-r2b.jsonl`/两个 `.err.log` 及外部 `checkpoint-handoff-zcode.md`。

### P3（本次 r2 新发现）
- **P3-8（证据/仓库卫生，建议集成方处置）**：`verification/M2-TA2C/dsh-review-r1.jsonl`（362,273 bytes / 279 行）与 0 字节 `dsh-review-r1.err.log` 在 `93f7b4b4` 被**提交入库**，与 r1 报告"请集成方清理这两个未跟踪文件"的建议相反。该转录含 Reviewer 完整思维链（45 条 `thinking`）、94 条 harness `status` 事件、**97 处本机绝对路径**，以及一条 401 错误原文（`Your api key: ****3cd7`、`request_id`、`api.deepseek.com/anthropic/...`，为掩码非有效凭据）。虽在 Task 允许路径内且无有效凭据，但把"每次 Review 的会话转录"作为常规交付会持续污染版本库，并已出现 r2/r2b 同类文件的处置难题。建议：明确"DSH 会话转录是否入库"的规则，本次至少移除 0 字节 err.log，并对 jsonl 做路径/凭据脱敏或改为 out-of-tree 归档。
- **P3-9（raw 日志可变性）**：`66dc361d` 修改了已提交的 `pytest-assets-r2-initial-fail.log`（1 行尾随空格 `:96: ` → `:96:`）。我确认**仅空白、未删证据**，但 raw log 的"原字节"属性被破坏（同一文件两个 commit 哈希），且 `run-results-r2.md` 未提及该次规范化。建议在证据说明中显式登记。
- **P3-10（断言覆盖缺口）**：新增断言是"回归锁定"而非判别力证明——数据在 `93f7b4b4` 先改为 `READY`，断言在 `0676865b` 后加，无法呈现"先红"；且断言只覆盖 3 个 source 的 `checksum_inventory` 字面值，未覆盖 `ko_sfx` 的值，也未断言路径在仓库根基准下**实际存在**。我另确认 `checksum_inventory` 字段**无任何运行时代码消费**（全仓仅 tests/README/cases.json/docs 命中），故路径漂移不会使任何测试变红。建议后续补一条"非空 `checksum_inventory` 路径必须存在于仓库根下"的参数化断言。

## 6. AC 对照（我的判定）

AC1–AC5 沿用 r1 的 PASS 判定（本次范围未触碰其证据）；AC6 仍未勾选（`doc/tasks/M2-TA2C.md:30` `- [ ]`，Task `status: in_review`）——正确，待集成后由集成方置 `done`。r1 的 P2-1/P2-2 落在 AC2/AC4 的"如实"轴上，本次已闭合，**AC 轴上不再有阻塞项**。

## 7. 结论与下一步

**Verdict = `approved`**（针对 reviewed_head=`8cb3a135` 的 P2 闭合与代码语义；0×P0/P1/P2）。本批准**不覆盖**集成动作本身；集成方在 main 上仍需完成：非沙箱环境独立复跑 `tests/m2_test_assets`（我受 `tmp_path` WinError 5 阻塞）、将 KO 新 4 个 ignored 文件非覆盖复制并复核 SHA-256、回填 `doc/STATUS.md`/`doc/REBASELINE_PLAN.md`、按 P3-8/P3-9 处置证据文件。

**建议转发指令（给 ZCode，代行集成）**：
> M2-TA2C r2 非作者复审结果：`approved`，reviewed_head=`8cb3a135`（返修实现 head=`66dc361d`），0×P0/P1/P2，P2-1/P2-2 判定关闭，报告见本会话 `dsh-review-r2b.jsonl`。请：① 在非沙箱环境复跑 `python -m pytest tests/m2_test_assets -q`（本沙箱因 pytest `tmp_path` WinError 5 无法复现作者 25 passed，标 `NOT_RUN/BLOCKED_BY_ENV`）；② 从 Task worktree 非覆盖复制 KO 新 4 个 ignored 文件（`韩漫_KO/02_public_ground_truth_peppercarrot/ep04/`，16,292,579 bytes）并按 `local_asset_inventory.json` 核对 SHA-256；③ 回填 `doc/STATUS.md:14/15/17` 与 `doc/REBASELINE_PLAN.md:34` 的 TA2C 状态；④ 处置 P3-8（`dsh-review-r1.jsonl` 362KB 会话转录 + 0 字节 `err.log` 已入库，含 97 处本机绝对路径与掩码 API key/request_id，建议脱敏或移出树，并明确后续 DSH 转录是否入库的规则）与 P3-9（`66dc361d` 修改了已提交 raw log 的空白，须在证据说明登记）；⑤ 清理本会话 untracked `dsh-review-r2.{jsonl,err.log}`、`dsh-review-r2b.{jsonl,err.log}` 与 `.dsh-review-tmp/`（我用 `git status` 每次告警 `Permission denied`，无法删除）。集成前用 `git status --porcelain` 证明工作树只剩预期内容。
