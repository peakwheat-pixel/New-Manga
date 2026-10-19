# P20-CLOSE-BOUND-HARDEN-2 AC5 裁定（r29）

日期：2026-10-20  
裁定者：Codex（Lead / Architect / Integrator）  
对象：`P20-CLOSE-BOUND-HARDEN-2` AC5、P20 的 R4-01 承接及后续状态  
写入范围：仅本文件。未修改 Task、Plan、STATUS、脚本或 AC5 原始证据；未调用 `coordinator-lease.py`，未执行 Git 写命令。

## 裁定摘要

1. **AC5 判定 `MET`。** 指定执行者是 Coordinator；本次记录的 Coordinator 会话满足 `UserInteractive=True`，运行脚本时确实创建了桌面主窗口，并由脚本通过窗口句柄发出正常关闭请求。进程在 54.4812 ms 内退出，退出码 0，残留进程 0；脚本退出码为 0。四份证据相互一致。
2. AC5 原文要求“由 Coordinator 在交互式桌面执行”，没有要求人坐在屏幕前目视确认。故“人是否实际看见窗口”不构成此 AC 的额外门槛。现有日志证明窗口句柄出现，不证明有人目视观察；不把未记录的人类观察写成事实。
3. 在 AC1–4、AC6–7 已由 Task 记录为达成的前提下，**HARDEN-2 的技术验收已满足，建议 Task 转为 `done`**。这不等于本文件已完成权威状态变更。Task 的正式终态仍须由 Codex 按协作协议完成集成记录、资源 closeout、Task/Plan/STATUS 同步，并运行 Task-scoped 治理检查。
4. **R4-01 的承接工作由 HARDEN-2 完成**：AC1–3 处理 holder 保留、饱和与 spawn 失败路径，AC4 修订审计边界，AC6 回归通过，AC5 补上真实桌面关闭实测。Plan 中 P20 主线本身仍为 `ready`，不会因子 Task 完成而自动变更。
5. Rust 环境基线 Task 仍是 `proposed / pending_user_release`，建议先保持 proposed；它不是 HARDEN-2 的依赖或关闭门槛。

## 1. AC5 证据核验与语义

### 1.1 可直接核实的执行事实

依据 `verification/P20-CLOSE-BOUND-1/ac5-run-20261020/`：

- `ac5-metadata.json` 和 `ac5-metadata.txt` 记录运行时段为 2026-10-20 04:26:39.683 至 04:26:44.338（+08:00），总运行 4.65 秒；PowerShell 7.6.6；执行时 HEAD 为 `acf9069f5deab7e7a68993fd25583070d9c573fc`。
- `ac5-console.log` 记录进程 PID `29812` 启动，主窗口 handle `73601958` 被检测到；其后记录主进程及子进程、`CloseMainWindow returned: True`、主进程在 54.4812 ms 内退出、应用退出码 0、残留进程数 0，以及 `SUCCESS: ... Clean exit verified.`。
- `ac5.exit` 内容为 `0`；metadata 的 `exit_code` 与 `desktop_exit_code` 均为 0。metadata 记录四个主证据文件均写入成功，没有使用 fallback。
- 运行二进制 SHA-256：`5f9170e2c48831922801fdd085613e44e019198b2cacf8264f0bde0dad7afcb6`。

### 1.2 “交互式桌面”是否要求人目视

AC5 原文的主体是 Coordinator，动作是“在交互式桌面执行”。脚本头注明确把适用环境描述为交互式 Windows 桌面，并说明非交互会话可能没有 GUI 能力。此次不是仅凭 `UserInteractive=True` 推断成功：运行记录同时显示真实桌面窗口 handle 出现，脚本通过 `CloseMainWindow` 关闭该窗口，并核验应用进程树退出。因此，**对原文约定的可执行含义，本次满足“交互式桌面执行”**。

任务记录另有“由人在交互桌面产生 PASS”的解释性文字，但 AC 原文没有规定观察者必须是自然人、必须目视检查界面，或必须提供截图/录像。执行者被明确指定为 Coordinator，而本次 Coordinator dsh 已执行动作；判定由 Codex 依据证据作出，未由交付方自行给自己记 PASS。不能把未写入 AC 的“人坐在屏幕前”追溯添加为门槛。

