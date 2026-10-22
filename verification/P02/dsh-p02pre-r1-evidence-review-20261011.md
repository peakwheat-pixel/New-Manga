```yaml
task_id: P02PRE-R1
reviewer: DeepSeek Harness（非作者）
author: Codex /root
base_commit: cddff58469b56e181019a8ddfeade80684bc7eb9
reviewed_head: cddff58469b56e181019a8ddfeade80684bc7eb9
decision: changes_requested
```

# Review：P02PRE-R1 一次性只读取证的实际结果（partial evidence）

## 范围与依据

**审查对象**：唯一实际运行结果 `verification/P02/p02pre-r1-evidence-20261011.json`（`2588454 bytes`，pin SHA-256 `8A1A056600F6A1B5C2E7980E4CCAE2B3DB085B1EF7EC7DC5CC7FD35A4A068B9C`；我只读其**文本内容**，未复算 hash）。

**对照输入（只读）**：`doc/tasks/P02PRE-R1.md`、`verification/P02/p02pre-r1-manifest-20261011.md`、`verification/P02/p02pre-r1-capture.ps1`、`doc/templates/REVIEW.md`。

**实际采集内容（我从 JSON 逐项读取到的）**

- 头：`task=P02PRE-R1`、`t0Utc=2026-10-11T07:01:01.5754915Z`、`cwd=G:\CODEX\New Manga`、`command` 与 Manifest `:13` 冻结 argv 一致；`process.powerShellVersion=5.1.26100.9549`、`hostName=ConsoleHost`。
- 身份：`name=HOME-MY\49745`、`sid=S-1-5-21-2196946971-914346751-4210154634-1001`、`authenticationType=CloudAP`、`impersonationLevel=None`、`isSystem=false`、`isAdministrator=false`、`whoami.exitCode=0`（含 token 组/完整性级别 Medium）。
- Git（main）：`revParse.exitCode=0`，stdout 四行 = `G:/CODEX/New Manga` / `.git` / `cddff584…7eb9` / `c25d051a…9f2b`；`branch.exitCode=0` → `main`；`status.exitCode=0`（`rawByteCount=41249`、`nulSegmentCountApprox=651`、SHA-256 已记）、`ls-files.exitCode=0`；`targetMatches=true`。
- 受保护清单：已逐个记录 **662** 条 regular file（`fileInventory` 首条起、末条止，均含 path/length/LastWriteTimeUtc/SHA-256），随后在该数组结束后停止；`gitMetadata=[]`、`gitMetadataAfter` 缺失、`indexStable`/`gitMetadataComplete` 未产生。
- 停止点：`repository.main.error = "System.Management.Automation.RuntimeException: Reparse path in protected inventory: .codex/skills/ask-matt"`（第 13137 行），`repository.main.state = "PROTECTED_HASH_FAILED"`（第 4121 行）。
- 未执行部分：`environment={}`、`paths={}`、`wer={}`、`protectedHashes={}`（均为空对象）；`classifications` 只保留脚本初始化值加身份项；`errors=[]`；`stopReason="MAIN_REPOSITORY_BASELINE_OR_HASH_FAILED"`。
- 未触碰证据：`rootPathChain`/`gitDirPathChain` 均为 `PRESENT` 且全链 `reparsePoint=false`；`gitMetadataBefore`（`.git/index`）`state=PRESENT`、`length=972663`、`lastWriteTimeUtc=2026-10-10T03:18:18.4750975Z`、SHA-256 `214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`。

**未审到的部分**：全部下游对象（scratch 仓库、12 输入根、13 输出叶、3 canary 叶、TEMP/cache 36 变量、3 个 WER 目录、WER 两个 LocalDumps key×两 view×四 value、12 个受保护文件 hash、ACL 端点前后比较）在本次运行中**均未执行**，故无可审证据。

---

## Architecture / 安全面结论

