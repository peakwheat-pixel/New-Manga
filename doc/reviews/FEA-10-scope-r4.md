<!-- FEA-10 scope review r4 (Codex independent) -->
# FEA-10 / FEA-10-PREREQ-1 建卡 scope review r4（Codex 独立）

- Reviewer：Codex 全新上下文；未参与建卡/实现；只读。
- reviewed_head：`9bc2093d1fdc4fc093d3c72007e5e414c9a2f1f5`。
- 结论：changes_requested，P0=0/P1=1/P2=2。
- DSH 处置：`doc/reviews/ADJ-2026-11-04-NEXT-TASK.md` §Scope Review r4。

---

verdict：**changes_requested**；**P0=0 / P1=1 / P2=2**。两卡尚不宜进入 scope freeze/实施 Appointment。

reviewed_head：`9bc2093d1fdc4fc093d3c72007e5e414c9a2f1f5`  
身份/来源：Codex 全新上下文 `/root`，用户指定独立 scope reviewer r4；`reviewer_kind=agent`。未参与建卡、实现或修订；全程只读，无修改、commit、push。

- **FEA-10-PREREQ-1：changes_requested**
- **FEA-10：changes_requested**

| r3 剩余项 | r4 闭环判定 |
|---|---|
| P1-1 文件级写域 | **部分闭环**：测试授权已逐文件，PREREQ 已有用途/AC 矩阵；仍有清单与矩阵冲突、漏列文件。 |
| P2-1 可复跑验证 | **部分闭环**：项目、solution、IPC 门径及重启脚本已命名；构建前提、过滤器及部分隔离/证据出口仍不完整。 |
| P2-2 AC5 计数 | **闭环**：后置限定明确只约束成功提交回执/完成计数，允许失败/控制状态持久化，与验证矩阵一致；建议顺手替换前段旧措辞。 |

剩余 findings 与最小修复：

- **P1-1｜两卡写域尚未自洽。** [PREREQ:65](</G:/CODEX/New Manga/doc/tasks/FEA-10-PREREQ-1.md:65>) 新增 `Fea10PrereqProjectionTests.cs`，验证命令也要求它，但 `allowed_paths` 未授权。FEA-10:59/125 仍列不存在的 `Host.Tests/RunMonitorTests.cs`，:127 又声明“不写”；:118 仍用 `Commands/*`，:123 仍用测试整目录概括用途/AC。**修复**：补新测试授权、删除误列 Host 文件、将矩阵同步为已列的具体文件与用途/AC。
- **P2-1｜验证命令仍不能完整直接复跑。** [PREREQ:87](</G:/CODEX/New Manga/doc/tasks/FEA-10-PREREQ-1.md:87>) 全部 `--no-build`，未列构建步骤；`FullyQualifiedName~WireTests` 实际只匹配 `AsciiWireTests`，遗漏同文件的 `CoreProtocolTests`。`verify_pins.ps1` 仍无完整调用；PREREQ 未给具体日志出口，FEA-10 AC1–6 仍泛称临时 DB，AC7 未明确脚本调用关系及同库参数传递。**修复**：补构建、真实类名过滤、完整脚本命令和隔离/日志规则。
- **P2-2｜部分文件用途映射不准确。** [FEA-10:122](</G:/CODEX/New Manga/doc/tasks/FEA-10.md:122>) 花括号展开将 `openai_client.py` 指向不存在的 `src/openai_client.py`。PREREQ:58–59 将 `SidecarErrorCode/SidecarException` 映射为 Run 原码投影，但二者实际承载传输故障；业务 `code/category/retryable` 由 `Wire/CoreProtocol.cs` 的 `CoreErrorInfo/CoreOperationException` 承载。**修复**：写全真实路径，明确复用业务错误类型及白名单实际投影落点，移除无依据的传输枚举扩写用途。

request builder：**语义边界已闭环**；现有 `payload_hash` 仅摘要协议 payload，后续仍构建目标语言、prompt、model、options 和 HTTP body。两卡已明确默认只读复用、窄改须 DSH 批准；路径误列见上。

依赖/越界：PREREQ 硬前置成立，FEA-10 不得先 ready；未混入 FEA-11/12/13/14。ADJ 拆分、wire 2.12 与 Core minor 边界一致；proposed 不构成实施授权；符合 2026-10-31 上下文独立规则。历史 r3 与当前 r4 标记可区分。

diff：`bb569c19d..9bc2093d1` 仅两卡、ADJ、r3 报告归档，共 4 文件；无生产代码或冻结契约变更。  
实际检查：`main`、工作区干净；common directory=`G:/CODEX/New Manga/.git`；`check.ps1` **EXIT=0 / PASS（3 warnings）**；pins **EXIT=0 / 17/17 PASS**。  
**NOT_RUN**：pytest、.NET build/test、真实 IPC/UI、故障注入、Core 重启行为测试；不判实现 AC 为 MET。

推荐下一步（Agent：**DSH**，可直接转发）：“在 `G:/CODEX/New Manga`、main、上述 head 基础上，仅修订两卡及 ADJ，闭环本轮三项 finding；保持 proposed，不改生产代码/冻结字节、不 push。复跑 check/pins，交付固定 commit 后交全新上下文复审；通过后先 Appointment PREREQ-1，FEA-10 等其 done。”