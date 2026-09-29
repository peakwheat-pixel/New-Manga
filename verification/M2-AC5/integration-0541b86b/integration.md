# M2-AC5 Integration Record — 0541b86b → merge 9db08dc7

- Integrator: Codex（编排会话代行，用户 2026-09-28/29 全权授权；Owner=ZCode 子 agent，Owner≠Integrator 保持）
- Integration merge: `9db08dc7548b70e8f4ee1d42e70e2e0c15838e63`（parents `ba11a23c`（r2 报告 import）+ `0541b86b8af7a26981861cf6d3e1c2fbb49250f7`（Owner 终 tip）；--no-ff 无冲突）
- Reviewer: DeepSeek Harness（非作者）两轮——r1 [approved_with_conditions](../../../doc/reviews/M2-AC5-eccf88e3-dsh-r1.md)（0×P0/P1、5×P2，session `session-ebd574e4`）→ Owner 返修 → r2 [**approved**](../../../doc/reviews/M2-AC5-0541b86b-dsh-r2.md)（0×P0/P1/P2、10×P3，session `session-e30a24a6`）；两份报告原字节 import（SHA256 `c0a943b5` / `dceeeb6f`），派发任务/JSONL/err 存档 [review-dsh-import](../review-dsh-import/)
- 交付链: release `82c85c0f` → claim `71b0e9aa` → 实现 `eccf88e3` → r0 交付 `783fc74f` → r1 闭合 `e3740b25`（delivery_head）→ 终 tip `0541b86b`；base=`6f79c040`
- 日期: 2026-09-29

## 1. 交付内容（Owner 交付，DSH 两轮独立复核）

- **打包链建立**（实现+验收混合 Task）：`tauri.conf.json` bundle active + NSIS；PyInstaller onedir **单闭包四入口**（host_bridge / core_service / acceptance_bridge / catalog_loader，frozen exe + 共享 `_internal`）打入 `resources/core-sidecar/`；独立构建 venv（pyinstaller 6.22.3 + PySide6_Essentials 6.11.2，不入产品依赖）；构建步骤 [packaging/m2ac5/README.md](../../../packaging/m2ac5/README.md)。
- **packaged spawn fail-closed**（AC2）：`M2RC1_PACKAGED=1` 显式或 `M2RC1_SRC_ROOT` 缺失 + sidecar exe 存在；缺失 → `CORE_SPAWN_FAILED:PACKAGED_SIDECAR_MISSING`（Command 构建前 typed 失败，绝不回落系统 python）；数据根缺省 `%APPDATA%\com.newmanga.m2rc1.desktop\{catalog,derived,managed,data}`；**dev spawn 行为等价**（Command 构建 argv/env/current_dir 逐字一致，成功路径子进程接管重构为共享 `adopt_child`——r2 A-⑤ 勘误后的准确表述）。
- **clean-start 验收**（AC3/AC4）：净化 PATH（剔 11 条目）+ `M2RC1_*` 清空 + `APPDATA=<lab>` 隔离下 NSIS `/S /D=` 静默安装 → **GATE PASS 25/25**（probe 13/13、ac1 双 launch 真实重启、production 真窗口、安装态 library probe CS-L1/L2/L3、宿主真实 `%APPDATA%` 零触碰 CS-Z4、无空格 guard CS-E3）；被测安装包 sha256 `5410e29e…` 全程复用未重建。
- **可复现性**（AC1）：sidecar `_internal` 156/157 hash 相同（唯一差异 `base_library.zip`=stdlib zip 内嵌时间戳）+ 4 入口壳工具链时间戳差异；输入 hash 留痕。
- **范围纪律**：`src/**` Python 零改动、requirements.txt 零改动、契约零改动、main.rs/core_bridge.rs 变更全在 Task 允许路径（f1/f2/f3 三份范围审计留痕）。
- **PySide6 闭包披露**：acceptance bridge 冻结装配硬依赖 Qt（M2-AC1 既有事实）→ PySide6_Essentials 进闭包；LGPLv3 义务、134 项资产、26.62 MiB 安装包体积、catalog_loader.exe 第 4 可执行、Qt 字体缺失告警——均已在 Handoff/verification-results 披露节如实登记。

## 2. DSH 两轮条件处置

