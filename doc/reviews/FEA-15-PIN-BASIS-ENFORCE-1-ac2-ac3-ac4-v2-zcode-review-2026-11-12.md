所有核对完成。现在汇总输出本次独立 Review 报告。

---

# FEA-15-PIN-BASIS-ENFORCE-1 当前候选（AC2/AC3 补测 + AC4 v2）独立 Review 报告

## 1. 审查者与独立来源

- **审查者**：ZCode CLI 全新会话（模型 GLM-5.3），本次 turn 即审查载体。本会话为全新启动，与 AC1d 确认（`sess_fd863071…`）、AC2/AC3 Review（`sess_6b151e7e…`）、follow-up Review（`sess_fb32a1da…`）、AC2/AC3 adjudication（`sess_dbdb62fe…`）均非同一会话；审查者未参与本 Task 任何实现、返修或裁决。
- **session/turn ID**：真实 session/turn ID：sess_426becfe-44b9-4e2e-9f16-9eaccdddbd05 / turn_80b3a6dd-0d90-4edf-b60f-c95ab3fd9f94（由本次 CLI JSON receipt 提取）。
- **方法与边界**：全程只读。主会话仅用 Read；git/sha256sum 核对经只读子代理执行（`git -C` 与复合命令被 plan mode 拦截，改用仓库根裸 git 命令与 `.git` 元数据文件直读等价取证）。未修改任何文件、未提交、未 push、未运行任何测试或 AC5 门禁。

## 2. Reviewed HEAD 与实际检查对象

| 对象 | 声称 | 实测 | 判定 |
|---|---|---|---|
| 主仓库 main | `7f1e7173e` clean | HEAD 一致；porcelain 空 | PASS |
| implementation worktree | 分支 `codex/fea-15-pin-basis-enforce-1` @ `7eefb54d` | 分支 ref 文件=`7eefb54dc…`，无 merge/rebase 进行中 | HEAD PASS（clean 无法独立复测，见 §7） |
| validation-ac2ac3 | HEAD `4ed7f32b3` | 分支 ref=`4ed7f32b3…`，clone-local autocrlf=false、longpaths=true | PASS |
| ac4-v2-clone-t / -f | 均为 candidate HEAD | 双双 detached @ `4ed7f32b3…`；T autocrlf=true / F=false；longpaths 均 true | PASS |
| r0-baseline | `bfae0b9bd` | detached @ `bfae0b9bd…`，autocrlf=false、longpaths=true | PASS |
| R0→7eef 改动 | 限 AC2/AC3 范围 | 4 提交（`fd843602`→`5e216dc5`→`ee0b25ac`→`7eefb54d`）；diff 恰 4 文件 +547/−27，全部在 allowed_paths 内 | PASS |
| 候选与实现一致性 | “blob 三项相同” | **四项**实测一致：check.ps1（`1a6f7ab3…`）、TASK.md（`89371702…`）、test_canonical_evidence_basis.py（`2b82fb2d…`）、test_architecture_assertions.py（`26f79e8a…`）；7eef 侧为 Git blob 口径，4ed 侧为 F-clone 工作树字节（autocrlf=false 且无 eol 规则 ⇒ 等价 blob 口径） | PASS（超卡面声明） |
| 提交图形态 | 未显式声明 | 4ed = main 基点 `dd6372420` + 实现分支 4 提交的 **cherry-pick 重放**（`58ff894`→`a2a3401`→`bf377705`→`4ed7f32`）；**7eef 非 4ed 祖先**，主仓库无 4ed 对象 | 事实确认（见 P3-1） |

## 3. 总体 Verdict

**APPROVED_WITH_LIMITATIONS**（P0=0、P1=0；2×P2、2×P3）。本 Review 不构成最终验收，不裁决、不释放 AC5。

## 4. AC 分项结论

### AC2（新旧表头与 basis 校验）— 成立（限已裁决范围，维持 ACCEPT_WITH_LIMITATIONS）

