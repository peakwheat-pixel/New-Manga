---
id: M2-REGION-RETYPE-CORE
title: "Region 改标 Core 实现：SetRegionType 全链+11 断言落测+协议 minor bump+旁路同步（T5b；按 rev 1.4 冻结契约）"
kind: feature
status: done
integration_commit: d8019810
approval: user_ruling_2026-10-04_释放T1b_T5b_T5c
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
depends_on: [M2-REGION-RETYPE-CONTRACT]
base_commit: 1b765007
branch: agent/zcode/M2-REGION-RETYPE-CORE
worktree: G:/CODEX/New Manga.worktrees/M2-REGION-RETYPE-CORE-zcode
integration_commit: null
---

# M2-REGION-RETYPE-CORE：Region 改标 Core 实现（T5b）

## 来源与目标

按已冻结的 M2-C1 rev 1.4 契约（T5a done）实现 `set_region_type` 全链 runtime。**范围纪律：只做 Core/Rust/测试三层，前端接通归 Workbench UI 实现 Task（blocked 不在本 Task）**。沿 SETTINGS-IPC 先例（命令面变更=协议 minor bump+packaging 门旁路同步）。

## Acceptance Criteria

- [ ] AC1 Core 层：`editing/service.py` 新增 retype 写路径（经 commit seam 新 revision、origin=user、review_state=UNREVIEWED 不触发需校对、policy 快照按 EV-8 裁决重快照——sfx 方向按改标时全局配置/非 sfx 强制 SKIP）；`core_service.py` 注册 `set_region_type` 命令（wire=rev 1.4 §5.4：请求 region_id/new_region_type/expected_revision?→响应 revision_no+生效态；错误语义零新增逐码复用）。
- [ ] AC2 Rust 层：production command+allowlist 三视图+envelope 挂接（production-only，沿 settings 两命令先例）；DTO 与 wire 逐字段一致。
- [ ] AC3 11 条断言落测：C1-C7（人工优先写通道不互斥/AI 侧 Revision+Lock 双守卫 fail-closed/乐观期望显式拒绝/改标后决策生效/机器笔人工叠加/目标缺失/page_id 语义）+P1-P4（重开持久/重检测幂等复用不回滚人工改标/撤销完整恢复/撤销后再改标幂等）——**两层覆盖**（service guard 返回+管线候选持久化，T5a P3-6 要求），先红后绿。
- [ ] AC4 读取面：`list_regions` 按 rev 1.4 返回 RegionListSummary（若实现为扩容既有命令则按契约取舍得案）——T5c 导出器与本 Task 消费同一读取面。
- [ ] AC5 协议 minor 2→3+旁路同步：PROTOCOL_MINOR 更新、frozen-probe/EXPECTED 计数/CS-L1 envelope minor 沿 SETTINGS-IPC 登记口径同步；**M2-AC5 GATE 25/25 重跑 PASS**。
- [ ] AC6 回归：三套件基线不回退（pytest 三套件 627+1sk 口径+cargo+vitest）；m2_acceptance 35 passed。

## 允许修改范围

`src/application/editing/service.py`、`src/bootstrap/core_service.py`、`src/interface/**`（handler 注册）、`src-tauri/src/**`（command/allowlist）、对应 `tests/**`、协议常量文件（PROTOCOL_MINOR）、Task/Handoff/`verification/M2-REGION-RETYPE-CORE/**`。

## 禁止范围

`doc/contracts/**`（rev 1.4 已冻结，实现中发现契约缺口=停等登记，不得改契约）、`apps/**` 前端、**`packaging/**` 除经追认的 CS-L1 协议字面量与 RC2 EXPECTED 计数同步外不改；spec 冻结**（Q1 附条件 b，DSH r1 返修措辞修订 2026-10-04）、`doc/STATUS.md`、既有设计稿。

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC3 11 断言 | pytest 新增（先红后绿） | dev venv | **PASS**：红态 43 failed @`084426dc` → 绿态 46 passed @`e40eeae0`（3 个管线候选持久化断言为既有机制场景守护，红绿不适用，已登记） | verification/M2-REGION-RETYPE-CORE/verification.md §3 |
| AC5 GATE | M2-AC5 GATE 25/25 | build_sidecar | **PASS 25/25**（EXIT=0；CS-L1 实测 ping minor=3；installer sha256 d6003ae7…，bundle HEAD=cfbf3859） | verification/M2-REGION-RETYPE-CORE/raw/retype-m2ac5-cleanstart-gate.json（DSH r1 P2-1 返修：AC5 raw 已还原原始 M2-AC5 证据，本轮产物搬至本 Task raw/） |
| AC6 回归 | 三套件+m2_acceptance | dev venv | **PASS**：650+1sk 0 failed（基线 627+1sk）+ cargo 47+0f+1ig（基线 46+1ig）+ vitest 49（基线 49）+ m2_acceptance 35 passed | verification/M2-REGION-RETYPE-CORE/verification.md §6 |

