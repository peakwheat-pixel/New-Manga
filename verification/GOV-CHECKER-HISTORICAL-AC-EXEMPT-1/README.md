# check.ps1 历史终态卡 AC 豁免 — 证据

Task：`GOV-CHECKER-HISTORICAL-AC-EXEMPT-1`（Owner：DSH / 独立复核 `gcheck-review`）
基线：HEAD `b8113e740`

**改动文件（3 个）**：
- `tools/governance/check.ps1`（豁免逻辑）
- `doc/09_COLLABORATION.md`（§4.3.1「历史终态卡豁免」段）
- `doc/TASK_LEDGER.md`（新建卡后重生成）

> 本文件经独立复核 r1 的 R-02/R-03/R-05/R-06 更正：基线数字的口径、AC 门禁错误条数、全仓统计口径、
> 「改动文件」清单均已修正。

## 1. 问题

`AC-CHECKBOX-AUTHORITY-1` 为 40 张历史卡引入 §4.3.1 的行内 HTML 注释标注
（`<!-- verified|not-applicable|blocked: … -->`）。但 `check.ps1` 的 lifecycle v3 门禁
（原 `:921`，改动后 `:926`）仍要求 AC 行末为 `<<MET|PARTIAL|BLOCKED|NOT_APPLICABLE>>`，于是 6 张
`governance_version: 3` 的历史终态卡在 `-TaskPath` 下报错。

## 2. 改动（3 处，纯新增分派，不删除任何既有校验）

### 2.1 识别「§4.3.1 形式」（三重限定）

```powershell
$htmlAcStyle = ($taskText -match '(?m)^[ \t]*-[ \t]*\[[ xX]\][^\r\n]*\*\*AC[0-9A-Za-z._-]*[^\r\n]*<!--\s*(verified|not-applicable|blocked)\s*:')
$historicalAcExempt = ($htmlAcStyle -and $metadata['governance_version'] -eq '3' -and $taskStatus -in @('done','closed_with_limitations'))
```

**三重与**：① AC 行（`**AC` 锚，同一行）带三种 HTML 注释之一；② `governance_version: 3`；
③ `status ∈ {done, closed_with_limitations}`。当前活跃 Task 不满足 ③ → 不受影响。

**作用域收窄（独立复核 r1 的 R-01）**：判定与校验均锚定 `**AC` 行，非 AC 的 checkbox 行不参与，
避免「零 AC 行 + 非 AC 行带注释」绕过「未找到任何 AC 行」，或反向误分派。

### 2.2 DONE-未完成豁免

原「DONE 不能保留未完成 AC」（`:856` → 改动后 `:861`）增加 `-not $historicalAcExempt -and` 前缀。
依据：§4.3.1 明确允许 `blocked` 的 AC 保持 `[ ]`。

### 2.3 §4.3.1 校验分支

原 `if (gv3 && 终态) { <§4.3 校验> }` 改为
`if (gv3 && 终态 && $historicalAcExempt) { <§4.3.1 校验> } elseif (gv3 && 终态) { <原 §4.3 校验，逐字节保留> }`。

§4.3.1 校验五项：① AC 行必须带三种注释之一；② `verified`/`not-applicable` 必须勾选、`blocked` 必须不勾选；
③ 注释原因非空；④ 裸 `[x]` 报错；⑤ 无 AC 行报错。

## 3. 改动前基线（`baseline.txt`）

**口径说明（R-02 更正）**：基线是在**新卡 `GOV-CHECKER-HISTORICAL-AC-EXEMPT-1` 已创建、
`TASK_LEDGER` 尚未重新生成**时测量的，因此每卡总错误数各含 **2 条 `TASK_LEDGER 已过期`**
（声明 635 个 Task / 实际 636；声明 11 个非终态 / 实际 12）——与本改动无关。

| 卡 | 总错误（含 2 条台账过期） | 其中 AC 门禁错误 |
|---|---|---|
| `CHAPTER-MANUAL-SORT` | 14 | 11（10 标记缺失 + 1 DONE-unfinished） |
| `FEA-04` | 14 | 9（8 标记缺失 + 1 DONE-unfinished） |
| `GATE3-COVERAGE-MATRIX` | 9 | 7（6 标记缺失 + 1 DONE-unfinished） |
| `RELEASE-PACKAGE-1` | 10 | 7（6 标记缺失 + 1 DONE-unfinished） |
| `MICA-FIX-1` | 9 | 6（5 标记缺失 + 1 DONE-unfinished） |
| `FEA-07-AC5-NATIVE-1` | 8 | 5（5 标记缺失；closed_with_limitations 不触发 DONE 项） |
| **合计** | — | **45**（40 标记缺失 + 5 DONE-unfinished） |

