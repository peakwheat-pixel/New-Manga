// P20-AC4-FPS-1: opt-in requestAnimationFrame frame-time recorder.
//
// Zero-cost default: importing this module registers NO rAF callback and
// allocates NO sample array. The singleton recorder (which owns the sample
// array) only comes into existence when startFpsRecorder() is called, and the
// only rAF registration points are start() and the frame callback itself —
// there is no permanently-registered loop with an "if (enabled) return"
// guard. The default production path never calls startFpsRecorder() unless
// one of the three explicit switches below is on:
//   1. build flag    VITE_M2_FPS_SAMPLING=1 (measurement build only)
//   2. query param   ?m2_fps=1
//   3. localStorage  m2rc1_fps_sampling=1
//
// No metric manipulation (user ruling 2026-10-18): every observed frame
// interval stays in the CSV export. A >=1s rAF gap is excluded from the
// kept-sample statistics ONLY when sampling confirms the page was hidden
// during that interval (visibilitychange tracking); a >=1s gap observed
// while the page stayed visible (foreground main-thread stall) is KEPT in
// the statistics. Excluded rows remain in the CSV with excluded=1 plus a
// reason, and the summary reports the all-sample max and the excluded-sample
// max alongside the kept stats so no observed stall can hide behind an
// exclusion. avg <= 50ms is the user-ruled pass criterion for the frame-rate
// part of AC4; p95 and max are ALWAYS reported as measured, even when above
// the threshold.

export const FPS_QUERY_PARAM = "m2_fps";
export const FPS_LOCALSTORAGE_KEY = "m2rc1_fps_sampling";
export const FPS_BUILD_ENV_FLAG_KEY = "VITE_M2_FPS_SAMPLING";
/** User-ruled AC4 frame-time criterion (2026-10-18): avg <= 50ms. */
export const FPS_AVG_THRESHOLD_MS = 50;
/** Frame intervals >= this are only excluded when they overlap a tracked
 * hidden interval (page not visible); they are kept in the CSV either way. */
export const FPS_GAP_EXCLUDE_MS = 1000;
export const FPS_GAP_EXCLUDE_REASON = "raf_gap_ge_1000ms_while_hidden";
export const FPS_NON_POSITIVE_EXCLUDE_REASON = "non_positive_delta";
export const FPS_P95_METHOD = "nearest-rank" as const;

export interface FpsFrameSample {
  /** 1-based index over all samples (kept and excluded alike). */
  seq: number;
  /** rAF timestamp of the frame that closed this interval (ms). */
  frameTsMs: number;
  /** Interval since the previous rAF callback (ms). */
  frameTimeMs: number;
  /** 1000 / frameTimeMs. */
  instantFps: number;
  excluded: boolean;
  excludeReason: string | null;
}

export interface FpsStats {
  samples: number;
  avgMs: number;
  minMs: number;
  maxMs: number;
  p95Ms: number;
}

export interface FpsSummary {
  running: boolean;
  /** Rows in the CSV export = kept + excluded. */
  totalSamples: number;
  kept: FpsStats | null;
  excludedCount: number;
  excludedReasons: Record<string, number>;
  /** Max frame interval over ALL samples, excluded ones included. Reported
   * so a long stall can never be hidden behind an exclusion. */
  allMaxMs: number | null;
  /** Max frame interval among the EXCLUDED samples only (null when none). */
  excludedMaxMs: number | null;
  /** True when a visibility source was attached while sampling; when false,
   * no >=1s gap is ever excluded (conservative keep). */
  visibilityTracked: boolean;
  /** rAF callbacks consumed to establish the first timestamp baseline. */
  baselineFrames: number;
  firstFrameTsMs: number | null;
  lastFrameTsMs: number | null;
  p95Method: typeof FPS_P95_METHOD;
  avgThresholdMs: number;
  avgWithinThreshold: boolean | null;
}

export interface FpsRecorder {
  start(): void;
  stop(): void;
  reset(): void;
  isRunning(): boolean;
  getSamples(): readonly FpsFrameSample[];
  getSummary(): FpsSummary;
  toCsv(): string;
  toJson(): string;
  /** Compact one-line summary for the window title (UIA-readable channel). */
  titleSummary(): string;
}

