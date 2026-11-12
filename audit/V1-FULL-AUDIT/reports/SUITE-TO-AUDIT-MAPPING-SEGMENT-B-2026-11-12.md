# 段 B 既有测试证据到专项审计映射

- 日期：2026-11-12（Asia/Shanghai）
- 审计基线：`10e4ee013835605800d3830fb960ae8d3aa04167`
- 本报告形成时 HEAD：`beaa13406438fab46ef56fa5a8852bf04ce7133d`
- 范围：仅把已提交的段 B suite 结果、静态检查和 AUDIT-00/01/02 阶段证据映射到恢复后的原始 AUDIT-00–14 定义。未运行新测试；不改变既有 suite 的 EXIT、PASS/FAIL/BLOCKED/SKIP，也不把有限 suite 结果提升为专项 PASS。

此前测试映射/执行裁决在原始专项清单恢复前形成，曾明确写明“未找到 01–14 定义”。该历史表述保留为当时事实；2026-11-12 原件恢复裁决使逐项定义现已可用。本报告补上当前映射，不回写或改写旧裁决原件。

## 结果映射

| 专项 | 已有相关证据及其真实结果 | 可支持的有限判断 | 仍缺的专项证据 / 当前状态 |
|---|---|---|---|
| AUDIT-00 项目盘点 | `reports/01_PROJECT_INVENTORY.md`；命令日志 `logs/audit-00-inventory-20261112.log`；段 B inventory 检查 EXIT 0；治理 default/TaskPath、pins 与 API inventory 另有已 pin 记录 | 静态项目、入口、schema/存储、依赖类别、测试/构建/交付结构盘点完成 | 外部模型文件字节、真实运行/GUI/安装未核；当前 `PASS` 仅限静态盘点 |
| AUDIT-01 架构 | `reports/AUDIT-01-02-ARCHITECTURE-STATIC-2026-11-12.md`；source architecture scan EXIT 0；Wire smoke 6/6 PASS；Core smoke 有 4 PASS / 7 `BLOCKED-SANDBOX-GRANT`；Avalonia TestHost 8/8 runner EXIT 1、TRX 0；sidecar isolated probe EXIT 0 复现两条 helper child 存活；ZCode Review 对 `beaa13406438fab46ef56fa5a8852bf04ce7133d` 给出 `ACCEPT`、维持 P2 | 支持受控条件下 `NM-AUD-0001` 生命周期缺陷；静态图和 Wire 子集只能支持报告中列出的架构观察 | 真实 sidecar/UI、完整 Host/Core 命令面、完整异常/状态/耦合审查未完成；阶段状态 `FAIL`，整体覆盖仍 partial；ZCode Review 未重跑测试或重算文件 hashes |
| AUDIT-02 源码质量 | Python AST/import graph EXIT 0（268 文件、0 syntax error）；Avalonia solution build EXIT 0（0 warning/error）；`dotnet format whitespace` EXIT 2（1,556 diagnostics）；七项 Python lint/type/security 工具未安装，`.NET analyzers` disabled | 仅能确认语法解析与当前配置下编译；格式诊断为真实扫描结果 | 类型、语义、完整安全、死代码/重复逻辑扫描缺失；当前 `BLOCKED` |
| AUDIT-03 漫画库/导入/项目管理 | 根 `pytest` EXIT 1（3,519 passed / 16 failed / 10 skipped）；被审用例未按 AUDIT 分类汇总；`SEG-B-PROBES-001` 目录 junction publication 实测越界写，Medium / High confidence | 后者是直接的隔离文件写路径证据，可纳入导入/文件管理风险；pytest 只能作为总体 Core suite 背景 | 未逐项映射导入格式、路径、重复、损坏图片、原文件保护、排序与项目生命周期；专项仍 `NOT_TESTED`，probe 风险已关联 |
| AUDIT-04 OCR/文本区域 | pytest 总体结果；报告记录 docTR 相关 2 项因依赖未安装而 skip、一个 manga detector 用例因环境版本而 skip | 只能确认 suite 中存在这些跳过项，不能确认 OCR 准确率或检测路径通过 | 无合成 ground truth、边界输入矩阵、OCR/检测质量测量；专项 `NOT_TESTED` |
| AUDIT-05 SFX | pytest 总体结果；无按 SFX 契约、区域状态和错误路由归类的报告 | 无可单独归因到本专项的既有结论 | SFX 需求/实现映射及针对性测试未完成；`NOT_TESTED` |
| AUDIT-06 AI 翻译 | pytest 总体结果；网络/TLS 相关 6 项 skip（环境缺 OpenSSL）；无真实付费 API 调用 | 不产生 provider/API 正确性或质量通过结论 | 翻译配置、重试/超时/并发、隐私和合成响应验证未完成；真实付费 API `NOT_RUN`；专项 `NOT_TESTED` |
| AUDIT-07 图片消除/修复/排版/导出 | pytest 总体结果；Reader export hook 3 项失败；既有其他模块用例未按本专项归组 | 3 个 Reader export 失败是已记录的具体 suite 失败；不能从大套件的 pass 数推断消除、修复、排版或导出完成 | 修复链路、像素/尺寸边界、排版/多页输出与写入目标未专项核验；`NOT_TESTED` |
| AUDIT-08 SQLite/持久化 | pytest 总体结果；1 个 FEA11 v7 fixture 因缺 `chapters.custom_rank` 失败；`SEG-B-PROBES-002` 实测 nmbak 磁盘写失败后数据库已改变且错误缺 rollback id；路径 `../` 的 nmbak defense probe 被拒绝 | 支持登记两个具体的 fixture/异常恢复观察；第三项只证明被测路径的 fail-closed | 并发读写、事务崩溃、迁移兼容、数据库关闭恢复和多文件部分写未验证；专项仍 `NOT_TESTED`，probe 风险已关联 |
| AUDIT-09 UI/UX | `.NET` 8 个测试 runner 在用例执行前因 TestHost access 失败（8/8 EXIT 1、TRX 0）；没有真实 GUI 会话 | 说明 headless TestHost 当前受阻，不是 UI 产品测试失败或通过 | 真实 UI/交互/无障碍/页面完整性 `BLOCKED`；专项 `NOT_TESTED` |
| AUDIT-10 性能/稳定性 | pytest 日志记录的是 suite elapsed；sidecar helper probe 有调用耗时观察，但使用受控休眠 helper | 不把测试 suite 耗时或 helper 清理观察冒充产品性能指标 | 无产品样本吞吐、内存/CPU、长跑、缓存和并发基准；专项 `NOT_TESTED` |
| AUDIT-11 安全/异常恢复 | `reports/AUDIT-11-SECURITY-STATIC-2026-11-12.md`、静态 inventory 与源码 manifest；`SEG-B-PROBES-001` directory junction 写越界、`SEG-B-PROBES-002` nmbak restore I/O failure、nmbak `../` defense-verified；Core smoke 7 项安全语义在 sandbox ACL 前置失败；`NM-AUD-0001` 经 ZCode 阶段 Review 接受为 P2；AUDIT-11 ZCode 独立 Review `ACCEPT`（0 P0/P1/P2，1 P3 已披露） | 证据支持阶段状态 `FAIL`，并将 blocked hook 检查保留为零证据；其余矩阵项只到报告标示的 PARTIAL/NOT_TESTED | 真实 vault/UI、恶意输入 fuzz、完整 SQL/命令污点、Python 漏洞数据库、竞态、生产 sidecar 关闭和远端材料可见性仍未验证；扫描器 SHA 差异为单个尾随空格且未重跑扫描；具体限制见 AUDIT-11 报告与 Review |
| AUDIT-12 Windows 构建/交付 | `dotnet build` EXIT 0 仅为开发 solution build；`packaged` smoke 指向 Legacy Tauri 产物，按裁决为 `NOT_RUN-legacy`；无干净环境安装记录 | 可支持当前源码在现有 SDK/工作区中的一次开发构建成功 | Release publish、资源/模型打包、安装/启动/卸载、中文路径、非管理员和干净 Windows 均未验证；专项 `NOT_TESTED` |
| AUDIT-13 端到端场景 | Wire smoke 6/6 PASS（真实 Core 子进程、协议 2.3 的有限命令）；Core smoke 4 PASS / 7 `BLOCKED-SANDBOX-GRANT`；Legacy frontend/packaged SKIP | 仅支持 Wire smoke 覆盖的有限协议行为 | A–H 场景均未完成；真实漫画数据禁止触碰，需使用获准合成输入；专项 `NOT_TESTED` |
| AUDIT-14 V1 完整性/技术债务 | AUDIT-00 inventory、当前阶段报告与已知 issue 台账可作来源 | 当前可以建立需求/实现/Mock/Legacy 的审计索引，尚不能给完成率 | 尚无逐需求 V1 承诺矩阵及 Mock/未接线/规划项分类；专项 `NOT_TESTED` |

