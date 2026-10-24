import { useEffect, useState, type CSSProperties } from "react";
import {
  FPS_AVG_THRESHOLD_MS,
  type FpsRecorder,
  type FpsSummary,
} from "./fpsRecorder";

// P20-AC4-FPS-1: floating control panel for the opt-in FPS recorder.
// Rendered ONLY when an explicit sampling switch is on (see main.tsx);
// a default page load never mounts it, so the default DOM is unchanged.
//
// Measurement-fidelity note: this panel deliberately does NOT poll the
// recorder on a timer — periodic re-renders during capture would perturb the
// very frame times being measured. Visible counters refresh on demand
// (Refresh) and on state transitions (Stop / Reset & Start).
//
// Export writes ONLY through the browser's explicit Save As picker
// (window.showSaveFilePicker, FPS-R1-04): the user picks the destination,
// cancelling writes nothing, and there is no default-download-location
// fallback. This code never learns an absolute path (the handle is opaque),
// preserving the no-direct-path-write frontend boundary.

function timestampFileStamp(): string {
  const now = new Date();
  const pad = (value: number) => String(value).padStart(2, "0");
  return (
    `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}` +
    `-${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`
  );
}

interface FileWritableLike {
  write(data: string): Promise<void>;
  close(): Promise<void>;
}

interface FileSystemFileHandleLike {
  createWritable(): Promise<FileWritableLike>;
}

interface SavePickerWindow {
  showSaveFilePicker?: (options: {
    suggestedName: string;
    types: ReadonlyArray<{
      description: string;
      accept: Record<string, ReadonlyArray<string>>;
    }>;
  }) => Promise<FileSystemFileHandleLike>;
}

export type SaveFileOutcome = "saved" | "cancelled" | "unsupported" | "failed";

/** Explicit Save As via the File System Access API (Chromium/WebView2).
 * - "cancelled": the user dismissed the picker — nothing is written anywhere.
 * - "unsupported": no picker in this environment — nothing is written; the
 *   caller directs the user to the Show/Copy channels instead. There is
 *   deliberately NO silent blob/anchor.download fallback, because that path
 *   writes to the WebView2 default download folder without an explicit
 *   destination choice (FPS-R1-04). */
async function saveTextViaPicker(
  filename: string,
  text: string,
  mime: string,
  extensions: ReadonlyArray<string>,
): Promise<SaveFileOutcome> {
  const pickerWindow = window as unknown as SavePickerWindow;
  if (typeof pickerWindow.showSaveFilePicker !== "function") return "unsupported";
  let handle: FileSystemFileHandleLike;
  try {
    handle = await pickerWindow.showSaveFilePicker({
      suggestedName: filename,
      types: [{ description: "FPS sampler export", accept: { [mime]: [...extensions] } }],
    });
  } catch (error) {
    const name = (error as DOMException | null)?.name;
    if (name === "AbortError") return "cancelled";
    return "failed";
  }
  try {
    const writable = await handle.createWritable();
    await writable.write(text);
    await writable.close();
    return "saved";
  } catch {
    return "failed";
  }
}

function exportNote(outcome: SaveFileOutcome, kind: "csv" | "json"): string {
  const upper = kind.toUpperCase();
  switch (outcome) {
    case "saved":
      return `${kind} saved to the chosen location (explicit Save As; nothing written elsewhere)`;
    case "cancelled":
      return `${kind} export cancelled — nothing written (no default-location fallback)`;
    case "unsupported":
      return `explicit save dialog unavailable in this environment — use Show ${upper} + copy; nothing written`;
    case "failed":
      return `${kind} save failed — use Show ${upper} + copy`;
  }
}

async function copyTextToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
}

const panelButtonStyle: CSSProperties = {
  fontSize: 11,
  padding: "2px 8px",
  margin: 1,
  background: "#1c2430",
  color: "#d8e0e8",
  border: "1px solid #2a3038",
  borderRadius: 4,
  cursor: "pointer",
};

export interface FpsRecorderPanelProps {
  recorder: FpsRecorder;
}

