---
task: RELEASE-GATE4-SIGNED-MATRIX-1
review_id: RELEASE-GATE4-MATRIX-REVIEW-2026-11-18
reviewed_head: 12bb456fa
reviewer: reviewer-g4
reviewer_context: >-
  独立子 agent 上下文（reviewer-g4），未参与条件 4 矩阵的设计、执行或返修；
  复核为只读，未重装/卸载、未改动仓库文件（本报告除外）、未改动 workspace stage/fixture。
date: 2026-11-18T03:00:00+08:00
decision: ACCEPTED_WITH_FINDINGS
p0: 0
p1: 2
p2: 7
condition4_recommendation: CLOSED_WITH_LIMITATIONS_AFTER_P1_DISPOSITION
---

# 条件 4 矩阵独立复核（RELEASE-GATE4-SIGNED-MATRIX-1）

## 0. 复核身份与范围

- **被审 head：`12bb456fa`**（`feat(release): 条件 4 AC5/AC6 实测通过 …`，main）。
- 复核开始时 HEAD 已是 `612adbac2`（补登 Canonical Evidence EV-G4-01..10 + STATUS 指针），复核期间又出现 `d582946eb`（STARTER R29）；两者均只改 `doc/**`。本报告的判定仍以 **`12bb456fa`** 为准，涉及后续提交时单独注明。
- 复核手段：读日志/卡片/裁决、重算 sha256、读四张 JPG、比对 workspace stage、核对当前机器状态、查 git 树与治理检查器。
- **未执行任何安装/卸载**；测试机当前状态为「无安装」：程序目录不存在、HKCU 卸载项不存在、Start Menu 文件夹不存在、数据根 530 文件 / 684,197,540 B（与 AC6 结束态一致）。
- 判定口径：**P0** = 阻断或虚假主张；**P1** = 关闭前必须处置的证据/口径缺口；**P2** = 不阻断的精确性/文档问题。

## 1. 结论摘要

- AC1、AC2、AC4、AC6 的**事实层面成立**，且关键数字可独立复算。
- AC3 的**安装核心成立**（ExitCode 0、1,040 文件、安装后 exe 与 stage 逐字节相同、HKCU 字段齐全），但 **Start Menu 证据自相矛盾**：AC3 日志记 0 项，卡面却写两个 `.lnk` 及精确字节数，且后者在已提交证据中无出处（**P1-02**）。
- AC5 的**安装器级回退机制成立**（确有卸载后重装、exe hash 序列可复现、数据根四步不变），但「0.1.0」是**同源重构包**，其 `app\NewManga.App.exe` 自报 `FileVersion=0.1.1.0` / `ProductVersion=0.1.1+292f2e77…`，与 0.1.1 相同；只有安装器/注册表/VERSION.json 标成 0.1.0。因此它证明的是**安装器版本标签与替换机制**，不是真实的跨产品版本升级/回退（**P1-01**）。
- **decision = `ACCEPTED_WITH_FINDINGS`**；P0=0，P1=2，P2=7。
- **条件 4 不能在本报告后无条件关闭**；在处置两条 P1（或由 Lead 明确接受为 limitation）并补齐 P2 后，可 `closed_with_limitations`。

## 2. 八项逐条判定表

| # | 复核问题 | 判定 | 关键依据 |
---|---|---|---|
| 1 | AC1/AC2：包 hash、`NotSigned`、无「签名已验证」主张 | **PASS** | 安装包 652,081,157 B / sha256 `3c9984b2…` 与 build-info 完全一致；`Get-AuthenticodeSignature` 实测 `NotSigned`；提及该包签名状态的记录均写「未签名」，未发现签名已验证主张 |
| 2 | AC3 数字自洽（ExitCode/1,040 文件/exe hash/HKCU） | **PASS_WITH_P1** | ExitCode=0、1,040 文件 / 827,026,762 B、exe `c2bf9265…` 与 stage 一致；HKCU 字段齐全；**Start Menu 记录矛盾（P1-02）** |
| 3 | AC4 四张截图是否为四个不同页面、是否安装版特征 | **PASS** | 四张分别是资料柜/工位/控制台/阅读器，画面不同、非空白、非重复；前 3 张状态栏有 `Host 就绪`；**画面中无 0.1.1 版本字样（P2-04）** |
| 4 | AC5 是否为「真回退」、exe hash 序列、数据根四步 | **PASS_WITH_P1** | 实为 `Uninstall.exe /S` + `setup.exe /S`；序列 `c2bf9265 → 9948f200 → c2bf9265 → 9948f200` 可复现；数据根四步均 530 / 684,197,540 B；**但 0.1.0 包 app 自报 0.1.1（P1-01）** |
| 5 | AC6 数据保护、530 条记录、卸载版本 | **PASS_WITH_P2** | 丢失 0 / 新增 0 / 变化 0；530 文件 / 684,197,540 B；JSON 实为 530 条且逐文件哈希与当前数据根 530/530 全匹配；**日志未明写卸载的是 0.1.0（P2-01）**、JSON 来源标注不准（P2-02） |
| 6 | 是否越界（只改 doc/ 与 verification/、无产品代码/安装包二进制、不动 Gate/条件 5） | **PASS** | `12bb456fa` 仅 3 个文件（卡 + 2 日志）；`5469952f6` 为 doc/证据；树内无 setup.exe/安装包；Technical Gate 与条件 5 结论未被改动 |
| 7 | 卡面诚实性（不宣布通过/已卸载/未签名/AC7 未勾选） | **PASS** | AC7 仍 `- [ ]`；卡面明写「本轮不宣布条件 4 通过」「测试机已卸载」「未签名」；AC7 行为「待复核」 |
| 8 | 治理门禁 | **PASS** | `check.ps1 -TaskPath …` 输出 `Governance check: PASS (3 warnings)`，exit 0 |

