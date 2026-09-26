# M2-RC1 独立 Review — Contract-Aligned Large-Media Resource Channel Runtime

- Task：[M2-RC1](../tasks/M2-RC1.md)（`kind: implementation`，Owner=ZCode）
- Reviewer：DeepSeek Harness（**非作者**；本次实现与证据均由 ZCode 产出，Reviewer 未参与实现）
- 仓库/工作区：`G:/CODEX/New Manga.worktrees/M2-RC1-zcode`
- Branch：`agent/zcode/M2-RC1-large-media-resource-channel-runtime`
- 固定 base：`2dca20cd971e3c2ae1a3ab8134ac0acdf98c45f1`
- **reviewed head：`f8ce10a2784c15dc7ba5ded6989f73ffa3cd5ce0`**（reflog 末行为该 commit，工作区 HEAD 一致）
- delivery head：`395523702a35b0f8a555cf2b58c3ec6df0496908`；Handoff 提交 `f8ce10a2` 在其上
- Contract 固定 blob：`fc35913801297ee1876ea395f9c5041a16226f20`（版本 1.1，§10.1/§10.2）
- 审查日期：2026-09-27
- 报告路径（Reviewer 唯一写路径）：`doc/reviews/M2-RC1-f8ce10a2.md`

## 0. 决定摘要

| 项 | 结论 |
|---|---|
| **决定** | **changes_requested** |
| 阻断项 | `F-01`（P1）：host grant 缓存命中时不再询问 Core，导致 revoke / 到期 / revision 切换对已缓存 URL 不生效，直接违反 T6「立即撤销」与 RC1-AC3 |
| 其余发现 | 1×P1、5×P2、7×P3（详见 §9，含测试覆盖缺口 F-13 与测试工程项 F-14） |
| 复跑 | **BLOCKED**（本审查会话 shell 不可用，见 §2）——未独立复现 35/9/8/10；已核对 Owner 原始日志与产物 |
| 范围 | **PARTIAL**（`git diff` 无法执行）；静态与间接证据全部落在授权路径内，无禁改路径命中 |
| 诚实边界 | **PASS**：S1-B3/B6/B8 NOT_RUN 保留、冷缓存 1 s 未宣称达标、无产品级安全/打包就绪宣称、模型权重未实现 |
| Contract 数值对齐 | **PASS**：T1/T2/T6 常量与握手对象形态逐条一致；错误码族存在 3 项未呈现（`F-07`，P3） |

## 1. 审查方法与工具限制（必须先读）

本会话的 DSH file sandbox 在启动 `pwsh` 时稳定失败：

```text
Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\M2-RC1-zcode)
```

对任何命令、任何 `workdir`（含 `C:\Windows\Temp`）均复现；`sandbox_permissions: danger-full-access` 一次性重试被拒：`requires approval, but no approval channel is available`。因此本 Reviewer **无法执行任何进程**，包括 `git`、`python -m pytest`、`cargo test`、`npm test`、`run_e2e.py`。

替代方法（全部只读文件系统工具：read / glob / grep）：

1. git 事实用**主仓库 reflog 文本**独立取得：`G:/CODEX/New Manga/.git/worktrees/M2-RC1-zcode/logs/HEAD`（9 行，含全部 commit 与 amend 记录）。
2. 范围用 **Owner 的 `git diff --name-status` 转录**（`verification/M2-RC1/final-verification.log` §5）+ 工作区实际文件清点 + `.gitignore` 交叉核对。
3. 语义审查用**逐行阅读实现**：Python Core 4 文件、Rust 3 文件、React 3 文件、4 个测试文件、全部 verification 产物。

**能力边界**：以下结论均为静态/证据审查，不构成运行验证；凡标 `BLOCKED` 的项，解除条件为「在有 shell 且 worktree 可写 ACL 的会话中复跑」。

## 2. 复跑结果（审查要求 2）

| 命令 | 期望 | 本 Reviewer 实测 | 判定 |
|---|---|---|---|
| `python -m pytest tests/m2_resource_channel -q` | 35 passed, exit 0 | 无法执行 | **BLOCKED** |
| `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --locked` | 9 passed, exit 0 | 无法执行 | **BLOCKED** |
| `npm test --prefix apps/desktop/frontend -- --run` | 8 passed, exit 0 | 无法执行 | **BLOCKED** |
| `python verification/M2-RC1/run_e2e.py` | 10/10 PASS, exit 0 ×2 | 无法执行 | **BLOCKED** |
| `git diff --name-status 2dca20cd..f8ce10a2` | 仅授权路径 | 无法执行（替代证据见 §3） | **BLOCKED**（替代证据充分度：高） |
| 工作区洁净度 `git status` | clean | 无法执行 | **BLOCKED** |

Owner 证据的内部一致性核对（Reviewer 可直接验证的部分）：

- `final-verification.log:5` `35 passed, 1 warning in 1.58s` + `exit 0`；`:9` `ok. 9 passed; 0 failed`；`:14` `Tests 8 passed`；四项 exit 0 齐全。
- **测试数量独立可复核**：`grep '^\s*def test_'` 在 `tests/m2_resource_channel/**` 得 **35** 个（`test_service.py` 15 + `test_handle_resolver.py` 12 + `test_bridge_and_thresholds.py` 8），与「35 passed」数量吻合，未被条件跳过的测试会用 `pytest.skip`（`test_handle_resolver.py:114`，junction 创建失败时）。
- **两次端到端逐项一致**：`raw/e2e-results-first.json` 与 `raw/e2e-results-repeat.json` 的 10 条 id/status/observed 逐项相同（唯一差异为 E-06 的两个随机 ID 片段，属预期），全部 `PASS`。
- **SHA 自洽**：`raw/e2e-fixtures.json:5` `asset.sha256=476b6ba1…eaf3 / bytes=49363` 与两轮结果 `:16-17` 的 `sha256` / `expected_sha256` 完全一致；`boundary.sha256=a6d72ac7…6484 / bytes=268435456` 与 E-08 `:72-73` 的 `served=declared=268435456` 一致。生成链可复核：`run_e2e.py:41-43` 直接 `from conftest import write_noise_png`，seed=5101 固定，`raw` 中的 digest 可由该函数确定性重算。
- **独立 node id 佐证**：`.pytest_cache/v/cache/nodeids` 恰含 **35** 条 node id，`.pytest_cache/v/cache/lastfailed` 为 `{}`（该目录被根 `.gitignore:3` 忽略、不随交付携带，但存在于工作区，系 pytest 实际运行过的残留），与「35 passed」的数量及三文件分布（15+12+8）互相印证。
- 结论：**Owner 的原始证据自洽、无内部矛盾**；但「无法由 Reviewer 独立复跑」这一事实必须随 PASS 引用。

