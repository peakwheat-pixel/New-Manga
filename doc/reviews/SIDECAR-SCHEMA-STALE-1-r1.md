# SIDECAR-SCHEMA-STALE-1 独立复核（r1）

- 审查者：`reviewer`（由 lead 派发的独立上下文子 agent；未参与 SIDECAR-SCHEMA-STALE-1 的实现与返修）
- 被审 head：`1803b2f5f`
- 时间：2026-11-16（+08:00）
- 结论：**CHANGES_REQUESTED**

> 审查基线说明：本次复核以 `1803b2f5f8a94d54eb22a3a015373df031d912e4` 为基线（其父提交 `f7d273d9a`；真正的代码改动在 `f7d273d9a`，`1803b2f5f` 本身只改任务卡 1 行）。审查期间仓库 HEAD 于 03:49:08 前进到 `caca93978`（同一作者新提交，见「后到提交的影响」），本报告仍按任务要求对 `1803b2f5f` 判定；后到提交带来的变化单独备注。

## 环境与只读声明

- 全部操作只读：`git log/show/diff`、读取文件、`Select-String`、`Get-FileHash`、用 build venv 的 Python 只读解析 `.pyc`（不执行被审 exe、不跑 `test.ps1`、不写仓内文件）。
- 唯一写入文件：本报告。
- 读取了下列仓外证据（workspace 属项目约定的派生产物目录）：`G:\CODEX\New Manga.workspace\tasks\SIDECAR-SCHEMA-STALE-1\*`、`...\B1-DOC-CLOSE-1\test-ps1.log`、`...\RELEASE-PACKAGE-BUNDLE-1\review-r1.md`、`...\artifacts\release\*`、`...\task-envs\FINAL-VALIDATION-1\out\*`、`...\task-envs\HOST-RESOURCE-SECURITY-1\evidence-rerun\*`、legacy Tauri 产物目录。

## 逐主张判定

### 主张 1：版本对照是否准确 —— **不成立（数字对，对象错）**

数据本身对：

```
$ Select-String -Path src/infrastructure/sqlite/schema.py -Pattern 'SCHEMA_VERSION_V'
L24..L56: SCHEMA_VERSION_V1 … SCHEMA_VERSION_V14（14 个常量）
$ python -c "from infrastructure.sqlite.schema import default_migrations; ..."
count= 14
versions= [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
max= 14
```

v14 与 v6 的差确实是 8。但**「旧 sidecar bundle 认 v6」这个对象指认是错的**：

1. **被审变更之前，仓库 bundle 里的 schema 已经是 v14。** 证据是变更前打的 release 包 `NewManga-e2c9fd058-win-x64`（2026-11-15 22:08 构建，早于本次重建）里的 sidecar：五个 exe mtime 全是 `2026-11-15 03:16:55`（即 `SIDECAR-REBUILD-1` 重建的那一份，不是 10/23 老产物）。用 build venv 只读解析其 `core-sidecar/_internal/infrastructure/sqlite/schema.pyc`：

```
old_release: sha256(data)=f1058b0768e4…  SCHEMA_NAMES=14  [V1..V14]
             default_migrations: contains V14=True, V-names=14, MIG_NAMES=14
new_bundle : sha256(data)=f1058b0768e4…  （与重建后的新 bundle 字节完全相同）
```

   且 `RELEASE-PACKAGE-BUNDLE-1/review-r1.md` L32 在重建前（22:29）已独立核对：包内 sidecar 与 `apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar/` **文件数/字节/SHA-256 逐一相同** ⇒ 变更前的 bundle = release 内 sidecar = v14。
   尺寸也能交叉印证：新 bundle 835.25 MiB − `python/` 43.56 MiB = 791.69 MiB，恰等于 release sidecar 的 1,024 文件 / 791.69 MiB（新 bundle 1,967 文件 = 1,024 + 942 + 1 个新 manifest）。

2. **被审材料自己引用的失败日志，跑的并不是 bundle。** `B1-DOC-CLOSE-1/test-ps1.log` L72 明确记录：

