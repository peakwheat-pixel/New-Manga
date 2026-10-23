import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  SettingsClientError,
  type PluginAuditEvent,
  type PluginEntry,
  type PluginsSnapshot,
} from "./client";
import { PluginSettingsPanel, type PluginPanelClientLike } from "./PluginSettingsPanel";

/**
 * PLUGIN-RUNTIME-1 §4.1–§4.4 / AC5 — the plugin management face:
 * real `plugins_list` snapshot, default-OFF global switch, per-plugin
 * switches (rejected plugins can never be toggled), the audit ledger, the
 * directory opener, and typed error copy. No fake controls: every button maps
 * to one production command.
 */

function plugin(id: string, overrides: Partial<PluginEntry> = {}): PluginEntry {
  return {
    plugin_id: id,
    status: "disabled",
    enabled: false,
    name: `Plugin ${id}`,
    version: "1.0.0",
    description: "",
    hooks: ["after_detect"],
    reason: null,
    ...overrides,
  };
}

function event(id: string, overrides: Partial<PluginAuditEvent> = {}): PluginAuditEvent {
  return {
    event_id: id,
    plugin_id: "acme-detect",
    event_type: "load_ok",
    hook_name: null,
    detail: {},
    occurred_at: "2026-10-23T06:40:00+00:00",
    ...overrides,
  };
}

function snapshot(plugins: PluginEntry[], globalEnabled = false): PluginsSnapshot {
  return { global_enabled: globalEnabled, plugins };
}

class FakePluginClient implements PluginPanelClientLike {
  snapshotValue: PluginsSnapshot;
  auditValue: PluginAuditEvent[];
  failList: unknown = null;
  failSet: unknown = null;
  globalCalls: boolean[] = [];
  pluginCalls: Array<{ plugin_id: string; enabled: boolean }> = [];
  openCalls = 0;

  constructor(snapshotValue: PluginsSnapshot, auditValue: PluginAuditEvent[] = []) {
    this.snapshotValue = snapshotValue;
    this.auditValue = auditValue;
  }

  async listPlugins(): Promise<PluginsSnapshot> {
    if (this.failList) throw this.failList;
    return this.snapshotValue;
  }

  async setPluginsEnabled(enabled: boolean): Promise<{ global_enabled: boolean }> {
    this.globalCalls.push(enabled);
    if (this.failSet) throw this.failSet;
    this.snapshotValue = { ...this.snapshotValue, global_enabled: enabled };
    return { global_enabled: enabled };
  }

  async setPluginEnabled(pluginId: string, enabled: boolean): Promise<{ plugin_id: string; enabled: boolean }> {
    this.pluginCalls.push({ plugin_id: pluginId, enabled });
    if (this.failSet) throw this.failSet;
    this.snapshotValue = {
      ...this.snapshotValue,
      plugins: this.snapshotValue.plugins.map((item) =>
        item.plugin_id === pluginId
          ? { ...item, enabled, status: enabled ? "enabled" : "disabled" }
          : item,
      ),
    };
    return { plugin_id: pluginId, enabled };
  }

  async listPluginAudit(): Promise<PluginAuditEvent[]> {
    return this.auditValue;
  }

  async openPluginDirectory(): Promise<void> {
    this.openCalls += 1;
  }
}