## 3. 范围与禁改路径（审查要求 1）

### 3.1 git 事实（reflog 独立取得）

```text
2dca20cd → a0e89f8f → 3948f767 → cd40ef26 →(amend) 7fcc272f →(amend) 991097d7 → 39552370 → f8ce10a2
```

- `f8ce10a2` 提交信息 `docs(M2-RC1): handoff for delivery 39552370`，与 reviewed head 一致；工作区 HEAD 无后续移动/回退记录。
- **991097d7 的 amend 链已被独立证实**（`3948f767..cd40ef26`、`cd40ef26..7fcc272f`、`7fcc272f..991097d7` 两次 amend），与 Handoff 第 19 行「曾误提交 target/ 产物，已在本 head 内 amend 修复」一致。

### 3.2 被审变更清单（`final-verification.log:20-61`，delivery head 991097d7）

41 条路径逐条归类，**全部落在授权路径内**：

| 授权路径 | 条目数 | 抽查结果 |
|---|---:|---|
| `apps/desktop/**` | 22 | `.gitignore` + frontend 9 + src-tauri 8 + `gen/schemas` 4 + `icons/icon.ico` |
| `doc/tasks/M2-RC1.md` | 1 | 自释放 commit 单文件带入（`baseline-selfcheck.md:23` 记录） |
| `src/application/resource_channel/**` | 4 | `__init__`/`dto`/`ports`/`service` |
| `src/infrastructure/resource_channel/**` | 4 | `__init__`/`handle_resolver`/`host_bridge`/`scope` |
| `tests/m2_resource_channel/**` | 4 | `conftest` + 3 test 文件 |
| `verification/M2-RC1/**` | 6（不含日志自身） | baseline-selfcheck / run_e2e / raw×4 |

- **无禁改路径命中**：清单中不存在 `doc/contracts/**`、`src/ui/**`、`src/bootstrap/app.py`、非 resource_channel 的 `src/**`、`packaging/**`、根依赖/锁文件、`doc/AD-001*`、M2-S1/S2/C2/S3 工件、`doc/00_INDEX.md`/`doc/STATUS.md`/`doc/12_ROADMAP.md`/`doc/tasks/README.md`。
- **无构建产物**：清单无任何 `target/**`、`node_modules/**`、`dist/**`、`*.pyc`。交叉核对：`apps/desktop/.gitignore`（`src-tauri/target/`、`frontend/node_modules/`、`frontend/dist/`）与根 `.gitignore`（`__pycache__/`、`*.py[cod]`、`.pytest_cache/`、`dist/`）覆盖了工作区中实际存在的这些未跟踪目录；工作区中确有 `src/application/resource_channel/__pycache__/*.pyc`、`apps/desktop/frontend/node_modules/**`（glob 可见，因 glob 包含 ignore 文件），但均被 ignore 规则覆盖且不在交付清单内。
- `f8ce10a2` 相对 991097d7 只多三个文档提交（`run-log.md`、`final-verification.log`、`doc/handoffs/M2-RC1-39552370.md`；`39552370` 另含 Task AC 回填），三者亦在授权路径内。

### 3.3 判定

**范围：PASS（基于可核实的间接证据）/ NOT_RUN（无条件独立复现），且发现一处文档数字矛盾（F-11）。**

- 用户特别要求复核的「991097d7 最终 diff 无构建产物」：**确认无产物**，依据为 amend 后重跑的 `final-verification.log` 清单 + 修正后的 `.gitignore` + reflog 的时间顺序（日志生成于 amend 之后）。
- 残留不确定：Reviewer 无法排除「工作区存在已跟踪文件的未提交修改」，也无法核对 39552370/f8ce10a2 两个 commit 的完整 diff（两个文档提交本身即 3 个新增文件，预计最终 diff ≈ 44 文件，与此判断无冲突）。

## 4. Contract 对齐（审查要求 3）

| 条款 | 要求 | 实现证据 | 判定 |
|---|---|---|---|
| T1 | 单资源上限 256 MiB；超出类型化拒绝、不部分交付 | `dto.py:18` `MAX_RESOURCE_BYTES = 256*1024*1024`；签发侧 `service.py:109-112` → `RESOURCE_TOO_LARGE`；host 侧 `resource_protocol.rs:35,404-406`；E-09 实测 `RESOURCE_TOO_LARGE` | **PASS** |
| T2 | ≥32 活跃引用、单资源 ≥16 并发订阅者，超限类型化限流 | `dto.py:22,26`；`service.py:143-163`（全局 32）+ `190-206`（订阅计数）；E2E/单测 `test_active_reference_limit`、`test_subscriber_limit_per_resource` | **PASS（实现）/ PARTIAL（测试覆盖）**：「32 个活跃引用 + 第 33 个超限」与 issue 路径的同资源 16 引用上限均未被测试（F-13，P2）；配额语义见 F-09，P3 |
| T3 | ≤25 MiB 热缓存首帧 P95 ≤200 ms；冷缓存 1 s 为目标不得称达标 | `App.tsx:186-201` P95 实测 2 ms；Task:35/60、Handoff:47 明确冷缓存 NOT_RUN | **PARTIAL**（实测 fixture 尺寸不满足「典型页」假设，见 F-04，P2） |
| T4 | 不物化整份资源；常驻缓冲 ≤32 MiB | host 单 chunk 16 MiB（`resource_protocol.rs:34,324`）；Python `read_chunks` 单块 16 MiB（`handle_resolver.py:322,358`）；桥为 control-only（`host_bridge.py:1-21`） | **PASS**，但 `HandleVerifiedFileReader.read()` 会整份物化（F-06，P3，非产品路径） |
| T5.1/T5.2 | WebView 不见 OS 路径；host 解析派生缓存相对路径 | `main.rs:27-42` `IssuedUrl{url,size,opaque_id}`；`client.ts:15-19`；grant 只经 stdio 到 host | **PASS** |
| T5.3 | `user-source` 无前端可见实现、签发即拒 | `dto.py:69` 白名单仅 derived/managed；`service.py:96-99`；`scope.py:34-40`；`resource_protocol.rs:50-56`；测试 `test_user_source_scope_refused_at_issue` | **PASS** |
| T5.4 | WebView 可见引用为不透明映射 ID | `service.py:135-141` `m2id.v1.` + `secrets.token_urlsafe(32)`（256 bit）；`client.test.ts:44-53` 断言无路径/digest/revision | **PASS** |
| T6 | 300 s 滑动 TTL；revision 切换/删除/pin release 立即撤销；在途不中断 | 默认 300 s（`dto.py:29`）、`resolve(renew=True)`/`touch` 续期（`service.py:186-188,216-227`）、`revoke_resource`（`242-263`）、revoke 明确不停在途读（`229-240`） | **FAIL**：Core 语义正确，但 host 缓存使撤销对 WebView 失效（F-01，P1） |
| §10.2 错误码最小集 | 稳定类型化最小集，不泄漏路径/映射表 | `dto.py:72-86` + resolver 家族；`host_bridge.py:112-115`、`resource_protocol.rs:96-114` 只出 code；`leakage-scan.json` CLEAN | **PARTIAL**（3 项未呈现，F-07，P3） |

