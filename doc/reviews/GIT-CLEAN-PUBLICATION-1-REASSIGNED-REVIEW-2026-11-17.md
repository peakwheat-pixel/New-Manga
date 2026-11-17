---
task_id: GIT-CLEAN-PUBLICATION-1
reviewer: reviewer-gcp1
reviewer_kind: subagent
reviewer_source: DSH 子 agent `reviewer-gcp1`（父 agent `lead`；独立上下文；未参与该 Task 的实现或返修）
author: Codex
base_commit: 349e61faff5f93067af5d4ce2d9e394e0d665b8c
reviewed_head: e34a90d001cce1fa966aec7d2b032bb5ad1cf148
observed_main_head: 24c573d1b7573736b6dc63f8e0a151659211f81a
reviewed_at: 2026-11-17T12:46:16+08:00
review_kind: reassigned-independence-review
decision: APPROVED_FOR_CLOSEOUT_WITH_LIMITATIONS
---

# Review：GIT-CLEAN-PUBLICATION-1（改派后独立复核）

## 0. 复核身份、范围与只读边界

- **Reviewer**：`reviewer-gcp1`（DSH 子 agent，父 agent 为 `lead`）。本会话为**独立上下文**，未参与 `GIT-CLEAN-PUBLICATION-1` 的实现、诊断、返修或 push；`reviewer_kind: subagent`。
- **复核对象**：Task 卡 `doc/tasks/GIT-CLEAN-PUBLICATION-1.md`、其 Canonical Evidence 表、`verification/GIT-CLEAN-PUBLICATION-1/**`、独立候选仓 `source-export-r4`、`review-package`/`review-package-r2`、DIAG 证据、push 记录与本地 publish 副本。
- **固定 head**：`reviewed_head = e34a90d001cce1fa966aec7d2b032bb5ad1cf148`（独立候选仓单 root commit）；`base_commit = 349e61faff5f93067af5d4ce2d9e394e0d665b8c`（源 main 基线）。
- **主仓观测 head**：`24c573d1b7573736b6dc63f8e0a151659211f81a`（复核开始时的 `main`；本复核不把它当作被审 head）。
- **只读声明**：本复核除写入本报告外，未修改任何文件；未执行 `git push`、未改 frontmatter、未改 `verification/**` 既有字节、未清理或移动候选/缓存/证据。复核期间观察到工作区出现其他 Agent 的未提交修改（不完整列举：`doc/tasks/AC-BLOCKED-CLOSE-1.md`、`DOC-CTRLCHAR-FIX-2.md`、`FEA-07.md`、`HUMAN-VS-AGENT-SPLIT-1.md`、`SIDECAR-SCHEMA-STALE-1.md`、`verification/DOC-CTRLCHAR-FIX-1/ctrlchar-scan-and-fix-2026-11-17.log`、`verification/GATE3-SETTINGS-SHORTCUT-1/` 等），非本复核产生，本复核未触碰。
- **时间**：`2026-11-17T12:46:16+08:00`（Asia/Shanghai）。
- **独立性说明**：2026-10-31 用户裁决已把 Review 独立性改为“上下文独立”；本复核为该口径下的 subagent 审查，作者 Codex 与本复核无同会话关系。Task 卡 frontmatter 的 `reviewer: Antigravity` 为历史字段，按 `doc/handoffs/NEXT-SESSION-STARTER.md:285-291` 应在真正改派复核时更新；本报告即为改派后的 Review 记录，见 CP-4。

## 1. 结论摘要

**decision: `APPROVED_FOR_CLOSEOUT_WITH_LIMITATIONS`。**

理由（按证据顺序）：

1. **AC1–AC3 的 `<<MET>>` 与实测一致**：724/724 源文件可追溯到 `349e61f`，源 blob、源 sha256、候选 sha256、字节数全部一致；6 个生成夹具与 3 个控制文件恰使 tracked = 733；338/338 禁止对象在候选对象库缺失；候选为单 root、无 parent、无 remote、1 个 loose ref、`fsck --strict` exit 0。
2. **AC4 的 `<<BLOCKED>>` 如实**：前端 435 passed（r3，tree 与 r4 相同）、r4 构建 exit 0；Rust r4 串行 153 passed / 0 failed / 1 ignored / 12 filtered；Core r2 771 passed / 3 failed；r4 默认并发 151/2（DIAG 记录）；packaged 12/0/154 仅在 DIAG 独立验证。没有任何把失败/未跑改成 PASS 的迹象。
3. **AC5 的 `<<PARTIAL>>` 方向如实**：delivery_head、Handoff、59 项 Canonical Evidence 均已形成且 pin 全匹配；但产品级 Gate 未关闭（AC4），且后续 head 的独立 Review 未闭合。按用户硬约束，**不得把 AC5 改为 MET**。
4. **push 记录可核到“本地可解析 + 本地副本可复算”的程度**：`e34a90d`、`892b9469e2fc...`、`e8147c6c8a...`、`ac7d488e1944...` 均在至少一个本地 Git 对象库中可 `cat-file -t` 解析；2026-10-26/2026-11-02 快照的文件数、字节数与顶层构成可由本地 publish 副本复算。**但现场 `git ls-remote` 因网络/代理不可达失败**，远端状态只能视为“记录 + 本地副本”间接可核，不是现场远端核验（见 §5、L-7）。
5. **可以收口为 `closed_with_limitations`，但不能收口为 `done`**：本 Task 的实质是“导出独立干净源码快照并在用户授权后推送”，该目标已由固定候选与 push 记录完成；剩余 AC4/AC5 是产品级 Gate 与证据边界，应原样保留并登记限制。收口前必须完成 §4.2 的资源核销、§4 的收口依据登记、STATUS 指针更正与本报告登记（CP-1…CP-6）；未完成这些程序项前不得改 status。

