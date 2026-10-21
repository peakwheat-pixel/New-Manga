# DeepSeek 独立审查

session: session-1bac51c5-047e-4596-baf5-d9d45099c877；exit 0；web_visibility=unverified

## 裁决

**approved（仅限六个历史 Task 的六行 Resource Manifest 格式修复，以及本 Task 自有证据/metadata）。**

这六行可以单独批准；批准它们**不会重新背书** 19 项历史 blob 差异，也不批准父任务 done、实际资源处置、源证据变化或剩余 24 项。P2 项不阻断六行，但 Codex 核销记录必须按实测值写清。

固定点：

- `reviewed_head`: `2573375dcc55b95d202ad2b6cdfee90d3f07c525`
- `diff_base`: `54ff86fb200a8446aa0135aeb90fb0cac9ea7963`
- `freeze`: `79f1eb8f29304cd2b16780328642471b8e064790`
- `source/delivery`: `4c415d8ea5ca9c7fff5c95f22dbf4f57b46652d8`
- 当前分支 `main`；`git status --porcelain --untracked-files=no` 为空；99 branches / 137 worktrees 均保留。

## 实测结果

### 1. 六行 diff、字节保全与语义保留

`git diff --check 54ff86fb2..HEAD` 无输出。六个旧 Task 均只有一行变化：

| Task | 行 | 结果 |
|---|---:|---|
| GOV-DEBT-CLEANUP-2 | 125 | 旧 7 列合并为 6 列；两个末尾说明均保留 |
| P09-AC3-DELETE-1 | 157 | `source_path` 改 `-`；原路径说明移入末列 |
| P09-AC3-DELETE-HARDEN-1 | 144 | 同上 |
| P09-MANAGED-READ-ROOT-TRUST-1 | 217 | 同上 |
| P20-AC4-FPS-1 | 156 | 同上 |
| P20-CLOSE-BOUND-HARDEN-1 | 244 | 同上 |

逐文件比较 base blob 与 HEAD blob，均只有指定一行不同；旧描述文字、旧 `source_path` 文字均在新末列中可找到。状态、AC、Review、Canonical Evidence 与 207 pin 字面值不在变更行内，未被修改。

P09-MANAGED 的既有混合 CRLF 已区分处理：

- 当前磁盘：`19874` 字节，`225` 个 CRLF，`233` 行。
- HEAD blob：`19649` 字节，`0` 个 CRLF，`233` 行。
- 磁盘 `CRLF→LF` 后与 HEAD blob **逐字节相等**；Git 内容 diff 仍只有第 217 行。
- 当前磁盘 raw SHA 与 `format-proof.json` 的 `after_raw_sha256` 匹配；HEAD blob SHA 因 Git 规范化不同，不能把两者混称同一 raw 字节。

### 2. 207 直接 pin 复算

从六份 Task 的 Canonical Evidence 表逐行重新提取并复算，207 行与 proof 记录逐项一致；哈希比较均不区分大小写：

| 分类 | 数量 | 复算结果 |
|---|---:|---|
| `HISTORICAL_BLOB_VALID` | 121 | 全部匹配 |
| `HISTORICAL_EOL_RESTORABLE` | 63 | 全部可由固定 blob 的 LF/CRLF 标准转换匹配 |
| `CURRENT_RAW_VALID_HISTORICAL_DIFFERENT` | 19 | 当前磁盘 raw 匹配，但固定 commit blob 不同 |
| `COMMIT_PIN_ONLY_NO_SHA` | 2 | `null` / `-`，无 SHA |
| `EXTERNAL_RAW_VALID` | 2 | 仓外 SOURCE_PIN，raw 匹配 |
| **合计** | **207** | **0 个分类不符** |

补充核验：

