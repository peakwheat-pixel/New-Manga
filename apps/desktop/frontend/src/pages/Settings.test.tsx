// @vitest-environment jsdom
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { LibraryClient } from "../library/client";
import { ReaderClient } from "../reader/client";
import { RegionClient } from "../region/client";
import { ResourceChannelClient } from "../resourceChannel/client";
import { SettingsClient } from "../settings/client";
import { WorkbenchClient } from "../workbench/client";
import type { InvokeFn, PageChrome, PageRuntime, RuntimeClients } from "../ui/types";
import { Settings } from "./Settings";

/**
 * UIUX-V2-RUNTIME-1 / 设置页 v2 运行时接线。
 *
 * 覆盖：整页加载态、`settings_get` 失败的错误码与重试、12 个分节的切换与
 * 键盘 roving tabindex（含点击后焦点、Home/End）、以及"没有 runtime 的静态
 * 预览不展示任何设置值"。
 */

let root: Root | undefined;
let container: HTMLDivElement | undefined;
let host: HTMLDivElement | undefined;

const ALL_SECTIONS = [
  "provider",
  "network",
  "ocr",
  "translation",
  "inpaint",
  "typeset",
  "model_gpu",
  "task_concurrency",
  "cache_revision",
  "recycle_bin",
  "backup_restore",
  "plugins",
] as const;

function mount(element: React.ReactElement): HTMLDivElement {
  container = document.createElement("div");
  document.body.appendChild(container);
  root = createRoot(container);
  act(() => {
    root?.render(element);
  });
  return container;
}

async function flush(rounds = 4) {
  for (let index = 0; index < rounds; index += 1) {
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });
  }
}

function q(selector: string): HTMLElement | null {
  return host?.querySelector<HTMLElement>(selector) ?? null;
}

function text(selector: string): string {
  return q(selector)?.textContent?.trim() ?? "";
}

function click(selector: string) {
  const target = q(selector);
  if (!target) throw new Error(`missing element: ${selector}`);
  act(() => {
    target.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
  });
}

function keydown(selector: string, key: string) {
  const target = q(selector);
  if (!target) throw new Error(`missing element: ${selector}`);
  act(() => {
    target.dispatchEvent(new window.KeyboardEvent("keydown", { key, bubbles: true }));
  });
}

interface MockState {
  failSettingsGet: boolean;
  settingsGetGate?: Promise<unknown>;
  settings?: Record<string, unknown>;
}

function makeInvoke(state: MockState) {
  const calls: Array<{ command: string; args?: Record<string, unknown> }> = [];
  const invoke: InvokeFn = vi.fn(async (command: string, args?: Record<string, unknown>) => {
    calls.push({ command, args });
    switch (command) {
      case "settings_get": {
        if (state.settingsGetGate) await state.settingsGetGate;
        if (state.failSettingsGet) throw new Error("CORE_UNAVAILABLE");
        // 冻结语义：JSON null / 缺键 = 未设置，页面不得替 Core 编造值。
        return { settings: state.settings ?? {} };
      }
      case "settings_provider_profiles_list":
        return { profiles: [] };
      case "settings_network_profiles_list":
        return { profiles: [] };
      case "settings_provider_bindings_resolve":
        return { profile_id: null, source: null };
      case "cleanup_preview":
        return { targets: [], total_bytes: 0, pending_cleanups: 0 };
      case "library_list_recycle_bin_books":
        return [];
      case "backup_list":
        return [];
      case "plugins_list":
        return { global_enabled: false, plugin_root: "plugins", plugins: [] };
      case "plugins_audit_list":
        return [];
      default:
        return {};
    }
  });
  return { invoke, calls };
}

const mockFetch = (async () => ({
  ok: true,
  arrayBuffer: async () => new ArrayBuffer(4),
  text: async () => "",
})) as unknown as typeof fetch;

function makeRuntime(invoke: InvokeFn): PageRuntime {
  const chrome: PageChrome = {
    theme: "dark",
    activePage: "settings",
    onNavigate: vi.fn(),
    onToggleTheme: vi.fn(),
    onOpenCommand: vi.fn(),
    commandOpen: false,
    context: { bookId: null, chapterId: null },
    onOpenBook: vi.fn(),
    onSelectChapter: vi.fn(),
  };
  const clients: RuntimeClients = {
    invoke,
    library: new LibraryClient(invoke),
    workbench: new WorkbenchClient(invoke),
    region: new RegionClient(invoke),
    resource: new ResourceChannelClient(invoke, mockFetch),
    reader: new ReaderClient(invoke),
    settings: new SettingsClient(invoke),
  };
  return { chrome, clients };
}

function renderSettings(runtime?: PageRuntime) {
  host = mount(
    <Settings
      theme="dark"
      onNavigate={runtime?.chrome.onNavigate ?? vi.fn()}
      onToggleTheme={runtime?.chrome.onToggleTheme ?? vi.fn()}
      runtime={runtime}
    />,
  );
  return host;
}

