# Review R3：P02PRE-R0S5（Round 2 整改后的独立复核）

> 纯静态文档审查：只读文本，未执行命令、未启动 runner/shell、未调用 API、未运行测试或 P02PRE 查询、未检查宿主、除本报告外未修改任何对象。不声称核验过任何 bytes/SHA-256、Git 或宿主机状态。

**决策：`APPROVED`（P0/P1/P2/P3 = 0/0/0/1，唯一 P3 非阻断）**

## Round 2 findings 逐项处置

| Round 2 ID | 级别 | 结论 | 依据 |
|---|---|---|---|
| **DSH-R0S5R2-P2-01**（canary 根） | P2 | **已解决** | manifest L42 第 3 组已改为 `root=G:\CODEX\P02-scratch-build-source` + 三项相对 leaf `verification/P02/tmp/{smoke-readonly-probe,lpac-write-control,lpac-write-deny-control}/`，并显式声明它们不在 `G:\CODEX\New Manga` 下。与 r6 L35/L115/L141–L143/L157 及 R0 evidence L114–L117（历史查询全在 scratch 内）一致；L44 对主仓/工作树/其它 clone 的 ACL 禁止原样保留。全文与 `*r0s5*` grep **无任何 canary leaf 指向主仓**。**未授权写 canary**：manifest L30 限 descriptor 只读、L61/L64 禁止写入与权限 canary，Task L55/L61 为“不试写/禁止写入”。 |
| DSH-R0S5R2-P3-01 | P3 | **已解决** | manifest L20 引作 R0 evidence §`实际执行调用与结果`, L18–L29（L18 确为该段落、L29 确为 `Get-FileHash` 行），并附 r6 L229。限制表述准确：历史方法不证明当前 runner 安全；13 项（12 份列名文档 + `.git/index`）不是完整 protected-file inventory；L46 的 12 个文件名与 R0 evidence L235–L246 逐行一致。 |
| DSH-R0S5R2-P3-02 | P3 | **已解决** | Task L71 并列三个精确报告路径（Round 1/2/3）并以“仅”限定；prompt/log 按 L34 归 Codex，未授予无关写入。 |
| DSH-R0S5R2-P3-03 | P3 | **已解决** | Task L26 已改为「先核对精确执行边界；只有当某一候选逐项取得无副作用证据、经非作者 Reviewer Review 和 Codex adjudication 清除后，才执行对应只读检查。当前没有候选获准运行。」 |
| DSH-R0S5R2-P3-04 | P3 | **已解决** | L41 `[x]` 与修订后的 r6 精确对象集相符（12 输入根 / 13 scratch leaf / 3 canary leaf = 28，对 r6 L74–L85/L123–L135/L141–L143 逐条一致）；Profile 路径不猜测；final 类 AC（L44–L46）保持 `[ ]`。 |

## 新增检查

- **无隐藏查询授权**：manifest L50/L54/L56 冻结 runner 与全部 getter（“no P02PRE host/…/hash query is permitted”），Task L26/L43/L62/L75、delivery L17 一致，无“已放行/可运行”措辞。
- **runner 仍为 `NOT_SAFE_FOR_R0`**：manifest §3/L56、delivery L27、Task L42；本 Review 不代表清除 shell、任何 getter 或 Build Barrier。
- **授权未升级**：Task/manifest/delivery/STATUS/PLAN/INDEX/P02.md 逐项维持五值风险原值、固定英文原文，以及 Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、build/Cargo=`NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`；未发现 profile/registry/ACL/file 写入、Windows Sandbox 或 Build/Cargo 授权扩张。
- **状态机一致**：Task `in_review`；STATUS/PLAN/INDEX/P02.md 均记 Round 1 `0/0/2/4`、Round 2 `0/0/1/4`、Round 3 进行中、尚无 host query 获准。

## Findings（本轮新增）

| ID | 级别 | 位置 | 说明与建议 |
|---|---|---|---|
| DSH-R0S5R3-P3-01 | P3（非阻断） | Task L55 | 该 bullet 以「**scratch** 仅限 r6 列出的 12 个只读输入根、13 个输出 leaf 和三个……canary leaf」起句，把多数不在 scratch 内的输入根置于 “scratch” 标签下。对象仍严格等于 r6 登记项，不构成扩权，仅分类措辞不精确。建议改为「本 Task 对象集合仅限 r6 列出的 12 个只读输入根、13 个 scratch 输出 leaf 和三个以 `G:\CODEX\P02-scratch-build-source` 为根的 canary leaf」；可在 final adjudication 中记录处置。 |

## 未能独立验证

三件 r0s5 对象/Round 2 报告/r6/R0 evidence 的 bytes-SHA-256 与 pin 值；live Git HEAD/tree/branch/worktree/`.git/index`；主仓与 scratch 两处 canary leaf 的落盘存在性/ACL 及 Registry/WER/profile/token 状态；“本轮零 host 查询/零写入”与 R0 历史取证真实性（Owner 自我报告，记 `NOT_VERIFIED`）；r6/R0 evidence 是否为被引用的冻结版本；Task L36 的 model/effort 声明；Microsoft 官方原文未抓取。

## 下一步（唯一）

由 `Codex /root` 执行 final adjudication（顺带记录 DSH-R0S5R3-P3-01），随后完成 integration verification 与 `codex-checkpoint-p02pre-r0s5-20261011.md`。期间不得派发任何 host/OS/Registry/WER/profile/token/ACL/path/environment/hash 查询，不得切换 shell 或运行 getter，不得创建/删除 profile，不得查询/安装/启用/启动 Windows Sandbox，不得触碰 Build/Cargo 与 AC1–AC7。

报告已写入 `verification/P02/dsh-p02pre-r0s5-review-r3-20261011.md`（本次唯一写入）。
