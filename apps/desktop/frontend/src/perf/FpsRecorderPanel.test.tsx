import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "../App";
import { FpsRecorderPanel } from "./FpsRecorderPanel";
import { createFpsRecorder, type FpsRecorderDeps } from "./fpsRecorder";

class FakeRaf {
  callback: ((timestampMs: number) => void) | null = null;
  nextHandle = 0;
  readonly request = (callback: (timestampMs: number) => void): number => {
    this.callback = callback;
    this.nextHandle += 1;
    return this.nextHandle;
  };
  readonly cancel = (_handle: number): void => {
    this.callback = null;
  };
  advance(timestampMs: number): void {
    const callback = this.callback;
    this.callback = null;
    if (callback) callback(timestampMs);
  }
  get deps(): FpsRecorderDeps {
    return { requestAnimationFrame: this.request, cancelAnimationFrame: this.cancel };
  }
}

function driveFrames(raf: FakeRaf, timestamps: number[]): void {
  for (const ts of timestamps) raf.advance(ts);
}

function buttonByText(container: HTMLElement, text: string): HTMLButtonElement {
  const buttons = Array.from(container.querySelectorAll("button"));
  const found = buttons.find((b) => b.textContent === text);
  if (!found) throw new Error(`button not found: ${text}`);
  return found as HTMLButtonElement;
}

/** Installs a window.showSaveFilePicker stand-in; pass null to simulate an
 * environment without the File System Access API. */
function stubSavePicker(
  window: JSDOM["window"],
  picker: ((...args: never[]) => Promise<unknown>) | null,
): void {
  Object.defineProperty(window, "showSaveFilePicker", {
    configurable: true,
    ...(picker === null ? {} : { value: picker }),
  });
}