**P0 = 0，P1 = 0，P2 = 5，P3 = 5。** P1 为 0 表示“没有必须补做新实验/新修复才能判断的实质缺陷”；CP-1…CP-6 是收口程序门，不是本 Review 的 P1 finding，但未完成即不得改 `closed_with_limitations`。

## 2. AC1–AC5 逐条核验

| AC | 卡面陈述 | 本次实测证据 | 裁定 |
|---|---|---|---|
| **AC1** | 724 个源文件、6 个生成夹具文件与逐文件源/导出指纹清单已核验 `<<MET>>` | `SOURCE_MANIFEST.json` 724 条：`source_missing=0`、`blob_mismatch=0`、`source_sha256_mismatch=0`、`candidate_sha256_mismatch=0`、`bytes_mismatch=0`；生成 6 项（5 PNG + `samples/manifest.json`）；tracked=733，额外文件恰为 `README.md`/`.gitignore`/`SOURCE_MANIFEST.json`；2 处 transform（`packaging/m2ac5/README.md`、`tests/core/test_core_detect.py`），733 文件内 `49745` 残留 0 | **MET 成立** |
| **AC2** | 338 个禁止对象缺失，素材/历史/日志排除及凭据命中裁定可核查 `<<MET>>` | 从 `audit/V1-FULL-AUDIT/evidence/push-material-disposition.json` 取 169 行、去重 338 个 ID；对候选 `git cat-file --batch-check`：**present=0 / absent=338**；候选树 733 项中 `.jpg/.jpeg/.zip/.db/.sqlite/.7z/.rar` 均 0；二进制 6 项 = `icon.ico` + 5 个合成 PNG；无 symlink、无 submodule | **MET 成立** |
| **AC3** | 候选独立单一根提交、无 remote、原 main/index 与 P04 指纹不变 `<<MET>>` | 候选 `rev-list --count HEAD=1`、`rev-list --parents -n 1` 仅自身（无 parent）、`show-ref` 仅 1 个 loose ref、`remote -v` 空、无 alternates/packed-refs/shallow/grafts/replace、`fsck --full --strict` exit 0、tracked 733、工作树 clean；候选对象库不含 `349e61f` 与 `e8147c6`（无共享对象库）；6 个 P04 pin 文件 `push-worktree-ownership.json` **6/6 sha256 匹配**；`349e61f` 仍是当前 main 的祖先 | **MET 成立（时点口径）**：AC3 的“原 main 不变”指 2026-10-24 冻结时点；当前 main 已前进到 `24c573d`，不得读成“当前 main 仍等于 349e61f”，见 L-3 |
| **AC4** | 前端 435 通过/构建通过，Rust 串行 153/1 忽略/12 过滤；Core 771 通过/3 失败 `<<BLOCKED: Core三组参数失败且旧icacls错误码未知，默认并发registry失败复现，packaged以诊断记录为准>>` | `frontend-tests-r3.log` 尾：`Test Files 45 passed (45)` / `Tests 435 passed (435)`；`frontend-build-r4.log`：`✓ built`；`rust-tests-r4-serial.log` 尾：`153 passed; 0 failed; 1 ignored; 12 filtered out`；`core-tests-r2.log` 尾：`3 failed, 771 passed`（同一参数化用例 3 组参数）；DIAG `rust-default-parallel-r2`：`151 passed / 2 failed / 1 ignored / 12 filtered`、exit 101；DIAG packaged：`12 passed / 0 failed / 154 filtered`、exit 0（仅 e34 的 packaged 源码，不构成产品 release）；旧 icacls `returncode/stderr` 仍 `UNKNOWN` | **BLOCKED 如实**；不得改 MET |
| **AC5** | 固定 SHA、Handoff 及冻结证据已形成 `<<PARTIAL: DSH r1独立Review为blocked，补充证据不等于批准push或Task完成>>` | `delivery_head=e34a90d` 在 frontmatter 与 `HANDOFF.md:6` 一致；`RESULT.md`、`HANDOFF.md`、`checkpoint.md` 存在；59 项 Canonical Evidence 全部 SHA 匹配；`dsh-review-r1.md` decision=`blocked`；后续 `antigravity-review-push-r1.md` 对 `e34a90d` push-gate 判 `approved`，且 `PUSH_RECORD_2026-10-25.md` 记录实际 push exit 0 | **PARTIAL 方向如实，但理由已过时**：AC5 行末“补充证据不等于批准push”在 2026-10-25 之后已被 push-gate approved + 实际 push 取代；保留 PARTIAL 正确（产品 Gate 未闭），但收口时必须以追加说明更正理由，见 F-02、L-2 |

**结论**：AC1–AC3 与实测一致；AC4 的 `BLOCKED`、AC5 的 `PARTIAL` 均未把失败/未跑写成通过，**不存在绿洗**。AC5 的理由需要追加更正，但不改变 PARTIAL 状态。

## 3. Canonical Evidence pin 抽查（问题 2）

### 3.1 方法

