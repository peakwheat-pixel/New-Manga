---
id: NEW-MANGA-V1-FULL-AUDIT
title: V1 全项目独立审计
kind: research
governance_version: 3
status: blocked
resume_status: in_progress
approval: user_approved
suggested_owner: Codex
owner: Codex
reviewer: null
depends_on: []
base_commit: 349e61faff5f93067af5d4ce2d9e394e0d665b8c
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: audit/V1-FULL-AUDIT
allowed_paths:
  - audit/V1-FULL-AUDIT/**
  - doc/tasks/NEW-MANGA-V1-FULL-AUDIT.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
---

# NEW-MANGA-V1-FULL-AUDIT

## 来源与目标
用户2026-10-24粘贴的完整自主审计指令；本轮新增只读审计 Task，不重新激活历史实现。Codex接任Lead Auditor，明确覆盖AUDIT-00–14；允许隔离本地扫描/测试与报告，不授权业务修改、安装、付费API、发布、删除、清理或上传项目材料。

## Acceptance Criteria
- [ ] AC1：固定Git/环境及有效源码清单，记录dirty和历史缺口。 <<PARTIAL: 基线已存，待交叉核验>>
- [ ] AC2：15项专项逐项有真实检查结果或具名阻断，关键链路深读与测试。 <<PARTIAL: 正在执行>>
- [ ] AC3：完整日志、问题分级、整改路线、正式报告和Release Gate落盘。 <<PARTIAL: 正在执行>>
- [ ] AC4：独立复核、证据pin和治理检查可核验；未满足不得置done。 <<PARTIAL: 尚未提交或独立审查>>

## 允许修改范围
仅frontmatter所列。审计日志/测试脚本由主控单一写入。三名子代理只读同一固定产品HEAD，无并发写入。用户显式审计目录优先于常规verification路径；运行派生产物放相邻workspace task-env。

## 禁止范围
src/**、apps/**、原有tests/**、共享契约、Schema、依赖、真实用户数据、历史证据及Git历史不修改。没有实现任务释放。

## 测试要求
使用 audit/V1-FULL-AUDIT/tests/audit_runner.py，日志保存argv/cwd/shell/interpreter/exit/elapsed；真实GUI若不可捕获则BLOCKED，不用JSX或Mock替代。真实API/模型标注和干净Windows无条件时BLOCKED。

## Canonical Evidence
待审计交付后固定文件SHA256；当前证据尚未提交，不伪造commit pin。

## Resource Manifest
| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga | PRESERVE_REFERENCED | — | evidence/baseline.json | 主工作区，不创建/移除worktree |
| task-env | G:/CODEX/New Manga.workspace/task-env/NEW-MANGA-V1-FULL-AUDIT | PRESERVE_REFERENCED | — | audit/V1-FULL-AUDIT | 隔离数据库/构建/临时数据，未授权删除 |
| artifact | audit/V1-FULL-AUDIT | PRESERVE_REFERENCED | — | evidence/ | 审计交付物保留 |
| dataset/model/test-material | — | NOT_APPLICABLE | — | — | 不获取私有漫画/新模型 |
| exchange | — | NOT_APPLICABLE | — | — | 无外部传输 |

## Rolling checkpoint
[audit/V1-FULL-AUDIT/AUDIT_RESUME.md](../../audit/V1-FULL-AUDIT/AUDIT_RESUME.md)。Reviewer尚未分配；不得虚构独立批准，保持in_progress直到可固定交付点。

## 2026-10-24 推送准备补充授权

用户同意上一轮推荐下一步：Codex 整理审计登记、同步台账，并离线检查 `origin/main..main` 的凭据与材料来源，形成固定 SHA 的推送清单。本补充仅增加 `doc/TASK_LEDGER.md` 的生成同步范围；扫描脚本、报告和证据沿用本 Task 的 audit 路径。不授权 push、历史重写、删除或业务实现，不将本 Task 置 done。

检查基线：`origin/main=6a68fdeb92d8a1c7903166a8076d6260bf8fa79a`、`main=349e61faff5f93067af5d4ce2d9e394e0d665b8c`。两份治理文档的在途修改属于本审计登记；6 个 `verification/P04/diagnostic_p22_*.jsonl` 在审计前已存在，具体生成者未证实，原位保留且不暂存。检查结果见 `audit/V1-FULL-AUDIT/reports/PUSH_READINESS.md`；此记录不替代独立审查。

## 2026-10-24 材料来源复核与差异证据

用户“下一步”授权继续已有推送准备的只读材料核验；不扩大业务或远端权限。按该调查实际需要读取 T1.1.1 的样本 manifest/生成脚本（固定 `ed607b755`）、真实素材记录和 M2-AC1 的合成 fixture 代码；只追溯历史材料，不运行 Legacy 产品诊断/修复。

Codex 记录：`.tmp.driveupload` 中存在169个JPEG，文件名集合、页数和1350×1920尺寸与 `verification/T1.1.1/author-verification.md` §6 和 `real-material/results.json` 完全吻合；但原记录无逐页hash，不能宣称已完成精确同源证明。该文档同时声明“版权像素不入库”，与临时压缩对象夹带图像的事实形成需处置的文档/实现差异；不改写旧证据来消除此差异。4个PNG与历史合成样本manifest精确匹配。详见 `audit/V1-FULL-AUDIT/reports/MATERIAL_CLEARANCE.md` 及 `evidence/push-material-inspection.json`。

34份SQLite主文件使用隔离原字节副本进行immutable只读检查，主文件hash保持不变；12份业务库与M2-AC1合成页hash匹配、5份P18业务库书架/章节/页面为空。发现22个本地路径单元格，未输出记录原文。不能由此证明缺失WAL/删除页无隐私内容，也不签发完整隐私清白结论。推送阻断仍为材料来源/传播许可待证明；已询问用户是否存在原始来源/许可记录，尚未据此获得上传或历史重写授权。

## 2026-10-24 用户材料处置裁决（当前有效）

用户对169张JPEG明确回复：“我自己的，但是不传播”。记录为用户本地持有/提供的素材，**禁止传播**，不推断用户拥有作品著作权，也不登记为可上传许可。该裁决取代此前“等待传播许可资料”的运行分支，不再默认要求用户补许可来放行完整历史。所有169个JPEG及其压缩外层blob均列为禁止上传项；本地对象、原件、旧证据及refs保持原位。

当前main及3个分批候选均包含这些外层blob，不能推送这些历史。后续推荐独立干净源码快照，须先明确目标分支/发布范围并释放Task；本裁决不授权删除、改写历史、实施新发布方案或push。具体裁决和对象指纹见 `audit/V1-FULL-AUDIT/evidence/push-material-disposition.json`。

2026-10-24 后续用户“下一步”授权本地快照准备，已独立冻结为GIT-CLEAN-PUBLICATION-1。完整历史上传因用户禁止传播素材而blocked；主控当前只执行新Task。全审其他AC/独立Review未完成，不置done、不把快照测试算成全审PASS；恢复全审时从in_progress续接，原证据保持原位。

## 2026-10-25 DSH 接管后的效力

DSH 接任 Lead / Architect / Integrator（见 `doc/GOVERNANCE_TAKEOVER_2026-10-25.md`）。本 Task 保持 `blocked`、`resume_status: in_progress`；Owner/审计作者仍为 Codex，不伪造独立审批。用户“169 张 JPEG 私有、不传播”的裁决不变：禁止推送包含这些字节的完整 main 历史，禁止把它们纳入任何待推对象。

本 Task 不因 DSH 接管自动恢复；重新启动需 DSH 明确范围冻结与独立 Reviewer Appointment。干净快照 push 的独立审查可复用本 Task 的材料隔离结论，但不得据此宣称全审完成或产品发布通过。
