import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { SettingsClient } from "./client";
import { DISABLED_SECTION_TEST_IDS, SETTINGS_CATEGORY_ORDER, SettingsPage } from "./SettingsPage";

/**
 * P15 AC1 — layout & category structure (AD-001 §5.2): 200px fixed
 * SettingsCategoryNav + SettingsContentPanel, twelve categories in the
 * frozen order, switching via React local state (no sub-route).
 *
 * SETTINGS-OPEN-A-1 AC3 — batch A opens OCR / translation parameters /
 * inpaint / typeset.
 * SETTINGS-OPEN-B-1 AC4 — batch B-1 opens model/GPU and tasks/concurrency.
 * SETTINGS-OPEN-B-2 AC3/AC4 — batch B-2 opens cache/Revision (preview +
 * manual cleanup + pending retry).
 * SETTINGS-OPEN-C-1-RECYCLE — batch C-1 opens the recycle bin (view + clear
 * operation surface; no settings write section). SETTINGS-OPEN-C-2-BACKUP —
 * batch C-2 opens backup/restore (create/list/restore/delete operation
 * surface; no auto_backup controls). Only plugins keep the disabled
 * placeholder and the "未开放" badge (11 open / 1 closed).
 */

const OPEN_CATEGORY_IDS = [
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
] as const;
const CLOSED_CATEGORY_IDS = ["plugins"] as const;

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
      case "cleanup_preview":
        return { targets: [], total_bytes: 0, pending_cleanups: 0 };
      case "library_list_recycle_bin_books":
        return [];
      case "backup_list":
        return [];
      case "backup_create":
        return {
          backup_id: "a".repeat(32),
          path: "a.nmbak",
          size_bytes: 1024,
          created_at: "2026-10-23T02:00:00+00:00",
          verified: true,
        };
      default:
        return {};
    }
  });
}

function useMountedPage() {
  const dom = new JSDOM("<!doctype html><html><body></body></html>", { url: "http://localhost" });
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  vi.stubGlobal("window", dom.window);
  vi.stubGlobal("document", dom.window.document);
  vi.stubGlobal("navigator", dom.window.navigator);
  vi.stubGlobal("HTMLElement", dom.window.HTMLElement);
  const container = dom.window.document.createElement("div");
  dom.window.document.body.appendChild(container);
  const root = createRoot(container);

  const q = (selector: string) => container.querySelector(selector) as HTMLElement | null;

  const mount = () => {
    act(() => {
      root.render(<SettingsPage client={new SettingsClient(makeInvoke())} />);
    });
  };

  const activateOpenCategory = async (categoryId: string) => {
    await act(async () => {
      (q(`[data-testid="settings-category-${categoryId}"]`) as HTMLButtonElement).click();
      await Promise.resolve();
    });
  };

  const cleanup = () => {
    act(() => {
      root.unmount();
    });
    vi.unstubAllGlobals();
  };

  return { dom, container, q, mount, activateOpenCategory, cleanup };
}

