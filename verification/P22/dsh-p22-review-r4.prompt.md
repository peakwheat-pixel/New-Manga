你是 DeepSeek Harness 的独立 Reviewer，请对 P22 Owner R4 Handoff 做一次只读、内容层复审。

## 固定审查对象
- Handoff：`G:\CODEX\New Manga.worktrees\P22-roundtrip-serialization-antigravity\verification\P22\antigravity-owner-p22.handoff.md`
- 声称 SHA-256：`C23B510BB3D70CED666A94FCA1DB904407ABDFDAA9D0C9C2C938604377D10262`（仅供文本对象 pin，不代表你验证过该 SHA）
- P22 Task：`G:\CODEX\New Manga\doc\tasks\P22.md`
- 声称 Task SHA-256：`7EBD7D40E7334C9422F4BF126A29B3D0F49300E2BDBAC86CEDFDB1ED74EE98C9`（仅供文本对象 pin，不代表你验证过该 SHA）
- R3 Review 报告：`G:\CODEX\New Manga.worktrees\P22-roundtrip-serialization-antigravity\verification\P22\dsh-p22-review-r3.stdout.md`
- Codex R3 adjudication：`G:\CODEX\New Manga\verification\P22\codex-r3-review-adjudication.md`
- R2 Review evidence：`dsh-p22-review-r2-attempt2.stdout.md`、`dsh-p22-review-r2-followup.stdout.md`
- R4 delivery claim：HEAD=`0e46ec7e8c23a1fc0ba793745f5101813b388ea3`，tree=`fb84f616886c73e645eb94eb451dcb46a11fb54b`，parent=`3038fe03ba57b42cf5039402b333fbf4b8efbc05`；Owner reports only the Handoff changed.

## 上轮 open findings，逐项核验
1. P2-1：清晰区分累计 `base(faea1a2c)..R2` 的 3 条路径（sidecar 由 R1 引入）与 R2 增量 `parent(R1=680e3830)..R2` 的 2 条路径；§3、§6 与给 Codex 的 forwardable instruction 均须保持这一区分，不能将累计 3 条命名为 R2 实际变更。
2. P3-1：准确表述 Antigravity 获授权且实际运行的 diff-check 范围；无 raw output 时明确未保存；不得把 Owner 未执行/未留证的 Codex 范围说成 Owner 核验。
3. P3-2：状态须表达 Owner 修订已提交、仍待独立 Review 与 Codex adjudication；不得声称新交付已收口、已审或已集成。
4. P3-3：R2 两轮 DSH 内容 Review 都保留 `object_binding=NOT_VERIFIED`；初次 CLI exit=`1`、follow-up exit=`0`；内容 Review 和 Git object/runtime 验证必须分开。

## 整体复审范围
- 通读 Handoff 与 live P22 Task，检查新增文字是否准确、前后一致，是否无意声称产品运行时 AC、集成或 Gate 已通过。
- 复核 P02 Build Gate/Hard Build Barrier 仍阻止 Cargo/Rust/Tauri/sidecar/runtime AC2；Handoff 不应建议提前集成或运行。
- 检查是否存在新的 P0/P1/P2/P3 内容问题；若有，给出精确小节/行号和最小修复方案。

## 严格限制与报告格式
- 只读查看所列文档和被引用的 P22 R2/R3 Review 文本。不得调用 shell、PowerShell、Git、hash、Windows API，不得运行测试、Cargo、build、sidecar 或 Sandbox，不得创建、修改、暂存或删除文件。
- 由于不运行 Git/hash，正式 `object_binding=NOT_VERIFIED`；只给内容层结论，不得声称已独立核验 commit/tree/parent、路径集、diff-check 退出码或工作区 cleanliness。
- 用简体中文报告：固定对象声称、所读文件、内容决策（APPROVED / APPROVED_WITH_CONDITIONS / CHANGES_REQUESTED）、P0/P1/P2/P3 数量、四项 finding 的 CLOSED/OPEN 逐项状态、其他发现、未验证限制、是否存在运行时/Gate误述。
