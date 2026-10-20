# DETECT-TILING-1 释放裁定（r34）

日期：2026-10-20  
裁定人：Codex（Lead / Architect / Integrator）  
只读基线：`001de58f69b370bb543ba69e4cf5726c77b26b11`  
基线工作区：dirty，存在大量既有修改及未跟踪文件；均属原作者，不纳入本裁定的改动。

## 裁定摘要

1. **批准立项方向：`DETECT-TILING-1` 应作为 Python Core 的独立 Task 提案。** 方案 B（提高 `MAX_DETECT_PIXELS`）否决；方案 C（调用方缩放）不作为 `core.detect` 的修复。方案 D 的必要补充是先证明解码器可在有界内存下读取超大 PNG/JPEG；不能把“裁 tile 后调用 provider”直接当作内存安全。
2. **范围收敛为 5 条 AC。** 必须包含边界重复控制。允许采用保守的 tile ownership / overlap 策略，但不能将重复 region 留作“以后再合并”后仍声称 P18 质量切片可用。
3. **`SEC-FMT-005` 与检测分块合并在同一 Task 作为同一个技术目标验收；但需逐字覆盖它的内存检查、处理策略和用户可理解警告要求。** 未覆盖全项就只能登记 `PARTIAL`，不能声称 SEC-FMT-005 已满足。
4. **建议 Owner：Antigravity；Reviewer：DSH。** 两者必须在实际释放记录中保持实现/审查分离。
5. **现在不重开 P18。** 先完成此 Task、解决 KO runtime 可行性/限制记录，再由 Codex 按授权和产品门槛状态决定是否重开 P18。

本文件是释放裁定与可执行 Task 草案，不会自行改变 `STATUS`、Plan 或创建/激活 Task。依项目治理，只有 Plan 明确激活、范围冻结且状态登记后方能派发实现；因此当前裁定为“方向批准，尚未释放”。

## 事实与风险核对

- `MAX_DETECT_PAGE_BYTES = 32 MiB`，`MAX_DETECT_PIXELS = MAX_DETECT_PAGE_BYTES // 3`，对应最多 `11,184,810` 个 RGB24 像素。`handle_detect` 在 `convert("RGB")` / `tobytes()` 前按全图像素数拒绝。
- 目标页 `2946×4167 = 12,275,982 px`，超过上限约 9.8%；现状是整页拒绝。该阈值表达的是单份 RGB24 帧缓冲的预算，不代表完整请求峰值（base64、编码字节、解码器内部缓冲和 tile/provider 缓冲）已受同一预算约束。
- Provider 接收原始 RGB 缓冲，provider `_validate_request` 的 byte-count gate 是第二道防线，应保持不变。因此 tile 划分、坐标偏移和结果汇总都在 handler/application 层完成。
- **关键实现风险**：只对 Pillow `Image` 做 `crop()` 后逐 tile `convert()`，不自动证明全图解码内存有界；若 Pillow 在首次像素访问时解码整张图，超大图仍可能分配全图像素缓存。Task 必须先实证选定解码方式的峰值内存行为；无法有界解码的输入必须在大分配前按明确上限拒绝并给出清晰错误。不能以 provider 每次只收到一块作为“不 OOM”证据。
- `SEC-FMT-005` 原文要求：对 `>10000×20000` 超大图检查可用物理内存，采取分块或尺寸限制，并给出清晰内存警告以防 OOM。现有 AC6 实测记录确认该安全测试不存在。仅保留固定像素阈值、或只覆盖约 12.3M px 真实页，都不等于满足 `>200M px` 场景。
- P18 复核记录：`ImportPages` 阻塞已解除；真实页仍受像素上限阻塞；`manga_ocr` 可导入，`paddleocr` / `paddle` 缺失，KO 链路仅部分解除。

## 五项问题裁决

### 5.1 是否立项及替代方案

**立项：是。** 一项 handler 层资源管理改动可以同时服务 P18 的真实页检测消费链与 AC6 的超大图安全要求，合并后能避免两套相互矛盾的限图规则。

- **方案 A：有条件批准。** 必须采用内存有界解码/扫描实现，或采用经验证的安全尺寸上限并在超限时清晰失败。若超大图实际要求成功检测，则选择前者；若解码库无法做到有界处理，可先将 `>10000×20000` 定义为安全拒绝并给出清晰警告，SEC-FMT-005 可以按“适当限制最大处理尺寸”验收，但不能把该拒绝说成 tiling 成功，也不能满足 P18 真实页直到该页确实通过。
- **方案 B：否决。** 调大常量直接扩大 RGB 帧预算，与原 32 MiB 保护目标冲突；也不能证明更大尺寸下完整解码峰值安全。
- **方案 C：不采纳为 `core.detect` 修复。** 调用方预缩放会改变检测输入及小字召回，且需改调用方宽高/图像一致性契约；这是产品质量和接口决策，超出此 Task。不得绕过 handler 的宽高一致性检查。
- **方案 D：增加解码内存模型与拒绝路径。** 在实现前验证 Pillow/其他已允许依赖的 PNG/JPEG 解码是否能有界读块；若不能，明确选择并验证安全上限、错误类型及错误信息。不要新增依赖，除非先另行授权。

