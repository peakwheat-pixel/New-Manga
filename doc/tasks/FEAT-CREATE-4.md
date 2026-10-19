---
id: FEAT-CREATE-4
title: 创建作品/章节能力（4/4）——前端表单与接线（空书架可新建 → 导入不再阻断）
kind: feature
governance_version: 2
status: done
approval: coordinator_release_20261017_after_FEAT_CREATE_3
suggested_owner: Codex
owner: codex
reviewer: null
depends_on: [FEAT-CREATE-3]
base_commit: ae44d0047092c584c7f82cde203e229c56505156
branch: codex/FEAT-CREATE-4
worktree: G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-4
integration_commit: fcd509fd9
delivery_head: f10cde075b65f13b9d17f4ab4a8457b3cf1c104a
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEAT-CREATE-4
---

# FEAT-CREATE-4：前端表单与接线（创建能力 4/4）

## 来源
①`FEAT-CREATE-1` 冻结 M2-C1 **rev 2.8**（`CreateBook`/`CreateChapter` + Tauri `library_create_book`/`create_chapter`）→ ②`FEAT-CREATE-2` Core 实现（535 passed）→ ③`FEAT-CREATE-3` host 注册（production **51** 命令、source 107/0/1、packaged 12/0）。本段接前端。

## Acceptance Criteria
- [x] **AC1 空书架可新建**：空书架下 `+ 新建作品` **可用**（`IsEnabled=True`），点击出现创建表单（标题必填）；提交经 `library_create_book` 成功后在书架**出现该作品**。
- [x] **AC2 可建章节**：选中作品后可**新建章节**（经 `create_chapter`），章节出现在章节列表，且可在阅读器进入。
- [x] **AC3 导入不再阻断**：存在作品/章节后，`导入作品` 入口**转为可用**（沿用 P19-UI-FIX-2 的反馈口径：有目标→选择器；无目标→可见原因）。
- [x] **AC4 错误与安全**：失败走 §5.10 封闭投影（稳定类别 + 脱敏文案），**不得**显示路径/Secret/原始异常；重复标题**允许**（契约 L616）、**不设长度上限**（L614）。
- [x] **AC5 测试**：新增前端测试（空书架可建、提交调用正确命令、失败显示脱敏文案、重复允许）；全量实际基线 **278** 不回归（本次 **285 passed**，增加 7）；`npm run build` exit 0。任务原文写 **274** 与当前 worktree 实测基线相差 4，按日志实测记录。
- [x] **AC6 真实 GUI 复验（必做）**：重建产品（`npm run build` → `build_sidecar.ps1 -Force` → `cargo build`，**校验 bundle==resource hash 一致**）+ 隔离 `NEWMANGA_DATA_ROOT`（复制 `%APPDATA%` 的 `catalog`/`data` + 空 `derived`，**不得改用户真实数据**）→ UIA 实测：`+ 新建作品` 可用 → 建作品 → 建章节 → 导入入口转可用；留 GUI 证据。
- [x] **AC7**：实现 commit + **Handoff** + Canonical Evidence（`status: done`；BL-15/17/19/16/18）已固定。独立 Review 与 Coordinator 集成尚未完成。

## 允许 / 禁止
- 允许：`apps/desktop/frontend/**`、本 Task、`doc/handoffs/FEAT-CREATE-4-*.md`、`verification/FEAT-CREATE-4/**`。
- 禁止：改契约、`src/**`、`apps/desktop/src-tauri/**`（Core/host 已交付；如需改动**先上报**）、Schema/迁移/依赖；改 STATUS/PLAN；碰用户 19 项 dirty；**不得**用前端假数据伪造"创建成功"。

## 依赖、风险与阻塞
- 前置：FEAT-CREATE-3（done）。**后继**：P19 的 AC2 主流程可开始。
- 风险：前端自造 wire/字段 → 必须以 §5.10 为准；伪造成功 → 明确禁止。