- 对 Task 卡 Canonical Evidence 表**全部 59 行**（EV 9 + SRC 37 + SUP 3 + DB 3 + DISP 5 + PUSH 2）逐行用 `Get-FileHash -LiteralPath <path> -Algorithm SHA256` 复算；路径含空格，统一用 `-LiteralPath`。
- 另用 Python `hashlib.sha256` 对 724 个 `SOURCE_MANIFEST` 文件与源 blob 做复核；结果与 PowerShell 一致。
- **实测：59/59 行全部 MATCH，0 MISMATCH，0 MISSING。**

### 3.2 抽查表（覆盖 CANONICAL / SOURCE_PIN、仓内 / 仓外）

| evidence_id | class | path | 记录 sha256 | 实测 sha256 | 一致? |
|---|---|---|---|---|---|
| EV-SOURCE | SOURCE_PIN | `G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1/source-export-r4/SOURCE_MANIFEST.json` | `be511fdb668ea9239ff1acdac6b2d52a74d57917e947339155bd76087a071d6a` | 同左 | ✅ |
| EV-GRAPH | CANONICAL | `G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1/review-package/validation.json` | `40d812e737f169b3dd9b915179fadf467cb120876833b64fc0553f1255c46d0e` | 同左 | ✅ |
| EV-R4 | CANONICAL | `.../review-package/checks-r4.json` | `65733bec9122f26452ee594c003cece891672c616463dca3ee25e7abfc3ae417` | 同左 | ✅ |
| EV-RUST | CANONICAL | `.../review-package/rust-tests-r4-serial.log` | `ab66e07c335a43a38b17ce945976d694dae7358861a9361d45327e6443616db7` | 同左 | ✅ |
| EV-CORE | CANONICAL | `.../review-package/core-checks-r2.json` | `5b6db7169948050d1d8079fe34a1e080b5b4d982d2b24dd8ad32038cd65d02a6` | 同左 | ✅ |
| EV-FRONTEND | SOURCE_PIN | `.../review-package/frontend-tests-r3.log` | `56f025c20e8a85aff29e827be7a1e07bf9919ca2082b6445d3758b8d82cc49da` | 同左 | ✅ |
| SRC-01 | SOURCE_PIN | `G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/checkpoint.md` | `0418afe62d547b1afd4d9100ef5506f562521667bf4cfe66a2d43f7c0f529d5d` | 同左 | ✅ |
| SRC-19 | SOURCE_PIN | `G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/HANDOFF.md` | `ca788a28a3f402ddb494d7ae9f00a37a77f7140b397f538c08973cae20108344` | 同左 | ✅ |
| SRC-37 | SOURCE_PIN | `G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/validation.json` | `40d812e737f169b3dd9b915179fadf467cb120876833b64fc0553f1255c46d0e` | 同左 | ✅ |
| SUP-38 | SOURCE_PIN | `.../review-package-r2/PACKAGE_MANIFEST.json` | `17a774a5f143f1ab03612fcf30ca94d2e11d392dd97e1640c868d9f6cffd1210` | 同左 | ✅ |
| SUP-39 | SOURCE_PIN | `.../review-package-r2/forbidden-object-fingerprints.json` | `de7f98c103c22d399505042835aa0c6ca045491f00f5fe55affc1b4607bba31e` | 同左 | ✅ |
| DB-41 | SOURCE_PIN | `.../GIT-CLEAN-PUBLICATION-DIAG-1/core-r2-source-pins/test_export_hook_effective_opt0/library.db` | `cafc7f9a04445771b6e765f9c583363630de1cb472378abd09b5b93510573c7f` | 同左 | ✅ |
| DISP-05 | SOURCE_PIN | `.../review-disposition-r1/VALIDATION.json` | `50e7b3ff2118368d63a5accb105893747629f9833a94b2a6959255a3e2c23920` | 同左 | ✅ |
| PUSH-02 | CANONICAL | `G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/antigravity-review-push-r1.md` | `144d9761f90f257bef9686f435af59c398f305ad015760540c38c7fe5b9dc852` | 同左 | ✅ |

> 说明：表中 `...` 省略的是同一 `G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1/` 前缀；实际复核使用完整路径。**全表 59/59 通过；抽表 14/14 通过。**

## 4. 结构证据复算（AC1–AC3 的独立重算）

### 4.1 候选仓

| 检查 | 命令 | 实测 |
|---|---|---|
| 根提交数 | `git rev-list --count HEAD` | `1` |
| parent | `git rev-list --parents -n 1 HEAD` | 仅 `e34a90d...`，无 parent |
| refs | `git show-ref` | 仅 `refs/heads/codex/clean-source-snapshot` |
| remote | `git remote -v` | 空 |
| 隔离文件 | `Test-Path .git/objects/info/alternates` 等 | alternates/shallow/grafts/replace 均 False；无 packed-refs |
| fsck | `git fsck --full --strict` | exit 0 |
| tracked | `git ls-files` | `733` |
| 树规模 | `git ls-tree -r -l -z HEAD` | 733 项，8,086,267 B；无 symlink/submodule |
| 共享对象 | `git cat-file -t 349e61f...` / `e8147c6...` | 均 `fatal: could not get object info`（不共享对象库） |

### 4.2 SOURCE_MANIFEST（724 + 6 + 3）