```
"sidecar": "G:\\CODEX\\New Manga.workspace\\task-envs\\HOST-CORECLIENT-1\\sidecar-copy\\core_service.exe"
```

   即报 `database schema v14 is newer than this application knows (v6)`（L377/384/403/410）的是 **workspace 里的测试副本 `sidecar-copy`**，不是 `build/sidecar` bundle。

3. **v6 的真正来源是 legacy Tauri 旧产物。** `apps/desktop-avalonia/scripts/prepare-sidecar.ps1` 的默认 `-Source` 仍指向 legacy 路径 `apps/desktop/src-tauri/target/release/resources/core-sidecar`；该目录存在，exe 全部是 `2026-10-23 19:21:28`（`core_service.exe` 68,887,500 B）。schema 时间线：`SCHEMA_VERSION_V6` 加入于 2026-10-23 15:01、`V7` 加入于 2026-11-03 ⇒ 10/23 19:21 构建的 sidecar 运行时最大值必然是 **v6**。`test.ps1:18` 默认 `SidecarDirectory` 是 `sidecar-copy`，`test.ps1:39-41` 只在目录**不存在**时才调用 `prepare-sidecar.ps1` ⇒ 该副本一旦生成就永久复用。

4. **卡片点名的包反而是反证。** 卡面写「如 `NewManga-0.2.0-dev-win-x64-models` 内含这个 v6 sidecar」。实测该包（`workspace/task-envs/FINAL-VALIDATION-1/out/NewManga-0.2.0-dev-win-x64-models/app/core-sidecar`）`core_service.exe` 为 400,098 B / mtime `2026-11-15 03:16:55`，其 `schema.pyc` 解析结果为 **V1..V14**，不是 v6。真正含 v6 的是老包 `NewManga-0.1.0-win-x64`（10/27 构建，v6 时代产物，其 `schema.pyc` 只有 V1..V6）。

**结论：**「sidecar 副本落后 8 个版本」成立；「bundle 落后 8 个版本、`package.ps1` 产物不可用、用户安装即 fail-closed」不成立。被审变更把 **测试夹具副本（10/23 legacy Tauri v6）** 错认成 **产品 bundle**；产品包在变更前已经是 v14。卡标题、AC1、AC2、影响面、Closeout 都建立在这个错误诊断上。

### 主张 2：package.ps1 的校验是否真能拦住坏包 —— **成立（就 schema 声明一致性而言；附 P2 限制）**

代码位置 `apps/desktop-avalonia/scripts/package.ps1:40-68`（在 `dotnet publish` 之后、sidecar 拷贝/VERSION.json/zip 之前）：

- manifest 缺失：`if(-not (Test-Path $sidecarManifest)) { throw ... }`（L50-52）。实测证据 `gate-check-1-no-manifest.log`：`EXIT: 1`，抛出「cannot prove which schema it understands」。
- schema 不等：`if([int]$sidecarSchema -ne [int]$sourceSchema){ throw ... }`（L65-67）。实测证据 `gate-check-2-stale-schema.log`：`EXIT: 1`，抛出「built against schema v6 but the source tree is at v14」。
- 解析失败会不会静默通过：不会。实测同一段管道在无匹配文件上返回 `$null`：

```
$ ... Measure-Object -Maximum).Maximum   # 在 doc/STATUS.md 上
value=[] isNull=True
```

  对应 L63 `if($null -eq $sourceSchema){throw ...}`，fail-closed。manifest 无效 JSON（`ConvertFrom-Json` + `$ErrorActionPreference='Stop'`）或 `schema_version` 缺失（L55 throw）也都抛错。
- 解析逻辑实测：`schema.py` 上的匹配只有 14 个常量赋值，`Measure-Object -Maximum` 返回 `System.Double` 的 `14`，`[int]` 转换无问题（`value=[14] type=System.Double`）。

