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

## L2 终局（2026-11-14，DSH 收口）

**结果：`BLOCKED`（性质＝环境资源缺失），已按止损条件挂起。**

三条路线全部走到终点，均无翻译产出（`regions_translated_differs = 0`）：

| 路线 | 命令 + scope | 终局 | 卡点 |
|---|---|---|---|
| 1 | `translate_untranslated` + **book** | `completed_with_failures`，8/8 failed | `detect` / `PROVIDER_NOT_CONFIGURED`（`manga-ocr` 只覆盖 OCR，无 detect 绑定） |
| 2 | `retranslate_region` + **region** | `blocked` | planning 门，**无 error_code**（`step_status={}`、`blocked_reasons=[]`） |
| 3 | `translate_all` + **page** | `completed_with_failures`，1/1 failed | `ocr` / `PROVIDER_NOT_CONFIGURED`（本地 `manga-ocr` 需 ONNX 模型，仓库与工作区**均无**） |

**已排除的 6 项假设**：sidecar 缺模型（已改源码 Core）、fixture 污染（每轮新建根）、Host/探针 payload 形状、协议 minor/字段错位、凭据无效（DeepSeek 探测 HTTP 200）、装配期 profile 缺失（`RUN_SNAPSHOT_INCOMPLETE` 已解）。

**未证明的**：Core → provider → 落库的端到端翻译。**它不影响产品可用性，只影响 Gate 条件 5 的措辞。**

### 解除 BLOCKED 所需条件（任一）

- **D**：提供 `manga-ocr`（或任一 OCR）ONNX 模型文件并放到 Core 可解析的位置 → 路线 3 可走通（page 已有 region，可跳过 detect）；
- **E**：配置远程视觉/OCR provider（如 GLM-4V）→ 同时替代 detect/ocr。

### 沉淀（后续可复用，不因 BLOCKED 而失效）

1. 源码 Core 入口：`python -m bootstrap.core_service`，需 `cwd=<repo>/src` + `PYTHONPATH=<repo>/src`；`core.ping` protocol 2.3 ready。
2. fixture `v6 → v14` 迁移无损（自动备份 ~4.0 MB verified），迁移后计数不变。
3. **装配期 provider 约束（实测）**：provider 在装配期一次性构建；只在 `StartRun.overrides` 塞 profile **不生效**（`base_url="" / model="" / credential_ref=None` → `RUN_SNAPSHOT_INCOMPLETE`）；**必须先写 `pipeline_defaults` 再启动 Core**。
4. region seed 的产品 API 路径：`editing.create_region` → `apply_ocr_result`（勿用 `save_manual_translation`，会触发 manual 保护导致 skipped）。
5. 证据：`verification/L2-CORE-E2E/`（README §8–§10，含 VERIFIED/INFERRED 分层与 `key_present`）。

### L2 路线 E 终局（2026-11-14，DSH 收口）—— 失败性质已精确到产品缺陷

路线 E（把 `ocr` 改绑**远程**视觉 provider GLM-4V，绕开本地 ONNX 依赖）**仍未取得产出**，但把失败从「缺模型」推进到「**Core 侧缺陷**」：

- **决定性证据**：进程内核对 `create_run` 后的 `run.provider_binding_snapshot["ocr"]`，其中是**完整合法**的 replay 配置 —— `provider_id: glm-vision-ocr`、`execution: { provider_id: openai-vision-ocr, provider_type: openai-compatible-vision, base_url: https://open.bigmodel.cn/api/paas/v4, model: glm-4v-flash, credential_ref, adapter_version, network_profile }`、`execution_digest: sha256:0c582839…`（合法）。
- **而执行期该 step 仍报 `PROVIDER_NOT_CONFIGURED`**。三种绑定形状均复现：

| # | ocr 绑定 | 结果 |
|---|---|---|
| E-1 | 用户 profile id `glm-vision-ocr`（type=openai-compatible-vision） | `ocr / PROVIDER_NOT_CONFIGURED` |
| E-2 | 固定注册槽 `openai-vision-ocr`（同时误删 translate profile → `RUN_SNAPSHOT_INCOMPLETE`，已排除为操作失误） | 不可用 |
| E-3 | 固定注册槽 + 保留 translate profile（**正确形状**） | StartRun 通过，**仍** `ocr / PROVIDER_NOT_CONFIGURED` |

- **新排除 5 项**：ocr 绑定缺失（快照证明存在）、槽位 id 写错（E-3 同样失败）、translate 被 profile 段覆盖（E-3 两者并存）、GLM key 未落 vault（cmdkey 成功 + `key_present: true`）、区域缺失（同页 2 region 已 seed、page scope 展开成功）。
- **结论**：**不是配置形状问题**（形状已被冻结快照证明合法），而是 **Core 侧 vision provider 的就绪/解析判定**未接受该配置。候选根因：`requirements` 的 endpoint/credential 校验、`resolve_for_run` 对 profile-id vs 槽 id 的比较、或 vision provider 需要 detect 前置。**属产品缺陷，需要独立诊断卡**。

**L2 最终状态：`BLOCKED`（性质＝Core 侧 vision provider 解析缺口）。** 三条 scope 路线 + 路线 E 共四次尝试全部穷尽，不再是「环境缺资源」能解释的。