### 4.1 `probe_config` 下发 digest vs 产品命令面（用户重点核对项）

- 证据机制：`main.rs:76-87` `probe_config` 返回 `fixture_shas`（来自环境变量 `M2RC1_FIXTURES`，`111-130`），页面用它在 E-01 里自证（`App.tsx:124-133`）；仅在证据运行时设置该环境变量。
- 产品命令面：`issue_resource_url`（`main.rs:52-64`）→ `IssuedUrl` 仅 `{url, size, opaque_id}`，**不含 digest/路径/revision**；`into_issued`（`34-42`）刻意不再 resolve 以免滑动续期。
- 端到端两轮结果 JSON 中的 `sha256/expected_sha256` 属证据产物，非调用方可见响应。
- **判定：该区别守得住**（在 `M2RC1_FIXTURES` 未设置的正常运行时 `fixture_shas` 为 `null`）。但探针命令本身仍编译进产品二进制并与产品命令共用一个 invoke 面（F-03，P2）。

## 5. RC1-AC4 句柄序列与双实现一致性（审查要求 4）

静态核对（Python `handle_resolver.py` 与 Rust `resource_protocol.rs`）：

| 序列步骤 | Python | Rust | 一致 |
|---|---|---|---|
| ID/格式门 | `service.resolve` + `dto` | `is_well_formed_id` 43 字符（`resource_protocol.rs:168-173`）先于查表 | ✓ |
| open-once | `_open_read_handle`（`104-122`，`FILE_FLAG_BACKUP_SEMANTICS`） | `open_once`（`293-314`，同 flag） | ✓ |
| containment（句柄推导） | `_final_path_of` + `_normalized` 前缀比较（`291-294`） | `final_path` + `normalized` 前缀比较（`388-394`） | ✓（归一化强度不同，F-08，P3） |
| identity（volume serial + file index） | `_BY_HANDLE_FILE_INFORMATION.identity()`（`83-87,299`） | `RawInfo` 13×DWORD（`184-200,397-400`） | ✓ |
| size + T1 | `301-307` | `401-406` | ✓ |
| 仅经句柄读取 | `_read_all_through` / `read_chunks` | `read_through` / `stream_digest` | ✓ |
| issue-time digest | `_digest_of(data)`（`312`）；`read_chunks` 流式累加（`370-375`） | 首验全量流式 `stream_digest`（`410-418`） | ✓（**频次不同**，F-02，P2） |
| 读后身份复核 | `316-317`、`376-377` | `489-493` | ✓ |
| reparse 处理 | 预打开 walk（`167-187`）+ 句柄属性（`295-296`） | 仅句柄 containment（无 walk、无 reparse 属性检查） | 差异（F-07/F-08，P3；权威防线在句柄层，方向 fail-closed） |
| 窄共享 fail-closed | 默认 `FILE_SHARE_READ`（`110,117-120`），测试 `test_shared_violation_fails_closed` | 恒 `FILE_SHARE_READ`（`299`） | ✓ |
| 宽共享 digest 兜底 | `share_write=True` 可用（`110`），并发测试 `test_in_place_rewrite_during_read_is_caught` | **未实现**（无 `FILE_SHARE_WRITE` 分支） | 差异（P3，见 F-08 注） |

对应 M2-S2 §3/§6：窄共享 fail-closed（`OPEN_FAILED_SHARING_VIOLATION`）与宽共享 digest 兜底（等大小改写 → `CONTENT_DIGEST_MISMATCH`）在 Python adapter 与 pytest 中双向落地；Rust 侧只实现窄共享，但由于 Rust 是产品读取路径，M2-S2 的宽共享可用性取舍**在本切片中未被产品化**（Handoff 第 27 行「窄/宽共享双模式」的描述对 Python adapter 成立，对 Rust 不成立）。

**关键削弱点**：Rust 的 digest 校验只在「该 grant 的第一次请求」执行（`410-418`），此后仅做 identity+size（`495-500` 无条件置 `digest_verified=true`）。因此 T-16/T-18 类「等大小原地改写」在首验之后不再被 digest 捕获 —— 见 F-02。

### 5.1 测试覆盖核对（静态，非复跑）

逐条读取 35 个测试后，AC4 声称的覆盖与实际测试的对应关系：

