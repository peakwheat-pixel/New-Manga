---
task_id: [GIT-CLEAN-CORE-ENV-2, FEA11-ENTRY-MISSING-1, INSTALLER-MATRIX-1, MAINT-1-RELEASE-MONITOR]
kind: external-ruling
authority: Codex（外部裁定；只读，未修改任何文件、未运行测试）
invited_by: DSH（Lead / Architect / Integrator）
issued_at: 2026-11-17T17:30+08:00
subject: CORE-ENV-2 处置 / FEA11-ENTRY-MISSING-1 处置 / Release Gate 条件 3-4-5 的人工项可代理性
decision: Q1=(B) closed_with_limitations / Q2=(A) 保持 blocked + 另立最小实现卡 / Q3=条件3 AGENT_ADJUDICATION_PENDING、条件4 另立签名矩阵卡、条件5 LIMITATION_ACCEPTED
adopted_by: DSH
---

# Codex 裁定（2026-11-17）：CORE-ENV-2 / FEA11-ENTRY-MISSING-1 / Gate 条件 3-4-5

> 本文件是 Codex 的书面裁定原文（只读产出，由 DSH 逐字保存）；末尾「DSH 采纳」段为 Lead 的采纳与执行记录。

## Q1 CORE-ENV-2

**裁定：选 B，`closed_with_limitations`。** 这是 Codex 依据 2026-11-17 委托授权作出的书面裁定，供 DSH 按 Task 生命周期记录；不在本次只读审查中修改状态。

