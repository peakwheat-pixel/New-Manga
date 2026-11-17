# 收口复核报告：INSTALLER-MATRIX-1 / GIT-CLEAN-PUBLICATION-DIAG-1

- **reviewed_head**：`31dd81832`（`31dd8183293856c7810d10e48b1f13b23b0bf24a`，main）
- **reviewer**：`reviewer-inst`（DSH 子 agent；**独立上下文，未参与**两卡的实现、返修、Handoff、收口或证据生成）
- **复核时间**：`2026-11-17T18:13:16+08:00`（Asia/Shanghai）
- **复核方式**：只读。未提交、未推送、未 checkout、未修改被审文件；唯一写入 = 本报告。
- **被审范围**：`doc/tasks/INSTALLER-MATRIX-1.md`、`doc/tasks/GIT-CLEAN-PUBLICATION-DIAG-1.md`、`verification/INSTALLER-MATRIX-1/**`、`verification/GIT-CLEAN-PUBLICATION-DIAG-1/**`、两张新卡（`RELEASE-GATE4-SIGNED-MATRIX-1`、`MAPMINT-ERROR-FIDELITY-1`）及其在 `doc/REBASELINE_PLAN.md` / `doc/TASK_LEDGER.md` 的登记。
- **时点说明**：复核启动时本地 HEAD = `31dd81832`（当时领先 origin 1 个提交）。复核期间 Lead 继续推进，报告落盘时 HEAD = `4459a0602` = `origin/main`（新增 `9818e7bad` / `6619e70b9` / `4459a0602` 三个提交）。**本报告的全部判定只针对 `31dd81832`**；两张被审卡与两处 verification 目录在 `31dd81832..4459a0602` 间无字节变化（`git diff --stat` 为空），故卡级结论不受分支前进影响。后续 `MAPMINT` 改判 `superseded`、`TASK_LEDGER` 计数修正属被审 head 之后的处置，不纳入本报告判定。
- **复核输入说明**：`verification/GIT-CLEAN-PUBLICATION-DIAG-1/r2/DISPOSITION.md` **不存在**；本项目唯一的 `r2/DISPOSITION.md` 在 `verification/GIT-CLEAN-RUST-ISOLATION-1/r2/`。L-D-4 的一致性按该文件核对（见 B6）。

## 0. 结论先行

| 卡 | decision | P0 | P1 | P2 | 能否保持 `closed_with_limitations` |
|---|---|---:|---:|---:|---|
| `INSTALLER-MATRIX-1` | **ACCEPTED_WITH_FINDINGS** | 0 | 2 | 4 | **可以有条件保持**（需 append-only 补登两条 P1 限制；见 §5） |
| `GIT-CLEAN-PUBLICATION-DIAG-1` | **ACCEPTED_WITH_FINDINGS** | 0 | 0 | 2 | **可以保持** |

跨卡治理另登记 1 条 P2（TASK_LEDGER 跟踪计数，见 §4）。合计：**P0 = 0；P1 = 2；P2 = 7**。

**未出现的坏情形（本复核重点核查）**：

1. AC7 **没有**被改成 `[x]` / `<<MET>>`，仍为 `[ ]` + `<<PARTIAL: …NOT_RUN…>>`。
2. 两卡都没有被置为 `done`，`integration_commit` 仍为 `null`；DIAG 卡「不集成本 Task、不置 done」原文保留。
3. 没有把 `Technical Gate` 或条件 4 宣称为通过；DIAG 的 AC3 仍 `<<PARTIAL>>`，RUST-ISOLATION 的 AC3 仍 `<<BLOCKED>>`。
4. `31dd81832^..31dd81832` 对 `verification/` 的 diff 为空；两卡的历史证据字节未被本次收口改动。

**出现的问题（不推翻收口方向，但必须登记/修补）**：

