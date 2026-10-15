# P02-NEW-TIME-X6 — T-only bounded Review（DSH r3）

| 项 | 值 |
|---|---|
| **reviewed_head** | `839e0089c971e9be984cd9e99a56ea0152ec1391` |
| **输入 manifest** | `verification/P02-NEW-TIME-X6/dsh-source-review-input-manifest-r3.json` |
| **manifest SHA-256** | `92E00F202E0CA460EBF33C5E61015C3CB4DDB5C3D119C0D7533CB35C20513180` |
| **source_commit** | `c83f65ade88d99046f26a1328f395af8621d12e7` |
| **Decision** | **PASS** |
| **P0/P1/P2** | **0 / 0 / 0** |

范围仅为三项指定问题；未扩大为 unrestricted audit，未修改任何文件（只读）。

---

## 1. Pin / 输入核验

**可核（离线交叉核对，全部一致）**

- r3 manifest 声明 9 个输入（`:11-75`），与官方 verifier 记录 9/9 相符（本报告不独立运行该 verifier）。
- **声明级不变式**：r3 manifest 的 executor 条目 = r2 manifest 的 executor 条目（`sha256=43ee7be2…`、`bytes=105343`、`blob=54afebd9…`；`r3:20-24` ≡ `r2:27-31`）；protocol r2 / inventory r2 / source-manifest r2 三条目亦逐字相同（`r3:33-52` ≡ `r2:41-59, 48-52`）。→ 本轮**未改** executor 与协议/清单类制品。
- selftest 条目**确有变化**：`a8823f59…/85767 B` → `9e113849…/85831 B`（`r2:34-38` → `r3:27-31`），**+64 B**，与“仅改两行”自洽（详见 §4）。
- **内容级核对**：工作树 executor 仍含 r2 已审的 SR-01/02 标记（`EXEC:1728` `--absolute-git-dir`、`:1863-1931` worktree index 检查、`:129` `MainRepositoryRoot`、`:577/607/614/1501/1505` dot-segment 与双根门），且无 `--git-common-dir`。→ 与“executor/runtime 源码保持不变”一致。
- Task 侧记录与本次范围自洽：`TASK:25` `revisions {implementation: 2, test: 2, evidence: 9}`；`TASK:77/78/79/104/105`；失败 stdout pin `2E60D9D5…`（`TASK:133/151`）与本轮派发陈述一致；7 项 SKIP 与“保留 fixture”同记录（`TASK:104`），selftest 内 `Add-Skip` 实为 7 条（`SELFTEST:122-128`），与 271/1/7 计数形状自洽。

**不可核（未采信为已复算）**：`pwsh` 在本会话因沙箱无法为工作区建立写授权而不可用（Win32 5，审批通道不可用），故**未执行任何命令**；manifest 自身 SHA-256、9 个文件的磁盘 SHA-256/`git_blob`、`HEAD=839e0089…`、clean 状态**均未由我复算**，采信 Codex 官方 verifier（9/9）与 Task 记录。

---

## 2. Q1 — 该失败是否确由 fixture/断言名不一致，修正后的断言语义与覆盖

| id | severity | disposition | evidence |
|---|---|---|---|
| **X6-T3-01** | 无（no defect） | **ACCEPT / 关闭** | 见下 |

- **根因确认为 fixture 与断言名字不一致**：fixture 中 pin 名为 `executor-source`（`SELFTEST:620`），而原断言硬编码 `collector-source`（r2 版 `:713`），二者永不相等 → 该断言恒 FAIL。executor 与 freeze-manifest 契约本身无缺陷：生产端 `Test-FreezeManifestBinding` 强制的是 self-pin **path**（`EXEC:820-831` 语义），pin `name` 为自由文本。
- **修正后断言语义（`SELFTEST:765`）**：
  `$meta.frozenTaskDeliverablePins[0].name -ceq $validManifest.taskDeliverablePins[0].name` **且** `...sha256 -ceq $collectorSelfSha`。
  → 第 1 条正是“meta pin name **原样来自** `$validManifest.taskDeliverablePins[0].name`”的 verbatim-copy 校验；第 2 条**保留** executor self-pin SHA 校验（fixture self-pin SHA 经 meta 工厂原样带出）。`$collectorSelfSha` 仍定义并注入 fixture（`SELFTEST:620`）。
- **无新增抛错风险**：`$validManifest.taskDeliverablePins[0]` 的数组索引在同一脚本内已被既有断言使用并通过（`SELFTEST:675-676`，attempt 1 中非失败项），故为已验证可用的访问形式。
- **manifest pin shape 覆盖仍完整保留**：
  - 字段完整性矩阵含 `taskDeliverablePins`（`SELFTEST:630`）；
  - pin shape 反例 `freeze-manifest-incomplete-pin-fails`（`:650`，缺 name/path/size/sha256 → 报 `contractPins[0]` 错误）；
  - self-pin 生产校验反例 `freeze-manifest-binding-missing-collector-self-pin-fails`（`:660-662`）；
  - meta 线 pin 原样性与 JSON round-trip：`:765` + `meta-json-roundtrip`（`:768`，要求 `frozenContractPins[0].sha256` 存在）；
  - pin 路径的历史隔离覆盖（`:674-678`）。
  → 断言**未被弱化为空断言**，且原测试含义（meta 线承载 manifest pins 且 self-pin SHA 完好）被更准确地表达。