**证据边界：** 证据足以证明窗口句柄出现及程序干净退出，不证明有人观看屏幕，也不证明窗口内容/视觉状态正确。若未来某 AC 真正需要人工可见性判断，应明确要求观察者、观察动作和证据类型；这不是本 AC 当前文本的条件。

### 1.3 对 AC5 的最终标签

`MET`。判定依据是本次 Coordinator 在真实交互桌面上下文中运行指定脚本，并得到窗口出现、正常关闭、限时退出、退出码 0、零残留的联合证据；单独的 `UserInteractive=True` 或脚本 exit 0 都不足以替代这些证据。

## 2. Task 终态、集成记录与计数

### 2.1 是否可转 `done`

按本 Task 当前记录，AC1–4、AC6–7 已勾选，AC5 现由本裁定判为 `MET`。没有剩余技术 AC 缺口，因此推荐 `P20-CLOSE-BOUND-HARDEN-2 → done`，而不是 `closed_with_limitations`。现有执行已经发生，不存在“执行了但缺人类观察者确认”的限制；把这种未列在 AC 的要求写成 limitation 会扩大原验收范围。

但协作协议规定，只有 Codex 完成集成、集成后验证、Canonical Evidence 与 Resource Manifest closeout、权威指针同步，并通过 Task-scoped checker 后，才能设置 `done`。本次授权只允许新增本裁定文件，故本轮**只完成 AC5 语义裁定，不声称 Task YAML/Plan/STATUS 已进入终态**。在权威文件仍未更新前，机器可见状态仍是 `in_review`。

### 2.2 `integration_commit`

本次 AC5 执行没有产生产品代码变更，也不需要为它另造一个合并提交；不能编造新的集成提交。正式 closeout 时仍须按协作协议填写实际承载并集成了 Task 交付物及证据的 HEAD/commit，只有在确认这些对象已位于目标集成基线上后才能填写。Task 当前 `branch: null`、`integration_commit: null` 不足以单独证明集成已完成。

本轮只读检查到的 checkout 分支名为 `antigravity/P09-AC3-DELETE-HARDEN-1`，不是从分支名即可认定的主线状态；工作区另有大量既存 dirty/untracked 内容，均属本裁定范围外且未改动。因此本文件不把当前 checkout 自行宣称为已完成 HARDEN-2 集成的主线，也不以分支名替代集成核验。

### 2.3 Plan 行与 done 计数

当前 `doc/REBASELINE_PLAN.md` 已登记 HARDEN-2 一行，状态为 `in_review（AC1-4/6/7 MET；AC5 已执行待判定）`，底部计数为 `done：41 项`。裁定成立后，状态应更新为 `done` 并把 AC5 标为 `MET`；在该 Task 被计入且无其他 DAG 状态同时变化的情况下，计数从 **41 增至 42**。这是预期同步结果，不是本文件已经执行的 Plan 修改。

## 3. P20 主线和 R4-01

HARDEN-2 的标题和来源明确是承接 `P20-CLOSE-BOUND-HARDEN-1` 的 R4-01。其 AC1–3、AC4、AC6 与本次 AC5 证据覆盖了所拆出的剩余工作。HARDEN-2 完成后，R4-01 的这条承接链可记为已处理；HARDEN-1 仍按原裁定 `closed_with_limitations` 保留历史状态，不回写成技术 PASS。

P20 Task 与 DAG 的主线状态仍为 `ready`。HARDEN-2 完成不会自动让 P20 转 `done`，也不会解决 P20 自身未闭合的发布验收项。当前可见的剩余内容包括：

- **AC4 交互响应与帧率：部分达成。** 最近 P20 记录为平均延迟 36.0 ms，但 p95/max 62.4 ms 超过 50 ms；FPS 与缩放平移无可见撕裂仍为 `NOT_MEASURED`，且延迟采用 avg 还是 p95 的门槛解释仍待用户裁决。P20 保持 AC4 未勾选。
- **AC1 的干净环境安装/卸载：未执行。** 安装包构建通过不等同于干净 Windows 环境安装及完整卸载验收；应在 P20 收口证据中保留该缺口。
- **AC3 单图批处理峰值：未测。** 当前基础空闲 Working Set 在调整后阈值内，但 AC 原文另有单图批处理峰值不超过 1.5 GB 的要求，现有记录不能自动覆盖它。
- **AC5 本地模型 CPU 推理：未实跑。** 无 GPU 环境下启动与基础功能已通过；由于没有模型文件，CPU 推理路径仍未证。

