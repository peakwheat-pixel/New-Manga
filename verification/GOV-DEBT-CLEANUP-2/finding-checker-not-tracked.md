# 发现：治理检查器 `check.ps1` 未受版本控制

**发现人**：Codex（在 `codex-release-two-r4.md` 中报告）
**独立复核**：dsh（本文档）
**复核时点**：HEAD `4c1b7bbfd`
**性质**：治理基础设施缺陷，非本 Task 交付物的缺陷

## 事实

`tools/governance/check.ps1` 是本项目全部治理检查的执行者——`doc/tasks/*.md` 的 300 个文件、
Plan/STATUS 指针、证据 pin、Resource Manifest 都由它判定。**但它从未进入版本控制。**

复核命令与结果：

```powershell
git ls-tree -r --name-only HEAD -- tools/governance/     # -> 0 行
git log --oneline -- tools/governance/check.ps1          # -> 无历史
git status --porcelain -- tools/governance/check.ps1     # -> ?? tools/governance/check.ps1
Test-Path tools/governance/check.ps1                     # -> True（磁盘上存在）
```

影响范围核实（不是整个 `tools/` 都未入库）：

| 文件 | 是否入库 |
|---|---|
| `tools/governance/check.ps1` | **否（untracked）** |
| `tools/p02/p02-new-time-baseline.ps1` | 是 |
| `tools/p02/p02-new-time-baseline-selftest.ps1` | 是 |

即：`tools/` 下 3 个文件中有 2 个已入库，**恰好是治理检查器这一个例外**。

## 为什么这很严重

1. **所有治理结论不可追溯。** 本项目多轮记录过「治理检查 PASS/FAIL」，例如本 Task 的
   `verification/GOV-DEBT-CLEANUP-2/ac9-governance-output.txt`。这些结论依赖检查器的具体实现，
   而检查器没有 commit，无法证明「当时的 PASS 是用哪一版规则判出来的」。
2. **规则可被无声修改。** 任何人改动 `check.ps1` 在 Git 层面不留痕迹。项目明令「不得放宽检查器
   规避预算」（见 `GOV-DEBT-CLEANUP-2` 的禁止范围），但这条禁令在技术上无法被审计执行。
3. **基线不可复现。** Codex 在 r4 中指出：因该文件未被 HEAD 跟踪，**"当前 HEAD 不能作为正式
   Task 的基线"**。这意味着任何以「修改 `check.ps1`」为范围的 Task（例如待释放的预算维护 Task）
   在现有状态下都无法建立可复现的 base/delivery 对比。
4. **与本轮工作直接相关。** 本 Task 的 AC3 记录「用户批准把预算从 2500/35 改为 7000/64」，
   该改动对象正是一个未入库文件。

## 本 Task 没有做什么

- **未执行 `git add tools/governance/check.ps1`**。把一个未受版本控制的治理检查器首次入库，
  属于对治理基础设施的实质性变更，不是「记录事实」，需独立授权与独立 Task。
- **未修改该文件任何内容**（本 Task 全程未改 `check.ps1`，见 `ac3-budget-decision.md`）。
- **未因该发现推翻任何既有结论**。已有的 PASS/FAIL 是在当时那版检查器下真实得到的；
  本文档只指出这些结论缺少可追溯的规则版本，不声称它们错误。

## 建议（需 Codex / 用户裁定，不在本 Task 授权内）

1. 将 `tools/governance/check.ps1` 纳入版本控制，并对当前磁盘内容记录其 sha256 作为「首次入库版本」。
2. 在 `GOV-DEBT-CLEANUP-2` 或后继 Task 的 Canonical Evidence 中，把**检查器版本**（commit + sha256）
   与检查输出一并固定，使 PASS/FAIL 可复现。
3. 在此之前，凡以「修改 `check.ps1`」为范围的 Task（含待释放的预算维护 Task），其 base_commit
   应指向**包含该文件的**提交，而非当前 HEAD。
