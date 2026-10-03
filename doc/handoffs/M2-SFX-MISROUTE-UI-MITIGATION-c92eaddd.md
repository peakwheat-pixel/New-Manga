---
task_id: M2-SFX-MISROUTE-UI-MITIGATION
author: ZCode
recipient: DeepSeek Harness（非作者 Reviewer）；集成核验=编排会话代行 Codex
base_commit: fb5d56c6
delivery_head: c92eaddd
status: in_review
---

# Handoff：M2-SFX-MISROUTE-UI-MITIGATION（SFX 误路由缓解 UI 设计切片）

**结论速览：五条 AC 全部以设计文档形态交付（`doc/design/M2-SFX-MISROUTE-UI-MITIGATION/design.md`，delivery=`c92eaddd`），零产品代码（`src/**`/`src-tauri/**`/`apps/desktop/frontend/src/**`/`doc/contracts/**`/`doc/STATUS.md` 零 diff）。AC3 对照发现三大契约缺口（region 读取命令不存在、改标命令不存在、疑似信号字段不存在），全部登记为 RC-1…RC-5 修订候选、未 widening。设计为纯文档，无运行验证——验证列=AC 逐条自检表 + AC4 断言清单自查 + diff 面核对。**

## 交付结果

### 交付物

| 文件 | 内容 |
|---|---|
| `doc/design/M2-SFX-MISROUTE-UI-MITIGATION/design.md`（新增目录） | 主设计契约：§0 结论速览 / §1 损害语义+改标语义表 / §2 领域事实六条 / §3 AC1 视觉契约 / §4 AC2 交互契约 / §5 AC3 数据需求 D1–D10 / §6 AC4 断言 A1–A13 / §7 AC5 EVOLVING EV-1…EV-8 / §8 边界自证 |
| `verification/M2-SFX-MISROUTE-UI-MITIGATION/ac-self-check.md`（新增） | AC1–AC5 逐条自检表（全 PASS）+ A1–A13 可测性自查 + diff 面核对 |

### 设计要点（Reviewer 快速索引用）

- **AC1 视觉**：警示=叠加层（warn 色 2px **实线**边框 E1 + `♪?` 徽标 pill E2，三重编码），**虚线框保留给「需校对」**（UI 契约既有目标语义，避免冲突）；改标成功态=skip 色 `♪` 类型徽标 E3（文案按 region policy 快照分档「SFX·保留原文」/「SFX·拟声词翻译链」）；反馈条 E4。入口双通道：RegionOverlay 右键菜单（与草稿右键闭合按草稿态互斥）+ RegionInspector 按钮组。Reader=页级提示条+跳转 Workbench（诚实于 reader 投影无 region 面）。机器改标（`sfx-arb-`）加 `⧉` 字形区分。
- **AC2 交互**：不对称状态机——speech→sfx 即时执行+undo（默认 skip 下只减害，不加重兜底负担）；sfx→speech 显式确认框（反向会重新进入对白翻译链=重新引入乱译风险）。撤销走 `restore_revision`（不得反向改标模拟）。policy 联动=region 级快照显示永远优先于全局设置，UI 只读不写。已渲染错误译文不因改标消失→反馈条附 `[重渲染本页]`（`rerender_single` 语义）。
- **AC3 数据**：D1–D10 逐项对照 M2-C1 rev 1.3。已承载：D1 RegionId、D9 settings 通道、D10 rerender 枚举；部分承载：D6 policy（settings 有、region 级读取无）、D7 改标历史（`ListRegionRevisions` 命令名有、RevisionSummary DTO 无）；缺失：D2 疑似信号字段、D3 改标命令（Core `RegionEditingService` 现无 `set_region_type`）、D4/D5 region 读取面（`RegionSummary` 被引用但结构未定义）、D8 Reader 页级疑似计数 → **RC-1…RC-5 修订候选，本 Task 零契约改动**。
- **AC4 断言**：13 条红线（A1 源文件零写路径、A2 警示/改标不得依赖 OCR 非空——BJ15 深盲形态 0 候选实证、A3 警示不自动触发领域变更、A4 gate 语义一致、A5 反向改标强制确认、A6 revision-only 改标与撤销、A7 `sfx-arb-` 机器来源可区分、A8 三重编码、A9 UI 禁重算 policy 门、A10 Reader 零写操作、A11 SfxPolicy 三值零改动、A12 改标入口限 speech↔sfx、A13 双主题对比度 ≥4.5:1）。
- **AC5**：零产品代码声明；静态原型验证页诚实省略（Workbench React 页不存在，原型页无挂载点无法验证两场景数据流）；EV-1…EV-8 演进项+冻结面清单（§7.3：断言、改标语义表、领域事实、状态机拓扑、三条视觉规则不可演进）。