P20 是否可在保留上述限制下最终收口、哪些子项需补测或由用户裁决，仍须按 P20 Task 原 AC 与现有治理状态单独处理。HARDEN-2 终态不替代这项决策。

## 4. 流程问题：为什么此前没人运行，以及环境前提应如何写

AC5 从 HARDEN-2 交付记录形成到 2026-10-20 本次执行前一直未执行；本次可核事实是 Task 先前明记 `未执行`，随后在 2026-10-20 首次留下运行记录。不能从当前证据精确断言“卡了多少天/小时”或所有此前轮次的次数；Task 声称的“93 轮”不是本裁定独立核实的事件日志事实。

可见的流程诱因是脚本头注把“非交互 agent session 缺少 GUI”写成无条件的泛化提醒，没有要求执行者先检查当前会话条件，也没有给出 `UserInteractive`、窗口 station/desktop 可用性或窗口句柄探测等可操作的前置判据。读者容易把“agent”类别误当成“必定非交互”，再把本来指定给 Coordinator 的实测跳过。Task 同时强调执行方不得自判 PASS，也可能被误读为执行本身也不可由 Coordinator agent 完成；实际上两者是执行与独立判定的职责分离。

因此，**是，环境前提应表达为可检测条件，而非对 Agent 身份作断言。** 合理写法应类似：“先探测当前会话是否具备可用交互桌面；若探测失败，记录具体条件与错误并标为未执行/阻塞；若探测成功，继续实际运行并以窗口及进程行为证据判定。执行者只记录事实，独立 Reviewer/Coordinator 按 AC 作最终判定。”这是一项流程改进建议；本次授权不允许修改脚本或治理文档，故不在此实施。

此结论遵循 r27 §5 的“事实核验先于语义生效”：先用当前运行记录确认 GUI 条件与实际窗口行为，再解释 AC；不把脚本注释或 `UserInteractive=True` 单独提升为结果。未来改变验收含义（例如增加必须人工目视）应先明确其对既有结果的影响和证据要求，再更新 AC，不能追溯性默示增加条件。

## 5. RUST-ENV-BASELINE-1 是否释放

`RUST-ENV-BASELINE-1` 当前 frontmatter 是 `status: proposed`、`approval: pending_user_release`，Plan 也将其列为 proposed。它针对 12 项 Rust 测试环境依赖失败，当前材料将其定性为待单独处理的环境基线工作；没有证据表明它是 HARDEN-2 完成的必要依赖。**建议暂不释放，保持 proposed，等待其自身授权与释放条件齐备。** 不应借 HARDEN-2 完成自动启动该 Task，也不应把那 12 项失败计作本次 AC5 的限制。

## 6. 证据索引与下一步

主要依据：

- `doc/tasks/P20-CLOSE-BOUND-HARDEN-2.md`：AC 原文、AC1–4/6/7 状态、AC5 执行说明与 canonical evidence 登记。
- `verification/P20-CLOSE-BOUND-1/ac5-run-20261020/ac5-console.log`
- `verification/P20-CLOSE-BOUND-1/ac5-run-20261020/ac5-metadata.json`
- `verification/P20-CLOSE-BOUND-1/ac5-run-20261020/ac5-metadata.txt`
- `verification/P20-CLOSE-BOUND-1/ac5-run-20261020/ac5.exit`
- `verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1`
- `doc/tasks/P20.md`、`doc/tasks/P20-CLOSE-BOUND-1.md`、`doc/tasks/P20-CLOSE-BOUND-HARDEN-1.md`
- `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/tasks/RUST-ENV-BASELINE-1.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/codex-adjudicate-pin-basis-r27.md` §5；核验先于改变现存判定语义。

**推荐下一步：** 在确认 HARDEN-2 实际交付与 AC5 四份证据已位于目标集成基线后，由 Codex 按协作协议完成 Task/Plan/STATUS 终态同步及只读治理检查；预期 Task=`done`、Plan done 计数 `42`。随后继续处理 P20 自身 AC4 的用户门槛裁决及其余未测发布项。`RUST-ENV-BASELINE-1` 暂不释放，除非用户另行授权。
