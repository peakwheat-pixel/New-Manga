全部证据链核验完毕（三轮只读子代理采集 + 直接文件审读交叉）。以下为独立裁决报告。

---

# FEA-15-PIN-BASIS-ENFORCE-1 · AC1d 独立基线确认裁决（只读、fresh session）

## 结论：`AC1D_PASS`

## 一、裁决身份

| 字段 | 值 |
|---|---|
| 裁决者 | ZCode 全新 CLI 会话（fresh session，仅本次只读 AC1d 基线确认） |
| Session / Turn ID | session sess_fd863071-c665-4b61-89be-2156ace80595 / turn turn_133dc2f6-c7f1-467c-a8a5-2c342f12c65a；同会话回执 turn turn_217dd2e1-13dd-4f53-83d2-f599bc9a81dd 仅复述原结论（回执调用 EXIT=0）。本会话内派生的只读采集子代理：`agent_3054fbd8-f92d-4a23-b536-d9b0e879138e`、`agent_e40b46f9-75a7-4776-ae75-f1704fc88cbb`、`agent_1fe57b8d-ca99-4b3f-8436-9940b5c0ba17`（仅执行只读 git/sha256 命令，未写任何文件） |
| 独立性 | 本会话非 AC1c A 裁决会话（`sess_72137bd6-9553-424d-b09f-4184866cd387` / `turn_fbce0bef…`），非主裁决/Addendum 会话（`sess_7b34d23e…`），非 STOP 裁决会话（`sess_e951752d…`），未参与本 Task 任何实现（本 Task 尚无实现）；本会话不承担最终 Review 或最终 adjudication |
| Reviewed HEAD（main） | `0851085cbeeaaea95d1fd94b55a435a3e2eef102`（本会话经只读子代理 `git rev-parse HEAD` 实测确认；`git status --porcelain` 为空） |
| 冻结 R0 | `bfae0b9bd6a9b85a9a546d2adda0b684783ddb24` |
| 历史比较基线 | `2df8db7a4d19b591e919ecc6e8f8651167800ef0`（A clone） |
| 本会话限制 | plan mode 禁止主会话直接 Bash；Git 级核验全部经只读子代理完成（与 AC1c A 裁决会话同限制口径，但本次完成了 rev-parse/cat-file/diff 级实测，非仅文件级） |

## 二、输入证据（全部实际读取并独立复核）

Task 卡、STATUS（L7 当前 Task 指针）、REBASELINE_PLAN（L55 节点 in_progress、L58 ACTIVE）、主裁决 + Addendum 2/3/4、AC1 delta STOP 裁决、AC1c A 裁决（ACCEPT_CONTINUE）、verification README、history-transition-ledger、三份 AC1a 日志、两份 delta JSON、A 侧 gates 日志、R0 main gates 日志、B 侧断言日志、check.ps1（:622-631/:669-724）、verify_pins.ps1（:15-28）、.gitattributes（全文）。

