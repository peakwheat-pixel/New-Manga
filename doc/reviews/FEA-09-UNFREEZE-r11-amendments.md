# FEA-09 UNFREEZE 修订提案 r11（最终最小包：无 wire 变更）

状态：**PROPOSAL r11 — 待独立复核（bounded scope）**（2026-11-04）
作者：DSH（Lead / Architect / Integrator）；依据：r1–r10 复核链结论与 DSH 架构裁决。
**核心裁决**：去除 r1–r10 中所有 **wire/DTO/内部算法** 契约变更，回到**最小语义修订**：
- **不新增/不改变任何 wire 请求/响应字段**（M2-C1 字节不因本包改变）；
- **不新增 Reader DTO 字段、不改变 initial_position**；
- resolve 加密源通过 **Host fresh-grant 协议**实现，`resolve_page_resource` 请求字节不变；
- 内部选择算法/错误优先级/状态机实现 = impl-design + 独立实现 Review。

本包只冻结以下 3 处语义 + 1 个能力名：

## 1. C-05 v1.2（语义修订，最小）

**§3.1 整体替换**（P1–P5/P7/P8 原字节保留）：

```text
V(p,t) ≡ (source_mode='managed' ∧ (V_artifact(p,t) ∨ V_copy_original(p,t)))
       ∨ (source_mode='referenced' ∧ V_ref(p,t))
V_artifact = 原 P1–P5（artifact/revision；不看 pages 尺寸/完整性/created_at）
V_copy_original = P1 ∧ integrity_status='complete' ∧ source_hash/managed_original_ref 非空
                  ∧ width>0 ∧ height>0 ∧ pages.created_at<=t
V_ref = 现有分支（字节不变）
不变量：① witness 独立（任一真即 V，另一失败不否定）；② V≠R（V 真不保证可读）；
③ V 真但 R 失败必须 typed，不得静默删除/隐藏该行；④ referenced 不得经 managed 分支。
```

- §3.2 表与 §5 失败语义同步（artifact 失败行仅描述 V_artifact）；§8 变更记录 v1.2。
- **不冻结**：best-artifact 选择算法、投影 SQL、PageView 字段/端口、Reader 呈现细节。

## 2. C-15 v1.1（迁移/读路径语义，最小）

1. **迁移**：旧正尺寸基线 `_LEGACY_COMPLETE_WHERE_POSITIVE`；v7 回填改用该谓词（v7 未发布，版本号不变）；断言：
   - 1：旧正尺寸 complete 集合 = 迁移后 managed `is_complete_page` 集合；NULL/零/负尺寸行保持 incomplete 并入恢复清单；
   - 2：expected = 旧 artifact 集合 ∪ 旧正尺寸 copy 集合（固定 t/父级/顺序）；分支各自守恒；同一迁移事务连接、固定 t；核验 get/list/纯查询投影三路径；非空资源禁跳 verifier；破坏 SQL/投影必失败；禁止迁回调调用 wire resolve/publish；
   - 3：旧正尺寸 complete 无 artifact 页保持 complete；未删/父未删/created_at<=t 时经 copy witness 可见；软删/未来时间仍不可见；
   - 5：资源对象 = 合格 original revision managed_path 否则 managed_original_ref；无路径/缺失/不可读 → `SOURCE_MIGRATION_RESOURCE_UNVERIFIED`；不得隐藏 V 页。
2. **读路径**：get/list 必须可见 V 全集（可完整构造行保持既有 Page 契约；不可构造但 V 真行以只读投影可观察，最低字段：page_id/chapter_id/source_mode/sort_order/witness ∈ {artifact,copy,artifact+copy,referenced}/original_available/source_hash?/original_ref?/width_px?/height_px?/integrity_status；空值 NULL；禁非 original hash 冒充；禁写回/伪造 provenance；未知 ID None）。
3. **Reader 边界（无 wire 变更）**：`GetReaderProjection` 字节不变，pages[] 仅可含正尺寸可读页；V 真但 R 不可读页**不进入 reader wire**（既有 M2-C1 DTO 不扩字段），由管理/诊断读路径（get/list 投影）暴露；reader 请求遇到不可读页时跳过该页并在既有错误面内返回可读部分（不新增字段/错误码）。UI-1 的"不可读提示"用管理读路径数据，不经 reader wire 扩展。
4. **managed resolve 选择**：M2-C1 **请求/响应字节不变**；仅内部资源选择：合格 current original revision managed_path → 否则 `pages.managed_original_ref`；都不可得 → 既有 `PAGE_NOT_FOUND`/内部错误 typed；不改变 `page-original-{page_id}` 键语义与 first-publish-wins；资源不可变（同键已发布摘要变化 → 不替换、typed 冲突），文件缺失自愈仍先比较记录摘要。
5. §4.1 V=C-05 v1.2；§4.3 同步"incomplete 且有合格 artifact witness 时按 V_artifact 可见"；变更记录 v1.1。

