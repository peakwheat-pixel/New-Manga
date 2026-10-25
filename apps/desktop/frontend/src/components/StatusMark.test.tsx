// @vitest-environment jsdom
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, describe, expect, it } from "vitest";
import { StatusMark, type StatusState } from "./StatusMark";

const style = readFileSync(resolve(process.cwd(), "src/components/StatusMark.css"), "utf8");

const EXPECTED: Array<{ state: StatusState; symbol: string; label: string; className: string }> = [
  { state: "queued", symbol: "·", label: "排队", className: "queued" },
  { state: "running", symbol: "◐", label: "进行中", className: "running" },
  { state: "done", symbol: "●", label: "完成", className: "done" },
  { state: "failed", symbol: "✗", label: "失败", className: "failed" },
  { state: "blocked", symbol: "▲", label: "阻塞", className: "blocked" },
  { state: "stale", symbol: "▨", label: "过期", className: "stale" },
  { state: "skipped", symbol: "–", label: "跳过", className: "skipped" },
  { state: "notStarted", symbol: "○", label: "未开始", className: "not-started" },
];

let root: Root | undefined;
let container: HTMLDivElement | undefined;

function mount(element: React.ReactElement) {
  container = document.createElement("div");
  document.body.appendChild(container);
  root = createRoot(container);
  act(() => {
    root?.render(element);
  });
  return container;
}

afterEach(() => {
  act(() => root?.unmount());
  container?.remove();
  root = undefined;
  container = undefined;
});

describe("StatusMark", () => {
  it.each(EXPECTED)("renders symbol, label and class for $state", ({ state, symbol, label, className }) => {
    const host = mount(<StatusMark state={state} />);
    const mark = host.querySelector<HTMLElement>(".nm-status");
    expect(mark).not.toBeNull();
    expect(mark?.dataset.state).toBe(state);
    expect(mark?.classList.contains("nm-status")).toBe(true);
    expect(mark?.classList.contains(`nm-status--${className}`)).toBe(true);
    expect(host.querySelector(".nm-status__mark")?.textContent).toBe(symbol);
    expect(host.querySelector(".nm-status__label")?.textContent).toBe(label);
    expect(host.textContent).toBe(`${symbol}${label}`);
  });

  it.each(EXPECTED)("keeps $state non-emoji", ({ state }) => {
    const host = mount(<StatusMark state={state} />);
    expect(host.textContent ?? "").not.toMatch(/[\u{1F300}-\u{1FAFF}]/u);
  });

  it("can hide the visible label while keeping the accessible name", () => {
    const host = mount(<StatusMark state="blocked" showLabel={false} />);
    expect(host.querySelector(".nm-status__label")).toBeNull();
    expect(host.querySelector(".nm-status__mark")?.textContent).toBe("▲");
    expect(host.querySelector(".nm-sr-only")?.textContent).toBe("阻塞");
    expect(host.textContent).toContain("阻塞");
  });

  it("uses the 24x24 marker class hook on every state", () => {
    for (const { state } of EXPECTED) {
      const host = mount(<StatusMark state={state} />);
      expect(host.querySelector(".nm-status__mark")).not.toBeNull();
      act(() => root?.unmount());
      container?.remove();
      root = undefined;
      container = undefined;
    }
  });

  it("pins the marker block to 24x24 with the control radius", () => {
    const marker = style.slice(style.indexOf(".nm-status__mark"), style.indexOf(".nm-status__label"));
    expect(marker).toContain("width: 24px");
    expect(marker).toContain("height: 24px");
    expect(marker).toContain("border-radius: var(--nm-radius-control)");
  });

  it("wires every state to its matching muted background and status colour", () => {
    const states = ["queued", "running", "done", "failed", "blocked", "stale", "skipped"] as const;
    for (const state of states) {
      const start = style.indexOf(`.nm-status--${state} .nm-status__mark`);
      expect(start, `${state} rule`).toBeGreaterThan(-1);
      const rule = style.slice(start, style.indexOf("}", start));
      expect(rule, state).toContain(`background: var(--nm-status-muted-${state})`);
      expect(rule, state).toContain(`color: var(--nm-status-${state})`);
    }
  });
});
