<!-- codex session: 01a1525f-27f3-7090-8773-a64e94baf6d7 | reviewed_head: 0fc6e57a7 -->

# R8 Review

**reviewed_head:** `0fc6e57a7520222f2036ddf463831c45d80b89db`  
**decision:** `CHANGES_REQUESTED` · **new findings:** 4  
**是否可关闭：否。** P09 AC3 delete 子条件仍为 `BLOCKED`。

## R7 findings

- **P1 — AC4 预览残留：通过转交解决，未修复。** [P09-PREVIEW-LIFECYCLE-RECLAIM-1.md](/G:/CODEX/New%20Manga/doc/tasks/P09-PREVIEW-LIFECYCLE-RECLAIM-1.md:21) 记录了残留的 5 行和 5 个 PNG、根因及待裁决问题；HARDEN-1 收口段明确判 `FAIL` 并转交。但主 Task 仍把 AC4 勾为完成，见新 finding 1。
- **P2 #2 — 查询前删除映射：通过转交解决，未修复。** 后继 Task 记录了“先删 `media_artifacts`、后清理”导致映射不可查，也说明前置快照仍不能判定行是否在用；HARDEN-1 收口段没有声称已修复。
- **P2 #3 — `handle_resolver` 范围：后继 Task 已纳入。** [P09-MANAGED-READ-ROOT-TRUST-1.md](/G:/CODEX/New%20Manga/doc/tasks/P09-MANAGED-READ-ROOT-TRUST-1.md:19) 的 scope 列出 8 处，包含 `handle_resolver`；AC3 也要求逐处覆盖。但主 Task 仍留有“7 处”的旧摘要，见新 finding 3。
- **P2 #4 — `delivery_head`：已解决。** Task 固定为 `1878f0b126e8a0e2603570f9b2009d8b70a259f1`，该 commit 可从当前 `HEAD` 到达。R7 reviewed head `2ba73a5e3df01346543cebc04bb90f4db23077fb` 到 delivery head 之间 `src`、`tests` 无差异；delivery head 包含 `unlink_by_handle` 及其删除路径接线。要求的探针与测试也在该 head 导出副本上通过。

## 新 findings

1. **P2 — AC4 被旧验收项标成已完成。** [Task 第 43、77 行](/G:/CODEX/New%20Manga/doc/tasks/P09-AC3-DELETE-HARDEN-1.md:43) 将 AC4 勾为完成并列为 `PASS`，但该测试只证明 origin 绑定；第 299 行又明确 AC4 `FAIL`、转交。按两个段落对照即可复现矛盾。最终收口段没有宣称残留已修复，但 Task 全文仍会给出已修复的印象。
2. **P2 — Handoff 的收口建议未按路线 B 更新。** [HANDOFF.md 第 8、95 行](/G:/CODEX/New%20Manga/verification/P09-AC3-DELETE-HARDEN-1/HANDOFF.md:8) 仍写着因 AC4 未通过而“不建议置为 done”，且后继 Task 仍写“建议新建”；实际后继 Task 已存在，用户裁决是 AC4 转出、本 Task 在删除路径范围内收口。对照 Task 第 297–301 行即可复现。
3. **P3 — 读取路径数量仍写 7。** [Task 第 262、289 行](/G:/CODEX/New%20Manga/doc/tasks/P09-AC3-DELETE-HARDEN-1.md:289) 仍称转交 7 处，与后继 Task 的 8 处 scope/AC3 不一致。
4. **P3 — Handoff 探针总数不符。** [HANDOFF.md 第 49–61 行](/G:/CODEX/New%20Manga/verification/P09-AC3-DELETE-HARDEN-1/HANDOFF.md:49) 标题说 8 个，表中实际列出 9 个。

## 验证结果

所有探针均在 `%TEMP%` 导出的 `delivery_head` 副本中运行；仓库保持只读。

| 探针 | `injection_fired` | `outside_survived` | 结果 |
|---|---:|---:|---|
| `r5b-p1-remove-managed-race-probe.py` | `True` | `True` | `SAFE` |
| `r5b-p1-collect-orphans-race-probe.py` | `True` | `True` | `SAFE`，移除数为 0 |
| `r6-p1a-publish-cleanup-race-probe.py` | `True` | `True` | `SAFE` |

- `python -m pytest tests/storage -q`：**86 passed**
- `python -m pytest tests/core -q`：**558 passed，1 warning**
- 跳过其余六个探针：`n002-race-probe.py`、`n002-race-probe2.py`、`n004-ancestor-probe.py`、`n004-production-order-probe.py`、`r5-p1-managed-remove-probe.py`、`r5-p1-cleanup-book-files-probe.py`。

`STATUS.md` 为 3167 字节；其中当前 Task 仍是 R8 `in_review`，并记载删除路径收口、AC4 判 FAIL 转出及 P09 AC3 `BLOCKED`，与 Task 当前状态相符。矛盾在 Handoff 的收口建议与路线 B 裁决之间。

**让结论变为 yes 的最小一步：**提交一次文档收口修订，统一 AC4 状态、Handoff 收口建议和后继任务措辞，并更正 7/8 处及 8/9 个探针的计数；保持 P09 AC3 delete 子条件为 `BLOCKED`。