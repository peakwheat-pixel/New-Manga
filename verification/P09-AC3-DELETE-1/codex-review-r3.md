---
task_id: P09-AC3-DELETE-1
reviewer: Codex
author: Antigravity
base_commit: 41bb13679615af557478b85ad6e0bd217f221666
reviewed_head: a04e4ea78d5b33a0f91efcdc06b396391c4b165e
decision: changes_requested
---

# P09-AC3-DELETE-1 第三轮独立复审

## 复审范围与结论

固定审查区间为 41bb13679615af557478b85ad6e0bd217f221666..a04e4ea78d5b33a0f91efcdc06b396391c4b165e。HEAD 与用户给定值一致。先读取 git diff --stat，结果为 82 files changed、4,846 insertions、739 deletions；随后逐文件核对了本 Task 涉及的前端、Core、SQLite、迁移、Rust bridge、验收脚本、测试与权威文档差异，并直接阅读实现源码。对本报告引用的代码与证据路径，已验证 reviewed_head 中实际包含该路径。

decision 为 changes_requested。R-001、R-002、R-004、R-005、R-006 已闭合；R-003、R-007、R-010 部分闭合；R-008、R-009、R-011、R-012 仍未闭合。另发现四项新的 P1 风险。当前不能批准 Task 收口，也不建议将 P09 AC3 从 BLOCKED 改为 PASS。

本轮没有运行 pytest、npm、Cargo、verify_all.py 或构建，没有创建测试/构建临时产物，也没有启动应用。收尾时进程查询未发现 m2rc1-desktop、core_service、host_bridge 进程。本轮没有修改产品代码、契约、Schema、ACL、依赖或其他文件；未进行 git add、commit、push、reset、clean、stash 或 checkout。

### 磁盘字节 SHA-256

以下为复审期间对磁盘文件实算的 SHA-256。STATUS 与 REBASELINE_PLAN 是 reviewed_head 之后仍有变化的工作区 overlay；只读记录其当前字节，不将其当作 reviewed_head 证据，也未触碰。

| 文件 | SHA-256 |
|---|---|
| doc/tasks/P09-AC3-DELETE-1.md | 5337ad1f21686d5fcf65dedd3d5eb84d36d45482db6067e77826dd08c2c4864b |
| doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md | f954c2fda2fb213120cae33f859928c97c35a6aa73fbea980098af8b0bc01c08 |
| verification/P09-AC3-DELETE-1/codex-review-r1.md | d56f3c7d7cb570f3948ea159f006ddf241046bcec27a04670fa6ca6c47c7705e |
| verification/P09-AC3-DELETE-1/codex-review-r2.md | 753f4adb94fe02448d981c399f56d9718645c9822cd035d8429813be70eb864b |
| verification/P09-AC3-DELETE-1/P09-AC3-DELETE-1-r2fix-delivery.md | 018dde67fdbcb7f591f425cd13f9eef87b289a9fdfba4344e321d261f50eb58b |
| verification/P09-AC3-DELETE-1/P09-AC3-DELETE-1-r2fix.json | 09dd43b866d2397d749b5057dabf6dd9db06f9465c7392ffc7d022a85dcd73f5 |
| src/infrastructure/sqlite/library.py | a96b3a2794935a473a5f0110105a76c21e7121291f1ab80d5a663a4b875bbf4a |
| src/infrastructure/sqlite/schema.py | 531f10c6a30078e4ae8d2743f1a27c998c9e9f22fc3bbd961b1976a0615d509d |
| src/infrastructure/sqlite/migrator.py | 0efe8def4c3c36b3b68605becf0233a6522b10b9fd0e83fe9973e48cf17e3d21 |
| src/infrastructure/sqlite/pipeline.py | d6c18cff8a2fdbf5a746c92791bde61075b70b754aafe868506f7e619311a551 |
| src/infrastructure/resource_channel/render_preview.py | ed77ad3f46403806834ba9ca8c1ee3681c2dfa0f1a9bab114ed94041644e38b3 |
| src/bootstrap/core_service.py | 4e6a46f0aeb662b9c9d7038d384fc0bd5e4b0aea9af3d7ef92827a2e9d359f98 |
| src/application/library/service.py | 0ebcfe3277938935b63103c93be930fec7de2c6f6bbd71b5d09713acbd5c31c7 |
| apps/desktop/frontend/src/library/client.ts | 2b94993b2d777c05d453d8b365bd8581bdd7378cf192b3aa2dc68a167050b06e |
| apps/desktop/frontend/src/bookshelf/BookshelfPage.tsx | 588106b2a1781b11083634c0135f66b3011d295520c26cbc96a30ac82f62a6b7 |
| apps/desktop/frontend/src/recycleBin/RecycleBinPage.tsx | 2cff2e5585794ca526b8d45931204235e1c514792d15fcbcac52f90693419445 |
| apps/desktop/src-tauri/src/main.rs | 63c9984d4a10796004df0848047d2189254309bcc8f9565718cfe6c63e5d4049 |
| apps/desktop/src-tauri/src/library_bridge.rs | 137627011322816e304879e54c66c36549f38affd71eadfd18c90c6e277d39da |
| tests/core/test_core_delete_commands.py | 58b628974d4643746a46f6bdef6adf7679a8780c78649ab938bc871a8f14a034 |
| verification/P09-AC3-DELETE-1/verify_all.py | 7fe9b475fdb794c32dfba8cc0dfde412ed9929b06a98d4e4c99192328b8ddf2b |
| verification/P09-AC3-DELETE-1/evidence/p09_ac3_delete_evidence.json | 67d4dbdb008a0603aa662471e22f80c2af669fb1eab784d92cec52f94d4d6261 |
| doc/tasks/P09.md | 43d2067dff71050df58d0e5dc0215f1727bf71c871c1d1f33f6dcb40d4fb8d8f |
| verification/P09/evidence/AC3-source-hashes.json | 56e40a827c20725cc1a66ddd527c521b84fcd059f624873732cfcecb814266e3 |
| verification/P09/evidence/AC3-source.png | 36452bb8d135ac96f1c453e11c23689d5917a2f0db42d154aca02722507153d7 |
| verification/P09/evidence/AC3-workflow-source.png | ee5f4ae0aae66a3d9ad8166933132bf2fad25da6220d8f02127f69546b5a4795 |
| doc/STATUS.md（HEAD 后工作区 overlay） | 88c176e641cf4c456c37a62d3bcb8822827fb7ff83573fee76fc68e8e0df4e0f |
| doc/REBASELINE_PLAN.md（HEAD 后工作区 overlay） | 2d514865eed149317a6cacb4d22b64485f3f5c07358371febf35a162d30fbfca |