**限制（见 Findings P2-1/P2-2）：** 它验证的是「manifest 自述 schema == 源码常量最大值」这一**声明一致性**，不校验 manifest 与实际 `core_service.exe`/内嵌 schema 的字节绑定；本次任务真实出现过的「新旧 `_internal` 混杂、core_service 启动即崩」（见 P1-2）这类坏 bundle，如果 manifest 恰好是 v14 就会通过本闸门。另外 `manifest.git_head` 只打印、不比对当前 HEAD。

### 主张 3：build_sidecar.ps1 是否真的会写 manifest —— **成立（附增量短路 P2）**

`packaging/m2ac5/build_sidecar.ps1:359-383`：

- 写 manifest 在构建成功之后：位于 PyInstaller（L314-320）、layout 断言（L329-349）、三组权重拷贝（L351-355）、plugin Python runtime（L356-358）全部之后。
- 解析不到会 throw：`$schemaVersionForManifest = $null`，`if($null -eq ...) { throw "... refusing to produce an unlabelled bundle" }`（L371-373），不会写 null。且 `schema.py` 不存在时同样为 null 而 throw。
- 产物实测存在：

```
$ Get-Content apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar/build-manifest.json
{
  "schema_version": 14,
  "git_head": "f7d273d9ab49a03eab25f5ec3f3416667515771a",
  "pyinstaller": "6.22.3",
  "built_at_utc": "2026-11-15T19:36:51.0177500Z",
  "schema_source_path": "src/infrastructure/sqlite/schema.py"
}
```

  与 `build-sidecar-2.log` 末行「schema manifest -> … (schema v14) / OK (HEAD=f7d273d9a, pyinstaller=6.22.3)」一致；manifest 写入时间为 2026-11-15T19:36:51Z = 本地 03:36:51，在 commit 之前、重建之后。

**限制（P2-3）：** 不带 `-Force` 且目标 bundle 已存在时，脚本在 L256-270 **增量短路并 `exit 0`**，该路径位于 manifest 写入段之前 ⇒ 「跑一次 build_sidecar 就会写 manifest」不成立。本次 AC5 用了 `-Force`，所以 manifest 确实写出，这点属实。

### 主张 4：限制是否被如实记录 —— **部分成立（仅 (c) 成立；(a)(b) 未记录，且报告/commit 归因有错）**

- (a) SFX 权重限制：**未记录在卡面**。`doc/tasks/SIDECAR-SCHEMA-STALE-1.md` 的 AC5 注释（@1803b2f5f）只写重建成功、v14、package 放行、schema 错误归零，没有一个字提 SFX 权重来源/无 VERSION.json；该限制只出现在 commit message 与仓外 `rebuild-report.md`。且报告的具体表述「仅靠大小(38.93≈缺失39MB)与来源推断」**不准确**：`build_sidecar.ps1` 的 `Copy-SfxWeights` 对 `yolo11s-seg.onnx` 强制校验 SHA-256 = `944e8114…d418d`，不匹配直接 throw（L196-214）；`detection_sfx.py:121-132` 记录 `base.pt 1f0fd609 → best.pt c22f0175 → best.onnx 944e8114` 的 v2b 链。实际复制文件的 hash 实测正是 `944e8114…d418d`。真正缺的是「该 pin 对应 v2b 的流水线记录（release 无 VERSION.json）」这层可核验性，而不是「只有大小/来源推断」。
- (b) `test.ps1` 仍 EXIT=1 / 未全绿：**@1803b2f5f 卡面未记录**，且 commit 把失败归因为「PowerShell 非交互环境问题，非产品缺陷」——这一归因后来被作者自己推翻（见 P1-2）。卡面 AC5 只写「schema v14/v6 错误归零」，细读虽未声称全绿，但读者会把它读成已修复；`closed_with_limitations` 之外没有 EXIT=1/5 failed 的披露。
- (c) AC6 BLOCKED：**如实**。卡 L108 仍是 `[ ] … <<BLOCKED: 待 AC4/AC5 实施后一并送审>>`，未被伪装为完成。

