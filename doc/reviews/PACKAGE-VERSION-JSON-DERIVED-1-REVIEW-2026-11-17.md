---
task_id: PACKAGE-VERSION-JSON-DERIVED-1
reviewer: reviewer-pvd
reviewer_kind: subagent
author: DSH
base_commit: 3ea6ea40d
reviewed_head: 1d2eae9dd
decision: ACCEPTED_WITH_FINDINGS
reviewed_at: 2026-11-17 21:52–22:10 (+08:00)
---

# Review：PACKAGE-VERSION-JSON-DERIVED-1（独立上下文复核）

**审查者身份与来源**：`reviewer-pvd`，DSH（root `lead`）派发的独立上下文子 agent；**未参与**本卡的实现、返修或证据生成，也未参与 `INSTALLER-METADATA-CONSISTENCY-1` 的取证。本复核只读仓库与 workspace 产物；除本文件外**未写任何仓库文件**；workspace 只在 `G:\CODEX\New Manga.workspace\tmp\review-pvd\` 下创建复核用临时 stage，**未改** `tmp\r23\red-nofield` 与任何 task-env fixture。`reviewer_kind=subagent`（2026-10-31 用户裁决口径）。

**被审 head**：`1d2eae9dd1c4da6548114eb3057182f4c8d9383a`（main）。复核开始（2026-11-17 21:52:58 +08:00）时 `git status --porcelain` 为空。
**复核期间的仓库移动（如实记录）**：

- main 在复核中前进到 `678a434defc8ee29a5943c0066aee67bd74c03cc`（仅 `doc/handoffs/NEXT-SESSION-STARTER.md` 的 R23 收尾追加）。`package.ps1` 两 head blob 均为 `2e2e5f4b243233d118d6a4dea23d3c1dd0761f8e`，护栏均为 `b522ea8acd6f1166131ef80ddfd718cf3410d103` ⇒ 本报告运行证据对 `1d2eae9dd` 仍然有效。
- 约 22:00 另一会话并行修改 license 变体线文档（`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、`doc/tasks/INSTALLER-MATRIX-1.md`、`doc/reviews/ZCODE-RULING-INSTALLER-LICENSE-2026-11-17.md`、`doc/tasks/LICENSE-VARIANT-DECLARATION-1.md`），并随后提交为 `349ccf121`（`docs(gate): 采纳 ZCode 裁定（许可声明非法/P0 发布阻塞/非条件 4 证据）+ 新卡 LICENSE-VARIANT-DECLARATION-1（等用户选向）`）。**非本复核所为**，本报告不评审；已按 blob 复核：`349ccf121` 未触及 `package.ps1`（仍 `2e2e5f4b…`）、护栏（仍 `b522ea8a…`）、本卡文件与 `verification/PACKAGE-VERSION-JSON-DERIVED-1/**`。报告定稿时 `git status` 只有本报告一个未跟踪文件。

**口径**：本报告只对上述 head 有效；head 变化后自动属历史记录。decision 采用派发指定的 `ACCEPTED` / `ACCEPTED_WITH_FINDINGS` / `REJECTED` 三值。

---

## 一、7 项逐条判定

