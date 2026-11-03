---
id: FEA-08
title: Source/回收站隔离原型（H4/H5/H6 能力矩阵与技术报告）
kind: prototype
governance_version: 3
status: proposed
approval: scope-r1 changes_requested（ZCode，P0=0/P1=3/P2=5）→ 已按最小修订更新，待 scope-r2
suggested_owner: codex
owner: codex
reviewer: 待 scope-r2 + impl Review appointment
depends_on:
  - FEA-01-FREEZE-1
base_commit: 7ded8bd37fb9c8f35c3c86defc3c4329edeaf8e1
branch: main
worktree: G:\CODEX\New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-08
allowed_paths:
  - doc/tasks/FEA-08.md
  - doc/research/FEA-08-*.md
  - doc/handoffs/FEA-08-*.md
  - doc/reviews/FEA-08-*.md
  - verification/FEA-08/**
---

# FEA-08：Source/回收站隔离原型

> 依据：`doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md` S3 FEA-08 行、H4/H5/H6 表（:794–:796）、§15.4 出口定义（:929）、精确匹配口径（:457/:469）、回收站语义（:512–:514）；`doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md`；`doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md`；`G-CONTRACT`/`G-DELETE-CONTRACT` 已 CLOSED（2026-11-01，AD-003 §5/STATUS；提案内 "OPEN" 为冻结时快照，字节不动）。
> 本卡在独立 scope Review 冻结前为 `proposed`，不得实施；workspace 派发 prompt 仅在 scope approved 后使用（本轮修订需同步）。

## 路径口径裁定（有意偏差登记，F08R1-003）
- **原型/脚本**：`G:\CODEX\New Manga.workspace\FEA-08\prototype\`（非 Git，控制仓库体积；FEA 线 workspace 根级实践）；Task/证据登记路径与每个脚本 SHA-256。
- **报告**：`doc/research/FEA-08-source-capability.md`（研究类，归 research；不写入冻结设计目录）。
- **临时数据**：`G:\CODEX\New Manga.workspace\FEA-08\tmp\`（合成数据，运行后清理并留日志）。
- 与提案 :929 "experiments/ + doc/design/ + workspace/tasks/FEA-08" 的偏差即上述三点，理由：原型非生产资产、报告非设计冻结物、临时数据沿用 FEA 线既有 workspace 根级实践。
- **depends_on**：`FEA-01-FREEZE-1`（已存在 Task）；FEA-00 仅作依据引用，不入 depends_on。

## 目标（原型，不产出生产实现）
隔离环境（synthetic 非真实资料、临时卷/目录）验证并交付：
- **H4 稳定源 lease**：读取期间检测外部替换/重命名/删除/断连/共享写/内存映射写；同一已验证句柄/流一致读取并计算 digest；不可保证返回 unavailable。
- **H5 Windows 回收站**：IFileOperation/SHFileOperation 仅对合成路径操作；失败/取消/部分失败/中断不永久删除；receipt/恢复核对；负向原型。
- **H6 精确页面匹配**：按 :457/:469 口径的 golden fixtures（PDF 重生成、ZIP/CBZ 重编码/重复名、GIF 首帧、色彩/方向、加密格式）；无法唯一精确匹配只给候选。

## OUT
- 生产 Source/导入实现、Host `SourceAccessRegistry`/grant、Core schema/DB、UI 集成（FEA-09+）。
- 真实用户文件/真实库/AppData 写入；改变文件系统或回收站设置；对非合成路径发起回收。
- **禁止 `SHEmptyRecycleBin` 等清空类 API**（避免清空用户真实回收站）。
- 无证据的 PASS；承诺覆盖所有卷/格式。

## BLOCKED / 限制登记
- 无硬件的卷类型/云盘行为：LIMITED/UNAVAILABLE，交产品裁决。
- **测试 SQLite/DB 文件行为不在本卡范围**（H4/H5/H6 为文件系统/OS 层验证；Source DDL 未冻，耦合未冻结 schema 会污染结论）。
- H6 新格式：登记候选策略，不扩大自动匹配。

## 验收（待 scope-r2 冻结）
- [ ] **AC-1（H4）**：
  1. digest 取自打开时验证过的**同一句柄/流**；读取前后以句柄级身份（volume serial + file index）与 size/mtime 比对，一致才成立；
  2. 读取中途外部替换/写入的结果只能是 **unavailable 或完整旧 digest**，不得出现混合/部分新内容 digest 的假成功；杜绝 check 后按路径另开文件；
  3. 矩阵场景含"内存映射写"；不可证则该项 LIMITED/UNAVAILABLE。 <<PARTIAL: 待实施>>
- [ ] **AC-2（H5）**：判定操作 = 失败/取消/中断后目标仍在原路径（保留），或成功回收时存在于回收站且**还原后 digest 与回收前一致**；覆盖提案 :512–:514 分支（不可回收卷/策略、网络盘限制、路径被替换、结果未知、目录不可回收则保留且不得改调永久 rmdir）；**禁止清空类 API、仅合成路径**；合成 fixture 回收站条目测试后还原并删除（数量/结果入日志）或显式登记保留；"模拟中断"恢复判据 = receipt + 文件系统事实核对，不重发 destructive 操作。 <<PARTIAL: 待实施>>
- [ ] **AC-3（H6）**：按 :457/:469 二分"精确匹配/候选"并附判定所用 digest 类型（图片强 digest；文件夹成员身份+digest；容器成员内容 digest/规范解码像素 digest、尺寸、方向、唯一性；重复成员名保持独立 occurrence；感知 hash/OCR 仅候选；GIF 仅首帧；PDF 记录页码与渲染参数）；golden fixtures 与结果报告。 <<PARTIAL: 待实施>>
- [ ] **AC-4（交付完整）**：能力矩阵为二维结构 = 卷类型（NTFS 本地/USB/SMB/…）× 输入类别（单图/文件夹/ZIP/CBZ/PDF）逐项"现状/需新增"结论；每项标注证据来源 **measured/mocked/inferred**，**mock/推断不得记 PASS（上限 LIMITED(mocked)）**；技术报告含依赖/许可（如加密 ZIP/PDF fixture 需最小新依赖，二选一：登记许可+不进生产闭包，或预生成 fixture+SHA-256）；无生产代码改动。 <<PARTIAL: 待实施>>

## 交付与证据
- 原型/脚本：`G:\CODEX\New Manga.workspace\FEA-08\prototype\`（非 Git；hash 登记）。
- 报告：`doc/research/FEA-08-source-capability.md`；证据：`verification/FEA-08/**`（命令/EXIT/日志/矩阵/原型 hash）；Handoff：`doc/handoffs/FEA-08-*.md`。

## 待 scope-r2 确认
1. 隔离测试 SQLite：**否**（已写入 BLOCKED）。
2. USB/SMB 无硬件：接受 mock/LIMITED(mocked)（已写入 AC-4）。
3. H6 加密格式 fixture：预生成+SHA 或最小依赖（pyzipper MIT）二选一（已写入 AC-4）。