describe("SettingsPage layout & categories (AC1)", () => {
  let page: ReturnType<typeof useMountedPage>;

  beforeEach(() => {
    page = useMountedPage();
  });

  afterEach(() => {
    page.cleanup();
  });

  it("renders the fixed 200px category nav and the content panel", () => {
    page.mount();
    const nav = page.q('[data-testid="settings-category-nav"]');
    expect(nav).not.toBeNull();
    expect(nav?.getAttribute("style") ?? nav?.style.width).toContain("200px");
    expect(page.q('[data-testid="settings-content-panel"]')).not.toBeNull();
  });

  it("renders the twelve categories in the frozen order with the frozen labels", () => {
    page.mount();
    const buttons = Array.from(
      page.container.querySelectorAll('button[data-testid^="settings-category-"]'),
    );
    const ids = buttons.map((b) =>
      (b as HTMLElement).dataset.testid?.replace("settings-category-", ""),
    );
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
    page.mount();
    expect(page.q('[data-testid="settings-page"]')).not.toBeNull();

    await page.activateOpenCategory("network");
    expect(page.q('[data-testid="settings-active-category"]')?.getAttribute("data-category-id")).toBe(
      "network",
    );
    expect(page.q('[data-testid="settings-content-network"]')).not.toBeNull();
    // The page container node is the SAME node across switches (no route
    // remount): the nav keeps its DOM identity.
    const navBefore = page.q('[data-testid="settings-category-nav"]');
    await page.activateOpenCategory("provider");
    expect(
      page.q('[data-testid="settings-active-category"]')?.getAttribute("data-category-id"),
    ).toBe("provider");
    expect(page.q('[data-testid="settings-content-provider"]')).not.toBeNull();
    expect(page.q('[data-testid="settings-category-nav"]')).toBe(navBefore);
  });

  it("opens exactly the batch-A + B-1 + B-2 + C-1 categories; only still-closed categories carry the 未开放 badge", () => {
    page.mount();
    const openFlags = SETTINGS_CATEGORY_ORDER.map(
      (id) => (page.q(`[data-testid="settings-category-${id}"]`) as HTMLElement).dataset.open,
    );
    expect(openFlags).toEqual([
      "true", // provider
      "true", // network
      "true", // ocr — batch A
      "true", // translation (sfx.policy + translation params)
      "true", // inpaint — batch A
      "true", // typeset — batch A
      "true", // model_gpu — batch B-1
      "true", // task_concurrency — batch B-1
      "true", // cache_revision — batch B-2
      "true", // recycle_bin — batch C-1
      "true", // backup_restore — batch C-2
      "false", // plugins
    ]);

    for (const id of OPEN_CATEGORY_IDS) {
      const button = page.q(`[data-testid="settings-category-${id}"]`) as HTMLButtonElement;
      expect(button).not.toBeNull();
      expect(button.disabled).toBe(false);
      expect(button.getAttribute("aria-disabled")).toBe("false");
      // The "未开放" aria-label/title only exists for still-closed partitions.
      expect(button.getAttribute("aria-label")).toBeNull();
      expect(button.getAttribute("title")).toBeNull();
      expect(button.textContent).not.toContain("未开放");
    }

    for (const id of CLOSED_CATEGORY_IDS) {
      const button = page.q(`[data-testid="settings-category-${id}"]`) as HTMLButtonElement;
      expect(button.disabled).toBe(true);
      expect(button.getAttribute("aria-disabled")).toBe("true");
      expect(button.getAttribute("aria-label")).toContain("未开放");
      expect(button.getAttribute("title")).toContain("等待 section schema 冻结");
      expect(button.textContent).toContain("未开放");
    }
  });
});