卡面至今没有定义 V2–V5 的变量或可用环境，AC1–AC3 因此仍为 `BLOCKED`，AC4 为 `PARTIAL`；没有执行结果或新证据可支持诊断结论。把它取消并称为“无价值”没有证据；继续保持 `proposed` 则保留了一张没有可执行解锁条件、也不能实施的卡。`proposed` 不得实施，`blocked` 须记录恢复条件；`closed_with_limitations` 是终态但不代表技术完成，且须保留未完成 AC 的原始状态与分类。[GIT-CLEAN-CORE-ENV-2:6-10,30,34-47](#)；[09_COLLABORATION.md:69-81](#)

若 DSH 按此裁定收口，卡面限制至少应记录：

- **未执行、未定论**：V2–V5 定义、控制项、版本 SHA、环境路径、预算与停止条件均缺失；不推断变量原意，不把旧 `UNKNOWN` 改成结论。
- **原样保留 AC 状态**：AC1–AC3 `BLOCKED`、AC4 `PARTIAL`；保留 `approval: pending_variable_and_environment_freeze`，不得标为通过。
- **ACL 边界仍有效**：没有任何 `/grant`、`/reset` 写入或真实 grant 返回码证据；只读查询不能代替写入失败的证据。
- **后续重启门槛**：只有变量矩阵与安全环境、预算及停止条件都具体冻结后，DSH 才可另行释放执行；没有新的冻结内容前不恢复实施。
- **Reviewer 改派**：Antigravity 已退出项目，应改派 ZCode 或新的独立 Codex 上下文。Codex 本裁定会话不得自审；Review appointment 与 Task 状态处置由 DSH 负责。[AGENTS.md「当前授权」「角色与交付」段，用户本轮提供；另见 09_COLLABORATION.md:7,16,20,81](#)

## Q2 FEA11-ENTRY-MISSING-1

**裁定：选 A，保持 `blocked`，另立错误映射保真实现卡。** 现卡的 allowed paths 仅覆盖 Task、Review、Plan/Status、Ledger 与 verification，没有产品源码范围；卡面也明确记录了内层异常被兜底丢弃，现有证据无法区分具体失败原因。[FEA11-ENTRY-MISSING-1:6-11,22-30,35-50](#)

这构成当前卡的实施阻塞：加日志或保留异常类型都要改产品代码，不能借诊断卡实施。它**不必然**构成共享契约变更：如果只在内部诊断元数据保留异常类型、外部错误码和 wire/API 行为不变，就不是当然的 Schema 变更；但若异常类型要进入 Host/Core wire、公共错误映射或 Schema，则属于须由 DSH 先冻结范围的共享契约变更。协议也明确，诊断结论不会自动授权修复，超出 `allowed_paths` 应先提范围变更。[09_COLLABORATION.md:24,56,71,78-81](#)

建议新卡先保持 `proposed`，最小范围为：

- 修复 `MapMintFailure` 的兜底路径，使内部诊断结果保留内层异常类型；**公共错误码、API/Schema 和 wire 行为不变**。
- 为 `FileNotFound`、`Unauthorized`、其他异常类别增加针对映射路径的回归断言；避免把原始路径或敏感消息写入外部错误。
- 固定源码及测试 `allowed_paths`、基线和复现命令；实现后重跑原 `FileStream` 入口复现，确认能区分异常类型。
- 若必须改公共映射或 wire/Schema，先由 DSH 冻结契约范围，再释放实现。

现卡继续保留未定论状态；不得在现卡里加日志或改产品代码。

## Q3 Gate 人工项

当前状态仍是条件 3 缺 overlay 视觉判断、条件 4 缺签名与真实安装矩阵、条件 5 质量基线 `NOT_RUN`；`Technical Gate=NOT_SATISFIED`。[STATUS.md:8,21-22](#)

### 条件 3：阅读器 overlay 视觉

**允许用独立 Codex/ZCode 的书面视觉裁定替代人工目视判断，但纯 headless 渲染、截图存在或像素 diff 单独都不够。** 这是对实际画面作出的委托判断；结果必须标明是 Agent 评估，不能记成“人眼已验证”。

最低证据：固定产品 head 与 exe hash；在真实窗口触发 F11 后保存原始截图；记录 Windows 版本、分辨率、DPI 与操作步骤；由未参与实现的 Codex 新上下文或 ZCode 对截图按全屏/无边框、遮挡、裁切和可读性作出具名书面判断，并附截图 hash。当前尚无这组 overlay 证据，因此仍标未完成；追加状态可用 `AGENT_ADJUDICATION_PENDING`，避免继续用“等人”作为唯一动作。[RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md:120-140](#)

### 条件 4：签名与安装矩阵

**脚本化矩阵可以替代人工执行，但必须真实运行于目标 Windows 环境；模拟结果或 dry-run 不可替代。** 最低证据：固定当前产品 commit 和安装包 hash；记录干净 Windows VM/机器的版本与快照；实际执行 clean install、启动、跨版本二进制升级与回退、四页可达、卸载；保存脚本、逐步日志和退出码、安装后文件/注册表状态、用户数据根安装前后的清单及哈希。签名须是实际 Authenticode 签名，并保存证书身份、时间戳和签名验证结果。现有 Gate 复评也指出此前回退只是改版本标签，完整跨版本矩阵与签名仍缺。[RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md:144-173](#)

**`INSTALLER-MATRIX-1`：建议转为 `closed_with_limitations`，完成证据与资源 closeout 后由 DSH 实际落状态。** 该卡范围是旧 sidecar 的机制验证，AC8 明确禁止据此宣称条件 4 通过；卡面 AC7 当前为 `NOT_RUN`，但 Gate 映射另称安装产物四页 5/5。关闭前应保留这项证据不一致，并先核对它是否对应同一安装包及 head；不能只据另一份 Review 将本卡 AC7 改成 `MET`。限制条目应写明：AC1–AC6 的实测范围、AC7 原始 `NOT_RUN`（除非完成证据对齐）、旧 sidecar、签名及跨版本升级/回退未证明，以及条件 4 仍不满足。[INSTALLER-MATRIX-1:6-8,35-60,66-73,75-104](#)；[RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md:155-167](#)

完整签名及真实矩阵超出这张旧 sidecar 机制卡的范围，应另立 `RELEASE-GATE4-SIGNED-MATRIX-1`，由 DSH 冻结范围并推进自动化。若执行环境或签名凭据不可用，记录 `NOT_RUN` 和具体缺项，不以模拟证据代替。

### 条件 5：人工 GT 与质量基线

**合成 GT 不可替代独立、人工产生的 GT，也不能支持识别或翻译准确率声明。** 它最多用于检查测试管线或格式，不是质量证据。若找到已有的独立人工标注数据，仍须核实代表性、来源、许可与输入/参考值的固定哈希；当前没有符合条件的数据，质量基线继续 `NOT_RUN`。[RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md:181-202](#)

按用户委托的书面裁决授权，我选择 Gate 条件原文允许的替代分支：**接受当前有边界限制**，边界为“没有代表性质量基线，不宣称翻译或识别准确率达标”。记录为 `LIMITATION_ACCEPTED`；实测基线仍是 `NOT_RUN`，不得改写成 PASS。现有一次模型/API 调用只能支持适配事实，不支持代表性质量结论。[RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md:181-198](#)

### 两张卡的状态建议

- **`INSTALLER-MATRIX-1`：`closed_with_limitations`**，按上文保留 AC 原状、证据差异和未满足项；完整签名/跨版本矩阵另立卡。
- **`MAINT-1-RELEASE-MONITOR`：保持 `in_progress`**。它被定义为长期维护节点，AC3 要求条件不足时保持 Gate 阻塞、不写 PASS；在其中追加上述裁定、每项下一步和停止条件即可，不要关闭监测伞位。[MAINT-1-RELEASE-MONITOR:6-11,42,46-49](#)
- 两卡 limitation 都要明确：条件 3 尚无 overlay 裁定证据；条件 4 的签名和完整真实矩阵未完成；条件 5 的质量基线仍 `NOT_RUN`，仅接受有边界限制。禁止据此将 `Technical Gate` 改为 `SATISFIED`。

## 需用户裁决清单

需用户裁决：是否将 `Technical Gate=NOT_SATISFIED` 改为 `SATISFIED`。本裁定不作此变更；在出现新的、明确针对 Gate 总体结论的用户裁决前，保持 `NOT_SATISFIED`。

除此之外，本次三组处置均在用户授予 Codex/ZCode 书面裁定的范围内，不需再询问用户。

## 边界声明

本次未修改文件、未运行测试。行号依据 GitHub `main` 上读取到的版本文档：`STATUS.md` `22b10bd0`、`09_COLLABORATION.md` `2e37a09d`、Gate 映射 Review `e854e915`、两张 Task 分别为 `c0b25dfc` 与 `6373833d`、维护卡 `8947a0b0`、安装矩阵卡 `402603e9`。本地 shell 无法启动，且 AGENTS.md 是用户直接粘贴的指令、未提供可核验行号；因此 AGENTS 授权依据按其“当前授权/角色与交付”段引用，具体 lifecycle 与责任边界同时引用了有行号的 `doc/09_COLLABORATION.md`。若本地文件与上述 `main` 快照不同，DSH 应在应用状态变更前核对本地行文。

**推荐下一步：**由 DSH 将本裁定作为 append-only 记录，按生命周期处置 CORE-ENV-2 和安装矩阵卡，保持 FEA11 卡阻塞并冻结最小错误映射实现卡；随后释放 `RELEASE-GATE4-SIGNED-MATRIX-1`，同时安排具名独立 Agent 对真实 F11 截图出书面视觉裁定。

---

## DSH 采纳（2026-11-17，Lead）

**采纳结论**：三组裁定全部采纳；唯一「需用户裁决」项（Gate 总体是否改 `SATISFIED`）维持现状 `NOT_SATISFIED`，不由 Agent 改判。

### 执行清单

1. **Q1 → 选 B**：`GIT-CLEAN-CORE-ENV-2` 收口为 `closed_with_limitations`；AC1–AC3 保持 `<<BLOCKED>>`、AC4 保持 `<<PARTIAL>>` 原字节；`approval: pending_variable_and_environment_freeze` 保留；reviewer 由已退出的 Antigravity 改派为**上下文独立子 agent**（本裁定不撤销 ACL 禁令）。
2. **Q2 → 选 A**：`FEA11-ENTRY-MISSING-1` **保持 `blocked`**（现卡 allowed_paths 无产品源码，不得在诊断卡里改代码）；另立一张 **`proposed`** 的最小实现卡（`MapMintFailure` 兜底保真：内部诊断保留内层异常类型，公共错误码/wire/Schema 不变；若必须改公共映射，先由 DSH 冻结契约范围）。
3. **Q3**：
   - **条件 3**：接受「委托书面视觉裁定」路径，但纯 headless 渲染/截图存在/像素 diff 单独不够；当前**无 F11 真实窗口截图证据** ⇒ 记为 `AGENT_ADJUDICATION_PENDING`（不再以「等人」为唯一动作）。
   - **条件 4**：脚本化矩阵可替代人工执行，但必须真实 Windows 环境 + 真实 Authenticode 签名；`INSTALLER-MATRIX-1` 收口为 `closed_with_limitations`（保留 AC7 原始 `NOT_RUN` 与证据不一致），完整签名/跨版本矩阵另立 `RELEASE-GATE4-SIGNED-MATRIX-1`（`proposed`）。
   - **条件 5**：合成 GT **不可**替代人工 GT；按 Gate 原文允许的替代分支登记 **`LIMITATION_ACCEPTED`** —— 边界为「没有代表性质量基线，不宣称翻译/识别准确率达标」，实测基线仍 `NOT_RUN`。
   - **`MAINT-1-RELEASE-MONITOR`**：保持 `in_progress`（长期维护节点），追加上述裁定与逐项下一步。
4. **禁止**：不把任何 `NOT_RUN` 写成 PASS、不改 `Technical Gate=NOT_SATISFIED`、不据此宣称条件 3/4/5 通过。
