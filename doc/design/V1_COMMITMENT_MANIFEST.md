# V1 Commitment Manifest / V1 承诺清单

**版本：** V1.0（2026-11-14，DSH 自动裁决记录）
**基线：** `main` 分支；近端集成 HEAD 记录于 `doc/STATUS.md`；本清单只声明 V1 交付承诺与证据指针，不替代 STATUS / Task / Review / 契约。
**审计来源：** `audit/V1-FULL-AUDIT/`（P7 完整审计，Task `NEW-MANGA-V1-FULL-AUDIT` 已由 DSH 集成收口；Codex 最终回退复审 `ACCEPT_WITH_LIMITATIONS`）。
**产品 Release Gate：** **BLOCKED**（真实 clean install、真实 GUI 全验收、真实模型 API 调用、完整验收证据未执行；见 `audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md`）。

本清单用于消除 README / AD-003 / STATUS / 索引之间的“V1 承诺”漂移：每一项都给出状态与可核验指针；未验证或不可执行的检查明确标 `NOT_RUN` / `BLOCKED`，不得读作 PASS。

## 1. V1 交付项与状态

| 交付项 | 状态 | 权威指针 / 证据 | 未完成或限制 |
|---|---|---|---|
| Windows 桌面 V2 shell（C#/.NET 9 + Avalonia） | 实现完成；真实 GUI 全验收 NOT_RUN | `doc/AD-002_TARGET_DESKTOP_ARCHITECTURE.md`；`audit/V1-FULL-AUDIT/reports/AUDIT-09-UI-UX-2026-11-13.md` | clean install / 全页面真机演练未执行 |
| 四个一级页面（书架 / 工作台 / 阅读器 / 设置） | 实现完成；Reader 零页 Retry 已修复 (AUDIT-09) | `apps/desktop-avalonia/`；`verification/AUDIT09-READER-EMPTY-RETRY-1/` | 真实 GUI 演练 NOT_RUN；Avalonia TestHost 历史阻塞未解除 |
| Python Core 侧车（SQLite 书库 / 流水线 / 本地推理） | 实现完成；质量基线见审计 | `src/`；`audit/V1-FULL-AUDIT/reports/FINAL_AUDIT_REPORT.md`（pytest 3,519 passed / 16 failed / 10 skipped；失败均为既有失败） | 16 个既有测试失败未修复（审计登记，非本轮引入） |
| 存储：ReferencedSource（新导入引用原文件；旧 Managed Copy 可读） | 架构已冻结 | `doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md` | — |
| 删除语义：普通删除/自动清理保护；显式彻底删除经确认且不删原文件 | 已冻结 | `doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md` | — |
| 备份/恢复（nmbak）：restore 失败 typed error + rollback ID | 本轮修复 | `verification/SEC-03-RESTORE-TYPED-ERROR-1/` | 真实库断电/多文件部分写 NOT_RUN |
| 导出：ZIP/PDF（单文件/可搜索双栏） | 实现完成；相邻 hook 选项失败（审计时）当前不可复现 | `audit/V1-FULL-AUDIT/reports/AUDIT-07-REPAIR-TYPESET-EXPORT-2026-11-13.md`；`verification/AUDIT07-EXPORT-HOOK-OPTIONS-1/` | 真实图像质量/视觉评分 NOT_RUN；原 3 失败保留原 finding |
| 交付工具：publish 输出移出仓库、清理范围受限 | 本轮修复 | `verification/AUDIT12-PUBLISH-OUTPUT-1/` | 真实 `dotnet publish`/安装 NOT_RUN |
| 侧车进程生命周期：取消/Dispose 后不遗留 EOF-ignoring 子进程 | 本轮修复 | `verification/CORE-01-SIDECAR-LIFECYCLE-1/` | — |
| 隐私：默认本地、无 telemetry、无网络监听；remote provider 显式配置后仅发送披露的数据类 | README 承诺；审计确认无监听器 | `README.md`；`audit/V1-FULL-AUDIT/reports/FINAL_AUDIT_REPORT.md` | — |
| 私有素材远端可见性（AUDIT-11-INC-001） | 已确认远端可见（公开仓库历史树可枚举 `.tmp.driveupload`）；处置未执行 | `verification/SEC-01-REMOTE-VISIBILITY-1/REPORT.md`；`verification/SEC-02-REMOTE-DISPOSITION-1/REPORT.md`（推荐保持现状+监测） | 远端暴露面处置（删分支/改写历史/平台请求）未执行；依赖用户/独立授权 |
| 质量门禁：default / TaskPath / verify_pins / API inventory | 四项治理门禁 18/18 pins、API 86、EXIT 0 | `tools/governance/`；`doc/TASK_LEDGER.md` | 门禁 PASS 不等于产品发布 PASS |
| 安装包/发布 | 0.1.1 早期；安装器未签名 | `README.md`；`doc/release/` | **Release Gate BLOCKED**；未做 clean install 验证 |
| 模型 API 真实调用 | NOT_RUN | 审计报告边界 | 需要真实 provider/费用/凭据；未执行 |

## 2. 明确不作为 V1 承诺

- 真实模型推理质量（OCR/翻译/inpaint 质量）与像素级视觉评分。
- 私人漫画素材的完整取证（第三方 clone/fork/平台缓存不可见）。
- Avalonia TestHost 全量测试恢复（历史 8/8 runner EXIT 1、TRX 0；本清单不把筛选测试通过写成全量恢复）。
- 远端暴露面的补救动作（删除分支、history rewrite、平台清理）——需要独立授权与影响评估。

## 3. 维护规则

- 本清单随 `doc/STATUS.md` 的当前程序变化更新；新增承诺必须有可核验指针，未验证项写 `NOT_RUN`/`BLOCKED`。
- 不得用本清单替代 Task 范围、Review 结论或契约字节；冲突时以 STATUS / Task / 契约 / 原始证据为准。
