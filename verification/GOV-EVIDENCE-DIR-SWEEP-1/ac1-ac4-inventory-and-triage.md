# AC1–AC4 — 两个来源 Task 的 evidence 目录盘点

**Task**: GOV-EVIDENCE-DIR-SWEEP-1 · **基线**: `3539d8d75` · **授权**: Codex r20 §2.2

## 一、盘点结果

| Task | 目录内文件 | 已登记 | **未登记** |
|---|---:|---:|---:|
| `EXPORT-REVEAL-1` | 12 | 8 | **4** |
| `P15` | 7 | 6 | **1** |
| **合计** | **19** | **14** | **5** |

**全部 19 个文件都已入库**（`git ls-files --others` 返回 0）——
所谓「未登记」是指**未在 Canonical Evidence 表登记**，不是未纳入版本控制。

## 二、逐文件判定（判据是内容，不是文件名）

### `EXPORT-REVEAL-1`

| 文件 | 判定 | 理由（读内容得出） |
|---|---|---|
| `dsh-review-r1.md` | 已登记 | `EXPORT-REVEAL-REVIEW-R1` |
| `frozen-export-attempt.log` | 已登记 | `EXPORT-REVEAL-FROZEN-ATTEMPT` |
| `merge-resolution.md` | 已登记 | `EXPORT-REVEAL-POST-MERGE-RESOLUTION` |
| `post-merge-packaged.log` | 已登记 | `EXPORT-REVEAL-RUST-PACKAGED` |
| `post-merge-python.log` | 已登记 | `EXPORT-REVEAL-CORE-TESTS` |
| `post-merge-source.log` | 已登记 | `EXPORT-REVEAL-ALLOWLIST-REFUSALS` |
| `resource-manifest.json` | 已登记 | `EXPORT-REVEAL-RESOURCES` |
| `reveal-roundtrip-status.md` | 已登记 | `EXPORT-REVEAL-GUI-BLOCK` |
| **`post-merge-packaged-capture-error.log`** | **`REGISTER`** | `error: Unrecognized option: 'A'` / `error: test failed` / **`EXIT_CODE=101`**。**失败尝试的原始记录**，证明该测试非一次通过 |
| **`pytest-core.log`** | **`REGISTER`** | `405 passed, 1 warning` / `EXIT_CODE=0`。对应 Closeout「Core 405 passed」；与已登记的 `post-merge-python.log` 是**合并前后两个阶段** |
| **`rust-packaged.log`** | **`REGISTER`** | `test result: ok. 8 passed; 0 failed` / `EXIT_CODE=0`。对应「packaged sidecar 8 passed」 |
| **`rust-source.log`** | **`REGISTER`** | `test result: ok. 82 passed; 0 failed; 1 ignored` / `EXIT_CODE=0`。对应「Rust source 82 passed / 1 ignored」 |

### `P15`

| 文件 | 判定 | 理由 |
|---|---|---|
| `dsh-review-r1.md` | 已登记 | `E8` |
| `npm-test.log` / `npm-build.log` | 已登记 | `E1` / `E2` |
| `pytest-tests-core.log` | 已登记 | `E3` |
| `cargo-test-source.log` / `cargo-test-packaged.log` | 已登记 | `E4` / `E5` |
| **`cargo-test-unfiltered-first-run.log`** | **`REGISTER`** | `error: test failed` / **`EXIT_CODE=101`**。P15 的 Closeout **明确提到它**：「Owner 保留未过滤首跑的失败日志并**如实命名**为 `cargo-test-unfiltered-first-run.log`（exit 101）」。这是**证据诚实性的正向记录** |

## 三、为什么 5 个全部 `REGISTER`，没有一个 `ARCHIVE`

因为**每一个都有判别力**，而且都能在对应 Task 的 Closeout Record 里找到文字引用：

