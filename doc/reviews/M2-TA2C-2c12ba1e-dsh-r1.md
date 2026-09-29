---
task_id: M2-TA2C
reviewer: DeepSeek Harness
base_commit: d4d3977907bc64177ef85c61da4c95901f135fc6
reviewed_head: 2c12ba1ec9d302de10a210211dfa46cd490845df
decision: changes_requested
session_id: session-c92590bf-7375-4e7e-a760-30dca83ea90b
raw_log: verification/M2-TA2C/dsh-review-r1.jsonl
---

审查已完成。以下是独立 Review 报告。

---

# M2-TA2C 独立非作者 Review（DSH）

- **reviewed_head** = `2c12ba1ec9d302de10a210211dfa46cd490845df`（Handoff 提交）
- **implementation_head** = `2e9797013dcb73280462a7b34390abcb2be12977`
- **fixed base** = `d4d3977907bc64177ef85c61da4c95901f135fc6`
- **Verdict = `changes_requested`**（0×P0、0×P1、2×P2、7×P3；全部为文档/元数据层与证据层缺口，不涉及资产安全或许可造假）
- 交付链核实：`d4d39779` → `ff2dee6c`(release) → `391faae8`(claim, 仅 Task 3+/3−) → `2e979701`(实现) → `2c12ba1e`(handoff, 仅 Handoff/Task/verification 12 文件)。`implementation_head..reviewed_head` 不含任何 `test_assets/**` 代码改动，证据链与 Handoff 叙述一致。

## 1. Architecture（范围与结构）

| 轴 | 结论 | 依据 |
|---|---|---|
| 唯一体系 | PASS：仅升级 `test_assets/comic_golden_suite`，无第二套 catalog | `git diff --name-status` 23 文件全落 Task 允许路径 |
| 生产范围 | PASS：`src/**`、`apps/**`、`requirements*`、`contracts`、`packaging` 零命中 | 同上 |
| 附件脚本未复用 | PASS：全仓 grep `download_assets_no_hf|stream_download|pack_downloaded|huggingface_hub|hf_hub` 无命中；附件只以静态审计文本存在 | `verification/M2-TA2C/attachment-audit.md` |
| 统一 JA/KO schema | PASS：68 Case 全含 `source_id/source_name/asset_type/source_url/license/ground_truth_types/image_available/annotation_available/pipeline_status`，`load_manifest` 强制类型与键集合 | `assets.py:42-83` |
| READY ≠ Pipeline PASS | PASS：577 个 pipeline 段全 `NOT_RUN`；README/run-results 显式声明分离 | `cases.json`，`README.md:20`、`run-results.md:3` |
| 可运行计数语义 | PASS：code-only/annotation-only/gated 均不计 READY（COO/Dialog `PARTIAL` 仅 76 annotation；Manga109 37 为 `MISSING_GATED_ASSET`） | 独立复算，见 §2 |
| CLI 扩展 | PASS：`--case-id` 校验落在所选 language/level 内（越界 `parser.error`），公开页仍限 HTTPS `www.peppercarrot.com` + 重定向白名单 | `assets.py:813-825`、`266-291` |
| ZIP 安全 | PASS：路径/绝对/`..`/drive/反斜杠/NUL/重复(casefold)/符号链接/加密/条目数与三重体积上限/声明大小一致性校验，DTD+ENTITY 拒绝，全程不落盘解压 | `assets.py:343-405`、`632-642` |
| 原子性与幂等 | PASS：`NamedTemporaryFile(.part)` + `os.link` 原子发布，`finally` 清理；已存在且有效→skip，已存在但无效→fail-closed 不覆盖 | `assets.py:487-536` |

## 2. Verification（我独立执行，非照抄）

**已在 reviewed_head 实测（EXIT=0）**

| 命令/复算 | 结果 |
|---|---|
| `assets.py list --level smoke` | `READY=20`（JA10+KO10）、`INVENTORY checked=92 missing=0 failures=0` |
| `assets.py missing --level regression` | `READY=23 / MISSING=8 / MISSING_GATED_ASSET=37`（=68，与 manifest-status-check.log 一致） |
| `assets.py verify --language ko --level regression --case-id K11 K12 K13` | `READY=3` |
| `assets.py download`（K11–K13 重复） | `downloaded=0 existing=6 failures=0`（幂等，未联网、未写盘） |
| 独立重算 `ko-webtoon-audit.json` | 80 文件 / 884,913,245 bytes / **0 mismatch** |
| 独立重算 `local_asset_inventory.json` | 9 asset / **92 文件 / 0 mismatch**；总字节反算 = 63,317,229，与 `README.md:38` 吻合 |
| 独立 ZIP 审计（KO E04 lang-pack） | 615 成员、无加密、无非常规类型；`lang/kr/{E04P02,E04P03,E04P07}.svg` 存在，含韩文 `flowPara` = 34/16/18 |
| `git ls-files` 媒体 / `git check-ignore` / `git diff --check`(两区间) | tracked media=**0**；新 KO JPEG+ZIP 命中 `韩漫_KO/.gitignore:/*`；diff-check 均 EXIT=0 |
| 网络来源核实 | 官方韩文 ep04 sources 页 200，含所用 3 个页面 URL 与 lang-pack URL（页面标 13.76 MiB ≡ inventory 14,428,439 bytes）；官方版权页 = **CC BY 4.0**；OpenMantra `LICENSE.md` = **CC BY-NC 4.0**（作者保守处置成立） |

