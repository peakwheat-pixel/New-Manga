import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { setNativeSelectValue } from "../testSupport/jsdomEvents";
import { SettingsClient } from "./client";
import { ModelGpuSettingsPanel } from "./ModelGpuSettingsPanel";
import {
  validateModelGpuSettingsDraft,
  type DevicePreference,
  type ModelGpuSettingsDraft,
} from "./sections";

/**
 * SETTINGS-OPEN-B-1 §4.1 / AC4 — model_gpu.device_preference (auto | cpu |
 * gpu, default auto) and model_gpu.allow_cpu_fallback (default true): enum
 * select + boolean switch, exact whole-section payload, post-save re-read, the
 * closed §9 error projection, and the read-only notes (runtime device probing;
 * GPU concurrency / model download stay closed in this batch).
 */
describe("ModelGpuSettingsPanel (SETTINGS-OPEN-B-1 §4.1)", () => {
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
  const select = (id: string) => q(`[data-testid="${id}"]`) as HTMLSelectElement;
  const saveButton = () =>
    q('[data-testid="model-gpu-settings-panel-save-btn"]') as HTMLButtonElement;

  it("shows the loading skeleton while settings_get(section) is pending", () => {
    const invoke = vi.fn(() => new Promise(() => {}));
    act(() => {
      root.render(<ModelGpuSettingsPanel client={new SettingsClient(invoke)} />);
    });
    expect(q('[data-testid="model-gpu-settings-panel-loading"]')).not.toBeNull();
    expect(select("model-gpu-device-preference")).toBeNull();
  });

  it("reads the model_gpu section, renders the persisted values and the read-only notes", async () => {
    const invoke = vi.fn(async (command: string, args?: Record<string, unknown>) => {
      expect(command).toBe("settings_get");
      expect(args).toEqual({ section: "model_gpu" });
      return { settings: { model_gpu: { device_preference: "gpu", allow_cpu_fallback: false } } };
    });
    await act(async () => {
      root.render(<ModelGpuSettingsPanel client={new SettingsClient(invoke)} />);
    });
    expect(q('[data-testid="model-gpu-settings-panel-unset"]')).toBeNull();
    expect(select("model-gpu-device-preference").value).toBe("gpu");
    expect(input("model-gpu-allow-cpu-fallback").checked).toBe(false);
    expect(q('[data-testid="model-gpu-allow-cpu-fallback-state"]')?.textContent).toContain(
      "禁止回退",
    );
    expect(q('[data-testid="model-gpu-settings-panel-effective"]')?.textContent).toContain(
      "优先 GPU",
    );
    // Review-b1 M1: the persisted-value summary uses the adjudicated label —
    // gpu is a validation/fallback preference, not a forced device.
    expect(q('[data-testid="model-gpu-settings-panel-effective"]')?.textContent).toContain(
      "GPU 不可用时按回退策略",
    );
    expect(q('[data-testid="model-gpu-settings-panel-effect-note"]')?.textContent).toContain(
      "对之后启动的任务生效",
    );
    // Read-only surface: ability probing is the Provider's job at Run time, and
    // the preference never forces the provider's internal device choice (M1).
    expect(q('[data-testid="model-gpu-settings-panel-runtime-note"]')?.textContent).toContain(
      "运行时探测",
    );
    expect(q('[data-testid="model-gpu-settings-panel-runtime-note"]')?.textContent).toContain(
      "设备偏好用于 GPU 可用性校验与 CPU 回退决策，不强制 Provider 内部设备实现。",
    );
    expect(q('[data-testid="model-gpu-settings-panel-description"]')?.textContent).toContain(
      "不强制 Provider 内部设备实现",
    );
    // Closed in this batch: GPU concurrency, model download / path management.
    const scopeNote = q('[data-testid="model-gpu-settings-panel-scope-note"]');
    expect(scopeNote?.textContent).toContain("GPU 并发策略");
    expect(scopeNote?.textContent).toContain("模型下载");
    expect(saveButton().disabled).toBe(true);
  });

  it("renders 未设置 with the Core defaults when the section is JSON null", async () => {
    const invoke = vi.fn(async () => ({ settings: { model_gpu: null } }));
    await act(async () => {
      root.render(<ModelGpuSettingsPanel client={new SettingsClient(invoke)} />);
    });
    const unset = q('[data-testid="model-gpu-settings-panel-unset"]');
    expect(unset).not.toBeNull();
    expect(unset?.textContent).toContain("device_preference=auto");
    expect(unset?.textContent).toContain("allow_cpu_fallback=true");
    expect(select("model-gpu-device-preference").value).toBe("auto");
    expect(input("model-gpu-allow-cpu-fallback").checked).toBe(true);
  });

  it("falls back to the Core defaults for out-of-domain persisted values (never invents)", async () => {
    const invoke = vi.fn(async () => ({
      settings: { model_gpu: { device_preference: "tpu", allow_cpu_fallback: "yes" } },
    }));
    await act(async () => {
      root.render(<ModelGpuSettingsPanel client={new SettingsClient(invoke)} />);
    });
    expect(select("model-gpu-device-preference").value).toBe("auto");
    expect(input("model-gpu-allow-cpu-fallback").checked).toBe(true);
  });

  it("offers exactly the auto | cpu | gpu value domain", async () => {
    const invoke = vi.fn(async () => ({ settings: { model_gpu: null } }));
    await act(async () => {
      root.render(<ModelGpuSettingsPanel client={new SettingsClient(invoke)} />);
    });
    expect(Array.from(select("model-gpu-device-preference").options).map((o) => o.value)).toEqual([
      "auto",
      "cpu",
      "gpu",
    ]);
    // Review-b1 M1: the option labels carry the validation/fallback semantics;
    // none of them promises a forced device.
    expect(
      Array.from(select("model-gpu-device-preference").options).map((o) => o.textContent),
    ).toEqual([
      "自动 (auto)",
      "仅 CPU (cpu，跳过 GPU 校验)",
      "优先 GPU (gpu，GPU 不可用时按回退策略)",
    ]);

    // The pure validator guards the same frozen domain (the Core re-validates).
    const invalid: ModelGpuSettingsDraft = {
      device_preference: "tpu" as DevicePreference,
      allow_cpu_fallback: true,
    };
    expect(validateModelGpuSettingsDraft(invalid).device_preference).toContain(
      "auto / cpu / gpu",
    );
    expect(
      validateModelGpuSettingsDraft({ device_preference: "cpu", allow_cpu_fallback: true }),
    ).toEqual({});
    expect(saveButton().disabled).toBe(true);
  });

  it("saves the exact whole-section payload and re-reads the persisted value", async () => {
    let stored: Record<string, unknown> = {
      device_preference: "auto",
      allow_cpu_fallback: true,
    };
    let getCalls = 0;
    const invoke = vi.fn(async (command: string, args?: Record<string, unknown>) => {
      if (command === "settings_update_section") {
        expect(args).toEqual({
          section: "model_gpu",
          values: { device_preference: "gpu", allow_cpu_fallback: false },
        });
        stored = args?.values as Record<string, unknown>;
        return {};
      }
      getCalls += 1;
      return { settings: { model_gpu: stored } };
    });
    await act(async () => {
      root.render(<ModelGpuSettingsPanel client={new SettingsClient(invoke)} />);
    });
    await act(async () => {
      setNativeSelectValue(dom.window, select("model-gpu-device-preference"), "gpu");
    });
    await act(async () => {
      input("model-gpu-allow-cpu-fallback").click();
    });
    expect(input("model-gpu-allow-cpu-fallback").checked).toBe(false);
    expect(saveButton().disabled).toBe(false);
    await act(async () => {
      saveButton().click();
    });
    expect(getCalls).toBe(2); // initial read + post-save re-read
    expect(select("model-gpu-device-preference").value).toBe("gpu");
    expect(input("model-gpu-allow-cpu-fallback").checked).toBe(false);
    expect(q('[data-testid="model-gpu-settings-panel-effective"]')?.textContent).toContain(
      "禁止",
    );
    expect(q('[data-testid="model-gpu-settings-panel-save-error"]')).toBeNull();
  });

  it("load failure shows the closed §9 projection with retry, never the raw payload", async () => {
    const invoke = vi.fn(async () => {
      throw "CORE_UNAVAILABLE";
    });
    await act(async () => {
      root.render(<ModelGpuSettingsPanel client={new SettingsClient(invoke)} />);
    });
    const bar = q('[data-testid="model-gpu-settings-panel-load-error"]');
    expect(bar).not.toBeNull();
    expect(bar?.getAttribute("data-message-key")).toBe("SETTINGS_UNAVAILABLE");
    expect(container.textContent).not.toContain("CORE_UNAVAILABLE");
    expect(q('[data-testid="model-gpu-settings-panel-load-error-retry"]')).not.toBeNull();
  });

  it("a failed save keeps the user's draft and shows the localized error", async () => {
    const invoke = vi.fn(async (command: string) => {
      if (command === "settings_update_section") {
        throw { code: "INVALID_REQUEST" };
      }
      return { settings: { model_gpu: { device_preference: "auto", allow_cpu_fallback: true } } };
    });
    await act(async () => {
      root.render(<ModelGpuSettingsPanel client={new SettingsClient(invoke)} />);
    });
    await act(async () => {
      setNativeSelectValue(dom.window, select("model-gpu-device-preference"), "cpu");
    });
    await act(async () => {
      saveButton().click();
    });
    const bar = q('[data-testid="model-gpu-settings-panel-save-error"]');
    expect(bar).not.toBeNull();
    expect(bar?.getAttribute("data-error-category")).toBe("validation");
    expect(select("model-gpu-device-preference").value).toBe("cpu");
    // The effective value is unchanged until a save succeeds.
    expect(q('[data-testid="model-gpu-settings-panel-effective"]')?.textContent).toContain(
      "自动",
    );
  });
});