## 3. C-16 v1.1（resolve 密码通道；无 wire 变更）

**新能力名**：`source.resolve-secret/1`（core.ping capabilities 追加；Host 在创建 secret 前检查；缺失/探测异常 → `CORE_CAPABILITY_MISSING`，不创建文件；旧 Core 无该能力 → Host 拒绝加密 resolve，加密页读 typed REQUIRED）。

**协议（冻结）**：
```text
1) Host 每次加密 referenced 页 resolve 前：
   a. revoke 上一 secret grant（若存在），确保最多一个；
   b. 生成 token [A-Za-z0-9_-]{22,64}，写 <DataRoot>/host/source-secrets/<token>.bin（"NMSSR1\0"+DPAPI，私有 ACL，原子创建，TTL<=300s 且<=单次请求）；
   c. 用既有 RegisterSourceReadGrant 注册恰好一个 fresh grant：scope/roots/facts/entries 与页 binding 的源一致；secret_ref={token,path,expires_at}。
2) 调 resolve_page_resource {page_id}（**请求字节不变**）。
3) Core：binding healthy；存在 live grant 的 scope 与 binding 的 source/version/entry/rendition 一致（Auth）；对加密页还要求**恰好一个** live grant 带 secret_ref 且其 scope 与 binding 一致（Secret-G）：
   - 0 个 → SOURCE_PASSWORD_REQUIRED；>=2 个 → SOURCE_ACCESS_DENIED；
   - 路径必须规范位于 Host 私有秘密目录、祖先无 reparse、普通文件、独占同句柄读取→零填充→删除；未验证路径不得读取/清理；
   - 一次性消费；重放/多义拒绝；cache 命中不要求 Secret-G/不消费 token（但 Auth 必须成立）；
   - 成功/失败/超时清理：Core 只清理已验证并消费对象；Host 负责超时/取消侧删除与启动孤儿回收（仅本目录 token 模式+TTL）。
4) 错误码复用 C-16 §6 既有映射（grant 过期→SOURCE_GRANT_EXPIRED；token/secret 缺失或过期→SOURCE_PASSWORD_REQUIRED；DPAPI/口令错误→SOURCE_PASSWORD_INVALID；撤销/多义→SOURCE_ACCESS_DENIED 等）；**不新增码**。
5) 密码/token/path 零泄漏（wire log/NDJSON/日志/receipt/UI/证据）；PDF raster 密码接缝；AES ZIP 仍 unsupported。
```
- §3 追加本协议、§6 引用既有错误码、§10 变更记录 v1.1。
- **不冻结**：内部候选选择函数、错误检查代码顺序、锁/句柄 API（委托 impl-design；实现 Review 验证"同输入唯一 + 不变量"）。

## 4. M2-C1（无字节变更）

- 本包**不修改** M2-C1 请求/响应/DTO；仅登记内部资源选择回退（artifact revision → managed_original_ref）为实现口径，`page-original-{page_id}`/first-publish-wins/错误面不变。
- 因此无需 M2-C1 amendment；若实现 Review 认定影响 wire 语义，再单独立项。

## 5. 实现设计委托与验证

- `doc/handoffs/FEA-09-impl-design-I001-I005.md` 承载：Page/只读投影映射、迁移验证器接线、host fresh-grant 协议顺序、候选选择、secret 文件校验/清理、错误映射、测试矩阵。
- 独立实现 Review 必须验证：契约不变量 + impl-design + 测试矩阵；未运行项 NOT_RUN。
- 测试矩阵：A（V/witness 组合、get/list 不丢 V 行、迁移断言与破坏测试、正尺寸基线、资源门禁、读者跳过不可读页的确定性）；B（Host fresh-grant 协议、0/1/多 Secret-G、capability、token 路径/对象/一次性/并发/超时/孤儿、无泄漏、真实 IPC 加密页、四象限）。

## 6. 冻结流程（A 单包，B 随 C-16 同流程或合批）

- r11 approved 且 P0/P1=0 → 语义修订提交（C-05/C-15/C-16）→ 逐文件三指纹/old-new blob → 已提交字节复核 → 仅元数据冻结（FROZEN/矩阵/载体 §8/旧 pin 保留）→ check + 17 pins。
- M2-C1 无字节变更，仅在载体登记"无改动"依据与版本链。
- 未运行项保持 NOT_RUN；实现后再由实现 Review/DSH 集成补证据。

## 7. 不做

不改 referenced 分支/四维 scope/import 状态机/WireLog 架构；不新增命令/错误码/依赖；不动 M2-C1 字节；不改 Reader DTO；不实现 UI；不补 ORIGINAL 行；协议 major/minor 不变。
