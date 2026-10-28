# RELEASE-VERIFY-1 实施报告（免证书发布完整性：SHA-256 清单/校验脚本 + 发行说明）

- Task：`doc/tasks/RELEASE-VERIFY-1.md`（shared task-4；Owner `region-workbench-owner`，Reviewer `dsh`）
- Branch / Worktree：`task/RELEASE-VERIFY-1` / `G:/CODEX/New Manga.workspace/worktrees/RELEASE-VERIFY-1`
- 基线：worktree 起点 `28991823a`（Task 卡登记 base `b54d2d36f`）
- 输入产物（**只读**，不复制进仓库）：base zip / models zip（AGPL-RELEASE-1 out）+ setup.exe（NSIS-INSTALLER-1 out），
  合计 897,602,964 B；产物哈希实测与 Task 卡一致。
- 背景：用户 2026-10-28 明确「没有证书，买不起」——签名线继续等待外部资源，本卡用零成本方案补齐发布完整性；
  **不关闭** V1-RELEASE-SIGNING-1。
- 未 push；未改产品源码/Core/旧壳/契约；未覆盖任何已发布产物；zip/exe 未入 Git。

## 1. 交付摘要

| AC | 结论 | 关键证据 |
|---|---|---|
| AC1 校验清单与脚本 | **MET** | `packaging/release/generate-checksums.ps1`（显式路径 / `-ArtifactDir` / 默认回退三级定位；只读哈希，绝不复制）+ `packaging/release/verify-release.ps1`（按清单逐项校验、缺失/不匹配 exit 1 并点名、`-Quiet`） | `logs/generate-checksums.log`、`logs/verify-positive.log`、`logs/verify-artifactdir.log`、`artifacts.json` |
| AC2 清单入库与可复算 | **MET** | `packaging/release/SHA256SUMS`（3 产物，标准 `sha256sum` 格式）+ `SHA256SUMS.json`（字节数/来源/生成时间）；`verify-release.ps1` 正反两向均可复算 | `checksums/SHA256SUMS`、`checksums/SHA256SUMS.json`、`logs/verify-positive.log` |
| AC3 负向验证 | **MET** | 复制 setup.exe 到 task-env，翻转第 34,305,604 字节（216→39，sha256 `ebad8662…`→`bb84e283…`）→ `verify-release.ps1 -SetupExe <篡改副本>` **FAIL exit 1** 且点名 `NewManga-0.1.0-setup.exe`；随后真实产物复验 **PASS**；另测缺失产物场景 3 项 MISSING / exit 1 | `logs/verify-negative-tamper.log`、`negative/tamper.json`、`logs/verify-missing.log`、`logs/verify-quiet-after-negative.log` |
| AC4 发行说明 | **MET** | `apps/desktop-avalonia/docs/RELEASE_NOTES_0.1.0.md`（变体/许可、两种安装方式、未签名 + SmartScreen「更多信息→仍要运行」、SHA-256 校验、数据根/卸载、已知限制、SignPath 等免费 OSS 签名替代）；`MANUAL_VERIFY.md` 增补链接与校验脚本指引 | `docs/release-notes-check.json`、`docs/manual-verify-link.json`、`docs/diff-stat.txt` |
| AC5 门禁 | **MET** | `extract-command-surface --check` PASS（66）；`test.ps1` 隔离复跑 **258/258 passed, 0 skipped**（2026-10-28）；`check.ps1 -TaskPath` PASS；证据全部 64-hex pin | `logs/extract-command-surface.log`、`test/summary.json`、`logs/test-ps1-console.log`、`check-governance.json` |

## 2. AC1/AC2 清单与脚本

### 产物与入库清单（`packaging/release/SHA256SUMS`，284 B）

```
ebad86624a0add5393b8a28d258e2334c23fd13ee52f0a0f0b598a5ba9753691  NewManga-0.1.0-setup.exe
480d06323ce482214955582dc86696bfdd8023e9227100941fd6b8873b237f67  NewManga-0.1.0-win-x64-models.zip
722fc62b53a4488dff8e3043b419a720cb59c3e4c790a9c8d19511efb627e8ef  NewManga-0.1.0-win-x64.zip
```

- 文件名按字节序（`sha256sum` 标准输出顺序）；两空格分隔，可直接 `sha256sum -c SHA256SUMS` 使用。
- `SHA256SUMS.json` sidecar 记录每个产物的 `role/filename/bytes/mb/sha256/source_path` 与 `release=0.1.0`、
  `generated_at_utc`、`total_bytes=897,602,964`；校验脚本自动读取 sidecar，**额外核对字节数**。