| # | 必测项 | 实测 | 判定 |
|---|---|---|---|
| 1 | 改动最小且正确；两字段由既有磁盘推导 | `a370a1f39` 对 `package.ps1` 仅 1 行替换（`1/1`）；唯一 hunk 在 `:151`，只追加 `models_bundled=$modelsBundled;models_bundled_bytes=[int64]$modelsBytes;`，未动其它逻辑。`:80` `$modelsBundled=(Test-Path .../models)`、`:81` `$modelsBytes=...Get-ChildItem .../models ... Measure-Object Length` 均为改动前既有代码，不是新开关 | **PASS**（最小性与推导来源成立；数值口径问题见 F-PVD-01） |
| 2 | 语法与运行 | `Parser::ParseFile` → `parse-errors: 0` | **PASS** |
| 3 | 红测可复现 | `red-nofield` 仍在；护栏 `FAILED with 3 problem(s)`、exit 1，**首条**逐字为 `FAIL: VERSION.json has no models_bundled field (must be derived from the stage, not omitted)`，与证据一致 | **PASS_WITH_FINDINGS**（可复现；后 2 条为夹具派生噪声，见 F-PVD-03） |
| 4 | 护栏没被削弱 | `git diff --numstat 7b47a38d8^..HEAD -- tools/ci/verify-package-manifest.ps1` = `98 0`：**最终 diff 相对基线纯新增、0 删除**。分提交看 `7b47a38d8` +59/0；`9c0939f2e` +42/-3 —— 那 3 行是替换 `7b47a38d8` **自己新加**的行（`$actualPaths`→`$actualByRel` 等），替换后更强（集合相等 + 重复 + 逐文件 bytes/sha256），相对基线仍是 0 删除 | **PASS** |
| 5 | AC4 的 PARTIAL 是否诚实 | 按派发命令实跑：package.ps1 在 `:51` 抛 `sidecar bundle has no build-manifest.json ...`，**exit=1**（4.5 s），与 README/卡面一致 ✓。但 **PARTIAL 的理由不完整**：我补做「有 build-manifest 的 sidecar」忠实 e2e（其余同既有 sidecar）后，package.ps1 exit 0、护栏仍 **exit 1（3 条 FAIL）**；干净 base 变体也 exit 1（1 条 FAIL，`no app_build section`）。即：**即使 `build_sidecar.ps1 -Force` 完成，AC4 依然不可达** | **PASS_WITH_FINDINGS**（记录本身诚实；limitation 漏了两条硬阻断，见 F-PVD-01/02） |
| 6 | 卡片与门禁 | `check.ps1 -TaskPath doc/tasks/PACKAGE-VERSION-JSON-DERIVED-1.md` → `Governance check: PASS (3 warnings)`、**exit 0**（无卡级错误）。`closed_with_limitations` + AC4 `<<PARTIAL>>` 本身未冒充 MET；但 AC3 标 MET 与 AC4 PARTIAL 自相矛盾（F-PVD-03），卡面测试记录陈旧（F-PVD-04） | **PASS_WITH_FINDINGS** |
| 7 | 不得越界 | 被审区间 `3ea6ea40d..1d2eae9dd` 仅 6 个文件：`package.ps1`(M)、`REBASELINE_PLAN.md`(M)、`TASK_LEDGER.md`(M)、本卡(M)、`verification/.../README.md`(A)、`.../ac3-red-...log`(A)。**0 个** `installer.nsi` / `packaging/nsis` / `LICENSE*` / `NOTICE*` / `THIRD_PARTY*` / `tools/ci` / governance 文件；`package.ps1` 许可证字段（`:149-150`）未动；本卡三笔提交未改护栏或任何 Gate 判定 | **PASS** |

**证据 pin 复核（附加项）**：按 `sha256_basis=BLOB` 口径（`git cat-file blob` 原始字节）重算，3/3 与卡面一致 —— `package.ps1` `118ca3ae…fb65`、红测日志 `8a6b7805…b25`、README `3cebfc4b…9343`。**无 finding**。（工作树 `Get-FileHash` 因 CRLF 与 blob 不同，属检出过滤，不是 pin 错误。）

---

## 二、实测记录

### 2.1 第 1 项：修复 diff 与推导来源

```powershell
git show a370a1f39 --stat --format="%H%n%an%n%ad%n%s"
git show a370a1f39 -- apps/desktop-avalonia/scripts/package.ps1
git show --numstat --format="" a370a1f39
# 1  1  apps/desktop-avalonia/scripts/package.ps1
# 6  0  verification/PACKAGE-VERSION-JSON-DERIVED-1/ac3-red-missing-toplevel-field.log
```

唯一 hunk：

```diff
@@ -148,7 +148,7 @@
 $bundledWeightsLicense=if($modelsBundled){...}else{...}
-@{version=$Version;...;models=$modelsStrategy;sidecar='bundled: ...';...}
+@{version=$Version;...;models=$modelsStrategy;models_bundled=$modelsBundled;models_bundled_bytes=[int64]$modelsBytes;sidecar='bundled: ...';...}
```

