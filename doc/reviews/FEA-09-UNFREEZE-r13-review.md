**结论：`changes_requested`；P0=0 / P1=2 / P2=0。R12-001 尚未完全闭合，r13 暂不可 approved／重冻。**

Reviewer：Codex，独立上下文 `/root`；未参与指定实现、裁决或提案起草修订；未派子代理。
本次仅只读核查、标准输出；未修改仓库、commit 或 push。

仓库：`G:\CODEX\New Manga`；branch=`main`；Git common directory=`G:/CODEX/New Manga/.git`。
`reviewed_head`／结束 HEAD：`a7f6363003573dd42d65033b2a84dff5d6c3e2d9`。
r13 为未跟踪工作树文件，2835 bytes，不属于上述 commit 的提交字节。
审查前后 r13 SHA-256 相同：
`8f1a520cf92f90f52c0344a714e23fb97a6f4a6c687136720f52f5e91538c0cd`
审查前后 `git status --porcelain=v1` 完全相同：16 项既有 ` D`、21 项 `??`。
状态输出 SHA-256：`eda8acd98a8d429661335b2c88178195ba0542b0c03c93777450549ef939a853`。

证据限制：指定 `FEA-09-UNFREEZE-r12-review.md` 为 ENOENT，Git `--all` 对应路径历史查询为空。
已读 r12 提案、r11 Review／提案、impl-design、指定正式契约、FROZEN／矩阵及 I001 裁决；R12-001 的原始 Review 全文无法核验。
R11-002 按本轮已确认结论保持 CLOSED，不重新打开。

1. **已闭合的外部语义**

- `pages[]` 为章节全部可读页，按规范序完整返回，不随 initial_position 截断。
- beginning 取首可读页、offset=0，保留 saved_progress；resume 无进度时同 beginning。
- 保存页可读时恢复保存页；在 V 内但不可读时向后找可读页、无则回绕，offset=0。
- 保存页移出且 DB 行不存在时锚点=0；成功响应保证 initial_position.page_id∈pages[]。
- V 空／零可读均返回 TARGET_NOT_FOUND；11 码逐页跳过，其余错误整请求失败、无部分结果。
- 管理诊断路径、无 wire／DTO 扩展方向可接受；但旧客户端兼容及移出页恢复仍受下列 P1 阻断。

2. **外部可观察的最小 P1**

**R13-001 — P1：offset 单位违反 M2-C1，破坏合法续读位置。**
位置：[r13 第23行](/G:/CODEX/New%20Manga/doc/reviews/FEA-09-UNFREEZE-r13-amendments.md:23)；M2-C1 §6.3 第955–956行。
r13 要求 offset 为 `0..1` 归一化；M2-C1 明确 Webtoon 使用源图像像素坐标，分页章节为0。
反例：高度10000的可读 Webtoon 页已保存 `scroll_offset_y=5000`；r13 同时要求恢复5000和归一化至0..1，无法兼容既有客户端。
最小修订：删除归一化要求；明确沿用 M2-C1 的像素坐标／分页0语义，保存页可读时原值恢复，替代页恢复为0。

**R13-002 — P1：相同 sort_order 下，移出页插入锚点存在两个可观察结果。**
位置：r13 第20–22行。
“严格小于保存页 sort_order 的页数”与“同 sort_order 按 page_id 规范序”的插入位置并不等价。
反例：可读 V 页为 `(10,a)`、`(10,c)`，已移出的保存页 DB 行为 `(10,b)`。
严格小于计数得到 a=0、恢复页a；按完整规范序插入得到 a=1、恢复页c。
最小修订：统一为完整 `(sort_order,page_id)` 比较下的插入位置；无需冻结内部算法或 DTO 映射。

3. **冻结与下一步**

两项修正前不能认定 R12-001 完全关闭，也不能据 r13 进入语义提交／重冻。
修正并经新上下文 approved、P0/P1=0 后，既定流程可行：语义提交→三指纹／old-new blob→提交字节复核→仅元数据重冻→check＋17 pins；M2-C1 登记精确版本、指纹、no-diff及行为兼容依据。

pytest／.NET／build／真实 IPC／DPAPI／迁移／竞态／泄漏扫描／check／17 pins：**NOT_RUN**。

推荐下一步：由 **DSH** 处置上述两项外部语义并补归档真实 r12 Review；本报告不释放生产返修。
可直接转发：
> DSH：请原字节归档本报告。在 `G:\CODEX\New Manga`、main，来源 base/head=`a7f6363003573dd42d65033b2a84dff5d6c3e2d9`，刷新并保留现有变更；于 FEA-09 登记范围，仅修订新提案及必要治理记录，修复 offset 单位与相同 sort_order 的恢复锚点，交付逐项 disposition、修订稿与 SHA-256，补归档真实 r12 Review。禁止生产代码、Schema、依赖、UI、用户数据、历史证据改写及 push。委派新上下文只读复核；后续运行 `pwsh -NoProfile -File tools/governance/check.ps1` 与 `pwsh -NoProfile -File tools/governance/verify_pins.ps1`，未运行项保持 NOT_RUN；approved 且 P0/P1=0 后才进入提交字节复核及元数据重冻。