---
task_id: M2-TA2C-TOOLING-GAPS
author: ZCode
recipient: Codex
base_commit: f3d684eb767414a3c5ac010f7920657204cc9336
delivery_head: a164e414e8ff62940229d60d4dc046f89308b8b3
status: in_review
---

# Handoff：M2-TA2C-TOOLING-GAPS

## 交付结果

TA2C DSH r2 候选 P3-6/P3-10 的工具清算已按冻结方案完成（基线 `f3d684eb`，实现 HEAD=`a164e414e8ff62940229d60d4dc046f89308b8b3`，分支 `agent/zcode/M2-TA2C-TOOLING-GAPS`，worktree `G:/CODEX/New Manga.worktrees/M2-TA2C-TOOLING-GAPS-zcode`）：

- **AC1（P3-6① source_url 主机白名单）**：`test_assets/comic_golden_suite/tools/assets.py` 新增 `SOURCE_URL_HOSTS` 显式常量与 `validate_source_url()`，`load_manifest` 对每个 case 的 `source_url` 施加校验（scheme 必须 https、host 在白名单、无嵌入凭据、端口仅 443/缺省），违规 `ValueError`（fail-closed）。白名单以 cases.json 实测 host 集合冻结：`{"www.peppercarrot.com", "huggingface.co"}`（47 + 21 cases；编排说明中预期的 `manga109.github.io` 实测不在任何 case 的 `source_url` 中，未纳入）。无网络请求，纯解析校验。
- **AC2（P3-10① checksum_inventory 运行时消费）**：新增 `verify_benchmark_source_inventories()`，`verify`/`list`/`missing` 三个命令路径统一消费 `benchmark_sources[*].checksum_inventory`：非空仓库根相对路径做安全路径校验（拒绝 `..`、盘符、绝对路径、symlink）+ 存在性校验；`local_asset_inventory.json` 条目沿用 `verify_inventory_files()` 既有逐文件 SHA-256 复核，其他审计清单（`verification/M2-TA2C/ko-webtoon-audit.json`）按存在性消费。输出新增 `BENCHMARK_INVENTORY\tchecked=N failures=M` 与 `INVALID_BENCHMARK_INVENTORY` 行；failures 使命令返回 1。`download` 不变。
- **AC3（P3-10②③④ 判别性断言）**：`tests/m2_test_assets/test_catalog.py` 新增参数化测试 `test_benchmark_checksum_inventory_paths_exist`（覆盖全部 4 个非空 checksum_inventory source）与 `test_ko_sfx_dialogue_cleaned_webtoon_inventory_semantics`。侦察确认 `ko_sfx_dialogue_cleaned_webtoon` 的 checksum_inventory **非 null**（= `verification/M2-TA2C/ko-webtoon-audit.json`），与编排说明预期的 null 不同，按 Task 预案"若非 null 则断言存在"处理并注释 README 的 null 语义。判别演示：`test_benchmark_inventory_missing_path_detection_demo`（坏路径 → failures 非空，红在受控内）+ 直接调用演示日志 `08-ac3-detection-demo-direct-call.log`。
- **AC4（P3-6② 目录命名快照）**：未重命名任何盘上目录；O01–O08、K11–K13 共 11 个 case 在 cases.json 新增 `naming_note` 注释性字段（02_open_ 与 02_public_ 两族前缀差异记为已知观察，统一留待后续）；`test_ko_ground_truth_directory_naming_snapshot` 锁定现状前缀（O01–O08 → `韩漫_KO/02_open_ground_truth_peppercarrot/`、K11–K13 → `韩漫_KO/02_public_ground_truth_peppercarrot/`、JA J38–J40 → `日漫_JA/02_open_ground_truth_peppercarrot/`）防漂移。cases.json 既有字段值零变更（语义级验证：剥离 naming_note 后与基线 JSON 全等）。
- **AC5**：diff 仅触及 4 个允许路径（assets.py、cases.json、test_catalog.py、README.md）+ 本 Task 文档/日志；`git diff --check` EXIT=0；`pytest tests/m2_test_assets` 34 passed EXIT=0；所有命令日志带 shell 头/HEAD/EXIT 尾。

提交列表：