describe("Batch A open categories host editable panels (AC3)", () => {
  let page: ReturnType<typeof useMountedPage>;

  beforeEach(() => {
    page = useMountedPage();
  });

  afterEach(() => {
    page.cleanup();
  });

  it("OCR category opens and renders OcrSettingsPanel instead of the placeholder", async () => {
    page.mount();
    await page.activateOpenCategory("ocr");
    expect(page.q('[data-testid="settings-active-category"]')?.getAttribute("data-category-id")).toBe(
      "ocr",
    );
    expect(page.q('[data-testid="settings-content-ocr"]')).not.toBeNull();
    expect(page.q('[data-testid="ocr-settings-panel"]')).not.toBeNull();
    expect(page.q('[data-testid="settings-disabled-section-ocr"]')).toBeNull();
    // The panel loaded the real section through the shared channel.
    expect(page.q('[data-testid="ocr-script"]')).not.toBeNull();
  });

  it("inpaint category opens and renders InpaintSettingsPanel instead of the placeholder", async () => {
    page.mount();
    await page.activateOpenCategory("inpaint");
    expect(page.q('[data-testid="settings-active-category"]')?.getAttribute("data-category-id")).toBe(
      "inpaint",
    );
    expect(page.q('[data-testid="settings-content-inpaint"]')).not.toBeNull();
    expect(page.q('[data-testid="inpaint-settings-panel"]')).not.toBeNull();
    expect(page.q('[data-testid="settings-disabled-section-inpaint"]')).toBeNull();
  });

  it("typeset category opens TypesetSettingsPanel and keeps reading direction as guidance only", async () => {
    page.mount();
    await page.activateOpenCategory("typeset");
    expect(page.q('[data-testid="settings-active-category"]')?.getAttribute("data-category-id")).toBe(
      "typeset",
    );
    expect(page.q('[data-testid="settings-content-typeset"]')).not.toBeNull();
    expect(page.q('[data-testid="typeset-settings-panel"]')).not.toBeNull();
    expect(page.q('[data-testid="settings-disabled-section-typeset"]')).toBeNull();
    // §3.4: direction is a Book/Chapter property — guidance, not a fake control.
    const note = page.q('[data-testid="settings-reading-direction-note"]');
    expect(note).not.toBeNull();
    expect(note?.textContent).toContain("书籍 / 章节属性");
    expect(note?.getAttribute("aria-disabled")).toBeNull();
  });

  it("translation keeps SfxPolicyControl and adds TranslationParamsPanel, replacing the context placeholder", async () => {
    page.mount();
    await page.activateOpenCategory("translation");
    expect(page.q('[data-testid="sfx-policy-control"]')).not.toBeNull();
    expect(page.q('[data-testid="translation-params-panel"]')).not.toBeNull();
    expect(page.q('[data-testid="settings-disabled-section-translation-context"]')).toBeNull();
    expect(page.q('[data-testid="translate-context-pages"]')).not.toBeNull();
  });

  it("keyboard navigation skips the still-closed categories", async () => {
    page.mount();
    const nav = page.q('[data-testid="settings-category-nav"]') as HTMLElement;
    const arrowDown = async () => {
      await act(async () => {
        nav.dispatchEvent(new page.dom.window.KeyboardEvent("keydown", { key: "ArrowDown", bubbles: true }));
        await Promise.resolve();
      });
    };
    // provider → network → ocr → translation: the closed-after-open
    // transitions still land on open categories only.
    for (let i = 0; i < 3; i += 1) {
      await arrowDown();
    }
    expect(page.q('[data-testid="settings-active-category"]')?.getAttribute("data-category-id")).toBe(
      "translation",
    );

    await page.activateOpenCategory("typeset");
    await arrowDown();
    // model/GPU is open since batch B-1, so it is the next stop (not skipped).
    expect(page.q('[data-testid="settings-active-category"]')?.getAttribute("data-category-id")).toBe(
      "model_gpu",
    );

    await arrowDown();
    expect(page.q('[data-testid="settings-active-category"]')?.getAttribute("data-category-id")).toBe(
      "task_concurrency",
    );

    // cache/Revision is open since batch B-2, so it is the next stop (not skipped).
    await arrowDown();
    expect(page.q('[data-testid="settings-active-category"]')?.getAttribute("data-category-id")).toBe(
      "cache_revision",
    );

    // The recycle bin is open since batch C-1, so it is the next stop.
    await arrowDown();
    expect(page.q('[data-testid="settings-active-category"]')?.getAttribute("data-category-id")).toBe(
      "recycle_bin",
    );

    // backup/restore is open since batch C-2, so it is the next stop.
    await arrowDown();
    expect(page.q('[data-testid="settings-active-category"]')?.getAttribute("data-category-id")).toBe(
      "backup_restore",
    );

    // The still-closed plugin category trails the open list: another
    // ArrowDown is clamped to the last OPEN category and never lands on it.
    await arrowDown();
    expect(page.q('[data-testid="settings-active-category"]')?.getAttribute("data-category-id")).toBe(
      "backup_restore",
    );
  });

  it("keyboard navigation never enters a closed category (ArrowUp from the first open one stays)", async () => {
    page.mount();
    const nav = page.q('[data-testid="settings-category-nav"]') as HTMLElement;
    await act(async () => {
      nav.dispatchEvent(new page.dom.window.KeyboardEvent("keydown", { key: "ArrowUp", bubbles: true }));
      await Promise.resolve();
    });
    expect(page.q('[data-testid="settings-active-category"]')?.getAttribute("data-category-id")).toBe(
      "provider",
    );
  });
});

