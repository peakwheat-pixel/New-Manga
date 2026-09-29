# Integration record：M2-AC5-BUILD-FRESH-CHECKOUT

- 集成方：Codex（代行，ZCode 编排会话，用户全权授权 2026-09-28/30）；集成日期 2026-09-30
- base=`251f7425`（release）→ claim `5d892bc1` → 实现 `d3ce2190` → 交付 `e2aa8d07` → r2 证据返修 `ed8a6ea6`
- Review 链（DSH 非作者静态；报告按被审 head 归档 doc/reviews/）：r1 `approved_with_conditions`（AC1-AC5 全 PASS 附条件：P2-1 tip 绑定/P2-2 原样日志/P2-3 热态实验/P3-3 负控/P3-6 build）→ r2 证据返修（`ed8a6ea6`，纯证据层实现 blob 零改动）→ r2 定点复审 `approved_with_conditions`（五条件全 CLOSED；唯一新 P2-1=机制句措辞与 pinned 源码相抵，doc-only）
- 关键实验（r2-05，集成采信）：热 target 下改名 core-sidecar → cargo check 触发 `missing sidecar bundle` 指引（不 touch 对照即触发）；真实机制（集成方按 r2 P2-1 改正）：bundle resource 被 tauri-build 无条件发射 rerun-if-changed + cargo「watched 路径缺失 ⇒ 恒 dirty」规则 → 确定性触发，比作者原 churn 解释更稳；上游改变资源 watch 行为时热态静默通过为理论边界（观察项）
- 集成验证：worktree 复跑 cargo test 44 passed EXIT=0；merge=`1a96f536`（parents `251f7425`+`ed8a6ea6`，无冲突）；post-merge main head 复跑 44 passed EXIT=0
- 集成收口落字：P2-1 机制句改正（Task+Handoff）、P3-2 README 命令修正 + frontend/dist 前置注、P3-4 区间审计日志（raw/final-scope-audit.log：251f7425..ed8a6ea6 仅 build.rs/ps1/README/Task/Handoff/verification/**，DIFFCHECK_EXIT=0）
- 集成裁决：AC1-AC5 按 DSH r1 逐项裁定 PASS（附条件已闭合）；Task 转 `done`
- 遗留移交（planning 候选）：①P3-1 build.rs `!is_dir()` 措辞（路径为文件时报错语义）——一行代码候选；②frontend/dist 缺失的模糊报错未覆盖（观察项）；③短路不校验产物完整性（Task 已登记）；④clippy 6 基线既有 error（Goal 候选池）
