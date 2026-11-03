# FEA-09 UNFREEZE 修订提案 r4（r3 + 增量修正；A/B 两包）

状态：**PROPOSAL r4 — 待第四次独立复核**（2026-11-04）
作者：DSH；依据：`doc/reviews/FEA-09-UNFREEZE-r3-review.md`（Codex 独立，`changes_requested` P0=0/P1=5/P2=1，reviewed_head `a7f636300`，SHA-256 `46f06092…`）。
**本文件相对 r3 的增量**：r4 只替换/新增下列条款；r3 其余条款继续有效。R2-003/R2-006/R2-007 已 CLOSED，不再改；R3-001…R3-006 逐项闭合如下。语义修订/重冻仍须第四次复核 approved 且 P0/P1=0。

## 0. R3 findings 处置

| ID | 处置 |
|---|---|
| R3-001 | 撤回"managed 专用 PageView 取代 get/list"；改为**保留现有 `Page` 契约**（可读行仍返回 Page），新增**降级行** `PageView` 与独立访问器；`get_page/list_pages` 返回 `Page | PageView`（referenced 可读行仍 Page）；PageView 的 `visibility_witness` 增加 `referenced` 值。 |
| R3-002 | 区分**纯投影**与**wire handler**：纯投影 `resource_ref=null`（未发布），只用于迁移/内部一致性；wire ReaderProjection 首次打开仍按既有行为 resolve/publish 可读页，仅不可读页进入 `unavailable_pages`；迁移回调禁 publish/resolve 不变。 |
| R3-003 | 加密 resolve 的授权不再要求 **import-bound grant live**；以 binding healthy + **fresh secret 签名 grant G** 的 scope/facts/locator 与 binding 一致为准；原 import grant 失效/撤销不影响已提交页的 R（但绑定必须 healthy）。 |
| R3-004 | 冻结 token→文件映射与 identity 来源：G.secret_ref.path 必须恰为 `<DataRoot>/host/source-secrets/<token>.bin`（token 正则；规范化/大小写/`..`/reparse 拒绝）；消费前 stat identity（volume/file id/size）→ 打开独占句柄 → 复验 identity → 同句柄读取/零填充/删除；不存在的路径绝不清理。 |
| R3-005 | 冻结计数与终止语义：仅"claim 后解密失败"计数；cache hit/取消/超时/授权失败不计数且不消费；冷却结束计数清零；claim 后取消：不计失败，密码变量清零、文件已删；claim 前取消：Core 不碰文件（Host 清理）；进程崩溃：启动孤儿清扫仅扫 `<DataRoot>/host/source-secrets/`。 |
| R3-006 | 修正下游影响表：删除目标集合沿用 C-04b 既有协议（软删/回收站页仍是目标），**不**以 V 为目标集合；内容摘要只统计可读页；A 载体明确 C-04b 无字节改动。 |

## A 包增量（I001）

### A4-1（替换 r3 A2 §4.4 第 1–3 段）

```text
Page（domain 实体）契约保持：仅承载数据完整且可读的 managed/referenced 页；
get_page/list_pages 返回 Page | PageView：
- Page：managed copy witness（完整列）或 artifact witness 且 original 可解析；referenced 行仍返回 Page（P8 完整）。
- PageView（降级只读投影）：仅当行 V=true 但无法构造 Page 时返回（managed artifact-only 缺列/thumbnail-only；或未来扩展的 referenced 降级），字段同 r3 §4.4 并：
  visibility_witness: 'artifact'|'copy'|'artifact+copy'|'referenced'
  source_mode: 'managed'|'referenced'
  resource_ref: str|null             -- 纯投影恒 null（未发布）；wire handler 填充
- 调用方不得把 PageView 强制转 Page；写路径只接受 Page；PageView 不接受 add/update/import 回写。
- 不得过滤 V 行：get_page(page_id) 对降级行返回 PageView；list_pages 返回混合序列（按 sort_order）。
```

### A4-2（替换 r3 A2 §4.2 reader 行 / A3 ReaderProjection 段）

```text
纯投影构建器（迁移/内部一致性用）：
  pages: [Page|PageView]（V 全集，按 sort_order）
  unavailable_pages: [{page_id, reason_code}]   -- 仅 R 不可得且无需 resolve 判定的页
  不发布、不解析资源、不写 last-used、不开新连接。
wire ReaderProjection（M2-C1 2.12-a）：
  pages[] 仍为可读页完整 DTO；首次打开时按既有 resolve_page_resource 行为解析/发布；
  resolve 返回 typed 失败的可读性缺失页 → 不进入 pages[]，进入新增可选 unavailable_pages[];
  unavailable_pages 仅含 V 真但 R 不可得页；排序按 sort_order；去重。
迁移断言 2 使用纯投影构建器，不使用 wire handler；破坏投影构建器必须验证失败。
```

