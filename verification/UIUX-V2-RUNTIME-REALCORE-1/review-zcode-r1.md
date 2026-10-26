# UIUX-V2-RUNTIME-REALCORE-1 — ZCode 独立复核 r1

verdict: approved

- 复核者：ZCode（未参与实现）
- 复核区间：`e1838875e2db951382d1efefcdef404cbf47a661..b4f5b7f61`（4fb5c1be9 / cb4590c02 / b4f5b7f61）
- 复核方式：只读。git show/diff、源码与证据通读、workspace 数据根 SQLite 只读对账、独立复跑守卫测试（vitest 5 passed / cargo test ascii_json_line 2 passed / tsc exit 0，全部与任务卡声称一致）。
- 总评：两个缺陷的修复本身正确、有真守卫、真实栈证据链完整；我做了仓库证据之外的独立对账（直接读各轮数据根的 SQLite 落库原始字节），修复前乱码与修复后还原均得到证实。发现的问题集中在证据留存与文档措辞（1×P2 + 5×P3），不阻塞收口。

## 逐条结论

### 1. F-1（P0 编码缺陷）— 修复成立

**是否真解决 cp936 stdin 问题：是。** `library_bridge.rs` 的 `ascii_json_line()`（apps/desktop/src-tauri/src/library_bridge.rs:31-42）对 `serde_json::Value::to_string()` 的输出做逐字符处理：非 ASCII 字符经 `encode_utf16` 输出为 `\uXXXX`。这一步是无损的，理由：

- serde_json 的 `to_string()` 已把字符串内的 `"`、`\`、控制字符转义为 ASCII 形式（`\"`、`\\`、`\n`、`\uXXXX`），因此后处理遇到的非 ASCII 字符只可能是字符串字面量内的合法 Unicode 文字字符（键名与值同等对待），不会与既有转义序列发生重组。
- 非 BMP 字符（emoji 等）由 `encode_utf16` 产出成对的代理转义（`\uD83D\uDE00` 形态），这是 JSON 标准允许且 `json.loads` / serde_json 均支持的写法；Rust `char` 不含孤立代理，故不可能产生非法 JSON。
- 我用仓库外原始数据独立对账：修复后 probe 轮（workspace `task-envs/UIUX-V2-RUNTIME-REALCORE-1/run-i17/data-root/library.db`）落库为 `'ascii-title' / '中文标题' / '中文 带空格' / '端到端验收-808947' / '雾港来信' / 'a中文b'`，与任务卡第 84-89 行引用的 probe 输出逐字一致，且是 SQLite 原始字节层面的证据，不是转录自查。

**只改发送方向是否够：够。** Core 侧两处响应写出均用默认 `json.dumps`（ensure_ascii=True）：

- `src/bootstrap/core_service.py:4574-4577`（`_emit`：`json.dumps(payload, separators=(",", ":")) + "\n"`）
- `src/infrastructure/resource_channel/host_bridge.py:181`（同形态）

默认 ensure_ascii=True 使 Core 发出的每一行天然纯 ASCII，即使 Python 以 cp936 编码 stdout，ASCII 也无损（ASCII 是 cp936 与 UTF-8 的公共子集），Rust 侧读行无需改动。请求方向则不同：Rust 侧 `to_string()` 输出 UTF-8 原样中文，Python frozen stdin 以 cp936 解码必然破坏——这正是只修发送方向的依据，且依据在代码中成立。

**其它 stdio 通道：**

- `settings_bridge.rs`：不是独立 stdio 通道。它复用 library 通道（文件头 `use crate::library_bridge::{... P15SettingsCommand}`），设置载荷经 `library_bridge` 的统一发送点出站，已被 `ascii_json_line` 覆盖（含设置值中的非 ASCII）。无需另修。
- `core_bridge.rs:216`：仍用原样 `request.to_string()` 写 stdin。**当前不是现实缺陷**——该通道载荷为 `resource_id`（Core 侧 `uuid.uuid4().hex`，src/application/library/service.py:23）、`revision`（"rev-N" 形态）、`opaque_id`/facts（sha256 hexdigest，src/infrastructure/resource_channel/handle_resolver.py:271），全部 ASCII 来源。DSH 在 core_bridge.rs:140-143 用注释记录了"Kept ASCII-only here too"的约束。但这是无守卫的隐式约束：若未来 revision/resource_id 改为从书名/文件名派生，同缺陷会在该通道复发且无测试拦截。登记为 P3（见问题 3）。
- `ac1_bridge.rs:105`：同样未转义，但该通道仅在 `M2AC1_TEST_MODE=1` 测试配置下 spawn（文件头注释），且是 `python -m` DEV 形态、载荷为验收循环固定 ASCII 标识。不构成产品暴露。