1. `19f8200e5ab5ee9795e9d7660d352108aed034cc` — chore: claim task（status in_progress、base_commit 固定）
2. `a164e414e8ff62940229d60d4dc046f89308b8b3` — feat: 白名单 + inventory 运行时消费 + 测试 + README（delivery head）
3. 交付 commit（本文档 + Task 回填 + verification 日志，文档性，不含代码）

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| 侦察：host 集合冻结 | python 枚举 cases.json 全部 source_url host | 系统 Python 3.14.6；HEAD=`a164e414` | PASS（2 host：huggingface.co 47、www.peppercarrot.com 21；4 个非空 checksum_inventory） | `verification/M2-TA2C-TOOLING-GAPS/raw/01-host-whitelist-reconnaissance.log` |
| AC1 红演示（旧代码不拒绝） | `git show f3d684eb:…/assets.py` 加载旧 `load_manifest` + 注入 `https://evil.example/x` 的 tmp manifest | 系统 Python 3.14.6；旧版=`f3d684eb`（固定基线），新版=工作区 | PASS（RED：旧版无错误接受；GREEN：新版 `ValueError: source_url host is outside the approved whitelist: K01`） | `raw/02-ac1-red-demo-old-vs-new.log` |
| AC1 单测 | `pytest tests/m2_test_assets -v`（参数化 2：evil.example https、同 host http 降级） | 系统 Python 3.14.6 + pytest 9.1.1；HEAD=`a164e414` | PASS（34 passed） | `raw/06-ac5-pytest-full.log` |
| AC2 verify ja smoke | `python test_assets/comic_golden_suite/tools/assets.py verify --language ja --level smoke` | 同上；HEAD=`a164e414` | PASS（EXIT=0，READY=10，INVENTORY checked=92 missing=0 failures=0，BENCHMARK_INVENTORY checked=4 failures=0） | `raw/03-ac2-verify-ja-smoke.log` |
| AC2 verify ko smoke | `python test_assets/comic_golden_suite/tools/assets.py verify --language ko --level smoke` | 同上 | PASS（EXIT=0，READY=10，同上汇总行） | `raw/04-ac2-verify-ko-smoke.log` |
| AC2 list 输出 inventory 状态 | `python test_assets/comic_golden_suite/tools/assets.py list --level smoke` | 同上 | PASS（EXIT=0，READY=20，BENCHMARK_INVENTORY checked=4 failures=0） | `raw/05-ac2-list-benchmark-status.log` |
| AC3 参数化存在性断言 | `pytest tests/m2_test_assets -v`（4 个非空 inventory source 逐一 `is_file()`） | 同上 | PASS | `raw/06-ac5-pytest-full.log` |
| AC3 判别演示（坏路径→红） | 直接调用 `verify_benchmark_source_inventories`，ko_sfx 条目指向不存在路径 | 同上 | PASS（REAL checked=4 failures=[]；BROKEN checked=3 failures=[missing: verification/M2-TA2C/does-not-exist.json]） | `raw/08-ac3-detection-demo-direct-call.log` |
| AC4 naming_note + 快照断言 | cases.json 文本级插入 11 个 naming_note；剥离字段后与基线 JSON 全等比对；pytest 快照测试 | 同上 | PASS（22 insertions/11 deletions，语义零变更） | `raw/06-ac5-pytest-full.log` + `git diff`（交付 commit） |
| AC5 范围与空白检查 | `git diff --check`；`git status --short`；`git ls-files -o --exclude-standard` | HEAD=`a164e414` | PASS（diff --check EXIT=0；改动仅 4 个允许路径；未跟踪文件仅本 Task 日志；复制素材全部命中 `日漫_JA/.gitignore`、`韩漫_KO/.gitignore`） | `raw/07-ac5-diff-check-and-scope-proof.log` |

未运行项：

- `tests/m2_acceptance` 未运行（Task 测试要求未包含；历史 PySide6 环境障碍不在本 Task 修复）。
- `download` 命令未重跑（冻结方案明确 `download` 不变；TA2C 集成已验证幂等）。
- Manga109 gated 案例素材不可得（BLOCKED_BY_ASSET_ACCESS），与基线一致，不影响 smoke。
- worktree 素材为主工作区只读复制品（96 个媒体文件：JA ep04/ep20 12、KO e04 4、KO webtoon 80），未入 Git；Reviewer 若需复现 AC2，请按"接收方式"准备素材。

## 接收方式