- 724/724：`source_blob` 与 `git ls-tree -r 349e61f` 的 blob 完全一致；`source_sha256` 与源 blob 内容 sha256 一致；候选文件 sha256 与 `sha256` 字段一致；`bytes` 一致。
- 2 处 transform：`packaging/m2ac5/README.md`、`tests/core/test_core_detect.py`，均 `REDACT_PERSONAL_DIRECTORY_LITERAL`；全仓 733 文件检索 `49745` = **0 命中**。
- 6 个生成夹具：5 个 `experiments/TASK-016/samples/*.png` + `samples/manifest.json`；`generated_files` 均有 sha256。**本复核未重跑生成器**（只读约束；重跑会写候选目录），生成器可复现性依据 `dsh-review-r1.md` 的 6/6 逐字节记录 + 本复核的 manifest/文件 hash 一致性。
- 3 个新增：`README.md`、`.gitignore`、`SOURCE_MANIFEST.json`；tracked 集合无其他额外文件。

### 4.3 禁止对象（338）

- `push-material-disposition.json`：169 行；`outer_object` + `embedded_git_object` 去重 = 338。
- 对候选 `git cat-file --batch-check`：**present=0 / absent=338**。
- `review-package-r2/forbidden-object-fingerprints.json` 亦为 169 行 / 338 unique；其 `source_sha256=78e89cddb790e4409785110756cf9f8627d0b0d4f93a620f94360047c388b2bd` 与源 disposition 实测 sha256 一致。

### 4.4 P04 保护

- `audit/V1-FULL-AUDIT/evidence/push-worktree-ownership.json` 的 6 个 `diagnostic_p22_*.jsonl`：`Get-FileHash` **6/6 匹配**，字节数 6/6 匹配；说明 AC3 的“P04 指纹不变”在可核范围内成立。

### 4.5 两个本地 publish 副本（问题 3 的结构事实）

| 快照 | head | tracked | tracked bytes | 顶层构成（实测） | 禁区 / 图片 |
|---|---|---|---|---|---|
| `publish/clean-snapshot-20261026` | `e8147c6c8a7edde4e5784999454acb5732a869fb`（父 `892b9469e2fc...`） | 875 | 15,772,089 B（约 15.04 MiB） | apps 283 / src 243 / tests 226 / **test_assets 86** / packaging 18 / tools 14 / root 5 | 无 `verification/doc/audit/wiki/archive/experiments/...`；仅 `icon.ico` 1 个图片 |
| `publish/clean-snapshot-20261102` | `ac7d488e1944893f961b94eb3d774c899f618829` | 1413 | 21,120,652 B（约 20.14 MiB） | apps 776 / src 254 / tests 249 / test_assets 86 / packaging 23 / tools 13 / root 11 / doc 1 | `doc/` 仅 `doc/design/redesign-v1/40-fusion/tokens.json`（推送记录已披露）；仅 `icon.ico` 1 个图片 |

> 2026-10-26 卡面写 `test_assets(81)`，实测 86；卡面各项 283+243+226+81+18+14+5=870，不等于 875。总量 875 正确，分项错误（P3，F-06）。卡面“15.3 MB”与实测 tracked 15,772,089 B 近似（15.04 MiB / 15.77 MB 十进制），不是精确值。

## 5. push 记录与 hash 可解析性（问题 3）

### 5.1 本地 `git cat-file -t` / `rev-parse` 结果

| hash | 主仓 `G:/CODEX/New Manga` | `publish/clean-snapshot-20261026` | `publish/clean-snapshot-20261102` |
|---|---|---|---|
| `e34a90d001cce1fa966aec7d2b032bb5ad1cf148` | commit | 无此对象（独立对象库） | 无此对象 |
| `892b9469e2fc2fe494ff4c469d1e54e94dcef571` | commit | commit | 无此对象 |
| `e8147c6c8a7edde4e5784999454acb5732a869fb` | commit | commit | 无此对象 |
| `ac7d488e1944893f961b94eb3d774c899f618829` | 无此对象 | 无此对象 | commit |
| `6a68fdeb92d8a1c7903166a8076d6260bf8fa79a` | commit | — | — |
| `349e61faff5f93067af5d4ce2d9e394e0d665b8c` | commit | — | — |
| `a3c936f68748047aee41c4c60d732adc5bdf55f7` | commit（parent=`349e61f...`） | — | — |

**结论**：所有被引用的完整 40 位 hash 均在至少一个本地对象库可解析；**没有发现伪造/不可解析的 40 位 hash**。`e34a90d` 属于独立候选仓/主仓；`892b9469`/`e8147c6` 属于 2026-10-26 快照；`ac7d488e` 属于 2026-11-02 快照；三者对象库彼此独立，符合“独立根提交、无共享历史”的设计。

### 5.2 三份记录的一致性

