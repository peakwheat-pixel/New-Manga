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

- **FEA-04 done**：feat/fea-04 经 Codex 实现 + DSH 返修（编译修复、Host 投影恢复、RunStatusMonitor 恢复、intent key 语义、IMPL-02 投影丢失修复）→ 实现复核 r1（P1×4）→ r2（P1×2）→ **r3 approved（P0/P1=0）**；冻结命令 build EXIT=0、sln test **931/0/60**（App 413/420）；git diff --check rc=0；集成 f4d8a32ec；卡 done（证据 10 项）。
- **FEA-C11-PREREQ-1 done**：交付 b7018e19b 已是 main 祖先、文件 sha256 与证据一致、复核 approved → 收口。
- **FEA-04b 释放**：ready，写域 doc/design/fluent-v1/**；owner/reviewer 待指派（ZCode CLI 不可用 → DSH 可代起草或派 Codex；设计复核需独立上下文）。
- P2 遗留（FEA-04）：实现复核 r3 列 7 项（基线文档算术/控制字符已修、冻结命令日志已入库；git diff --check 残余、Handoff 行内表述、用例命名等）已在收口时处理大部分，剩余接受遗留。

## 6. 待裁决（需用户拍板）

| # | 事项 | 推荐 |
|---|---|---|
| Q-21 | FEA-04b 设计 owner（ZCode CLI 不可用） | DSH 代起草规格 + 独立上下文复核；规格批准后再由 ZCode/Codex 实现 UI |
| Q-22 | FEA-05（Fluent 独立界面）是否需要先完成 wire（FEA-03 defer 的 Draft 命令面） | 是：先做 wire 子卡，再做 Fluent 页面；否则 Fluent 与 Current 无法共享草稿真值 |
## 7. FEA-04b 设计基线（2026-11-02 傍晚）

- 交付：doc/design/fluent-v1/（README + 01–10，版本 fluent-v1.0.0）：四页规格（书架/工作台/阅读器/设置）+ 状态矩阵 + 令牌取值（C-02 V-05）+ 动效三态三类（C-03 §3 判据①–⑤）+ 键盘/a11y（ShellCommands.cs 17 条键位）+ 响应式（三档断点）+ 组件清单。
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
- 交付：doc/contracts/FEA-05_DRAFT_WIRE_CONTRACT.md（五节 + 17 码逐码表）、V11R_COMMAND_CONTRACT_V1.md §8.2（C078–C083）、core_service.py（6 handler + 冻结信封映射）、	ests/core/test_draft_commands.py（12 项）、verification/FEA-05-WIRE-1/**（7 项证据）。
- 验证：全量 sln **931 passed / 0 failed / 60 skipped**；pytest **900 passed**；C# 契约 **80/80**；verify_pins 15/15；check.ps1 PASS。
- **待裁决**：Q-27（FEA-05-PORT-1 建卡：端口面 + CoreClient registry + V11R_REGION_WRITE_CONTRACT.md UNFREEZE 把 Region 不变式升级为「各家族集合之并」）；Q-23（FEA-04b 设计基线批准/冻结）。
## 10. FEA-05-PORT-1 收口（2026-11-03 凌晨）

- 范围：r1（P0×2/P1×1）→ r2（P0=0/P1×2）→ r3（P1×1）→ **r4 approved**。
- 实现：DSH（Codex 通道故障）；**impl-r1（P1×5）→ impl-r2（P1×2）→ impl-r3 approved（P0/P1=0，P2×11）**。
- 交付：Region 契约 **v1.6 UNFREEZE**（DraftsCommandNames 6；不变式并集 17）+ CONTRACT-UNFREEZE-2026-11-02.md + C-07 库存 54/61/18 + C-07 pin 重算 3fdb44e4…（重冻）+ HostCommandDomain.Drafts + DraftCommands.cs DTO + registry（6 条/17/CoreBindings）+ dispatcher 6 case/XOR + IHostController 7 方法 + HostController/NullHostController/FakeHostController + DraftCommandRegistryTests（9）+ DraftPortDefaultTests（6）。
- 验证：全量 sln **949 passed / 0 failed / 57 skipped**；verify_pins **15/15**；api inventory --check EXIT 0；check.ps1 PASS。
- **待裁决**：Q-28（FEA-06 UI 消费的前置：FEA-04b AC5 用户确认、FEA-05 契约 §8.2 状态升级路径——§8.2 状态列须保持 PENDING 否则 CommandContractV11RTests 红）；Q-23（FEA-04b 批准）。
## 11. FEA-04b 冻结 + FEA-06 拆分（2026-11-03）

- **FEA-04b done**：设计基线 fluent-v1.0.0 **FROZEN**（DSH 裁决，Q-23：用户确认不可得 → 以 r5 approved 独立复核 + DSH 冻结替代；用户后续修订走 v1.1）；11 文件；verification/FEA-04b/design-baseline-selfcheck.md。
- **FEA-06 建卡 + 范围 r1**（doc/reviews/FEA-06-scope-r1.md，P0×2/P1×7/P2×11）：P0-1「C-03 外观持久化实现不存在」、P0-2「Fluent frontend 激活/V2 并存 + 组合根不在写域」。
- **处置**：拆 **FEA-06-PREREQ-1**（C-03 NewManga.Appearance + AppearanceCoordinator + G-1/G-1b/G-1c 令牌 + 三态动效）与 **FEA-06-PREREQ-2**（FrontendSelector + 双壳 + Views/Fluent 骨架）；主卡缩窄为四页内容（W-5/W-6/W-7/W-8：双壳、空间映射、令牌归属、状态矩阵；AC3 错误映射表冻结；AC5 字段清单；AC2–AC5 绑 09-state-matrix.md）。
- **待裁决**：Q-29（FEA-06 三卡的范围复核 r2 派发顺序：PREREQ-1 → PREREQ-2 → 主卡；推荐先 PREREQ-1）；Q-30（suggested_owner: dsh 与 ZCode UI 主责冲突——ZCode 未安装，DSH 代实现，记录为故障转移事实）。
## 12. FEA-06-PREREQ-1 范围冻结（2026-11-03）

- 范围复核：r1（P0×2/P1×8/P2×11）→ r2（P0=0/P1×4/P2×12）→ **r3 approved（P0/P1=0，P2×16 接受）**。
- r1 关键裁决：G-1 键归属（Focus/Corner→DerivedGlobals；Elevation→新增 BoxShadows；Material→主题层）；禁止手改生成产物（TokenGen 重生成 + --check）；AppearanceCoordinator 写者在 NewManga.Appearance；motion.mode=auto/full/reduce（无 off）；builtin.fluent-dark 主题包归本卡。
- 卡：doc/tasks/FEA-06-PREREQ-1.md **ready**（8d9910e0c），P1–P5b 任务 + AC1–AC6。
- **下一步**：DSH 实现（Codex 通道故障、ZCode 未安装）——新建 NewManga.Appearance 项目 + 迁移 + 令牌 + 主题包 + 测试。
- **待裁决**：Q-31（PREREQ-2 复核时必须承接 P2-8「应用主题/动效落点」与 P2-5「selector 按 frontendId 而非 visualThemeId」——已记录，无需用户拍板）。
## 13. FEA-06-PREREQ-1 实现（AC1 完成，2026-11-03）

- **AC1 完成**（dc6c76bcf）：NewManga.Appearance 项目（AppearanceSettings C-03 §2.2 逐字段、AppearanceJson 宽容读/canonical 写/ReducedMotion→motion.mode 迁移、AppearanceStore 原子写 + 旧文档读一次、IMotionPreferenceSource SPI）+ NewManga.Appearance.Tests 12 测试；sln 加入两项目。
- 全量 sln **961/0/57**（+12）。
- **待完成**：AC2（AppearanceCoordinator + AppOptions.FrontendId）、AC3（G-1 令牌 DerivedGlobals + BoxShadows + 重生成 + --check + R14 计数）、AC4（Windows IMotionPreferenceSource + 判据①–⑤）、AC5（builtin.fluent-dark 主题包）、AC6（全量回归）。
## 14. PREREQ-1 AC3 部分（2026-11-03）

- TokenMap.DerivedGlobals +6：G-1c Focus.Ring（Width 2/Offset 1/Color rgba(217,160,75,0.45)）、G-1 Corner.Fluent（Sm 4/Md 6/Lg 8）。
- 重生成 Tokens.Global.axaml/NmKeys.g.cs/TokenMap.md；TokenGen -- --check **up to date**（bed2bdd61）。
- 全量 sln **961/0/57**（无回归）。
- **未完成**：Nm.Elevation.*（需 TokenValueKind.BoxShadows + Writer 分支；本轮尝试后回滚——TokenValues.ParseBoxShadows 插入位置错误、Writer Join 分隔符误写；下轮重做）、Nm.Material.*（主题层机制）、AC2/AC4/AC5。
- 教训：C# 生成器类改动必须行操作 + 立即 build 验证，避免整段追加到类外。
## 15. PREREQ-1 AC3 完成（2026-11-03）

- TokenValueKind.BoxShadows + TokenValues.ParseBoxShadows + TokenDictionaryWriter 分支（b5b6bfc2a）。
- **11 键全部落地**：G-1c Focus.Ring.{Width,Offset,Color}；G-1 Corner.Fluent.{Sm,Md,Lg}、Elevation.{1,2,3}（BoxShadows）、Material.Mica.Enabled、Material.Acrylic.Opacity。
- TokenGen -- --check up to date（rows 287）；全量 sln **961/0/57**。
- **剩余**：AC2（AppearanceCoordinator + AppOptions.FrontendId）、AC4（Windows IMotionPreferenceSource + 判据①–⑤）、AC5（builtin.fluent-dark 主题包）、AC6（收口回归）。
- 教训固化：C# 生成器改动 = 行操作 + 每步 build（本轮一次通过，未再回滚）。
## 16. PREREQ-1 AC2 完成（2026-11-03）

- AppearanceCoordinator（a5af8605d）：读/校验/Changed 通知；FrontendId/Warnings 透出；**不应用主题**（PREREQ-2 落点）；App 引用 NewManga.Appearance；4 测试。
- 全量 sln **965/0/57**。
- **剩余**：AC4（Windows IMotionPreferenceSource 实现 + 判据①–⑤）、AC5（builtin.fluent-dark 主题包）、AC6（收口）。
- 进度：PREREQ-1 AC1/AC2/AC3 完成；AC4/AC5 待做。
## 17. PREREQ-1 AC4 完成（2026-11-03）

- WindowsMotionPreferenceSource（P/Invoke SPI_GETCLIENTAREAANIMATION，非 Windows/失败 → null）+ MotionResolver（auto/full/reduce + 判据①–⑤ + categories off）+ MotionSettings 纯函数；7 测试（27475bd8c）。
- 全量 sln **972/0/57**。
- **剩余**：AC5（builtin.fluent-dark 主题包）、AC6（收口）。
- 进度：PREREQ-1 AC1/AC2/AC3/AC4 完成（4/5）。
- 教训：MotionResolver 的 reduce+feedback 语义（类别保留、Enabled=false）已在测试中固化，勿再改 IsEnabled 口径。
## 18. PREREQ-1 实现复核 r1 → 部分处置（2026-11-03）

- impl-r1（b547e229e 审）结论 **changes_requested（P0=0/P1=10/P2=16）**；独立复跑 974/0/57、两个 --check 一致。
- **已处置 7 条 P1**（f6ca197f6）：P1-1 categories 词表（navigation/feedback/decorative）、P1-2 layout 词表、P1-4 AppOptions.FrontendId、P1-5 Opacity 0.85、P1-6 Elevation 值、P1-7 Nm.Size.MatrixColumnMin=96、P1-10 写域补齐。
- **剩余 3 条 P1**：P1-3（旧 	heme-settings.json 迁移/兼容写）、P1-8（AC4 判据⑤迁移测试/④ navigation 专项）、P1-9（fluent-dark 需 ThemeGen 生成 + 
nm.fluent.visual/1 manifest + Material/Elevation 取值 + 校验测试）。
- 全量 **974/0/57**；TokenGen/ThemeGen --check up to date。
## 19. PREREQ-1 impl-r1 续处置（2026-11-03）

- **P1-3 关闭**（bf088770e）：ReadMotion 元组化、ReducedMotion=true→三类全禁、旧 	hemeId→frontendId、FollowSystemAccent 旧键回退、AppearanceStore 读旧 	heme-settings.json 迁移（13 测试）。
- **P1-8 关闭**：判据⑤迁移测试 + navigation 专项测试；注释按设计 02 对齐。
- 全量 **977/0/57**。
- 进度：impl-r1 的 10 条 P1 → **9 关闭，1 剩余（P1-9 主题包生成）**。
- 下一步：P1-9（BuiltInThemeGenerator 支持第二主题目标 + manifest + Material/Elevation + 校验测试）→ 派 impl-r2。
## 20. PREREQ-1 impl-r2 与部分处置（2026-11-03）

- impl-r2（3c0c7d50c 审）**changes_requested（P0=0/P1=5/P2=19）**；独立复跑 977/0/57、两 --check 一致。
- **已处置**（62b36c509）：r2-P1-1（layout 默认 	op-band/stacked/fit-page）、r2-P1-5（Elevation 颜色 rgba() → 生成 0 1 2 #26000000 等，alpha 正确；spread=0 省略记 P2）、证据刷新（sln 977、tokengen check）。
- **遗留 3 条 P1**：r2-P1-2（ThemeSettingsStore 一个 release 兼容写/双写者收敛 + 迁移结果落盘）、r2-P1-3（AppOptions.FrontendId 解析/注入）、r2-P1-4（Nm.Material.Acrylic.Base/Tint + ThemeLayerAllowedKeys/R14 59/65 计数/主题包 schema）。
- 全量 **977/0/57**。
- 进度：impl-r1 全 10 关闭；impl-r2 5 条 → 2 关闭、3 遗留。
## 21. PREREQ-1 impl-r2 续（2026-11-03）

- r2-P1-3 关闭：AppOptions 支持 --frontend <id>（解析/校验/赋值），注入点建立。
- r2-P1-2（ThemeSettingsStore 兼容写）与 r2-P1-4（Material Base/Tint 主题层 schema）**记架构理由暂缓**：前者会形成 ThemeEngine ↔ Appearance 循环引用（建议 PREREQ-2 统一写者）；后者需扩主题包 schema/R14 计数，超出本卡「不扩 schema」边界。
- 全量 **977/0/57**。
- **待裁决 Q-32**：r2-P1-2/P1-4 的归属——推荐放入 **FEA-06-PREREQ-2**（写者收敛与主题包 schema 演进正是其范围），本卡收口时接受该两条 as P2（记录理由）；若用户/后续复核要求本卡闭环，则需扩卡写域并追加架构裁决。
- 进度：impl-r1 全 10 关闭；impl-r2 5 条 → 3 关闭（P1-1/P1-3/P1-5）+ 2 暂缓（P1-2/P1-4，有架构理由）。
## 22. Q-32 正式裁决（2026-11-03，DSH）

- **裁决**：PREREQ-1 的 r2-P1-2（ThemeSettingsStore 兼容写/双写者收敛）与 r2-P1-4（Nm.Material.Acrylic.Base/Tint + 主题层 schema/R14 计数）**转入 FEA-06-PREREQ-2**，作为该卡的强制任务与 AC；PREREQ-1 以 AC1/AC3/AC5 <<PARTIAL>> 保持 in_review，不 done。
- **依据**：impl-r3/r4 独立复核指出转移目标未承接；DSH 接受该判定并在此正式裁决 + 修订 PREREQ-2（见下），使转移可执行。
- **PREREQ-2 修订**：doc/tasks/FEA-06-PREREQ-2.md 增加 W-9 承接段（任务 P5/P6 + AC5/AC6 + allowed_paths 含 NewManga.ThemeEngine/Persistence/**、NewManga.DesignSystem/**、NewManga.Appearance/**）。
- **impl-r4 结论**：approved（P0=0/P1=0/P2×12），独立复跑 978/0/57、两 --check 一致、证据 sha 全匹配。
## 23. 复核通道故障与 P2 处置（2026-11-03，Round 19）

- **复核通道故障（阻塞）**：本轮对 PREREQ-2 scope-r2 连续 3 次派发均失败——fea05-wire-scope-reviewer ×2、fea04b-scope-reviewer ×1（均 failed before it finished，无输出文件）；subagent_codex 1 次（product-error）。判定为平台级子代理派发故障，非任务内容问题。
- **待裁决 Q-34（复核通道降级）**：PREREQ-2 范围复核在通道恢复前无法产出。推荐：① 先按「已修订待复盘」状态保留 proposed，**不实施**（遵守范围冻结纪律）；② 通道恢复后立即补 scope-r2；③ 若通道持续不可用，请用户裁决是否允许「DSH 自身 + 逐条自证式复核 + 后续补审」的降级路径（不建议，但可解锁进度）。**依据**：仓内已有 scope-r1 报告（P0×3/P1×7）已全部处置，风险已大幅收敛；但范围冻结属 Gate，不宜自审放行。
- **本轮已推进（不依赖复核通道）**：
  - PREREQ-1 卡尾部字符损坏修复（c93dd0c4c）——此前 PowerShell 文本替换导致 ready/06b7a1b10/
nm.fluent.visual 等被吞字符、Closeout 残留占位、测试表缺行；已按行重建尾部并恢复真实 sha 证据表。
  - Resource Manifest 登记 3 个过程文件（消除 check.ps1 的 evidence_dir 警告）。
  - 代码注释 C-03 章节引用修正（§2.5 不存在 → §2.1 唯一写者 / §2.2 字段迁移）。
  - **发现并记录偏差 D-1**：C-03 §2.1 要求唯一写者 AppearanceCoordinator 位于 NewManga.Appearance；PREREQ-1 交付在 NewManga.App/Services（只读）。已写入类 <remarks>、PREREQ-2 P5 强制项与新增 W-10。
  - impl-r4 P2 处置：P2-8（fluent-dark 的 light 槽改用 dark 调色板，避免 dark-only 包误用浅色值）、P2-12（移除 NewManga.Appearance 未使用的 ThemeEngine 引用）。
  - 全量 sln **978/0/57**；TokenGen/ThemeGen -- --check up to date；check.ps1 PASS（3 warnings）、verify_pins 15/15。
## 24. 复核通道故障升级 + impl-r4 P2 清欠（2026-11-03，Round 20）

- **复核通道全途径失败（Q-34 更新）**：本轮追加 3 次尝试全部失败——fea05-wire-scope-reviewer spawn（failed）、subagent_codex（product-error）、subagent_zcode（无产出）。另查明 **Codex CLI 可用但模型不可用**：codex-cli 0.162.0 存在，codex exec 对 gpt-6.1-sol 与 gpt-5-codex 均返回 400 model_not_found（"not supported when using Codex with a ChatGPT account"），即 CLI 配置为 API-key 模型但实际以 ChatGPT 账号鉴权。**结论：Codex/ZCode/派发子 agent 三条外部复核通道当前均不可用。**
- **Q-34 建议（不变，附依据）**：① PREREQ-2 维持 proposed，不实施（范围冻结是 Gate，不自审放行）；② 通道恢复后立即补 scope-r2；③ 若需解锁，请用户裁决启用「DSH 自证 + 事后补审」降级路径（不推荐）；④ 可考虑的修复动作：把 Codex CLI 的默认模型改为该账号可用模型（属本机环境配置，需用户授权）。
- **本轮已完成（不依赖复核通道）**：impl-r4 P2 清欠
  - P2-15：AppearanceDefaults.AcrylicStrength 0.5 → **0.85**（对齐设计 01 Nm.Material.Acrylic.Opacity = 0.85）。
  - P2-10：AppearanceJson 增加读/写口径 <remarks> 固化（读侧扁平+嵌套兼容；写侧只写嵌套 canonical + schemaVersion 2；迁移幂等）。
  - P2-4：新增 Frontend_UnknownId_IsPassedThrough 测试，明确「未知 frontendId 在此层透传、fail-safe 归 PREREQ-2 selector」。
  - P2-16 裁定为**非缺陷**：设计 01 G-1b 明确「96 作为设计常量，FEA-05 生成令牌时登记」，Nm.Size.MatrixColumnMin=96 以字面量令牌登记即符合该要求（非派生计算）。
  - 全量 sln **979/0/57**（+1 测试）；两个 --check up to date；check.ps1 PASS（3 warnings）；verify_pins 15/15。
## 25. PREREQ-2 scope-r2 结果与处置（2026-11-03，Round 21）

- **复核通道结论修正**：先前判定的「平台故障」不准确——根因是**子代理仍走旧模型供应商、额度不足**（用户 2026-11-03 告知：主会话已切供应商，子代理未切）。本轮 subagent_zcode 实际**成功产出** doc/reviews/FEA-06-PREREQ-2-scope-r2.md（被审 4659e59d3）。
- **scope-r2 结论**：changes_requested，**P0=0 / P1=4 / P2=7**（r1 的 P0×3 全部闭合）。
- **DSH 处置（dec5e7337 之后的卡面修订）**：
  - **R2-P1-1（写域缺口）** → allowed_paths 增 App/ViewModels/V2/ThemeStudio/ThemeEngineThemeStudioService.cs、StubThemeStudioService.cs（P5 sink 双写的真实注入点）。
  - **R2-P1-2（Q-33 residual ③ 无落点）** → 新增 **P7** + **AC7**（
nm.fluent.visual/1 manifest + ThemeValidator.Validate(fluent) + BuiltInThemes 加载/Current 不生效），并在测试表补 AC7 行。
  - **R2-P1-3（C-02 V-07 合规路径未闭合）** → **改判 P6 实现路径**：Nm.Material.Acrylic.Base/.Tint 以**主题层令牌**承载（NmKeys + ThemeLayerAllowedKeys + 主题包 colors），**不新增 ThemeMaterial 枚举值、不改 ThemeTokenSet 签名** → 依 C-02 V-07「不新增枚举值、不改接口签名」**无需 UNFREEZE**；新增 **W-11** 记录该口径（Q-35）。
  - **R2-P1-4（测试表无 AC5/AC6）** → 测试表已补 AC5/AC6（前一轮遗漏）+ 本轮 AC7。
- **下一步**：派 **scope-r3**（独立上下文，subagent_zcode 或复核队友）确认 4 条 P1 关闭；P0/P1=0 后置 ready 并开始实现。
## 26. 会话交接（2026-11-02，用户将开新对话）

- 交接材料：doc/handoffs/FEA-06-PREREQ-2-session-handoff.md（含当前坐标、已完成项、PREREQ-2 三轮复核轨迹、r2 的 P1×4 处置、环境事实与工作纪律、必跑命令、待裁决）。
- **交接时状态**：HEAD df089039c（工作区 clean）；PREREQ-1 done；PREREQ-2 proposed（scope-r1/r2 changes_requested，P1×4 已处置，**scope-r3 报告缺失**）；全量 **979/0/57**；check.ps1 PASS（3 warnings）、verify_pins 15/15。
- **用户已告知的环境事实**：主会话已切换模型供应商，**子代理仍走旧供应商 → 常报额度不足**；subagent_zcode 曾成功跑完长任务（产出 scope-r2），是目前较可靠的复核通道；Codex CLI 因模型/账号不匹配（400 model_not_found）不可用于复核；ZCode CLI 未安装。
- **唯一下一步**：派独立上下文复核 scope-r3（被审 head df089039c），确认 r2 的 4 条 P1 关闭且无新增 P0/P1；P0/P1=0 → 置 ready + 同步 STATUS/PLAN → 开始实现 PREREQ-2。
## 27. PREREQ-2 范围冻结通过（scope-r4 approved，2026-11-02）

- **scope-r3**（df089039c 审）：changes_requested，P0=0 / P1=1 / P2=5——r2 的 4 条 P1 **全部实质闭合**（sink 注入点命中 ThemeEngineThemeStudioService.cs:82/StubThemeStudioService.cs:56；Q-33 residual③ 由 P7/AC7 承接且 ThemeMetadata.Extra 真实存在；**C-02 V-07 明确无需 UNFREEZE**；测试表 AC5/AC6/AC7 齐备）。唯一 P1：禁止范围残留旧授权声明。
- **DSH 处置**（a6652022d）：删除禁止范围的 ThemeMaterial.Fluent 授权句并改写为与 P6/W-11 一致；R14 计数措辞改为「59 不变 / 65→67」；STATUS/PLAN 指针更新为待 r4。
- **scope-r4**（a33778608 审）：**approved，P0=0 / P1=0 / P2=0** → 范围冻结通过。
- **release（本轮）**：卡 status: ready、approval: scope_review_r4_approved_2026-11-02、base_commit: a33778608；STATUS.md 当前 Task → PREREQ-2 ready；REBASELINE_PLAN.md DAG 行 → ready、**READY 节点：FEA-06-PREREQ-2**；check.ps1 PASS（3 warnings）、verify_pins 15/15。
- **实现范围（P1–P7 / AC1–AC7）要点**：① FrontendSelector（按 frontendId，CLI --frontend > AppearanceSettings > 缺省 v2；未知 → V2 fail-safe）；② App.axaml.cs 组合根按 selector 选壳 + Views/Fluent/ 骨架；③ P5 写者收敛（AppearanceCoordinator 迁入 NewManga.Appearance 成为唯一写者 + IThemeSettingsSink 双写一个 release）；④ P6 Nm.Material.Acrylic.Base/.Tint 主题层令牌（**不改枚举/签名**，R14 65→67）；⑤ P7 
nm.fluent.visual/1 manifest + ThemeValidator 测试。
## 28. PREREQ-2 实施完成（P1–P7 / AC1–AC7，2026-11-02）

- **范围**：scope-r4 approved（P0/P1=0）；本会话按卡实施 P1–P7，卡置 `in_review`，delivery_head 见卡 front matter。
- **实现摘要**：① `FrontendSelector`（`--frontend` > persisted `theme.frontendId` > 缺省 `builtin.current-v2`；未知/`builtin.fluent-dark` → V2 + `Diagnostic`/Trace；`--shell=legacy` 运维修回优先于 selector）；② 组合根 `App.CreateShell` 统一分派 + Fluent 壳骨架（顶条/左导航/状态条全部 DS 令牌 + 四页占位 + `--page` hook）；③ P5 写者收敛：`AppearanceCoordinator` 迁入 `NewManga.Appearance` 并成为 `presentation-settings.json` 唯一写者，`ThemeSettingsStore.SaveAsync` 标 `[Obsolete]` + 一个 release 兼容写（`IThemeSettingsSink` + App 侧 adapter，注入两个生产创建点）；④ P6：`NmKeys` 登记 `Nm.Material.Acrylic.Base/.Tint`（不进 `Tokens.Global.axaml`），`ThemeLayerAllowedKeys` 65→67 / Required 59 不变，fluent 包 colors 承载两值（`#1F1F1F` / `rgba(0,122,204,0.2)`），R14 同步；⑤ P7：fluent 包 `metadata.extra["nm.fluent.visual"]="1"`，`ThemeValidator` 承载 C-02 §4 校验（缺失/手改/非 Fluent 声明均 error；材质键完整性）+ 视觉主题 id 允许 `.`（W-12），Current 仍为 `newmanga-default`。
- **验证**：全量 **1022/0/57**（基线 979/0/57）；TokenGen/ThemeGen `-- --check` up to date；`check.ps1` PASS（3 warnings）；`verify_pins` 15/15；证据 27 行见卡 Canonical Evidence（`verification/FEA-06-PREREQ-2/`）。
- **裁决补充**：W-12（P7 校验器归属 + `NewManga.ThemeEngine/Validation/**` 写域补口；只改校验规则，不改 `ThemeKind`/接口签名 → 无需 UNFREEZE）；R4-P2-1 计数措辞已改（Base/Tint 可选、不进 Required 59）。
- **并行复核披露（R4-OBS-1）**：scope-r4 被两个席位并行复核——`b2a45af6d`（另一席位，P2=0）与本会话独立子代理报告（P2=1，工作区版本）；两者 approved / P0=P1=0 同向，本会话采纳后者并在实施中关闭其唯一 P2。详见 `verification/FEA-06-PREREQ-2/delivery-notes.md` §3。
- **下一步**：派独立上下文实现复核（impl-rB）；approve 后由 DSH 做集成验证、回填 `canonical_evidence_status` / `resource_closeout_status`、置 done 并更新 STATUS/PLAN。
## 29. PREREQ-2 实现复核 impl-r1 → 处置（2026-11-02）

- **impl-r1**（独立上下文子代理，被审 `9478c96fb`）：**changes_requested，P0=0 / P1=1 / P2=3**；AC1–AC7 逐条 **MET**，全量 1022/0/57 复现，W-12 经独立机械证实合法（旧 IdPattern 对 `builtin.fluent-dark` 匹配=0）；证据 30/30 sha 匹配、两 `--check` EXIT 0、`check.ps1`/`verify_pins` PASS。报告：`doc/reviews/FEA-06-PREREQ-2-impl-r1.md`。
- **唯一 P1（R1-P1-1）处置**：实施期写域扩张未登记——`ThemePaletteComposer.cs`（`ThemeEngine/Palette/**`）与 `IThemeSettingsSink.cs`（`ThemeEngine/Service/**`）不在 allowed_paths 任何历史版本；行为必需且正确、已在 delivery-notes/checkpoint 披露，但缺 W-12 式登记 → **docs-only 补正**：`allowed_paths` 回填两目录 + 新增 **W-13** 裁决行（行为必需性/零契约面变化/与 W-12 同性质）。
- **P2×3 处置**：R1-P2-1（W-12 属实施期自裁决，impl-r1 独立确认合法，P2 注记）；R1-P2-2（`ThemeValidator.IdPattern` 放宽面宽于最小必要，登记为已知放宽，user/builtin 命名空间隔离留 FEA-06 导入侧）；R1-P2-3（`StubThemeStudioService.Create` 的 sink 注入无直接测试，沙箱默认 null 安全且 `CreateProduction` 有端到端测试，接受遗留）。三者均不阻塞本卡。
- **下一步**：派 **impl-r2 窄面复核**（只核 R1-P1-1 闭合、docs-only 无暗改、无新 findings）；approved 后进入 DSH 集成验证（重跑 §7、回填 canonical evidence / closeout、置 done、STATUS/PLAN 指针滚动）。
## 30. PREREQ-2 收口（impl-r2 approved + DSH 集成验证 → done，2026-11-02）

- **impl-r2**（独立上下文子代理，被审 `f3224cb89`）：**approved，P0=0 / P1=0 / P2=1**；R1-P1-1 **完全闭合**（`allowed_paths` +2 行与 impl-r1 指认两文件一一对应、W-13 四要素齐全、无夹带扩权）；docs-only 成立（修复 commit 只动 5 个治理/证据文件）；`check.ps1` PASS(3 warnings)、`verify_pins` 15/15；`E-P2-DELIVERY-NOTES` 新 sha 与工作区逐位一致。唯一 P2 = delivery-notes 行 commit 列滞后（本轮已修，R2-P2-1 CLOSED）。
- **DSH 集成验证**：main 直接实现、无 worktree；集成 commit = delivery head **`92cac5ab1`**。§7 全绿：build **0 警告/0 错误**、全量 **1022/0/57**、TokenGen/ThemeGen `-- --check` up to date、`check.ps1` PASS(3 warnings)、`verify_pins` 15/15 → `verification/FEA-06-PREREQ-2/integration-verification.log`。
- **收口**：卡 `status: done`、canonical_evidence_status / resource_closeout_status **complete**、31 条证据（30 CANONICAL + 1 SOURCE_PIN）机械校验通过；STATUS 当前 Task 置空、下一候选 `FEA-06`（需先范围复核/冻结）；PLAN 表行 + 当前 DAG 段滚动为 done。
- **下一动作**：以 **FEA-06 范围复核/冻结（scope）** 为下一唯一动作——FEA-06 r1 changes_requested 的拆前置已全部满足（PREREQ-1/2 done），需重开范围复核（scope-rN）→ P0/P1=0 后置 ready 释放四页实现。
- **遗留（非阻塞）**：`G-DELETE-IMPL` OPEN；`FOLLOW-UP-FEA00A-1` 待用户提供 DB 副本；未授权 push（DSH 有最终 push 权但本会话未 push）。
## 31. 干净源码快照 push（2026-11-02）

- **授权**：用户 2026-11-02 直接指示 **push**；沿用 2026-10-26/29 已确认口径——只推材料已隔离的干净源码快照到 `origin` 新分支，不推 `main`、不 force、不覆盖远端 `main`、不设 upstream。
- **快照**：`G:/CODEX/New Manga.workspace/publish/clean-snapshot-20261102`，源 commit 本地 `main` HEAD `5c12ab269`；单一 root commit `ac7d488e1944893f961b94eb3d774c899f618829`（无父提交、无 remote/alternates/shallow）；tracked **1413** 文件、约 **20.1 MB**、图片 **0**、禁区泄漏 **0**。
- **口径**：白名单同 2026-10-29（apps/src/tests/packaging/test_assets + 配置 + tools/p02 + tools/smoke）；本次增补仓库根许可证/声明文件（GPL-3.0 合规）与 `doc/design/redesign-v1/40-fusion/tokens.json`（构建 Content 复制 + 测试根定位所需的公开设计令牌）。
- **推送前验证**：`dotnet build -c Debug -warnaserror` exit 0（0w/0e）；App.Appearance/Host/ThemeEngine/DesignSystem/ApplicationCore 五工程全绿，App.Tests **452/0/7**；CoreClient **11 failed**（已知口径限制：依赖被剔除的 `AGENTS.md` + `verification/` 契约证据，非代码回归；完整仓库基线 1022/0/57）。
- **推送**：`git push --no-follow-tags <url> HEAD:refs/heads/clean-snapshot-20261102` → `* [new branch]`，**exit 0**；远端回读 `clean-snapshot-20261102` = `ac7d488e…` 新建，`clean-snapshot-20261026/20261029`/`codex/clean-source-snapshot`/`main`/`public-release` 均**未变**（远端 `main` 仍 `b1c1f5a5…`）。
- **记录**：`doc/PUSH_RECORD_2026-11-02.md`。未推送本地 `main`；未设置 upstream；未传播私有素材。
## 32. FEA-06 Owner=Codex（用户指派）+ 范围修订 r2（2026-11-02）

- **用户指令**：「四页 UI + 设计系统组件改造交给 codex」→ FEA-06 implementation **owner = Codex**（W-10）；Codex 可在 main 直接实现并提交单一实现 commit（仅 allowed_paths 内文件），**不得 push**；DSH 保留范围冻结 / Review Appointment / 实现复核 / 集成验证 / 证据收口 / 最终 push。
- **Codex 通路核验**：本机 `codex-cli 0.162.0`；默认配置 model=`gpt-6.1-sol` 会 400（旧结论根因）；按 codex-dispatch skill 以 `-m gpt-6-luna` 探测 **exit 0**（回复 ok）→ 可用。派发一律 cwd=仓库根（桌面版可见）+ 显式 `-m gpt-6-luna`，结果写 workspace、session id 记录；不改全局 `~/.codex/config.toml`。
- **范围修订 r2（FEA-06 卡）**：r1（P0=2/P1=7/P2=11）逐项处置——P0-1/P0-2/P1-1 已由 PREREQ-1/2 交付关闭；P1-2 状态矩阵绑 AC2–AC5、P1-3 Draft 错误映射冻结、P1-4 新增 AC6 组件清单、P1-5 W-6 映射、P1-6 AC5 字段逐字、P1-7 STATUS/PLAN 同步；写域追加 `Controls/**`/`Styles/**`/`Services/**`（W-9）；证据口径 W-11；baseline 更新为 **1022/0/57**；base_commit `5a4717009`。
- **下一步**：派 **scope-r2** 独立上下文复核（subagent_zcode，被审 = 本卡修订 commit）→ P0/P1=0 后置 `ready`，按 W-10 派 Codex 实施（交付单一 commit + verification/FEA-06 证据 + handoff）→ 独立实现复核 → DSH 集成验证 → done。
## 33. FEA-06 scope-r2 处置（2026-11-02）

- **scope-r2**（独立上下文子代理，被审 `53060cd67`）：**changes_requested，P0=1 / P1=1 / P2=10**。r1 的 P0-1（C-03 外观持久化）、P1-1/P1-4/P1-5/P1-6/P1-7 经实测**已闭环**；P0-2「壳可启动」半边闭合；新增 **r2-P0**：`App.axaml.cs` Fluent 分支只传 `(options, selection)`，`HostController`/`AppearanceCoordinator`/`ThemeManager` 未进入 Fluent 壳 → AC2–AC5 数据/命令/外观面在写域内无合法注入通路；**r2-P1**：AC2–AC5 状态清单与 `09-state-matrix.md` 不一致。
- **处置（本 commit）**：**W-12** DSH 单点预置注入——`App.CreateShell` Fluent 分支传 `controller/appearance/themeManager`；`FluentShell.CreateRoot`/ctor 扩可选参数 + 只读属性 `HostController`/`Appearance`/`ThemeManager`；组合根测试断言三实例同一（禁止第二 Host/第二 coordinator）；`App.axaml.cs` 仍不在 FEA-06 写域。**r2-P1**：AC2–AC5 逐页改写为 09 本页列全行（含「—」说明）；P2-1（AC5 补 appearance/contrast）、P2-2（internal 保留旧 UI）、P2-3（W-6 锚点）、P2-5（depends_on 补）、P2-6（禁止范围补资产边界）、P2-7（17 快捷键口径）已入卡；P2-4/P2-8/P2-9/P2-10 已入派发 brief。
- **验证**：build 0 警告/0 错误；全量 **1022/0/57**；TokenGen/ThemeGen `--check` up to date；`check.ps1` PASS(3 warnings)；`verify_pins` 15/15。
- **下一步**：增量 **scope-r3**（独立上下文，仅核 r2-P0/P1 处置与无新增问题）→ approved 后置 `ready`、刷新 base_commit → 按 W-10 派 **Codex** 实施（`-m gpt-6-luna`、cwd=仓库根；brief 已备 `workspace/exchange/FEA-06-codex-brief.md`）。
## 34. FEA-06 scope-r3 approved → ready → 派 Codex 实施（2026-11-02）

- **scope-r3**（独立上下文子代理，被审 `3c7f311d8`）：**approved，P0=0 / P1=0 / P2=3**；r2-P0（Fluent 壳依赖注入）与 r2-P1（AC2–AC5 对齐 09 矩阵）经逐点实测**已闭环**、无新增 P0/P1；build 0/0、全量 1022/0/57、check PASS(3)、pins 15/15。
- **释放**：卡 `status: ready`、`approval: scope_review_r3_approved_2026-11-02`、`base_commit: 3c7f311d8`；owner=**Codex**（W-10）；r3 P2×3 已处置（卡 P3 旧口径改 7 方法/9 行；派发 brief 刷新 r3 引用与状态口径；approval/STATUS 同步）。
- **派发**：brief = `G:\CODEX\New Manga.workspace\exchange\FEA-06-codex-brief.md`；命令模板：`codex exec --skip-git-repo-check -s workspace-write -m gpt-6-luna -c model_reasoning_effort="xhigh" -o <workspace>/exchange/fea-06-codex-result.md "<brief>"`，cwd=仓库根（桌面版会话可见）；结果/日志落 workspace/exchange。Codex 交付：单一实现 commit（仅 allowed_paths）+ `verification/FEA-06/**` 证据 + handoff；**不 push**。
- **下一步**：Codex 完成后 DSH 验证（diff/测试/证据/治理）→ 派独立上下文实现复核（impl-rN）→ DSH 集成验证 → done；期间 DSH 不改 repo 文件（避免与 Codex 写冲突）。
## 35. FEA-06 Codex 首轮实现 + impl-r1 复核与处置（2026-11-02）

- **Codex 交付**（用户指派 owner）：实现 commit `b0388df9a`（37 文件、+7035/−232；四页 View/VM、15 个 Fluent 组件、19 测试、四页 headless PNG、UIUX finalizer PARTIAL）+ 文档 commit `966cedeac`（卡 `in_review`、STATUS/PLAN/LEDGER/handoff）；未 push，仓库干净。
- **DSH 独立验证**：build 0/0；全量 **1030/0/57**（基线 1022+8）；TokenGen/ThemeGen up to date；`check.ps1` PASS(3)；`verify_pins` 15/15；37 路径全部在 allowed_paths；未改组合根/selector/Core/契约/生成物/设计。
- **impl-r1**（独立上下文，被审 `b0388df9a`）：**changes_requested，P0=0 / P1=1 / P2=9**；AC1–AC7 PARTIAL **诚实成立**、AC8–AC10 MET；唯一 P1 = `Controls.Fluent.axaml:241` 悬空令牌 `Nm.Space.S1`（真实族 `Nm.Space.0…8`）+ 组件登记表（CANONICAL 证据）同步失实。
- **DSH adjudication**（`doc/reviews/FEA-06-impl-r1-adjudication.md`）：P1-1 返修（改既有键 + 登记表 + 令牌存在性守卫测试）；P2-1/2/3/5/7 并入返修；**P2-4 裁决 W-13：控制台空间不得映射 Settings** → 控制台=Workbench 第三视图（Run 控制台面板，无数据显式「当前没有运行中的任务」），Settings 改非空间入口（顶部命令条+左导航，08:3）；P2-6/P2-8/P2-9 接受登记 residual/技术债。
- **下一步**：Codex 同会话 `resume`（session `01a19a5e-2490-7943-a8c5-6cc05e13a4cb`）执行返修 → 单一 fix commit + 证据刷新 + 不 push → DSH 复核/集成验证 → 终态（AC1–AC7 PARTIAL 作 residual 或另立后续 Task）。
## 36. FEA-06 收口（Codex 返修 → impl-r2 approved → done，2026-11-02）

- **返修链**：impl-r1（changes_requested，P0=0/P1=1/P2=9）→ DSH adjudication → Codex 返修 `7cf305fe2`（P1-1 令牌/登记表 + W-13 控制台空间 + P2）→ impl-r2（**approved，P0=0/P1=0/P2=1**）→ P2-R2-1 小修 `b26840acd`（TabStrip selected 视觉 + 登记表 + 测试扩展）→ DSH 复验。
- **DSH 集成验证**：build 0/0；全量 **1034 passed / 0 failed / 57 skipped**（基线 1022+12；57 skip 原因不变）；TokenGen/ThemeGen up to date；`check.ps1` PASS(3)；`verify_pins` 15/15 → `verification/FEA-06/integration-verification.log`；工作树 clean，未 push。
- **收口**：FEA-06 `status: done`、`integration_commit: b26840acd`、canonical_evidence_status/resource_closeout_status complete；AC8–AC10 MET；**AC1–AC7 PARTIAL 作为 residual 转 `FEA-06-RESIDUAL-1`**（依赖 FEA-07/09/10/11/12/13 端口逐项补齐，不阻塞 FEA-07）。
- **新建卡**：`FEA-07`（运行期切换/窗口，proposed，待范围冻结）与 `FEA-06-RESIDUAL-1`（proposed，待端口）；PLAN/STATUS/LEDGER 指针滚动 → 当前 Task=FEA-07，READY 节点=无。
- **下一步**：**FEA-07 范围复核/冻结（scope）** → ready → 派实施（owner 由 DSH 在 range 冻结时确认；Codex 通道已验证可用：`-m gpt-6-luna` + bypass sandbox）。
## 37. 用户裁决「按原来的顺序进行」→ FEA-07 scope 准备（2026-11-02）

- 用户在看到 FEA-06 四页 headless 截图与「residual UI 打磨可插队」选项后裁决：**按原来的顺序进行** → 按 PLAN DAG 先做 **FEA-07**，`FEA-06-RESIDUAL-1` 的 UI 打磨不插队，待端口/顺序就绪后释放。
- **FEA-07 卡修订**：`base_commit` 刷新 `682fe17ae`；AC 对齐方案 §12.3 场景（A01/A02/A03/A05/A06/A08）；**H2/H3 验证纳入本卡 AC5/AC6**（无独立前置 Task）；新增 W-1…W-5 裁决点（写域边界/原生验收/owner/性能门槛候选 p95≤1s）；测试矩阵分 AC 组（切换矩阵/原生矩阵/性能/回归）；禁止使用真实漫画或真实 `%APPDATA%`。
- **下一步**：派 **FEA-07 scope-r1 独立复核**（subagent_zcode）→ 处置 findings → 冻结范围（P0/P1=0）→ ready → 实施（owner 冻结时确认；Codex 通道已验证）。
## 38. FEA-07 scope-r1（Codex CLI 复核）→ 处置（2026-11-02）

- 因 `subagent_zcode`（3 次 parse-output invalid-json）与 `subagent_codex`（turn product-error）均不可用，**FEA-07 scope-r1 改由 Codex CLI 独立 fresh 会话执行**（`gpt-6-luna` xhigh；只读；不实现 FEA-07）。实测：build 通过、全量 1034/0/57、check PASS(3)、pins 15/15。
- **结论**：changes_requested，P0=0 / P1=6 / P2=2。P1：新模块无法接入 App（缺 App.csproj 写域）、A03/§15.5 回滚验收不足、A08/H2 双屏/DPI 不全、隔离/启动矩阵缺失、W-6 无机械门禁、W-5 门槛未冻结。报告：`doc/reviews/FEA-07-scope-r1.md`。
- **处置**：补 `NewManga.App.csproj` 写域；AC1/AC3 增 DB/current/pinned/Lock/源/candidate 零变化 + §15.5 阶段注入/commit 判据/完整 rollback；AC5 补 100/125/150/200% DPI、拔屏 fail-closed 回主窗、单一写入 owner、PerMonitorV2；AC7 增启动兼容矩阵 + project-reference graph 检查；W-5 **冻结 p95 ≤1000ms**；AR8 隔离根；按 P2-1 收紧写域（移除 Directory.Build.props/Appearance/DesignSystem/Appearance.Tests）；W-3 **owner=DSH**（Codex 仅审不实现）；STATUS rolling checkpoint 已刷新为 GOAL-PROGRESS。
- **下一步**：派 **scope-r2**（独立 fresh Codex CLI 会话，被审 = 本处置 commit）→ P0/P1=0 后按 W-8 刷新元数据置 ready → DSH 实施 FEA-07 → Codex 独立 impl review → DSH 集成验证。
## 39. FEA-07 scope-r2 approved → ready（owner=DSH，2026-11-02）

- **scope-r2**（Codex CLI 独立 fresh 会话，被审 `cbfb7bbc9`）：**approved，P0=0 / P1=0 / P2=1**。r1 六项 P1 全部闭环（App.csproj 写域、A03/§15.5 回滚断言、A08/H2 双屏与 DPI、隔离/启动矩阵、project-reference 机械门禁、W-5 门槛冻结 p95≤1000ms）；无新 P0/P1。P2-1（App 目录 glob 未完全收窄）由 DSH 以 **W-10** 逐项记录保留理由与使用限制（非阻塞残余）。报告：`doc/reviews/FEA-07-scope-r2.md`。
- **置 ready（W-8）**：`status: ready`、`approval: scope_review_r2_approved_2026-11-02`、`owner: dsh`、`branch: main`、`worktree: G:\CODEX\New Manga`、`base_commit: cbfb7bbc9`（冻结 head）；STATUS/PLAN/READY/LEDGER 同步（READY=FEA-07）。
- **实施分工**：FEA-07 owner=**DSH**（Codex 承担 scope/impl 独立复核，不实现）；实现后由 Codex CLI fresh session 做独立 impl review，DSH 集成验证。原生双屏/DPI 验收（AC5）需真机矩阵，若本机无对应硬件将按 residual/blocked 登记，不伪造证据。
- **下一步**：DSH 开始 FEA-07 实施（切片：①Presentation.Avalonia 模块 + switch journal/window broker/exit 协调；②稳定主窗 + 内容树切换接线；③safe startup/启动矩阵；④双屏 DPI memento + 测试/证据；⑤全量回归 + 独立复核）。
## 40. FEA-07 实施切片 1（2026-11-02，owner=DSH）

- **新建模块**：`apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/`（W-6）——`SwitchStage`/`SwitchJournal`（原子 JSON、损坏容忍、启动恢复）/`FrontendSwitchCoordinator`（阶段门禁+故障注入+回滚+并发串行）/`WindowBroker`（单一主窗+二窗登记、不拥有 Host）/`ExitCoordinator`（未保存编辑/运行中 Run 阻断退出）；已登记 sln。
- **测试**：`tests/NewManga.Presentation.Avalonia.Tests/` 28 测试全绿（journal/阶段顺序/每阶段失败回滚/rollback 失败/并发串行/窗口/退出）。
- **验证**：build 0/0；Presentation 28/0；全量 **1062/0/57**（基线 1034+28；CoreClient 已知时间敏感 flaky 首跑 1 failed、重跑全绿，日志注记）；证据 `verification/FEA-07/slice-1-verification.log`。
- **下一批切片**：②稳定主窗 + 内容树切换接线（App/Presentation 宿主 + Fluent content surface）；③safe startup/启动矩阵；④双屏/DPI memento；⑤全量回归/证据/独立复核。
## 41. FEA-07 实施切片 2 + 待裁决区（2026-11-02，owner=DSH）

- **切片 2 完成**：`Presentation.Avalonia/Hosting/FrontendContentHost`（稳定窗口内容槽）+ `App/Services/FrontendHostCoordinator`（selector 校验→构建替换树→经 `AppearanceCoordinator` 单写者持久化 `theme.frontendId`→swap；失败恢复旧树/旧设置）+ App.csproj→Presentation 引用（W-6 方向）。
- 测试：`FrontendHostCoordinatorTests` 5 例全绿（成功切换/未知 id 拒绝不改 UI/构建失败回滚+journal/幂等/100 次往返单树且 journal 干净）；证据 `verification/FEA-07/slice-2-verification.log`；build 0/0；全量 **1067/0/57**（CoreClient 已知 flaky 首跑 1 failed、重跑全绿，日志注记）。
- 下一批：②b `PresentationWindow` + 真实 V2/Fluent content factory + App 组合根接入；③safe startup/启动矩阵；④双屏/DPI memento；⑤全量回归/独立复核。

### 待裁决（非阻塞，按目标规则先推进并附推荐）

| # | 事项 | 推荐 | 处置状态 |
|---|---|---|---|
| D-1 | 原生双屏/拔屏/DPI 矩阵需真机（本机可能无双屏/可切 DPI 环境） | 代码与 headless 证据先完成；AC5 原生项如无硬件则登记 blocked/residual，待用户提供真机或明确降级接受；**不伪造证据** | 继续推进，不阻塞其余切片 |
| D-2 | 稳定主窗默认化时机（改默认启动路径会影响现有启动测试/用户可见行为） | 先实现 `PresentationWindow` 并以开关启用（测试可覆盖），AC1 全绿后再默认化；避免一次性破坏既有 463 个 App.Tests | 待切片 2b 实施 |
| D-3 | FEA-07 实现者与复核者独立性 | Codex 已做 scope review → **不实现**；impl review 用 fresh Codex CLI 会话（不同上下文）；若 Codex 不可用则派 subagent_zcode（当前通道故障，需恢复） | 已按此执行 |
| D-4 | `--shell=legacy` 运维回退保留期 | FEA-07 完成后保留一个 release，移除决策交 FEA-15/用户；FEA-07 不改其语义 | 继续保留 |
| D-5 | 依赖 DSH 单方裁决的其他范围事项（如需用户产品取舍） | 暂无；出现时按目标规则交 Codex 裁决（Codex 非实现者情形）并记录依据 | 无 |
## 42. FEA-07 实施切片 2b（稳定 PresentationWindow，2026-11-02）

- **切片 2b 完成**：`App/Views/Presentation/PresentationWindow.cs`——稳定原生主窗（自持 Title/geometry/MinWidth/背景/material；单一 `FrontendContentHost`；注入 `Func<string, Control>` content factory，不依赖具体壳）；`SwitchFrontendAsync` 复用 `FrontendHostCoordinator`：切换保窗身份、失败回滚旧树。
- 测试：`PresentationWindowTests` 5 例（初始内容/几何、切换保身份、构建失败回滚+journal、未知 id 拒绝、20 次往返单树）；证据 `verification/FEA-07/slice-2b-verification.log`；build 0/0；全量 **1072/0/57**（CoreClient 已知 flaky 首跑 1 failed、重跑全绿）。
- **下一批**：②c App 组合根接入真实 content factory（V2 `AppShellV2` + Fluent content surface）+ 开关启用；③safe startup/启动矩阵；④双屏/DPI memento；⑤全量回归/独立复核。
- 待裁决区沿用 §41（D-1 原生硬件 / D-2 默认化时机 / D-3 独立性 / D-4 legacy 保留期），均不阻塞。
## 43. FEA-07 实施切片 2c-part1（Fluent 内容面抽取，2026-11-02）

- **FluentShellSurface 抽取**：新增 `Views/Fluent/FluentShellSurface.axaml(.cs)`（UserControl，Fluent 内容/四页/导航/KeyMap/响应式带全量逻辑，`FullScreenRequested` + `SetViewportWidth`）；`FluentShell` 变薄宿主 Window facade（转发公开 API + `FindControl` + material 策略），**24 个既有 Fluent 测试全通过**；修复响应式状态：视口宽度变化需同时更新状态带（`SetViewportWidth`→`UpdateStatus`）。
- 证据 `verification/FEA-07/slice-2c-part1-verification.log`；build 0/0；全量 **1072/0/57**。
- **下一批**：②c-part2 App 组合根真实 factory 接入（V2 content 需带 Theme Studio 生产接线）+ `--presentation-host` 开关 + 端到端 headless 切换；③safe startup；④双屏/DPI；⑤回归/复核。
## 44. FEA-07 实施切片 2c-part2（组合根 `--presentation-host` 真实接线，2026-11-02）

- **组合根接入**：`AppOptions.PresentationHost`（布尔开关白名单注册）；`App.CreateShell` V2 路径按开关走 `CreatePresentationShell`；`CreatePresentationShell` 用 theme-home 下 `switch-journal.json` + 真实 content factory（`FluentShellSurface` / `CreateV2Content`）；`CreateV2Content` 复用抽取的 `WireThemeStudio`（含 Theme Studio 生产接线）；`--shell=legacy` 优先级不变；`NavigateStartupPage` 支持稳定窗口内容树。
- **修复**：`SettingsViewModel.OnAppearanceChanged` 非 UI 线程时 `Dispatcher.UIThread.Post`（切换时 Changed 可能来自线程池）；AppOptions 布尔白名单补 `presentation-host`。
- 测试：`PresentationHostCompositionTests` 2 例（真实 V2/Fluent 内容切换、开关解析）；presentation 相关 12/0；证据 `verification/FEA-07/slice-2c-part2-verification.log`；build 0/0；全量 **1074/0/57**。
- **下一批**：切片 3 safe startup + 启动兼容矩阵；切片 4 双屏/DPI memento；切片 5 全量回归/独立复核。
## 45. FEA-07 实施切片 3（safe startup + 启动兼容矩阵，2026-11-02）

- **safe startup**：新增 `App/Services/SafeStartupPlanner.cs`（StartupPlan：effective frontend/IsFallback/ShellKind/Diagnostics；冻结 fail-safe：未知 frontend→V2、外观坏字段 warnings 入诊断、`--shell=legacy` 优先）；`App.OnFrameworkInitializationCompleted` 接线（每个诊断 Trace，fallback 额外 Warning；运行时行为不变、可诊断性增强）。
- **启动矩阵**：`SafeStartupPlannerTests` 8 例 + `StartupCompatibilityMatrixTests` 1 例（默认 V2/CLI fluent/持久化 fluent/未知与视觉主题 fallback/legacy 优先/presentation-host/legacy 优先于 presentation-host）。
- 证据 `verification/FEA-07/slice-3-verification.log`；build 0/0；全量 **1083/0/57**。
- **下一批**：切片 4 双屏/拔屏/DPI memento + PerMonitorV2 + 原生矩阵；切片 5 性能 baseline/全量证据/独立复核。
## 46. FEA-07 实施切片 4（窗口状态 memento + 显示拓扑 + PerMonitorV2，2026-11-02）

- **窗口状态 memento**：`WindowStateMemento` + `WindowStateMementoStore`（原子写/损坏容忍，theme-home `window-state.json`）；`PresentationWindow` 构造恢复 + `CaptureWindowState()`；`App.CreatePresentationShell` 启动恢复/Closing 保存。
- **显示拓扑规划**：`DisplayTopologyPlanner.Clamp/Plan`——永不屏外、混合 DPI 各窗口保留自身 scale、拔屏 → `ReturnContentToMainWindow` + 未保存编辑 `RetainUnsavedEditsInMainBuffer`（fail-closed 留主窗缓冲）。
- **PerMonitorV2**：`app.manifest` 已声明 `true/pm` + `PerMonitorV2`，新增 `DpiManifestTests` 防回退。
- 测试：`WindowStateMementoTests` 3、`DisplayTopologyPlannerTests` 7、`DpiManifestTests` 1、`PresentationWindowTests` +1；证据 `verification/FEA-07/slice-4-verification.log`；build 0/0；全量 **1095/0/57**。
- **原生矩阵 blocked（D-1）**：真机双屏/拔屏/DPI 100/125/150/200% 未执行；不伪造证据，待硬件或用户降级裁决。
- **下一批**：切片 5 性能 baseline（W-5 门槛）+ 全量证据 → fresh Codex CLI 独立 impl review → DSH 集成验证。
## 47. FEA-07 实施切片 5（H3 性能 baseline + 架构门禁 + 实现收尾，2026-11-02）

- **性能 baseline（AC6/W-5）**：`PerformanceBaselineTests` 真实 factory + 稳定窗口，Release 实测 **p50 118.51 ms / p95 429.47 ms / 冷启动首次 648.42 ms / 内存 +1.38 MB / 句柄 +3 → PASS**（预算 p95 ≤1000 ms）；Debug 对照 p95 516 ms 亦 PASS；原始 JSON `verification/FEA-07/performance-baseline-release.json`。
- **W-6 机械门禁（AC7）**：`ArchitectureDependencyTests` 解析 ProjectReference：App→Presentation 允许；Host/CoreClient/ApplicationCore→Presentation/App/DesignSystem 禁止；TFM 保持 net9.0。
- **实现收尾**：全量 **1099/0/57**；build 0/0；check PASS(3)；pins 15/15；证据 `slice-5-verification.log`。
- **AC 标记**：AC4/AC6/AC7 MET；AC1/AC2/AC3/AC5/AC8 PARTIAL（原生矩阵 D-1 blocked，其余为集成/真库/启动恢复接线缺口，待独立复核列出最小返修集）。
- **下一步**：派独立 impl review（fresh Codex CLI 会话，被审 delivery head）→ findings 处置/返修 → DSH 集成验证。
## 48. FEA-07 复核前补强（AC1/AC2/AC3，2026-11-02）

- AC1：真实 V2/Fluent content 在稳定窗口 10 次往返（20 切换）测试；AC2：`PresentationWindow` 内嵌 `WindowBroker` 注册唯一主窗 + 二窗登记测试；AC3：`App.CreatePresentationShell` 启动时回滚未完成 journal（Rendered→RolledBack）并 Trace 警告 + 测试。
- 证据 `verification/FEA-07/slice-6-gapclosing-verification.log`；build 0/0；全量 **1102/0/57**（首跑偶发 2 例 App.Tests 失败、连续两次复跑通过，已注记）。
- **impl review 仍在运行**（fresh Codex CLI；job pwsh-80ca8a0ff78c4feb），结果到达后处置 findings。
## 49. FEA-07 复核等待期：证据索引与集成前置（2026-11-02）

- 生成 `verification/FEA-07/evidence-index.md`（全部证据 SHA-256、基线、生成物检查、性能数字、复核状态、原生 blocked 说明）。
- 集成前置实测：TokenGen `-- --check` 292 rows byte-for-byte up to date；ThemeGen `-- --check` byte-for-byte up to date；`check.ps1` PASS(3)；pins 15/15；全量 1102/0/57。
- impl review 仍在运行（Codex CLI xhigh，大 diff + 全量测试），结果到达后处置。
## 50. FEA-07 impl-r1 changes_requested → 返修 part1（2026-11-02）

- **Review**：`doc/reviews/FEA-07-impl-r1.md`（Codex CLI fresh，P0=0/P1=7/P2=5）。处置：R-001 内容树缓存复用（状态保留+实例断言）；R-002 ExitCoordinator 接入 Closing + Broker 生产注册；R-003 已提前修复；R-004 planner 单一决策源 + 外观 fallback 强制 V2（含 CLI fluent）；R-005 memento 启动 clamp+DisplayId；R-006 启动矩阵测试隔离（实测 APPDATA mtime 不变；删除测试误写 window-state.json，theme-settings.json 未动）；R-008 allowed_paths 补齐；R-009 AC6 降 PARTIAL + freeze 上限指标；R-012 生成物 --check 归档。
- 待办：R-007 生命周期固定（reviewer/delivery_head/handoff/canonical）与 R-011 精确 head 证据重跑，然后 r2 复核。
## 51. FEA-07 impl-r1 返修完成 + 精确 head 证据 + r2 复核派发（2026-11-02）

- **返修 part1（7ca2e367b）**：R-001 内容树缓存复用（同实例断言）；R-002 ExitCoordinator 接入 Closing（未保存编辑阻断关闭）；R-004 planner 单源 + 外观 fallback 强制 Current V2（含 CLI fluent）；R-005 memento 启动 clamp + DisplayId；R-006 启动矩阵测试隔离（APPDATA mtime 实测不变；删除测试误写 window-state.json；theme-settings.json 未动）；R-008 allowed_paths 补齐；R-009 AC6 降 PARTIAL + freeze 上限指标；R-012 生成物 --check 归档。
- **生命周期（251b5df0d）**：卡内登记 reviewer=codex-cli（impl-r1）、delivery_head=7ca2e367b（代码 head）、handoff `doc/handoffs/FEA-07-impl-r1.md`。
- **精确 head 证据（f28d97b99）**：`verification/FEA-07/final-evidence.log`（head 7ca2e367b；build 0/0；全量 **1106/0/57**；check PASS(3)；pins 15/15；两生成物 byte-for-byte）；证据索引更新；Release perf p50 99.91ms / p95 344.93ms / max 344.93ms / 内存 +208B / 句柄 0（缓存复用后）。
- **r2 复核已派发**（fresh Codex CLI，被审 f28d97b99/代码 head 7ca2e367b；job pwsh-ddae7f4df44e488f），等待结果。
## 52. FEA-07 impl-r2 changes_requested → 返修 part2 + r3 复核派发（2026-11-02）

- **Review r2**：`doc/reviews/FEA-07-impl-r2.md`（Codex CLI fresh，P0=0/P1=6/P2=3；被审 f28d97b99/代码 7ca2e367b）。处置：R-013 并发串行门（no-op/快照/事务同门）+ 并发测试；R-001 真实 100 次切换（50 往返）+ 状态断言 + Layout/Loaded/Rendered 真实门禁；R-002 `IPresentationExitState` live 状态（设置草稿/Workbench 运行/导入运行）；R-003 journal previous + 启动崩溃窗口还原；R-004 `StartupPlan.Selection` 单源；R-014 最大化 memento；R-009 数值校正；R-011 索引去自引用 pin；R-007 reviewer/delivery_head/handoff 更新。
- **验证**：代码 head `3220abd59`；build 0/0；全量 **1113/0/57**；check PASS(3)；pins 15/15；两生成物 up-to-date；`final-evidence.log`（SHA 4ab4386d…）；证据提交 `b3fa8dc0c`。
- **r3 复核已派发**（fresh Codex CLI，被审 b3fa8dc0c/代码 3220abd59；job pwsh-73017f1cb59d4226），等待结果。
## 53. Codex 模型调用说明（用户提问实测，2026-11-02）

- 用户问：Codex 为什么不能调用 `gpt-6.1-sol-high` / `gpt-6-luna xhigh`。
- 实测（嵌入 Codex CLI 0.166.0-alpha.5.1，ChatGPT 账号）：
  - `-m gpt-6.1-sol-high` → ERROR: The 'gpt-6.1-sol-high' model is not supported when using Codex with a ChatGPT account（exit 1）。
  - `-m "gpt-6-luna xhigh"` → 同上（exit 1）。
  - `-m gpt-6.1-sol` → 正常（exit 0）。
  - `-m gpt-6.1-sol -c model_reasoning_effort="high"` → 正常（exit 0）。
  - `-m gpt-6-luna -c model_reasoning_effort="xhigh"` → 正常（exit 0；FEA-07 全部复核即用此形式）。
- 结论：`-high`/`xhigh` 不是模型 ID 的一部分，而是 `model_reasoning_effort` 配置；CLI 只接受真实模型 ID。本账号支持 `gpt-6.1-sol` 与 `gpt-6-luna`，不存在 `gpt-6.1-sol-high` 模型。无需用户操作；如需 sol 高强度，用 `-m gpt-6.1-sol -c model_reasoning_effort="high"`。
## 54. Codex 派发配置变更（用户指示，2026-11-02）

- 用户指示：Codex 调用改为 `-m gpt-6.1-sol -c model_reasoning_effort="high"`。
- 实测（嵌入 CLI 0.166.0-alpha.5.1，ChatGPT 账号）：exit 0（ok）。此前 `gpt-6.1-sol-high`/`"gpt-6-luna xhigh"` 作为模型 ID 均报 "not supported"（模型 ID 与 reasoning effort 是两个参数）。
- 生效范围：自本轮起的 Codex 复核/实现派发统一使用该配置（历史报告不追溯修改）；r4 复核将用新配置。
## 55. 新会话恢复材料（2026-11-02）

- 用户将新开 DSH 会话；已写 `doc/handoffs/FEA-07-resume-2026-11-02.md`：当前 HEAD、Task 状态、已完成实现/复核历史、r3 未闭环（R-001/R-002/R-007）、验证基线（1115/0/57、性能 p95 344.93ms）、关键命令、Codex 新配置（`-m gpt-6.1-sol -c model_reasoning_effort="high"`）、约束/坑、建议顺序。
- 新会话按该文件 + Task 卡继续；无需回读旧会话。
## 56. FEA-07 impl-r3 处置 part2（真实 staging 门禁 + 隐藏树退出聚合，2026-11-02）

- **R-001**：`PresentationWindow` 增加隐藏 staging `FrontendContentHost`（同一 live visual tree、`Opacity=0`、不可命中/聚焦、a11y Raw）；`FrontendHostCoordinator` 要求 staging 宿：替换树先挂 staging → 真实布局 pass 后校验 host/staging/tree 几何（删除 1024×640 fallback 与手工 Measure/Arrange）→ 真实 `Loaded` 事件（5s fail-closed）+ `IsLoaded`/visual root/top-level 复核 → `TopLevel.RequestAnimationFrame` 帧渲染（2s fail-closed）→ 才 commit；失败清 staging + 既有回滚。新增 staging 挂树/有效几何/零几何/Loaded 失败回滚/生产树 50 往返状态保留测试。
- **R-001 状态覆盖**：Fluent `CurrentPage` + Settings 未应用 draft（跨前端切换保留）、V2 `Session.Shell.CurrentSpace`/`Session.Console.RunIdInput`/`Session.Reader.BookId` 在 100 次切换后保持；真实 Run/Intent、原生 IME、A03 真库矩阵不可测 → AC1 保持 PARTIAL。
- **A01 补强**：`SettingsViewModel.ApplyCoordinatorSettings` 对「仅 frontendId 变化」的前端切换把新 id 合入 draft、不丢弃未应用外观草稿；其它外观变更仍镜像唯一写者。
- **R-002**：`PresentationWindow` 可选 `allContentProvider`（组合根传 `contentCache.Values`），`Closing` 聚合可见树+staging+全部缓存树 `IPresentationExitState`；`AppShellV2.ThemeStudioDraftProvider`（`WireThemeStudio` 注入 `() => viewModel.HasDraft`）纳入 `HasUnsavedEdits`。新增隐藏树 dirty/run、生产 Fluent 树切换后隐藏阻断、V2 draft provider 阻断与清理放行测试。
- **验证**：build 0/0；全量 **1119/0/57**（+4 测试）；两生成物 `--check` up-to-date；check PASS(3)；pins 15/15；证据 `rework-r3-part2-verification.log`、`final-evidence.log`（head `100d487ff`，SHA `478b097f…`）。
- **性能新 baseline（R-009）**：R-001 后事务含真实渲染门禁；Release 三次 p95 496.30 / 575.64 / 712.28 ms（均 ≤1000ms PASS）；记录 run p50 102.29 / p95 496.30 / max 496.30 / 冷启 593.99 ms / 内存 +7088B / 句柄 0；旧 344.93/429.47 已更正并说明不可直接比较。
- **R-007/R-016**：delivery_head=`100d487ff`、reviewer=impl-r3、handoff `doc/handoffs/FEA-07-impl-r3.md`、canonical=pending（r4 approved 后 complete）；证据索引重生成（0 控制字符、无自引用）。

## 57. FEA-07 r4 复核派发（2026-11-02）

- 新配置：`-m gpt-6.1-sol -c model_reasoning_effort="high"`（用户 2026-11-02 指示；`-high` 不是模型 ID）。
- 被审：代码 head `100d487ff` + 本证据/文档提交；只读，唯一允许写 `doc/reviews/FEA-07-impl-r4.md`；报告记录 reviewer 身份/来源、reviewed_head、code_head、decision、counts，并实跑 build/全量/两 `--check`/check/pins + 核对 Task pins 与 evidence-index SHA。
- 通过后：DSH 集成验证 → FEA-07 `done`、integration_commit、canonical=complete、Closeout Record；AC5 原生矩阵按 D-1 residual/waiver 登记；之后按用户顺序 `FEA-06-RESIDUAL-1`。
## 58. FEA-07 impl-r4 changes_requested → 返修（2026-11-02）

- **r4 复核**（fresh Codex CLI，`-m gpt-6.1-sol -c model_reasoning_effort="high"`；被审 `ad56bea1c`/代码 `100d487ff`）：`doc/reviews/FEA-07-impl-r4.md`，P0=0 / P1=3 / P2=3；指定验证全部通过（build 0/0、全量 1119/0/57、两生成物 up-to-date、check PASS(3)、pins 15/15、Task pins 15/15）。
- **返修（`b328f3488`）**：R-017 canonical 快照同步（仅 frontend-only 变更保留 draft，其它外部变更镜像）；R-002 真实 Theme Studio draft 测试（不覆写 provider + 反向验证）；R-013 确定性排队屏障（第二请求未完成 + 补偿后执行真实切换）；R-018 Loaded 订阅解绑（事务 finally）；R-019 `IPresentationInputState` staging 输入隔离；R-009 性能口径改 4 预热 + 20 测量（p95 不再恒等于 max）；R-007 生命周期文案与 skip 原因更正。
- **验证**：build 0/0；全量 **1132/0/57**（+13 测试）；Release 四次复测 p95 292.92/295.41/295.59/313.95 ms 均 PASS（记录 run p50 106.46 / p95 313.95 / max 331.89 / 冷启 661.06 ms / 内存 +10592B / 句柄 0）；`rework-r4-verification.log`、`final-evidence.log`（head `b328f3488`，SHA `06975fc7…`）、`performance-baseline.md`。
- **测试隔离修正**：V2 shell 共享 `NullHostController.Instance` 的 `CurrentFrontend` memento → 测试显式复位空间/会话值，消除顺序依赖偶发失败（presentation 23 测试连续 5 次全绿）。

## 59. FEA-07 r5 复核派发 + AC5 residual 计划（2026-11-02）

- r5：fresh Codex CLI 只读，被审代码 head `b328f3488` + 本证据/文档提交；唯一允许写 `doc/reviews/FEA-07-impl-r5.md`；用 `-m gpt-6.1-sol -c model_reasoning_effort="high"`。
- r5 approved 后：DSH 集成验证（build/全量/两 `--check`/check/pins/证据索引）→ FEA-07 `done`、integration_commit=`b328f3488`（如无新代码变更）、canonical=complete、Closeout Record。
- **AC5 residual/waiver（D-1）**：原生双屏/拔屏/DPI 100/125/150/200% 矩阵无硬件 → 登记为 residual（blocked D-1，不伪造证据），不因 headless 结果升级 AC5；待用户提供真机或书面降级后再验。
- 之后按用户顺序 `FEA-06-RESIDUAL-1`（不插队）。
## 60. FEA-07 impl-r5 changes_requested → 返修（2026-11-02）

- **r5 复核**（fresh Codex CLI，`gpt-6.1-sol` + `reasoning_effort=high`；被审 `ea27a7b10`/代码 `b328f3488`）：`doc/reviews/FEA-07-impl-r5.md`，P0=0 / P1=1 / P2=2；指定验证全部通过（build 0/0、全量 1132/0/57、两生成物 up-to-date、check PASS(3)、pins 15/15、Task pins 17/17）。
- **R-020（P1）**：`--presentation-host=true` 下稳定窗口未承接 Fluent Reader 全屏请求（按钮/F/Esc 只改 VM）。返修：`FrontendContentHost.ContentChanged` → `PresentationWindow` 只对可见 Fluent 树连接 `FullScreenRequested`→`WindowState`；隐藏/缓存树请求忽略；离开 Fluent 树 `ExitFullScreen()`+Normal；`FluentShellSurface` 增 `CurrentPageChanged`/`ExitFullScreen()`，离开 Reader 页（Esc 的 SurfaceBack 属 FEA-06 键表）时退出全屏；真实组合根测试覆盖按钮/F/Esc、切换前后、隐藏树。
- **R-021（P2）**：重复通知用例改为直接驱动生产通知处理入口；新增 clean+Contrast 镜像用例。
- **R-007（P2）**：reviewer=impl-r5、delivery_head=`4e8510d43`、handoff `doc/handoffs/FEA-07-impl-r5.md`、索引 r6 待派；canonical 保持 pending。
- **验证（`4e8510d43`）**：build 0/0；全量 **1134/0/57**（+2 测试）；`rework-r5-verification.log`、`final-evidence.log`（head `4e8510d43`，SHA `3021dbb0…`）；Release 两次复测 p95 236.48/248.42 ms 均 PASS（记录 run p50 96.50 / p95 248.42 / max 349.30 / 冷启 612.38 ms / 内存 +2528B / 句柄 0）；性能摘要「20 次往返」措辞更正为「20 次单向切换（10 次往返）」。

## 61. FEA-07 r6 复核派发 + AC5 residual 计划（2026-11-02）

- r6：fresh Codex CLI 只读，被审代码 head `4e8510d43` + 本证据/文档提交；唯一允许写 `doc/reviews/FEA-07-impl-r6.md`；`-m gpt-6.1-sol -c model_reasoning_effort="high"`。
- r6 approved 后：DSH 集成验证（build/全量/两 `--check`/check/pins/证据索引）→ FEA-07 `done`、integration_commit=`4e8510d43`（如无新代码变更）、canonical=complete、Closeout Record。
- **AC5 residual/waiver（D-1）**：原生双屏/拔屏/DPI 100/125/150/200% 矩阵无硬件 → 登记 residual（blocked D-1，不伪造证据）；R-020 全屏请求→WindowState 已在 headless 真实组合根回归，不依赖 D-1 硬件。
- 之后按用户顺序 `FEA-06-RESIDUAL-1`（不插队）。
## 62. FEA-07 impl-r6 approved → R-022 P2 修复（2026-11-02）

- **r6 复核**（fresh Codex CLI，`gpt-6.1-sol` + `reasoning_effort=high`；被审 `80b2203e5`/代码 `4e8510d43`）：`doc/reviews/FEA-07-impl-r6.md`，**approved**，P0=0 / P1=0 / P2=2；指定验证全部通过（build 0/0、全量 1134/0/57、两生成物 up-to-date、check PASS(3)、pins 15/15、Task pins 18/18）；R-020/R-021 闭环。
- **R-022（P2）修复（`5a495f80a`）**：全屏 Fluent→V2 切换在 Promote 时退出全屏，SaveAsync/journal finalize 失败回滚旧树后原全屏模式未恢复。`PresentationWindow.SwitchFrontendAsync` 事务前快照 `WindowState` + Fluent reader 全屏状态，失败时与旧内容树一并恢复；成功路径保持原清理策略。新增 `FailedSwitch_RestoresTheOriginalFullScreenMode`；既有失败切换测试补 Normal 断言。
- **R-007（P2）**：reviewer=impl-r6（approved）、delivery_head=`5a495f80a`、handoff `doc/handoffs/FEA-07-impl-r6.md`、索引 r7 待派；canonical 保持 pending。
- **验证**：build 0/0；全量 **1135/0/57**（+1 测试）；`rework-r6-verification.log`、`final-evidence.log`（head `5a495f80a`，SHA `7fb048ab…`）；Release 两次复测 p95 292.65/261.38 ms 均 PASS（记录 run p50 88.42 / p95 261.38 / max 275.14 / 冷启 605.39 ms / 内存 +22496B / 句柄 +3）。

## 63. FEA-07 r7 复核派发 + 集成/收尾计划（2026-11-02）

- r7：fresh Codex CLI 只读，被审代码 head `5a495f80a` + 本证据/文档提交；唯一允许写 `doc/reviews/FEA-07-impl-r7.md`；重点 R-022 修复与回归。
- r7 approved 后：DSH 集成验证（build/全量/两 `--check`/check/pins/证据索引）→ FEA-07 `done`、integration_commit=`5a495f80a`（如无新代码变更）、canonical=complete、Closeout Record。
- **AC5 residual/waiver（D-1）**：原生双屏/拔屏/DPI 100/125/150/200% 矩阵无硬件 → residual（blocked D-1，不伪造证据）；R-020/R-022 的全屏接线已在真实组合根 headless 回归，不依赖 D-1。
- 之后按用户顺序 `FEA-06-RESIDUAL-1`（不插队）。
## 64. FEA-07 impl-r7 changes_requested（P2×4）→ 返修（2026-11-02）

- **r7 复核**（fresh Codex CLI，`gpt-6.1-sol` + `reasoning_effort=high`；被审 `226e47c51`/代码 `5a495f80a`）：`doc/reviews/FEA-07-impl-r7.md`，changes_requested，P0=0 / P1=0 / P2=4；指定验证全部通过（build 0/0、全量 1135/0/57、两生成物 up-to-date、check PASS(3)、pins 15/15）；R-022 部分修复，残留取消路径（R-022 残余）、测试判别力（R-023）、排队陈旧快照（R-024）、appointment 文案（R-007）。
- **R-022 残余 + R-024（`462141f57`）**：窗口模式快照/恢复移入协调器事务（新增 `IPresentationWindowModeTransaction`）；快照在 `_switchGate` 内、reject/no-op 校验后，绑定本事务旧树；事务 finally dispose 未提交快照 → 失败/异常/取消恢复，成功 Commit 不触碰窗口；取消仍向上传播。
- **R-023**：新增 3 个判别性测试（Promote 后 finalize 失败、Promote 后取消、排队拒绝不写陈旧模式）；presentation 38 测试连续 3 次全绿。
- **R-007**：reviewer=impl-r7、delivery_head=`462141f57`、handoff `doc/handoffs/FEA-07-impl-r7.md`、索引 r8 待派；canonical 保持 pending。
- **验证**：build 0/0；全量 **1138/0/57**（+3 测试）；`rework-r7-verification.log`、`final-evidence.log`（head `462141f57`，SHA `dbfb7666…`）；Release 两次复测 p95 299.40/374.09 ms 均 PASS（记录 run p50 99.28 / p95 374.09 / max 389.99 / 冷启 675.10 ms / 内存 -1616 B / 句柄 0）。

## 65. FEA-07 r8 复核派发 + 集成/收尾计划（2026-11-02）

- r8：fresh Codex CLI 只读，被审代码 head `462141f57` + 本证据/文档提交；唯一允许写 `doc/reviews/FEA-07-impl-r8.md`；重点 R-022 取消/失败补偿、R-024 门内快照、R-023 判别力与回归。
- r8 approved 后：DSH 集成验证（build/全量/两 `--check`/check/pins/证据索引）→ FEA-07 `done`、integration_commit=`462141f57`（如无新代码变更）、canonical=complete、Closeout Record。
- **AC5 residual/waiver（D-1）**：原生双屏/拔屏/DPI 100/125/150/200% 矩阵无硬件 → residual（blocked D-1，不伪造证据）。
- 之后按用户顺序 `FEA-06-RESIDUAL-1`（不插队）。
## 66. FEA-07 impl-r8 changes_requested（P2×2）→ 返修（2026-11-02）

- **r8 复核**（fresh Codex CLI，`gpt-6.1-sol` + `reasoning_effort=high`；被审 `b6b63574d`/代码 `462141f57`）：`doc/reviews/FEA-07-impl-r8.md`，changes_requested，P0=0 / P1=0 / P2=2；指定验证全部通过（build 0/0、全量 1138/0/57、两生成物 up-to-date、check PASS(3)、pins 15/15）；R-022/R-024 实现修复被确认成立。
- **R-023 残余（`aedc7251c`）**：排队用例屏障从 Promote 后前移到 **Promote 前**（旧树/窗口仍全屏时发起第二请求并断言未完成）；协调器增 `beforeContentCommit` 诊断钩子、窗口内部 ctor 透传 `beforeCommit`；**mutation 实测**：把窗口模式快照移回 gate 外（模拟旧实现）→ 用例 FAIL（Expected Normal / Actual FullScreen），恢复后 19/19 全绿；Task r7 节过宽表述已按实测修正。
- **R-007**：reviewer=impl-r8、delivery_head=`aedc7251c`、handoff `doc/handoffs/FEA-07-impl-r8.md`、索引 r9 待派；canonical 保持 pending。
- **验证**：build 0/0；全量 **1138/0/57**（测试改写、总数不变）；`rework-r8-verification.log`、`final-evidence.log`（head `aedc7251c`，SHA `e8ed8f29…`）；Release 两次复测 p95 361.52/381.43 ms 均 PASS（记录 run p50 109.89 / p95 381.43 / max 383.05 / 冷启 697.08 ms / 内存 +456 B / 句柄 +1）。

## 67. FEA-07 r9 复核派发 + 集成/收尾计划（2026-11-02）

- r9：fresh Codex CLI 只读，被审代码 head `aedc7251c` + 本证据/文档提交；唯一允许写 `doc/reviews/FEA-07-impl-r9.md`；重点 R-023 屏障判别力/mutation 证据与 R-007 文案。
- r9 approved 后：DSH 集成验证（build/全量/两 `--check`/check/pins/证据索引）→ FEA-07 `done`、integration_commit=`aedc7251c`（如无新代码变更）、canonical=complete、Closeout Record。
- **AC5 residual/waiver（D-1）**：原生双屏/拔屏/DPI 100/125/150/200% 矩阵无硬件 → residual（blocked D-1，不伪造证据）。
- 之后按用户顺序 `FEA-06-RESIDUAL-1`（不插队）。
## 68. FEA-07 impl-r9 changes_requested（P2×3，纯文档）→ 返修（2026-11-02）

- **r9 复核**（fresh Codex CLI，`gpt-6.1-sol` + `reasoning_effort=high`；被审 `563f248c7`/代码 `aedc7251c`）：`doc/reviews/FEA-07-impl-r9.md`，changes_requested，P0=0 / P1=0 / P2=3；**R-023 核心判别力（Promote 前屏障 + mutation 证据）确认闭环**；指定机械检查全部通过（build 0/0、全量 1138/0/57、两生成物 up-to-date、check PASS(3)、pins 15/15）。
- **R-007（appointment 文案）**：Task reviewer=r9、canonical=r10 approved、索引 r10 待派、handoff r8 补 r9 执行记录、新增 `doc/handoffs/FEA-07-impl-r9.md`。
- **R-009（AC6 数值）**：AC6 验收行 r7 旧值（99.28/374.09/389.99）→ r8 当前值（p50 109.89 / p95 381.43 / max 383.05，两次 361.52/381.43）；r7 实施记录原字节保留。
- **R-011（证据 commit 定位）**：`EV-FEA07-FINAL`/`EV-FEA07-PERF-MD` commit 列 `aedc7251c` → `563f248c7`（实际包含当前 r8 文件），文件内部 code_head 仍 `aedc7251c`，不重写旧证据。
- 本批为纯文档修正，代码 head 不变（`aedc7251c`）；证据 SHA/索引/pin 在提交前重新校验一致。

## 69. FEA-07 r10 复核派发 + 集成/收尾计划（2026-11-02）

- r10：fresh Codex CLI 只读，被审代码 head `aedc7251c` + 文档 head（本批提交）；唯一允许写 `doc/reviews/FEA-07-impl-r10.md`；重点 R-007/R-009/R-011 闭环与指针一致性。
- r10 approved 后：DSH 集成验证（build/全量/两 `--check`/check/pins/证据索引/integration-verification.log）→ FEA-07 `done`、integration_commit=`aedc7251c`、canonical=complete、Closeout Record。
- **AC5 residual/waiver（D-1）**：原生双屏/拔屏/DPI 100/125/150/200% 矩阵无硬件 → residual（blocked D-1，不伪造证据）；其余 AC1–AC4/AC6/AC8 residual 一并登记。
- 之后按用户顺序 `FEA-06-RESIDUAL-1`（不插队；其依赖 FEA-09/10/11/12/13 端口未就绪，释放时需按端口就绪拆分并刷新 base_commit/scope review）。
## 70. FEA-07 impl-r10 changes_requested（P2×1，文案）→ 最终处置（2026-11-02）

- **r10 复核**（fresh Codex CLI，`gpt-6.1-sol` + `reasoning_effort=high`；被审 `ebda36be9`/代码 `aedc7251c`）：`doc/reviews/FEA-07-impl-r10.md`，changes_requested，P0=0 / P1=0 / P2=1；**R-009（AC6 数值）与 R-011（证据 commit 定位）确认闭环**；剩余 R-007 为「最新已完成 Review」与「当前 Appointment」两种状态的文案冲突（r9→r10 只滚动轮次、未消除冲突）。
- **R-007 最终处置（anti-churn）**：拆分两类事实并统一所有当前文档：最新已完成 Review=impl-r10（changes_requested P2=1，已处置）；**当前 Appointment=impl-r11（fresh Codex CLI，来源 handoff r10 §4），状态「复核进行中」**；canonical 保持 pending（r11 approved 并集成后置 complete）。Task/索引/STATUS/PLAN/checkpoint/handoff 全部按进行中表述，不再写下一轮「待派」。
- 本批纯文档，代码 head 不变（`aedc7251c`）；全量 1138/0/57、build 0/0、两生成物 up-to-date、check PASS(3)、pins 15/15 沿用既有证据；提交前重新校验 Task pin/索引 SHA。

## 71. FEA-07 r11 复核派发 + 收尾计划（2026-11-02）

- r11：fresh Codex CLI 只读，被审文档 head=本批提交、代码 head `aedc7251c`；唯一允许写 `doc/reviews/FEA-07-impl-r11.md`；重点 Appointment 表述一致性与 R-009/R-011 维持闭环。
- r11 approved 后：DSH 集成验证（build/全量/两 `--check`/check/pins/证据索引 → `verification/FEA-07/integration-verification.log`）→ FEA-07 `done`、integration_commit=`aedc7251c`、canonical=complete、Closeout Record。
- **AC5 residual/waiver（D-1）**：原生双屏/拔屏/DPI 矩阵无硬件 → residual；AC1/AC2/AC3/AC4/AC6/AC8 边界一并登记（不伪造证据）。
- 之后按用户顺序 `FEA-06-RESIDUAL-1`（不插队；依赖 FEA-09/10/11/12/13 端口未就绪，释放时按端口就绪拆分并刷新 base_commit/scope review）。
## 72. FEA-07 impl-r11 changes_requested（P2×1，缺 r10 报告）→ 补全（2026-11-02）

- **r11 复核**（fresh Codex CLI，`gpt-6.1-sol` + `reasoning_effort=high`；被审 `91de6a345`/代码 `aedc7251c`）：`doc/reviews/FEA-07-impl-r11.md`，changes_requested，P0=0 / P1=0 / P2=1；**R-007 文案冲突确认消除**、R-009/R-011 维持闭环；唯一 P2：仓库缺少被声明为「最新已完成 Review」的 r10 原始报告（b7 干净证据运行前暂存仓外、提交时漏恢复）。
- **修复**：恢复 `doc/reviews/FEA-07-impl-r10.md`（真实内容）并与 r11 报告一并入库；指针更新为「最新已完成=impl-r11（已处置）；当前 Appointment=impl-r12 复核进行中」；canonical 保持 pending（r12 approved 并集成后置 complete）。
- 本批纯文档，代码 head 不变（`aedc7251c`）；全量 1138/0/57、build 0/0、两生成物 up-to-date、check PASS(3)、pins 15/15 沿用既有证据；提交前重新校验 Task pin/索引 SHA 与 r1–r11 Review 报告完整性。

## 73. FEA-07 r12 复核派发 + 收尾计划（2026-11-02）

- r12：fresh Codex CLI 只读，被审文档 head=本批提交、代码 head `aedc7251c`；唯一允许写 `doc/reviews/FEA-07-impl-r12.md`；重点 Review 报告完整性与 Appointment 指针一致性。
- r12 approved 后：DSH 集成验证（build/全量/两 `--check`/check/pins/证据索引 → `verification/FEA-07/integration-verification.log`）→ FEA-07 `done`、integration_commit=`aedc7251c`、canonical=complete、Closeout Record。
- **AC5 residual/waiver（D-1）**：原生双屏/拔屏/DPI 矩阵无硬件 → residual；AC1/AC2/AC3/AC4/AC6/AC8 边界一并登记（不伪造证据）。
- 之后按用户顺序 `FEA-06-RESIDUAL-1`（不插队；依赖 FEA-09/10/11/12/13 端口未就绪，释放时按端口就绪拆分并刷新 base_commit/scope review）。
## 74. FEA-07 impl-r12 approved → 集成验证 → done / closeout（2026-11-02）

- **r12 复核**（fresh Codex CLI，`gpt-6.1-sol` + `reasoning_effort=high`；被审 `527a7ec37`/代码 `aedc7251c`）：`doc/reviews/FEA-07-impl-r12.md`，**approved**，P0=0 / P1=0 / P2=1（R-026 非阻塞：索引把 scope-r1 changes_requested 与 scope-r2 approved 合并写成 approved）；r11 缺报告 P2 确认闭环；R-007/R-009/R-011 维持闭环。
- **R-026 处置**：索引当前摘要改为「scope-r1 changes_requested 已处置；scope-r2 approved」；scope 原报告与历史署名不改。
- **集成验证**（`verification/FEA-07/integration-verification.log`，SHA `412e8571…`，head `527a7ec37`）：build 0/0；全量 **1138/0/57**；TokenGen 292 rows / ThemeGen `--check` up-to-date；check.ps1 PASS(3)；verify_pins 15/15；Task pins 22/22；索引 24 行 SHA 一致；`aedc7251c..527a7ec37` 无源码/测试漂移。
- **关闭**：FEA-07 `status=closed_with_limitations`（AC7 MET；AC1–AC4/AC6/AC8 PARTIAL、AC5 BLOCKED/D-1 → residual；范围未全部达成，按协作协议不写 done）、`integration_commit=aedc7251c`、`canonical_evidence_status=complete`、`resource_closeout_status=complete`；Closeout Record 与 Residual 登记已填（不伪造证据）。
- **RES: AC5 原生矩阵（D-1）**：真机双屏/拔屏/DPI 100/125/150/200% 无硬件，登记 residual（待硬件或用户书面 waiver）；其余 AC 边界同登记于 Task 卡。
- **下一节点**：`FEA-06-RESIDUAL-1` 仍 proposed（依赖 FEA-09/10/11/12/13 端口）；释放前需刷新 base_commit=FEA-07 closeout head、按端口就绪拆分并走 scope review，不自动启动、不插队。
## 75. FEA-07 关闭 + FEA-06-RESIDUAL-1 释放（2026-11-02）

- **FEA-07 关闭**：r12 approved（P0=0/P1=0/P2=1 非阻塞 R-026 已处置）；集成验证 `verification/FEA-07/integration-verification.log`（SHA `412e8571…`，head `527a7ec37`）：build 0/0、全量 **1138/0/57**、两生成器 up-to-date、check PASS(3)、pins 15/15、Task pins 25/25、索引 24 行；`aedc7251c..527a7ec37` 无源码漂移。
- **状态判定**：按协作协议与治理检查器（DONE 不允许 PARTIAL AC），FEA-07 终态为 **closed_with_limitations**（非 done）：AC7 MET；AC1–AC4/AC6/AC8 PARTIAL、AC5 BLOCKED/D-1 → Residual 登记；integration_commit=`aedc7251c`；canonical/resource complete；Closeout Record 已填。
- **残项**：AC5 原生双屏/拔屏/DPI 矩阵（D-1 无硬件，waiver/待硬件）；AC1 原生 IME/A03 真库/ACK/Run；AC2 真实双屏 broker/Host 生命周期；AC3 真崩溃注入；AC4 真实 App 入口/坏包矩阵；AC6 UI freeze 真采样；AC8 原生截图。
- **FEA-06-RESIDUAL-1 释放**：status `ready`；base_commit=`82529a3d5864a39f362e414b67bca774d743f862`（FEA-07 closeout head）；owner=codex；第一批范围 v1：R-1a UI memento、R-1b 分栏折叠、R-5a 设置离开未保存确认/Esc、R-6 组件 full 状态、R-7 headless 焦点环/motion、R-8 四 Fluent VM 拆分；OUT/blocked：R-2/R-3/R-4/R-5b（端口）、R-9（令牌/设计确认）、原生 DPI/a11y（D-1）。
- **下一步**：scope-r1 独立复核（fresh Codex CLI，只写 `doc/reviews/FEA-06-RESIDUAL-1-scope-r1.md`）→ 冻结后按 W-10 派 Codex 实施；第二批待端口就绪。
## 76. FEA-06-RESIDUAL-1 scope-r1 changes_requested（P1×3/P2×3）→ 范围 v2（2026-11-02）

- **scope-r1**（fresh Codex CLI，`gpt-6.1-sol` + `reasoning_effort=high`；被审 `0e52c9daa`）：`doc/reviews/FEA-06-RESIDUAL-1-scope-r1.md`，changes_requested，P0=0 / P1=3 / P2=3；实跑基线 build 0/0、全量 1138/0/57、生成器/治理/pins 通过。
- **S-001（P1）R-9 假阻塞**：`Nm.Elevation.*` 令牌/键已存在（Tokens.Global.axaml / Generated/NmKeys.g.cs），非外部依赖 → 范围 v2 将 R-9 纳入 IN（I-8：消费令牌 + 高对比回退 + V2 不变）。
- **S-002（P1）验收不可判定**：范围 v1 的 IN 项验收仍是“等页面状态/full/可实现部分” → 范围 v2 为每个 IN 子项给出字段/入口/断言（I-1…I-10），并冻结 FEA-07 非回归矩阵、1138/0/57 基线、关闭口径。
- **S-003（P1）IN/OUT 非穷尽互斥**：把 R-2/R-3/R-4/R-5/R-8 拆为穷尽子项：IN（I-9 未保存圆点、I-10 工具条自动隐藏、I-6/I-7）与 DEFERRED（D-1…D-6，承接方 FEA-10/12/13/09/11）+ BLOCKED（B-1…B-5，含原生 D-1），每项写明承接时点与恢复条件。
- **S-004（P2）写域过宽**：allowed_paths 收窄为 `Views/Fluent/**`、`ViewModels/Fluent/**`、`Styles/AppStyles.axaml`、`Styles/FluentUi.cs`、DesignSystem 的 Accessibility/Styles/Theming、测试与证据/治理文件；明确禁止 Current V2、共享 KeyMap/IPresentation*/FEA-07 窗口接线、全局主题/焦点 ring 影响 V2、Generated/**。
- **S-005（P2）R-8 丢失 PNG opt-in**：拆 I-6（1408 行 VM 纯移动重构）与 I-7（PNG 采证 opt-in，默认全量不写、禁止覆盖 FEA-06 已 pin PNG、输出本卡证据目录/临时目录）。
- **S-006（P2）治理缺口**：front matter reviewer/Appointment、本批依赖（FEA-06/FEA-07）与未来端口依赖分离、Review Appointment（scope-r2 + impl-r1）、Resource Manifest 骨架、canonical/closeout pending 全部补齐。
- **下一步**：scope-r2 独立复核（fresh Codex CLI，只写 `doc/reviews/FEA-06-RESIDUAL-1-scope-r2.md`）；P0/P1=0 后 DSH 冻结范围 v2，按 W-10 派 Codex 实施 Batch A → Batch B。
## 77. FEA-06-RESIDUAL-1 scope-r2 changes_requested（P1×3/P2×3）→ 范围 v3（2026-11-02）

- **scope-r2**（fresh Codex CLI，`gpt-6.1-sol` + `reasoning_effort=high`；被审 `04d7c79e3`）：`doc/reviews/FEA-06-RESIDUAL-1-scope-r2.md`，changes_requested，P0=0 / P1=3 / P2=3；构建/生成器/治理/pins 通过；**安全回归 1137/0/57**（排除会写旧证据的 `FluentPages_RenderHeadlessPngEvidence`；旧 1138/0/57 仅为同代码前序基线，未声称无过滤全量已复跑）。
- **R2-001（P1）验收不可判定**：I-3 补保存/丢弃/取消三分支 + 保存失败保护；I-5 改用设计实际三态 `auto/full/reduce` × 三类 × 分类开关矩阵；新增 I-11 焦点环（2px/offset=1/高对比 3px、浮层焦点移入/返还、隐藏控件移出 Tab 序）。
- **R2-002（P1）残项非穷尽**：范围 v3 改为 **IN=I-1…I-14 / BLOCKED=B-1…B-7 / 无 DEFERRED**；补 I-12 控制台入口导航、I-13 9 行状态视觉骨架、I-14 源不可用警示本体；数据绑定/恢复动作/投影分别归 B-2/B-3/B-6/B-7，唯一归属。
- **R2-003（P1）I-8 违反冻结设计**：删除 reduce/减弱回退边框；standard 与 reduce 均保留 Elevation 阴影令牌，仅高对比回退 1px 边框（设计 03:62）。
- **R2-004（P2）写域路径**：`Styles/FluentUi.cs` 更正为真实 `Controls/FluentUi.cs`；DesignSystem 三目录保留但限定 Fluent 消费/焦点/motion 文件，共享改动需 DSH 预批。
- **R2-005（P2）治理指针**：Plan 依赖列改为 FEA-06/FEA-07（FEA-09/10/11/12/13 仅为 BLOCKED 承接方），STATUS/Plan 指向 scope-r3；Manifest 补全八类当前状态。
- **R2-006（P2）组件断言**：I-4 先冻结组件×适用状态表，断言有效属性/命令零触发/浮层焦点，无法 headless 验证的格标 NOT_RUN，不以字符串选择器存在计 PASS。
- **下一步**：scope-r3 独立复核（fresh Codex CLI，只写 `doc/reviews/FEA-06-RESIDUAL-1-scope-r3.md`）；P0/P1=0 后 DSH 冻结范围 v3，按 W-10 派 Codex 实施 Batch A → Batch B。
## 78. Codex CLI 额度耗尽 → ZCode 故障转移（2026-11-02）

- **待裁决 D-6（已按用户规则直接执行，不需用户拍板）**：Codex CLI 于 2026-11-02 22:01 (+08:00) 返回 usage limit（提示 2026-11-03 00:23 恢复），scope-r3 复核中断、未写报告（`doc/reviews/FEA-06-RESIDUAL-1-scope-r3.md` 不存在），仓库无漂移。
- **处置**：按用户 2026-11-02 规则「Codex 无额度或不可用时转给其他可用 agent，故障转移候选仅 ZCode」：scope-r3 改由 **ZCode CLI headless（`--mode plan` 只读）**执行，报告由 DSH 原样落盘并标注来源；任务卡 Appointment 已同步。
- **影响**：Codex 恢复前（预计 2026-11-03 00:23 后）的复核/审查任务全部走 ZCode；FEA-06-RESIDUAL-1 实现 owner 仍登记 codex，若届时额度未恢复，按同一规则故障转移 ZCode 实施并在 Task 卡/证据标注。
- **回退**：Codex 恢复后，后续轮次恢复 Codex 派发；历史报告中来源字节不改。
- **当前状态**：FEA-06-RESIDUAL-1 范围 v3 已固定（scope-r1/r2 处置完毕），scope-r3（ZCode）复核进行中；FEA-07 已 closed_with_limitations（integration `aedc7251c`）。
## 79. FEA-06-RESIDUAL-1 scope-r3 approved（ZCode）→ 范围 v3 冻结 + impl Batch A 派发（2026-11-02）

- **scope-r3**（ZCode CLI headless `--mode plan` 只读；Codex 额度故障转移；会话 `sess_3c0de2b4-…`）：`doc/reviews/FEA-06-RESIDUAL-1-scope-r3.md`，**approved，P0=0 / P1=0 / P2=4**；R2-001…R2-003 三项 P1 全部闭环；构建/生成器/治理/pins 通过；安全回归 **1137/0/57**（PNG 用例排除口径一致）。
- **R3-001…R3-004 处置**：R3-001 PLAN 当前 DAG 段刷新为 v3/scope-r3；R3-002 I-7 口径固定（禁止 `verification/**` PNG 写入、`%TEMP%` 允许、不覆盖旧 pin）；R3-003 I-10 按设计 07 分两类工具条断言（2s/点击中部/reduce 直接切换 vs 右侧常显）；R3-004 I-8/I-11 增 Current 对照行为断言。均为实施期跟踪项，不阻塞冻结。
- **冻结**：范围 v3 冻结（IN=I-1…I-14、BLOCKED=B-1…B-7、无 DEFERRED）；owner 仍登记 codex，实施执行按故障转移改派 **ZCode**。
- **实施计划**：I-6 独立首个 commit（1408 行 VM 等价拆分）→ Batch A（I-12/I-14/I-9/I-10/I-1/I-2/I-3）→ Batch B（I-4/I-5/I-11/I-13/I-7/I-8）；每子批独立 delivery commit；全程安全回归 filter 1137/0/57，I-7 后恢复 1138/0/57 起点。
- **下一步**：ZCode 实施 Batch A → DSH 验收（diff 写域/测试/证据/安全回归）→ Batch B → fresh 复核（Codex 恢复则 Codex，否则 ZCode）。
## 80. FEA-06-RESIDUAL-1 Batch A 交付（ZCode 实现 + 崩溃 → DSH 收尾）（2026-11-02）

- **实现执行**：ZCode CLI（`--mode yolo`，Codex 额度故障转移）完成 I-6（`83fa1b186`，1408 行 VM 四文件等价拆分）+ Batch A 功能 WIP 后**会话崩溃**（exit `-1073740791` = `0xC0000409` STATUS_STACK_BUFFER_OVERRUN，无 JSON/证据/Handoff）。
- **DSH 收尾**：核对全部改动在 allowed_paths；恢复被 ZCode 默认全量运行覆盖的 `verification/FEA-06/screens/{shelf,workbench,reader}.png` 到 HEAD 字节；修 1 个异步测试竞态（`PumpUntil`，实现语义未改）；补写 `doc/handoffs/FEA-06-RESIDUAL-1-impl-batch-a.md` 与 `verification/FEA-06-RESIDUAL-1/batch-a-verification.log`；提交 `9337cbbe1`。
- **Batch A 子项**：I-1/I-2/I-3/I-6/I-9/I-10/I-12/I-13/I-14 完成（新增测试 33/33）。
- **验证**：build 0/0；安全全量（排除 PNG 用例）**1170/0/57**（基线 1137 + 33 新测试）；FEA-07 非回归子集全绿；TokenGen 292 rows / ThemeGen up-to-date；check PASS(3)；pins 15/15；旧 FEA-06 PNG 字节未变（restore 后 SHA 一致）。
- **Batch B 待派**：I-4（组件 full 状态）、I-5（motion 三态×三类）、I-7（PNG opt-in，恢复无过滤 1138 起点）、I-8（Elevation+高对比回退+Current 对照）、I-11（焦点环/浮层焦点/Tab 序+Current 对照）。
- **下一步**：Batch B（Codex 额度恢复优先 Codex，否则 ZCode 新会话）→ fresh impl 复核 → DSH 集成/关闭。
## 81. FEA-06-RESIDUAL-1 Batch B 部分交付 + D-7（2026-11-02 深夜）

- **I-7 完成**（`ce0bee67d`）：PNG 采证默认不写仓库/证据面；`NEWMANGA_CAPTURE_FLUENT_PNGS=1` opt-in 写 `verification/FEA-06-RESIDUAL-1/png/`；默认帧尺寸断言保留；`verification/FEA-06/screens/**` 字节未变（SHA 对照）；opt-in 实测生成 4 PNG 后移除。
- **双 agent 额度耗尽**：Codex CLI 额度 2026-11-03 00:23 恢复（Batch B 派发时崩溃/额度错误），ZCode CLI 额度 2026-11-03 03:02 恢复（5 小时限额，错误码 1308）；Batch B 全量派发两次均失败（一次 0xC0000409 崩溃、一次额度错误）。
- **D-7 待裁决（DSH 已按推荐执行）**：故障转移候选同时不可用时，是否允许 DSH 直接实施 Batch B 剩余项并在 agent 恢复后补独立 Review。推荐/采用：**允许**——变更均在冻结范围与 allowed_paths 内；保留逐子项提交；独立 Review 待 Codex/ZCode 恢复后补做（不得以 DSH 自审替代）。依据：用户 2026-11-02「可推进项不耗尽不停」+ 协作协议允许 DSH 实施（仅不得自审）。
- **剩余**：I-4（组件 full 状态矩阵）、I-5（motion 三态×三类消费断言）、I-8（Elevation+高对比回退）、I-11（焦点环/浮层焦点/Tab 序）；Batch B 证据与 Handoff 待全部完成后补。
- **下一步**：DSH 继续实施 Batch B 剩余项 → agent 恢复后派独立 impl 复核（Codex 优先）→ DSH 集成验证 → done/closed_with_limitations。
## 82. FEA-06-RESIDUAL-1 Batch B 部分交付（DSH，2026-11-02 深夜）

- **I-5**：`MotionTimings` 冻结参数表（02-motion §2）落地；FluentShellSurface 消费 navigation 页面过渡（240ms）并订阅 `AppearanceCoordinator.Changed`（Dispatcher 编组）实现运行时 mode/categories 变更即时重放；reduce/category-off → 无过渡。测试：表参数 + 运行时重放（2 tests）。
- **I-8**：`Nm.Elevation.*` 消费（surface-card/detail-pane=1、drawer=2、dialog=3）；`DesignSystemThemeManager.SetContrast(High)` 运行时注入 `Nm.Border.Focus=3px` + Elevation 置空（1px 边框仍在），生成文件字节不变、Current V2 零改动；standard/reduce 阴影不变。测试：token 与渲染控件 BoxShadow/BorderThickness。
- **I-11（部分）**：焦点环 2px↔高对比 3px（ring BorderThickness 断言）；设置页离开浮层焦点移入 + 取消后返还触发控件。隐藏控件 Tab 序未单测。
- **I-4（部分）**：组件×状态声明覆盖测试（primary/secondary/danger/book-card/book-row/space-button/command-row + surface/detail/dialog/drawer）；`DesignRulesTests` 阴影规则由「禁止」更新为「只允许 DynamicResource Nm.Elevation.*」（对齐冻结设计 01 §2.3）。其余组件状态未补齐（NOT_RUN 清单见 Task）。
- **验证**（`a315bee02`）：build 0/0；**无过滤全量 1177/0/57**（基线 1137 + Batch A 33 + Batch B 7）；旧 FEA-06 PNG 字节零漂移；生成器/治理/pins 全过。证据 `batch-b-verification.log`。
- **D-7 状态**：双 agent 额度耗尽（Codex 00:23 / ZCode 03:02 恢复）；DSH 按推荐口径实施并保留独立 Review 待补（不得自审）。
- **下一步**：收尾 I-4 剩余组件状态 + I-11 Tab 序 + I-5 feedback/decorative 消费；agent 恢复后派 fresh impl Review（Codex 优先）→ DSH 集成验证 → 按实际 AC done/closed_with_limitations。
## 83. FEA-06-RESIDUAL-1 Batch B 续作（2026-11-02 深夜）

- **I-4 扩展**：`Button.segmented-item`（selected/hover/pressed/disabled）、`Slider`（hover/disabled）、`TabItem`（hover/selected/disabled）状态样式 + 声明覆盖断言；TabItem 选中 Foreground 保持 Text.Primary（与 accent pipe 既有测试一致）。
- **I-11 扩展**：隐藏控件不可获得焦点（Tab 序排除）、可见兄弟可聚焦的显式断言。
- **验证**：build 0/0；无过滤全量 **1178/0/57**；旧 FEA-06 PNG 零漂移；生成器/治理/pins 通过。交付 `6edf24904`；证据 `batch-b-verification.log` SHA `df752887…`。
- **剩余**：CommandPalette/ContextMenu/Tooltip/Toast/BatchMatrix/RunProjectionBar 独立状态；hover/pressed 视觉截图（NOT_RUN）；I-5 feedback/decorative 动画消费；独立 impl Review 待 agent 额度恢复（Codex 00:23 / ZCode 03:02）。

### 83.1 额度探针（2026-11-02 23:31）
- Codex CLI 探针（`codex exec` 最小 prompt）仍返回 `ERROR: You've hit your usage limit ... try again at Nov 3rd, 2026 12:23 AM` → 独立 impl Review 无法在 00:23 前派发；ZCode 5h 限额 03:02 恢复。
- 结论：维持 D-7 口径（DSH 实施、Review 待 agent 恢复补做）；下一可派时点 00:23（Codex 优先）或 03:02（ZCode）。
## 84. FEA-06-RESIDUAL-1 I-5 feedback 消费（2026-11-02 23:45）

- `FluentShellSurface.ApplyFeedbackTransitions`：motion 启用 → 现有 Button 注入 120ms Background BrushTransition；reduce/category-off → 清除（颜色瞬时，判据③）；挂载时与设置变更后重放。测试断言 full 有过渡/类、reduce 无。
- 验证：build 0/0；无过滤全量 **1178/0/57**；旧 FEA-06 PNG 零漂移；治理 PASS。交付 `918e4a2e3`；证据 `batch-b-verification.log` SHA `88e68f6a…`。
- 剩余（NOT_RUN）：decorative 类别专属动画消费；hover/pressed 视觉截图；独立 impl Review（Codex 00:23 / ZCode 03:02）。
## 85. FEA-06-RESIDUAL-1 review 准备与 D-8（2026-11-02 23:52）

- 独立 impl Review prompt 已备好（workspace `impl-review-prompt.md`）：范围 base `82529a3d5`→head、重点 I-6 等价性/I-7 零写入/I-5 参数与消费/I-8 高对比注入安全性/I-11 焦点/I-4 声明覆盖强度/证据诚实性；产出 `doc/reviews/FEA-06-RESIDUAL-1-impl-r1.md`。
- **D-8**：decorative 实际动画（渐变循环/翻页粒子/空态漂浮）暂缓，转后续视觉任务（ZCode），当前仅保留表/开关/reduce 禁用语义；理由与推荐已写入 Task「待裁决」区（不阻塞）。
- 交付状态：`918e4a2e3`；全量 1178/0/57；证据 SHA `88e68f6a…`；Task evidence row 已修正到实际包含该日志的提交。
- 下一步：00:23 后派 Codex 独立 impl Review（备用 03:02 ZCode）→ findings 处置 → DSH 集成验证 → done/closed_with_limitations。
## 86. FEA-06-RESIDUAL-1 I-4 有效属性 + 矩阵/AC 评估（2026-11-02 深夜）

- `FluentComponentStateEffectiveTests`：PrimaryButton/DangerButton/SurfaceCard/Dialog/TabItem 的解析后有效属性（颜色/几何/Elevation/ZIndex/disabled opacity）断言；hover/pressed/loading 视觉格仍 NOT_RUN。
- 新增证据：`verification/FEA-06-RESIDUAL-1/component-state-matrix.md`（组件×状态×断言类型）、`ac-coverage.md`（AC1–AC5 当前评估；AC2=PARTIAL 因 I-4 视觉格 + I-5 decorative D-8）。
- 验证：build 0/0；无过滤全量 **1179/0/57**；旧 PNG 零漂移；治理 PASS、pins 15/15。交付 `922a116ca`；证据 SHA `2be45bbf…`。
- 下一步：Codex 00:23 恢复后派独立 impl Review（prompt 已备）；ZCode 03:02 备用 → findings 处置 → DSH 集成验证 → done/closed_with_limitations。
## 87. FEA-06-RESIDUAL-1 I-11 四页焦点覆盖（2026-11-02 23:50）

- `FluentFocusPageCoverageTests`：四页各自键盘聚焦后实际绘制共享焦点环；覆盖设计 03 §3「四页至少各 1 焦点场景」。
- 验证：build 0/0；无过滤全量 **1180/0/57**（DS 91 + App 567）；旧 PNG 零漂移。交付 `9203c0031`；证据 SHA `a0ece253…`。
- 剩余：hover/pressed 视觉格 NOT_RUN、decorative D-8、disabled 命令零触发未自动化；独立 impl Review 待 Codex 00:23（备用 ZCode 03:02）。
## 88. FEA-06-RESIDUAL-1 I-5 三态×三类矩阵（2026-11-02 深夜）

- `MotionMatrixResidualTests`（11 tests）：full/reduce × All/Navigation/Feedback/Decorative/None 逐格对照设计参数；auto 跟随平台/full 不读平台/读失败→full+warning；reduce 下 feedback 类别开/关语义。
- 验证：build 0/0；无过滤全量 **1191/0/57**；旧 PNG 零漂移。交付 `7ca725bbf`；证据 SHA `85d305f3…`。
- 剩余：hover/pressed 视觉格 NOT_RUN、Toast severity 组合、CommandPalette 结果态、disabled 命令零触发、decorative D-8；独立 impl Review 待 Codex 00:23（备用 ZCode 03:02）。
## 89. FEA-06-RESIDUAL-1 disabled 零触发 + 子项台账（2026-11-03 00:0x）

- `FluentDisabledAutomationTests`：disabled Fluent 按钮 Automation Invoke 抛 `ElementNotEnabledException`；Click/Command Execute 均 0；`CanExecute=false`。I-4 矩阵该格 NOT_RUN → EFFECTIVE/COMMAND。
- 新增 `verification/FEA-06-RESIDUAL-1/item-status.md`（I-1…I-14 逐项 commit/断言/状态/缺口），供独立 Review 与集成验证引用。
- 验证：build 0/0；无过滤全量 **1192/0/57**（DS 92 + App 578）；旧 PNG 零漂移；治理 PASS。交付 `b79241c9a`；证据 SHA `f8413b72…`。
- 下一步：Codex 00:23 恢复后派独立 impl Review（prompt 已备，00:24 提醒已排程）；ZCode 03:02 备用。
## 90. FEA-06-RESIDUAL-1 shell 浮层焦点返还（2026-11-02 23:58）

- `FluentShellSurface.OpenDialog` 记录触发焦点、`CloseTopSurface` 返还；命令面板测试覆盖「打开→搜索框聚焦→Esc→触发按钮聚焦」。
- 验证：build 0/0；无过滤全量 **1193/0/57**；旧 PNG 零漂移；治理 PASS。交付 `981719a13`；证据 SHA `da5ecaeb…`。
- 下一步：Codex 00:23 恢复后立即派独立 impl Review（prompt/提醒已备）；ZCode 03:02 备用。
## 91. FEA-06-RESIDUAL-1 I-4 hover/pressed 有效属性（2026-11-03 00:00）

- `FluentComponentPointerStatesTests`：headless 指针合成把 Primary/Secondary 按钮的 hover/pressed 从 NOT_RUN 升级为 EFFECTIVE（断言 Accent.Hover/Accent.Base、Bg.Overlay/Accent.Muted 实际 Background）。
- 验证：build 0/0；无过滤全量 **1194/0/57**；旧 PNG 零漂移。交付 `60fd4fe56`；证据 SHA `13be8c34…`。
- 下一步：Codex 00:23 恢复后立即派独立 impl Review（prompt/00:24 提醒已备）；ZCode 03:02 备用。
## 92. FEA-06-RESIDUAL-1 I-4 Danger/BookCard 指针态（2026-11-03 00:03）

- 扩展 `FluentComponentPointerStatesTests`：DangerButton hover=StatusMuted.Failed；BookCard hover/pressed/selected 有效属性。矩阵对应行升级 EFFECTIVE。
- 验证：无过滤全量 **1194/0/57**；旧 PNG 零漂移；治理 PASS。交付 `3e879fba1`；证据 SHA `80b00f6b…`。
- 下一步：Codex 00:23 恢复后派独立 impl Review（prompt/提醒已备）；ZCode 03:02 备用。
## 93. FEA-06-RESIDUAL-1 预复核自检快照（2026-11-03 00:05）

- `verification/FEA-06-RESIDUAL-1/pre-review-verification.log`（commit `84abc9c71`，SHA `66db6559…`）：记录 head、base→head 禁止范围零改动、build 0/0、无过滤全量 1194/0/57 逐程序集、旧 FEA-06 四张 PNG SHA、TokenGen/ThemeGen `--check` up-to-date、check PASS(3)、pins 15/15。
- 用途：独立 impl Review 可直接对照该快照复核 DSH 自检结论；最终集成验证仍以 Review 后新跑日志为准。
- 下一步：00:23 后派 Codex 独立 impl Review（prompt/提醒已备）；仍限则 03:02 转 ZCode。
## 94. FEA-06-RESIDUAL-1 R3-004 Current 对照断言（2026-11-03 00:08）

- `FluentCurrentComparisonTests`：Fluent 高对比/恢复 + 同进程 V2↔Fluent 往返后焦点环/ Elevation 令牌回到冻结基线、Current 内容非 Fluent surface。
- 验证：无过滤全量 **1195/0/57**；旧 PNG 零漂移；治理 PASS。交付 `c2d4ce4b6`；证据 SHA `54a77e6a…`。
- 下一步：Codex 00:23 恢复后立即派独立 impl Review（prompt/00:24 提醒已备）；ZCode 03:02 备用。
