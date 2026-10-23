# PLUGIN-RUNTIME-1 独立 Review r3（r2 处置复核）

- Reviewer：`reviewer-settings-a`（非实现者）
- 审查头：**`992225d5f3ba5368c10a58e1925ad96bcde9ba00`**
- 实现链：`c7934429`（base）→ `a80cfd0b`（实现）→ `d603fd51` → `7253286f`（r1）→ `28876385` → `97485b89`（r2）→ `992225d5`（pin）
- 结论：**approved**。r2 的 P1/P2 主体均已闭环，未发现新 blocker；余下 4 项 P2（设计 §8 一行旧表述、STATUS 的 r1 文案、GUI 截图 02 未显示资源管理器、流式 stdin/进程树边界）属于关闭前可顺手修的文档/证据加固，不阻塞产品验收。

## 1. r2 处置复核

| r2 finding | 状态 | 核对 |
|---|---|---|
| P1-1 Task/Design 旧安全承诺 | fixed（主契约） | Task `:42` 改为“Core 不授予任何能力句柄 / 非 OS 沙箱”；Task `:73` 明确“任意路径”仅指 Core 接口，并提示 trusted-code 下插件仍可自行访问；Design §4.3 `:194`、§4.5 `:212` 加实现注记，明确恶意插件仍可读写/联网；代码/UI/Handoff 一致 |
| P1-3 Task 正文/Closeout | fixed | Task `:33` `in_review`；`:112` “待 Review approved 后 closeout”；STATUS/LEDGER/Handoff 均 `in_review` |
| P2 前端 `plugin_root` | fixed | `PluginsSnapshot` 删除字段，normalize/fake 同步删除；Core/wire 仍不投影绝对路径 |
| P2 输出上限 | fixed | 改为 `Popen` + 流式读取；按**字节**累计超 256KB 即 `kill()`；stderr `DEVNULL`；中文 100k 字符（约 300KB）测试通过 |
| P2 fingerprint/重复 load_ok | fixed | `_write_state` 复用 `_manifest_fingerprint`（`sort_keys`）；`test_enable_does_not_duplicate_load_ok` 覆盖 list → enable → list×2 仅 1 条 `load_ok` |
| P2 双源 schema 校验 | fixed | `test_frozen_runtime_contract` 改为 `application_metadata.schema_version` vs `SELECT MAX(schema_version) FROM schema_migrations`，不再是同源回读 |
| P2 schema_ref | fixed（基本） | `run_hook` 注入 `schema_ref=nm-plugin-hook/1`，并加 `isinstance(..., str)` 防御检查（见 P3-1） |
| P2 GUI 打开目录 | fixed（代码/证据部分） | `main.rs` 改为 `NEWMANGA_DATA_ROOT` → `LOCALAPPDATA/New Manga` + `plugins`，与 Core 同源；GUI 点击后有 notice 和 screenshots/02（见 P2-3） |
| AC6 拆分 | fixed | AC6a `[x]` API/隔离；AC6b `[ ]` GUI Hook 触发 **NOT_RUN**，evidence 行已改 `AC1-AC6a` |

## 2. 验证

| 检查 | 结果 |
|---|---|
| 定向 pytest（runtime + core wire） | **31 passed** |
| 全量 pytest | **2640 passed / 9 skipped / 3 既有失败**（与交付说明一致：detector 权重 2 + workbench 时序 1） |
| vitest | **45 files / 434 tests passed** |
| `tsc --noEmit` | exit 0 |
| `check.ps1` | PASS（3 warnings：3 非终态、STATUS 预算、lifecycle v1） |
| v6 | schema=6；两表 0 行/两索引；`test_v6_tables_start_empty_and_are_indexed` 覆盖 |
| 输出上限 | 中文 100k 字符用例按字节拒绝，符合修复声明 |
| 审计 | enable 后 list×2 不再重复 `load_ok`；状态驱动测试通过 |
| GUI | 12 开；默认关；拒绝原因；逐插件启停；审计；打开目录 notice `已打开插件目录`；screenshots/02 |
| Rust | 证据 `153 passed / 1 ignored / 12 filtered`；Reviewer 本机仍因 `M2RC1_PYTHON` 未设置无法完整复跑，未计产品失败 |

## 3. 剩余 P2（不阻塞）

1. **Design §8 `:291` 仍保留旧表述**：`首版可先只支持"纯计算"插件（无文件/网络）`。§4.3/§4.5 已有实现注记，但 §8 风险项未加注，仍可能与“trusted code”冲突。建议补一句“见 §4.3 实现注记，非 OS 沙箱”，或删除该括号。
2. **STATUS 文案仍是 r1**：`doc/STATUS.md:7` 当前写“r1 修复待复审”；实际已是 r2 修复后复审。建议改为“r2 修复待复审/复审中”，避免与 Handoff `97485b89` 不一致。
3. **screenshots/02 未显示资源管理器**：02 是应用面板（含“已打开插件目录” notice），不是 Explorer 窗口；因此“资源管理器打开 `file:///.../data-root/plugins`”路径仍只由 notice/code 证明。建议补一张 Explorer 截图（或接受 code path 证据）；非阻塞。
4. **流式 stdin/进程树边界**：`Popen` 已限制 stdout，但 `process.stdin.write(payload_bytes)` 在超时等待之前执行，payload 巨大或管道阻塞时仍可能卡住；`kill()` 只杀直接子进程，孙进程未由 job object/进程树处理。建议后续把 stdin 写入纳入超时、限制 payload 大小，并在 SANDBOX follow-up 中处理进程树。
5. **P3（可忽略）**：`schema_ref` 的类型检查作用在常量 `HOOK_SCHEMA_REF` 上，属于自证；payload/结果仍无 versioned schema 校验；本期只作为标记可接受，建议在 Handoff 写明“仅注入/标记，不校验 schema”。

## 4. 结论

**approved。**

- P1-1/P1-2/P1-3 已闭环；Task/Design 主安全契约、生命周期、AC6 拆分均与实现一致。
- 产品面（子进程隔离、默认禁用、迁移 v6、wire/Rust/前端、无绝对路径投影）通过独立验证；无新 P1。
- 建议 closeout 前顺手修 P2-1/P2-2/P2-3（文档/证据），P2-4/P3 可留 SANDBOX follow-up 或后续 PLUGIN-RUNTIME-2。
- 关闭后下一步：`PLUGIN-RUNTIME-2`（Hook 流水线接线）或先释放 `PLUGIN-RUNTIME-SANDBOX-1`。**当前可 approved/closeout。**
