# DOC 类 blocked 闭合（第 1 批）— 证据

Task：`AC-DOC-CLOSE-1`（Owner：DSH）｜基线 `d99c1fba3`

## 1. `V11R-C-RESEARCH-1` AC5 → `verified`

**验收要求**：「不修改任何生产代码；不引入依赖」。

**核验方法**：该卡 frontmatter 有 `base_commit: c73239999` 与 `delivery_head: ba59a6c0d`。
用 `git show --stat ba59a6c0d` 直接看该提交改了什么：

```
doc/design/theming/RESEARCH_V1.md   | 108 ++++
doc/plan/V11R_SCREEN_SPECS.md       | 102 ++++
doc/tasks/V11R-B-1.md … V11R-C-3.md | 49 × 9
10 files changed, 602 insertions(+)
```

**结论**：10 个文件**全部在 `doc/` 下**，`src/`、`apps/`、`tests/` **0 命中**；
未触碰任何依赖清单文件 ⇒ 「不修改任何生产代码」+「不引入依赖」均成立。
日志：`v11r-c-research-ac5-verify.log`。

> 说明：原 `blocked` 理由是「该卡无 commit 字段，无法独立验证」——实际卡面有
> `delivery_head`，只是当时按 `commit` 字段名去找所以漏了。这是「用错字段名导致误判为不可验证」的典型。

## 2. `GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1` AC7 → **保持 `blocked`**（如实归因）

AC7 要求三条命令真实运行并记录 EXIT，且**集成复验后**才 done。2026-11-15 补做：

| 命令 | 结果 | EXIT |
|---|---|---|
| `python -B tools/governance/tests/test_residual_runtime_identity.py` | **Ran 12 tests / FAILED (failures=3)** | **1** |
| `pwsh -NoProfile -File tools/governance/check.ps1` | PASS (3 warnings) | 0 |
| `git diff --check` | （无输出） | 0 |

**三个失败**：

| 测试 | 期望 | 实得 |
|---|---|---|
| `test_all_seven_errors_are_resolved` | `index.errors == []` | 仓库现有 **167** 处声明错误 |
| `test_protection_set_did_not_shrink` | 声明扫描 `errors == 7` | **167** |
| `test_user_data_root_is_now_protected` | `catalog`/`data`/`derived` 命中保护 | 未命中（`[]`） |

**是否本轮引入？否。** 独立扫描 167 处错误的来源（`decl-error-distribution.log`）：

| code | 条数 |
|---|---:|
| `TABLE_SCHEMA_INCOMPLETE` | 53 |
| `DECL_RELATIVE_UNRESOLVED` | 27 |
| `DECL_ENV` | 20 |
| `DECL_GLOB` | 16 |
| `DECL_DESTINATION_UNRESOLVED` | 12 |
| `TABLE_DELIMITER` | 10 |
| `DECL_UNKNOWN_DISPOSITION` | 10 |
| 其它 | 19 |

分布文件全为**历史卡与历史证据**（`FEA-06-RESIDUAL-1/2`、`FEA-07-AC5-NATIVE-1`、`P19`、
`FEA-11-L-*` 系列、`verification/FEA-07-RESIDUAL-3/RESOURCE-MANIFEST.json` 等）；
**本轮新增文件 0 命中**。

**结论**：卡面旧记的「Ran 12 tests / EXIT 0」是 2026 年某时点状态；随仓库增长（638 卡 + 大量证据），
该测试的「全仓声明扫描必须干净」前提已不成立。AC7 **不能改判**，理由已更新为上述实测与归因。

## 3. 不引入新缺陷（AC3）

初次把集成复验日志放在 `verification/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1/integration/`，
触发该卡 `-TaskPath` 的「DONE evidence_dir 含未登记文件」**新错误**。
已把日志移到本卡证据目录 `verification/AC-DOC-CLOSE-1/gov-residual-integration-reverify.log`，
该卡 `-TaskPath` 错误数从 **7 回落至 6**（剩余 6 条均在基线即存在）。

## 4. 新登记技术债（AC4）

**仓库级声明扫描 167 处错误**（见上表）——这是独立的技术债，影响：
- `test_residual_runtime_identity.py` 的 3 个测试；
- 「仓库声明无错误」这一治理前提。

建议后续立卡：`GOV-DECLARATION-SCAN-CLEANUP-1`（清理历史卡的表格 schema / 声明路径 / 环境变量声明）。

## 5. 计数与不回归

```
verify_final.py（AC_BASE=0b517259e）：40/40 卡、260/260 AC、verified 189 / blocked 65 / NA 6
  （改判前 188 / 66）
check.ps1（全局）                → PASS (3 warnings)
verify_pins.ps1                  → PASS (all 18)
generate_api_inventory.py --check → OK (1/80/6=87)
```

## 6. 已知

- `V11R-C-RESEARCH-1` 的 `-TaskPath` 仍有 4 条先存错误（`EVIDENCE_BASIS_HEADER_INVALID`、
  缺 canonical evidence / `integration_commit` / Resource Manifest）——该卡是 lifecycle v2 且历史
  frontmatter 不完整，不在本卡范围。
- `GOV-RESIDUAL` 的 6 条先存错误同样未处理（含 `Evidence commit 不含所 pin 文件`、
  Resource Manifest 路径问题）。
