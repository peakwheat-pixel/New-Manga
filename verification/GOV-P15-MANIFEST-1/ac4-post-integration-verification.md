# 集成后验证 — GOV-P15-MANIFEST-1

**依据**: Codex r24 §1「集成后验证与 Plan 文本」
**执行**: 2026-10-20，主 checkout `antigravity/P09-AC3-DELETE-HARDEN-1`

## 一、r24 要求验证什么

r24 §1 原文：

> 验证建议至少包括：核对 `2f9d549d5` 的祖先包含关系和本 Task 允许 diff；
> 运行 Task-scoped 与全局 `tools/governance/check.ps1`；单独核对 P15：
> manifest 缺失错误确已消失，预期仅余 `SettingsPage.test.tsx` 的既有时间性 pin 失配。

## 二、五项验证结果

### 1. approved source head 的祖先包含关系

```
git merge-base --is-ancestor 2f9d549d5 HEAD
2f9d549d5 is ancestor of 7b1cb6a78 : YES
```

**通过。** r3 Review 批准的 `2f9d549d5` 确实是当前 HEAD 的祖先。

### 2. 交付之后的允许 diff

`2f9d549d5..HEAD` 触及 **6 个路径**：

| 路径 | 性质 |
|---|---|
| `doc/tasks/GOV-P15-MANIFEST-1.md` | 本 Task 自身记录 |
| `doc/REBASELINE_PLAN.md` | Plan 行 |
| `doc/reviews/GOV-P15-MANIFEST-1-*-antigravity-r{1,2,3}.md` | 三份 Review 落盘 |
| `verification/P09-GOVERNANCE-DEBT-20261019/codex-closeout-p15man-r23.md` | Codex 裁定落盘 |

**没有任何** `src/`、`apps/`、`tests/`、`tools/` 或 `verification/P15/` 的路径。
**通过。**

### 3. 是否存在 merge

```
merge commits after delivery: 0 (expected 0)
```

**通过。** 确认为原地集成，无 merge、无 cherry-pick。

### 4. 检查器

| 范围 | 结果 |
|---|---|
| `-TaskPath doc/tasks/GOV-P15-MANIFEST-1.md` | **PASS**（1 warning: STATUS 预算） |
| 全局 | **PASS**（1 warning: 同上） |

**通过。**

### 5. P15 单独核对

```
errors: 1
 FAIL: Evidence SHA-256 不匹配：apps/desktop/frontend/src/settings/SettingsPage.test.tsx
'Resource manifest 不存在' eliminated: YES
```

| 项 | 期望 | 实际 |
|---|---|---|
| `Resource manifest 不存在` 已消除 | **是** | **YES** |
| 剩余错误数 | 1 | **1** |
| 剩余错误类型 | `SettingsPage.test.tsx` 时间性 pin 失配 | **一致** |

**通过。** 该错误是本 Session 已定性的「时间性失配」——后续提交 `528c6289c` 修改过
该文件，pin 指向的是交付当时的字节事实。归属 `GOV-PIN-LINEAGE-1`。

## 三、总判定

```
VERDICT: PASS - integration verified, may record integration_commit
```

## 四、因此按 r24 §1 记录 integration_commit

r24 §1 的原地集成口径：

> 完成验证后，填验证完成时的真实完整 HEAD，并在 Closeout 写明没有 merge/cherry-pick、
> approved source 已在受控目标祖先链、验证命令/结果/时间及 HEAD。
> 若验证中产生新提交，记验证后实际 HEAD。

本次验证**未产生新提交**，故 `integration_commit` 填验证时的 HEAD `7b1cb6a78`。

**这不是占位值**：它是「验证完成时的真实 HEAD」，且验证结果全部记录在上文。

## 五、可复跑

```powershell
cd "G:\CODEX\New Manga"
git merge-base --is-ancestor 2f9d549d5 HEAD; echo "ancestor: $?"
git diff --name-only 2f9d549d5..HEAD
git log --format="%h %p" 2f9d549d5..HEAD
python C:\Users\49745\AppData\Local\Temp\verify-integration-p15man.py
```
