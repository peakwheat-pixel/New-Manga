## 结论

**changes_requested**

- `reviewed_head = 798cc8161f44de03032f23243b6eaf8526b0202d`
- `diff_base = f47c68969dac7d3cec0dddbe3fca4ea2fa7803db`
- `delivery/source = 6e3bac7867c67a2e76e45e2facbbf859d5dba526`

代码实现本身未发现逻辑缺陷；R2 的两个 P2 已实际修正：`_resolve_identity(..., warn_alias=False)`、warning 正文补 `origin/locator`，6 个空探针目录也已补登记。**但固定 diff 的 `git diff --check` 在新 head 上失败**，属于 Task metadata/固定证据门的 P1，因此本轮不能 approved。

## P0 / P1 / P2

**P0：0。**

**P1（changes_requested）：`git diff --check` 失败（CRLF 被当作行尾空白）。**

- `git -C WT diff --check f47c…798cc` **exit 2**，对以下三个新增/修改文件的**每一行**报 `trailing whitespace`：
  - `verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1/checkpoint.md`
  - `verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1/runtime-proof-r3.json`
  - `verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1/test-execution.json`
- 原因是这些文件以 CRLF 存储（证据目录 `.gitattributes` 为 `* -text`，不会自动归一化）；`git diff --check` 把 `\r` 视为 trailing whitespace。报告、Review、r3/r4 日志为 LF，未被标记。
- 这不是代码/测试逻辑问题，但它是本 Task 明确要求的固定门，且 R2 的 `71dc9bd` 当时为 exit 0，属于 R3 metadata 回归。
- 修正要求：仅将上述三个文件改为 LF（不改内容、不增加 whitespace 例外/ignore）；重新生成受影响的 EV pin（至少 `runtime-proof-r3`、`test-execution`，`checkpoint` 若在 EV 表内也一并）；重签固定 head 后重新运行 `git diff --check` 和 `check.ps1`。代码与测试未变，不需要因这次修正重跑 127。

**P2（不阻塞逻辑，但应说明/修正）：**

1. `runtime-proof-r3.json` 记录 `evidence_pin_declarations: 22`、`2517/1839 → 2529/1844`；当前 31 EV 实时为 `2526/1848 → 2538/1853`。它是最终 EV 登记前的快照，但文件名/字段容易被当成 31 EV 的实时测量；建议明确标注为 pre-final-EV snapshot，或另行生成 31 EV 的实时 proof。
2. `checkpoint.md` 仍写“当前 dirty 均属本 Task”，而 WT 当前 `git status --porcelain` 为空；这是恢复说明的陈旧表述，修正 CRLF 时可一并更新。
3. 六个探针目录在本进程 `os.listdir` 均为 `PermissionError`（ACL 限制），因此我核验的是“6 个目录存在 + 6 条登记 + inventory `entries: []` + 未删除/未改权限”，未能再次独立枚举其内容；这不影响“不删除、保持原位”的结论。

## 实际只读校验

**代码 diff：**

- `git diff 6e3bac786…798cc8161 -- tools` 为空；`git diff f47c…798cc -- tools` 只含共享 scanner 与 policy。
- 新代码仅两处对齐：`index._resolve_identity(source, origin, locator, warn_alias=False)`；`DECL_BROAD_ROOT_PRESERVED` 正文为 `role/policy/origin/locator/root/source_keep`。
- T01 断言 `file/locator` 出现在完整 message；T12 观察 helper 的 6 次 `_resolve_identity` 调用均为 `warn_alias=False`。

**同 canonical 数据独立 scan（base 旧模块 vs WT 新模块）：**

- base：`24 errors / 2526 declarations / 256 warnings / 1848 protected roots`
- candidate：`12 / 2538 / 268 / 1853`
- 移恰 **12** 条、新增 **0**；剩余 12 条完整 identity（含 `file/locator/message`）按原顺序相等；移除集合与 policy 六条 `error_pair` 多重集完全相等。
- `+12 Declaration / +12 warnings / +5 roots`；旧 protected 为 candidate 子集；`scanned` 与 index 一致；新增 warnings 恰为 `DECL_BROAD_ROOT_PRESERVED`。

**31 EV：**

