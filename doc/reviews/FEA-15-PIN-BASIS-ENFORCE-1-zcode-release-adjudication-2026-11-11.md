---
task_id: FEA-15-PIN-BASIS-ENFORCE-1
adjudicator: ZCode 独立只读 Integrator
session_id: sess_7b34d23e-ddaf-4ec5-bbb3-964edd74fc58
decision_turn_id: turn_6003c9f3-2448-4fe1-b382-871356eaaa11
base_commit: 2df8db7a4d19b591e919ecc6e8f8651167800ef0
decision: RELEASE_WITH_BASELINE_PREREQUISITE
---

# ZCode 释放裁决：显式 evidence SHA 基准

2026-11-11，独立 ZCode 会话释放 governance v3 Task `FEA-15-PIN-BASIS-ENFORCE-1`，Owner codex，依赖已完成的 `FEA-15-PIN-POLICY-1`；Review 和最终裁决分别使用未参与实现且彼此不同的独立 ZCode 会话。CLI EXIT 0；本记录由 Codex 按会话回复整理。后续两个 Addendum 分别细化当前全集刷新和冻结脚本的安全调用。

目标：新 Canonical Evidence 表在 `class` 后增加 `sha256_basis`，值域严格为 `BLOB`、`WORKTREE`、`EXTERNAL_SHA256`。新七列表逐行必填并按选择的字节源校验：BLOB 要求 commit 包含路径且精确 hash；WORKTREE 仅按声明工作区字节并说明复现环境；EXTERNAL_SHA256 指仓外来源，不可读取不得 PASS。旧六列表继续现有 r194 工作区或 BLOB 匹配语义，不迁移历史 pin。本 Task 自身继续使用六列表作为兼容样本。

允许修改：本 Task 卡/Review/Handoff、`doc/templates/TASK.md` 的 evidence 列及说明、`tools/governance/check.ps1` 的七列表识别与 basis 验证、`tools/governance/tests/**`、STATUS/Plan/Ledger 指针和 `verification/FEA-15-PIN-BASIS-ENFORCE-1/**`。实现与 dry-run 在 `G:/CODEX/New Manga.workspace/FEA-15-PIN-BASIS-ENFORCE-1/` 的隔离基线与候选副本；main 承载任务文档和经批准的集成。

禁止修改 18 frozen pins/`verify_pins.ps1`、历史 Task/Review/Handoff/checkpoint/evidence/pin 字节、`.gitattributes`、任何 renormalize 或其 dry-run、冻结契约/Schema/API/产品源码/依赖、`task_ledger.py`；禁止资源清理、gc/prune/repack、push 和提权。若确需禁止范围，停止并另行裁决。旧 inventory 的 5,376 行是历史测量快照，不是当前全集的预设值。

验收：AC1 在实施前固定真实基线、代表样本、环境与 checker 实跑，并依 Addendum 完成增量归因和独立基线确认；AC2 实现模板和新旧表判别；AC3 覆盖旧格式、新 basis 缺失/非法/三类来源、PNG、CRLF 与 mixed-EOL；AC4 在 Windows autocrlf true/false fresh checkout 对比，旧行无未解释变化、增量单列，Linux 为 NOT_RUN；AC5 集成后 default、本卡及两个 prior TaskPath、18 pins、API、Handoff/独立 Review/终裁。任何新旧格式不可区分、未解释历史变化、外部或 EOL 行为异常、需改历史/属性/契约时停止。

R-001 不因实现自动关闭，须由最终 Integrator 据证据明确裁定。仓内新证据 BLOB pin 指向包含文件的实际 commit；仓外资源保留并按清单核验，不清理。
