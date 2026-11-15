# 历史卡元数据缺陷修复 — 证据

Task：`GOV-HISTORICAL-CARD-METADATA-REPAIR-1`（Owner：DSH）
基线：`ed8b56c9f`

## 1. 问题

`GOV-CHECKER-HISTORICAL-AC-EXEMPT-1` 消除 **AC 门禁**误差后，5 张 gv3 历史终态卡在
`check.ps1 -TaskPath` 下仍因**卡面元数据**缺陷 FAIL：

| 卡 | 缺陷（修复前） |
|---|---|
| `CHAPTER-MANUAL-SORT` | `evidence_dir` 含 2 个未登记文件（`four-pieces.log`、`pending-host-cache-test.cs.txt`） |
| `FEA-04` | ① `E-SCOPE` 路径 `doc/reviews/FEA-04-scope-r1/r2/r3.md` 不存在（实为 3 个独立文件）；② `evidence_dir` 含 11 个未登记日志；③ `worktree/branch` 的 `sha256/manifest` 列是散文（「分支 feat/fea-04（…）」） |
| `RELEASE-PACKAGE-1` | `task-env` 的 `sha256/manifest` = 「待填」 |
| `MICA-FIX-1` | 同上 |
| `FEA-07-AC5-NATIVE-1` | `DEFECTS.md` 的 sha256 与当前 blob 不匹配（`be905e0c…` → `2407dd2c…`） |

`GATE3-COVERAGE-MATRIX` 此前已 PASS，无需改动。

## 2. 修复（只改 `Canonical Evidence` / `Resource Manifest` 两张表）

| 卡 | 改动 |
|---|---|
| `CHAPTER-MANUAL-SORT` | 新增 `EV-CMS-08`（`four-pieces.log`，CANONICAL/BLOB）、`EV-CMS-09`（`pending-host-cache-test.cs.txt`，SOURCE_PIN/BLOB） |
| `FEA-04` | ① `E-SCOPE`（不存在的合并路径）替换为 `E-SCOPE-R1/R2/R3` 三行（各自真实文件 + sha256）；② 新增 `E-LOG-01…11` 登记 11 个构建/测试过程日志（SOURCE_PIN）；③ `worktree/branch` 的 `sha256/manifest` 改为真实路径 `G:/CODEX/New Manga.workspace/FEA-04/.git`，并写「worktree 存在（feat/fea-04 @43bce62e4）；已集成 f4d8a32ec，保留未 prune」 |
| `RELEASE-PACKAGE-1` | `task-env` 的 `sha256/manifest` 改为 `…/task-envs/RELEASE-PACKAGE-1/out/package-summary.json`，结果列写「已核（2026-11-15）：package-summary.json、NewManga-0.1.0-win-x64.zip 等存在」 |
| `MICA-FIX-1` | 同上，改为 `…/task-envs/MICA-FIX-1/solid.bmp`，结果列写「已核：solid.bmp / pattern.bmp 各 8,294,454B 存在」 |
| `FEA-07-AC5-NATIVE-1` | `EV-AC5-P05`（`DEFECTS.md` 行）的 sha256 更新为当前 blob `2407dd2cd02f97ee…` |

**sha256 口径**：全部用 `git cat-file blob HEAD:<path>` 的原始字节 SHA-256（与 `check.ps1` 的 OR 判据 ——
工作区字节或 commit blob 任一匹配 —— 兼容；避免 `Get-FileHash` 被 CRLF/BOM 影响）。

## 3. 结果：6 卡全 PASS

`check.ps1 -TaskPath`（明细见 `after.txt`）：

```
CHAPTER-MANUAL-SORT    PASS (3 warnings)
FEA-04                 PASS (3 warnings)
GATE3-COVERAGE-MATRIX  PASS (3 warnings)
RELEASE-PACKAGE-1      PASS (3 warnings)
MICA-FIX-1             PASS (3 warnings)
FEA-07-AC5-NATIVE-1    PASS (4 warnings)
```

修复前：5 张 FAIL（1/3/0/1/1/1 errors）。

## 4. 修复前（before）

```
CHAPTER-MANUAL-SORT    FAIL (1 errors, 3 warnings)   <- DONE evidence_dir 含未登记文件
FEA-04                 FAIL (3 errors, 3 warnings)   <- Canonical 路径缺失 / evidence_dir 未登记 / Resource manifest 不存在
GATE3-COVERAGE-MATRIX  PASS (3 warnings)
RELEASE-PACKAGE-1      FAIL (1 errors, 3 warnings)   <- Resource manifest 不存在：待填
MICA-FIX-1             FAIL (1 errors, 3 warnings)   <- Resource manifest 不存在：待填
FEA-07-AC5-NATIVE-1    FAIL (1 errors, 4 warnings)   <- Evidence SHA-256 不匹配
```

## 5. 不回归

```
check.ps1（全局）            → PASS (3 warnings)
verify_pins.ps1              → PASS (all 18)
generate_api_inventory.py    → OK (1/80/6=87)
```

**改动面（r1 复核后更正）**：9 个文件 = 5 张卡 + 本卡 + 证据 2 个 + `doc/TASK_LEDGER.md`，
`224 insertions / 10 deletions`（TASK_LEDGER 为新建卡后防止「台账过期」所必需，亦在本卡 `allowed_paths` 内）。
**AC 行、`status`、结论章、Handoff/Review 记录零改动**；`tools/**` 零改动（未弱化 checker 换 PASS）。

## 6. 已知与不淡化

1. **`FEA-07-AC5-NATIVE-1` 有 4 warnings**（其余 5 卡 3 warnings）——该卡既有，非本次引入。
2. **`FEA-07` 的 `EV-AC5-P05` ID 在卡内重复**（两个不同文件共用同一 ID：`DEFECTS.md` 与
   `evidence/physical-state-after-…`）。本次只更新了 `DEFECTS.md` 那一行的 sha，**未改 ID**；
   重复 ID 属卡面既有缺陷，建议后续清理。
3. 本修复**只消除检查器缺陷**，不代表这些历史卡的结论有新证据；AC 的 `blocked` 项仍为 `blocked`。
4. 台账：新建本卡后 `TASK_LEDGER` 曾过期（6 卡各多 2 条 `TASK_LEDGER 已过期` 错误），
   已重生成；这也是「新建卡必须重跑 `task_ledger.py --write`」的第 3 次复现。
