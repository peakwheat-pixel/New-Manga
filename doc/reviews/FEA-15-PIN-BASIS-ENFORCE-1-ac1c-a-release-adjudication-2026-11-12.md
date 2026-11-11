核验完毕，证据链闭合。以下为裁决报告。

---

# FEA-15-PIN-BASIS-ENFORCE-1 · AC1c A 侧实测释放裁决（只读、上下文独立）

| 字段 | 值 |
|---|---|
| Task ID | FEA-15-PIN-BASIS-ENFORCE-1 |
| 裁决者 | ZCode 全新 CLI 会话（fresh session，仅本次只读裁决） |
| Session ID | `sess_72137bd6-9553-424d-b09f-4184866cd387` / `turn_fbce0bef-c175-43a1-a065-31fdc00180a7` |
| Reviewed HEAD（main） | `71de053288a37f7792db5e47e8e0ccf21dceaf82`（本会话 plan mode 禁止 git 子命令，HEAD 依派发固定上下文 + 工作树文件级证据，与 Addendum 4 §1 同口径） |
| A clone HEAD | `2df8db7a4d19b591e919ecc6e8f8651167800ef0`（`core.autocrlf=true`、clone-local `core.longpaths=true`，A 侧日志在册） |
| 输入 | Addendum 3/4、Task 卡、verification README、history-transition-ledger、`ac1c-a-gates-8d1d75ca.log`、当前治理脚本（check.ps1 / verify_pins.ps1）、`.gitattributes`、三份在册门禁日志（359d09d / cfa1866 / a18d21bf） |
| **结论** | **`ACCEPT_CONTINUE`** |

## 独立性声明

本会话为全新 ZCode 会话，未参与本 Task 任何实现（本 Task 尚无实现）、未参与主裁决及 Addendum 1–4 的撰写、未参与 A 侧测量。全程只读：未改任何文件、未重跑任何门禁/inventory/delta/matrix、未触碰 checker / 18 frozen pins / `.gitattributes` / 历史 evidence / A clone 配置。本会话不是 AC1d 基线确认会话，也不是最终 Review 或最终 adjudication 会话。

## 一、停止门命中说明（先行回答）

**命中。** Addendum 4 §8 停止条件全集含「外部或 EOL 行为异常」；A 侧 default/pins 的结果偏离 §5 所设预期锚（GOV-REFINCIDENT-1 clean 终态同文案），Owner 据此停止、保持 `blocked`、保留现场、原样记录 FAIL、不改任何配置规避——**处置完全正确**。§8 对命中的处置是「命中即停、保留现场、交 ZCode 再裁决」——本报告即该指定裁决。经逐项归因（下述），该「异常」不成立为异常：全部偏差可归约为两个已在册、确定性、可复现的机制类，无未归因残余。停止 hereby 解除，AC1c A 侧以本裁决修订后的预期锚为准通过。

## 二、结论论证：为何是 ACCEPT_CONTINUE（而非另两个选项）

- **不是 `STOP_REPRODUCTION_REQUIRED`**：测量内部自洽且算术精确（见 §三 E1：6992+64×1=7056 逐字节闭合），并与三组独立在册运行互证（`delivery-gates-359d09d`、`delivery-gates-final-cfa1866`、`ac1c-main-stop-gates-a18d21bf`）；机制有代码级定位（check.ps1:627/:679、verify_pins.ps1:23、`.gitattributes` r187 注释）。重跑不会产生新信息，且本会话被禁止重跑。
- **不是 `STOP_REQUIRE_ADDENDUM`**：偏差全部是 Addendum 4 已披露事实的**派生后果**——§2.4 已明示 A clone 为 fresh checkout、工作区 EOL 字节与开发主树不同并禁止 basis 跨环境断言；§7 已允许 clone-local 配置并课以记录义务（A 侧已全部履行：porcelain 前后、autocrlf、longpaths、HEAD、版本、逐命令 EXIT）。§8 的救济路径就是「交 ZCode 再裁决」，无需回到原释放会话另立 Addendum。没有任何未归因变化、没有任何冻结面被触碰、无需修改任何释放条件之外的东西。

## 三、关键证据与逐类归因

### E 类：`core.autocrlf=true` 工作树字节膨胀（环境机制，确定性）

