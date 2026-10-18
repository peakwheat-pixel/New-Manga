import { JSDOM } from "jsdom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  FPS_AVG_THRESHOLD_MS,
  FPS_GAP_EXCLUDE_REASON,
  FPS_LOCALSTORAGE_KEY,
  FPS_NON_POSITIVE_EXCLUDE_REASON,
  FPS_QUERY_PARAM,
  createFpsRecorder,
  getActiveFpsRecorder,
  readFpsRecorderRequest,
  startFpsRecorder,
  stopFpsRecorder,
  type FpsRecorderDeps,
  type FpsVisibilitySource,
} from "./fpsRecorder";

/** Deterministic rAF stand-in: exactly one pending callback at a time,
 * manually advanced by the test with explicit frame timestamps. nowMs doubles
 * as the injected performance.now() clock so hidden-interval bookkeeping and
 * rAF timestamps share one time domain. */
class FakeRaf {
  callback: ((timestampMs: number) => void) | null = null;
  nextHandle = 0;
  registrations = 0;
  cancelledHandles: number[] = [];
  nowMs = 0;
  readonly request = (callback: (timestampMs: number) => void): number => {
    this.callback = callback;
    this.nextHandle += 1;
    this.registrations += 1;
    return this.nextHandle;
  };
  readonly cancel = (handle: number): void => {
    this.cancelledHandles.push(handle);
    this.callback = null;
  };
  advance(timestampMs: number): void {
    this.nowMs = timestampMs;
    const callback = this.callback;
    this.callback = null;
    if (callback) callback(timestampMs);
  }
  setNow(timestampMs: number): void {
    this.nowMs = timestampMs;
  }
  get deps(): FpsRecorderDeps {
    return {
      requestAnimationFrame: this.request,
      cancelAnimationFrame: this.cancel,
      now: () => this.nowMs,
    };
  }
}

/** Deterministic visibility stand-in for the >=1s-gap exclusion rule. */
class FakeVisibility {
  hidden = false;
  private listeners: Array<() => void> = [];
  setHidden(hidden: boolean): void {
    this.hidden = hidden;
    for (const listener of [...this.listeners]) listener();
  }
  get source(): FpsVisibilitySource {
    return {
      addListener: (onChange) => {
        this.listeners.push(onChange);
        return () => {
          this.listeners = this.listeners.filter((l) => l !== onChange);
        };
      },
      isHidden: () => this.hidden,
    };
  }
}

