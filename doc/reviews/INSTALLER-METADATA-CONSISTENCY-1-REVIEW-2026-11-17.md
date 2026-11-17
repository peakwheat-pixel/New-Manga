---
task_id: INSTALLER-METADATA-CONSISTENCY-1
reviewer: reviewer-imc
reviewer_kind: subagent
author: DSH
base_commit: 7f59ae461
reviewed_head: 96959e45c
decision: ACCEPTED_WITH_FINDINGS
reviewed_at: 2026-11-17 21:33–21:42 +08:00
---

# Review：INSTALLER-METADATA-CONSISTENCY-1（独立上下文复核）

**审查者身份与来源**：`reviewer-imc`，DSH（root `lead`）派发的独立上下文子 agent；**未参与**本卡的实现、返修或证据生成，未参与 `INSTALLER-MATRIX-1` 的取证。本复核只读仓库与 workspace 产物，除本文件外未写任何仓库文件（复核前后 `git status --porcelain` 均为空）。`reviewer_kind=subagent`（2026-10-31 用户裁决口径）。

**被审 head**：`96959e45c9a4f5b36854033c3f189f9719b023fb`（main）。复核窗口 `7f59ae461..96959e45c`，实际改动只有 `7b47a38d8`（脚本 + 证据）与 `96959e45c`（收口文档）两笔。

**口径**：本报告只对上述 head 有效；head 变化后自动属历史记录。decision 采用本次派发指定的 `ACCEPTED` / `ACCEPTED_WITH_FINDINGS` / `REJECTED` 三值（与 `doc/templates/REVIEW.md` 的 `approved/changes_requested` 枚举对应：`ACCEPTED_WITH_FINDINGS` ≈ 有保留地通过）。

---

## 一、7 项逐条判定

| # | 必测项 | 实测 | 判定 |
|---|---|---|---|
| 1 | 红测可复现（旧 stage 应 5 FAIL / EXIT=1） | 5 条 FAIL、`EXIT=1`，逐字与 `verification/INSTALLER-METADATA-CONSISTENCY-1/README.md:56-61` 一致 | **PASS** |
| 2 | 绿测可复现（fixture2 应 OK / EXIT=0） | fixture2 仍存在；`OK (exe, core_service, 0 onnx / 0 B …)`、`EXIT=0`，与 README:72 一致 | **PASS**（绿例是 5 文件合成 stage，不是 package.ps1 产物，见 F-02） |
| 3 | 新增检查是「加严」而非放宽/作弊 | diff `+59 / -0`；新增 6 类检查全部走 `Add-Failure`；原有检查一行未删未改；「排除 manifest 自身」理由成立（`package.ps1:157` 先枚举、`:160` 后写 manifest） | **PASS_WITH_FINDINGS**（F-04/F-05/F-06 为空档，非放宽） |
| 4 | 红测不是「既有失败」 | 用 `7b47a38d8^` 版脚本跑同一 stage：`OK (… 3 onnx / 632552582 B all match VERSION.json)`、`EXIT=0` | **PASS**（红测证明的是新增判别力） |
| 5 | stage 来源判断（非 package.ps1 干净输出） | manifest mtime `2026-10-28 13:16:59`、根/`app` 两个 `VERSION.json` 哈希不同、manifest 含 1010 条 `app/core-sidecar/python/*`：三条全部实测成立；结论成立 | **PASS_WITH_FINDINGS**（F-03：mtime 表述不准，但结论不受影响） |
| 6 | 卡片与门禁 | `check.ps1 -TaskPath …` → `Governance check: PASS (3 warnings)`、`EXIT=0`；`closed_with_limitations` 与 AC5 `<<PARTIAL>>` 恰当 | **PASS_WITH_FINDINGS**（F-01/F-02 要求更正证据与限制表述；F-07/F-08 文档精度） |
| 7 | 不得越界 | 无 Gate/检查器/NSIS 改动；`verification/**` 无 M/D（`--diff-filter=MD` = 0）；旧 stage 无任何文件 mtime ≥ 2026-11-16，总 `1037 files / 889,353,540 B / 848.15 MB` 与既有记录一致 | **PASS** |

---

## 二、实测记录（命令与输出）

### 2.1 环境与 head