| 项 | 结论 | 依据 |
|---|---|---|
| 写入面是否只有唯一 `CreateNew` 证据文件 | `PASS_WITH_EVIDENCE` | 产出文件即 Manifest `:15` 的唯一路径；无 append/overwrite 迹象；脚本为单次写入（`ps1:546`） |
| 是否越出 allowlist（路径/对象/进程） | `PASS_WITH_EVIDENCE`（就本次已到达范围而言） | 访问对象=身份 getter、主仓 `.git` 链、`rev-parse`/`symbolic-ref`/`status`/`ls-files`、受保护清单枚举；无 scratch/WER/registry/ACL 访问记录 |
| 是否调用 profile API / 写 registry / 改 ACL / canary 写 / build / Cargo / AC / Sandbox | `PASS_WITH_EVIDENCE`（未发生） | JSON 中不存在相应对象或结果；且运行在受保护清单阶段即已停止 |
| 主仓 `.git/index` 是否被本次运行改动 | `PASS_WITH_EVIDENCE`（未改动） | 只记录到运行前 `gitMetadataBefore`（含 SHA-256，LastWrite 早于 T0），无运行后快照要求被触发 |
| 发现 reparse/symlink 时是否安全停机（不跟随、不读取、不清理） | `PASS_WITH_EVIDENCE` | 错误串明示 "Reparse path in protected inventory: .codex/skills/ask-matt"；该对象之后未再访问；无删除/覆盖动作 |
| 是否把未执行的 getter 记成 FAILED 或 PASS | `PASS_WITH_EVIDENCE`（未发生） | 下游对象在 JSON 中**根本不存在**（`environment/paths/wer/protectedHashes` 为空对象），未伪造成 FAILED，也未标 PASS |
| 是否把 UNPROVABLE 改成 PASS | `PASS_WITH_EVIDENCE`（未发生） | `private_registry_absence=UNPROVABLE`、`tempCache=UNPROVABLE`、`werEffectivePolicy=UNPROVABLE`、`process_and_path_access_closure=UNPROVABLE_NOT_MONITORED_IN_R1` 原样保留 |
| 是否将本次查询成功解释为 Gate PASS | `PASS_WITH_EVIDENCE`（未发生） | `hostIdentity` 仅 `PASS_WITH_EVIDENCE`；无任何 Gate 结论；`product_build_and_ac1_ac7=NOT_RUN` |
| Task/Manifest 的“单次调用即取得完整受保护清单基线”设计假设 vs 实际仓库 | `FAILED`（设计假设不成立，非脚本缺陷） | 主仓 Git 索引包含 reparse 型登记对象（`.codex/skills/ask-matt` 等），脚本按冻结规则必然停机，清单无法在本次形态下完整枚举 |

---

## Verification 结论（逐项，按冻结分类口径）

| # | getter / 检查 | 结论 | 依据 |
|---|---|---|---|
| 1 | 证据目标不存在门 + 单次 `CreateNew` 写入 | `PASS_WITH_EVIDENCE` | 证据文件已生成且为唯一运行结果；未发现第二份/追加 |
| 2 | 执行身份与冻结期望（user/SID/非提权/非 impersonation） | `PASS_WITH_EVIDENCE` | `name`/`sid` 与 `manifest:21` 完全一致；`isAdministrator=false`；`impersonationLevel=None`；`whoami.exitCode=0` |
| 3 | `whoami /all` 子进程与原始 bytes | `PASS_WITH_EVIDENCE` | 记录 executable/argv/exit/raw bytes；`stderr` 空 |
| 4 | main 仓库 Git 目标（toplevel/common-dir/HEAD/tree/branch） | `PASS_WITH_EVIDENCE` | `targetMatches=true`，四项与冻结值逐字一致 |
| 5 | Git 原始 stdout bytes（status SHA-256/字节数/NUL 计数） | `PASS_WITH_EVIDENCE` | status 记录 `rawByteCount=41249`、`nulSegmentCountApprox=651`、SHA-256；`exitCode=0`、`stderr` 空 |
| 6 | 受保护清单逐文件 hash（main，运行前） | `FAILED`（在 reparse 边界停机；已完成 662 条） | `state=PROTECTED_HASH_FAILED` + 错误串 |
| 7 | `.git/HEAD`/`index`/`config` metadata 与 index 前后稳定断言 | `NOT_RUN` | `gitMetadata` 为空、`gitMetadataAfter` 缺失；仅保留运行前 index 快照 |
| 8 | scratch 仓库基线（HEAD/tree/DETACHED/common-dir） | `NOT_RUN` | `paths`/`environment` 为空；main 失败后脚本按规则跳过 |
| 9 | 12 个只读输入根 metadata/owner/DACL/路径链 | `NOT_RUN` | `paths={}` |
| 10 | 13 个 scratch 输出叶 + 3 个 canary 叶 metadata/ACL/直接 entry count | `NOT_RUN` | `paths={}` |
| 11 | TEMP/cache/config 36 个环境变量读取与 HOMEDRIVE+HOMEPATH 一致性 | `NOT_RUN` | `environment={}`；`homeEnvironmentCheck` 未产生 |
| 12 | 3 个 WER 目录 metadata/ACL | `NOT_RUN` | `wer={}` |
| 13 | WER 两 key×两 view×四 value 只读 getter（含 registry error 计数） | `NOT_RUN` | `wer={}` |
| 14 | ACL 端点前后比较（owner/SDDL/祖先链）与 `ACL_UNVERIFIABLE`/`ACL_QUERY_ERROR` 分类 | `NOT_RUN` | 无 `aclStability` |
| 15 | 12 个受保护文件 hash（含本 Task/manifest/脚本自身） | `NOT_RUN` | `protectedHashes={}` |
| 16 | 汇总计数与 fail-stop 聚合（`summary`） | `NOT_RUN` | 无 `summary`（停机早于汇总）；顶层 `stopReason` 有效 |
| 17 | 有效权限 / 瞬时 ACL 写 / OS access closure / 动态子进程与写入闭包 | `REQUIRES_ACTIVE_TEST` | Manifest `:65`/`:71` 明示；本次未测 |
| 18 | private registry absence / profile 路径与 store / 有效 WER policy | `UNPROVABLE` | JSON 分类原样保留，未被执行结果“洗白” |
| 19 | Build / Cargo / AC1–AC7 | `NOT_RUN` | JSON `product_build_and_ac1_ac7=NOT_RUN`；本次未执行 |
| 20 | Windows Sandbox | N/A（按用户决定在范围外） | 无相关对象 |

