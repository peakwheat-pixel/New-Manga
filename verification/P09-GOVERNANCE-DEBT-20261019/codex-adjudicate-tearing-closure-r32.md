# P20 AC4 撕裂项收口裁定（r32）

日期：2026-10-20  
裁定者：Codex（Lead / Architect / Integrator）  
对象：P20 AC4 缩放平移撕裂子项、P20 收口状态及 AC 可验收性治理规则  
授权范围：仅新增本文件。未修改 Task、STATUS、Plan、代码或既有证据；未调用 `coordinator-lease.py`，未执行 Git 写命令。

## 裁定摘要

1. **撕裂子项按 limitation 收口，不再要求本轮人工重试或新增高速采集工具链。** 状态仍是 `UNOBSERVED`，不能写成“无可见撕裂”或 PASS。建议准确记录为：

   > **缩放平移撕裂未观察（LIMITATION）：** 本 Task 未能建立稳定的真实桌面观察会话，未执行缩放/平移观察；因此本次构建在所测环境下是否出现可见撕裂仍未知。Windows DWM 窗口合成通常降低撕裂风险，但某些呈现路径（例如支持 tearing 的 flip/VRR 路径）仍允许撕裂；不能据 DWM 存在推断撕裂不可能。本结论仅表示未验证，不表示确认无撕裂。

   选择这一路径的理由：此前 r30 已认可有边界、有记录的人工观察可作为视觉验收，但本轮三次尝试均未使应用稳定出现在前台；无帧精确设备，现阶段为这一项建立 ≥240 fps 采集和逐帧分析工具链成本显著且超出剩余验收价值。该裁定将未验证事实与技术风险一并保留。若将来在实际用户环境发现撕裂，应作为产品缺陷重新处理。

2. **DWM 合成不使撕裂在技术上绝对不可能。** 普通窗口化 DWM 路径通过合成降低撕裂机会；但现代 Windows 存在 DirectFlip/Independent Flip 等路径，DWM 可暂停参与逐帧合成，DXGI 亦定义窗口化 `ALLOW_TEARING` 与可变刷新率呈现。故“DWM 合成下撕裂极罕见”只能作一般风险判断，不能作为本构建不存在撕裂的证据。Tauri/WebView2 窗口在通常窗口化场景下风险较低，但驱动、显示器/刷新率、窗口覆盖状态及具体 GPU 呈现路径可影响结果；当前资料不能确认本次窗口实际采用何种路径，也不能给出发生概率。 limitation 应反映残余可能，而不宣称已测得风险为低。

3. **本轮失败应归为工具/会话环境阻塞，不能据现有记录判定操作者做错。** PowerShell 启动在长时间等待后转后台，随后 job 被回收且进程消失；CUA 截图显示 Edge，窗口列表/启动操作反复报告 session ended；进程枚举证实当时没有应用进程。这些记录支持“观察前置条件未建立”，不支持“观察到失败”或“缩放操作错误”。但失败只能证明**本轮 Agent 桌面操作链路不可用**，不证明所有人工观察均不可执行。若以后要补验，建议由有显示器且能直接控制桌面的人员在本机执行，并在开始前确认应用进程、前台窗口和可见画面，再按预先冻结的缩放/平移动作观察；留存观察者、时间、应用构建、显示器/刷新率、窗口模式、操作范围、结论和可用影像。避免再次采用会在等待时回收应用进程的启动/等待封装。无需把本轮归咎于执行者，也不应以反复重试同一失效 CUA session 作为完成条件。

4. **P20 仍保持 `ready`；本文件不授权把 P20 改为 `closed_with_limitations` 或 `done`。** AC4 可以把撕裂这一子项明确登记为 limitation，但 P20 Task 本身仍有其他记录的未验证项，包括 AC1 干净环境安装/卸载、AC3 单图批处理峰值、AC5 本地模型 CPU 推理；此外 P20 的 canonical evidence 与 resource closeout 仍为 `pending`。`closed_with_limitations` 需要用户明确接受 P20 全部未完成项及停止验收；“裁定撕裂按 limitation 记录”不等于用户已批准 P20 整体限项关闭。`done` 则要求所有已释放 AC 通过并完成 closeout。当前 Plan 的 `done` 计数维持 **42**。不得仅凭本裁定更新 AC 勾选、Task 状态、STATUS、Plan 或 closeout 字段。

5. **P20 的确有 closeout 字段。** Task frontmatter 当前有 `canonical_evidence_status: pending`、`resource_closeout_status: pending`；终态前还需依协作协议填写证据/资源核销以及 Closeout Record 的未关闭项和保留理由等内容。`ready` 阶段尚未进入终态，字段存在但不代表现在已经完成 closeout，也不要求为了本裁定立刻填它们。