## 3. AC1/AC2：环境、包冻结与未签名披露

**实测（独立复算）**

- 安装包：`G:\CODEX\New Manga.workspace\tmp\r28\inst\NewManga-0.1.1-setup.exe`
  - `652081157` B；`sha256 3c9984b21d663a9ec9a8890387e5800df7d85a3005ed66f0231c67653751df05`。
  - 与 `verification/WEIGHTS-LICENSE-PROVENANCE-1/ac3-installer-build-info-clean.json:9-13`（bytes / sha256 / `authenticode_status=NotSigned`）一致。
- `Get-AuthenticodeSignature` 实测 `Status=NotSigned`；`SignerCertificate` 为空；stage 内 `app\NewManga.App.exe` 同样 `NotSigned`。
- 全仓库检索 `3c9984b2`：`doc/handoffs/NEXT-SESSION-STARTER.md:1409`、`doc/handoffs/STATE-OF-PROJECT-2026-11-18.md:39`、`doc/reviews/RELEASE-GATE4-EXECUTION-CHECKLIST-2026-11-17.md:25`、`doc/tasks/LICENSE-VARIANT-DECLARATION-1.md:229,232`、卡 `:97`、`ac1-environment-and-package.log:15`、`verification/WEIGHTS-LICENSE-PROVENANCE-1/ac3-clean-package-verify.log:3` 等；其中显式提到签名状态的记录均写「**未签名**」。**未发现暗示该包签名已验证的记录。**
- 历史文档中的 `Status = Valid`（`doc/release/SIGNPATH-APPLICATION-CHECKLIST.md:56`、`doc/tasks/V1-RELEASE-SIGNING-1.md:47`、`verification/GATE4-REMAINING-1/README.md:56`）是旧签名路线/未来验收口径，不是对本包签署结果的声明；`V1-RELEASE-SIGNING-1` 的 AC2 已带 `not-applicable` 注记。
- 整体未签名披露：`README.md:11,43` 明写 SmartScreen「未知发布者」提示；`packaging/nsis/installer.nsi:12,79` 也标注 unsigned。

**环境一致性**

- AC1 记录 `Win11 专业版 10.0.26300 / build 26300 / HOME-MY / China Standard Time`，当前机器 `Get-CimInstance Win32_OperatingSystem` 与 `COMPUTERNAME` 实测一致。
- 当前 agent 会话屏幕为 1920×1080，而 AC1 记录 2560×1440（阅读器截图 `ac4-page4-reader.jpg` 恰为 2560×1440）；这更像会话/显示状态差异，不构成对日志的否定，但说明「同机复现」时显示环境可能不同。

**P2-05**：AC1 日志只固定了包 hash，未记录包内 `app_build.repo_head`。stage `VERSION.json` 记录 `repo_head=292f2e77…`（0.1.1 包的构建点），而 `292f2e77..12bb456fa` 的产品面差异只有 `packaging/nsis/installer.nsi` 与 `apps/desktop-avalonia/docs/LICENSE_AUDIT.md`（无运行时 C#/Python 代码差异）。建议 AC1 证据补记 repo_head，避免「固定产品 commit」只靠包 hash 间接承载。

## 4. AC3：干净安装

**实测（日志 + stage 复算）**

- 旧安装清场：`ac3-clean-install.log:3-6` 记录旧 `uninstall.exe ExitCode=0`，清场后程序目录/卸载项均不存在，数据根 530 / 684,197,540 B。**这解释了 AC1「安装前 1,038 文件」与 AC3「安装前 0 文件」的差异**（AC1 是清场前状态，AC3 的 0 是清场后状态），不构成未解释的矛盾。
- 安装：`installer ExitCode=0`，35.1 s；安装后 1,040 文件 / 827,026,762 B。
- 安装后 `app\NewManga.App.exe`：37,344,576 B / `c2bf9265d4c821ff5a99659e9560089def91b93b8b8485bac944bb0a310b7d8d`。**我直接重算 stage** `G:\CODEX\New Manga.workspace\tmp\r28\pkg\NewManga-0.1.1-win-x64-models\app\NewManga.App.exe`，结果同为 37,344,576 / `c2bf9265…`，逐字节一致成立。
- HKCU：`DisplayName=New Manga`、`DisplayVersion=0.1.1`、`Publisher=New Manga`、`UninstallString`、`InstallLocation` 均记录（`ac3-clean-install.log:17-19`）。
- 当前机器已无该安装（程序目录/卸载项/Start Menu 均不存在），无法二次核对安装后目录；这是 AC6 的预期结果，不是缺陷。

**P1-02：Start Menu 证据自相矛盾**

