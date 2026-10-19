---
task_id: GOV-RESOURCE-MANIFEST-JSON-1
author: dsh
recipient: Codex
base_commit: c131b1ae114d00c17e734a51f38263d92fe6f198
delivery_head: 7d09143d6df73d6c12a9769beaf19cfd70cc313c
status: ready_for_review
revision: 2
---

# Handoff（第 2 版）：GOV-RESOURCE-MANIFEST-JSON-1

## 为什么是第 2 版

第 1 版（delivery_head `5ee07c258`）被 Antigravity 判为 **NOT APPROVED**，三个 P1 都是真的。
本版针对这三条修复，并把 `delivery_head` 前移到 `7d09143d6`。

## 第 1 版 Review 的三个 P1 与修复

### P1-1 `ALREADY_ABSENT` 绝对路径检查失效（安全缺陷）

**原缺陷**：用裸 `Join-Path` 拼路径，绝对路径会被粘在仓库根后面。实测：

```
Join-Path "G:\...\GOV-RESOURCE-MANIFEST-JSON-1" "C:/Windows/System32/notepad.exe"
-> G:\...\GOV-RESOURCE-MANIFEST-JSON-1\C:\Windows\System32\notepad.exe
-> Test-Path: False      （而该文件确实存在）
```

后果：任何绝对路径目标一律被判定为「不存在」，**伪造消失可完全逃逸**。

**修复**：改用 `Resolve-LocalPath`（只在路径非 rooted 时前缀仓库根）。
**回归用例 17**：`ALREADY_ABSENT` 指向真实存在的 `C:/Windows/System32/notepad.exe` → 必须 FAIL。

### P1-2 schema 拒绝仓库里唯一一份真实清单

**原缺陷**：Draft-7 校验 `P19-UI-FIX-1/resource-manifest.json` 有 8 处失败——
`additionalProperties: false` 禁掉了 worktree 上合法的 `branch` / `base_commit` / `delivery_head`；
且强制 `PRESERVE_*` 必须带 `sha256` 或 `manifest_path`，而 7 个真实资源一个都没有。

**修复**：容忍额外元数据、完整性字段改为可选、结构要求保留。
**现在 Draft-7 校验该 JSON 为 0 错误。**

### P1-3 离线测试写入真实 `doc/tasks/`

**原缺陷**：违反 r7 §2.4「绝不能把 fixture Task 放入主仓真实 `doc/tasks/`」。

**修复**：先验证了 `-TaskPath` 接受仓库外路径（检查器照样正常工作），
于是 fixture Task 移到系统临时目录，只有被引用的 manifest 留在 `verification/` 下、每例删建。
runner 现在**断言 `doc/tasks/` 未被触碰**，泄漏则报错并清理。

### 顺带补的两个 P2

- 用例 18：引用中含 glob（`` `verification/@TID@/*.json` ``）→ 应拒绝；
- 用例 19：非法 JSON → 应被捕获而非崩溃。

## 当前验证结果

| AC/场景 | 命令 | 结果 |
|---|---|---|
| 离线套件 | `python tools/governance/tests/run-resource-manifest-cases.py` | **19/19，exit 0** |
| 隔离 | 同上（runner 自报） | `tempdir=True manifest=True doc/tasks untouched=True` |
| 真实树治理 | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (1 warnings)** |
| schema vs 真实 JSON | Draft-7 校验 | **0 errors** |
| 检查器语法 | `[Parser]::ParseFile` | parsed OK |

提交链：`4b6308a7f` → `eab5531b0` → `7da0d9a07` → `7350da5e9` → `5ee07c258` → `2ddb0963a` → **`7d09143d6`**。

## 仍然成立的那处「放宽」（请复核是否被 P1-2 的修复影响）

`closeout_counts` 与 `resources` 布尔不一致时只记 `WARN`、不判 `FAIL`，因为
`P19-UI-FIX-1` 声明 `moved=6` 而 7 个资源全是 `moved=false`——两个口径不同，不是数据错误。
Codex r8 已裁定接受（选项 D/A），条件是 note 必须真的输出。note 已接到 `Add-Warning` 并实测可见。

**P1-2 的修复没有动这条规则**，只动了 schema 的字段宽松度与完整性字段可选性。

## 明确未做

- 未修改 `verification/P19-UI-FIX-1/resource-manifest.json`。
- 未生成「解析视图」文件（Codex r8 §3.3 倾向不生成）。
- 未修改任何其它 Task、Plan 条目或资源；未重钉任何 pin。

## 接收方式

Reviewer：**Antigravity**，针对固定 `delivery_head = 7d09143d6df73d6c12a9769beaf19cfd70cc313c`。
请逐条复核上述三个 P1 是「已修复 / 未修复」，再给总体结论。
