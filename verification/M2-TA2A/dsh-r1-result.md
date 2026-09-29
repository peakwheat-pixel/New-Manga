## M2-TA2A 独立审查报告（非作者 Reviewer）

**Reviewed commit**：`a6977cf9ddea3f2e15a19c8d5ca06a3e82e342a9`
**验证**：`git rev-parse HEAD` = `a6977cf9ddea3f2e15a19c8d5ca06a3e82e342a9` ✅（分支 `agent/codex/M2-TA2A-ja-public-assets`，worktree 根另有 2 个**预先存在**的未跟踪文件 `verification/M2-TA2A/dsh-r1-result.md`、`dsh-r1-stderr.log`，非本 Task 产物）
**只读纪律**：未修改/提交任何仓库文件，未切换分支，未把媒体纳入 Git；全部实验在临时目录内完成（见文末副作用披露）。

---

### 一、执行命令与真实结果

| 命令 | 真实结果 |
|---|---|
| `git rev-parse HEAD` | `a6977cf9...`，与指定 commit 相等 ✅ |
| `python -m pytest tests/m2_test_assets -q` | **NOT_RUN (ENV_BLOCKED)**：本审查环境沙箱拒绝 pytest `tmp_path` 创建（`PermissionError WinError 5` on `…\Temp\dsh-*\pytest-of-49745`），2 passed / 19 errors，19 个 error 全部是 fixture 环境错误，非代码失败 |
| 替代证据：直接以自建绝对 tmp 调用全部 21 个测试函数 | **21/21 断言通过**（含 drift、ZIP slip、redirect、损坏输入、archive 幂等） |
| `assets.py verify --language ja --level smoke` | **EXIT 0**；`READY=10`，`INVENTORY checked=88 missing=0 failures=0` ✅ 与证据一致 |
| `assets.py verify --language ko --level smoke` | **EXIT 0**；`READY=10`，inventory 一致 |
| `assets.py list / missing --language ja --level smoke` | **EXIT 0**；READY=10 / no missing |
| `assets.py download --language ja --level regression` | **EXIT 0**；`downloaded=0 existing=20 gated_cases=37 failures=0`，未发起 gated 下载、幂等 ✅ |
| 离线 verify（patch `urlopen`+`open_public_comic_url` 抛错） | **EXIT 0**；READY=10，无网络访问 ✅ |
| 独立重算 inventory 88 文件 size+SHA-256；解析 74 XML；ZIP 全成员 CRC | `missing=0 mismatch=0`；XML 74/74 可解析；2 ZIP `testzip=None`（615/463 entries）✅ |
| `git ls-files` 媒体 / 本 commit 新增媒体 | 本 commit **新增媒体 0**；annotation+license tracked=76 ✅ |
| 端到端 CLI 矩阵（临时 suite，不改仓库） | 见 findings 证据 |

---

### 二、结论

**`APPROVED`** — 无 P0、无 P1。

理由：本 Task 新增的 10 个 JA 公开页 JPEG + 2 个 ZIP 全部有逐文件 SHA-256，合法但哈希漂移时 `verify/list/missing` 实测均输出 `PARTIAL` 且 **EXIT 1**；gated 来源零访问且正确保持 `MISSING_GATED_ASSET`；COO/Manga109Dialog 仅 annotation 保持 `PARTIAL`；JMangaBench/Text Mask `BLOCKED_BY_ASSET_ACCESS`、OpenMantra `MISSING`；本 commit 未新增任何受限原图，未触及生产 Schema/migration/Pipeline/Provider/UI/dependency lock；precommit finding R-001 已处置。P2 均为防御性/口径类，不阻断集成，但建议集成前逐项裁决。

**R-001 处置核对（已闭环）**：`run-results.md:23-24` 已是 `21 passed`、`INVENTORY checked=88 missing=0 failures=0`；无 `verified=88`、无 source-group 聚合 checksum（`source-audit.md:21` 明确声明）；`integration-checks.log:69` 保留「19 → 21」历史说明。

---

### 三、Findings

#### P0 / P1
**无 P0、无 P1。**

#### P2