### 变更路径与提交列表

| commit | 内容 |
|---|---|
| `8d844726`（claim） | Task frontmatter：`status: ready→in_progress`、`base_commit: fb5d56c6` 回填、`owner_claim: 2026-10-03T22:26:03Z` |
| `c92eaddd`（**delivery_head**） | 设计文档 + 自检记录（2 文件 +366 行，产品面零 diff） |
| 本 handoff commit | `doc/handoffs/M2-SFX-MISROUTE-UI-MITIGATION-c92eaddd.md` + Task 交付记录回填（status 保持 in_progress，Review 后由集成方流转） |

## 验证证据

设计交付无运行验证；验证形态 = 逐条自检 + 断言自查 + diff 面核对（Task 测试表计划即「设计评审（DSH 非作者静态 review）+AC4 断言清单逐条自检」）。

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1–AC5 自检 | design.md §3–§7 逐条对照 Task 合同 AC 原文走查 | base=`fb5d56c6` / `c92eaddd` | 5/5 PASS（AC5 静态原型页=诚实省略非缺失） | `verification/M2-SFX-MISROUTE-UI-MITIGATION/ac-self-check.md` §1 |
| AC4 断言可测性 | A1–A13 逐条「可测？」自查（每条给了实现 Task 可构造的测试形态） | 同上 | 13/13 可测 | 同上 §2 |
| 领域语义准确性 | 改标语义表/领域事实六条逐一对照源码：`src/application/translation/context/gate.py:32-42`、`src/infrastructure/providers/detection_sfx.py:150-215`（`ARBITRATED_LABEL_PREFIX="sfx-arb-"` @202）、`src/bootstrap/core_assembly.py:1013-1049`、`src/domain/regions/entities.py`（RegionType 六值/RegionOrigin/SfxPolicy）、`src/application/editing/service.py` 方法清单（无 set_region_type） | base=`fb5d56c6` | 一致（行号已写入 design.md §2） | design.md §1.3/§2 |
| 契约现状对照 | M2-C1 rev 1.3 §3.1/§5/§5.3/§9/§10 逐节核对 D1–D10 | 同上 | D1/D9/D10 已承载、D6/D7 部分承载、D2/D3/D4/D5/D8 缺失→RC 候选 | design.md §5 |
| 禁改面自检 | `git status --porcelain` + `git diff fb5d56c6..HEAD --name-only` 核对 + `git diff --check` | 本 handoff commit | 改动面仅 Task/design/verification/handoffs 四处；`doc/contracts/**`、`src/**`、`src-tauri/**`、`apps/desktop/frontend/src/**`、`doc/STATUS.md`、token 真值零命中；`git diff --check` EXIT=0 | 本表 + 下节收尾记录 |
| NOT RUN：产品测试 | 零产品代码，无运行面 | — | NOT_RUN（预期，零 diff 自证） | `git diff` 清单 |

## 接收方式

- 分支 `agent/zcode/M2-SFX-MISROUTE-UI-MITIGATION`，worktree `G:/CODEX/New Manga.worktrees/M2-SFX-MISROUTE-UI-MITIGATION-zcode`，base=`fb5d56c6`，delivery=`c92eaddd`，本 handoff 在其后。
- Reviewer 复核指引（DSH 非作者静态 review，建议顺序）：
  1. **语义正确性**（最高优先）：design.md §1.3 改标语义表与 §2 领域事实六条对照上述源码锚点复核——尤其 manual 与 skip 同判 SKIP、policy 快照「仅新建 region 生效」scope、`sfx-arb-` 前缀 deliberately 复用 `startswith("sfx-")` 分发、BJ13 对仲裁不可达（sfx 通道零响应）四条，是 AC2/AC4 设计决定的因果基础。
  2. **断言清单判别力**：A1–A13 是否「违反即红」且无豁免口；重点压测 A2（BJ15 深盲形态：警示依赖 OCR 即失效）与 A6（反向改标模拟撤销的排除）。
  3. **契约缺口登记口径**：RC-1…RC-5 是否有未被登记的 widening 意图混入设计正文（本文立场：候选登记≠契约变更授权）。
  4. **视觉体系一致性**：E1–E4 token 引用与 UI 契约 §7.2 三重编码/叠加不合并/需校对虚线框保留三条规则无冲突。
