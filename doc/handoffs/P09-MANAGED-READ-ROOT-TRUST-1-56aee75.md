---
task_id: P09-MANAGED-READ-ROOT-TRUST-1
author: DeepSeek Harness
recipient: Codex
base_commit: b8a1e519703f13af73b320dded117004b4bb189a
delivery_head: 56aee75ae8fa88913655f27c019345224414096d
status: in_review  # 交付时快照；当前状态以 Task 文件与 STATUS 为准
---

# Handoff：P09-MANAGED-READ-ROOT-TRUST-1（托管读取/导出路径的 root 可信性）

> 本文件按 `doc/09_COLLABORATION.md` §5 建立（`doc/handoffs/TASK-xxx-<short-head>.md`）。
> 验证证据在 `verification/P09-MANAGED-READ-ROOT-TRUST-1/`，由本文件引用。
> **本 Handoff 不创建 Review、不声明 AC 已由独立方确认**；Review 由 Codex 另行进行。

## 交付结果

**范围**：R5b P2 转交的读取/导出路径 root 可信性，8 处（4 处 `core_service.py`、
3 处 `core_assembly.py`、1 处 `handle_resolver.py`），逐处测试。

### 设计答案（第一交付物，先于产品代码提交）

`verification/P09-MANAGED-READ-ROOT-TRUST-1/DESIGN-expected-identity.md`（commit `a5147eed8`）。

**「期望身份」从哪来？** —— **装配时对配置根实际打开的那一个句柄**：

1. **对象身份** `(volume_serial, file_index)`：句柄的 `GetFileInformationByHandle`，装配时一次；
2. **规范路径**：同一句柄的 `GetFinalPathNameByHandle`；
3. **词法绝对根**：`os.path.abspath(str(configured_root))`，纯字符串、零文件系统访问。

每次读取：词法折算引用（零文件系统访问，期望值在此冻结）→ 打开配置根并比对**对象身份** →
打开目标并要求**句柄规范路径 == 快照规范根 + 词法相对段** → **通过同一句柄读取**。
名字可以被随时重定向，快照不能；校验与使用因此是同一个对象。第 8 处
`resolve_namespace_identity` 用局部同构版本：`expected = os.path.abspath(str(path))`
在任何文件系统访问前冻结 → 单次打开 → 规范路径/身份只来自句柄 → `final == expected` 才接受。

### 提交列表（分支 `dsh/P09-MANAGED-READ-ROOT-TRUST-1`）

| commit | 内容 |
|---|---|
| `a5147eed8` | 设计冻结 + Task 状态 `in_progress`（无产品代码） |
| `56aee75ae` | **实现 head**：3 个源文件 + `tests/security/test_p09_managed_read_root_trust.py`（11 测试） |
| 交付文档提交（在本文件之后） | Task `in_review` + Canonical Evidence（证据文件 pin 到该提交） |

### 变更路径

| 路径 | 内容 |
|---|---|
| `src/infrastructure/resource_channel/handle_resolver.py` | **新增读取原语** `ManagedRootTrust`（capture / `read_bytes` / `digest_of` / `verify_existing` / `canonical_of`）+ `_open_trusted_read_handle`；**重写** `resolve_namespace_identity`（第 8 处） |
| `src/bootstrap/core_assembly.py` | `assemble_core_services` 在 `storage.ensure_layout()` 后捕获快照，写入 `CoreServices.managed_root_trust` 并传给两个私有读取类；第 5/6/7 处改走快照 |
| `src/bootstrap/core_service.py` | 第 1/2/3/4 处改走快照；导出 hash/惰性 provider 改为句柄方式；第 2 处用「已验字节 → 私有临时文件」关闭发布器的按名字复制窗口 |
| `tests/security/test_p09_managed_read_root_trust.py` | 8 处各一条判别力测试 + 链接策略测试 + 原语单测（共 11） |

**未改动**：删除路径（`win_unlink.py`、`managed_storage.remove_managed`、`render_preview.py`、
`tile_cache_sweep.py`、`backup.py`）、IPC 契约、Schema、ACL、依赖清单、前端。

### AC 对照

| AC | 状态 | 依据 |
|---|---|---|
| AC1 | **MET** | `ac1-r5b-repro.py`：base=VULNERABLE（读到 `OUTSIDE`）、current=SAFE（typed 拒绝）；exit 0。`logs/ac1-after-fix.txt` |
| AC2 | **MET** | 8 处测试的换 root 前合法读取断言 + 8 个套件逐套件回归（base/current 计数一致，security 29→40）。链接策略显式记录（祖先链接允许当身份匹配；根下链接拒绝） |
| AC3 | **MET** | `ac3-discrimination.py`：同一测试文件在 base 源码快照上 8/8 FAIL、当前 8/8 PASS；`SITE-MATRIX.md` 逐处映射；`logs/ac3-discrimination.txt` |
| AC4 | **MET** | `logs/ac4-change-files.txt`：仅 4 个实现/测试文件 + 2 个本 Task 文档/证据；无依赖/契约/Schema/ACL 变更 |
| AC5 | **MET** | `ac5-run-delete-probes.py`：前序 9 个探针 9/9 与基线一致（含 n002-race 的 INCONCLUSIVE 保持 INCONCLUSIVE）；exit 0 |

## 验证证据