## 依赖、风险与阻塞

depends_on=M2-REGION-RETYPE-CONTRACT（done）。与 T5c 并行（写范围零冲突：本 Task src/src-tauri/tests，T5c experiments）；集成串行 T5b→T5c。风险：实现中发现契约语义缺口→停等登记（不得擅自改契约或实现）；GATE 重跑需 sidecar 构建时间。

## 交付与运行记录

- Handoff：[doc/handoffs/M2-REGION-RETYPE-CORE-zcode-delivery-cfbf3859.md](../handoffs/M2-REGION-RETYPE-CORE-zcode-delivery-cfbf3859.md)（实现链 claim=`07fe4a9e` → 红态=`084426dc` → Core 绿=`e40eeae0` → Rust+旁路=`cfbf3859` → 文档 commit）。Review：尚无。
- 实现摘要：AC1 `service.set_region_type`（commit seam 单笔新 revision/origin=user/review_state=UNREVIEWED/EV-8 重快照）+ `service.list_region_summaries` + `core_service` 两命令（wire=rev 1.4 §5.4，错误零新增语义）；AC2 Rust production-only 两命令+三视图+capabilities；AC3 C1-C7/P1-P4 两层断言；AC4 RegionListSummary 最小五字段读取面（脚注 a 空列表）；AC5 PROTOCOL_MINOR 2→3+三处旁路同步+frozen-probe 维持冻结；AC6 三套件全绿。遗留与取舍登记见 Handoff §风险与遗留。
- **DSH r1（approved_with_conditions，0×P0/P1）返修已落**：必修 P2-1（AC5 raw 还原+本轮 GATE 产物搬本 Task raw/ `retype-m2ac5-*`，git show 实测旧值=原始 M2-AC5 证据 installer `5410e29e…`/minor 0）+ P2-2（`set_region_type` 非 APPLIED 显式三分支：INPUT_REVISION_CHANGED 保持冲突态，DB_FAILED/LOCK_CHANGED 抛 RuntimeError→UNKNOWN/internal；单测先红后绿）；P3-1/2/3/4 修、P3-5 登记，P4-1/3/4 修、P4-2/5/6/7 登记。返修后回归：pytest editing+pipeline 143 passed、三套件 650+1sk 持平、全量 1780 passed/1 skipped/1 failed（唯一失败=T1b 资产计数 pre-existing，HEAD 同样失败，不代修）、cargo 49+0f+1ig（47→49）。处置对照表：Handoff「DSH r1 修订段」+ verification §10。status 保持 in_progress 待 r2 复核与 Codex 集成。


## 集成收口（2026-10-04，编排会话代行 Codex）

- **integration_commit=`d8019810`**（merge，无冲突）；**r1 返修 commit=`0f88cbcd`（链顶）**——frontmatter 修正（r2 P3-1：status 曾被 Owner 回填误写回 ready、base_commit 69321db7 系 Task 书写笔误）与链顶登记（r2 P3-2）由本收口闭合。
- 集成复跑：editing+pipeline+providers+core+m2_acceptance 五目录 **793 passed 1 skipped**（=143+650 合集，全绿）；cargo/vitest 未重跑（返修后 Owner 已留 raw 证据，集成面零前端改动）。
- **test_catalog 100 vs 97 失败 pre-existing 实证**：`git show 1b765007` 断言 `== 97`（:33-34）与 cases.json 100 在 base 已矛盾——SFX-E2E-MATERIAL 入池 3 页后断言未更新，与 T5b 改动零因果（补齐 r2 P4-1 独立归因证据）；断言更新小切片登记候选（归属 SFX-E2E-MATERIAL 遗留）。
- 集成追认（Q1 附条件 a）：`packaging/m2ac5/run_clean_start_e2e.py`（CS-L1 envelope 2→3）与 `verification/M2-RC2/run_e2e.py`（PRODUCTION_EXPECTED 7→9）旁路同步追认合规；`capabilities/m2rc1-commands.json`+`gen/schemas/`×4+`permissions/`×2 新增=宿主机制必然产物，沿 M2-AC1 F-008 先例追认入库。
- 契约实现态（r1 P3-6）：本收口登记 `set_region_type`/`list_regions` runtime 已实现（rev 1.4 条文不变，实现态注记归下次触碰契约的 Task 落字）。
