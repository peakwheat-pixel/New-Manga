# 治理检查器的两个漏洞（2026-10-20 发现）

**发现场景**：收口 `TEST-ENV-ASSUMPTIONS-1` 与 `P11-PROJECTION-TEST-ALIGN-1` 时，
检查器报出 5 个错误，其中 **4 个是同一个原因**，并且顺带暴露了**另一个从未被触发的漏洞**。

## 一、漏洞 A：Resource Manifest 表头写错会让整张表被当成数据

### 现象

```
FAIL: Resource disposition 无效：DISPOSITION
FAIL: Resource manifest 不存在：sha256/manifest_path
FAIL: Resource disposition 无效：**NOT_APPLICABLE**
FAIL: Resource manifest 不存在：—
```

### 根因

**`tools/governance/check.ps1:44-52` 的 `Get-TableRows`**：

```powershell
if ($cells.Count -gt 0 -and $cells[0] -notmatch '^[-: ]+$'
    -and $cells[0] -notmatch '^(?i:evidence_id|resource_type)$') { ... }
```

**它靠第一列的值来排除表头行**，白名单只有 `evidence_id` 和 `resource_type`。

**模板 `doc/templates/TASK.md:72` 用的正是 `resource_type`**：

```
| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
```

**而我手写的三张表都用了 `resource`**——**不在白名单里，于是表头被当成一条资源记录。**

**后果**：`disposition` 列读到的是字面量 `DISPOSITION`，`sha256/manifest_path` 列被当成清单路径。

**所以错误信息在说「你的 disposition 名字叫 DISPOSITION」——听起来像数据错，
实际是表头错。**

### 第二个连锁问题：粗体也会让 disposition 非法

**即使表头写对，`**NOT_APPLICABLE**` 仍然非法。**

**`check.ps1:427`**：

```powershell
$disposition = $row[2].ToUpperInvariant()
```

**它只转大写，不剥 Markdown 强调标记。** 所以 `**NOT_APPLICABLE**` ≠ `NOT_APPLICABLE`。

**这与我此前在 `SEARCHABLE-PDF-CJK-1` 里写的格式直接冲突**——
**那张表用了 `**（无）**` 和 `**NOT_APPLICABLE**` 加粗。**

### 修复

| 文件 | 改动 |
|---|---|
| `doc/tasks/TEST-ENV-ASSUMPTIONS-1.md` | 表头 `resource` → `resource_type`；`**NOT_APPLICABLE**` → `NOT_APPLICABLE` |
| `doc/tasks/P11-PROJECTION-TEST-ALIGN-1.md` | 同上 |
| `doc/tasks/SEARCHABLE-PDF-CJK-1.md` | 同上 |

## 二、最重要的发现：`SEARCHABLE-PDF-CJK-1` 的资源记录从未被检查过

**`SEARCHABLE-PDF-CJK-1` 在 Round 180 以 `closed_with_limitations` 收口，Round 180 的检查报告 `PASS`。**

**但那次 PASS 检查的是**另一个** Task。**

**原因**：`check.ps1` 只校验 **`doc/STATUS.md` 指向的那一个 Task**（或 `-TaskPath` 显式指定）。

**Round 180 我在同一条命令里先改了 STATUS（指向 `RUST-ENV-BASELINE-1`）再跑检查——
所以检查器看的是 `RUST-ENV-BASELINE-1`，`SEARCHABLE-PDF-CJK-1` 一个字都没被读。**

**今天用 `-TaskPath` 单独检查，立刻暴露 4 个 manifest 错误。**

**这不是检查器的 bug，是我的操作顺序问题。**

**但它说明一件更重要的事**：

> **`Governance check: PASS` 只覆盖「当前指针指向的那个 Task」。**
>
> **它从不表示「所有 Task 都合法」。**

**而 `PASS` 这个词，读起来像是后者。**