- 清单只写文件名（不写本机绝对路径），发布时与产物同目录分发即可；校验脚本按以下顺序定位真实产物：
  1. 显式 `-BaseZip/-ModelsZip/-SetupExe`；
  2. `-ArtifactDir\<filename>`（发布 staging 目录，一次覆盖三产物）；
  3. 已知 task-env 默认位置（AGPL-RELEASE-1 out / NSIS-INSTALLER-1 out）。

### 脚本

| 脚本 | 行为 |
|---|---|
| `packaging/release/generate-checksums.ps1` | 解析产物（三级定位）、流式 SHA-256、按字节序生成 `SHA256SUMS` + sidecar JSON；`-NoWrite` 可只预览；明确拒绝“复制产物”——只 `Get-Item`/流式读取。 |
| `packaging/release/verify-release.ps1` | 解析 `SHA256SUMS`（兼容 ` *filename` 形式）、逐项校验存在性 + SHA-256（+ sidecar 字节数）、`-Quiet` 只输出 OK/FAIL 摘要；任一失败 exit 1 并打印 `MISSING`/`HASH`/`SIZE` 具体项。 |

## 3. AC3 负向验证（证明校验非恒真）

- 篡改对象：`NewManga-0.1.0-setup.exe` 的 **task-env 副本**（真实发布产物未被修改）。
- 篡改内容：offset `34,305,604`（文件中部），字节 `216 (0xD8)` → `39 (0x27)`（XOR 0xFF）。
- sha256：`ebad86624a0add5393b8a28d258e2334c23fd13ee52f0a0f0b598a5ba9753691` → `bb84e2832a9bf6bdbb899d89f672864b5a7c1d3acbbf27f4400ec32be25c0fa9`。
- 结果：`verify-release.ps1 -SetupExe <tampered>` → `FAIL  NewManga-0.1.0-setup.exe  sha256 expected=…ebad8662… actual=…bb84e283…`，
  `RELEASE VERIFY: FAIL (1/3 entries failed)`，**exit 1**；另两个真实产物仍 OK。
- 补充负向：`-ArtifactDir <空目录>` → 3 项 `MISSING`、`FAIL (3/3)`、exit 1。
- 篡改后复验真实产物：`-Quiet` → `RELEASE VERIFY: PASS (3/3)`，exit 0（证明失败不是脚本自损/环境问题）。

## 4. AC4 发行说明

`apps/desktop-avalonia/docs/RELEASE_NOTES_0.1.0.md`（9 节，约 6 KB）覆盖：

1. 变体与许可证：base=`GPL-3.0-or-later` / models=`AGPL-3.0`（含 Ultralytics YOLO11s-seg 说明）/ NSIS setup=base 内容。
2. 三产物文件名、字节数、SHA-256 表 + `SHA256SUMS` 说明。
3. 两种安装方式：NSIS per-user（默认目录、`/S` 静默、卸载）与 zip + `install.ps1`（含 base 缺模型提示）。
4. SHA-256 校验三种方法（`Get-FileHash` / `verify-release.ps1` / `certutil`）。
5. **未签名说明**：SmartScreen 提示与 **「更多信息 → 仍要运行」** 操作指引；企业环境提示；先校验哈希。
6. 数据根 `%APPDATA%\com.newmanga.desktop`、升级（覆盖安装/备份建议）、卸载（NSIS/`uninstall.ps1`，不代删用户数据）。
7. 已知限制：未签名、models 仅 zip、per-user、覆盖式升级无回滚/自动更新、日志行为。
8. 免费替代：SHA-256 校验（零成本完整性）+ **SignPath Foundation 等免费 OSS 代码签名**（未来版本可签）。
9. 链接到 `MANUAL_VERIFY.md`、`UPGRADE.md` 与仓库校验脚本。

- `MANUAL_VERIFY.md` 顶部状态块新增：指向发行说明、许可/未签名指引、SHA-256 校验脚本链接；JSON 检查确认链接 target 存在。
- 关键词/章节自动核对：`docs/release-notes-check.json`（required_keywords 全部命中，`missing_keywords=[]`）。

## 5. AC5 门禁