export interface FpsVisibilitySource {
  /** Register a visibility-change listener; returns its unregister function. */
  addListener(onChange: () => void): () => void;
  isHidden(): boolean;
}

export interface FpsRecorderDeps {
  requestAnimationFrame: (callback: (timestampMs: number) => void) => number;
  cancelAnimationFrame: (handle: number) => void;
  /** Same time domain as the rAF timestamps (performance.now). */
  now?: () => number;
  /** Visibility tracking source; omitted/null = no tracking (gaps are kept). */
  visibility?: FpsVisibilitySource | null;
}

const NO_SAMPLES: readonly FpsFrameSample[] = [];

function roundMs(value: number): number {
  return Math.round(value * 1000) / 1000;
}

function isExplicitOn(value: string | null | undefined): boolean {
  if (value === "1") return true;
  return typeof value === "string" && value.trim().toLowerCase() === "true";
}

/** Real-browser default: the document visibilitychange events. Absent (e.g.
 * a bare node test environment) the recorder simply tracks nothing and keeps
 * every >=1s gap in the statistics — the conservative direction. */
function defaultVisibilitySource(): FpsVisibilitySource | null {
  try {
    const doc = (globalThis as { document?: Document }).document;
    if (!doc || typeof doc.addEventListener !== "function") return null;
    return {
      addListener(onChange) {
        doc.addEventListener("visibilitychange", onChange);
        return () => doc.removeEventListener("visibilitychange", onChange);
      },
      isHidden: () => doc.visibilityState === "hidden",
    };
  } catch {
    return null;
  }
}

export interface FpsSwitchSources {
  queryString: string;
  localStorageValue: string | null;
  buildFlagValue: string | undefined;
}

// Keep `import.meta.env` a literal access: Vite's build-time define replaces
// the whole env object, so a measurement build with VITE_M2_FPS_SAMPLING=1
// bakes the flag into the bundle while default builds resolve undefined.
const viteEnv = (import.meta as unknown as { env?: Record<string, string | undefined> }).env;

function defaultQueryString(): string {
  try {
    const w = (globalThis as { window?: { location?: { search?: string } } }).window;
    return w?.location?.search ?? "";
  } catch {
    return "";
  }
}

function defaultLocalStorageValue(): string | null {
  try {
    const w = (globalThis as { window?: { localStorage?: { getItem(k: string): string | null } } }).window;
    return w?.localStorage?.getItem(FPS_LOCALSTORAGE_KEY) ?? null;
  } catch {
    return null;
  }
}

/** True only when one of the three explicit switches asks for sampling. */
export function readFpsRecorderRequest(overrides?: Partial<FpsSwitchSources>): boolean {
  const sources: FpsSwitchSources = {
    queryString: defaultQueryString(),
    localStorageValue: defaultLocalStorageValue(),
    buildFlagValue: viteEnv?.[FPS_BUILD_ENV_FLAG_KEY],
    ...overrides,
  };
  const queryValue = new URLSearchParams(sources.queryString).get(FPS_QUERY_PARAM);
  return (
    isExplicitOn(queryValue) ||
    isExplicitOn(sources.localStorageValue) ||
    isExplicitOn(sources.buildFlagValue)
  );
}

function computeKeptStats(keptFrameTimes: number[]): FpsStats | null {
  if (keptFrameTimes.length === 0) return null;
  const sorted = [...keptFrameTimes].sort((a, b) => a - b);
  const n = sorted.length;
  // nearest-rank: p95 = sorted[ceil(0.95*n)-1]
  const p95Index = Math.max(0, Math.ceil(0.95 * n) - 1);
  const sum = sorted.reduce((acc, value) => acc + value, 0);
  return {
    samples: n,
    avgMs: roundMs(sum / n),
    minMs: roundMs(sorted[0]),
    maxMs: roundMs(sorted[n - 1]),
    p95Ms: roundMs(sorted[p95Index]),
  };
}

