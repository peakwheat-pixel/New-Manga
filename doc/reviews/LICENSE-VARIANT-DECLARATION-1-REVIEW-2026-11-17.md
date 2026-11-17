---
task_id: LICENSE-VARIANT-DECLARATION-1
reviewer: reviewer-lvd
reviewer_kind: subagent
author: DSH
base_commit: 02c3aaeda
reviewed_head: a5e57958b
reviewed_at: 2026-11-17T23:13:00+08:00
decision: ACCEPTED_WITH_FINDINGS
---

# Review：LICENSE-VARIANT-DECLARATION-1（方向 A 独立复核）

- **reviewed_head**：`a5e57958b`（main）。复核时仓库工作区 HEAD 为 `9f93842a5`，`git diff a5e57958b..9f93842a5 --stat` = `doc/handoffs/NEXT-SESSION-STARTER.md | 47 +++++++++-`（1 file, +46/−1，纯 handoff 文档），与被审代码/文档无关，故以 `a5e57958b` 为审查对象并逐条对照实物。
- **reviewer**：`reviewer-lvd` —— DSH 主会话派发的**独立上下文子 agent**，**未参与** `LICENSE-VARIANT-DECLARATION-1` 的实现、取证或返修；本轮只读复核 + 写本报告。`reviewer_kind: subagent`。
- **时间**：2026-11-17 22:52–23:20（+08:00）。
- **只读声明**：未修改仓库内任何被审文件、未提交/推送/checkout、未改动既有 stage / fixture。本复核的合成 stage 与临时产物全部写在 `G:\CODEX\New Manga.workspace\tmp\lvd-review\`（非仓库路径）。

## 0. 结论摘要

| 项 | 结果 |
|---|---|
| `decision` | **ACCEPTED_WITH_FINDINGS** |
| P0 / P1 / P2 | **1 / 1 / 3** |
| 方向 A 的执行是否成立 | **成立**：文档主表、NSIS 变体化、fail-closed 护栏、生成器口径均实测有效，7/7 Canonical Evidence 的 sha256 与 `02c3aaeda` blob 逐条相符 |
| 「随包」一致性 | **不成立**：AC3 所指的 `setup.exe`（`a4b11458…`）内装的是**修正前**的三份合规文档（P0-1）；仓库侧另有 4 处仍称 models 变体随包 `yolo11s-seg`（P1-1） |
| `closed_with_limitations` | **可以保持**（不得改 `done`，也不必回退 `blocked`），但前提是卡内追加 P0-1/P1-1 返修条目并声明该 `setup.exe` 作废、禁止发布 |

## 1. 七项逐条判定

| # | 审查项 | 判定 | 关键实测（详见 §2–§8） |
|---|---|---|---|
| 1 | 三份文档与实际权重逐项一致；无「含 yolo11s-seg」/「含权重包声明 GPL」 | **PARTIAL（FAIL）** | 3 个 ONNX 的字节/sha256/合计数**全部一致**；含权重包**无一处**再声明 `GPL-3.0-or-later`；但 `NOTICE.md:37`、`THIRD_PARTY_LICENSES.md:36 / :53 / :69` 仍把 models 变体写成含 `yolo11s-seg.onnx`（该文件不在包内）→ P1-1 |
| 2 | NSIS 变体化真生效，四处读取 `${VARIANT_NAME}`/`${VARIANT_LICENSE}`，`VARIANT_CONTENT` 在 `.nsi` 内推导 | **PASS** | 四处 = `:80 / :92 / :93 / :123`；`:70–76` 由 `${VARIANT_NAME}` 推导中文。自建编译 `LegalCopyright=AGPL-3.0 (models)`；探针编译输出 `VARIANT_CONTENT=含模型权重`（models）/`不含模型权重`（base）。命令行**只传 ASCII** |
| 3 | 自建 makensis 最小 stage 编译 | **PASS** | `MAKENSIS_EXIT=0`，产物 81,837 B；未覆盖仓库内任何文件 |
| 4 | fail-closed（权重 + 非 AGPL ⇒ throw）有效 | **PASS** | 代码 `:190–192`（throw 在 `:191`）；实跑合成 stage（护栏已 EXIT=0 通过）→ `BUILD_EXIT=1`、未产出 setup.exe；旧 stage 护栏实跑 `EXIT=1`（8 条 FAIL），与 `ac4` 证据一致 |
| 5 | 7 行 Canonical Evidence sha256 == `02c3aaeda` blob；`ac3-models-version.json` 字段 | **PASS** | 7/7 全部相符（BLOB 口径）；`license=AGPL-3.0`、`models_bundled_bytes=632,552,582` 均正确 |
| 6 | 诚实性三条 | **PASS** | 卡面 `:142–146` 三条限制**全部存在**（待核实/保守过度声明、未目验渲染、未签名） |
| 7 | `check.ps1` 门禁；`closed_with_limitations` 是否恰当 | **PASS（判定见 §9）** | `Governance check: PASS (3 warnings)`，`CHECK_EXIT=0`；状态**可保持** `closed_with_limitations`，**不得**改 `done` |

## 2. 文档 vs 实物逐项比对（审查项 1）

实物口径：`G:\CODEX\New Manga.workspace\tmp\r24\pkgmodels2\NewManga-0.1.1-win-x64-models\app\core-sidecar\models`（AC3 打包 stage，与 `...\tmp\r24\sidecar-models\models` 源 fixture 逐字节一致）。

| 文件 | 文档值（仓库 `a5e57958b`） | 实测值 | 判定 |
|---|---|---|---|
| `detector/rtdetr-v2-fixed.onnx` | 171,618,071 / `c7fb5af1a8982416` | 171,618,071 / `c7fb5af1a8982416b56955e621c1b10397730807956998066e2fbc132c77bbc3` | 一致 |
| `ocr/manga-ocr-onnx/encoder_model.onnx` | 343,454,249 / `15fa8155fe9bc1a7` | 343,454,249 / `15fa8155fe9bc1a7d25d9bb353debaa4def033d0174e907dbd2dd6d995def85f` | 一致 |
| `ocr/manga-ocr-onnx/decoder_model.onnx` | 117,480,262 / `ef7765261e9d1cdc` | 117,480,262 / `ef7765261e9d1cdc34d89356986c2bbc2a082897f753a89605ae80fdfa61f5e8` | 一致 |
| 3 onnx 合计 | 632,552,582 | 632,552,582（3 个） | 一致 |
| 6 个 config/vocab | 109,678（`NOTICE.md:10`、`LICENSE_AUDIT.md:10/26`） | 109,678（`models/` 目录合计 632,662,260 − 632,552,582） | 一致 |
| `yolo11s-seg.onnx` 40,824,255 | `NOTICE.md:37`「**当前 models 变体随包的 YOLO11s-seg 已核实为 AGPL-3.0**」 | **不在包内**（`models/` 仅 9 个文件，无该文件） | **不一致（P1-1）** |
| 同上 | `THIRD_PARTY_LICENSES.md:36` 表格行（表头称「REPACK-5 实测清单…与包内文件逐一核对」） | 同上 | **不一致（P1-1）** |
| 同上 | `THIRD_PARTY_LICENSES.md:53`「models 变体包含**上述** AGPL-3.0 权重」 | 上述含该不存在的文件 | **不一致（P1-1）** |
| 同上 | `THIRD_PARTY_LICENSES.md:69` Gate「[x] models 变体含 AGPL 组件（Ultralytics YOLO11s-seg）」 | 同上 | **不一致（P1-1）** |
| 含权重包许可 | `NOTICE.md:8/10/18`、`LICENSE_AUDIT.md:10/27`、`THIRD_PARTY_LICENSES.md:42–44` | models = **AGPL-3.0**（保守过度声明），base = GPL-3.0-or-later | **一致**；三份文档**无一处**再把含权重包说成 `GPL-3.0-or-later` |

复现命令：

```pwsh
Get-ChildItem '<stage>\app\core-sidecar\models' -Recurse -File |
  ForEach-Object { "{0}`t{1}`t{2}" -f $_.Name,$_.Length,(Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower() }
Select-String -Path NOTICE.md,THIRD_PARTY_LICENSES.md,apps\desktop-avalonia\docs\LICENSE_AUDIT.md -Pattern 'yolo11s-seg'
```

`LICENSE_AUDIT.md` 本身**正确**：`:22–24` 三行与实测一致，`:30` 明确写出「此前写成 yolo11s-seg…已更正」。

## 3. NSIS 变体化（审查项 2）

`git show 02c3aaeda -- packaging/nsis/installer.nsi apps/desktop-avalonia/scripts/build-installer.ps1` 与当前文件一致，四处已全部变体化：

| 原硬编码处 | 现位置 | 现值 |
|---|---|---|
| `LegalCopyright` | `installer.nsi:80` | `"${VARIANT_LICENSE} (${VARIANT_NAME}); see LICENSE and LICENSE-AGPL-3.0.txt"` |
| `MUI_WELCOMEPAGE_TEXT` | `installer.nsi:92` | `"本安装包为 ${VARIANT_NAME} 变体（${VARIANT_CONTENT}，按 ${VARIANT_LICENSE} 分发）…"` |
| `MUI_LICENSEPAGE_TEXT_TOP` | `installer.nsi:93` | `"${VARIANT_NAME} 变体整体按 ${VARIANT_LICENSE} 分发。…"`（原「含 Ultralytics YOLO11s-seg 权重」句已删除） |
| 安装日志 | `installer.nsi:123` | `"variant=${VARIANT_NAME} (${VARIANT_LICENSE}; unsigned)"` |

`VARIANT_CONTENT` 的中文**确为 .nsi 内推导**（`:70–76`，由 ASCII 的 `${VARIANT_NAME}` 分支），命令行只传 `VARIANT_NAME`/`VARIANT_LICENSE`；`ac3-nsis-variant-defines.log` 亦只有两行 ASCII 定义。

实证（本次自建编译，非抄卡）：

```pwsh
& "C:\Program Files (x86)\NSIS\makensis.exe" /V2 "/DVERSION=9.9.9" "/DVERSION4=9.9.9.0" `
  "/DSTAGE_DIR=G:\CODEX\New Manga.workspace\tmp\lvd-review\stage" `
  "/DOUT_FILE=G:\CODEX\New Manga.workspace\tmp\lvd-review\lvd-test.exe" `
  "/DVARIANT_NAME=models" "/DVARIANT_LICENSE=AGPL-3.0" packaging\nsis\installer.nsi
```

- `MAKENSIS_EXIT=0`；产物 `lvd-test.exe` = 81,837 B；
- 产物版本资源：`LegalCopyright=AGPL-3.0 (models); see LICENSE and LICENSE-AGPL-3.0.txt`；
- 判别探针（`installer.nsi` 的逐字节副本 + 一行 `!warning`，保留 UTF-8 BOM；不带 BOM 会 `Bad text encoding`）：`models` → `VARIANT_CONTENT=含模型权重`；无定义 → `VARIANT_NAME=base VARIANT_LICENSE=GPL-3.0-or-later VARIANT_CONTENT=不含模型权重`。

## 4. fail-closed（审查项 4）

**代码**：`apps/desktop-avalonia/scripts/build-installer.ps1:190–192`

```pwsh
190  if ($stageOnnx.Count -gt 0 -and $script:variantLicense -ne 'AGPL-3.0') {
191      throw "LICENSE-VARIANT-DECLARATION-1: stage bundles $($stageOnnx.Count) onnx file(s) but VERSION.json license='$variantLicense'; must be AGPL-3.0"
192  }
```

前置条件链闭合：`VERSION.json` 属必检文件（`:101`、`:104–105` 缺失即 throw），无 `license` 字段亦 throw（`:183–185`），故 `:190` 无「字段缺失绕过」路径。`:152–155` 的 manifest guard 先执行（对旧 stage 是第一道拦截），`:190` 是独立的第二道。

**实跑**（合成 stage：1 个 50,000 B 占位 `.onnx`，`VERSION.json.license=GPL-3.0-or-later`，先单独跑护栏确认通过）：

| 用例 | 命令 | 结果 |
|---|---|---|
| 权重 + GPL | `pwsh -NoProfile -File apps\desktop-avalonia\scripts\build-installer.ps1 -StageDir <synth-gpl> -OutDir <ws> -Version 9.9.9` | 护栏 `OK (1 onnx / 50000 B)` → **`:191` 抛出** `…license='GPL-3.0-or-later'; must be AGPL-3.0`，`BUILD_EXIT=1`，**未产出** setup.exe |
| 权重 + AGPL（正控制） | 同上，`<synth-agpl>` | `BUILD_EXIT=0`，产出 setup.exe（`97d4e23b…`），说明判据不是「一律拒绝」 |

**旧 stage 复跑**（未改动其字节）：

```pwsh
pwsh -NoProfile -File tools\ci\verify-package-manifest.ps1 `
  -StageDir 'G:\CODEX\New Manga.workspace\task-envs\INSTALLER-MATRIX-1\stage\NewManga-0.1.1-win-x64'
```

`GUARD_EXIT=1`，**8 条 FAIL**，计数与 `ac4-old-stage-still-rejected.log` 完全一致（version 0.1.0 vs 0.1.1；`models_bundled` False vs True；`models_bytes` 0 vs 632,552,582；1968 条 vs 1036；1041 条不存在；109 条未登记；883 条 bytes 不符；892 条 sha256 不符）。仅「示例条目」的取样顺序不同（`Get-ChildItem` 枚举序），不影响结论。该旧 stage 的 `VERSION.json` 确为 `variant=base / license=GPL-3.0-or-later / models_bundled=true / 632,552,582 B` —— 正是 ZCode 判定的非法组合，现被护栏与 `:190` 双重拦截。

## 5. 证据链（审查项 5）

`git cat-file blob 02c3aaeda:<path>` 取字节后重算 sha256，**7/7 与该卡 Canonical Evidence 表逐条一致**：

| evidence_id | 卡面 sha256（前 16） | 重算 | 一致 |
|---|---|---|---|
| EV-LVD-01 README.md | `5fe45b10d451b7e9…` | 同 | ✓ |
| EV-LVD-02 ac3-models-version.json | `d6d623ff4e09c3f5…` | 同 | ✓ |
| EV-LVD-03 ac3-models-guard.log | `c7e2291f64435492…` | 同 | ✓ |
| EV-LVD-04 ac3-installer-build-info.json | `4601675136f40a74…` | 同 | ✓ |
| EV-LVD-05 ac3-nsis-variant-defines.log | `b829772b0f483f78…` | 同 | ✓ |
| EV-LVD-06 ac4-old-stage-still-rejected.log | `88dc4063d0acde32…` | 同 | ✓ |
| EV-LVD-07 ac3-models-package-manifest.json | `70a224306f8395f5…` | 同 | ✓ |

- `ac3-models-version.json`：`license="AGPL-3.0"`、`models_bundled_bytes=632552582`、`models_dir_bytes=632662260`、`bundled_weights_license` 为实际三文件（非硬编码 yolo）—— 全部符合要求。
- `ac3-models-package-manifest.json`：`variant=models`、`models_bytes=632552582`、`models_dir_bytes=632662260`。
- **口径提示（非缺陷）**：卡面 `sha256_basis=BLOB` 正确；仓库工作区文件因 CRLF 与 blob（LF）不同字节，若按工作区文件重算会得到不同值（如 `ac3-models-version.json` worktree 1411 B vs blob 1377 B）。后续复核务必继续用 `git cat-file blob`，不要用工作区文件。

## 6. 诚实性（审查项 6）

卡面 `doc/tasks/LICENSE-VARIANT-DECLARATION-1.md:142–146` 三条**全部存在**：

1. `:143`「未做权重上游许可的『核实认定』：三项仍标『待核实』，整包 AGPL-3.0 是**保守过度声明**，不是核实结论。」
2. `:144`「安装向导的**实际渲染**未目验…只验证了 makensis 编译成功与变体定义送达。」
3. `:145`「`setup.exe` **未签名**（`authenticode=NotSigned`）；Release Gate 条件 4 仍需真证书。」

`verification/LICENSE-VARIANT-DECLARATION-1/README.md:60–62` 同口径复述。三项均未被夸大或省略。

## 7. 门禁（审查项 7）

```pwsh
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/LICENSE-VARIANT-DECLARATION-1.md
```

```
Governance scope: 15 current documents; no historical directory scan.
Task: doc\tasks\LICENSE-VARIANT-DECLARATION-1.md
WARN: 存在 2 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3160 bytes / 28 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：6724 bytes / 64 lines
Governance check: PASS (3 warnings)
```

`CHECK_EXIT=0`；3 条 warning 均与本卡无关（非终态 Task 计数、STATUS/PLAN 篇幅预算）。`doc/STATUS.md` 的 `closed_with_limitations` 清单已含 `LVD`，`doc/TASK_LEDGER.md` 为聚合口径（不逐条列终态卡），二者不矛盾。

## 8. Findings

| ID | 级别 | 位置 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| **P0-1** | **P0（禁止发布）** | `verification/LICENSE-VARIANT-DECLARATION-1/ac3-installer-build-info.json` 所指产物；stage `…\tmp\r24\pkgmodels2\NewManga-0.1.1-win-x64-models`；exe `…\tmp\r24\instout4\NewManga-0.1.1-setup.exe` | **AC3 的 setup.exe 内装的是修正前的三份合规文档**：`NOTICE.md` 仍称 models 随包 `Ultralytics YOLO11s-seg`（40,824,255 B）并「已核实」，`LICENSE_AUDIT.md` 仍写「642.3 MiB / yolo11s-seg」，`THIRD_PARTY_LICENSES.md` 无「3 项待核实 + 保守过度声明」段。⇒ 该 release candidate 对接收方仍是**与实物矛盾的合规披露**（ZCode 裁定 Q2 的 P0 类别），且卡面「改后由 `package.ps1` 干净重建」对该产物**不成立** | 7z 抽出后：`setup.exe` 内 `NOTICE.md`=`81ebf5abbccf0adb…`、`THIRD_PARTY_LICENSES.md`=`ee5393685aa9f098…`、`LICENSE_AUDIT.md`=`bbb34044bae6ee2f…`；仓库同文件分别为 `f8aa97316f3d3e67…`、`ec26d2ad48a2c842…`、`84d89124b7c59513…`。三份 stage 副本 CRLF 归一化后**逐字节等于 `4ca94f0df` 的 blob**（即修正前版本）。时间线：stage `VERSION.json` 22:21:23 → 仓库文档改于 22:22–22:24 → `setup.exe` 22:46:11（仍未重打包） | 先修 P1-1，再**重跑 `package.ps1 -WithModels` + `build-installer.ps1`**；用 `7z e -o<tmp> setup.exe NOTICE.md THIRD_PARTY_LICENSES.md LICENSE_AUDIT.md` 逐份比对仓库根 sha256 相等，并把该比对写入 AC3 证据。**当前 `a4b11458…` 这个 setup.exe 作废、不得发布** | open |
| **P1-1** | P1（正式 Release 前必须通过） | `NOTICE.md:37`、`THIRD_PARTY_LICENSES.md:36`、`:53`、`:69` | 仓库侧仍有 4 处把 models 变体描述为「随包 yolo11s-seg 且已核实」，与实物（3 个 ONNX，无该文件）矛盾；照现状重打包仍会产出 P0-1 同类问题。`THIRD_PARTY_LICENSES.md:36` 所在表更自称「与包内文件逐一核对」 | `Select-String -Path NOTICE.md,THIRD_PARTY_LICENSES.md -Pattern 'yolo11s-seg'`：`:37`「当前 models 变体随包的 YOLO11s-seg 已核实为 AGPL-3.0…」；`:36` 该行 40,824,255 B 行仍在「随包清单」；`:53`「包含上述 AGPL-3.0 权重」；`:69`「[x] models 变体含 AGPL 组件（Ultralytics YOLO11s-seg）」 | 四处改为「历史登记/当前不在包内」口径：`:37` 删除「随包」断言或改为「3 个 ONNX 待核实 ⇒ 保守 AGPL」；`:36` 移出「随包清单」表（或加「历史，不在 0.1.1 包内」列）；`:53` 改为「上述 3 个待核实权重」；`:69` 勾选项改为「models 变体含待核实权重 ⇒ 保守 AGPL」 | open |
| P2-1 | P2 | `build-installer.ps1:180–192` | 只交叉校验「权重 ↔ license」，不校验「variant 名称 ↔ 权重」。合成用例：权重 + `variant=base` + `license=AGPL-3.0` → `BUILD_EXIT=0`，向导将显示「base 变体（**不含模型权重**，按 AGPL-3.0 分发）」，`LegalCopyright=AGPL-3.0 (base)` | `synth-weights-agpl` 实跑：`BUILD_EXIT=0`，`out-agpl\NewManga-9.9.9-setup.exe` 的 `LegalCopyright=AGPL-3.0 (base)`、`build-info.variant=base` | 许可方向是保守的（AGPL），无漏声明；但仍是对内容的错误陈述。建议 `:181` 兜底逻辑同样用于校验：`VERSION.json.variant` 与 onnx 存在性不符即 throw（或强制由文件推导） | open |
| P2-2 | P2 | `packaging/nsis/installer.nsi:64–69` | 无 `VARIANT_*` 定义时默认 `base / GPL-3.0-or-later`。`build-installer.ps1` 一定会传（且 `VERSION.json` 必存在），但 `.nsi` 文件头 `:3–5` 恰好教人手工 `makensis … -DSTAGE_DIR=<base stage>`；对手工编译权重 stage 会**静默**产出「base/GPL」声明，与注释「an unknown build is loud, not lying」相反 | 默认分支探针编译：`VARIANT_NAME=base VARIANT_LICENSE=GPL-3.0-or-later`；`ac3-nsis-variant-defines.log` 证明脚本路径会传定义 | 建议默认改为 `!error`（强制显式传变体），或默认值改为 `unknown` 之类不可作为许可声明的占位 | open |
| P2-3 | P2 | `apps/desktop-avalonia/scripts/package.ps1:105–107` | 注释仍写「the models variant ships Ultralytics YOLO11s-seg (AGPL-3.0)」；这是 P1-1 残留文字的上游来源 | 读代码即可复现 | 与 `:155–159` 的实测口径同步改写 | open |

P0/P1 计数：**P0 ×1（P0-1）、P1 ×1（P1-1）、P2 ×3（P2-1…P2-3）**。

## 9. 结论

### 9.1 方向 A 的执行是否成立

**成立（机制层面）**，理由均为实测而非引用卡面：

1. **声明跟着字节走**：`installer.nsi` 四处文案已无硬编码，`build-installer.ps1` 从 stage 的 `VERSION.json` 取变体与许可并传 ASCII 定义；自建编译与已产出 setup.exe 的 `LegalCopyright` 都是 `AGPL-3.0 (models)`，`base` 则回落到 `GPL-3.0-or-later (base)`。
2. **非法组合被挡住**：`:190–192` 的 throw 在「权重 + 非 AGPL」时确实触发（合成 stage 实跑 `BUILD_EXIT=1`，未产出 exe）；旧 stage 护栏实跑 `EXIT=1`（8 FAIL），判别力两侧都有。
3. **生成器口径自洽**：`package.ps1` 的 `models_bytes` 改为 ONNX 口径、`bundled_weights_license` 由实际文件生成；`ac3-models-version.json / package-manifest.json` 与实测 3 ONNX / 632,552,582 B 完全一致。
4. **证据链可信**：7/7 Canonical Evidence 的 sha256 与 `02c3aaeda` blob 相符，`ac3`/`ac4` 计数与本次复跑一致。
5. **诚实性达标**：三条限制如实写明，未把「保守过度声明」包装成「已核实」。

### 9.2 能否保持 `closed_with_limitations`

**可以保持，但不得原样保持，更不得改 `done`。**

- **不应回退 `blocked`**：方向 A 的规则、护栏与生成器都已在实测中工作；剩余的 `setup.exe` 陈旧文档属「打包时序」与「4 处残留文字」问题，不是方向选择问题。
- **不应升 `done`**：P0-1 使 AC2/AC3 的「随包」完成声明不成立；ZCode 裁定 Q2 把「随包合规文件与实物矛盾」定为 P0/禁止发布，P1-1 又是同一类陈述的仓库侧残留。
- **保持方式**：在卡面 Closeout Record 追加两条限制 ——（a）`a4b11458…` 这个 `setup.exe` 及 `pkgmodels2` stage **作废，不得发布/不得作为条件 4 证据**（与其现有「不构成发布验收」一致）；（b）P0-1 + P1-1 为**发布前返修项**（修文档 → 重打包 → 用 7z 比对包内三份文档 sha256 == 仓库根）。做完并可复现后，再谈是否收口。条件 4 仍须在新包字节上重跑（与 ZCode Q3 一致）。

### 9.3 边界声明

**本复核不构成产品发布验收，也不构成对上游许可的法律结论。** 三项随包权重的上游许可属性本复核**不予认定**（与 ZCode 裁定「证据不足」一致）；本报告只判定「声明是否跟随实物」「证据是否可复现」「护栏是否真拦住」，不判定 Apache-2.0/AGPL 的法律归属。本复核只对 `a5e57958b` 有效；该 head 之后若新增提交或新证据，本报告自动成为历史记录。

## 10. 复现清单（本复核新增的临时产物，均在 workspace，非仓库）

| 路径 | 用途 |
|---|---|
| `…\New Manga.workspace\tmp\lvd-review\stage\` | 审查项 3 的最小 stage（占位文件） |
| `…\tmp\lvd-review\lvd-test.exe` | 审查项 3 产物（81,837 B） |
| `…\tmp\lvd-review\installer-probe.nsi`、`probe-*.exe/.log` | `VARIANT_CONTENT` 分支判别探针（保留 UTF-8 BOM） |
| `…\tmp\lvd-review\synth-weights-gpl\`、`synth-weights-agpl\` | fail-closed 合成 stage（护栏 EXIT=0 通过；分别 `BUILD_EXIT=1` / `=0`） |
| `…\tmp\lvd-review\extract\` | 从 `setup.exe` 用 7-Zip 抽出的包内文档与 `VERSION.json` |