- 复核不需运行环境；复核产出按 REVIEW 模板落 `doc/reviews/`。

## 下一任务建议（必填）

- Task ID / 标题：无既有 ready Task 可直接衔接；两个候选方向供编排裁决（都不由本 Handoff 创建占位 Task）：
  1. DSH Review 闭合 + Codex 集成本设计 Task（Review 通过后 status 流转 done）；
  2. 未来「Workbench React 页 + region/译文 IPC 通道」Task 释放时，RC-1…RC-5（design.md §5）作为 M2-C1 契约修订候选清单、A1–A13（design.md §6）作为该实现 Task 的 UI 验收输入。
- 推荐 Agent / Reviewer：集成/裁决=编排会话代行 Codex；实现=ZCode 或 Qoder（届时按合同分配）。
- 推荐原因与前置依赖：本设计的产品实现 blocked_on Workbench React 页面与 region/译文 IPC 通道存在（Task 合同「交付与运行记录」节原文），当前无可释放的实现前置。
- Recovery point：仓库 `G:/CODEX/New Manga`（worktree 同名 `.worktrees/`），branch `agent/zcode/M2-SFX-MISROUTE-UI-MITIGATION`，base=`fb5d56c6`，delivery=`c92eaddd`。
- 允许修改路径：实现 Task 届时按其合同；本 Task 剩余允许面仅 Review 返修（design.md/Task/Handoff/verification 本 Task 目录）。
- 禁止范围与新增授权条件：`doc/contracts/**` widening 须未来授权 Task 在 M2-C1 Revision history 登记；`doc/STATUS.md` 归集成方。
- 交付物：见上表；验证命令、环境与完成 Gate：DSH review verdict + 集成核验（零运行面，Gate=diff 面核对 + AC4 断言清单被实现 Task 引用无冲突）。
- 可直接转发给 Agent 的指令：「对 branch `agent/zcode/M2-SFX-MISROUTE-UI-MITIGATION`（delivery=`c92eaddd`）执行非作者静态 review：对象 `doc/design/M2-SFX-MISROUTE-UI-MITIGATION/design.md`，按本 Handoff『接收方式』四步复核顺序，verdict 与逐条发现按 REVIEW 模板落 `doc/reviews/M2-SFX-MISROUTE-UI-MITIGATION-<review_head>.md`。」

## 风险与遗留

- **EV-8（OPEN）改标后 policy 快照语义**：沿用创建时快照 vs 按当前配置重快照（类比新建语义）——UI 侧已按「显示 Core 返回的实际生效值」设计成两裁决兼容，但 Core 语义归 RC-2 契约修订裁决，未决前实现 Task 不得自行选择。
- **D8/RC-5 Reader 数据面**：Reader 页级提示条在字段落地前不渲染（不虚构数据）——若 Workbench 先行、Reader 投影后行，两场景上线节奏可能不同步（设计已按可分离交付组织）。
- **警示信号初始只有人工来源**：当前检测器对 BJ 形态零响应，heuristic 来源（EV-1）无近期落地计划；在此之前警示完全依赖用户逐页人工发现——本设计只承诺「可发现/可修正」，不承诺自动化发现（方案⑤立论边界，预期内）。
- **回退方法**：纯文档交付，回退=revert 本分支三个 commit（`8d844726`/`c92eaddd`/handoff commit），零产品面影响。
- 关联 Task：DOMAIN-EXT-DIAG（损害证据）、REGION-OVERLAP-ARBITRATION（`sfx-arb-` 前缀与仲裁不可达语义）、M2-SETTINGS-UI-SFX-POLICY / M2-SETTINGS-IPC-CHANNEL（设置页联动与 §5.3 通道）、M2-UI1（token 体系与 Workbench 组件映射先例）。

## 实验附录

不适用（纯设计交付，零实验、零运行）。
