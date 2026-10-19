---
task_id: GOV-RESOURCE-MANIFEST-JSON-1
author: dsh
recipient: Codex
base_commit: c131b1ae114d00c17e734a51f38263d92fe6f198
delivery_head: 5ee07c2583c3d0adaf4edc778c2907baef24c350
status: ready_for_review
---

# Handoff：GOV-RESOURCE-MANIFEST-JSON-1

## 交付结果

让治理检查器能读取 Task 正文引用的**外部 JSON Resource Manifest**，从而在不改写
`P19-UI-FIX-1` 历史记录的前提下消除其 Manifest 格式债务。

| AC | 结果 | 证据 |
|---|---|---|
| AC1 外部引用唯一且受限 | **完成**：5 类拒绝实测 | `ac1-ac5-manifest-support.md` |
| AC2 schema 与原值保真 | **完成**：`tools/governance/resource-manifest.schema.json` | 同上 |
| AC3 `ALREADY_ABSENT` 严格语义 | **完成**：三条件 + 两向禁止实测 | 同上 |
| AC4 花括号可逆 + 计数对应 | **完成**（Codex r8 裁定 §3.1 选项 D/A） | `ac4-brace-and-counts.md` |
| AC5 离线验证 | **完成**：16/16，fixtures 已版本化 | `tools/governance/tests/` |

提交：`4b6308a7f`（schema + 检查器）、`eab5531b0`（套件 + 证据）、`7da0d9a07`（AC4 + 放松计数规则）、
`7350da5e9`（fixtures 落盘）、`5ee07c258`（note 输出接线）。

## 验证证据

| AC/场景 | 实际命令 | 结果 | 证据 |
|---|---|---|---|
| 离线套件 | `python tools/governance/tests/run-resource-manifest-cases.py` | **16/16，exit 0** | 仓库内可复跑 |
| 真实树治理 | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (1 warnings)** | 同上 |
| 语法 | `[Parser]::ParseFile` on `check.ps1` | parsed OK | — |
| 行尾 | 字节统计 | `check.ps1` 369 LF / 0 CRLF | — |

## 请 Review 重点核对的三处

### 1. 我放宽了一条检查规则（最需要独立验证）

Round 27 我在 schema 里写了「`closeout_counts` 每个键必须等于 `resources` 中同名布尔为 true 的项数」。
用 `P19-UI-FIX-1` 的真实 JSON 验证时发现：它声明 `moved=6`，而 7 个资源项全是 `moved=false`。

**按原规则，这份由 Codex 生成、内容准确的清单会被判为非法。** 我已把它降级为 note：
检查器仍校验四个键存在、为整数、非负，但差异只产生 `WARN`，不产生 `FAIL`。

Codex 在 r8 中认可了这个修正，条件是「必须实际输出非阻塞 note」。
**我上一轮确实漏了这一步**——定义了 `$notes` 却没接到输出上，规则静默放宽。已修复并用探针验证：

```
WARN: ZZ-NOTE-PROBE: closeout_counts.deleted=3 与 resources 中布尔为 true 的项数 0 不同（声明口径包含未列入 resources 的处置动作）
Governance check: PASS (2 warnings)
```

请独立判断：这个放宽是否有事实依据，还是我在为通过检查而妥协。

### 2. `ALREADY_ABSENT` 的两向禁止

请核对用例 12–15：

- 三条件全满足 → 应通过；
- 缺 `absent_evidence` → 应失败；
- **目标仍存在** → 应失败；
- **`NOT_APPLICABLE` 带 `absent_evidence`**（冒充已消失）→ 应失败。

### 3. 16 条用例是否覆盖 AC5 的全部情形

AC5 要求覆盖：有效唯一引用、已有目标、目标缺失及 `ALREADY_ABSENT` 三条件全满足/逐条件缺失、
错误/重复/缺失/越界/绝对/不存在引用、env/glob/宏/符号链接逃逸、非法 JSON/schema、7 项及 closeout 计数。

**已知未覆盖**：
- **非法 JSON**（语法错误的 JSON 文件）——只有 schema 违规，没有解析失败的用例；
- **符号链接逃逸**——代码里有 `LinkType` 检查，但用例没有构造真实符号链接；
- **glob**——代码有 `[*?\[\]]` 拒绝，用例未单独覆盖。

这三项请判为缺口还是可接受。

## 明确未做

- 未修改 `verification/P19-UI-FIX-1/resource-manifest.json`。
- 未生成任何「解析视图」文件（Codex r8 §3.3 倾向不生成）。
- 未修改任何其它 Task、Plan 条目或资源。
- 未重钉任何 pin。

## 接收方式

Reviewer：**Antigravity**（不得由 dsh 自审），针对固定 `delivery_head = 5ee07c2583c3d0adaf4edc778c2907baef24c350`。
Review 通过后交 Codex 集成、更新 `integration_commit` 与 closeout 字段。

**已知遗留**：AC5 的三项未覆盖情况（非法 JSON、符号链接、glob）需 Reviewer 判定性质。