| AC4/AC3 声称的场景 | 实际测试 | 判定 |
|---|---|---|
| malformed / unknown / revoked / expired ID | unknown/revoked/expired ✓（`test_service.py:81,84,89`）；**malformed ID 未覆盖**（仅「未知 method」`test_bridge_and_thresholds.py:55-58`，`service.py:175-176` 的空 ID 分支无测试） | PARTIAL |
| 范围逃逸（词法 `../`、绝对路径、盘符） | ✓ `test_service.py:47-60`（`C:` 与 `../`）；POSIX `/etc/...` 与 UNC 分支（`service.py:100`）未覆盖 | PASS/部分 |
| reparse/junction 逃逸 | ✓ `test_handle_resolver.py:80-103`（junction，接受 `REF_REPARSE_POINT`/`REF_OUT_OF_SCOPE` 两者）＋ `105-116`（capture 侧）；symlink 未覆盖 | PASS |
| 句柄后同尺寸改写、摘要不匹配 | ✓ `test_handle_resolver.py:65-71`、`155-218` | PASS |
| 共享冲突（窄共享 fail-closed） | ✓ `test_handle_resolver.py:118-141` | PASS |
| 超大资源（T1） | ✓ `test_bridge_and_thresholds.py:92-119`、`test_service.py:62-69` | PASS |
| **只读约束** | **未覆盖**（无断言 `GENERIC_READ`/拒绝写模式；实现见 `handle_resolver.py:111-114`） | **FAIL（覆盖声称不成立）** |
| open-once | **未覆盖**（无 `CreateFileW` 调用计数/单句柄断言） | 未覆盖 |
| 读后身份复核 | **未覆盖**（`handle_resolver.py:316-317,376-377` 无对应测试） | 未覆盖 |
| 宽共享 `share_write=True` 正向可用性 | 仅在并发测试中以可用性前提出现（`test_handle_resolver.py:205`），无「窄共享失败/宽共享成功」对照 | 部分 |
| 在途读取不被 revoke 中断 | **未覆盖**（`service.py:229-234` 仅为 docstring 承诺） | 未覆盖 |
| 默认 300 s TTL、`touch` 续期、pin release | 测试均注入 50/100 s（`test_service.py:91,99`），**默认值/touch/pin release 未覆盖** | 未覆盖 |
| Core 重启旧 ID 不重绑 | ✓ `test_service.py:128-135`（同进程新实例，非真实新进程） | PASS/部分 |

结论：AC4 的**核心句柄序列已被负向测试实质覆盖**（这是本切片最有价值的测试资产），但「只读约束」「open-once」「读后身份复核」「在途不中断」四项为**声称覆盖而实际未覆盖**；另有若干弱断言（析取式接受多个 code、恒真断言）与非 Windows 上 `conftest.py` 模块级 `ctypes.WinDLL` 导致 **collection error 而非 skip**（`test_handle_resolver.py:15` 的 `skipif` 保护不到 conftest 导入）—— 汇总为 F-13/F-14。

## 6. 诚实边界（审查要求 5）

| 项 | 证据 | 判定 |
|---|---|---|
| S1-B3 NOT_RUN | Task:36,61；Handoff:48；run-log.md:57-58；无产品级安全宣称 | **PASS** |
| S1-B6 冷缓存 NOT_RUN、1 s 不得称达标 | Task:35,60；Handoff:47；run-log.md:55-56；Contract §10.1 T3 同样写明 | **PASS** |
| S1-B8 NOT_RUN、不宣称打包就绪 | Task:36；Handoff:49；`tauri.conf.json:27` `bundle.active=false` | **PASS** |
| S1-B5 部分完成表述（重启不重绑已测、密钥生命周期未做） | Handoff:50；`service.py:10-14`；测试 `test_core_restart_never_rebinds_old_ids` | **PASS** |
| S1-B11 产品级防护仍 UNVERIFIED | Handoff:51；`dto.py:3-6`、`handle_resolver.py:14-16` 注释保留 | **PASS** |
| 模型权重通道未实现 | Task:36；Handoff:52；T7 未落任何代码 | **PASS** |
| 无产品级安全/打包就绪宣称 | Task:25,36；Handoff:118；M2-S3「适用边界」原样保留（`M2-S3…:146-172`） | **PASS** |

## 7. Architecture（审查要求 6）

| 维度 | 证据 | 判定 |
|---|---|---|
| 依赖方向 React→Tauri→Python Core | `client.ts` 仅 `invoke` + `fetch`；`main.rs` 通过 `StdioCoreChannel`（`core_bridge.rs:98-129`）spawn sidecar；Reverse 无 Python→Rust | **PASS** |
| 字节不进 JSON/Base64 IPC | `host_bridge.py` 方法集仅 ping/issue/resolve/touch/revoke/revoke_resource/shutdown，响应无字节；host 自行读文件（route A） | **PASS** |
| Core 权威 + host 可信层分工 | Core 拥有 ID 表/TTL/撤销/限额；host 只持有 grant 并做句柄校验读取 | **PASS**（授权语义仍为切片级，F-03） |
| 隔离性（新增模块无产品 import） | `application/resource_channel/*` 仅 stdlib + 自身；`infrastructure/resource_channel/*` 仅 application/resource_channel + stdlib | **PASS** |
| 隔离性（进程级） | `python -m infrastructure.resource_channel.host_bridge` 触发 `src/infrastructure/__init__.py:3` → 产品 `filesystem`/`sqlite`/`domain` 模块导入 | **PARTIAL**（F-05，P2；无 PySide6 依赖、无副作用） |
| 根依赖零改动 | 新 Python 代码仅标准库；`apps/desktop` 使用自有 `Cargo.toml`/`Cargo.lock`/`package.json`/`package-lock.json`（scoped，授权范围内） | **PASS（间接）** |

## 8. 未覆盖风险（Reviewer 未能验证的面）

1. 全部运行时行为（§2 BLOCKED）；尤其 256 MiB 边界、限流、并发、端到端矩阵仅依据 Owner 日志。
2. 无 shell 意味着无法核对 `39552370`/`f8ce10a2` 的完整 diff、无法确认工作区无未提交的已跟踪修改。
3. 真实 WebView2 缓存行为（M2-S3 L-03 的单宿主单样本结论）未在本任务重测；本任务引入的 **host 内部缓存** 是 S3 探针没有的新面（F-01/F-02）。
4. 内存预算（T4）无进程级 RSS 采样（Handoff:119 自认）；本 Review 只能确认缓冲策略，不能确认实测峰值。
5. `gen/schemas/*.json` 为 Tauri 生成物，未核对与 `tauri.conf.json` 的一致性。
6. `frontend/dist` 未检查（构建产物、被 ignore）。
7. 未审查 `apps/desktop/frontend/src/main.tsx`、`index.html` 与 `build.rs` 的细节（非资源通道语义面）。
8. 未验证 `host_bridge.py` 文档承诺的 `fatal` 事件（`host_bridge.py:14`）——实现中不存在该分支，也无测试（F-14）。
9. 未验证 Python `resolve` 在时钟回退下的行为；`test_service.py:101-107` 实际把 clock 从 1000 退到 90，而续期写 `now + ttl`（`service.py:186-187`）会使 `expires_at` 从 1100 缩短为 190（测试注释「near expiry」与事实不符，F-14）。

## 9. Findings

### F-01 [P1] host grant 缓存命中时不询问 Core，撤销/TTL/revision 切换对已缓存 URL 失效