### 5.2 AC 数量及边界去重

7 条草案可收敛为下方 5 条。将真实页与普通页对照放同一 AC；将白名单/输入语义与阈值不变并入契约安全 AC；将固定 head 独立 Review 与所有证据归入交付 AC。

边界合并不应延期到后续 Task：若相邻 tile 重复返回同一文本框，会污染 region 数量和 P18 质量评测；若无证据地删除候选，又可能造成漏检。建议优先采用**带 overlap 的 tile + 确定性归属**：每个 tile 有 core ownership 区与 context overlap，按候选中心点归属唯一 tile；中心落在 overlap 的边界情形使用固定 tie-break（如左上到右下 tile 顺序），并在同一 tile 内保留全部候选。若现有模型的检测框中心不适合作唯一归属，则另设基于 polygon IoU 的跨 tile 去重，阈值必须通过合成跨边界 fixture 校准后冻结。验收需证明重复候选被抑制且跨边界完整框不丢；具体算法由 Owner 提案、Reviewer 复核，不能仅留在证据说明里而无测试。

### 5.3 与 `SEC-FMT-005` 的关系

并入 `DETECT-TILING-1`，作为其“超大输入内存安全”验收；Task 记录与 AC6 的追溯关系。**原文不宜不加改写地当作一个单独 checkbox**，因为它混合了机制、策略与结果。应拆成可测条件，合并写入一个 AC：读取/解码前检查可用内存或使用等效的硬上界策略；以 `>10000×20000` 图像验证安全处理或安全拒绝；用户可读错误/警告明确说明限制/可行操作；测量进程峰值内存或其他可重复指标证明不会尝试超预算全图分配。这里“可用物理内存检查”不能由固定常量推定；若实现采用适当尺寸限制替代，应在 AC6 对照记录中说明它满足原文允许的第二条路径及边界。

### 5.4 Owner / Reviewer

- Owner：**Antigravity**，符合 AGENTS.md 对通用 Python / 应用 / 测试实现的分工。Task 范围冻结前不得派发。
- Reviewer：**DSH**，前提是 DSH 不参与实现，且 review 固定 `delivery_head`。DSH 为当前 coordinator 并不自动使其失去独立技术审查资格；若实际 DSH 参与实现，则改由 Antigravity 与另一未实现者互换角色，不能自审。
- Codex 保留 Task 释放、契约范围判断及集成裁定职责。Qoder 不得作为 Owner 或 Reviewer。

### 5.5 P18 和 Python 3.14 KO 可行性

**Tiling 只解除真实页在 `core.detect` 的尺寸阻塞，不会单独解开 P18。** P18 AC2 的质量门槛仍需用户裁决；KO detector 的权重/runtime 缺口也仍在。因此即使 DETECT-TILING-1 完成，也不能直接重开一个明知无法完整跑通的 P18 切片。

本机当前 Python 为 `3.14.6`。截至本裁定查阅的官方资料：PaddleOCR 文档称其 Python 包支持 Python 3.8+；但 PyPI 当前 `paddlepaddle 3.3.1` 的 Windows wheel 列表最高到 CPython 3.13，没有 `cp314-win_amd64`。因此在本机 Python 3.14 上，**PaddleOCR Python 包本身可能可装，但官方 PaddlePaddle runtime wheel 不可用**。这足以判定“直接在当前 3.14 环境安装完整 `paddleocr` + `paddle` 本机链路”当前没有受支持 wheel 路径；若仍要继续，应先做独立兼容性实验（例如项目允许的其他 Python 版本/隔离运行环境），同时核对 P18 冻结 runtime 契约，不能直接换应用运行时。

若项目指定运行时固定为 Python 3.14，且兼容性实验确认没有支持的 Paddle runtime，则 P18 KO 可登记为 `LIMITATION / BLOCKED_BY_UPSTREAM_RUNTIME_SUPPORT`，停止无期限等待，不可宣称 KO 质量 AC 通过。若允许独立兼容 Python runtime，则先立范围明确的可行性验证 Task；本轮不授权安装依赖或变更 runtime。