- 文档值：卡 `:104` 写「Start Menu 存在 `New Manga` 文件夹（`New Manga.lnk` 2,304 B + `卸载 New Manga.lnk` 1,279 B）」；AC3 的 AC 定义（`:56`）也要求记录 Start Menu 快捷方式。
- 实测值：`ac3-clean-install.log:20` 写 **`Start Menu 项: 0（）`**；在仓库与 workspace 文本文件中检索 `2304` / `1,279` / `New Manga.lnk` 均无出处。
- 原因可定位：`G:\CODEX\New Manga.workspace\tmp\r30\ac3-install.ps1:68-69` 用 `-Filter '*NewManga*'` 在 `%APPDATA%\Microsoft\Windows\Start Menu\Programs` 下递归查找，而实际文件夹名是 **`New Manga`（含空格）**，通配符不匹配，故恒为 0。`ac6-uninstall.ps1:7,26` 用带空格的路径检查，`ac6-uninstall.log:9` 记录卸载前「Start Menu 文件夹存在：True」——证明文件夹确实存在过，AC3 的 0 是检查脚本假阴性，而卡面的 2,304/1,279 B 仍无已提交证据。
- 影响：AC3 的「记录 Start Menu 快捷方式」在该日志中实际未成立；卡面数字无法从证据复核。**处置**：用正确路径重录（或引用 AC6 的存在性检查），并把两个 `.lnk` 的名称/大小落到日志；否则删除未背书的精确字节数。

## 5. AC4：四页截图

**逐张核对（`read_image`）**

| 文件 | 页面 | 画面要点 | 状态栏 |
|---|---|---|---|
| `ac4-page1-bookshelf.jpg` | 资料柜 | 作品卡「BOOK-FIXTURE-1 日漫_JA 测试书 / 8 页」、页列表 001–008、顶部三空间 | `Host 就绪` |
| `ac4-page2-workbench.jpg` | 工位 | 页面预览 1200×1660、页缩略图条、缩放 86%、`01/08`、Region 提示 | `Host 就绪` |
| `ac4-page3-settings.jpg` | 控制台（设置） | 「设置中心 · 9 分区」九行全部列出（任务与队列/Provider/网络/模型/缓存/备份/插件/诊断/外观） | `Host 就绪` |
| `ac4-page4-reader.jpg` | 阅读器 | F11 沉浸式全屏，标题栏 `返回 (Esc) · BOOK-FIXTURE-1 … 第 1 章`，第 1/8 页 | 无（沉浸模式） |

- 四张确为**四个不同页面**，非同一画面重复、非空白；均为真实窗口（前 3 张有窗口边框，第 4 张为 2560×1440 全屏）。
- 与安装产物的关联：`ac4-four-pages.log:5-7` 记录被测 exe 为 `%LOCALAPPDATA%\Programs\NewManga\app\NewManga.App.exe`（37,344,576 / `c2bf9265…`），脚本 `ac4-four-pages.ps1:5-7,26-27` 也硬编码安装后路径。仓库 JPG 与 workspace `tmp\r30\ac4\page*.png`（2026-11-18 02:31:06–02:31:33 生成）尺寸一致、逐像素近似（缩放到 64×48 的平均绝对差 1.47–2.95），可认为 JPG 由当次实拍 PNG 转换，而非复用旧图。
- **P2-04**：四张画面均**没有版本号**（标题栏只有 `New Manga`），因此「来自 0.1.1 安装产物」只能靠日志/脚本与 hash 相同来支撑，不能由画面自证；建议后续在截图里同时截到版本/关于信息，或在 UIA 证据中记录 exe 路径与 hash。

## 6. AC5：升级与回退

**成立的部分**

- `ac5-upgrade.ps1:30-45` 明确：回退前调用 `Uninstall.exe /S`，再调用 `setup.exe /S`——**确实是卸载后重装，不是改注册表标签**。
- exe hash 序列实测（stage 重算）：
  - 0.1.1 stage exe = `c2bf9265…`（37,344,576 B）；
  - 0.1.0 stage exe = `9948f20017bb55ca5e626cf86ec6fdb142f892e1b5d46a157d4b08bba2b590e5`（37,344,583 B）。
  - 日志序列 `c2bf9265 → 9948f200 → c2bf9265 → 9948f200`（`ac5-upgrade-rollback.log:7,12,16,21`）与两次安装包一致。
- 数据根四步均为 **530 文件 / 684,197,540 B**；五次安装/卸载 ExitCode 全 0。
- 0.1.0 setup 实测存在：652,083,863 B / `19e6d0e3…`，与卡 `:98` 一致。

**P1-01：「0.1.0」是同源重构包，app 版本未变**

- 卡 `:98` 写「对照旧版 …（同源构建，仅版本号不同）」；`:106` 写 `0.1.0（exe 9948f200…）`。
- 实测 `G:\CODEX\New Manga.workspace\tmp\r30\pkg010\NewManga-0.1.0-win-x64-models\app\NewManga.App.exe`：
  - `FileVersion = 0.1.1.0`，`ProductVersion = 0.1.1+292f2e770278413f8650f04632c03fb84c76f927`；
  - 与 0.1.1 stage exe 的版本元数据**完全相同**；
  - 只有 `NewManga-0.1.0-setup.exe` 的 `FileVersion=0.1.0`、HKCU `DisplayVersion` 和 stage `VERSION.json` 的 `version` 为 0.1.0；该 `VERSION.json` 的 `app_build.repo_head=5469952f6…` 也没有出现在 exe 的 `ProductVersion`（后者仍是 `292f2e77…`）。
