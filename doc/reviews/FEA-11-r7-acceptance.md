# FEA-11 用户裁决记录（2026-11-05）：closed_with_limitations

- 裁决人：用户（本会话直接指令）。
- 裁决内容（三问三答）：
  1. **FEA-11 终态**：选 **A. 接受 limitation → closed_with_limitations**——接受「Host 自签授权（P0-1）由 FEA-11-HOST-AUTH-1 后续闭合」「lineage 读隔离（AC11-5）由 FEA-11-LINEAGE-1 闭合」两项 limitation，FEA-11 以 `closed_with_limitations` 收口。
  2. **承接卡授权**：**启动 FEA-11-HOST-AUTH-1、FEA-11-LINEAGE-1、FEA-11-AC4-GAPS-1、FEA-11-MATCH-1、FEA-11-SCAN-1 实施**（可与 FEA-11 并行；depends_on FEA-11-PREREQ-1）。
  3. **FEA-12 前置**：**允许 G-DELETE-IMPL 采用「隔离 fixture + 模拟回收站路径」**作为门禁验证口径（不触碰真实回收站）；FEA-12 可进入 scope review。
- 依据：FEA-11 七轮独立 Review（r1–r7，`doc/reviews/FEA-11-r1.md`…`FEA-11-r7.md`）均 changes_requested，剩余硬阻塞均为承接范围，而非本卡可内部修复；用户据 DSH 建议选择 closed_with_limitations。

## 约束（必须随 limitation 生效）

> **LINEAGE-1 完成前，任何 UI / 读路径 / 渲染 / 导出 / Run 不得消费同步后的新 binding**；仅允许 Core seam 测试与受控验证使用。

## Limitation 清单（即 closed_with_limitations 的边界）

| # | 限制 | 承接 |
|---|---|---|
| L-1 | **P0-1**：Host 未自签 canonical `HostAuthorization`、未走 Registry durable 授权（operation_id/authorization 仍由调用方提供，Host 仅 journal 透传）；Core 侧校验为最后防线 | FEA-11-HOST-AUTH-1 |
| L-2 | **AC11-5/LINEAGE-1**：lineage native 写入与 ListRegions/渲染/导出/Run/编辑读隔离未实现；旧区域/旧 revision 对新 binding 的可见性未验证（见上方约束） | FEA-11-LINEAGE-1 |
| L-3 | AC11-1：定时扫描与 watcher 消费者未实现（本卡两条路径已测） | FEA-11-SCAN-1 |
| L-4 | AC11-3：生产 scan 不写 pixel profile；旧库 fixture/独立 match 测试缺失 | FEA-11-MATCH-1 |
| L-5 | AC11-4：并发 apply / DB 失败 / 第三区域 BaseRevision 冲突证据缺失 | FEA-11-AC4-GAPS-1 |
| L-6 | AC11-6：folder source 的 relink 一律 typed 拒绝（需 repoint/resync）；跨卷/成员重排/其他项目不误改证据缺失 | 文档 limitation（无独立卡） |
| L-7 | AC11-7：管理诊断查询接线未实现 | 后续读投影/UI 切片 |
| L-8 | AC11-8：逐崩溃点杀进程恢复矩阵 NOT_RUN；capability/recovery CommitReceipt 无自动化测试 | 测试债务（承接卡/后续） |
| L-9 | AC11-9：真实 IPC 为 Core 直连（未走 HostRuntime/dispatcher）；旧键/旧摘要不可变、pre-sync 旧 binding 证据缺失 | Host E2E 证据后续 |
| L-10 | AC11-10：EV/Manifests 以最终证据提交定稿；r7 log 为复合摘要 | DSH 定稿（本次） |
| L-11 | IPC/App.Tests 在全量 .NET 后首跑偶发 flaky（复跑 3/3 或单跑绿）；根因未定位 | 测试债务 |

- **`closed_with_limitations` 不等于可发布**（`doc/09_COLLABORATION.md:79`）；上述约束与承接卡是产品可用的前置。
- 证据：r1–r7 报告、`verification/FEA-11/EV.md`、`AC-MATRIX.md`、`RESOURCE-MANIFEST.json`、`DELIVERY-MANIFEST.json`、`changed-files.txt`、`logs/**`。