| 记录 | 关键值 | 实测/交叉核对 | 结论 |
|---|---|---|---|
| `doc/PUSH_RECORD_2026-10-25.md:15,39-45,59-61` | push `e34a90d` → `refs/heads/codex/clean-source-snapshot`；exit 0；远端 main `6a68fdeb` | 候选/主仓可解析 `e34a90d`；候选无 remote；`antigravity-review-push-r1.md:115` approved 仅 bind `e34a90d`；`doc/tasks/GIT-CLEAN-PUBLICATION-1.md:193-197` 与记录一致 | **内部一致**；远端状态见 L-7 |
| 卡面 `## 2026-10-26 实际发布记录`（`:200-216`） | 首次 `892b9469e2fc...`；875 files / 15.3 MB；test_assets(81) | publish 副本 head `e8147c6`，父 `892b9469`；875 files；15,772,089 B；test_assets **86**；无禁区目录 | **hash/文件数一致；分项计数错误（F-06）** |
| 卡面 `## 2026-10-26 快照同步（第二次）`（`:218-225`） | `892b946..e8147c6`；远端 `clean-snapshot-20261026=e8147c6` | publish 副本 `show-ref`：`refs/remotes/origin/clean-snapshot-20261026=e8147c6`；`doc/PUSH_RECORD_2026-11-02.md:60` 同 | **一致** |
| `doc/STATUS.md:22` | `clean-snapshot-20261026=892b946e`、`clean-snapshot-20261102=ac7d488e` | `892b946e` **不是可解析 hash**（`git cat-file -t 892b946e` fatal）；正确首个提交是 `892b9469`；当前 branch head 是 `e8147c6`；`ac7d488e1944...` 在 2026-11-02 副本可解析 | **20261026 值错误（笔误且非 head）**；20261102 正确（F-01） |
| `doc/PUSH_RECORD_2026-11-02.md:15,58-63` | `ac7d488e1944...`；1413 files；21,120,652 B；远端 `clean-snapshot-20261026=e8147c6` | 2026-11-02 副本：1413 files、21,120,652 B、head `ac7d488e1944...`；20261026 副本 head `e8147c6` | **一致** |

### 5.3 现场远端核验的边界

尝试执行只读：

```text
git ls-remote --heads https://github.com/peakwheat-pixel/New-Manga.git
```

实测失败：

```text
fatal: unable to access 'https://github.com/peakwheat-pixel/New-Manga.git/':
Failed to connect to github.com port 443 via 127.0.0.1 after 2102 ms: Could not connect to server
exit=128
```

因此：**远端 refs 的“当前值”未能在本复核中现场核验**；本报告只确认“本地记录 + 本地 publish 副本 + 本地对象”一致。`doc/STATUS.md:22` 的 `ac7d488e` 与 `doc/PUSH_RECORD_2026-11-02.md` 的 `e8147c6` 都只能算“记录层一致”，不能写成“远端现场已核验”。这不推翻 2026-10-25 的 push-gate review 或 2026-10-26/11-02 的推送记录，但必须作为 L-7 限制登记。

### 5.4 远端 main 的时间线

- 卡面 2026-10-26 段（`:214`）与 `doc/PUSH_RECORD_2026-10-25.md:60`、`doc/PUSH_RECORD_2026-10-29.md:70`：远端 main = `6a68fdeb92d8a1c7903166a8076d6260bf8fa79a`。
- `doc/PUSH_RECORD_2026-11-02.md:62`：远端 main = `b1c1f5a56840988e149c18375f6e414bf5c7fbda`（“未变”）。
- 本卡未记录 `6a68fdeb → b1c1f5a5` 的变化来源；这不是本卡 push 造成的，但说明“远端 main 未变”只在该记录时点成立（L-12）。

## 6. Findings

### P0 = 0

无证据伪造、无私有对象泄漏、无不可恢复的数据/历史破坏。

### P1 = 0

没有“必须补做新实验/新修复才能判断”的实质缺陷；AC4/AC5 的阻断是已经披露的产品/环境 Gate，不是本卡的证据缺口。

### P2（5 条）

| ID | 级别 | 文件:行 | 触发与影响 | 实测命令/值 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| F-01 | P2 | `doc/STATUS.md:22` | 权威 STATUS 把 2026-10-26 分支写成 `892b946e`；该 8 位串不是可解析对象，且即使更正为 `892b9469` 也只是首提交，不是当前 head `e8147c6`。读者会拿错 hash | `git -C "G:/CODEX/New Manga" cat-file -t 892b946e` → `fatal: Not a valid object name`；`git rev-parse 892b9469` → `892b9469e2fc2fe494ff4c469d1e54e94dcef571`；`publish` 副本 head → `e8147c6c8a7edde4e5784999454acb5732a869fb` | 收口提交更正为 `clean-snapshot-20261026=892b9469（首提交）→e8147c6（当前 head）`，或只写 head 并注明首提交 | open |
| F-02 | P2 | `doc/tasks/GIT-CLEAN-PUBLICATION-1.md:44`；对照 `:191-197` | AC5 行末理由仍写“DSH r1独立Review为blocked，补充证据不等于批准push或Task完成”；但 2026-10-25 已有 `antigravity-review-push-r1.md` 对 `e34a90d` push-gate approved，并已实际 push。理由已过时；保留 PARTIAL 仍正确，但不能让读者以为 push 未获任何独立审查 | `antigravity-review-push-r1.md:115` decision=approved；`doc/PUSH_RECORD_2026-10-25.md:44-45` exit 0；AC5 仍 `[ ] <<PARTIAL>>` | 追加说明：PARTIAL 的理由改为“产品级 Gate 未闭 + 后续 head 的独立 Review 未闭合”；保留原行字节，不改写 | open |
| F-03 | P2 | 卡面 `:200-225`；`PUSH_RECORD_2026-11-02.md:53-64` | 2026-10-26 的 `892b9469→e8147c6` 与 2026-11-02 的 `ac7d488e` 是用户直接授权的快照分支推送，但 `verification/GIT-CLEAN-PUBLICATION-1/` 内没有覆盖这些精确 head 的 Appointment/Review；唯一 push-gate review 绑定 `e34a90d`。协议 §7 要求“任何新交付 head 重新 Appointment Review” | Appointment/Review 文件 bind `reviewed_head: e34a90d`；`git cat-file` 显示 `ac7d488e` 仅存在于 2026-11-02 副本；无对应 Review 文件 | 在卡面登记为 limitation：后续 head 的推送依据是用户直接授权，不是独立 push-gate 结论；若未来再推新 head，必须先 Appointment | open（限制） |
| F-04 | P2 | `verification/GIT-CLEAN-PUBLICATION-1/*.log`（19 个） | 19 个原始日志均无 EXIT/shell/venv 头；exit 只在 checks JSON。`review-package-r2` 有 19 个事后 envelope（标注 `RETROSPECTIVE_ENVELOPE...`、`venv=UNRECORDED`），不是原始运行头。Q-009 证据纪律未完全满足 | `Get-ChildItem -Filter *.log` → 19；`Select-String -Pattern '^EXIT|^exit=|Exit code'` → 0 命中；`DIAG RESULT.md:34` 明确 envelope 为事后整理 | 收口限制登记；不重跑已到上限的 Core 失败来补头；新运行必须即时写 RUN_HEADER/EXIT | open（限制） |
| F-05 | P2 | 候选工作树 `apps/desktop/frontend/node_modules`、`dist`、`verification/P04/diagnostic_p22_692_1792842383784.jsonl` | 候选 live 工作树不是纯 tracked 目录（ignored 产物 3 类；node_modules 约 84 MB、dist、jsonl 含本机路径）。以目录/zip 交付会携带构建产物与本地路径；Git 对象交付不受影响 | `git status --porcelain --ignored` → 3 行；`git clean -ndX` 列出 3 项；worktree 90.8 MB vs tracked 8,086,267 B | 卡面限制：只允许 Git 对象/分支交付，禁止复制/压缩 live 目录；已由 push 记录披露 | open（限制） |