### 2. F-2（P1 死按钮）— 修复正确且与既有约定一致

`Shelf.tsx` 的修复与其它三页的既有接线同构：

- Workbench.tsx:97-125、Reader.tsx:59-86：`onOpenCommand?: () => void; commandOpen?: boolean;` + `onClick={onOpenCommand}` + `aria-expanded={commandOpen}`。
- Settings.tsx:270-280：`onClick={() => runtime.chrome.onOpenCommand()}` + `aria-expanded={commandOpen}`。
- Shelf.tsx 修复后（apps/desktop/frontend/src/pages/Shelf.tsx:491-494、:585）：`paletteOpen = palette?.open ?? commandOpen`；`openCommand = palette ? () => palette.onOpen() : (onOpenCommand ?? noop)`。

两种模式均正确：运行时 `palette=null`（RuntimeShelf，Shelf.tsx:1028-1029 传 `chrome.onOpenCommand`/`chrome.commandOpen`）时行为与其它三页等价；设计预览 `palette` 非 null 时保持原自托管行为（palette 优先，commandOpen 被忽略）。设置页 fixture 模式（runtime 为 null）按 Settings.tsx:270 的 `runtime ? ... : null` 分支不渲染触发器，不存在同类死按钮；本次修复未引入新的不一致。唯一细微差异是 Shelf 用 noop 兜底而其它页直调，属更防御的写法，非缺陷。

### 3. 证据可复现性 / 是否夸大

**「真实 Tauri 生产窗 + 真实 Python Core」成立。** run-i18/report.json 记录：`exeSha256=54F0957F…`（与 README 验收构建表一致）、`M2RC1_PACKAGED=1`（packaged 模式=frozen sidecar）、`__neverSet=[M2RC1_PROBE_OUT, M2AC1_TEST_MODE, M2RC1_SRC_ROOT]`（无 probe/dev 面）、S1 断言 `typeof window.__TAURI__ === "object"` 与生产 IPC allowlist 公告 66 条。S6 的中文标题 `端到端验收-322242` 与 run-i18 数据根 SQLite 落库逐字一致——UI→Tauri IPC→Rust 桥→Core→SQLite 全链真实。不是 mock/dev 桥。

**「两版 exe 差异仅 additionalBrowserArgs」：配置层面成立，二进制层面措辞过强。** 我核对了产品 `tauri.conf.json` 窗口段（title/width/height 与验收配置完全相同，仅验收配置多 `additionalBrowserArgs`，且该串手工保留了 wry 默认的 disable-features 再追加调试端口——这是窗口级参数整体替换语义下的正确做法）。但两个 exe SHA 不同（两次独立构建的非确定性），"两版代码完全相同、唯一差异 additionalBrowserArgs"只能对**构建配置**主张，不能对**二进制字节**主张。README 措辞宜限定为"配置差异"。发布 exe 未跑 7 场景已在 R1 如实登记（无 CDP 技术上不可行），发布冒烟有独立截图证据（release-smoke.png），不构成宣称过度。

**AC3/AC4/AC5 诚实。** AC3/AC4 从未勾选；AC5 曾误勾 [x]，b4f5b7f61 收口时主动降回 [ ]——这是诚实性加分。AC2 的载体是验收构建而非发布二进制，Task 卡与 README 均已披露区分。

**一处夸大：见问题 R-P2-1（四组合实测无证据）。**

### 4. 范围扩张（D3）— 可接受

原卡"不允许修改产品源码"被 DSH 单方扩张为卡内直修。判定可接受，理由：

1. 治理授权：AGENTS.md 规定 DSH 作为 Lead/Integrator 拥有任务释放与范围冻结、契约与架构裁决权；用户 2026-10-26 明确授权"自动推进到产品完成"。范围变更被逐条记录（D3）、`allowed_paths` 同步扩大、并给出"若审查认为越权则拆分独立修复 Task"的处置选项。
2. 替代方案确实更差：JS 侧转义不可行（请求序列化点在 Rust 的 serde_json，前端无法控制线上形式）；Python 侧修（`stdin.reconfigure` 或二进制读）需重打包重分发 sidecar；另立 Task 需要第二次构建/验收循环。Rust 侧 ASCII 线上形式是最小正确修复点，F-2 只能在 Shelf.tsx 修。
3. 制衡在本轮补齐：DSH 不得自审自己的变更，本报告即该制衡；且 push 未执行（doc/STATUS.md:26 REALCORE push 裁决=未执行）。

