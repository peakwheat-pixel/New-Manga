请对 P02 AppContainer contract r7 与 Phase A manifest r3 做一次只读、非作者内容 Review。你是 DeepSeek Harness reviewer，不是 Owner，也不负责 Gate 放行。

## 固定审查对象（SHA 由 Codex 在调用前计算；你不需要也不得复算）
- Live Task：`G:\CODEX\New Manga\doc\tasks\P02.md`，声称 SHA-256=`AC200DA1D9565BD612420C0518752D4CCCDFB32FA62C85CDD01449BDCE81FF72`
- Contract：`G:\CODEX\New Manga\verification\P02\appcontainer-isolation-contract-r7.md`，声称 SHA-256=`7FBFFE6583511CBF5348539D1D8A2C4174000D93950FD54DBCDFBBC5B6C90ADF`
- Phase A manifest：`G:\CODEX\New Manga\verification\P02\appcontainer-readonly-preflight-r3.md`，声称 SHA-256=`AC45329A58BFFA3AF6984E02207E1AF4AD54E46644DFEEC25B50869E26C4BC43`
- 前轮 Review：r6 DSH report `verification/P02/dsh-appcontainer-contract-r6-review.stdout.md`，SHA-256=`D8821DF6D93AE47FA650C88FFB90516027F0310BAED6874ABB6210E7A49CAC96`
- Codex r6 adjudication：`verification/P02/codex-appcontainer-contract-r6-adjudication.md`，声称 SHA-256=`103CBD5FBBDDBFF478F823355932A44AD1D0F02897746D328DBECE4BAA983759`
- Source history for count verification: `verification/P02/appcontainer-readonly-preflight-r2.md` and `verification/P02/appcontainer-isolation-contract-r6.md`.

## Review objectives
1. 逐条核对 DSH-R6A-01..12 的处置是否实际体现在 r7 contract/r3 manifest；不假定 Codex adjudication 自证正确。
2. 特别核验 Phase A 环境变量集合：R6 report / 其建议称“24 项”，但 r2 manifest 原文可能实际只列 23 项。请直接逐项数源文件的具名变量，并判断 r3 是否准确保留原集合、明确“完整集合”、将 r7 §6 未列变量留为 `NOT_RUN / Phase B`，且未为凑数扩展读取范围。
3. 检查 WER T0/T1 是否明确为同一测量进程、T0 在任何 Phase A read 前、T1 在全部 read 后进程退出前，并在两次均覆盖同一 5 个对象（2 个精确键 + 3 个目录）。
4. 检查 environment 类别/隐私处理、TRITON_CACHE_DIR、未列变量/路径/字段、悬空 §4.5、scratch ACL/label mutation 当前 NOT_APPROVED 状态、Phase A root metadata 不含子项/内容 inventory、scratch 相对路径基准、四个 scratch roots、exclusion manifest Phase B-only、不得打开或哈希任何文件等条目是否完整、一致、可执行。
5. 检查 Phase A 是否仍为候选而非已冻结/已运行；是否完整阻止 profile/private-registry API、ACL/registry/label mutation、写 probe、工具链/build、Sandbox；是否保持 `private_registry_absence=UNPROVABLE / BLOCKED`、`profile=NOT_CREATED`、`OS isolation preflight=NOT_RUN`、`Build Gate=BLOCKED`、`Hard Build Barrier=EFFECTIVE`、`AC1–AC7=BLOCKED / NOT_RUN`。
6. 检查 Contract、manifest、Task 之间路径、版本、数量、Gate、授权和状态是否一致；列出任何潜在歧义或越界。

## 约束与输出
- 只读查看上述确切文档。不得使用 shell、PowerShell、Git、hash、Windows API 或外部网络；不得修改/创建/暂存/删除任何文件；不得运行任何 OS measurement、profile API、ACL/registry操作、probe、构建、测试、Cargo/Rust/Tauri 或 Windows Sandbox。
- 只给**内容层**结论；正式 `object_binding=NOT_VERIFIED`，不声称独立核验 SHA、Git objects、worktree、输出文件或任何 OS 状态。
- 用简体中文输出结构化 Review：内容 Decision（APPROVED / APPROVED_WITH_CONDITIONS / CHANGES_REQUESTED）、P0/P1/P2/P3 计数、DSH-R6A-01..12 每项 CLOSED/OPEN 与证据行号、任何新 finding（分级/精确文件行/最小修正）、数量差异的实数核验、当前 Gate 与 Review 不构成的授权边界。
- 任一 P0/P1/P2 open finding 必须阻止 Phase A。P3 逐项标明阻断性和是否影响安全或范围。
