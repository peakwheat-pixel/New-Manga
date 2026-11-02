// @vitest-environment jsdom
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, describe, expect, it } from "vitest";
import { useAcrylicBudget } from "./useAcrylicBudget";

interface ProbeProps {
  activeId: string | null;
  layers: string[];
}

function Probe({ activeId, layers }: ProbeProps) {
  const budget = useAcrylicBudget(activeId, layers);
  return (
    <div data-testid="probe" data-blur-count={budget.blurCount}>
      {layers.map((id) => (
        <span
          key={id}
          data-testid={`layer-${id}`}
          data-blurred={budget.isBlurred(id)}
          className={budget.className(id, id === "c" ? "acrylic-24" : "acrylic")}
        />
      ))}
    </div>
  );
}

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

function classes(host: HTMLElement, id: string): string[] {
  return [...(host.querySelector(`[data-testid="layer-${id}"]`)?.classList ?? [])];
}

describe("useAcrylicBudget", () => {
  it("keeps every layer when the screen is within budget", () => {
    const host = mount(<Probe activeId="a" layers={["a", "b"]} />);
    expect(host.querySelector('[data-testid="probe"]')?.getAttribute("data-blur-count")).toBe("2");
    expect(classes(host, "a")).toContain("nm-acrylic");
    expect(classes(host, "b")).toContain("nm-acrylic");
  });

  it("downgrades non-active layers when three acrylic layers would coexist", () => {
    const host = mount(<Probe activeId="c" layers={["a", "b", "c"]} />);
    expect(host.querySelector('[data-testid="probe"]')?.getAttribute("data-blur-count")).toBe("2");
    expect(classes(host, "c")).toContain("nm-acrylic-24");
    expect(classes(host, "a")).toContain("nm-acrylic");
    expect(classes(host, "b")).toContain("nm-acrylic-off");
    expect(classes(host, "b")).not.toContain("nm-acrylic");
  });

  it("puts the active layer first in visual priority", () => {
    const host = mount(<Probe activeId="b" layers={["a", "b", "c"]} />);
    expect(classes(host, "b")).toContain("nm-acrylic");
    expect(classes(host, "a")).toContain("nm-acrylic");
    expect(classes(host, "c")).toContain("nm-acrylic-off");
  });

  it("never keeps more than the budget when the active id is not declared", () => {
    const host = mount(<Probe activeId="missing" layers={["a", "b", "c", "d"]} />);
    expect(host.querySelector('[data-testid="probe"]')?.getAttribute("data-blur-count")).toBe("2");
    expect(classes(host, "a")).toContain("nm-acrylic");
    expect(classes(host, "b")).toContain("nm-acrylic");
    expect(classes(host, "c")).toContain("nm-acrylic-off");
    expect(classes(host, "d")).toContain("nm-acrylic-off");
  });
});
