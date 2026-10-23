import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { DisabledSection, DISABLED_SECTION_REASON } from "./DisabledSection";
import { PLUGIN_SECTION_DESCRIPTION, PLUGIN_SECTION_REASON } from "./SettingsPage";

/**
 * SETTINGS-OPEN-C-3-PLUGIN §4.5 — the plugin partition stays "未开放" but its
 * placeholder carries the frozen read-only copy and never renders an operable
 * control (no enable/reload/open-directory without a runtime).
 */
describe("DisabledSection (SETTINGS-OPEN-C-3-PLUGIN §4.5)", () => {
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

  const q = (testId: string) => container.querySelector(`[data-testid="${testId}"]`) as HTMLElement | null;

  it("renders the frozen plugin copy with no operable control", () => {
    act(() => {
      root.render(
        <DisabledSection
          testId="settings-disabled-section-plugins"
          title="Plugin / Hooks"
          reason={PLUGIN_SECTION_REASON}
          description={PLUGIN_SECTION_DESCRIPTION}
          showPlaceholderControl={false}
        />,
      );
    });
    const section = q("settings-disabled-section-plugins");
    expect(section).not.toBeNull();
    expect(section?.getAttribute("aria-disabled")).toBe("true");
    expect(section?.getAttribute("data-disabled-reason")).toBe(PLUGIN_SECTION_REASON);
    expect(q("settings-disabled-section-plugins-reason")?.textContent).toContain(
      "插件系统尚未实现",
    );
    expect(q("settings-disabled-section-plugins-description")?.textContent).toContain(
      "当前版本未安装插件运行时",
    );
    // §4.5: no enable/reload/open-directory button can exist without a runtime.
    expect(section?.querySelector("button")).toBeNull();
  });

  it("keeps the generic placeholder control for sections without a dedicated face", () => {
    act(() => {
      root.render(
        <DisabledSection testId="generic-disabled-section" title="示例分区" />,
      );
    });
    const section = q("generic-disabled-section");
    expect(section?.getAttribute("data-disabled-reason")).toBe(DISABLED_SECTION_REASON);
    const button = section?.querySelector("button");
    expect(button).not.toBeNull();
    expect(button?.disabled).toBe(true);
    expect(q("generic-disabled-section-description")).toBeNull();
  });
});
