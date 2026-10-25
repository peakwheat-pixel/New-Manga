import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const css = readFileSync(resolve(process.cwd(), "src/design/tokens.css"), "utf8");

function block(selector: string): string {
  const escaped = selector.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const match = css.match(new RegExp(`${escaped}\\s*\\{([\\s\\S]*?)\\n\\}`, "m"));
  if (!match) throw new Error(`missing CSS block: ${selector}`);
  return match[1];
}

function declarations(source: string): Map<string, string> {
  const result = new Map<string, string>();
  const re = /--([a-z0-9-]+)\s*:\s*([^;]+);/gi;
  let match: RegExpExecArray | null;
  while ((match = re.exec(source)) !== null) {
    result.set(match[1], match[2].trim());
  }
  return result;
}

const DARK: Record<string, string> = {
  "nm-bg-canvas": "#1B1B1B",
  "nm-bg-mica": "#202020",
  "nm-bg-solid": "#202020",
  "nm-bg-layer": "#272727",
  "nm-bg-card": "#2B2B2B",
  "nm-bg-alt": "#323232",
  "nm-acrylic-tint": "rgba(43,43,43,0.55)",
  "nm-acrylic-tint-strong": "rgba(43,43,43,0.78)",
  "nm-acrylic-stroke": "rgba(255,255,255,0.10)",
  "nm-acrylic-highlight": "rgba(255,255,255,0.06)",
  "nm-line-divider": "rgba(255,255,255,0.07)",
  "nm-line-control": "rgba(255,255,255,0.09)",
  "nm-line-strong": "rgba(255,255,255,0.14)",
  "nm-text-primary": "#FFFFFF",
  "nm-text-secondary": "rgba(255,255,255,0.79)",
  "nm-text-tertiary": "rgba(255,255,255,0.54)",
  "nm-text-disabled": "rgba(255,255,255,0.36)",
  "nm-accent-base": "#60CDFF",
  "nm-accent-hover": "#9EF1FF",
  "nm-accent-active": "#2BB7F6",
  "nm-accent-muted": "rgba(96,205,255,0.16)",
  "nm-accent-on": "#000000",
  "nm-accent-ring": "rgba(96,205,255,0.45)",
  "nm-status-queued": "#5C6169",
  "nm-status-running": "#5B93B8",
  "nm-status-done": "#6FA97D",
  "nm-status-failed": "#C9634F",
  "nm-status-blocked": "#C8903F",
  "nm-status-stale": "#9A8AB0",
  "nm-status-skipped": "#4A4F55",
  "nm-status-muted-queued": "rgba(92,97,105,0.18)",
  "nm-status-muted-running": "rgba(91,147,184,0.16)",
  "nm-status-muted-done": "rgba(111,169,125,0.14)",
  "nm-status-muted-failed": "rgba(201,99,79,0.16)",
  "nm-status-muted-blocked": "rgba(200,144,63,0.16)",
  "nm-status-muted-stale": "rgba(154,138,176,0.16)",
  "nm-status-muted-skipped": "rgba(74,79,85,0.14)",
};

const LIGHT: Record<string, string> = {
  "nm-bg-canvas": "#EEEEEE",
  "nm-bg-mica": "#F3F3F3",
  "nm-bg-solid": "#F3F3F3",
  "nm-bg-layer": "#FAFAFA",
  "nm-bg-card": "#FFFFFF",
  "nm-bg-alt": "#F2F2F2",
  "nm-acrylic-tint": "rgba(249,249,249,0.72)",
  "nm-acrylic-tint-strong": "rgba(249,249,249,0.88)",
  "nm-acrylic-stroke": "rgba(0,0,0,0.08)",
  "nm-acrylic-highlight": "rgba(255,255,255,0.70)",
  "nm-line-divider": "rgba(0,0,0,0.06)",
  "nm-line-control": "rgba(0,0,0,0.09)",
  "nm-line-strong": "rgba(0,0,0,0.14)",
  "nm-text-primary": "#1A1A1A",
  "nm-text-secondary": "rgba(0,0,0,0.79)",
  "nm-text-tertiary": "rgba(0,0,0,0.54)",
  "nm-text-disabled": "rgba(0,0,0,0.36)",
  "nm-accent-base": "#005FB8",
  "nm-accent-hover": "#0078D4",
  "nm-accent-active": "#004578",
  "nm-accent-muted": "rgba(0,95,184,0.10)",
  "nm-accent-on": "#FFFFFF",
  "nm-accent-ring": "rgba(0,95,184,0.40)",
  "nm-status-queued": "#6E7378",
  "nm-status-running": "#3D6E8E",
  "nm-status-done": "#3F6B4F",
  "nm-status-failed": "#A8462F",
  "nm-status-blocked": "#8A6A1F",
  "nm-status-stale": "#6B5E82",
  "nm-status-skipped": "#8A8F94",
  "nm-status-muted-queued": "rgba(110,115,120,0.12)",
  "nm-status-muted-running": "rgba(61,110,142,0.12)",
  "nm-status-muted-done": "rgba(63,107,79,0.12)",
  "nm-status-muted-failed": "rgba(168,70,47,0.12)",
  "nm-status-muted-blocked": "rgba(138,106,31,0.12)",
  "nm-status-muted-stale": "rgba(107,94,130,0.12)",
  "nm-status-muted-skipped": "rgba(138,143,148,0.12)",
};

