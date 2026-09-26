# M2-S1 证据清单与复现说明

- 权威执行转录：[`raw/00-run-all.log`](raw/00-run-all.log)（含确切命令、日志行数、逐探针 exit code、
  收集到的结果 JSON 的 SHA-256）。
- 重复运行（第二次在已存在旧 report 文件的情况下）：[`raw/04-repeat-run-1.log`](raw/04-repeat-run-1.log)。
  两次均 `all_zero = True`。
- 全量文件 hash：`raw/06-evidence-hashes.log`（该文件自身不被自哈希——鸡生蛋问题，属已知例外）。

## 1. 探针（可执行输入）

| 文件 | 作用 |
|---|---|
| `probes/00_recon.ps1` | 只读固定点/clone/环境转录 → `raw/00-recon.log` |
| `probes/00_meminfo.py` | 主机内存/CPU/OS 事实（ctypes，绕开被沙箱拒绝的 CIM） |
| `probes/m2s1_lab.py` | 共享库：psapi 内存计量、确定性 PNG 生成、capability token 原型、section/handle ctypes 封装 |
| `probes/make_fixtures.py` | 合成 fixture 生成器（固定种子）→ `raw/fixtures.json` |
| `probes/probe_a_token.py` | 路线 A：受限引用/token（Core 子进程 + JSON 控制通道 + 带外读文件） |
| `probes/probe_b_stream.py` | 路线 B：管道流式/分块（含背压、取消、截断、崩溃、超限拒绝） |
| `probes/probe_c_section.py` | 路线 C1/C2/C3：命名 section、匿名 section + `DuplicateHandle`、只读写屏障 |
| `probes/probe_d_base64.py` | 路线 D：JSON/Base64 对照（含按文档内分块与按消息边界分块、naive 最坏情况一次） |
| `probes/probe_e_concurrency.py` | 并发/容量：A/B/C 三路线的 1/2/4/8 消费者 |
| `probes/run_all.ps1` | 统一 runner（首次运行前会清理陈旧 report；不清理则第二次运行会误读旧结果——见 §5） |

## 2. 结果与日志

| 文件 | 内容 |
|---|---|
| `raw/fixtures.json` | 每个 fixture 的尺寸、PNG 字节、SHA-256、种子、zlib 级别 |
| `raw/probeA-result.json` | 路线 A 的 15 个场景、控制通道双向字节、Core/宿主内存 |
| `raw/probeB-result.json` | 路线 B 的 12 个场景、字节、耗时、吞吐、首字节、WS 增量 |
| `raw/probeC-result.json` | 路线 C 的 14 个场景（C1/C2/C3） |
| `raw/probeD-result.json` | 路线 D 的 8 个场景（含 0 字节拒绝与 naive 最坏情况） |
| `raw/probeE-result.json` | 并发 11 个场景 |
| `raw/05-final-digest.log` | 上述 JSON 的紧凑摘要（便于 Reviewer 快速比对） |
| `raw/10..14-*.log` | 各探针的完整 stdout + `exit_code=` |

所有收集到的结果 JSON 的 SHA-256 同时出现在 `raw/00-run-all.log` 的 `P-04` 段与
`raw/06-evidence-hashes.log`，两者一致（已核对）。

## 3. 复现步骤

```powershell
Set-Location 'C:/Users/49745/.codex/worktrees/M2-S1-dsh-resource-channel'

# 1) 固定点核验（只读）
pwsh -NoProfile -File verification/M2-S1/probes/00_recon.ps1

# 2) 全套探针（含 fixture 生成）；日志同时落盘并输出到控制台
pwsh -NoProfile -File verification/M2-S1/probes/run_all.ps1 `
  | Tee-Object -FilePath verification/M2-S1/raw/00-run-all.log

# 3) 清理 lab（可选）
Remove-Item -Recurse -Force (Join-Path $env:TEMP 'm2s1-lab')
```

前置条件：Windows x64、Python 3.14（`python` 在 PATH）、PowerShell 7、`cmd.exe`（用于创建 junction）。
lab 目录默认 `%TEMP%\m2s1-lab`，可用 `-Lab` 覆盖。探针会创建约 200 MB 合成 fixture。

## 4. 缺陷与修正记录（影响可复现性，必须保留）

执行中发现并修正了**两个探针自身**的缺陷。两者都只影响探针，不影响 `src/**`；记录在此以便 Reviewer
判断证据可信度时知情。

### 4.1 路线 C 误读上一轮遗留的 report 文件

`C2-02/C2-03` 通过轮询子进程写出的 report 文件获取 `(pid, handle)`，但**未在启动前删除上一轮遗留的
report**。第二次运行时轮询立即读到旧文件，于是用了**已退出进程**的 PID，`OpenProcess` 返回
`ERROR_INVALID_PARAMETER (87)`，把“同用户可复制句柄”这一真实属性**误报为拒绝**。

- 修正：所有子进程 report 路径在 spawn 前先删除（`probe_a/b/c/d/e` 全部处理）；
  `C2-02` 增加 `holder_alive_while_hostile_ran` 断言，避免再用死进程得出结论。
- 验证：修正后连续两次运行结果一致（`raw/00-run-all.log` 与 `raw/04-repeat-run-1.log`），
  且 `C2-02 hostile_duplication_succeeded = true`、`C2-03 DUPLICATE_HANDLE_FAILED`。

修正后的判别性场景：`C2-03`（伪造句柄值 65520 → `DUPLICATE_HANDLE_FAILED`）、
`C2-06`（相邻句柄值 +4 → `SECTION_MAP_FAILED`，说明 4 字节对齐的相邻值可能命中另一个有效句柄，
但仍不构成该 section）、`C2-04`（外来句柄值用于自身句柄表 → `SECTION_MAP_FAILED`）。

### 4.2 路线 A 并发场景的丢失更新（lost update）

`probe_e_concurrency.py` 的 route A 用 `delivered[0] += path.stat().st_size` 在 8 个线程里累加交付字节。
该 read-modify-write **不是原子操作**：8 消费者运行时丢失了两次更新，`bytes_delivered` 报
60,774,125 B（正确值 81,032,259 B），而 `errors` 为空、场景仍被判 `PASS`——即**测量本身掩盖了不一致**。

- 修正：改为每个 worker 写入自己的槽位（`delivered[index] = size`）并在 join 后求和；
  同时把 `status` 收紧为“`bytes_delivered` 必须等于 `expected_bytes`”，使同类问题今后必然 FAIL。
- 验证：修正后 `E-A-route-A-consumers-8` 报 81,032,259 B（与期望值精确相等），
  连续两次运行一致。
- 影响范围：仅影响 `probeE` 中 route A 的字节合计与聚合吞吐；其余场景不受影响。

## 5. `BLOCKED` / `NOT_RUN` / `UNVERIFIED` 清单

`BLOCKED`：无。

`NOT_RUN`（原因）：Tauri/WebView 资产协议（本 Task 无 Tauri runtime）；React 消费者与重连（Task 排除）；
真实 Core worker 取消（无产品进程模型）；Core 重启后的引用行为；缓存清理探针；断线重取快照；
冷缓存吞吐（页缓存热）；打包/沙箱形态；模型权重通道；Revision 绑定撤销；
产品 pytest/GUI/IPC runtime（Task 范围要求不运行）。

`UNVERIFIED`：源文件边界的 OS 级 ACL/完整性级别；真实漫画页压缩率下的字节量；
低完整性/跨会话对手的拒绝；命名 section 的显式 security descriptor 方案；
`DuplicateHandle` 在非默认 DACL 下的行为。