- **文件/行**：`apps/desktop/src-tauri/src/resource_protocol.rs:439-454`（缓存命中直接 `entry.grant.clone()`，不调用 `channel.resolve`）、`:59-67`（`CachedGrant` 无过期/撤销字段）、`:495-500`（请求成功即置 `digest_verified`）；`src-tauri/src/main.rs:164-178`。
- **触发条件**：`issue_resource_url` → 对该 URL 完成任意一次成功 fetch（例如 `?chunk=0`，缓存建立）→ 调用 `revoke_ref` / `revoke_resource_refs`（或 Core 侧 revision 切换/删除/pin release 触发 `revoke_resource`）→ 再次 fetch 同一 URL。
- **影响**：host 返回 `200` 与完整字节，**不返回 `REF_REVOKED`**；TTL 到期同理（缓存命中不触发 Core 侧 resolve）。违反 Contract §10.1 T6「immediate revocation (the next resolve returns a typed `REF_REVOKED`)」的产品语义与 RC1-AC3「revision 切换、删除与 pin release 立即撤销」。Handoff:120「撤销即时性由 resolve 即时性保证」的声称在缓存存在时不成立。对 WebView 而言，短 TTL 提供的「悬挂引用窗口 ≤300 s」保护实际被无限延长（缓存条目从不过期，且无上限）。
- **为何现有证据未发现**：E-04（`App.tsx:152-161`）顺序是 `issue → revoke → fetch`（缓存未命中，走 resolve，因此 PASS）；Rust 单测 `revoked_id_propagates_typed_410`（`main.rs:315-323`）同样是 revoke 先于首次请求。M2-S3 的 L-03「缓存绕过对照」（`M2-S3…:119`）证明的是 WebView2 HTTP 缓存不绕过，其模拟表**每次请求都查表**，与本实现的 host 缓存属不同面。
- **复现（建议的最小用例）**：
  1. Rust 单测：`registered(...)` → `handle_m2res_request(url, …)` 断言 200 → `env.channel.revoke(&opaque)` → `handle_m2res_request(url, …)` 期望 410/`REF_REVOKED`，当前会得到 200。
  2. 端到端：在 `App.tsx` E-04 前先 `fetchAll` 一次 `revocable.url` 再 revoke，观察是否仍 200。
- **建议**：缓存条目记录 `resolved_at` 并在命中时按 TTL 重新 `resolve`（或至少 `touch`）以校验撤销状态；把「续期」与「撤销校验」解耦（可用 `renew=false` 的 resolve）；或由 Core 主动推送撤销。修复后需补两条回归用例（撤销后、过期后、revision 切换后，已缓存 URL 必须类型化拒绝）。

### F-02 [P2] 首验之后不再校验 digest，等大小原地改写可绕过 digest 层；与 Python adapter 语义不一致

- **文件/行**：`resource_protocol.rs:410-418`（仅 `!entry.digest_verified` 时流式校验）、`:495-500`（无条件置 true）；对照 `handle_resolver.py:312`（`read` 每次校验）、`:370-375`（`read_chunks` 每次校验）。
- **触发条件**：首次请求（digest 通过）之后，同用户对手对同一路径做**等大小**原地改写（identity、size 均不变），再请求任一 chunk。
- **影响**：host 返回被改写内容且不做 digest 校验；M2-S2 T-16/T-18 的「digest 兜底」在首验后失效（M2-S2 §7 的 digest 语义「解析到的 == 签发时的」被削弱为「首次解析 == 签发时」）。同时也使 Python/Rust 两处实现的 fail-closed 强度不等价（Python 每次 digest，Rust 只首次）。
- **复现**：单测中先用 `registered()` 请求一次 200，再 `std::fs::write` 等大小改写（保持 file index），再次请求同一 URL，将得到 200 与新内容（当前无 `CONTENT_DIGEST_MISMATCH`）。
- **建议**：把 digest 与缓存有效性绑定（例如记录首验时的 `mtime`/USN 并在变化时重验），或在每次 grant 缓存命中时重验 digest；若坚持首验一次，必须在 Task/Handoff 中显式记录该削弱及其威胁模型，并同步说明与 Python adapter 的差异。

### F-03 [P2] 产品命令面暴露探针命令与 WebView 可控的 catalog 注册（分层信任缺口）

- **文件/行**：`main.rs:44-50`（`register_catalog(resource_id, rel_path)` 由页面提供相对路径）、`:76-104`（`probe_config` / `probe_write_results` / `probe_exit`）、`:179-187`（全部注册进 `invoke_handler`）；`gen/schemas/capabilities.json` = `{}`（无 capability 限制）；`tauri.conf.json:19` `"csp": null`；`App.tsx:121-122,224` 前端确实自行注册 catalog。
- **触发条件**：WebView 内任意 JS 执行（页面脚本、被注入的脚本；CSP 为 null 时风险更高）调用 `register_catalog` + `issue_resource_url`，即可让 Core 为 **scope root 下任意已存在文件**签发引用并读取字节（不受业务授权约束）；`probe_write_results` 可向 `M2RC1_PROBE_OUT` 指定路径或 `%TEMP%\m2rc1-probe-results.json` 写入任意内容；`probe_exit` 可终止应用。
- **影响**：T5 分层信任的意图是「host 可信层持有受限引用、Core 决定授权」，而当前**资源选择权在 WebView 侧**；`catalog` 由 host 注入本身已在 Handoff:120 披露为切片边界，但「前端可直接写 catalog」未披露，属新缺口。证据/产品命令面未隔离，且 `fixture_shas` 通道在产品运行时可被页面探测（无 `M2RC1_FIXTURES` 时为 null）。
- **同一命令面的另两个参数也由 WebView 控制**：`issue_resource_url` 暴露 `ttl_override: Option<f64>`（`main.rs:52-64`，前端探针即用它把 TTL 降到 1 s：`App.tsx:163-168`），因此调用方可传入任意大的 TTL 覆盖 T6 的 300 s 默认；`revision: String`（同处）由前端提供，Core 仅作为不透明字符串存储与撤销匹配（`service.py:113-114,242-263`），不校验其与任何产品 revision 的对应关系。探针用途下合理，但产品面需要把这两个参数收回 Core/host 权威侧。
- **缓解事实**：`bundle.active=false`（不可打包）、本切片明确不宣称产品级安全（S1-B3/B8 NOT_RUN）、scope 白名单排除 `user-source`，因此不构成虚假声明；但作为 runtime 最小切片，命令面应在进入集成前收紧或登记为后续 Task 的前置项。
- **建议**：探针命令以 `#[cfg(debug_assertions)]` 或 Cargo feature 门控，或拆分为独立 evidence 构建；`register_catalog` 移出 WebView 可见面（由 Core/SQLite 权威注入）；为窗口配置 capability/ACL；设置非 null CSP；`probe_write_results` 至少限制在固定证据目录并校验路径。

