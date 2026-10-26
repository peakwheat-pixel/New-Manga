# UIUX-V2-RUNTIME-NARROW-1 — DSH 独立复核 r1

verdict: approved

复核对象：`e9a409927`（ZCode 交付）
复核人：DSH（本卡 Reviewer，未参与实现）
复核方式：不只看报告——独立复跑了 E2E / tsc / vitest，并回到源码与历史提交核实根因。

## 一、根因核实（这是本卡最关键的一步）

ZCode 声称根因是 `apps/desktop/frontend/src/ui/ui.css:18` 的 `.nm-app { min-width: 1024px; }`。
我独立核对：

```
git show e9a409927^:apps/desktop/frontend/src/ui/ui.css
L13: .nm-app {
L18:   min-width: 1024px;     ← 改前确实存在
```

`git show e9a409927 -- ui.css` 的 diff 里，`-  min-width: 1024px;` 被删除，并补了说明注释。
**根因成立**：根容器被硬下限撑到 1024，`#root`/`body` 只有 900，`overflow: hidden` 把溢出裁掉，于是 `documentElement.scrollWidth` 报 1024。

它同时否证了我此前在任务卡里猜的三个候选（书架网格 `minmax` / 详情面板固定宽 / 标题栏三段最小宽）——
标题栏三段 min-content 实测 884 < 900，本就不是撑宽源。**猜错的候选被我写进了卡里，它用实测推翻了，这点要记。**

## 二、独立复跑（不采信交付方数字）

| 项 | 我的实测 | 与交付方一致性 |
|---|---|---|
| `node e2e/uiux-v2/run.mjs` | **`run-i4` 10/10 场景 PASS，exit 0** | 一致（它跑的是 run-i3） |
| S10 矩阵 | 900×700 四页与 1280×800 四页均 `scrollWidth === clientWidth === innerWidth` | 一致 |
| `tsc --noEmit` | **exit 0** | 一致 |
| `npx vitest run` | **567 passed / 60 files** | 一致 |
| 构建新鲜度 | CSS 14:16:37 → dist 14:16:57 → exe 14:18:14；exe SHA `C1AB2749…` | 与它报告的被测 exe 一致（不是拿旧界面测） |

`1280` 档不退化有逻辑与实测双重支撑：`min-width: 1024px` 在 1280 视口本就不触发，且复跑 1280 四页全 PASS。

## 三、范围合规

`git show --stat e9a409927`：只改 `pages.css`(+15)、`ui.css`(+6/−1)、`run.mjs`、`env.mjs`、新增 `diag-narrow.mjs`、
`verification/UIUX-V2-RUNTIME-NARROW-1/**`、`doc/tasks/…`、`doc/handoffs/…`。

我逐项核对禁区：**没有** `tokens.css`、`base.css`、`STATUS.md`、`REBASELINE_PLAN.md`、`TASK_LEDGER.md`、`tauri.conf.json`、任何 `.rs`。
设计令牌与信息架构未动。

它还主动发现并修正了一处遗留：`e2e/uiux-v2/lib/env.mjs` 的隔离根与证据目录原本还指着 REALCORE-2，
按本卡硬约束 1 改指 `task-envs/UIUX-V2-RUNTIME-NARROW-1` 与本卡 verification 目录——这是我的疏漏，它补上了。

## 四、人眼复核（自动化断言之外）

我看了 `run-i3-shots/11-900x700-dpr2-shelf.png`（1800×1400，DPR2 实际渲染）：
标题栏（品牌/四 tab/搜索/窗口按钮）、工具栏（搜索/筛选/排序/导入/新建）、书架网格、详情面板（封面/标题/两枚数字块/章节行/两个按钮）、
状态条（`完成 Core 在线 … Core ready … 1 部作品`）**全部完整可见，无裁切、无重叠、无横滚**。真实 Core 数据在位（`端到端验收-659134`、1 章节）。

## 五、问题清单

| id | 严重度 | 位置 | 现象 | 处置 |
|---|---|---|---|---|
| N-1 | P3 | 书卡封面 | 900 档书卡封面上的标题文字为竖排装饰，长标题会被裁（宽窗同样存在，非本卡引入） | 不阻塞；建议后续在封面组件里做两行截断或字号自适应，属视觉打磨 |
| N-2 | P3 | `min-height: 680px` | 仅去了宽度下限，高度下限仍在；视口高 <680 会有同类纵向溢出 | ZCode 已自报；本卡 AC 只覆盖宽度，建议后续单独立项或并入响应式收口 |

两条都是它自己在"已知限制"里先说的，不是被我挖出来的——**诚实度合格**。

## 六、判定

`approved`。根因定位准确且有实测证据；修复克制（一处硬下限 + 一个窄断点），没有借机改设计语言；
断言从 `KNOWN_DEFECT` 升级为**两档四页硬断言**，回退会被立刻抓住；独立复跑全绿。

**可以收口为 done。** 两条 P3 作为后续候选登记，不在本卡解决。
