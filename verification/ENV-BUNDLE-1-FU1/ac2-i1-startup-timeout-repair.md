# ENV-BUNDLE-1-FU1 AC2 I1：packaged startup timeout 返修记录

日期：2026-10-16。返修基于 `151d14b95679852b736b5270f027639ccfbd3054`，代码与重跑原始日志提交于 `cffa9666fbbe5f2adfe213de37a8beb20a994a38`。本记录用于复核 AC2 启动超时脆弱性、修复边界及重跑结果；交付仍待独立 Reviewer 复跑，不代表已接受。

## Reviewer 复现与反例

问题发生在测试夹具 `PackagedLab::start_library()`：每次启动 68,717,156-byte frozen `core_service.exe` 后，必须等待真实 startup ping，但旧启动 deadline 固定为 30 秒。并发 cargo 编译和另一条 Task 负载下，Core 启动响应超过该 deadline，测试将其报告为 `CORE_UNAVAILABLE`。同一用例之后既有失败也有通过，说明该验收结果对机器负载及冷启动时序敏感。

| Reviewer 运行 | 实际结果 | 耗时 | 归档日志 | 原始来源路径 | SHA-256 |
|---|---|---:|---|---|---|
| 全量六项；机器同时 cargo 编译及执行另一条 Task | 4 passed / 2 failed；失败为 `real_core_sidecar_rc4_commands_round_trip_typed_errors` 与 `real_core_sidecar_retype_pair_empty_page_and_typed_rejection`，均 startup ping timed out | 111.59 s | [reviewer-rerun-packaged.log](reviewer-rerun-packaged.log) | `G:/CODEX/New Manga.workspace/tmp/guarded/FU1-reviewer-rerun-packaged.log` | `0ae5ab593cc859dd2203b1c8773f0bd899161aa3f4a24844cba74d7037d0a004` |
| 隔离重跑 retype 单项（第一次） | 0 passed / 1 failed；同一启动 ping 超时 | 35.03 s | [reviewer-rerun-isolated.log](reviewer-rerun-isolated.log) | `G:/CODEX/New Manga.workspace/tmp/guarded/FU1-reviewer-rerun-isolated.log` | `4c1b9e469efd445863bd6be1888ec9bdc2688f5830cee708ceab6ec0539c347f` |
| 隔离重跑同一 retype 单项（第二次） | 1 passed / 0 failed | 13.58 s | [reviewer-rerun-isolated-2.log](reviewer-rerun-isolated-2.log) | `G:/CODEX/New Manga.workspace/tmp/guarded/FU1-reviewer-rerun-isolated-2.log` | `188097a7583267cab7061be719a90c10fc71bbc882e43d2e5a8aadefdc0b1141` |

仓库内三份 Reviewer 日志均由上述原始路径复制并逐字节比对 SHA-256；源日志保持只读。原作者此前机器空闲时的 `6/6` 运行耗时 `8.73 s`，见 [原 AC2 日志](ac2-packaged-six-tests.log)。

这些数据支持“30 秒测试启动 deadline 会制造负载相关假阴性”的判定；它们不说明业务协议断言失败，也不能据此推断每次失败的精确 Core 启动时长。

## 有界修复

仅修改 `apps/desktop/src-tauri/src/packaged_sidecar_tests.rs` 的测试夹具启动 deadline：

- 新环境变量：`M2RC1_PACKAGED_STARTUP_TIMEOUT_SECS`。
- 默认值：`120` 秒；只接受正整数，非法值或零值直接失败。
- 未设置时使用新默认值；设置时可覆盖，便于测试环境配置。
- startup ping 仍须真实成功，`spawn_with_startup_ping(...).expect(...)` 保留；六项场景断言未改、未删除、未跳过，也未 mock frozen bundle。
- 代码注释引用 Reviewer 的 `111.59 s` 负载运行、隔离 `13.58 s` 成功反例与 frozen exe 大小，说明默认值理由。

测试源文件 SHA-256：`2420f614e47cde03645f69fdba1ea9267d823d0ab1c48dc16590f305c41ffffa`。原始重跑日志：[ac2-packaged-six-tests-i1-repair.log](ac2-packaged-six-tests-i1-repair.log)；SHA-256：`500c6ff537c793d112943251671d89d14761578aec25f7315c90bd34fe5ca821`。

