import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ExportDialog, type ExportDialogProps } from "./ExportDialog";

describe("ExportDialog", () => {
  let dom: JSDOM;
  let root: Root;
  let host: HTMLDivElement;

  afterEach(() => {
    act(() => root?.unmount());
    vi.unstubAllGlobals();
  });

  function mount(overrides: Partial<ExportDialogProps> = {}) {
    dom = new JSDOM("<!doctype html><html><body></body></html>", { url: "http://localhost" });
    vi.stubGlobal("window", dom.window);
    vi.stubGlobal("document", dom.window.document);
    vi.stubGlobal("HTMLElement", dom.window.HTMLElement);
    vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
    host = dom.window.document.createElement("div");
    dom.window.document.body.appendChild(host);
    root = createRoot(host);
    const props: ExportDialogProps = {
      isOpen: true, bookId: "book-1", chapterId: "chapter-1", pageIds: ["page-1"],
      snapshot: null, history: [], busy: false, historyLoading: false, error: null,
      onClose: vi.fn(), onStart: vi.fn(async () => true), onCancel: vi.fn(),
      onReveal: vi.fn(), onRefreshHistory: vi.fn(), ...overrides,
    };
    act(() => root.render(<ExportDialog {...props} />));
    return props;
  }

  it("renders format-specific options, enforces PNG single-page selection, and sends the selected options", async () => {
    const props = mount({ pageIds: ["page-1", "page-2"] });
    const format = host.querySelector('[data-testid="export-format"]') as HTMLSelectElement;
    act(() => { format.value = "png"; format.dispatchEvent(new dom.window.Event("change", { bubbles: true })); });
    const pngWarning = host.querySelector('[role="status"]');
    expect(pngWarning?.textContent).toContain("PNG 只能导出单页");
    expect((host.querySelector('[data-testid="start-export"]') as HTMLButtonElement).disabled).toBe(true);

    act(() => { format.value = "pdf"; format.dispatchEvent(new dom.window.Event("change", { bubbles: true })); });
    expect(host.textContent).toContain("PDF 内容");
    const pdfContent = host.querySelectorAll("select")[1] as HTMLSelectElement;
    act(() => { pdfContent.value = "searchable_dual_layer"; pdfContent.dispatchEvent(new dom.window.Event("change", { bubbles: true })); });
    await act(async () => { (host.querySelector('[data-testid="start-export"]') as HTMLButtonElement).click(); });
    expect(props.onStart).toHaveBeenCalledWith(expect.objectContaining({
      book_id: "book-1", chapter_ids: ["chapter-1"], ordered_page_ids: ["page-1", "page-2"],
      format: "pdf", format_options: { pdf_content: "searchable_dual_layer" }, stale_policy: "abort",
    }));
  });

  it("shows selection cancellation, snapshot progress/actions, history, and busy state", async () => {
    const props = mount({
      onStart: vi.fn(async () => false),
      snapshot: {
        export_id: "export-1", status: "running", completed_pages: 1, total_pages: 2,
        current_page_id: "page-2", completed_at: null, output: null, error_code: null,
      },
      history: [{
        export_id: "export-old", book_id: "book-1", chapter_ids: ["chapter-1"], ordered_page_ids: ["page-1"],
        format: "zip", created_at: "2026-10-16T00:00:00Z", completed_at: "2026-10-16T00:01:00Z",
        status: "completed", sha256: null,
      }],
    });
    expect(host.querySelector('[aria-label="导出进度"]')?.getAttribute("value")).toBe("1");
    expect(host.querySelector('[data-testid="cancel-export"]')).not.toBeNull();
    expect(host.querySelector('[data-testid="export-history-completed"]')?.textContent).toContain("ZIP");
    await act(async () => { (host.querySelector('[data-testid="start-export"]') as HTMLButtonElement).click(); });
    expect(host.querySelector('[data-testid="export-message"]')?.textContent).toContain("选择已取消");

    act(() => { (host.querySelector('[data-testid="cancel-export"]') as HTMLButtonElement).click(); });
    expect(props.onCancel).toHaveBeenCalledOnce();
    const reveal = host.querySelector('[data-testid="export-history-completed"] button') as HTMLButtonElement;
    act(() => reveal.click());
    expect(props.onReveal).toHaveBeenCalledWith("export-old");

    act(() => root.render(<ExportDialog {...props} busy historyLoading />));
    expect(host.textContent).toContain("正在读取导出历史");
    expect((host.querySelector('[data-testid="start-export"]') as HTMLButtonElement).disabled).toBe(true);
  });

  it("refreshes history on open and closes with Escape", () => {
    const props = mount();
    expect(props.onRefreshHistory).toHaveBeenCalledOnce();
    expect(host.textContent).toContain("暂无导出记录");
    act(() => dom.window.dispatchEvent(new dom.window.KeyboardEvent("keydown", { key: "Escape" })));
    expect(props.onClose).toHaveBeenCalledOnce();
  });

  it("localizes retryable errors and retries by refreshing the authoritative export state", () => {
    const onRetry = vi.fn();
    mount({ error: "CORE_UNAVAILABLE", onRetry });
    const error = host.querySelector('[data-testid="export-error"]');
    expect(error?.textContent).toContain("Python Core 核心服务当前不可用");
    expect(error?.textContent).not.toContain("C:\\");
    const retry = error?.querySelector("button");
    expect(retry?.textContent).toBe("重试");
    act(() => retry?.click());
    expect(onRetry).toHaveBeenCalledOnce();
  });
});