```powershell
cd 'G:\CODEX\New Manga'; git rev-parse HEAD        # 96959e45c9a4f5b36854033c3f189f9719b023fb
git status --porcelain=v1                          # （空）
git log --oneline -4
# 96959e45c docs(tasks): … 收口（AC1-AC4/AC6 MET、AC5 部分）+ INSTALLER-MATRIX-1 补 L-IM-8
# 7b47a38d8 test(ci): verify-package-manifest 增加 package-manifest.json 交叉校验…
# 7f59ae461 docs(tasks): 新卡 INSTALLER-METADATA-CONSISTENCY-1 …
```

### 2.2 红测（第 1 项）

```powershell
pwsh -NoProfile -File tools/ci/verify-package-manifest.ps1 `
  -StageDir "G:\CODEX\New Manga.workspace\task-envs\INSTALLER-MATRIX-1\stage\NewManga-0.1.1-win-x64"
```

```
verify-package-manifest: FAILED with 5 problem(s)
  FAIL: package-manifest.json version mismatch: manifest=0.1.0 VERSION.json=0.1.1
  FAIL: package-manifest.json models_bundled mismatch: manifest=False actual=True (3 onnx files)
  FAIL: package-manifest.json models_bytes mismatch: manifest=0 actual=632552582
  FAIL: package-manifest.json lists 1968 file(s) but the stage holds 1036 (excluding the manifest itself)
  FAIL: package-manifest.json lists 1041 file(s) that are not in the stage (e.g. app/core-sidecar/python/plugin-python.sha256, …, python312.dll)
EXIT=1
```

判定：与卡面/README 记录的 5 条逐字一致（含缺失条目预览的前 5 个路径）。**只读**：复核期间未写该 stage；stage 内无 2026-11-16 之后 mtime 的文件（见 2.6）。

### 2.3 绿测（第 2 项）

```powershell
pwsh -NoProfile -File tools/ci/verify-package-manifest.ps1 `
  -StageDir "G:\CODEX\New Manga.workspace\tmp\r23\fixture2\NewManga-9.9.9-win-x64"
```

```
verify-package-manifest: OK (exe, core_service, 0 onnx / 0 B all match VERSION.json)
EXIT=0
```

fixture2 内容：`package-manifest.json`(826 B)、`VERSION.json`(470 B)、`app/NewManga.App.exe`、`app/VERSION.json`(470 B，与根同 sha256)、`app/core-sidecar/core_service.exe` 共 5 文件；manifest 列 4 条（不含自身），`bytes=37745588` 与实际相符 ⇒ 该绿例能证明「一致元数据不误报」，但**不能**证明 `package.ps1` 真实产物可通过（见 F-02）。

### 2.4 改动前校验器是否通过同一 stage（第 4 项）

```powershell
git show '7b47a38d8^:tools/ci/verify-package-manifest.ps1' |
  Set-Content "$workspace\tmp\reviewer-imc\verify-package-manifest-PRE.ps1" -Encoding utf8
pwsh -NoProfile -File "$workspace\tmp\reviewer-imc\verify-package-manifest-PRE.ps1" `
  -StageDir "<旧 stage>" -RepoRoot 'G:\CODEX\New Manga'
