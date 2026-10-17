# P15-C1-FU2：契约 minor 漂移全文复查

## 固定输入

- Task：`P15-C1-FU2`
- 分支：`codex/P15-C1-FU2`
- 基线：`ac430e2c732e9a266e6e3fef6a2b6a800b02a87f`
- 目标：`doc/contracts/P15_SETTINGS_IPC_CONTRACT.md`
- 版本权威：§2 第 16 行 `version = { major: 2, minor: 7 }`；本次未修改 §2。

## 搜索方式

在 PowerShell 中对完整契约逐个执行以下 literal pattern 搜索；`[regex]::Escape` 保证每个 pattern 按字面匹配，`Select-String` 大小写不敏感：

```powershell
$p = 'doc/contracts/P15_SETTINGS_IPC_CONTRACT.md'
$patterns = @('2.6', 'minor 6', 'minor: 6', 'minor, 6', '6 →', 'Core 2')
foreach ($pattern in $patterns) {
  Select-String -Path $p -Pattern ([regex]::Escape($pattern)) -CaseSensitive:$false
}
```

## 命中与处置

| Pattern | 完整契约命中 | 逐处判断 |
|---|---|---|
| `2.6` | §2 第 16 行；修订记录第 327、334 行；依据映射第 346、350 行 | §2 第 16 行将 `rev 2.6` 明确称为未发布的旧草案请求，并说明 rev 2.7 对省略 `provider_profile_id` 的请求返回 `INVALID_REQUEST`；这是兼容影响的历史描述，不是当前 minor。第 327、334、346、350 行是修订沿革与依据映射，分别记载初始 `2.5→2.6`、FU1 `2.6→2.7`，均为历史事实。以上均保留；没有残留的当前 `Core 2.6` 声明。 |
| `minor 6` | 无 | 无命中；§2 当前值以 `minor: 7` 表示。 |
| `minor: 6` | 无 | 无命中。 |
| `minor, 6` | 无 | 无命中。 |
| `6 →` | 无 | 无命中；契约中记录的历史版本迁移是 `2.5→2.6` / `2.6→2.7`，不表示当前 minor 为 6。 |
| `Core 2` | §4.2 第 125 行：`Core 2.7 私有 stdio 命令` | 唯一命中是已对齐的当前描述；§4.2 原 `Core 2.6` 已改为 `Core 2.7`。 |

## AC 与测试状态

- AC1：仅将 §4.2 的 `Core 2.6` 更为 `Core 2.7`；§2 的权威值未改。
- AC2：上述六种 pattern 已逐一复查；保留的 `2.6` 命中均明确是历史兼容说明/修订沿革，不是过时的当前 P15 Core minor 引用。
- 测试：全部 `NOT_RUN`。这是只修订契约文字的设计 Task；没有运行时实现可验证，未运行产品、协议或安全测试。全文模式搜索是静态文档复查，不计为测试。
- Wire 语义：未改字段、命令、状态或错误语义；只修改 §4.2 的版本文字。

## SHA-256 复核口径

哈希按文件系统中的原始字节计算。当前 worktree 的 `git ls-files --eol` 显示契约索引为 LF、工作文件为 CRLF，Git `core.autocrlf=true`；主仓库 checkout 后可用以下命令复算同一文件 pin：

```powershell
(Get-FileHash -Algorithm SHA256 -LiteralPath 'doc/contracts/P15_SETTINGS_IPC_CONTRACT.md').Hash.ToUpperInvariant()
```

本交付只在指定 linked worktree 内读写；主仓库未检出或修改该分支文件。主仓库集成后应按上述命令复算契约 pin（RV-P15-04）。