## 交付与运行记录
- 2026-10-17 Coordinator 释放（dsh, epoch 6）。
- Owner：Codex；branch=`codex/FEAT-CREATE-4`；worktree=`G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-4`；base=`ae44d0047092c584c7f82cde203e229c56505156`。
- 实现 `delivery_head`=`f10cde075b65f13b9d17f4ab4a8457b3cf1c104a`；Handoff=`doc/handoffs/FEAT-CREATE-4-f10cde075.md`；Task 状态=`in_review`。没有独立 Review、push、merge 或 STATUS/PLAN 修改。
- 全量 `npm test`：28 files / 285 passed / 0 failed / 0 skipped；实测基线 278 passed，净增 7。`npm run build` exit 0。
- AC6 真实 GUI/UIA：侧车 build、`cargo build` 成功；5/5 bundle/resource SHA-256 匹配；隔离数据根里创建作品、章节、进入阅读器、导入流程可用。`%APPDATA%` 源 `catalog` / `data` 树哈希前后相同。
- 任务指定“既有 274”与当前 worktree 的全量实测基线 278 不一致；不掩盖差异，证据同时保留两份完整日志。

## Canonical Evidence

`commit` 使用 `git rev-parse` 的完整提交值；`sha256` 按当前交付 worktree 的磁盘字节计算。每项均校验 `git cat-file -e <commit>:<path>` 包含性；类目仅使用 `CANONICAL` / `SOURCE_PIN`。主仓库字节 parity 留给 Coordinator closeout（BL-16），此 Task 不声称已验证。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EVID-CREATE4-RESULTS | AC1–AC7 | verification/FEAT-CREATE-4/ac-results.md | f10cde0752b0b47206fe3812e891353242f1be25 | b4f807db302e284b679d34828a37316f0957d967c58eb36d25b4384cd1f9345e | CANONICAL |
| EVID-CREATE4-BASELINE | AC5 | verification/FEAT-CREATE-4/frontend-npm-test-baseline.log | f10cde0752b0b47206fe3812e891353242f1be25 | 64b58ddd0246e6436d2d4430b3a6183325afa52aa6cc6b057525f46d7d7f8cf4 | CANONICAL |
| EVID-CREATE4-TEST | AC5 | verification/FEAT-CREATE-4/frontend-npm-test-delivery.log | f10cde0752b0b47206fe3812e891353242f1be25 | 9a096aa74b4746a193818bc6f22afa4ae7962597ad6d5b6f73fe2f47e5c8b57e | CANONICAL |
| EVID-CREATE4-FRONTEND-BUILD | AC5/AC6 | verification/FEAT-CREATE-4/frontend-npm-build-delivery.log | f10cde0752b0b47206fe3812e891353242f1be25 | f7b7409c2025d8dc8955757b64eae1b99301aa886d11674d22b817cfbbc16ab1 | CANONICAL |
| EVID-CREATE4-SIDECAR | AC6 | verification/FEAT-CREATE-4/sidecar-build.log | f10cde0752b0b47206fe3812e891353242f1be25 | dc51309c6a559d72924e0d860a612feab8aa79b3c1fcc0552b3abb0bf929dc0a | CANONICAL |
| EVID-CREATE4-CARGO | AC6 | verification/FEAT-CREATE-4/cargo-build.log | f10cde0752b0b47206fe3812e891353242f1be25 | e1bcc1317afa35dbe2f6ae9429cb5ec361df3179cc5027e643b5d7ce67bae0b6 | CANONICAL |
| EVID-CREATE4-HASH | AC6 | verification/FEAT-CREATE-4/sidecar-resource-hash.json | f10cde0752b0b47206fe3812e891353242f1be25 | badd10979cf6950a2e6f63fd547c59e4127ccc32009815c8ebfd36094c7522f7 | CANONICAL |
| EVID-CREATE4-ISOLATION | AC6 | verification/FEAT-CREATE-4/isolation-copy.json | f10cde0752b0b47206fe3812e891353242f1be25 | 1fbddc38bff956a1f80a9121cb5dd8d8ec556755bf04a9105a5080b3967ecc67 | CANONICAL |
| EVID-CREATE4-UIA-RUN | AC1–AC3/AC6 | verification/FEAT-CREATE-4/gui-r5/uia-run.log | f10cde0752b0b47206fe3812e891353242f1be25 | b309f7e591bc3fc8c538b7fbe4926e51001a2515c6a4d7d5f09f5ea5da4b2015 | CANONICAL |
| EVID-CREATE4-UIA-EMPTY | AC1/AC6 | verification/FEAT-CREATE-4/gui-r5/initial-bookshelf.uia.txt | f10cde0752b0b47206fe3812e891353242f1be25 | c5831e5283247d1a9162e77839715299d74ede007c6953b1a39d9ce0abe6787d | CANONICAL |
| EVID-CREATE4-UIA-BOOK | AC1/AC6 | verification/FEAT-CREATE-4/gui-r5/create-book.uia.txt | f10cde0752b0b47206fe3812e891353242f1be25 | f50363461c5317a560f6e4be49bdd89a93d7068cb1dca89c21d40be283d7b019 | CANONICAL |
| EVID-CREATE4-UIA-CHAPTER | AC2/AC6 | verification/FEAT-CREATE-4/gui-r5/chapter-created.uia.txt | f10cde0752b0b47206fe3812e891353242f1be25 | 39ea1d92520e3dd051e8dde72881d99d6659bd94f9927cb913ae6a6e2deaf365 | CANONICAL |
| EVID-CREATE4-UIA-IMPORT | AC3/AC6 | verification/FEAT-CREATE-4/gui-r5/import-available.uia.txt | f10cde0752b0b47206fe3812e891353242f1be25 | f6b6555d7b5f7bab841d1f5f36645eb342b7684888c47d67155985dedb7a23aa | CANONICAL |
| EVID-CREATE4-ISOLATED-DB | AC1/AC2/AC6 | verification/FEAT-CREATE-4/isolated-records-check.log | f10cde0752b0b47206fe3812e891353242f1be25 | 967027b50e93ef24b9daf124073ae0533ba9671b07ceffd36708a963c52ba679 | CANONICAL |
| EVID-CREATE4-APPDATA | AC6 | verification/FEAT-CREATE-4/source-preservation-check.json | f10cde0752b0b47206fe3812e891353242f1be25 | dcf824b91666b1988b61e57e3f08c8d4942195b3c58182956e07882ea38984d1 | CANONICAL |
| EVID-CREATE4-HANDOFF | AC7 | doc/handoffs/FEAT-CREATE-4-f10cde075.md | 7141c7f0ee825ed211e5e2646d19c9d0de6f9837 | 1828ff39f6dfa3302cbaf48a8ba9adad13a0c1e8b220e7c3b93e11109a0e3b2f | CANONICAL |

