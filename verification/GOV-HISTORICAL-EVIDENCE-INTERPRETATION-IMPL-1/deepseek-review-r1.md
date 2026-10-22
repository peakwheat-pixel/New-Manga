---
task_id: GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1
author: DeepSeek Harness
base_commit: d760caeb6
reviewed_head: 090bed6f61fceb07267cb1a46de314380e9205fd
decision: changes_requested
---

## 结论

**changes_requested**

- `source base = cc6387d660d6970c4e71c996f479e9e7c6af8674`
- 实际 `diff_base = d760caeb6`
- `reviewed_head = 090bed6f61fceb07267cb1a46de314380e9205fd`
- `delivery = c4c44d4978c68879aed83537926ff184cd9ebb54`

实现主体、候选效果、21 EV、Owner 的 145/0 与双回放均成立，但存在一个 **P1：发布末检没有重新验证两个 reference guard 目录的存在性与目录类型**，只复核了 real。该缺口违反已批准设计的“发布前复读…两个引用目录核存在性/目录类型/real”的 fail-closed 要求，故本轮不能批准 merge。

## P0 / P1 / P2

### P1（阻断）

**P1-1：reference guard 的最终存在性/类型检查缺失**

- 位置：
  - `tools/governance/clean_workspace.py:1750`：初始 `guard_identity` 仅在这里检查 `os.path.isdir(...)`。
  - `tools/governance/clean_workspace.py:1942-1944`：发布前最终 `targets` 循环只调用 `resolve_real_target(root)`，没有再次检查 `os.path.lexists` / `os.path.isdir`。
  - 测试缺口：`verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/tests/test_historical_evidence.py:302-321` 的 T15 只注入 real 漂移；`:248-253` 的 T11 只测初始目录缺失。
- 触发：在初始 `guard_identity` 之后、`_finish_declaration_scan`/最终 `targets` 之前，删除或把 `tools/governance/tests`、`verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1` 替换为普通文件。
- 影响：Windows `resolve_real_target` 对缺失路径仍返回同一 lexical/real 路径，最终检查通过；helper 会移除 5 个错误、登记 6 条 Declaration，并报告 7 错误，而不是 `SOURCE_DRIFT` 并保留原 12。引用根已不存在/类型错误却被报告为 `PRESERVE_REFERENCED`，不是 fail-closed。
- 修复建议：最终阶段对两个 reference guard 重新执行 `os.path.lexists` + `os.path.isdir`（或让 `targets` 记录 guard kind，final loop 按 kind 检查），不新增 Declaration、不改变 `+6/+4`；增加 T15 的“初始验证后删除/替换 reference 目录”负例，断言 `SOURCE_DRIFT`、原 12 错误和原容器不变。

### P2

1. **broad policy 未被固定摘要绑定**：`tools/governance/clean_workspace.py:1777-1781` 读取并验证 broad policy 的 12 角色/五根输出，但没有像自身策略那样校验 broad policy 的 approved canonical/raw SHA。若 broad policy 被替换为另一份仍自洽、仍有 12 角色/五根的 tracked 策略，historical Gate 会接受它。当前 canonical broad 正确，但建议在实现中冻结 broad canonical/raw 常量或明确绑定已审 commit。
2. **candidate-effect 的 1895 是 EV 前快照，不是当前实时值**：`candidate-effect.json:29,44,207` 记录 `old/new protected_roots=1895`，Task 运行记录也写 1895；当前 canonical（21 EV 后）实际为 old/new `2611/1916 → 2617/1916`，比快照多 21 个 EV 根。建议在 Task/report 中明确“1895 为 EV 登记前快照”，不要作为实时保护根数；这不影响“旧保护是当前集合子集”的结论。
3. **最终 line227 只复核 real**：设计已明确 line227 是第 7 个 real 复检对象；当前代码满足 real，但没有复核其目录类型。若按 P1 修 reference 目录类型，可顺带明确 line227 的类型是否属于契约；当前不单独阻断。

## Architecture