### F-04 [P2] T3 热缓存 P95 由 49 KB fixture 证明，未覆盖「典型页 ≤25 MiB」

- **文件/行**：`App.tsx:186-201`（复用 `res-probe`/`asset.png`）；`run_e2e.py:43`（`write_noise_png(...,128,128,seed=5101)`）；`raw/e2e-results-first.json:53-67`（`p95_ms=2`，timings 1–2 ms）；`raw/e2e-fixtures.json:5-6`（`bytes=49363`，约 48 KB）。
- **触发条件**：以该证据支撑 T3「≤25 MiB 典型页热缓存首帧 P95 ≤200 ms」的验收线。
- **影响**：AC5 要求的测量对象是「≤25 MiB 页面」，实测对象是 ~48 KB（约为目标尺寸的 0.2%）。2 ms 的结果无法外推到 25 MiB（后者需要跨多个 16 MiB chunk 且受磁盘吞吐影响）。Task/Handoff 的表述（「热缓存 P95≈1 ms（≤200 ms 预算 PASS）」）容易被读作 T3 达标。
- **建议**：用 11.5 MiB（M2-S2 typical fixture）或 25 MiB fixture 复测一次 first-byte-to-host，或在 Task/Handoff 中显式标注「实测尺寸 49,363 B，25 MiB 未测」。

### F-05 [P2] sidecar 启动经 `infrastructure` 包初始化传递性导入产品模块

- **文件/行**：`src/infrastructure/__init__.py:3` `from infrastructure import filesystem, sqlite`（→ `infrastructure/sqlite/__init__.py:3` → `reading_export` → `domain.books.entities` 等）；启动点 `core_bridge.rs:104-114`（`python -m infrastructure.resource_channel.host_bridge`）。
- **触发条件**：任何 sidecar 启动。
- **影响**：RC1 的资源通道进程无法与产品 `domain`/`ports`/`sqlite` 模块解耦；「无产品 import」这一隔离性表述对新增模块自身成立、对进程启动链不成立。当前无 PySide6 依赖、无导入副作用，因此未造成故障；但后续若产品模块引入 GUI 或重依赖，sidecar 将连带受影响。
- **建议**：以独立入口脚本或 `importlib` 直载模块启动 sidecar（不经过 `infrastructure` 包 `__init__`），或在后续 Task 中调整 `src/infrastructure/__init__.py`（本 Task 禁改）。

### F-06 [P3] `HandleVerifiedFileReader.read()` 整份物化资源；`read_chunks` 末段才校验 digest

- **文件/行**：`handle_resolver.py:190-203`（`_read_all_through` 累积全部 chunk 再 `join`，峰值≈2× 资源）、`:276-320`（`read`）、`:322-379`（`read_chunks` 在 `yield` 全部块之后才比对 digest，异常时已交付字节）。
- **影响**：与 T4「不物化完整资源／常驻缓冲 ≤32 MiB」以及 AC2「超限、无效与未授权请求不得部分交付」存在潜在冲突。当前产品读取路径在 Rust（host 先全量 digest 首验再分块服务），Python 这两条路径仅被测试调用，故影响有限；但作为「M2-S2 语义产品化」的 adapter，其内存与部分交付语义应在文档中标注，避免后续被当作产品路径引用。
- **建议**：`read()` 明确标注 test/probe-only；`read_chunks` 若要用于产品，需改为「先验后发」（或首验 + 分块）。

### F-07 [P3] Contract §10.2 错误码最小集存在未呈现项，且未逐条记录豁免理由

- **文件/行**：`dto.py:72-86` 已定义 16 个码；对照 Contract `§10.2`（`M2-C1_TYPED_IPC_CONTRACT.md:292`）的最小集：`REF_READ_ONLY`、`MEDIA_TOO_LARGE_BY_HANDLE`、`REF_SIGNATURE_INVALID` 在实现中**不可达**（无写模式请求、无签名 token 方案、句柄超限时报 `RESOURCE_TOO_LARGE`：`handle_resolver.py:305`、`resource_protocol.rs:405`）；`REF_REPARSE_POINT` 仅 Python 侧可达（`handle_resolver.py:187,258,296`），Rust 侧无对应检查。
- **影响**：Contract 允许 runtime 增加码，但要求「must preserve these semantics」；当前偏差未被 Task/Handoff 逐条说明，集成方难以判断是「架构不适用」还是「遗漏」。
- **建议**：在 Task 或 Handoff 增加错误码对齐矩阵，逐条标注「已实现 / 不适用（理由）/ 后续 Task」。

### F-08 [P3] 双实现细节差异（归一化、reparse 早期层、宽共享模式）

- **文件/行**：`handle_resolver.py:159-164`（`os.path.normpath` + `casefold`）vs `resource_protocol.rs:282-291`（仅小写与分隔符替换，无 `normpath`/8.3 归一化）；Rust 无预打开 reparse walk 与 `FILE_ATTRIBUTE_REPARSE_POINT` 检查；Rust 无 `share_write` 分支（`:293-314`），Python 有（`:110`）。
- **影响**：两处实现在边界输入上的接受/拒绝集合不完全相同（当前方向均为 fail-closed：Rust 更严格地拒绝、Python 多一层早期拒绝）；M2-S2「两种共享模式都是产品取舍、不预选」只被 Python adapter 覆盖，Rust 产品路径固定为窄共享 fail-closed（可能与被占用文件的可访问性取舍有关，但未记录）。
- **建议**：统一路径归一化语义（Rust 增加 `GetFullPathNameW`/`PathCchCanonicalize` 或等价处理）；在文档中记录 Rust 的 reparse/共享策略取舍。

### F-09 [P3] T2 的「订阅者」与「活跃引用」配额语义混用

