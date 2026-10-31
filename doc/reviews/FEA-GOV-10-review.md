---
document_id: FEA-GOV-10-review
kind: independent_review
task_id: FEA-GOV-10
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate task-23（独立上下文；未参与清单生成与 C-07 撰写）"
reviewer_independent: true
reviewed_by_implementer: false
reviewed_head: 60b2b4e2b
reviewed_head_full: 60b2b4e2bdf8b830ecf14b06769e2b3cb58c0429
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == 60b2b4e2b）"
reviewed_document: doc/plan/FEA-C07_API_INVENTORY.md
reviewed_sha256: e39ed0191f86e5b7e7c0896b40e9a37abe73935dff9f1fed7f6df6458d9d7086
reviewed_sha256_basis: "HEAD 的 LF blob（97 行；由 063f35c01 引入）"
source_of_truth:
  - apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs（423 行；`IReaderProgressSink` :104、`IHostController` :116）
  - apps/desktop-avalonia/src/NewManga.App/Services/RunContracts.cs（612 行；`IRunController` :359）
baseline: "doc/plan/V11R_AVALONIA_CONTRACT.md §5 `:239`（36 方法保持原签名、新增只允许追加）· doc/plan/FEA-01_CONTRACT_DRAFT.md C-07 行 · doc/status 链"
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 1
p2_count: 4
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T04:42:33+08:00
captured_by: c01b-reviewer
---

# 独立复核：FEA-C07 应用端口清单（API Inventory）

**本报告不是** 冻结动作、不释放任何 Task，也不构成执行授权。本轮用独立解析器重新从 C# 接口块枚举成员，逐项与清单比对，并核对 V11R §5 的冻结面口径。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 1** / P2 × 4）。**

清单的**主体内容完全准确**——这在本系列复核里是少见的：

- **计数与归属 ✅**：`IReaderProgressSink` 1 + `IHostController` 47 + `IRunController` 6 = **54**，与代码逐块枚举**完全一致**（我独立解析三块：47/6/1，零差异）。
- **签名 ✅**：54 个成员的**名称 + 返回类型 54/54 全一致**（含嵌套泛型 `Task<IReadOnlyList<T>>` 8 个）；另抽查 12 个成员的参数形态也与代码一致（但参数未入清单 → P2-2）。
- **接口边界 ✅**：47 个均在 `IHostController` 直接声明块内（不含继承的 1+6），6 个在 `IRunController` 块内，1 个在 `IReaderProgressSink`；与 `IHostController : IReaderProgressSink, IRunController, IAsyncDisposable`（`:116`）及文档 `:13`「继承的方法分别列出」一致。
- **完整性 ✅**：方法集合**双向零差异**（无代码有而清单无，也无清单有而代码无）；两源文件自生成 HEAD `e7e43543b` 起未改动（blob 相同），清单未过期。

**但 1 条 P1 使「冻结依据」不完整**：文档 `:95` 写「冻结时以本文件 **+ 生成脚本** 为准」、`:96` 写「『旧签名不变』的可验证基线 = **反复运行生成脚本**得到同一集合」——而**仓库里不存在该生成脚本**（`tools/`、`scripts/` 无匹配，全仓 grep `FEA-C07_API_INVENTORY`/`api_inventory` 0 命中）。本轮我用手工解析复现了 54/54（可作一次性证据），但冻结后他人无法按文档描述重跑。

| 审查项 | 判定 |
|---|---|
| 1. 计数与归属（54 = 1+47+6） | **通过**（独立复现，零差异） |
| 2. 签名准确性（抽查 ≥10） | **通过**（54/54 名称+返回类型一致；抽查 12 个参数形态一致，但清单无参数列 → P2-2） |
| 3. 接口边界 | **通过** |
| 4. 完整性（遗漏/多余） | **部分**（方法零差异 ✓；4 个非方法成员未列 → P2-3） |
| 5. 用途/与 V11R §4 冻结面一致 | **不通过**（P1-1 生成脚本缺失；P2-1 缺变更类别列；P2-4 口径混淆） |
| 6. 数据安全 | **通过**（只读；`check.ps1` PASS；未 push） |