`1d2eae9dd:package.ps1:80-81`（修复前既有，未被本提交改动）：

```powershell
$modelsBundled=(Test-Path (Join-Path $sidecarDst 'models'))
$modelsBytes=if($modelsBundled){(Get-ChildItem (Join-Path $sidecarDst 'models') -Recurse -File|Measure-Object Length -Sum).Sum}else{0}
```

判定：新增字段确实取自上两行；`-WithModels` 只决定 robocopy 是否 `/XD models`（`:73`），最终值读的是落盘后的 `$sidecarDst`，不是新开关。

### 2.2 第 2 项：语法

```powershell
pwsh -NoProfile -Command '$e=$null; [void][System.Management.Automation.Language.Parser]::ParseFile("apps\desktop-avalonia\scripts\package.ps1",[ref]$null,[ref]$e); $e.Count'
# parse-errors: 0
```

### 2.3 第 3 项：红测（复现）

```powershell
pwsh -NoProfile -File tools/ci/verify-package-manifest.ps1 -StageDir "G:\CODEX\New Manga.workspace\tmp\r23\red-nofield"
```

```text
verify-package-manifest: stage=G:\CODEX\New Manga.workspace\tmp\r23\red-nofield repo=G:\CODEX\New Manga

verify-package-manifest: FAILED with 3 problem(s)
  FAIL: VERSION.json has no models_bundled field (must be derived from the stage, not omitted)
  FAIL: package-manifest.json bytes mismatch for 1 file(s): VERSION.json (manifest=470 actual=442)
  FAIL: package-manifest.json sha256 mismatch for 1 file(s) (e.g. VERSION.json)
red-test exit code: 1
```

与证据一致。夹具实测：`red-nofield/VERSION.json` = 442 B，而 manifest 条目记 470 B ⇒ 第 2/3 条是被删字段后**未同步 manifest** 的派生噪声，非缺字段判别力本身（详见 F-PVD-03）。

### 2.4 第 4 项：护栏是否被削弱

```powershell
git diff --numstat 7b47a38d8^..HEAD -- tools/ci/verify-package-manifest.ps1
# 98  0  tools/ci/verify-package-manifest.ps1
git show --numstat --format="%h" 7b47a38d8 -- tools/ci/verify-package-manifest.ps1   # 59 0
git show --numstat --format="%h" 9c0939f2e -- tools/ci/verify-package-manifest.ps1   # 42 3
```

`9c0939f2e` 的 3 行删除是替换 `7b47a38d8` 新加的 `$actualPaths` 块，换成 `$actualByRel` + `$seen`/`$duplicates`/`$badBytes`/`$badHash`/`$unlisted`，属**加强**；相对基线 `7b47a38d8^` 最终为纯新增。另核：护栏基线版（`7b47a38d8^`）**本来就要求** `app_build`（`if (-not $version.app_build) { Add-Failure ... }`），不是新加要求。

### 2.5 第 5 项：AC4 实跑 + 补充端到端（关键）

**(a) 派发命令原样（sidecar 无 `build-manifest.json`）**

```powershell
pwsh -NoProfile -File apps/desktop-avalonia/scripts/package.ps1 -Version 0.1.1 -WithModels `
  -OutputRoot "G:\CODEX\New Manga.workspace\tmp\review-pvd\out" `
  -SidecarDir "G:\CODEX\New Manga.workspace\task-envs\INSTALLER-MATRIX-1\stage\NewManga-0.1.1-win-x64\app\core-sidecar"
```

```text
Exception: G:\CODEX\New Manga\apps\desktop-avalonia\scripts\package.ps1:51
Line |
  51 |      throw ("sidecar bundle has no build-manifest.json under $SidecarD ...
     |      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     | sidecar bundle has no build-manifest.json under G:\CODEX\New
     | Manga.workspace\task-envs\INSTALLER-MATRIX-1\stage\NewManga-0.1.1-win-x64\app\core-sidecar -- it cannot prove
     | which schema it understands. Rebuild it with packaging/m2ac5/build_sidecar.ps1 -Force (that script writes the
     | manifest).
elapsed=4.5s exit=1
```