### P3（5 条，minor）

| ID | 级别 | 文件:行 | 触发与影响 | 实测值 | 建议 |
|---|---|---|---|---|---|
| F-06 | P3 | 卡面 `:207` | 2026-10-26 快照分项 `test_assets(81)` 与实测 86 不一致；各项相加 870，不等于总量 875 | `git ls-tree -r HEAD -- test_assets` = 86；总量 875 正确 | 改为 `test_assets(86)` 或只保留总量，收口说明中标注 |
| F-07 | P3 | `SOURCE_MANIFEST.json` `generated_files[5]` | 第 6 个生成物 `experiments/TASK-016/samples/manifest.json` 缺 `generator` 字段（另外 5 个有）；`RESULT.md` 有文字说明，但机器清单未闭合 | Python 读取 `generated_files`：5 项含 generator，1 项不含 | 在收口说明中注明该 manifest 由同一 generator 创建；不改候选字节（head 冻结） |
| F-08 | P3 | 卡面 Canonical Evidence 表 `:70-134` | `doc/PUSH_RECORD_2026-10-25.md`、`doc/PUSH_RECORD_2026-11-02.md` 是 push 结论的关键记录，但不在 Canonical Evidence 表内、无 SHA pin；目前只有 git-tracked 文档 | 表中 PUSH-01/02 只 pin Appointment/Review，无 push record 行 | 收口提交可把两份 push record 作为新增 SOURCE_PIN（append-only），或明确它们只是交付记录、不属 AC pin |
| F-09 | P3 | `verification/GIT-CLEAN-PUBLICATION-1/validation.json:62`、`snapshot.json:12-13` | 冻结字段 `review: NOT_RUN`、`push: NOT_AUTHORIZED` 是 2026-10-24 冻结时点值；卡片后续已记录 r1 blocked 与实际 push。单独读这两个冻结文件（validation 为 CANONICAL、snapshot 为 SOURCE_PIN）会误以为“从未 review/push” | 文件值 vs 卡面 `:154-225` | 收口说明注明“点值证据，冻结于 review/push 之前”；不改原字节 |
| F-10 | P3 | `doc/PUSH_RECORD_2026-10-25.md:60`、`doc/PUSH_RECORD_2026-10-29.md:70`；`doc/PUSH_RECORD_2026-11-02.md:63` | 远端 main 从 `6a68fdeb`（10-25/10-29）变为 `b1c1f5a5`（11-02），本卡未记录变化来源；不是本卡推送造成，但“远端 main 未变”只适用于各自时点 | 三份记录逐字对比 | 收口限制注明该时间线；不要把 10-25 的“main 未变”外推到 11-02 之后 |

## 7. 收口前置条件（CP，必须由 Lead 在改 status 前完成）

> 这些是 `doc/09_COLLABORATION.md` §4/§4.2 的程序门；未完成前，卡必须保持 `in_review`。它们不是本 Review 的 P1 finding，但**不能以“Review 已批准”为由跳过**。

