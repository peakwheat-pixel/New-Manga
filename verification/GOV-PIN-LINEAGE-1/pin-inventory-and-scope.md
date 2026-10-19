# `GOV-PIN-LINEAGE-1` 的可执行清单（r24 前置工作）

**产出时间**: 2026-10-20 · **性质**: 只读扫描 · **依据**: Codex r24 §2「释放前需可执行清单」

## 一、为什么要先做这个

r24 §2 拒绝释放 `GOV-PIN-LINEAGE-1`：

> 目前只能核实两项 pin，另外五项尚无可执行清单。

**它拒绝的是一件对的事**——一个带着猜测清单释放的 Task 会产生需要返工的工作。

本文件把清单做出来。**清单做出来了，Task 才有释放的条件。**

## 二、扫描方法与范围

扫描 `doc/tasks/*.md` 的 `## Canonical Evidence` 表，取每一行的
`path` / `commit` / `sha256` 三元组，然后：

1. 计算当前磁盘文件的 SHA-256，与 pin 比较；
2. 若不符，用 `git log <pinned-commit>..HEAD -- <path>` 查是否有后续提交碰过该路径；
3. 若无后续提交且该路径在 pin commit 中存在，则标记为 `UNEXPLAINED` 并逐字节诊断。

**扫描范围**：全部 **313 个 Task 文件**。

## 三、总量

| 项 | 值 |
|---|---:|
| Task 文件 | 313 |
| **有 commit + sha256 的证据 pin** | **1214** |
| **失配** | **92** |
| 失配率 | **7.6%** |

**r24 估计的「7 项」与实际相差一个数量级。** 这不是 r24 的错误——它当时只能看到本会话
涉及的两个 Task。

## 四、三类失配与处置

| 类别 | 数量 | 性质 | 处置 |
|---|---:|---|---|
| **`TIME_BASED`** | **63** | 路径在 pin 之后被**其它提交**合法修改 | **保留原 pin + 追加 lineage**（r20 §2.2） |
| **`LINE_ENDING`** | **6** | **文件内容完全相同**，仅行尾不同 | **加 `.gitattributes` + 重算 pin**（同 `GOV-EOL-PIN-1`） |
| **`MISSING_FILE`** | **23** | 路径在磁盘上不存在 | **单独判断**（见 §七） |

## 五、`TIME_BASED` 63 项（按 Task）

| Task | 数量 |
|---|---:|
| `P15-CORE-1A` | 7 |
| `HOST-ISSUER-1` | 6 |
| `P13-C1` | 6 |
| `P15-CORE-1B` | 6 |
| `P20-CLOSE-BOUND-1` | 4 |
| `P12-C1` | 3 |
| `ENV-BUNDLE-1`、`FEAT-IMPORT-MULTI-1`、`GOV-RESOURCE-MANIFEST-JSON-1`、`HOST-ISSUER-1-C1`、`P09-AC3-DELETE-HARDEN-1`、`P09-FU2`、`P15-C1-FU1`、`P15-CORE-1C`、`P22-REBASE-1` | 各 2 |
| 其余 19 个 Task | 各 1 |

**共同特征**：全是「pin 指向交付当时的字节，之后主线继续演进」。
例如 `HOST-ISSUER-1-C1` 的 `M2-C1_TYPED_IPC_CONTRACT.md` pin，
而该契约后来由 `8b5282889`（rev 2.11）等提交修改过。

**处置口径**（r20 §2.2）：

> 保留原 evidence_id、原 commit、原 SHA-256；**追加清晰的 pin lineage / supersession 说明**，
> 记录后续变更提交及现有内容不再匹配的原因。**重算并覆盖原值会把「后来内容」
> 替换成「当时证据」，破坏历史可追溯性。**

## 六、`LINE_ENDING` 6 项 —— 这批不是「时间问题」

| Task | evidence_id | 路径 | blob | 磁盘 |
|---|---|---|---|---|
| `HOST-TTL-BOUNDARY-1` | `EVD-HOSTTTL-AC6-RUST-DIAG` | `ac6-rust-concurrency-diagnostic-6284f6f.jsonl` | LF | CRLF |
| `HOST-TTL-BOUNDARY-1` | `EVD-HOSTTTL-AC6-RUST-DIAG-EXPORT` | `ac6-export-rust-concurrency-diagnostic-7fbce30.jsonl` | LF | CRLF |
| `P17` | `EVID-P17-03` | `verification/P17/pytest.log` | LF | CRLF |
| `P17` | `EVID-P17-05` | `verification/P17/cargo-packaged.log` | LF | CRLF |
| `P19-UI-FIX-1` | `P19UI-TEST` | `frontend-npm-test-final.log` | LF | CRLF |
| `P19-UI-FIX-1` | `P19UI-FRONTEND-BUILD` | `frontend-npm-build-final.log` | LF | CRLF |