与 `verification/.../README.md:34-45` 记录一致。**注意**：该失败发生在 VERSION.json 写入之前，所以它证明不了「修好生成器后会过闸」。

**(b) 忠实 e2e：给 sidecar 补上 `build-manifest.json`（模拟 `build_sidecar.ps1 -Force` 之后；其余同既有 sidecar）**

构造（仅在 `tmp\review-pvd\`）：复制既有 stage sidecar 的 5 个 exe，加
`build-manifest.json = {"schema_version":14,"git_head":"678a434d…"}`（与 `src/infrastructure/sqlite/schema.py` 的 V14 一致），
`models/detector/fake.onnx` 1000 B + `models/ocr/config.json` 71 B（结构模仿 `build_sidecar.ps1:147-169` 会复制的 config/vocab）。

```powershell
pwsh -NoProfile -File apps/desktop-avalonia/scripts/package.ps1 -Version 0.1.1 -WithModels `
  -OutputRoot "G:\CODEX\New Manga.workspace\tmp\review-pvd\out-e2e" `
  -SidecarDir "G:\CODEX\New Manga.workspace\tmp\review-pvd\fake-sidecar"
# elapsed=7.6s exit=0
# VERSION.json: variant=models, models_bundled=True, models_bundled_bytes=1071

pwsh -NoProfile -File tools/ci/verify-package-manifest.ps1 `
  -StageDir "G:\CODEX\New Manga.workspace\tmp\review-pvd\out-e2e\NewManga-0.1.1-win-x64-models"
```

```text
verify-package-manifest: FAILED with 3 problem(s)
  FAIL: VERSION.json has no app_build section
  FAIL: models_bundled_bytes mismatch: json=1071 actual=1000
  FAIL: package-manifest.json models_bytes mismatch: manifest=1071 actual=1000
guardrail exit=1
```

**(c) 干净 base 变体（同一假 sidecar，不加 `-WithModels`）**

```text
package.ps1 exit=0
VERSION.json: variant=base, models_bundled=False, models_bundled_bytes=0
verify-package-manifest: FAILED with 1 problem(s)
  FAIL: VERSION.json has no app_build section
guardrail exit=1
```

**(d) 对照实验（证明上面两条就是全部原因，且护栏本身可满足）**

把 (b) 的 stage 复制一份，手工补 `app_build{exe_sha256, exe_bytes, repo_head}` 并把 `models_bundled_bytes`/
`package-manifest.models_bytes` 改为护栏口径（1000 B），重生成 manifest：

```text
verify-package-manifest: OK (exe, core_service, 1 onnx / 1000 B all match VERSION.json)
exit=0
```

**(e) 真实 sidecar 的算术（不是合成值）**

- 既有 `app/core-sidecar/models/`：9 个文件 = **632,662,260 B**（3 个 `*.onnx` = **632,552,582 B**；5 个 json + vocab.txt = **109,678 B**）。
- `package.ps1:81` 口径 = 全部 9 个文件 → `models_bundled_bytes=632,662,260`；
  护栏 `:119-122` 口径 = 仅 `*.onnx` → 632,552,582 ⇒ **必差 109,678 B**。
- `packaging/m2ac5/build_sidecar.ps1:147-169` 明确复制 `vocab.txt` 与 5 个 config json ⇒ **重建 sidecar 不会消除差额**。

### 2.6 第 6 项：卡片与门禁

```powershell
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/PACKAGE-VERSION-JSON-DERIVED-1.md
```

```text
Governance scope: 15 current documents; no historical directory scan.
Task: doc\tasks\PACKAGE-VERSION-JSON-DERIVED-1.md
WARN: 存在 2 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3162 bytes / 28 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：6724 bytes / 64 lines
Governance check: PASS (3 warnings)
check.ps1 exit code: 0
```

（该次运行在 `678a434d` 干净工作树上；本卡文件与 `1d2eae9dd` 相同。）

### 2.7 第 7 项：不得越界