- **CP-1｜收口依据**：在卡面新增 `## Closeout Record`（或等价追加段），写明 §4 的收口依据：AD-002 已批准并以 Avalonia/C#/.NET 取代 Tauri/React 旧栈（`AGENTS.md:54`；旧栈仅保留历史证据），本卡剩余 AC4 的 frontend/Rust 部分属于旧栈验证；Python Core 仍属当前架构，其 Core 3 项环境失败仍作为 limitation 保留，不冒充被 AD-002 取代。若 Lead 认为这不构成 §4 的“用户明确裁决/目标架构取代”，则**不得**改 `closed_with_limitations`，应保持 `in_review` 并请用户书面裁决。
- **CP-2｜资源核销**：按 §4.2 完成 `Resource Manifest` 的实际行（4 个本地候选 `source-export`/`r2`/`r3`/`r4`、`cargo-target`、`rust-check-environment*`、`pytest-temp-*`、`review-package`/`review-package-r2`、DIAG task-env），全部标 `PRESERVE_REFERENCED`（不删除、不移动，因仍被 Review/证据引用），把 `resource_closeout_status` 从 `pending` 置 `complete`；不得把“待生成”占位留在终态。
- **CP-3｜指针更正**：更正 `doc/STATUS.md:22`（`892b946e` → 首提交 `892b9469e2fc...` + 当前 head `e8147c6c8a...`，或只写 head 并注明首提交）；把 `doc/TASK_LEDGER.md:47` 的 `GIT-CLEAN-PUBLICATION-1` 从 `in_review` 改为 `closed_with_limitations`（若最终收口）；同步 `doc/REBASELINE_PLAN.md:61` 的“表外节点”说明；不动历史记录。
- **CP-4｜Reviewer 登记**：按 `doc/handoffs/NEXT-SESSION-STARTER.md:285-291` 把 Task 卡 `reviewer:` 改为 `reviewer-gcp1`，写明 `reviewer_kind: subagent` 与来源（DSH 子 agent / 父 agent `lead` / 本报告路径）；保留 `antigravity-review-push-r1.md` 与 `dsh-review-r1.md` 原字节，历史署名不改写。
- **CP-5｜限制清单**：把 §8 的 L-1…L-12 追加进卡面（或 `## Closeout Record` 的 limitation 段），每条保留可核文件/命令；**不得**改 AC4/AC5 的 `<<BLOCKED>>`/`<<PARTIAL>>` 标记，不得删弱既有断言或证据行。
- **CP-6｜收口判定**：CP-1…CP-5 未全部完成前，Task 保持 `in_review`；完成后也只能置 `closed_with_limitations`，不得置 `done`，不得宣称产品发布验收或 Gate 通过。

## 8. 限制清单（建议写入卡面；每条一句话、可核）

1. **L-1｜AC4 保持 BLOCKED**：Core 为 771 passed / 3 failed（同一参数化用例的 3 组参数，`core-tests-r2.log` 尾），r4 默认并发为 151 passed / 2 failed / 1 ignored / 12 filtered / exit 101（DIAG `rust-default-parallel-r2`），packaged 的 12 passed / 0 failed / 154 filtered / exit 0 仅为 DIAG 对 e34 packaged 源码的独立验证，不改写为产品通过。
2. **L-2｜AC5 保持 PARTIAL**：`delivery_head=e34a90d`、`HANDOFF.md`、59 项 Canonical Evidence 已形成（59/59 sha256 MATCH），但产品级 Gate 未闭且后续快照 head 没有独立 Review 绑定，不得改 MET 或 `done`。
3. **L-3｜快照时点**：`delivery_head=e34a90d` 是源 main `349e61f`（2026-10-24）的快照，不含之后 main 的 AD-002/Avalonia/FEA 提交（复核时 main=`24c573d`），不得当作当前产品代码。
4. **L-4｜日志证据纪律**：`verification/GIT-CLEAN-PUBLICATION-1/` 的 19 个原始 `.log` 无 EXIT/shell/venv 头，`review-package-r2` 的 19 个 envelope 是事后整理且 `venv=UNRECORDED`，原始运行头不可追溯。
5. **L-5｜交付介质**：候选 live 工作树含 ignored `node_modules`（约 84 MB）、`dist` 与 `verification/P04/diagnostic_p22_692_1792842383784.jsonl`，只允许 Git tracked 对象/分支交付，禁止复制或压缩 live 目录。
6. **L-6｜后续 head 的审查缺口**：2026-10-26 的 `892b9469e2fc...`→`e8147c6c8a...` 与 2026-11-02 的 `ac7d488e1944...` 快照分支推送有用户直接授权记录（`doc/PUSH_RECORD_2026-11-02.md` 等），但没有覆盖这些精确 head 的独立 Review/Appointment；唯一 push-gate Review 绑定 `e34a90d`。
7. **L-7｜远端未现场核验**：本次 `git ls-remote --heads https://github.com/peakwheat-pixel/New-Manga.git` 因 proxy `127.0.0.1` 连接失败（exit 128），远端 refs 只能由本地记录与 `publish/clean-snapshot-20261026`/`20261102` 副本间接核验，未做现场远端确认。
8. **L-8｜STATUS hash**：`doc/STATUS.md:22` 的 `clean-snapshot-20261026=892b946e` 不可解析（正确首提交 `892b9469e2fc...`，当前 head `e8147c6c8a...`），收口前必须更正或加注。
9. **L-9｜分项计数**：2026-10-26 卡面 `test_assets(81)` 与实测 86 不符（283+243+226+81+18+14+5=870≠875），总量 875 正确但分项需更正。
10. **L-10｜生成物字段**：`SOURCE_MANIFEST.json` 的 `generated_files[5]`（`experiments/TASK-016/samples/manifest.json`）缺 `generator` 字段，第六个生成物来源仅在 `RESULT.md` 文字中闭合。
11. **L-11｜证据绑定口径**：Core 771/3 实测于 r2 `b1e6935`，前端 435 实测于 r3 `87accae`，不是 e34 同 head 重跑；绑定依赖 `src=1571a2ca84...`、`tests/core=da2f41fb16...`、`apps/desktop/frontend=662ad099f9...` 的 tree 等价。
12. **L-12｜产品 Gate 与远端 main 时间线**：安装包/签名/真实 GUI/模型/完整审计仍 `NOT_RUN`；远端 main 在 2026-10-29 记录为 `6a68fdeb`、2026-11-02 记录为 `b1c1f5a5`，本卡未记录该变化来源，不得把 10-25 的“main 未变”外推到 11-02 之后。