**诊断结果：6 项全部是 `LINE_ENDING_ONLY`。**

验证方法：取出 pin commit 中的 blob，与磁盘文件**各自归一化为 LF**，SHA-256 **完全相同**。

```
bytes: blob=2546 disk=2554 | after LF-normalise identical: True
bytes: blob=2541 disk=2549 | after LF-normalise identical: True
bytes: blob=10003 disk=10093 | after LF-normalise identical: True
bytes: blob=8659 disk=8746 | after LF-normalise identical: True
bytes: blob=149052 disk=151643 | after LF-normalise identical: True
bytes: blob=417 disk=430 | after LF-normalise identical: True
```

**这不是「时间问题」，是「转换问题」**——`core.autocrlf=true` 让工作区是 CRLF、
blob 是 LF，而 pin 是按其中一种字节算的。

**这与 `GOV-EOL-PIN-1` 处理的完全是同一类**，处置也一样：
为这些路径加 `.gitattributes` 的 `text eol=lf`，然后重算 pin。

**关键区别**：`TIME_BASED` 的 63 项**不能重算**（会破坏历史），
`LINE_ENDING` 的 6 项**必须重算**（内容本就相同，只是字节表示不同）。
**两者用相反处置，理由不同。**

## 七、`MISSING_FILE` 23 项 —— 全部集中在一个 Task

| Task | 数量 |
|---|---:|
| **`P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION`** | **23** |

**23 项全部在这一个 Task**，路径形如：

```
.../C3-GIT-TOPLEVEL-RESOLUTION/zcode-owner-preflight-r1.json
.../C3-GIT-TOPLEVEL-RESOLUTION/zcode-owner-preflight-r2.json
.../P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION-R1.md
```

**判断**：这不是 23 个独立问题，是**一个 Task 的路径约定整体失效**
（可能该 Task 的证据放在仓外 workspace，或路径前缀写错）。

**处置**：不在 `GOV-PIN-LINEAGE-1` 范围内。**应作为独立发现上报**，
由 Codex 判断是否单独立项。

**理由**：`GOV-PIN-LINEAGE-1` 定义的是「pin 的 lineage（时间演进）」，
而这 23 项是「路径根本不存在」——**不同性质，不同修法**。

## 八、因此 `GOV-PIN-LINEAGE-1` 的真实范围

| 范围 | 数量 | 是否属本 Task |
|---|---:|---|
| `TIME_BASED` 保留 + lineage | **63** | **是**（r20 §2.2 的主体） |
| `LINE_ENDING` 修 `.gitattributes` + 重算 | **6** | **否**（属 `GOV-EOL-PIN-1` 同类，应单独立项或并入） |
| `MISSING_FILE` 路径失效 | **23** | **否**（性质不同，应单独上报） |

**结论：`GOV-PIN-LINEAGE-1` 的可执行范围是 63 项 `TIME_BASED`，不是 7 项，也不是 92 项。**

## 九、给 Codex 的三个新问题

1. **63 项 vs r20 估计的 7 项**：范围扩大了 9 倍。
   是仍按 r20 原方案（逐项追加 lineage 说明），还是需要重新裁定范围？
2. **6 项 `LINE_ENDING`**：是并入 `GOV-PIN-LINEAGE-1`（因为它们也是 pin 失配），
   还是单独立一个「EOL pin 续修」Task？（`GOV-EOL-PIN-1` 已做过四个路径，
   这 6 个是漏网的）
3. **23 项 `MISSING_FILE`** 全在 `P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION`：
   该 Task 的证据路径整体失效，是路径写错、还是证据在仓外？**需要先诊断再决定是否修。**

## 十、可复跑

```powershell
python C:\Users\49745\AppData\Local\Temp\pin-inventory.py
python C:\Users\49745\AppData\Local\Temp\pin-summary.py
python C:\Users\49745\AppData\Local\Temp\diag-unexplained.py
```

产物：`verification/GOV-PIN-LINEAGE-1/pin-inventory.json`（92 项明细）