describe("Batch B-1 open categories host editable panels (AC4)", () => {
  let page: ReturnType<typeof useMountedPage>;

  beforeEach(() => {
    page = useMountedPage();
  });

  afterEach(() => {
    page.cleanup();
  });

  it("model/GPU category opens and renders ModelGpuSettingsPanel instead of the placeholder", async () => {
    page.mount();
    await page.activateOpenCategory("model_gpu");
    expect(page.q('[data-testid="settings-active-category"]')?.getAttribute("data-category-id")).toBe(
      "model_gpu",
    );
    expect(page.q('[data-testid="settings-content-model-gpu"]')).not.toBeNull();
    expect(page.q('[data-testid="model-gpu-settings-panel"]')).not.toBeNull();
    expect(page.q('[data-testid="settings-disabled-section-model-gpu"]')).toBeNull();
    // The panel loaded the real section through the shared channel.
    expect(page.q('[data-testid="model-gpu-device-preference"]')).not.toBeNull();
    expect(page.q('[data-testid="model-gpu-allow-cpu-fallback"]')).not.toBeNull();
    // Read-only note: capability probing belongs to the Provider at Run time.
    expect(page.q('[data-testid="model-gpu-settings-panel-runtime-note"]')?.textContent).toContain(
      "运行时探测",
    );
  });

  it("task/concurrency category opens TasksSettingsPanel with the serial-execution note", async () => {
    page.mount();
    await page.activateOpenCategory("task_concurrency");
    expect(page.q('[data-testid="settings-active-category"]')?.getAttribute("data-category-id")).toBe(
      "task_concurrency",
    );
    expect(page.q('[data-testid="settings-content-task-concurrency"]')).not.toBeNull();
    expect(page.q('[data-testid="tasks-settings-panel"]')).not.toBeNull();
    expect(page.q('[data-testid="settings-disabled-section-task-concurrency"]')).toBeNull();
    expect(page.q('[data-testid="tasks-retry-max-attempts"]')).not.toBeNull();
    expect(page.q('[data-testid="tasks-retry-backoff-seconds"]')).not.toBeNull();
    // §4.2: concurrency count is a forced invariant — read-only note only.
    expect(page.q('[data-testid="tasks-settings-panel-serial-note"]')?.textContent).toContain(
      "任务串行执行",
    );
    expect(page.q('[data-testid="tasks-concurrency"]')).toBeNull();
  });
});

describe("Batch B-2 open category hosts the cache/Revision cleanup surface (AC3)", () => {
  let page: ReturnType<typeof useMountedPage>;

  beforeEach(() => {
    page = useMountedPage();
  });

  afterEach(() => {
    page.cleanup();
  });

  it("cache/Revision category opens CacheRevisionPanel instead of the placeholder", async () => {
    page.mount();
    await page.activateOpenCategory("cache_revision");
    expect(page.q('[data-testid="settings-active-category"]')?.getAttribute("data-category-id")).toBe(
      "cache_revision",
    );
    expect(page.q('[data-testid="settings-content-cache-revision"]')).not.toBeNull();
    expect(page.q('[data-testid="cache-revision-panel"]')).not.toBeNull();
    expect(page.q('[data-testid="settings-disabled-section-cache-revision"]')).toBeNull();
    // Real preview state, not a disabled placeholder: the empty cache is
    // surfaced explicitly and the operations are visible but gated.
    expect(page.q('[data-testid="cache-revision-panel-empty"]')?.textContent).toContain(
      "无可清理文件",
    );
    expect(
      (page.q('[data-testid="cache-revision-panel-cleanup-btn"]') as HTMLButtonElement).disabled,
    ).toBe(true);
    // §4.3: retention policy / automatic cleanup are read-only, not fake controls.
    expect(page.q('[data-testid="cache-revision-panel-policy-note"]')?.textContent).toContain(
      "Revision 保留策略与自动清理未开放",
    );
  });
});