- 逐项 `raw = blob = pin` 全部成立（EV-1…EV-31）。
- Task `parse_markdown_declarations`：**EVIDENCE_PIN 31、errors 0**（36? 本次实际 47 declarations）。
- 两旧源 SHA 仍为 `5961e38e…`、`e95bdfa8…`；policy SHA `f1c201ae…` 与 main 相同；69 项例外表未修改。

**最新 127 日志与回放（Owner 证据，仅只读核验，不是我复跑）：**

- `new-tests-r4.log`：18、exit 0、0 skip；canonical 与 raw agent-output 两个 SHA 均匹配 `test-execution.json`，尾部 `Ran 18 tests ... OK`。
- `declaration-tests-r3.log`：29、exit 0、0 skip；两 SHA 匹配，尾部 OK。
- `hardening-tests-r3.log`：80、exit 0、0 skip；两 SHA 匹配，尾部 OK。
- `replay-r3-clean_workspace.json` / `replay-r3-remove_worktrees.json`：均 `ok: true`，`15 candidates / 15 rejected / 0 deleted / 0 violations`。
- `test-execution.json` 已明确区分 raw CRLF 路径/hash 与 canonical LF 路径/hash，R2 的哈希混淆已修正；但 canonical 的 `runtime-proof-r3.json`、`test-execution.json` 本身现在是 CRLF，触发上述 P1。

**内存 REAL_DRIFT / 无副作用（本轮实际执行，纯 `mock` + `io.BytesIO`）：**

- 基线（关闭 helper）：24 errors。
- `warn_alias` 观察：成功 helper 调用 6 次，flags `[False] × 6`；原 index warnings 未增加。
- REAL_DRIFT（使用 `norm_abs` 小写比较）：`REAL_DRIFT`，errors 25（原 24+1），declarations/roots/warnings 保持 2526/1848/256。
- 人为让 `_resolve_identity` 期间 real 目标变化的副作用探针：仍 `REAL_DRIFT`、25 errors、warnings 仍 256，原容器无新增 warning；新 call 的无副作用目标成立。
- R2 的 14 个负例未全部重复；本轮仅补做上述关键项。

**6 个空探针目录：**

- 实际 6 个：5 个 `dsh-probe-*` + `.dsh-mode-29c6eed9`。
- `review-probe-inventory.json` 登记 6 个；Task Resource Manifest 中 `reviewer-probe` 连续 6 行，均为 `PRESERVE_REFERENCED`；`.dsh-mode` 已补入，R2 的“5 登记/6 实际”P2 已修复。
- 6 个均存在；本进程无法枚举内容（ACL 拒绝），inventory 记录 `entries: []`；未删除、未改权限、未迁移。

**canonical 检查：**

- `check.ps1`：**PASS（2 warnings）**。
- `git diff --check`：**exit 2**（上述 P1）。

## Owner 证据 / 我的执行 / NOT_RUN

- **Owner 证据（只读核对）**：127 = 18/29/80、0 skip；r3 双回放 15/0/0；31 EV pins；raw/canonical 日志双 hash。
- **我实际执行**：base/candidate 同数据 scan、31 EV 校验、Task parse、6 目录/Manifest 登记、日志与回放 hash/结果、REAL_DRIFT 与无副作用内存 mock、`check.ps1`、`git diff --check`。
- **NOT_RUN**：
  - Reviewer 完整 18 fixture 复跑：**NOT_RUN**（sandbox 禁写，Task TMP 不可用；上一会话 exit `4294967295` 不是 Review/PASS）。
  - 127 全套未由我重跑；以上是 Owner 日志核验。
  - canonical consolidate 全 100/138 盘点未跑。
  - 真实 apply/cleanup/迁移/归档/GC/prune/push/ACL/Legacy：未执行。
  - 未合并 main，未删除/移动任何探针目录，未改 100 分支/138 工作树。

## 范围与下一步

- 本结论只针对本实现与本 Task metadata，**不批准**父 Task done、r212 清理禁令解除、真实 cleanup、删除 6 个探针目录或 push。
- 建议 Codex：把 `checkpoint.md`、`runtime-proof-r3.json`、`test-execution.json` 转为 LF 并重签受影响 EV；更新固定 reviewed head；重跑 `git diff --check`（应 exit 0）和 `check.ps1`；随后再交 DeepSeek R3。**当前 `798cc8161` 不 merge。** 代码/测试逻辑无需改动，127 结果可沿用。