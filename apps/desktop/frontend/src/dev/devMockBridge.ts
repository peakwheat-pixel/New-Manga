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
 *    渲染 v2 运行时根，四个页面导航与布局完整可见。
 *  - 只读命令返回**形状合法**的固定样例数据，让真实数据路径（表格、章节、
 *    页序、状态面）也能在浏览器里被肉眼检查；未列出的命令一律以
 *    `MOCK_DENIED:<command>` 拒绝，页面因此展示真实的错误态而不是假装成功。
 *
 * 硬约束：
 *  - 真实桥存在时绝不覆盖，打包 app 行为字节不变。
 *  - 生产构建里 `import.meta.env.DEV` 为 false，本函数不会被调用。
 *  - 这里的数据全部是假的，只用于 UI 验证；业务事实只认 Python Core。
 *    页面上常驻角标会写明这一点，截图证据必须保留角标。
 */

type InvokeFn = (command: string, args?: Record<string, unknown>) => Promise<unknown>;

const now = Date.now();
const iso = (minutesAgo: number) => new Date(now - minutesAgo * 60_000).toISOString();

const BOOKS = [
  {
    book_id: "book-mist-harbor",
    title: "雾港来信",
    original_title: "霧港からの手紙",
    is_favorite: true,
    is_archived: false,
    page_count: 128,
    created_at: iso(60 * 24 * 40),
    updated_at: iso(12),
  },
  {
    book_id: "book-daylight",
    title: "白昼残响",
    original_title: "白昼の残響",
    is_favorite: false,
    is_archived: false,
    page_count: 96,
    created_at: iso(60 * 24 * 30),
    updated_at: iso(60),
  },
  {
    book_id: "book-spring",
    title: "春日构造",
    original_title: null,
    is_favorite: false,
    is_archived: true,
    page_count: null,
    created_at: iso(60 * 24 * 20),
    updated_at: iso(60 * 6),
  },
  {
    book_id: "book-iron",
    title: "铁与麦穗",
    original_title: "鉄と麦穂",
    is_favorite: true,
    is_archived: false,
    page_count: 204,
    created_at: iso(60 * 24 * 90),
    updated_at: iso(60 * 26),
  },
];

const CHAPTERS: Record<string, Array<{ chapter_id: string; title: string; chapter_number: string; sort_order: number }>> = {
  "book-mist-harbor": [
    { chapter_id: "ch-mh-12", title: "潮汐留下的名字", chapter_number: "012", sort_order: 12 },
    { chapter_id: "ch-mh-11", title: "第七盏路灯", chapter_number: "011", sort_order: 11 },
    { chapter_id: "ch-mh-10", title: "没有寄出的信", chapter_number: "010", sort_order: 10 },
  ],
  "book-daylight": [
    { chapter_id: "ch-dl-03", title: "白昼的第一段", chapter_number: "003", sort_order: 3 },
    { chapter_id: "ch-dl-02", title: "残响", chapter_number: "002", sort_order: 2 },
  ],
  "book-spring": [{ chapter_id: "ch-sp-01", title: "春天的构造", chapter_number: "001", sort_order: 1 }],
  "book-iron": [
    { chapter_id: "ch-ir-11", title: "麦穗与齿轮", chapter_number: "011", sort_order: 11 },
    { chapter_id: "ch-ir-10", title: "铁轨", chapter_number: "010", sort_order: 10 },
  ],
};

function pagesFor(chapterId: string) {
  return Array.from({ length: 6 }, (_, index) => ({
    page_id: `${chapterId}-p${index + 1}`,
    source_filename: `page-${String(index + 1).padStart(3, "0")}.png`,
    sort_order: index + 1,
  }));
}

