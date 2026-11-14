# FEA 收口后路线（2026-11-14）

基线：`main` @ `73a182a61`。FEA 线 DoD v2 已达成；本路线处理「FEA 之后还剩什么、按什么顺序做」。

## 已完成（不再重复）

- FEA 线 DoD 五条（`MAINT-1-FEA-LINE-CLOSEOUT-v2-2026-11-14.md`）
- 4A/4B（查看对照）+ C1 八项（`MAINT-2-C1-BATCH-1` closed）
- provider 两条路径真实调用（翻译 DeepSeek / 视觉 OCR GLM）
- 自动翻译可行性评估（`MAINT-1-AUTO-TRANSLATE-FEASIBILITY-2026-11-14.md`，结论：零 UNFREEZE）

## 剩余四条线

| 线 | 内容 | 价值 | 成本 | 阻塞 |
|---|---|---|---|---|
| **L1 自动翻译功能** | T-A 配置桥 → T-B 运行路径 → T-C 入口文案 | **高**（用户可见功能 + 解锁 Gate 条件 5 端到端） | 中（T-A 4–6 文件） | G3 `INVALID_REQUEST` 未定位 |
| **L2 Core 端到端验证** | 改探针直驱源码 Core + 干净 8 页 fixture | 中（把「provider 已验」推到「落库已验」） | 低–中 | 需重建 fixture |
| **L3 Gate 条件 6** | 当前 head 的独立最终 Review | 中（收口证明，无新代码） | **低**（纯复核） | 无 |
| **L4 Gate 条件 1/2/5** | 7 项 finding / 远端可见性 / 质量基线 | 高（解锁 Gate） | 高 | 1 需逐项实现、2 需远端访问、5 需人工 GT |

## 优先级与理由

1. **L3 立刻做**：零代码、零风险、能确认「已完成的收口是真的」。若 L3 发现问题，L1 的返工成本会上升，所以先做。
2. **L1 先 T-A**：这是自动翻译唯一的「必做新代码」，且不触契约。T-A 完成后 L2 才有意义（配置桥通了，探针才能拿到真实 binding）。
3. **L2 在 T-A 之后**：探针直驱源码 Core 绕开 sidecar 缺模型的问题；干净 fixture 可从 `BOOK-FIXTURE-1` 私有副本重建。
4. **L4 只做能做的部分**：finding 逐项裁决（可做）；远端可见性调查与质量基线（需用户资源，登记不推进）。

## 分阶段

### 阶段 1（当前）
- L3：派独立上下文做 Gate 条件 6 复核（覆盖：三指针、Canonical Evidence、limitation 登记、门禁、Commit 与证据一致）
- L1-T-A：释放 `TRANS-BINDING-BRIDGE` 卡并实现（Core 内把 P15 profile/binding 镜像进 `settings["providers"]["profiles"]`，只含 `credential_ref`，fail-closed，复用 `save_settings_section` seam）

### 阶段 2
- L1-T-B：修 `library_start_run` 的 `INVALID_REQUEST`；`RunBindingDefaults` 扩为「ocr + translate（有配置时）」
- L2：探针直驱源码 Core + 干净 fixture，拿 Core 端到端翻译产出

### 阶段 3
- L1-T-C：工作台「开始处理」补 provider 前置门 + 四类错误文案
- L4 的 finding 逐项裁决

### 阶段 4（依赖用户）
- L4 的远端可见性、质量基线、clean install 矩阵

## 每阶段的门禁

- 四件套：`check.ps1`（默认 + TaskPath）、`verify_pins`、`generate_api_inventory --check`、受影响测试
- 独立 Review（未参与实现的上下文）
- 状态先证据后翻转

## 预算约束

`doc/REBASELINE_PLAN.md` 6964/7000（余 36 B）。阶段 1 只能登记**一张**卡；后续卡需先压缩 PLAN 或并入表外节点行。
