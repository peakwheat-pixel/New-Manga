我已用 read 工具逐份读取全部固定对象。以下为纯文档内容 Review，本会话未运行任何命令、未做任何测量、未修改任何文件。

---

# P02 AppContainer r6 / Phase A manifest 独立内容 Review（DSH 非作者）

## 1. 审查对象与 object_binding

| 对象 | 实际读取形态 | object_binding |
|---|---|---|
| `doc/tasks/P02.md` | 全文 386 行 | 见下 |
| `verification/P02/appcontainer-isolation-contract-r6.md` | 全文 177 行 | 见下 |
| `verification/P02/appcontainer-readonly-preflight-r2.md` | 全文 47 行 | 见下 |
| `verification/P02/dsh-appcontainer-contract-r5-review.stdout.md` | 全文 169 行 | 见下 |
| `verification/P02/codex-appcontainer-contract-r5-adjudication.md` | 全文 43 行 | 见下 |

- 五个固定路径均存在且可读，**未出现缺失或实质内容不可读**的情况。
- **`object_binding = NOT_VERIFIED`**：本会话不具备且被禁止使用 shell/PowerShell/Git/Windows API，未复算任何 SHA-256/字节数，未读取 `.git`，未核验 `main@cddff58469b56e181019a8ddfeade80684bc7eb9` / `tree=c25d051a4b9a0bd9773b50170e100f575ea19f2b`，也未验证派发值（Task `F23FF5…40D3`、contract `A7ED63…0C49`、manifest r2 `FD7C6A…7828`、r5 报告 `95F747…2C63`、r5 adjudication `9FBA6D…753C`）。本报告全部结论只绑定“本会话用 read 工具实际读到的前述路径内容（行数与文本）”，**不是 exact-object hash Review**。
- 按项目先例，`object_binding=NOT_VERIFIED`（不可核验 ≠ mismatch）不单独否定内容结论，但本轮 Review 不能充当 exact-object 通过凭证。

## 2. 内容 Decision

**`CHANGES_REQUESTED`**（内容层）。正式整体结论：**`NOT_VERIFIED`**（因 object_binding 未建立）。

判定口径：r5 的 R5C-01..09 在 r6/manifest r2/Task 中**均有可指认的落地修订**，未发现“只写在 adjudication 自述里”的空头修正；但 Phase A 执行细则仍有两项 P2 歧义（WER 采样作用域、环境变量子集口径），在这些消歧前不能把 manifest r2 当作“无歧义可执行清单”。

## 3. P0/P1/P2/P3 计数与全部 open finding

| 严重度 | 数量 | 编号 |
|---|---|---|
| P0 | 0 | — |
| P1 | 0 | — |
| P2 | 2 | DSH-R6A-01、DSH-R6A-02 |
| P3 | 10 | DSH-R6A-03 … DSH-R6A-12 |
| 合计 | 12 | 全部 open |

（编号避开历史 `F-xx`/`G-xx`/`H-xx`/`R4-xx`/`R5-xx`/`R5C-xx`/`R1-xx`/`R9F-xx` 命名空间。）

### P2

**DSH-R6A-01（P2）— WER T0/T1 的作用域与相对触发点仍未无歧义**

- 依据：contract r6 `:35`（§1.1.8“在只读 preflight **前后**记录 …存在性及文件名/长度/last-write time/file ID”）、r6 `:44`（§1.2“**读取前后各一次**的 WER 快照”）；manifest r2 `:21-22`（“在**其他 Phase A 读取开始前**立即采集一次 WER 快照 T0，在**所有读取完成后**立即以相同范围再采一次 T1”）、“相同范围”未定义；manifest `:36-37`（§命令和证据边界只约束“测量期间不写 evidence”，未说明 T1 是否必须在测量进程仍存活时采集）。
- 冲突点：(a)“相同范围”究竟是 r6 §1.1.8 的 3 个目录，还是 manifest `:23-27` 的 2 个 registry 键 + 3 个目录；(b) T0 是在 12 输入根 4 scratch 根根元数据读取之前，还是仅在其他读取之前，措辞按执行顺序不同会得到不同基线；(c) T1 若在进程退出后由 Codex 另行采集，则“新直接子项 → UNKNOWN/BLOCKED”的因果链不再属于同一次测量。
- 最小修正：在 manifest 明确写出“T0 = 本清单全部读取（含 5 项 WER 对象）开始前；T1 = 同一测量进程内、全部读取结束后、进程退出前；两次均覆盖 §:23-27 全部 5 项对象”，并与 r6 §1.1.8/§1.2 用同一词。