## Resource Manifest

由 `GOV-DEBT-CLEANUP-2` AC6 补录；来源 `verification/P09-GOVERNANCE-DEBT-20261019/
missing-manifest-resource-facts.md`（实测）。**本表不构成任何删除/移动/归档授权**。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task worktree | `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-4` | `PRESERVE_UNKNOWN` | `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-4` | `c4697526c430cde233e0ffc7936f840ccd152323847b9986d7ffe5243eee04ac` | 实测存在且已注册；dirty=0，untracked=0；HEAD 已在当前分支历史中 |
| task env | 无 | `NOT_APPLICABLE` | — | `c4697526c430cde233e0ffc7936f840ccd152323847b9986d7ffe5243eee04ac` | 实测 `New.Manga.workspace/task-envs/FEAT-CREATE-4` 不存在 |
| agent output | 无 | `NOT_APPLICABLE` | — | `c4697526c430cde233e0ffc7936f840ccd152323847b9986d7ffe5243eee04ac` | 实测 agent-output（coordinator 与根）均不存在 |
| evidence | `verification/FEAT-CREATE-4/` | `PRESERVE_REFERENCED` | `verification/FEAT-CREATE-4/` | `c4697526c430cde233e0ffc7936f840ccd152323847b9986d7ffe5243eee04ac` | 目录存在，28 个文件；未登记文件见 evidence-dir-classification.md |

## Closeout Record

- 关闭：2026-10-17（dsh）。Reviewer=dsh（approved）。合并 cd509fd9（--no-ff，无冲突）。
- 复核要点：前端真调 library_create_book×11 / create_chapter×9（形状符 §5.10）；空书架 + 新建作品 **GUI 实测 IsEnabled=True**；前端 **278 passed**（基线 274 → +4）；isolation_copy=PASS source_unchanged=true（**用户真实数据未变**）；构建链（npm build → sidecar 重建 → cargo）完成。
- **DAG 效果**：创建能力四段链（FEAT-CREATE-1..4）全部 done → **P19 的 AC2 主流程具备真实前置能力**。
