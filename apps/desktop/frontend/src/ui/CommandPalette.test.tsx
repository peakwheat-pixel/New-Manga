// @vitest-environment jsdom
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { CommandPalette } from "./CommandPalette";
import type { CommandSpec } from "./types";

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

function keydown(target: Element, key: string, options: KeyboardEventInit = {}) {
  act(() => {
    target.dispatchEvent(new window.KeyboardEvent("keydown", { key, bubbles: true, ...options }));
  });
}

function typeInto(input: HTMLInputElement, value: string) {
  const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value")?.set;
  act(() => {
    setter?.call(input, value);
    input.dispatchEvent(new window.Event("input", { bubbles: true }));
  });
}

function commands(overrides: Partial<CommandSpec>[] = []): CommandSpec[] {
  const base: CommandSpec[] = [
    { id: "shelf", label: "前往书架", hint: "浏览作品", icon: "book", run: vi.fn() },
    { id: "settings", label: "前往设置", hint: "识别与翻译", icon: "settings", run: vi.fn() },
    { id: "theme", label: "切换主题", hint: "Mica / Acrylic", icon: "moon", run: vi.fn() },
  ];
  overrides.forEach((patch, index) => {
    if (patch) Object.assign(base[index], patch);
  });
  return base;
}

beforeEach(() => {
  document.body.innerHTML = "";
});

afterEach(() => {
  act(() => root?.unmount());
  root = undefined;
  container = undefined;
});

describe("CommandPalette", () => {
  it("renders nothing while closed and focuses the input when opened", () => {
    const host = mount(<CommandPalette open={false} onClose={() => undefined} commands={commands()} />);
    expect(host.querySelector('[data-testid="command-palette"]')).toBeNull();

    act(() => {
      root?.render(<CommandPalette open onClose={() => undefined} commands={commands()} />);
    });
    const input = document.querySelector<HTMLInputElement>('[data-testid="command-input"]');
    expect(input).not.toBeNull();
    expect(document.activeElement).toBe(input);
  });

  it("moves the highlight with ArrowDown/ArrowUp/Home/End and wraps", () => {
    mount(<CommandPalette open onClose={() => undefined} commands={commands()} />);
    const dialog = document.querySelector('[data-testid="command-palette"]')!;
    const activeId = () =>
      dialog.querySelector('[role="option"][aria-selected="true"]')?.getAttribute("data-testid");

    expect(activeId()).toBe("command-item-shelf");
    keydown(dialog, "ArrowDown");
    expect(activeId()).toBe("command-item-settings");
    keydown(dialog, "ArrowDown");
    expect(activeId()).toBe("command-item-theme");
    // 末项再按向下回到首项（环绕），不是卡住。
    keydown(dialog, "ArrowDown");
    expect(activeId()).toBe("command-item-shelf");
    keydown(dialog, "ArrowUp");
    expect(activeId()).toBe("command-item-theme");
    keydown(dialog, "Home");
    expect(activeId()).toBe("command-item-shelf");
    keydown(dialog, "End");
    expect(activeId()).toBe("command-item-theme");
  });

  it("runs the highlighted command on Enter and closes first", () => {
    const list = commands();
    const onClose = vi.fn();
    mount(<CommandPalette open onClose={onClose} commands={list} />);
    const dialog = document.querySelector('[data-testid="command-palette"]')!;
    keydown(dialog, "ArrowDown");
    keydown(dialog, "Enter");
    expect(onClose).toHaveBeenCalledTimes(1);
    expect(list[1].run).toHaveBeenCalledTimes(1);
    expect(list[0].run).not.toHaveBeenCalled();
  });

  it("closes on Escape from the window even when focus escapes the dialog", () => {
    const onClose = vi.fn();
    mount(<CommandPalette open onClose={onClose} commands={commands()} />);
    // 焦点被挪到面板外（例如宿主窗口复用焦点），Esc 仍必须生效。
    act(() => {
      (document.body as HTMLElement).focus();
    });
    act(() => {
      window.dispatchEvent(new window.KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
    });
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("filters by query and reports an explicit empty state", () => {
    mount(<CommandPalette open onClose={() => undefined} commands={commands()} />);
    const input = document.querySelector<HTMLInputElement>('[data-testid="command-input"]')!;
    typeInto(input, "设置");
    expect(document.querySelectorAll('[role="option"]')).toHaveLength(1);
    expect(document.querySelector('[data-testid="command-item-settings"]')).not.toBeNull();

    typeInto(input, "没有这个命令");
    expect(document.querySelectorAll('[role="option"]')).toHaveLength(0);
    expect(document.querySelector('[data-testid="command-empty"]')).not.toBeNull();
  });

  it("refuses to run a command that declares a disabledReason", () => {
    const list = commands([{ disabledReason: "未选择作品" }]);
    const onClose = vi.fn();
    mount(<CommandPalette open onClose={onClose} commands={list} />);
    const dialog = document.querySelector('[data-testid="command-palette"]')!;
    const first = document.querySelector<HTMLButtonElement>('[data-testid="command-item-shelf"]')!;
    expect(first.disabled).toBe(true);
    expect(first.textContent).toContain("未选择作品");
    keydown(dialog, "Enter");
    expect(list[0].run).not.toHaveBeenCalled();
    expect(onClose).not.toHaveBeenCalled();
  });

  it("traps Tab inside the dialog and restores focus to the opener on close", () => {
    // 唤起按钮放在 React 树之外：它就是"打开面板之前用户聚焦的那个元素"。
    const opener = document.createElement("button");
    opener.setAttribute("data-testid", "opener");
    document.body.appendChild(opener);
    opener.focus();
    expect(document.activeElement).toBe(opener);

    container = document.createElement("div");
    document.body.appendChild(container);
    root = createRoot(container);
    act(() => {
      root?.render(<CommandPalette open onClose={() => undefined} commands={commands()} />);
    });

    const dialog = document.querySelector('[data-testid="command-palette"]')!;
    const items = Array.from(dialog.querySelectorAll<HTMLElement>('[role="option"]'));
    const last = items[items.length - 1];
    act(() => last.focus());
    keydown(last, "Tab");
    // 从末项 Tab → 回到面板内第一个可聚焦元素（输入框），而不是逃离面板。
    expect(dialog.contains(document.activeElement)).toBe(true);
    expect(document.activeElement?.getAttribute("data-testid")).toBe("command-input");

    // 关闭后焦点回到唤起它的按钮。
    act(() => {
      root?.render(<CommandPalette open={false} onClose={() => undefined} commands={commands()} />);
    });
    expect(document.activeElement).toBe(opener);
  });
});