- 模板新增七列与 BLOB/WORKTREE/EXTERNAL_SHA256 语义说明（`doc/templates/TASK.md` diff `7d318638d→574b82d74`）；checker 严格识别 legacy 六列（不区分大小写）与新七列（大小写敏感、列名精确），非法表头 fail-closed（`EVIDENCE_BASIS_HEADER_INVALID`）。
- 新七列三类 basis 校验完整：BLOB 要求有效 commit+仓库内路径+Git blob 精确 SHA；WORKTREE 要求 `WORKTREE_ENV=` 声明+仓库内+工作树字节精确 SHA、不回退 blob（有判别用例）；EXTERNAL_SHA256 要求仓外可读文件、不可读即 FAIL。legacy 六列保留 r194 OR 语义（worktree 匹配或 blob 匹配），未迁移任何历史 pin。
- 双环境实测：实现 HEAD 7eef 专项 18 passed/9 subtests/EXIT=0（autocrlf=true）；T clone 同口径 EXIT=0；F clone 16 passed+2 skipped/EXIT=0（skip 为 F 下 blob/worktree 字节不可分的前提不成立，与 AC1/AC2/AC3 adjudication §3.3 互补口径一致，README 未计作覆盖通过——诚实）。

### AC3（判别测试覆盖）— 成立；P1-1/P1-3 修复评估为充分

- 412 行专项测试覆盖 AC3 字面清单全部条目（旧格式、basis 缺失/非法/大小写、三类来源、commit 不含路径、缺失路径、PNG exact bytes、CRLF/mixed-EOL、旧格式结果不变），并已落地 adjudication §4.1 的 R-001 四类负例（行 arity／非法 SHA／无效 commit／basis-路径方向，`ee0b25ac` 提交）。
- **P1-1（legacy PNG fallback）修复充分**：`test_legacy_png_blob_fallback_matches_r0_checker` 在同一 fixture 中把 PNG 工作树字节改写为 worktree-only 后，用 blob SHA 作 legacy pin，**对照运行候选 checker 与 `git show R0:check.ps1` 的 R0 checker**，两者均须完整 PASS。这正面覆盖了 follow-up Review 要求的“候选与基线对二进制 pin 判定一致”；在项目钉定的 PowerShell 7.6.9 运行时下新旧实现的字节基一致（P3-6 撤回口径）。四个历史 TaskPath 复跑仍按裁决保留在 AC5。
- **P1-3（正向 fixture 须 checker 整体 PASS）修复充分**：`assert_basis_passes` 现在断言 `FIXTURE_PROCESS_EXIT=0` **且** `Governance check: PASS`，不再是仅查错误串缺失。
- P1-2（证据入库/卡面更新）已闭合：证据提交链 `a9ca1798`→`bb44720a`→`32f229f2`→`a036a85f`→`547f2729`→`7f1e7173` 齐全，卡面/README 同步。

### AC4（跨 checkout 对照）— 证据成立，两项证据质量 P2 待 adjudication 处置

- **T/F gates（native CWD）与卡面逐项一致**：T default/TaskPath 因 Plan 工作树 7035 bytes 超 7000 预算 EXIT=1（各 2 warnings）；T pins 16 mismatch（C01b/C02/C03/C05–C16/FEA01，C04b/C17 OK）EXIT=1——恰等于 AC1c A 既有集合；F default/TaskPath PASS（3 warnings）EXIT=0、pins 仅 C04b/C17 EXIT=1——恰等于 dd637242 基线集合；双侧 API EXIT=0；双侧专项 pytest EXIT=0。四个 wrong-CWD 首跑日志明确作废，未用于结果。
- **C1**：16/16 mismatch 经 CRLF→LF 归一化后与冻结 pin 及候选 HEAD blob 逐项一致，EXIT=0。
- **C2**：T/F 双侧 frozen generator（pin_inventory.py/pin_inventory_delta.py）2/2 HEAD=base=source blob 且 SHA 等于 PIN-POLICY-1 冻结 pin，EXIT=0。
- **三层对照**：R0 inventory 5455 行、T/F 各 5462 行；delta 双侧均 +8/−1/~0；8 条 ADDED 全部归因本 Task 卡，唯一 REMOVED 行为同 evidence_id（`ac1a-stop-readme`）README pin 更新替代；文件级 diff 恰为 Addendum A.1 的 11 路径集（observed=11 expected=11）；历史 4737 路径 1032 raw-equal + 3705 T 侧归一化后相等 + 0 failures。
- **全量治理套件诚实呈现**：61 passed / 2 skipped / 3 failed / 62 subtests / **EXIT=1**，失败为 `test_residual_runtime_identity` 三项（169 个 TABLE_DELIMITER，首例 CHAPTER-SELECTOR-1.md），与既有 dd637242 baseline control 同名复现；README 明示“本 checkpoint 未重跑 baseline”、“失败仍按 FAIL 记录”。未发现任何把 EXIT=1 改写为 PASS 的表述。
- **Canonical Evidence**：最近 22 行 pin（ac2ac3-followup 至表尾）全量复核 **22/22 PASS**——每行 commit 包含该 path 且 Git blob SHA-256 与 pin 逐字符一致；更早 AC1 系行有 AC1d 19 行 blob audit 记录佐证。
- 主仓门禁：da333639 与 54ea97774 两轮 default/TaskPath PASS（3 warnings）、18/18 pins、API 全 EXIT=0。
- Linux NOT_RUN 如实保留。