## Finding 汇总

| ID | 级别 | 状态 | file:line 依据 | 最小修法 |
|---|---:|---|---|---|
| R-001 | P1 | closed | src/infrastructure/sqlite/library.py:746-751；tests/core/test_core_delete_commands.py:467-485 | 已 fail-closed：runtime 查询异常设为 BOOK_BUSY；异常注入测试确认删除被拒绝且 Book 仍在。 |
| R-002 | P1 | closed | src/infrastructure/sqlite/library.py:754-799；tests/core/test_core_delete_commands.py:323-407 | 已预检共享 Managed Copy、目标外 Artifact 路径与跨项目 Revision 引用，冲突时拒绝。 |
| R-003 | P1 | partial | src/infrastructure/sqlite/library.py:910-927、887-897、973-975；tests/core/test_core_delete_commands.py:525-535；contract M2-C1 §5.11.4 | step_run_id 已先冻结，输出引用据此清空；但 pipeline_stage_states 只有注释没有脱离 SQL，测试还断言目标 Page ID 保留；run_json 也只删 scope 顶层键，嵌套 target/task/step 引用未清。保留 stage-state 行并清除 Page/Revision/locator 引用；完整清理嵌套历史快照并加真实持久化断言。 |
| R-004 | P1 | closed（page-original 重试路径） | src/infrastructure/sqlite/library.py:617-630、848-863、1061-1085；tests/core/test_core_delete_commands.py:543-599 | manifest 持久化 page_ids 与 Managed targets；重试从 manifest 恢复 page_ids 并清理 deterministic page-original。随机 preview 遗留另见 N-003。 |
| R-005 | P2 | closed | src/infrastructure/sqlite/library.py:1093-1103 | book_id 先做路径分量校验，book 目录限制在 books_base 内并检查 reparse point，原来的越界路径缺口已收敛。递归遍历仍违反另一个范围要求，见 R-011。 |
| R-006 | P1 | closed | src/infrastructure/sqlite/migrator.py:175-185；tests/core/test_core_delete_commands.py:607-647 | finally 在恢复 FK 前先 rollback 活动事务；自定义非 sqlite 异常注入测试核验 rollback 与 FK 恢复。 |
| R-007 | P1 | partial | apps/desktop/frontend/src/recycleBin/RecycleBinPage.tsx:33-43、84-89；apps/desktop/frontend/src/library/client.ts:61、120-130；src/application/library/service.py:83-89；src/infrastructure/sqlite/library.py:683-688；apps/desktop/src-tauri/src/main.rs:68-140、1576-1630；tests/core/test_core_delete_commands.py:654-675；apps/desktop/frontend/src/recycleBin/RecycleBinPage.test.tsx:338-363 | 回收站 UI 已请求专用命令；Service 查询软删除集合；Core 的整库判断也已对数据库全部 books 做精确集合比较。可是新命令未注册到 Tauri production command/handler，也没有 Python Core IPC handler；repo 搜索只有前端常量/调用与 Service 方法。页面 catch 后 setBooks([])，真实 UI 会静默显示空回收站。现有 Core 测试直接调 Service，React 测试 mock 命令，均未证明真实 IPC 到服务数据源。补齐 command→Core→Service 路由，保留可见错误，并加入真实装配/dispatcher 断言；确认 UI 分母由全部活动与软删除 Book 组成。 |
| R-008 | P1 | open | verification/P09-AC3-DELETE-1/verify_all.py:206-209、327-330、346-350、366-370 | 多张表的 rows 用 else 0 硬编码，恒真地报告零行；后续 Managed/Derived 检查只打印数量，没有 orphan 扫描或断言。foreign_key_check 也不能替代 v5 已移除的 page locator 关系核查。改为按表结构执行真实 orphan/count 断言并覆盖含存量派生数据场景。 |
| R-009 | P2 | open | apps/desktop/src-tauri/src/library_bridge.rs:261-269、7242-7275 | host 原样复制任意 details.phase；现有 Rust 单测只覆盖 preflight。将投影限制为固定 preflight/cleanup 并测未知值降级/拒绝。 |
| R-010 | P2 | partial | doc/tasks/P09-AC3-DELETE-1.md:6、17-19、144-151、177-184；doc/tasks/P09.md:59、128-132、159-163；verification/P09/evidence/AC3-source-hashes.json | STATUS/Plan 的 HEAD 后 overlay 当前把 P09-AC3-DELETE-1 标为 in_review，但权威 Task 仍为 ready、delivery_head=null、canonical evidence 与 resource closeout pending；Task 的删除 evidence pin 为 560dd8…，实际 JSON 磁盘 SHA 是 67d4db…；P09 Canonical Evidence 仍 pin AC3-source-hashes 为 6c201…，实际磁盘 SHA 为 56e40…，并保留旧 AC3-DELETE-BLOCK。P09.md:59 宣称完成，与 :128、:131、:159-163 的 blocked/未实现记录冲突。同步 Task delivery/evidence/closeout 和 P09 canonical pins，消除相互矛盾记录。 |
| R-011 | P2 | open | src/infrastructure/sqlite/library.py:1094-1117；apps/desktop/src-tauri/src/main.rs:974-976；contract M2-C1 §5.11.4 | 仍 os.walk storage.root/books/book_id，即使只 rmdir 空目录也会递归枚举、进入并移除空子目录；用户可选导出目标，未见其被排除于该遍历之外。删掉目录遍历，只按 manifest/catalog 明确登记的 Managed/derived 文件清理，并保证用户导出路径不被枚举。 |
| R-012 | P1 | open | doc/tasks/P09-AC3-DELETE-1.md:35、111、137-142；doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:1200、1224；doc/STATUS.md（overlay）:9、doc/REBASELINE_PLAN.md（overlay）:14 | Task 与契约仍写明 AC1 冻结不授权 runtime 实现、待 Codex 明确释放范围；当前没有 Task allowlist/release 记录。STATUS/Plan 只把它列为复审中，不能代替实现范围释放。先由有权 Coordinator 在权威 Task/STATUS 记录范围与 Owner release，再处理实现集成。 |
| N-001 | P1 | open | src/infrastructure/sqlite/library.py:900-907；src/infrastructure/sqlite/schema.py:461-471；tests/core/test_core_delete_commands.py:497-503 | 删除事务将同一 run 的所有目标 target_id 设为空；v5 仍有 UNIQUE(pipeline_run_id, target_id)。多页 run 会触发唯一约束，整个永久删除失败。改用唯一且无定位语义的 detached 值或安全 schema 方案，并测试至少两个目标的真实 Run。 |
| N-002 | P1 | open | src/bootstrap/core_service.py:1219-1228；apps/desktop/frontend/src/library/client.ts:353-364；apps/desktop/frontend/src/recycleBin/RecycleBinPage.tsx:101-127 | Core 返回逐项 deleted/cleanup_pending；前端错误包装只留 code/message，确认 UI 保留原 frozen 全量目标。重试会再次提交已删除 ID，Core 对该项返回 BOOK_NOT_FOUND，无法按契约只重试 pending IDs。保留安全逐项状态，让用户明确确认 pending 子集，并测试“已删除+pending”批量重试。 |
| N-003 | P1 | open | src/bootstrap/core_service.py:1877-1881；src/infrastructure/resource_channel/render_preview.py:64-79、157-181；src/infrastructure/sqlite/library.py:1067-1085 | reader 对译图调用 publish() 生成随机 preview-UUID catalog entry；永久删除只查 page-original-{page_id}。collect_orphans 保留有 catalog row 且文件存在的 preview，因此删除成功后译图 preview 与 catalog row 仍可用。把属于目标 Book 的 preview resource IDs 持久化到 cleanup manifest 并纳入首次及重试清理；补真实译图残留断言。 |
| N-004 | P1 | open | src/infrastructure/sqlite/library.py:1076-1085 | 先对 catalog rel_path 执行 resolve()，再对解析后的目标调用 lstat()/reparse 检查；若授权目标被替换成指向 derived root 内另一个文件的 symlink，resolve 后 lstat 看到的是普通目的文件，随后可能 unlink 另一个资源。对未解析的目录项和每层路径先做 reparse/containment 检查，使用不会跟随链接删除目的资源的安全删除方式，并在 preflight 拒绝替换。 |

