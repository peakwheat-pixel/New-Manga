# AC2 — 两个异常条目的处置

**Task**: GOV-UNTRACKED-BACKLOG-1 · **性质**: 只读判定，不删除不移除

## 条目 1：`CON`

### 指纹

| 项 | 值 |
|---|---|
| 仓库相对路径 | `CON`（仓库根目录） |
| 大小 | 34778 bytes |
| 创建 / 修改 | 2026-10-13 10:20:41 / 10:20:42 |
| 类型 | 纯文本 CSV，两列 `"Path","Hash"` |
| 行数 | **275 行**（含表头） |
| SHA-256 | `8241373A2CC3AC428786E92B23A5872952CF7635E8A5153CAC660560C4AC8714` |

### 内容样本

```
"Path","Hash"
"G:\CODEX\sfx_review\final_sfx_list.csv","942B48C2A8BBB25196781282885820441A9A688ADBF70129E9D6DF045DD70086"
"G:\CODEX\sfx_review\gain_sheet_01_clean.png","73AA02FE25E06571B8764E3BEC06D794FBE5D018BDE3680C333A362DCA779A60"
"G:\CODEX\sfx_review\review_sheet_01.png","F7D28419F217B79D1C01F3453AC37D886AEE56645F929F92E26A46EC41EE723C"
```

全部指向 `G:\CODEX\sfx_review\` 下的 SFX 评审素材（CSV 清单与 PNG 图版），
即一份**内容哈希清单**。

### 生成来源推断

`CON` 是 **Windows 的保留设备名**（与 `PRN` / `AUX` / `NUL` / `COM1` 同类）。
它是脚本把**空变量**当重定向目标的结果，形如：

```powershell
Get-ChildItem ... | Export-Csv -Path $out    # $out 为空 -> 写入 CON
```

时间与内容指向一次 SFX review 的哈希快照作业。**文件名畸形，内容真实。**

### 引用状态

- 已入库文档引用：**0**（本 Task 记录它之前，无任何 `doc/**/*.md` 提及）；
- Git 追踪：否（untracked）。

### 结论：**不得删除，建议归档但不在本 Task 执行**

理由：

1. 内容是**真实的哈希清单**，可能是某次 SFX 评审的唯一记录；
2. 文件名畸形不构成丢弃数据的授权——AGENTS.md 要求「确认来源、引用后才能移动或清理」；
3. 但它在仓库根目录、文件名违反 Windows 约定，长期留在此处会持续干扰工具链
   （`git status` 只能加引号显示，部分工具对此类名字行为不可预期）。

**建议**（交后续 Task 执行，本 Task 不动）：重命名并移入
`G:\CODEX\New Manga.workspace\archive\sfx-review\`，同时记录原路径与 SHA-256，
再在 `doc/` 留下一条指向新位置的索引。

### 读取方法：实测结论与我的预期相反

我原本打算写「普通 `Get-Content` 会去读控制台设备而不是这个文件」。
**实测证明这个说法是错的**，此处按实测记录：

| 方法 | 结果 |
|---|---|
| `Get-Content -LiteralPath "G:\CODEX\New Manga\CON"` | **读到 275 行**，内容正确 |
| `Get-Content -LiteralPath "\\?\G:\CODEX\New Manga\CON"` | 读到 275 行，内容相同 |
| 两者 `Get-FileHash -Algorithm SHA256` | **同为 `8241373A...C8714`** |

即：在该仓库根目录下，Windows 保留名的遮蔽**并未发生**——普通路径与 `\\?\` 扩展路径
访问到的是同一个真实文件。

保留 `\\?\` 前缀的方法仍然可用且更稳妥（它对路径长度与保留名都有绕行作用），
但**不能声称普通路径会读错**。这条差异记在这里，因为「凭印象写结论」正是本 Task
要清理的那类债务。

**风险仍然存在但未在本环境复现**：其他工具（尤其非 .NET 的、或经由 cmd 的）
对 `CON` 的行为可能不同。归档时应优先改名，不要指望所有工具都能正确访问它。

## 条目 2：`INTERRUPTED by Codex before final report; no exit marker; partial JSONL preserved; not Review evidence`

### 指纹

| 项 | 值 |
|---|---|
| 仓库相对路径 | 上列长句（102 字符，含 `;` 与空格） |
| 大小 | 72 bytes |
| 内容 | 单行：`verification/P02/dsh-appcontainer-contract-r3-review-attempt1.status.txt` |

### 生成来源推断

某个脚本把**路径参数**写到了**输出文件名**的位置，形如：

```powershell
$msg | Out-File -FilePath $pathArg    # $pathArg 是目标路径，不是消息
```

消息文本「INTERRUPTED by Codex before final report...」本来是要写进某个状态文件的内容。
**纯 bug 产物，无独立信息**——它的内容只是一个路径，而那个路径本身在
`verification/P02/` 下也是未入库文件。

### 引用状态

- 已入库文档引用：**0**（除本 Task 自身的记录外）；
- Git 追踪：否。

### 结论：**内容无价值，但仍不得由本 Task 删除**

它不含任何别处没有的事实——内容就是另一个路径的字符串。但它仍是**他人的未提交产物**，
AGENTS.md 明确「未提交内容归原作者所有」。

**建议**（交后续 Task）：由原脚本作者确认后删除；若无法确认，移入仓外 archive 并记录指纹。
本 Task **不删除**。

## 两个条目的共同点

它们都不是项目文档，都源于**写文件时的参数错误**，都**没有任何已入库文档引用**，
且都能通过「不丢弃、先记录」的方式安全处理。

它们也提示了一个系统性风险：**脚本写文件时缺少路径校验**。
本会话中我自己也踩过类似的坑（`guarded-write` 的 `--repo` 指向主 checkout）。
是否需要在工具层加一道「目标路径不得为保留设备名、不得含换行/分号长句」的检查，
属另一次范围，本 Task 只记录不立规。
