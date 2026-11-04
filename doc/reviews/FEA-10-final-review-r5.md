---
task_id: FEA-10
reviewer: Codex（用户指定的全新上下文 /root；第 7 轮最终独立实现 Review）
reviewer_kind: agent
author: Codex / ZCode / DSH（实现及历轮返修）
base_commit: 018646501467d7d40ab7f512beb8a6690cee6f6a
reviewed_head: 290717f1ceb9f4c7180cebc3fae4e596b49d9ae6
decision: approved
---

# FEA-10 最终独立实现 Review r5（第 7 轮）

**结论：approved；P0=0、P1=0；新增非阻断 P2=3。可以交 DSH 进入集成与 closeout 流程，但本报告不把 Task 直接置为 done：AC9 的集成验证、权威指针对账、canonical evidence 与资源核销仍待 DSH。**

F4-01、F4-02 的认证材料走私已闭合。13 种认证负例 × override/defaults 在 Prepare 全部拒绝，另以重算正确 digest 的篡改候选单独打 Accept，26 次也全部拒绝，数据库零变化、没有 Run 行或两列快照落盘。合法扁平词条表中的 token/headers 在 PreparedRun、settings_snapshot_json、run_json 均保留，接受后快照不可变。

不能把上述结果扩写为“所有列表 glossary 都拒绝”或“_redact 单独覆盖所有认证键”。本轮确认的两个防御边界与一处 Python 日志命令缺口见 F5-01…03；均未复现 PreparedRun/Accept 的敏感材料泄漏，不列 P1。

## 身份、范围与上下文

- 审查者为用户直接指定的全新 Codex 上下文 /root，未参与任何实现、返修或既有证据生成；没有可核实的主会话 UUID，不虚构 ID。本轮未派子 agent。遵循仓库 Review 模板关于 Architecture/Verification 必须覆盖、Standards/Spec 可选、无需双轴并行的约定。
- 仓库 G:/CODEX/New Manga，main，Git common directory .git。开始时 HEAD 为上述 reviewed_head，工作树干净。只允许写本报告；未修改生产代码、测试、证据、契约或权威指针，未 commit/push。
- 增量命令：git diff 018646501467d7d40ab7f512beb8a6690cee6f6a 290717f1ceb9f4c7180cebc3fae4e596b49d9ae6。共 15 文件，提交 d1972f0f7cd9b3e17c5289818b5b3b25e164d5e9（返修）及 290717f1ceb9f4c7180cebc3fae4e596b49d9ae6（EV/manifest 回填）。
- 生产增量仅 src/application/tasks/store.py、src/infrastructure/sqlite/pipeline.py；另改一份专项测试，其余为文档/清单/日志。逐 hunk 阅读本增量，追读 Prepare/Accept、SQLite 接受/提交、provider freeze/resolve/fallback、canonical builder、专项测试及 C# 默认 binding、RunMonitor/RunStateStore、真实 IPC 测试；不宣称重新逐行审查全部历史实现。
- 依据：AGENTS.md 用户给定约束、AD-002/AD-003、STATUS、REBASELINE_PLAN 当前 DAG、指定 rolling checkpoint、Task AC/写域/EV、Review 模板、协作协议 §4/§5.1/§6.12；用户指定的 impl-r1、rework-review-r1、final-review-r1/r2/r3/r4；rework r6、AC-MATRIX、Handoff、ADJ-2026-11-04-FEA-10-R2。
- 契约：doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md（SC-R01…09）、FEA-C13_DRAFT_PROTECTION_DRAFT.md（SC-D07/08/12）、FEA-C05_PAGE_VISIBILITY_DRAFT.md、FEA-C04b_DELETE_PROTOCOL_DRAFT.md，以及 doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md rev 2.12 §5.5。冻结文档中的历史“运行未实现”不作为否定现有实现的依据。
- 增量基线、Task 的范围基线 d831cf…、实际实现基线 aa7bcd6161be5df07e2b8bf546600fec04af038f 分开使用；冻结和前置边界另从实际实现基线检查。

## Architecture、Standards 与 Spec

**Architecture：通过（保留 P2 边界）。** 继续采用 Python Core/SQLite 单写者、既有 store/scheduler、两阶段 Prepare/Accept、canonical builder、candidate-only seam、durable receipt。认证键扫描使用从根累计的键路径，错置 typeset.font_family.translate.glossary 不再取得豁免；含对象/列表值的 glossary Mapping 整表拒绝，不再只扫 nested values。Accept 在写入前重新执行快照校验，不能以重算正确 digest 绕过。未新增依赖、Schema、wire 或其他 Task 功能。

**Standards（executed）：** 增量范围合规、EV 字节绑定有效、历史报告未改写。没有另列阻断性代码规范问题或 Fowler smell；新主套件日志的完整命令仍不足（F5-02），既有 skip 原因追溯限制保留。

**Spec（executed）：** F4-01/F4-02 的认证拒绝目标通过独立负例及 Accept 探针；合法业务词条保留。r6 对“任何列表形状直接拒绝”的文字超过实际行为（F5-01）。_redact 的合法 Mapping 豁免路径/形状条件与 scanner 对齐，但两者的全部拒绝/删键策略不等价（F5-03），不能把它当成完整认证验证器。AC 按下表分别判断。

## Findings（本轮）