## 第二轮五项 P1 逐条复核

1. R-007：partial。回收站查询 Service 本身只返回软删除 Book，Core 整库集合比较也正确；但是实际前端命令没有注册或 IPC 路由，测试只覆盖 Service 直调和 UI mock，所以生产页面会 fail-soft 显示空回收站。尚未证明真实数据源。
2. R-001：closed。runtime 查询异常现在映射为 BOOK_BUSY；RuntimeError 注入测试覆盖拒绝路径。
3. R-003：partial。先保存 step_run_id 集合的修复与输出引用测试已加入；stage-state 没有实际 detach，且测试保留 page target_id，run_json 的嵌套定位符也未清。
4. R-004：closed（限 page-original）。manifest 保存 page_ids 与 Managed targets，重试使用该快照；故障注入测试验证 page-original 清理。随机 preview 未入 manifest 是 N-003。
5. R-006：closed。finally 先 rollback 后恢复外键；非 sqlite 异常路径有专门测试。

## 新发现

N-001 至 N-004 均为本轮对真实源码和 Schema 的额外核验结果，详见 finding 表。其中 N-001 会让标准多页流水线历史触发唯一约束并回滚删除；N-002 使 cleanup_pending 无法按契约完成显式的逐项重试；N-003 在真实译图阅读后留下带 catalog 行的 derived preview；N-004 在 reparse 检查前 resolve 目标，可能误删 derived root 内另一个登记资源。这些均阻断 AC2/AC4 收口。

