## Review 结论：changes_requested

**固定点**：base `50d784300ac74d6ded633685bfce201cdddb630a`，reviewed_head `3ff9dba39694751a72fd1a67380757041cd7dc08`，交付固定点 `488ab6cbec7774df8c0c3b2e8a9e169750a92101`（`git rev-parse` 实测一致；`488ab6..3ff9dba` 仅 1 个 docs 元数据提交）。

研究主体（R23/R24 非声明身份、现有例外的精确适用性、信任边界）经我独立只读重算，与 Owner 证据一致；但**证据 pin 表存在一处静默失效的格式缺陷**，使本 Task 宣称的 10 条 EV pin 实际上未被 guard 注册为保护，故不能 approved。

---

### 一、我实际重算（Read-only，未执行本 Task 探针脚本）

- **10 条 EV pin**：按 `split('|')[3:6]` 取 path/commit/sha，逐条以磁盘 `read_bytes()` 与 `git cat-file blob 488ab6cbe:path` 的 stdout 字节比对；**10/10 两者均等于 pin**，且 `disk==blob`、commit 均解析为 `488ab6cbec77…`。未用文本模式代替字节。
- **原始两日志**：R23 `bdabb170…`（24213 B，untracked `??`）、R24 `caac6afd…`（161783 B，tracked clean）；`base..head` 对 `verification/P02-NEW-TIME-BASELINE/` 无 diff。
- **逐行 NDJSON**：6 值（meta1/observation4/closed1）与 64 值（1/62/1）；逐值调用实际 `parse_json_declarations` 均 **0 声明/0 错误**；两种资源节点签名 **0 匹配**；`path` 键 54/184、`disposition` 各 1、按探针定义 pin 相关路径串 **18/28**（与证据一致）。
- **默认扫描**：32 errors、1704 保护根、67 条例外、仅两日志为 `JSON_PARSE`；连续两次默认扫描错误身份集合完全相同（before/after 稳定）。guard 盘上 SHA `7e59e8fe…` 与 identity-proof 一致。
- **候选扫描**（workspace 现存 `candidate-analysis-only.json`，69 = 原 67 + 2，前 67 项与正式表逐项相等）：**30 errors**，移除项恰为 R23/R24 两条 `JSON_PARSE`，无新增错误，其余 30 身份（code/file/locator/message）不变；保护根 1704 且基线保护集合是子集。
- **6 例机制重跑**：错 path→31、错 hash→31、内存字节漂移→31（R23 仍 fatal）；漂移为合法声明→30 且 R23 声明被解析；**trust-boundary 例**（现存 poison 清单 hash 与探针 synthetic 字节 `b5696f5c…` 精确相等）→30、R23 被解码前整文件绕过、**0 声明注册**。即"例外匹配在解码前，语义靠可信独审"的信任边界成立，**不是安全 PASS**。
- **历史表**：磁盘 raw `238039dd…`（18912 B，CRLF）、Git blob `c2f185fb…`（18575 B），`CRLF→LF` 后与 blob 相等，`git status` clean；`DEFAULT_JSON_EXCEPTION_MANIFEST` 仍指向旧 Task 表，旧 Task 第 125 行确为 `EV-JSON-EXCEPTIONS` + `cacd1c021` + `c2f185fb…`。
- **双 hash**：workspace 原始 stdout `6c68fab5…`（2996 B），版本化 LF 副本 `6e67271a…`（=EV-7），两者 LF 转写相等；`probe-run.exit`=`0`。
- **分寸**：98 heads / 136 worktrees；任务路径工作区 clean（审查期间无写入）；`git diff --check base..head` rc=0；diff 范围仅 allowed_paths；治理 `check.ps1` **PASS**（2 条 warning，含 STATUS 预算 80%）。
- **STATUS 差异**：仅切换当前 Task 为 in_review、保留父 Task `blocked`、正式 32 错误、STATUS/r212 禁令与"尚未只剩 main"；未释放、未宣称父 done。

### 二、静态检查 / 未测区分

- **静态**：`load_json_exceptions` 的 path/64 位 sha/reason 校验与 `isfile`+raw SHA 匹配、`scan_repo_declarations` 的解码前例外短路、`parse_json_declarations` 两签名，均逐行核对，与上述实测一致。
- **未测/NOT_RUN**：未运行 `probe-source.py.txt` 与本 Task probe（按要求，避免写产物）；未复跑 Owner 的原始进程；产品/构建回归 NOT_RUN（无代码变更）；未通扫历史、未读其它 worktree、未核 workspace 内 `review.jsonl` 等派发产物；未验证"修正后"保护根数值（见 P1）。

### 三、问题分级

- **P0**：无。
- **P1（阻断）**：`doc/tasks/GOV-NDJSON-NONDECL-IDENTITY-1.md` 的 Canonical Evidence 表中，六列分隔行 `|---|---|---|---|---|` 与首行 `|EV-1|…` 之间多了一个**空行**。guard 的 Markdown 表格解析在此终止：现状实测 `EVIDENCE_PIN` = **0、EV 声明 = 0**（仅 Resource Manifest 的 2 条声明）；仅删除该空行的内存副本即得 **10 条 EVIDENCE_PIN、0 错误**。即 10 条 pin 目前只是正文文字，未被实际保护索引注册，与 AC4"证据 pin 核销"及本 Task 的目的相悖，属静默失效。
- **P2**：`verification/…/checkpoint.md` 正文写"`in_progress`完成待独审"，与 front matter/交付记录的 `in_review` 不一致；修正时可一并对齐。
- **P2（提示，不阻断）**：`18/28` 为按探针 `pin_context` 定义得到的**有限抽样**，不是完整引用清册——证据已如此声明，修正后不应改写为"全部引用已保护"。

### 四、精确修正（只涉及元数据，我不自行修改）

1. 在 `doc/tasks/GOV-NDJSON-NONDECL-IDENTITY-1.md` 中**删除** Canonical Evidence 表分隔行后的那一个空行（仅此一处；10 条 EV 的 path/commit/sha 一律不动）。
2. 提交后用同一只读方法复核：`parse_markdown_declarations` 预期 `EVIDENCE_PIN=10、errors=0`；默认 `scan_repo_declarations` 预期仍 **32 errors**，保护集合**只增不减**（修正后重算并记录新的保护根数，不得低于 1704）。
3. 将 `delivery_head` 固定到新提交，重跑 `git diff --check`、`check.ps1`，由我在**新固定 head** 做一次增量复核（EV 字节未变，无需重做全部身份重算）。
4. `checkpoint.md` 的 `in_progress` 措辞同步为 `in_review`。

### 五、批准边界（即使修正后批准，也仅此而已）

只批准**只读身份研究**：正式 32 错误保留、不登记任何例外、不改旧表/旧 Task/原 pin/日志/guard、不解除保护与清理禁令、不批准父 Task done、不宣称"只剩 main"。拟议的 `GOV-NDJSON-EXCEPTION-CONFIG-1` 仍须单独冻结 Task/Plan/STATUS 并另行独审，本 Review 不构成其释放或实现批准。

**建议下一步**：Codex 仅做上述空行/措辞元数据修正并提交，报告新 head；我据此做增量复核后再进入 closeout。