---

## 3. Q2 — summary `revision` 标注准确性

| id | severity | disposition | evidence |
|---|---|---|---|
| **X6-T3-02** | 无（no defect） | **ACCEPT** | 见下 |

`SELFTEST:921`：`revision = 'x6-selftest-r2 (T-only AC2 assertion correction; executor r2 includes SR-01/02/03 repairs)'`

- “**x6-selftest-r2**” ↔ `TASK:25` `revisions.test: 2`（T-only 修正 = test revision 2），并与 `TASK:105` 对该标签的记载一致 → **准确**。
- “**T-only AC2 assertion correction**” ↔ 实际改动仅为本 selftest 的断言/说明文字，executor 未改（r3 manifest executor 条目与 r2 逐字相同） → **准确**。
- “**executor r2 includes SR-01/02/03 repairs**” ↔ `TASK:25` `revisions.implementation: 2`；executor 字节 pin 未变且正是含 SR-01/02/03 修复的 r2 版本 → **准确**。
- 唯一可读性提示（**非缺陷、不请求返修**）：标签中的 “r2” 与 I1 “source delivery r2”（`source-manifest-r2.json` 曾 pin 另一 selftest 哈希 `a8823f59…`）字面重合；括注已作区分，且字节身份应以 commit/hash pin（`839e0089` / `9e113849…`）为准而非标签。

---

## 4. Q3 — 是否引入新 P0/P1/P2、破坏原 AC 测试含义、或带来安全/数据损坏/不可逆风险

| id | severity | disposition | evidence |
|---|---|---|---|
| **X6-T3-03** | 无（no defect） | **ACCEPT / 无回归** | 见下 |

- **改动面**：仅两处语义性内容（`SELFTEST:765` 断言谓词+说明、`:921` revision 字符串）；声明字节差 +64 B（85767 → 85831），与“两行”自洽；未触及 fixture 定义（`:620` 不变）、shape/binding 反例集、SKIP 表、fixture 写入逻辑与退出判定（`:944` `exit 1 if assertsFailed>0`）。
- **无新 P0/P1/P2**：无新增写入/删除/替换/执行/子进程/网络/注册表；新谓词为既有内存对象的纯比较；断言集合**只增不减**，不存在把失败“改绿”的绕过（原断言预期值由 fixture 自身派生，仍要求 name 原样 + SHA 一致）。
- **原 AC 测试含义未被破坏**：AC2 的“Parser 零错误 + 纯内存 selftest 通过 + 记录 exit/SKIP”要求与 selftest 结构均未变；production self-pin 与 pin shape 覆盖保留（§2）。
- **安全/数据损坏/不可逆风险**：无。本次仅改测试源码文本；executor/runtime 源码声明与内容均未变（§1）；不新增任何可写路径或可删除目标。
- **明确未做的主张**：本次只 review **修正**本身。**修复后的 Parser/selftest 尚未由 Codex 重跑，故 X6-AC2 仍未 PASS**；`TASK:78` 亦如此记载（“故 AC2 尚未 PASS”）。

---

## 5. 阻塞结论

**无 blocker。P0 = 0，P1 = 0，P2 = 0。** 本次 T-only 有界 Review **通过**（PASS），不请求再次返修、不消耗 I2（I1/I2 仍 1/2）。

X6-SR-01/02/03 已关闭、X6-SR-04..13 保持 backlog；DSH r2 的非阻塞观察 N1（`\\?\`/`//?/` 等路径形式）与 N2（`<RunId>/` 阶段措辞）按 `codex-source-review-adjudication-r2.md:17/19` 作为 Codex freeze/pre-run 的路径与阶段约束处理，非本轮 blocker。

---

## 6. 未运行事项（NOT_RUN，本轮不可据此放行）

- 我本人：未执行任何命令（含只读命令），未运行 Parser / selftest / executor / probe / 测试，未产生任何文件写入。
- 修复后的 Parser 与纯内存 selftest：**NOT_RUN（待 Codex 重跑）** → AC2 保持未 PASS。
- Codex freeze、final pre-run：**NOT_RUN / 未放行**。
- X6 executor one-shot、result VERIFY、post-run Review、Build/Cargo、Windows Sandbox、产品 AC1–AC7：**全部未放行（NOT_RUN）**。
- 需 Codex 复核：manifest SHA `92E00F20…` 与 9 个文件磁盘 hash/blob/HEAD 复算（注意 `core.autocrlf` 行尾展开）；`r2→r3` 的 `git diff` 确认 selftest 仅两行、executor 与其他 r2 制品零改动；修复后 Parser 零错误 + selftest exit 0（SKIP 逐项记录）。
- 旧 H1/P2-1 结论与 13 项历史缺失记录**保持原样**，本轮不读取、不补齐、不替代、不代表。