## 未验证或不能据此宣告通过的事项

- pytest、frontend npm test、Cargo test/build 均 NOT_RUN；本轮依据源码和现有测试断言静态复核，不把现有测试文件当作本轮运行结果。
- verification/P09-AC3-DELETE-1/verify_all.py 未运行。其现存断言有硬编码零值和缺失 orphan 扫描，证据中的 AC4 PASS 不可采信。
- 未通过真实 Tauri/Core runtime 验证回收站 IPC；源码路由缺失本身已足以判 R-007 未闭合。
- 未执行删除工作流，未独立复验所有样本生命周期步骤或生产数据库历史脱离。
- 源样本当前字节 SHA-256 与 P09 pin 中的 sample hashes 相同；这只支持样本字节指纹一致，不替代更新 canonical evidence，也不证明 AC4/永久删除完整性。

## 是否可收口并把 P09 AC3 由 BLOCKED 翻为 PASS

否。当前不可收口，也不应据此将 P09 AC3 整体由 BLOCKED 翻为 PASS。两份源样本的当前磁盘 SHA-256 与记录值相符，但 P09 Canonical Evidence 的 source-hashes pin 仍是旧值、AC3-DELETE-BLOCK 仍在，Task 与 P09.md 的证据/closeout 状态相互矛盾；更有多项 P1 删除安全与残留问题未解。只可记录“样本哈希窄项当前匹配”，不能把它扩展为项目级永久删除已验收。

建议下一步：Coordinator 先在权威 Task/STATUS 记录 implementation scope release 和 allowed paths，再交由 Owner 修复所有 P1 与 R-008/R-009/R-011，并重建可审计的 AC4 orphan/locator 证据；随后由 Codex 对新的固定 commit 复审。
