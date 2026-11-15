---
task: E9
adjudicator: zcode (subagent agent-6, independent context)
adjudicated_head: 1984eaf6e
verdict: SCHEME_E
date: 2026-11-15
---

# E-9 解锁裁决（ZCode）

## 裁决：**方案 E（新）** —— 判别"文件型注册根"，直接用 `roots[0]` 作容器路径。
**A / B / C / D 均不采纳。**

## 一、裁决者核实的代码事实（并推翻 DSH 的前提）

| 裁决者查证 | 结论 |
|---|---|
| `SourceImportModels.cs:243-252` `RegisterRoot(path)` | `roots=[path 本身]` |
| `SourceImportModels.cs:800-809` `IssueGrantsAsync` | `var path = Path.GetFullPath(source.Path)` → `FindOrRegisterRootAsync(path)` → `IssueAsync(..., path, kind, ...)` ⇒ **registry root 与 sourcePath 是同一个值** |
| `SourceScanScheduler.cs:1640-1658` | sync 扫描链同样以**容器文件路径**调 `IssueAsync` |
| `Fea11HostAuthIpcTests.cs:340-342` | 测试注释直言 *"Production registers ONE root == the user-selected SOURCE (the container file itself)"*，并注册 `[newZip]` |

**⇒ DSH 的核心前提「zip 源 root == 父目录」与代码不符。**
非 folder 源的 `roots[0]` **本来就是容器路径**，**不需要任何新的持久化**。

`MintRecoveryGrantsAsync`（`SourceOperationCoordinator.cs:294-297`）在**没看 `roots[0]` 是文件还是目录**之前
就做 folder-only 拒绝 —— 属**过度保守**，**不是**"正确的自我保护"。
`AcknowledgeAsync:468` / `RecoverAsync:581` 同径，确认**正常 ACK 也被挡**（不只是崩溃恢复）。

**技术可行**：`SourceSecurity.Contains:120-121` 在 `root == path` 时成立 ⇒ `Registry.Authorize` 可验文件根；
`IssueLockedAsync:563-575` 对文件路径 `DescribeContainer` / 物理 facts 正常；单可读根约束（R-r2-03, `:277`）已在。

**方案 A 的契约面判断虽对（Host 私有 Registry 本就持久化 roots 绝对路径，`SourceAccessRegistry.cs:8`），但没有必要** ——
它要解决一个不存在的问题。B/C 需 UNFREEZE 且撞 C-17 §5.2 绝对路径禁令，确认不可行。

## 二、是否值得做：**值得**

- **用户价值**：zip/cbz/pdf 是 C-16 冻结的五种 kind 之一、**AD-003 ReferencedSource 引用导入的主场景 —— 首发已支持，不是边缘**。
  E-9 挡的是**正常同步完成链**（不是崩溃边角）：apply 后 ACK 必败 → gate 停 pending → 新 binding 永不可读。
- **风险**：方案 E 比现状**更安全** —— 授权落在**注册时用户亲选的那个文件**上（现状 folder 也只是目录级）。
  残留风险仅"目录 root + 容器 kind"的手工注册组合，**判别分支兜得住**。
  方案 A 反而引入新状态文件与 registry 的漂移面。
- **成本**：**一个判别分支 + 测试翻转**，远小于 A（新持久化类 + 安全审查）、远小于 B/C。

## 三、落地要求

1. **`MintRecoveryGrantsAsync`**：
   - `sourceKind == "folder"` → 走现状；
   - 非 folder 且 **`File.Exists(roots[0])`** → 以 `roots[0]` 为 `sourcePath` 重铸
     （**identity / 物理 facts 验证链原样保留，fail-closed 不变**）；
   - `Directory.Exists(roots[0])` + 容器 kind → **维持 `SOURCE_PLAN_UNAVAILABLE`** typed 拒绝。
2. **E9 登记文件随实现回退**；4 个被挡测试**翻回正向断言**（含 `CrashPoint_Recover`）；
   **`crash-ack.ps1` 须实测达到 `CRASH_POINT=SATISFIED`**。
   落地前维持现状：已改造的 3 个**不放宽**，`CrashPoint_Recover` **保持红**。
3. **交付须含**：zip 正向恢复用例 + "目录 root + 容器 kind 仍 typed 拒绝"的**负例**；
   **契约零改动**（`verify_pins` 18/18 不动）。

## 四、一句话结论

**路径不在别处、就在 registry 的文件型根里 —— 一个判别分支即可解锁，不必新增任何持久化或动 C-17。**