| ID | 位置 | 证据（我实测） | 影响 | 修复建议 |
|---|---|---|---|---|
| P2-1 | `manifests/local_asset_inventory.json`（88 文件全在 `日漫_JA/`，无 KO 条目）+ `tools/assets.py:135-137` + `README.md:13,22` | 临时 suite 造 `hf_cleaned_webtoon` case，把合法 PNG 换成**另一个合法 PNG**（同结构、不同内容）→ `verify --language ko --level smoke` = **EXIT 0 / READY** | KO 10 Case（80 文件）的 `READY` 只有存在性+PNG 结构校验，无任何 checksum 基准；题面「任意合法但 checksum drift 的图像/ZIP 不得显示 READY」若覆盖 KO 则**不满足**（本 Task 新增 JA 媒体不受影响，已实测 PARTIAL+exit 1） | ①为 KO 80 文件登记 size+SHA-256；或②README/inventory 明确声明 KO 仅结构性校验。若验收方认定该语句覆盖全部 READY 图像，本条应升级为 P1 |
| P2-2 | `tools/assets.py:149`（`print_cases`→`status`）、`:800-824`（list/missing 不调 `validate_present`）+ `README.md:12` | CRC 被破坏但仍非空的 PNG：`list`、`missing` = **EXIT 0 / READY**；仅 `verify` = EXIT 1 + `INVALID … invalid or truncated PNG` | README 称 CLI「按本地文件、inventory checksum 和格式检查计算状态」，但 `list/missing` 对 `hf_cleaned_webtoon`/`manga109_title` 无格式检查；用 list 做健康检查会漏报损坏资产 | README 明确 `list/missing` 不做逐文件格式/哈希校验，或让 list 对 READY case 复用 `validate_present` |
| P2-3 | `tools/assets.py:179-183`（缺失媒体只计 missing）、`:810-818`（`any(path.exists())` 才校验）+ `README.md:13` | 公开页 case 的 JPEG 与 ZIP **同时缺失**：`verify --language ja --level smoke` = **EXIT 0**，仅 `MISSING=1`、`INVENTORY missing=2 failures=0` | 对 `open_public_comic_page` 而言 JPEG/ZIP 是必需文件，却在「可选媒体」口径下不使命令失败；以 exit code 做 Gate 会漏检 JA 页面丢失，与「命令失败状态要明确」有张力 | 对声明 READY/smoke 的 case，其必需媒体缺失计入 failures（或增加 `--strict`）；如保留现语义，应在 README 显式给出 exit code 口径 |
| P2-4 | `test_assets/comic_golden_suite/日漫_JA/.gitignore:7-14` | `git check-ignore --no-index -v` 对假想路径 `02_public_annotations/Manga109Dialog/evil.jpg`、`…/COO-…/v2022.07.07/evil.png`、`02_public_annotations/evil.zip` 全部 **NOT_IGNORED**（根 `.gitignore` 无媒体全局规则） | 白名单目录内任何非 XML 文件（含受限图像/归档）都不会被忽略，未来误 `git add` 会直接进 Git。当前提交 0 违规，仅规则不完整 | 在白名单目录内追加 `*.jpg`/`*.jpeg`/`*.png`/`*.zip` 等忽略规则，或改为逐文件名精确白名单 |

#### P3

| ID | 位置 | 说明 / 建议 |
|---|---|---|
| P3-1 | `doc/STATUS.md:22` | `Planned next` 仍写「Execute M2-TA2A public asset acquisition」，与 `in_progress`+资产已交付的证据滞后；集成时回填为 Review/Integration 状态 |
| P3-2 | `tools/assets.py:800-807` | 缺 annotation 时 `INVALID_INVENTORY` 与 per-case `READY` 行并存（实测），虽有 EXIT 1；建议 SUMMARY 增补整体 `FAILED` 标记，避免读者误解 |
| P3-3 | `tools/assets.py:547-596` | Webtoon 下载未校验重定向目标 host（公开页下载器有 strict redirect handler）；且 `:559-560` 的 `ValueError` 不在 case 级 try 内，manifest 错误会中断整个 CLI 而非记为该 case 失败 |
| P3-4 | `tools/assets.py:554-556` | Webtoon 已存在文件直接 skip、不校验有效性；损坏文件不会在 `download` 中被发现或修复（`verify` 可发现） |

---

### 四、资产状态 vs Pipeline 状态（严格区分）

- **资产 `READY`（仅文件完整性）**：JA 公开页 J38–J47（10 JPEG + 2 ZIP，40,284,868 B）、KO K01–K10（80 文件，884,913,245 B，实测排除 `.gitignore/.gitkeep`）。
- **`PARTIAL`**：COO 37 XML+license（3,333,257 B，`<onomatopoeia>` 含日语拟声词+坐标，已解析）、Manga109Dialog 37 XML+license（3,406,525 B，`<speaker_to_text>` ID 关系，非对白 transcription）。
- **`BLOCKED_BY_ASSET_ACCESS`**：Manga109 图像 0、JMangaBench_Mixed 0（code-only）、Text Mask 0。
- **`MISSING`**：OpenMantra（CC BY-NC 4.0 范围未确认）、KO Pepper&Carrot O01–O08。
- **Pipeline：全部 `NOT_RUN`**（OCR/Detection/Translation/Inpainting/Typesetting/Reading Order/SFX/Speaker/Webtoon slicing 等），`READY` 不代表任何应用链路通过——文档、inventory `pipeline_execution_status` 与实测一致。

Task 状态核对：`cases.json` 65 Case ID 唯一（10 KO Webtoon + 8 KO Pepper&Carrot + 37 Manga109 + 10 JA 页面）；smoke ja=10 / ko=10；`local_path` 全部 Windows 兼容、无绝对路径/反斜杠/盘符；baseline JA smoke 由 J01–J10（gated）调整为 J38–J47（公开页）与 README 声明一致。

---

### 五、审查副作用（如实披露）

审查期间为绕过 pytest 沙箱限制，在 worktree 根创建了两个 scratch 目录 **`.review-tmp-basetemp`、`.review-tmp2`**，沙箱拒绝删除（`WinError 5`，`rmdir`/`shutil.rmtree` 均失败）。两者为**未跟踪、空目录**，不在本 commit 内，但会以「Permission denied」噪声出现在 git 输出。请在普通权限 shell 中执行：
`Remove-Item -Recurse -Force ".review-tmp-basetemp",".review-tmp2"`。除此之外工作树无任何改动。

---

### 六、推荐下一步

1. Codex 在集成前裁决 4 项 P2：至少补齐 `日漫_JA/.gitignore` 白名单目录内的媒体忽略规则（P2-4）并明确 README 的 `verify/list/missing`/exit code 口径（P2-2、P2-3）；P2-1 由用户/验收方裁定是否要求 KO 纳入 checksum。
2. 清理上述两个 scratch 目录（非本 Task 产物）。
3. Review 已闭环、无 P0/P1：若 P2 按上条处置，可进入 Codex 集成验证；**M2-TA2B 仍为 gated follow-up，无需释放新 Task**。
