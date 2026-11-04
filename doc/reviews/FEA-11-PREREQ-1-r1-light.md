# FEA-11-PREREQ-1 P2 处置轻量复核（C-17，r1 后新 head）

- 审查者：**ZCode 全新上下文**（session `sess_39a3cee4-31a4-4f5c-a4b0-fcf3a328d1f6`；未参与起草/返修/前次 Review）。
- 复核 head：`c7940fa7179e2b1d029fa58fb09e9a8dea13f5eb`；结论 **approved（新 P0=0/P1=0/P2=0，6/6 项 P2 处置确认，无漂移，范围 0 域外）**。
- 报告正文由 DSH 依据其最终回复归档（ZCode 只读）。

冻结记录草案 PENDING 项全部正确留给 DSH 冻结流程（未被提前回填）。全部复核点已核完，以下为轻量复核报告正文。

---

# FEA-11-PREREQ-1 P2 处置轻量复核报告（C-17，r1 后新 head）

- **审查者**：ZCode 全新上下文（本会话；未参与 C-17 起草/收尾/返修/前次 Review）。
- **复核 head**：`c7940fa7179e2b1d029fa58fb09e9a8dea13f5eb`（= 当前 HEAD，工作区 clean）；增量 = `f2068d468`（P2 处置+r1 报告归档+复跑日志）+ `c7940fa71`（EV 重签一行）。
- **只读声明**：未修改任何仓库文件、未 commit/push；本报告为唯一产出。

## 结论

**approved（新 P0=0 / P1=0 / P2=0）。可进入 DSH 冻结。**

## P2 处置逐项确认表（6/6）

| Finding | 处置（实际 diff） | 复核结果 |
|---|---|---|
| **R17-1** §8 retryable 差异 | STALE_BASE_REVISION 行说明列追加：本面 `true`=“重新 prepare/确认后可重试”；FEA-05 `false`=“同请求原样重发不可重试”；retryable 是命令级投影（M2-C1 §8） | ✅ code/category/conflict\|true 三列**未变**；FEA-05 `:59` 冻结为 `conflict\|false` 引用准确；与 M2-C1 §8“命令级投影、不得推广全局映射”一致，两面并存不构成冲突 |
| **R17-2** scope=all 超 20 book | §5.3 正文补：book 去重数超 project_ids 上限 20 时 Scan/PlanBody 以 **INVALID_REQUEST** 拒绝并提示按 project_ids 分批（不静默截断、不回退 current） | ✅ 边界明确无歧义；与 §5 `:207` "project_ids 1..20" 一致；INVALID_REQUEST 为既有形状错误码；**未改任何 DTO/表格定义** |
| **R17-3** apply 守卫 + §2.1 措辞 | §3.1 confirmed→apply 守卫列加“plan 未过期（expires_at）”；§2.1 改为“仅对 v5 执行 `PRAGMA foreign_key_check`、对 v7 执行 validate 回调；v8 纯新增空表不触发两者” | ✅ `expires_at` 真实存在（DDL `:41`/索引 `:54`/Plan DTO `:250`）；与 `src/infrastructure/sqlite/migrator.py:222,231`（FK check 仅 v5）、`:236`（validate 仅 v7）**代码事实逐一相符**，v8 为 8≠5≠7 不触发推断正确；迁移语义零变化 |
| **R17-4** operation_id 归属 | §7.1 新增一行：captured_v7 行回填当次 operation_id（可审计）；native 日常写入留 NULL | ✅ 与 §2 DDL `:106`（可 NULL、FK→source_operations）兼容；captured_v7 捕获与 operation 创建同一业务事务，FK 时序自洽 |
| **R17-5** examples 判别力 | **不改契约**；Handoff 记录“如实保留，由 FEA-11 生产装配测试承接” | ✅ 契约/脚本/examples.log 零修改（两 commit 文件清单证实）；未伪造更强证据，与 r1 建议一致 |
| **R17-6** capabilities Core 侧 | §5.1 该行备注追加“**Core 不注册该名**，向 Core 发送按 M2-C1 既有未知命令语义拒绝（UNKNOWN_COMMAND）” | ✅ M2-C1 `:133` 确认 UNKNOWN_COMMAND 既有语义；与 transport=host-local 编译一致（wire-schema 字节未变佐证）；有效防止 Core 误注册 |

## 是否引入新 P0/P1/P2：无