- 分支 `agent/zcode/M2-TA2C-TOOLING-GAPS`，worktree `G:/CODEX/New Manga.worktrees/M2-TA2C-TOOLING-GAPS-zcode`，Git common directory=`G:/CODEX/New Manga/.git`。
- 静态审查：`git diff f3d684eb..a164e414 -- test_assets/comic_golden_suite/tools/assets.py tests/m2_test_assets/test_catalog.py test_assets/comic_golden_suite/manifests/cases.json test_assets/comic_golden_suite/README.md`。
- 单元级复现（无素材依赖）：worktree 根运行 `python -m pytest tests/m2_test_assets -v`。
- CLI 级复现（需素材）：worktree 无 gitignored 素材时，从主工作区只读复制 `test_assets/comic_golden_suite/日漫_JA/02_open_ground_truth_peppercarrot`、`韩漫_KO/02_public_ground_truth_peppercarrot`、`韩漫_KO/01_real_webtoon_cleaned_dataset`（annotation XML 76 个文件为 tracked，checkout 即在位），然后运行 README"使用"节的 verify 命令；或按 TA2C 先例在主工作区验证（但主工作区只读，须在集成树复验）。
- Reviewer 检查点建议：(1) 白名单常量与实测集合一致性；(2) `REPO_ROOT` 仓库根基准语义（模块常量，测试 tmp patch 不影响）；(3) cases.json 仅 naming_note 增量；(4) 判别演示不依赖网络。

## 下一任务建议（必填）

- Task ID / 标题：M2-TA2C-TOOLING-GAPS 独立非作者 Review（Task frontmatter 已登记 reviewer=DeepSeek Harness）
- 推荐 Agent / Reviewer：DeepSeek Harness（静态审查 + 独立复跑 pytest）
- 推荐原因与前置依赖：协作协议要求独立 Review 后 Codex 才能集成；本 Task 为 P3-6/P3-10 清算，review 对象固定为 `a164e414`。前置：无（素材非必需）。
- Recovery point：仓库 `G:/CODEX/New Manga`；分支 `agent/zcode/M2-TA2C-TOOLING-GAPS`；worktree `G:/CODEX/New Manga.worktrees/M2-TA2C-TOOLING-GAPS-zcode`（review worktree 待 Codex 创建，base=`f3d684eb`，head=`a164e414e8ff62940229d60d4dc046f89308b8b3`）。
- 允许修改路径：`doc/reviews/M2-TA2C-TOOLING-GAPS-*.md`、`verification/M2-TA2C-TOOLING-GAPS/**`（reviewer 证据）。
- 禁止范围与新增授权条件：不修改实现代码与素材；不改 cases.json；不合并 master；发现缺陷按模板出 `changes_requested` 并留证据。
- 交付物：`doc/reviews/M2-TA2C-TOOLING-GAPS-a164e414-dsh-r1.md`（REVIEW 模板）。
- 验证命令、环境与完成 Gate：`python -m pytest tests/m2_test_assets -v`（系统 Python 3.14.6 + pytest 9.1.1，34 passed 预期）；`git diff --check f3d684eb..a164e414` EXIT=0；Gate=approved 后 Codex（代行）集成并回填 integration_commit。
- 可直接转发给 Agent 的指令：对 `G:/CODEX/New Manga.worktrees/M2-TA2C-TOOLING-GAPS-zcode`（或按 recovery point 新建 review worktree）中 head=`a164e414` 的 M2-TA2C-TOOLING-GAPS 实施做独立非作者静态审查：核对 Task 方案冻结四点、AC1-AC5 证据与 `verification/M2-TA2C-TOOLING-GAPS/raw/*.log`，复跑 pytest，输出 `doc/reviews/M2-TA2C-TOOLING-GAPS-a164e414-dsh-r1.md`；不改实现。

## 风险与遗留

- **ko_sfx inventory 非 null 与编排预期不符**：编排说明预期 `ko_sfx_dialogue_cleaned_webtoon` 的 checksum_inventory 为 null，实测为 `verification/M2-TA2C/ko-webtoon-audit.json`（TA2C r1 返修时统一写入）。已按 Task 预案断言"存在"，未改任何既有字段值。Review 如判定应保持 null 语义，需要 Codex 裁决（属 cases.json 既有字段变更，本 Task 禁止范围）。
- **白名单不含 manga109.github.io**：以 cases.json 实测数据冻结为 2 host（编排说明预期 3 host 含 manga109.github.io，实测无任何 case 引用该 host）。未来新增 host 需显式扩 `SOURCE_URL_HOSTS`。
- **README 文档与运行时行为一致性**：README 第 15 行"当前 CLI 不据此拒绝另一个结构正确的 PNG"（KO webtoon SHA 审计仅外部复核）在本 Task 后仍成立——ko-webtoon-audit.json 仅做存在性消费，未升级为逐文件哈希复核；如需升级属新授权范围。
- **测试收集期读取 manifest**：`benchmark_inventory_params()` 在 pytest 收集期调用 `load_manifest()`；manifest 损坏将以 collection error 形式红（fail-closed，可接受）。
- 回退方法：revert `a164e414` 即恢复基线行为；无数据迁移、无破坏性操作。