- 两个 exe 字节确实不同（37,344,583 vs 37,344,576；大量字节差异），所以不是「把 0.1.1 的同一个文件复制过去」。但差异来自同源重编译，不是产品版本差异；app 自身仍自报 0.1.1。
- 对照事实：workspace 内存在**真实的历史 0.1.0 安装包** `G:\CODEX\New Manga.workspace\task-envs\GATE4-PAGES-UPGRADE-1\out-0.1.0\NewManga-0.1.0-setup.exe`（652,164,075 B / `1d573ab4…` / `FileVersion=ProductVersion=0.1.0`，base 变体，build-info 记录 stage 1,037 文件 / 889,353,810 B）。AC1 记录的「安装前 1,038 文件 / 889,400,166 B」与该历史 0.1.0 base 安装量级吻合；本次矩阵没有用它做真实旧版升级，而是新建了同源 0.1.0 models 包。
- 结论：AC5 证明了**安装器/卸载/重装机制与文件替换**，没有证明**真实旧版本 → 新版本**的升级/回退（数据 schema、旧 sidecar、真实旧功能差异均未覆盖）。卡面「仅版本号不同」也不准确：app 的版本号并未改变。
- **处置（二选一）**：
  1. 用真实历史 0.1.0（上列 base 包；需登记变体差异/数据根兼容限制），或按风险 R2 从旧 commit 构建 models 0.1.0，重跑 AC5；或
  2. 把 AC5 明确改为 `MET_WITH_LIMITATION`，在卡面写清「0.1.0 为同源重构，app 自报 0.1.1；仅验证安装器级版本回退，不验证真实跨版本兼容」。

## 7. AC6：卸载与用户数据保护

**成立的部分**

- `ac6-uninstall.log:14-15`：`Uninstall.exe ExitCode=0`（0.6 s）。
- 卸载后：程序目录不存在、HKCU 卸载项不存在、Start Menu 文件夹不存在（`:17-19`）。
- 数据根：530 文件 / 684,197,540 B；丢失 0 / 新增 0 / 变化 0（`:20-23`）。
- `ac6-dataroot-before.json`：顶层 `file_count=530`、`total_bytes=684197540`、`files` 长度 **530**（Python 实测），逐文件 `bytes`/`sha256` 齐全。
- **独立强校验**：我按清单逐一重算当前 `%APPDATA%\com.newmanga.desktop` 的 530 个文件：`missing=0 / added=0 / hash_or_size_mismatch=0`，即当前数据根与清单 530 条**完全一致**；这同时佐证 AC6 的「零变化」与卡面「测试机已卸载、数据根保留」。
- 卸载的确实是 0.1.0：日志「卸载前程序目录 1,040 文件 / 827,027,191 B」与 AC5 结束时 0.1.0 的字节数一致（`ac5-upgrade-rollback.log:21`），但与 0.1.1 的 827,026,762 B 不同。

**P2-01：未明写版本**

`ac6-uninstall.log` 与卡 `:107` 都没有写「卸载的是 0.1.0」；读者需靠 827,027,191 B 与 AC5 交叉推断。建议日志增加 `DisplayVersion=0.1.0` 或「卸载前注册版本」一行，避免被误读为卸载 0.1.1。

**P2-02：before JSON 的来源标注不准**

`ac6-dataroot-before.json` 由 `matrix-baseline2.ps1:50-61` 在 AC1 阶段（02:28，安装前）生成；`ac6-uninstall.ps1:8` 虽然定义了 `$before`，但后续从未使用它，AC6 自己重新生成 `$mPre` 做比对（`:38-64`）且未落盘。因此该 JSON 实际是「安装前基线」，不是「AC6 卸载前清单」；卡面/EV-G4-10 的「卸载前」标注不准确。内容本身与当前数据根 530 条完全一致，故不推翻 AC6 结论，但建议改标注为「AC1 基线（安装前）」，或把 AC6 自己的 pre-manifest 一并提交。

## 8. 越界、门禁与卡面诚实性

**未越界**

- `git show --stat 12bb456fa`：仅 `doc/tasks/RELEASE-GATE4-SIGNED-MATRIX-1.md`（+23/−2）与 `verification/.../ac5-upgrade-rollback.log`、`ac6-uninstall.log`（新增）。
- `git diff-tree --numstat 12bb456fa`：无二进制新增；整个矩阵执行提交 `5469952f6` 也只改 `doc/**` 与 `verification/**`（含 4 张 JPG + JSON 清单），未改 `packaging/**`、`apps/**`、Python/C# 源码，未提交 setup.exe。
- `git ls-tree -r 12bb456fa` 中没有 NewManga 安装包；仅历史测试用 zip fixture 等既有文件。
- `doc/STATUS.md` 在 `12bb456fa` 仍写 Technical Gate=NOT_SATISFIED、条件 4 归本卡（`proposed`）；`RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md` 未被本卡改动，条件 5 结论未变。
- 注：`612adbac2` 随后把 STATUS 改为「4 矩阵已跑完（AC1–AC6 MET，待独立复核）」，仍未写「条件 4 通过」；不构成虚报。