const EMPTY_READS: Record<string, unknown> = {
  core_ping: { status: "ok", protocol_version: { major: 2, minor: 1 }, capabilities: ["library", "reader"] },
  library_list_books: BOOKS,
  library_list_recycle_bin_books: [],
  // 注意 wire 形状：导航投影是 {chapters:[...]} / {pages:[...]}，不是裸数组
  // （client.ts 会以 PAGE_NAV_MALFORMED 拒绝裸数组）。
  list_chapters: (args?: Record<string, unknown>) => ({
    chapters: CHAPTERS[String(args?.bookId ?? "")] ?? [],
  }),
  list_chapter_pages: (args?: Record<string, unknown>) => ({
    pages: pagesFor(String(args?.chapterId ?? "ch")),
  }),
  // 资源通道：resolve → issue → fetch 是三步；issue 返回的 URL 指向下面的
  // fetch 垫片，由它合成一张占位页图（不做真实图，只验证布局与加载态）。
  resolve_page_resource: (args?: Record<string, unknown>) => {
    const pageId = String(args?.pageId ?? "page");
    return { resource_id: `page-original-${pageId}`, revision: "rev-1" };
  },
  issue_resource_url: (args?: Record<string, unknown>) => {
    const resourceId = String(args?.resourceId ?? "resource");
    return {
      url: `nm-mock-res://${encodeURIComponent(resourceId)}/rev-1`,
      size: 4096,
      opaque_id: `opaque-${resourceId}`,
    };
  },
  revoke_ref: { revoked: true },
  list_regions: () => ({
    regions: [
      { region_id: "region-1", region_type: "dialogue", sfx_policy: "preserve", origin: "machine", revision_no: 1 },
      { region_id: "region-2", region_type: "narration", sfx_policy: "preserve", origin: "machine", revision_no: 1 },
      { region_id: "region-3", region_type: "sfx", sfx_policy: "translate", origin: "manual", revision_no: 2 },
    ],
    page_size: { width: 1440, height: 2048 },
  }),
  library_start_run: { run_id: "run-mock-1", status: "running" },
  library_get_run_snapshot: {
    run_id: "run-mock-1",
    command: "translate_untranslated",
    scope: { kind: "chapter", chapter_id: "ch-mh-12" },
    status: "running",
  },
  library_get_task_projection: {
    run_id: "run-mock-1",
    run_status: "running",
    run_title: "翻译 · 第 012 话",
    overall_progress: 0.4,
    current_page_id: "ch-mh-12-p3",
    current_step_type: "translate",
    step_flow: [
      { type: "ocr", label: "识别", state: "done" },
      { type: "translate", label: "翻译", state: "running" },
      { type: "typeset", label: "排版", state: "queued" },
    ],
    rows: pagesFor("ch-mh-12").map((page, index) => ({
      page_id: page.page_id,
      page_order: page.sort_order,
      filename: page.source_filename,
      status: index < 2 ? "completed" : index === 2 ? "running" : "waiting",
      is_locked: false,
      is_pipeline_current: index === 2,
      error_code: null,
    })),
    tasks: pagesFor("ch-mh-12").map((page, index) => ({
      task_id: `task-${page.page_id}`,
      page_id: page.page_id,
      status: index < 2 ? "completed" : index === 2 ? "running" : "waiting",
      error_code: null,
      steps: [
        {
          step_run_id: `step-${page.page_id}`,
          step_type: "translate",
          status: index < 2 ? "completed" : index === 2 ? "running" : "waiting",
          retry_no: 0,
          error_code: null,
          provider: "mock-provider",
          model: "mock-model",
          device: "cpu",
        },
      ],
    })),
    counts: { total: 6, completed: 2, failed: 0, skipped: 0, blocked: 0, waiting: 3, processing: 1 },
    blocked_reasons: [],
    controls: {
      can_pause: true,
      can_stop: true,
      can_continue: false,
      can_restart: false,
      can_abandon: true,
      can_retry_failed: false,
    },
  },
  list_region_revisions: [],
  settings_get: { settings: {} },
  library_get_reader_projection: (args?: Record<string, unknown>) => {
    const chapterId = String(args?.chapterId ?? "ch-mh-12");
    const pages = pagesFor(chapterId).map((page, index) => ({
      page_id: page.page_id,
      order: index,
      width_px: 1440,
      height_px: 2048,
      original: {
        resource_ref: { resource_id: `page-original-${page.page_id}`, revision: "rev-1" },
        artifact_revision_id: "artifact-1",
        sha256: "0".repeat(64),
      },
      translated: {
        resource_ref: null,
        artifact_revision_id: null,
        rendered_from_revision_id: null,
        current_source_revision_id: null,
        sha256: null,
      },
    }));
    return {
      book_id: "book-mist-harbor",
      chapter_id: chapterId,
      mode: "original",
      layout: "rtl",
      pages,
      saved_progress: null,
      initial_position: { page_id: pages[0].page_id, scroll_offset_y: 0 },
    };
  },
  library_save_reading_progress: {
    book_id: "book-mist-harbor",
    chapter_id: "ch-mh-12",
    mode: "original",
    last_page_id: "ch-mh-12-p1",
    scroll_offset_y: 0,
    progress_percent: 16,
    last_read_at: iso(1),
    total_read_seconds: 120,
  },
};

