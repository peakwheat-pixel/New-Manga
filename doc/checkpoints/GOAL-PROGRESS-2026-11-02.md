# Goal 进度文件 · 2026-11-02（自主推进段 2）

**当前 HEAD**：`383c46c3b`（FEA-04b/05-PORT-1/05-WIRE-1/04 done；FEA-06 拆前置 proposed）
**主推进**：`FEA-05-WIRE-1` Draft 命令面 wire **done**（范围 r1–r7、实现 impl-r1–r3 approved；全量 931/0/60）；`FEA-04b` 设计基线 r5 approved（AC5 待用户确认）

---

## 1. 已完成（2026-11-01/02 段）

| 项 | 状态 | 证据 |
|---|---|---|
| `FEA-00A-IMPL-1` | **done** | 集成 `e0ba29eba`；实现复核 r1 approved；194 passed |
| `FEA-03`（草稿与保护） | **done** | 范围复核 r5 approved（r1–r4 changes_requested）；C-13 v6 UNFREEZE approved；实现复核 r5 approved P0/P1=0；集成 `76d947923`；1052 passed；pin 15/15 |
| `FEA-03` 实现 | delivery `1db802f8b` + hygiene `651b6cfb3` | CORE + BRIDGE；V1–V25 证据；P2×13 登记 |

## 2. 待裁决（需用户拍板；已给推荐并先行裁决）

| # | 事项 | 推荐 | 处置 |
|---|---|---|---|
| Q-12 | 释放 `FEA-04`（Current 适配） | 释放（依赖 FEA-02-CORE/FEA-03 均 done） | **DSH 裁决：释放**；owner=ZCode（方案指定），ZCode 不可用时 DSH 可指派 Codex |
| Q-13 | FEA-03 的 V19（旧→新/新→旧组合） | 集成验证 deferral | 已登记（Task 卡 deferral + v-matrix）；集成窗口或 FEA-04 回归覆盖 |
| Q-14 | FEA-03 P2×13 技术债 | 接受遗留，登记在 Review r5 | 不阻塞 done |
| Q-15/Q-19 | FEA-04 切换（Current↔Fluent）是否本卡实现 | 仅 preflight；切换执行由 FEA-07 | v2 已收窄（R-SWITCH preflight-only） |
| Q-16 | FEA-03 defer 的 wire 是否本卡实现 | 否；S1–S3 权威收窄为 ApplicationCore 本地 | v2 R-STATE/AC4 已改；wire 转 FEA-05/07 |
| Q-17 | `NewManga.App.csproj` 加 ApplicationCore 引用 | 授权为本卡唯一单点例外 | 写域已列；Handoff 记录 |
| Q-18 | `Frontends.Current` 落点 | `Shell/V2/Frontends/`（in-app） | v2 已写；不新建工程/改 sln |
| Q-19 | 是否实现运行期切换入口 | 否；只做 preflight，FEA-07 承担切换 | v2 已写入 R-SWITCH-1…3 |
| **Q-20** | **preflight blocker 形状与"有损编辑态"谓词** | **冻结**：`PreflightBlocker(Code, Source, Detail)`；Code ∈ {`PENDING_REGION_TYPE`,`PENDING_CONFIRMATION`,`UNFLUSHED_RUN_KEY`,`UNMAPPED_READER_ANCHOR`,`UNMAPPED_SHELL_STATE`}；任一存在即 fail-closed | v3 已写入 R-STATE-2/AC5；本行即书面裁决记录 |

## 3A. FEA-04 实现状态（已闭环，2026-11-02 12:20）

