import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { SettingsClient } from "./client";
import { DISABLED_SECTION_TEST_IDS, SETTINGS_CATEGORY_ORDER, SettingsPage } from "./SettingsPage";

/**
 * P15 AC1 — layout & category structure (AD-001 §5.2): 200px fixed
 * SettingsCategoryNav + SettingsContentPanel, twelve categories in the
 * frozen order, switching via React local state (no sub-route).
 * P15 AC2 — every non-frozen partition is visible, not operable, and
 * states the reason "等待 section schema 冻结".
 */

function makeInvoke() {
  return vi.fn(async (command: string) => {
    switch (command) {
      case "settings_provider_profiles_list":
        return { profiles: [] };
      case "settings_network_profiles_list":
        return { profiles: [] };
      case "settings_provider_bindings_resolve":
        return { profile_id: null, source: null };
      case "settings_network_profile_resolve":
        return { network_profile_id: null, mode: "Direct", source: "direct" };
      default:
        return {};
    }
  });
}

describe("SettingsPage layout & categories (AC1)", () => {
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

  const mount = (invoke: ReturnType<typeof makeInvoke>) => {
    act(() => {
      root.render(<SettingsPage client={new SettingsClient(invoke)} />);
    });
  };

  const q = (selector: string) => container.querySelector(selector) as HTMLElement | null;

  it("renders the fixed 200px category nav and the content panel", () => {
    mount(makeInvoke());
    const nav = q('[data-testid="settings-category-nav"]');
    expect(nav).not.toBeNull();
    expect(nav?.getAttribute("style") ?? nav?.style.width).toContain("200px");
    expect(q('[data-testid="settings-content-panel"]')).not.toBeNull();
  });

  it("renders the twelve categories in the frozen order with the frozen labels", () => {
    mount(makeInvoke());
    const buttons = Array.from(container.querySelectorAll('button[data-testid^="settings-category-"]'));
    const ids = buttons.map((b) => (b as HTMLElement).dataset.testid?.replace("settings-category-", ""));
    expect(ids).toEqual([...SETTINGS_CATEGORY_ORDER]);
    const labels = buttons.map((b) => (b as HTMLElement).textContent);
    expect(labels[0]).toContain("Provider");
    expect(labels[1]).toContain("网络/代理");
    expect(labels[2]).toContain("OCR");
    expect(labels[3]).toContain("翻译");
    expect(labels[4]).toContain("图片修复");
    expect(labels[5]).toContain("排版样式");
    expect(labels[6]).toContain("模型/GPU");
    expect(labels[7]).toContain("任务/并发");
    expect(labels[8]).toContain("缓存/Revision");
    expect(labels[9]).toContain("回收站");
    expect(labels[10]).toContain("备份/恢复");
    expect(labels[11]).toContain("Plugin/Hooks");
  });

  it("switches categories via local state only — no sub-route, no remount of the page", async () => {
    mount(makeInvoke());
    const page = q('[data-testid="settings-page"]');
    expect(page).not.toBeNull();

    const networkBtn = q('[data-testid="settings-category-network"]') as HTMLButtonElement;
    await act(async () => {
      networkBtn.click();
    });
    expect(q('[data-testid="settings-active-category"]')?.getAttribute("data-category-id")).toBe("network");
    expect(q('[data-testid="settings-content-network"]')).not.toBeNull();
    // The page container node is the SAME node across switches (no route
    // remount): the nav keeps its DOM identity.
    const navBefore = q('[data-testid="settings-category-nav"]');
    await act(async () => {
      (q('[data-testid="settings-category-provider"]') as HTMLButtonElement).click();
    });
    expect(q('[data-testid="settings-active-category"]')?.getAttribute("data-category-id")).toBe("provider");
    expect(q('[data-testid="settings-content-provider"]')).not.toBeNull();
    expect(q('[data-testid="settings-category-nav"]')).toBe(navBefore);
  });

  it("marks only the three open categories open; the rest carry the 未开放 badge", () => {
    mount(makeInvoke());
    const openFlags = SETTINGS_CATEGORY_ORDER.map(
      (id) => (q(`[data-testid="settings-category-${id}"]`) as HTMLElement).dataset.open,
    );
    expect(openFlags).toEqual([
      "true", // provider
      "true", // network
      "false", // ocr
      "true", // translation (hosts sfx.policy)
      "false",
      "false",
      "false",
      "false",
      "false",
      "false",
      "false",
      "false",
    ]);
    const ocrBtn = q('[data-testid="settings-category-ocr"]') as HTMLElement;
    expect(ocrBtn.textContent).toContain("未开放");
  });
});

