# P19-UI-MANIFEST-VIEW-1 裁定（r11）

日期：2026-10-19  
裁定人：Codex（用户明确请求本次裁定）  
事实基线：worktree `G:/CODEX/New Manga/.agents/worktrees/P19-UI-MANIFEST-VIEW-1`，branch `P19-UI-MANIFEST-VIEW-1`，HEAD `4543e23a0`；主 checkout `G:/CODEX/New Manga`。本裁定不修改 Task、Plan、STATUS、检查器或清单；仅供后续按授权完成 closeout。

## 2.1 本 Task 结论

1. **AC1、AC2 达成；AC3 未达成。** 精确证据记录了正文引用修正、原处置散文事实保留、源 JSON SHA-256 前后一致；检查器不再报 `Resource Manifest 引用必须位于 verification/**`，解析目标为指定 JSON。可是 AC3 明确要求变更后恰有三项已知错误且无新增错误；实际为十项，因此该 AC 必须记 `FAIL`，不得改写为 PASS 或称本 Task 完全通过。
2. **4→10 不能作为清洁化结果接受，但不回退引用。** 这是新可达的清单检查发现了原先被引用格式挡住的资源目的地问题，并包含一项本 worktree 与主 checkout 的 `verification/P19/import-no-response-r4.md` SHA 换行差异；现有证据没有表明此次正文修改改写了这些数据。回退虽会让计数回到 4，却会重新引入已修复的引用错误、隐藏清单检查结果，并使 AC1/AC2 失败。保留修正，将净错误增加和各错误原文作为限制披露。
3. **终态裁定：`closed_with_limitations`，不是 `done`。** 本次用户明确要求 Codex 对该限制作终局裁定；AC3 仍按原状态记录为 FAIL，理由为已集成检查器在成功解析外部清单后暴露既有的目的地表示/存在性债务，另有 worktree 环境差异。不得据此声称 P19 检查 PASS，也不恢复本 Task 的实现。`canonical_evidence_status` 仅在 AC1/AC2 及未通过 AC 的 closure evidence 均可复核、索引完整后设 `complete`；`resource_closeout_status` 仅在按 §4.2 完成资源逐项盘点后设 `complete`。所有资源保留，删除/迁移/归档均记实际数量（本 Task 未授权任何此类操作，预期均为 0）。关闭记录须列出 AC1/AC2 `PASS`、AC3 `FAIL`、AC4/AC5 的保护证据及 AC6 的实际交付/审查状态；不可把终态或证据齐全等同技术通过。

**回退裁定：不回退。** 保留 `doc/tasks/P19-UI-FIX-1.md` 的仓库相对清单引用；禁止为消除检查输出而改源 JSON、P19 历史证据、pins 或检查器。

## 2.2 六项目的地错误的归属

“Same …” 是位置关系描述/同源指针，不是可直接传给 `Test-Path` 的路径；对它调用 `Resolve-LocalPath` 后检查散文路径必然失败。具体六项中有 **五项** 是该类标记：`Same ignored target/dist locations in this worktree`、`Same source location`、`Same shared build environment`、`Same local cache location`、`Same main-repository paths`。第六项 `apps/desktop/src-tauri/target/p19-ui-fix-1-isolation-20261017` 是路径形状的目的地，但报告为当前不存在；它不是“Same …”指针，不能被同源规则静默豁免，应保留为独立的待核实/真实路径问题。

裁定选择 **A（限缩实施）**：另立检查器能力 Task，给外部 JSON Manifest 中明确、白名单化的 `Same …` 目的地定义同源语义。建议语义为将标记视作 `source_path` 的位置关系、不把标记文本本身当路径，并输出可审计 note；不得据 note 宣称不同目的地已存在。只覆盖证据中这类明确 sentinel；空值、`-`、其他自然语言按当前规则处理，不顺带放宽。保留 `target/...isolation...` 的路径存在性检查，直到其存在性有证据或其自身记录被独立裁定。

建议后继 Task：`GOV-RESOURCE-MANIFEST-SAME-LOCATION-1`，kind 为 governance/checker，Owner 建议 Antigravity、Reviewer 建议 DeepSeek Harness。冻结范围时至少包括：

