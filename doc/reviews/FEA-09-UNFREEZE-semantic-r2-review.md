# FEA-09 UNFREEZE 语义补正提交（a9276fbae）已提交字节独立复核

- Reviewer：ZCode 独立会话（GLM-5.3），session `sess_f155bf21-4fb4-4770-91ce-c1b9fa63e9ae`；未参与 FEA-09 实现/I001 裁决/r1–r15 起草或本次提交。
- 只读：未修改文件/commit/push。
- reviewed_head：`a9276fbaeeb7dd9fa85569910dfe314ee45bbff0`。
- Codex 本日额度耗尽（2026-11-04 03:33 恢复），按用户长期授权故障转移候选仅 ZCode。

---

# FEA-09 UNFREEZE 补正复核报告（已提交字节 a9276fbae）

**审查者**：ZCode 独立会话（GLM-5.3，session 本轮新开）；未参与 FEA-09 实现、I001 裁决、r1–r15 起草或本次提交。**只读**：未修改任何文件、未 commit/push；Bash 在 plan mode 下被禁，全部经 Read/ReadSessionContext 取证。

## 1. P1-1（reader 摘要承载）：**CLOSED**

对照上一轮（sess_1517188b）三要素逐一核验 C-15 §4.2 reader 行：

| 要素 | 补正文本 | 判定 |
|---|---|---|
| 锚点算术 | ③`a = V 页中满足 (P.sort_order,P.page_id) < (保存页.sort_order,保存页.page_id)` 的页数（**完整二元组 0-based 插入位置；同 sort_order 按 page_id**）；**无 DB 页行则 a=0**；`首个 logical_order>=a 的可读页（无则回绕）`；②不可读路径 a=logical_order 同构 | ✅ |
| beginning 分派 | 忽略保存进度、首可读页 offset 0、**saved_progress 不删除/不改写**——与 M2-C1 §6.3 L952 `without mutating saved_progress` 一致 | ✅ |
| offset 引用 | **规范性引用 M2-C1 §6.3**：Webtoon 逻辑 Page 源图像素坐标（**非负有限 number**、合法范围/页高校验沿 M2-C1、**不取整不归一化**）、分页=0、resume 原值、替代/回绕/beginning/无进度均 0；不变量 `initial_position.page_id ∈ pages[]` | ✅ |

M2-C1 §6.3 权威文本核对：L935/L948 `scroll_offset_y: number`（对照 L917 `order: integer`，number 为有意区分）、L955 非负像素坐标+分页=0、L956 拒 negative/non-finite/超页高+resume 原值——r15 R14-001 与 R13-002 冻结成果在重冻后有权威锚点。

## 2. P2-1（版本引用陈旧）：**CLOSED**

上一轮三处定位逐一复验：C-16 §10 →「C-05 v1.2/C-06 v1.1/C-15 v1.1」✅；C-16 §8 →「C-15 v1.1」✅；C-15 §7 →「C-05 v1.2」✅。全文扫描无新残留：C-15 §0 第 27 行「C-05 v1.1：新增 referenced 分支」为历次修订**分层描述**（紧邻 v1.2 追加行），非陈旧生效引用；I-4 来源列同口径，上一轮已放行，不重开。

## 3. 通过项

- **三契约与 r15 最终包一致**：补正逐点覆盖 R14-001 全部条款；C-05 v1.2（V_managed 析取/witness 独立/反例 1–8/P1–P5/P7/P8 保留）与 C-16 v1.1（fresh-grant/Secret-G/零泄漏/resolve 字节不变）原文在场，补正未触碰其通过面。
- **无 wire/DTO 字节变更**：`GetReaderProjection` 字节不变、resolve 仍 `{page_id}`、`PROTOCOL_MINOR` 不 bump、无新增 `IHostController`；补全面全部为语义/引用层。
- **M2-C1 零改动（间接核实）**：§6.3 现文本与 r15-review 引用的 L917–919/L935/L948/L955/L956 行号**零漂移**、内容逐点一致；字节级 no-diff 复算 NOT_RUN。
- **自洽性核验**：C-15 §4.2「C-16 §6 既有 11 码」= §6 全 18 码中逐页可用码（授权/密码/格式/条目/预算/registry/identity 类），11+7（整请求级）=18 吻合，非矛盾。
- **冻结流程可执行**：三契约头部一致登记候审→复核后重冻；载体 `CONTRACT-UNFREEZE-2026-11-04.md` 待建、旧 pin/新 pin 写入口径（FROZEN 记录+verify_pins）齐备；r15-review P2 的 r14-review 已原字节归档（head `a7f636300`、SHA-256 `afb924d2…` 与 r15-amendments 引用一致）。

## 4. NOT_RUN

git diff 字节级复算、三指纹/old-new blob SHA-256、check.ps1/verify_pins、pytest/.NET/build/IPC/DPAPI/迁移全部 **NOT_RUN**（文档级审查；Bash 禁用）。

## 5. 结论

**verdict: approved**（P0=0 / P1=0 / P2=0）。P1-1/P2-1 均 CLOSED，可据此进入仅元数据重冻。

---

**推荐下一步**：由 **DSH** 按 r15 冻结路径执行：仅元数据重冻（三契约 FROZEN 状态/矩阵/载体 `CONTRACT-UNFREEZE-2026-11-04.md` §8/旧 pin 替换）→ 三指纹/old-new blob 复算归档 → `check.ps1` + 17 pins 门禁。无需 ZCode 侧进一步操作。