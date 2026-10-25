# Review Appointment：UIUX-V2-RUNTIME-1

- **Task**：[UIUX-V2-RUNTIME-1](../../doc/tasks/UIUX-V2-RUNTIME-1.md)（`in_review`）
- **任命方**：DSH（Lead / Architect / Integrator），2026-10-25
- **Reviewer**：**ZCode**（未参与本 Task 实现）
- **审查对象（冻结）**：
  - `base_commit` = `b51d202c9ffab869d26bdb15b38459147991685c`
  - `reviewed_head` = `1853f0a0795ca93a26f6a41efc6c14bd77a3c7b1`
  - 审查范围 = `git diff b51d202c9 1853f0a07`。**注意**：该区间还包含一个前置治理提交 `f7e63c70c`（把两个休眠 Rust Task 的 Reviewer 从已停用的 Antigravity 改派为 ZCode，只动 4 个 doc 文件）。它不属于本 Task 的技术交付，审查时请跳过；技术变更全部在 `apps/desktop/frontend/src/**` 与 `verification/UIUX-V2-RUNTIME-1/**`。
- **唯一写入路径**：`verification/UIUX-V2-RUNTIME-1/review-zcode-r1.md`
  - 审查者**只允许**创建/写入这一个文件。不得修改任何源码、测试、Task 卡、STATUS、PLAN、TASK_LEDGER 或其它证据文件。
  - 只读可访问：仓库全部文件、dev server（`localhost:5189`）、`npx vitest`、`node node_modules/typescript/bin/tsc --noEmit`。
- **为什么是 ZCode**：协作协议要求"Owner 与 Reviewer 必须不同"，且 DSH 不得审自己实现的变更。本 Task 由 DSH 实现主体（书架页、运行时根、令牌桥接、共享组件与文档），工作台页与阅读器/设置页由子 Agent 实现；ZCode 未参与任何部分，满足独立性要求。

## 必须覆盖的审查轴（每轴给 PASS / FAIL / NOT_VERIFIED + 证据）

1. **正确性**：四页在真实 IPC 数据路径上的状态机是否自洽（loading/empty/error/ready 互斥、卸载清理、Blob URL revoke、轮询停止、越界保护）。
2. **诚实数据**：运行时分支是否存在 fixtures 常量回流（假进度、假状态、假模型名、假文本）；无来源字段是否省略或标「未知/未识别」。
3. **单一 UI**：`App.tsx` 默认路径是否只渲染 `UiRoot`；`AppShell` 是否仅 `?view=legacy`；运行时根是否 import 任何历史页面容器；是否存在两套外观同时可达。
4. **设计规则**：圆角 8/4/2/0；字号 28/20/14/12（装饰字豁免）；间距走 `--nm-space-*`；颜色/描边/状态色走 `--nm-*`；无 emoji；七态三重编码（颜色+符号+文字）；同屏 `backdrop-filter` ≤2 且命令面板开启时低优先级层降级；阴影仅两档 elevation 且内容面板零阴影。
5. **令牌单一真相**：`theme/tokens.ts` 与 `design/tokens.css` 逐值一致（含 light 主题）；主题切换是否真的影响既有内联样式消费者（模块级常量是否仍有冻结）。
6. **可访问性**：命令面板的 Tab 圈禁 / Esc / 焦点还原 / `aria-activedescendant`；PrimaryNav roving tabindex；错误面是否为 `role="alert"` 且显示错误码；空态是否可被读屏识别。
7. **证据可核查性**：`verification/UIUX-V2-RUNTIME-1/` 下的 tsc/vitest 原始输出能否复现（reviewer 自行复跑并比对）；截图与 `visual-verification.md` 的逐项描述是否与实际一致；HUMAN_VERIFY/NOT_RUN 项是否被如实标注而不是冒充通过。
8. **范围合规**：是否改动了 Rust/Python/契约/依赖；是否删除或弱化了既有测试（重点看 `App.test.tsx` 与 `DesignPreview.test.tsx` 的既有断言改动是否属于产品行为的直接后果）。

## 明确禁止

- 不得修改任何文件（唯一例外：上面的 review 写路径）。
- 不得执行 `git add` / `git commit` / `git checkout` / `git stash` / `git reset` / `git clean` / push。
- 不得启动新的 dev server 端口或删除他人进程；如需浏览器预览，使用 `localhost:5189`（已在运行）或自行用 `--headless=new --screenshot` 方式只读截屏。
- 不得把"测试全绿"当作"视觉正确"的证据：jsdom 不应用样式表，样式结论必须来自真实渲染或对 CSS 的逐条人工核对。

## 输出格式（写入 review 文件）

```
# Review：UIUX-V2-RUNTIME-1（ZCode r1）
decision: approved | changes_requested | blocked
reviewed_head: 1853f0a07
base_commit: b51d202c9
## 各轴结论
（八轴逐条：PASS/FAIL/NOT_VERIFIED + 依据）
## Findings
| id | 严重度 P0/P1/P2/P3 | 位置（文件:行） | 问题 | 依据 | 建议 |
## 复跑记录
（实际命令、退出码、关键输出；未复跑的项写 NOT_RUN 及原因）
## 对 AC1–AC13 的逐项判断
## 结论与放行条件
```

严重度定义：P0 = 会导致用户可见的错误/数据造假/两套 UI 并存；P1 = 明显违背设计规则或可访问性、或测试不足以支撑主张；P2 = 局部不一致/债务；P3 = 观察项。

## 审查完成后的流程

Review 落盘后由 DSH 处置 findings：P0/P1 必须修复并重新定位审查（同一失败上限 2 次），P2/P3 逐条裁决（修复或登记为后续 Task）。只有 `decision: approved` 或 DSH 处置后复审通过，才由 DSH 回填 `integration_commit` 并把 Task 改为 `done`。

---

## 增量复审任命（r2）

- **触发**：r1 `decision: changes_requested`（0×P0 / 1×P1 / 1×P2 / 5×P3），处置提交 `af421b9e6`。
- **复审对象（冻结）**：`1853f0a07`（r1 reviewed head）→ `af421b9e6`（修复 head）。增量范围：
  - 新增 `apps/desktop/frontend/src/pages/Shelf.test.tsx`（F-1 守卫）
  - `apps/desktop/frontend/src/dev/devMockBridge.ts`（F-2 枚举修复）
  - `apps/desktop/frontend/src/ui/PageState.tsx`（F-4 `role="status"`）
  - `apps/desktop/frontend/src/components/PrimaryNav.tsx`（F-6 注释）
  - 证据重采：`tsc-run.txt`、`vitest-run.txt`、`shots/03-workbench-real-data.png`、`visual-verification.md`（F-2/F-3 处置记录）
  - `APPOINTMENT.md`、`doc/tasks/UIUX-V2-RUNTIME-1.md`（F-6 范围披露、R6/R7 债务登记）
- **复审只需覆盖**：F-1/F-2 是否真正修复（含复跑 `npx vitest run` 与 `tsc --noEmit`）、F-3/F-4/F-6 是否落实、F-5/F-7 的债务登记是否如实、以及修复本身是否引入新问题。其余六轴 r1 已 PASS，不要求重走；若发现与修复相关的新问题，按原严重度定义登记。
- **唯一写入路径**：`verification/UIUX-V2-RUNTIME-1/review-zcode-r2.md`（其余路径只读）。
- **输出**：同上格式 + 对 r1 七条 finding 的逐条处置判定（CLOSED / STILL_OPEN / NOT_VERIFIED）。