参考： [PaddleOCR 安装文档](https://www.paddleocr.ai/main/en/version3.x/installation.html)；[PyPI PaddlePaddle 发布文件](https://pypi.org/project/paddlepaddle/)。

## 建议冻结的 Task 元数据与 AC

```yaml
task_id: DETECT-TILING-1
status: proposed
language: zh-CN
parent: ARCH-DOC-REBASELINE
base_commit: 001de58f69b370bb543ba69e4cf5726c77b26b11
owner: Antigravity
reviewer: DSH
```

`parent` 选 `ARCH-DOC-REBASELINE`，因为本 Task 同时承接它的 AC5 消费链（经 P18 AC5）和 AC6 的 SEC-FMT-005；P18 是下游消费者，不是唯一父任务。释放时须复核 base 和 dirty 状态，不得把当前 dirty 工作区内容误当成该 commit 已包含的基线。建议 Task 自身在实现前核实 fixture 的许可、来源与 hash；若用户指定的 `2946×4167` 页无法提供，AC 不可用其它图替代并声称通过。

### AC1 — 有界解码与分块坐标

超出单帧 `MAX_DETECT_PIXELS` 的 PNG/JPEG 按明确 tile 几何处理；证明解码器不会先分配无界全页 RGB buffer，且每次 provider 请求的原始缓冲不超过 `MAX_DETECT_PIXELS × 3` bytes。保持 provider byte-count gate 不变。tile 结果按偏移映射回整页坐标，输出 shape、坐标范围及异常输入行为均有测试。

### AC2 — 重叠边界结果唯一且不漏

固定 tile overlap 与跨 tile 归属/去重规则；相同文本块不得重复进入最终 `candidates`，跨边界文本块不得因归属规则丢失。使用可复现合成框及边界位置 fixture 覆盖重叠、相邻、不相交和 tie-break；证据说明参数选择依据。规则须确定性。

### AC3 — 32 MiB 契约与输入语义不变

`MAX_DETECT_PAGE_BYTES`、`MAX_DETECT_PIXELS` 数值不变；PNG/JPEG 白名单、base64 严格校验、编码字节上限、正整数 width/height 与解码尺寸一致性保持原语义。正常页走单次 provider 检测，候选结果与基线逐项一致；不得经调用方缩放绕过尺寸/宽高校验。

### AC4 — 真实页和普通页对照

用被拒的 `2946×4167` 页实测成功输出整页坐标 region 集；保存来源/许可、文件 hash、Provider/runtime/模型及权重版本/hash、tile 参数、峰值内存和原始结果证据。与一张冻结的正常页比较修改前后结果，证明正常页仍走等价路径且结果逐项一致。真实样本缺失时标 `BLOCKED`，不得用合成图替代。

### AC5 — SEC-FMT-005 超大图安全、回归与独立审查

对 `>10000×20000` PNG/JPEG 验证有界分块成功，或在全图解码前按明示尺寸/可用内存策略安全拒绝；不得 OOM。拒绝时给调用方明确的用户可读限制/警告。记录峰值内存与测试环境，并把结果映射到 SEC-FMT-005 原文各子要求。全部既有 `core.detect` 测试通过，新增测试覆盖格式白名单、base64、宽高不一致和像素边界。固定 `delivery_head`，由未实现者 Review，提交 findings 与处理结果。

## 范围裁定

保留允许范围的窄化版本：

- `src/bootstrap/core_service.py`（handler 及相邻注释；不改常量值）
- 新增就近 detection tiling/decoder 模块（路径在 Task 冻结时确定）
- `tests/**` 中与本 Task 直接相关的用例
- `verification/DETECT-TILING-1/**`

禁止改 `ports.detection` 契约/provider byte gate、两项上限常量、调用方缩放契约、无关安全测试、依赖及 Python runtime。若安全实现必须改共享接口、增加依赖或更换 runtime，暂停并另行裁定。

## 释放前 Gate 与推荐下一步

1. Codex 在治理允许时新建 Task 并登记 Plan/STATUS：确认当前唯一 coordinator、依赖、`base_commit`、branch/worktree、allowed paths；dirty 主 checkout 不作为 Owner 工作区。
2. Owner 在编码前提交一页解码/内存策略说明：对 PNG 与 JPEG 分别说明是否会全图解码、tile 生成如何避免全页缓冲、所有主要同时存活缓冲的上界，以及超上限失败路径。Reviewer 先审此策略；若不能证明有界，先做解码可行性研究或收紧为安全尺寸拒绝，不能开始宣称 tiling 满足 AC。
3. 确认 `2946×4167` 原始样本可合法使用并能在隔离工作区提供；否则 AC4 为 BLOCKED。
4. 独立完成 Python 3.14/PaddlePaddle runtime 可行性验证。当前官方 wheel 证据不支持 cp314；根据验证结论，要么评估获批的隔离兼容环境，要么将 P18 KO limitation 固定记录。
5. DETECT-TILING-1 交付后，Codex 先集成与核验 SEC-FMT-005 覆盖，再结合用户对 P18 产品门槛的裁决决定是否重开 P18。ARCH-DOC-REBASELINE AC4/AC5/AC6 当前 PARTIAL 状态不因本裁定自动变化。

**建议下一步：**Codex 完成 Task/Plan/STATUS 的正式释放冻结；Owner Antigravity，Reviewer DSH，依赖为 AC2 产品门槛裁决不阻断检测安全实现本身，但 P18 重新启动前必须具备用户裁决。可转发给 Antigravity 的任务指令应在正式释放后生成，复用本文件的 AC、base 和 scope；本裁定当前不等于该指令已派发。