**未能独立复现（NOT_RUN / BLOCKED_BY_ENV，非作者缺陷）**

- `python -m pytest tests/m2_test_assets`：**NOT_RUN**。本 DSH 沙箱下 pytest 创建 `tmp_path/basetemp` 目录后立即 `os.scandir` 报 `PermissionError [WinError 5]`，25 项中 **23 项 setup ERROR**；我尝试三种 basetemp 位置（会话 TEMP/独立 TEMP/工作区）均同因失败。仅 2 个不依赖 `tmp_path` 的 manifest 测试实测通过（`-k "manifest_has_unique or source_registry"` → `2 passed`, EXIT=0）。作者 `pytest-assets.log`（`25 passed`，含 Shell/Python/Tested_HEAD/EXIT）**形式完整但无法在本沙箱复现**；其余 23 项我以代码静态审查确认断言真实（原子发布、幂等 `fetch` 未调用、跨主机重定向拒绝、短读/断流不发布、CRC 损坏、ZIP slip、DTD/entity、checksum 漂移使结构有效页退回 `PARTIAL`），非空转。
- `tests/m2_acceptance`：**NOT_RUN**（同上环境原因）；作者 `acceptance-baseline.log` 与 `acceptance-implementation.log` 失败用例名**逐条一致**（8 failed/24 passed/3 skipped），`BASELINE_FAILURE` 定性成立（见 P3-4）。
- `tests/core`：作者标 `BLOCKED_BY_ENV`（PySide6 缺失），我未复跑，接受该标注。

## 3. Findings

### P0
无。

### P1
无。

### P2

- **P2-1（状态一致性）** `test_assets/comic_golden_suite/manifests/cases.json:147-166`（`status: "PARTIAL"` 在 `:149`）与 `test_assets/comic_golden_suite/README.md:23`、K01–K10 的 `asset_status: "READY"` 冲突：同一来源「KO Cleaned Webtoon 固定 10 Case」在 README 标 `READY`、在 manifest 源注册表标 `PARTIAL`，且该源记录未给出 PARTIAL 判据（许可受限还是完整性不足）。源注册表其他条目用 `READY` 表示"文件已取得且完整"，两处同字段取值不同即用户要求的"状态一致性"缺口。
- **P2-2（元数据真实性/基准不一致）** `cases.json:161 / :191 / :116`：
  - `peppercarrot_japanese_localized_pages.checksum_inventory = null`（`:191`），但其 12 个媒体文件确实在 `manifests/local_asset_inventory.json` 中且 `README.md:24` 明写"逐文件大小与 SHA-256 见 inventory"——**字段与声明/事实矛盾**；
  - `ko_sfx_dialogue_cleaned_webtoon.checksum_inventory` 指向 `verification/M2-TA2C/ko-webtoon-audit.json`（仓库根基准），而 `coo_and_manga109_dialog` 用 `manifests/local_asset_inventory.json`（suite root 基准）——**同一字段两种路径基准**。

### P3

