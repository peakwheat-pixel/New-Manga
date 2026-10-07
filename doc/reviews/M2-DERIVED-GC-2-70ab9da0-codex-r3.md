---
task_id: M2-DERIVED-GC-2
reviewer: Codex（非作者）
reviewed_head: 70ab9da0
evidence_tip: 18ad2335
base_commit: 7c19b3d6
decision: changes_requested
findings: 4
conditions: 3
---

## 复核判定

- **F-01 — NOT FIXED（P1）**：WAL 权威复核已改为普通只读连接，但初始化仍可能把结构不符的已知表当作自有空 catalog 绑定。[_read_namespace_row](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/catalog_store.py:150>) 将 `OperationalError` 一概当成“没有绑定表”；后续检查只核表名与行数，没有验证表结构（[第 267 行](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/catalog_store.py:267>)、[第 286 行](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/catalog_store.py:286>)）。例如已有空表 `resource_catalog(x)` 会通过检查；`CREATE TABLE IF NOT EXISTS` 不会修正它，却会继续创建其他表并尝试绑定（[第 204 行](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/catalog_store.py:204>)）。这不符合“只接受新建或空的自有 catalog”。  
  新 WAL 用例也不一定覆盖锁内权威复核：它允许 immutable 探针看到“表不存在”（`probe_count is None`），初始化可在预检阶段就拒绝，未必走到普通只读复核（[测试第 368–405 行](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/tests/m2_resource_channel/test_catalog_authority.py:368>)）。建议校验已知表的实际列结构，并补充坏 schema 被拒绝且零写入的用例；WAL 用例应让主库已有表结构、仅未 checkpoint 的行在 WAL 中。

- **F-02 — NOT_VERIFIED（P2；实现有修，测试未证明）**：打开后的 reparse 与 final-path 核验确实存在（[handle_resolver.py 第 556–561 行](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/handle_resolver.py:556>)）。但新增用例只断言最终抛错且不是预检错误消息，仍无法区分“打开失败”和“打开后核验拒绝”；第 452 行的 `with_name(...) is not None` 恒真（[测试第 421–452 行](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/tests/m2_resource_channel/test_handle_resolver.py:421>)）。因此竞态第二道防线尚未被该测试判别。建议让测试明确观察到 post-open 核验被调用，或断言其专属拒绝结果及句柄关闭。

- **F-03 — FIXED（本机策略与证据口径）；分发 Gate 执行仍 NOT_VERIFIED**：G7 现在明确说明原位改写不会改变 OS file identity，安全策略依赖 UNKNOWN 时禁用 sweep；旧 catalog 的拒绝策略和分发前阻断 Gate 也已写明（[g7-enablement-boundary.md 第 21、23 行](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/g7-enablement-boundary.md:21>)）。真实 Core subprocess 用例断言未绑定旧 catalog 启动失败、旧行保留且没有 namespace 绑定表（[test_catalog_authority.py 第 427–479 行](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/tests/m2_resource_channel/test_catalog_authority.py:427>)）。矩阵也把“本机单版本机制 PASS”与“分发迁移 Gate=阻断、NOT_VERIFIED”分开记录（[g1-g7-matrix.md 第 86–88 行](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/g1-g7-matrix.md:86>)）。分发验收尚无执行证据，必须继续作为发布前阻断条件，不能记 PASS。

- **F-08 — NOT_VERIFIED（P2；Python 回归已补，安装包来源未证）**：pytest 日志绑定完整 commit `70ab9da0`，记录 `1931 passed, 1 skipped`，skip 原因为既有 dev venv ML 栈豁免（[pytest-full.log 第 1、427 行](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/pytest-full.log:427>)）。AC5 第三轮日志有运行时 HEAD、安装包 SHA，并保留唯一 CS-L1 FAIL（[third-round-full-stdout.log 第 36、80 行](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/packaged-ac5-run/third-round-full-stdout.log:36>)）。但这些记录没有把 sidecar/NSIS 的构建 HEAD 与该安装包 SHA 连起来；矩阵第 17 行称按 `70ab9da0` 重建，第 84 行仍记 sidecar 构建 HEAD 为 `7f652473`（[g1-g7-matrix.md 第 17、84 行](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/g1-g7-matrix.md:17>)）。因此安装态结果不能独立证明运行的是返修后的 Core。建议补充可审计的构建命令、HEAD 与产物 SHA 对照，再执行 packaged 验收。

## 范围纪律

**通过。** `7c19b3d6..70ab9da0` 的 15 个变更路径都在 Task 的 `allowed_paths` 内：两个允许的生产文件、允许的测试文件、Task/Review 文档及本 Task 的 verification。该范围未触及禁止的产品 schema、ports、React/UI、acceptance/ac1 bridge、公共 API 语义、依赖或 packaging spec/build 文件。`70ab9da0..18ad2335` 在 `src/apps/tests/packaging` 下无差量，后续差量是文档与证据。未发现 F-04–F-07、F-09 回潮；未重跑这些测试。

## Verdict 与下一步

**`changes_requested`**：F-01 仍有初始化误绑定路径；F-02 的竞态测试和 F-08 的安装态构建来源仍未验证。F-03 的分发 Gate 虽已正确登记，执行证据仍是发布前阻断条件。

建议 ZCode 补上坏 schema 的拒绝与零写入测试、让 F-02 用例确实命中打开后核验，并归档返修 commit 到 sidecar/安装包 SHA 的构建链证据后再提交复核。

## 只读核查记录

使用 `git -c safe.directory="G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode" -C "G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode"` 执行只读 Git 命令。直接 `git -C` 首次被 dubious-ownership 保护拦截；随后只用命令级 `-c` 重试，未改全局配置。

- `rev-parse 70ab9da0 18ad2335 HEAD`：确认代码 commit、证据 tip 与当前 HEAD。
- `diff --name-status 7c19b3d6..70ab9da0`：15 个变更路径，均在允许范围内。
- `show` Task、实现、相关测试、G7 文档、矩阵及 raw 日志：核对上述实现和证据。
- `diff --check 7c19b3d6..70ab9da0`：无输出，检查通过。
- `diff --name-status 70ab9da0..18ad2335 -- src apps tests packaging`：无差量。
- `status --short`：看到若干未提交的 Tauri 生成文件变化；它们不在本次固定 commit 范围内，未触碰。

未运行 pytest、Windows 竞态复现或打包 runner；遵从本轮只读核查要求，测试结果仅审阅已归档日志。