---

## 2. Findings

### P1

#### P1-1 — 「冻结以本文件 + 生成脚本为准」中的生成脚本不存在

- 位置：清单 `:5`（生成方式）、`:95`（「冻结时以本文件 + **生成脚本**为准」）、`:96`（「反复运行**生成脚本**得到同一集合」）。
- 证据：
  - `tools/`、`scripts/` 下无任何 api/inventory/port 生成脚本（`Get-ChildItem tools, scripts -Recurse` 无匹配）；
  - 全仓 `*.ps1/*.py/*.md` 对 `FEA-C07_API_INVENTORY`、`api_inventory`、`api-inventory` 的检索 **0 命中**；
  - 清单 `:5` 自述「生成方式：解析 `{IHostController.cs,RunContracts.cs}` 的 interface 块…**不是**手工枚举」——生成确实发生（本轮我以独立解析器复现 47/6/1，与清单逐项一致），但工具本体未入库。
- 影响：C-07（FEA-01 `:56`）要求「由代码生成的方法清单…**旧签名不变的可验证基线**」；现在「可验证」依赖一个不在仓库里的脚本，冻结后 review/实现 Task 无法按文档描述重跑校验，也违反「清单必须与生成脚本同步」这一自设约束（`:12`）。本轮手工复现只能算一次性证据，不能替代可重跑工具。
- 建议（二选一）：
  1. 入库生成脚本（如 `tools/generate_api_inventory.py`，输出 Markdown 到 stdout/`doc/plan/`），并在 `:5`/`:95` 写明确路径与调用命令；
  2. 若坚持不入库，则把 `:95-96` 改为「以本文件为冻结基线；变更时按本文 §1-§3 的枚举规则人工复核并在 Task 中记录」，删除「生成脚本」措辞（否则文档自述的冻结依据不可执行）。

### P2

#### P2-1 — 缺「变更类别 / 风险」列，V11R §5 `:239` 的「36 基线」无法在清单内核对

- 位置：清单三张表（`:26-91`）均只有「# / 方法 / 返回类型」三列。
- 证据：`doc/plan/V11R_AVALONIA_CONTRACT.md:239`：「`IHostController` **已有 36 方法保持原签名与行为**（审计 §6）。新增方法只允许**追加**」；FEA-01 C-07 亦要求「旧签名不变的可验证基线」。清单 47 个方法中未标注哪些属于 V11R 前的 36、哪些是 V11R 新增（按 47−36=11 计，但清单未给映射）。
- 建议：加一列「基线/变更类别」（`36 基线` / `V11R 新增` / `IRun` / `Sink`），或在 §统计 下注明 36 与 47 的差集由 git 历史定界。

#### P2-2 — 清单无参数列，「签名」实际只覆盖名称 + 返回类型

- 位置：清单 `:32-91`（表头「方法 / 返回类型」）。
- 证据：抽查 12 个成员的代码签名，参数均存在且各异——如 `SaveReadingProgressAsync(chapterId, pageId, mode="original", scrollOffsetY=null, elapsedSecondsDelta=0, ct)`（`IHostController.cs:106-112`）、`ControlRunAsync(runId, action, idempotencyKey=null, ct)`（`RunContracts.cs:369-373`）、`RetryFailedTargetsAsync(runId, idempotencyKey, ct)`（`:388-391`，**必填** idempotencyKey）、`StartExportAsync(bookId, chapterId, orderedPageIds, targetPath, format="zip", pdfContent=null, stalePolicy=null, ct)`（`IHostController.cs:344`）。
- 影响：「签名不变」包含参数；当前清单无法发现参数级 breaking（例如把 `idempotencyKey` 改必填/可选、改参数顺序）。
- 建议：补参数列（可移入折叠/附录表），或在 `:5` 明确声明「本清单只保证名称+返回类型，参数以代码为权威」。

#### P2-3 — 「成员数」实为方法数：4 个非方法成员未计入