**卡面诚实性（AC7）**

- AC7 在 `12bb456fa` 与当前 head 均为 `- [ ]`（卡 `:60`），执行表行写「待复核」（`:108`）。
- 明写「本轮**不宣布**条件 4 通过，也不动 Technical Gate」（`:112`）、「测试机现状：**已卸载**」（`:114`）、包「**未签名**」（`:97,103`）。
- 当前机器状态与「已卸载」一致（见 §0）。
- **P2-03**：卡 `:77-80` 的「测试要求」表仍全部为 `NOT_RUN`（执行后未更新）；AC4 的复选框缺 `<<MET>>` 标记（AC1/2/3/5/6 均有）。属文档一致性/可读性问题。

**门禁**

```
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/RELEASE-GATE4-SIGNED-MATRIX-1.md
→ Governance check: PASS (3 warnings); EXITCODE=0
```

3 条 warning：存在 2 个非终态 Task；`doc/STATUS.md` 达到预算 80%；`doc/REBASELINE_PLAN.md` 达到预算 80%。均为既有预算/台账提醒，不针对本卡。

**范围外观察（不计入本报告 P 级，交 WEIGHTS-LICENSE-PROVENANCE-1 处置）**：`verification/WEIGHTS-LICENSE-PROVENANCE-1/ac3-clean-package-verify.log` 显示包内 **`LICENSE_AUDIT.md` `SAME=False`**（包内 sha256 `d94740db…`），而 `doc/reviews/RELEASE-GATE4-EXECUTION-CHECKLIST-2026-11-17.md:25` 写「包内六份许可文件与仓库逐字节相同」。两者对同一包（652,081,157 / `3c9984b2…`）给出不同结论。该差异不改变本报告对条件 4 安装/回退/卸载矩阵的判定（AC1 只冻结包字节与 hash），但关闭 Gate 前应由该证据的归属任务把「六份」改成「五份」或说明 `LICENSE_AUDIT.md` 的例外。

## 9. Findings

### P0（0）

无。

### P1（2）

| ID | 位置 | 实测值 vs 文档值 | 命令/证据 | 处置 |
|---|---|---|---|---|
| **P1-01** | 卡 `:98,106`；`ac5-upgrade-rollback.log`；0.1.0 stage | 文档：「0.1.0 / 同源构建，仅版本号不同」；实测：0.1.0 包内 app `FileVersion=0.1.1.0`、`ProductVersion=0.1.1+292f2e77…`，与 0.1.1 相同；只有 installer/注册表/VERSION.json 标 0.1.0；真实历史 0.1.0 base 安装包存在但未使用 | `(Get-Item '<pkg010>\app\NewManga.App.exe').VersionInfo`；`(Get-Item '<inst010>\NewManga-0.1.0-setup.exe').VersionInfo`；`Get-FileHash` | 用真实旧版重跑 AC5，或把 AC5 改为 `MET_WITH_LIMITATION` 并在卡面写明「同源重构、app 仍自报 0.1.1、仅验证安装器级回退」 |
| **P1-02** | 卡 `:104`；`ac3-clean-install.log:20`；`ac3-install.ps1:68-69` | 文档：两个 `.lnk`（2,304 B / 1,279 B）；实测：AC3 日志记 `Start Menu 项: 0（）`；检索无 2,304/1,279 出处；AC6 日志证明文件夹存在过 | `ac3-install.ps1` 的 `*NewManga*` 过滤缺空格；`ac6-uninstall.log:9` | 用正确路径重录 Start Menu（含两个 `.lnk` 名称/大小），或删除未背书数字并引用 AC6 的存在性证据 |

### P2（7）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| P2-01 | `ac6-uninstall.log`、卡 `:107` | 未明写卸载的是 0.1.0；仅靠 827,027,191 B 与 AC5 交叉推断 | 日志/卡面补 `DisplayVersion=0.1.0` |
| P2-02 | `ac6-dataroot-before.json`、卡 EV-G4-10 | JSON 由 AC1 安装前基线生成，不是 AC6「卸载前」清单；AC6 脚本未消费该文件 | 改标注为「AC1 基线」，或提交 AC6 自己的 pre-manifest |
| P2-03 | 卡 `:77-80`、`:57` | 「测试要求」表仍全 `NOT_RUN`；AC4 缺 `<<MET>>` | 更新为实际结果；统一标记 |
| P2-04 | 四张 JPG | 画面无 0.1.1 版本字样；`Host 就绪` 只在 1–3 张 | 截图带版本/关于信息，或 UIA 证据记录 exe 路径+hash |
| P2-05 | `ac1-environment-and-package.log` | 未记产品 commit；命令头写 `matrix-baseline.ps1`，实际为 `matrix-baseline2.ps1`（`:12`） | 补记 `app_build.repo_head=292f2e77…`；修正脚本名 |
| P2-06 | 卡 `:56,104`；checklist `:13,59` | 「干净环境」实为同一台已用机器：先卸载旧安装、数据根已存在 530 文件、无 VM/快照；卡面披露了「先卸载」，但未登记无快照限制 | 在卡面/limitation 明写「单机、非全新 VM、数据根为既有 530 文件」；若 Gate 严格要求 VM/快照则需重跑 |
| P2-07 | `doc/reviews/RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md:31,151` | 仍把「真实证书」列为条件 4 缺口，与 2026-11-18「不需要证书」裁决不一致；关闭条件 4 前需同步 | 更新 Gate 映射的条件 4 段（本卡 allowed_paths 已含该文件） |