- **r1 五个 P2 全部实质闭合**（r2 逐项 verified）：P2-1（156/157 勘误四处同步）、P2-2（安装态 stdio probe CS-L1/L2/L3）、P2-3（README 补齐）、P2-4（runner 删除全部对宿主真实 `%APPDATA%` 的删除/写入 + 四类 launch env `APPDATA=<lab>` pin + CS-Z4 证明）、P2-5（f1/f2 范围原始三件套）。
- **r2 剩余 10×P3 集成方处置**（本轮收口 commit 落字，逐项标注"r2 P3-x 勘误/修正"）：
  - 已落字闭合：P3-1 措辞（CS-L2 收窄为"envelope 合法，空库 count=0，无条目可断言键"）、P3-2（raw/README：`cleanstart-r1-final.log` 无头/无 EXIT 如实标注 + gate.json 就地覆盖归属注记）、P3-3（P2-1 引用改 `runA.txt:11 vs runB.txt:11`，diff.txt 行号系 hunk 编号不可解析）、P3-4（Task：gate 20/20→25/25、raw 27→34 份、Review 链回填、frontmatter done）、P3-6（requirements-build.txt `../requirements.txt`→`../../requirements.txt` 两处）、P3-8（"约 150 项"→**134 项实数**（PySide6 129 + shiboken6 5）；"sidecar 95 MB"无 raw 支撑作废）、P3-10（f3 r1-only 审计：`git diff --name-status 783fc74f..e3740b25` 18 文件全落允许路径，[raw/i-integration-replay.log](../raw/i-integration-replay.log)）。
  - 登记候选（未释放禁止实施）：P3-1 数据面（library probe seed 后 count≥1 断言）、P3-5（runner seed 步骤净化 env 口径加固）、P3-7（Rust 源注释"byte-for-byte"旧措辞，随下次触碰 `core_bridge.rs`/`main.rs` 时改）、P3-9（宿主 `%LOCALAPPDATA%\New Manga` 零接触 CS-Z5 加固 + 证据文件名防就地覆盖）。

## 3. 集成复跑与一个如实记录的问题（fresh-checkout 构建前置）

- 集成 head `9db08dc7` 复跑：**i1 首跑 EXIT=101**——`build.rs:39` panic `resource path 'target\core-sidecar\core-sidecar' doesn't exist`：tauri resources 声明指向 gitignored 构建产物，主 worktree 未跑过 `build_sidecar.ps1`。这正是 DSH r1 P3-4/r2 P3-4 预警的构建链脆弱性，实际后果为 **fresh checkout 上 cargo 基线不可跑**（非产品行为回归；dev 运行行为不受影响，Owner/CI worktree 因已有产物未暴露）。
- **处置**：集成侧以固定 venv（pyinstaller 6.22.3）跑 `build_sidecar.ps1` 重建产物后 **i1-retry EXIT=0（38 passed + 1 ignored）**；`packaging/m2ac5/build_sidecar.ps1` 输出绑定 HEAD=9db08dc7。**构建顺序约束如实登记：任何 fresh checkout 必须先跑 `packaging/m2ac5/build_sidecar.ps1` 才能 cargo build/test**；根治（tauri beforeBuildCommand 钩子 / build.rs 容忍缺失 + 运行期 fail-closed）登记为候选（未释放禁止实施，涉及 `tauri.conf.json`/`build.rs` 需另立切片）。
- 复跑终态（[raw/i-integration-replay.log](../raw/i-integration-replay.log)，HEAD=9db08dc7）：**cargo 38 passed + 1 ignored EXIT=0；pytest tests/m2_acceptance 35 passed EXIT=0；vitest 31 passed EXIT=0；`git diff --check 6f79c040..9db08dc7` EXIT=0；f3 r1-only 审计 EXIT=0**。

## 4. 遗留登记（不阻断 done）

- 真干净 Windows 机覆盖 NOT_RUN（M2 Release Gate 范围，释放时冻结口径=本机模拟）。
- NSIS 卸载流程未测（AC 未要求）；bit-for-bit 可复现需 `/Brepro`/SOURCE_DATE_EPOCH 类机制（候选）。
- PDF/MOBI 闭包（pypdfium2/mobi 延迟 import）不在 sidecar（候选）。
- fresh-checkout 构建顺序前置 + beforeBuildCommand 根治（候选，见 §3）。
- P3-1 数据面 / P3-5 / P3-7 / P3-9 runner/Rust 加固（候选，见 §2）。
- Owner branch/worktree 保留于终 tip `0541b86b`。

## 5. 结论

DSH r1 `approved_with_conditions`（5×P2）经 Owner 返修全部实质闭合，r2 `approved`（0×P0/P1/P2）；剩余 P3 由集成方落字闭合（7 项）或登记候选（4 项）；集成 head 三层基线全绿、diff --check 整树干净；打包产物可复现、clean-start 25/25、fail-closed 无 python 回落、dev 行为不变。**M2-AC5 置 `done`**；M2 Release Gate 的可测对象（NSIS 安装包 + 自包含 sidecar）已就位，Gate 本身（真干净机、Windows matrix、console policy）仍待后续释放。