export function createFpsRecorder(deps?: Partial<FpsRecorderDeps>): FpsRecorder {
  // Allocated ONLY inside start(); null before the first start and after
  // reset(), which is the test-auditable "no array unless sampling" state.
  let samples: FpsFrameSample[] | null = null;
  let running = false;
  let lastTs: number | null = null;
  let rafHandle: number | null = null;
  let seq = 0;
  let baselineFrames = 0;
  // Hidden-interval bookkeeping lives in the same performance.now domain as
  // the rAF timestamps (deps.now defaults to performance.now).
  let hiddenIntervals: Array<[number, number]> | null = null;
  let openHiddenStart: number | null = null;
  let removeVisibilityListener: (() => void) | null = null;
  let visibilityTracked = false;

  const raf: FpsRecorderDeps["requestAnimationFrame"] =
    deps?.requestAnimationFrame ??
    ((callback) => globalThis.requestAnimationFrame(callback));
  const cancelRaf: FpsRecorderDeps["cancelAnimationFrame"] =
    deps?.cancelAnimationFrame ?? ((handle) => globalThis.cancelAnimationFrame(handle));
  const now: () => number = deps?.now ?? (() => performance.now());
  const visibility: FpsVisibilitySource | null =
    deps?.visibility === undefined ? defaultVisibilitySource() : deps.visibility;

  function closeOpenHiddenInterval(): void {
    if (openHiddenStart !== null && hiddenIntervals !== null) {
      hiddenIntervals.push([openHiddenStart, now()]);
      openHiddenStart = null;
    }
  }

  function onVisibilityChange(): void {
    if (visibility === null) return;
    if (visibility.isHidden()) {
      if (openHiddenStart === null) openHiddenStart = now();
    } else {
      closeOpenHiddenInterval();
    }
  }

  /** Overlap test against closed hidden intervals [h0, h1]. The frame covers
   * (prevTs, frameTs]; boundary contact counts (conservative exclusion). */
  function gapOverlapsHidden(prevTs: number, frameTs: number): boolean {
    if (hiddenIntervals === null) return false;
    closeOpenHiddenInterval();
    return hiddenIntervals.some(([h0, h1]) => h1 >= prevTs && h0 <= frameTs);
  }

  function onFrame(frameNow: number): void {
    if (!running) return;
    if (lastTs === null) {
      // First callback only establishes the baseline timestamp; it carries
      // no interval and produces no sample.
      lastTs = frameNow;
      baselineFrames += 1;
      rafHandle = raf(onFrame);
      return;
    }
    const prevTs = lastTs;
    const delta = frameNow - prevTs;
    lastTs = frameNow;
    // >=1s gaps are excluded ONLY when visibility tracking confirms the page
    // was hidden inside the interval; a visible-page stall stays in the kept
    // statistics (FPS-R1-05, no spike masking).
    const excluded =
      delta <= 0 ||
      (delta >= FPS_GAP_EXCLUDE_MS && gapOverlapsHidden(prevTs, frameNow));
    const excludeReason = delta <= 0
      ? FPS_NON_POSITIVE_EXCLUDE_REASON
      : excluded
        ? FPS_GAP_EXCLUDE_REASON
        : null;
    seq += 1;
    // samples is non-null whenever running (start() allocated it).
    samples!.push({
      seq,
      frameTsMs: frameNow,
      frameTimeMs: roundMs(delta),
      instantFps: delta > 0 ? roundMs(1000 / delta) : 0,
      excluded,
      excludeReason,
    });
    rafHandle = raf(onFrame);
  }

  function getSummary(): FpsSummary {
    const all = samples ?? [];
    const keptTimes = all.filter((s) => !s.excluded).map((s) => s.frameTimeMs);
    const excludedTimes = all.filter((s) => s.excluded).map((s) => s.frameTimeMs);
    const kept = computeKeptStats(keptTimes);
    const excludedReasons: Record<string, number> = {};
    for (const s of all) {
      if (s.excluded && s.excludeReason) {
        excludedReasons[s.excludeReason] = (excludedReasons[s.excludeReason] ?? 0) + 1;
      }
    }
    return {
      running,
      totalSamples: all.length,
      kept,
      excludedCount: excludedTimes.length,
      excludedReasons,
      allMaxMs: all.length > 0 ? Math.max(...all.map((s) => s.frameTimeMs)) : null,
      excludedMaxMs: excludedTimes.length > 0 ? Math.max(...excludedTimes) : null,
      visibilityTracked,
      baselineFrames,
      firstFrameTsMs: all.length > 0 ? all[0].frameTsMs : null,
      lastFrameTsMs: all.length > 0 ? all[all.length - 1].frameTsMs : null,
      p95Method: FPS_P95_METHOD,
      avgThresholdMs: FPS_AVG_THRESHOLD_MS,
      avgWithinThreshold: kept ? kept.avgMs <= FPS_AVG_THRESHOLD_MS : null,
    };
  }

  return {
    start() {
      if (running) return;
      running = true;
      if (!samples) samples = [];
      if (!hiddenIntervals) hiddenIntervals = [];
      // The visibility listener is registered here (and only here), keeping
      // the closed state free of any listener registration.
      if (visibility) {
        visibilityTracked = true;
        removeVisibilityListener = visibility.addListener(onVisibilityChange);
        if (visibility.isHidden()) openHiddenStart = now();
      }
      // The ONLY initial rAF registration point.
      rafHandle = raf(onFrame);
    },
    stop() {
      if (!running) return;
      running = false;
      closeOpenHiddenInterval();
      if (removeVisibilityListener) {
        removeVisibilityListener();
        removeVisibilityListener = null;
      }
      if (rafHandle !== null) {
        cancelRaf(rafHandle);
        rafHandle = null;
      }
    },
    reset() {
      this.stop();
      samples = null;
      lastTs = null;
      seq = 0;
      baselineFrames = 0;
      hiddenIntervals = null;
      openHiddenStart = null;
      visibilityTracked = false;
    },
    isRunning() {
      return running;
    },
    getSamples() {
      return samples ?? NO_SAMPLES;
    },
    getSummary,
    toCsv() {
      const header = "seq,frame_ts_ms,frame_time_ms,instant_fps,excluded,exclude_reason";
      const rows = (samples ?? []).map(
        (s) =>
          `${s.seq},${s.frameTsMs},${s.frameTimeMs},${s.instantFps},${s.excluded ? 1 : 0},${s.excludeReason ?? ""}`,
      );
      return [header, ...rows].join("\n");
    },
    toJson() {
      return JSON.stringify(
        {
          meta: {
            task: "P20-AC4-FPS-1",
            avg_threshold_ms: FPS_AVG_THRESHOLD_MS,
            p95_method: FPS_P95_METHOD,
            gap_exclude_ms: FPS_GAP_EXCLUDE_MS,
            gap_exclude_rule:
              "delta >= gap_exclude_ms is excluded only when it overlaps a tracked page-hidden interval; visible-page stalls are kept in the kept-sample statistics",
            numeric_format: "ms values rounded to 3 decimals",
          },
          summary: getSummary(),
          samples: samples ?? [],
        },
        null,
        2,
      );
    },
    titleSummary() {
      const s = getSummary();
      const keptPart = s.kept
        ? ` avg=${s.kept.avgMs} p95=${s.kept.p95Ms} max=${s.kept.maxMs}`
        : " avg=NA p95=NA max=NA";
      const allMaxPart = s.allMaxMs === null ? "" : ` allmax=${s.allMaxMs}`;
      const verdict = s.avgWithinThreshold === null ? "" : ` avg<=${FPS_AVG_THRESHOLD_MS}ms:${s.avgWithinThreshold ? "PASS" : "FAIL"}`;
      return `M2FPS state=${s.running ? "RUNNING" : "STOPPED"} samples=${s.totalSamples}${keptPart}${allMaxPart} excluded=${s.excludedCount}${verdict}`;
    },
  };
}

// Module-level singleton. null = no recorder object, no sample array, no
// rAF registration — the default state of a fresh page load.
let activeRecorder: FpsRecorder | null = null;

export function getActiveFpsRecorder(): FpsRecorder | null {
  return activeRecorder;
}

/** Idempotent: creates the singleton on first call and starts sampling.
 * Only reachable through an explicit switch (see readFpsRecorderRequest). */
export function startFpsRecorder(deps?: Partial<FpsRecorderDeps>): FpsRecorder {
  if (!activeRecorder) {
    activeRecorder = createFpsRecorder(deps);
  }
  activeRecorder.start();
  return activeRecorder;
}

/** Stops sampling but keeps the recorder (and its data) exportable. */
export function stopFpsRecorder(): FpsRecorder | null {
  if (!activeRecorder) return null;
  activeRecorder.stop();
  return activeRecorder;
}
