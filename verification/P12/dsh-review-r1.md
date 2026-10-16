# P12 独立 Review（R1）

| 项 | 值 |
|---|---|
| Task | P12（书架导入 UI 实现：四页 Shell + 书架页 + 导入） |
| Owner | antigravity |
| Reviewer | dsh（epoch 6；独立于 Owner） |
| 交付 commit | 实现 `a8a63020f`；记录 `a2dcbb9f6` |
| 基线 | `1b41caee4b38ba9aa1c9a6579219b32dd1f24499` |
| 结论 | **changes_requested（I1，1 项）** —— 实现质量高、范围干净、测试与构建可复现；但**模式分流在初始渲染即挂载生产四页**，构成对 probe/AC1 冻结证据面的实质回归风险 |

## 1. 已独立验证且成立的部分

| # | 验证项 | 方法 | 结果 |
|---|---|---|---|
| V1 | 交付范围 | `git diff --name-only 1b41caee4..a2dcbb9f6` | **仅** `apps/desktop/frontend/src/**` + Task/Handoff/verification；**零**改动 `src/**`、`doc/contracts/**`、`requirements.txt`、`Cargo.toml`、`package.json`、`package-lock.json` |
| V2 | 前端测试（**独立复跑**） | `npx --prefix apps/desktop/frontend vitest run` | **Test Files 16 passed / Tests 171 passed，exit 0**（与 Owner 声明一致） |
| V3 | 生产构建（**独立复跑**） | `npm --prefix apps/desktop/frontend run build` | **exit 0**，64 modules，`dist/assets/index-520NFLnQ.js` 249.26 kB（与 Owner 产物一致） |
| V4 | 证据哈希 | `Get-FileHash` 复算三项 | `vitest.log` `6af7ca07…`、`build.log` `f181f975…`、`boundary_audit.txt` `b016e9c2…` —— **与 Owner 声明的 pin 逐一吻合** |
| V5 | 主仓保护 | 主仓 HEAD + status | tracked dirty **恒为 19（用户原有）** |
| V6 | 缺口 disabled | 读 §7 的 24 条缺口对应控件 | 按设计基线 disabled 呈现，未发现 mock 或私有 wire 绕过 |
| V7 | 边界合规 | 前端口径核查 | 未见 SQLite / 任意 OS 路径 / 模型直连；大图仍走资源通道 |

Owner 如实声明了环境限制：无头 Windows 下 WebView2 取不到 GUI 窗口句柄（`0x80070578`），因此**真实 GUI e2e runner 未运行**，回归保障由单测承担。

## 2. I1（必须返修，bounded）

**finding**：`apps/desktop/frontend/src/App.tsx` 的模式分流以
`const [appMode, setAppMode] = useState<"probe" | "ac1" | "production">("production")`
起步，渲染尾部为：

```tsx
const safeInvoke = activeInvoke || tauriInvokeSafe();
return <AppShell invoke={safeInvoke} />;     // appMode === "production" 时
```

即**任何窗口的首次渲染都会挂载生产四页应用**，只有 effect 检测出 probe/AC1 模式后才切回探针壳。后果（均基于当前代码事实）：

1. `AppShell` 用 `display:none` **同时挂载四页**（keep-alive，`shell/AppShell.tsx:243-300`），其中 `BookshelfPage` 挂载后即 `await activeClient.listBooks()`（`bookshelf/BookshelfPage.tsx:58/73`）→ 真实调用 **`library_list_books`**。
2. `library_list_books` 属 **production-only 命令**（`apps/desktop/src-tauri/src/main.rs:56-58`），**在 probe 与 AC1 面被移除**（`command_allowlist` 的过滤逻辑）。因此 probe/AC1 runner 窗口会**额外发生被拒的生产命令调用**。
3. `App.tsx` 原有注释明确写着该不变量：「the deny matrix and the probe driver must see the exact pre-Task DOM」/「probe/ac1 路径 keep `navChrome=false` forever」。当前实现使**首帧即为生产 DOM**，与该不变量直接冲突；RC2-AC1 的硬化面证据协议正建立在这组形状上。
4. `safeInvoke` 在 `activeInvoke` 为 undefined 时取 `tauriInvokeSafe()`——**在真实窗口里这是真 invoke**，所以第 1–2 条不是纸面推断。

**Owner 现有测试为何没抓到**：`App.test.tsx` 的三个用例中，
① 「mounts production AppShell」**恰恰因为初始值就是 `production`** 而通过（且该用例没有 `__TAURI__`，`tauriInvokeSafe()` 退化为 noop，因此掩盖了真实调用）；
② 只覆盖 `?view=console` 逃生口；
③ 只断言 effect 解析**之后**的最终状态。
**没有任何用例断言"检测完成之前不得出现 `app-shell`"**——这正是回归所在。

**返修要求（bounded）**：

1. **让检测前的状态保持中性**：新增独立的 `"detecting"` 态（或等价方案），在模式判定完成前**不得挂载 `AppShell`**。
   建议保持与既有行为最接近的形态：检测期间渲染**冻结的 console 探针壳**（而非生产四页）；
   `?view=console` 逃生口与既有语义保持不变。
2. **补初始渲染断言**：新增/扩展单测，断言 (a) 未注入 `__TAURI__`、以及 (b) `probe_config` 尚未 resolve 的**首帧**，
   均**不含** `[data-testid="app-shell"]`；并断言这两条路径下**不会**产生 `library_list_books` / `settings_get` 之类的生产命令调用
   （用一个记录所有 `invoke(cmd)` 的 mock 断言"未调用"）。
3. 重跑 `vitest run` 与 `npm run build`，把新日志归档进 `verification/P12/` 并更新 Task 的 Canonical Evidence sha256。
4. **不得**为本项修改 probe/AC1 的既有 DOM 形状、`navChrome` 语义或 `library/client.ts` 的生产调用逻辑。

**不做**：不得改动 `src/**`、契约、依赖；不得借返修扩产品范围；不得删除既有测试。

## 3. 已接受的信息性记录（非返修项）

- **N1**：`tauriInvokeSafe` 由 effect 内部提升为模块级函数——已核对它不依赖闭包变量，属等价重构，**接受**。
- **N2**：AC6 的"零回归"结论目前**仅由单测支撑**（真实 e2e runner 因无头环境未运行）。
  I1 收敛后，该限制应随 AC6 证据一并如实保留，**不得**表述为"e2e 已验证"。
- **N3**：构建/测试耗时与产物字节与 Owner 声明一致，证据哈希吻合。

## 4. 收敛计划

`I1 返修（Owner=antigravity，bounded，仅前端 + 测试） → Reviewer 复跑 vitest/build 并复核初始渲染断言 → 必要时 I2（上限 1 次） → 集成 → closeout`。