| ID | 级别 | 文件/行 | 触发、影响与复现 | 建议与状态 |
|---|---|---|---|---|
| F5-01 | P2 | src/application/tasks/store.py:257；src/infrastructure/providers/handlers.py:1237；verification/FEA-10/AC-MATRIX.md 的 rework r6 节 | glossary 本体非 Mapping 时是递归扫描后继续，不是直接拒绝。translate.glossary=[{normal:"word"}]、["word"]、"word" 在 override/defaults 共 6 格均可 Prepare→Accept，并原形落两列；handler 对非 Mapping 返回空 glossary。故 r6“任何层叠/混合/列表形状直接 RUN_SNAPSHOT_INCOMPLETE”不准确。带 authorization 的 list 本体仍拒绝；本轮无认证泄漏，限定为非规范配置的类型/说明缺口，不升级 P1。 | DSH 明确非 Mapping glossary 的兼容口径，按需拒绝或规范化，并把当前说明限定为“Mapping 中含容器值则拒绝；其他形状递归扫认证键”。新增 list 本体和非字符串标量的类型回归。open，非阻断；不得据本报告宣称全类型强校验完成。 |
| F5-02 | P2 | verification/FEA-10/logs/dsh-rework6-pytest-main.log:1 | COMMAND=C:/Python314/python.exe -m pytest tests/fea10 -q; then full suite，后半段没有实际测试目录/参数，不是完整可复制的 pwsh 调用。shell、TEMP/TMP、解释器和两阶段 EXIT 均有；55/1058 输出存在，专项又由主审复跑通过，因此不是伪造或关键链路缺失的确证。 | 后续实际运行日志逐条记录完整命令及环境；本轮 full suite 命令缺口留存，不凭推测补写旧日志。F4-03 原 IPC 头问题已修复，但“本轮所有日志均完整 COMMAND”的总括声明不能认可。open，非阻断。 |
| F5-03 | P2 | src/infrastructure/sqlite/pipeline.py:1502、:1518、:1526；src/application/tasks/store.py:269 | _redact 的敏感 substring 集合仍不含 authorization/headers/bearer/signing_key 等 scanner 认证键；直接对 mixed authorization 或 glossary list authorization 调用 _redact，哨兵仍保留，而 scanner 拒绝。两函数遍历列表均不记录数组边界，直接输入 translate=[{glossary:{token:S}}] 时 scanner PASS、_redact 保留；生产 Prepare/Accept 随后因 translate 非对象拒绝，未形成落盘绕过。属于辅助函数策略不完全一致的防御纵深缺口，不能把 helper 结果扩大为最终安全漏洞。 | 统一明确“词条豁免”与“认证键集合/合法容器路径”策略；如保留不同职责，文档明确 _redact 不是认证验证器，并加 helper 和端到端对照。不要要求整表脱敏器与抛错验证器具有相同返回行为。open，非阻断。 |

## 上轮 findings 与历轮修复

| 项目 | 本轮处置 | 独立依据 |
|---|---|---|
| F4-01 / F3-01 / F2-01 的错置路径走私 | fixed at d1972f0f… | 原 typeset.font_family.translate.glossary.authorization、列表包装、其他 translate 字段、旧错置 glossary 均在 override/defaults 拒绝；无 PreparedRun，无 DB 写；Accept 独立拒绝。 |
| F4-02 的混合表漏扫认证同级键 | fixed at d1972f0f… | 认证键前/后两种顺序、混合 token、普通嵌套值、列表词条值、层叠 glossary 均整体拒绝；Accept 重新计算正确 digest 仍拒绝。非 Mapping 本体的额外宽泛声明另记 F5-01。 |
| F4-03 的 r5 IPC 命令头 | fixed for new IPC log | r6 dotnet.log:214 含项目、Release、--no-build、完整 FullyQualifiedName filter 和两项 env 赋值；:2 为共用 shell/TEMP/TMP/python 头，:219 有 EXIT=0。旧 r5 日志原字节保留。Python 新缺口另记 F5-02。 |
| RR-01 / FR-01 认证与过滤目标 | closed，限已验证 Prepared 路径 | 非执行段过滤、嵌套认证拒绝与本轮 glossary 负例均成立；不宣称任意字符串里的 secret 可自动识别。 |
| RR-02 / FR-02 / F2-02 EV | closed 保持 | 二进制 git show + hashlib，commit 与 CRLF hash 对应；manifest 7/7。 |
| R-001…R-004 | closed 保持 | 合法 typeset 键/非执行段过滤、binding 三种键形状规范化、unsupported fallback fail-closed、Python local typed binding 的专项通过；C# RunPayloads 共用 RunBindingDefaults 及真实测试方法存在。 |
| RR-03 / RR-09 | 成功日志已补；历史失败保留 | r6 主套件输出 1058、build 0/0、.NET 1345/0/75；命令缺口与未复跑范围另列，不改写旧失败历史。 |
| RR-04 / RR-05 / RR-06 | 修复保持 | fallback Mapping 检查、本地 typed 集合及 model/type resolve 检查、Core provider_bindings null/非对象 INVALID_REQUEST 守卫仍在；本增量未改这些逻辑。 |
| RR-07 / RR-08 / FR-08 / F2-04 | 处理保持 | 真实 IPC 输出写 workspace；当前导航指向 RunControllerNullFakeTests.PreparedRunPayload_CarriesTheHostDefaultBindings，实际类/方法存在。历史旧名称不被当成当前入口。 |
| FR-03…FR-07 | 修复保持 | primary 的 mock/local/remote 共用 _freeze_fallbacks；null binding 拒绝、accepted settings 再 freeze、合法词条保留、非法 execution section 拒绝均保持，相关专项在 55 项中通过；非 Mapping glossary 不在这些既有“section 必须对象”检查内。 |

不虚构 RR-10…RR-14：实际 rework-review-r1 findings 为 RR-01…RR-09。

| 既有债务 | 保留的真实边界（最终处置归 DSH） |
|---|---|
| R-005 | 支持的 local typed adapter 有 model/type 检查；专项与合成 adapter 不等于真实模型替换/质量验收。 |
| R-006 | 支持类型但配置不完整的 StartRun 仍可能提前 fail-closed；兼容时点差异继续披露。 |
| R-007 | C# RunMonitor/RunStateStore 只发布查询结果，没有第二状态真值；Python is_terminal 仍无生产消费者，不宣称原生 UI E2E 完成。 |
| R-008/R-009/R-010 | workspace IPC 输出、当前 EV/清单一致性和 Owner/DSH 范围口径已处理；历史错误字节保留。 |
| R-011 | Host candidate/attempt 缓存上限与清理代价未修。 |
| R-012 | InMemory pause/cancel 与生产 SQLite seam 的差异继续明示；本轮拒写结论依据生产 SQLite 故障注入。 |
| R-013 | crash_restart 验证恢复放弃、payload 可诊断和零提前写，不证明重启后 candidate 能继续提交。 |
| R-014 | 合法 token/headers 词条保留；历轮衍生的认证走私本轮已闭合，不能继续当作未修 P1，也不扩写为任意容器都合法。 |
| R-015/R-016 | source lease 异常归并 db_failed、preview 异常统一 unavailable 的诊断局限仍在；系统级 lease 与真实模型验收未跑。 |

## AC1–AC10 独立结论