```text
git diff --name-status 3ea6ea40d..1d2eae9dd
M  apps/desktop-avalonia/scripts/package.ps1
M  doc/REBASELINE_PLAN.md
M  doc/TASK_LEDGER.md
M  doc/tasks/PACKAGE-VERSION-JSON-DERIVED-1.md
A  verification/PACKAGE-VERSION-JSON-DERIVED-1/README.md
A  verification/PACKAGE-VERSION-JSON-DERIVED-1/ac3-red-missing-toplevel-field.log
```

禁改模式命中数 0（`*.nsi` / `packaging/nsis` / `LICENSE*` / `NOTICE*` / `THIRD_PARTY*` / `tools/ci` / governance）。
`package.ps1` 的 diff 只有 `:151` 一行，`:149-150` 的 license 声明未变。证据 pin 按 BLOB 口径 3/3 匹配（见 §一 附加项）。

---

## 三、Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| F-PVD-01 | **P1** | `apps/desktop-avalonia/scripts/package.ps1:81,151`；`tools/ci/verify-package-manifest.ps1:119-122,132-137,169-173` | `$modelsBytes` 统计 `models/` 下**全部文件**，护栏只累加 `*.onnx`。`-WithModels` 干净 stage 的 `VERSION.json.models_bundled_bytes` 与 `package-manifest.models_bytes` 都会比护栏值大 ⇒ **FAIL**。真实 sidecar 差额 109,678 B，且 `build_sidecar.ps1` 会复制 config/vocab，重建 sidecar 不会消除。卡的目标「干净产物过闸」因此不成立；AC4 即便重建 sidecar 也不可达 | §2.5(b)(e)：`FAIL: models_bundled_bytes mismatch: json=1071 actual=1000`、`package-manifest.json models_bytes mismatch: manifest=1071 actual=1000`（exit 1）；真实数据 632,662,260 vs 632,552,582 | 让 `models_bundled_bytes`（及 `package-manifest.models_bytes`）按护栏口径只计 `*.onnx`；若认为护栏口径应改为全目录，须 DSH 裁决且不得放宽。另注：`models_bundled` 布尔是「models 目录存在」而非「onnx>0」，空目录场景也会不一致，建议一并改为 `onnx count -gt 0` | open |
| F-PVD-02 | **P1** | `apps/desktop-avalonia/scripts/package.ps1:151`；`tools/ci/verify-package-manifest.ps1:63`；`build-installer.ps1:148-155` | 干净 `package.ps1` 的 `VERSION.json` 模板**没有 `app_build` section**（全仓无任何脚本写它；`git log -S app_build -- package.ps1` 为空）。护栏缺 section 即 FAIL，`build-installer` fail-closed ⇒ **base 与 models 变体都过不了闸**，与 sidecar 无关。卡面/README/closeout 的 limitation 只写「sidecar 无 build-manifest」，即使 `build_sidecar.ps1 -Force` 完成，AC4 仍不可达；CI 的 package→build-installer 链路也会在 fail-closed 闸前失败（`.github/workflows/build-release.yml:100-115` 无补字段步骤） | §2.5(b)(c)：干净 base `FAILED with 1 problem(s): VERSION.json has no app_build section`（exit 1）；models 3 条 FAIL 含同条 | 后续卡在 `package.ps1` 写 `app_build`：`exe_sha256`/`exe_bytes` 实测 + `repo_head` 从 exe `ProductVersion` 反解（与护栏 `:82-95` 同口径）；并在卡面 limitation 补记本阻断。**不得**把 AC4 改 MET | open |
| F-PVD-03 | P2 | `doc/tasks/PACKAGE-VERSION-JSON-DERIVED-1.md:54`；`verification/PACKAGE-VERSION-JSON-DERIVED-1/README.md:24-32`；`tmp\r23\red-nofield` 夹具 | AC3 原文含「修复后同流程 → PASS」，但证据只有红（EXIT=1），无任何 post-fix PASS；与 AC4 PARTIAL 自相矛盾（同一个 green 流程）。红测夹具是派生 stage（`VERSION.json` 442 B vs manifest 记 470 B），3 条 FAIL 的后 2 条是「删字段后未同步 manifest」的噪声，不是判别力本身 | §2.3 输出；`Get-Content red-nofield\VERSION.json` 442 B；manifest 条目 470 B | AC3 改为 red-only 或降 PARTIAL；红测说明注明后 2 条为夹具派生噪声；不得用「3 problem(s)」暗示 3 条独立判别力 | open |
| F-PVD-04 | P2 | `doc/tasks/PACKAGE-VERSION-JSON-DERIVED-1.md:71-75,83-87` | 卡面「测试要求」三行仍全为 `NOT_RUN/无`，「交付与运行记录」仍写「Handoff：尚无。Review：尚无。实际测试：尚无」，与 Closeout Record、`verification/PACKAGE-VERSION-JSON-DERIVED-1/` 及本 Review 直接矛盾。`check.ps1` 不校验这类内容，PASS 不能替代人工核对 | 卡面行号与 closeout 对照 | 收口时回填测试结果与 Review 路径；Review 字段可写本报告 | open |

