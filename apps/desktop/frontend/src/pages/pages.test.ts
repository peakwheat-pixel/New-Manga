import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const css = readFileSync(resolve(process.cwd(), "src/pages/pages.css"), "utf8");

function block(selector: string): string {
  const escaped = selector.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const match = css.match(new RegExp(`${escaped}\\s*\\{([\\s\\S]*?)\\n\\}`, "m"));
  if (!match) throw new Error(`missing CSS block: ${selector}`);
  return match[1];
}

describe("v2 page geometry", () => {
  it("keeps the shelf titlebar and toolbar at 48px", () => {
    expect(block(".nm-titlebar")).toContain("height: var(--nm-band-titlebar)");
    expect(block(".nm-toolbar")).toContain("height: var(--nm-band-toolbar)");
  });

  it("keeps the 168px card and 340px detail panel", () => {
    expect(block(".nm-book-card")).toContain("width: 168px");
    expect(block(".nm-book-grid")).toContain("repeat(5, 168px)");
    expect(block(".nm-book-cover")).toContain("aspect-ratio: 2 / 3");
    expect(block(".nm-detail")).toContain("width: 340px");
    expect(block(".nm-detail")).toContain("flex: 0 0 340px");
  });

  it("keeps the 44px floating status bar inset by 16px", () => {
    const status = block(".nm-floating-status");
    expect(status).toContain("height: 44px");
    expect(status).toContain("left: var(--nm-space-4)");
    expect(status).toContain("right: var(--nm-space-4)");
    expect(status).toContain("bottom: var(--nm-space-4)");
  });

  it("keeps the workbench 72 / 360 / 40 geometry", () => {
    expect(block(".nm-filmstrip")).toContain("width: 72px");
    expect(block(".nm-filmstrip__thumb")).toContain("width: 52px");
    expect(block(".nm-filmstrip__thumb")).toContain("height: 52px");
    expect(block(".nm-inspector")).toContain("width: 360px");
    expect(block(".nm-inspector__rail")).toContain("width: 48px");
    expect(block(".nm-inspector__panel")).toContain("width: 312px");
    expect(block(".nm-pipeline")).toContain("height: 40px");
  });

  it("keeps the reader top 48 / bottom 40 floating bands", () => {
    expect(block(".nm-reader__top")).toContain("height: 48px");
    expect(block(".nm-reader__bottom")).toContain("height: 40px");
    expect(block(".nm-reader__page-area .nm-page-sheet")).toContain("aspect-ratio: 2 / 3");
  });

  it("uses no radius values outside 8 / 4 / 2 / 0 across the v2 stylesheets", () => {
    const sheets = [
      "src/pages/pages.css",
      "src/design/base.css",
      "src/design/acrylic.css",
      "src/components/StatusMark.css",
    ].map((file) => readFileSync(resolve(process.cwd(), file), "utf8"));
    const values = sheets.flatMap((sheet) =>
      [...sheet.matchAll(/border-radius:\s*([^;]+);/g)].map((match) => match[1].trim()),
    );
    expect(values.length).toBeGreaterThan(0);
    for (const value of values) {
      expect([
        "var(--nm-radius-overlay)",
        "var(--nm-radius-control)",
        "var(--nm-radius-cell)",
        "8px",
        "4px",
        "2px",
        "0",
        "inherit",
      ]).toContain(value);
    }
  });
});

