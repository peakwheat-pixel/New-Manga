# CONTRACT-UNFREEZE-2026-11-04（C-05 v1.2 / C-15 v1.1 / C-16 v1.1）

状态：**FROZEN 已执行（2026-11-04）**
作者：DSH（Lead / Architect / Integrator）
依据：实现 Review r1 R1-I001/R1-I005；I001 独立裁决（方案 B，`doc/reviews/FEA-09-I001-adjudication.md`）；UNFREEZE 提案链 r1–r15（`doc/reviews/FEA-09-UNFREEZE-r*-amendments.md`）；UNFREEZE r15 独立复核 **approved**（`doc/reviews/FEA-09-UNFREEZE-r15-review.md`，ZCode 故障转移复核，P0=0/P1=0/P2=1）；已提交字节独立复核 **approved**（ZCode 两次：`sess_1517188b-38c0-4310-9c92-1a71575a5826` 首次 changes_requested P1×1/P2×1 → 补正提交 → `sess_f155bf21-4fb4-4770-91ce-c1b9fa63e9ae` approved P0/P1/P2=0）。

**历史载体保留**：`doc/reviews/CONTRACT-UNFREEZE-2026-11-03.md` 原字节不变（v1.1 期记录）。

---

## 1. 语义修订提交（复核字节）

| 项 | 值 |
|---|---|
| 语义修订提交 1 | `ed570681b57e1343cb8c477f5dd7d23200a2dab4`（三契约正文） |
| 语义修订提交 2（补正） | `a9276fbaeeb7dd9fa85569910dfe314ee45bbff0`（C-15 §4.2 reader 恢复算法/offset 规范引用 + 版本引用；仅 2 文件） |
| 复核对象 | 上述提交后的已提交字节（与工作树一致，审查时 clean） |

| 契约 | 文件 | 旧版本 | 旧 pin（保留） | 复核字节 sha256（semantic HEAD） | 语义 blob（复核时） |
|---|---|---|---|---|---|
| C-05 | `doc/plan/FEA-C05_PAGE_VISIBILITY_DRAFT.md` | v1.1 | `a234346fb0eec2304c598024740bd0c26eea18117dde6dae5b49410192d58e82` | `284ce9552e4d569e67bc885386c316b5c40c971e2eb33b578abfeec5429357e7` | `52d09aad4dd2aa5a92f1038ac5f61dcb491ba74b` |
| C-15 | `doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md` | v1.0 | `6da686178f4d2e739906938e2bbcfbb57c9d59f3836e17c80c8764b477cd91bc` | `6b93a3683c85771c897ee56531287f8e16f284020d5af7185fbf14e4774c02f9` | `e3011e60bf8797a1e2bbc1a0603433091a115f12` |
| C-16 | `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` | v1.0 | `6e7f8d3d7a81c3588a8db1878579e4b1f4fd5330e4bbbab54e5ff5165afa1b0f` | `b0adc6538a33d4e64bcc290e297ed1484b2d58aa66eb03cedf346b35cf01b0ee` | `aed15820ea75625ac2d8eca6f5198645f667b681` |

## 2. 冻结字节（§1A pin 口径）

| 契约 | 冻结版本 | sha256（工作树，verify_pins 口径） | git hash-object（blob id） |
|---|---|---|---|
| C-05 | **v1.2** | `f6e6f3cb1fe19b253688f14ddf55f106b8bb89d3d3ab946a185cc12c34dc4714` | `32d039c0e8d10063076ecded1b333a4f4a512ab6` |
| C-15 | **v1.1** | `d8c0a3bcfc21229bff8f6feb6853866cdea7dc902b76f1ae45b0d374ce6579d6` | `a0286bac06aa89587a6a7cbcf08461aae8add865` |
| C-16 | **v1.1** | `0b9511a55ea15fafdc2de7d33fb204e5c7e2cf2efed69977ee6dd092f22e5905` | `bd36fc19c0c54df469c7dfe68ee824f6af531b17` |

## 3. §1B 冻结字节 vs 复核字节

| 契约 | 复核字节（semantic HEAD） | 冻结字节（本载体） | 差异 |
|---|---|---|---|
| C-05 | `284ce955…` | `f6e6f3cb…` | **仅状态行**（`UNFREEZE v1.2 候审` → `FROZEN v1.2` + 载体/冻结记录/复核标识）；条款字节=复核字节 |
| C-15 | `6b93a368…` | `d8c0a3bc…` | **仅状态行**（同上，v1.1）；条款字节=复核字节 |
| C-16 | `b0adc653…` | `0b9511a5…` | **仅状态行**（同上，v1.1）；条款字节=复核字节 |

- 冻结提交**不含条款编辑**；agent 复核链已覆盖条款字节。
- 历史 pin 与原 Review 字节保留；本载体不静默替换历史证据。

## 4. M2-C1（无字节变更登记）

| 项 | 值 |
|---|---|
| 文件 | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` |
| 当前版本 | rev 2.11（2026-10-19，P09-AC3-DELETE-HARDEN-1 AC1） |
| 语义提交范围核验 | `git diff --stat ed570681b^ a9276fbae -- doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` 为空（无 diff） |
| 行为兼容依据 | resolve 请求/响应仍 `{page_id}` → `{resource_id, revision}`；ReaderProjection/`initial_position`/`scroll_offset_y` 字节不变；managed 页 `page-original-*` 稳定键/first-publish-wins 不变；reader 恢复规则为既有 M2-C1 §6.3 语义的实现口径（引用而非修订）；`PROTOCOL_MINOR` 不 bump |
| 17 pins 覆盖 | **不覆盖 M2-C1**；本表单独登记，不声称 17/17 为其背书 |

## 5. 修订内容（r15 最终最小包摘要）

- **C-05 v1.2**：§3.1 managed `V=V_artifact ∨ V_copy_original`、witness 独立、V/R 分离、反例矩阵 1–8、参考投影形状；§3.2/§5 同步；P1–P5/P7/P8 原字节保留。
- **C-15 v1.1**：§1 正尺寸基线 + union 守恒断言（同事务连接/固定 t/三路径/非空禁跳 verifier/破坏必失败）、§4.1 V、§4.2 五读路径（V 行不丢/managed 资源选择与不可变/reader 恢复算法与 offset 规范引用 M2-C1 §6.3）、§4.3、§4.4 只读投影最小集、§0/§7 依赖与版本引用。
- **C-16 v1.1**：§0 `source.resolve-secret/1`；§3.1 resolve 加密源 fresh-grant 密码通道（**resolve wire 字节不变**，token 无 path，一次性/路径/清理/零泄漏，0/≥2 Secret-G typed）；§6/§10 同步。
- 实现设计委托（不冻结）：`doc/handoffs/FEA-09-impl-design-I001-I005.md`。

## 6. 冻结后

1. `verify_pins.ps1` 17/17 PASS（新 pin：C05/C15/C16 已写入 FROZEN 记录）；`check.ps1` PASS。
2. 释放 R1-I001/R1-I005 实现（Task FEA-09）；实现 Review 独立校验契约不变量 + impl-design + 测试矩阵。
3. 旧载体/旧 pin/历史 Review 原字节保留；后续修改必须重新 UNFREEZE。

## 7. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-04 | 建立：C-05 v1.2/C-15 v1.1/C-16 v1.1 UNFREEZE；r1–r15 复核链 + 已提交字节两次复核；冻结 pin 与 §1B；M2-C1 无字节变更登记 | DSH |
