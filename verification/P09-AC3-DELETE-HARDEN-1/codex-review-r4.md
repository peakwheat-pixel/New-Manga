<!-- codex session: 01a151af-5b62-7831-ab1e-a77c5ff0fc76 | reviewed_head: 2f09d0d1f -->

reviewed_head: `a68d48afb06c198bdff8bed4b44e16136bbc06b4`  
decision: `changes_requested`  
findings: **3**（R3 的 N-004 未关闭；新增 P2、P3 各 1 项）

## 验证结果

| 探针 | `injection_fired` | `outside_survived` | 判定 |
|---|---:|---:|---|
| `n002-race-probe.py` | `False`（脚本字段为 `race_hook_fired`） | `True` | **INCONCLUSIVE**。脚本虽打印 `SAFE`，但攻击 hook 没触发，不能据此判安全。 |
| `n002-race-probe2.py` | `True` | `True` | **SAFE**。运行后另核实 `root\pages` 确实是指向 outside 的 junction。 |
| `n004-ancestor-probe.py` | `True` | `True` | **SAFE，仅针对该注入时序**。另核实 `mklink` 返回 0，`trusted` 是 reparse point，且与 `outside` 指向同一目录。 |

实际运行结果：

- `python -B -m pytest -p no:cacheprovider tests/storage -q`：**86 passed**。
- `python -B -m pytest -p no:cacheprovider tests/core -q`：**558 passed**，1 条 Pillow deprecation warning。
- `verify_all.py`：**exit 0**；历史 JSON 写入被进程内拦截，前后磁盘 SHA-256 均为 `67d4db…d6261`。脚本报告 10 项误删防护零副作用、历史脱离通过、orphan 为 0、AppData 未改。
- 六个指定 Rust preview-rotation 测试：**各 1 passed**；另跑 `permanently_delete_error_phase`：**1 passed**。
- `tests/packaging/test_frozen_runtime_contract.py`：**3 passed**。

`verify_all.py` 的历史 JSON 写入确已拦截；它仍打印了“Wrote structured evidence”，但该文件未被写入。`pytest tests` 全量套件本轮未运行。

## R3 六项判定

| Finding | 判定 | 实际证据 |
|---|---|---|
| N-001 | **CLOSED** | 契约 rev 2.11 明确说明协议版本仍为 minor 3、回收站错误 wire 值为 `LIST_BOOKS_FAILED` / `UNKNOWN`；与 Core 常量及响应投影一致。[core_service.py](<G:/CODEX/New Manga/src/bootstrap/core_service.py:189>)、[契约](<G:/CODEX/New Manga/doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:811>) |
| N-002 → N-004 | **NOT_CLOSED** | 逐句柄链能阻止链建立之后的祖先替换，但生产调用先对 root 执行 `Path.resolve()`。我按生产顺序实测：先把 `trusted` junction 到 `outside`，解析得到 `outside\derived`，随后删除函数返回 `True`，外部文件消失。见 [library.py](<G:/CODEX/New Manga/src/infrastructure/sqlite/library.py:1110>)。 |
| N-003 | **CLOSED** | 11/11 已登记 pin 的磁盘字节 SHA-256 均匹配；每个 `commit:path` 均存在。Task 中全部 14 个完整 40 位 SHA 均能解析为 commit。[Task pins](<G:/CODEX/New Manga/doc/tasks/P09-AC3-DELETE-HARDEN-1.md:154>) |
| F-002 | **CLOSED** | 六个指定 Rust 测试均实跑通过；`tests/core` 558 项通过。 |
| F-007 | **CLOSED** | 当前分类为 4 项环境可用性反转、2 项 Transformers API 不兼容；Task 与 AC12 证据均保留了这一区分。[Task](<G:/CODEX/New Manga/doc/tasks/P09-AC3-DELETE-HARDEN-1.md:85>) |
| N-005 | **CLOSED** | 删除路径实际使用 `_FILE_OPEN`；`_FILE_OPEN_IF` 仅作为未使用常量保留，缺失组件不会被创建。[win_unlink.py](<G:/CODEX/New Manga/src/infrastructure/filesystem/win_unlink.py:53>)、[使用点](<G:/CODEX/New Manga/src/infrastructure/filesystem/win_unlink.py:246>) |

## AC1–AC12

