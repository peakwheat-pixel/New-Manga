# FEA-11 Appointment（DSH，2026-11-04）

状态：**scope 冻结 + Appointment 完成；Task 置 `ready`，等待 Owner 认领；不 push**
Task：`doc/tasks/FEA-11.md`（scope：scan/diff/plan + 页匹配/lineage + relink/repoint/resync + durable operation；实际 **10 条 AC**（AC11-1…10））
依据：`doc/reviews/FEA-11-scope-r2.md`（ZCode 全新上下文，approved P0=0/P1=0/P2=4）；`doc/reviews/FEA-11-scope-r1.md`（S11-001…011）；`doc/tasks/FEA-11-PREREQ-1.md`（done）；`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md`（v1.0 FROZEN）；C-14/C-15 v1.1/C-16 v1.1/C-05 v1.2/C-13；M2-C1 rev 2.12（NO_INCREMENT）。

## 1. 角色

| 角色 | Agent | 说明 |
|---|---|---|
| Owner（实施） | **ZCode** 新实现会话 | 立即启动（Codex 额度耗尽至 2026-11-05 00:51）；写域严格按 Task 卡 allowed_paths |
| Reviewer（独立上下文） | DSH 派发的全新上下文（Codex 恢复后或新 ZCode 会话；未参与实现） | 只读 reviewed_head；报告归档 |
| Integrator / 冻结核对 | DSH | 门禁复跑、范围、C-17 一致性、证据、集成、closeout |

## 2. 冻结 scope

- 10 条 AC（AC11-1…10）按 `doc/reviews/FEA-11-scope-r2.md` 的断言表冻结；禁止把未执行项标 MET。
- 写域：按 Task 卡 allowed_paths 逐文件；**不含** C-17 契约文件、旧 17+1 冻结契约、共享组合根、App/UI、FEA-08/09/10 证据、migrator.py（v8 只改 schema.py `default_migrations()`）。
- 条件项（scope-r2 写域节）：若实现证明必须改 `render_preview.py`（自愈验证）或 `regions.py` 等写域外文件，**先停下报告 DSH**，由 DSH 逐文件窄批并记录，不得自行扩大。
- 上游：C-17 v1.0（DDL/状态机/命令面/CAS/lineage/resolve）；若发现 C-17 条款不可实现，先报告 DSH，不自行改契约。

## 3. 裁决（本 Appointment 记录）

1. **定时扫描/后台调度**：本卡首版实现三路——启动/访问前检查、操作前强验证（lease+digest）、目录 watcher 消费者（hint 丢失/overflow 后全量重枚举）；**定时扫描生产者与后台调度登记承接 Task `FEA-11-SCAN-1`（后续小卡，待建卡）**，不在本卡 AC 强制；不得静默缺失（缺则登记）。
2. AC 数：**10 条**（历史提交信息「12 AC」为笔误）。
3. 命令面/确认语义/CAS/lineage/resolve 版本选择以 C-17 冻结字节为准；实现不得暗改。
4. M2-C1 无增量；若真实链路证明必须增量，先报 DSH。

## 4. 硬边界

- 不 commit、不 push（DSH 集成提交）；不新建依赖；不改冻结契约字节/共享组合根；不碰真实用户数据/AppData/外部卷/回收站；不实现 FEA-12/13/14/SCAN-1 范围。
- 测试隔离：所有 DB/fixtures/TEMP/TMP/Host registry 固定在 `G:/CODEX/New Manga.workspace/FEA-11/` 子目录；不得复写 `verification/FEA-09/**`、`verification/FEA-10/**` tracked 证据（若被测试重写须恢复原字节）。
- 真实链路：Core scan/diff/plan/apply/relink-repoint-resync/resolve 的真实 IPC 至 Host/API；不含 UI（后续切片）。

## 5. 门禁与完成定义

- 最少门禁：pytest `tests/fea11` + 主套件与 providers；Release build 0/0；全量 .NET；真实 IPC（`Fea11SourceIpcTests`）；check.ps1 PASS；verify_pins 18/18；范围 0 域外；FEA-09/10 证据零 diff；源字节守恒（测试不写源）。
- 交付：代码/测试/Handoff/`verification/FEA-11/**`（AC-MATRIX、日志、IPC 输出、迁移负测）；Task 卡 in_review + AC 标记如实。
- 完成定义：Owner 交付 → DSH 复跑门禁与范围 → 全新上下文 Review（P0=0/P1=0）→ DSH 处置 → 集成提交 → Task done → 更新 PLAN/STATUS。

## 6. 后续

- FEA-11 done 后按 PLAN 继续：FEA-12（先解 `G-DELETE-IMPL`）、FEA-13/14/15、FEA-11-SCAN-1 建卡；GIT-CLEAN 线按既有裁决排序。
