/**
 * DEV-ONLY 浏览器预览垫片（不参与生产运行时行为）。
 *
 * 用途：`npm run dev` 在普通浏览器里打开 http://localhost:5188 时，页面没有
 * `window.__TAURI__.core.invoke`。App.tsx 的启动探测会在 TAURI_BRIDGE_MISSING
 * 处停下并只渲染一行状态文字，于是看不到四个一级页面。
 *
 * 这里在「真实 Tauri 桥不存在」时注入一个仅供预览的 IPC 垫片：
 *
 *  - `ac1_request` / `probe_config` 等探测命令一律拒绝，App 因此走
 *    production 分支（runInteractiveDenyMatrix -> setAppMode("production")），
 *    渲染真正的 <AppShell>，四个页面导航与布局完整可见。
 *  - 只对少量只读命令返回最小合法数据（空书架、空列表），让空态样式的
 *    改动也看得见；其余命令一律以 `MOCK_DENIED:<command>` 拒绝。
 *
 * 硬约束：
 *  - 真实桥存在时绝不覆盖，打包 app 行为字节不变。
 *  - 生产构建里 `import.meta.env.DEV` 为 false，本函数不会被调用。
 *  - 这里的数据全部是假的：业务事实只认 Python Core。
 */

type InvokeFn = (command: string, args?: Record<string, unknown>) => Promise<unknown>;

/** 只读命令的最小合法响应；形状按 library/client.ts 的期望（数组）。 */
const EMPTY_READS: Record<string, unknown> = {
  core_ping: { ok: true },
  library_list_books: [],
  library_list_recycle_bin_books: [],
  list_chapters: [],
  list_chapter_pages: [],
  list_regions: [],
  list_region_revisions: [],
  // App.test.tsx 的 production 用例钉住的空设置形状。
  settings_get: { settings: {} },
};

const mockInvoke: InvokeFn = (command) => {
  if (Object.prototype.hasOwnProperty.call(EMPTY_READS, command)) {
    return Promise.resolve(EMPTY_READS[command]);
  }
  return Promise.reject(new Error(`MOCK_DENIED:${command}`));
};

function renderBadge(): void {
  if (typeof document === "undefined" || document.getElementById("dev-mock-badge")) return;
  const badge = document.createElement("div");
  badge.id = "dev-mock-badge";
  badge.textContent = "浏览器预览 · 假数据";
  badge.title = "Tauri IPC 未连接，本页数据来自 dev mock（src/dev/devMockBridge.ts）";
  badge.style.cssText = [
    "position:fixed",
    "right:10px",
    "bottom:10px",
    "z-index:2147483647",
    "padding:4px 9px",
    "border-radius:999px",
    "background:rgba(255,181,0,.92)",
    "color:#201400",
    "font:600 11px/1.4 Consolas,monospace",
    "pointer-events:none",
    "box-shadow:0 2px 8px rgba(0,0,0,.35)",
  ].join(";");
  document.body.appendChild(badge);
}

/** 安装预览垫片；真实 Tauri 桥或非浏览器环境时静默跳过。 */
export function installDevMockBridge(): void {
  if (typeof window === "undefined") return;
  const globalWindow = window as unknown as {
    __TAURI__?: { core?: { invoke?: InvokeFn } };
  };
  if (globalWindow.__TAURI__?.core?.invoke) return;

  globalWindow.__TAURI__ = { core: { invoke: mockInvoke } };
  renderBadge();
  console.info("[dev-mock] Tauri IPC 垫片已安装：界面可预览，数据为假（仅 UI 验证用）。");
}
