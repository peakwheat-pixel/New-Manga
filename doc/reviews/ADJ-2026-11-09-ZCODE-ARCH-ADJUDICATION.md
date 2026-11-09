# ADJ-2026-11-09 · ZCode 独立架构裁决（三项跨层事项）

- 裁决者：**ZCode**（独立上下文；未参与 FEA 线实现）
- 派发：DSH 2026-11-09（goal 指令：硬阻塞交 ZCode 裁决）
- 被审 head：`06f73a9fc`；ZCode sessionId：`sess_1c39decd-135a-4d87-827a-03fd41e311d6`
- 原始输出：`G:\CODEX\New Manga.workspace\agent-output\zcode-adjudication-2026-11-09\raw-output.json`（response 另存 `response.md`）
- DSH 处置：**全盘采纳**（无修订；细则见 §4）

## 1. 事项一：FEA-11-HOST-AUTH-3 载体

**裁决：批准「C-17 单 pin ADDITIVE_UNFREEZE（路线 B + D-4 合批）」；A、C 均 `ARCHITECTURE_BLOCKED`。**

| 项 | 结论 |
|---|---|
| B（恢复路径重发 grant，新增只读计划物化投影命令） | **批准**：读回 Core 已持久化的 `source_sync_plans.body_json`；不新增披露面、零写、无 schema/migration；C-17 v1.1 有同型 additive 先例，18 pins 仅重算 C17 |
| D-4（plan 读回/预检） | 与 B 同一条命令、同批、不加 pin |
| A（Core grant 持久化/重绑定） | **ARCHITECTURE_BLOCKED**：抵触 C-15:304 / C-16:224 / C-06:40/42 / C-17:266 四条冻结明文；`signing_key` 随载荷，落盘即可重签材料；属安全不变量级变更 |
| C（Host-only kill + 外部托管 Core） | **ARCHITECTURE_BLOCKED**：语义+传输双阻断（C-16:24/224、C-06:42 已实现于 `source_read_refs.py:253-260`） |
| D-3（retry 命令） | **out_of_scope**（无 UI/命令面消费者） |
| R-01 错误码 | 期望码是 **`SOURCE_ACCESS_DENIED`**（非 `SOURCE_GRANT_EXPIRED`），必须落进卡面与 AC |
| R-03 | 另立缺陷卡（契约允许「全缺失源 `grant_ids=[]`」但 Core 拒绝、分支不可达），不在本卡顺手修 |

**风险**：新只读命令须 host-only + closed shape + wirelog 脱敏断言；崩溃注入须断言 Python sidecar 确被杀（否则记 NOT_RUN，不得冒充 PASS）。

## 2. 事项二：FEA-13-SRC-6（SC-B01 ④ 包内源引用/授权元数据）

**裁决：单列实现卡、立项；不阻塞 FEA-15 正式验收（验收登记为已知 limitation）。**

- 理由：C-09 SC-B01「必须包含」项、SC-B07 增量④已预留；明确不做需契约 errata；AD-003 引用模型下不随包恢复会导致重装后须全部重新授权。
- 时序：排在 HOST-AUTH-3 之后（同域 SourceAccessRegistry/Host 授权）。
- 风险：DPAPI CurrentUser 绑定 → **同机恢复有效、跨机恢复须重授权**（不得写成通用跨机恢复）。

## 3. 事项三：数据根迁移（FEA-13 片 6）

**裁决：指针归属 = Host 独占（Core 永无切换权）；不与 FEA-14-SET 合并；维持单列 blocked，待 FEA-14 切片 scope 定稿设置存储形状后释放为「Core 迁移原语 + Host 编排切换」。**

- 理由：指针是进程配置（`HostOptions.cs:46` + `NEWMANGA_DATA_ROOT`），Host 另有多个按 DataRoot 布局的持久物（SourceAccessRegistry、operation journal、日志）；「Host+Core 协作」最终提交点仍是 Host。
- 释放时：按 scope review §7 片 6 allowed_paths 冻结，AC 含 L-5 四条与 marker 前/后崩溃注入；**切换期间 Core 停机、Host 主导重启**（两阶段，禁止在线热切换）。
- 依赖：FEA-14 切片 scope 须显式包含「数据根指针持久化 + 切换入口」一行。

## 4. DSH 处置（采纳后的动作）

| # | 动作 | 状态 |
|---|---|---|
| 1 | `FEA-11-HOST-AUTH-3` 卡按裁决改写（B+D4 载体、A/C blocked、D-3 out_of_scope、错误码纠正），status 维持 `blocked`（待 UNFREEZE 程序） | 本轮落盘 |
| 2 | 建 `FEA-13-SRC-6` 卡（proposed；Host staging 交接面 + 恢复反向；owner 建议 ZCode） | 本轮落盘 |
| 3 | 数据根迁移：FEA-13 scope 记录追加「Host 独占 / 依赖 FEA-14 / 两阶段切换」裁决；释放条件写入 | 本轮落盘 |
| 4 | FEA-15 验收矩阵 A7 加「源授权元数据未入包」已知 limitation（指向 SRC-6） | 本轮落盘 |
| 5 | 启动 C-17 UNFREEZE 载体草案（唯一无前置依赖项） | 下一轮 |

**不构成**：本裁决不构成 UNFREEZE 完成、不构成任何实现授权、不改契约字节与 18 pins。

## 5. 建议时序（采纳）

1. HOST-AUTH-3（UNFREEZE 程序：载体草案 → 独立 byte-level 复核 → 重冻 → pin 重算）
2. FEA-14 切片 scope（含数据根指针行）
3. MIGRATE-6 与 SRC-6 并行释放（DSH 划清 DataRoot 写域子路径）