**计数：P0=0，P1=2，P2=2。**

---

## 四、Architecture / Verification 结论

**Architecture**：改动只在打包元数据生成端一行，不触及分层、契约、依赖、持久化、安全或许可证声明；无 scope creep。**主要架构风险不在代码结构，而在元数据语义**：生成端（全目录字节）与校验端（仅 onnx 字节）使用的是两个不同口径，F-PVD-01 属此类；F-PVD-02 是「校验器要求一个从未有生成器的 section」的跨卡缺口。

**Verification**：7 项中第 1/2/3/4/7 项 PASS，第 5/6 项 PASS_WITH_FINDINGS。关键补充实测证明：**即使给 sidecar 补上 `build-manifest.json`，干净 `package.ps1` 产物仍被护栏拒绝**（models 3 FAIL / base 1 FAIL）；把 `app_build` 补上并把 models 字节改为 onnx 口径后，同一 stage 即 `OK (… 1 onnx / 1000 B all match VERSION.json)`、exit 0 —— 两条阻断是充分且可修的。

---

## 五、结论与复审

- **这次修复是否成立**：作为「在 `VERSION.json` 模板中写出由磁盘推导的 `models_bundled` / `models_bundled_bytes`」的修复——**成立**：最小、语法通过、数据来自 `:80-81` 既有推导、红测首条 FAIL 可复现、护栏未削弱、无越界、证据 pin 3/3 真实。作为「让干净 `package.ps1` 产物过闸」的修复——**不成立**：F-PVD-01（models 变体字节口径）与 F-PVD-02（缺 `app_build`，base/models 都中）仍然阻断；AC4 的 PARTIAL 理由只写了第一道门（sidecar 无 build-manifest），漏了这两条。
- **decision**：**ACCEPTED_WITH_FINDINGS**。接受这一行变更本身，但不接受「干净产物已可过闸」的推论；P1 必须由 DSH 处置。
- **能否保持 `closed_with_limitations`**：**可以保持该终态标签**——它没有把 AC4 写成 MET，AC4 `<<PARTIAL>>` 在当前事实下是恰当的（甚至更应当强调 blocked）。但**当前 limitation 文本不准确**：它暗示「重建 sidecar 即可端到端」，实测证伪。因此我的口径是：**只有在补记 F-PVD-01/02（或转后续卡）后，这个 `closed_with_limitations` 才算准确**；否则该收口不完整。建议新开后续卡（如 `PACKAGE-VERSION-JSON-COMPLETE-1`）处理 `app_build` 与 onnx 字节口径，本卡不必返修以保持证据链；**AC4 保持 PARTIAL，不得改 MET**。
- **剩余风险**：F-PVD-01/02 修复前，CI/手工发布走标准 `package.ps1 → build-installer.ps1` 路径仍会在 fail-closed 闸处失败；若有人手工补 `VERSION.json` 绕过，则回到 `INSTALLER-MATRIX-1` 那类「手写元数据」风险。
- **复审**：head 变化或 P1 处置后追加新 head 与 disposition，不覆盖本记录。

**声明：本复核不构成产品发布验收。** 它只对 `1d2eae9dd` 上的本卡变更与证据做独立技术核查；发布 Gate、安装包验收与用户可见行为仍需 DSH 的集成验证与另行授权。
