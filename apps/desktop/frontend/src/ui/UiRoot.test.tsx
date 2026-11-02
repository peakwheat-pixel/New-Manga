// @vitest-environment jsdom
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { UiRoot } from "./UiRoot";
import type { RuntimeClients } from "./types";

let root: Root | undefined;
let container: HTMLDivElement | undefined;

function makeClients(): RuntimeClients {
  const library = {
    corePing: vi.fn(async () => ({
      status: "ok",
      protocol_version: { major: 2, minor: 1 },
      capabilities: [],
    })),
    listBooks: vi.fn(async () => []),
    listChapters: vi.fn(async () => []),
    listChapterPages: vi.fn(async () => []),
    resolvePageResource: vi.fn(async () => ({ resource_id: "res-1", revision: "rev-1" })),
    listRecycleBinBooks: vi.fn(async () => []),
    createBook: vi.fn(async () => ({
      book_id: "b-new",
      title: "新作品",
      original_title: "",
      is_favorite: false,
      is_archived: false,
      page_count: null,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    })),
  };
  const settings = {
    getSfxSection: vi.fn(async () => null),
    getSfxPolicy: vi.fn(async () => ({ enabled: false })),
    listProviderProfiles: vi.fn(async () => []),
    listNetworkProfiles: vi.fn(async () => []),
    listPlugins: vi.fn(async () => ({ global_enabled: false, plugins: [] })),
  };
  return {
    invoke: vi.fn(async () => null),
    library,
    workbench: {},
    region: {},
    resource: {},
    reader: {},
    settings,
  } as unknown as RuntimeClients;
}

function mount(clients: RuntimeClients) {
  container = document.createElement("div");
  document.body.appendChild(container);
  root = createRoot(container);
  act(() => {
    root?.render(<UiRoot clients={clients} />);
  });
  return container;
}

function keydown(init: KeyboardEventInit) {
  act(() => {
    window.dispatchEvent(new window.KeyboardEvent("keydown", { bubbles: true, ...init }));
  });
}

beforeEach(() => {
  document.body.innerHTML = "";
  window.localStorage.clear();
  delete document.documentElement.dataset.theme;
  delete document.documentElement.dataset.view;
});

afterEach(() => {
  act(() => root?.unmount());
  root = undefined;
  container = undefined;
});

describe("UiRoot (v2 runtime root)", () => {
  it("mounts the shelf page by default and marks the v2 root scope", () => {
    const host = mount(makeClients());
    expect(host.querySelector('[data-testid="app-root"]')).not.toBeNull();
    expect(host.querySelector('[data-testid="page-shelf"]')).not.toBeNull();
    expect(document.documentElement.dataset.view).toBe("app");
    expect(document.documentElement.dataset.theme).toBe("dark");
  });

  it("switches all four pages with Ctrl/Cmd + 1..4", () => {
    const host = mount(makeClients());
    keydown({ key: "2", ctrlKey: true });
    expect(host.querySelector('[data-testid="page-workbench"]')).not.toBeNull();
    keydown({ key: "3", ctrlKey: true });
    expect(host.querySelector('[data-testid="page-reader"]')).not.toBeNull();
    keydown({ key: "4", ctrlKey: true });
    expect(host.querySelector('[data-testid="page-settings"]')).not.toBeNull();
    keydown({ key: "1", ctrlKey: true });
    expect(host.querySelector('[data-testid="page-shelf"]')).not.toBeNull();
  });

  it("opens and closes the global command palette with Ctrl+K and Escape", () => {
    const host = mount(makeClients());
    keydown({ key: "k", ctrlKey: true });
    expect(host.querySelector('[data-testid="command-palette"]')).not.toBeNull();
    // 命令面板里必须含四页导航 + 主题切换，否则入口是假的。
    for (const id of ["go-shelf", "go-workbench", "go-reader", "go-settings", "toggle-theme"]) {
      expect(document.querySelector(`[data-testid="command-item-${id}"]`)).not.toBeNull();
    }
    keydown({ key: "Escape" });
    expect(host.querySelector('[data-testid="command-palette"]')).toBeNull();
  });

  it("runs a palette command to navigate", () => {
    const host = mount(makeClients());
    keydown({ key: "k", ctrlKey: true });
    const item = document.querySelector<HTMLButtonElement>('[data-testid="command-item-go-settings"]')!;
    act(() => {
      item.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
    });
    expect(host.querySelector('[data-testid="page-settings"]')).not.toBeNull();
    expect(host.querySelector('[data-testid="command-palette"]')).toBeNull();
  });

  it("flips the html data-theme attribute so the CSS token layer follows", () => {
    const host = mount(makeClients());
    const toggle = host.querySelector<HTMLButtonElement>('[data-testid="theme-toggle"]')!;
    act(() => {
      toggle.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
    });
    expect(document.documentElement.dataset.theme).toBe("light");
    act(() => {
      host.querySelector<HTMLButtonElement>('[data-testid="theme-toggle"]')!.dispatchEvent(
        new window.MouseEvent("click", { bubbles: true }),
      );
    });
    expect(document.documentElement.dataset.theme).toBe("dark");
  });

  it("keeps the runtime on exactly one UI: no legacy page container is imported", () => {
    // 这条是产品"单一 UI"的机械守卫：运行时根与 App 一旦重新 import 历史
    // 内联样式页面容器，四页就会重新长成两套外观（本项目已发生过一次）。
    const uiRoot = readFileSync(resolve(process.cwd(), "src/ui/UiRoot.tsx"), "utf8");
    const legacyImport = /(shell\/AppShell|bookshelf\/BookshelfPage|workbench\/WorkbenchPage|reader\/ReaderPage|settings\/SettingsPage)/;
    expect(uiRoot).not.toMatch(legacyImport);

    const app = readFileSync(resolve(process.cwd(), "src/App.tsx"), "utf8");
    // AppShell 只允许出现在 ?view=legacy 的显式回退分支里。
    expect(app).toMatch(/legacyRequested\s*\?\s*<AppShell/);
    expect(app).toMatch(/<UiRoot invoke=\{safeInvoke\}/);
    // 默认（生产窗）分支不得再渲染 AppShell。
    expect(app).not.toMatch(/return\s*<AppShell invoke=\{safeInvoke\}\s*\/>\s*;/);
  });
});