| 文件 | Closeout 中的对应表述 |
|---|---|
| `pytest-core.log` | 「Core 405 passed」 |
| `rust-source.log` | 「Rust source 82 passed / 1 ignored」 |
| `rust-packaged.log` | 「packaged sidecar 8 passed」 |
| `post-merge-packaged-capture-error.log` | 说明「合并后重跑」之前的那次失败 |
| `cargo-test-unfiltered-first-run.log` | **明确点名**（证据诚实性） |

**两份失败日志尤其重要**：它们证明交付方**保留了失败记录**，而不是只留成功的。
删掉它们会让证据集看起来更干净，但会抹掉「曾经失败过」这个事实。

## 四、登记方式

补登记到各自的 `Canonical Evidence` 表，**用 `SOURCE_PIN` 类**：

- `EXPORT-REVEAL-1`：4 行，commit `4e4d73a0b`（合并后验证阶段）
- `P15`：1 行（`E9`），commit `e5f1a719b`（实现提交）

**为什么用 `SOURCE_PIN` 而不是 `CANONICAL`**：这些是**来源侧的原始运行日志**，
不是本 Task 产生的判别力证据。它们记录某一时刻的字节事实，与其自身的 commit 绑定。

## 五、效果：检查器错误数下降

| Task | 改动前 | 改动后 | 消除的 |
|---|---:|---:|---|
| `EXPORT-REVEAL-1` | **7 errors** | **2 errors** | `evidence_dir 含未登记文件`（4 个文件）+ 4 个 "disposition 无效" 副产物 |
| `P15` | **4 errors** | **2 errors** | `evidence_dir 含未登记文件`（1 个文件） |

**剩余错误全部是既有的，与本 Task 无关**：

| Task | 剩余错误 | 性质 |
|---|---|---|
| `EXPORT-REVEAL-1` | `Evidence SHA-256 不匹配：M2-C1_TYPED_IPC_CONTRACT.md` | **时间性失配**（契约已演进到 rev 2.11）→ 属 `GOV-PIN-LINEAGE-1` |
| `EXPORT-REVEAL-1` | `DONE 不能保留未完成 Acceptance Criteria` | **真实情况**（AC4-③ `BLOCKED`），不是缺陷 |
| `P15` | `Evidence SHA-256 不匹配：SettingsPage.test.tsx` | **时间性失配**（后续提交 `528c6289c` 修改）→ 属 `GOV-PIN-LINEAGE-1` |
| `P15` | `Resource manifest 不存在` | 缺文件 → 属 `GOV-P15-MANIFEST-1` |

**本 Task 只处理「未登记」，不处理 pin 与 manifest**——后两者分别有专门 Task。

## 六、一个实现过程中的错误（如实记录）

第一次运行时，我把 5 行补登记加进了**错误的表**——落到了 `Resource Manifest` 而不是
`Canonical Evidence`。检查器立刻报 4 条 `Resource disposition 无效`。

原因是我用「以 `|` 开头的行」定位最后一行，而这个正则匹配到了 Resource Manifest 段落。

**修正方式**：先把插入范围限定在 `## Canonical Evidence` 与下一个 `## ` 之间，
再取该范围内最后一个 `|` 行。

**这件事本身说明了这条 AC 的价值**：如果我只是「加了几行然后说加好了」，
那 4 条 disposition 错误会留在文件里，而我会以为任务完成了。
**是检查器告诉我加错了表。**

## 七、AC1–AC4 状态

| AC | 结果 | 证据 |
|---|---|---|
| AC1 只读清单 | 达成 | `ac1-ac2-inventory.json`（19 项含 hash）、本文 §一/§二 |
| AC2 逐文件判定 | 达成 | 本文 §二；5 个 `REGISTER`，0 个 `ARCHIVE` |
| AC3 引用核查 | 达成 | 每个 `REGISTER` 都能指向 Closeout Record 的具体表述（§三） |
| AC4 执行移动 | **不适用（0 个 ARCHIVE）** | 无文件需要移动，故未执行任何移动 |

AC5（Handoff + Review）待后续轮次。