| AC | 本轮状态 | 判断依据与限制 |
|---|---|---|
| AC1 | MET | 实读 Prepare/Accept/store.accept；专项独立验证零 DB 写/零执行、四元组 SHA-256、stale/expiry/incomplete；写入在 BEGIN IMMEDIATE 的 validate 后。 |
| AC2 | MET（保留 P2 类型/防御边界） | typed execution/digest/fallback fail-closed 保持；26 个认证 Prepare + 26 个 adversarial Accept 全拒，零落盘；合法 token/headers 保留。F5-01 非规范 glossary 类型与 F5-03 helper 策略差异不得隐去；没有证据据此否定最终 Prepared 接受边界的认证安全。 |
| AC3 | MET（ADJ §2.1 限定口径） | transport fixture 拦截 endpoint/model/body，preview/send 同 builder、payload 四路摘要一致，与 preparedDigest 分开；邻页变更 stale、接受后配置隔离专项通过。上游 OCR 依赖仅 requires_upstream_output，不宣称未来正文可预览。 |
| AC4 | MET（已披露边界） | 同键重放不取新快照；新键失败子集/关联 source_run_id/当前上下文冻结；凭据/版本阻塞与恢复、retry provider 变化不改旧快照专项通过。“显式 retry 即确认”的既有口径与真实模型验证限制保留。 |
| AC5 | MET（生产 SQLite seam 层） | 独立运行故障矩阵及成功事务测试；revision/Lock/manual/final/stale/source guard/Binding/draft/DB/pause/cancel/crash 等断言 live、revision、成功回执不提前写；多 Region 编辑 apply 与 pipeline step 单位分开。crash 是 abandoned 恢复，系统级 source lease 未验证。 |
| AC6 | MET（Core 专项 + C# 结构） | pause/stop 请求位持久化时状态仍 running；scheduler 安全边界后改变；终态共同不变量、非法组合、同库重开专项通过；C# 只查询发布。保留 R-007，未宣称原生 UI 点击矩阵通过。 |
| AC7 | MET | 专项包含丢 ACK/过期/配置漂移后原 Run 找回、异 fingerprint 拒绝、不同 key 同 request_id 分离、两个独立 Python 进程同库及 restart receipt；真实 stdio 重启另有 r6 IPC 日志。 |
| AC8 | MET（指定验证范围） | production assembly Prepare→Accept→transport→commit 专项通过；按用户允许核对 r6 .NET/真实 IPC 日志，未冒充主审实跑；总数不减少。真实外网/模型质量、Windows 系统故障与原生 UI 仍 NOT_RUN。 |
| AC9 | BLOCKED（仅 DSH 收口项） | pins 17/17、冻结/前置/组合根零 diff、增量写域、EV/manifest 通过；本报告批准精确 head。DSH 集成后验证、权威指针对账、canonical_evidence_status/resource_closeout_status 与 Handoff closeout 仍 pending。 |
| AC10 | MET | 无新依赖/Schema/未冻结 wire、FEA-11/12/13/14 实现或组合根改动；只用合成隔离数据；无用户源文件/真实应用库操作。 |

## Verification：实际执行、证据与 NOT_RUN

共同环境：CWD=G:/CODEX/New Manga；shell=pwsh 7.6.8，C:/Program Files/PowerShell/7/pwsh.exe；Python=C:/Python314/python.exe 3.14.6，venv=none；PYTHONPATH=src，PYTHONDONTWRITEBYTECODE=1。TEMP/TMP 同指：

G:/CODEX/New Manga.workspace/FEA-10/fixtures/final5-review-895785c723ef49909e0b432f7a6d155b/

