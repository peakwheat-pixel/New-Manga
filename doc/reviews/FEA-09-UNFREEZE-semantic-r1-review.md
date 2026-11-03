# FEA-09 UNFREEZE 语义修订提交（ed570681b）已提交字节独立复核

- Reviewer：ZCode 独立会话（GLM-5.3），session `sess_1517188b-38c0-4310-9c92-1a71575a5826`；未参与 FEA-09 实现/I001 裁决/r1–r15 起草或本次提交。
- 只读：未修改文件/commit/push。
- reviewed_head：`ed570681b57e1343cb8c477f5dd7d23200a2dab4`。
- Codex 本日额度耗尽（2026-11-04 03:33 恢复），按用户长期授权故障转移候选仅 ZCode。

---

# FEA-09 UNFREEZE 语义修订提交（ed570681b）已提交字节独立复核

**审查者**：ZCode 独会话（GLM-5.3），未参与 FEA-09 实现、I001 裁决、r1–r15 起草及本次提交。**只读**：零修改、零 commit/push。审查基线 = HEAD `ed570681b57e1343cb8c477f5dd7d23200a2dab4`（工作区 clean，工作区字节=HEAD）。已读：三份 DRAFT、r11–r15 amendments/review、M2-C1（头部/revision history/§6.3 定位）、2026-11-03 载体。

## 1. C-05 v1.2 —— 通过
- `V_managed=V_artifact∨V_copy_original`、模式分派、referenced 不得穿透（反例 8）均在 §3.1；`V_copy_original` 条件与 r11 §1 逐项一致。
- witness 独立（§3.1 冻结段：一真即 V、互不否定、父级软删否定两个 witness）；V/R 分离（资源选择属 R、R 失败 typed 不得隐藏 V 行）成立且与 §3.2 R 定义自洽。
- 反例矩阵 1–8、投影形状（不丢 V 行、禁 thumbnail/clean hash 冒充、禁写回/伪造 provenance）完整；§5 v1.2 注与 §3.2 v1.2 失败行一致（「不可见」限定 artifact witness）。
- P1–P5/P7/P8 原文：§3 与 V_ref 块结构完整、编号连续；无 v1.1 字节基线可比（git 旧版读取被 plan mode 拦截），按 r15 链声明+变更记录间接核实一致。

## 2. C-15 v1.1 —— 一处 P1
- 断言 1/2/3/5 与 r11+r12 链一致：`_LEGACY_COMPLETE_WHERE_POSITIVE` 与 §2.1 回填 UPDATE 谓词等价；union 守恒（分支分别守恒、不要求 V=complete/旧 artifact 集）、同事务连接/固定 t/get-list-纯投影三路径、非空禁跳 verifier、破坏必失败均在 §1；「禁迁回调 wire resolve/publish」由 §1 回调禁 Host 调用 + §4.2 纯投影不 publish/resolve 语义覆盖。
- §4.1 V 与 C-05 §3.1 一字面对应；§4.3 incomplete+artifact witness 可见、§4.4 投影最小集（字段/NULL 语义/禁冒充/未知 ID None/去重/选择顺序）与 r11 §2.2 一致。
- **P1-1（§4.2 reader 行，摘要承载不完整）**：R12-001 最终形态（r13 冻结文本）的算法定义层未落入契约——缺 ①锚点算术（`(sort_order,page_id)` 完整二元组 0-based 插入位置、无 DB 行 a=0、「首个 logical_order>=a、无则回绕」）；②beginning 分派「saved_progress 不删除/不改写」；③「offset 沿用 M2-C1 §6.3 既有单位与校验（非负有限 number）」引用。现有文本只写「resume 按保存页可读/不可读/已移出/无进度规则」，同 sort_order 歧义无契约约束——R13-002/R14-001 两轮修正成果在重冻后无权威锚点，与 r15 approved 最终最小包不一致，不可据此完整重冻。
- 修复（最小契约层）：在 C-15 §4.2 reader 行（或 C-16 §3.1 邻近）补入上述三要素，引用 M2-C1 §6.3 为规范性引用；其余零改动。

## 3. C-16 v1.1 —— 通过
§0 能力门禁（`source.resolve-secret/1`、缺失/异常不建文件、typed `SOURCE_PASSWORD_REQUIRED`）；§3.1 fresh-grant 协议与 r11 §3 逐项一致（revoke 上一 grant、token `[A-Za-z0-9_-]{22,64}`、`NMSSR1\0`+DPAPI/私有 ACL/原子/TTL≤300s、恰好一个 fresh grant）；0/≥2 Secret-G → REQUIRED/DENIED；路径规范/无 reparse/普通文件/独占句柄→零填充→删除、未验证不读不清、一次性/重放拒绝、cache 命中 Auth 必须成立；清理分工与零泄漏（含 PDF raster 接缝、AES ZIP unsupported）齐全。撤销/过期/多义码映射与 §6 v1.1 补充一致（REVOKED 不改 DENIED、不新增码、category/retryable 沿原表）。**resolve 请求/响应字节零变更**确认（§3.1「仍 `{page_id}`」；secret_ref 为 C-06 既有字段，非新增）。

## 4. M2-C1 零改动 —— 间接核实成立
commit message 限三契约；文件头部/revision history 无 2026-11-04 修订痕迹（最新 rev 2.11/2026-10-19）；§6.3 `scroll_offset_y: number`/像素坐标/分页 0 原样在场（R14-001 引用基础成立）。字节级 `git diff` no-diff 未运行（见 NOT_RUN）。

## 5. 结论

**P0=0 / P1=1 / P2=1**；`verdict: changes_requested`。P2-1：版本引用陈旧——C-16 §10 冻结条件「C-05 v1.1/C-15 v5」、C-16 §8「C-15 v5」、C-15 §7 表「C-05 v1.1」未随 v1.2/v1.1 更新，建议随 P1-1 修复合并修正。除上述外无外部可观察矛盾或遗漏；P1-1 闭合后即可重冻。

**NOT_RUN**：字节级 `git show/diff`（plan mode 拦截）、三指纹/old-new blob 复算、`check.ps1`/`verify_pins`、pytest/.NET/build/IPC/DPAPI/迁移/竞态/泄漏全部未运行（文档级审查）。

**推荐下一步**：由 **DSH** 按 P1-1/P2-1 做最小契约层补写（三要素 + 版本引用）后重新提交，并再次独立复核已提交字节；通过后按 r15 §冻结路径执行仅元数据重冻（FROZEN/矩阵/载体 `CONTRACT-UNFREEZE-2026-11-04.md`/check+17 pins）。