beforeEach(() => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
});

afterEach(() => {
  act(() => root?.unmount());
  container?.remove();
  root = undefined;
  container = undefined;
  host = undefined;
  delete (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT;
});

describe("Settings v2 runtime", () => {
  it("shows the page-level loading state while settings_get is in flight", async () => {
    let release!: (value: unknown) => void;
    const gate = new Promise((resolve) => {
      release = resolve;
    });
    const state: MockState = { failSettingsGet: false, settingsGetGate: gate };
    const { invoke } = makeInvoke(state);
    renderSettings(makeRuntime(invoke));
    await flush(2);

    expect(q('[data-testid="settings-loading"]')).not.toBeNull();
    expect(q('[data-testid="settings-content-provider"]')).toBeNull();
    // 标题栏与分节导航在加载态就已经可用（外壳不随数据卸载）。
    expect(q('[data-testid="settings-titlebar"]')).not.toBeNull();
    expect(q('[data-testid="settings-category-ocr"]')).not.toBeNull();

    await act(async () => {
      release({ settings: {} });
      await Promise.resolve();
    });
    await flush();

    expect(q('[data-testid="settings-loading"]')).toBeNull();
    expect(q('[data-testid="settings-content-provider"]')).not.toBeNull();
  });

  it("shows the settings_get error code and recovers through the retry action", async () => {
    const state: MockState = { failSettingsGet: true };
    const { invoke, calls } = makeInvoke(state);
    renderSettings(makeRuntime(invoke));
    await flush();

    expect(q('[data-testid="settings-error"]')).not.toBeNull();
    expect(text('[data-testid="page-error-code"]')).toContain("CORE_UNAVAILABLE");
    // 失败时不得挂载任何 panel，避免把"读不到"渲染成"空设置"。
    expect(q('[data-testid="settings-content-provider"]')).toBeNull();
    expect(q('[data-testid="provider-profile-panel"]')).toBeNull();
    expect(calls.some((call) => call.command === "settings_provider_profiles_list")).toBe(false);

    state.failSettingsGet = false;
    click('[data-testid="page-error-retry"]');
    await flush();

    expect(q('[data-testid="settings-error"]')).toBeNull();
    expect(q('[data-testid="settings-content-provider"]')).not.toBeNull();
    // 页脚展示 sfx 分节的真实读取结果：JSON null / 缺键 = 未设置，不编造默认值。
    expect(text('[data-testid="settings-sfx-policy"]')).toContain("未设置（按 Core 默认）");
    // readiness 探针就是一次 settings_get({section:"sfx"})。
    expect(
      calls.some((call) => call.command === "settings_get" && call.args?.section === "sfx"),
    ).toBe(true);
  });

  it("shows the effective SFX policy from the settings_get projection", async () => {
    const state: MockState = {
      failSettingsGet: false,
      settings: { sfx: { policy: "translate" } },
    };
    const { invoke } = makeInvoke(state);
    renderSettings(makeRuntime(invoke));
    await flush();

    expect(text('[data-testid="settings-sfx-policy"]')).toBe("SFX 策略 · 翻译 (translate)");
  });

  it("exposes the same command trigger as the other primary pages", async () => {
    const state: MockState = { failSettingsGet: false };
    const { invoke } = makeInvoke(state);
    const runtime = makeRuntime(invoke);
    renderSettings(runtime);
    await flush();

    const trigger = q('[data-testid="command-trigger"]');
    expect(trigger).not.toBeNull();
    expect(trigger?.getAttribute("aria-haspopup")).toBe("dialog");
    expect(trigger?.getAttribute("aria-expanded")).toBe("false");
    expect(text('[data-testid="command-trigger"]')).toContain("Ctrl");
    act(() => {
      trigger?.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
    });
    expect(runtime.chrome.onOpenCommand).toHaveBeenCalledTimes(1);

    // 命令面板打开时：aria-expanded 跟随真实状态，导航这层低优先级亚克力
    // 必须降级成 .nm-acrylic-off（页面 0 层 + 模态 1 层 ≤ 2）。
    const openRuntime: PageRuntime = {
      ...runtime,
      chrome: { ...runtime.chrome, commandOpen: true },
    };
    await act(async () => {
      root?.render(
        <Settings
          theme="dark"
          onNavigate={openRuntime.chrome.onNavigate}
          onToggleTheme={openRuntime.chrome.onToggleTheme}
          runtime={openRuntime}
        />,
      );
    });
    expect(q('[data-testid="command-trigger"]')?.getAttribute("aria-expanded")).toBe("true");
    expect(q('[data-testid="settings-section-nav"]')?.classList.contains("nm-acrylic-off")).toBe(true);
    expect(host?.querySelectorAll(".nm-acrylic, .nm-acrylic-24, .nm-acrylic-strong")).toHaveLength(0);
  });

  it("switches between all twelve sections by click and keeps a roving tabindex", async () => {
    const state: MockState = { failSettingsGet: false };
    const { invoke } = makeInvoke(state);
    renderSettings(makeRuntime(invoke));
    await flush();

    // 12 个分节按冻结顺序渲染，且只有当前分节在 Tab 序列里。
    expect(host?.querySelectorAll('[data-testid^="settings-category-"]')).toHaveLength(12);
    expect(q('[data-testid="settings-category-provider"]')?.getAttribute("tabindex")).toBe("0");
    expect(q('[data-testid="settings-category-ocr"]')?.getAttribute("tabindex")).toBe("-1");

    for (const section of ALL_SECTIONS) {
      click(`[data-testid="settings-category-${section}"]`);
      await flush(2);
      expect(q(`[data-testid="settings-content-${section}"]`)).not.toBeNull();
      expect(q('[data-testid="settings-error"]')).toBeNull();
      // 切分节只换内容带，外壳与导航不卸载。
      expect(q('[data-testid="settings-content-panel"]')).not.toBeNull();
    }

    // 每个分节挂的是既有 panel（抽查：OCR / 翻译 / 回收站 / 备份）。
    click('[data-testid="settings-category-ocr"]');
    await flush();
    expect(q('[data-testid="ocr-settings-panel"]')).not.toBeNull();
    click('[data-testid="settings-category-translation"]');
    await flush();
    expect(q('[data-testid="sfx-policy-control"]')).not.toBeNull();
    click('[data-testid="settings-category-recycle_bin"]');
    await flush();
    expect(q('[data-testid="recycle-bin-settings-panel"]')).not.toBeNull();
    click('[data-testid="settings-category-backup_restore"]');
    await flush();
    expect(q('[data-testid="backup-settings-panel"]')).not.toBeNull();
  });

  it("moves the section tab with ArrowDown / Home / End and focuses the real tab", async () => {
    const state: MockState = { failSettingsGet: false };
    const { invoke } = makeInvoke(state);
    renderSettings(makeRuntime(invoke));
    await flush();

    // jsdom 的合成 MouseEvent 不会像真实浏览器那样在 mousedown 时给按钮上焦点，
    // 这里显式 focus 当前 tab 来模拟"键盘用户已经在 tablist 里"的起点。
    const providerTab = q('[data-testid="settings-category-provider"]');
    expect(providerTab).not.toBeNull();
    act(() => {
      providerTab?.focus();
    });
    expect(document.activeElement?.getAttribute("data-testid")).toBe("settings-category-provider");

    keydown('[data-testid="settings-category-provider"]', "ArrowDown");
    expect(q('[data-testid="settings-category-network"]')?.getAttribute("aria-selected")).toBe("true");
    expect(q('[data-testid="settings-category-network"]')?.getAttribute("tabindex")).toBe("0");
    expect(document.activeElement?.getAttribute("data-testid")).toBe("settings-category-network");

    keydown('[data-testid="settings-category-network"]', "End");
    expect(q('[data-testid="settings-category-plugins"]')?.getAttribute("aria-selected")).toBe("true");
    expect(document.activeElement?.getAttribute("data-testid")).toBe("settings-category-plugins");

    keydown('[data-testid="settings-category-plugins"]', "Home");
    expect(q('[data-testid="settings-category-provider"]')?.getAttribute("aria-selected")).toBe("true");
    expect(document.activeElement?.getAttribute("data-testid")).toBe("settings-category-provider");

    keydown('[data-testid="settings-category-provider"]', "ArrowUp");
    expect(q('[data-testid="settings-category-plugins"]')?.getAttribute("aria-selected")).toBe("true");
    // 收尾：把最后一个分节（plugins）panel 的异步读取在 act 内跑完。
    await flush();
  });

  it("keeps the static design preview honest instead of fabricating values", () => {
    renderSettings(undefined);

    expect(q('[data-testid="page-settings"]')).not.toBeNull();
    expect(q('[data-testid="settings-titlebar"]')).not.toBeNull();
    expect(host?.querySelectorAll('[data-testid^="settings-category-"]')).toHaveLength(12);
    // 无 runtime：不渲染任何 panel，只显式标注"预览无 IPC 通道"。
    expect(q('[data-testid="settings-preview-blocked"]')).not.toBeNull();
    expect(text('[data-testid="settings-preview-blocked"]')).toContain("没有真实 IPC 设置通道");
    expect(q('[data-testid="ocr-settings-panel"]')).toBeNull();
    // 侧栏页脚的状态只属于真实通道，预览里不显示。
    expect(q('[data-testid="settings-channel-status"]')).toBeNull();
    // 命令入口需要 chrome.onOpenCommand；静态预览没有运行时，不渲染假按钮。
    expect(q('[data-testid="command-trigger"]')).toBeNull();

    click('[data-testid="settings-category-ocr"]');
    expect(text('[data-testid="settings-section-title"]')).toBe("OCR");
  });
});
