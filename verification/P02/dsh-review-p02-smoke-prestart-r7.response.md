# P02 R7 exact-head 独立 Review — 最终正式报告

## decision
**`CHANGES_REQUESTED`**

R3 sequencing clarification 本身合格（最小、只改不可实现时序、未扩权），R2 manifest artifact 内部一致性我已独立复现全部通过；但本 HEAD 有 **3×P2** 需最小返修，其中 F-02 使"启动前复核 HostFolder manifests"按记录的命令集不可执行。

## 绑定对象确认（只对该 commit 作结论）
| 项 | 值 | 核对 |
|---|---|---|
| Delivery HEAD | `ab3958e1270084d80f2edb228aebc6e463233602` | ✅ `git rev-parse HEAD` |
| Delivery tree | `c2829a7f3186ad4c7efe9c872d6e0932c58a1b7b` | ✅ `git rev-parse HEAD^{tree}` |
| base | `b3d36dd4db1a156e3db1057d40b32869880546cf` | ✅ 为 delivery 父提交 |
| 变更范围 | 24 files，全部 `doc/**`(4) + `verification/P02/**`(20)；无产品源码/依赖/契约/build | ✅ `git diff --name-status` |
| artifact 字节 | 13/13（11 records + summary + r3 XML）`git hash-object --no-filters` == blob SHA-1，BYTE_IDENTICAL | ✅ |
| 副作用 | 未修改任何文件；复核前后 tracked 零 diff、未跟踪集合一致 | ✅ |

## finding 计数
**P0=0，P1=0，P2=3，P3=7**