**结论**：本次 partial 结果**支持其记录的 `stopReason`**（`MAIN_REPOSITORY_BASELINE_OR_HASH_FAILED` 与 `repository.main.state=PROTECTED_HASH_FAILED` 因果一致），**停在了预期的 reparse 边界**，且未把任何未执行的 getter 写成 FAILED/PASS。但**这份 partial 不足以支撑 R1 的基线目标**：受保护清单未闭合（662/未知总数），下游全部 getter 未运行。

---

## Findings

| ID | 级别 | 文件/行（证据位置） | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| F-01 | **P1** | `p02pre-r1-evidence-20261011.json:13137` + `:4121`；对照 `manifest:64`、`task:61` | **主仓 Git 索引内含 reparse 型登记对象**（首个为 `.codex/skills/ask-matt`，其后同类 `.dsh/skills/*`、`.gemini/antigravity/skills/*` 等）。脚本按冻结规则正确停机，但该条件**确定性复现**：换时间、加轮次、放行新 run 都会在同一处停住，受保护清单永远无法在“只读、不跟随 reparse”前提下完成 → R1 无法产出其核心基线，后续（R2 及 Gate 输入）始终缺少 main/scratch 的完整 protected inventory 与 index 前后断言 | `error` 原文字面值；`state=PROTECTED_HASH_FAILED`；`gitMetadata=[]`；`paths/environment/wer/protectedHashes` 全空 | 不要重跑同一脚本期待不同结果。请 Codex 在 adjudication 中给出轨径决定，例如：(a) 接受本次停机为 R1 的**正式结果**，把“受保护清单闭包”整体改判 `UNPROVABLE`/`REQUIRES_ACTIVE_TEST` 并明确 R2 输入缺项；(b) 冻结修订版 manifest/脚本，对 Git 登记的非 regular（mode `120000`/symlink/reparse）对象规定**只记 metadata/mode、不跟随、不 hash、不断言内容**的显式分支（并保留拒绝跟随原则），重新走 Review；两轨都需新 Review + adjudication，不得就地放宽 | open（需 Codex 裁决） |
| F-02 | **P2** | 同上 `:4231-4233`、`:4894`、`:13135` | **清单在 reparse 前只完成 662 条**，无总数、无“剩余未处理”计数：`paths` 被完整转储但无 `processedCount/omittedCount`，fail-stop 记录里也没有已处理数。裁决者只能靠人工数出 662，无法从证据本身判断覆盖率与缺口大小 | `fileInventory` 条目区间（第 145–4116 行）为 662 条；`.codex/skills/ask-matt` 是第 663 个 `paths` 元素；无任何 count 字段 | 在 fail-stop 记录中增加 `processedCount`/`totalCandidateCount`/`firstBlockingPath`（并保留原错误串），使 partial 的“缺了多少”自证；无需改动 allowlist | open（下次修订或 adjudication 记录中补） |
| F-03 | **P3** | 同上 `:13135` | `paths` 数组末尾有一个**空字符串元素**（与 Git NUL 记录数/`fileInventory` 数不完全对齐），且该元素本会在循环中产生一次无效迭代。不影响本次结果（更早即抛出），但属清单口径的隐性不一致，可能被误读为“存在一个空路径对象” | 第 13135 行 `""`，位于 `wiki/repowiki/repo-map.txt` 之后 | 在证据中省略空路径或显式过滤并记录；同时在 `paths` 旁注明其来源与去重口径 | open（文档/实现微调） |
| F-04 | **P3** | 同上 `:51-57`、`:74-78`（`commands`）、`:22-25`（`whoami`） | `ConvertTo-Json` 把命令记录序列化成**数组**，**前两个元素为空对象**、真实记录在索引 `[2]`。字段本身完整，但读者/工具若按索引 `[0]` 取记录会取到空对象，增加误读风险 | `revParse`/`branch`/`status`/`files` 四处同一形态；`whoami` 亦为三元素数组 | 序列化前取单个对象（或在证据中加 `commands.<name>.record` 单值副本），避免空占位元素；不改动查询语义 | open（可随下次修订一并清理） |