- `tools/governance/check.ps1`：只扩展外部 JSON Resource Manifest 对显式同源 sentinel 的解释，并产出说明性 note；不改 P19 清单或历史表格路径规则。
- `tools/governance/tests/run-resource-manifest-cases.py` 与对应 fixtures：覆盖已知 sentinel、普通有效目的地、缺失的真实路径仍报错、空值/`-` 不被意外豁免。
- 不改 `verification/P19-UI-FIX-1/resource-manifest.json`、P19 Task/evidence/pins、其他 Task、schema/依赖或清理任何资源；若实现需要扩大这些边界，先由 Codex 另行裁定。
- 新 Task 的验收须证明 sentinel 不再触发“最终路径未验证”、note 保留同源关系、普通不存在路径仍失败，并运行既有 Resource Manifest 用例及指定治理检查；不能把仍缺失的隔离副本路径记为通过。

## 2.3 与 GOV-RESOURCE-MANIFEST-JSON-1 的关系

这是 **新的独立能力，不是要求 reopen `GOV-RESOURCE-MANIFEST-JSON-1` 的缺口**。已集成任务提供外部 JSON 解析、schema 校验和沿用目的地路径存在性检查；现有契约/Task 范围没有定义 `destination_path` 中自然语言同源标记的语义。让完成的任务回头承接新 sentinel 行为会混淆已 Review、已集成的范围。保持该 Task `done`，以后继 Task 扩展其消费者行为；依赖顺序为先有 `GOV-RESOURCE-MANIFEST-JSON-1`（已集成），再释放同源语义 Task。新 Task 不依赖或重开 `P19-UI-MANIFEST-VIEW-1`；P19 closeout 只记录发现和后续 Task 引用。

## DSH 收尾本 Task 的顺序

1. **保留变更，不做回退或扩围。** 不改 P19 JSON、`tools/**`、P19 历史日志、evidence pin 或资源；确认引用正文仍是 `verification/P19-UI-FIX-1/resource-manifest.json`，源 JSON hash 仍为 `b0772d93ab8ed9182497a43e0761f0d4ccc5560768f806ba86eb8048905c4dc2`。
2. **核齐现有证据。** 在本 Task 已授权的 evidence 目录内记录命令完整 stdout/stderr、退出码、十项错误的逐项结果，以及 4→10 对照；明确标注两项日志 SHA 不匹配、worktree 中 `import-no-response-r4.md` 的环境差异、8 个未登记文件合并项、五项同源 sentinel 和一项缺失路径。不得把 AC3 的预期三项改写成实际结果。复核单节 diff、原散文事实和源 JSON 未变。
3. **更新交付与请求独立 Review。** DSH 在获准的 Task/evidence/Handoff 路径内固定本次 delivery head，Handoff 逐项陈述 AC1/AC2 通过、AC3 失败及本裁定的“不回退/有限关闭”结论；随后由非作者 Antigravity 针对精确 head 复核改动边界、实际错误清单、源数据保护和限制表述。Review 不得把 AC3 判成通过。
4. **Codex closeout。** 审阅 Handoff/Review 与实际差异，完成 Resource Manifest 资源盘点及 closure evidence；按协作协议更新 Task 生命周期/关闭记录、权威指针和 Plan/STATUS，并运行适用的只读治理检查。将 Task 置 `closed_with_limitations`，保留 AC3 `FAIL` 与全部十项观察，不设 `done`。不得删除或移动该 Task 的 worktree/资源来追求 clean。
5. **后继任务另行释放。** Codex 在该 Task closeout 后创建并冻结 `GOV-RESOURCE-MANIFEST-SAME-LOCATION-1` Task，核实依赖和允许路径，随后才更新 Plan DAG/状态并释放 Antigravity；本裁定本身不授权其实施。

Plan 中本 Task 的终态行建议为：

```markdown
|P19-UI-MANIFEST-VIEW-1|GOV-RESOURCE-MANIFEST-JSON-1|closed_with_limitations（AC1/AC2 达成；AC3 因 4→10 错误清单不满足，按 Codex r11 保留修正并披露）|
```

从 READY 声明中移除此 Task；当前 `READY 节点：ARCH-DOC-REBASELINE、P20` 保持不变，`done` 计数不增加。**后继 Task 的 Plan 行只在 Codex 同时创建 Task 文件、确认范围和依赖后加入**；建议届时使用：

```markdown
|GOV-RESOURCE-MANIFEST-SAME-LOCATION-1|GOV-RESOURCE-MANIFEST-JSON-1|proposed（外部 Resource Manifest 显式 Same-location sentinel 语义；不改源 JSON）|
```

以上 Plan 行是 closeout/后续释放时的精确建议，不代表本文件写入时已经更改权威 Plan 或 STATUS。