describe("PluginSettingsPanel (PLUGIN-RUNTIME-1 §4.1–§4.4)", () => {
  let dom: JSDOM;
  let container: HTMLDivElement;
  let root: Root;

  beforeEach(() => {
    dom = new JSDOM("<!doctype html><html><body></body></html>", { url: "http://localhost" });
    vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
    vi.stubGlobal("window", dom.window);
    vi.stubGlobal("document", dom.window.document);
    vi.stubGlobal("navigator", dom.window.navigator);
    vi.stubGlobal("HTMLElement", dom.window.HTMLElement);
    container = dom.window.document.createElement("div");
    dom.window.document.body.appendChild(container);
    root = createRoot(container);
  });

  afterEach(() => {
    act(() => {
      root.unmount();
    });
    vi.unstubAllGlobals();
  });

  const q = (selector: string) => container.querySelector(selector) as HTMLElement | null;
  const button = (testId: string) => q(`[data-testid="${testId}"]`) as HTMLButtonElement | null;
  const checkbox = (testId: string) => q(`[data-testid="${testId}"]`) as HTMLInputElement | null;

  const render = async (client: PluginPanelClientLike) => {
    await act(async () => {
      root.render(<PluginSettingsPanel client={client} />);
    });
    await act(async () => {
      await Promise.resolve();
    });
  };

  it("renders the loading skeleton first", async () => {
    const client: PluginPanelClientLike = {
      listPlugins: vi.fn(() => new Promise<PluginsSnapshot>(() => {})),
      setPluginsEnabled: vi.fn(),
      setPluginEnabled: vi.fn(),
      listPluginAudit: vi.fn(),
      openPluginDirectory: vi.fn(),
    };
    act(() => {
      root.render(<PluginSettingsPanel client={client} />);
    });
    expect(q('[data-testid="plugin-settings-loading"]')).not.toBeNull();
  });

  it("renders discovered plugins with status, hooks and the rejection reason", async () => {
    const client = new FakePluginClient(
      snapshot([
        plugin("acme-detect", { status: "enabled", enabled: true }),
        plugin("acme-broken", {
          status: "rejected",
          reason: "PLUGIN_PERMISSIONS_UNSUPPORTED: this release only loads permissions: []",
        }),
      ]),
    );
    await render(client);

    expect(q('[data-testid="plugin-settings-item-acme-detect"]')).not.toBeNull();
    expect(q('[data-testid="plugin-settings-status-acme-detect"]')?.textContent).toContain("已启用");
    expect(q('[data-testid="plugin-settings-status-acme-broken"]')?.textContent).toContain("已拒绝");
    expect(q('[data-testid="plugin-settings-reason-acme-broken"]')?.textContent).toContain(
      "PERMISSIONS_UNSUPPORTED",
    );
    // A rejected plugin can never be toggled on.
    expect(button("plugin-settings-toggle-acme-broken")).not.toBeNull();
    expect(button("plugin-settings-toggle-acme-broken")?.disabled).toBe(true);
    expect(q('[data-testid="plugin-settings-policy-note"]')?.textContent).toContain("permissions: []");
  });

  it("shows the empty state when the plugin root has no plugins", async () => {
    await render(new FakePluginClient(snapshot([])));
    expect(q('[data-testid="plugin-settings-empty"]')).not.toBeNull();
  });

  it("toggles the global kill switch through plugins_set_enabled", async () => {
    const client = new FakePluginClient(snapshot([plugin("acme-detect")]));
    await render(client);
    const toggle = checkbox("plugin-settings-global-toggle");
    expect(toggle?.checked).toBe(false);

    await act(async () => {
      toggle!.click();
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(client.globalCalls).toEqual([true]);
    expect(q('[data-testid="plugin-settings-notice"]')?.textContent).toContain("插件系统已启用");
  });

  it("enables one plugin through plugins_set_plugin_enabled", async () => {
    const client = new FakePluginClient(snapshot([plugin("acme-detect")]));
    await render(client);
    expect(client.pluginCalls).toEqual([]);

    await act(async () => {
      button("plugin-settings-toggle-acme-detect")?.click();
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(client.pluginCalls).toEqual([{ plugin_id: "acme-detect", enabled: true }]);
    expect(q('[data-testid="plugin-settings-notice"]')?.textContent).toContain("已启用插件 acme-detect");
  });

  it("opens the plugin directory through the Rust-local command", async () => {
    const client = new FakePluginClient(snapshot([]));
    await render(client);
    await act(async () => {
      button("plugin-settings-open-dir-btn")?.click();
      await Promise.resolve();
    });
    expect(client.openCalls).toBe(1);
    expect(q('[data-testid="plugin-settings-notice"]')?.textContent).toContain("已打开插件目录");
  });

  it("renders the audit ledger events", async () => {
    const client = new FakePluginClient(
      snapshot([]),
      [
        event("e1", { event_type: "enabled", plugin_id: "__global__" }),
        event("e2", { event_type: "hook_invoked", hook_name: "after_detect" }),
        event("e3", { event_type: "plugin_error", hook_name: "after_detect" }),
      ],
    );
    await render(client);
    const list = q('[data-testid="plugin-settings-audit-list"]');
    expect(list).not.toBeNull();
    expect(list?.textContent).toContain("已启用");
    expect(list?.textContent).toContain("Hook 调用");
    expect(list?.textContent).toContain("Hook 错误");
  });

  it("maps CORE_UNAVAILABLE loads and PLUGIN_NOT_LOADED actions to fixed copy", async () => {
    const failing = new FakePluginClient(snapshot([]));
    failing.failList = new SettingsClientError("CORE_UNAVAILABLE", "no core");
    await render(failing);
    expect(q('[data-testid="plugin-settings-load-error"]')?.textContent).toContain("插件服务当前不可用");

    act(() => {
      root.unmount();
    });
    root = createRoot(container);
    const toggling = new FakePluginClient(snapshot([plugin("acme-detect")]));
    toggling.failSet = new SettingsClientError("PLUGIN_NOT_LOADED", "manifest rejected");
    await render(toggling);
    await act(async () => {
      button("plugin-settings-toggle-acme-detect")?.click();
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(q('[data-testid="plugin-settings-error"]')?.textContent).toContain("未通过校验");
  });
});