- 3 处带注释路径（`EV-09`、`EV-10`、`EV-11`）只在解释时剥离 `` `（…）`` 后缀；Task 表内原字面值完整保留，未改写。
- 19 个 `CURRENT_RAW_VALID_HISTORICAL_DIFFERENT` 与 proof 的 `historical_limitations` 集合完全一致；仍全部 BLOCKED，没有重签、没有改旧 pin、没有把“当前 raw 匹配”说成历史 blob 已恢复。
- 需要说明的边界：207 项中 **195 项**的 pin 与当前磁盘 raw 相等；**10 项**存在 EOL 差异——其中 8 项 pin 等于固定 blob 而当前磁盘是其 CRLF 变体，2 项 pin 等于 blob 的 LF→CRLF 结果而当前磁盘为 LF。这 10 项的 `refined_identity.raw_sha256` 均与当前磁盘匹配，且本 Task 未触碰这些资产。因此报告中的“207 份原始 SHA 均未改变”只能理解为**本 Task 前后未改变这些资产**，不能表述为“207 个 pin 都等于当前磁盘字节”。

### 3. 实际 parser 与 mock 前后对照

直接调用当前 `tools/governance/clean_workspace.py` 的 `scan_repo_declarations(canonical repo, workspace)`：

| 指标 | 当前 HEAD 实测 | 模拟六 Task 为 base 内容 |
|---|---:|---:|
| errors | **24** | **30** |
| declarations | 2455 | 2449 |
| protected roots | 1787 | 1785 |
| JSON_PARSE | 0 | 0 |

- 消解恰好 6 个指定错误：1 个 `TABLE_ROW_ARITY`（GOV-DEBT-CLEANUP-2 第 6 行）和 5 个 `DECL_RELATIVE_UNRESOLVED`（P09-AC3-DELETE-1、HARDEN-1、MANAGED-READ-ROOT-TRUST-1、P20-AC4-FPS-1、P20-CLOSE-BOUND-HARDEN-1）。
- 剩余 24 个错误的 `code/file/locator/message` 完整身份相等；新增错误为 0。
- 旧 protected 集合是当前集合的子集；新增 2 个受保护根，未减少旧保护。
- 未把 HEAD 新增的自有 JSON 文件置空，未虚构 `JSON_PARSE`。

注意：proof 的 `current_before/after` 仍是 **2445/2451、1781/1783**，比当前 HEAD 实测少 4 个自有 EV 声明；这是自有 4 份 EV 登记前/登记过程中的快照。错误数 30→24 不受影响。当前实测快照应记录为 **2449→2455 / 1785→1787**。

### 4. 自有 4 份 EV 与 check

`doc/tasks/GOV-NONRESOURCE-MANIFEST-FORMAT-1.md` 的 Canonical Evidence 表 4 行字段完整：

- `evidence_id` / `AC/Gate` / `path` / `commit` / `sha256` / `class` 均可解析。
- `parse_markdown_declarations` 实际注册 **4 个 EVIDENCE_PIN，0 errors**。
- 4 份文件均满足 `raw == blob == pin`；commit `9ca7cee6a…` 中对应 blob 与磁盘一致。
- `pwsh -NoProfile -File tools/governance/check.ps1`：**PASS，2 warnings，exit 0**。warning 为非终态 Task 数量与 STATUS 预算，不是本 Task 失败。

## P0 / P1 / P2

**P0：无。**

**P1：无阻断项。**

**P2（不阻断六行批准，但核销记录必须写清）：**

1. **计数快照需用实测值。** proof 的 `current_after_counts` 仍写 protected 1783；当前 HEAD 实测为 1787（自有 4 份 EV 登记后增加）。不能把 1783 当作固定 head 的最终保护数。建议 Codex 在核销记录中写“30→24；declarations 2449→2455；protected 1785→1787（proof 的 1781→1783 为早期快照）”。
2. **207 pin 与当前磁盘的 EOL 边界。** 10 项 pin 不等于当前磁盘 raw，但 proof 的 `raw_sha256` 字段与磁盘一致；报告不能概括成“207 个 pin 全部等于磁盘”。这不影响六行格式修复，也不构成历史 pin 重签。
3. **P09-MANAGED 的 raw/ Git 规范化表述。** 磁盘混合 CRLF 与 HEAD blob LF-only 不同；归一化后逐字节相等且只有第 217 行内容变化。核销时不能声称“磁盘 raw 字节等于 HEAD blob”，只能声称 Git 内容 diff 只有该行、proof after raw 与磁盘一致。
4. **delivery_head 与 reviewed_head 区分。** Task/Handoff 的 `delivery_head: 4c415d8ea` 是源实现 commit；本次独立审查固定 head 是 `2573375dcc55…`。核销记录应同时写明两者，避免把 4c 当作最终审查 head。

## 未测与范围边界

- 109 工具回归**未重复运行**：本次无 `tools/**` 代码变更；不把未跑写成通过。
- 产品、构建、安装、UI 和真实资源处置均为 **NOT_RUN**。
- 未修复 19 项历史 blob 身份限制；继续保持 BLOCKED。
- 未批准父任务 done、实际资源清理/迁移/归档、余 24 项治理错误，也未改变源证据或代码。
- 未执行网络、派发、cleanup、GC、prune、push 或 Legacy 执行；未写文件、未改 ACL/ref/checkout/commit。

## 下一步

Codex 可在同一 `main`、固定 `reviewed_head=2573375dcc55b95d202ad2b6cdfee90d3f07c525` 下完成集成复验和核销，但核销文本必须沿用上述 P2 边界，尤其写入实测 **30→24、1785→1787、2449→2455**，不得将 19 项历史 pin 重签或把余 24 项纳入本次批准。