**DSH-R6A-02（P2）— Phase A 环境变量集合与 r6 §6 环境表的关系未声明显式**

- 依据：r6 `:121`（“未列变量不设置”）、`:123-141`（环境表，含 `PYTHONPYCACHEPREFIX`、`PYTHONDONTWRITEBYTECODE`、`HF_ASSETS_CACHE`、`HF_XET_CACHE`、`HF_TOKEN_PATH`、`HF_HUB_DISABLE_IMPLICIT_TOKEN`、`HF_HOME`/`HF_HUB_CACHE` 之外的 HF 变量等）、`:156`（Phase B 须逐项列 exact path/API/允许字段）；r6 `:44`（§1.2 只写“**列明的** controller 环境变量”）；manifest r2 `:19`（Phase A 只读 24 个具名变量，其中 `HF_ASSETS_CACHE`/`HF_XET_CACHE`/`PYTHONPYCACHEPREFIX`/`PYTHONDONTWRITEBYTECODE`/`HF_TOKEN_PATH`/`HF_HUB_DISABLE_IMPLICIT_TOKEN` **不在** 24 项内）。
- 影响：manifest r2 既未声明“24 项即 Phase A 全集、其余 r6 §6 变量属 Phase B”，也未声明“§:19 仅为子集且不构成完整 cache 闭包证据”；结合 r6 `:143`（“变量只作重定向，不替代动态写入闭包”）虽不产生错误结论，但执行者可能误读 Phase A 环境读取为 r6 §6 的穷尽核对，或反过来在结果中漏登未列变量的 UNKNOWN 状态。
- 最小修正：在 manifest `:19` 末句加入“本集合为 Phase A 全集；r6 §6 中未列出的映射变量一律 `NOT_RUN / Phase B`，Phase A 结果不构成 cache 重定向闭包证据”。

### P3

