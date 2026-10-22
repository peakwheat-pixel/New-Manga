已完成 Round 2 静态文档复核，报告写入 `verification/P02/dsh-p02pre-r0s5-review-r2-20261011.md`（除该文件外未改动任何对象；未运行命令/API/测试，未做 bytes/hash/Git/OS 核验）。

## 决策：`CHANGES_REQUESTED`（P0/P1/P2/P3 = 0/0/1/4）

### Round 1 finding 处置
| Round 1 ID | 结论 |
|---|---|
| DSH-R0S5-P2-01 | **已解决（实质）**：manifest L20/L32/L46 已写“R0 evidence §`固定文件 hash 前/后对照` 的精确 13 项 = 12 份列名文档 + `.git/index`”，声明 `Get-FileHash` 为历史方法、current hashes 未采集、且非 R6 全量清单；12 个文件名与 R0 evidence L235–L246 逐行吻合。遗留引用缺陷见新 P3-01。 |
| DSH-R0S5-P2-02 | **部分解决 → 阻断**：身份基准（`HOME-MY\49745` / SID / 非提权 / 无 impersonation）与 28 项计数、12 输入根 + 13 scratch leaf 枚举均与 r6 逐条一致；但 canary leaf 根路径写错（见 P2-01），"No protected/deny path is added" 未满足。 |
| P3-01 / P3-02 / P3-03 | **已解决**（Task L5=`in_review` 且 STATUS/PLAN/INDEX 一致；manifest L5 明写 R0S5 新增授权、不extend 旧 waiver；治理文本已改为条件式）。 |
| P3-04 | **结构已满足**：L44–L46 final 类 AC 保持未勾选；但 L41 勾选失准（新 P3-04）。 |

### 新增 findings
| ID | 级别 | 位置 | 要点 |
|---|---|---|---|
| **DSH-R0S5R2-P2-01** | **P2** | manifest L42（涉 L30/L44）；Task L53/L55 | 三个 canary leaf 被写成**主仓** `G:\CODEX\New Manga\verification\P02\tmp\...`。r6 L35/L115/L141–143/L157 把 “3 canary 规则”绑在 scratch `G:\CODEX\P02-scratch-build-source`，R0 evidence L114–L117 的历史查询也全在 scratch 内。后果：把 r6 明列 protected/deny 的主仓加入 28 项 ACL 候选，与 manifest 自身 L30、L44 自相矛盾；一旦 runner gate 解除，可能误指向受保护目录（含正向 canary 写入）。 |
| DSH-R0S5R2-P3-01 | P3 | manifest L20 | 引用 `R0 evidence §实际命令` 不存在；实际在 §`实际执行调用与结果`（L18/L29），或 r6 L229。 |
| DSH-R0S5R2-P3-02 | P3 | Task L71 | 写入所有权只列 Round 1 Review 文件，未含 L34 已登记的 `dsh-p02pre-r0s5-review-r2-20261011.md`。 |
| DSH-R0S5R2-P3-03 | P3 | Task L26 | 仍写“审查并执行**已证明安全**的只读候选，**再由** Reviewer Review”，与 L43/L75、manifest L50/L56 的“无 getter 已清除、先审后执行”相左。 |
| DSH-R0S5R2-P3-04 | P3 | Task L41 | AC 勾选 `[x]`（只引用 r6 精确对象）与 canary 根路径错误冲突。 |

### 未能独立验证
输入对象的 bytes/SHA-256（含 prompt 与 manifest L21 的 pin 值）；live Git HEAD/tree/branch/worktree 与 `.git/index` hash；宿主与 OS/Registry/WER/profile/token/ACL 实际状态（含 `verification\P02\tmp\` 两处 canary 的落盘情况）；“本轮零 host 查询/零写入”这一 Owner 自我报告；r6 与 R0 evidence 是否为其冻结版本。

### 安全面
未发现隐藏查询授权或扩权：runner 仍为 `NOT_SAFE_FOR_R0`，manifest L56 的零查询冻结与 Task L43/L62/L75、delivery L13 一致；授权未被写成 waiver、Gate PASS、Build Barrier 放行或 build/Cargo/AC1–AC7 许可。唯一实质缺口是 P2-01，且其危害目前被零查询冻结中和。

### 推荐下一步（唯一）
由 `Codex /root` 修正 manifest L42 的 canary 根路径（改回 scratch 根并注明相对根）、L20 引用、Task L26/L41/L71 措辞，然后重发 Round 3 文档复核；因 P2-01 属“精确对象集”实质变更，**不得**沿用本轮判断。期间不得执行任何 host/OS/Registry/WER/profile/token/ACL/path/env/hash 查询，不得换 shell 或运行 getter，不得创建/删除 profile 或触碰 Sandbox、Build/Cargo、AC1–AC7。