- **P3-1** `verification/M2-TA2C/source-audit.md:9` "SVG 韩文文本节点分别 34/16/18"：我实测含韩文 `flowPara` 为 34/16/18 ✓，但 E04P07 另含 1 个 `<text>`+2 `<tspan>` 韩文块（韩文文本块实为 19），口径未注明"仅计 flowPara"。
- **P3-2** `tools/assets.py:110`：`required_files()` 调 `validate_public_profile(profile)` 未传 `language`，member 语言一致性在该路径不校验（`load_manifest:83`/`download:544` 已校验，行为无偏差），建议统一传参。
- **P3-3** `verification/M2-TA2C/run-results.md:13`：首次真实下载（4 文件）未保留 raw log（作者已如实披露）；在线首跑证据仅有 inventory 哈希复验与重复运行的 `existing` 计数。
- **P3-4** `verification/M2-TA2C/acceptance-baseline.log:1`：基线 HEAD=`391faae8`（claim）而非 Task 测试计划要求的固定 base `d4d39779`。claim 仅改 Task 3 行，实质等价，但未对固定 base 直接取证。
- **P3-5** 文档滞后：`doc/REBASELINE_PLAN.md:34` 写 TA2C "状态 `ready`"，`doc/STATUS.md:14` 写 "implementation claim pending / worktree is pending creation"，而 reviewed_head 上 Task 已是 `in_review`、实现已提交、worktree 已存在（即本工作区）。属 release 时点文字未随实施/claim 同步。
- **P3-6** 命名与校验口径：既有 `O01–O08` 用 `韩漫_KO/02_open_ground_truth_peppercarrot/**`，本次新增 `K11–K13` 用 `韩漫_KO/02_public_ground_truth_peppercarrot/ep04`，同族目录名不一致易混淆；`manual_source_page` 的 `source_url` 仅有 `https://` 前缀断言、无主机白名单（`assets.py:306-325` 只覆盖 `open_public_comic_page`）。
- **P3-7** Review 环境残留（须集成方清理，非作者交付）：① `.dsh-review-tmp/`——我运行 pytest 时产生，沙箱对其后续 `scandir/rmdir/icacls` 一律返回 Access denied，`danger-full-access` 升级因无审批通道被拒，**我无法删除**；② `verification/M2-TA2C/dsh-review-r1.jsonl`（sessionId = 本会话 `session-c92590bf-…`）与空 `dsh-review-r1.err.log`——本 Review 会话 harness 转录副产物，**untracked、不属于固定 diff**。两者均未影响任何 tracked 文件（`git diff` 为空、`git diff --check` EXIT=0）。

## 4. AC 对照（我的判定）

AC1 PASS（附件/来源审计文本真实，网络核实两项关键许可）；AC2 PASS（schema 统一、577 段 `NOT_RUN`、gated/annotation-only 不计可运行）；AC3 PASS（KO 4 文件哈希与 ZIP member 独立复算一致；未重复下载 844 MiB）；AC4 PASS（9 来源状态与实物一致，无伪造 READY）；AC5 PASS（四命令 + `--case-id` 幂等实测；L0 20/L1-L2 68 定义 23 READY/8 MISSING/37 gated 如实）；**AC6 未完成**（`doc/tasks/M2-TA2C.md:30` 未勾选，Task `status: in_review`，正确）——但 P2-1/P2-2 落在 AC2/AC4 的"如实"轴上，故本 Review 不批准进入集成。

## 5. 推荐下一步

**给 Owner（Codex Desktop）的最小返修（仅 2 处、零代码/零重建/零重跑）：**
1. `manifests/cases.json:147-166`：把 `ko_sfx_dialogue_cleaned_webtoon.status` 与 `README.md:23` 对齐为同一值，并在 `notes` 写明该状态的判据（若保留 `PARTIAL`，须说明是"许可/GT 部分受限"而非完整性不足）。可一并同步 `pytest` 的临时断言（如新增 `assert` 需重跑，请保留新 raw log）。
2. `cases.json:191` 把 `peppercarrot_japanese_localized_pages.checksum_inventory` 填为 `manifests/local_asset_inventory.json`，并统一 `ko_sfx...`(:161) 的路径基准（建议全部相对 suite root 或全部相对仓库根，并在 README 注明基准）。
3. 可选：`source-audit.md:9` 补"仅计 flowPara"口径；`docker` 无需改动。

修毕后请以固定新 HEAD 重新提交 Handoff（含新日志的 Shell/Python/Tested_HEAD/EXIT），并请集成方在非沙箱环境清理 `.dsh-review-tmp/` 与本会话的 `dsh-review-r1.*` 未跟踪文件；清理后用 `git status --porcelain` 证明工作树只剩预期内容。

**建议转发指令（给 Codex Desktop）**：
> M2-TA2C 非作者 Review 结果：`changes_requested`（0×P0/P1、2×P2、7×P3，reviewed_head=`2c12ba1e`）。请只做两处元数据返修：①`cases.json:147-166` 的 `ko_sfx_dialogue_cleaned_webtoon.status` 与 `README.md:23` 对齐并写明判据；②`cases.json:191` 的 `checksum_inventory` 补为 `manifests/local_asset_inventory.json` 并统一 `:161` 的路径基准。返修后提交固定新 HEAD + 更新 Handoff，声明 pytest/m2_acceptance 的新日志（含 Tested_HEAD/EXIT），并请集成方清理 `.dsh-review-tmp/` 与 `verification/M2-TA2C/dsh-review-r1.{jsonl,err.log}`（Review 会副产物、untracked）。