## 10. 条件 4 能否关闭

**逐 AC 结论**

- **AC1：成立**（环境/包 hash/测试机标识齐全；包 hash 与 build-info 一致；产品 commit 仅缺显式记录，P2-05）。
- **AC2：成立**（`NotSigned` 实测且如实登记；README/NSIS 有 SmartScreen 披露；无签名已验证主张）。
- **AC3：核心成立，证据有 P1**（ExitCode 0 / 1,040 文件 / exe 与 stage 一致 / HKCU 齐全；Start Menu 记录不成立，P1-02）。
- **AC4：成立**（四页实拍、互不相同、真实窗口；安装后 exe 与 stage 同 hash；版本字样缺失为 P2-04）。
- **AC5：机制成立，真实跨版本不成立**（真卸载重装 + hash 序列 + 数据根不变；但「0.1.0」为同源重构、app 自报 0.1.1，P1-01）。
- **AC6：成立**（ExitCode 0；程序/HKCU/Start Menu 清理；数据根 530 / 684,197,540、0/0/0；JSON 530 条且当前数据根 530/530 全哈希匹配；版本声明与 JSON 来源为 P2）。
- **AC7：未勾选，待复核**；卡面未宣布条件 4 通过。

**能否关闭**

- **不能无条件把条件 4 标为「通过」或普通 `closed`。** 现有证据足以证明安装/卸载/四页/数据保护，但 AC5 的「上一版本」不是真实旧版，AC3 的 Start Menu 记录与卡面矛盾。
- **可以走 `closed_with_limitations`**，前提是 Lead 先处置：
  1. P1-01：要么用真实历史 0.1.0（base 包 `652,164,075 B / 1d573ab4…`，登记变体/数据兼容限制）或旧 commit 构建的 models 0.1.0 重跑 AC5；要么把 AC5 降为 `MET_WITH_LIMITATION` 并在卡面写清「同源重构、app 仍 0.1.1、只验证安装器级回退」。
  2. P1-02：补正 AC3 Start Menu 证据（正确路径 + 两个 `.lnk` 名称/大小），或删除未背书数字并引用 AC6 存在性证据。
  3. P2-06：把「单机、非全新 VM、无快照、数据根既有」写入 limitation；若 Gate 按 checklist 严格要求干净 VM/快照，则需重跑 AC3/AC5/AC6。
  4. P2-07：同步 Gate 六条映射的条件 4 段（不再要求真实证书）。
  5. 其余 P2（AC6 版本、JSON 来源、卡面测试表、AC4 版本证据、AC1 commit）在关闭前一并修正。
- **若不能接受上述 limitation，则条件 4 仍缺**：真实旧版本 → 当前版本的升级/回退证据（含旧 sidecar/数据 schema 兼容）、正确的 Start Menu 证据、干净 VM/快照（若适用）。

## 11. 方法与限制

- 本报告只对 `reviewed_head: 12bb456fa` 的证据负责；`612adbac2`/`d582946eb` 为复核期间出现的 doc-only 后续提交，不改变本报告对矩阵执行的判定。
- 证据文件的 Canonical Evidence sha256（卡 `:120-129`，在 `612adbac2` 登记）逐条按 **git blob** 重算全部一致；由于本仓库 `core.autocrlf=true`，工作区文本文件为 CRLF，直接 `Get-FileHash` 会得到不同值——复核 pin 必须用 `git cat-file blob <commit>:<path>`，不能用工作区文件哈希。10 条 pin 的实际核验见附录。
- 未重装/卸载任何东西；当前机器无安装、数据根 530/684,197,540 B 的状态与 AC6 结束态一致。
- 未修改任何仓库文件（本报告除外）、未修改 workspace 的 stage/fixture、未提交/推送。
- 本复核为证据复核，不替代安装器/产品代码的独立测试；AC3 安装后目录、HKCU、Start Menu 的「安装时」状态因机器已卸载，只能以日志为准（AC3 的 stage exe 哈希已独立重算）。

**声明：本复核不构成产品发布验收；本复核不改变 `Technical Gate`（仍为 `NOT_SATISFIED`），也不改变条件 5 的 `LIMITATION_ACCEPTED`。**

## 附录 A：Canonical Evidence hash 核验（git blob）

