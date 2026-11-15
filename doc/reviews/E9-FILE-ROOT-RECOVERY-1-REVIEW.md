---
task: E9-FILE-ROOT-RECOVERY-1
reviewer: zcode (subagent agent-7, independent context, read-only)
reviewed_head: d756393a5
verdict: ACCEPT_WITH_LIMITATIONS
date: 2026-11-15
---

# E-9 修复落地独立复核（ZCode）

## 结论：**ACCEPT_WITH_LIMITATIONS**

实质交付（判别分支、crash PASS 证据、负例固定、fail 性质澄清、审计）**全部独立复核为真**；
limitations 仅限**表述精度与枚举边界**。

## 逐条判定

| 主张 | 判定 | 复核者给出的依据 |
|---|---|---|
| **A** 判别分支等价比 | **成立** | `SourceOperationCoordinator.cs:204` 谓词 = `folder(Ordinal) \|\| File.Exists(root)`，调用点 `:312`；与 366704138 的 inline 条件经 diff 逐字比对为 **De Morgan 等价，无语义漂移**。`Ordinal` 大小写敏感沿袭文件内既有惯例，kind 由 Core 权威下发（C-16 冻结小写枚举）；`roots[0]` 空白时 `File.Exists` 返回 false → typed 拒绝，**fail-closed 正确** |
| **B** crash-ack 转 PASS | **成立** | `crash-ack.ps1:203-266` 的 10 项 CHECK **全由 park/recover 数据计算**，任一失败即 `FAIL+exit 12`；**归档目录只在全过后才创建**（`:268-288`）⇒ 目录存在即 PASS 路径真实执行。复核者**独立复算** 10 项全成立（pid 14064→29708、session 6348→53b5、sha256/db_counts 相同、grant 无交集、`second_call=recovered, frames=0`、gate_open=true）；`source_path` 确为 `source-v2.zip`（E-9 场景本体）；pids-after 为空；wire 日志含 `CompleteSourceOperationRecovery`、**0 个 `SOURCE_PLAN_UNAVAILABLE`** |
| **C** 负例判别力 | **基本成立，表述不精确** | 见下节 |
| **D** fail 不转 skip | **成立** | 前置断言属实（`:213/271`）；"不得新增 skip"有出处（`checkpoints:2311`）；第三种做法（Trait 分类/独立 playlist）技术上存在但**比 skip 更隐蔽或改"全量"语义**，不优于保持 fail + 文档固定读法 |
| **E** 阻塞项回溯 | **Gate 范围内成立，枚举边界有小漏** | 见"漏掉的开放项" |

## ★ 判别力核实：kill count 是 **5/6**，不是 4/6

无条件 `true` 时**真的变红**的是 **5 个**：

- 4 个 Theory（`DirectoryRoot_ForAContainerKind_StaysRejected` 的第一半 `Assert.False` 红）；
- **加上** `ContainerRoot_MustBeAnExistingFile` —— 其第一半
  `Assert.False(IsRecoverableRoot("zip", 不存在的路径))` **同样必红**。

**不红的是** `FolderRoot_IsAlwaysUsable_BecauseTheRootIsTheContainer` ——
但它的**判别方向相反**：若谓词被**收紧**为只留 `File.Exists(root)`（去掉 folder 分支），**只有它会红**。

**⇒ 6 用例合计对「放宽」与「收紧」两个方向都有判别力。**
DSH 原表述"4 个 Theory 变红"**字面真实但低估了 kill count**。

## DSH 漏掉的开放项（不在 Gate 字面内，属枚举完整性）

1. **E-7 的开放部分**：管道并发窗口（4 处）+ 5 项未修 —— **纯技术、可做**，
   与"条件 5 端到端"同类却未被并列点名。
2. **条件 2 的处置动作**（SEC-01/02：删除含素材分支、force-push、转私有、联系 GitHub）：
   按裁决**均需 Owner 显式授权** —— 属**真等待授权**，不是误判。

**⇒ 均不构成误判。**

## DSH 的新错误：**未发现实质错误**

两个小瑕疵：

1. **判别力表述 4→5**（如上，方向是**保守低估**，不是夸大）；
2. `crash-ack.ps1:290` 的 `acknowledge_once=1` 是**写死字符串**而非计算字段
   —— 但 10 项 CHECK 均为计算，**不动摇 PASS 有效性**；且该脚本是**既有代码，非本轮改动**。

另核实：`verification/E9-NEGATIVE-TEST-1/` 独立目录确实不存在（证据内嵌于
`E9-FILE-ROOT-RECOVERY-1` §5，与委托描述一致）；登记文件回退已由 `31e770c89` 履行。

## 复核者自陈未完成

- **未亲跑** `dotnet test` 复现 mutation 红 / 全量计数（只读约束下构建会写 obj/bin）；
  判别力结论基于**断言语义静态复算 + DSH 的 PROBE 输出交叉验证**。
- `journal_present` / `verify_pins 18/18` 未亲自重算。

## 处理（DSH，2026-11-15）

两条 limitation **已按建议更正**：
1. `E9-FILE-ROOT-RECOVERY-1` §5.3 补正 kill count 为 **5/6**，并写明**双向判别力**；
2. `BLOCKED-ITEM-AUDIT-1` 补入**边界备注**（E-7 开放部分、SEC 处置授权）。
