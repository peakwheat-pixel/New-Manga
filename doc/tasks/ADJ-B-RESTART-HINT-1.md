---
id: ADJ-B-RESTART-HINT-1
title: 裁决 B 的运行前提核实 → 缺陷成立：重启提示未在 Provider 配置入口展示
kind: fix
governance_version: 3
status: done
disposition: "裁决 B 要求『保留并清楚展示』重启约束；实测该提示只出现在错误文案里，配置入口看不到"
approval: DSH 2026-11-15（按裁决 B 的『若提示不可见应单独开卡』条款）
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on: []
base_commit: eb8b5c82a
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/ADJ-B-RESTART-HINT-1
allowed_paths:
  - doc/tasks/ADJ-B-RESTART-HINT-1.md
  - doc/reviews/ADJ-B-RESTART-HINT-1-*.md
  - doc/reviews/MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/ADJ-B-RESTART-HINT-1/**
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs
  - apps/desktop-avalonia/src/NewManga.App/Views/V2/Console/ConsoleView.axaml
  - apps/desktop-avalonia/tests/NewManga.App.Tests/RestartHintVisibilityTests.cs
---

# ADJ-B-RESTART-HINT-1：重启提示未在配置入口展示

## 裁决 B 留给 DSH 的前提

`doc/reviews/MAINT-1-EXTERNAL-ADJUDICATION-codex-2026-11-14.md` 裁决 B 选择"暂时保持现状"，
同时写明两条硬要求与一条待核实前提：

- 要求：**保留并清楚展示**"修改模型配置后重启应用生效"；**不要**声称保存后已立即生效。
- 待核实：**"B 的投入产出判断依赖现有重启提示覆盖相关配置入口，且重启后确能使用新配置；
  这是待 DSH 在开卡前核实的运行前提"**。
- 若"提示不可见"，**应单独按实际故障开卡**。

## 核实结论：缺陷成立（P2）

| 事实 | 位置 |
|---|---|
| 句子**存在**且是唯一常量 | `NewManga.App/Services/TranslateErrorText.cs:16` `RestartHint = "修改模型配置后需重启应用生效。"` |
| 但**只出现在错误文案**里 | `TranslateErrorText.cs:20`（`PROVIDER_NOT_CONFIGURED` 的后半句） |
| `RestartHintShort` **定义后再无引用** | `TranslateErrorText.cs:41` |
| **Provider 配置段没有该提示** | `ConsoleView.axaml` "② Provider 与凭据"段（安全约束 banner + 标题 + 按钮 + 列表），**无重启提示** |
| 全仓 `RestartHint` 引用 | 仅上述三处，**无任何 UI 绑定** |

⇒ 用户在**真正修改模型配置的入口**看不到"需重启"，只在**翻译失败**时才可能读到。
这正是裁决 B 说的"提示不可见"。

## 修复

| 文件 | 改动 |
|---|---|
| `ConsoleViewModel.cs` | 新增 `public string RestartHintText => TranslateErrorText.RestartHint;`（**复用常量**，不复制文案） |
| `ConsoleView.axaml` | Provider 段的安全 banner 下新增 `<TextBlock Classes="meta" Text="{Binding RestartHintText}" />` |

**为什么不用 `AlertBanner`**：`AlertBanner.Severity` 是受限枚举（`NmStatus`），不接受 `"Info"` ——
第一次尝试即编译失败（`AVLN3000`），改用轻量 `TextBlock`。已记入本卡。

## 判别力与回归

| 项 | 结果 |
|---|---|
| 新增测试 `RestartHintVisibilityTests`（2 个） | **2 passed / 0 skipped** |
| **判别力**：删掉 XAML 里的 `TextBlock` | **`ProviderSection_PaintsTheRestartHint` 变红**，已还原 |
| **无夹具全量 App.Tests** | **953 / 0 / 11 / 964**（新增 2 个测试；**skip 仍 11，未新增**） |

## 未做

- **"重启后确能使用新配置"未验证**：这需要真实模型权重（`yolo11s-seg.onnx` 缺失）与真实 Provider 凭据，
  属用户不可替代的实物。**如实标 `NOT_RUN`**，不因为改了提示就宣称该前提已满足。
- 裁决 A（手动排序）已由 `CHAPTER-MANUAL-SORT` 交付，本卡未触碰。