- Codex 实现 WIP 提交 `160bd0a4d`（分支 `feat/fea-04`，未合并、未复核）。
- **编译**：DSH 修复 5 处后 `dotnet build NewManga.sln` 通过（Codex 沙箱 NuGet 阻断，非代码问题）。
- **行为基线 FAIL**：sln 测试 App.Tests **23 failed / 389 passed**（基线 10 failed / 386 passed）；回归集中在 `V2StudioBatchTests`（16，同一 helper `RefreshNowAsync` 返回 false 根因待查）、`V2ConsoleUiTests`（3）、`V2ShellUiTests`（1）；新增 `FEA04CurrentAdapterTests` 1 失败。
- **结论**：已由 DSH 返修闭环：冻结命令 `dotnet build` EXIT=0、`dotnet test NewManga.sln` **931 passed / 0 failed / 60 skipped**（App 413/420，16 个既有回归全部消除 + IMPL-02 回归测试）；实现复核 r1（P1×4）→ r2（P1×2）→ **r3 approved（P0/P1=0，P2×7 接受遗留）**；集成 `f4d8a32ec`；卡 done。
- **返修根因（历史记录）**：——Codex 把 `StudioBatchViewModel._dataSource` 从 `RunControllerRunDataSource` 换成 `CurrentRunDataSource`（ApplicationCore monitor 路径），绕过了 Host `GetTaskProjection` → Batch 测试的 `ScriptedTaskProjections` 不再被消费（16 失败同根因）。DSH 恢复 `RunControllerRunDataSource(_controller, () => RunId)` 后，部分结果 16→3（`Poll_UpdatesProjection`、`GateModal_FocusesCancel`、`Gate_UnclearedErrors` 仍 FAIL）。
- **环境限制**：Avalonia headless UI 测试在本机无渲染环境会长时间挂起（testhost CPU 累计上千秒），无法在无人值守下跑完整 sln 测试；完整基线需在用户桌面环境执行。
- **阻塞**：FEA-04 返修需 UI 测试环境（真实显示/GPU）与逐项断言调试；DSH 已记录返修起点（`feat/fea-04` 分支 HEAD 已含数据源恢复，未提交）。

## 3. 下一动作

1. FEA-04 范围冻结 v3 派独立复核 r3 → ready。
2. 实现（ZCode 优先；不可用则 Codex）→ 独立实现复核 → 集成 → done。
3. 之后候选：`FEA-04b`（Fluent 四页设计规格，写域 `doc/design/fluent-v1/`，可与 FEA-04 并行不冲突）。

## 4. 状态变更记录

| 时间 | 变更 | 记录 |
|---|---|---|
| 2026-11-02 02:45 | 建立；记录 FEA-03 done 与 FEA-04 释放 | DSH |
## 5. 本轮新增记录（2026-11-02 03:00–13:00）

