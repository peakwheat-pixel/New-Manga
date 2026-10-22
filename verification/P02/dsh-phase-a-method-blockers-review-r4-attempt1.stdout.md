## P02 Phase A blocker memo r4 · 非作者只读 Review（内容层）

### 1. 内容结论

- **内容结论：`APPROVED_WITH_CONDITIONS`**（仅内容/引用层）。P0/P1/P2 未发现；3 项 P3 为引用精度问题，不改变任何 Gate、阶段或范围结论。
- r4 已落实 attempt 3 三项被接受的修订：
  1. **current Task pin + 行锚点**：r4:8 明确「最初以 attempt 2 pin（108405 bytes / `7521168C…`）为准；本轮在 attempt 3 Review pin（111260 bytes / `351EB291…`）下重新核对」，并声明「两个快照是不同修订，不互换」。逐字复核当前 `doc/tasks/P02.md`：`:68–70` 为 `PROJECT_ORCHESTRATION_AUTHORIZATION`、`:58–62` 为本机替代 Sandbox 裁决及其 Build Gate 边界、`:382–386` 为同一裁决的 continuation 段——三处命中所引语义。
  2. **formal `object_binding=NOT_VERIFIED`**：r4:15 对 r7 内容 Review 明写「formal `object_binding=NOT_VERIFIED`，仅为内容层结论、不是 exact-object 凭证」，与 `dsh-appcontainer-contract-r7-review.stdout.md:12`、r7 adjudication:20 一致。
  3. **版本化 r8 载体**：r4:21 将「新版本 contract r8」定为下一 Phase A 候选的**唯一**释放载体；:19 要求 r8 统一唯一前置条件集合并为新 manifest 写明版本化载体/API 路径解析顺序/句柄访问/错误映射；:27 要求同一 r8 先修正 `GetFileInformationByHandleEx(FileHardLinkInfo)` 再谈 Phase B measurement。
- 引用准确性：attempt 3 report pin `D2E31146…DF3BE`（:15 与 Task:477 一致）、adjudication 的 `0/0/0/3`、`13 closed / 1 partial / 0 open` 均与 r3 attempt3 adjudication:10 一致；r1/r2 结论与计数（`0/0/4/5`、`0/0/2/4`）与 r1 adjudication:19、r2 adjudication:20 一致；prior memo pins（`AB063510…`、`A35CB3A7…`、`44C1F4B2…`、`140DA099…`、`846E4ADA…`、`B49B855F…`、`77347674…`、`7B881C5C…`）均与 `doc/tasks/P02.md:421/431/444/450/458/472` 同值。
- 未发现覆写或不当代表 memo r3：r4:11 明写「只修正 RV4-P3-01..03 的引用与契约载体说明；memo r3 保持不变」，r3 现文本与 attempt 3 pin 一致（仍 57 行 9033 bytes 声明值）。
- 未发现 Task 状态虚报：r4 无任何 object binding 成立、Gate PASS 或测量完成的主张；:8 明写「授权是范围许可，不是 OS 证据或 Gate PASS」，:37 明写 Gate token「全部是状态记录，不是 Gate 通过证据」。
- 阶段隔离成立：:21/:35 维持 Phase A controller-only 只读与排除项；:25 单列 Phase B/Build Gate 缺口并声明「不能并入下一 Phase A manifest」；manifest r3 未被提升为可执行（:15「不能据此推出 r3 可执行」）；r7 `APPROVED` 被限定为内容层且附 object_binding 说明；未把静态 Review 或用户授权当作 OS 证据；未构建屏障保持有效。
- 与 contract r7 / r7 adjudication 无矛盾：r4:19 陈述的 r7 §8.1（`r7:156`）与「精确下一步」第 3 条（`r7:177`，含「均无歧义」）逐字核对成立；`r7:115`、`r7:177` 锚点命中。r4:15 关于 T0/T1 次序不在缺口之列、:16 关于 23 项集合不含 ProgramData、%LOCALAPPDATA%\CrashDumps 可解析，均与 `appcontainer-readonly-preflight-r3.md:20–28` 一致。

### 2. 新增 finding 计数

| 级别 | 数量 |
|---|---:|
| P0 | 0 |
| P1 | 0 |
| P2 | 0 |
| P3 | 3 |

### 3. accepted attempt 3 findings 与处置核对

| 来源 finding | 裁决 | r4 处置 | 本 Review 判定 |
|---|---|---|---|
| RV4-P3-01（Task pin 与锚点基线） | 接受 | :8 双快照并列 + attempt 3 pin 下复核声明 + 「不互换」 | **closed（文本层）** |
| RV4-P3-02（契约修订载体/可溯依据） | 接受 | :19/:21/:27 指定 r8 为唯一载体，含重新 pin/Review/adjudication 前置 | **部分闭合 → RV5-P3-02** |
| RV4-P3-03（r7 Review 自身 object_binding） | 接受 | :15 补 formal `object_binding=NOT_VERIFIED` | **closed** |
| RV3-P3-05（锚点未注明快照） | 保持 partial | :8（RV4-P3-01 已吸收）；attempt 2/3 快照分列不倒推 | **closed（文本层）** |

### 4. 新增 findings

**RV5-P3-01 · 文件自指命名残留（P3）**
- 位置：`verification/P02/codex-phase-a-method-blockers-20261010-r4.md:57`（另见 :9 末句「本 memo r3 候选创建时当前 Task…」——该处为历史快照分句，可接受）。
- 证据：:1 标题为「memo r4 candidate」、Task:478 亦以 r4 登记，但 :57 仍写「本 memo r3 仅供新的非作者文本 Review」。memo r3 已是 attempt 3 的固定 Review 对象且其 adjudication 已存在（Task:477–478）。
- 影响：读者/派发方无法从文内确定本轮被审对象是 r4 还是 r3；不构成 Gate 或范围错误，但降低引用自足性。
- 最小修正：:57 改为「本 memo r4 仅供新的非作者文本 Review」，或加限定「memo r3（本文件前身）已由 attempt 3 Review/adjudication 固定」。