- **diff 全量人工核对**：契约仅 6 处说明性文字（5 行替换+1 行新增=11 行变化，与 `--stat` 精确吻合，无隐藏修改）；全部落在 FROZEN-C17 §1B 列举的 §2/§3/§5/§7/§8 内，且均为 additive 注释——DDL、DTO 表、错误表三列（code/category/retryable）、迁移语义、状态机动作/目标态**零变化**。
- **无漂移**：`wire-schema.json` 本会话复算 SHA-256 = `9fed28fa1e8b6…b32de1e`，与 EV 表、DSH wire 日志 `WIRE_SCHEMA_SHA256` 三方一致；DSH 复跑 validate_wire EXIT=0（文档实时编译 == 冻结 schema）。
- **无冻结契约冲突**：对 FEA-05 / M2-C1 引用均忠实（上述逐项）；C-14/C-15/C-16/C-05/C-13 相关条款未被触碰。
- **范围 0 域外**：两 commit 文件全部为 doc/**（治理/报告/Handoff/Task）+ verification/logs/**；无生产代码/测试/依赖/用户数据变更；protected 对象（17 冻结契约+M2-C1+schema/migrator/pins 脚本）零触碰。冻结记录草案 PENDING 项未被提前回填（正确）。

## 复跑/核验结果与 NOT_RUN

| 项 | 状态 | 说明 |
|---|---|---|
| 哈希等价核验 | **全部 PASS** | ① C-17 新字节 `1d425887…` == EV 重签值；② 旧字节（`git show 69d7c31ee:…`）`cb7c5749…` == r1 时 EV 旧值（**旧→新链条闭合**）；③ wire-schema `9fed28fa…` 无漂移；④ DSH 三脚本复跑日志（P2 处置工作树，2026-11-04T22:11:56，提交前一秒）全 EXIT=0，且 `f2068d468→c7940fa71` 仅 Task 一行变化 → **复跑时脚本+契约字节 == 当前 HEAD**；⑤ 工作区 clean、HEAD 一致 |
| 本会话 Python 复跑 validate_contract 等 | **NOT_RUN** | plan mode 门禁拦截 Python 进程调用（与 r1 会话同情形，非脚本问题）；已以上述哈希/日志等价核验替代 |
| 真实 v7→v8 升级链/杀进程矩阵/真实 IPC/lease/DPAPI/resolve 字节/全量回归 | NOT_RUN | 沿 r1 口径，归 FEA-11（Handoff 已如实登记） |

## 观察注记（非 finding，不阻塞）

1. §5.3 `:269` 新句“重新预览**␣**scope=all”句号后有一处多余半角空格——纯排版瑕疵，不在 DTO/表格/wire 面，不影响语义与机器解析；可忽略或随冻结元数据编辑一并处理。
2. 三个 dsh-validate 日志头部格式微调（EXIT 尾行归一化、新增 shell/head/时间戳元数据行）——日志可追溯性增强，非证据语义变化。

## 可否进入 DSH 冻结：**可以**

本报告 approved 后，路径与 FROZEN-C17 §3.4–5 一致：DSH 仅做明确记录的冻结元数据编辑（回填 §1/§1B：轻量复核 head `c7940fa71` + r1 head `69d7c31ee`、Reviewer=ZCode 全新上下文）→ 最后编辑后复算三指纹（工作树 SHA-256 与 Git blob 分列，勿混用 hash-object ID）→ 回填 Task EV commit 列 → 单点追加 verify_pins 第 18 项（18/18）→ DSH 侧复跑三 validate + check.ps1 + verify_pins.ps1 记录逐项 EXIT → Task done → 更新 PLAN/STATUS → 派发 FEA-11 scope-r2（全新上下文）。

**推荐下一步**：DSH 接收本报告，按上述路径执行冻结。可转发指令：

```text
请 DSH 在 G:/CODEX/New Manga（main）接收 FEA-11-PREREQ-1 P2 处置轻量复核报告（reviewed_head=c7940fa7179e2b1d029fa58fb09e9a8dea13f5eb；ZCode 全新上下文，未参与起草/返修/前次 Review；decision=approved，新 P0=0/P1=0/P2=0；6 项 P2 处置全部确认到位，wire-schema 9fed28fa 无漂移，EV 重签 1d425887 与 C-17 新字节复算一致，范围 0 域外）。处置：按 FROZEN-C17 §3.4-5 冻结——回填 §1/§1B（轻量复核 head c7940fa71 + r1 head 69d7c31ee、Reviewer=ZCode 全新上下文）、最后编辑后复算三指纹（工作树 SHA-256 与 Git blob ID/blob SHA 分列）、回填 Task EV commit 列、单点追加 verify_pins 第 18 项 C17=FEA-C17_SOURCE_SYNC_DRAFT.md（18/18）、DSH 侧复跑 validate_contract/validate_examples/validate_wire 与 check.ps1/verify_pins.ps1 并记录逐项 EXIT（本复核会话受 plan mode 限制未复跑 Python，已以哈希/日志等价核验替代）、Task 转 done、更新 PLAN/STATUS，随后派发全新上下文执行 FEA-11 scope-r2。可选：冻结元数据编辑时顺手消除 C-17 §5.3 :269 "重新预览。 scope" 句号后多余半角空格（非阻塞排版瑕疵，若消除则三指纹须在最后编辑后复算）。无其他下一步操作。
```