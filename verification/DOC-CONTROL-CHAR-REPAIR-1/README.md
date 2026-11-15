# doc/tasks 控制字符修复 — 证据

Task：`DOC-CONTROL-CHAR-REPAIR-1`（Owner：DSH；独立复核 `ctrlchar-review`）
基线：`3fd3316ed` → 实现 commit `9a0651e6e` → r1 返修（本文件所在提交）

## 1. 问题

`doc/tasks/**` 中 **65 个文件 / 113 处**含 C 风格转义泄漏。**损坏规律（独立复核 r1 确证）**：
把**转义字母原位替换成对应控制字节** ——
`v→0x0B`、`a→0x07`、`b→0x08`、`f→0x0C`、`e→0x1B`、**`0→0x00`**。

后果：`verification` 写成 `erification`、`apps/` 写成 `pps/`、`frozen` 写成 `rozen`、
`vitest` 写成 `itest` —— 这些词在卡面**不可 grep**。

## 2. 方法与判定

1. **全量清点**：`scan.py` 输出每处的 文件/行/字符偏移/hex/上下文（`scan.md`：113 行表格 + 逐行原文）。
2. **映射候选**：`0x0B→v`、`0x07→a`、`0x08→b`、`0x0C→f`、`0x1B→e`、`0x00→0`。
3. **验证驱动**：把候选替入后取该位置 ASCII token，检查是否存在于
   （a）仓库文本 token 集合（782,253 条），或（b）`git cat-file -t` 可解析的 commit。
   **最终树重算：102 / 113 = 90.3% 可由自动验证覆盖**（词表已排除 `doc/tasks/**` 以避免自证循环；其中 5 个 commit
   `0e752fbad`、`075dc1682`、`04b657131`、`09d7e76c1`、`0e1f71151` 实测 `git cat-file -t` = commit）。
4. **人工判定 11 处**：token 是路径/文件名/短 sha 前缀（词表未收录但上下文唯一可判）；
   其中 **2 处**（`GOV-EVIDENCE-DIR-SWEEP-1.md:48/:56`）原文是**两字节 `\a`**
   （`G:\CODEX\New Manga.workspace\archive\...` 的路径分隔符被转义）。
5. **完备性反查**：对 `0x00` 的候选集必须包含数字 `0`，并用 `git cat-file -t` 反证
   「错误值不是对象」—— `e752fbad`/`e75dc1682`/`e4b657131`/`e9d7e76c1`/`e1f71151` 均 `NOT_A_OBJECT`，
   而 `0e752fbad`/`075dc1682`/`04b657131`/`09d7e76c1`/`0e1f71151` 均为 commit。

**无法唯一判定：0 处**（113/113 均有明确依据，明细见 `verify.log`）。

## 3. r1 复核返修（10 处 `0x00`）

初版把 `0x00` 误映射为 `e`（7 处）或判为删除（3 处），**10 处全部判错**。独立复核以
`git cat-file -t` 给出决定性证据后全部修正：

| 文件:行 | 初版 | 修正为 | 依据 |
|---|---|---|---|
| `D-14-STATUS-COLOR-FIX.md:86` | `e75dc1682` | `075dc1682` | commit |
| `GPU-ORT-PROBE-1.md:95` | `e4b657131` | `04b657131` | commit |
| `HOST-TILE-CHANNEL-1.md:183` | `e9d7e76c1` | `09d7e76c1` | commit |
| `RUN-EXPORT-E2E-1.md:93` | `e4b657131` | `04b657131` | commit + handoff |
| `RELEASE-REPACK-2.md:91` | `e91a201d` | `091a201d` | sha 前缀（`UPGRADE.md` 旁证） |
| `RELEASE-REPACK-3.md:92` | `e91a201d` | `091a201d` | 同上 |
| `LEGACY-SHELL-REMOVAL-1.md:92` | `e9d7e76c1` | `09d7e76c1` | commit |
| `DESIGN-V2-IMPL-1.md:107` | 删除 | `0e752fbad` | commit + handoff 文件名同值 |
| `RELEASE-PACKAGE-1.md:96` | 删除 | `0ee47fb7` | sha256 前缀（同族规律） |
| `THEME-MACOS-2.md:124` | 删除 | `0e1f71151` | commit + `PLAN-HISTORY.md:79` |