**反例** `ADJ-B-RESTART-HINT-1`（gv3 终态、无 HTML 注释）：总错误 8（含 2 条台账过期），
其中 **AC 门禁错误 1 条**（「未找到任何 AC 行」）—— 该条在改动前后**保持 1→1 不变**。

## 4. 改动后（`after.txt`，台账已重生成）

| 卡 | AC 门禁错误 | 其它错误 | 总体 |
|---|---|---|---|
| `CHAPTER-MANUAL-SORT` | **0** | 1（`evidence_dir` 未登记 `four-pieces.log`、`pending-host-cache-test.cs.txt`） | FAIL (1) |
| `FEA-04` | **0** | 3（Canonical 路径缺失 / `evidence_dir` 未登记 / Resource manifest 不存在） | FAIL (3) |
| `GATE3-COVERAGE-MATRIX` | **0** | 0 | **PASS** |
| `RELEASE-PACKAGE-1` | **0** | 1（Resource manifest 待填） | FAIL (1) |
| `MICA-FIX-1` | **0** | 1（Resource manifest 待填） | FAIL (1) |
| `FEA-07-AC5-NATIVE-1` | **0** | 1（`DEFECTS.md` SHA-256 不匹配） | FAIL (1) |
| **反例** `ADJ-B-RESTART-HINT-1` | **1（不变）** | 5 | FAIL (6) |

**结论**：
1. 6 张卡的 **AC 门禁错误 45 → 0**；`GATE3-COVERAGE-MATRIX` 由 FAIL 变 **PASS**；
2. **反例的 AC 门禁错误 1 → 1 不变**，证明门禁未被放宽；
3. 剩余 7 条错误是各卡**独立的历史缺陷**，不由本 Task 修复（需改历史卡 manifest/pin，超出授权）；
4. 6 卡 checkbox 行与 `**AC` 行**完全相等**（10/8/6/6/5/5），作用域收窄不影响它们。

## 5. 边界用例（分派正则纯字符串测试，6/6 符合预期）

| 用例 | 期望 | 实测 |
|---|---|---|
| S1 AC 行 + HTML 注释 | True | **True** |
| S2 正文单独注释、AC 无注释 | False | **False** |
| S3 AC 行无 `**AC` 锚 | False | **False** |
| S4 零 AC 行 + 非 AC checkbox 带注释 | False | **False** |
| S5 AC 用 `<<MET>>` + 非 AC 行带注释 | False | **False** |
| S6 `blocked` AC 注释（未勾选） | True | **True** |

## 6. 全仓统计（R-05 更正：以复核者实测为准）

`doc/tasks/` 下 `governance_version: 3` 且终态（`done`/`closed_with_limitations`）的卡共 **271** 张：
- 用 §4.3 `<<...>>` 标记：**224** 张（走原分支）
- 用 §4.3.1 HTML 注释：**6** 张（本豁免唯一适用集）
- 两者都无：**41** 张（仍按原分支报错）

⇒ 豁免面精确覆盖 6 张，占 271 的 2.2%。

## 7. 四件套（改动后）

```
check.ps1（全局）            → PASS (3 warnings)   ← 与改动前 HEAD 版同为 3 warnings
verify_pins.ps1              → PASS (all 18)
generate_api_inventory.py    → OK (1/80/6=87)
```

## 8. 未削弱论证（三条独立证据）

1. **代码层**：原 §4.3 分支以 `elseif` 完整保留；复核者把 HEAD 与工作树的该段切片做 `-ceq`，
   39 行逐字节相同（`IDENTICAL = True`）。
2. **行为层**：反例 `ADJ-B-RESTART-HINT-1` 的 AC 门禁错误保持 1→1；6 个边界用例全部符合预期。
3. **范围层**：271 张 gv3 终态卡中仅 6 张（2.2%）进入豁免；当前活跃 Task 不满足终态条件。

## 9. 已知限制

- 本 Task 自身在收口前为 `in_progress`，未登记 `REBASELINE_PLAN` DAG，故自测
  `check.ps1 -TaskPath doc/tasks/GOV-CHECKER-HISTORICAL-AC-EXEMPT-1.md` 会报「当前 DAG 未登记非终态 Task」
  （复核 r1 的 R-07）——该卡标 `done` 后不再触发，无需登记 DAG。
- 豁免仅覆盖 **AC 门禁**；6 卡中 5 张的其余历史缺陷（见 §4）不在范围内。
