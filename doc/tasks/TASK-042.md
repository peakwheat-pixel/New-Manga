---
id: TASK-042
title: 超大 Webtoon 带状/流式解码（承接 TASK-020 遗留 BLOCKED）
kind: implementation
status: in_review
approval: approved_by_user
suggested_owner: DeepSeek Harness
owner: ZCode
reviewer: Codex
depends_on: [TASK-020, TASK-038]
base_commit: 904fca185c9900c0b2df297529a58ece831dc0a0
branch: agent/zcode/TASK-042-streaming-decode
worktree: G:/CODEX/New Manga.worktrees/TASK-042-zcode
integration_commit: null
---

# TASK-042：超大 Webtoon 带状/流式解码

**READY（2026-09-18 用户批准"两项都批准"——本项为超大 webtoon 的流式解码依赖）**：Owner=`ZCode`、Reviewer=`Codex`（**非作者**）、base=`904fca1`。

**改派说明（2026-09-18，经用户确认"适合交给 ZCode"）**：Owner 由 `DeepSeek Harness` 改为 `ZCode`（**连续性最优**：本 Task 要改的 tile 路径与 `webtoon_tiles.py` 即 ZCode 在窗口内的交付；原 `agent/deepseek/TASK-042-streaming-decode` 分支与 worktree **无任何提交**，已按约定移除重建为 `agent/zcode/**`）。Reviewer 保持 `Codex`（非作者）。

**复审特别提示（给 Reviewer）**：AC ② 要翻转的表征断言钩子是**本 Task 作者自己在 TASK-020 写的**——复审必须确认新断言**更强**（带状解码成功 + 内存界 + 逐像素等价），**不是**把旧断言改宽松；该测试**不得删除**。

## 来源（TASK-020 已把问题钉得很准）

[TASK-020 Handoff](../handoffs/TASK-020-7833604.md) 第 31–37 行实测：

- Qt PNG handler 在 rgb32 ≳**300MB** 时**任何读取方式都失败**（高度 40000＝256MB 成功；50000＝305MB 失败；65535/70000/200000 全失败）；`setClipRect` 不改变结果（**handler 先分配整图再裁剪**）；系统可用内存 19GB → 排除 OOM。
- 1600×200000 ＝ **1.28GB rgb32**，当前依赖下无法解码。
- 已交付：TileGrid 对 200000px 高的**几何**验证全过；解码失败固化为**表征断言**（`pytest.raises(OSError)`）+ `oversize-record.json` 记录 BLOCKED 口径与解锁条件；**并有意留下"解锁后该断言会失败以提醒更新口径"的回归钩子**。

用户已批准"引入流式解码依赖"这一解锁条件①。

## 依赖选择（Codex 裁定，附理由）

**首选：不新增依赖 —— 用 stdlib 实现 PNG 带状读取**（`zlib` + PNG 行过滤器；只保留目标带的扫描行）。
理由：①所需能力只是"从我们自己的 managed PNG 取一条带"，PNG 是 zlib 压缩的**逐行**格式，带读无需整图；②`Pillow` 对 PNG **没有**区域/增量解码（`load()` 仍整图），**解决不了 1.28GB**；③`pyvips`（libvips）虽是最贴合的大图流式方案，但引入**原生 DLL**，会增加 TASK-027 打包与 Windows 分发风险。

**备选（已获用户批准，仅在实测证明 stdlib 不足时启用）**：新增 `pyvips`。启用**必须**在 Handoff 给出：为何 stdlib 不足的具体反例、安装前后全仓对照、以及**打包影响**说明（TASK-027 相关）。

## Acceptance Criteria

- [ ] **AC ①（带状解码）**：能对 1600×200000 量级的 PNG **在不整图解码的前提下**取得指定带（起始行+高度），并回映到原图坐标；**给出峰值内存实测**（须显著低于 1.28GB，建议给出"带大小 × 常数"的界）。
- [ ] **AC ②（翻转遗留钩子，不得删除测试）**：TASK-020 的表征断言（`test_oversize_page_geometry_and_decoder_limit_record` 的 `pytest.raises(OSError)`）与 `oversize-record.json` 按**新口径**更新：改为断言带状解码**成功**并记录新的内存/耗时实测；**保留**该测试的回归价值（几何断言不变），并在 Handoff 说明"这是按原设计的钩子更新口径"。
- [ ] **AC ③（fail-closed 变体矩阵）**：不支持的 PNG 变体（交错 Adam7、16-bit、调色板、非 PNG 源）一律 **typed fail-closed**，**不静默降级**为整图解码失败或空图；错误须可诊断并进入 provenance/记录。
- [ ] **AC ④（端到端可达）**：经 TASK-020/038 的 tile 路径，超大页在生产装配下可读（视口带按需解码）；未注入 tile 工厂时**回退路径行为不变**。
- [ ] **AC ⑤（依赖纪律）**：若最终引入 `pyvips`，`requirements.txt` **仅新增该项**并提供上述三份证据；若未引入，Handoff 明写"未新增依赖"及理由。
- [ ] **AC ⑥（判别力 + 回归）**：新测试对**修前代码**失败（放 base `904fca1` 的 `src` 上跑并留证）；`tests/reading_export`、`tests/core`、`tests/providers` 与全仓 passed **不减少**；全仓串跑 **≥5 次**逐次记录（同一 shell + 同一 venv）。
- [ ] **AC ⑦** 交付 Handoff、取证，经**非作者** Review 与 Codex 集成后才能 done；并登记 TASK-020 遗留项②关闭。

