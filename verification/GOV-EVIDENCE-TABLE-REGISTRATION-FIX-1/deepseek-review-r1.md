# Review 结论：`changes_requested`

- 仓库：`G:/CODEX/New Manga`
- `base`：`f72dd96ee51f21cc24472b05cceaf488060b679a`
- 实现：`244d08e4eb5bb7aee1b6b54d0198093bcd16b48c`
- `reviewed_head` / 当前 HEAD：`fa18dc2c6f4ae381563d507064020e248ea56052`
- Task 与 Handoff 的 `delivery_head` 均为 `244d08e4e`；checkpoint 为 `in_review`。
- 未发现 P0。实现层面的空行修正和 pin 保全通过；阻塞点是 **before 侧错误身份证据无法复现**。

## 已独立实测通过

1. **3 个目标文件只移除空行**
   - `GIT-MAINLINE-CONVERGENCE-1.md`：161→151 行，删除 10 行；非空字节行 110→110，序列完全相同。
   - `GOV-PATH-HEADER-COMPAT-1.md`：118→116 行，删除 2 行；非空字节行 88→88，序列完全相同。
   - `GOV-DECLARATION-RESIDUAL-32-AUDIT-1.md`：111→108 行，删除 3 行；非空字节行 80→80，序列完全相同。
   - 合计删除 **15 个空行**；三个文件非空字节行 SHA 前缀分别为 `f1b27e2e...`、`6198b460...`、`9e9ee5f9...`。三文件 head 内容与 `244d08e4e` 完全相同。

2. **51 条原始 pin**
   - 51 行、51 个唯一 path。
   - `raw 磁盘 = git cat-file blob stdout bytes`：**51/51**。
   - 磁盘 SHA-256 = pin SHA-256：**51/51**。
   - base 侧 blob 也等于原 pin：**51/51**；`base..head` 未改动任何原 pin 文件：**0**。

3. **head parser 注册**
   - `GIT-MAINLINE-CONVERGENCE-1`：19/19，0 errors。
   - `GOV-PATH-HEADER-COMPAT-1`：19/19，0 errors。
   - `GOV-DECLARATION-RESIDUAL-32-AUDIT-1`：13/13，0 errors。
   - 合计 **51/51** 实际注册。

4. **本 Task 5 条 pin**
   - 5/5 实际注册，0 errors。
   - 5/5 磁盘字节 = blob 字节；5/5 SHA-256 匹配；commit 均为 `dcfb553d...`。

5. **head 默认 32 错误**
   - 直接调用 `scan_repo_declarations(repo, ws)`，未使用 `--out`，head 为 **32 errors**。
   - 32 条完整 `(code, message, file, locator)` 多重集与 `registration-proof.json` 的 `error_identities` **完全一致**。

6. **保护集合只增不减**
   - head `protected_roots`：**1758**。
   - base 内存重建：**1722**。
   - 移除保护：**0**；新增：**36**；base 集合是 head 子集。
   - proof 的 30 个 `new_protected_roots` 全部存在于 head、均不在 base。

7. **资源与范围**
   - heads：**98**；worktrees：**136**。
   - `git diff --check base..head`：exit 0。
   - `tools/governance/check.ps1`：**PASS**，2 个 warning（14 个非终态 Task；STATUS 达到预算 80%），无 error。
   - `base..head` 共 13 个文件，全部落在 Task `allowed_paths` 内。
   - 实现后仅 6 个自身文档/证据元数据文件变化；未改三个目标表、未改 `tools/governance/`。
   - 复核后 tracked diff 为 0。

8. **保护快照的可解释性**
   - 按集合差可解释为：base `1722` + 本 Task Resource Manifest 的 `agent-output` 1 = **1723**；+ proof 的 30 个新保护根 = **1753**；+ 本 Task 5 条 Canonical Evidence pin = **1758**，与 head 实测一致。
   - 因此 `1723→1753` 作为快照与 head 相差 5 条自有 pin，方向合理；但 244d 树本身未直接重算。