- 变更范围符合冻结：只改 `tools/governance/clean_workspace.py` 共享尾部、新 `historical-evidence-interpretation.json`、本 Task E/Task/Handoff/权威导航；`read_text`、69 例外、三消费者、旧源/旧 pin/产品代码未改。
- 单 helper 在 broad 收口之后调用；broad fatal 原样返回；自身 policy absent+untracked no-op；自身 enabled 时要求 broad tracked、无 broad fatal、12 个完整 role warning/Declaration 唯一、五根保护在；否则 `DEPENDENCY_INACTIVE`，原错误全留。候选实测 broad inactive 为 `13 errors`（原 12+1），不是 24→19。
- 使用内置 canonical 摘要 `3f4cae13b0848ed105b5ba59c7538c8456c991b1403596ca64b68b63381e4b7d` 绑定完整策略 schema/值；重复 JSON 键、未知键/类型、tracking/raw/real/C0/UTF8/parse 快照、模板 fence/rows、line227 原声明、两个 reference guard 均被验证。
- 原子暂存复制所有 mutable 容器/scanned；只移除 5 个完整错误，新增 6 Declaration/4 warning；失败只在原输入 +1 fatal；无原 index warning 副作用。
- 候选同 canonical 实测：old `12 / 2611 / 1916 / 272` → new `7 / 2617 / 1916 / 276`；恰移除 5、其余 7 完整 identity 不变，`+6 Declaration/+4 warning/+0 protected root`，旧保护子集、`scanned` 一致；四源 raw SHA 与 P22 untracked 不变。

## Verification

**实际执行（只读/stdout，无文件写）**

- 旧模块 vs WT 新模块对 canonical 同数据 scan：上述 12→7、+6/+4/+0、旧 subset、scanned 一致；移除的 5 与 policy 五错误完整对象匹配；剩余 7 与 old 减 5 完全相等。
- 21 EV 逐项 `raw = blob = pin` 全部成立；Task 实际 `EVIDENCE_PIN 21 / errors 0`。
- policy canonical 摘要 `3f4cae13…` 与代码常量一致；policy 在 canonical/WT 均 tracked，raw SHA 同为 `1499ddcf…`；两个 reference 目录、四源、line227 当前均 exact 受保护。
- broad 证据：12 条 `DECL_BROAD_ROOT_PRESERVED`、broad policy tracked、无 broad fatal；代码按 warning 的 file/locator/role/root 对应 12 个完整 Declaration，未使用两源 83 声明总数（T18 已覆盖）。
- 纯内存负测：broad inactive → `13 errors`、`DEPENDENCY_INACTIVE`、declarations/roots/warnings 不变；第 6 次 staging 失败 → `13 errors`、`POLICY_INVALID`、原容器不变；重复 broad marker → `DEPENDENCY_INACTIVE`、无部分发布。未创建任何 fixture/临时文件。
- `verify_effect.py` 只读运行：**exit 0 / PASS**；baseline 1895 保护集合是当前 new 集合子集，old 12、new 7、五移除、四 SHA 均通过。
- canonical `check.ps1`：**PASS（2 个既有 warning）**；`git diff --check d760caeb6..090bed6f`：**exit 0**。
- WT `status --porcelain` 为空；`tools/**` 仅共享 scanner 改动；canonical 旧代码不含 helper，正式 12 未提前改变。

**Owner 证据（只读核对，未由我复跑）**

- `new18.log` 18、`broad18.log` 18、`declaration29.log` 29、`hardening80.log` 80，均 `OK` / `EXIT=0`，合计 145 / 0 skipped。
- `replay-clean.log` / `replay-remove.log` 各 `15 rejected / 0 deleted / 0 violations`。
- `candidate-effect.json` old 2590/1895→new 2596/1895、12→7、+6/+4、五移除、四 raw SHA；`declaration-audit`、`clean-workspace-refused`、`worktree-removal-refused` 均为 7 错误；`new18-first-attempt.raw.log` 保留初败，未隐藏。
- `execution.json` raw/canonical hash 与实际日志一致。

**NOT_RUN / 剩余风险**

- Reviewer 未复跑 18/145 fixture（会创建临时目录，明确 NOT_RUN）；Owner 的 145 仍为 Owner 实测，不是我的复跑。
- 未执行真实 canonical 全盘 consolidate、产品构建/测试、103 分支/141 WT 全量资源/句柄盘点、真实 apply/cleanup。
- P1 的最终目录类型/存在性竞态未由测试覆盖；P2 的 broad 摘要绑定未冻结；1895/1916 快照口径需继续区分。

## Merge Gate 与范围

当前 **不可 merge**。需先修复 P1（final reference guard 存在性/目录类型；建议同时补 T15 负例），重新生成固定 head 和 EV 后再交 DeepSeek 复审；之后 Codex 正常 merge/main 复验、资源原位核销才可 done。

本 Review 只针对本 Task 的精确历史解释实现，不批准运行例外、原件修改、P22 接管、真实 cleanup、父 Task done、r212 解除或 push；103 heads/141 WT 全部保留。

真实CLI exit0；session-0fa5098c-d90a-465f-b919-9eb52e3b8418；cwd canonical，web_visibility=unverified。原始JSONL G:/CODEX/New Manga.workspace/agent-output/codex/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/review-r1.jsonl SHA-256 eab708de61925acb1394245d47779f0e3b6b26226740b7b70d40fb64d8cbe2b4。
