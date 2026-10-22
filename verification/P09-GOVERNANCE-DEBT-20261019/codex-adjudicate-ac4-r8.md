# GOV-RESOURCE-MANIFEST-JSON-1 AC4 裁定 R8

日期：2026-10-19  
裁定人：Codex / Lead / Architect / Integrator / Reviewer  
对象：`GOV-RESOURCE-MANIFEST-JSON-1`，交付候选 `7350da5e91b380862de4dc61009bd945ad193e03`

## 3.1 AC4 判据裁定

**裁定 D（AC4 的计数语义按 A 接受）：AC4 满足。** 对本案，`closeout_counts` 是处置动作总数；`resources` 是需声明去向的资源对象清单。两者不是同一计数总体，动作总数可以包含未列入 `resources` 的证据日志。因此，`moved: 6` 与 7 个资源项的 `moved: false` 并不构成数据错误，也不要求二者算术相等。

R3 §2 判据 4 的“逐一对应”在本 Task 中解释为：解析必须保留原 JSON 的全部 7 个资源项，并逐键保留 `closeout_counts` 的 4 个声明值；解析结果不得丢项、增项、重项、改写表达式或更改计数。这里的“计数不一致”指解析视图未忠实保留原 JSON 的计数，或计数字段本身不符合 schema；它不要求将动作总数与资源数组中的布尔值强行等同。该解释由原清单 `closeout_note` 对 6 个证据日志改名的明确说明支持。

本结论只裁定该源 JSON 的只读核对和本 Task 的 parser/schema 语义，不授权改写历史 JSON。无需新增 6 个资源项，也不得改 `closeout_counts`。AC4 记录中的四个花括号表达式均已证明可逐字逆向重组，11 条拆分路径保持字符串级原文，`%APPDATA%` 不展开；7 个资源项及 4 个计数键均保留。AC4 可标记满足。

**不生成 P19 解析视图文件。** AC4 在这里要求核对；P19 兼容视图及其 Task 检查重跑明确属于后续 Task，且不在本 Task 的 `allowed_paths` 内。保留现有只读核对证据即可，不增加待维护产物，不改变 P19 原文件。

## 3.2 对 closeout_counts 规则调整的复核

**概念裁定：接受这项规则修正，不视为为迁就检查器而放宽。** 严格要求动作总数等于资源布尔计数，会错误否定一份由日志改名动作准确说明的历史清单。schema 说明此语义、离线用例允许“声明值与资源布尔计数不同”，与本裁定一致。

但规则调整只取消两种口径之间的算术等式；它没有取消字段契约。进入 Review 前，DSH 必须确保检查器对 `closeout_counts` 的四个键逐一检查：键必须存在、值必须是 JSON 整数且非负；缺键、字符串/浮点/布尔等非整数值及负值均应失败。差异应作为可见的非阻塞 note 输出，不能静默吞掉。当前候选源码中，差异已加入 `Notes`，但主检查流程尚未消费/输出 `checked.Notes`；且对缺键的 `[int]$null` 转换可能得到 0。因此，目前不能仅凭 schema description 与用例 9 宣称运行时检查满足上述字段契约。DSH 应在本 Task 允许路径内补齐并用离线用例验证。

## 3.3 DSH 完成 Task 并进入 Review 的顺序

1. 更新 `verification/GOV-RESOURCE-MANIFEST-JSON-1/ac4-brace-and-counts.md`：引用本裁定，将 AC4 结论改为满足；说明 `moved: 6` 是 resources 数组外的 6 个日志改名动作；记录解析保真要求、无需生成解析视图及 P19 JSON 未修改。不要改 P19 的源 JSON。
2. 在 Task 允许路径内补齐 `closeout_counts` 运行时校验和 note 输出：严格检查四键存在、JSON 整数、非负；资源布尔数与声明值不同只输出 note、不判失败。保留现有 schema 语义，不把差异从“note”改成“错误”。
3. 补齐独立落盘的 AC4 离线 fixtures/断言：至少包括可逆花括号拆分保真、不可逆/歧义表达式拒绝或阻塞、声明计数与资源布尔数不同但接受并输出 note、缺键/非整数/负数拒绝。fixture 与运行器仍在 `tools/governance/tests/**`；不得触碰 P19 源文件。然后重跑完整离线集，记录环境、命令、每例 stdout/stderr/exit code 和总退出码。已有 16/16 结果不能代替新增 AC4 覆盖及复跑证据。
4. 更新 `verification/GOV-RESOURCE-MANIFEST-JSON-1/ac1-ac5-manifest-support.md` 和 Task 的 AC/验证记录，使 AC1–AC5 状态、实际测试数和任何限制与当前代码及证据一致；保留未运行/阻塞项原状，不把计划写成通过。
5. 固定最终 delivery head，按 Task 模板更新 Handoff；为进入 `in_review` 所需的每项已释放 AC/Gate 准备唯一 canonical evidence、路径、含文件的 commit、SHA-256 与分类。确认变更仅在 `allowed_paths` 内，且没有未解释的源文件改动。
6. DSH 在交付 head、AC 证据和 Handoff 齐备后请求进入 `in_review`；由 Reviewer **Antigravity** 对该精确 head 独立 Review。DSH 不审查自己的实现。Review 通过、Codex 集成验证与资源 closeout 完成前，不标记 Task `done`。

## 状态与依据

本裁定依据 `verification/P09-GOVERNANCE-DEBT-20261019/codex-integration-closeout-r3.md` §2、指定 worktree 的 AC4 与 AC1–AC5 证据、P19 原始 JSON、当前 schema/checker/fixtures，以及 `GOV-RESOURCE-MANIFEST-JSON-1` Task。P19 原始 JSON 按只读来源处理。