只创建合成测试材料；默认值的写入发生在比较基线之前，不冒充 Prepare 零写。探针脚本通过 pwsh here-string 经 stdin 执行，不写生产测试文件。本报告保存命令、探针和输出判别 artefact；不回填 verification/**。

| 场景 | 实际命令/方法 | 结果 |
|---|---|---|
| 治理 | pwsh -NoProfile -File tools/governance/check.ps1 | PASS，4 warnings，EXIT=0。 |
| pins | pwsh -NoProfile -File tools/governance/verify_pins.ps1 | PASS，17/17，EXIT=0。 |
| 专项 | C:/Python314/python.exe -m pytest tests/fea10 -q -p no:cacheprovider | 55 passed、0 skipped、4.86s，EXIT=0。 |
| Prepare/Accept glossary | 本报告附录脚本，stdin Python | 34 格：26 拒绝，6 个非规范安全值接受（F5-01），2 个合法词条表接受；全部 Prepare 零写，无认证哨兵落盘。EXIT=0。 |
| 独立 adversarial Accept | 同一 13 个认证输入重算正确四元组摘要，分别模拟 override/defaults | 26 次 RUN_SNAPSHOT_INCOMPLETE；total_changes 与完整 iterdump hash 均不变，Run=0。EXIT=0。 |
| helper 对照 | 直接 _scan_auth_material/_redact，附录原始输出 | 合法 Mapping 与错置 token 路径符合预期；mixed authorization、list boundary 的差异记 F5-03。EXIT=0。 |
| EV/manifest | subprocess.check_output 二进制 git show + hashlib + LF/CRLF 对照 | 7/7 match；15 文件增量无遗漏、域外=0。EXIT=0。 |
| 保护边界 | git diff --name-only aa7bcd6161be5df07e2b8bf546600fec04af038f 290717f1 -- doc/plan doc/contracts verification/FEA-08 verification/FEA-09 doc/tasks/FEA-08.md doc/tasks/FEA-09.md doc/handoffs/FEA-08-closeout.md doc/handoffs/FEA-09-closeout.md apps/desktop-avalonia/src/NewManga.App/App.axaml apps/desktop-avalonia/src/NewManga.App/App.axaml.cs apps/desktop-avalonia/src/NewManga.App/NewManga.App.csproj apps/desktop-avalonia/NewManga.sln | EMPTY，EXIT=0；实际检查整个 doc/plan，不依赖猜测契约文件名。 |
| diff hygiene | git diff --check 018646501467d7d40ab7f512beb8a6690cee6f6a 290717f1 | 无输出，EXIT=0。 |
| DSH r6 日志核对 | logs/dsh-rework6-{dotnet,providers,pytest-main}.log | Python 55/1058、providers559/4、build0/0、.NET1345/0/75、IPC1；各阶段 EXIT=0。主套件命令不足见 F5-02。 |

主审门禁输出摘录（完整命令与环境如上）：

~~~text
Governance scope: 15 current documents; no historical directory scan.
Task: doc\tasks\FEA-10.md
WARN: 存在 9 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3169 bytes / 30 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：5332 bytes / 53 lines
WARN: evidence_dir 含未登记过程文件（归入 workspace 或列为 SOURCE_PIN）
Governance check: PASS (4 warnings)
EXIT=0
PIN AUDIT: PASS (all 17)
EXIT=0
.......................................................                  [100%]
55 passed in 4.86s
EXIT=0
~~~

最后一条 warning 的实际列举为 changed-files.txt、DELIVERY-MANIFEST.json、OWNER-CHECKPOINT.md、record_delivery.py、RESOURCE-MANIFEST.json、ipc/real-ipc.txt、logs/canonical-commit.log、logs/dotnet-build-final.log，均在 verification/FEA-10 下；本报告不将该既有 warning 擅自消除。

r6 .NET 独立求和：21+38+253+117+78+31+136+671=1345 passed，46+22+7=75 skipped，总计1420、failed=0；另一次定向真实 IPC 为1/0/0。Python 主套件1057→1058，专项54→55，与本增量增加1个测试一致。providers共563，559通过、4跳过。完整 skip 原因没有逐项写在这些新日志中，不能把79个 skip 当成通过或臆造原因；延续前轮追溯限制。主套件的 Pillow warning、尾部历史 QML TypeError 仍可见，不据此释放 Legacy 修复任务。

**NOT_RUN：** 本轮未复跑 .NET build/全量/真实 IPC、Python core/pipeline/providers 全量（仅按授权核对日志）；未做真实模型/外网质量、原生 UI 点击、Windows 系统级 lease/真实模型替换，未逐文件重算2512个历史 fixture 的资源聚合值。没有扫描早期系统 TEMP、访问真实用户库或清理任何资源；未发生需要恢复的 tracked 证据变更。

## EV、manifest、资源与治理差异

| AC-MATRIX 来源 | Git blob（LF） | CRLF 工作树 basis |
|---|---|---|
| d1972f0f7cd9b3e17c5289818b5b3b25e164d5e9 | 15836 bytes；SHA-256=8e77589eef5c961a0c6e6870b1ab47e2fb95a2115e0f5d94a9e8e59bdf15d67c | 15952 bytes；SHA-256=65f6dee67b5cec1e2a57fc973006c7e221021c1bd2a490e04999b0da6a03df68 |
| reviewed_head | 同上 | 同上 |
| 当前工作树 | CRLF 字节 | 15952 bytes；SHA 同上 |

Task EV commit=d1972f0f… 与 sha=65f6dee6… 匹配。CRLF basis 先归一 LF 再转 CRLF；没有用 PowerShell 文本重定向代替二进制 blob。

DELIVERY-MANIFEST 的7项（两份生产文件、专项测试、AC-MATRIX、3份r6日志）均匹配工作树 bytes/SHA，也匹配清单 head=d1972f0f… 的 CRLF 字节。excluded_docs 是本增量4份文档；另排除manifest自身、资源/范围生成文件后，增量15文件无遗漏。d1972f0f→290717f1 只改 Task 与 manifest。created_at/uncommitted 是生成时的记录，head/generated_after_head 为后补锚点，不据此宣称提交后重新生成过清单。

RESOURCE-MANIFEST：2512 cases，处置均为 PRESERVE_REFERENCED，记录 unreadable=[]；build/bin/obj 保留、early_system_temp=PRESERVE_UNKNOWN/scanned=false/cleanup=false，无新 worktree/dependency/model。只核对清单结构/声明与变更，不以此证明每个历史文件仍同字节。本次 review fixture 为本报告新引用材料，晚于旧清单生成，需由 DSH 核销或保留；不得改旧清单冒充当时已有。

治理事实留交 DSH：STATUS/Task 为 in_review，PLAN 仍有“AC2/3/4/6续作”旧措辞，指定 rolling checkpoint 是更早恢复点；Task delivery_head 仍a9293458、integration_commit=null、canonical/resource状态pending。用户本轮指定的精确 head 是实际审查对象，旧字段不能替代它，也不意味着当前 Task 已关闭。

## closeout 与推荐下一步

本 reviewed_head 满足“无 P0/P1”的实现审查批准条件。F5-01…03及上列既有 P2/NOT_RUN 必须由 DSH 如实登记处置；不能改成全形状/全平台/全模型通过。当前不能直接done；DSH完成集成后验证、AC9指针及资源核销后可closeout。若选择修改生产代码处理P2，须固定新head并重新Review，不能沿用本head批准。

推荐下一步 Task：FEA-10 的 DSH 集成/closeout 切片，Agent=DSH。恢复点：G:/CODEX/New Manga，main，base=018646501467d7d40ab7f512beb8a6690cee6f6a，当前head=290717f1ceb9f4c7180cebc3fae4e596b49d9ae6；无需新worktree。范围限本Task集成记录、Task/Handoff、STATUS/PLAN当前指针及FEA-10 evidence/resource manifest；不修改冻结契约、Schema/依赖、FEA-08/09证据、组合根或用户数据。交付为准确的integration_commit、canonical/resource complete、AC9及closeout Handoff、集成后验证输出。通过前不自动释放FEA-11。

可直接转发：

> DSH：请在G:/CODEX/New Manga的main核对HEAD=290717f1ceb9f4c7180cebc3fae4e596b49d9ae6，基线018646501467d7d40ab7f512beb8a6690cee6f6a，接收doc/reviews/FEA-10-final-review-r5.md（第7轮approved，P0/P1=0）。先处置并保留F5-01…03与既有P2/NOT_RUN，按FEA-10既定范围执行集成/closeout；不改冻结契约、Schema/依赖、FEA-08/09证据、组合根或用户数据，不push。对齐Task/STATUS/PLAN真实head和AC口径，重跑集成所需pytest tests/fea10、check.ps1与verify_pins.ps1并保存完整COMMAND/shell/解释器/TEMP/TMP/EXIT，逐项记录skip；如修改生产字节则冻结新head另派Review。核销或保留本报告引用的final5-review fixture及既有资源，完成Handoff、EV commit/hash、manifest、integration_commit和canonical/resource状态后才置done。通过前不释放FEA-11。

报告落盘后复跑 check.ps1：PASS（4 warnings），EXIT=0；git status --short 仅有本报告 untracked，tracked/staged diff 均为空，HEAD 仍为 290717f1ceb9f4c7180cebc3fae4e596b49d9ae6。未 commit/push。

## 附录：可复制探针与实际输出 artefact

重放时将 TEMP/TMP 指向新的 final5-review-<uuid>/ 目录，并设置 PYTHONPATH=src、PYTHONDONTWRITEBYTECODE=1；不得复用本报告已存在的子目录。执行方式为 pwsh 的 `@' ... '@ | C:/Python314/python.exe -`，然后记录 `$LASTEXITCODE`。下列为本轮实际 Python stdin 内容；输出仅省略重复的 schema bootstrap 提示（每例先建合成库），保留全部判别 JSON，未把已接受的非规范输入改记拒绝。

### Prepare、合法 Accept 与 helper 原脚本

~~~python
import os,json,hashlib
from pathlib import Path
from tests.core.test_fea00a_pipeline_seam import _new_workspace
from domain.tasks.models import PipelineScope,ScopeType,PipelineError
from application.tasks.store import _scan_auth_material
from infrastructure.sqlite.pipeline import _redact
S="SYNTHETIC-FINAL5-AUTH"
cases={
"old_misplaced":{"typeset":{"font_family":{"glossary":{"authorization":S}}}},
"old_layered":{"translate":{"glossary":{"outer":{"glossary":{"authorization":S}}}}},
"misplaced_translate":{"typeset":{"font_family":{"translate":{"glossary":{"authorization":S}}}}},
"layered_translate":{"translate":{"glossary":{"outer":{"translate":{"glossary":{"authorization":S}}}}}},
"mixed_auth_first":{"translate":{"glossary":{"authorization":S,"outer":{"normal":"value"}}}},
"mixed_auth_last":{"translate":{"glossary":{"outer":{"normal":"value"},"authorization":S}}},
"mixed_token":{"translate":{"glossary":{"token":S,"outer":{"normal":"value"}}}},
"mixed_list":{"translate":{"glossary":{"authorization":S,"outer":["word"]}}},
"misplaced_list":{"typeset":{"font_family":[{"translate":{"glossary":{"authorization":S}}}]}},
"other_translate":{"translate":{"target_language":{"translate":{"glossary":{"authorization":S}}}}},
"layered_list":{"translate":{"glossary":{"outer":[{"translate":{"glossary":{"authorization":S}}}]}}},
"normal_headers":{"typeset":{"font_family":{"headers":{"authorization":S}}}},
"glossary_list_auth":{"translate":{"glossary":[{"authorization":S}]}},
"glossary_list_normal":{"translate":{"glossary":[{"normal":"word"}]}},
"glossary_list_text":{"translate":{"glossary":["word"]}},
"glossary_scalar":{"translate":{"glossary":"word"}},
"legal":{"translate":{"glossary":{"token":"word-value","headers":"another-word"}}},
}
def state(core):
    return (core.conn.total_changes, hashlib.sha256("\n".join(core.conn.iterdump()).encode()).hexdigest())
out=[]
for name,settings in cases.items():
    for mode in ("override","defaults"):
        p=Path(os.environ["TEMP"])/(name+"-"+mode); p.mkdir()
        core,_,region=_new_workspace(p)
        try:
            scope=PipelineScope(ScopeType.REGION,selected_ids=(region,))
            if mode=="defaults":
                for section,values in settings.items():
                    core.pipeline_defaults.save_settings_section(section,values)
            before=state(core); prepared=None
            try:
                prepared=core.pipeline.prepare_run("ocr_region",scope,**({"overrides":{"settings":settings}} if mode=="override" else {}))
                prepare_zero=state(core)==before
                run,created=core.pipeline.accept_prepared_run(prepared,scope,idempotency_key="probe")
                row=core.conn.execute("SELECT settings_snapshot_json,run_json FROM pipeline_runs WHERE run_id=?",(run.run_id,)).fetchone()
                glossary=prepared["settingsSnapshot"]["translate"]["glossary"] if name.startswith("glossary") or name=="legal" else None
                legal_keep=(all(json.loads(column)["translate"]["glossary"]["token"]=="word-value" for column in [row[0]]) and json.loads(row[1])["settings_snapshot"]["translate"]["glossary"]["token"]=="word-value") if name=="legal" else None
                headers_keep=(json.loads(row[0])["translate"]["glossary"]["headers"]=="another-word" and json.loads(row[1])["settings_snapshot"]["translate"]["glossary"]["headers"]=="another-word") if name=="legal" else None
                immutable=None
                if name=="legal":
                    try: run.settings_snapshot["translate"]["glossary"]["token"]="changed"
                    except TypeError: immutable=True
                result=dict(case=name,mode=mode,result="ACCEPTED",created=created,prepare_zero=prepare_zero,prepared_sentinel=S in str(prepared),columns_sentinel=[S in c for c in row],glossary=str(glossary),token_both_columns=legal_keep,headers_both_columns=headers_keep,immutable=immutable)
            except PipelineError as e:
                result=dict(case=name,mode=mode,result=e.code,zero_side_effects=state(core)==before,no_prepared=prepared is None,runs=core.conn.execute("select count(*) from pipeline_runs").fetchone()[0],error_contains_sentinel=S in str(e))
            out.append(result); print(json.dumps(result,ensure_ascii=True,sort_keys=True))
        finally:core.conn.close()
for name,value in {
"legal_settings":cases["legal"],
"legal_override":{"settings":cases["legal"]},
"misplaced_token":{"typeset":{"font_family":{"translate":{"glossary":{"token":S}}}}},
"layered_token":{"translate":{"glossary":{"outer":{"translate":{"glossary":{"token":S}}}}}},
"mixed_token":cases["mixed_token"],
"mixed_authorization":cases["mixed_auth_first"],
"glossary_list_auth":cases["glossary_list_auth"],
"wrong_list_path":{"translate":[{"glossary":{"token":S}}]},
}.items():
    try:_scan_auth_material(value); scan="PASS"
    except PipelineError as e:scan=e.code
    print(json.dumps(dict(redact_case=name,scan=scan,redacted=_redact(value),redacted_sentinel=S in str(_redact(value))),sort_keys=True))
print("SUMMARY="+json.dumps(dict(total=len(out),rejected=sum(r["result"]!="ACCEPTED" for r in out),accepted=sum(r["result"]=="ACCEPTED" for r in out),sentinel_leaks=sum(any(r.get("columns_sentinel",[])) for r in out)),sort_keys=True))

~~~

### 本次实际输出

~~~text
shell=pwsh 7.6.8; TEMP=G:/CODEX/New Manga.workspace/FEA-10/fixtures/final5-review-895785c723ef49909e0b432f7a6d155b/; TMP=G:/CODEX/New Manga.workspace/FEA-10/fixtures/final5-review-895785c723ef49909e0b432f7a6d155b/; python=C:/Python314/python.exe 3.14.6; venv=none; COMMAND=Python probe via stdin
{"case": "old_misplaced", "error_contains_sentinel": false, "mode": "override", "no_prepared": true, "result": "RUN_SNAPSHOT_INCOMPLETE", "runs": 0, "zero_side_effects": true}
{"case": "old_misplaced", "error_contains_sentinel": false, "mode": "defaults", "no_prepared": true, "result": "RUN_SNAPSHOT_INCOMPLETE", "runs": 0, "zero_side_effects": true}
{"case": "old_layered", "error_contains_sentinel": false, "mode": "override", "no_prepared": true, "result": "RUN_SNAPSHOT_INCOMPLETE", "runs": 0, "zero_side_effects": true}
{"case": "old_layered", "error_contains_sentinel": false, "mode": "defaults", "no_prepared": true, "result": "RUN_SNAPSHOT_INCOMPLETE", "runs": 0, "zero_side_effects": true}
{"case": "misplaced_translate", "error_contains_sentinel": false, "mode": "override", "no_prepared": true, "result": "RUN_SNAPSHOT_INCOMPLETE", "runs": 0, "zero_side_effects": true}
{"case": "misplaced_translate", "error_contains_sentinel": false, "mode": "defaults", "no_prepared": true, "result": "RUN_SNAPSHOT_INCOMPLETE", "runs": 0, "zero_side_effects": true}
{"case": "layered_translate", "error_contains_sentinel": false, "mode": "override", "no_prepared": true, "result": "RUN_SNAPSHOT_INCOMPLETE", "runs": 0, "zero_side_effects": true}
{"case": "layered_translate", "error_contains_sentinel": false, "mode": "defaults", "no_prepared": true, "result": "RUN_SNAPSHOT_INCOMPLETE", "runs": 0, "zero_side_effects": true}
{"case": "mixed_auth_first", "error_contains_sentinel": false, "mode": "override", "no_prepared": true, "result": "RUN_SNAPSHOT_INCOMPLETE", "runs": 0, "zero_side_effects": true}
{"case": "mixed_auth_first", "error_contains_sentinel": false, "mode": "defaults", "no_prepared": true, "result": "RUN_SNAPSHOT_INCOMPLETE", "runs": 0, "zero_side_effects": true}
{"case": "mixed_auth_last", "error_contains_sentinel": false, "mode": "override", "no_prepared": true, "result": "RUN_SNAPSHOT_INCOMPLETE", "runs": 0, "zero_side_effects": true}
{"case": "mixed_auth_last", "error_contains_sentinel": false, "mode": "defaults", "no_prepared": true, "result": "RUN_SNAPSHOT_INCOMPLETE", "runs": 0, "zero_side_effects": true}
{"case": "mixed_token", "error_contains_sentinel": false, "mode": "override", "no_prepared": true, "result": "RUN_SNAPSHOT_INCOMPLETE", "runs": 0, "zero_side_effects": true}
{"case": "mixed_token", "error_contains_sentinel": false, "mode": "defaults", "no_prepared": true, "result": "RUN_SNAPSHOT_INCOMPLETE", "runs": 0, "zero_side_effects": true}
{"case": "mixed_list", "error_contains_sentinel": false, "mode": "override", "no_prepared": true, "result": "RUN_SNAPSHOT_INCOMPLETE", "runs": 0, "zero_side_effects": true}
{"case": "mixed_list", "error_contains_sentinel": false, "mode": "defaults", "no_prepared": true, "result": "RUN_SNAPSHOT_INCOMPLETE", "runs": 0, "zero_side_effects": true}
{"case": "misplaced_list", "error_contains_sentinel": false, "mode": "override", "no_prepared": true, "result": "RUN_SNAPSHOT_INCOMPLETE", "runs": 0, "zero_side_effects": true}
{"case": "misplaced_list", "error_contains_sentinel": false, "mode": "defaults", "no_prepared": true, "result": "RUN_SNAPSHOT_INCOMPLETE", "runs": 0, "zero_side_effects": true}
{"case": "other_translate", "error_contains_sentinel": false, "mode": "override", "no_prepared": true, "result": "RUN_SNAPSHOT_INCOMPLETE", "runs": 0, "zero_side_effects": true}
{"case": "other_translate", "error_contains_sentinel": false, "mode": "defaults", "no_prepared": true, "result": "RUN_SNAPSHOT_INCOMPLETE", "runs": 0, "zero_side_effects": true}
{"case": "layered_list", "error_contains_sentinel": false, "mode": "override", "no_prepared": true, "result": "RUN_SNAPSHOT_INCOMPLETE", "runs": 0, "zero_side_effects": true}
{"case": "layered_list", "error_contains_sentinel": false, "mode": "defaults", "no_prepared": true, "result": "RUN_SNAPSHOT_INCOMPLETE", "runs": 0, "zero_side_effects": true}
{"case": "normal_headers", "error_contains_sentinel": false, "mode": "override", "no_prepared": true, "result": "RUN_SNAPSHOT_INCOMPLETE", "runs": 0, "zero_side_effects": true}
{"case": "normal_headers", "error_contains_sentinel": false, "mode": "defaults", "no_prepared": true, "result": "RUN_SNAPSHOT_INCOMPLETE", "runs": 0, "zero_side_effects": true}
{"case": "glossary_list_auth", "error_contains_sentinel": false, "mode": "override", "no_prepared": true, "result": "RUN_SNAPSHOT_INCOMPLETE", "runs": 0, "zero_side_effects": true}
{"case": "glossary_list_auth", "error_contains_sentinel": false, "mode": "defaults", "no_prepared": true, "result": "RUN_SNAPSHOT_INCOMPLETE", "runs": 0, "zero_side_effects": true}
{"case": "glossary_list_normal", "columns_sentinel": [false, false], "created": true, "glossary": "[{'normal': 'word'}]", "headers_both_columns": null, "immutable": null, "mode": "override", "prepare_zero": true, "prepared_sentinel": false, "result": "ACCEPTED", "token_both_columns": null}
{"case": "glossary_list_normal", "columns_sentinel": [false, false], "created": true, "glossary": "[{'normal': 'word'}]", "headers_both_columns": null, "immutable": null, "mode": "defaults", "prepare_zero": true, "prepared_sentinel": false, "result": "ACCEPTED", "token_both_columns": null}
{"case": "glossary_list_text", "columns_sentinel": [false, false], "created": true, "glossary": "['word']", "headers_both_columns": null, "immutable": null, "mode": "override", "prepare_zero": true, "prepared_sentinel": false, "result": "ACCEPTED", "token_both_columns": null}
{"case": "glossary_list_text", "columns_sentinel": [false, false], "created": true, "glossary": "['word']", "headers_both_columns": null, "immutable": null, "mode": "defaults", "prepare_zero": true, "prepared_sentinel": false, "result": "ACCEPTED", "token_both_columns": null}
{"case": "glossary_scalar", "columns_sentinel": [false, false], "created": true, "glossary": "word", "headers_both_columns": null, "immutable": null, "mode": "override", "prepare_zero": true, "prepared_sentinel": false, "result": "ACCEPTED", "token_both_columns": null}
{"case": "glossary_scalar", "columns_sentinel": [false, false], "created": true, "glossary": "word", "headers_both_columns": null, "immutable": null, "mode": "defaults", "prepare_zero": true, "prepared_sentinel": false, "result": "ACCEPTED", "token_both_columns": null}
{"case": "legal", "columns_sentinel": [false, false], "created": true, "glossary": "{'token': 'word-value', 'headers': 'another-word'}", "headers_both_columns": true, "immutable": true, "mode": "override", "prepare_zero": true, "prepared_sentinel": false, "result": "ACCEPTED", "token_both_columns": true}
{"case": "legal", "columns_sentinel": [false, false], "created": true, "glossary": "{'headers': 'another-word', 'token': 'word-value'}", "headers_both_columns": true, "immutable": true, "mode": "defaults", "prepare_zero": true, "prepared_sentinel": false, "result": "ACCEPTED", "token_both_columns": true}
{"redact_case": "legal_settings", "redacted": {"translate": {"glossary": {"headers": "another-word", "token": "word-value"}}}, "redacted_sentinel": false, "scan": "PASS"}
{"redact_case": "legal_override", "redacted": {"settings": {"translate": {"glossary": {"headers": "another-word", "token": "word-value"}}}}, "redacted_sentinel": false, "scan": "PASS"}
{"redact_case": "misplaced_token", "redacted": {"typeset": {"font_family": {"translate": {"glossary": {}}}}}, "redacted_sentinel": false, "scan": "RUN_SNAPSHOT_INCOMPLETE"}
{"redact_case": "layered_token", "redacted": {"translate": {"glossary": {"outer": {"translate": {"glossary": {}}}}}}, "redacted_sentinel": false, "scan": "RUN_SNAPSHOT_INCOMPLETE"}
{"redact_case": "mixed_token", "redacted": {"translate": {"glossary": {"outer": {"normal": "value"}}}}, "redacted_sentinel": false, "scan": "RUN_SNAPSHOT_INCOMPLETE"}
{"redact_case": "mixed_authorization", "redacted": {"translate": {"glossary": {"authorization": "SYNTHETIC-FINAL5-AUTH", "outer": {"normal": "value"}}}}, "redacted_sentinel": true, "scan": "RUN_SNAPSHOT_INCOMPLETE"}
{"redact_case": "glossary_list_auth", "redacted": {"translate": {"glossary": [{"authorization": "SYNTHETIC-FINAL5-AUTH"}]}}, "redacted_sentinel": true, "scan": "RUN_SNAPSHOT_INCOMPLETE"}
{"redact_case": "wrong_list_path", "redacted": {"translate": [{"glossary": {"token": "SYNTHETIC-FINAL5-AUTH"}}]}, "redacted_sentinel": true, "scan": "PASS"}
SUMMARY={"accepted": 8, "rejected": 26, "sentinel_leaks": 0, "total": 34}
EXIT=0
~~~

### 单独对 Accept 提交恶意快照的原脚本

先生成正常候选，再替换 settingsSnapshot（override 模式同步替换 overrides；defaults 模式写当前默认值），对恶意四元组重算正确 digest。该探针与 Prepare 拒绝分开，证明 Accept 的拒绝不是沿用 Prepare 异常或摘要格式错误。

~~~python
import os,json,hashlib
from pathlib import Path
from tests.core.test_fea00a_pipeline_seam import _new_workspace
from domain.tasks.models import PipelineScope,ScopeType,PipelineError
from application.tasks.store import prepared_quartet,snapshot_digest
S="SYNTHETIC-FINAL5-ACCEPT"
cases={
"misplaced":{"typeset":{"font_family":{"translate":{"glossary":{"authorization":S}}}}},
"mixed_first":{"translate":{"glossary":{"authorization":S,"outer":{"normal":"value"}}}},
"mixed_last":{"translate":{"glossary":{"outer":{"normal":"value"},"authorization":S}}},
"mixed_list":{"translate":{"glossary":{"authorization":S,"outer":["word"]}}},
"layered":{"translate":{"glossary":{"outer":{"translate":{"glossary":{"authorization":S}}}}}},
"misplaced_list":{"typeset":{"font_family":[{"translate":{"glossary":{"authorization":S}}}]}},
"other_field":{"translate":{"target_language":{"translate":{"glossary":{"authorization":S}}}}},
"layered_list":{"translate":{"glossary":{"outer":[{"translate":{"glossary":{"authorization":S}}}]}}},
"old_misplaced":{"typeset":{"font_family":{"glossary":{"authorization":S}}}},
"old_layered":{"translate":{"glossary":{"outer":{"glossary":{"authorization":S}}}}},
"normal_headers":{"typeset":{"font_family":{"headers":{"authorization":S}}}},
"mixed_token":{"translate":{"glossary":{"token":S,"outer":{"normal":"value"}}}},
"glossary_list_auth":{"translate":{"glossary":[{"authorization":S}]}},
}
def state(c):
 return (c.conn.total_changes,hashlib.sha256("\n".join(c.conn.iterdump()).encode()).hexdigest())
n=0
for name,settings in cases.items():
 for mode in ("override","defaults"):
  p=Path(os.environ["TEMP"])/("accept-"+name+"-"+mode);p.mkdir()
  c,_,r=_new_workspace(p)
  try:
   scope=PipelineScope(ScopeType.REGION,selected_ids=(r,))
   candidate=c.pipeline.prepare_run("ocr_region",scope)
   if mode=="defaults":
    for section,values in settings.items():c.pipeline_defaults.save_settings_section(section,values)
   else:candidate["overrides"]={"settings":settings}
   candidate["settingsSnapshot"]=settings
   quartet={k:candidate[k] for k in ("requestedTargets","settingsSnapshot","providerBindingSnapshot","constraintSnapshotRef")}
   candidate["preparedDigest"]=candidate["snapshotDigest"]=snapshot_digest(quartet)
   before=state(c)
   try:
    c.pipeline.accept_prepared_run(candidate,scope,idempotency_key="adversarial-accept")
    raise AssertionError("unsafe candidate accepted")
   except PipelineError as e:
    assert e.code=="RUN_SNAPSHOT_INCOMPLETE",(name,e)
    assert state(c)==before
    assert c.conn.execute("select count(*) from pipeline_runs").fetchone()[0]==0
    assert S not in str(e)
    n+=1
    print(json.dumps(dict(case=name,mode=mode,accept=e.code,zero_side_effects=True,runs=0,columns_have_no_rows=True),sort_keys=True))
  finally:c.conn.close()
print("ACCEPT_REJECTIONS="+str(n))

~~~

### Accept 实际输出

~~~text
shell=pwsh 7.6.8; python=C:/Python314/python.exe 3.14.6; venv=none; COMMAND=adversarial Accept via stdin; TEMP=TMP=G:/CODEX/New Manga.workspace/FEA-10/fixtures/final5-review-895785c723ef49909e0b432f7a6d155b/
{"accept": "RUN_SNAPSHOT_INCOMPLETE", "case": "misplaced", "columns_have_no_rows": true, "mode": "override", "runs": 0, "zero_side_effects": true}
{"accept": "RUN_SNAPSHOT_INCOMPLETE", "case": "misplaced", "columns_have_no_rows": true, "mode": "defaults", "runs": 0, "zero_side_effects": true}
{"accept": "RUN_SNAPSHOT_INCOMPLETE", "case": "mixed_first", "columns_have_no_rows": true, "mode": "override", "runs": 0, "zero_side_effects": true}
{"accept": "RUN_SNAPSHOT_INCOMPLETE", "case": "mixed_first", "columns_have_no_rows": true, "mode": "defaults", "runs": 0, "zero_side_effects": true}
{"accept": "RUN_SNAPSHOT_INCOMPLETE", "case": "mixed_last", "columns_have_no_rows": true, "mode": "override", "runs": 0, "zero_side_effects": true}
{"accept": "RUN_SNAPSHOT_INCOMPLETE", "case": "mixed_last", "columns_have_no_rows": true, "mode": "defaults", "runs": 0, "zero_side_effects": true}
{"accept": "RUN_SNAPSHOT_INCOMPLETE", "case": "mixed_list", "columns_have_no_rows": true, "mode": "override", "runs": 0, "zero_side_effects": true}
{"accept": "RUN_SNAPSHOT_INCOMPLETE", "case": "mixed_list", "columns_have_no_rows": true, "mode": "defaults", "runs": 0, "zero_side_effects": true}
{"accept": "RUN_SNAPSHOT_INCOMPLETE", "case": "layered", "columns_have_no_rows": true, "mode": "override", "runs": 0, "zero_side_effects": true}
{"accept": "RUN_SNAPSHOT_INCOMPLETE", "case": "layered", "columns_have_no_rows": true, "mode": "defaults", "runs": 0, "zero_side_effects": true}
{"accept": "RUN_SNAPSHOT_INCOMPLETE", "case": "misplaced_list", "columns_have_no_rows": true, "mode": "override", "runs": 0, "zero_side_effects": true}
{"accept": "RUN_SNAPSHOT_INCOMPLETE", "case": "misplaced_list", "columns_have_no_rows": true, "mode": "defaults", "runs": 0, "zero_side_effects": true}
{"accept": "RUN_SNAPSHOT_INCOMPLETE", "case": "other_field", "columns_have_no_rows": true, "mode": "override", "runs": 0, "zero_side_effects": true}
{"accept": "RUN_SNAPSHOT_INCOMPLETE", "case": "other_field", "columns_have_no_rows": true, "mode": "defaults", "runs": 0, "zero_side_effects": true}
{"accept": "RUN_SNAPSHOT_INCOMPLETE", "case": "layered_list", "columns_have_no_rows": true, "mode": "override", "runs": 0, "zero_side_effects": true}
{"accept": "RUN_SNAPSHOT_INCOMPLETE", "case": "layered_list", "columns_have_no_rows": true, "mode": "defaults", "runs": 0, "zero_side_effects": true}
{"accept": "RUN_SNAPSHOT_INCOMPLETE", "case": "old_misplaced", "columns_have_no_rows": true, "mode": "override", "runs": 0, "zero_side_effects": true}
{"accept": "RUN_SNAPSHOT_INCOMPLETE", "case": "old_misplaced", "columns_have_no_rows": true, "mode": "defaults", "runs": 0, "zero_side_effects": true}
{"accept": "RUN_SNAPSHOT_INCOMPLETE", "case": "old_layered", "columns_have_no_rows": true, "mode": "override", "runs": 0, "zero_side_effects": true}
{"accept": "RUN_SNAPSHOT_INCOMPLETE", "case": "old_layered", "columns_have_no_rows": true, "mode": "defaults", "runs": 0, "zero_side_effects": true}
{"accept": "RUN_SNAPSHOT_INCOMPLETE", "case": "normal_headers", "columns_have_no_rows": true, "mode": "override", "runs": 0, "zero_side_effects": true}
{"accept": "RUN_SNAPSHOT_INCOMPLETE", "case": "normal_headers", "columns_have_no_rows": true, "mode": "defaults", "runs": 0, "zero_side_effects": true}
{"accept": "RUN_SNAPSHOT_INCOMPLETE", "case": "mixed_token", "columns_have_no_rows": true, "mode": "override", "runs": 0, "zero_side_effects": true}
{"accept": "RUN_SNAPSHOT_INCOMPLETE", "case": "mixed_token", "columns_have_no_rows": true, "mode": "defaults", "runs": 0, "zero_side_effects": true}
{"accept": "RUN_SNAPSHOT_INCOMPLETE", "case": "glossary_list_auth", "columns_have_no_rows": true, "mode": "override", "runs": 0, "zero_side_effects": true}
{"accept": "RUN_SNAPSHOT_INCOMPLETE", "case": "glossary_list_auth", "columns_have_no_rows": true, "mode": "defaults", "runs": 0, "zero_side_effects": true}
ACCEPT_REJECTIONS=26
EXIT=0
~~~