describe("Batch C-1 open category hosts the recycle-bin surface (AC3)", () => {
  let page: ReturnType<typeof useMountedPage>;

  beforeEach(() => {
    page = useMountedPage();
  });

  afterEach(() => {
    page.cleanup();
  });

  it("recycle bin category opens RecycleBinSettingsPanel instead of the placeholder", async () => {
    page.mount();
    await page.activateOpenCategory("recycle_bin");
    expect(page.q('[data-testid="settings-active-category"]')?.getAttribute("data-category-id")).toBe(
      "recycle_bin",
    );
    expect(page.q('[data-testid="settings-content-recycle-bin"]')).not.toBeNull();
    expect(page.q('[data-testid="recycle-bin-settings-panel"]')).not.toBeNull();
    expect(page.q('[data-testid="settings-disabled-section-recycle-bin"]')).toBeNull();
    // §2.4: the retention policy is a read-only note, never a fake control.
    expect(page.q('[data-testid="recycle-bin-settings-policy-note"]')?.textContent).toContain(
      "没有调度器",
    );
  });
});

describe("Batch C-2 open category hosts the backup/restore surface (AC3)", () => {
  let page: ReturnType<typeof useMountedPage>;

  beforeEach(() => {
    page = useMountedPage();
  });

  afterEach(() => {
    page.cleanup();
  });

  it("backup/restore category opens BackupSettingsPanel instead of the placeholder", async () => {
    page.mount();
    await page.activateOpenCategory("backup_restore");
    expect(page.q('[data-testid="settings-active-category"]')?.getAttribute("data-category-id")).toBe(
      "backup_restore",
    );
    expect(page.q('[data-testid="settings-content-backup-restore"]')).not.toBeNull();
    expect(page.q('[data-testid="backup-settings-panel"]')).not.toBeNull();
    expect(page.q('[data-testid="settings-disabled-section-backup-restore"]')).toBeNull();
    // §3.2: automatic backups are a read-only note, never a fake control.
    expect(page.q('[data-testid="backup-settings-policy-note"]')?.textContent).toContain(
      "自动备份",
    );
  });
});

describe("Still-disabled partitions: visible, not operable, reasoned (AC2)", () => {
  let page: ReturnType<typeof useMountedPage>;

  beforeEach(() => {
    page = useMountedPage();
  });

  afterEach(() => {
    page.cleanup();
  });

  const assertDisabledCategory = (categoryId: string, label: string) => {
    const button = page.q(`[data-testid="settings-category-${categoryId}"]`) as HTMLButtonElement;
    expect(button).not.toBeNull();
    expect(button.disabled).toBe(true);
    expect(button.getAttribute("aria-disabled")).toBe("true");
    expect(button.getAttribute("aria-label")).toContain("未开放");
    expect(button.getAttribute("aria-label")).toContain("等待 section schema 冻结");
    expect(button.title).toContain("等待 section schema 冻结");
    expect(button.textContent).toContain(label);
    expect(button.textContent).toContain("未开放");
  };

  it("Plugin/Hooks category remains visible but cannot be invoked", () => {
    page.mount();
    assertDisabledCategory("plugins", "Plugin/Hooks");
  });

  it("keeps a reasoned placeholder id for every still-closed partition", () => {
    page.mount();
    // Batch C-2 opened backup/restore: only the plugin partition remains.
    expect(Object.keys(DISABLED_SECTION_TEST_IDS).sort()).toEqual(["plugins"]);
    // None of them is mounted while the page sits on an open category.
    for (const testId of Object.values(DISABLED_SECTION_TEST_IDS)) {
      expect(page.q(`[data-testid="${testId}"]`)).toBeNull();
    }
  });
});