修正后 `doc/tasks/**` 仍为**零控制符**（独立扫描 638 个 blob，0 命中）。

## 4. 结果

| 指标 | 值 |
|---|---|
| 修复处数 | **113 / 113** |
| 涉及文件 | **65** |
| 残留控制符 | **0** |
| 无法唯一判定 | 0 |
| 自动验证覆盖 | **102/113 = 90.3%**（词表排除 `doc/tasks/**`；≥ AC1 的 80% 门槛） |

**差异最小化**（r1 逐字节复核确认）：65 个卡文件行数不变；97 个受影响行
**全部只由控制符替换推导出**；未受影响行 100% 逐字节相同。
`numstat`：`1/1`×43、`2/2`×14、`3/3`×2、`4/4`×1、`5/5`×2；3 个 HEAD blob 含控制符的文件
（`D-14-STATUS-COLOR-FIX`、`GPU-ORT-PROBE-1`、`LEGACY-SHELL-REMOVAL-1`）在 git 中显示 binary，
但 `git diff --text` 与 blob 大小为 6197/8150/6667 **不变**、严格 UTF-8、无 NUL、CR 数不变。

**可 grep 性**（`doc/tasks/*.md`，`Select-String -List`、默认不区分大小写）：
`verification` 631 文件｜`apps/` 365｜`frozen` 155｜`vitest` 93｜`existing` 49。
（区分大小写口径：`verification` 631、`apps/` 365、`frozen` 89、`vitest` 86、`existing` 33。）

## 5. 不回归

```
check.ps1                    → PASS (3 warnings)
verify_pins.ps1              → PASS (all 18)
generate_api_inventory.py    → OK (1/80/6=87)
verify_locators.py（AC 注释）→ 418/418 行内命中，0 偏差
```

AC 注释里的 418 个 `test:`/`grep:` 定位符全部不受影响（控制符均在非 AC 行）。

## 6. 已知限制（不淡化）

1. **`doc/tasks` 仍有同类损坏未修（r1 的 P2-3，此前未披露）**：
   - **33 个 TAB（`\t`）**：如 `\tsc`、`\test.ps1`、`\task/…`、`\tokens.json`；
   - **20 个 CR（`\r`）**：如 `SCHEDULER-THREAD-DIAG-1.md:105` 的 `；\refresh()`；
   - **VT 被当换行造成的行首断词**：如 `FEA-09.md:322/325`、`IMPORT-TRIAGE-1.md:47`。
   这些不在本卡登记的 113 处内（AC-CHECKBOX-AUTHORITY-1 §7.8 只登记了
   `[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]` 这一族），需另立 Task；本卡不声称「所有词已恢复」。
2. **3 个文件在 git 中仍显示为 binary**：其 HEAD blob 含控制符，git 按 binary 处理 diff；
   修复后工作区是合法 UTF-8 且无控制符。
3. **2 处替换使文件 +1 字节**（`\a` 两字节复原），这是**还原**而非膨胀。
4. **`app-on-4k-dpr2.png` 在仓库与磁盘均不存在**（既有问题，非本卡引入）。
5. `doc/tasks/**` 之外（`doc/reviews/**`、`verification/**`）是否也有同类损坏**未排查**。

## 7. 复现

```powershell
cd "G:\CODEX\New Manga"
python "G:\CODEX\New Manga.workspace\tasks\DOC-CONTROL-CHAR-REPAIR-1\scan.py"
python "G:\CODEX\New Manga.workspace\tasks\DOC-CONTROL-CHAR-REPAIR-1\repair.py" --dry-run
# 逐处判定表（113 行）：见本目录 control-char-inventory.md（逐处判定表）与 verify-final.log（机器可读）
```