- **文件/行**：`service.py:143-163`（`_enforce_limits` 用同一资源的**活跃引用数**限制 `MAX_SUBSCRIBERS_PER_RESOURCE`）、`:190-206`（`_Entry.subscribers` 为**每个引用**的计数）。
- **影响**：单资源实际并发订阅上限为 16（满足 T2 下界「≥16」），但两类配额被混用：多引用各 1 订阅与单引用 16 订阅在语义上不可区分，也无 per-resource 订阅者视图。`resolve(renew=True)` 一律使用默认 TTL（忽略签发时的 `ttl_seconds`，`service.py:186-188,227`），探针 TTL 覆盖仅在首次到期窗口生效。
- **建议**：区分「引用配额」与「资源订阅配额」，或在文档中固定当前口径；`resolve` 续期使用条目自身的 TTL。

### F-10 [P3] 缓存无上限、chunk 偏移截断、0 字节资源不可服务、未校验 URL host

- **文件/行**：`resource_protocol.rs:65-67`（`HashMap` 无上限/淘汰）、`:322`（`SetFilePointer(offset as i32)` 无返回值检查；在 T1 256 MiB 内无实际风险）、`:456-463`（`size == 0` 时任何 chunk 都返回 `REF_MALFORMED`）、`:121-148`（未校验 host 是否为 `m2res.localhost`）。
- **影响**：长期运行下缓存可无限增长（内存 DoS 面）；0 字节派生资源无法通过通道交付；其余为健壮性/整洁性缺陷。
- **建议**：为缓存加容量上限与 TTL 淘汰；`size == 0` 特判；`SetFilePointer` 返回值检查；host 白名单校验。

### F-11 [P3] Handoff 声称的变更文件数与证据日志不一致（30 vs 41/44）

- **文件/行**：`doc/handoffs/M2-RC1-39552370.md:21`（「变更路径（30 文件…）」）、`:24`、`:65`（「仅 4 类授权路径（30 文件）」）vs `verification/M2-RC1/final-verification.log:20-61`（**41** 条 `git diff --name-status` 记录，且不含 `run-log.md`/`final-verification.log`/Handoff 自身）；按此推算 f8ce10a2 相对 base 约 **44** 文件。
- **影响**：集成方按「30 文件」核对会被误导；属文档准确性问题，非实现问题。
- **建议**：把 Handoff/Task 中的文件数更正为最终 head 的实际数目（建议在 f8ce10a2 上重跑一次 `git diff --name-status` 并写入证据）。

### F-12 [P3] 证据可复现性与测试保真度细节

- **`leakage-scan.json` 无生成器**：`verification/M2-RC1/` 下仅 `run_e2e.py`，没有生成该扫描的脚本或命令记录；词表仅 8 项、只扫 2 个结果 JSON（不含 `probe-runtime.log`/`fixtures.json`）。
- **runner 门控把 NOT_RUN 视为通过**：`run_e2e.py:141` 只统计 `FAIL`/`MISSING`，而 E-08/E-09 在 `App.tsx:218,230` 有 `NOT_RUN` 兜底 → runner 无法区分「未跑到」与「通过」（本轮 raw 结果确为 10/10 PASS，不受影响）。
- **前端测试 mock 与真实契约不符**：`client.test.ts:8-11` 生成的 ID 为 51 字符且 URL 仍带 `m2id.v1.` 前缀（真实 `build_url` 剥前缀、段长 43），因此该测试无法发现 ID 长度/形态回归。
- **未注册 pytest marker**：`final-verification.log:5` 的 `1 warning` 很可能来自 `test_bridge_and_thresholds.py:92` 的 `@pytest.mark.slow` 未注册（`pytest.ini:1-2` 只有 `testpaths = tests`，无 `markers`/`strict-markers`）；该 mark 不影响默认运行集。
- **conftest 冗余**：`tests/m2_resource_channel/conftest.py:24-28` 重复导入同一类（`ResourceChannelService` 与 `_Svc`）；`layout.small_payload` 动态属性（`:101-102,115`）。
- **建议**：为扫描脚本与 `fixtures.json` 生成过程留命令记录；runner 把 `NOT_RUN` 计入非成功（或在输出中区分）；修正前端 mock 的 ID 形态并断言 `ID_LENGTH`；注册 `slow` marker；清理冗余导入。

### F-13 [P2] AC4/AC3 声称的部分场景实际未被测试覆盖（只读约束、open-once、读后身份复核、T2 真实压力、T6 默认值与 touch/pin release、在途不中断）

- **文件/行**：AC 声称见 `doc/tasks/M2-RC1.md:33-34`；测试实体见 `tests/m2_resource_channel/**`（对标见 §5.1）。具体缺口：
  - 只读约束：无任何测试断言只读打开或写模式拒绝（实现 `handle_resolver.py:111-114`，无 `REF_READ_ONLY` 码）。
  - open-once：无测试统计 `CreateFileW` 次数或断言单句柄（`handle_resolver.py:249,288,336`）。
  - 读后身份复核：`handle_resolver.py:316-317`、`376-377` 无测试触发。
  - T2 真实上限：`test_service.py:139-145` 用 `max_active_references=4`，`155-157` 只断言常量；issue 路径的同资源 16 引用分支（`service.py:154-163`）无测试。
  - T6 默认 300 s / `touch` / pin release / 在途不中断：测试注入 50–100 s TTL（`test_service.py:91,99`），`touch`（`service.py:216-227`）、`revoke_bookkeeping_for`（`265-268`）无测试调用，`service.py:229-234` 的 carve-out 仅 docstring。
- **影响**：AC3/AC4 与 AC5 的 `[x]` 勾选在「覆盖」维度上强于实际证据；回归时这些分支（尤其是 T2 上限与在途 revoke 语义）可能被静默破坏。这属于**证据强度**问题，不否定已实现逻辑本身。
- **建议**：补 6 条测试：①32 个真实引用 + 第 33 个 `RESOURCE_LIMIT_EXCEEDED`；②同资源第 17 个引用被拒；③只读打开断言；④读中 `revoke` 后读取仍完成；⑤`touch` 续期与默认 300 s 断言；⑥pin release 走 `revoke_resource` 的路径断言。或在 Task 中把 AC3/AC4 的覆盖项标注为「部分覆盖」。

### F-14 [P3] 测试与证据工程细节缺陷（可移植性、弱断言、文档与实现不一致）

