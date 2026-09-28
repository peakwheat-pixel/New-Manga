import { renderToString } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";
import { LibraryPanel } from "./LibraryPanel";
import { LibraryClient } from "./client";
import type { BookSummary } from "./types";

describe("LibraryPanel Component", () => {
  it("renders books list in success state", () => {
    const books: BookSummary[] = [
      {
        book_id: "book-001",
        title: "海贼王",
        original_title: "ONE PIECE",
        is_favorite: true,
        is_archived: false,
        page_count: 24,
        created_at: "2026-09-28T10:00:00Z",
        updated_at: "2026-09-28T10:00:00Z",
      },
    ];

    const html = renderToString(
      <LibraryPanel initialState={{ books, loading: false, error: null }} />
    );

    expect(html).toContain("海贼王");
    expect(html).toContain("ONE PIECE");
    expect(html).toContain("页数: 24");
    expect(html).toContain("2026-09-28T10:00:00Z");
    expect(html).toContain("★ 收藏");
    expect(html).toContain('data-testid="library-book-list"');
  });

  it("renders empty state message when book list is empty", () => {
    const html = renderToString(
      <LibraryPanel initialState={{ books: [], loading: false, error: null }} />
    );

    expect(html).toContain("书架为空，暂无书目");
    expect(html).toContain('data-testid="library-empty"');
    expect(html).not.toContain('data-testid="library-book-list"');
  });

  it("renders explicit CORE_UNAVAILABLE error UI with no auto-retry notice", () => {
    const html = renderToString(
      <LibraryPanel
        initialState={{
          books: null,
          loading: false,
          error: "CORE_UNAVAILABLE",
        }}
      />
    );

    expect(html).toContain("Core 服务不可用 (CORE_UNAVAILABLE)");
    expect(html).toContain("系统不会自动重试");
    expect(html).toContain('data-testid="library-error"');
    expect(html).not.toContain('data-testid="library-book-list"');
  });

  it("renders loading indicator when loading is true", () => {
    const html = renderToString(
      <LibraryPanel initialState={{ loading: true, books: null, error: null }} />
    );

    expect(html).toContain("正在加载书目数据...");
    expect(html).toContain('data-testid="library-loading"');
  });

  it("interacts with LibraryClient without auto-retrying on failure", async () => {
    let callCount = 0;
    const invoke = vi.fn(async (cmd: string) => {
      callCount += 1;
      if (cmd === "library_list_books") {
        throw "CORE_UNAVAILABLE";
      }
      return null;
    });

    const client = new LibraryClient(invoke);
    await expect(client.listBooks()).rejects.toMatchObject({
      code: "CORE_UNAVAILABLE",
    });

    // Verify it was called exactly once, no retry loop
    expect(callCount).toBe(1);
  });

  it("mounts LibraryPanel without initialState and transitions to CORE_UNAVAILABLE when client call is rejected", async () => {
    class MockNode {
      childNodes: MockNode[] = [];
      parentNode: MockNode | null = null;
      nodeType = 1;
      appendChild<T extends MockNode>(child: T): T {
        child.parentNode = this;
        this.childNodes.push(child);
        return child;
      }
      removeChild<T extends MockNode>(child: T): T {
        const idx = this.childNodes.indexOf(child);
        if (idx !== -1) {
          this.childNodes.splice(idx, 1);
          child.parentNode = null;
        }
        return child;
      }
      insertBefore<T extends MockNode>(newNode: T, refNode: MockNode | null): T {
        if (!refNode) return this.appendChild(newNode);
        const idx = this.childNodes.indexOf(refNode);
        if (idx !== -1) {
          newNode.parentNode = this;
          this.childNodes.splice(idx, 0, newNode);
        } else {
          this.appendChild(newNode);
        }
        return newNode;
      }
    }

    class MockElement extends MockNode {
      nodeName: string;
      tagName: string;
      attributes: Record<string, string> = {};
      style: Record<string, any> = {};
      ownerDocument: any;

      constructor(tag: string, ownerDoc?: any) {
        super();
        this.nodeType = 1;
        this.nodeName = tag.toUpperCase();
        this.tagName = tag.toUpperCase();
        this.ownerDocument = ownerDoc;
      }
      setAttribute(k: string, v: any) { this.attributes[k] = String(v); }
      removeAttribute(k: string) { delete this.attributes[k]; }
      getAttribute(k: string) { return this.attributes[k]; }
      addEventListener() {}
      removeEventListener() {}
      get textContent(): string {
        return this.childNodes.map(c => (c as any).textContent || (c as any).nodeValue || "").join("");
      }
      set textContent(v: string) {
        this.childNodes = [new MockTextNode(v, this.ownerDocument)];
      }
    }

    class MockHTMLIFrameElement extends MockElement {}

    class MockTextNode extends MockNode {
      nodeName = "#text";
      nodeValue: string;
      ownerDocument: any;

      constructor(text: any, ownerDoc?: any) {
        super();
        this.nodeType = 3;
        this.nodeValue = String(text);
        this.ownerDocument = ownerDoc;
      }
      get textContent(): string { return this.nodeValue; }
      set textContent(v: string) { this.nodeValue = String(v); }
    }

    const doc: any = {
      nodeType: 9,
      nodeName: "#document",
      activeElement: null,
      addEventListener: () => {},
      removeEventListener: () => {},
      createElement: (tag: string) => new MockElement(tag, doc),
      createTextNode: (text: any) => new MockTextNode(text, doc),
    };
    const win: any = {
      addEventListener: () => {},
      removeEventListener: () => {},
      document: doc,
      Node: MockNode,
      Element: MockElement,
      HTMLIFrameElement: MockHTMLIFrameElement,
    };
    (globalThis as any).window = win;
    (globalThis as any).document = doc;
    (globalThis as any).Node = MockNode;
    (globalThis as any).Element = MockElement;

    const { createRoot } = await import("react-dom/client");

    let callCount = 0;
    const invoke = vi.fn(async (cmd: string) => {
      callCount += 1;
      if (cmd === "library_list_books") {
        throw "CORE_UNAVAILABLE";
      }
      return null;
    });

    const client = new LibraryClient(invoke);
    const container = new MockElement("DIV", doc);
    const root = createRoot(container as any);

    // Mount without initialState: triggers fetchBooks() inside useEffect
    root.render(<LibraryPanel client={client} />);

    // Wait for the async call and state transition
    await vi.waitFor(() => {
      expect(callCount).toBe(1);
      expect(container.textContent).toContain("Core 服务不可用 (CORE_UNAVAILABLE)");
      expect(container.textContent).toContain("系统不会自动重试");
    });

    expect(invoke).toHaveBeenCalledWith("library_list_books");
    expect(callCount).toBe(1);
  });
});