**额外发现（属同一「诚实性」问题）：**
- 卡尾 `Closeout Record`（L133-142）仍写「Closeout：…核实与登记；**修复未做**」「AC4（打包加一致性校验）与 AC5（重建 bundle）**标 BLOCKED**」——与卡面 L106/L107 的 `[x] … <<MET>>` **直接矛盾**（parent/HEAD 两次改卡都只滚动了 AC 行，没有更新 Closeout）。
- front matter `canonical_evidence_status: complete`，但 Canonical Evidence 表（L123-125）仍只有 `EV-SSS-01` 这条 **v6 归因**的旧证据；AC4/AC5 的新证据（gate-check 日志、rebuild 报告、manifest）全部只在仓外 workspace，未进 `verification/**`，也未 pin。这份唯一的 canonical 证据现在被本复核证明归因错误。
- AC5 的 `<<MET>>` 叙述把「重建一个**本来就 v14** 的 bundle + 手工替换测试副本」写成「sidecar bundle 重建使 schema 对齐达成」，属于把「环境修补」写成「修复达成」。

## Findings

### P0

**P0-1（诊断对象错误，产品影响主张不成立）**
- 位置：`doc/tasks/SIDECAR-SCHEMA-STALE-1.md:3`（标题）、`:66`（结论）、`:70-83`（影响面）、`:121-142`（Canonical Evidence/Closeout）；`1803b2f5f` commit message；`cc8e517f0` commit message。
- 问题：把测试夹具副本 `sidecar-copy`（10/23 legacy Tauri v6 产物）错认成 `package.ps1` 打包的 bundle，据此断言「bundle 落后 8 个版本 / 安装包不可用」。事实是变更前 bundle 已是 v14；卡面点名的 `NewManga-0.2.0-dev-win-x64-models` 实测内嵌 v14 sidecar；唯一含 v6 的是 10/27 的 `NewManga-0.1.0-win-x64` 老包（v6 时代产物，非本缺陷）。B1 证据日志本身（L72）就写着失败 sidecar 是 `sidecar-copy`。
- 证据：见「主张 1」的 .pyc 解析结果、`sha256=f1058b07…` 新旧同源、release 1,024 文件/791.69 MiB、`RELEASE-PACKAGE-BUNDLE-1/review-r1.md:32`、B1 log L72、`prepare-sidecar.ps1:16` + legacy exe mtime 10/23 19:21 + V6/V7 提交时间线、0.2.0-dev 包内 schema.pyc=V14。
- 建议：重开该卡的 AC1/AC2/标题/影响面；把缺陷重新定义为「test.ps1/prepare-sidecar.ps1 默认从 legacy Tauri 10/23 产物取 sidecar，且副本不刷新」；在卡面明确「产品包（e2c9fd058 / 0.2.0-dev）内 sidecar 为 v14，未受此缺陷影响」，并附 .pyc/manifest 证据（可入库为 `verification/**` 新证据）。不得以当前表述关闭。

**P0-2（真正的修复没有做）**
- 位置：`apps/desktop-avalonia/scripts/prepare-sidecar.ps1:16`（默认 `-Source` 指向 legacy Tauri）、`apps/desktop-avalonia/scripts/test.ps1:18`（默认副本路径）、`test.ps1:39-41`（目录存在即不刷新）。
- 问题：被审三次提交只改 `package.ps1`、`build_sidecar.ps1`、卡面（`git diff --stat cc8e517f0 1803b2f5f` = 3 files），**没有改**测试夹具的选取/刷新逻辑。实质修复是对 workspace 副本的手工替换（`sidecar-copy` 目录 CreationTime 实测 `2026-11-16 03:46:41`，即审查进行中重建），不可复现、不随仓库分发。任何接近真实全新环境的运行仍会：① 若 legacy 路径存在 → 取 10/23 v6 sidecar；② 若不存在 → `prepare-sidecar` 直接 throw（legacy 源缺失）。
- 建议：二选一并入库：a) `test.ps1`/`prepare-sidecar.ps1` 默认从 `apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar` 取，并对已存在副本校验 `build-manifest.json.schema_version` 与源码一致，不一致则重建或失败；b) 删除 legacy 默认，强制显式 `-Source`，副本带 manifest+hash 并在每次 test 前比对。补一个「副本旧于 bundle → 必须失败/刷新」的测试。

