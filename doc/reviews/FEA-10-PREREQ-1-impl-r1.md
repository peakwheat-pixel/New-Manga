<!-- FEA-10-PREREQ-1 implementation review r1 (Codex independent, approved) -->
# FEA-10-PREREQ-1 实现 Review r1（Codex 独立）

- Reviewer：Codex 全新上下文；未参与实现/返修；只读。
- reviewed_head：`728c8bb0570f1b4fe4dc20928b6e09150cea5a63`（base `1254d4e0`）。
- 结论：**approved P0=0/P1=0/P2=1（非阻断：dispatcher 接线缺测试覆盖）**。
- DSH 处置：P2-01 接受为后续债务（不阻断 closeout）；报告原字节归档。

---

**verdict：approved；P0=0 / P1=0 / P2=1（非阻断）。**
reviewed_head：`728c8bb0570f1b4fe4dc20928b6e09150cea5a63`；base：`1254d4e0`。
身份/来源：Codex 全新上下文独立 Reviewer r1（`/root`）；辅助只读审查 `/root/spec`、`/root/standards`；均未参与实现或返修。

- **P2-01｜dispatcher 接线缺少测试覆盖**：[Fea10PrereqProjectionTests.cs:22](/G:/CODEX/New%20Manga/apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea10PrereqProjectionTests.cs:22) 等测试调用真实生产 `ProjectRunError`，但未经过 `InvokeAsync` 的 catch/filter。断开投影接线后，这些测试仍可能通过。最小修复：补经生产 dispatcher 注入错误 envelope 的测试，覆盖三新码、unknown、旧码，并断言 code/requestId/category/retryable/安全消息。

| AC | verdict | 核验结果 |
|---|---|---|
| AC1 | MET | rev 2.12 增量覆盖两命令、字段、3 码、§8 Proposed、两个局部例外及 wire 2.12；运行 minor 分离清楚，未宣称运行已实现。 |
| AC2 | MET | ordinal 不可变白名单；未注册码降为 unknown/false、安全短消息，保留 code/requestId；三新码按冻结值映射，CoreProtocol/传输枚举未改。 |
| AC3 | MET，附 P2 | 注册前后对照调用真实生产投影函数；覆盖旧码及 envelope/ASCII 保真；dispatcher 接线尚无测试保护。 |
| AC4 | MET，证据限定 | DSH build 0 warnings/0 errors；全量 1344 passed/0 failed/74 skipped；定向 13/13、23/23。真实 sidecar Run 回归仍未执行。 |
| AC5 | PARTIAL，符合当前阶段 | EV/Resource/Handoff 已登记；Task 保持 in_review，未提前 done。固定交付与最终 closeout 字段仍待 DSH 收口。 |

实际复跑：`check.ps1` EXIT=0（3 warnings）；`verify_pins.ps1` EXIT=0（17/17）；`git diff --check 1254d4e0..728c8bb0` EXIT=0。
本 Reviewer 的 build/全量/定向测试：**NOT_RUN**，遵守不得产生文件的只读约束；上述测试结果来自已核对日志，74 skipped 未计作通过。
范围核对：实现路径符合 allowed_paths；额外治理文件属于 DSH 集成记录。C-05/C-15/C-16/C-07、FEA-08/09 closeout、FEA-09 evidence、共享组合根和 Run runtime 未改；未新增依赖，未发现确定的旧 Run 错误投影回归。收尾工作树仍干净。

推荐下一步（可转发）：**DSH：请在 main、上述 reviewed_head 归档 r1 报告，处置 P2-01，并完成本卡 AC/交付字段与证据收口及集成 closeout；仅更新获授权的治理文件，不改冻结字节、不 push。FEA-10 须在本卡 done 后按 Appointment 释放。**