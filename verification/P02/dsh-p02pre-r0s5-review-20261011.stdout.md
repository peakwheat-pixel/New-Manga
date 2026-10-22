# P02PRE-R0S5 独立静态 Review 报告（DeepSeek Harness / 非作者）

报告已写入 `verification/P02/dsh-p02pre-r0s5-review-20261011.md`（本次唯一写入；未执行任何命令）。

## 结论

**`changes_requested`**（无 P0/P1；P2=2，P3=4，均可随 Codex adjudication 收敛，不强制第三轮 Review）

## 五项检查点裁定

| # | 检查点 | 裁定 |
|---|---|---|
| 1 | 2026-10-11 授权表述、不得变成新 waiver/Gate PASS/Barrier 放行 | **通过**。Task L22/L24、manifest L5–L13、delivery L23 三处一致；五值风险原值、固定英文原文 `technical condition unmet; user explicitly accepted residual risk`、`P02PRE=BLOCKED`、`Build Gate=BLOCKED`、`Hard Build Barrier=EFFECTIVE`、`build/Cargo=NOT_RUN`、`AC1–AC7=BLOCKED / NOT_RUN` 逐字保持，与 r6 L14/L16/L20 对齐 |
| 2 | 候选限于 r6 精确对象/方法、不猜 profile 路径、边界受限 | **基本通过**（2 项 P2 精度缺口）。身份禁 `whoami`/P/Invoke/子进程；profile 明文“无精确安全路径即 `UNPROVABLE`、禁猜 SID 派生路径”；WER 限两键三目录、禁枚举与读 dump；scratch 限 12 输入根/13 leaf/3 canary；证据输出限 `*r0s5*` 与四个治理摘要 |
| 3 | 当前 `exec_command`/PowerShell 链视为未证明 | **通过且方向正确**。manifest L35–L39 要求 executable/version + 完整 argv + startup/profile/cache/history + wrapper/temp/log + 全部可能子进程证据，明写 `shell=PowerShell`/`login=false` 单独不足、`-NoProfile` 子进程不证明父启动器；未获新证据 + 非作者 Review + adjudication 前 **“no query permitted”**，仅静态分类继续 |
| 4 | 五类状态语义 | **通过**。`FAILED` 需实际执行的失败检查；未执行/安全停机不记失败；历史 `PASS_WITH_EVIDENCE` 仅限 R0 已捕获对象/时点，未外推；方法为 `NOT_SAFE_FOR_R0` 不等于条件失败 |
| 5 | AC/manifest/delivery/Reviewer 独立性/Gate 处理一致、无隐藏查询授权 | **存在一致性缺陷**（见下），但**未发现隐藏查询授权**：Task L42/L73 的执行许可均以 runner + getter 双证据为前提，manifest 把当前状态整体冻结为零查询，`glob` 中无任何 r0s5 证据文件 |

## Findings

- **DSH-R0S5-P2-01**（manifest L31 / Task L50 / delivery L13）：R0 历史 hash 记为 13 项 `PASS_WITH_EVIDENCE`，但未给 R0 evidence 段落引用；把 `.git/index` 一并称 “protected file” 与该表“12 文档 + `.git/index`”构成不符；且 R0 当年采集链（r6 L229 记为 PowerShell `Get-FileHash`）正是本 manifest 判定无副作用未证明的同类 runner。需补引用、构成说明与“历史结论不构成当前 runner 证明”。
- **DSH-R0S5-P2-02**（manifest L27/L29 / Task L50/L51）：身份核对未写与 r6 L49–L51 冻结值的比对基准与记录字段；“Path ACL”只写 “exact r6 path list only” 而全文未给路径枚举/计数（对比 scratch 有 12/13/3 精确计数）。需补基准与精确路径集合。
- **DSH-R0S5-P3-01**：Task `status: in_progress` 与 STATUS/PLAN 记的 “Round 1 Review READY” 不一致（协议 §4 待审应为 `in_review`）。
- **DSH-R0S5-P3-02**：manifest L5 授权句未带续次标识与“新增授权”字样，可能被误读为沿用 R0S4 授权。
- **DSH-R0S5-P3-03**：STATUS L7/L9、PLAN L5/L9 写“已证明安全只读取证”，字面预设“已证明安全”成立，而 manifest L27–L33 每项初始处置均为 `NOT_SAFE_FOR_R0`/`UNPROVABLE`。
- **DSH-R0S5-P3-04**：Task L40–L46 AC 复选框全未勾选，其中 L45/L46 在交付文本中已实质满足，缺状态映射。

## 残留限制（本 Review 不主张）

未核验任何本地 bytes/SHA-256、Git status/HEAD/tree、`.git/index` 副作用、用户未提交完整性、OS/Registry/WER/profile/ACL/path 状态，以及“零 host 查询、未启动子进程、未换 shell”这一 Owner 自我报告的真实性（一律 `NOT_VERIFIED` / `NOT_RUN`）；未验证任何方法是否真的无副作用、也未验证 r0s5 是否执行过查询；Microsoft 官方原文 `NOT_FETCHED`。本 Review 不授权执行、不放行任何 Gate、不改变 waiver，也不代替 Codex adjudication。

## 推荐下一步

由 `Codex /root` 执行 P02PRE-R0S5 独立 adjudication，并顺带处置 DSH-R0S5-P2-01/02 与 P3-01…P3-04（补 R0 evidence 引用与 13 项构成、给身份基准与 ACL 路径枚举、统一 Task 为 `in_review`、明示新增授权、修正“已证明安全”措辞、逐项标注 AC）。期间不得派发任何 host query、不得换 shell 或运行 getter、不得创建 profile、不得触碰 Windows Sandbox 与 Build/Cargo/AC1–AC7。