**E1 Plan 防膨胀 FAIL（default + 全部四个 TaskPath 共有）**
- check.ps1:627 预算按**文件系统工作树字节**计（`Get-Item.Length`），预算 7000 bytes / 64 lines（:624）。
- `2df8db7` 的 Plan blob 为 6992 bytes（README 在册），64 行纯 LF；autocrlf=true checkout 后每行 +1 byte → 6992+64=**7056**，与 A 日志 FAIL 数字逐字节吻合；行数 64 未超限（仅 bytes 超限，与日志一致）。
- 同一 6992/64 在 **main 工作树**（无膨胀）上的先例即 Addendum 4 §5 预期锚本身：`delivery-gates-final-cfa1866.log` 中 GOV-REFINCIDENT-1 clean 终态 default **EXIT=0**，仅 `WARN … 已达到预算的 80%：6992 bytes / 64 lines`。A 侧输出与该锚**同文案结构、唯一差异即 EOL 膨胀的 64 bytes 与由此触发的 WARN→FAIL**。
- 仓内证据链：`.gitattributes` 存在多条逐路径 `text eol=lf` 规则，其注释**原文明示同一陷阱**——SEC-FIX-PATH-ECHO-1（"core.autocrlf=true would otherwise emit CRLF and break the pin"）、GOV-PLAN-BUDGET-1、P19-UI-MANIFEST-VIEW-1（"every pin fails on a fresh clone - the same trap"）、GOV-EOL-PIN-1 r187（"a clean clone would have made it all 320"）、REALUSE-DATA-SAFETY-7、FEA-08。而 `doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/plan/**`（契约草稿）**从未获得 eol 规则**——A 侧命中的正是这个未覆盖面。这是本仓已文档化、重复发生、已知修法的历史行为类，不是新异常。

**E2 verify_pins 16/18 MISMATCH**
- verify_pins.ps1:23 对 `doc/plan/` 下**工作树源文件**做 `Get-FileHash` 比对冻结记录中的 pin——纯工作树字节口径，无 blob 回退。
- 18/18 pins 在 main 工作树于 `cfa1866`（2df8db7 之前）与 `a18d21bf`（2df8db7 之后）两次全 PASS，pin 值完全一致 → 18 个契约源文件字节在整个窗口不变；A 侧 16 个 MISMATCH 的 actual 值差异只能来自 A 工作树字节（EOL），非内容漂移。
- C04b/C17 在 A 侧 PASS：属该冻结环境下未被转换的路径类；逐路径转换行为已由冻结基线工件本身刻画（A 侧 matrix `BASIS_COUNTS`：BLOB 749 / WORKTREE 3137 / MIXED 627 / UNRESOLVED_COMMIT 339 / INCONSISTENT 241）。本裁决不要求对单文件 git 内部转换行为作进一步解释。

**E3 FEA-06-PREREQ-1 的 5 条 Evidence SHA-256 不匹配**
- check.ps1:700–724（r194）为双基准：工作树 SHA **或** 行内 commit 的 blob SHA 任一匹配即过。A 侧失配证明工作树基准失配（`verification/FEA-06-PREREQ-1/**` 与 `apps/**` 均无 eol 规则 → 转换）；blob 基准亦未救回。无论这些行在无膨胀环境下是否可过，其失败均为冻结基线 + 固定配置的确定性输出，不构成历史字节变化。

### S 类：静态冻结基线事实（与 EOL、与工作树环境无关）

**S1 FEA-06-PREREQ-1**：`AppearanceCoordinator.cs` 路径缺失（check.ps1:679 为工作树 `Test-Path`；该文件**在当前 main 也不存在**——历史路径已迁移的树事实）；evidence_dir 含 3 个未登记文件；DONE 纪律 4 条（canonical_evidence_status / resource_closeout_status / Resource Manifest / closeout）；PARTIAL AC1/AC3/AC5 3 条。全部为旧 done 卡在演进后 checker 下的静态卡面/树面事实。
**S2 CHAPTER-SELECTOR-1**：Resource manifest 残缺行 1 条 + AC1–AC5 状态标记缺失 5 条——M2 时代旧卡格式先于 `<<MET>>` 标记约定（`doc/tasks/*.md` 有 r187 eol=lf 规则，卡面为 LF，与 EOL 无关；旁证：AGPL/AD002 两张较新卡的全部卡级检查通过）。
**S3 首测记录而非判定翻转**：就现有在册证据，四个代表历史 TaskPath 在当前 checker 代下**无任何先例运行记录**（359d09d 只跑过 FEA-15-PIN-EOL-GOV-1；recovery/a18d21bf 只跑过本卡），故不构成 §8 的「旧行 checker 判定**变化**」，而是首次在册判定。若 Owner 掌握相反在册记录，须先提交再复议本条。

### 残余

