import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { setNativeInputValue } from "../testSupport/jsdomEvents";
import { SettingsClient } from "./client";
import { TasksSettingsPanel } from "./TasksSettingsPanel";

/**
 * SETTINGS-OPEN-B-1 §4.2 / AC4 — tasks.retry_max_attempts (int 1–3, default 3)
 * and tasks.retry_backoff_seconds (float 0.1–30, default 1.0): numeric range
 * validation blocks the write, the payload carries numbers (not draft
 * strings), the saved value is re-read from the Core projection, and the
 * concurrency count is surfaced as the read-only "任务串行执行（并发数不开放）"
 * note — never a fake control.
 */
describe("TasksSettingsPanel (SETTINGS-OPEN-B-1 §4.2)", () => {
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
  const input = (id: string) => q(`[data-testid="${id}"]`) as HTMLInputElement;
  const saveButton = () =>
    q('[data-testid="tasks-settings-panel-save-btn"]') as HTMLButtonElement;

  it("shows the loading skeleton while settings_get(section) is pending", () => {
    const invoke = vi.fn(() => new Promise(() => {}));
    act(() => {
      root.render(<TasksSettingsPanel client={new SettingsClient(invoke)} />);
    });
    expect(q('[data-testid="tasks-settings-panel-loading"]')).not.toBeNull();
    expect(input("tasks-retry-max-attempts")).toBeNull();
  });

  it("reads the tasks section, renders the persisted values, the serial note and the effect note", async () => {
    const invoke = vi.fn(async (command: string, args?: Record<string, unknown>) => {
      expect(command).toBe("settings_get");
      expect(args).toEqual({ section: "tasks" });
      return { settings: { tasks: { retry_max_attempts: 2, retry_backoff_seconds: 2.5 } } };
    });
    await act(async () => {
      root.render(<TasksSettingsPanel client={new SettingsClient(invoke)} />);
    });
    expect(q('[data-testid="tasks-settings-panel-unset"]')).toBeNull();
    expect(input("tasks-retry-max-attempts").value).toBe("2");
    expect(input("tasks-retry-backoff-seconds").value).toBe("2.5");
    expect(q('[data-testid="tasks-settings-panel-effective"]')?.textContent).toContain(
      "重试上限 2 次",
    );
    expect(q('[data-testid="tasks-settings-panel-effect-note"]')?.textContent).toContain(
      "对之后启动的任务生效",
    );
    expect(q('[data-testid="tasks-settings-panel-serial-note"]')?.textContent).toContain(
      "任务串行执行（并发数不开放）",
    );
    // No concurrency control exists anywhere in this panel.
    expect(q('[data-testid="tasks-concurrency"]')).toBeNull();
    expect(input("tasks-retry-max-attempts").getAttribute("max")).toBe("3");
    expect(input("tasks-retry-backoff-seconds").getAttribute("min")).toBe("0.1");
    expect(saveButton().disabled).toBe(true);
  });

  it("renders 未设置 with the Core default retry policy when the section is JSON null", async () => {
    const invoke = vi.fn(async () => ({ settings: { tasks: null } }));
    await act(async () => {
      root.render(<TasksSettingsPanel client={new SettingsClient(invoke)} />);
    });
    const unset = q('[data-testid="tasks-settings-panel-unset"]');
    expect(unset).not.toBeNull();
    expect(unset?.textContent).toContain("retry_max_attempts=3");
    expect(unset?.textContent).toContain("retry_backoff_seconds=1.0");
    expect(input("tasks-retry-max-attempts").value).toBe("3");
    expect(input("tasks-retry-backoff-seconds").value).toBe("1.0");
  });

  it("saves the numeric whole-section payload and re-reads the persisted value", async () => {
    let stored: Record<string, unknown> = { retry_max_attempts: 3, retry_backoff_seconds: 1 };
    let getCalls = 0;
    const invoke = vi.fn(async (command: string, args?: Record<string, unknown>) => {
      if (command === "settings_update_section") {
        expect(args).toEqual({
          section: "tasks",
          values: { retry_max_attempts: 2, retry_backoff_seconds: 2.5 },
        });
        stored = args?.values as Record<string, unknown>;
        return {};
      }
      getCalls += 1;
      return { settings: { tasks: stored } };
    });
    await act(async () => {
      root.render(<TasksSettingsPanel client={new SettingsClient(invoke)} />);
    });
    await act(async () => {
      setNativeInputValue(dom.window, input("tasks-retry-max-attempts"), "2");
    });
    await act(async () => {
      setNativeInputValue(dom.window, input("tasks-retry-backoff-seconds"), "2.5");
    });
    expect(saveButton().disabled).toBe(false);
    await act(async () => {
      saveButton().click();
    });
    expect(getCalls).toBe(2); // initial read + post-save re-read
    expect(input("tasks-retry-max-attempts").value).toBe("2");
    expect(input("tasks-retry-backoff-seconds").value).toBe("2.5");
    expect(q('[data-testid="tasks-settings-panel-effective"]')?.textContent).toContain(
      "退避 2.5 秒",
    );
    expect(q('[data-testid="tasks-settings-panel-save-error"]')).toBeNull();
  });

  it("blocks the save and explains the range when retry_max_attempts is out of 1–3", async () => {
    const invoke = vi.fn(async () => ({ settings: { tasks: null } }));
    await act(async () => {
      root.render(<TasksSettingsPanel client={new SettingsClient(invoke)} />);
    });
    await act(async () => {
      setNativeInputValue(dom.window, input("tasks-retry-max-attempts"), "4");
    });
    const error = q('[data-testid="tasks-retry-max-attempts-error"]');
    expect(error).not.toBeNull();
    expect(error?.textContent).toContain("1–3");
    expect(input("tasks-retry-max-attempts").getAttribute("aria-invalid")).toBe("true");
    expect(saveButton().disabled).toBe(true);
    expect(invoke).not.toHaveBeenCalledWith("settings_update_section", expect.anything());
  });

  it("rejects a non-integer retry_max_attempts (string draft still representable)", async () => {
    const invoke = vi.fn(async () => ({ settings: { tasks: null } }));
    await act(async () => {
      root.render(<TasksSettingsPanel client={new SettingsClient(invoke)} />);
    });
    await act(async () => {
      setNativeInputValue(dom.window, input("tasks-retry-max-attempts"), "2.5");
    });
    expect(q('[data-testid="tasks-retry-max-attempts-error"]')?.textContent).toContain("1–3");
    expect(saveButton().disabled).toBe(true);
  });

  it("blocks the save and explains the range when retry_backoff_seconds is out of 0.1–30", async () => {
    const invoke = vi.fn(async () => ({ settings: { tasks: null } }));
    await act(async () => {
      root.render(<TasksSettingsPanel client={new SettingsClient(invoke)} />);
    });
    await act(async () => {
      setNativeInputValue(dom.window, input("tasks-retry-backoff-seconds"), "0.05");
    });
    const error = q('[data-testid="tasks-retry-backoff-seconds-error"]');
    expect(error).not.toBeNull();
    expect(error?.textContent).toContain("0.1–30");
    expect(input("tasks-retry-backoff-seconds").getAttribute("aria-invalid")).toBe("true");
    expect(saveButton().disabled).toBe(true);
    expect(invoke).not.toHaveBeenCalledWith("settings_update_section", expect.anything());
  });

  it("accepts the frozen boundary values 1 / 3 and 0.1 / 30", async () => {
    const invoke = vi.fn(async () => ({ settings: { tasks: null } }));
    await act(async () => {
      root.render(<TasksSettingsPanel client={new SettingsClient(invoke)} />);
    });
    await act(async () => {
      setNativeInputValue(dom.window, input("tasks-retry-max-attempts"), "1");
      setNativeInputValue(dom.window, input("tasks-retry-backoff-seconds"), "0.1");
    });
    expect(q('[data-testid="tasks-retry-max-attempts-error"]')).toBeNull();
    expect(q('[data-testid="tasks-retry-backoff-seconds-error"]')).toBeNull();
    expect(saveButton().disabled).toBe(false);

    await act(async () => {
      setNativeInputValue(dom.window, input("tasks-retry-max-attempts"), "3");
      setNativeInputValue(dom.window, input("tasks-retry-backoff-seconds"), "30");
    });
    expect(q('[data-testid="tasks-retry-max-attempts-error"]')).toBeNull();
    expect(q('[data-testid="tasks-retry-backoff-seconds-error"]')).toBeNull();
    expect(saveButton().disabled).toBe(false);
  });

  it("load failure shows the closed §9 projection with retry, never the raw payload", async () => {
    const invoke = vi.fn(async () => {
      throw "CORE_UNAVAILABLE";
    });
    await act(async () => {
      root.render(<TasksSettingsPanel client={new SettingsClient(invoke)} />);
    });
    const bar = q('[data-testid="tasks-settings-panel-load-error"]');
    expect(bar).not.toBeNull();
    expect(bar?.getAttribute("data-message-key")).toBe("SETTINGS_UNAVAILABLE");
    expect(container.textContent).not.toContain("CORE_UNAVAILABLE");
    expect(q('[data-testid="tasks-settings-panel-load-error-retry"]')).not.toBeNull();
  });

  it("a failed save keeps the user's draft and shows the localized error", async () => {
    const invoke = vi.fn(async (command: string) => {
      if (command === "settings_update_section") {
        throw { code: "INVALID_REQUEST" };
      }
      return { settings: { tasks: { retry_max_attempts: 3, retry_backoff_seconds: 1 } } };
    });
    await act(async () => {
      root.render(<TasksSettingsPanel client={new SettingsClient(invoke)} />);
    });
    await act(async () => {
      setNativeInputValue(dom.window, input("tasks-retry-max-attempts"), "1");
    });
    await act(async () => {
      saveButton().click();
    });
    const bar = q('[data-testid="tasks-settings-panel-save-error"]');
    expect(bar).not.toBeNull();
    expect(bar?.getAttribute("data-error-category")).toBe("validation");
    expect(input("tasks-retry-max-attempts").value).toBe("1");
    // The effective value is unchanged until a save succeeds.
    expect(q('[data-testid="tasks-settings-panel-effective"]')?.textContent).toContain(
      "重试上限 3 次",
    );
  });
});