| evidence_id | 文件 | 卡面 sha256（前 12） | git blob 实测（前 12） | 一致 |
|---|---|---|---|---|
| EV-G4-01 | ac1-environment-and-package.log | 473f06b1fef0 | 473f06b1fef0 | ✅ |
| EV-G4-02 | ac3-clean-install.log | 7c72e5762f34 | 7c72e5762f34 | ✅ |
| EV-G4-03 | ac4-four-pages.log | 6af1db0f1076 | 6af1db0f1076 | ✅ |
| EV-G4-04 | ac4-page1-bookshelf.jpg | c1a44f3f31ec | c1a44f3f31ec | ✅ |
| EV-G4-05 | ac4-page2-workbench.jpg | 8df06f62f00d | 8df06f62f00d | ✅ |
| EV-G4-06 | ac4-page3-settings.jpg | 10761638af40 | 10761638af40 | ✅ |
| EV-G4-07 | ac4-page4-reader.jpg | 0de8c1d72d72 | 0de8c1d72d72 | ✅ |
| EV-G4-08 | ac5-upgrade-rollback.log | cc9f781fd139 | cc9f781fd139 | ✅ |
| EV-G4-09 | ac6-uninstall.log | a2896e78931e | a2896e78931e | ✅ |
| EV-G4-10 | ac6-dataroot-before.json | 5cdd21212aef | 5cdd21212aef | ✅ |

（卡面完整 sha256 见 `doc/tasks/RELEASE-GATE4-SIGNED-MATRIX-1.md:120-129`；该表在 `612adbac2`（被审 head 之后）加入，10 条均按 `12bb456fa` 的 git blob 复核；命令：`git cat-file blob 12bb456fa:verification/.../<file> | python -c "sha256"`。）

## 附录 B：关键命令（节选）

```powershell
# 包与 exe
(Get-FileHash 'G:\CODEX\New Manga.workspace\tmp\r28\inst\NewManga-0.1.1-setup.exe' -Algorithm SHA256).Hash
(Get-AuthenticodeSignature 'G:\CODEX\New Manga.workspace\tmp\r28\inst\NewManga-0.1.1-setup.exe').Status
(Get-Item 'G:\CODEX\New Manga.workspace\tmp\r28\pkg\NewManga-0.1.1-win-x64-models\app\NewManga.App.exe').Length
(Get-FileHash 'G:\CODEX\New Manga.workspace\tmp\r28\pkg\NewManga-0.1.1-win-x64-models\app\NewManga.App.exe' -Algorithm SHA256).Hash

# 0.1.0 stage（AC5）
(Get-FileHash 'G:\CODEX\New Manga.workspace\tmp\r30\pkg010\NewManga-0.1.0-win-x64-models\app\NewManga.App.exe' -Algorithm SHA256).Hash
(Get-Item 'G:\CODEX\New Manga.workspace\tmp\r30\pkg010\NewManga-0.1.0-win-x64-models\app\NewManga.App.exe').VersionInfo

# AC6 清单 530 条与当前数据根逐文件哈希
python -c "…json + os.walk + hashlib.sha256…"   # missing=0 / added=0 / mismatch=0

# 治理
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/RELEASE-GATE4-SIGNED-MATRIX-1.md
```

---

# P1 复检追加（2026-11-18，reviewer-g4）

> 只复核 P1-01 / P1-02 的处置，未重做整轮复核，未重装/卸载任何东西。复核目标 head = **`bf7859965`**；复核时实际 HEAD 已到 `dc1caccbb`（仅补登 EV-G4-11/12，doc-only），P1 判定以 `bf7859965` 为准。

## 12. P1-01：AC5 用真实历史 0.1.0 包重做 —— **CLOSED**（附 caveat）

### 12.1 实测核对

- 历史包指纹：`G:\CODEX\New Manga.workspace\task-envs\GATE4-PAGES-UPGRADE-1\out-0.1.0\NewManga-0.1.0-setup.exe`
  = **652,164,075 B / sha256 `1d573ab4…` / setup FileVersion=0.1.0**，与新日志第 8 行一致。
- 历史 stage 的 app exe：`…\stage-0.1.0\NewManga-0.1.0-win-x64\app\NewManga.App.exe`
  = **99,554,850 B / sha256 `a3ec2133b5da3f619b752c818371ba54867b4c150fdba65b8c22d8b17f739230`**，与新日志第 21/40 行一致；`FileVersion=0.1.1.0`、`ProductVersion=0.1.1+71cecb95a10c42ffe02d1396ab065e1fc9c43ca9`。
- 历史包构建点 `71cecb95` = **2026-11-15 04:44** 的真实旧提交（`git merge-base --is-ancestor 71cecb95 HEAD` 为真）；`71cecb95..bf7859965` 的产品面差异为 **55 files / +3,860 / −208**（含 Host/Python 测试、`packaging/nsis/installer.nsi` 等），不是同源重构。
- 0.1.1 stage exe = 37,344,576 B / `c2bf9265…`（新日志第 30 行），与既有一致。
- 回退后 app exe 回到 `a3ec2133…`（新日志第 40 行），与首次 0.1.0 相同。
- 数据根五步：第 13/20/29/39/47 行均为 **530 文件 / 684,197,540 B**；当前机器确已卸载（程序目录/卸载项/Start Menu 均不存在），数据根仍 530 / 684,197,540 B。
- Start Menu：新日志第 22-24/31-33/41-43 行在三次安装后均记录 `New Manga.lnk` 2,304 B + `卸载 New Manga.lnk` 1,279 B（附 sha256）。

### 12.2 判定

**P1-01 CLOSED。** 这次用的是真实旧包、真实旧二进制（99.5 MB 旧构建 vs 37.3 MB 单文件构建，构建 commit `71cecb95` vs `292f2e77`），升级/回退是真卸载重装；不是上一轮那种同源改标签。