describe("P20-AC4-FPS-1 fpsRecorder (AC1 default-off / sampling / export)", () => {
  let dom: JSDOM;
  let rafSpy: FakeRaf;

  beforeEach(() => {
    dom = new JSDOM("<!doctype html><html><body></body></html>", { url: "http://localhost/" });
    vi.stubGlobal("window", dom.window);
    // A spy on the global rAF entry point proves whether ANY registration
    // happened, including through the default (non-injected) deps path.
    rafSpy = new FakeRaf();
    vi.stubGlobal("requestAnimationFrame", rafSpy.request);
    vi.stubGlobal("cancelAnimationFrame", rafSpy.cancel);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  // ---- AC1: default-off is zero-cost (no rAF registration, no array) ----

  it("module import + default switch read register no rAF callback and keep no recorder instance", () => {
    // Importing the module and evaluating the switches must not touch rAF.
    expect(readFpsRecorderRequest()).toBe(false);
    expect(rafSpy.registrations).toBe(0);
    // No recorder object exists => no sample array was ever allocated.
    expect(getActiveFpsRecorder()).toBeNull();
  });

  it("a created recorder that has not started registers no rAF and exposes no samples", () => {
    const recorder = createFpsRecorder();
    expect(recorder.isRunning()).toBe(false);
    expect(rafSpy.registrations).toBe(0);
    expect(recorder.getSamples()).toEqual([]);
    expect(recorder.getSummary().totalSamples).toBe(0);
    expect(recorder.getSummary().kept).toBeNull();
  });

  it("switch reading: only explicit on-values enable; every channel is honored", () => {
    // query param channel
    expect(readFpsRecorderRequest({ queryString: `?${FPS_QUERY_PARAM}=1` })).toBe(true);
    expect(readFpsRecorderRequest({ queryString: `?${FPS_QUERY_PARAM}=true` })).toBe(true);
    expect(readFpsRecorderRequest({ queryString: `?${FPS_QUERY_PARAM}=TRUE` })).toBe(true);
    expect(readFpsRecorderRequest({ queryString: `?${FPS_QUERY_PARAM}=0` })).toBe(false);
    expect(readFpsRecorderRequest({ queryString: "?unrelated=1" })).toBe(false);
    // localStorage channel
    expect(readFpsRecorderRequest({ localStorageValue: "1" })).toBe(true);
    expect(readFpsRecorderRequest({ localStorageValue: " true " })).toBe(true);
    expect(readFpsRecorderRequest({ localStorageValue: "0" })).toBe(false);
    expect(readFpsRecorderRequest({ localStorageValue: null })).toBe(false);
    // build flag channel
    expect(readFpsRecorderRequest({ buildFlagValue: "1" })).toBe(true);
    expect(readFpsRecorderRequest({ buildFlagValue: "true" })).toBe(true);
    expect(readFpsRecorderRequest({ buildFlagValue: undefined })).toBe(false);
    // default sources read the (switch-free) stubbed window
    expect(readFpsRecorderRequest()).toBe(false);

    // localStorage really is read from the window when no override is given
    dom.window.localStorage.setItem(FPS_LOCALSTORAGE_KEY, "1");
    expect(readFpsRecorderRequest()).toBe(true);
    dom.window.localStorage.removeItem(FPS_LOCALSTORAGE_KEY);
    expect(readFpsRecorderRequest()).toBe(false);
  });

  // ---- AC2: enabled state registers rAF and samples per frame ----

  it("start registers exactly one rAF callback, the first frame is baseline-only, then per-frame samples follow", () => {
    const raf = new FakeRaf();
    const recorder = createFpsRecorder({ ...raf.deps, visibility: null });
    recorder.start();
    expect(raf.registrations).toBe(1);

    raf.advance(0); // baseline frame: establishes timestamp, no sample
    expect(recorder.getSamples()).toEqual([]);
    expect(recorder.getSummary().baselineFrames).toBe(1);

    raf.advance(16.7);
    raf.advance(33.4);
    raf.advance(50.1);
    // start(1) + baseline re-register(1) + one re-register per sample(3)
    expect(raf.registrations).toBe(5);

    const samples = recorder.getSamples();
    expect(samples).toHaveLength(3);
    expect(samples[0]).toMatchObject({
      seq: 1,
      frameTsMs: 16.7,
      frameTimeMs: 16.7,
      instantFps: 59.88,
      excluded: false,
      excludeReason: null,
    });
    expect(samples[1].frameTimeMs).toBe(16.7);
    expect(samples[2].frameTimeMs).toBe(16.7);
    expect(samples.map((s) => s.seq)).toEqual([1, 2, 3]);
  });

  it("default deps bind to the global rAF entry point on start", () => {
    const recorder = createFpsRecorder(); // no injected deps
    recorder.start();
    expect(rafSpy.registrations).toBe(1);
    rafSpy.advance(0);
    rafSpy.advance(10);
    expect(recorder.getSamples()).toHaveLength(1);
    recorder.stop();
  });

  it("stop cancels the pending callback; no further samples are recorded", () => {
    const raf = new FakeRaf();
    const recorder = createFpsRecorder({ ...raf.deps, visibility: null });
    recorder.start();
    raf.advance(0);
    raf.advance(10);
    recorder.stop();
    expect(recorder.isRunning()).toBe(false);
    expect(raf.cancelledHandles).toHaveLength(1);
    expect(raf.callback).toBeNull();
    raf.advance(20); // nothing registered anymore
    raf.advance(30);
    expect(recorder.getSamples()).toHaveLength(1);
  });

  it("start is idempotent while running (no duplicate registration)", () => {
    const raf = new FakeRaf();
    const recorder = createFpsRecorder({ ...raf.deps, visibility: null });
    recorder.start();
    recorder.start();
    expect(raf.registrations).toBe(1);
  });

  // ---- AC4 (FPS-R1-05): >=1s gaps are excluded ONLY when hidden was tracked ----

  it("a >=1s gap WITHOUT visibility tracking (visible-page stall) is KEPT in the kept statistics", () => {
    const raf = new FakeRaf();
    const recorder = createFpsRecorder({ ...raf.deps, visibility: null });
    recorder.start();
    raf.advance(0);
    raf.advance(100); // 100ms normal frame
    raf.advance(5200); // 5100ms gap, page stayed visible (no hidden interval)
    raf.advance(5216.7);

    const samples = recorder.getSamples();
    expect(samples).toHaveLength(3);
    // No sample is excluded: nothing confirms the page was hidden.
    expect(samples.every((s) => !s.excluded)).toBe(true);
    const summary = recorder.getSummary();
    expect(summary.excludedCount).toBe(0);
    expect(summary.excludedReasons).toEqual({});
    expect(summary.visibilityTracked).toBe(false);
    // The 5100ms stall participates in the kept statistics — no spike masking.
    expect(summary.kept?.samples).toBe(3);
    expect(summary.kept?.maxMs).toBe(5100);
    expect(summary.avgWithinThreshold).toBe(false);

    const csv = recorder.toCsv();
    expect(csv).toContain("2,5200,5100,0.196,0,");
  });

  it("a >=1s gap overlapping a tracked hidden interval is excluded with a reason, yet stays in the CSV", () => {
    const raf = new FakeRaf();
    const vis = new FakeVisibility();
    const recorder = createFpsRecorder({ ...raf.deps, visibility: vis.source });
    recorder.start();
    raf.advance(0);
    raf.advance(100); // 100ms normal frame (visible)
    raf.setNow(110);
    vis.setHidden(true); // page hidden at t=110
    raf.advance(5200); // 5100ms gap covering the hidden interval
    raf.setNow(5210);
    vis.setHidden(false); // page visible again at t=5210
    raf.advance(5216.7);

    const samples = recorder.getSamples();
    expect(samples).toHaveLength(3);
    expect(samples[1]).toMatchObject({ excluded: true, excludeReason: FPS_GAP_EXCLUDE_REASON });
    expect(samples[0].excluded).toBe(false);
    expect(samples[2].excluded).toBe(false);

    const summary = recorder.getSummary();
    expect(summary.excludedCount).toBe(1);
    expect(summary.excludedReasons).toEqual({ [FPS_GAP_EXCLUDE_REASON]: 1 });
    expect(summary.kept?.samples).toBe(2);
    expect(summary.visibilityTracked).toBe(true);

    const csv = recorder.toCsv();
    const lines = csv.split("\n");
    expect(lines[0]).toBe("seq,frame_ts_ms,frame_time_ms,instant_fps,excluded,exclude_reason");
    expect(lines[2]).toBe("2,5200,5100,0.196,1,raf_gap_ge_1000ms_while_hidden");
  });

  it("a >=1s gap with a visibility source that never saw a hidden interval stays kept", () => {
    const raf = new FakeRaf();
    const vis = new FakeVisibility();
    const recorder = createFpsRecorder({ ...raf.deps, visibility: vis.source });
    recorder.start();
    raf.advance(0);
    raf.advance(100);
    raf.advance(5200); // long gap but the tracked page never went hidden
    raf.advance(5216.7);
    const summary = recorder.getSummary();
    expect(summary.excludedCount).toBe(0);
    expect(summary.kept?.samples).toBe(3);
    expect(summary.kept?.maxMs).toBe(5100);
    expect(summary.visibilityTracked).toBe(true);
  });

  it("summary reports the all-sample max and the excluded-sample max alongside the kept stats", () => {
    const raf = new FakeRaf();
    const vis = new FakeVisibility();
    const recorder = createFpsRecorder({ ...raf.deps, visibility: vis.source });
    recorder.start();
    raf.advance(0);
    raf.advance(16); // kept 16
    raf.advance(100); // kept 84
    raf.setNow(105);
    vis.setHidden(true);
    raf.advance(5200); // hidden gap 5100 -> excluded
    raf.setNow(5205);
    vis.setHidden(false);
    raf.advance(5216); // kept 16
    const summary = recorder.getSummary();
    expect(summary.kept).toEqual({ samples: 3, avgMs: 38.667, minMs: 16, maxMs: 84, p95Ms: 84 });
    expect(summary.allMaxMs).toBe(5100);
    expect(summary.excludedMaxMs).toBe(5100);
    // With no exclusions at all both maxima still reflect the truth.
    const clean = createFpsRecorder({ ...new FakeRaf().deps, visibility: null });
    clean.start();
    expect(clean.getSummary().allMaxMs).toBeNull();
    expect(clean.getSummary().excludedMaxMs).toBeNull();
  });

  it("a non-positive delta is excluded with a reason instead of producing an infinite fps", () => {
    const raf = new FakeRaf();
    const recorder = createFpsRecorder({ ...raf.deps, visibility: null });
    recorder.start();
    raf.advance(0);
    raf.advance(50);
    raf.advance(50); // same timestamp twice -> delta 0
    const samples = recorder.getSamples();
    expect(samples[1]).toMatchObject({
      excluded: true,
      excludeReason: FPS_NON_POSITIVE_EXCLUDE_REASON,
      instantFps: 0,
    });
  });

  // ---- AC4: summary math (avg/max/p95 nearest-rank) is reported as measured ----

  it("summary reports avg/min/max/p95 over kept samples with the nearest-rank method", () => {
    const raf = new FakeRaf();
    const recorder = createFpsRecorder({ ...raf.deps, visibility: null });
    recorder.start();
    // deltas: 10, 10, 15, 15, 10 -> sorted [10,10,10,15,15]
    // p95 index = ceil(0.95*5)-1 = 4 -> 15; avg = 60/5 = 12
    for (const ts of [0, 10, 20, 35, 50, 60]) raf.advance(ts);
    const summary = recorder.getSummary();
    expect(summary.kept).toEqual({
      samples: 5,
      avgMs: 12,
      minMs: 10,
      maxMs: 15,
      p95Ms: 15,
    });
    expect(summary.p95Method).toBe("nearest-rank");
    expect(summary.avgThresholdMs).toBe(FPS_AVG_THRESHOLD_MS);
    expect(summary.avgWithinThreshold).toBe(true);
  });

  it("avg above the 50ms user criterion is reported as FAIL, never rounded away", () => {
    const raf = new FakeRaf();
    const recorder = createFpsRecorder({ ...raf.deps, visibility: null });
    recorder.start();
    for (const ts of [0, 80, 160]) raf.advance(ts); // two 80ms frames
    expect(recorder.getSummary().kept).toEqual({ samples: 2, avgMs: 80, minMs: 80, maxMs: 80, p95Ms: 80 });
    expect(recorder.getSummary().avgWithinThreshold).toBe(false);
  });

  it("titleSummary carries the verdict and the all-sample max in the UIA-readable one-line form", () => {
    const raf = new FakeRaf();
    const recorder = createFpsRecorder({ ...raf.deps, visibility: null });
    recorder.start();
    raf.advance(0);
    raf.advance(100);
    raf.advance(5200); // visible-page stall: kept, so avg/max must show it
    recorder.stop();
    expect(recorder.titleSummary()).toBe(
      "M2FPS state=STOPPED samples=2 avg=2600 p95=5100 max=5100 allmax=5100 excluded=0 avg<=50ms:FAIL",
    );
  });

  // ---- AC2: structured exports ----

  it("toCsv emits one row per sample, kept and excluded alike", () => {
    const raf = new FakeRaf();
    const recorder = createFpsRecorder({ ...raf.deps, visibility: null });
    recorder.start();
    raf.advance(0);
    raf.advance(16);
    raf.advance(32);
    const csv = recorder.toCsv();
    expect(csv.split("\n")).toEqual([
      "seq,frame_ts_ms,frame_time_ms,instant_fps,excluded,exclude_reason",
      "1,16,16,62.5,0,",
      "2,32,16,62.5,0,",
    ]);
  });

  it("toJson embeds meta, summary and every sample", () => {
    const raf = new FakeRaf();
    const recorder = createFpsRecorder({ ...raf.deps, visibility: null });
    recorder.start();
    raf.advance(0);
    raf.advance(16);
    const parsed = JSON.parse(recorder.toJson());
    expect(parsed.meta).toMatchObject({
      task: "P20-AC4-FPS-1",
      avg_threshold_ms: 50,
      p95_method: "nearest-rank",
      gap_exclude_ms: 1000,
    });
    expect(parsed.meta.gap_exclude_rule).toContain("hidden");
    expect(parsed.summary.totalSamples).toBe(1);
    expect(parsed.summary.allMaxMs).toBe(16);
    expect(parsed.samples).toHaveLength(1);
    expect(parsed.samples[0].frameTimeMs).toBe(16);
  });

  it("reset stops sampling, drops the array and restarts seq/baseline from scratch", () => {
    const raf = new FakeRaf();
    const recorder = createFpsRecorder({ ...raf.deps, visibility: null });
    recorder.start();
    raf.advance(0);
    raf.advance(10);
    recorder.reset();
    expect(recorder.getSamples()).toEqual([]);
    expect(recorder.getSummary().baselineFrames).toBe(0);
    expect(recorder.isRunning()).toBe(false);
    recorder.start();
    raf.advance(500); // fresh baseline
    raf.advance(510);
    const samples = recorder.getSamples();
    expect(samples).toHaveLength(1);
    expect(samples[0].seq).toBe(1);
    expect(samples[0].frameTimeMs).toBe(10);
  });

  // ---- singleton wiring (used by main.tsx only when a switch is on) ----

  it("startFpsRecorder is a singleton; stopFpsRecorder keeps data exportable", () => {
    const first = startFpsRecorder(rafSpy.deps);
    const second = startFpsRecorder(rafSpy.deps);
    expect(second).toBe(first);
    expect(getActiveFpsRecorder()).toBe(first);
    rafSpy.advance(0);
    rafSpy.advance(10);
    const stopped = stopFpsRecorder();
    expect(stopped).toBe(first);
    expect(first.isRunning()).toBe(false);
    // data survives stop for export
    expect(first.getSamples()).toHaveLength(1);
    first.reset();
  });
});