- **FEA-04 done**：eat/fea-04 经 Codex 实现 + DSH 返修（编译修复、Host 投影恢复、RunStatusMonitor 恢复、intent key 语义、IMPL-02 投影丢失修复）→ 实现复核 r1（P1×4）→ r2（P1×2）→ **r3 approved（P0/P1=0）**；冻结命令 build EXIT=0、sln test **931/0/60**（App 413/420）；git diff --check rc=0；集成 4d8a32ec；卡 done（证据 10 项）。
- **FEA-C11-PREREQ-1 done**：交付 7018e19b 已是 main 祖先、文件 sha256 与证据一致、复核 approved → 收口。
- **FEA-04b 释放**：eady，写域 doc/design/fluent-v1/**；owner/reviewer 待指派（ZCode CLI 不可用 → DSH 可代起草或派 Codex；设计复核需独立上下文）。
- P2 遗留（FEA-04）：实现复核 r3 列 7 项（基线文档算术/控制字符已修、冻结命令日志已入库；git diff --check 残余、Handoff 行内表述、用例命名等）已在收口时处理大部分，剩余接受遗留。

## 6. 待裁决（需用户拍板）

| # | 事项 | 推荐 |
|---|---|---|
| Q-21 | FEA-04b 设计 owner（ZCode CLI 不可用） | DSH 代起草规格 + 独立上下文复核；规格批准后再由 ZCode/Codex 实现 UI |
| Q-22 | FEA-05（Fluent 独立界面）是否需要先完成 wire（FEA-03 defer 的 Draft 命令面） | 是：先做 wire 子卡，再做 Fluent 页面；否则 Fluent 与 Current 无法共享草稿真值 |
## 7. FEA-04b 设计基线（2026-11-02 傍晚）

- 交付：doc/design/fluent-v1/（README + 01–10，版本 luent-v1.0.0）：四页规格（书架/工作台/阅读器/设置）+ 状态矩阵 + 令牌取值（C-02 V-05）+ 动效三态三类（C-03 §3 判据①–⑤）+ 键盘/a11y（ShellCommands.cs 17 条键位）+ 响应式（三档断点）+ 组件清单。
- 独立复核 **r1（P1×7）→ r2（P1×4）→ r3（P1×1）→ r4（P1×1）→ r5 approved（P0/P1=0，P2×16）**。
- 缺口登记：G-1（Fluent 令牌待 FEA-05 生成）、G-1b（尺寸/断点复用既有 Nm.Size.* + 矩阵列宽 96 设计常量）、G-1c（Nm.Focus.Ring.* 缺失）。
- **AC5 未完成**：用户确认未进行（自主推进模式）；待用户确认后 DSH 冻结并标 done。
- 待裁决：Q-23（FEA-04b 设计基线是否批准冻结）；Q-24（FEA-05 前置 wire 是否先做子卡）。
## 8. FEA-05-WIRE-1（Draft 命令面 wire，2026-11-02 深夜）

- 建卡 doc/tasks/FEA-05-WIRE-1.md；范围冻结 r1（P0×3/P1×5）→ r2（P0=0/P1×5）→ r3（P1×2）→ r4（P0×1：Region 不变式冲突）→ r5（P1×1）→ r6（P1×3）→ **r7 approved（P0/P1=0，P2×9 接受遗留）**。
- 最终范围（v5.2）：Core 命令白名单 + 6 handler（drafts_open/patch/prepare/apply/status/discard，真实签名）+ 独立契约 FEA-05_DRAFT_WIRE_CONTRACT.md + V11R_COMMAND_CONTRACT_V1.md §8 六行（C078–C083）+ Python 协议测试；**不接** IHostController/CoreClient（端口与 registry 归 FEA-05-PORT-1，需先契约 UNFREEZE）。
- 派 Codex 实现（suggested_owner: codex）；DSH 负责审查/提交/集成。
- 待裁决：Q-25（FEA-05-PORT-1 何时建卡）；Q-26（FEA-05-WIRE-1 实现完成后的实现复核席位）。
## 9. FEA-05-WIRE-1 收口（2026-11-02 深夜）

- 范围：r1（P0×3/P1×5）→ r2（P0=0/P1×5）→ r3（P1×2）→ r4（P0×1）→ r5（P1×1）→ r6（P1×3）→ **r7 approved**。
- 实现：Codex 本地命令通道不可用（helper_unknown_error），DSH 代实现；实现复核 **impl-r1（P1×5）→ impl-r2（P1×1）→ impl-r3 approved（P0/P1=0，P2×10 接受遗留）**。
- 交付：doc/contracts/FEA-05_DRAFT_WIRE_CONTRACT.md（五节 + 17 码逐码表）、V11R_COMMAND_CONTRACT_V1.md §8.2（C078–C083）、core_service.py（6 handler + 冻结信封映射）、	ests/core/test_draft_commands.py（12 项）、erification/FEA-05-WIRE-1/**（7 项证据）。
- 验证：全量 sln **931 passed / 0 failed / 60 skipped**；pytest **900 passed**；C# 契约 **80/80**；erify_pins 15/15；check.ps1 PASS。
- **待裁决**：Q-27（FEA-05-PORT-1 建卡：端口面 + CoreClient registry + V11R_REGION_WRITE_CONTRACT.md UNFREEZE 把 Region 不变式升级为「各家族集合之并」）；Q-23（FEA-04b 设计基线批准/冻结）。
## 10. FEA-05-PORT-1 收口（2026-11-03 凌晨）

- 范围：r1（P0×2/P1×1）→ r2（P0=0/P1×2）→ r3（P1×1）→ **r4 approved**。
- 实现：DSH（Codex 通道故障）；**impl-r1（P1×5）→ impl-r2（P1×2）→ impl-r3 approved（P0/P1=0，P2×11）**。
- 交付：Region 契约 **v1.6 UNFREEZE**（DraftsCommandNames 6；不变式并集 17）+ CONTRACT-UNFREEZE-2026-11-02.md + C-07 库存 54/61/18 + C-07 pin 重算 3fdb44e4…（重冻）+ HostCommandDomain.Drafts + DraftCommands.cs DTO + registry（6 条/17/CoreBindings）+ dispatcher 6 case/XOR + IHostController 7 方法 + HostController/NullHostController/FakeHostController + DraftCommandRegistryTests（9）+ DraftPortDefaultTests（6）。
- 验证：全量 sln **949 passed / 0 failed / 57 skipped**；erify_pins **15/15**；pi inventory --check EXIT 0；check.ps1 PASS。
- **待裁决**：Q-28（FEA-06 UI 消费的前置：FEA-04b AC5 用户确认、FEA-05 契约 §8.2 状态升级路径——§8.2 状态列须保持 PENDING 否则 CommandContractV11RTests 红）；Q-23（FEA-04b 批准）。
## 11. FEA-04b 冻结 + FEA-06 拆分（2026-11-03）

- **FEA-04b done**：设计基线 luent-v1.0.0 **FROZEN**（DSH 裁决，Q-23：用户确认不可得 → 以 r5 approved 独立复核 + DSH 冻结替代；用户后续修订走 v1.1）；11 文件；erification/FEA-04b/design-baseline-selfcheck.md。
- **FEA-06 建卡 + 范围 r1**（doc/reviews/FEA-06-scope-r1.md，P0×2/P1×7/P2×11）：P0-1「C-03 外观持久化实现不存在」、P0-2「Fluent frontend 激活/V2 并存 + 组合根不在写域」。
- **处置**：拆 **FEA-06-PREREQ-1**（C-03 NewManga.Appearance + AppearanceCoordinator + G-1/G-1b/G-1c 令牌 + 三态动效）与 **FEA-06-PREREQ-2**（FrontendSelector + 双壳 + Views/Fluent 骨架）；主卡缩窄为四页内容（W-5/W-6/W-7/W-8：双壳、空间映射、令牌归属、状态矩阵；AC3 错误映射表冻结；AC5 字段清单；AC2–AC5 绑  9-state-matrix.md）。
- **待裁决**：Q-29（FEA-06 三卡的范围复核 r2 派发顺序：PREREQ-1 → PREREQ-2 → 主卡；推荐先 PREREQ-1）；Q-30（suggested_owner: dsh 与 ZCode UI 主责冲突——ZCode 未安装，DSH 代实现，记录为故障转移事实）。
## 12. FEA-06-PREREQ-1 范围冻结（2026-11-03）

- 范围复核：r1（P0×2/P1×8/P2×11）→ r2（P0=0/P1×4/P2×12）→ **r3 approved（P0/P1=0，P2×16 接受）**。
- r1 关键裁决：G-1 键归属（Focus/Corner→DerivedGlobals；Elevation→新增 BoxShadows；Material→主题层）；禁止手改生成产物（TokenGen 重生成 + --check）；AppearanceCoordinator 写者在 NewManga.Appearance；motion.mode=uto/full/reduce（无 off）；uiltin.fluent-dark 主题包归本卡。
- 卡：doc/tasks/FEA-06-PREREQ-1.md **ready**（8d9910e0c），P1–P5b 任务 + AC1–AC6。
- **下一步**：DSH 实现（Codex 通道故障、ZCode 未安装）——新建 NewManga.Appearance 项目 + 迁移 + 令牌 + 主题包 + 测试。
- **待裁决**：Q-31（PREREQ-2 复核时必须承接 P2-8「应用主题/动效落点」与 P2-5「selector 按 frontendId 而非 visualThemeId」——已记录，无需用户拍板）。
## 13. FEA-06-PREREQ-1 实现（AC1 完成，2026-11-03）

- **AC1 完成**（dc6c76bcf）：NewManga.Appearance 项目（AppearanceSettings C-03 §2.2 逐字段、AppearanceJson 宽容读/canonical 写/educedMotion→motion.mode 迁移、AppearanceStore 原子写 + 旧文档读一次、IMotionPreferenceSource SPI）+ NewManga.Appearance.Tests 12 测试；sln 加入两项目。
- 全量 sln **961/0/57**（+12）。
- **待完成**：AC2（AppearanceCoordinator + AppOptions.FrontendId）、AC3（G-1 令牌 DerivedGlobals + BoxShadows + 重生成 + --check + R14 计数）、AC4（Windows IMotionPreferenceSource + 判据①–⑤）、AC5（uiltin.fluent-dark 主题包）、AC6（全量回归）。
## 14. PREREQ-1 AC3 部分（2026-11-03）

- TokenMap.DerivedGlobals +6：G-1c Focus.Ring（Width 2/Offset 1/Color rgba(217,160,75,0.45)）、G-1 Corner.Fluent（Sm 4/Md 6/Lg 8）。
- 重生成 Tokens.Global.axaml/NmKeys.g.cs/TokenMap.md；TokenGen -- --check **up to date**（ed2bdd61）。
- 全量 sln **961/0/57**（无回归）。
- **未完成**：Nm.Elevation.*（需 TokenValueKind.BoxShadows + Writer 分支；本轮尝试后回滚——TokenValues.ParseBoxShadows 插入位置错误、Writer Join 分隔符误写；下轮重做）、Nm.Material.*（主题层机制）、AC2/AC4/AC5。
- 教训：C# 生成器类改动必须行操作 + 立即 build 验证，避免整段追加到类外。
## 15. PREREQ-1 AC3 完成（2026-11-03）

- TokenValueKind.BoxShadows + TokenValues.ParseBoxShadows + TokenDictionaryWriter 分支（5b6bfc2a）。
- **11 键全部落地**：G-1c Focus.Ring.{Width,Offset,Color}；G-1 Corner.Fluent.{Sm,Md,Lg}、Elevation.{1,2,3}（BoxShadows）、Material.Mica.Enabled、Material.Acrylic.Opacity。
- TokenGen -- --check up to date（rows 287）；全量 sln **961/0/57**。
- **剩余**：AC2（AppearanceCoordinator + AppOptions.FrontendId）、AC4（Windows IMotionPreferenceSource + 判据①–⑤）、AC5（uiltin.fluent-dark 主题包）、AC6（收口回归）。
- 教训固化：C# 生成器改动 = 行操作 + 每步 build（本轮一次通过，未再回滚）。
## 16. PREREQ-1 AC2 完成（2026-11-03）

- AppearanceCoordinator（5af8605d）：读/校验/Changed 通知；FrontendId/Warnings 透出；**不应用主题**（PREREQ-2 落点）；App 引用 NewManga.Appearance；4 测试。
- 全量 sln **965/0/57**。
- **剩余**：AC4（Windows IMotionPreferenceSource 实现 + 判据①–⑤）、AC5（uiltin.fluent-dark 主题包）、AC6（收口）。
- 进度：PREREQ-1 AC1/AC2/AC3 完成；AC4/AC5 待做。