### A4-3（替换 r3 D 表 C-04b 行）

```text
C-04b 删除预览/内容摘要：删除目标集合与保护披露沿用 C-04b 既有协议（含软删/回收站对象，不以 V 为目标集合）；内容摘要仅统计可读页；不可读 V 页在摘要中标注 unavailable，不改变删除事务语义。A 载体登记"无字节改动"依据。
```

## B 包增量（I005）

### B4-1（替换 r3 B1 验证顺序第 2 步）

```text
授权顺序（替换 2) import-bound grant live）：
  1) binding healthy（page_bindings.status='healthy'）
  2) fresh secret 签名 grant G live：G.session/generation/expiry 有效；G.secret_ref.token == payload.secret_token；
     G.scope 的 source_kind/container facts/entries 与 binding 的源/entry 一致（container digest+volume+file+locator/ordinal）
  3) 原 import-bound grant 无需 live（其职责是导入期绑定，已提交页的 R 由 fresh grant 授权）；但 binding→source/version/entry 必须存在且 digest 一致。
  4) G.secret_ref.path == <DataRoot>/host/source-secrets/<token>.bin（token 正则 [A-Za-z0-9_-]{22,64}；规范化绝对路径；拒绝 reparse/替换/大小写别名/..）
  5) 打开前 stat(volume/file id/size) → 打开独占句柄 → 复验 identity → 原子 claim token → 同句柄读取/零填充/删除
```

### B4-2（替换 r3 B1 一次性/准入段）

```text
- 原子性：claim 在锁内完成；claim 失败（重放/不匹配/路径非法）→ SOURCE_ACCESS_DENIED（retryable=false），不计数、不清理文件（Host 清理）。
- 准入：每 (page_id, accepted_source_version) 单飞 semaphore；排队请求在准入前不 claim、不计数。
- 计数：仅 claim 成功且解密返回 SOURCE_PASSWORD_INVALID 时 +1（原子）；连续 3 次 → 冷却 300s（第 3 次失败时间起算）；冷却结束计数清零；成功解密计数清零；cache hit 不改变计数；取消/超时/授权失败不计数。
- 终止分支：
  未 claim 的取消/超时/失败：Core 不读不删文件；Host 在响应/超时后删除自己的文件。
  已 claim 后取消/超时：Core 已读取并删除文件；密码变量清零；不计数。
  进程崩溃：启动时仅清扫 <DataRoot>/host/source-secrets/ 下符合 token 正则且超 TTL 的文件；不触碰其他路径。
- cache hit：不要求 token；若请求带 token，Core 不 claim、不消费（Host 响应后删除）；host 必须以 capability 为前提。
```

### B4-3（替换 r3 D 表其余行补充）

```text
C-08 快照：快照可含 V 真 R 不可得页；resource_ref=null + reason_code；快照守恒断言不变；A 载体登记。
C-09 备份/迁移：断言 5 资源门禁不变；备份字节不变；A 载体登记。
C-14 缓存/lease：rendition cache 边界不变；B 的 secret 消费不写 cache；登记。
导出：仅可读页；V 真 R 不可得页 typed skip（错误码既有）；FEA-14 消费方登记。
UI-1：unavailable 占位、密码重试/冷却、capability 缺失提示；不新增 C-07 方法。
M2-C1：A 定稿 2.12-a 字节为 B 基线；B 只改 ResolvePageRequest secret_token 与对应错误面；版本链唯一；各自单独指纹，不并入 17 pin。
```

## C. 冻结流程（沿用 r3 §C，补充）

- 语义修订提交后，除三指纹外，**新增文件级 diff 清单**（每契约文件 old/new blob ID）并写入载体；第四次复核 valid 后仅元数据冻结提交；最终状态行改动后重算最终 pin，同时保留语义提交指纹与旧 pin。
- A 完成冻结并落 M2-C1 2.12-a 指纹后，B 的语义提交必须基于该字节；两包不得并行改写 M2-C1。

## D. 测试矩阵增量

A：get/list 对可读行仍 Page、降级行 PageView（混合排序）；referenced 可读行仍 Page；PageView 不丢行、不返回 0 假尺寸；纯投影 resource_ref=null；wire 首次打开可读页正常 resolve/publish，unavailable_pages 仅 R 不可得；迁移纯投影 vs wire 边界。
B：授权不再依赖 import grant live（撤销后仍可 resolve？绑定 healthy + fresh grant）；token 路径正则/reparse/替换/大小写/../；claim 前取消/超时/拒绝的清理归属；claim 后取消/超时；冷却边界与并发准入；cache hit 带 token 不消费；崩溃孤儿清扫仅本目录；重放/跨页/跨源/跨版本。
