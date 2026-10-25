import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const css = readFileSync(resolve(process.cwd(), "src/design/acrylic.css"), "utf8");

function block(selector: string): string {
  const escaped = selector.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const match = css.match(new RegExp(`${escaped}\\s*\\{([\\s\\S]*?)\\n\\}`, "m"));
  if (!match) throw new Error(`missing CSS block: ${selector}`);
  return match[1];
}

describe("acrylic material", () => {
  it("paints the 40px tier with tint, blur, saturate, stroke, highlight and overlay radius", () => {
    const rule = block(".nm-acrylic");
    expect(rule).toContain("background: var(--nm-acrylic-tint)");
    expect(rule).toContain("-webkit-backdrop-filter: blur(40px) saturate(140%)");
    expect(rule).toContain("backdrop-filter: blur(40px) saturate(140%)");
    expect(rule).toContain("border: 1px solid var(--nm-acrylic-stroke)");
    expect(rule).toContain("box-shadow: inset 0 1px 0 var(--nm-acrylic-highlight)");
    expect(rule).toContain("border-radius: var(--nm-radius-overlay)");
  });

  it("keeps the mandatory feTurbulence data-URI noise layer", () => {
    const noise = block(".nm-acrylic::after");
    expect(noise).toContain("content: \"\"");
    expect(noise).toContain("position: absolute");
    expect(noise).toContain("inset: 0");
    expect(noise).toContain("pointer-events: none");
    expect(noise).toContain("opacity: var(--nm-acrylic-noise)");
    expect(noise).toContain("mix-blend-mode: overlay");
    expect(noise).toContain("data:image/svg+xml");
    expect(noise).toContain("feTurbulence");
    expect(noise).toContain("fractalNoise");
    expect(noise).toContain("baseFrequency=%220.5%22");
    expect(noise).toContain("numOctaves=%223%22");
    expect(css.match(/feTurbulence/g)?.length ?? 0).toBeGreaterThanOrEqual(3);

    // 强度集中在单一变量上，三档伪元素共用，避免各写一个值后漂移。
    expect(css).toContain("--nm-acrylic-noise: 0.08");
    expect(css.match(/opacity: var\(--nm-acrylic-noise\)/g)?.length ?? 0).toBeGreaterThanOrEqual(3);
    // 颗粒尺度无法用 var() 注入，所以三处必须字面量一致，靠测试防漏改。
    expect(css.match(/baseFrequency=%220\.5%22/g)?.length ?? 0).toBe(3);
  });

  it("provides the 24px band tier and the strong modal tier", () => {
    const band = block(".nm-acrylic-24");
    expect(band).toContain("blur(24px) saturate(140%)");
    expect(band).toContain("background: var(--nm-acrylic-tint)");

    const strong = block(".nm-acrylic-strong");
    expect(strong).toContain("background: var(--nm-acrylic-tint-strong)");
    expect(strong).toContain("blur(40px) saturate(140%)");
    expect(strong).toContain("border: 1px solid var(--nm-acrylic-stroke)");
  });

  it("drops only the blur when backdrop-filter is unsupported", () => {
    expect(css).toContain("@supports not (backdrop-filter: blur(1px))");
    const fallback = css.slice(css.indexOf("@supports not (backdrop-filter: blur(1px))"));
    expect(fallback).toContain("backdrop-filter: none");
    expect(fallback).toContain("background: var(--nm-acrylic-tint)");
    expect(fallback).toContain(".nm-acrylic-24");
    expect(fallback).toContain(".nm-acrylic-strong");
  });

  it("switches every tier to a solid surface under prefers-reduced-transparency", () => {
    expect(css).toContain("@media (prefers-reduced-transparency: reduce)");
    const start = css.indexOf("@media (prefers-reduced-transparency: reduce)");
    const reduced = css.slice(start);
    expect(reduced).toContain("background: var(--nm-bg-solid)");
    expect(reduced).toContain("backdrop-filter: none");
    expect(reduced).toContain("content: none");
    expect(reduced).toContain(".nm-acrylic-24");
    expect(reduced).toContain(".nm-acrylic-strong");
    expect(reduced).toContain(".nm-acrylic-off");
  });

  it("ships the budget fallback with tint but no blur and no noise", () => {
    const off = block(".nm-acrylic-off");
    expect(off).toContain("background: var(--nm-acrylic-tint-strong)");
    expect(off).toContain("backdrop-filter: none");
    expect(off).toContain("border: 1px solid var(--nm-acrylic-stroke)");
    expect(css).not.toContain(".nm-acrylic-off::after");
  });
});

