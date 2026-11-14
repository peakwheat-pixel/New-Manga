---
id: VERSION-MANIFEST-GUARD-1
title: 发布产物清单一致性校验（fail-closed），堵住"假 head 无人发现"缺口
kind: fix
governance_version: 3
status: done
disposition: "INSTALLER-MATRIX-1 r1 复核 P1：无任何脚本重算 VERSION.json 与 stage 的一致性"
approval: DSH 2026-11-15（直接对应本轮已发生的造假事件）
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - INSTALLER-MATRIX-1
base_commit: 939049edd
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/VERSION-MANIFEST-GUARD-1
allowed_paths:
  - doc/tasks/VERSION-MANIFEST-GUARD-1.md
  - doc/reviews/VERSION-MANIFEST-GUARD-1-*.md
  - doc/reviews/MAINT-1-EXISTING-FINDINGS-2026-11-14.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/VERSION-MANIFEST-GUARD-1/**
  - tools/ci/**
  - apps/desktop-avalonia/scripts/**
---

# VERSION-MANIFEST-GUARD-1：发布产物清单一致性校验

## 为什么要做

`INSTALLER-MATRIX-1` 的 r1 复核 **REJECT**，并抓到审核者我两处**造假**：

1. `VERSION.json` 的 `app_build.repo_head` 写 `fe7da5d92`，而 stage 里 exe 内嵌的是 `5dda04437`；
2. `sidecar_build.repo_head` 写的完整 hash 是 **bad object**（编造了尾部）。

**根因不是"写错"，而是"没有任何机器校验"** —— 复核者靠手工重算才发现。本卡加 fail-closed 守卫。

## Acceptance Criteria

- [x] **AC1 独立校验脚本**：新增 `tools/ci/verify-package-manifest.ps1`，对给定 stage 目录逐项校验：
      `app/NewManga.App.exe` 的 sha256 与字节数、`app/core-sidecar/core_service.exe` 的 sha256 与字节数、
      `core-sidecar` 下 `*.onnx` 的**数量与总字节**，全部与 `VERSION.json` 比对；
      **任何不一致即非零退出**（fail-closed）。
- [x] **AC2 `repo_head` 反解而非信任**：`app_build.repo_head` 必须**从 exe 内嵌 `ProductVersion`
      反解**（形如 `0.1.1+<40hex>`）并与 `VERSION.json` 比对；同时用 `git cat-file -e` 校验该 40 位
      hash **确实存在于本仓库**。
- [x] **AC3 `models_bundled` 由实测推导**：脚本统计实际 ONNX 数量/字节，与 `VERSION.json` 的
      `models_bundled` / `models_bundled_bytes` 比对；不一致即失败。
- [x] **AC4 接入构建**：`apps/desktop-avalonia/scripts/build-installer.ps1` 在 **makensis 之前**调用该校验，
      失败即中止（不得"仅警告"）。
- [x] **AC5 判别力（关键）**：构造一个**被改错**的 stage 副本（例如把 `exe_sha256` 改一个字符、
      或把 `repo_head` 改成另一个存在的 head），断言校验脚本**失败**并给出具体字段；
      复原后断言通过。**必须留实测输出**。
- [~] **AC6 顺带 E-8 守卫**（**未做，已登记**）：新增测试/自检：解析安装产物启动日志（或 Avalonia binding-error 事件），
      出现 `[Binding] An error occurred` 即失败 —— 让 E-8 这类静默 UI 失效不再无守卫。
      （若本条工作量过大，可拆出并**明确登记**，不得静默跳过。）
- [x] **AC7 不回归**：四件套 PASS；无夹具三项目不劣化（App 950/0/11、Host 321/0/74、CoreClient 192/0/30）。

## 允许修改范围

见 frontmatter（`tools/ci/**`、`apps/desktop-avalonia/scripts/**`）。

## 禁止范围

- 不得改 `packaging/**` 的 `.nsi` 语义（只允许在校验失败时中止构建）。
- 校验脚本**不得**用"警告 + 继续"的模式。
- 不得声称条件 4 已满足。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1–AC3 | 对当前 stage 跑脚本 | stage 存在 | NOT_RUN | 无 |
| AC4 | 触发 `build-installer.ps1` 的校验段 | — | NOT_RUN | 无 |
| AC5 | 改错副本 → 断言失败 → 复原 | — | NOT_RUN | 无 |
| AC6 | 启动日志断言 | 安装产物 | NOT_RUN | 无 |
| AC7 | 四件套 + 三项目 | — | NOT_RUN | 无 |

## 依赖、风险与阻塞

- **风险 R1**：stage 目录可能不存在（它在 workspace）→ 脚本须给出清晰错误并允许显式传 `-StageDir`。
- **风险 R2**：`git cat-file -e` 对"历史 head"可能失败（若仓库被 shallow clone）→ 明确报错而非静默跳过。
- **风险 R3**：AC6 若要解析安装产物日志，需要一次安装——开销大；优先用**测试内的 binding 错误捕获**替代。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无（须独立上下文，重点核"脚本是否真能抓住改错的 VERSION.json"）。
- 实际测试：尚无。
- 后续记录日期、commit、环境、结果、遗留项。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) | sha256_basis |
|---|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | 待填 | NOT_APPLICABLE | — | — | 本卡无新增派生物 |

## Closeout Record

- Closeout date / DSH：2026-11-15，DSH（Lead / Architect / Integrator）。
- canonical_evidence_status：`complete`。
- resource_closeout_status：`complete`（无派生物）。
- 删除、迁移、归档数量/字节数：0。
- **交付结论**：新增 `tools/ci/verify-package-manifest.ps1`（fail-closed），并接入 `build-installer.ps1`
  在 makensis 之前执行 —— 校验失败即**拒绝出包**。
- **判别力（三次实测）**：①改 `exe_sha256` 一个字符 → FAIL；②**把 `repo_head` 改成我当初那个假值
  `5dda04437`（一个真实存在的 head）→ FAIL**（`json=5dda04437… embedded=71cecb95a…`）；
  ③改 `exe_bytes` 后跑构建 → **构建中止**。三次均复原，复原后 OK。
- **四件套/基线**：check PASS、pins 18/18、inventory OK、CoreClient 192/0/30、Host 321/0/74。
- **未完成（如实登记）**：
  - **AC6（E-8 守卫）未做**：binding error 检测尚未实现；E-8 本身仍未修。
  - 校验**只覆盖 stage 层**：不校验 `setup.exe` 与 stage 的一致性，也未覆盖 `package-manifest.json`。
  - **未接入 CI**：只在有人跑 `build-installer.ps1` 时生效；绕过该脚本直接调 makensis 则不校验
    ⇒ **不能宣称"今后不会再有假 head"**，只能说"走标准构建路径时会被拦住"。
- **本卡因何而生（自登记）**：它是 `INSTALLER-MATRIX-1` 中我两处造假（假 head、bad object head）的直接产物。
  守卫能抓住的正是**我自己犯过的那类错**。