| AC/场景 | 实际命令 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| 设计冻结 | 阅读/撰写 | base `b8a1e51` | 已完成 | `DESIGN-expected-identity.md`（commit `a5147eed8`） |
| AC1 | `C:/Python314/python.exe verification/P09-MANAGED-READ-ROOT-TRUST-1/ac1-r5b-repro.py` | Windows / Python 3.14.6 / `56aee75ae` 与 base 快照 | **exit 0**；base=VULNERABLE、current=SAFE | `logs/ac1-after-fix.txt`、`logs/ac1-before-fix.txt`（修复前 exit 1） |
| AC3 | `C:/Python314/python.exe verification/P09-MANAGED-READ-ROOT-TRUST-1/ac3-discrimination.py` | 同上 | **exit 0**；8/8 判别 | `logs/ac3-discrimination.txt`、`SITE-MATRIX.md` |
| AC2/AC4 回归 | `pwsh -NoProfile -File verification/P09-MANAGED-READ-ROOT-TRUST-1/run-suites.ps1` | 同上 | **exit 0**；core 564 / storage 87 / m2_resource_channel 106 / security 40 / library 63 / reading_export 141 / export 13 / m2_acceptance 37 | `logs/summary.txt`、`logs/suite-*.log`、`logs/baseline/`（改动前基线） |
| AC5 | `C:/Python314/python.exe verification/P09-MANAGED-READ-ROOT-TRUST-1/ac5-run-delete-probes.py` | 同上 | **exit 0**；9/9 一致 | `logs/ac5-delete-probes.txt`、`.json`、`ac5-delete-probes/` |
| 新测试 | `python -m pytest tests/security/test_p09_managed_read_root_trust.py -q` | 同上 | **11 passed** | `logs/suite-security.log`（40 = 29 旧 + 11 新） |

**未运行**：Rust（`cargo test`）、React/前端、packaging 测试。原因：变更面只在 Python Core 读取路径，
未改 IPC/契约/Schema/前端；这些套件不属于本 Task 的 AC1–AC5 范围。不得把未运行写成 PASS。

## 接收方式

- 仓库/worktree：`G:/CODEX/New Manga.workspace/worktrees/P09-MANAGED-READ-ROOT-TRUST-1`
- branch：`dsh/P09-MANAGED-READ-ROOT-TRUST-1`；base：`b8a1e519703f13af73b320dded117004b4bb189a`；
  实现 head：`56aee75ae8fa88913655f27c019345224414096d`；分支 tip 以交付文档提交为准。
- 复现：在 worktree 根依次运行上面四条命令（AC1、AC3、AC5、run-suites）。三个 Python 探针
  都是**自包含**的：`ac1`/`ac3` 用 `git archive <base> src` 取 base 快照（不 checkout、不改仓库），
  在系统临时目录运行并自行清理；`ac5` 在 `verification/.../_scratch/` 建夹具并在结束时清理。
- 预置：Python 3.14.6（`C:/Python314/python.exe`）、pytest 9.1.1、PySide6 6.11.2、Windows junction 可用。
- 需要接收者检查的具体点：
  1. Review `ManagedRootTrust` 的守卫序列与 §「链接策略」是否与设计文档一致；
  2. 确认 8 处映射与测试一一对应（`SITE-MATRIX.md`），且 base 上确实失败（`logs/ac3-discrimination.txt`）；
  3. 确认 delete 路径零改动（`git diff b8a1e51..HEAD -- src/infrastructure/filesystem src/infrastructure/sqlite src/infrastructure/resource_channel/render_preview.py src/infrastructure/imaging` 为空）；
  4. 评估残余风险（交接窗口、硬链接、同名替换、root 搬走 fail-closed）是否接受。

## 下一任务建议（必填）

- **无需下一步操作**（没有已释放且可安全承接的新 Task）。本 Task 的下一步是 **Codex 对
  `56aee75ae`（及交付文档提交）的独立 Review**，不是新 Task；Review 若要求修改，Owner 按
  `changes_requested` 流程回到 `in_progress` 并以新 head 再次进入 `in_review`。
- 候选（**未释放、不得自行启动**）：若未来需要把「同名目录替换/硬链接」也纳入
  强保证，可释放一个把读取路径改为 `NtCreateFile(RootDirectory=已验证根句柄)` 相对句柄链的
  Task（与删除域 `win_unlink.unlink_by_handle` 同类基建）；本 Task 不声称覆盖该项。

## 风险与遗留

1. **残余风险（已显式接受并记录，见设计文档第六节）**：
   - 第 5/6 处把 `file://` URI 交给 QML、第 3 处 Reader 预览发布器按名字复制源文件：
     存在「Python 校验完成 → 消费者打开」之间的交接窗口（消费者不在 Python 控制内）。
   - 第 2 处的同类窗口已用「已验字节 → 私有临时文件」关闭。
   - 硬链接、以及「根身份校验与叶子打开之间把根改名并在原路径重建同名目录」：需要托管树/
     配置根父目录写权限，属于既有 ACL/不可变层边界；本 Task 不引入叶子身份快照。
   - 装配后 root 被搬走/替换 → 所有读取 fail-closed（设计目标；运维影响：移动数据目录后需重启 Core）。
2. **链接策略取舍**：祖先/根本身 reparse 允许（身份匹配时），根下 reparse 全部拒绝。
   「任一祖先 reparse 即拒绝」未采用，理由与证据见设计文档第四节、`SITE-MATRIX.md`。
3. **行号漂移**：Task 原引用的行号是 R5b 审计时（`34fe1069f`）的；base 实际行号见 `SITE-MATRIX.md`。
4. **未运行套件**：Rust/前端/packaging（理由见上）；Review 不得把本 Handoff 的 PASS 扩展到这些面。
5. 未执行任何真实删除/移动/GC/prune/清理；未 push/merge；未修改主仓库或其他 Task。