无。15+7+1+16 条失败全部落入 E/S 两类；AGPL-RELEASE-1 与 AD002-FOLLOWUPS-1 除 Plan budget 外**全部卡级检查实际通过**。不变性层不受污染：正式不变性基线是 inventory/delta（`ADDED=62 / REMOVED=0 / CHANGED=2` 已由 Addendum 4 接受为一次性衔接），门禁层结果不进入跨环境不变性断言。

## 四、实际通过 / 失败 / NOT_RUN（严格口径）

| 项 | 实际结果 | 裁定 |
|---|---|---|
| A default | **EXIT=1**（仅 Plan budget 7056/64） | 真实 FAIL；归因 E1；接受为 A 环境基线特征输出，**不改写为 PASS** |
| AGPL-RELEASE-1 / AD002-FOLLOWUPS-1 TaskPath | **EXIT=1**（仅 Plan budget） | 同上；卡级检查实际通过 |
| FEA-06-PREREQ-1 TaskPath | **EXIT=1**（15 errors） | 真实 FAIL；E3+S1 |
| CHAPTER-SELECTOR-1 TaskPath | **EXIT=1**（7 errors） | 真实 FAIL；E1+S2 |
| verify_pins | **EXIT=1**（16/18 MISMATCH；C04b/C17 OK） | 真实 FAIL；E2；16 个 actual 值**永不**登记为新 pin（禁止 pin 迁移） |
| API inventory | **EXIT=0**，1/79/6=86 | 实际 PASS，与 359d09d/cfa1866 完全一致 |
| 固定边界矩阵 | **EXIT=0**，SHA `e8c48163…`；wrapper `e4300b7b…` 与在册一致；`MODELED_R194=ACCEPT 4513 / NONPASS 925`，TOTAL 5438 | 实际 PASS（矩阵为 r194 predicate 模拟，非逐行 check.ps1——按其自述口径采信） |
| **NOT_RUN** | AC1b/B 侧全部（R0 断言、B TaskPath）；AC2、AC3、AC4（含 autocrlf=false 对照与 Linux）；AC5（集成门禁、独立 Review、终裁）；R-001 终裁 | 全部保持 NOT_RUN，**不得写成 PASS** |

A 侧无 NOT_RUN 项：Addendum 4 §5 所列五类（default、四 TaskPath、18 pins、API、矩阵）全部实际执行并逐项记录 HEAD/clean/环境/EXIT。

## 五、对 `core.autocrlf=true` 下 EOL / 历史 evidence / pin mismatch 的裁定