## 5. Findings

### P0：0 项
### P1：0 项

### P2-1：AC4 v2 生成日志的输出 SHA 与 Canonical pin 系统性口径不一致（工作树 CRLF vs Git blob LF）

- **位置**：`verification/FEA-15-PIN-BASIS-ENFORCE-1/ac4-v2-inventory-audit.log:10`（`AUDIT_JSON_SHA256=acd19f03…`）、`ac4-r0-inventory.log`、`ac4-v2-t-inventory.log`、`ac4-v2-f-inventory.log`、`ac4-v2-t-inventory-delta.log`（含 `BASELINE_SHA256`）、`ac4-v2-f-inventory-delta.log`；README 第 110 行引用 `acd19f03…` 作为 "audit JSON SHA-256"。
- **复现依据**：六份日志声称的输出 SHA 全部等于生成时落盘的工作树字节（实测主仓库当前工作树同值），而 Canonical Evidence pin（`ac321500…`、`578b9e30…`、`6d29d0fd…`、`5206e4c5…`、`9daceedc…`、`ae697e5c…`）为入库 LF blob 口径，两者对每个文件都不同。audit JSON 已双向逐字节闭合（28227=27650+577 CR，`tr -d '\r'` 后等于 blob），**内容零篡改**；根因为 FEA-15 verification 目录无 `.gitattributes` eol 规则（仓库内其他 23 个 verification 子目录均有）+ 生成脚本 Windows 文本模式写盘 + autocrlf=true 入库归一化。
- **影响**：pin→blob 主链路完好可复核（22/22 PASS，checker legacy OR 语义下经 blob fallback 通过）；但日志/README 中的 SHA 无法以 `git show` 口径复现，与本 Task “显式字节基准”主题直接相悖，后续验证者在 LF 检出或 Linux 上会复核失败。
- **必要修复**：README/Task 卡 AC4 段补口径标注（或补录 blob 口径 SHA 六值）；AC5 集成前完成。不阻断 AC4 adjudication，不要求改产品代码。

### P2-2：v2 clone 创建审计的时间戳未按裁决要求证明“配置先于 checkout”

- **位置**：`verification/FEA-15-PIN-BASIS-ENFORCE-1/ac4-v2-clone-creation-audit.log:8-9,16-17`；对照 AC2/AC3 adjudication §5.1（“在日志记录 `.git/config` 写入时间先于 checkout reflog 时间”）与 AC1c B 先例（18:26:32 < 18:26:49，方向正确）。
- **复现依据**：T/F 的 `CONFIG_LAST_WRITE_UTC`（22:21:20.9Z / 22:21:29.4Z）**晚于** `CHECKOUT_REFLOG_UTC`（`2026-11-12T06:20:42+08:00` = 22:20:42Z）38–47 秒，且审计 START（22:21:18Z）先于 config 写入——提示审计脚本可能重设了 config（刷新 last-write）或该字段实为 clone reflog。
- **影响**：行为正确性有独立字节证据闭合（F 检出为 LF、T 为 CRLF、generator integrity 双侧一致——若配置未先于 checkout 生效，F 必然呈现 CRLF 与观察矛盾），故不推翻 AC4 结论；但该审计文件本身未按裁决指定的形态提供顺序证明，字段语义未解释。
- **必要修复**：实现者澄清两个字段的语义与采集方式，必要时以 reflog 原文/原始 config 写入证据补记；随 AC4 adjudication 或 AC5 文档修正。