describe("Disabled partitions: visible, not operable, reasoned (AC2)", () => {
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

  const mountAndSwitch = async (categoryId: string) => {
    const invoke = makeInvoke();
    act(() => {
      root.render(<SettingsPage client={new SettingsClient(invoke)} />);
    });
    await act(async () => {
      (container.querySelector(`[data-testid="settings-category-${categoryId}"]`) as HTMLButtonElement).click();
    });
  };

  /** The shared per-partition assertion: visible section + disabled control
   * + the frozen reason string. */
  const assertDisabledSection = (testId: string, expectedTitlePart: string) => {
    const section = container.querySelector(`[data-testid="${testId}"]`) as HTMLElement | null;
    expect(section).not.toBeNull();
    expect(section?.getAttribute("aria-disabled")).toBe("true");
    // Visible: the title text is rendered.
    const title = container.querySelector(`[data-testid="${testId}-title"]`) as HTMLElement | null;
    expect(title?.textContent ?? "").toContain(expectedTitlePart);
    // Reason: the frozen cause string.
    const reason = container.querySelector(`[data-testid="${testId}-reason"]`) as HTMLElement | null;
    expect(reason?.textContent ?? "").toContain("等待 section schema 冻结");
    // Not operable: no enabled interactive control inside the section.
    const buttons = Array.from(section?.querySelectorAll("button") ?? []);
    expect(buttons.length).toBeGreaterThan(0);
    for (const button of buttons) {
      expect((button as HTMLButtonElement).disabled).toBe(true);
    }
    // No input/select/textarea at all — nothing to type into.
    expect((section?.querySelectorAll("input, select, textarea") ?? []).length).toBe(0);
  };

  it("OCR partition is disabled with the frozen reason", async () => {
    await mountAndSwitch("ocr");
    assertDisabledSection(DISABLED_SECTION_TEST_IDS.ocr, "OCR");
  });

  it("translation-context partition is disabled inside the open translation category", async () => {
    await mountAndSwitch("translation");
    assertDisabledSection(DISABLED_SECTION_TEST_IDS.translationContext, "翻译参数 / 上下文策略");
    // The same category still hosts the open SFX control (AC2 open table).
    expect(container.querySelector('[data-testid="sfx-policy-control"]')).not.toBeNull();
  });

  it("inpaint partition is disabled", async () => {
    await mountAndSwitch("inpaint");
    assertDisabledSection(DISABLED_SECTION_TEST_IDS.inpaint, "图片修复");
  });

  it("typeset partition and the reading-direction partition are both disabled", async () => {
    await mountAndSwitch("typeset");
    assertDisabledSection(DISABLED_SECTION_TEST_IDS.typeset, "排版 / Text Style");
    assertDisabledSection(DISABLED_SECTION_TEST_IDS.readingDirection, "阅读方向");
  });

  it("model/GPU partition is disabled", async () => {
    await mountAndSwitch("model_gpu");
    assertDisabledSection(DISABLED_SECTION_TEST_IDS.modelGpu, "模型 / GPU");
  });

  it("task/concurrency partition is disabled", async () => {
    await mountAndSwitch("task_concurrency");
    assertDisabledSection(DISABLED_SECTION_TEST_IDS.taskConcurrency, "任务 / 并发");
  });

  it("cache/Revision partition is disabled", async () => {
    await mountAndSwitch("cache_revision");
    assertDisabledSection(DISABLED_SECTION_TEST_IDS.cacheRevision, "缓存 / Revision");
  });

  it("recycle bin (G2) partition is disabled with the frozen reason", async () => {
    await mountAndSwitch("recycle_bin");
    assertDisabledSection(DISABLED_SECTION_TEST_IDS.recycleBin, "回收站");
  });

  it("backup/restore partition is disabled", async () => {
    await mountAndSwitch("backup_restore");
    assertDisabledSection(DISABLED_SECTION_TEST_IDS.backupRestore, "备份 / 恢复");
  });

  it("Plugin/Hooks partition is disabled", async () => {
    await mountAndSwitch("plugins");
    assertDisabledSection(DISABLED_SECTION_TEST_IDS.plugins, "Plugin / Hooks");
  });
});
