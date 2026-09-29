---
id: M2-TA2C-TOOLING-GAPS
title: "comic_golden_suite 工具清算：source_url 主机白名单 + checksum_inventory 运行时消费与判别性断言（TA2C P3-6/P3-10）"
kind: fix
status: in_progress
approval: orchestrator_delegated_2026-09-30
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（待派发，非作者静态）
depends_on: []
base_commit: f3d684eb767414a3c5ac010f7920657204cc9336
branch: agent/zcode/M2-TA2C-TOOLING-GAPS
worktree: G:/CODEX/New Manga.worktrees/M2-TA2C-TOOLING-GAPS-zcode
integration_commit: null
---

# M2-TA2C-TOOLING-GAPS：TA2C P3-6/P3-10 工具清算

## 来源与目标

- M2-TA2C DSH r2 review 登记候选（doc/reviews/M2-TA2C-8cb3a135-dsh-r2.md:93,99）：
  - **P3-6**：`manual_source_page` 类 case 的 `source_url` 仅 `https://` 前缀断言、无主机白名单；O01–O08（`韩漫_KO/02_open_ground_truth_peppercarrot/**`）与 K11–K13（`…_public_ground_truth_peppercarrot/ep04`）同族目录命名不一致。
  - **P3-10**：`checksum_inventory` 字段**无任何运行时代码消费**（全仓仅 tests/README/cases.json/docs 命中）；既有断言只覆盖 3 个 source 字面值、未覆盖 `ko_sfx`、未断言路径在仓库根基准下实际存在，路径漂移不会使任何测试变红。
- Goal 追溯：doc/GOAL.md（2026-09-30）清算集合 T3。
- 一个可观察的交付结果：`tools/assets.py` 运行时消费并校验 `checksum_inventory`（存在性 + 哈希复核），非白名单 `source_url` 被拒；故意造坏的 inventory 路径会使测试变红（判别力 artefact）。

## 方案冻结（编排裁决，用户可撤销）

1. **P3-6① 主机白名单**：`load_manifest` 对每个 case 的 `source_url` 施加主机白名单校验（白名单 = `www.peppercarrot.com` + `huggingface.co` + `manga109.github.io`（或以 cases.json 实际出现的 https host 集合冻结为常量），实现先侦察再定，原则：与下载入口 `PUBLIC_COMIC_HOST` 同风格的显式常量 + `ValueError` fail-closed；**不网络请求**，纯解析校验）。
2. **P3-6② 目录命名**：**不改盘上目录**（本地素材路径稳定性优先，`local_path` 与既missive本地状态/manifest 引用联动）。以 cases.json 为目录名事实源：`test_catalog.py` 增一条断言锁定「同 source 族 cases 的 `local_path` 前缀一致」的**现状快照**并注释命名不一致为已知观察（若快照断言因现状不一致无法写成"一致"，则写显式枚举现状 + 注释，把不一致固化为受管事实）。
3. **P3-10 运行时消费**：`tools/assets.py` 的 `verify` 增加对 cases.json `benchmark_sources[*].checksum_inventory` 非空路径的校验（路径存在 + 若为 local_asset_inventory.json 则复用既有逐文件哈希复核路径）；`list` 输出 inventory 状态。`download` 不变。
4. **P3-10 判别性断言**：`tests/m2_test_assets/test_catalog.py` 新增参数化断言：所有非空 `checksum_inventory` 路径在仓库根基准下存在；覆盖含 `ko_sfx_dialogue_cleaned_webtoon` 在内的**全部** sources；并补一个判别力演示（tmp manifest 中故意指向不存在路径 → `assets.load_manifest`/`verify` 报错，先红后绿的"红"由该演示承担）。

## Acceptance Criteria

- [ ] AC1（白名单）：非白名单 host 的 `source_url` 在 `load_manifest` 被拒（单测：tmp manifest 注入 `https://evil.example/x` → ValueError）；白名单内既有 manifest 加载不受影响（既有测试全绿）。
- [ ] AC2（inventory 运行时消费）：`assets.py verify` 对非空 `checksum_inventory` 路径做存在性与（对 local_asset_inventory.json）逐文件哈希复核；`python tools/assets.py verify --language ja --level smoke` 与 `--language ko --level smoke` EXIT=0（素材在主工作区，若 worktree 无素材则以 `--manifest` 注入或从主工作区只读复制方式验证，如实记录）。
- [ ] AC3（判别性断言）：参数化断言覆盖全部 sources 的非空 inventory 路径存在性；判别演示（坏路径 → 红）入日志。
- [ ] AC4（命名快照）：同族目录命名现状以受管断言固化 + 注释（不重命名）。
- [ ] AC5（范围与证据）：diff 仅触及允许路径；`git diff --check` EXIT=0；pytest `tests/m2_test_assets` 全绿 EXIT=0；日志带 shell 头/HEAD/EXIT。

## 允许修改范围

- `test_assets/comic_golden_suite/tools/assets.py`
- `test_assets/comic_golden_suite/manifests/cases.json`（仅新增注释性字段如 `naming_note`，不改既有字段值）
- `tests/m2_test_assets/test_catalog.py`（或新增测试文件）
- `test_assets/comic_golden_suite/README.md`（行为变化说明）
- 本 Task 文件、Handoff、verification/M2-TA2C-TOOLING-GAPS/**

## 禁止范围

- `test_assets/**` 素材文件本体（图像/XML/ZIP/inventory 文件值）、目录重命名
- `src/**`、`apps/**`、`packaging/**`
- cases.json 既有字段值变更（status/local_path/license 等）

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 白名单拒毒 | tmp manifest 注入非白名单 URL → ValueError（先红演示） | 标准 pytest | NOT_RUN | 待入 verification |
| AC2 verify 消费 inventory | `assets.py verify` 两语言 smoke EXIT=0 | 素材可用 | NOT_RUN | 待入 verification |
| AC3 参数化存在性断言 | pytest tests/m2_test_assets EXIT=0 + 坏路径红演示 | 标准 pytest | NOT_RUN | 待入 verification |
| AC5 回归 | pytest tests/m2_test_assets 全套 + diff --check | 标准 pytest | NOT_RUN | 待入 verification |

## 依赖、风险与阻塞

- 风险 1：白名单集合若漏实际 host 会使 load_manifest 拒绝合法 manifest——实现前先枚举 cases.json 全部 https host（以数据为准冻结常量）。
- 风险 2：verify 复核 local_asset_inventory.json 哈希需要素材在位——worktree 无素材时按 AC2 注记方式验证并如实记录。
- 阻塞：无。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无。
- 后续实际记录包含日期、commit、环境、结果、遗留项；最终由 Codex（代行）填写 integration_commit 并改 done。
