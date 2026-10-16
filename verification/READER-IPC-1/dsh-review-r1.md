# READER-IPC-1 独立 Review（R1）

| 项 | 值 |
|---|---|
| Task | READER-IPC-1（Tauri host 接线阅读器投影面；P17 前置） |
| Owner | codex |
| Reviewer | dsh（epoch 6；独立于 Owner，`route-agent.py` 机器排除 Owner） |
| 交付 | 实现 `96c7b057672589892458a3d1e78c91031f8f03e6`；HEAD `6aadc70de`（其后为 docs 提交） |
| 基线 | `f7d9da6b3` |
| 结论 | **approved**（含 1 项**非阻断范围观察**，见 §3） |

## 1. 独立验证且成立的部分

| # | 验证项 | 方法 | 结果 |
|---|---|---|---|
| V1 | 范围 | `git diff --name-only f7d9da6b3..HEAD` | 契约**未改**；`build.rs`、`capabilities`、`gen/schemas/**`、2 个新权限定义（`library_get_reader_projection.toml` / `library_save_reading_progress.toml`）、`src/{library_bridge,main}.rs`、`packaged_sidecar_tests.rs`、Task/Handoff/verification；**另有 1 处范围外文件**（见 §3） |
| V2 | 命令与四处同步（AC1/AC2） | 读实现 + diff | **PASS**。`library_get_reader_projection` / `library_save_reading_progress` 两条 production-only；`PRODUCTION_COMMANDS` / `generate_handler!` / `build.rs` app-manifest / `capabilities` + 自动生成权限定义**同一提交**；probe=7 / AC1=6 冻结形状不变 |
| V3 | **§6.3 语义红线（AC3）** | 读实现 | **PASS**。`StdioLibraryChannel::get_reader_projection` 为**纯透传**（`round_trip("GetReaderProjection", …)` 原样返回 Core JSON）→ Core 侧 `beginning` 不改 `saved_progress`、缺失译图为 null 等语义**由构造保证不被改写**；`save_reading_progress` 以 `if let Some(...)` **仅在存在时**写入 `scroll_offset_y` / `elapsed_seconds_delta`（缺失不重发）；资源引用保持不透明、继续走 §10 通道 |
| V4 | 拒绝面（AC4-②） | 读 `packaged_sidecar_tests.rs` | **PASS**。`missing_chapter → TARGET_NOT_FOUND`、`invalid_mode → INVALID_REQUEST`、`missing_page → TARGET_NOT_FOUND`；**且 frozen 证据行 `sqlite_unchanged=true`** → 证明拒绝路径**无写副作用** |
| V5 | 免夹具的 frozen 域级证据（AC4-③） | 读归档日志 | **PASS**。`READER_IPC_RESULT … protocol=2.3`，全部为**域级** typed 错误（非 `PROTOCOL_MALFORMED`） |
| V6 | **证据 pin + 提交包含性（BL-17 强校验）** | 逐个 `Get-FileHash` + **`git cat-file -e <sha>:<path>`** | **PASS**：记录的提交 `96c7b057672589892458a3d1e78c91031f8f03e6` **真实存在**（`git cat-file -t` → commit），4 条证据行**路径全部包含**；4 个 sha256 **全部与磁盘匹配** |
| V7 | 套件 | 读归档日志 | **PASS**。source **89 passed / 0 failed / 1 ignored**；frozen packaged **11 passed / 0 failed**；reader 专项 **1 passed**；Core pytest **407 passed** |
| V8 | 未弱化既有测试 | `git diff --numstat` | **PASS**。`_seed_core` 新增 `include_translations` **默认 `True`**（既有调用行为不变）；其余为新增断言/新测试 |
| V9 | 如实限定 | 读 Handoff | **PASS**：成功投影/成功进度保存未验证（无真实 book/chapter/page 夹具）、GUI e2e 未运行（无头无 WebView2 句柄），均如实声明 |

## 2. 结论：approved

两条命令按契约 §5 行 158/159 的冻结形状接线；host 侧**不改写**投影、**不消费**任何资源引用、**缺失可选值不重发**；拒绝面与"无写副作用"均有实测证据；证据记录自体可验证（**BL-17 合规**）。

## 3. 非阻断观察：范围定义缺口（**我自己的 Task 缺陷**，非 Owner 过犯）

Owner 额外修改了 **`tests/core/test_p16_reader_export.py`**（+58/−7），新增 Core 测试 `test_reader_projection_reports_missing_translation_as_null`，断言**缺失译图必须为 null** 且 `"path" not in json.dumps(projection).lower()`。

- 该文件**既不在我写的允许范围、也不在禁止范围**——是**我在 READER-IPC-1 的 Task 中留下的范围定义缺口**（我只禁止了 `src/**`，未对 `tests/core/**` 表态）。
- Owner 的动机可理解且**实质上更严格**地满足了我的 AC3（"红线必须由测试钉死"——而 `missing translated = null` 的正确落点正是 Core 测试）。
- 变更**纯新增且不弱化**（V8），Core pytest 由 405 增至 407 全绿。
- **裁定：非阻断**。不要求返修；但**必须继承两条教训**：(1) 后续 Task 的允许/禁止范围必须**显式覆盖 `tests/core/**`**；(2) 若某 AC 的红线属 **Core 侧语义**，应在 Task 中写明"可由 `tests/core/**` 的**新增**测试证成，禁止修改既有断言"。

## 4. 记录性事项（closeout 处理）

- **BL-15**：`delivery_head` 记实现提交 `96c7b0576…`，而分支 HEAD 为 `6aadc70de` → closeout 以实际 HEAD 冻结。
- 集成预告：本分支与已集成的四族在 `build.rs`/`capabilities`/`main.rs`/`library_bridge.rs`/`gen/schemas/**` 上预期冲突（叠加式）；解析后**计数须按合并后真实值**更新（预计 **30 条生产 / 37 条命令**：18 + 6 Run + 1 reveal + 3 export + 2 reader）。