6. **建议新增 AC 可验收性规则，价值明确，需经治理 Task 修改协议。** 建议规则针对每个 AC 的每项独立要求，不把实现中的验收器误当成测量证据：释放前应写明可执行的验收程序/步骤、环境与责任方、判定量或观察标准、需要保留的证据，以及程序不可用时如何阻塞/降级。人工观察也属于验收程序，但必须写清观察对象、动作、观察者/角色、记录内容和判定标准。没有已建立或可执行的程序时，应在 Task 释放前重写、拆分或由有权者明确批准为限制项；实施阶段发现缺口时不得把未观察推成通过。该规则预防 AC4 撕裂项这种“标准存在但验收程序未建立”的缺陷，也涵盖量化判据歧义。

   建议文本：

   > **AC 可验收性（释放前置）。** 每项 AC 及其独立子要求在 Task 释放前，必须指定可执行的验收程序（自动化命令/工具或明确的人工步骤）、适用环境与执行责任、判定量/判定标准，以及应保存的证据。量化判定须声明主统计量、采样/计算口径和其他报告量的用途；多个独立门槛须逐项列出并说明合取或优先级。人工判定须定义观察对象、操作范围、观察角色、记录项与通过/失败标准。若程序尚不存在或在释放环境不可执行，应先修订 AC/范围或在释放前取得明确的限制接受；不得在实施后以推断或空白证据判为通过。

   这条规则不应要求所有 AC 都有自动化脚本：可重复的人工步骤可以满足要求。它与 §4.4 “语义改动的核验前置”互补，前者处理释放前的可验收性，后者处理改变既有判定语义前的影响核验。当前只裁定建议，不修改 `doc/09_COLLABORATION.md`；应由后续有授权的治理 Task 按生命周期审查该条与 §4.4、Task 模板及检查器职责的边界。

## 依据与事实边界

- `doc/STATUS.md`：P20 当前为 `ready`，AC4 部分完成。
- `doc/tasks/P20.md`：用户已将交互延迟、帧率的主判据定为 avg ≤ 50 ms，并要求报告帧率 p95/max；撕裂采用人工观察。三项量化结果已满足各自裁决；AC4 原行仍未勾选。P20 另有未验证项，且 closeout 字段待处理。
- `verification/P20/ac4-measurability-correction.md` 与 `verification/P20-AC4-FPS-1/ac3-real-desktop/`：FPS 有真实桌面记录，单页 1266 样本（avg 16.681 ms、p95 16.8、max 17、excluded 0），Webtoon 1202 样本（avg 17.527 ms、p95 33.3、max 33.5、excluded 0）。`ac4-measurability-analysis.md` 中“记录器未挂载/未测”的旧结论已由 correction 明确撤回，不作为本裁定事实来源。
- `verification/P20/ac4-tearing-attempt.md`：三次尝试失败；本轮没有应用窗口、没有滚动或缩放、没有观察撕裂。其“DWM 下极罕见”措辞不是实测结论，本裁定不采作风险事实。
- `verification/P09-GOVERNANCE-DEBT-20261019/codex-adjudicate-ac4-closure-r30.md`：人工观察可作为有范围、有记录的验收方式；未观察仍为 NOT_MEASURED。该文件的 FPS 事实判断已被 r31 与 correction 更正，故只引用其人工观察路径，不沿用其过时的 FPS 状态判断。
- `verification/P09-GOVERNANCE-DEBT-20261019/codex-adjudicate-fps-measure-r31.md`：不另立 FPS 入口 Task；FPS 证据已存在，撕裂仍需独立观察结论。
- Microsoft Learn：窗口化 DWM 路径通过合成降低撕裂机会，但不构成“任何现代呈现路径都不可能撕裂”的保证；DXGI 文档明确说明 flip/Independent Flip 呈现及窗口化 tearing/VRR 支持。[DXGI Presentation Path](https://learn.microsoft.com/en-us/windows-hardware/drivers/display/dxgi-presentation-path)、[DXGI flip model](https://learn.microsoft.com/en-us/windows/win32/direct3ddxgi/dxgi-flip-model)、[Variable refresh rate displays](https://learn.microsoft.com/en-us/windows/win32/direct3ddxgi/variable-refresh-rate-displays)。这些资料支持“不能断言技术上不可能”，但不证明本机 build 26300 的特定窗口此刻启用了允许撕裂的路径。

## 当前结论

撕裂：**LIMITATION / UNOBSERVED**。P20：**保持 `ready`，done 计数仍为 42**。本文件只形成裁定依据，不替代 Task 生命周期变更、用户对整体限项关闭的明确接受或 P20 的正式 closeout。