## 三、漏洞 B：工作区 SHA-256 在 `core.autocrlf=true` 下不稳定

### 现象

**用 `-TaskPath` 检查 `SEARCHABLE-PDF-CJK-1`，8 条证据全部报**：

```
FAIL: Evidence SHA-256 不匹配：src/infrastructure/export/qt_free.py
（共 8 条）
```

**而这些 sha256 是我在 Round 179 亲自用 `hashlib.sha256` 算的。**

### 根因

**`check.ps1:355` 用的是**：

```powershell
(Get-FileHash -LiteralPath $evidencePath -Algorithm SHA256).Hash
```

**即**工作区字节**的哈希。**

**而本仓库 `core.autocrlf = true`**——**任何 `git checkout` / `git merge` 之后，
工作区文件被重写成 CRLF。**

**实测（同一 HEAD 的同一文件）**：

| 来源 | SHA-256 |
|---|---|
| **工作区当前字节** | `474f3e2ce96baa03a36fe9bcedce146f55610a42a6cc08c1e383a0293a2403ec` |
| **`git show HEAD:<path>` 字节** | `53af6735067367de0ab2b5b0f3d45fabdebcff0f01e32307c56df42e57b5a88c` |

**两者不同，且工作区那份会在下次 checkout 时被重写。**

**所以：Evidence 的 SHA-256 pin 是**易腐的**。**
**它在写入的那一刻有效，在一次 checkout 之后失效——而失效与代码无关。**

### 修复：改为 commit-only pin

**`check.ps1:341`** 允许二者取一：

```powershell
if (-not $commit -and -not $sha) { Add-Error "Evidence 必须有 commit 或 SHA-256 pin：$path" }
```

**commit pin 是稳定的**：`git cat-file -e "<commit>:<path>"` 检查的是**对象库**，
**不受工作区行尾影响**（git 内部按 LF 规范存储）。

**所以三个 Task 的证据表全部改为 `sha256` 列填 `-`，只留 commit。**

**代价**：commit pin 证明「该 commit 含此文件」，但不证明「当前工作区内容未被改动」。
**对证据表而言前者足够**——证据要回答的是「依据在哪」，不是「工作区是否干净」。

## 四、这两个漏洞共同说明的事

| 漏洞 | 本质 |
|---|---|
| **A** | **表头被当成数据**——一条靠首列字面量排除表头的启发式规则 |
| **B** | **哈希口径与存储口径不一致**——检查工作区字节，而工作区字节被 autocrlf 重写 |

**两者的共同点：检查器验证的是**它方便拿到的**东西，而不是**语义上该验证的**东西。**

**而它们都表现为「错误信息指向了错误的位置」**：
A 说 disposition 名字错（实际是表头），B 说证据哈希不匹配（实际是行尾被重写）。

## 五、建议（未实施，需 Codex 裁定）

1. **`Get-TableRows` 的表头白名单不应对字面量敏感**——
   更稳的做法是「跳过紧邻分隔行的前一行」，或同时接受 `resource` 与 `resource_type`
2. **disposition 解析应剥掉 Markdown 强调标记**（`**`、`*`、`` ` ``）
3. **Evidence SHA-256 应改为对 git blob 计算**（`git show <commit>:<path> | sha256`），
   或在文档里明确写「该哈希针对工作区字节，autocrlf 会使其失效」
4. **收口流程应显式用 `-TaskPath` 复检该 Task**，不要依赖 STATUS 指针顺带覆盖

## 六、明确未做

- **未修改 `tools/governance/check.ps1`**（检查器是共享契约，需 Codex 冻结范围）
- **未修改 `doc/templates/TASK.md`**
- **未追溯修正其他历史 Task 的 manifest 或证据 pin**（r38 禁止批量回改）
- **未验证**是否还有别的已收口 Task 存在同样的 `resource` 表头问题
  ——**这可能是个批量的历史问题，但不在本次授权内**