不判越权。附注：交付直接落 main、无独立 worktree，属 DSH 集成权限内，已在 Closeout Record 如实记载。

### 5. 回归守卫判别力

- **Rust 2 条（library_bridge.rs:5893-5917）：真守卫。** 把 `ascii_json_line` 改回 `value.to_string()` 则 `line.is_ascii()` 断言必红；第二条（ASCII 输入恒等）防过度转义，是辅助而非缺陷守卫。我复跑 `cargo test ascii_json_line` → 2 passed。
- **jsdom 守卫 1（Shelf.test.tsx:187-199）：真守卫。** mount 完整 `Shelf`（runtime → RuntimeShelf → palette=null），点击后断言 `chrome.onOpenCommand` 被调 1 次；缺陷态（`palette?.onOpen()` 对 null 无操作）下该断言必红。任务卡"回退修复后 1 failed"与此相符（红的就是这条）。
- **jsdom 守卫 2（Shelf.test.tsx:201-207）：弱守卫，见问题 R-P3-2。** 它只断言 `commandOpen=false` 时 aria-expanded="false"——原缺陷（恒 false）下同样通过，对"aria-expanded 恒 false"无判别力；且 E2E S3（run.mjs:242-281）只断言面板 DOM 出现与焦点还原，不查 aria-expanded。全库无 `commandOpen=true → aria-expanded=true` 覆盖。
- 我复跑 `npx vitest run src/pages/Shelf.test.tsx` → 5 passed，与任务卡一致。

### 6. 任务卡诚实性

发现表 F-1/F-2/F-3 与 diff、workspace 原始数据一致；测试要求表数字全部复现（vitest 5 passed / cargo 2 passed / tsc exit 0 / run-i18 7/7 exit 0）；Canonical Evidence 表 30 项 pin 到 4fb5c1be9，抽查的文件均在。风险表 R1-R3 本身属实，但有遗漏（见 R-P2-1、R-P3-3、R-P3-5）。

## 问题清单