- 位置：清单 `:17-22`（统计表「成员数」）。
- 证据：`IHostController` 块内除 47 个 `Task` 方法外，还有 4 个非方法成员：`HostViewSnapshot Snapshot { get; }`（`:118`）、`event EventHandler? Changed;`（`:120`）、`int StartRequests { get; }`（`:127`）、`string ExportDirectorySuggestion { get; }`；`IAsyncDisposable.DisposeAsync`（继承）未列。
- 影响：标题写「成员数」但只数方法；若按「应用端口成员」口径应为 51（47 方法 + 4 非方法）。
- 建议：统计表改「方法数」，或补非方法成员小表并注明 `DisposeAsync` 不计入的理由。

#### P2-4 — `:11` 把「36」说成「命令契约数」，口径混淆

- 位置：清单 `:11`「**命令契约数**（冻结文档的 36/57 口径）与 **C# 端口方法数** 是两个不同计数，不得互相替代」。
- 证据：V11R §5 `:239` 的 **36 是 `IHostController` 的方法数**（「已有 36 方法保持原签名」），不是命令数；57 才可能是命令/端口面的另一个口径（冻结文档 36/57 引用见 FEA-01 C-07 行）。
- 建议：改为「36 = V11R 前 `IHostController` 方法基线（V11R §5 `:239`）；57 = 冻结文档的命令口径；本清单 54 = C# 端口方法数」。

---

## 3. 核验明细（供复核）

- **独立枚举**（不改文件，仅供比对）：`IHostController` 块 `:116-423` → 47 个 `Task` 方法；`IRunController` 块 `:359-392` → 6 个；`IReaderProgressSink` 块 `:104-113` → 1 个。合计 **54**，与清单逐项 `名称|返回类型` 比对：**仅代码有 = 0，仅清单有 = 0**。
- **抽样 12 个成员**：`SaveReadingProgressAsync`、`StartAsync`、`CreateChapterAsync`、`LoadReaderBookAsync`、`ListChaptersAsync`、`PutCredentialAsync`、`SaveNetworkProfileAsync`、`ImportFilesAsync`、`StartExportAsync`、`CreateBackupAsync`、`RestoreBackupAsync`、`RerenderPageAsync` —— 名称/返回类型全一致；参数形态与代码一致（清单未列参数）。
- **生成时 HEAD 有效性**：`git log e7e43543b..HEAD -- IHostController.cs RunContracts.cs` 为空，两文件 blob 与 `e7e43543b` 相同 → 清单对当前代码有效、未过期 ✓。
- **治理**：`check.ps1` 实跑 `PASS (3 warnings)` EXIT=0；`git status --porcelain` 为空（仅本报告新建后出现 `??`）；`origin/main..HEAD` = 187 提交（**未 push**）✓；引入提交 `063f35c01`（+97 行，仅该文档）。

---

## 4. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**，`task-23`）身份出具本报告，`reviewer_kind: subagent`，独立上下文。
- **未参与**清单生成、未参与 C-07 / V11R 契约 / FEA-01 撰写，未参与 `apps/**`、`src/**` 任何实现。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`；未触碰真实数据根、未执行安装脚本或迁移。唯一执行的命令为只读 `check.ps1`（运行后 `git status` 为空）与只读取证（PowerShell 读取/解析 C# 文件、`git log`/`git rev-parse`）。
- 计数与签名结论来自我**独立重写的解析器**（不引用清单自述的 54），再把结果与清单比对；脚本缺失结论来自 `tools/`、`scripts/` 列举与全仓 grep。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为空；`reviewed_head == HEAD == 60b2b4e2b`。

---

## 5. NOT_RUN

- 未运行 `dotnet build` / `dotnet test` / 任何编译（纯文档复核；签名以源码文本为准）。
- 未核 54 个方法的**行为语义**（只核名称/返回类型/归属/参数形态）。
- 未核 `IAsyncDisposable.DisposeAsync` 的实现类是否满足接口（只看接口声明）。
- 未核冻结文档「36/57」的原始出处全文（只核 V11R §5 `:239` 与 FEA-01 C-07 行）。
- 未核 Core 侧命令清册（不在本轮范围）。
- 未核远端历史细节（仅核本地 `origin/main..HEAD` 未 push）。

—— 报告结束（`verdict: changes_requested`，P0×0 / P1×1 / P2×4）。