## P0

无。

## P1

### P1-1：before 侧“默认 32 错误完整身份不变”未被复现，和 `registration-proof.json` 冲突

- 复核方法：将 `base..head` 涉及的全部变更文档按 **base 内容在内存回填**（base 不存在的新增文件视为空），当前未跟踪文件保持不变，直接调用实际 `scan_repo_declarations(repo, ws)`，不写文件、不使用 `--out`。
- 实测结果：
  - **base：`protected_roots=1722`，`errors=34`**
  - **head：`protected_roots=1758`，`errors=32`**
  - proof 声明：`default_before_errors=32`、`default_after_errors=32`、`same_full_error_multiset=true`。
- head 的 32 条身份与 proof 完全一致；但 base 多出 2 条错误，说明 **base 侧完整错误多重集不是 32**。新增的 Task/Handoff/证据文件不可能消除既有错误，因此这 2 条差异应落在三个 base 目标表或其 base 内容上。
- 这也意味着 proof 中每个目标的 `parser_errors: []`（before）不能直接采信；至少现有的 before 证据不足以支持“32→32、完整身份不变”。
- 如果这 2 条是空行截断表格产生的瞬时 `TABLE_*` 错误、修复顺带消除了它们，本身可以是合理结果；但必须如实记录为 **34→32**，并列出仍保留的 32 条身份，不能继续写“完整多重集相同”。
- 该项不要求改动三个表的非空行或 pin；需要修正的是 before 测量、`registration-proof.json`、report/AC3 的表述。

## P2

### P2-1：before 的 9/12/0 未做逐文件独立复算
- 本次只直接复算了 head 的 19/19/13、0 errors；before 的 `9/12/0` 仅来自 Owner 证据。
- 算术上自洽：`51 - (9+12+0) = 30`，正好等于 proof 的 30 个新增保护根；但这不能替代三个 base 文件的逐文件 parser 输出。
- 应补：三个 base 文本分别调用实际 parser 的注册数、错误清单和行号。

### P2-2：244d 的 1723/1753 快照未在 244d 树上直接重算
- 当前只能通过 base 1722、head 1758 和集合差解释该快照；按指示属于 **Owner 快照证据**，不是本次独立重算结果。
- 该解释与实测一致，暂不作为独立 blocker。

### P2-3：未跟踪内容无法由固定 head 证明未被修改
- 可确认：tracked diff 为 0；本次复核未执行显式写文件命令；变更路径均在 allowed_paths。
- 不可确认：复核前的未跟踪内容基线。`tools/governance/__pycache__` 现有 1 项，无法确认是本轮还是既有，未清理、未修改。
- “未改未跟踪内容”目前只能作为 Owner 声明，不能作为 Git 可复现事实。

### 非问题
- 纯 Markdown 修正不运行产品测试是合理的；head parser、51 pin raw/blob/SHA、治理 check 已覆盖本次文档变更的关键风险。

## 判定与下一步

**`changes_requested`**：实现本身未见需回退的缺陷，P1-1 关闭前不应批准 AC3，也不应据此冻结 `GOV-NDJSON-EXCEPTION-CONFIG-1`。

建议 Codex 在不改三个表非空行、不改 51 pin 的前提下：
1. 对三个 base 文件逐个实际 parse，给出 before 注册数和完整错误清单；
2. 用实际全库扫描复核 base 是 32 还是 34，并修正 `registration-proof.json` 的 `default_before_errors` / `same_full_error_multiset`；
3. 如确认 34→32，明确说明被消除的 2 条错误身份及剩余 32 条身份；
4. 更新 report/AC3/Handoff 后提交新的固定 head，重新独立 Review。

清理禁令、父 Task blocked、32 errors 现状及旧保护集合约束均不因本 Review 解除。