1. **A 侧 FAIL 为环境读数，非历史变化**：blob 层不变性成立（Plan blob 6992<7000 与锚先例同数字；18 契约源字节经 cfa1866/a18d21bf 双侧夹逼不变；porcelain 仅 Task-local untracked JSON）。不构成「旧行 checker 判定变化」，不触发任何历史修复义务。
2. **A 侧 FAIL 是该冻结环境的规范输出**：固定 clone + 固定配置 + 冻结基线下完全确定；今后任何同配置复跑必须逐字节复现本组结果（这正是其作为 A 侧基线的复现锚性质）。反向：若复跑出现**不同**结果，才是新停止事件。
3. **跨环境断言口径延伸**：Addendum 4 §2.4 对 `basis` 的跨环境排除，同构延伸到门禁层——Plan 预算、evidence SHA、verify_pins 均为工作树字节敏感检查，任何「门禁结果不变性」断言只能建立在 blob 基准或同字节环境之上。AC4 的 autocrlf true/false 对照是把本裁定形式化的指定场所。
4. **已知修法本轮禁用**：为 `doc/plan/**`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md` 补 `eol=lf` 规则是该陷阱类的既有修法，但 `.gitattributes` 属本 Task 冻结禁区——缺口仅登记为未来授权 Task 候选，本 Task 及 B/AC1d 阶段一律不得实施。

## 六、预期锚修订（本裁决对 Addendum 4 §5 default 锚的精确化）

A 侧 default 的预期锚由「GOV-REFINCIDENT-1 clean 终态同文案（main 工作树）」精确化为：**同一文案结构下，`core.autocrlf=true` fresh checkout 的确定性推论**——Plan 行表现为 `FAIL 7056 bytes / 64 lines`、EXIT=1；pins 表现为 16/18 MISMATCH（C04b/C17 OK）；API/矩阵 EXIT=0。实测与该修订锚逐项相符，**AC1c A 侧判定为满足**。`CHANGED=2` 一次性衔接维持原样登记，永不归零。

## 七、R0 冻结与 B 侧执行条件

1. **R0 := 本裁决落盘 + 卫生项闭合 + Task 卡恢复（`blocked→in_progress`、移除 blocked_reason、AC1 引用本裁决）+ STATUS 当前指针 + Plan 节点确认，一并提交入 main 后的 HEAD**（Addendum 4 §5 定义应用于本次恢复动作）。
2. **B 侧环境裁定**：B clone 须在 checkout 前设置 clone-local `core.autocrlf=false`（与 §7 允许 clone-local `core.longpaths=true` 同构：仅 clone 本地 config，不触碰任何 commit/tree/blob/保护面），并照实记录。理由：main 全部在册门禁均在无膨胀字节环境下通过；B 的目的（R0 载体 + 本卡 TaskPath）要求 Addendum 3 §4「TaskPath EXIT=0」确定性可达。若 Owner 改以 autocrlf=true 跑 B，Plan budget FAIL 将确定复现并直接触发 §4 停止门，该路径**不予放行**（除非另行裁决）。
3. B 侧仍只做：§5 文件级在场断言、`R0..2df8db7` 反向差异全落在释放允许增量集、`tools/governance/**` 与 `doc/templates/**` 逐文件 blob 同一、clean/环境记录、仅运行本卡 TaskPath（预期 EXIT=0）。**不得**在 B 重复 inventory/delta/repro、历史 TaskPath 或样本矩阵；不得写仓内路径。

## 八、卫生项（非阻塞，in_review 前必须闭合）

1. **ac1c-boundary-matrix 自 pin 疑点**：Task 卡该行 pin `68ec4b50…` 与 README 及 A 日志一致记录的 `e8c48163…` 不一致；本会话受 plan mode 限制无法哈希核验。Owner 须以 `Get-FileHash` + `git cat-file blob 6086a5b1f…:verification/FEA-15-PIN-BASIS-ENFORCE-1/pin-r194-matrix-2df8db7.json` 双基准核验：blob 基准命中 `68ec4b50…` 则在卡内补注 basis 说明；否则将行内 pin 修正为实测值（卡文件属 allowed_paths；**不得**改动矩阵 JSON 本身字节）。因证据行校验仅对 in_review+ 状态生效（check.ps1:669），此项目前不阻塞 B/AC1d，但阻塞 AC5。
2. **ac1-addendum4 行 pin 为全大写**：checker 于 :676 先 `ToLowerInvariant` 故不会报格式错误，但与全表小写约定不一致，恢复卡状态时一并规范化。

## 九、允许的下一步（最小且合规；不授权任何实现）

AC1d 独立基线确认通过前，模板/checker/test 实现提交禁令不变；R-001 不因本裁决关闭；A clone 及其产物维持 `PRESERVE_REFERENCED`。建议下一 Agent 为 **Owner=Codex**，可转发指令：

```text
Task FEA-15-PIN-BASIS-ENFORCE-1（Owner: codex）。ZCode AC1c A 侧释放裁决已出：ACCEPT_CONTINUE（报告待存 doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-ac1c-a-release-adjudication-2026-11-12.md，回填 session/turn id）。按报告执行：
1) 落盘裁决报告原文；
2) Get-FileHash + git cat-file 双基准核验 ac1c-boundary-matrix pin（68ec4b50 vs e8c48163），按裁定修正卡行或补注 basis；规范化 ac1-addendum4 大写 pin；
3) Task 卡 blocked→in_progress、移除 blocked_reason、AC1 更新为引用本裁决的 PARTIAL、Rolling Checkpoint 追加；STATUS 当前指针与 Plan 节点确认；
4) 一并提交入 main，该 HEAD 即 R0；
5) 建 B clone @R0（checkout 前 clone-local core.autocrlf=false、core.longpaths=true，全部记录），执行 Addendum 4 §5 断言集（文件在场、R0..2df8db7 反向差异在允许集、tools/governance/** 与 doc/templates/** 逐文件 blob 同一、clean/环境），只运行本卡 TaskPath（预期 EXIT=0），逐项记录；
6) 完成后派发 AC1d：fresh ZCode 会话（不同于本裁决会话、最终 Review 与最终 adjudication），输入=repro anchor、正式 inventory/delta、history-transition-ledger、A 侧 gates、B 侧 R0 断言与 TaskPath 结果。
禁止：任何模板/checker/test 实现（AC1d 通过前）、修改 18 frozen pins/verify_pins.ps1/.gitattributes/历史字节、pin 迁移、把 NOT_RUN 或 FAIL 写成 PASS、清理 A clone。B 侧不得以 autocrlf=true 运行（如需变更须再裁决）。
```

---

**推荐下一步**：由 Codex 按上述可转发指令落盘本报告并冻结 R0、执行 B 侧；随后以全新 ZCode 会话完成 AC1d。本会话不写仓库、不承担 AC1d 或最终 Review。