---
id: FEA-09
title: 引用源与导入（Core source schema/read/cache、Host SourceAccessRegistry/授权、导入 plan/receipt）
kind: implementation
governance_version: 3
status: proposed
approval: pending_scope_review（草案；未冻结前不得实施）
suggested_owner: codex
owner: 未指派（scope review approved 后由 DSH Appointment）
reviewer: pending scope review（独立上下文；scope-r1 待派发）
depends_on:
  - FEA-08
  - FEA-01-FREEZE-1
base_commit: 待 scope 冻结时登记（草案基于 2870a9fa5 + FEA-08 收口）
branch: main
worktree: G:\CODEX\New Manga
delivery_head: 未开始
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-09
allowed_paths:
  - doc/tasks/FEA-09.md
  - doc/handoffs/FEA-09-*.md
  - doc/reviews/FEA-09-*.md
  - verification/FEA-09/**
  - src/application/importing/
  - src/application/resource_channel/
  - src/infrastructure/resource_channel/
  - src/bootstrap/core_assembly.py
  - src/bootstrap/core_service.py
  - src/infrastructure/sqlite/
  - apps/desktop-avalonia/src/NewManga.Host/
  - apps/desktop-avalonia/tests/
out_of_scope:
  - UI V2 视图/ViewModel 写域（FEA-14 系列）；本 Task 只经 Core→Host 提供可观察结果与进程内断言
  - 生产 Schema DDL、共享契约/C-04b 等冻结字节改动（需 DSH 另行裁决）
  - 真实用户数据/真实外部卷/真实永久删除流程（FEA-12 与 D 流程）
  - `G-DELETE-IMPL`、FEA-11 变化/重定位、备份/迁移（FEA-13）
  - push
---

# FEA-09 — 引用源与导入（scope 草案，待独立 scope review）

## 依据

- 提案 S3 `FEA-09` 行（:648）、写域（:930）、可观察 AC（:1040）、§15.4 出口、§15.7 追溯（:457/:469/:512–:514）；[AD-003](../AD-003_REFERENCED_SOURCE_ARCHITECTURE.md)（引用源、独立授权面、`SourceAccessRegistry`、Windows 回收站桥、回退开关）。
- FEA-08 已闭环（`verification/FEA-08/**`）：H4（strict 拦截/混合流不可证）、H5（回收站保留/还原语义）、H6（精确匹配判据）、能力矩阵与原始门禁证据；本 Task **不得**回退或重新解释 FEA-08 的判定边界，只消费其结论。
- Gate：`G-CONTRACT` 已 CLOSED（STATUS 2026-11-01）；`src/application/importing/` 为既有包路径但当前无 `.py` 源文件（本草案按提案 :930 登记，scope review 须核对实际包布局后再冻结）。

## 范围（草案）

1. **Core source schema/read/cache**：引用源登记（locator/identity facts/authorization generation）、读取路径与可再生产物（cache key 至少含 SourceVersion/Entry/decoder 版本/参数）；不复制永久全尺寸原件。
2. **Host SourceAccessRegistry/授权**：Host 私有、**持久化**的授权面 + 新 `source-read` grant；旧一次性 `ImportPages` grant（≤300 秒、直属成员、进程内）不得复用为持久通行证（AD-003 §3.5）。
3. **导入 plan/receipt**：五类输入（单图/文件夹/ZIP/CBZ/PDF）的 plan/receipt、失败项原因、可跳过、取消语义（已提交保留、未提交不出现）、按项目进度与成功/失败/跳过汇总。
4. **完整性谓词（F-11/F-38）**：旧“完整页”谓词要求 managed ref 的路径必须适配引用源；五读路径/半写负例继续成立；对 source 原字节零写入。
5. **回退**：关闭引用导入后 managed 双读保持；新 Schema 禁旧写。

## Acceptance Criteria（草案，scope review 冻结）

- [ ] **AC-1（草案）**：五类输入（单图/文件夹/ZIP/CBZ/PDF）分别建立成功/不支持/损坏 fixture；每类给出可复现判定与证据。
- [ ] **AC-2（草案）**：PDF 按页码、文件路径按**自然数字排序**（不是字典序），并用边界 fixture（1/2/10/100）断言。
- [ ] **AC-3（草案）**：重复归档名按 **occurrence 保序**独立处理，不得仅用 digest 合并或丢失 occurrence；给出重复名/重复同图负例。
- [ ] **AC-4（草案）**：加密项目支持密码重试；**日志与持久快照不得出现明文密码**；失败项有明确原因且可跳过。
- [ ] **AC-5（草案）**：取消后已提交项目保留、未提交项目不出现；按当前项目显示可观测进度并汇总成功/失败/跳过。
- [ ] **AC-6（草案）**：每项以**隔离数据**断言 Core→Host 可观察结果，且 source 文件原字节（hash/mtime）不变；共享源项目结果独立。
- [ ] **AC-7（草案）**：完整性谓词五读路径/半写负例在引用源路径下成立；旧 managed 双读保持；新 Schema 禁旧写测试。
- [ ] **AC-8（草案）**：证据=fixture + 隔离断言 + 独立 Review + DSH 集成验证；不触真实用户数据；不 push。

## 待 scope review 裁决

1. AES ZIP 是否引入 pyzipper（MIT；仅 fixture/测试闭包，不进生产闭包）或预生成 fixture。
2. `SourceAccessRegistry` 持久化载体与 Schema 边界（SQLite 表 vs Host 私有存储），须先确认是否触碰共享 Schema 冻结。
3. UI 可观察路径：以现有 V2 页面经 Host IPC 断言，或仅 Core→Host 进程内断言（本 Task out_of_scope 已排除 UI 写域）。
4. IFileOperation per-item sink 与真实取消的验证方式（LIMITED 或真机）。
5. `src/application/importing/` 当前无源文件——按拟议新包冻结，还是并入 `resource_channel`；scope review 必须给出结论。

## 验证方式（草案）

- Gate：build 0w/0e、全量测试不减少、check/vpins、`src_changes` 仅限 allowed_paths、旧 FEA-06 四 PNG 不变、未 push。
- 隔离证据：Core→Host 断言日志、fixture SHA、source bytes hash 前后一致、密码不落日志的审计；TEMP/证据外置、不写真实用户数据。
- 生命周期：scope review（独立上下文）→ DSH 冻结 → 实现 → 独立 impl Review → DSH 集成验证 → done。

## Closeout Record

- 未开始（proposed）。