| ID | 级别 | 位置 | 影响 | 最小修复 |
|---|---|---|---|---|
| F-01 | P2 | `verification/P02/codex-checkpoint-p02-smoke-prestart-r2-delivery.md:8`,`:9`；`doc/tasks/P02.md:90`；`doc/STATUS.md:9`；`doc/REBASELINE_PLAN.md:7` | `independent canonical JSON/hash/schema/order validation=PASS` 无任何 artifact（`git ls-files` 无 validator，r2 目录仅 11 records+summary，commit body 仅一行）；R2 checkpoint item 3 的 "verify" 与 Gate 记账含不可复现断言。**事实我已独立复现为真，故非事实错误，但交付未留证**；`r2.py:186-187` 的 round-trip 自检恒真，不能充当该 validator | 落盘 validator + 原始 stdout/exit（如 `codex-smoke-prestart-manifest-r2-validate.{py,stdout.log,exit}`）并在上述 4 处引用；或把措辞降为"作者侧自检（in-script canonical round-trip；独立验证未留证）" |
| F-02 | P2 | `doc/tasks/P02.md:93`；`codex-checkpoint-p02-smoke-admission-r2.md:19,:20,:27`；`codex-smoke-prestart-manifest-r2.py:210-214`（仅 `--config/--clone/--output-dir`）、`:216-218`（输出目录硬固定）、`:252`（`exist_ok=False`）、`:263/:289`（`"xb"`）、`:296-300` | `P02.md:93` 要求启动前"立即复核 … HostFolder manifests"，但 r2 目录已提交存在，重跑必在 `:252` `FileExistsError` → 脚本自报 `BLOCKED`/exit 2；无 `--recheck/--compare` 只读模式。执行者只能在唯一一次启动窗口内改脚本/改路径（记录外即兴），或跳过该步 —— 此时 138,947 个未算文件元数据与 189,336 条路径记录的时效性无任何保障（与未披露残留窗口叠加） | (a) 提供 re-check 模式：只读重扫 11 mapping，与已提交 records 逐条比对（path/type/size；全量根再比 SHA-256），写入新的 r3 evidence 并留 exit；或 (b) 把 `:93` 改为"递归 manifest 为单次捕获基线（r2），启动前只复核可重跑项（root 203-entry、clone/object/pin、资源阈值、r3 config hash、`wsb list --raw`、UI readiness）"并登记基线陈旧 residual |
| F-03 | P2 | `doc/STATUS.md:3`、`doc/00_INDEX.md:3`（对照 `b3d36dd4` 同址）；闭合记录 `dsh-review-p02-preflight-r6.response.md:55` | R6 Review **F-05（已闭合）回退**：`P05 曾在 DSH exact-head Review BLOCKED 后故障转移` 及 `verification/P05/dsh-review-blocked-checkpoint-5288db42.md` 链接被删除；`git grep 故障转移 -- doc/STATUS.md doc/00_INDEX.md` 在 delivery 零命中（base 命中 2 处）。事实未全丢（`doc/tasks/P05.md:70,73`、handoff 仍在），但已闭合条件被回退且未登记理由 | 在 `STATUS:3`、`00_INDEX:3` 恢复该句与链接；若确要移除，须登记理由与替代引用位置 |
| F-04 | P3 | `codex-checkpoint-p02-smoke-admission-r2.md:14`,`:20`；erratum 侧 `…-r3-sequencing.md:4` | R2 item 5 原文（start 前绑定 running session/window）仍留在 `## Required before any wsb start` 下且无 superseded 标记；引用仅单向（R3→R2） | 在 `admission-r2:20` 行尾或节标题加 `Superseded by R3 sequencing clarification (timing only)` |
| F-05 | P3 | `doc/tasks/P02.md:88`（12/12）与 `:90`（11/11）；`codex-smoke-admission-preflight-r2.json`（`commands.hostfolders="…all 12 frozen roots"`；`hostfolders[10]/[11]`=Git cmd / Git mingw64，Build-only RO）；`…preflight-r2.md:8,:10` | 12-root（存在性/root-level reparse）与 11-mapping（r3 XML）域差未桥接；base 版原有的"只覆盖根存在状态、不是递归 manifest"提示已删 → 读者可能误认为 12 个冻结根均已递归覆盖（Git 两根确实不在 Smoke manifest 内） | 在 `P02.md:88/90` 或 `delivery:8` 加一句桥接说明 |
| F-06 | P3 | `verification/P02/codex-smoke-prestart-manifest-r1.py`（与 r2 仅 2 行差异，无无效声明）；`verification/P02/smoke-prestart-manifests-r1/**`（仅 3 个 records，无 summary/README/NOTICE） | R1 无效性仅存在于目录外文字（`P02.md:90`、`r2-start:9`、`r2-delivery:9`）。实测 r1 全为 `not_computed`（scratch 0/7,656、python-base 0/37,024 verified）→ 不会被误当已哈希 R2，但"清楚标为无效"目前只成立于目录之外 | 目录内加 README/NOTICE（`INVALID_PARTIAL_HISTORY / NOT_GATE_EVIDENCE / superseded by r2`），r1 脚本首行加同义声明 |
| F-07 | P3 | `verification/P02/` 无 `codex-smoke-prestart-manifest-r2.*` 的 stdout/exit | 无法从交付确认该次运行的进程退出码（summary 存在 + `overall_status=PASS` 可推断，非直接证据） | 落盘 `SCAN_START/SCAN_DONE` stdout 与 exit 并在 `delivery:8` 引用 |
| F-08 | P3 | `codex-smoke-prestart-manifest-r2.py:282`；被 `P02.md:90`、`delivery:8` 当结果引用 | `"reparse_points_followed": 0` 是硬编码常量而非测量值（不跟随行为由 `lstat`+`:138-141` 设计保证、`issues=[]` 自洽，陈述为真但引用不严谨） | 由 issues 派生，或改名/注明为设计不变量 |
| F-09 | P3 | `codex-checkpoint-p02-smoke-admission-r3-sequencing.md:6`（`four targetable windows`）；`…-r2-delivery.md:10`（`list_apps`/`list_windows` succeeded）；`verification/P02/` 无 sky 原始输出 | R3 新增的启动前门"UI backend readiness"唯一证据是散文，"4"及成功声明不可复核 | 落盘 `list_apps`/`list_windows` 原始输出（或清单+计数+时间戳）并在 R3:6 引用 |
| F-10 | P3 | `doc/00_INDEX.md:5`（对照 `PLAN:7`、`STATUS:9`、`P02.md:90`、`delivery:8` 均已披露） | 入口文档摘要未提 6 个 toolchain 根 metadata-only / 33 样本 / **138,947** 未算字节，读者可能高估覆盖（数值本身不假） | `INDEX:5` 补该区分 |