- INSTALLER 的 r1 P1 `F-02` **只修了一半**：`app/VERSION.json` 已改写为 0.1.1 真值，但包内 `package-manifest.json` 仍是 2026-10-28 的 `0.1.0` 残留，且随安装包落盘；卡面 `Closeout Record` 的 L-IM-1..5 未登记。
- INSTALLER 的 r1 P1 `F-03` **未结**：包是 `variant=base` 却内置 632,552,582 B 权重，随包 `NOTICE.md` / `LICENSE_AUDIT.md` 仍写「base 不含权重、models 变体 AGPL-3.0」，根 `VERSION.json` 却按 `GPL-3.0-or-later` 分发；`LICENSE_AUDIT.md` 对 rtdetr/OCR 权重写「待核实」。该项未进入 L-IM 限制清单。

## 1. 10 项逐条判定表

> 判定口径：PASS = 实测与卡面/证据一致；PASS_WITH_FINDINGS = 主结论成立，但有需登记/修补的偏差；FAIL = 与卡面不符且影响结论。

| # | 复核项 | 实测值（关键） | 判定 |
|---|---|---|---|
| A1 | **AC1–AC6 真实** | stage `1,037 files / 889,353,540 B`（= 848.15 MiB）；`setup.exe` `652,107,016 B`（621.9 MiB）sha256 `0c041599…58f06`；stage exe `99,554,850 B` sha256 `a3ec2133…9230`，`ProductVersion=0.1.1+71cecb95a…`；`core_service.exe` `400,098 B` sha256 `605088…52ee`，mtime `2026-11-14T19:16:55.3503345Z`；models 三件合计 `632,552,582 B`；`host.log` 含 `core_service ready` / `host_bridge ready` / `credential port ready` / `self-check status=Passed`；README 记用户数据根 `532 files / 967,726,273 B`，前后 SHA-256 均 `6ae4d6da…46d9b2`。**卡面数字与证据一致**。AC4/AC6 只有 README §3 汇总，无独立 pin 的 install/uninstall 原始 transcript（P2-IM-3）。 | PASS_WITH_FINDINGS |
| A2 | **AC7 未被偷改通过** | `31dd81832` 卡面第 90 行为 `- [ ] … <<PARTIAL: 未在打包产物上逐页导航（NOT_RUN）；不以 headless 结果冒充；见 §限制 L-IM-2>>`；无 `[x]`、无 `<<MET>>`；`git diff 31dd81832^ 31dd81832` 中只新增该 `<<PARTIAL>>` 标记，语义未变。 | PASS |
| A3 | **CE 10 行 sha256** | 以 `998e04ae4` 的 Git blob 独立重算，**10/10 全部 MATCH**（不止抽 5 行）：`EV-IM-01` `6dac2fcc…5ac5`（CANONICAL）、`EV-IM-09` `f80bdcd4…27ef`（CANONICAL）、`EV-IM-02` `27782980…d30b`、`EV-IM-03` `ab0e416d…4f68`、`EV-IM-04` `90b8897a…8116`、`EV-IM-05` `2de165cc…88ef`、`EV-IM-06` `149f79fc…db22`、`EV-IM-07` `8cd0ab1f…a636`、`EV-IM-08` `90b8897a…8116`、`EV-IM-10` `d391ca4e…d5e3`。与卡面逐字相同。 | PASS |
| A4 | **INSTALLER 资源核销** | `G:/CODEX/New Manga.workspace/task-envs/INSTALLER-MATRIX-1/RESOURCE-MANIFEST.json` 存在（1,645 B），独立重算 sha256 = `c94feccbe6a1f7149a3cc664f339e8e9b95b0ba7d796cb997ded77ff620c9e82`，**与卡面一致**；destination 实测存在；7 个目录合计 **1,068 files / 2,194,905,712 B**（与 manifest 及卡面一致；该口径排除 manifest 自身 1,645 B 与 `data-hash-before-pages.txt` 66 B；含这两项为 1,070 files / 2,194,907,423 B）。 | PASS |
| A5 | **INSTALLER 门禁** | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/INSTALLER-MATRIX-1.md` → `Governance check: PASS (3 warnings)`，exit 0。3 warning：非终态 Task 提示、STATUS/REBASELINE_PLAN 预算 80%。最后一次运行于 `4459a0602` 干净树；两张被审卡在该提交字节未变，卡级校验相同。 | PASS |
| B6 | **DIAG 收口正当性** | `status: closed_with_limitations`（**不是** `done`），`integration_commit: null`；卡面 §2026-10-25「approved 仅对诊断 head `fed1a9cf3` 有效；不集成本 Task、不置 done、不自动升级父候选」原文未改。L-D-1..4 与 `RESULT.md` / `dsh-review-r1.md` / `verification/GIT-CLEAN-RUST-ISOLATION-1/r2/DISPOSITION.md` 一致：AC3 PARTIAL（R-01/R-09）、仅诊断未集成（R-001/R-002 边界）、packaged 12/0/154 只绑定 e34、`rust-default-parallel-r2` 实测 `151 passed; 2 failed; 1 ignored; 12 filtered` + exit 101，生产饱和风险由 RUST-ISO AC3 `<<BLOCKED>>` 承载。父卡 `GIT-CLEAN-PUBLICATION-1` 实测为 `closed_with_limitations`。 | PASS |
| B7 | **DIAG AC 未被改义** | `31dd81832^..31dd81832` 对该卡的 diff 只有：`status`、`reviewer`、`resource_closeout_status`、Resource Manifest 四行、末尾追加 Closeout Record；AC3 仍 `[ ]` + `<<PARTIAL: 冻结与EXIT追溯已补齐；旧日志环境不可补造；DSH已接受PARTIAL…>>`，AC1/AC2/AC4 仍 `[x]` + `<<MET>>`，无任何 AC 文字或标记被改写。 | PASS |
| B8 | **历史证据字节未动** | `git diff --stat 31dd81832^ 31dd81832 -- verification/` 输出为空（EMPTY）。本次提交的 7 个文件全部在 `doc/`，不含 `verification/`。 | PASS |
| B9 | **DIAG 资源核销** | `RESOURCE-MANIFEST.json` 存在（392 B），独立重算 sha256 = `529f835eda7491043e497fb85161e2a0e7af74c5261c2522157834f7dd60a414`，**与卡面一致**；destination 存在；独立重算 **13,101 files / 1,885,941,148 B**（该口径排除全部 `.git` 元数据 1,788 文件 / 5,038,900 B，及 manifest 自身 392 B；含 `.git` 与 manifest 的原始递归计数为 14,890 files / 1,890,980,440 B）。计数口径未在卡面/manifest 中写明（P2-DG-1）。 | PASS_WITH_FINDINGS |
| B10 | **两张新卡** | `31dd81832` 时两张均为 `status: proposed`：`RELEASE-GATE4-SIGNED-MATRIX-1`（kind=infra）、`MAPMINT-ERROR-FIDELITY-1`（kind=fix）。frontmatter 齐全（id/title/kind/governance_version/status/approval/suggested_owner/owner/reviewer/depends_on/base_commit/branch/worktree/integration_commit/delivery_head/canonical_evidence_status/resource_closeout_status/evidence_dir/allowed_paths 均在）；两卡 `allowed_paths` 均含 `evidence_dir`；AC 均可执行（RELEASE AC1–AC7、MAPMINT AC1–AC6 为具体动作+预期）；已登记进 `REBASELINE_PLAN`（「表外节点」行）与 `TASK_LEDGER`（两个 `proposed` 非终态）；未见任何「Gate 通过 / 条件 4 满足」的宣称（RELEASE disposition 明写条件 4 未满足；MAPMINT 不涉 Gate）。两项偏差：①被审 head 的 TASK_LEDGER 跟踪计数为 666 tracked / 2 untracked，实际两卡已入库（668/0），见 P2-GOV-1；②两卡均未带模板的 Canonical Evidence / Resource Manifest 章节，MAPMINT 的 `base_commit` 为 null 且 allowed_paths 未含产品源码/测试（Codex Q2 要求释放前冻结），属 `proposed` 阶段可接受、但 `in_review`/释放前必须补齐。 | PASS_WITH_FINDINGS |

## 2. A. INSTALLER-MATRIX-1 findings

**r1 复核项状态回填（供对照）**：F-01 已关闭（exe `ProductVersion` 与 `VERSION.json app_build.repo_head` 均为 `71cecb95a…`）；F-04 已关闭（`repo_head_source: DECLARATION`）；F-05 措辞已改为「清单 SHA-256」（不再说逐字节）；F-06 污染数字已更正（+8 files / +757,282,501 B）。**仍未关闭**：F-02 → P1-IM-1；F-03 → P1-IM-2；F-07 → P2-IM-3；F-08（无 staleness 守卫，README §6 自认未做）→ 本报告列为已知遗留，不单独编号（不阻塞本卡机制结论）。

### P1-IM-1（P1）包内 `package-manifest.json` 仍是 0.1.0 残留，随安装包分发，收口未登记

- **实测 vs 卡面**：
  - 卡面 `Closeout Record` 只写「AC1–AC6 已有实物证据」「10 行 BLOB」「0 删除/迁移/归档」，L-IM-1..5 未提该文件；README §5 只说「重做时已把 `app/VERSION.json` 一并改写为当前真实值」，未说 `package-manifest.json`。
  - `stage\NewManga-0.1.1-win-x64\package-manifest.json`：`381,448 B`，mtime `2026-10-28 13:16:59 +08`；JSON 实测 `"package": "NewManga-0.1.0-win-x64"`、`"version": "0.1.0"`、`"bytes": 225701934.0`、`"models_bundled": false`。
  - 同 stage 根 `VERSION.json`：`0.1.1`、`889,353,540 B` stage、`models_bundled: true`、`632,552,582 B` 权重。两者直接冲突。
  - 安装目录 `C:\Users\49745\AppData\Local\Programs\NewManga\package-manifest.json` 同为 `381,448 B`（安装器按 `File /r` 落盘）。
  - r1 Review `doc/reviews/INSTALLER-MATRIX-1-review-r1.md` 的 `F-02`（P1）明确同时点名 `app/VERSION.json` 与 `package-manifest.json`；本次只修了前者。
- **命令**：`Get-Content '...\stage\NewManga-0.1.1-win-x64\package-manifest.json' -Raw | ConvertFrom-Json | Select package,version,bytes,models_bundled`；`Get-Item ...\package-manifest.json | Select Length,LastWriteTime`；`Get-Item ...\stage\...\VERSION.json`。
- **影响**：不推翻 AC1–AC6 的机制结论（根 `VERSION.json`、exe、sidecar 与实物一致，我已独立重算）；但这是 r1 P1 未完全关闭 + 收口限制清单漏登，包元数据自相矛盾会误导后续审计/发行检查。
- **建议**：下一次重打包时同步生成/删除 `package-manifest.json`，或在卡面 `Closeout Record` append-only 补登「L-IM-6：包内 `package-manifest.json` 仍为 0.1.0 残留，不影响安装器行为但与根 `VERSION.json` 不自洽」。**不得**据此改 AC7 或宣称条件 4。

### P1-IM-2（P1）`variant=base` + 内置 632,552,582 B 权重 + `GPL-3.0-or-later` 声明，与随包许可审计文件冲突；r1 F-03 未结

- **实测 vs 卡面**：
  - 根 `VERSION.json`：`"variant": "base"`、`"license": "GPL-3.0-or-later"`、`"models_bundled": true`、`"bundled_weights_license": "the three bundled ONNX files are the project's own pinned weights (see NOTICE.md)…"`；同文件 `models` 字段又写「license/notice 口径需按内置权重重新复核」。
  - 随包 `NOTICE.md` 变体表：**base = 不含模型权重 / GPL-3.0-or-later；models = 含权重 / AGPL-3.0**；并写「models 变体整体按 AGPL-3.0 分发的原因：随包分发 Ultralytics YOLO11s-seg 权重」。
  - 随包 `LICENSE_AUDIT.md`：「base 变体不随包任何模型权重」「`detector/rtdetr-v2-fixed.onnx`、`ocr/manga-ocr-onnx/{encoder,decoder}_model.onnx` 等 —— 上游声明 **[待核实]**，不作为本包许可结论的阻断项」。
  - 实物：stage `app/core-sidecar/models` 三件合计 `632,552,582 B`（`rtdetr-v2-fixed.onnx=171,618,071`、`encoder_model.onnx=343,454,249`、`decoder_model.onnx=117,480,262`），即**base 标签的包实际含权重**。
  - r1 `F-03`（P1）要求「去权重（base）或按 AGPL-3.0 声明（models 变体）」；本次改写了 `models_bundled` 与 `bundled_weights_license` 陈述，但**没有**统一 `variant`/`license` 与随包审计文件，也没有登记为限制。
- **命令**：`Get-Content '...\stage\...\VERSION.json' -Raw`；`Get-Content '...\stage\...\NOTICE.md'`；`Get-Content '...\stage\...\LICENSE_AUDIT.md' -Raw`；`Get-ChildItem '...\stage\...\app\core-sidecar\models' -Recurse -File | Measure-Object Length -Sum`。
- **影响**：不影响安装/卸载机制本身；但这是发行许可口径问题：包自报 base/GPL 却含权重，且权重上游许可「待核实」。本卡 AC8 已禁止据此宣称条件 4 通过，卡也只是机制验证，因此**不要求重跑矩阵**；但收口限制必须补登，否则后续以该包为基线做签名/发行会继承错误口径。
- **建议**：在 `Closeout Record` append-only 补登「L-IM-7：包为 base 标签但内置 632,552,582 B 权重，`NOTICE.md`/`LICENSE_AUDIT.md` 仍按 base 无权重描述，`rtdetr`/OCR 上游许可待核实；条件 4 与发行许可均未满足」；正式发行前按模型许可二选一处理。

### P2-IM-1（P2）AC8 在本提交由 `[ ]` 翻成 `[x] <<MET>>`，未在 Closeout 说明

- `git diff 31dd81832^ 31dd81832 -- doc/tasks/INSTALLER-MATRIX-1.md` 显示：AC8 原 `- [ ] **AC8 不虚报**…` 改为 `- [x] … <<MET>>`；AC1–AC6 只是补 `<<MET>>` 标记（原本已 `[x]`），AC7 补 `<<PARTIAL>>` 标记（原本已 `[ ]`）。AC8 是**唯一**翻转勾选项的 AC。
- 其实质可支持（`git ls-files` 无 exe/setup 入库；卡面明确不宣称条件 4），故不判 P1。建议在 Closeout 补一句 AC8 的 MET 依据，避免「收口时顺手刷绿」的观感。

### P2-IM-2（P2）§测试要求 与 §交付与运行记录 未回流

- 卡面 §测试要求 五行的「实际结果」仍全为 `NOT_RUN`、「证据」全为 `无`；§交付与运行记录 仍写「Handoff：尚无。Review：尚无。实际测试：尚无。」。
- 这与 AC1–AC6 `[x] <<MET>>`、CE 10 行、`verification/INSTALLER-MATRIX-1/README.md` 直接矛盾；顶部「状态澄清」只解释了 AC 表的旧状态，没有在这两节加指针。建议 append-only 在两节加「见顶部状态澄清与 verification README；本节为历史快照」。

### P2-IM-3（P2）AC4/AC6 的 exit code 与 install/uninstall 原始日志未留存/pin；HKCU 键名与 `.nsi` 不符；当前机器终态无法复核

- README §3 是唯一的 install/uninstall 汇总（`DATA BEFORE…`、`install /S exit=0`、`uninstall /S exit=0`、`MANIFEST HASH BEFORE/AFTER`），没有独立的原始 transcript；r1 `F-07`（P2）未关闭。
- 现在的 `%TEMP%\NewManga-uninstall-0.1.1.log`（2026-11-15 05:18:55）与 `NewManga-uninstall-0.1.0.log`（05:19:46）**属于之后的 `GATE4-PAGES-UPGRADE-1` 运行**（其 README §5 记录了 0.1.0/0.1.1 六步矩阵），不能当作本卡 AC6 的原始日志。
- 当前 `%LOCALAPPDATA%\Programs\NewManga` **存在**（1,038 files / 889,400,166 B，创建于 2026-11-15 05:21:46，含与 stage 完全一致的 exe/VERSION.json），HKCU `...\Uninstall\NewManga` 存在（DisplayName `New Manga`、DisplayVersion `0.1.1`），Start Menu 两项存在——这是后续 GATE4 安装留下的状态，不是本卡卸载失败；但它意味着「程序目录/HKCU/StartMenu 全清理」的**终态**只能在 README 的时点快照中成立，现在无法从机器状态独立复核。
- README §1 写「HKCU `New Manga 0.1.1`」；`.nsi` 实测键为 `Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_ID}`（实机为 `...\Uninstall\NewManga`），版本在 `DisplayVersion` 而不是键名——措辞需更正。
- **旁证**：`GATE4-PAGES-UPGRADE-1/README.md` §3/§5 在 05:11–05:23 独立记录用户数据根 hash 同为 `6ae4d6da…d9b2`，可交叉支持本卡 AC6 的「前后一致」在当时成立。当前数据根已漂移（530 files / 683,864,388 B，含 6 个 `.nmbak`），属后续运行，不计入本卡。
- 建议：登记为「证据为时点快照，原始 exit/log 未保留」，并更正 HKCU 键名表述；不必为此重跑矩阵。

### P2-IM-4（P2）L-IM-2 的「可能不是同一安装包/head」与实测不符

- L-IM-2 原文：「Gate 映射 Review 另称『安装产物四页 5/5』，两者证据不一致，未对齐（**可能不是同一安装包/head**）」。
- 实测：`verification/GATE3-FOUR-PAGE-WALKTHROUGH-1/README.md` §11.1 记录安装产物 `version = 0.1.1+71cecb95a10c42ffe02d1396ab065e1fc9c43ca9`、`sha256 = a3ec2133b5da3f61`，与本卡 stage 的 exe **完全同一 head、同一 exe**；「head 不同」不成立（setup.exe 的 NSIS 包装字节是否完全相同未在该证据中记录，但安装后的产品二进制相同）。
- **这不支持把 AC7 改成 MET**：该证据由别的卡运行、未纳入本卡 AC7 的证据集，`Codex Q3` 也明确要求「不能只据另一份 Review 把本卡 AC7 改成 MET」。因此 **AC7 必须保持 `NOT_RUN`**；建议把括注改为「他卡运行、未对齐到本卡 AC7 证据集」，避免用未证实的「head 不同」当理由。

## 3. B. GIT-CLEAN-PUBLICATION-DIAG-1 findings

### P2-DG-1（P2）RESOURCE-MANIFEST 的 13,101 / 1,885,941,148 计数口径未写明（排除 `.git` 与自身）

- manifest 只有 `total_file_count` / `total_bytes` / `content_digest`，没有 `scope`/`excluded` 字段。独立复现必须知道：排除全部 `.git` 元数据 **1,788 files / 5,038,900 B** 与 manifest 自身 **392 B**，才得到 13,101 / 1,885,941,148；直接 `Get-ChildItem -Recurse -File -Force` 是 14,890 / 1,890,980,440。
- 这不是数字错误（manifest 与卡面一致），而是**可复现性**缺口。建议下次编辑 manifest 时补 `"scope": "exclude .git and self"` 或 `excluded` 列表；无需重算历史证据。

### P2-DG-2（P2）DIAG 的 `allowed_paths` 未包含自己的 Review 路径

- `31dd81832` 的 DIAG `allowed_paths` 有 `verification/GIT-CLEAN-PUBLICATION-DIAG-1/**`、Task、STATUS/PLAN/LEDGER、workspace 等，但**没有** `doc/reviews/GIT-CLEAN-PUBLICATION-DIAG-1-*.md`；本次两份合并复核只能落在 `doc/reviews/INSTALLER-MATRIX-1-CLOSEOUT-REVIEW-2026-11-17.md`（属 INSTALLER 的 allowed path）。
- 不影响本次收口结论；建议下次编辑 DIAG 卡时补该路径，或在合并复核规则里明确「Diag 卡复核随 INSTALLER 关闭复核落盘」。

## 4. 跨卡 / 治理 finding

### P2-GOV-1（P2）被审 head 的 TASK_LEDGER 跟踪计数与实际不符（已在后续提交修正）

- `31dd81832` 的 `doc/TASK_LEDGER.md`：`task files 668`、`terminal 663`、`non-terminal 4`、`task files tracked by git 666`、`task files untracked (drafts) 2`、`non-terminal tracked by git 2`。
- 实测该 head：`git ls-files doc/tasks` = 669（含 `README.md`，任务文件 668），两张新卡都在该提交中（`A`），即 **tracked 668 / untracked 0**；非终态 4 张（FEA11 blocked、MAINT-1 in_progress、MAPMINT proposed、RELEASE proposed）全部 tracked。台账把两张新卡当成未跟踪 drafts，是生成台账时尚未 `git add` 的旧快照；check.ps1 只校验 `task files` 与 `non-terminal` 两个数字，未校验跟踪行，故 PASS 未拦住。
- **已在 `4459a0602` 修正**：现台账为 `tracked 668 / untracked 0`、`non-terminal 2`（MAPMINT 已 superseded、FEA11 已 closed）。本 finding 针对被审 head 的记录准确性，不要求再次修改。

## 5. 明确回答：两张卡能否分别保持 `closed_with_limitations`

**INSTALLER-MATRIX-1：可以有条件保持 `closed_with_limitations`。**

- 保持的理由：AC1–AC6 的机制证据真实且可独立重算（stage/setup/exe/sidecar/日志/CE/manifest 全部对上）；AC7 如实 `NOT_RUN`；卡面明确不宣称条件 4；`integration_commit: null`；收口为 `closed_with_limitations` 而不是 `done`，符合 Codex Q3 的「保留 AC 原状与未满足项」。
- 条件：在卡面 `Closeout Record` **append-only** 补登 `P1-IM-1`（`package-manifest.json` 0.1.0 残留）与 `P1-IM-2`（base 标签+内置权重+GPL 声明与随包许可审计冲突）为 L-IM-6/L-IM-7（或在下一次重打包修复两者并留证）。在此补登完成前，本复核认为该卡的「收口记录」不完整，但**不要求**退回 `in_progress`，也**不要求**把任何 AC 改成 MET。
- 禁止：不得据此把 AC7 改为 MET、不得宣称条件 4 或 Technical Gate 通过、不得把 P1-IM-1/2 写成「已解决」。

**GIT-CLEAN-PUBLICATION-DIAG-1：可以保持 `closed_with_limitations`。**

- 理由：收口未违反「不集成、不置 done」；AC3 保持 `PARTIAL`；AC1/2/4 保持 `MET`；历史证据与 CE 字节未动；L-D-1..4 与 RESULT / dsh-review-r1 / RUST-ISO r2 DISPOSITION 一致；资源核销数字与 sha256 全部对上。仅 P2（计数口径、review 路径）不构成维持收口的障碍。

**两卡共同边界（本复核不放松）**：

- `Technical Gate = NOT_SATISFIED` 不变；条件 4 仍不满足（AC7 NOT_RUN、无签名、跨版本未证明、旧 sidecar、许可口径未结）。
- 不把任何 `NOT_RUN` / `PARTIAL` / `BLOCKED` 改写成 PASS/MET；不弱化任何既有断言。

## 6. 声明

**本复核不构成产品发布验收。** 本报告只回答两卡在 `31dd81832` 的收口证据是否真实、记录是否自洽、收口是否越界；不批准安装包签名、不批准条件 4、不批准 push/release、不批准把 DIAG 补丁集成到 main，也不替代用户或 DSH 对 Gate 总体结论的裁决。复核未运行安装/卸载（避免副作用），未重跑任何产品测试；AC1–AC6 的产品行为以证据文件与工作区产物为准。

## 附录 A：关键命令与实测输出摘要

```text
# head / clean
git rev-parse HEAD                                   -> 31dd81832（复核启动时）
git diff --stat 31dd81832^ 31dd81832 -- verification/ -> EMPTY
git show --stat --oneline 31dd81832                  -> 7 files, all doc/

# INSTALLER stage / setup / exe / sidecar
stage:        Get-ChildItem -Recurse -File | Count=1037; Sum=889,353,540
setup:        Length=652,107,016; SHA256=0c0415993b6deab7027baee941f683487a263a0e0fb65c2cd16040ee4c358f06
exe:          Length=99,554,850;  SHA256=a3ec2133b5da3f619b752c818371ba54867b4c150fdba65b8c22d8b17f739230
              VersionInfo.ProductVersion=0.1.1+71cecb95a10c42ffe02d1396ab065e1fc9c43ca9
core_service: Length=400,098; SHA256=6050881163753d32eca2fb1c0c824d9de7852bf62fb808926f5b6fc74a6b52ee
              LastWriteTimeUtc=2026-11-14T19:16:55.3503345Z

# CE 10/10（BLOB 998e04ae4）
EV-IM-01 6dac2fcc...5ac5 MATCH   EV-IM-02 27782980...d30b MATCH
EV-IM-03 ab0e416d...4f68 MATCH   EV-IM-04 90b8897a...8116 MATCH
EV-IM-05 2de165cc...88ef MATCH   EV-IM-06 149f79fc...db22 MATCH
EV-IM-07 8cd0ab1f...a636 MATCH   EV-IM-08 90b8897a...8116 MATCH
EV-IM-09 f80bdcd4...27ef MATCH   EV-IM-10 d391ca4e...d5e3 MATCH

# INSTALLER resource manifest
RESOURCE-MANIFEST.json Length=1,645
SHA256=c94feccbe6a1f7149a3cc664f339e8e9b95b0ba7d796cb997ded77ff620c9e82  MATCH card
resource dirs 7; files 1,068; bytes 2,194,905,712（排除 manifest 与 data-hash-before-pages.txt）
raw 1,070 files / 2,194,907,423 B

# DIAG resource manifest
RESOURCE-MANIFEST.json Length=392
SHA256=529f835eda7491043e497fb85161e2a0e7af74c5261c2522157834f7dd60a414  MATCH card
files 13,101; bytes 1,885,941,148（排除全部 .git 1,788 files / 5,038,900 B 与 manifest 392 B）
raw 14,890 files / 1,890,980,440 B

# governance
check.ps1 -TaskPath doc/tasks/INSTALLER-MATRIX-1.md  -> PASS (3 warnings), exit 0
check.ps1 -TaskPath doc/tasks/GIT-CLEAN-PUBLICATION-DIAG-1.md -> PASS (3 warnings), exit 0

# r2 evidence
rust-default-parallel-r2.json exit=101; r2.log: 151 passed; 2 failed; 1 ignored; 12 filtered out
DIAG-05 / DIAG-43 / DISP-01 文件字节 SHA256 与 CE 表 MATCH
```

## 附录 B：本次复核发现的关键不一致（一页速查）

| ID | 级别 | 一句话 | 证据位置 |
|---|---|---|---|
| P1-IM-1 | P1 | 包内 `package-manifest.json` 仍 0.1.0（381,448 B，2026-10-28），随安装包分发；L-IM 未登记 | stage/安装目录 `package-manifest.json` |
| P1-IM-2 | P1 | `variant=base` + 632,552,582 B 权重 + `GPL-3.0-or-later`，与随包 `NOTICE.md`/`LICENSE_AUDIT.md`（base 无权重、models=AGPL）冲突；rtdetr/OCR 许可待核实 | stage `VERSION.json` / `NOTICE.md` / `LICENSE_AUDIT.md` |
| P2-IM-1 | P2 | AC8 由 `[ ]` 翻 `[x] <<MET>>`，Closeout 未说明 | commit diff |
| P2-IM-2 | P2 | §测试要求 / §交付与运行记录 仍全 NOT_RUN/尚无 | 卡面 106–129 |
| P2-IM-3 | P2 | AC4/AC6 无原始 exit/log；HKCU 键名写法不符 `.nsi`；当前终态来自后续 GATE4 安装 | README §3、TEMP 日志、HKCU、`.nsi` |
| P2-IM-4 | P2 | L-IM-2「可能不是同一安装包/head」与 GATE3 走查的同一 exe/head 不符；AC7 仍必须 NOT_RUN | GATE3 README §11.1 |
| P2-DG-1 | P2 | DIAG manifest 13,101 计数排除 `.git` 与自身未写明 | manifest / 递归重算 |
| P2-DG-2 | P2 | DIAG allowed_paths 缺自己的 `doc/reviews/…-*.md` | 卡面 20–29 |
| P2-GOV-1 | P2 | HEAD 台账 tracked 666/untracked 2 与实际 668/0 不符；已在 4459a0602 修正 | TASK_LEDGER vs `git ls-files` |

---

**reviewer 签名**：`reviewer-inst`（独立上下文；只读复核；本报告为唯一写入）。