| 命令 | 结果 | 证据 |
|---|---|---|
| `python apps/desktop-avalonia/scripts/extract-command-surface.py --check` | **PASS：66 commands**（resource 3 / workbench 12 / library 8 / settings 33 / region 6 / reader 4） | `logs/extract-command-surface.log` |
| `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence-test` | **PASS 258/258 passed, 0 skipped**（coreclient 61 / host 60 / app 137；2026-10-28；产品代码零改动） | `test/summary.json`、`logs/test-ps1-console.log` |
| `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/RELEASE-VERIFY-1.md` | **PASS**（rebase main 后；非阻断 warning） | `check-governance.json`（原始日志 task-env `logs/check-governance.log`） |
| `generate-checksums.ps1` + `verify-release.ps1` | 生成 exit 0；正向校验 PASS 3/3（默认路径与 `-ArtifactDir` 硬链接副本两种模式） | `logs/generate-checksums.log`、`logs/verify-positive.log`、`logs/verify-artifactdir.log` |

## 6. 风险与遗留

1. **清单与产物分离**：`SHA256SUMS` 入库、产物在 task-env/发布页；发布时必须把 `SHA256SUMS` 与三个产物一起分发（发行说明已写明）。清单不写本机路径，可跨机器使用。
2. **校验脚本的路径回退**：默认 task-env 路径仅为本机约定；跨机器/发布目录请用 `-ArtifactDir` 或显式参数（脚本报错会提示）。
3. **未签名不改变**：本卡不产生签名，SmartScreen 提示仍存在；签名归 V1-RELEASE-SIGNING-1（不断卡）。
4. **哈希校验的边界**：SHA-256 只证明“与清单一致”，清单本身真实性依赖官方发行页/渠道；未来签名可补强真实性。
5. `SHA256SUMS.json` 的 `source_path` 泄露本机构建路径（含用户名）——已在 sidecar（不参与 `sha256sum` 校验）；如公开发布可只分发 `SHA256SUMS`（纯文件名+哈希），sidecar 留作内部审计。
6. 本卡未改 STATUS/PLAN/LEDGER（DSH 统一更新）。

## 7. 复现命令

```powershell
# 生成清单（默认读取 AGPL-RELEASE-1 / NSIS-INSTALLER-1 的产物位置，只读）
pwsh -NoProfile -File packaging/release/generate-checksums.ps1

# 或显式/staging 目录
pwsh -NoProfile -File packaging/release/generate-checksums.ps1 `
  -BaseZip <base.zip> -ModelsZip <models.zip> -SetupExe <setup.exe>
pwsh -NoProfile -File packaging/release/generate-checksums.ps1 -ArtifactDir <release staging dir>

# 正向校验（默认位置 / -ArtifactDir / -Quiet）
pwsh -NoProfile -File packaging/release/verify-release.ps1
pwsh -NoProfile -File packaging/release/verify-release.ps1 -ArtifactDir <dir> -Quiet

# 负向：篡改副本必须 FAIL
pwsh -NoProfile -File packaging/release/verify-release.ps1 -SetupExe <tampered copy>   # exit 1

# 门禁
python apps/desktop-avalonia/scripts/extract-command-surface.py --check
pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence-test
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/RELEASE-VERIFY-1.md
```

## 8. 证据索引（`verification/RELEASE-VERIFY-1/`）

| 路径 | 内容 |
|---|---|
| `checksums/SHA256SUMS` / `checksums/SHA256SUMS.json` | 入库清单副本与 sidecar（字节/来源/生成时间） |
| `artifacts.json` | 三产物来源路径、字节、sha256、只读/未复制入仓库声明 |
| `logs/generate-checksums.log` | 生成日志（三产物哈希与写入路径） |
| `logs/verify-positive.log` / `logs/verify-artifactdir.log` | 正向校验 PASS（默认定位 + `-ArtifactDir` 硬链接副本） |
| `logs/verify-negative-tamper.log` / `negative/tamper.json` | 篡改副本校验 FAIL + 篡改明细（offset/字节/前后 hash） |
| `logs/verify-missing.log` | 缺失产物负向（3 项 MISSING、exit 1） |
| `logs/verify-quiet-after-negative.log` | 篡改后真实产物复验 PASS（`-Quiet`） |
| `docs/release-notes-check.json` | 发行说明关键词/章节自动核对 |
| `docs/manual-verify-link.json` | MANUAL_VERIFY 链接存在性与 target 解析 |
| `docs/diff-stat.txt` | 文档改动 diff stat/status |
| `logs/extract-command-surface.log` | 命令面 `--check` PASS（66） |
| `test/summary.json`、`logs/test-ps1-console.log` | 隔离复跑 258/258 |
| `check-governance.json` | `check.ps1 -TaskPath` PASS 记录（原始 tee 日志在 task-env） |
| `REPORT.md` | 本报告 |