**本会话独立 Git 级复算（关键结果，全部与在册值一致）：**
- R0..2df8db7 反向 diff = **25 路径**，与 B 日志逐项相同（3 M + 22 A），全部落在 frontmatter `allowed_paths` 内；
- `tools/governance/**` + `doc/templates/**` 在 2df8db7..bfae0b9 diff 为**空**；check.ps1/verify_pins.ps1 blob 在 2df8db7、bfae0b9、0851085 三个提交均为 `b56a832f…`/`25d63260e8f922d1f796451e6ade2df2911ff521`；
- R0→reviewed HEAD 增量仅 4 文件（M Task 卡、M README、A 两份 R0/B 日志），均在允许集；`bfae0b9..HEAD` 仅 `817415797`、`0851085cb` 两个证据/pin 提交；
- 冻结禁区未触碰：`.gitattributes`（`23d5cacf…` 两提交不变）、`verify_pins.ps1`、`doc/plan/**` 在 2df8db7..0851085 无差异；
- E1 算术闭合：2df8db7 Plan blob 实测 **6992 bytes / 64 行** → autocrlf=true 工作树 6992+64=**7056**，与 A 侧 FAIL 数字逐字节吻合；
- 矩阵双基准实测：blob `68ec4b50c3bbfc450218bc35fdc7da8f43454cf23eaedae8cbd4c872d879ec41`/4316 bytes/122 行；工作树 `e8c48163d5c552b337a478326d7e7e8d7c637c2304741c66b579f48ce6a70246`/4438 bytes（4316+122=4438 闭合）；Task 卡 pin 指向 blob；
- Task 卡 Canonical Evidence 15 行 pin 中 **14 行按行内 commit 逐一复算 SHA-256 全部一致**（含三份 AC1a JSON/log：`2aca6413…`/`f88f9905…`/`c27247db…`/`43e64561…`/`f4035837…`/`b2f060dd…`；两份裁决 `6e2c11c4…`/`46c7e493…`；Addendum 4 `ebbd38fb…`；ledger `56cefbc9…`；A gates `7db89740…`；R0/B 两日志 `0f4b9dc4…`/`488924df…`；README `cf233443…`）；wrapper `e4300b7b…` 经四份运行日志内嵌自证间接闭合；
- delta JSON changed 两行逐字段与 ledger/Addendum 4 一致（identity 与 `pin_sha256` 不变，`class` 空→`CANONICAL`、`ac_gate` 措辞变更）；added 31+18+13=62；
- 机制引用属实：verify_pins.ps1:23 为工作树 `Get-FileHash` 口径；check.ps1:700-724 r194 双基准注释原文在册；.gitattributes 确认 `doc/plan/**`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md` 无 eol 规则（E1 未覆盖面论断成立）。

## 三、逐项实际 EXIT / NOT_RUN（严格口径）

**A 侧（AC1c A，@2df8db7，`core.autocrlf=true`，log `ac1c-a-gates-8d1d75ca.log`）**

| 项 | 实际结果 | 对照 AC1c A §六修订锚 |
|---|---|---|
| default | **EXIT=1**（仅 Plan 7056/64） | 相符；真实 FAIL，保持 FAIL |
| AGPL-RELEASE-1 / AD002-FOLLOWUPS-1 TaskPath | **EXIT=1**（仅 Plan budget；卡级检查实际通过） | 相符 |
| FEA-06-PREREQ-1 TaskPath | **EXIT=1**（15 errors） | 相符（E3+S1） |
| CHAPTER-SELECTOR-1 TaskPath | **EXIT=1**（7 errors） | 相符（E1+S2） |
| verify_pins | **EXIT=1**（16/18 MISMATCH；C04b/C17 OK，逐项名单一致） | 相符；16 个 actual 永不登记为新 pin |
| API inventory | **EXIT=0**，1/79/6=86 | 相符 |
| 固定边界矩阵 | **EXIT=0**，输出 SHA `e8c48163…` | 相符 |

**AC1a（@2df8db7）**：reproduction `EXIT=0`（输出与历史 `27ab6ac6…` 逐字节一致）；inventory `EXIT=0`（5,438 行 = 5,420 + 18，`records`/`total_pin_rows` 结构验证）；delta `EXIT=0`（`ADDED=62 / REMOVED=0 / CHANGED=2`，已由 Addendum 4 冻结为一次性衔接，永不归零）。

**B 侧（@R0=bfae0b9，clone-local `core.autocrlf=false`/`core.longpaths=true` 于首次 checkout 前设置并有时间戳证据，log `ac1c-b-r0-assertions-taskpath-bfae0b9.log`）**：HEAD/clean/clone-config PASS；Task/STATUS/Plan 在场 PASS；25 差异路径全在允许集 PASS；24/24 治理与模板 blob 同一 PASS；**本卡 TaskPath `EXIT=0`（3 warnings）**；clean after PASS；OVERALL `EXIT=0`。B 的 default/pins/API/inventory/delta/repro/历史 TaskPath/矩阵**未运行**，NOT_RUN 保持。

**R0 main gates（main 工作树，log `r0-main-gates-bfae0b9.log`）**：default、本卡 TaskPath、18 pins（18/18 PASS）、API 全部 **EXIT=0**（各 3 warnings；API 1/79/6=86）。

**其余 NOT_RUN（不得写成 PASS）**：AC2、AC3、AC4（含 autocrlf=false 对照与 Linux）、AC5（集成门禁、fresh 独立 Review、终裁）、R-001 终裁。

## 四、结论理由

1. **Addendum 4 §6 前置全部满足**：AC1c A 侧五类全部实际执行且 EXIT 与 ACCEPT_CONTINUE 修订锚逐项相符；B 侧断言集全部 PASS 且仅运行本卡 TaskPath；AC1d 指定输入（repro anchor、正式 inventory/delta、ledger、A 侧 gates、B 侧 R0 断言与 TaskPath）在册且经本会话独立 Git 级复核。
2. **§8 停止条件逐项未命中**：无 post 对比违规（无实现）、无表头不可区分（无实现）、无旧行判定翻转（四 TaskPath 为首测在册）、EOL 异常已由 ACCEPT_CONTINUE 归因为确定性环境机制且 `.gitattributes` 未动、25/25 差异在允许集、24/24 blob 同一、B 载体三项在场、全部冻结禁区 blob 级不变、无清理/gc/push、全链 clean。
3. **R0 有效性**：bfae0b9 符合 Addendum 4 §5 与 AC1c A §七.1 的 R0 定义（裁决落盘 + Task 卡恢复 in_progress + STATUS/Plan 指针一并入 main 后的 HEAD）；其后至 reviewed HEAD 仅两个证据/pin 提交，增量全在允许集。
4. **数字自洽无未归因残余**：5350→5376→5438、+26/-0/0 与 +62/-0/2、added 归因 31/18/13、changed 两行归因 `d26c43c…`、basis_count_delta 与 Addendum 4 §2.4 环境敏感摆动解释一致（basis 不入断言）。
5. **卫生项闭合**：matrix pin 双基准已按 AC1c A §八.1 处置（pin 指向 blob + 卡内 basis 注注）；Addendum 4 pin 已小写规范化（复算一致）。

## 五、实施授权边界（AC1D_PASS 后放行的内容）

- **仅解除 AC2/AC3 的 BLOCKED**：允许按 Task 卡开始模板七列、check.ps1 新旧表判别与 basis 校验、tests 实现；实现分支/worktree 从冻结基线（R0 基点）创建，main 不直接实现。
- **持续禁令**：18 frozen pins、`verify_pins.ps1`、`.gitattributes`（含为本 Task evidence 目录补 eol 规则——见观察 2）、历史 Task/Review/evidence/pin 字节、renormalize 及 dry-run、pin 迁移、资源清理/gc/prune/repack/push；B clone 其它门禁保持 NOT_RUN，不得补跑充当基线；A 侧 FAIL 锚为该环境规范输出，同配置复跑须逐字节复现，不同即新停止事件。
- **post-implementation 对照口径**：以 5,438 行 inventory 为唯一历史不变性基线、R0 为基点；历史行硬不变性 = identity 逐行在场、`pin_sha256` 不变、`deleted=0`、`changed=0`；出现任何 `changed>0`/`deleted>0`/未归因新增即停、交 ZCode 再裁决；`basis`/`basis_counts` 不参与断言。
- **会话纪律**：最终 Review 与最终 adjudication 须为彼此独立的新 ZCode session，本会话与 `sess_72137bd6…` 均不得担任；R-001 待最终 Integrator 显式裁决。

## 六、未解停止项

**无。** 两项非阻塞观察（如实登记，不影响本结论）：
1. Task 卡 pin 表中 inventory/delta/repro 三行 pin 为入库 blob SHA，README artifacts 表列 A clone 工作树输出 SHA，两口径均已复算一致，但卡内仅对 matrix 行做 basis 注释，建议 Owner 后续对三行补注（与 AC1c A §八.1 处置同构）。
2. `verification/FEA-15-PIN-BASIS-ENFORCE-1/**` 未获 `.gitattributes` eol 规则，autocrlf=true 环境下该目录证据文件将持续存在工作树/blob 双读数（matrix 已实例化）；补规则属冻结禁区，仅登记为未来授权候选，AC2/AC4 实现时按 Task 卡处理。

---

**推荐下一步**：派发者保存本报告原文、回填 Task（AC1 更新为引用本 AC1d 裁决，session/turn ID 补记），随后 Owner=Codex 按 Task 卡从 R0 冻结基线创建实现 worktree，开始 AC2/AC3 实现（上方授权边界内）；AC4/AC5 门禁实际执行后再进入 fresh 独立 Review 与终裁链。
## 派发回执（Codex 记录）

- 原始 AC1d JSON stdout 保存在 G:\CODEX\New Manga.workspace\FEA-15-PIN-BASIS-ENFORCE-1\zcode-ac1d-baseline-confirmation-2026-11-12.json.txt，其中包含本报告原文、session sess_fd863071-c665-4b61-89be-2156ace80595、裁决 turn turn_133dc2f6-c7f1-467c-a8a5-2c342f12c65a；对应 stderr 文件为 0 bytes。原始长运行命令的子进程 EXIT 未被外层 exec 返回并保存，因此此处不把它伪记为 EXIT=0。
- 同一 ZCode session 的回执 turn turn_217dd2e1-13dd-4f53-83d2-f599bc9a81dd 仅复述上一 turn 的 AC1D_PASS，没有重新审查或改变裁决；回执调用 EXIT=0、stderr 0 bytes。其原始 JSON 与命令记录保存在 G:\CODEX\New Manga.workspace\FEA-15-PIN-BASIS-ENFORCE-1\zcode-ac1d-receipt-2026-11-12.json.txt、zcode-ac1d-receipt-2026-11-12.log。