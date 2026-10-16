import { renderToString } from "react-dom/server";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { JSDOM } from "jsdom";
import { describe, expect, it, vi } from "vitest";
import type { BookSummary } from "../library/types";
import { PageListPanel } from "./PageListPanel";

/**
 * M2-PAGE-NAV-PROJECTION-1: three-level drill-down render pins. The panel
 * is a pure display component (data/loading state is owned by
 * <WorkbenchPage>, which carries the interactive coverage), so the
 * component contract -- what each level renders per its loading state and
 * which callbacks a click feeds -- is asserted on the static render, the
 * established test split of this frontend.
 */

const BOOK: BookSummary = {
  book_id: "book-1",
  title: "Test Manga",
  original_title: "テスト漫画",
  is_favorite: false,
  is_archived: false,
  page_count: 2,
  created_at: "2026-10-07T00:00:00Z",
  updated_at: "2026-10-07T00:00:00Z",
};

const CHAPTER = { chapter_id: "ch-1", title: "First", chapter_number: "1", sort_order: 1 };
const PAGE = { page_id: "p-1", source_filename: "001.png", sort_order: 1 };

function renderPanel(overrides: Partial<Parameters<typeof PageListPanel>[0]> = {}) {
  return renderToString(
    <PageListPanel
      books={[BOOK]}
      selectedBookId={null}
      chapters={[]}
      chaptersBusy={false}
      chaptersError={null}
      selectedChapterId={null}
      pages={[]}
      pagesBusy={false}
      pagesError={null}
      pageId=""
      onPageIdChange={() => {}}
      onSelectBook={() => {}}
      onSelectChapter={() => {}}
      {...overrides}
    />,
  );
}

describe("<PageListPanel> three-level drill-down (M2-PAGE-NAV-PROJECTION-1)", () => {
  it("scrolls the located current page into view", async () => {
    const dom = new JSDOM("<!doctype html><html><body></body></html>", { url: "http://localhost" });
    const seen: string[] = [];
    Object.defineProperty(dom.window.HTMLButtonElement.prototype, "scrollIntoView", {
      configurable: true,
      value: vi.fn(function (this: HTMLButtonElement) { seen.push(this.getAttribute("data-testid") ?? ""); }),
    });
    vi.stubGlobal("window", dom.window);
    vi.stubGlobal("document", dom.window.document);
    vi.stubGlobal("HTMLElement", dom.window.HTMLElement);
    vi.stubGlobal("HTMLButtonElement", dom.window.HTMLButtonElement);
    vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
    const host = dom.window.document.createElement("div");
    dom.window.document.body.append(host);
    const root = createRoot(host);
    const props = {
      books: [BOOK], selectedBookId: "book-1", chapters: [CHAPTER], chaptersBusy: false,
      chaptersError: null, selectedChapterId: "ch-1", pages: [PAGE, { ...PAGE, page_id: "p-2" }],
      pagesBusy: false, pagesError: null, onPageIdChange: () => {}, onSelectBook: () => {}, onSelectChapter: () => {},
    };
    try {
      await act(async () => root.render(<PageListPanel {...props} pageId="p-1" />));
      seen.length = 0;
      await act(async () => root.render(<PageListPanel {...props} pageId="p-2" />));
      expect(seen).toEqual(["page-tile-p-2"]);
    } finally {
      act(() => root.unmount());
      dom.window.close();
      vi.unstubAllGlobals();
    }
  });

  it("keeps the debug page-id entry and renders no chapter level before a book is selected", () => {
    const html = renderPanel();
    expect(html).toContain('data-testid="page-id-input"');
    expect(html).toContain('data-testid="book-tile-book-1"');
    expect(html).not.toContain('data-testid="chapter-list"');
    expect(html).not.toContain('data-testid="page-nav-list"');
  });

  it("renders chapter tiles with number and title when a book is selected", () => {
    const html = renderPanel({
      selectedBookId: "book-1",
      chapters: [CHAPTER],
    });
    expect(html).toContain('data-testid="chapter-list"');
    expect(html).toContain('data-testid="chapter-tile-ch-1"');
    expect(html).toContain("#1");
    expect(html).toContain("First");
    expect(html).not.toContain('data-testid="chapters-busy"');
    expect(html).not.toContain('data-testid="chapters-error"');
    expect(html).not.toContain('data-testid="chapter-list-empty"');
  });

  it("renders the chapter loading/error/empty states distinctly", () => {
    const busy = renderPanel({ selectedBookId: "book-1", chaptersBusy: true });
    expect(busy).toContain('data-testid="chapters-busy"');
    expect(busy).not.toContain('data-testid="chapters-error"');
    expect(busy).not.toContain('data-testid="chapter-list-empty"');

    const failed = renderPanel({
      selectedBookId: "book-1",
      chaptersError: "CORE_UNAVAILABLE",
    });
    expect(failed).toContain('data-testid="chapters-error"');
    expect(failed).toContain("CORE_UNAVAILABLE");
    expect(failed).not.toContain('data-testid="chapter-list-empty"');

    const empty = renderPanel({ selectedBookId: "book-1" });
    expect(empty).toContain('data-testid="chapter-list-empty"');
  });

  it("renders page tiles and highlights only the current page once a chapter is selected", () => {
    // renderToString never fires events, so the page-tile -> onPageIdChange
    // WIRING is pinned at the integration layer (WorkbenchPage.test.tsx
    // clicks page-tile-* and asserts the resolve -> image chain); this
    // static case pins what the panel renders per its props, including the
    // selected-page highlight (r2 N-05: the claim now carries an assertion).
    const html = renderPanel({
      selectedBookId: "book-1",
      chapters: [CHAPTER],
      selectedChapterId: "ch-1",
      pages: [PAGE, { ...PAGE, page_id: "p-2", source_filename: "002.png", sort_order: 2 }],
      pageId: "p-1",
    });
    expect(html).toContain('data-testid="page-nav-list"');
    expect(html).toContain('data-testid="page-tile-p-1"');
    expect(html).toContain('data-testid="page-tile-p-2"');
    // the selected-page highlight lands on exactly the current page's tile
    const tileMarkup = (testId: string) =>
      html.match(new RegExp(`<button[^>]*data-testid="${testId}"[^>]*>`))?.[0] ?? "";
    expect(tileMarkup("page-tile-p-1")).toContain("background:#e8edff");
    expect(tileMarkup("page-tile-p-2")).not.toContain("background:#e8edff");
    expect(html).not.toContain('data-testid="pages-busy"');
    expect(html).not.toContain('data-testid="pages-error"');
    expect(html).not.toContain('data-testid="page-nav-list-empty"');
  });

  it("renders the page loading/error/empty states distinctly", () => {
    const busy = renderPanel({
      selectedBookId: "book-1",
      selectedChapterId: "ch-1",
      pagesBusy: true,
    });
    expect(busy).toContain('data-testid="pages-busy"');
    expect(busy).not.toContain('data-testid="page-nav-list-empty"');

    const failed = renderPanel({
      selectedBookId: "book-1",
      selectedChapterId: "ch-1",
      pagesError: "PAGE_NAV_MALFORMED",
    });
    expect(failed).toContain('data-testid="pages-error"');
    expect(failed).toContain("PAGE_NAV_MALFORMED");

    const empty = renderPanel({
      selectedBookId: "book-1",
      selectedChapterId: "ch-1",
    });
    expect(empty).toContain('data-testid="page-nav-list-empty"');
  });
});
