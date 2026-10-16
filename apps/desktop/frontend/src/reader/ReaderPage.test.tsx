import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { renderToString } from "react-dom/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { CoreEventMap } from "../events";
import { ReaderPage } from "./ReaderPage";
import type { ReaderProjection } from "./types";

const DUMMY_PNG_BYTES = Uint8Array.from([
  0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,
  0x00, 0x00, 0x00, 0x0d, 0x49, 0x48, 0x44, 0x52,
  0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
  0x08, 0x06, 0x00, 0x00, 0x00, 0x1f, 0x15, 0xc4, 0x89,
  0x00, 0x00, 0x00, 0x0b, 0x49, 0x44, 0x41, 0x54,
  0x78, 0x9c, 0x63, 0x60, 0x00, 0x02, 0x00, 0x00, 0x05, 0x00, 0x01,
  0xa5, 0xf6, 0x45, 0x40,
  0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82,
]);

async function nextTick() {
  for (let i = 0; i < 10; i += 1) {
    await Promise.resolve();
  }
}

describe("ReaderPage (P17: AD-001 §4 / W18, W19, W20)", () => {
  let dom: JSDOM;
  let container: HTMLDivElement;
  let root: ReturnType<typeof createRoot>;
  let createdBlobs: Blob[];
  let revokedUrls: string[];

  const createMockProjection = (overrides?: Partial<ReaderProjection>): ReaderProjection => ({
    book_id: "book-1",
    chapter_id: "chap-1",
    mode: "original",
    layout: "rtl",
    pages: [
      {
        page_id: "page-1",
        order: 0,
        width_px: 800,
        height_px: 1200,
        original: {
          resource_ref: { resource_id: "res-orig-1", revision: "original" },
          artifact_revision_id: "rev-1",
          sha256: "1".repeat(64),
        },
        translated: {
          resource_ref: { resource_id: "res-trans-1", revision: "trans-1" },
          artifact_revision_id: "rev-trans-1",
          rendered_from_revision_id: "rev-src-1",
          current_source_revision_id: "rev-src-1",
          sha256: "2".repeat(64),
        },
      },
      {
        page_id: "page-2",
        order: 1,
        width_px: 800,
        height_px: 1200,
        original: {
          resource_ref: { resource_id: "res-orig-2", revision: "original" },
          artifact_revision_id: "rev-2",
          sha256: "3".repeat(64),
        },
        translated: {
          resource_ref: null, // missing translation (AC2)
          artifact_revision_id: null,
          rendered_from_revision_id: null,
          current_source_revision_id: null,
          sha256: null,
        },
      },
    ],
    saved_progress: {
      book_id: "book-1",
      chapter_id: "chap-1",
      mode: "original",
      last_page_id: "page-1",
      scroll_offset_y: 0,
      progress_percent: 50,
      last_read_at: "2026-10-16T12:00:00Z",
      total_read_seconds: 60,
    },
    initial_position: { page_id: "page-1", scroll_offset_y: 0 },
    ...overrides,
  });

  beforeEach(() => {
    dom = new JSDOM("<!doctype html><html><body></body></html>", { url: "http://localhost" });
    createdBlobs = [];
    revokedUrls = [];

    Object.defineProperty(dom.window.HTMLElement.prototype, "clientWidth", {
      configurable: true,
      get: () => 800,
    });
    Object.defineProperty(dom.window.HTMLElement.prototype, "clientHeight", {
      configurable: true,
      get: () => 600,
    });
    Object.defineProperty(dom.window.URL, "createObjectURL", {
      configurable: true,
      value: (blob: Blob) => {
        createdBlobs.push(blob);
        return `blob:test-reader-${createdBlobs.length}`;
      },
    });
    Object.defineProperty(dom.window.URL, "revokeObjectURL", {
      configurable: true,
      value: (url: string) => {
        revokedUrls.push(url);
      },
    });

    vi.stubGlobal("window", dom.window);
    vi.stubGlobal("document", dom.window.document);
    vi.stubGlobal("navigator", dom.window.navigator);
    vi.stubGlobal("Node", dom.window.Node);
    vi.stubGlobal("Element", dom.window.Element);
    vi.stubGlobal("HTMLElement", dom.window.HTMLElement);
    vi.stubGlobal("URL", dom.window.URL);
    vi.stubGlobal("fetch", async () => {
      return new Response(DUMMY_PNG_BYTES.slice(), {
        status: 200,
        headers: { "content-type": "image/png" },
      });
    });
    vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);

    container = dom.window.document.createElement("div");
    dom.window.document.body.appendChild(container);
    root = createRoot(container);
  });

  afterEach(async () => {
    await act(async () => {
      root.unmount();
      await nextTick();
    });
    vi.clearAllTimers();
    vi.unstubAllGlobals();
  });

  it("renders 48px ReaderToolbar and empty state when no chapterId is selected (AC1, §4.2, §4.3)", () => {
    const html = renderToString(<ReaderPage chapterId={null} />);

    expect(html).toContain('data-testid="reader-page"');
    expect(html).toContain('data-testid="reader-toolbar"');
    expect(html).toContain('height:48px');
    expect(html).toContain('data-testid="reader-empty"');
    expect(html).toContain("尚未选择阅读章节");

    // CRITICAL BOUNDARY: NEVER render export panel (W21-W25归P14)
    expect(html).not.toContain("export-dialog");
    expect(html).not.toContain("start-export");
    expect(html).not.toContain("library_start_export");
  });

  it("loads projection via library_get_reader_projection (W18) and renders pages via resource channel (W5, AC2)", async () => {
    const projection = createMockProjection();
    const invoke = vi.fn().mockImplementation(async (cmd: string, _args?: Record<string, unknown>) => {
      if (cmd === "library_get_reader_projection") {
        return projection;
      }
      if (cmd === "issue_resource_url") {
        return {
          url: "http://m2res.localhost/m2id/res-1",
          size: DUMMY_PNG_BYTES.length,
          opaque_id: "res-1",
        };
      }
      if (cmd === "library_save_reading_progress") {
        return projection.saved_progress;
      }
      return null;
    });

    await act(async () => {
      root.render(
        <ReaderPage
          chapterId="chap-1"
          chapterTitle="第 1 话：开始"
          invoke={invoke}
        />
      );
      await nextTick();
    });

    // 1. Assert W18 call
    expect(invoke).toHaveBeenCalledWith("library_get_reader_projection", {
      chapterId: "chap-1",
      mode: "original",
      startPosition: "resume",
    });

    // 2. Assert W5 Resource Channel invocation (issue_resource_url)
    expect(invoke).toHaveBeenCalledWith("issue_resource_url", {
      resourceId: "res-orig-1",
      revision: "original",
    });

    // 3. Assert rendered elements
    const pageImg = container.querySelector('[data-testid="reader-page-img"]') as HTMLImageElement;
    expect(pageImg).not.toBeNull();
    expect(pageImg.src).toContain("blob:test-reader-");

    // 4. Position indicator: 1 / 2
    const pageNum = container.querySelector('[data-testid="reader-page-number"]');
    expect(pageNum?.textContent).toContain("1 / 2");
  });

  it("handles RTL and LTR navigation directions correctly (§4.5, §4.6)", async () => {
    const projection = createMockProjection({ layout: "rtl" });
    const invoke = vi.fn().mockImplementation(async (cmd: string) => {
      if (cmd === "library_get_reader_projection") return projection;
      if (cmd === "issue_resource_url") {
        return { url: "http://m2res.localhost/m2id/res", size: DUMMY_PNG_BYTES.length, opaque_id: "res" };
      }
      if (cmd === "library_save_reading_progress") return projection.saved_progress;
      return null;
    });

    await act(async () => {
      root.render(<ReaderPage chapterId="chap-1" invoke={invoke} />);
      await nextTick();
    });

    // In RTL, left click or ArrowLeft goes to NEXT page (page 2)
    const navLeft = container.querySelector('[data-testid="paged-nav-left"]') as HTMLElement;
    expect(navLeft).not.toBeNull();

    await act(async () => {
      navLeft.click();
      await nextTick();
    });

    const pageNum = container.querySelector('[data-testid="reader-page-number"]');
    expect(pageNum?.textContent).toContain("2 / 2");

    // In RTL, right click or ArrowRight goes to PREVIOUS page (back to page 1)
    const navRight = container.querySelector('[data-testid="paged-nav-right"]') as HTMLElement;
    await act(async () => {
      navRight.click();
      await nextTick();
    });
    expect(pageNum?.textContent).toContain("1 / 2");
  });

  it("presents missing translated artifact as null with fallback to original and '未翻译' badge (AC2 contract red line)", async () => {
    // Page 2 has translated.resource_ref = null
    const projection = createMockProjection({
      initial_position: { page_id: "page-2", scroll_offset_y: 0 },
    });
    const invoke = vi.fn().mockImplementation(async (cmd: string) => {
      if (cmd === "library_get_reader_projection") return projection;
      if (cmd === "issue_resource_url") {
        return { url: "http://m2res.localhost/m2id/res", size: DUMMY_PNG_BYTES.length, opaque_id: "res" };
      }
      return null;
    });

    await act(async () => {
      root.render(<ReaderPage chapterId="chap-1" invoke={invoke} />);
      await nextTick();
    });

    // Switch to translated mode
    const modeBtn = container.querySelector('[data-testid="reader-mode-translated"]') as HTMLButtonElement;
    await act(async () => {
      modeBtn.click();
      await nextTick();
    });

    // Assert missing translation badge is displayed
    const missingBadge = container.querySelector('[data-testid="badge-missing-translation"]');
    expect(missingBadge).not.toBeNull();
    expect(missingBadge?.textContent).toContain("未翻译 (回退原文)");

    // Resource issued should be the original's resource (fallback), NOT a fabricated path
    expect(invoke).toHaveBeenCalledWith("issue_resource_url", {
      resourceId: "res-orig-2",
      revision: "original",
    });
  });

  it("handles stale translation with '译文可能过期' badge (AC2 / M2-C1 §6.3)", async () => {
    const staleProjection = createMockProjection({
      pages: [
        {
          page_id: "p-stale",
          order: 0,
          width_px: 800,
          height_px: 1200,
          original: {
            resource_ref: { resource_id: "res-orig", revision: "original" },
            artifact_revision_id: "rev-orig",
            sha256: "1".repeat(64),
          },
          translated: {
            resource_ref: { resource_id: "res-trans", revision: "rev-old" },
            artifact_revision_id: "rev-trans",
            rendered_from_revision_id: "rev-old-source",
            current_source_revision_id: "rev-new-source", // DIFFERS -> STALE!
            sha256: "2".repeat(64),
          },
        },
      ],
      initial_position: { page_id: "p-stale", scroll_offset_y: 0 },
    });

    const invoke = vi.fn().mockImplementation(async (cmd: string, _args?: Record<string, unknown>) => {
      if (cmd === "library_get_reader_projection") return staleProjection;
      if (cmd === "issue_resource_url") {
        return { url: "http://m2res.localhost/m2id/res", size: DUMMY_PNG_BYTES.length, opaque_id: "res" };
      }
      return null;
    });

    await act(async () => {
      root.render(<ReaderPage chapterId="chap-1" invoke={invoke} />);
      await nextTick();
    });

    // Switch to translated mode
    const modeBtn = container.querySelector('[data-testid="reader-mode-translated"]') as HTMLButtonElement;
    await act(async () => {
      modeBtn.click();
      await nextTick();
    });

    const staleBadge = container.querySelector('[data-testid="badge-stale-translation"]');
    expect(staleBadge).not.toBeNull();
    expect(staleBadge?.textContent).toContain("译文可能过期");
  });

  it("supports Webtoon vertical scrolling with logical Page original-image pixel coordinate mapping (AC2, M2-C1 §6.3)", async () => {
    const webtoonProjection: ReaderProjection = {
      book_id: "book-1",
      chapter_id: "chap-webtoon",
      mode: "original",
      layout: "webtoon_vertical",
      pages: [
        {
          page_id: "webtoon-page-1",
          order: 0,
          width_px: 800, // source width
          height_px: 4000, // source height
          original: {
            resource_ref: { resource_id: "webtoon-res", revision: "original" },
            artifact_revision_id: "rev-1",
            sha256: "4".repeat(64),
          },
          translated: {
            resource_ref: null,
            artifact_revision_id: null,
            rendered_from_revision_id: null,
            current_source_revision_id: null,
            sha256: null,
          },
        },
      ],
      saved_progress: {
        book_id: "book-1",
        chapter_id: "chap-webtoon",
        mode: "original",
        last_page_id: "webtoon-page-1",
        scroll_offset_y: 1200,
        progress_percent: 30,
        last_read_at: "2026-10-16T12:00:00Z",
        total_read_seconds: 45,
      },
      initial_position: { page_id: "webtoon-page-1", scroll_offset_y: 1200 },
    };

    const invoke = vi.fn().mockImplementation(async (cmd: string) => {
      if (cmd === "library_get_reader_projection") return webtoonProjection;
      if (cmd === "issue_resource_url") {
        return { url: "http://m2res.localhost/m2id/webtoon", size: DUMMY_PNG_BYTES.length, opaque_id: "wt" };
      }
      if (cmd === "library_save_reading_progress") return webtoonProjection.saved_progress;
      return null;
    });

    await act(async () => {
      root.render(<ReaderPage chapterId="chap-webtoon" invoke={invoke} />);
      await nextTick();
    });

    const webtoonView = container.querySelector('[data-testid="webtoon-reader-view"]') as HTMLElement;
    expect(webtoonView).not.toBeNull();

    // Trigger scroll event on webtoon view
    await act(async () => {
      Object.defineProperty(webtoonView, "scrollTop", { value: 600, configurable: true });
      webtoonView.dispatchEvent(new dom.window.Event("scroll"));
      await nextTick();
    });

    // Advance timer to trigger debounced progress save
    await act(async () => {
      await new Promise((r) => setTimeout(r, 900));
      await nextTick();
    });

    // Assert saveReadingProgress was called with logical page coordinate
    const saveCalls = invoke.mock.calls.filter(([cmd]) => cmd === "library_save_reading_progress");
    expect(saveCalls.length).toBeGreaterThan(0);
    const lastSaveArgs = saveCalls[saveCalls.length - 1][1];
    expect(lastSaveArgs).toMatchObject({
      chapterId: "chap-webtoon",
      mode: "original",
      pageId: "webtoon-page-1",
    });
    expect(typeof lastSaveArgs.scrollOffsetY).toBe("number");
    expect(lastSaveArgs.scrollOffsetY).toBeGreaterThanOrEqual(0);
  });

  it("switches between resume and beginning start positions without mutating saved progress (AC2)", async () => {
    const projection = createMockProjection();
    const invoke = vi.fn().mockImplementation(async (cmd: string) => {
      if (cmd === "library_get_reader_projection") return projection;
      if (cmd === "issue_resource_url") {
        return { url: "http://m2res.localhost/m2id/res", size: DUMMY_PNG_BYTES.length, opaque_id: "res" };
      }
      return null;
    });

    await act(async () => {
      root.render(<ReaderPage chapterId="chap-1" invoke={invoke} />);
      await nextTick();
    });

    // Click '从头开始' (beginning)
    const beginningBtn = container.querySelector('[data-testid="reader-pos-beginning"]') as HTMLButtonElement;
    expect(beginningBtn).not.toBeNull();

    await act(async () => {
      beginningBtn.click();
      await nextTick();
    });

    // Assert GetReaderProjection requested with start_position="beginning"
    expect(invoke).toHaveBeenCalledWith("library_get_reader_projection", {
      chapterId: "chap-1",
      mode: "original",
      startPosition: "beginning",
    });
  });

  it("satisfies AC3 Event Discipline: re-queries snapshot on core:ReadingProgressChanged without using event payload to drive position", async () => {
    let capturedListener: ((event: { payload: CoreEventMap["core:ReadingProgressChanged"] }) => void) | null = null;
    const customListen = vi.fn().mockImplementation(async (event: string, handler: any) => {
      if (event === "core:ReadingProgressChanged") {
        capturedListener = handler;
      }
      return () => { capturedListener = null; };
    });

    const projection = createMockProjection();
    const invoke = vi.fn().mockImplementation(async (cmd: string) => {
      if (cmd === "library_get_reader_projection") return projection;
      if (cmd === "issue_resource_url") {
        return { url: "http://m2res.localhost/m2id/res", size: DUMMY_PNG_BYTES.length, opaque_id: "res" };
      }
      return null;
    });

    await act(async () => {
      root.render(<ReaderPage chapterId="chap-1" invoke={invoke} customListen={customListen} />);
      await nextTick();
    });

    expect(customListen).toHaveBeenCalledWith("core:ReadingProgressChanged", expect.any(Function));
    expect(capturedListener).not.toBeNull();

    const callsBefore = invoke.mock.calls.filter(([cmd]) => cmd === "library_get_reader_projection").length;

    // Simulate event firing with payload
    await act(async () => {
      capturedListener!({
        payload: {
          book_id: "book-1",
          chapter_id: "chap-1",
          mode: "original",
        },
      });
      await nextTick();
    });

    const callsAfter = invoke.mock.calls.filter(([cmd]) => cmd === "library_get_reader_projection").length;
    // CRITICAL AC3 ASSERTION: Re-queries authoritative projection from host/Core!
    expect(callsAfter).toBeGreaterThan(callsBefore);
  });

  it("handles error state and provides retry mechanism (AC1, §4.4)", async () => {
    let shouldFail = true;
    const projection = createMockProjection();
    const invoke = vi.fn().mockImplementation(async (cmd: string) => {
      if (cmd === "library_get_reader_projection") {
        if (shouldFail) {
          throw new Error("CORE_UNAVAILABLE");
        }
        return projection;
      }
      if (cmd === "issue_resource_url") {
        return { url: "http://m2res.localhost/m2id/res", size: DUMMY_PNG_BYTES.length, opaque_id: "res" };
      }
      return null;
    });

    await act(async () => {
      root.render(<ReaderPage chapterId="chap-1" invoke={invoke} />);
      await nextTick();
    });

    const errorCard = container.querySelector('[data-testid="reader-error"]');
    expect(errorCard).not.toBeNull();
    expect(errorCard?.textContent).toContain("CORE_UNAVAILABLE");

    // Click Retry button
    shouldFail = false;
    const retryBtn = container.querySelector('[data-testid="reader-retry-btn"]') as HTMLButtonElement;
    await act(async () => {
      retryBtn.click();
      await nextTick();
    });

    // Error is resolved, page img rendered
    expect(container.querySelector('[data-testid="reader-error"]')).toBeNull();
    expect(container.querySelector('[data-testid="reader-page-img"]')).not.toBeNull();
  });

  it("handles keyboard navigation shortcuts (§4.6: O/T, Esc, arrow keys)", async () => {
    const projection = createMockProjection();
    const invoke = vi.fn().mockImplementation(async (cmd: string) => {
      if (cmd === "library_get_reader_projection") return projection;
      if (cmd === "issue_resource_url") {
        return { url: "http://m2res.localhost/m2id/res", size: DUMMY_PNG_BYTES.length, opaque_id: "res" };
      }
      return null;
    });

    const onReturnToBookshelf = vi.fn();

    await act(async () => {
      root.render(
        <ReaderPage
          chapterId="chap-1"
          invoke={invoke}
          onReturnToBookshelf={onReturnToBookshelf}
        />
      );
      await nextTick();
    });

    // Press Esc -> triggers onReturnToBookshelf
    await act(async () => {
      dom.window.dispatchEvent(new dom.window.KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
      await nextTick();
    });
    expect(onReturnToBookshelf).toHaveBeenCalled();

    // Press 'T' -> switches to translated mode
    await act(async () => {
      dom.window.dispatchEvent(new dom.window.KeyboardEvent("keydown", { key: "t", bubbles: true }));
      await nextTick();
    });
    expect(invoke).toHaveBeenCalledWith("library_get_reader_projection", {
      chapterId: "chap-1",
      mode: "translated",
      startPosition: "resume",
    });
  });
});