**必须写入 limitation 的 caveat**：

1. 历史 0.1.0 的 app **也自报** `FileVersion=0.1.1.0`、`ProductVersion=0.1.1+71cecb95…`。因此「0.1.0」是**安装器/包级版本**，不是应用自报版本；若 Gate 的「版本」要求应用可见版本变化，这一项仍未满足；若要求真实旧二进制升级/回退，已满足。
2. 新日志**未打印收尾卸载的 ExitCode**：脚本 `ac5-real-upgrade.ps1:101` 计算了 `$u4`，但日志第 45-49 行没有输出它，而第 56 行声称「全部 ExitCode=0」。补一行 `卸载 ExitCode=$u4` 即可。
3. 升级/回退后**没有启动 app 读取数据**；AC5 的 AC 文本不要求，但「真实跨版本兼容」若要更强，需补一次启动/读取，或写入 limitation。

## 13. P1-02：Start Menu 证据补正 —— **CLOSED**

- `ac3-clean-install.log` 的 diff **只在末尾追加 9 行**（第 22-29 行），原第 1-20 行逐字保留，原「Start Menu 项: 0（）」未被覆盖；追加说明与实际原因一致（`ac3-install.ps1:68-69` 的 `-Filter '*NewManga*'` 漏了目录名 `New Manga` 中的空格）。
- 卡面 AC3 行已改为引用 `ac5-upgrade-rollback-real.log`，保留「原 0 项是过滤串写错」的更正说明；两个 `.lnk` 的 2,304 / 1,279 B 在新日志第 23-24/32-33/42-43 行有字节与 sha256，**不再是未背书数字**。
- `ac6-uninstall.log` 仍证明卸载后 Start Menu 目录被清理（存在=False）。

**残余 P2（不阻断）**：

1. AC3 那次 0.1.1 干净安装本身仍没有 Start Menu 快照；现有尺寸来自**同一 0.1.1 安装器**在 AC5 重做中的第 2 步（新日志第 31-33 行）。作为等价证据可接受，但不是同一次安装实例；若要严格同实例，补一条 AC3 安装后的 Start Menu 快照。
2. 三次安装的 `.lnk` **sha256 各不相同**（2,304/1,279 B 稳定）；这通常是 `.lnk` 内嵌目标/时间等元数据所致，但日志未说明，容易被误读为捷径内容不一致。建议加一句「尺寸稳定、sha256 随安装时间变化」。

**P1-02 CLOSED。**

## 14. 五条 limitation 是否足够

方向正确，但按我上一轮标准，**需要两处补充、一处措辞修正**：

1. **补充**：历史 0.1.0 的 app 自报 `FileVersion 0.1.1.0`（见 §12.2）；AC5 未在升级/回退后启动应用读取数据。
2. **补充（P2-01/P2-02）**：卡面 P2 段写 P2-01/P2-02「见下方 limitation」，但五条 limitation 里**没有**这两项——AC6 未明写卸载的是 0.1.0；`ac6-dataroot-before.json` 是 AC1 安装前基线，不是 AC6 卸载前清单。要么补进 limitation，要么删掉这个悬空引用。
3. **措辞**：limitation 3 的「历史 0.1.0 包属旧构建（base 变体）」应补一句「其 app 自报 0.1.1.0；0.1.0 为包/安装器标签」，否则读者会以为应用版本也变成了 0.1.0。

其余四条（单机/无 VM 快照、既有数据根、未签名、AC4 隔离数据根）表述可以保留。

## 15. 条件 4 能否 `closed_with_limitations`

**可以。** 两条 P1 已实质关闭；下面只是关闭登记前建议补齐的 **P2/登记项**，不构成新的阻断性证据缺口：

1. 新 AC5 日志补收尾卸载 `ExitCode`（或不再声称未展示的那一项）。
2. limitation 3 补「app 自报 0.1.1.0 + 未启动应用读取数据」；并解决 P2-01/P2-02 的悬空「见下方 limitation」引用。
3. Canonical Evidence 补钉：修改后的 `ac3-clean-install.log` 在 `bf7859965` 的新 blob 为 `b2969af65dd09e83292b0708b40475335b5749148b8a8ff935d6ecb4edf98b81`，而 EV-G4-02 仍指 `12bb456fa` 的旧 blob `7c72e576…`——建议新增一条 EV 或在 EV-G4-02 注明「含追加更正前的 12bb456fa 版本」；本次追加会改变复核报告字节，EV-G4-12 的 `f5a6f76e…` 需随新提交重钉（EV-G4-11 已与 `ac5-upgrade-rollback-real.log` 的 `e769ca2e…` 匹配）。
4. `doc/reviews/RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md:31` 仍把「真实证书」列为条件 4 缺口（P2-07）；关闭前同步该行或注明已被 `MAINT-1` 的 2026-11-18 更正覆盖。
5. 可选：给 AC3 补一条同实例 Start Menu 快照，或明确接受「同一安装器、另一安装实例」的等价证据。

除这些 P2/登记项外，**没有发现阻止 `closed_with_limitations` 的新证据缺口**；条件 4 可关闭，但仍**不得**写成无条件 `closed` 或「条件 4 通过」的更强结论，且不改变 `Technical Gate=NOT_SATISFIED`。