describe("design tokens v2", () => {
  it("declares all 37 colours under :root[data-theme=dark]", () => {
    const actual = declarations(block(':root[data-theme="dark"]'));
    const colours = [...actual.entries()].filter(([name]) => DARK[name] !== undefined);
    expect(colours).toHaveLength(37);
    for (const [name, value] of Object.entries(DARK)) {
      expect(actual.get(name), `dark --${name}`).toBe(value);
    }
  });

  it("declares all 37 colours under :root[data-theme=light]", () => {
    const actual = declarations(block(':root[data-theme="light"]'));
    const colours = [...actual.entries()].filter(([name]) => LIGHT[name] !== undefined);
    expect(colours).toHaveLength(37);
    for (const [name, value] of Object.entries(LIGHT)) {
      expect(actual.get(name), `light --${name}`).toBe(value);
    }
  });

  it("keeps the two theme palettes in lockstep", () => {
    expect(Object.keys(DARK).sort()).toEqual(Object.keys(LIGHT).sort());
  });

  it("publishes the shared typography, radius, spacing, band and elevation tokens", () => {
    const root = declarations(block(":root"));
    expect(root.get("nm-font-ui")).toBe(
      '"Segoe UI Variable Text", "Microsoft YaHei UI", system-ui, sans-serif',
    );
    expect(root.get("nm-font-data")).toBe(
      '"Cascadia Mono", "Consolas", ui-monospace, monospace',
    );
    expect(root.get("nm-text-display")).toBe("700 28px/36px var(--nm-font-ui)");
    expect(root.get("nm-text-title")).toBe("700 20px/28px var(--nm-font-ui)");
    expect(root.get("nm-text-body")).toBe("400 14px/20px var(--nm-font-ui)");
    expect(root.get("nm-text-body-strong")).toBe("500 14px/20px var(--nm-font-ui)");
    expect(root.get("nm-text-caption")).toBe("400 12px/16px var(--nm-font-ui)");
    expect(root.get("nm-text-data")).toBe("400 12px/16px var(--nm-font-data)");
    expect(root.get("nm-radius-overlay")).toBe("8px");
    expect(root.get("nm-radius-control")).toBe("4px");
    expect(root.get("nm-radius-cell")).toBe("2px");
    expect(root.get("nm-space-1")).toBe("4px");
    expect(root.get("nm-space-2")).toBe("8px");
    expect(root.get("nm-space-3")).toBe("12px");
    expect(root.get("nm-space-4")).toBe("16px");
    expect(root.get("nm-space-5")).toBe("24px");
    expect(root.get("nm-band-titlebar")).toBe("48px");
    expect(root.get("nm-band-toolbar")).toBe("48px");
    expect(root.get("nm-elevation-8")).toBe("0 8px 16px rgba(0,0,0,0.16)");
    expect(root.get("nm-elevation-16")).toBe("0 16px 32px rgba(0,0,0,0.22)");
  });

  it("only uses 8 / 4 / 2 / 0 radius values", () => {
    const radii = [...css.matchAll(/--nm-radius-[a-z-]+\s*:\s*([^;]+);/g)].map((m) => m[1].trim());
    expect(radii.length).toBeGreaterThan(0);
    for (const radius of radii) {
      expect(["8px", "4px", "2px", "0"]).toContain(radius);
    }
  });
});