```

```
verify-package-manifest: OK (exe, core_service, 3 onnx / 632552582 B all match VERSION.json)
EXIT=0
```

结论：**红测不是既有失败**。旧 stage 的 `VERSION.json` 与 exe/sidecar/onnx 实物本来就自洽，5 条 FAIL 全部来自新增的 `package-manifest.json` 交叉校验 ⇒ 新增判别力成立。

### 2.5 stage 来源三条（第 5 项）

| 卡片/README 主张 | 实测 | 判定 |
|---|---|---|
| `package-manifest.json` mtime 2026-10-28 | `2026/10/28 13:16:59`（381,448 B；sha256 `68752b31…`，与 README:14 一致） | 成立 |
| 根 `VERSION.json` 与 `app/VERSION.json` 哈希不同 | `c8459587…fd9`(2,518 B) vs `5a8c6abf…e67`(2,063 B)；根文件多出 `bundled_weights_license` / `migration` / `installer` 三个字段 | 成立（`package.ps1:154` 的 `Copy-Item` 本应逐字节相同） |
| manifest 列了含 `app/core-sidecar/python/*` 的条目 | 1010 条 `app/core-sidecar/python/*`；当前 stage 无 `app/core-sidecar/python` 目录；1041 条所列路径不在 stage | 成立 |

补充（强化同一结论）：`package.ps1:141-151` 的 VERSION.json 模板**不产出**根文件中的 `models_bundled` / `models_bundled_bytes` / `models_bundled_detail` / `installer` 字段（`models_bundled` 只出现在 `:95` 的 `sidecar_build` 内），仓库内无脚本写 `models_bundled_detail` ⇒ 根/`app` 两个文件是**人工维护/改写**的，不是生成器输出。`doc/reviews/INSTALLER-MATRIX-1-CLOSEOUT-REVIEW-2026-11-17.md:58` 也记录根 `VERSION.json` 有 `models_bundled: true`，与本复核实测一致。

### 2.6 卡片与门禁（第 6 项）

```powershell
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/INSTALLER-METADATA-CONSISTENCY-1.md
```

```
Governance scope: 15 current documents; no historical directory scan.
WARN: 存在 2 个非终态 Task …
WARN: doc/STATUS.md 已达到预算的 80%：3162 bytes / 28 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：6724 bytes / 64 lines
Governance check: PASS (3 warnings)
EXIT=0
```

3 条 WARN 均为既有预算/台账提示，与本卡无关。

**证据 pin 校验（sha256_basis=BLOB）**：`git ls-files --eol` 显示 5 个证据文件中 4 个为 `i/lf w/crlf`（`core.autocrlf=true` 会改写工作区），按 LF 归一化后逐一重算：

| evidence | 卡片记录 | 重算（LF） | 判定 |
|---|---|---|---|
| EV-IMC-01 README.md | `e5fae254…172b` | `e5fae254…172b` | ✓ |
| EV-IMC-02 ac4-red-old-stage.log | `e557f37b…6887` | `e557f37b…6887` | ✓ |
| EV-IMC-03 ac5-green-consistent-stage.log | `2a049497…ad6f` | `2a049497…ad6f` | ✓ |
| EV-IMC-05 ac1-inconsistency.json | `15fd10bc…8d03` | `15fd10bc…8d03` | ✓ |
| EV-IMC-06 ac1-inconsistency.log | `c86feb09…5335` | `c86feb09…5335` | ✓ |
| EV-IMC-04 verify-package-manifest.ps1（SOURCE_PIN） | `87600784…2797` | `87600784…2797` | ✓ |

⇒ pin 本身按 BLOB 口径正确（工作区 CRLF 差异不构成 pin 失配）；F-01 是**被 pin 内容的真实性**问题，不是 pin 计算问题。

### 2.7 边界与不越界（第 7 项）

```powershell
git diff --name-status 7b47a38d8^ 96959e45c
# M doc/REBASELINE_PLAN.md, doc/STATUS.md, doc/TASK_LEDGER.md,
#   doc/tasks/INSTALLER-MATRIX-1.md, doc/tasks/INSTALLER-METADATA-CONSISTENCY-1.md,
#   tools/ci/verify-package-manifest.ps1
# A verification/INSTALLER-METADATA-CONSISTENCY-1/{README.md, ac1-inconsistency.json,
#   ac1-inconsistency.log, ac4-red-old-stage.log, ac5-green-consistent-stage.log}
git diff --name-status --diff-filter=MD 7b47a38d8^ 96959e45c -- verification/   # 0 行
git diff --name-status 7b47a38d8^ 96959e45c -- packaging/ tools/governance/ .github/
# 仅 M tools/ci/verify-package-manifest.ps1
```

- **Gate 判定未变**：未触碰 `packaging/nsis/installer.nsi`、`tools/governance/**`、任何 Gate 映射/裁定文档；`doc/STATUS.md` 只把 `closed_with_limitations` 计数 9→10 并列入本卡；`doc/REBASELINE_PLAN.md` 只把本卡移出「表外节点」；`INSTALLER-MATRIX-1.md` 为**末尾 append-only**（+20 行），其 AC7 仍是 `[ ]` + `<<PARTIAL: …NOT_RUN…>>`，条件 4 仍归 `RELEASE-GATE4-SIGNED-MATRIX-1`。
- **旧 stage 未被覆盖**：全部 1037 文件、总计 `889,353,540 B`（848.15 MB），与 `INSTALLER-MATRIX-1` 记录的「848.15 MB/1037 files」及 REVIEW 记录的 `889,353,540 B` 一致；无任何文件 `LastWriteTime ≥ 2026-11-16`（0 个）。
- **既有 `verification/**` 字节未变**：窗口内该目录只有 A（新增本卡 5 个文件），M/D = 0。
- 说明：本复核为证明空档所做的破坏性实验全部在 `G:\CODEX\New Manga.workspace\tmp\reviewer-imc\` 的**副本**上进行，未触碰 fixture2 原件与旧 stage。

---

## 三、「加严」专项分析（第 3 项）

### 3.1 只新增、未删减

`git show 7b47a38d8 -- tools/ci/verify-package-manifest.ps1`：`--numstat` = `59  0`（59 行新增、0 行删除），原 135 行校验逻辑（VERSION.json 存在性、exe sha256/bytes、`repo_head` 反解与 `git cat-file -e`、core_service sha256/bytes、onnx 数量/字节）逐字未动。新增 6 类检查：

1. `manifest.version == VERSION.version`
2. `manifest.variant == VERSION.variant`
3. `manifest.models_bundled` 存在且 == (onnx 数 > 0)
4. `manifest.models_bytes` 存在且 == 实测 onnx 总字节
5. `manifest.files` 条数 == stage 实际文件数（排除 manifest 自身）
6. `manifest.files` 每条 `path` 都真实存在于 stage

全部经 `Add-Failure` 进入同一 `$failures` 列表，最终 `exit 1`——没有任何「降级为 warning」「仅在特定 stage 生效」「读环境变量跳过」的旁路；不存在把 FAIL 变成 PASS 的代码路径。**「加严」成立。**

### 3.2 「排除 manifest 自身」的理由成立

`apps/desktop-avalonia/scripts/package.ps1`：

- `:157` `$files=Get-ChildItem $stage -Recurse -File`（枚举 stage）
- `:158-159` 逐文件写 `path/bytes/sha256`
- `:160` `$manifest | ConvertTo-Json … | Set-Content (Join-Path $stage 'package-manifest.json')`（**之后**才写 manifest）
- zip 输出在 `$OutputRoot`，不在 stage 内

⇒ manifest 不可能出现在自己的 `files` 列表里；排除自身是**生成器既定语义**，不是为通过检查而临时放水。且排除用 `FullName -eq`（PowerShell 字符串比较大小写不敏感），对正常路径足够。

### 3.3 存在的空档（如实评）

| 空档 | 是刻意还是遗漏 | 实测 | 影响 |
|---|---|---|---|
| 未逐文件校验 `sha256`/`bytes`（manifest 自身带这两个字段，`package.ps1:159`），也未校验 `manifest.bytes`/`sidecar_bytes` | **文档未声明**。AC3 只承诺版本/权重/文件集，代码注释也未说明；从「避免 build-installer 之后重写 VERSION.json 导致误报」的角度可解释为取舍，但没有记录 | 把 fixture2 副本的 `app/VERSION.json` 改成同尺寸 470 B 不同内容（新 sha256 `e1fc8e1d…`，manifest 仍记 `e6fe5f34…`）→ `OK / EXIT=0` | 内容级/字节级不一致可通过；卡片用来论证来源的「根/app 哈希不同」也不被该护栏覆盖 |
| 文件集只做「条数相等 + 所列路径存在」，不是集合相等 | 遗漏（无去重、无反向检查） | 把 manifest 的 `core_service.exe` 条目替换为 `VERSION.json` 的重复条目（条数不变）→ 仍有 1 个磁盘文件未被列出，但 `OK / EXIT=0` | 极端构造下可漏掉「有文件未描述」 |
| `-StageDir` 带尾部 `\` 时假阳性 | 遗漏（未归一化路径） | 同一一致 stage：不带 `\` → `OK/EXIT=0`；带 `\` → `FAILED with 1 problem(s)`（"lists 4 file(s) that are not in the stage"）、`EXIT=1` | `build-installer.ps1:88` 用 `Resolve-Path .Path`（无尾分隔符），CI 路径不触发；手工调用会误报 |

以上都是**不完整**，不是「放宽」或「作弊」；不影响红测 5 条 FAIL 的真实性，也不影响本卡核心结论。

---

## 四、Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 |
|---|---|---|---|---|---|
| F-01 | **P1** | `verification/INSTALLER-METADATA-CONSISTENCY-1/ac1-inconsistency.json:38`、`ac1-inconsistency.log:14`；生成器 `G:\CODEX\New Manga.workspace\tmp\r23\collect-metadata.py:26` | AC1 证据称「`VERSION.json` 无 `models_bundled` 字段」，与实物相反：该文件 2,518 B、sha256 `c8459587…fd9`（**与同一 JSON 自己记录的 `version_json_sha256` 相同**），内容含 `"models_bundled": true`、`"models_bundled_bytes": 632552582`、`"models_bundled_detail": "rtdetr…=171618071, decoder…=117480262, encoder…=343454249"`。collector 把该结论**硬编码**成字符串，不是实测。影响：CANONICAL 证据失实，读者会误判不一致类型（实际是 manifest 陈旧 0.1.0/false/0，而非 VERSION.json 缺字段）；不改变 5 条 FAIL | `Get-Content '<stage>\VERSION.json' -Raw`（见 2.5）；`Get-FileHash '<stage>\VERSION.json'`；`doc/reviews/INSTALLER-MATRIX-1-CLOSEOUT-REVIEW-2026-11-17.md:58` 同日已记录 `models_bundled: true` | 更正两个 AC1 证据文件为实测值（`VERSION.json models_bundled=true / 632,552,582 B`），红测输出不变；collector 入库或改为读 `vj.get("models_bundled")`；重出后同步更新 Canonical Evidence 的 sha256 pin |
| F-02 | **P1** | `apps/desktop-avalonia/scripts/package.ps1:89-96,141-151`；`tools/ci/verify-package-manifest.ps1:120-122`；`apps/desktop-avalonia/scripts/build-installer.ps1:148-155`；`.github/workflows/build-release.yml:101-115` | **生成器与护栏字段集不闭合（既有，非 7b47a38d8 引入）**：`package.ps1` 的 VERSION.json 模板只在 `sidecar_build` 内写 `models_bundled`，**没有顶层** `models_bundled`/`models_bundled_bytes`；护栏在顶层缺失时 `Add-Failure "VERSION.json has no models_bundled field"`；`build-installer.ps1:152` 在 makensis 前 fail-closed，CI 直接串联两者且无补字段步骤 ⇒ **干净 `package.ps1` 产物即使 manifest 完全自洽也会被拒**。因此 AC5 所述「干净目录重建后校验器通过」在现码下不可达，需同时改 `package.ps1`。卡片限制 2 只写「仍可能产出不一致 manifest（如复用未清理 stage）」，未披露此点 | 读 `package.ps1:151`（无顶层字段）、`verify-package-manifest.ps1:120-122`、`build-installer.ps1:152`、workflow:104/112；`git show 6485c44b8 --stat`（引入护栏时未改 package.ps1） | 开后续卡：让 `package.ps1` 由磁盘推导并写出顶层 `models_bundled`/`models_bundled_bytes`（或并入 stage 生成步骤）；在本卡 Closeout 限制清单 append 一条；**AC5 保持 `<<PARTIAL>>`，不得改 MET** |
| F-03 | P2 | `verification/.../README.md:16`；`doc/tasks/INSTALLER-METADATA-CONSISTENCY-1.md:134`；`doc/tasks/INSTALLER-MATRIX-1.md` 新增段 | 文档写「stage 其余文件 mtime 2026-11-15」；实测 1037 个文件中：9 个 `2026-10-27`（models）、11 个 `2026-10-28`（根目录 docs/scripts + manifest）、1017 个 `2026-11-15` ⇒「其余 11-15」不准。结论仍成立（manifest 由 `package.ps1:157→160` 在阶段末尾写出，其 10-28 mtime 与 11-15 的 exe/VERSION 并存即证明本轮未重生成；且 `Copy-Item` 会保留源 mtime，单看根文件 mtime 不足以论证） | `Get-ChildItem <stage> -Recurse -File \| Group-Object {$_.LastWriteTime.ToString('yyyy-MM-dd')}` | 改为「20 个文件早于 2026-11-01（models 10-27、根目录 10-28）；其余 1017 个 11-15」，并在三处同步 |
| F-04 | P2 | `tools/ci/verify-package-manifest.ps1:174-181` | `-StageDir` 末尾带 `\` 时，`$file.FullName.Substring($StageDir.Length + 1)` 少切一位 ⇒ 全部路径被判「不在 stage」，一致 stage 也 FAIL（假阳性） | 副本实测：`-StageDir "<path>"` → `OK/EXIT=0`；`-StageDir "<path>\"` → `FAILED with 1 problem(s)`、`EXIT=1` | 入口归一化：`$StageDir = (Resolve-Path -LiteralPath $StageDir).Path`（与 `build-installer.ps1:88` 一致） |
| F-05 | P2 | `tools/ci/verify-package-manifest.ps1:170-192`；`apps/desktop-avalonia/scripts/package.ps1:158-159` | 未校验 manifest 的逐文件 `sha256`/`bytes`、`manifest.bytes`、`sidecar_bytes` ⇒ 内容级不一致可通过；卡片用来论证来源的「根/app `VERSION.json` 哈希不同」也未被护栏覆盖。AC3 原文只要求版本/权重/文件集，故不是 overclaim，但 README「AC3 修复（只加严，不放宽）」与卡面均未登记该限制 | 副本把 `app/VERSION.json` 改成同尺寸不同内容（新 sha256 `e1fc8e1d…` vs manifest `e6fe5f34…`）→ `OK/EXIT=0` | 在 README/卡面登记为已知限制（或后续卡加逐文件校验，需同时评估 build-installer 之后改写 VERSION.json 的场景） |
| F-06 | P2 | `tools/ci/verify-package-manifest.ps1:176-192` | 文件集只校验「条数相等 + 所列路径存在」，manifest 内重复 `path` 可掩盖「某磁盘文件未列出」 | 副本把 `core_service.exe` 条目替换为 `VERSION.json` 重复条目 → `OK/EXIT=0`，但 `core_service.exe` 未被任何条目描述 | 增加反向检查（磁盘每个相对路径必须出现在 `files` 中），或直接比较 `HashSet` 集合并拒绝重复 `path` |
| F-07 | P2 | `doc/tasks/INSTALLER-METADATA-CONSISTENCY-1.md:105-112,118,125`；`verification/.../README.md:25` | ① Canonical Evidence 中 `EV-IMC-02`/`EV-IMC-03` 各重复一行（106/107 与 110/111）；② Resource Manifest 写「3 个文件（README + 2 日志）」，实测 evidence_dir **5 个文件**、Canonical Evidence 共 8 行（6 个唯一 evidence，另有 2 行重复）；③ README「实物 1,037」未注明含 manifest 自身（护栏口径 1,036）；④ 收口记录写 `build-installer.ps1:151` 调用，实测调用在 `:152`（`:149-151` 为存在性检查，`:153-155` 为 throw） | `Get-ChildItem verification\INSTALLER-METADATA-CONSISTENCY-1`；`Get-Content build-installer.ps1 \| Select -Skip 143` | 删重复行、把「3 个文件」改为「5 个文件」、注明 1,036/1,037 口径、行号改 152 |
| F-08 | P2 | `doc/tasks/INSTALLER-METADATA-CONSISTENCY-1.md:63`；`verification/.../README.md:3` | ① AC3 原文要求「manifest 的 version/models_bundled/models_bytes 由实际产物推导**或让脚本在写入前断言与 VERSION.json 一致**」，实际实现落在**发布护栏**（build-installer 之前），`package.ps1` 未改；收口已说明形态，但 AC3 行仍按原文标 `<<MET>>`，属语义偏移（结论可接受）；② README 头写 `head: 7f59ae461`，而红测依赖的脚本改动只存在于 `7b47a38d8`（当时为未提交工作区改动） | 读卡 63 行、README 3 行、`git log -- tools/ci/verify-package-manifest.ps1` | AC3 行 append「以发布护栏实现（见 Closeout Record）」；README 头改为「head=7f59ae461 + 未提交的 verify-package-manifest.ps1 改动（后入 7b47a38d8）」 |

**计数：P0 = 0；P1 = 2（F-01、F-02）；P2 = 6（F-03…F-08）。**

> F-02 是既有缺口（`6485c44b8` 引入护栏时未同步 `package.ps1`），**不是** `7b47a38d8` 引入，也不构成对本卡「加严」的否定；但它使本卡 AC5 的「重建后校验通过」在现码下无法达成，必须在限制清单里如实登记并另开卡，否则后续按 AC5 字面重跑会用错结论。

---

## 五、结论：加严是否成立、能否保持 `closed_with_limitations`

1. **「加严」成立（有保留）**：`+59/-0` 的纯新增，6 类检查全部为 failure；同一旧 stage 在改动前 `OK/EXIT=0`、改动后 `FAILED with 5 problem(s)/EXIT=1` ⇒ 新增了**真实判别力**，不是把既有失败包装成新发现，也没有删/弱化任何原检查。保留在：未逐文件校验 sha256/bytes（F-05）、文件集非集合相等（F-06）、尾分隔符假阳性（F-04）——都是**不完整**而非放宽。

2. **能否保持 `closed_with_limitations`：可以，但需三处收尾**：
   - **必须**：更正 AC1 证据中与实物相反的 `models_bundled` 表述（F-01，P1）；
   - **必须**：在限制清单补登「`package.ps1` 不写顶层 `models_bundled` ⇒ 干净重建也会被护栏拒绝」并开后续卡（F-02，P1）；**AC5 保持 `<<PARTIAL>>`，不得改 MET**；
   - **建议**：F-03/F-07/F-08 文档精度修正；F-04/F-05/F-06 登记为限制或后续加严。
   
   `status: closed_with_limitations` 这一档本身是恰当的：AC4 判别力与 AC1 复现有实测、AC6 边界成立；AC5 客观上未做完整重建（且如 F-02 所示，现码下做了也不会通过），`<<PARTIAL>>` 正确。**不能**因为「红测 5 条 FAIL 很漂亮」就把 AC5 升为 MET。

3. **不改变任何 Gate 判定**：条件 4 仍归 `RELEASE-GATE4-SIGNED-MATRIX-1`；`INSTALLER-MATRIX-1` 的 AC7 仍 `[ ]`/PARTIAL；本次只新增了一条限制（L-IM-8）。

---

## 六、本复核不构成产品发布验收

本报告只回答派发的 7 项问题，**不构成**任何产品发布验收、Gate 判定、签名/许可证裁定或对 `setup.exe` 安装行为的验收。未执行：`package.ps1` 完整重建（~1.4 GB sidecar + ~800 MB zip）、`build-installer.ps1`/makensis 出包、安装/卸载/四页可达性、Gate 条件 4 签名矩阵。上述结论不得被引用为「包元数据已修复」——本卡证明的是「不一致产物会被拦住」，生成器侧的修复（F-02）仍未完成。

---

## 七、推荐下一步

1. **DSH（本卡收尾，append-only）**：按 F-01 更正 `verification/INSTALLER-METADATA-CONSISTENCY-1/ac1-inconsistency.json` 与 `.log`（`VERSION.json models_bundled=true / 632,552,582 B`），重出后更新 EV-IMC-05/06 的 sha256 pin；按 F-02 在 Closeout 限制清单补登生成器字段缺口；按 F-03/F-07/F-08 修正文档精度。
2. **新开一张卡（建议 Owner：DSH）**：`PACKAGE-VERSION-JSON-DERIVED-1` —— 让 `apps/desktop-avalonia/scripts/package.ps1` 由磁盘/产物推导写出顶层 `models_bundled`/`models_bundled_bytes`（并评估是否由同一处推导 `content` 字段），使「干净重建 + `verify-package-manifest.ps1` 通过」成为可达目标；该卡完成前 AC5 不得升级。
3. **可选**：对 `tools/ci/verify-package-manifest.ps1` 做小步加严（F-04 路径归一化、F-06 集合反向检查）；F-05 逐文件 sha256 校验需先确认 build-installer 之后是否会重写 stage 内文件，避免误报。