**RV5-P3-02 · r7:156「三项准入」未展开、r7 adjudication 契约级依据未逐字引用（P3）**
- 位置：`...-r4.md:19`。
- 证据：attempt 3 的 RV4-P3-02 建议「修正与下一 Phase A 候选须以契约修订（新 r8 或 Codex 契约级 adjudication）为载体并重新 pin/Review」，并指出 `r7 adjudication:52` 是当前唯一依据；r4:19 采纳 r8 载体，但「列出的三项准入」未列明三项（内容为范围、Review/adjudication/object pin 完成、禁 profile/private-registry API 与禁写，见 `codex-appcontainer-contract-r7-adjudication.md:52`、`r7:156`），且只以文末「（RV4-P3-02）」标注，未给出依据行锚。
- 缓解：:15、:21 已明写 r3 不可执行与「不产生新可执行候选」，误读为「准入已满足」的风险已被上下文覆盖，故非 P2。
- 最小修正：:19 补「三项为：候选范围、Review/adjudication/逐文件 SHA·object pin 完成、不得调用 profile/private-registry API 且不得写入」，并补「（r7 adjudication:52）」。

**RV5-P3-03 · r4:11 归属句语法压缩致指代模糊（P3）**
- 位置：`...-r4.md:11`。
- 证据：原句「memo r4 基于 attempt 3 Review 固定对象（memo r3 SHA-256=…），只修正 RV4-P3-01..03…」把「r4 基于 r3 修订」压缩为「基于被审对象」，与 :10/:11 其他句的严格 pin 粒度不一致。
- 最小修正：改为「memo r4 以 attempt 3 固定 Review 对象 memo r3（SHA-256=…）为修订基线」。

### 5. `object_binding` 限制

**`object_binding = NOT_VERIFIED`。** 本次审查为纯只读内容审查，未运行 shell/PowerShell/Git/hash/测试/Cargo/build/API/ETW/process observer/OS measurement/profile/ACL/registry/label/probe/Windows Sandbox，未修改、创建、删除或移动任何文件。所有字节数与 SHA-256（Task 114140/`F1FAD4AD…`、r4 9987/`ADFA4A2A…`、attempt 3 adjudication `457ED4C4…`、attempt 3 report `D2E31146…`、memo r3 9033/`77347674…`、attempt 2 adjudication `7B881C5C…`、contract r7 `7FBFFE65…`、manifest r3 `AC45329A…`、r7 adjudication `6C585068…`、r7 report `C1FADDC2…`）**均为文本一致性观察**，不构成对象绑定或 hash 复核；本 Review 不得被表述为 exact-hash / object-bound Review，也不得被表述为「Review 通过」。我独立只读核对的是：上述文件正文与行号、`doc/tasks/P02.md` 的 :40–99/:370–486、contract r7 的 :100–178、manifest r3 全文、r7 report 首部与本报告所引各 adjudication 段落。不可核对项：所有字节数/SHA、Git 与工作区状态、本机 OS/registry/ACL/profile 状态、CLI exit 与 session mount 证据、派发 prompt 文件自身身份。

### 6. 精确 Gate 边界

以下 11 项与 `doc/tasks/P02.md:395/404/410/439/480` 同集合同取值，r4:41–51 未做任何提升：

1. **Phase A=`BLOCKED / NOT_RUN`**（未执行/未授权状态，不是测试失败，也不是 OS 测量结果）
2. private_registry_absence=`UNPROVABLE / BLOCKED`
3. profile=`NOT_CREATED`
4. ACL/registry=`NOT_MODIFIED`
5. scratch ACL/label mutation=`AUTHORIZATION_PATH_DEFINED / NOT_APPROVED`
6. OS isolation preflight=`NOT_RUN`
7. hook/cache/child-process closure=`BLOCKED / NOT_VERIFIED`
8. **Build Gate=`BLOCKED`**
9. build=`NOT_AUTHORIZED / NOT_RUN`
10. **Hard Build Barrier=`EFFECTIVE`**
11. **AC1–AC7=`BLOCKED / NOT_RUN`**

本内容结论**不是** Gate PASS、不是 Phase A 执行授权、不解除 Build Gate 或 Hard Build Barrier、不放行 build 或 AC1–AC7；不得据任何静态 Review 推断本机 OS 证据或执行许可；不得据此创建 profile、改 ACL/registry/label、写入、probe、运行测试/Cargo/build/Sandbox；不改变 P02 Task、contract r7、manifest r3、memo r1/r2/r3 与各 adjudication 的任何字节或 pin。

**推荐下一步（唯一可执行项，给 Codex，Lead / Integrator；仍全程只读/纯文档）**：在不触碰任何执行路径的前提下，仅在 r4 上做最小文本修订以闭合 RV5-P3-01（:57 自指命名）、RV5-P3-02（:19 展开 r7:156 三项并补 r7 adjudication:52 锚点）、RV5-P3-03（:11 归属句改写）；重新固定 Task 与 r4 的字节/SHA 并派发新的非作者只读 Review，再由 Codex adjudicate。在 r8 固定、非作者 Review 与 Codex adjudication 完成前，不产生新可执行 Phase A 候选、不运行任何测量、不构建。