无 P0。**在记录范围内未发现**：越权读写、profile API 调用、registry/ACL 变更、canary 写、build/Cargo/AC、Sandbox 接触，或把未执行项写成 PASS/FAILED 的情形；`whoami` 文本存在编码显示乱码，但其原始 bytes/hash/Base64 同记录保留，故不单列为 finding。

---

## 结论与复审

**decision：`changes_requested`**

1. **本次 partial 结果本身可被采信为“一次按规则安全停机的真实运行”**：身份与 Git 目标匹配、唯一 `CreateNew` 证据写入、reparse 边界正确停机、未越界、未伪造分类、`stopReason` 与仓库状态因果自洽。
2. **Codex 可以 adjudicate 这份 partial evidence**，并可在其基础上**规划新的、单独 Review 的采集**——因为脚本无缺陷、停机可解释、失败原因明确。但请把 F-01 作为裁决输入：**同一脚本的再次运行不会推进**（同一 reparse 条件必然再次触发），必须先在 Task/manifest 层决定“接受停机并改判闭包为 UNPROVABLE”还是“冻结显式处理 Git 登记非 regular 对象的修订版”。
3. **本次批准/不批准均不等于**：新脚本或新运行的放行授权、R1 Task 完成、以及任何 P02 Gate 的通过。R1 的基线目标（完整受保护清单、index 前后断言、scratch/TEMP-cache/WER/ACL 与动态隔离输入）在本结果中**仍未成立**。
4. **建议的最小下一步**：Codex 先 adjudicate 本 partial（含 F-01 轨径选择），再按所选轨径冻结修订并**另行**取得非作者 Review 后，才谈唯一一次新采集；期间不得创建第二份 evidence、不得放宽 reparse 边界。

**保持不变的 Gate/Owner 状态（本 Review 不授权任何变更）**：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。

### Limitations（阻止/限制我独立验证的事项）

- **未复算任何 hash 或字节数**：`pwsh` 工具在本会话沙箱准备阶段即失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)`）。因此 evidence 的 `2588454 bytes` 与 pin SHA-256 的匹配**未经我验证**；JSON 内部各 SHA-256 字段（含 status、受保护清单条目、`.git/index`）也**未经我复算**，我仅核对其存在性与字段自洽性。
- **未执行任何命令**：未运行 capture/脚本/PowerShell/Git/OS/ACL/registry/WER/environment/hash query；未 build/Cargo/AC；未修改任何项目文件（本报告由派发方保存）。
- **按边界未做的动作**：未解码或回显原始 Git-status Base64、未列举其中文件名单；未解析/跟随/读取 `.codex/skills/ask-matt` 链接目标或其内容，也未推断其指向；未读取用户漫画/库/数据。
- **未复核项**：scratch 实际 HEAD/tree；`paths` 数组的“空字符串”与 Git NUL 记录数差异的确切成因（仅记录现象）；`whoami` 原始 bytes 与展示文本的编码对应关系（仅确认 raw bytes 已保存）。
- **静态/证据审查不证明**任何宿主条件已通过，也不构成任何 Gate PASS。