## 跨 suite 结果与不可外推项

- `pytest`：3,519 passed / 16 failed / 10 skipped / 11 warnings，EXIT 1。失败具体为 Reader export hook 3 项、FEA11 v7 fixture 1 项、plugin sandbox 12 项；pytest 总数不是 15 个专项的通过率。
- `probes`：2 passed / 1 failed，EXIT 1。两项 finding 为隔离实测，第三项是 `../` 被拒绝的防线验证；不等于 AUDIT-11 全项结论。
- `.NET tests`：8/8 runner EXIT 1、TRX 0 tests，状态为 `BLOCKED-TESTHOST-ACCESS`。不能记作产品测试 FAIL 或 PASS。
- `smoke --only core,wire`：17 checks 中 10 PASS / 7 FAIL，runner EXIT 1；7 项 Core 失败由 ZCode 记为 `BLOCKED-SANDBOX-GRANT` 及级联。程序报告保持 FAIL。
- `governance`：已有 default check EXIT 0（3 warnings）；历史 checkpoint 上 TaskPath / 18 pins / API inventory 的 EXIT 0 只适用于各日志记录的 HEAD。最终交付 HEAD 仍需复跑。
- `frontend`、`rust`、`desktop`、`npm-audit`、`packaged` 为 Legacy / 非当前产品证据，`NOT_RUN-legacy`；真实 GUI、付费 API 与私有漫画内容未验证。

## 状态结论

映射只确定既有 suite 证据与专项的关系，不宣告专项完成。当前有效专项状态仍以 `AUDIT_TASKS.md` 和 Task 卡为准：AUDIT-00 为有限范围 `PASS`，AUDIT-01 为 `FAIL`，AUDIT-02 为 `BLOCKED`，AUDIT-11 阶段结果为 `FAIL`（独立 Review `ACCEPT`，P3 已披露）；AUDIT-03–10、12–14 仍未完成，AUDIT-11 的其余检查面也未完成。Release Gate 继续 `BLOCKED`。AUDIT-11 专项后续证据详见阶段报告与 `reports/ZCODE-AUDIT-11-REVIEW-2026-11-12.md`。