## 9. 验证覆盖与未覆盖

| 场景 | 命令/步骤 | 结果 | 证据 |
|---|---|---|---|
| Canonical Evidence 全表 | `Get-FileHash -LiteralPath ... -Algorithm SHA256` ×59 | **PASS 59/59 MATCH** | 本报告 §3；SHA 值逐行一致 |
| SOURCE_MANIFEST 724 | Python hashlib + `git ls-tree -r 349e61f` + `git cat-file --batch` | **PASS**：724/724 blob/source_sha256/candidate_sha256/bytes 一致；2 transform；0 残留 `49745` | 本报告 §4.2 |
| 338 禁止对象 | `git cat-file --batch-check` on 338 unique IDs | **PASS**：present=0 / absent=338 | 本报告 §4.3 |
| 候选 Git 隔离 | `rev-list`/`show-ref`/`remote -v`/`fsck --strict`/`ls-files`/`cat-file -t` | **PASS**：1 root、无 parent、无 remote、1 ref、fsck 0、733 tracked、无共享对象 | 本报告 §4.1 |
| P04 pin | `Get-FileHash` on 6 jsonl | **PASS 6/6** | `push-worktree-ownership.json` |
| 前端 435 / 构建 | 读 `frontend-tests-r3.log` 尾、`frontend-build-r4.log`、`checks-r4.json` | 435 passed；build `✓ built`；npm-ci/build exit 0 | 日志/JSON |
| Rust 串行 153 | 读 `rust-tests-r4-serial.log` 尾、`checks-r4.json` | 153 passed / 0 failed / 1 ignored / 12 filtered / exit 0 | 日志/JSON |
| Core 771/3 | 读 `core-tests-r2.log` 尾、`core-checks-r2.json` | 3 failed / 771 passed / exit 1；同一参数化用例 3 组 | 日志/JSON |
| r4 默认并发 | 读 DIAG `RESULT.md:9`、`dsh-review-r1.md` | 151/2/1/12 / exit 101；未裁决 | DIAG RESULT |
| packaged | 读 DIAG `RESULT.md:51`、`dsh-review-r1.md:46` | 12 passed / 0 failed / 154 filtered / exit 0（e34 packaged 源码） | DIAG |
| 2026-10-26 快照 | `git ls-tree -r -l -z HEAD`、`git ls-files` | 875 files / 15,772,089 B；test_assets 86；无禁区；icon.ico | publish 副本 |
| 2026-11-02 快照 | 同上 | 1413 files / 21,120,652 B；doc 1（tokens.json）；icon.ico 1 | publish 副本 |
| 远端 refs | `git ls-remote --heads https://github.com/...` | **NOT_VERIFIABLE**：proxy 连接失败 exit 128 | 本报告 §5.3 |
| 2026-10-26 tsc/vitest 567 passed | 未重跑（本地副本无 node_modules；重跑会安装依赖） | **NOT_RUN（本复核）**；仅核文件构成与记录 | `doc/tasks/GIT-CLEAN-PUBLICATION-1.md:209-213` |
| 2026-11-02 .NET 测试 / 11 failed | 未重跑（非本卡范围） | **NOT_RUN（本复核）**；记录保留 | `doc/PUSH_RECORD_2026-11-02.md:37-46` |
| 安装包/签名/真实 GUI/模型/完整审计 | 未运行 | **NOT_RUN** | Task/DIAG 边界 |
| 治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GIT-CLEAN-PUBLICATION-1.md` | **PASS (3 warnings)**，exit 0（复核时） | 命令输出 |

## 10. 明确声明

- 本复核**不构成产品发布验收**：安装包、代码签名、真实 GUI、真实模型、完整产品审计仍为 `NOT_RUN`；`Technical Gate=NOT_SATISFIED` 等既有 Gate 结论**不因本报告改变**。
- 本复核**不改变 AC4/AC5 的 `BLOCKED`/`PARTIAL`**，不建议把它们改成 `MET`，也不建议删除/弱化任何既有断言或证据行。
- 本复核**不批准任何新的 push**，也不把 2026-10-26/11-02 的推送追认为“已由独立 Review 覆盖”；它只判断该卡是否可以 `closed_with_limitations` 收口，以及收口必须携带的限制。
- 本复核**只读**：除本文件外未写入任何文件；`verification/**`、候选仓、publish 副本、Task 卡 frontmatter、`doc/STATUS.md` 等均未改动。若 Lead 需要更新卡面/STATUS/台账，请按 CP-1…CP-6 执行，不要改动本报告的证据值。

---

**复核者**：`reviewer-gcp1`（DSH 子 agent，独立上下文，未参与实现）
**复核时间**：2026-11-17T12:46:16+08:00
**reviewed_head**：`e34a90d001cce1fa966aec7d2b032bb5ad1cf148`
**base_commit**：`349e61faff5f93067af5d4ce2d9e394e0d665b8c`
**decision**：`APPROVED_FOR_CLOSEOUT_WITH_LIMITATIONS`
