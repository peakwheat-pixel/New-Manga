// @vitest-environment jsdom
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import App from "../App";
import { DesignPreview } from "./DesignPreview";

let root: Root | undefined;
let container: HTMLDivElement | undefined;

function mount(element: React.ReactElement) {
  container = document.createElement("div");
  document.body.appendChild(container);
  root = createRoot(container);
  act(() => {
    root?.render(element);
  });
  return container;
}

function click(host: HTMLElement, selector: string) {
  const target = host.querySelector<HTMLElement>(selector);
  if (!target) throw new Error(`missing element: ${selector}`);
  act(() => {
    target.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
  });
}

beforeEach(() => {
  delete document.documentElement.dataset.theme;
  window.history.replaceState({}, "", "/");
});

afterEach(() => {
  act(() => root?.unmount());
  container?.remove();
  root = undefined;
  container = undefined;
  delete document.documentElement.dataset.theme;
});

describe("DesignPreview (v2 static skeleton)", () => {
  it("renders the shelf skeleton with titlebar, toolbar, five-column grid, detail panel and floating status", () => {
    const host = mount(<DesignPreview />);

    expect(host.querySelector('[data-testid="design-preview"]')?.getAttribute("data-page")).toBe("shelf");
    expect(host.querySelector('[data-testid="page-shelf"]')).not.toBeNull();
    expect(host.querySelector('[data-testid="shelf-titlebar"]')).not.toBeNull();
    expect(host.querySelector('[data-testid="shelf-toolbar"]')).not.toBeNull();
    expect(host.querySelectorAll('[data-testid="shelf-grid"] .nm-book-card')).toHaveLength(10);
    expect(host.querySelector('[data-testid="shelf-detail"]')).not.toBeNull();
    expect(host.querySelector('[data-testid="shelf-statusbar"]')).not.toBeNull();
    expect(host.querySelector('[data-testid="chapter-list"]')?.children.length).toBe(5);

    // The two declared acrylic layers fit the budget.
    expect(host.querySelectorAll(".nm-acrylic, .nm-acrylic-24, .nm-acrylic-strong")).toHaveLength(2);
    expect(host.querySelector('[data-testid="shelf-detail"]')?.classList.contains("nm-acrylic")).toBe(true);
    expect(host.querySelector('[data-testid="shelf-statusbar"]')?.classList.contains("nm-acrylic-24")).toBe(true);
  });

  it("opens the command palette as the third acrylic layer and downgrades the status bar", () => {
    const host = mount(<DesignPreview />);
    click(host, '[data-testid="command-trigger"]');

    expect(host.querySelector('[data-testid="command-palette"]')).not.toBeNull();
    expect(host.querySelector('[data-testid="command-backdrop"]')).not.toBeNull();
    expect(host.querySelector('[data-testid="shelf-statusbar"]')?.classList.contains("nm-acrylic-off")).toBe(true);
    expect(host.querySelector('[data-testid="shelf-detail"]')?.classList.contains("nm-acrylic")).toBe(true);
    expect(host.querySelector('[data-testid="command-palette"]')?.classList.contains("nm-acrylic-strong")).toBe(true);

    // Performance gate: never more than two live backdrop-filter layers.
    expect(host.querySelectorAll(".nm-acrylic, .nm-acrylic-24, .nm-acrylic-strong")).toHaveLength(2);

    act(() => {
      window.dispatchEvent(new window.KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
    });
    expect(host.querySelector('[data-testid="command-palette"]')).toBeNull();
    expect(host.querySelector('[data-testid="shelf-statusbar"]')?.classList.contains("nm-acrylic-24")).toBe(true);
  });

  it("switches to the workbench via the shelf tabs", () => {
    const host = mount(<DesignPreview />);
    click(host, '[data-testid="tab-workbench"]');

    expect(host.querySelector('[data-testid="design-preview"]')?.getAttribute("data-page")).toBe("workbench");
    expect(host.querySelector('[data-testid="page-workbench"]')).not.toBeNull();
    expect(host.querySelector('[data-testid="filmstrip"]')).not.toBeNull();
    expect(host.querySelector('[data-testid="workbench-canvas"]')).not.toBeNull();
    expect(host.querySelector('[data-testid="inspector"]')).not.toBeNull();
    expect(host.querySelector('[data-testid="pipeline"]')).not.toBeNull();
    expect(host.querySelector('[data-testid="canvas-stage"] [data-testid="page-placeholder"]')).not.toBeNull();
    expect(host.querySelectorAll('[data-testid="filmstrip"] .nm-filmstrip__item')).toHaveLength(18);
    expect(host.querySelectorAll('[data-testid="pipeline"] .nm-stage')).toHaveLength(10);
    expect(host.querySelector('[data-testid="inspector"]')?.classList.contains("nm-acrylic")).toBe(true);
    expect(host.querySelectorAll(".nm-acrylic, .nm-acrylic-24, .nm-acrylic-strong")).toHaveLength(1);

    // 一级切换栏必须在工作台上同样可用，否则只能靠画布里的单向后跳转。
    const wbTabs = host.querySelector('[data-testid="page-workbench"] [data-testid="tab-workbench"]');
    expect(wbTabs).not.toBeNull();
    expect(wbTabs?.getAttribute("data-active")).toBe("true");
    expect(host.querySelector('[data-testid="page-workbench"] [data-testid="tab-shelf"]')).not.toBeNull();
    expect(host.querySelector('[data-testid="page-workbench"] [data-testid="tab-reader"]')).not.toBeNull();
  });

  it("switches to the immersive reader via the shelf tabs", () => {
    const host = mount(<DesignPreview />);
    click(host, '[data-testid="tab-reader"]');

    expect(host.querySelector('[data-testid="design-preview"]')?.getAttribute("data-page")).toBe("reader");
    expect(host.querySelector('[data-testid="page-reader"]')).not.toBeNull();
    expect(host.querySelector('[data-testid="reader-top"]')?.classList.contains("nm-acrylic-24")).toBe(true);
    expect(host.querySelector('[data-testid="reader-bottom"]')?.classList.contains("nm-acrylic-24")).toBe(true);
    expect(host.querySelector('[data-testid="page-placeholder"]')).not.toBeNull();
    expect(host.querySelectorAll(".nm-acrylic, .nm-acrylic-24, .nm-acrylic-strong")).toHaveLength(2);

    // 阅读器浮层里也要有一级切换栏，且不能因此多出亚克力层。
    const rdTabs = host.querySelector('[data-testid="page-reader"] [data-testid="tab-reader"]');
    expect(rdTabs).not.toBeNull();
    expect(rdTabs?.getAttribute("data-active")).toBe("true");
    expect(host.querySelector('[data-testid="page-reader"] [data-testid="tab-shelf"]')).not.toBeNull();

    // Reader chrome is navigable back to the shelf.
    click(host, '[data-testid="reader-top"] [aria-label="返回书架"]');
    expect(host.querySelector('[data-testid="page-shelf"]')).not.toBeNull();
  });

  it("toggles dark and light themes through the real root attribute", () => {
    const host = mount(<DesignPreview />);
    expect(document.documentElement.dataset.theme).toBe("dark");

    click(host, '[data-testid="theme-toggle"]');
    expect(host.querySelector('[data-testid="design-preview"]')?.getAttribute("data-theme")).toBe("light");
    expect(document.documentElement.dataset.theme).toBe("light");

    click(host, '[data-testid="theme-toggle"]');
    expect(document.documentElement.dataset.theme).toBe("dark");
  });

  it("is reachable from the App entry with ?view=design", () => {
    window.history.replaceState({}, "", "/?view=design");
    const host = mount(<App />);
    expect(host.querySelector('[data-testid="design-preview"]')).not.toBeNull();
    expect(host.querySelector('[data-testid="page-shelf"]')).not.toBeNull();
  });
});