## 重点项独立判断（结论）
1. **R3 时序澄清 = 满足 criterion 1**：`:6`（交互式非提权 shell + `@oai/sky` backend readiness + `list_apps/list_windows` + 0 environments + 其余预检）、`:7`（唯一 `wsb start` 返回 session ID 后、任何 guest command 前绑定唯一 window、保存截图、绑定 ID/dimensions/hash；失败停止同一 session、`BLOCKED / NOT_VERIFIED`、不重试）、`:8`（不授权 Build / 产品测试 / 第二次尝试 / 额外 HostFolder）逐条对应；仅 F-04 为精度项。
2. **R2 artifact 内部一致性 11/11 通过（我独立重算）**：11 个 `records_sha256` 全匹配；summary 重 dump 自洽；records canonical 重序列化 == 磁盘字节；`(casefold, path)` 排序恒真；schema 键集/枚举/null 一致；计数 **204,419**（files 189,336 + dirs 15,083）；`full` 小型根 **50,356**；选样 **33**；`not_computed` **138,947**；`overall_status=PASS`、11/11 `PASS`、`issues=[]`、`writable_mapping_count=1`、index 1..11 有序；config **2609 B / `9af44513…664d` / 无 CRLF**；r3 XML 11 mappings 与 `r2.py:18-30 EXPECTED` 完全一致。**文档未夸大覆盖**（除 F-10）。
3. **collector 防错足够但存在未披露残留窗口**：reparse/symlink 不跟随（不压栈）、词法 containment、大小写冲突检测、缺失样本阻断、`(size,mtime_ns,st_ino)` 三方哈希期一致性、目录 `(mtime_ns,st_ino)` 扫后复核、issues→BLOCKED→exit 2 均成立。**未披露点**：138,947 个 `not_computed` 文件在扫描期与扫描后**完全无变化检测**（目录 mtime 不反映已有文件内容变化），而缓解它的启动前复核正是 F-02 阻断项；全量哈希文件在其哈希完成后被改写亦不可检测（固有限制）；`out_of_root_path` 为词法 containment，实际防护来自 reparse 检查；`r2.py:186-187` 自检恒真。
4. **R1 无效标注 = 部分满足**（外部清楚、目录内缺失）→ F-06；不会被误当 R2 或 Gate 证据。
5. **Task/Plan/Status/Index 状态一致**（Smoke=`NOT_RUN`、preflight=`BLOCKED / INCOMPLETE`、Build Gate=`BLOCKED`、build=`NOT_AUTHORIZED / NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`、Hard Build Barrier=`EFFECTIVE` 四文档齐备），唯一缺陷为 F-03。

## 实际运行 vs 未运行（不把未执行写成 PASS）
**我实际执行（只读）**：`git rev-parse/log/diff --stat/--name-status/--check`（EXIT=0）/`ls-tree --long`/`hash-object --no-filters`/`status -uall`/`show <base>:…`；Python 重算 11 records SHA-256、summary 自洽、canonical、排序、schema、counts、config hash、r1↔r2 差异；**`python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py` → EXIT=0，7 项全 PASS**（本 HEAD 独立执行；此运行由我完成，交付内未记录）。

**我未运行（一律不是我的 PASS）**：Windows Sandbox / `wsb` / 任何 guest command / `@oai/sky`（R3 的 UI-window-screenshot 绑定完全未验证）；**未读取、未扫描、未重哈希任何 HostFolder 实际内容**（records 与当前宿主真实状态的对应性未验证）；未进入 `G:\CODEX\P02-scratch-build-source`（clone HEAD/tree、porcelain、hardlink=1、私有 common dir、EOL pins 均为采信记录）；未运行 Build / 产品测试 / Vitest / runner / GUI / 真实 WebView / Cargo；未复核作者 Stage-1 宿主测量（CIM/AppX、`wsb` identity/version/hash、cores/RAM/磁盘、SID、root 203/203 与 digest）；未验证"唯一 Sandbox window"在真实 WSB 下可实现（运行期属性）。

## 残留限制
一致性结论仅指 **artifact 内部自洽**，不等于宿主输入已被证实；上列未运行项保持 NOT_RUN；r3 XML 映射 1（clone RW）与映射 2（其子目录 RO）为**嵌套映射**（`codex-p02-wsb-smoke-config-r3.xml:11-12`），属冻结设计（R4/R6 已审），我仅记录不重裁；F-02 未修则启动瞬间宿主状态与 04:27–04:28 捕获基线之间无受记录复核机制。

## 建议下一步
Codex 在 `codex/P02-process-isolation` 追加一个纯文档/证据 commit，闭合 **F-02（必须）**、**F-01**、**F-03**（F-04..F-10 可一并），随后把新固定 HEAD/tree 派发 DeepSeek Harness exact-head 复审；复审通过前保持 `Smoke=NOT_RUN`、**不执行 `wsb start`**。