### P1

**P1-1（「dotnet test 全过」与事实不符）**
- 位置：`1803b2f5f` commit message「dotnet test 全过」；`rebuild-report.md` §5 同口径。
- 问题：同一作者自己的实测结果不是全过。`test-ps1-final.log`（2026-11-16 03:48:23，`HOST-RESOURCE-SECURITY-1/evidence-rerun/test/dotnet-test-Debug.log` 同源）为 **失败 5 / 通过 251 / 跳过 0 / 总计 256**（L415/418），5 个失败为 `RunBindingFixTests.ModelsBuild_…`、`CommandWiringB1/B2…FrozenCore`、`Fea12Core_DeleteTrash…`、`Fea12NewCommands_FrozenCore…`。而被审 head 引用的两次重跑 `test-ps1-after2/3.log`（各 65 行）在 `probe-core-commands.ps1` 处终止，日志里**根本没有 dotnet test 输出** ⇒ 把「测试没跑」当成「测试全过」。后续 `caca93978` 已自行更正为 5 failed/251 passed（说明作者后来发现了），但被审 head 的公开声明是错的。
- 建议：在卡面/证据中记录 5 failed 的准确数字与失败测试名，明确「schema 错误归零 ≠ 全绿」；如要继续引用 `test.ps1` 的 dotnet 结果，附 `test-ps1-final.log`/TRX。

**P1-2（EXIT=1 的根因归因错误）**
- 位置：`1803b2f5f` commit message「管道正在被关闭 … PowerShell 非交互环境问题，非产品缺陷」；`rebuild-report.md` §5；卡面 AC5 注释未提 EXIT=1。
- 问题：后续 `rebuild-report-v2.md` §4 与 `caca93978` 已承认：`robocopy /E` **叠加复制**导致新旧 `_internal` 混杂，`core_service.exe` 启动即崩（`Failed to import encodings module`），`probe-core-commands.ps1:89` 的 `StandardInput.WriteLine` 才报「管道正在被关闭」——是「子进程已死」的症状，不是 PowerShell 环境问题。被审 head 把自身操作造成的副本损坏误判为「非产品缺陷」，且报告还写「副本比源大…只影响磁盘占用，不影响测试」，均与事实不符。
- 建议：更正 commit/报告（commit 不可改则登记勘误），卡面记录「EXIT=1 的真实根因 = 测试副本被叠加复制损坏；修法 = 删除后完整复制」；把「副本完整性」纳入 P0-2 的夹具校验。

**P1-3（卡面限制记录不全 + 内部自相矛盾）**
- 位置：`doc/tasks/SIDECAR-SCHEMA-STALE-1.md:103-108`、`:121-142`。
- 问题：(a) SFX 权重限制未进卡；(b) EXIT=1/5 failed 未进卡；(c) AC6 BLOCKED 如实；Closeout Record 仍写「修复未做 / AC4、AC5 标 BLOCKED」与 `[x] MET` 矛盾；`canonical_evidence_status: complete` 但新增 AC4/AC5 证据未进仓、未 pin；唯一 canonical 证据（EV-SSS-01）归因错误。
- 建议：更新 Closeout/Evidence 表；把 AC5 的 MET 依据改为「bundle 重建 + manifest 落地（并注明 schema 早已是 v14）」；补 (a)(b) 两条限制；`status` 与 `reviewer` 字段按实际复核结果更新；新证据入库并 pin。

### P2