**DSH-R6A-03（P3）— `TRITON_CACHE_DIR` 环境表登记仍不具名**
- 依据：r6 `:97`（`python-cache/` 行“Python/Torch/HF/**Triton** cache variables，包括 TRITON_CACHE_DIR 映射到 python-cache/triton”）对合同 §6 表而言仍是泛称类别；manifest `:19` 却已把 `TRITON_CACHE_DIR` 作为精确逐项变量读取。
- 影响：R5C-06 的“登记”只落在行内注解；若 Phase A 结果按“是否符合本清单声明的宿主/路径类别”逐变量输出，`TRITON_CACHE_DIR` 需要一个确定的类别标签，否则会出现无类别的裸值。
- 最小修正：在 r6 §6 表中把 `TRITON_CACHE_DIR` 单独成行，映射 `scratch python-cache/triton`。

**DSH-R6A-04（P3）— manifest `:19` 的 REDACTED 谓词与“类别归类”要求互相牵引**
- 依据：manifest `:19`（“只报告每个值是否符合本清单声明的宿主/路径类别；若值位于用户私密路径，仅记 REDACTED / UNKNOWN”）。
- 影响：“类别”与“私密路径”未定义判定标准（属于用户目录 = 私密？`C:\Users\49745\AppData\Local\Programs\Python\Python312` 是否算用户私密路径），执行者可能对同一变量给出不同处置，或把原值写入 stdout。
- 最小修正：明确类别枚举（`HOST_SYSTEM` / `USER_PRIVATE` / `SCRATCH_EXPECTED` / `UNDETERMINED`），并规定输出**只写类别标签**、任何情形不落原值。

**DSH-R6A-05（P3）— manifest 未声明“额外变量一律不读取”的延迟规则**
- 依据：r6 `:155`（Phase A 严格按 manifest 执行，“不得…创建文件或目录，不运行写 probe 或工具链”）、`:156`（Phase B 逐项冻结）。
- 最小修正：在 manifest §Phase A 允许读取末尾加入“本清单未列出的任何变量、路径、字段一律不读取并保持 `NOT_RUN`，扩展项须走 Phase B 清单”。

**DSH-R6A-06（P3）— 悬空交叉引用：r6 `:34` 的“§4.5”**
- 依据：r6 `:34` 写“仅 **§4.5** 列出的精确 leaf 可按各自权限使用”；但该契约 §4 只有编号约束 1–5（`:106-110`），**不存在 §4.5 小节**；三条 leaf 实际定义在 §4 表（`:99-102`）与 §4 约束 5（`:110`）。
- 影响：与 R5C-04 同源的“引用完整性”缺陷，执行者按 §4.5 检索会落空。
- 最小修正：改为“§4 scratch 表与 §4 约束 5 列出的三条精确 leaf”。

**DSH-R6A-07（P3）— r6 `:15` 的 ACL/Low label 授权句与“当前 Gate 状态”之间缺显式入口条件**
- 依据：r6 `:15`（“只有相关 Review、只读预检与后续 Gate 均明确放行后，才可对这些输出叶子…设置必要的 Package SID DACL ACE 与 Low mandatory label”）与 `:8`（当前状态表：`OS isolation preflight=NOT_RUN`、`Build Gate=BLOCKED`）并列，但 `:8` 未给出该写入路径的显式准入 token。
- 影响：读者可能把 `:15` 读作已存在的许可路径，而 `:8` 只列“只读”类状态 token（R5C-05 的机读比对场景正是逐 token 核对）。
- 最小修正：在 `:8` 增补 `scratch ACL/label mutation=AUTHORIZATION_PATH_DEFINED / NOT_APPROVED`（或等价 token），使 `:15` 的“均明确放行”有可机读锚点。

**DSH-R6A-08（P3）— r6 §4“既有内容清单 / 根元数据”措辞可再收紧**
- 依据：r6 `:83`（“output-root 安全快照**和既有内容清单**属于 Phase B”）、`:81`（“Phase A 仅依 manifest 对固定根路径**取根目录元数据**”）与 manifest `:12`（“读取**根目录元数据**…不得递归、枚举子项”）。
- 影响：三处语义一致（清单=Phase B，Phase A 只取根元数据），但“既有内容清单”与“根元数据”两个词在 r6 内未互指，易被读成 Phase A 的根元数据包含内容清单。
- 最小修正：在 `:83` 加“（即根元数据以外的子项/内容信息一律 Phase B）”。

**DSH-R6A-09（P3）— r6 §4 scratch 表的路径前缀未在表内声明**
- 依据：r6 `:85-102`/`:99` 全为相对路径（`apps/desktop/frontend/node_modules/`、`verification/P02/tmp/` 等），`":81"` 仅以“Scratch clone”泛指；绝对前缀只在 manifest `:14-17` 出现（`G:\CODEX\P02-scratch-build-source\...`）。
- 最小修正：在 §4 表标题加“所有相对路径均相对 `G:\CODEX\P02-scratch-build-source`；主仓对应目录保持 deny”。

**DSH-R6A-10（P3）— “四个 scratch 根”未在 manifest 内命名**
- 依据：r6 `:44`/manifest `:12` 均写“12 个输入根 + **四个**精确 scratch 目录”，manifest `:14-17` 逐条列出但未称作“四个 scratch 根”。
- 最小修正：在 manifest `:12` 后加“（下列 4 条即四个 scratch 根）”，使机读枚举与散文标题可对应。

**DSH-R6A-11（P3）— r6 §1.1.9 的 exclusion manifest 适用性未声明**
- 依据：r6 `:36`（“任何保护文件 digest 前，先建立 `verification/P02/appcontainer-preflight-exclusions-r1.json`…”）仍为“任何”，manifest `:31` 已明确 Phase A“不哈希文件”、`:45` 说明 Phase A 不产生受保护文件前后 hash。
- 最小修正：在 r6 加一句“Phase A 不执行任何受保护文件 digest，故 §1.1.9 的 exclusion manifest 在 Phase A 不适用；其创建与冻结属 Phase B/后续 Gate”。

**DSH-R6A-12（P3）— manifest 的“不哈希”限定词可加严**
- 依据：manifest `:12`（“不得递归、枚举子项、**打开或哈希普通文件**”）与 `:31`（“不哈希文件”）用词不完全一致，“普通文件”这一限定词为理论上的例外留了口子。
- 最小修正：统一为“不得打开或哈希任何文件”。

## 4. R5C-01..09 逐项 CLOSED / OPEN 判断（只认文档实际条文，不采信 adjudication 自述）

| Finding | 判定 | 实际落点（本次读取的行号） |
|---|---|---|
| R5C-01（P1）契约/manifest 首轮范围不一致、P1-02 出口不可达 | **CLOSED** | r6 `:5`（授权范围“限于 Codex-only 隔离预检（执行前置见 §8.1）”）、`:42-46`（新增 §1.2 Phase A/B 边界：Phase A 仅 controller 身份/token 字段、12 输入根+4 scratch 目录根元数据、列明环境变量、WER 前后各一次；明确排除文件内容/hash、子进程、profile、private registry、系统 loader/runtime ACL、output-root 内容与安全描述符、Git/clone pins）、`:77`（系统文件 DACL 与 `S-1-15-2-2` ACE 核对属 Phase B、P1-02 继续 BLOCKED）、`:81`/`:83`（clone pins、output-root 快照归 Phase B）、`:155`（Phase A 不能解除 P1-01、P1-02 或 Build Gate）、`:177`（P1-02 出口条件已同步为“只有 Phase B 证据或其他已证实 blocker 才能支持”）。R5C-01 点名的四处冲突条文（r5 `:71/:46/:97/:147`）在 r6 均已被改写或收窄，未发现残留的 Phase A 现在时越界指令。 |
| R5C-02（P2）Task 行号引用失效 | **CLOSED** | r6 `:22`、`:100`、`:158` 已全部改用稳定语义锚点（“P02 Task 中‘Smoke 的只读 canary alias’段落语义继续有效”“P02 Task‘Smoke 的只读 canary alias’”），全文未再出现 `Task:79`/`Task:81` 类行号引用；Task 侧 `P02.md:95` 保留原文段落与之对应。 |
| R5C-03（P2）未精确标识本轮清单 | **CLOSED** | r6 `:155` 首次给出“verification/P02/appcontainer-readonly-preflight-r2.md，SHA-256=FD7C6AAB…7828”；`P02.md:85` 同步给出路径+SHA，`:87` 要求固定 P02 Task SHA 一并派发。契约内现已自证“本轮清单”唯一。 |
| R5C-04（P3）§4 表缺三条 leaf 行 | **CLOSED** | r6 `:99-102` 逐行列出 `verification/P02/tmp/`（父目录不授写权）与三条 leaf：`smoke-readonly-probe/`（不授 Package SID 写 ACE/不改 label，写成功即 BLOCKED）、`lpac-write-control/`（正向 canary，Phase B Gate 放行后仅新增一个唯一文件）、`lpac-write-deny-control/`（负向 DACL control，不授 ACE/不改 label）。§4 约束 3/5（`:108`、`:110`）再次逐条独立声明策略。 |
| R5C-05（P3）状态 token 不统一 | **CLOSED** | r6 `:8` 采用 `private_registry_absence=UNPROVABLE / BLOCKED`、`profile=NOT_CREATED`、`ACL/registry=NOT_MODIFIED`、`OS isolation preflight=NOT_RUN`、`hook/cache/child-process closure=BLOCKED / NOT_VERIFIED`、`Build Gate=BLOCKED`、`build=NOT_AUTHORIZED / NOT_RUN`、`Hard Build Barrier=EFFECTIVE`、`AC1–AC7=BLOCKED / NOT_RUN`；与 `P02.md:86`、manifest `:4`/`:47` 逐 token 一致（Task 另在 `:70`/`:76`/`:117` 等处使用同一命名）。 |
| R5C-06（P3）Triton 变量与 WER 前后采样 | **CLOSED（附 DSH-R6A-03）** | r6 `:97` 已出现 `TRITON_CACHE_DIR`（含映射 `python-cache/triton`）；manifest `:19` 精确逐项读取；WER 前后两次采样见 r6 `:35`/`:44` 与 manifest `:21-22`。变量未单独成行属登记精度问题，不构成未修正。 |
| R5C-07（P3）Task 保留 r4 现在时待审状态 | **CLOSED** | `P02.md:124-126` 已改为“### 历史记录：2026-10-10 r4 AppContainer contract follow-up（已被 r5 Review 取代）”，并写明“r4 不再是当前候选，也不是 Gate 凭证”；`:72` 段标为“历史快照”；`:82-87` 记录 r5 已完成、r6 为当前候选。 |
| R5C-08（P3）`profile root`/`profile 树` 术语残留 | **CLOSED** | 本次通读 r6 全文，仅出现 `profile directory`、`local-data directory`、`private registry storage`（如 `:38`、`:52`、`:56`、`:125`、`:158`、`:159`），未再发现 `profile root` 或 `profile 树`。 |
| R5C-09（P3）授权句与执行前置字面张力 | **CLOSED** | r6 `:5`（“本契约定义的授权范围限于 Codex-only 隔离预检（执行前置见 §8.1），不扩大产品 AC、Owner allowlist 或输出 allowlist”）、`:12`（授权“是执行范围许可，不是 Review、测试、预检或 Gate 凭证”）、`:155`（“只有 DSH r6 内容 Review 完成且 Codex adjudicate 后，才可严格按该 manifest 执行”）。 |

**重点项复核（三项继续成立，且文档内无互相矛盾）**：private registry 创建前不存在性保持 `UNPROVABLE / BLOCKED`（r6 `:28`、`:52`、`:156`、`:158`）；`GetAppContainerRegistryLocation` 被明确禁止（r6 `:54`“本 Task 禁止调用”，`:52`，manifest `:31`）；profile 继续不得创建（r6 `:52`、`:53`、manifest `:31`）。三者均未被任何 Phase A 只读读取授权解除。

## 5. 需求 3：Phase A 排除面确认

对照 manifest `:31-33` 与 r6 `:18`、`:42-46`、`:77`、`:81-83`、`:155-156`，**逐项确认 Phase A 明确排除**：

1. **system loader/runtime DACL**（含 `S-1-15-2-2` ACE 核对）— 排除，保持 `NOT_RUN`，P1-02 续 `BLOCKED`（r6 `:77`）。
2. **moniker / profile / local-data directory 状态** — 排除，保持 `UNKNOWN / BLOCKED`（r6 `:46`、`:52`、manifest `:31`）。
3. **scratch output-root security/content inventory** — 排除，`Phase A 仅取固定根路径根元数据`（r6 `:81`、`:83`）。
4. **Git / worktree / clone pins** — 排除，保持 `UNKNOWN / NOT_RUN`（r6 `:44`、`:81`、manifest `:31`）。
5. **所有 profile / private-registry API**（`CreateAppContainerProfile`、`DeleteAppContainerProfile`、`GetAppContainerRegistryLocation`、`GetAppContainerFolderPath`，及派生/创建/复用 profile）— 排除（r6 `:52`、`:54`；manifest `:31`）。
6. **写探针** — 排除（r6 `:38`“不运行写探针或 MIC 探针”；manifest `:31`、`:33`）。
7. **ACL/registry 修改** — 排除（r6 `:18` 零 ACL/label 修改范围；manifest `:33`；`:8` `ACL/registry=NOT_MODIFIED`）。
8. **工具链 / build** — 排除（r6 `:20` 不授权 Cargo/Tauri/PyInstaller/Smoke；`:155` 不运行工具链；manifest `:31`）。
9. **Windows Sandbox**（查询/安装/启用/启动）— 排除（r6 `:20`；manifest `:33`；`P02.md:58-62` 本机验证裁决 §）。

结论：该要求**满足**，未发现 Phase A 残留的越界现在时指令。

## 6. 需求 4：Phase B 前置条件清晰度

- **清晰**：r6 `:156` 明列“系统 loader/runtime DACL、moniker/profile/local-data-directory 状态、output-root 安全快照和许可的 inventory、Git porcelain/worktree/source pins 与 clone pins 均排除于 Phase A”，并要求 Phase B **逐项列明 exact path/object、读取 API、允许字段、证据文件、隐私处理及 `UNKNOWN/BLOCKED` 判据**，且“须完成非作者 Review 与 Codex adjudication”。
- **清晰**：r6 `:46` 补充“在此之前…均保持 `UNKNOWN / BLOCKED / NOT_RUN`”“Phase A 不会使这些检查变为可达或默认获准”；`:156` 明确“本契约当前没有授权任何 profile API”；`:177` 明确“Phase A 不会自动开始 Phase B”。
- **清晰**：Phase A **不可**解开 `P1-01`（r6 `:28`、`:52`）、`P1-02`（r6 `:77`、`:177`）、`Build Gate`/`Hard Build Barrier`（r6 `:155`、`:160`、`:176`）；`:155` 明确“Phase A 不能解除 P1-01、P1-02 或改变 Build Gate”。
- 两处清单字段集合表述略有差异（r6 `:46` 用“独立冻结 manifest 中列出的精确路径与方法”，`:156` 用 6 字段清单），属可合并的详略差；建议在 §8.2 复述 §1.2 的完整字段集合，但不构成阻断。

## 7. 需求 5：历史 r4/r5 Task 状态与用户授权定位

- r4 段落已标为历史（`P02.md:124-126`），r5 已完成并记录（`:82-87`），r6/manifest r2 标为“候选，不是 Review PASS”（`:85`）。
- 用户授权定位正确、未被写成 Gate 凭证：`P02.md:70`（“授权是 scope 许可，不是测试或 Gate 通过凭证”）、`:87`（“用户授权仅为范围授权，不是 Gate/测试凭证”）；r6 `:12`、manifest `:5` 同义。
- 未发现把用户授权写成 Review/测试/Gate 凭证的条文。

## 8. 需求 6：scratch leaf / 环境 / WER / 状态 token / 稳定锚点核对

- **三条 scratch leaf**：权限行已逐条落地且策略互不重叠（r6 `:99-102`、约束 3/5 `:108`/`:110`；manifest `:14-17`）。仅 `r6:34` 的“§4.5”为悬空引用 → **DSH-R6A-06**。
- **`TRITON_CACHE_DIR`**：manifest 精确具名；r6 环境表仍为泛称类别 → **DSH-R6A-03**。
- **WER 采样**：T0/T1 两次同范围已写入 → 但作用域/触发点仍有歧义 → **DSH-R6A-01**；与 exclusion manifest 的适用性 → **DSH-R6A-11**。
- **状态 token**：r6/`P02.md`/manifest 三处逐 token 一致（见 R5C-05 判定）。唯一可增补项是 ACL/label 写入路径的显式准入 token → **DSH-R6A-07**。
- **稳定 Task 语义锚点**：`P02.md:95` 段落 ↔ r6 `:22`/`:100`/`:158` 引用一致；clone 基线 pin `7ce3c40…`/`ce8056b8…` 在 `P02.md:88` 与 r6 `:81` 一致。

## 9. 是否允许进入本轮 Phase A

**否——当前不允许。** 全部前置条件：

1. **本 Review 已完成**（内容层 `CHANGES_REQUESTED`，12 项 open），按 r6 `:155` 尚不满足“内容 Review 完成且 Codex adjudicate 后”的完整条件。
2. **Codex 必须逐项 adjudicate** DSH-R6A-01..12，并对每项给出接受/驳回/延期的显式处置（r6 `:176`）。
3. **任何修订都会改变 r6/manifest r2/Task 字节**，必须重新固定 SHA-256、重新绑定对象关系，并按项目惯例确认是否另派只读复审；不得沿用 `A7ED63…0C49` / `FD7C6A…7828` / `F23FF5…40D3` 作为修订后对象的 pin。
4. **`object_binding` 必须另行建立**：本轮为 `NOT_VERIFIED`，内容层通过不等于 exact-object 通过；修订后的新候选若仍以本会话方式审查，将同样只有 `object_binding=NOT_VERIFIED`。
5. 执行时不得调用任何 profile/private-registry API、不得创建 profile、不得修改 ACL/label/registry、不得创建文件或目录、不得运行写探针/工具链/build/Sandbox（r6 `:155`、`:20`；manifest `:31-33`）。
6. 即便 Phase A 全部执行完成，也不得据此解除 `private_registry_absence=UNPROVABLE / BLOCKED`、`P1-01`、`P1-02` 或 `Hard Build Barrier`。

## 10. 当前 Gate 状态（本次 Review 未改变任何 Gate）

`private_registry_absence=UNPROVABLE / BLOCKED`；`profile=NOT_CREATED`；`ACL/registry=NOT_MODIFIED`；`OS isolation preflight=NOT_RUN`；`hook/cache/child-process closure=BLOCKED / NOT_VERIFIED`；`Build Gate=BLOCKED`；`build=NOT_AUTHORIZED / NOT_RUN`；`Hard Build Barrier=EFFECTIVE`；`AC1–AC7=BLOCKED / NOT_RUN`。

**本轮 Review 不构成**：profile 创建或复用许可、ACL/label/registry 修改许可、OS isolation preflight/PASS、Smoke、build、AC1–AC7 的任何批准，也不解除 Hard Build Barrier；不宣称任何运行时或隔离 Gate 通过。三项控制（`smoke-readonly-probe/`、`lpac-write-control/`、`lpac-write-deny-control/`）本轮均为 `NOT_RUN`。

## 11. 边界声明（本 Review 不能证明的内容）

1. 本会话**未运行** shell、PowerShell、Git、Windows API 或任何系统 measurement；未做 OS measurement；未创建/复用 profile；未访问或修改 private registry；未修改 ACL/label/owner/policy；未运行 probe、写探针、MIC 探针、工具链、build、Cargo、Tauri、PyInstaller、Smoke、GUI 或 Windows Sandbox；未提权、未 take ownership、未联网。
2. 本会话**未修改、创建或删除任何文件**；未落盘 Review 报告，全文仅存在于本次对话输出。
3. 未复算任何 SHA-256、字节数或 Git 对象 → `object_binding=NOT_VERIFIED`；本报告**不是** exact-object hash Review，不因派发 prompt 或 Codex adjudication 给出的 SHA 声明而改称已绑定对象。
4. 未联网核对 r6 §9 引用的 Microsoft 一手页面，对 `S-1-15-2-2`、`GetAppContainerRegistryLocation` absent-state 等外部事实只做文档内部一致性审查。
5. 未独立回溯 r2/r3 契约与 r2/r3/r4 DSH 报告原文；R5C-01..09 的判定基于本轮实际读到的 r5 报告、r5 adjudication、r6 契约、manifest r2 与 Task 文本。
6. 未做任何本机路径存在性/形态测量；manifest `:14-17` 与 r6 §3 的 12 个输入根仅按文档字面确认。

## 12. 推荐下一步（单一可转发指令）

> 请 **Codex（Integrator/Gate owner）** 对 r6 契约、manifest r2 与本 Review 作**纯文档 adjudicate + 修订**，不得创建 profile、不得调用任何 profile/private-registry API、不得修改 ACL/label/registry、不得运行 probe/measurement/Sandbox/build，并保持 `private_registry_absence=UNPROVABLE / BLOCKED`、`profile=NOT_CREATED`、`ACL/registry=NOT_MODIFIED`、`OS isolation preflight=NOT_RUN`、`Build Gate=BLOCKED`、`build=NOT_AUTHORIZED / NOT_RUN`、`Hard Build Barrier=EFFECTIVE`、`AC1–AC7=BLOCKED / NOT_RUN`：
> (1) **DSH-R6A-01（P2）**：在 manifest 明确 WER T0/T1 的触发点（全部 Phase A 读取开始前 / 同一测量进程内全部读取结束后）与“相同范围”= r6 §1.1.8 的 3 个目录 + manifest 的 2 个 registry 键；
> (2) **DSH-R6A-02（P2）**：在 manifest §Phase A 允许读取声明“所列 24 个变量即 Phase A 全集，r6 §6 其余映射变量 `NOT_RUN / Phase B`，Phase A 结果不构成 cache 重定向闭包证据”；
> (3) **DSH-R6A-03..12（P3）**：改为 `TRITON_CACHE_DIR` 单独成行；定义环境值类别枚举并只输出类别标签；加“未列项一律不读取”；把 `r6:34` 的“§4.5”改为“§4 scratch 表与 §4 约束 5”；在 `:8` 增补 scratch ACL/label mutation 的准入 token；收紧“既有内容清单 / 根元数据”措辞；在 §4 表标题声明相对路径前缀；明确“四个 scratch 根”；声明 §1.1.9 在 Phase A 不适用；统一“不得打开或哈希任何文件”；
> (4) 修订后**重新固定** r6/manifest r2/Task 的 SHA-256 与对象绑定，并按需另派只读复审；在 Codex 逐项 adjudication 完成、新 pin 生效且 `object_binding` 另行建立之前，**不得运行任何 OS measurement、不得进入 Phase A**；
> (5) 之后执行 Phase A 亦不得解除 private-registry blocker、`P1-01`、`P1-02` 或 Hard Build Barrier；Phase B 每条新增读取仍需独立逐路径/逐 API/逐字段 manifest + 非作者 Review + Codex adjudication。

**给用户**：当前无需新授权。唯一可能需要裁决的情形仍未变（r6 `:177`）：若将来只读或 Phase B 证据证实非提权 controller 无法读取系统对象 DACL，或系统未预置适用的 `S-1-15-2-2` ACE，则本机非提权 Codex-only 路线不可实施，需在“停止本机 AppContainer 路线 / 另行授权替代方案 / 接受 Build Gate 持续 `BLOCKED`”三者中选择。

*报告结束。本报告为只读内容审查产物；DSH 未运行 shell/Git/Windows API，未做 measurement、profile 创建、ACL/registry 修改、probe、build 或 Sandbox，未创建、修改或删除任何文件。*