## 允许修改范围

- `src/infrastructure/imaging/**`
- `src/application/reading/**`（仅在确需适配读取路径时；须说明理由）
- `requirements.txt`（**仅**在启用备选时新增 `pyvips`）
- `tests/reading_export/**`、`tests/core/**`
- `doc/tasks/TASK-042.md`、`doc/handoffs/TASK-042-*.md`、`verification/TASK-042/**`、`verification/TASK-020/**`（仅更新 `oversize-record.json` 与相关记录）

## 禁止范围

- 不得修改 Schema/migration、pipeline seam 本体、模型/SFX 策略、`AGENTS.md`、其他 Task；不得新增除（备选）`pyvips` 之外的依赖。
- **不得用"增大上限/关闭校验/整图兜底"等方式绕过**；不得静默降级；不得放宽或删除既有断言（AC ② 是**按原设计更新口径**，不是删除）。
- 不处理 MOBI（由 [TASK-041](TASK-041.md) 承接）；不重开 TASK-020 的其他已收口项。

## 测试要求

- `python -m pytest tests/reading_export -q -p no:cacheprovider -rs`（含超大页带读与变体矩阵）
- 全仓 `python -m pytest -q -p no:cacheprovider -rs -rf`（≥5 次逐次记录）
- 性能/内存证据须给出**实测方法**（探针脚本 + 原始输出），不得把建议值写成实测。

## 依赖、风险与阻塞

硬依赖：TASK-020（tile 实现与遗留登记）、TASK-038（生产装配注入）。用户已批准流式解码依赖（备选路径）。

风险：
- **自研 PNG 带读的正确性**是主要风险（行过滤器/边界/CRLF 无关但 IDAT 分段要处理）→ AC ③ 的变体矩阵必须覆盖"我们不支持什么"，且必须有"与 Qt 整图解码逐像素一致"的对照（在小图上做等价性验证，再上大图）。
- 若最终启用 `pyvips`，打包与分发影响需在 TASK-027 前明确。

## 交付与运行记录

- Handoff：尚无。Review：尚无。实际执行/测试：尚无（`ready`，实施未开始）。
- **历史状态**：2026-09-18 由 Codex 创建为 `ready`（base=904fca1）。
- **最近状态（当前，唯一）**：2026-09-18 09:1x 由 ZCode 开工（status→`in_progress`）；分支 `git merge master` 快进至 `7ea1629`（W5-W7 收口后 HEAD）。实施开始：`src/infrastructure/imaging/streaming_png.py`（stdlib zlib＋PNG 行过滤器带状读取，单遍游标）＋接入 `TiledPageRasterizer`＋翻转 TASK-020 表征钩子＋变体 fail-closed 矩阵＋Qt 逐像素对照。**依赖决策：首选 stdlib（不启用 pyvips）**。
- **最近状态（当前，唯一）**：实现 head=`fc6c649`（开工 `ebe5755`）：`streaming_png.py` 新建（单遍游标带读＋全 5 种过滤器＋typed 变体拒绝）＋`TiledPageRasterizer` 改驱动流式读取（Qt 从 imaging 模块移除）＋纯 stdlib PNG 编码器＋`test_streaming_png.py` 11 例（含 Qt 逐像素一致）＋TASK-020 表征钩子按原设计翻转（oversize 1600×200000 带状解码**成功**、窗口=恰 1/50 整页 rgb32、tracemalloc 峰值留证）。**未新增依赖（stdlib-only，pyvips 备选未启用）**。回归：mandated reading_export 93 passed/0 skipped、全仓 ×5 每次 798 passed/0 skipped exit 0。**status=in_review：待 Codex（非作者）Review 与集成**——集成后登记 TASK-020 遗留②关闭。