export function FpsRecorderPanel({ recorder }: FpsRecorderPanelProps) {
  const [summary, setSummary] = useState<FpsSummary>(() => recorder.getSummary());
  const [dataOutput, setDataOutput] = useState("");
  const [note, setNote] = useState("");

  useEffect(() => {
    // Signal "running" through the window title so an external UIA driver can
    // observe recorder state without touching the DOM (P20 App.tsx precedent).
    document.title = recorder.titleSummary();
  }, [recorder, summary]);

  const refresh = () => setSummary(recorder.getSummary());

  const stop = () => {
    recorder.stop();
    setSummary(recorder.getSummary());
    setNote("stopped");
  };

  const resetAndStart = () => {
    recorder.reset();
    recorder.start();
    setDataOutput("");
    setSummary(recorder.getSummary());
    setNote("reset & started");
  };

  const showCsv = () => {
    setDataOutput(recorder.toCsv());
    setNote("csv shown below");
  };

  const showJson = () => {
    setDataOutput(recorder.toJson());
    setNote("json shown below");
  };

  const exportCsv = async () => {
    const outcome = await saveTextViaPicker(
      `m2-fps-${timestampFileStamp()}.csv`,
      recorder.toCsv(),
      "text/csv",
      [".csv"],
    );
    setNote(exportNote(outcome, "csv"));
  };

  const exportJson = async () => {
    const outcome = await saveTextViaPicker(
      `m2-fps-${timestampFileStamp()}.json`,
      recorder.toJson(),
      "application/json",
      [".json"],
    );
    setNote(exportNote(outcome, "json"));
  };

  const copyCsv = async () => {
    const ok = await copyTextToClipboard(recorder.toCsv());
    setNote(ok ? "csv copied to clipboard" : "clipboard unavailable; use Show CSV");
  };

  const kept = summary.kept;

  return (
    <div
      data-testid="fps-recorder-panel"
      role="toolbar"
      aria-label="FPS sampler panel"
      style={{
        position: "fixed",
        top: 8,
        right: 8,
        zIndex: 9999,
        width: 320,
        padding: 8,
        boxSizing: "border-box",
        background: "#101418",
        color: "#d8e0e8",
        border: "1px solid #2a3038",
        borderRadius: 6,
        fontFamily: "Consolas, monospace",
        fontSize: 11,
        lineHeight: 1.5,
      }}
    >
      <div style={{ fontWeight: 700 }}>FPS sampler (P20-AC4-FPS-1)</div>
      <div data-testid="fps-panel-state">
        state: {summary.running ? "RUNNING" : "STOPPED"} · samples: {summary.totalSamples} (excluded {summary.excludedCount})
      </div>
      <div data-testid="fps-panel-stats">
        {kept
          ? `avg: ${kept.avgMs} ms | p95: ${kept.p95Ms} ms | max: ${kept.maxMs} ms | min: ${kept.minMs} ms`
          : "avg: n/a | p95: n/a | max: n/a (no kept samples yet)"}
      </div>
      <div data-testid="fps-panel-verdict">
        avg&lt;={FPS_AVG_THRESHOLD_MS}ms:{" "}
        {summary.avgWithinThreshold === null ? "n/a" : summary.avgWithinThreshold ? "PASS" : "FAIL"}
        {summary.excludedCount > 0
          ? ` · excluded reasons: ${JSON.stringify(summary.excludedReasons)}`
          : ""}
        {summary.allMaxMs !== null && summary.allMaxMs !== kept?.maxMs
          ? ` · all-sample max: ${summary.allMaxMs} ms (a stall larger than the kept max was observed)`
          : ""}
      </div>
      <div>
        <button type="button" style={panelButtonStyle} onClick={refresh}>FPS: Refresh</button>
        <button type="button" style={panelButtonStyle} onClick={stop}>FPS: Stop</button>
        <button type="button" style={panelButtonStyle} onClick={resetAndStart}>FPS: Reset &amp; Start</button>
      </div>
      <div>
        <button type="button" style={panelButtonStyle} onClick={showCsv}>FPS: Show CSV</button>
        <button type="button" style={panelButtonStyle} onClick={showJson}>FPS: Show JSON</button>
        <button type="button" style={panelButtonStyle} onClick={() => void exportCsv()}>FPS: Export CSV</button>
        <button type="button" style={panelButtonStyle} onClick={() => void exportJson()}>FPS: Export JSON</button>
        <button type="button" style={panelButtonStyle} onClick={() => void copyCsv()}>FPS: Copy CSV</button>
      </div>
      <div style={{ minHeight: 14, color: "#8aa0b4" }}>{note}</div>
      <textarea
        data-testid="fps-data-output"
        aria-label="FPS sampler data output"
        readOnly
        value={dataOutput}
        style={{
          width: "100%",
          height: 140,
          boxSizing: "border-box",
          background: "#0b0e12",
          color: "#c8d2dc",
          border: "1px solid #232a33",
          borderRadius: 4,
          fontFamily: "Consolas, monospace",
          fontSize: 10,
        }}
      />
    </div>
  );
}