## 返修后全量 AC2 重跑

执行环境与结果来自上述原始 Cargo 日志：

- Shell：PowerShell `7.6.6`；`cargo 1.98.1`；`rustc 1.98.1`。
- 命令：`cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml packaged_sidecar_tests::real_ -- --nocapture --test-threads=1`。
- 环境：`M2RC1_PACKAGED=1`；`M2RC1_SRC_ROOT`、`M2RC1_PYTHON` unset；`M2RC1_PACKAGED_STARTUP_TIMEOUT_SECS` unset，因此实际使用默认 `120` 秒；运行 Core 使用 frozen PyInstaller bundle，不依赖外部 Python venv。
- 结果：`6 passed; 0 failed; 0 ignored; 77 filtered out`；Cargo 测试时长 `139.55 s`，含编译的命令总耗时 `174.24 s`；exit code `0`。
- frozen `core_service.exe`：worktree `apps/desktop/src-tauri/target/core-sidecar/core-sidecar/core_service.exe`；68,717,156 bytes；SHA-256 `896bd56286b25bc8539028d52f3ef991cfbcbda24f93ae6c6d75758a7dbfd842`。

| packaged 场景 | 结果 | 保留的断言语义 |
|---|---|---|
| `real_core_sidecar_answers_startup_ping_on_fresh_catalog` | PASS | 真实 startup ping 返回 protocol 2.3，并创建 catalog |
| `real_core_sidecar_rc4_commands_round_trip_typed_errors` | PASS | revision list/restore/rerender 返回 `TARGET_NOT_FOUND` |
| `real_core_sidecar_retype_pair_empty_page_and_typed_rejection` | PASS | 未知 page 为空 regions；未知 region 返回 `TARGET_NOT_FOUND` |
| `real_core_sidecar_round_trip` | PASS | frozen catalog/host sidecar 往返及 `REF_REVOKED` |
| `real_core_sidecar_settings_round_trip_and_typed_rejection` | PASS | 合法设置读回；非法值返回 `INVALID_REQUEST` 且保留旧值 |
| `real_library_sidecar_round_trip_and_eof` | PASS | Core protocol 2.3、空书架及 EOF `CORE_UNAVAILABLE` |

## 生产启动 deadline 调查（只报告）

生产 Host 启动路径也把 Core startup ping deadline 设为 30 秒：

- `apps/desktop/src-tauri/src/main.rs:816-822` 注释说明生产 Core 必须在 channel sidecar 前通过 30 秒 startup ping。
- `apps/desktop/src-tauri/src/main.rs:832-851` 是生产启动分支；packaged Core 调用在 `main.rs:834-841`，传入 30 秒位于 `main.rs:840`；source-backed Core 调用在 `main.rs:842-849`，传入 30 秒位于 `main.rs:848`。失败会使 Host 启动路径的 `.expect(...)` panic。
- `apps/desktop/src-tauri/src/library_bridge.rs:611-618` 的 `spawn_with_startup_ping` 接收调用方提供的 `startup_timeout`；`library_bridge.rs:626-634` 按该值等待并在超时后返回 `CORE_UNAVAILABLE`，没有独立的宽松默认值。

因此，若生产环境使用同一 frozen bundle 且承受相似并发负载，Host 启动也存在同类冷启动误判风险。这是根据测试复现和调用参数作出的风险推断，**本次未对生产启动进行故障复现，也未改任何产品代码**。请 Coordinator 另立 Task 决定产品期限和启动失败处理；AC3 HostControl `REF_EXPIRED` 仍维持原 `BLOCKED` 判定。

## 本次未覆盖

- 未重新运行 77 项 source-backed 用例、NSIS installer 或 GUI 安装验收；本次只执行 AC2 要求的六项 packaged 测试。
- 未执行显式覆盖环境变量的第二轮；本次全量运行使用新默认值。
- Reviewer 对返修提交的独立复跑尚未发生，Task 仍待 Review。