**P2-1（package.ps1 只证明声明一致，不证明 bundle 实际能力）**
- 位置：`apps/desktop-avalonia/scripts/package.ps1:49-68`。
- 问题：manifest 是纯自述 JSON，未绑定 `core_service.exe`/内嵌 `schema.pyc` 的 hash；`package.ps1` 不校验 `manifest.git_head` 与当前 HEAD（实测 manifest 为 `f7d273d9a`，打包时 HEAD 已是 `caca93978`，只打印不拦截）。因此「manifest 正确但 bundle 混入旧/坏文件」会通过；本次 `encodings` 事故证明这类混杂真实会发生。
- 建议：manifest 增写 `core_service.exe` sha256（package.ps1 的 `sidecarBuildInfo` 已有该值），package 时复算比对；或让 `build_sidecar.ps1` 把 bundle 的 `schema.pyc` sha256 也写进 manifest 并校验；并打印/断言 manifest HEAD 与当前 HEAD 的差异说明。

**P2-2（解析口径是源码常量最大值，不是运行时迁移集）**
- 位置：`package.ps1:57-63`、`build_sidecar.ps1:363-370`。
- 问题：两边都用 `Select-String 'SCHEMA_VERSION_V(\d+)\s*=' | Measure-Object -Maximum`，而不是 `default_migrations()`/bundle 内嵌迁移。如果出现「常量加了/删了但迁移集没同步」，两边仍一致、闸门放行；注释掉/写入注解形式的常量会造成误报（方向 fail-closed，不危险）。空匹配返回 `$null` 并 throw，这一点实测成立，不会被静默绕过。
- 建议：改为 `python -c "import ...; print(max(m.schema_version ...))"` 或直接解析 bundle 内 `schema.pyc` 的 `default_migrations`；至少在注释里写明这是 proxy。

**P2-3（build_sidecar 增量短路路径不写 manifest）**
- 位置：`packaging/m2ac5/build_sidecar.ps1:247-270`。
- 问题：不带 `-Force` 且目标存在时 `exit 0`，早于 L359-383 的 manifest 段 ⇒ 老 bundle（无 manifest）会被「成功」退出但 package 拒绝；已有旧 manifest 时短路也不会刷新。方向安全（错误告警而非错误放行），但「跑 build_sidecar 就有 manifest」不成立。
- 建议：短路路径也校验/重写 manifest；或目标存在但无 manifest 时 throw 并提示 `-Force`。

**P2-4（报告结论被自己后续推翻，且未在 head 更正）**
- 位置：`rebuild-report.md` §4「只影响磁盘占用，不影响测试」、§5「PowerShell 非交互环境问题」。
- 问题：作者在 03:48 的 `rebuild-report-v2.md` 与 `caca93978` 中已承认这两点错误，但被审 head（03:45）引用的是旧报告，未做勘误登记。
- 建议：把 v2 报告并入卡面证据引用，或在旧报告顶部加「已被 v2 取代」；commit message 无法修改时在卡面登记勘误。

**P2-5（SFX 权重的「限制」表述不准确）**
- 位置：`rebuild-report.md` §3；`1803b2f5f` commit message。
- 问题：写「仅靠大小(38.93≈缺失39MB)与来源推断」，但构建实际强制 SHA-256 pin 校验（`build_sidecar.ps1:204/210/214`），且文件实测 hash 与 v2b pin 一致、`detection_sfx.py:121-132` 记录了 v2b 部署链。真实的限制是「pin 的流水线出处无法用 release 的 VERSION.json 交叉验证」，而非「没有 hash 校验」。这一条是「低估了自身验证」而不是美化，但仍属事实表述不准。
- 建议：改写成「已按 v2b pin 校验 SHA-256；缺的是该 pin 对应训练流水线的独立可核验记录（release 无 VERSION.json）」。

### P3