describe("P20-AC4-FPS-1 FpsRecorderPanel (mount gating + export channels)", () => {
  let dom: JSDOM;
  let container: HTMLDivElement;
  let root: Root;
  let createObjectUrlMock: ReturnType<typeof vi.fn>;
  let originalCreateObjectUrl: unknown;
  let anchorClickSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    dom = new JSDOM("<!doctype html><html><body></body></html>", { url: "http://localhost/" });
    vi.stubGlobal("window", dom.window);
    vi.stubGlobal("document", dom.window.document);
    vi.stubGlobal("navigator", dom.window.navigator);
    vi.stubGlobal("HTMLElement", dom.window.HTMLElement);
    container = dom.window.document.createElement("div");
    dom.window.document.body.appendChild(container);
    root = createRoot(container);
    // The vitest node environment already polyfills URL.createObjectURL, so
    // replace it unconditionally with an observable mock and restore after.
    // The export path must NEVER call it (FPS-R1-04: no silent blob download).
    originalCreateObjectUrl = (URL as { createObjectURL?: unknown }).createObjectURL;
    createObjectUrlMock = vi.fn(() => "blob:test-url");
    Object.defineProperty(URL, "createObjectURL", { value: createObjectUrlMock, configurable: true });
    anchorClickSpy = vi.spyOn(dom.window.HTMLAnchorElement.prototype, "click");
  });

  afterEach(() => {
    act(() => {
      root.unmount();
    });
    if (originalCreateObjectUrl === undefined) {
      delete (URL as { createObjectURL?: unknown }).createObjectURL;
    } else {
      Object.defineProperty(URL, "createObjectURL", { value: originalCreateObjectUrl, configurable: true });
    }
    delete (dom.window as { showSaveFilePicker?: unknown }).showSaveFilePicker;
    vi.unstubAllGlobals();
  });

  // ---- AC1 companion: the default app tree never contains the panel ----

  it("App rendered without a sampling switch mounts no FPS panel (default DOM unchanged)", async () => {
    await act(async () => {
      root.render(<App />);
    });
    expect(container.querySelector('[data-testid="fps-recorder-panel"]')).toBeNull();
    expect(dom.window.document.title).not.toContain("M2FPS");
  });

  // ---- panel behaviour while sampling ----

  it("shows running state and live sample count after refresh", async () => {
    const raf = new FakeRaf();
    const recorder = createFpsRecorder({ ...raf.deps, visibility: null });
    recorder.start();
    await act(async () => {
      root.render(<FpsRecorderPanel recorder={recorder} />);
    });
    expect(container.querySelector('[data-testid="fps-recorder-panel"]')).not.toBeNull();
    expect(container.querySelector('[data-testid="fps-panel-state"]')?.textContent).toContain("RUNNING");

    driveFrames(raf, [0, 16, 32]);
    await act(async () => {
      buttonByText(container, "FPS: Refresh").click();
    });
    expect(container.querySelector('[data-testid="fps-panel-state"]')?.textContent).toContain("samples: 2");
    expect(container.querySelector('[data-testid="fps-panel-stats"]')?.textContent).toContain("avg: 16 ms");
    recorder.stop();
  });

  it("Stop freezes sampling and publishes the one-line summary to the window title", async () => {
    const raf = new FakeRaf();
    const recorder = createFpsRecorder({ ...raf.deps, visibility: null });
    recorder.start();
    driveFrames(raf, [0, 16, 32]);
    await act(async () => {
      root.render(<FpsRecorderPanel recorder={recorder} />);
    });
    await act(async () => {
      buttonByText(container, "FPS: Stop").click();
    });
    expect(recorder.isRunning()).toBe(false);
    expect(dom.window.document.title).toContain("M2FPS state=STOPPED samples=2");
    expect(dom.window.document.title).toContain("avg=16");
    recorder.stop();
  });

  it("Reset & Start drops previous samples and samples afresh (multi-round runs)", async () => {
    const raf = new FakeRaf();
    const recorder = createFpsRecorder({ ...raf.deps, visibility: null });
    recorder.start();
    driveFrames(raf, [0, 16]);
    await act(async () => {
      root.render(<FpsRecorderPanel recorder={recorder} />);
    });
    await act(async () => {
      buttonByText(container, "FPS: Reset & Start").click();
    });
    expect(recorder.isRunning()).toBe(true);
    driveFrames(raf, [1000, 1016]);
    expect(recorder.getSamples()).toHaveLength(1);
    expect(recorder.getSamples()[0].seq).toBe(1);
    recorder.stop();
  });

  // ---- export channels ----

  it("Show CSV / Show JSON fill the read-only output area for UIA ValuePattern pickup", async () => {
    const raf = new FakeRaf();
    const recorder = createFpsRecorder({ ...raf.deps, visibility: null });
    recorder.start();
    driveFrames(raf, [0, 16]);
    await act(async () => {
      root.render(<FpsRecorderPanel recorder={recorder} />);
    });
    await act(async () => {
      buttonByText(container, "FPS: Show CSV").click();
    });
    const output = container.querySelector('[data-testid="fps-data-output"]') as HTMLTextAreaElement;
    expect(output.value.startsWith("seq,frame_ts_ms,frame_time_ms,instant_fps,excluded,exclude_reason")).toBe(true);
    expect(output.value).toContain("1,16,16,62.5,0,");

    await act(async () => {
      buttonByText(container, "FPS: Show JSON").click();
    });
    expect(output.value).toContain("\"task\": \"P20-AC4-FPS-1\"");
    recorder.stop();
  });

  it("Export CSV writes ONLY through the explicit Save As picker to the chosen destination", async () => {
    const raf = new FakeRaf();
    const recorder = createFpsRecorder({ ...raf.deps, visibility: null });
    recorder.start();
    driveFrames(raf, [0, 16]);
    const written: string[] = [];
    const handle = {
      createWritable: vi.fn(async () => ({
        write: vi.fn(async (data: string) => {
          written.push(data);
        }),
        close: vi.fn(async () => {}),
      })),
    };
    let suggestedName = "";
    stubSavePicker(dom.window, async (options: { suggestedName: string }) => {
      suggestedName = options.suggestedName;
      return handle;
    });
    await act(async () => {
      root.render(<FpsRecorderPanel recorder={recorder} />);
    });
    await act(async () => {
      buttonByText(container, "FPS: Export CSV").click();
    });
    await act(async () => {});
    expect(handle.createWritable).toHaveBeenCalledTimes(1);
    expect(written).toEqual([recorder.toCsv()]);
    expect(suggestedName).toMatch(/^m2-fps-\d{8}-\d{6}\.csv$/);
    expect(container.textContent).toContain("saved to the chosen location");
    // FPS-R1-04: no silent blob/anchor.download fallback path was taken.
    expect(createObjectUrlMock).not.toHaveBeenCalled();
    expect(anchorClickSpy).not.toHaveBeenCalled();
    recorder.stop();
  });

  it("Export cancelled in the Save As dialog writes nothing and falls back to no location", async () => {
    const raf = new FakeRaf();
    const recorder = createFpsRecorder({ ...raf.deps, visibility: null });
    recorder.start();
    driveFrames(raf, [0, 16]);
    stubSavePicker(dom.window, async () => {
      throw new dom.window.DOMException("The user aborted the request", "AbortError");
    });
    await act(async () => {
      root.render(<FpsRecorderPanel recorder={recorder} />);
    });
    await act(async () => {
      buttonByText(container, "FPS: Export JSON").click();
    });
    await act(async () => {});
    expect(container.textContent).toContain("cancelled — nothing written");
    expect(container.textContent).toContain("no default-location fallback");
    expect(createObjectUrlMock).not.toHaveBeenCalled();
    expect(anchorClickSpy).not.toHaveBeenCalled();
    recorder.stop();
  });

  it("Export without a save-picker API writes nothing and points to the Show/Copy channels", async () => {
    const raf = new FakeRaf();
    const recorder = createFpsRecorder({ ...raf.deps, visibility: null });
    recorder.start();
    driveFrames(raf, [0, 16]);
    stubSavePicker(dom.window, null); // no showSaveFilePicker in this environment
    await act(async () => {
      root.render(<FpsRecorderPanel recorder={recorder} />);
    });
    await act(async () => {
      buttonByText(container, "FPS: Export CSV").click();
    });
    await act(async () => {});
    expect(container.textContent).toContain("explicit save dialog unavailable");
    expect(container.textContent).toContain("nothing written");
    expect(createObjectUrlMock).not.toHaveBeenCalled();
    expect(anchorClickSpy).not.toHaveBeenCalled();
    recorder.stop();
  });

  it("Copy CSV degrades to a visible note when the clipboard is unavailable", async () => {
    const raf = new FakeRaf();
    const recorder = createFpsRecorder({ ...raf.deps, visibility: null });
    recorder.start();
    driveFrames(raf, [0, 16]);
    // Force a clipboard-less navigator regardless of jsdom version behaviour
    vi.stubGlobal("navigator", {});
    await act(async () => {
      root.render(<FpsRecorderPanel recorder={recorder} />);
    });
    await act(async () => {
      buttonByText(container, "FPS: Copy CSV").click();
    });
    expect(container.textContent).toContain("clipboard unavailable");
    recorder.stop();
  });
});