### P3（informational）

- **P3-1**：候选 4ed 与实现 HEAD 7eef 提交图平行（cherry-pick 重放、非祖先关系），主仓库无 4ed 对象；卡面以 blob 三项声明一致（实测四项一致），但“候选形态=dd637242+4 cherry-pick”未在卡面/README 针对 4ed 显式登记（README 仅对 bf377 描述 overlay 形态）。建议 AC5 集成时登记 7eef↔4ed 映射，防止“集成 4ed”与“集成实现分支”混淆。
- **P3-2**：legacy 分支错误报告顺序变化（class 校验移至路径检查前），一行多错时错误条目更多；fail-closed 方向不变，无静默翻转。
- （R-002 死锁、R-003 作用域、R-004 符号链接、R-005 WORKTREE commit 列、R-006 报错膨胀均已经 adjudication §4 登记处置，本 Review 未发现新证据需要改判，不重复计数。）

## 6. 仍须保留的 limitation / NOT_RUN 清单（核实均在卡面/README 保留）

1. T 侧 default/TaskPath EXIT=1（Plan 工作树 7035/7000 bytes 超预算）与 T 侧 16 个 pin EOL mismatch——保持 FAIL 原样（与 AC1c A 集合一致）。
2. F 侧 C04b/C17 pin mismatch EXIT=1（与 dd637242 基线集合一致）。
3. 全量治理套件 3 failed / EXIT=1（baseline 同名复现，本 checkpoint 未重跑 baseline 已如实披露）。
4. Linux cross-check NOT_RUN。
5. 四个历史 TaskPath（AGPL-RELEASE-1、AD002-FOLLOWUPS-1、FEA-06-PREREQ-1、CHAPTER-SELECTOR-1）、AC5 全部 gates、集成后完整 bundle、最终集成 Review/adjudication 均 NOT_RUN；AC5 NOT RELEASED。
6. Release-R-001 最终 disposition 与 Review-R-001 终闭合仍留 AC5 终裁；R-001 四类负例测试已提前落地（`ee0b25ac`）但终裁确认仍在 AC5。
7. FEA-15 verification 目录 worktree/blob 双字节口径限制（AC1d 段已披露；本次 P2-1 是其新实例）。
8. 本 Review 自身：implementation worktree 与各 clone 的 clean 状态因 plan mode 权限拦截无法独立实测（HEAD/配置经 `.git` 元数据核实；无 merge/rebase 进行中标志）；4ed 侧 blob 以 F-clone 工作树等价口径实测；未运行任何测试/门禁。

## 7. 对“单独 ZCode AC4 adjudication”的建议

**可以进入**。本次 Review 结论为 APPROVED_WITH_LIMITATIONS、P0/P1=0，AC4 证据的行为结论（gates/C1/C2/三层对照/诚实登记）全部经独立复核成立。建议该 adjudication 由**另一个**新 ZCode session 执行（与本 Review 及既往各 session 均不同上下文），裁决输入至少包含：

1. 本报告 P2-1、P2-2 的处置（建议：均作为 AC4 接受的附带条件——口径标注补全与审计字段澄清列入 AC5 集成前置或随 AC5 文档修正，不要求改动产品代码/测试）；
2. P3-1 的 7eef↔4ed 映射登记建议；
3. T 侧 Plan 预算 FAIL 与 16 mismatch 是否按 AC1c A 同类口径锚定为 autocrlf=true 确定性效应（本 Review 注意到其机制与 AC1c A 的 7056/6992 完全同源，支持锚定，但该裁定权在 adjudication）；
4. AC5 维持 NOT RELEASED；Release-R-001/Review-R-001 终闭合留 AC5 终裁。

**无需下一步操作由本 Review 触发的仓库改动**；推荐下一步：将本报告原文保存为 `doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-ac4-v2-zcode-review-2026-11-12.md`（补录真实 session/turn ID）并提交后，委托新的独立 ZCode session 执行 AC4 adjudication。