- **P3-1**：`package.ps1:68` 把 manifest 的 `git_head` 打进日志但不与当前 HEAD 比对（被审时 `1803b2f5f`/打包后 `caca93978` 均与 `f7d273d9a` 不同）；建议绑定说明或断言。
- **P3-2**：schema 校验位于 `dotnet publish`（L33）之后，坏 bundle 仍会先白跑一次 publish；可在 sidecar 存在性检查（L40）处前移。
- **P3-3**：卡面/证据数字抽查：253/3/0 ✓（B1 log）；835.3 MB ✓（实测 835.25 MiB / 875,823,531 B）；「400 KB launcher」✓（400,098 B）；8 版本差 ✓（v14−v6，但属 `sidecar-copy` 而非 bundle）；「203/0/30 四件套」在仓内现存日志中**无法复算**（仅见 `RELEASE-PACKAGE-1` 卡进度注释与 `version-check.log` 自述；`doc/STATUS.md:18` 的无夹具口径是 954/325/192，口径不同）。commit message 的 `check PASS(3w)` 实测成立（跑 `tools/governance/check.ps1`：`PASS (3 warnings)`）；`pins 18/18`、`inventory 1/80/6=87` 未复算。

## 后到提交的影响（审查期间，非被审 head）

`caca93978`（03:49:08，作者同一人）在审查期间落地，内容与相关性：
- commit message 承认「测试用的不是 build/sidecar bundle，差点误判为重建无效」以及 `encodings`/管道归因错误，并如实写「失败 5 / 通过 251 … 仍未全绿」，还在 AC5 注释里补了「test.ps1 仍有 5 failed，本卡不宣称全绿」；
- 但**仍未更正**「bundle 曾是 v6 / 产品包不可用」的诊断，卡标题/AC1/AC2/Closeout 原样保留；其 `rebuild-report-v2.md` 仍写「旧 bundle 是 v6 时代的产物」；
- 该提交只改卡面 1 行（`git diff --stat 1803b2f5f caca93978` = 1 file），没有修 `prepare-sidecar.ps1`/`test.ps1`；`sidecar-copy` 仍是手工替换的 workspace 状态。

因此：后到提交改善了 (b) 的披露与管道归因，但本报告对 (a)、(c 之外的矛盾)、P0-1、P0-2 的判定不受影响；若以 `caca93978` 作为新送审 head，主张 4(b) 可改判「已披露（5 failed）」，主张 1 仍为「不成立」。

## 我实际验证过的（可复算）

1. `git rev-parse HEAD` → `1803b2f5f…`；`git log --oneline -4` → `1803b2f5f` / `f7d273d9a` / `cc8e517f0`；审查中 HEAD 变为 `caca93978`；`git status --porcelain` 空。
2. `git diff --stat cc8e517f0 1803b2f5f` → `package.ps1` +29、`build_sidecar.ps1` +26、卡面 2 行；`git diff --stat 1803b2f5f caca93978` → 卡面 1 行。
3. `Select-String` schema.py → V1..V14；`python -c "…default_migrations()…"` → `count=14 versions=[1..14] max=14`。
4. 只读解析 release/新 bundle/0.1.0/0.2.0-dev 的 `schema.pyc`（`marshal.loads` + `co_names`/`default_migrations` co_names）：
   - release e2c9fd058：`SCHEMA_NAMES=14`，含 V14；`sha256(data)=f1058b0768e4…`
   - 新 bundle：`sha256(data)=f1058b0768e4…`（完全相同）
   - 0.2.0-dev 包：14 个，含 V14；0.1.0 base 包：6 个（V1..V6）。
