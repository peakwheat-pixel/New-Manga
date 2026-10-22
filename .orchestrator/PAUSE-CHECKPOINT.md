# 暂停检查点（PAUSE CHECKPOINT）

- **暂停时间**：2026-10-16（Asia/Shanghai）
- **触发者**：用户明确指令 —— 「本轮完成后，暂停任务，我要重启 dsh」
- **性质**：**用户主动暂停（非故障、非阻塞、非停止授权）**。Goal 保持 **active**；重启后**继续**从本检查点恢复。
- **执行者**：dsh（Active Coordinator, epoch 5）

---

## 1. 最终 Git 状态（Live 事实，暂停时快照）

| 项 | 值 |
|---|---|
| main HEAD | `ea23da4d1f96d3294a6a8b353bfa113f15f80254` |
| 当前分支 | `main` |
| tracked dirty | **19**（全部为用户既有 dirty，本会话全程未变） |
| 治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1` → **PASS (1 warning)** |
| warning | `doc/REBASELINE_PLAN.md` 达预算 80%（2287 bytes / 34 lines） |
| INFLIGHT | `.orchestrator/INFLIGHT.json` → op=`CLOSEOUT_HOST_ISSUER_1_COMPLETE`，status=**DONE** |
| 运行中作业 | **无**（`job_list` 全部 completed） |
| 未提交治理改动 | **无**（全部已 commit） |

**用户既有 19 项 dirty（严禁触碰／推送／reset／stash）**：
`.qoder-credits/report.json`、`AGENTS.md`、`doc/00_INDEX.md`、`doc/01_FUNCTIONAL_ARCHITECTURE.md`、`doc/03_DATA_MODEL.md`、
`doc/04_USER_FLOW.md`、`doc/06_TRANSLATION_PIPELINE.md`、`doc/09_COLLABORATION.md`、`doc/11_ARCHITECTURE_MAPS.md`、
`doc/12_ROADMAP.md`、`doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md`、`doc/WORKTREE_SAFETY_INVENTORY.md`、
`doc/tasks/P02-NEW-TIME-X6-BUILD-CARGO.md`、`doc/tasks/P02-NEW-TIME-X6.md`、`doc/tasks/P02.md`、
`doc/templates/HANDOFF.md`、`doc/templates/REVIEW.md`、`doc/templates/TASK.md`、
`verification/PROJECT-ROADMAP-20261008/ROADMAP.md`

---

## 2. 重启后的恢复流程（必须按序执行 R1–R6）

重启 dsh 后，**先读本文件**，然后：

| 步骤 | 动作 |
|---|---|
| **R1** | **Git/FS 事实**：`git rev-parse HEAD`、`git status --porcelain --untracked-files=no`（应=19）、`git worktree list` |
| **R2** | **治理+租约**：`pwsh -NoProfile -File tools/governance/check.ps1`（应 PASS）；核对 `.orchestrator/runtime.json` 的 epoch/lease；必要时用 `coordinator-lease.py` 重新取得租约（epoch 可能已递增） |
| **R3** | **权威指针漂移**：`doc/STATUS.md` 的「当前 Task」与 `doc/REBASELINE_PLAN.md` 的 READY 行是否一致（应=**ARCH-DOC-REBASELINE**） |
| **R4** | **EXTERNAL_CHANGE 分类**：若 dirty ≠ 19，逐项归因；**不得**重置/覆盖/删除未归因改动 |
| **R5** | **日志设施**：读 `.orchestrator/{INFLIGHT.json,OPLOG.ndjson,BACKLOG.md,RUNTIME_DIRECTIVES.md}` 与 `BL11-ENV-EVIDENCE.md` |
| **R6** | **下一 READY 判定**：见第 4 节候选，选一个释放 |

---

## 3. 本会话（第 1–15 轮）已交付并被集成的工作

| Task | 状态 | 集成 commit |
|---|---|---|
| P06 GC 分发迁移 | done | `d3342895` |
| P10 凭据配置契约 | done | `c46c0df0` |
| P11 长任务生命周期契约 | done | `ceca5721` |
| P09 导入 Core | closed_with_limitations | `c6a7339f` |
| P09-FU1 测试基线 | done | `860f6cda` |
| P13 Run runtime（控制/恢复/投影） | done | `8d7cad13` |
| P13-C1 Runtime IPC 契约 rev 2.0 | done | `c61d8f8c` |
| P16 阅读/导出 Core | done | `e1be3082` |
| P16-C1 Reader/Export 契约 rev 2.1 | done | `27622aa3` |
| P12-C1 导入 IPC 契约 rev 2.2 | done | `ed8e44e7` |
| P09-FU2 导入 IPC 接线 | done | `897bc7ec` |
| P18 JA/KO 质量资格 | closed_with_limitations | `44958159` |
| HOST-ISSUER-1-C1 HostControl 契约 rev 2.3 | done | `b9cb0623` |
| HOST-CORE-1 Core 侧 HostControl 接收端 | done | `67ee4a58` |
| HOST-ISSUER-1 Tauri host 引用签发 | done | `7fce3ab3` |

**协议演进**：Core 协议已从 major 1 / minor 6 → **major 2 / minor 3**（P13-C1 → P16-C1 → P12-C1 → HOST-ISSUER-1-C1）。

---

## 4. 重启后的下一批候选（按优先级）

1. **P12 / P17（书架导入 UI / 阅读器 UI）** —— 其 wire 与 host 命令面**均已就绪**
   （`library_import_file` / `library_import_folder` / `library_start_export` 已实现且未暴露 HostControl）。
   ⚠️ **前置**：需先释放 **ZCode 工作台/书架设计 Task**；但 `runtime.json` 中 **`zcode = UNKNOWN`（不可用）** →
   重启后先复核 zcode 可用性，不可用则按 DIR-2 由 codex/antigravity 承担（Task 内明确分配）。
2. **BL-11b（重建 sidecar bundle）** —— 旧 bundle 与协议 2.3 不匹配，导致**打包端到端不可验证**；
   修复入口 `packaging/m2ac5/build_sidecar.ps1`（需先建 build venv `task-envs/m2ac5-build`），
   并完成 frontend build（`frontend/dist` 亦为 gitignored 前置）。这是**取得真实端到端结论的唯一路径**。
3. **P18 两个技术缺口**：检测**像素上限 `11184810`**、**KO detector 权重缺失**（`PROVIDER_NOT_CONFIGURED`）。
4. **BL-12（治理检查器未版本化）** —— `tools/governance/check.ps1` **未被 Git 跟踪**，
   导致**任何 fresh worktree 无法运行治理检查**；建议尽快单独处置。

---

## 5. 待用户裁决（不阻塞推进，但需用户决定）

- **P18 的产品发布门槛**：JA/KO 质量达到何种程度才允许声明"支持该语言"？
  依据 `experiments/P18/qualification-plan.md` §2。**AI 不得代定。**

---

## 6. 未决/已知限制（须如实继承，不得声称已完成）

| id | 内容 |
|---|---|
| **BL-11b** | 旧 bundle 与协议 2.3 不匹配 → 6 项真实 sidecar Rust 集成测试在主仓与 worktree **均失败**；**packaged E2E 全部 `NOT_RUN`** |
| **BL-12** | `tools/governance/check.ps1` 未纳入版本控制 → worktree 自检结构性缺失 |
| **BL-9** | 无项目级永久删除操作 → P09 `AC-IMPORT-002`（AC3）受限 |
| **BL-4** | ARCH-DOC-REBASELINE 的 AC4–AC6 仍待 P18/P20/P16/P17（部分已满足，需重启后复核） |
| **BL-7** | `delivery_head` 申报与实际 HEAD 不一致（本会话共发生 **12 次**），每次均由 Coordinator 冻结为实际值 |
| **P18 AC5** | 真实 JA/KO 端到端链路**未跑通**（导入 wire 当时缺失；现 `P09-FU2` 已补，**可重跑**） |
| **P09 AC3** | 项目级永久删除验收仍受限 |

---

## 7. 关键资源位置

- **治理**：`doc/{STATUS.md,REBASELINE_PLAN.md}`；Task 文件 `doc/tasks/**`
- **运行时治理**：`.orchestrator/{INFLIGHT.json,OPLOG.ndjson,BACKLOG.md,RUNTIME_DIRECTIVES.md,BL11-ENV-EVIDENCE.md}`
- **技能脚本**：`C:\Users\49745\.agents\skills\multi-agent-project-orchestrator\scripts\`
- **本会话 worktree**：`G:\CODEX\New Manga.workspace\worktrees\{P13*,P16*,P12-C1*,P09-FU2*,P18*,HOST-CORE-1,HOST-ISSUER-1,HOST-ISSUER-1-C1}`
- **临时/证据**：`G:\CODEX\New Manga.workspace\tmp\guarded\`（各 Task 的 prompt 与 owner 结果）
- **BL-11 证据**：`.orchestrator/BL11-ENV-EVIDENCE.md` + `G:\CODEX\New Manga.workspace\tmp\guarded\bl11-*.log`

---

## 8. 纪律提醒（重启后必须继续遵守）

- 用户 **19 项 dirty / untracked / 既有 worktree / 既有 linked worktree**：**只读保留**，不删除、不 reset、不 stash、不 push。
- 新 Task 必须服务项目目标 / 已登记 AC / 解除真实 DAG 依赖 / 修复验证暴露的问题；非必要优化进 BACKLOG。
- **Anti-Thrash**：同一策略不得连续失败两次；第二次失败须记录签名并更换策略。
- **Commit 幂等**：提交前检查变更是否已存在、是否只属当前 Task 范围。
- **Merge 冲突**：语义级解析（保留双方有效修改），记录依据，不得盲目 ours/theirs。
- **治理写入**：必须经 `coordinator-lease.py guarded-write`；**注意它只写入、不提交**，提交需另行执行。
- **EXTERNAL_CHANGE**：不可归因的改动标记并隔离，不覆盖、不删除。
- **BLOCKED_WAITING_EXTERNAL_DECISION** 仅在四条件同时成立时使用。