| id | 严重度 | 位置 | 现象 | 依据 | 建议处置 |
|---|---|---|---|---|---|
| R-P2-1 | P2 | doc/tasks/UIUX-V2-RUNTIME-REALCORE-1.md:77（F-1 根因栏）、4fb5c1be9 commit message、README.md:31-32 | 「PYTHONIOENCODING/PYTHONUTF8 对冻结 bootloader 无效（四种组合实测返回完全相同的乱码）」的对比实验**没有任何可对账输出**：workspace `task-envs/UIUX-V2-RUNTIME-REALCORE-1/probe-encoding/` 下有 none/no-encoding/utf8/utf8-env/io/both 六个隔离数据根，但每个的 `library.db` books 表均为空，也无任何日志/截图记录各组合的返回；目录数（6）与"四种组合"亦不对应 | 本复核实地扫描（sqlite 只读查询全空）；乱码本身另有铁证（run-i14/i15 落库 `闆炬腐鏉ヤ俊`），缺的只是"env 钉死无效"这半句的实验留痕 | 收口时二选一：补一次带输出留痕的对比实验入 workspace 并登记；或将该句改为如实措辞（如"尝试过多种 env 组合未见改善，输出未留存"）。注意修复方案本身不依赖该声称（ASCII 线上形式强于任何 env 钉死），故不阻塞 |
| R-P3-2 | P3 | apps/desktop/frontend/src/pages/Shelf.test.tsx:201-207 | 守卫 2 只测 aria-expanded=false 分支，对"恒 false"回归无判别力；`commandOpen=true → aria-expanded="true"` 全库无覆盖（jsdom 与 E2E S3 均无） | makeRuntime 硬编码 `commandOpen: false`（:75），测试断言与缺陷态不可区分 | 后续小修：makeRuntime 支持覆写 commandOpen，补一条 true 分支断言（或 E2E S3 补一条 `aria-expanded` 检查）。非阻塞 |
| R-P3-3 | P3 | apps/desktop/src-tauri/src/core_bridge.rs:216、ac1_bridge.rs:105 | 两个次要通道仍用原样 `to_string()` 写 stdin。core_bridge 当前载荷（uuid hex/rev-N/sha hex）恰好 ASCII 故无现实缺陷，且 :140-143 已有注释记录约束，但无任何守卫钉住"该通道载荷必须 ASCII"的隐式前提；载荷形态一旦演变（如 revision 从书名派生）缺陷会静默复发 | 本复核逐一核对 resource_id（service.py:23 uuid4().hex）、revision、opaque_id（handle_resolver.py:271 sha256 hexdigest）来源 | 登记为后续候选 Task：把 `ascii_json_line` 提为共享 helper 并让 core_bridge 复用（一行改动），或加单测断言 core_bridge 请求线上 ASCII。本轮不强制 |
| R-P3-4 | P3 | verification/UIUX-V2-RUNTIME-REALCORE-1/README.md:31 | 「两版代码完全相同，唯一差异是 additionalBrowserArgs」在二进制层面不可证（两 SHA 不同属两次构建的非确定性）；该句对配置成立（我已核对窗口段仅差 args），对字节不成立 | tauri.conf.json 窗口段 vs tauri.acceptance.conf.json 逐字段比对；README 自己登记了两个不同 SHA | 措辞改为"构建配置唯一差异是 additionalBrowserArgs，二进制因构建非确定性必然不同"。收口时顺手修正 |
| R-P3-5 | P3 | verification/UIUX-V2-RUNTIME-REALCORE-1/README.md:39-49（run 历史表） | run 表只列 i2/i4/i5/i6/i8/i18，未说明 i1/i3/i7/i9-i17 去向；其中 **i14/i15 恰是修复前乱码的原始落库证据轮**（数据根 `library.db` 含 `'ascii-title','闆炬腐鏉ヤ俊'`），证据价值最高的失败样本反而既未入表也未登记为 SOURCE_PIN | 本复核扫描 workspace 全部 run-iN 数据根 | 收口时在 README run 表补一行说明（i9-i16 为 probe/诊断轮，数据根在 workspace）；建议把 run-i14 或 i15 的落库乱码作为 F-1 修复前证据显式登记（哪怕只登记 workspace 路径） |
| R-P3-6 | P3 | doc/tasks/UIUX-V2-RUNTIME-REALCORE-1.md:81-90（probe 引文） | Task 卡引用的 probe 6 行输出是 console 转录，未落盘为 canonical 证据（run-i17/logs 只有 app 的 stderr/stdout） | run-i17/logs 目录内容核对；但 run-i17 数据根 SQLite 落库与引文逐字一致（本复核已对账），故仅降级为 P3 | 后续 probe 类脚本建议同时把 stdout 写入 logs/；本轮无需返工 |

## 可复现性判断

**认同：这是可复现的脚本化验收，且质量高于本仓此前的截图识图方式。** 依据：

1. 脚本与配置全部版本化（e2e/uiux-v2/ 四个文件 + tauri.acceptance.conf.json），复现命令写在 README（先验收构建再指 UIUX_E2E_EXE，流程自洽：验收构建覆盖同名 exe 后 CDP 才可用）；run.mjs 每轮自动分配新 run-iN 槽位且 `assertLaunchTargetsClean` 拒绝覆盖既有证据。
2. 断言是 DOM/行为级（aria 属性、计算样式、真实鼠标/键盘事件、allowlist 行数），不是看图；`exit 0` 语义严格（任一 check 失败即非零）。
3. 被测二进制可对账：report.json 记录 exeSha256，与 README 双版本表可核对；本轮 run-i18 = 验收构建 54F0957F…。
4. 失败史不隐藏：5 个失败轮 report 入库（EV-20..24），失败明细与 F-3 叙述吻合（run-i8 S6 被拒正是 F-1 修复前直接证据）。
5. 我在仓库证据之外做了独立交叉验证：直接只读查询各轮数据根 SQLite——修复前 run-i14/i15 落库乱码 `闆炬腐鏉ヤ俊`、修复后 run-i17 六种 title 形态全部无损、run-i18 与 S6 生成逻辑一致。产品行为与证据记载在原始字节层面互证。

保留意见（不影响 verdict）：验收只能跑在验收构建上（R1，已如实登记）；「四组合 env 实测」缺留痕（R-P2-1）；建议 DSH 收口时完成 R-P2-1 与 R-P3-4/R-P3-5 的文字修正，并将 R-P3-3 登记为后续候选。