5. `Get-ChildItem`/`Measure-Object`：新 bundle 1,967 文件 / 875,823,531 B（835.25 MiB）；`python/` 942 文件 / 43.56 MiB；release sidecar 1,024 文件 / 791.69 MiB；0.1.1 release sidecar `schema.pyc` = V1..V6。
6. `Get-Content build-manifest.json` → `schema_version=14, git_head=f7d273d9a, pyinstaller=6.22.3`；`build-sidecar-2.log` 末行同口径；`Get-Item core_service.exe` = 400,098 B，mtime 2026-11-15 19:36:42 UTC。
7. `package.ps1` 静态检查（L40-68）与两个 gate 日志（EXIT=1 的两段抛错原文）；`Measure-Object -Maximum` 空匹配返回 null 的实测；manifest 缺字段/字符串/整数解析的 pwsh 实测。
8. 动态复算解析管道：`schema.py` 上 `value=[14] type=System.Double`。
9. `B1-DOC-CLOSE-1/test-ps1.log`：L72 sidecar=sidecar-copy；L377/384/403/410 v6 报错；L435 `失败: 3, 通过: 253, 跳过: 0, 总计: 256`；head `eaf82396d`、EXIT 1。
10. `SIDECAR-SCHEMA-STALE-1/test-ps1-after.log`（03:42）：L65 sidecar=sidecar-copy，L380+ v6 报错，L435 `失败:4, 通过:252`；`after2/3.log` 各 65 行，止于 `probe-core-commands.ps1` 的「管道正在被关闭」，无 dotnet test 段。
11. `test-ps1-final.log`（03:48:23）：L60 PASS 66 commands；L418 `失败: 5, 通过: 251, 跳过: 0, 总计: 256`；无 v6/encodings/pipe 错误行。
12. `prepare-sidecar.ps1:16` 默认 `-Source` = legacy Tauri 路径；该路径 exe mtime 全为 2026-10-23 19:21:28（`core_service.exe` 68,887,500 B）；`git log -S SCHEMA_VERSION_V6/V7` → V6 2026-10-23 15:01、V7 2026-11-03。
13. `package-summary-models.json`：`sidecar_mb=835.25`、`generated_at_utc=2026-11-15T19:41:08Z`（即 apply 后 package.ps1 放行那次产物，`NewManga-0.1.0-win-x64-models.zip` 03:41:08）；stage sidecar 内 manifest 读回 v14。
14. `doc/tasks/SIDECAR-SCHEMA-STALE-1.md` 全文（@1803b2f5f）：L106/L107 `[x] MET`、L108 AC6 `[ ] BLOCKED`、L121-125 只 pin EV-SSS-01、L133-142 Closeout「修复未做/AC4、AC5 标 BLOCKED」。
15. `tools/governance/check.ps1` → `Governance check: PASS (3 warnings)`，EXIT=0。
16. `detection_sfx.py` L117-132（v2b 链与 `SFX_WEIGHTS_SHA256`）；`build_sidecar.ps1` L185-222（Copy-SfxWeights 的 SHA-256 强制）；release 内 `yolo11s-seg.onnx` 实测 hash `944e8114…d418d`，release 目录无任何 `VERSION.json`。
17. `rebuild-report.md` / `rebuild-report-v2.md` / `gate-check-1/2.log` / `RELEASE-PACKAGE-BUNDLE-1/review-r1.md` L32。

## 我无法验证的

- 未在真实 Windows 桌面/干净机器上安装并启动安装包（会写盘且需要 GUI 交互）；「用户安装后 fail-closed/正常启动」只能由静态证据（包内 sidecar 的 schema.pyc / manifest）推断，未做端到端运行。
- 未运行任何被审 exe（`core_service.exe` 等）和 `test.ps1`（会写 workspace/evidence、可能改用户数据根），因此 5 个 dotnet 失败/EXIT=1 只复用了作者 workspace 里的日志与 TRX，未独立复现。
- 203/0/30「四件套」无夹具口径无现存原始日志可复算；`pins 18/18`、`inventory 1/80/6=87` 未复算（只复算了 `check.ps1`）。
- 旧 `sidecar-copy`（报告称 2026-10-23 / 992 MB / 3432 文件 / 无 manifest）已被 2026-11-16 03:46:41 的手工替换覆盖，无法直接读取其内容；「它是 v6」由 B1 运行时错误、legacy Tauri 产物 mtime、V6/V7 提交时间线与后来 `encodings` 事故交叉推断。
- 无法验证 SFX 权重 `944e8114…` 的「真实 v2b 训练来源」——只能验证它与代码 pin 一致；pin 之上的训练/导出流水线记录未在仓库或 release 产物中找到。
- 未复跑 `package.ps1` 场景 1/2，只读取作者 03:30/03:31 的 gate-check 日志与其时 head（`cc8e517f0`）的代码；代码在 `f7d273d9a` 提交，逻辑一致，但严格说两段实测不是在被审 head 上重跑的。