| AC | 判定 | 依据 |
|---|---|---|
| AC1 | **PASS** | `tests/core` 全绿，包含 Core dispatcher 路由；代码中可见 Tauri production 注册。 |
| AC2 | **PASS** | `tests/core` 全绿，包含多目标 Run 删除回归。 |
| AC3 | **PARTIAL** | Core 测试通过；本轮未运行 React/Vitest 混合 pending 重试测试。 |
| AC4 | **PASS** | Core 测试通过；六个 preview-rotation Rust 测试实跑通过。 |
| AC5 | **PARTIAL** | 两个实际触发的 junction 探针通过；但生产式“根祖先在 resolve 前已是 junction”复现成功误删，见 N-004。 |
| AC6 | **PASS** | `verify_all.py` 实测历史脱离通过；`tests/core` 全绿。 |
| AC7 | **PASS** | `verify_all.py` 在真实迁移库上完整运行通过，orphan 扫描为 0。 |
| AC8 | **PASS** | `verify_all.py` 通过；`library.py` 中无 `os.walk` 调用。 |
| AC9 | **PASS** | `permanently_delete_error_phase` 实跑 1 passed。 |
| AC10 | **PASS** | schema v5 packaging 测试实跑 3 passed。 |
| AC11 | **PASS** | 11 个 pin 的磁盘 SHA、`commit:path` 和完整 SHA 均通过核验。指定分支 tip 另有一个仅更新 Task `delivery_head` 的后续提交；未纳入本次固定 head 代码审查。 |
| AC12 | **NOT_VERIFIED** | 本轮没有重跑 `pytest tests` 全量套件；既有报告的 4+2 分类正确，但不能替代本轮全量验证。 |

## 新增问题

- **P2 — N-004 探针可能把“junction 未建立”报告为 SAFE**：[n004-ancestor-probe.py:19](<G:/CODEX/New Manga/verification/P09-AC3-DELETE-HARDEN-1/n004-ancestor-probe.py:19>) 在 `mklink /J` 前就设置 `fired`，没有检查命令结果或确认链接目标；失败时目录已被删除，后续拒绝缺失路径仍可能得到 `outside_survived=True`，造成假阳性。本轮通过外部检查确认本次 `mklink` 成功，但探针本身应验证 junction。
- **P3 — 探针临时目录不遵守 workspace 路径规则**：[n004-ancestor-probe.py:6](<G:/CODEX/New Manga/verification/P09-AC3-DELETE-HARDEN-1/n004-ancestor-probe.py:6>) 使用默认 `tempfile.mkdtemp()`，直接运行会写入系统默认临时目录；仓库要求新 temp 放在相邻 workspace 的 Task 子目录（`AGENTS.md:44`）。

## Standards

发现上述 P3 workspace 临时目录规则问题；未发现其他有文档依据的标准违规。

## Spec

N-004 的逐句柄打开在 anchor 建立后没有重新解析完整路径；`_open_root` 的 `opened.pop()` 正确把最终 root handle 转交调用方，父句柄在 `finally` 关闭，删除函数也在 `finally` 关闭已登记句柄。`DELETE` 只在最终文件的 `want_delete=True` 时请求。Windows 上调用方会先拒绝空路径，句柄实现失败返回 `False`，不会因失败回退到路径删除；`None` 回退仅适用于非 Windows。

字面 UNC 路径拒绝是 fail-closed；当前 AC/契约没有 UNC 支持要求。盘符锚点的通用安全性仍需收窄：Windows drive letter 属于 DOS device namespace，可由 `DefineDosDevice` 修改；系统启动时建立的盘符映射对非管理员受保护，但 SUBST/映射盘并不等同于“无祖先的本地卷根”。当前机器没有现存 SUBST 映射；本轮未验证该别名路径是否会经调用方 `Path.resolve()` 规范化，故这项风险为 **NOT_VERIFIED**。[Microsoft DefineDosDeviceW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-definedosdevicew)、[GetVolumeNameForVolumeMountPointW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getvolumenameforvolumemountpointw)。

## 结论

**不能进入集成 `done`。** N-004 的生产调用路径仍可删除根祖先 junction 指向的外部文件；AC5 保持 PARTIAL。已核实 `P09` 的 AC3 delete 子条件仍为 **BLOCKED**，不得翻为 PASS。

建议下一步：让 Task Owner 移除删除前对 root 的跟随式 `Path.resolve()`，对未解析的绝对 root 从真实卷锚点逐段拒绝 reparse；增加覆盖生产调用顺序的既有祖先 junction 回归测试，并修正 N-004 探针的 junction 确认与 temp 位置，再固定新 head 复审。

只读边界说明：未修改仓库文件；验证夹具由必跑探针和 `verify_all.py` 创建在 `G:\CODEX\New Manga.workspace\temp\P09-AC3-DELETE-HARDEN-1-R4\`，按不删除文件的约束保留。仓库原有的 `.qoder-credits/report.json` 修改状态保持不变。