- **非 Windows 可移植性**：`conftest.py:24-31` 在**模块级**导入 `handle_resolver`，后者在模块级执行 `ctypes.WinDLL("kernel32")`（`handle_resolver.py:54`）；因此非 Windows 上整个 `tests/m2_resource_channel` 会 **collection error**，`test_handle_resolver.py:15` 的 `skipif(os.name != "nt")` 保护不到 conftest 导入。仓库内无 CI workflow 兜底。
- **弱/恒真断言**：`test_handle_resolver.py:101-103`（接受两个 code）、`:150-151`、`:216-218`；`test_bridge_and_thresholds.py:46,77,88`（`"sha256"`/`"PNG"`/`"C:"` 判别力弱）；`:79-88` 的 docstring 声称 WebView 拿不到任何控制面字段，但该响应实际含 `rel_path`+`sha256`（host 为可信层，属预期，只是断言未表达这一点）。
- **文档与实现不一致**：`host_bridge.py:14` 声明 `fatal` 事件，实现中无该分支也无测试。
- **时钟语义**：`test_service.py:101-107` 注释与时钟轨迹不符（见 §8 第 9 项）；`resolve` 续期无条件写 `now + default_ttl`（`service.py:186-187`），时钟回退会缩短窗口、且忽略条目自身 TTL（与 F-09 同源）。
- **证据扫描面**：`raw/leakage-scan.json:3-6` 只扫两个结果 JSON，未扫 `raw/e2e-fixtures.json`（其 `:2` 含宿主绝对路径 `C:\Users\49745\...`，但因非调用方可见面而未被判为泄漏）；扫描词表仅 8 项且无生成脚本（与 F-12 同源）。
- **未注册 mark**：`test_bridge_and_thresholds.py:92` 的 `@pytest.mark.slow` 未在 `pytest.ini` 注册（该文件仅 `testpaths = tests`），即 `final-verification.log:5` 的 `1 warning`。
- **建议**：把 Win32 依赖下沉到 adapter 并对 conftest 做平台守卫；收紧断言为精确 code；删除 `fatal` 文档或实现之；注册 marker；为泄漏扫描补脚本与更宽词表。

## 10. findings_disposition

| ID | 级别 | 处置 | 归属 |
|---|---|---|---|
| F-01 | P1 | **must_fix_before_integration**（或由 Codex 在集成记录中显式接受并把修复升为独立 Task；在此之前不得宣称 T6/AC3 端到端成立） | ZCode（实现）/ Codex（决策） |
| F-02 | P2 | must_fix_or_explicitly_record_before_integration（与 F-01 同源，建议一并修复） | ZCode |
| F-03 | P2 | **should_fix**（命令面门控/ACL/CSP）；可延后但必须登记，且不得在关闭前宣称产品级安全 | ZCode（后续 Task）/ Codex |
| F-04 | P2 | must_retest_or_reword_before_done（补 25 MiB 级热缓存测量或改写表述） | ZCode |
| F-05 | P2 | should_fix（sidecar 启动解耦）；修复需改 `src/infrastructure/__init__.py`，属禁改路径 → 转后续 Task | Codex（范围决策） |
| F-06 | P3 | record_only（在文档中标注 Python adapter 的 test/probe 定位） | ZCode |
| F-07 | P3 | must_record（补错误码对齐矩阵） | ZCode |
| F-08 | P3 | record_only / 后续 Task | Codex |
| F-09 | P3 | record_only（文档固定口径） | ZCode |
| F-10 | P3 | record_only / 后续 hardening | ZCode |
| F-11 | P3 | must_record（更正文件数并附最终 diff 证据） | ZCode |
| F-12 | P3 | should_fix（证据可复现性与测试保真度） | ZCode |
| F-13 | P2 | must_record_or_fix（补 T2/T6/只读/open-once/读后复核/在途 六类测试，或把 AC3/AC4 覆盖项降级为「部分覆盖」） | ZCode |
| F-14 | P3 | should_fix（测试工程与文档一致性） | ZCode |

## 11. 复验清单（变更后由 Reviewer 或集成方执行）

1. 在有 shell 的会话中复跑四条命令（§2），确认 35 / 9 / 8 / 10 与 exit 0。
2. 新增并通过：`fetch → revoke → fetch` 必须得到 `REF_REVOKED`（Rust 单测 + 端到端各一条）。
3. 新增并通过：首验后等大小原地改写 → 第二次请求必须类型化拒绝（`CONTENT_DIGEST_MISMATCH`）。
4. 补 T3 尺寸测量（≥11.5 MiB fixture 或明确改写表述）。
5. 更正 Handoff/Task 的文件数与本 head 的 `git diff --name-status` 证据。
6. 由范围审查者执行 `git diff --name-status 2dca20cd..<new head>` 与 `git diff --check`，确认仍无禁改路径与构建产物。
7. 按 F-13 补齐六类测试（T2 真实上限、同资源引用上限、只读、open-once、读后身份复核、在途 revoke、默认 300 s/touch/pin release），或把 AC3/AC4 的对应覆盖项降级为「部分覆盖」并记录。

## 12. 结论

本交付在**静态语义层面**与 Contract 1.1 §10 高度对齐：T1/T2/T5/T6 的常量与分层信任形态正确，AC4 的 open-once→containment→identity→size→digest→读后复核序列在 Python 与 Rust 两侧的代码中都真实存在（测试覆盖缺口见 F-13），字节确实停留在 host 侧而不进入 JSON/Base64，诚实边界（S1-B3/B5/B6/B8、模型权重、产品级安全与打包就绪）保留完整、无夸大宣称。证据自洽（fixture SHA、两轮一致性、泄漏扫描）且 amend 后的 diff 无构建产物。

但 F-01 是一个会影响 **RC1-AC3/T6 端到端语义**的真实缺陷：host 侧的 grant 缓存使「立即撤销」只对未缓存的引用生效，而现有 E-04/单测的调用顺序恰好绕过了这一窗口；F-02 使 digest 兜底在首验后失效（同一缓存机制）。此外 F-13 显示 AC3/AC4 的覆盖勾选强于实际测试（只读约束、open-once、读后身份复核、T2 真实上限、在途不中断等未覆盖），F-04/F-11 是证据与表述的准确性问题。因此本 Review 的决定为 **changes_requested**：请 Owner 修复 F-01（以及同源的 F-02），补齐或降级 F-13 的覆盖项，并处理 F-04、F-11 的证据/表述问题；F-03/F-05 可作为后续 Task，但在关闭前不得宣称产品级安全或打包就绪。修复后由本次 Reviewer 或 Codex 指定的非作者复核 §11 清单即可转 approve。

---

Reviewer：DeepSeek Harness（非作者）｜reviewed head `f8ce10a2`｜决定 **changes_requested**｜findings：1×P1、5×P2、7×P3