const mockInvoke: InvokeFn = (command, args) => {
  if (Object.prototype.hasOwnProperty.call(EMPTY_READS, command)) {
    const value = EMPTY_READS[command];
    return Promise.resolve(typeof value === "function" ? value(args) : value);
  }
  return Promise.reject(new Error(`MOCK_DENIED:${command}`));
};

/* ------------------------------------------------------------------ *
 * 资源通道 fetch 垫片
 *
 * 真实运行时页图走 HTTP：`${url}?chunk=N`。dev 环境没有 host 的
 * `http://m2res.localhost`，所以 issue 返回自定义 scheme
 * `nm-mock-res://<resource>/<rev>`，由这里的 fetch 包装器合成一张占位页图。
 * 一张图 < 一个 chunk（issue 里 size 固定 4096），因此只会取 chunk 0。
 * ------------------------------------------------------------------ */

const MOCK_SCHEME = "nm-mock-res://";
let placeholderPage: Blob | null = null;

function drawPlaceholderPage(): Promise<Blob> {
  if (placeholderPage) return Promise.resolve(placeholderPage);
  const canvas = document.createElement("canvas");
  canvas.width = 720;
  canvas.height = 1024;
  const ctx = canvas.getContext("2d");
  if (!ctx) {
    placeholderPage = new Blob([], { type: "image/png" });
    return Promise.resolve(placeholderPage);
  }
  // 纸张底色与三条分格 + 两个对话气泡：只是让"页图已加载"这件事可见，
  // 不含任何作品内容。
  ctx.fillStyle = "#f2f0ea";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.strokeStyle = "#c9c5ba";
  ctx.lineWidth = 2;
  ctx.strokeRect(24, 24, canvas.width - 48, canvas.height - 48);
  ctx.fillStyle = "#dcd8cd";
  ctx.fillRect(56, 120, 300, 260);
  ctx.fillRect(380, 120, 284, 180);
  ctx.fillRect(56, 420, 608, 220);
  ctx.fillStyle = "#fffdf8";
  ctx.strokeStyle = "#9b9689";
  ctx.beginPath();
  ctx.ellipse(200, 250, 110, 70, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();
  ctx.beginPath();
  ctx.ellipse(500, 760, 130, 80, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = "#6b675e";
  ctx.font = "600 16px Consolas, monospace";
  ctx.fillText("DEV MOCK PAGE — NOT A REAL MANGA PAGE", 56, 980);

  return new Promise<Blob>((resolve) => {
    canvas.toBlob((blob) => {
      placeholderPage = blob ?? new Blob([], { type: "image/png" });
      resolve(placeholderPage);
    }, "image/png");
  });
}

function installResourceFetchShim(): void {
  if (typeof window === "undefined") return;
  const win = window as unknown as { fetch: typeof fetch; __nmMockFetch?: boolean };
  if (win.__nmMockFetch) return;
  win.__nmMockFetch = true;
  const original = win.fetch.bind(window);
  win.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    const url =
      typeof input === "string" ? input : input instanceof URL ? input.href : input.url;
    if (url.startsWith(MOCK_SCHEME)) {
      const blob = await drawPlaceholderPage();
      return new Response(blob, { status: 200, headers: { "content-type": "image/png" } });
    }
    return original(input as RequestInfo, init);
  }) as typeof fetch;
}

function renderBadge(): void {
  if (typeof document === "undefined" || document.getElementById("dev-mock-badge")) return;
  const badge = document.createElement("div");
  badge.id = "dev-mock-badge";
  badge.textContent = "浏览器预览 · 假数据";
  badge.title =
    "Tauri IPC 未连接，本页数据来自 dev mock（src/dev/devMockBridge.ts），仅用于 UI 验证，不代表产品事实";
  badge.style.cssText = [
    "position:fixed",
    "right:10px",
    "bottom:10px",
    "z-index:2147483647",
    "padding:4px 9px",
    "border-radius:8px",
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
  installResourceFetchShim();
  renderBadge();
  console.info("[dev-mock] Tauri IPC 垫片已安装：界面可预览，数据为假（仅 UI 验证用）。");
}
