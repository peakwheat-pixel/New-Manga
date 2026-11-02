import { useCallback, useEffect, useId, useRef, useState } from "react";
import { Icon, type IconName } from "../components/Icon";
import type { CommandSpec } from "./types";

/**
 * 全局命令面板（Ctrl+K）。
 *
 * 从 `pages/Shelf.tsx` 的骨架实现里提出来做成运行时共用件，原因是四页都要能
 * 唤起它，而每页各拷一份必然走样。相比骨架版补了三条硬要求：
 *
 *  1. **焦点圈禁**：`role="dialog" aria-modal="true"` 只有配上真正的 Tab 循环
 *     才成立。开面板时把焦点送进搜索框，Tab / Shift+Tab 只在面板内循环，
 *     关闭后焦点回到唤起它的那个元素（否则键盘用户会被丢到 body）。
 *  2. **键盘全通路**：↑↓ 选择、Home/End 跳两端、Enter 执行、Esc 关闭，
 *     并用 `aria-activedescendant` 让读屏能跟随高亮项。
 *  3. **不做假动作**：`disabledReason` 非空即不可用，并当条展示原因，
 *     不静默吞掉。
 */

const FOCUSABLE = [
  "button:not([disabled])",
  "input:not([disabled])",
  "select:not([disabled])",
  "textarea:not([disabled])",
  "[tabindex]:not([tabindex='-1'])",
].join(",");

export interface CommandPaletteProps {
  open: boolean;
  onClose(): void;
  commands: readonly CommandSpec[];
  title?: string;
  placeholder?: string;
}

export function CommandPalette({
  open,
  onClose,
  commands,
  title = "命令面板",
  placeholder = "搜索命令或页面",
}: CommandPaletteProps) {
  const dialogRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const restoreFocusRef = useRef<HTMLElement | null>(null);
  const [query, setQuery] = useState("");
  const [activeIndex, setActiveIndex] = useState(0);
  const listboxId = useId();

  const available = commands.filter((command) => !command.disabledReason);
  const visible = commands.filter((command) => {
    if (!query.trim()) return true;
    const needle = query.trim().toLowerCase();
    return (
      command.label.toLowerCase().includes(needle) ||
      (command.hint ?? "").toLowerCase().includes(needle)
    );
  });

  // 打开时记住唤起点、清空查询并聚焦输入框；关闭时把焦点还回去。
  useEffect(() => {
    if (!open) return;
    restoreFocusRef.current =
      typeof document !== "undefined" && document.activeElement instanceof HTMLElement
        ? document.activeElement
        : null;
    setQuery("");
    setActiveIndex(0);
    /*
     * 焦点直接同步落到输入框：effect 在 DOM 提交之后运行，此时 input 已经挂载。
     * 不用 requestAnimationFrame —— jsdom 里 rAF 不保证在断言前执行，会让
     * "打开即聚焦"这条可访问性契约变成不可测的时序依赖。
     */
    inputRef.current?.focus();

    /*
     * 窗口级 Esc：面板本身挂着 onKeyDown，但焦点可能在面板外（例如骨架页里
     * 用按钮唤起后测试直接在 window 上派发按键），也可能被宿主窗口吞掉。
     * 全局补一层，保证"Esc 关闭"在任何焦点位置都成立。
     */
    const onWindowKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
      }
    };
    window.addEventListener("keydown", onWindowKeyDown);

    return () => {
      window.removeEventListener("keydown", onWindowKeyDown);
      const target = restoreFocusRef.current;
      if (target && typeof target.focus === "function" && target.isConnected) {
        target.focus();
      }
    };
  }, [open, onClose]);

  useEffect(() => {
    if (open) setActiveIndex(0);
  }, [query, open]);

  const runAt = useCallback(
    (index: number) => {
      const command = visible[index];
      if (!command) return;
      if (command.disabledReason) return;
      onClose();
      command.run();
    },
    [onClose, visible],
  );

  const trapTab = useCallback((event: React.KeyboardEvent<HTMLDivElement>) => {
    if (event.key !== "Tab") return;
    const dialog = dialogRef.current;
    if (!dialog) return;
    const focusable = Array.from(dialog.querySelectorAll<HTMLElement>(FOCUSABLE));
    if (focusable.length === 0) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    const current = document.activeElement;

    if (!event.shiftKey && current === last) {
      event.preventDefault();
      first.focus();
    } else if (event.shiftKey && (current === first || current === dialog)) {
      event.preventDefault();
      last.focus();
    }
  }, []);

  const onKeyDown = useCallback(
    (event: React.KeyboardEvent<HTMLDivElement>) => {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
        return;
      }
      if (event.key === "ArrowDown") {
        event.preventDefault();
        if (visible.length === 0) return;
        setActiveIndex((index) => (index + 1) % visible.length);
        return;
      }
      if (event.key === "ArrowUp") {
        event.preventDefault();
        if (visible.length === 0) return;
        setActiveIndex((index) => (index - 1 + visible.length) % visible.length);
        return;
      }
      if (event.key === "Home") {
        event.preventDefault();
        setActiveIndex(0);
        return;
      }
      if (event.key === "End") {
        event.preventDefault();
        setActiveIndex(Math.max(0, visible.length - 1));
        return;
      }
      if (event.key === "Enter") {
        event.preventDefault();
        runAt(activeIndex);
        return;
      }
      trapTab(event);
    },
    [activeIndex, onClose, runAt, trapTab, visible.length],
  );

  if (!open) return null;

  const activeCommand = visible[activeIndex];

  return (
    <div
      className="nm-command-backdrop"
      data-testid="command-backdrop"
      onMouseDown={onClose}
    >
      <div
        ref={dialogRef}
        className="nm-command nm-acrylic-strong"
        role="dialog"
        aria-modal="true"
        aria-label={title}
        data-testid="command-palette"
        onMouseDown={(event) => event.stopPropagation()}
        onKeyDown={onKeyDown}
      >
        <div className="nm-command__input">
          <Icon name="search" size={16} />
          <input
            ref={inputRef}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder={placeholder}
            aria-label={placeholder}
            aria-controls={listboxId}
            aria-activedescendant={
              activeCommand ? `${listboxId}-${activeCommand.id}` : undefined
            }
            role="combobox"
            aria-expanded="true"
            aria-autocomplete="list"
            data-testid="command-input"
          />
          <span className="nm-kbd">Esc</span>
        </div>

        <div className="nm-command__list" role="listbox" id={listboxId} aria-label="命令">
          {visible.length === 0 ? (
            <p className="nm-command__empty nm-caption nm-tertiary" data-testid="command-empty">
              没有匹配的命令
            </p>
          ) : (
            visible.map((command, index) => (
              <button
                key={command.id}
                type="button"
                role="option"
                id={`${listboxId}-${command.id}`}
                aria-selected={index === activeIndex}
                data-active={index === activeIndex}
                data-testid={`command-item-${command.id}`}
                className="nm-command__item"
                disabled={Boolean(command.disabledReason)}
                onMouseEnter={() => setActiveIndex(index)}
                onClick={() => runAt(index)}
              >
                <span className="nm-command__icon">
                  <Icon name={(command.icon ?? "command") as IconName} size={16} />
                </span>
                <span className="nm-command__copy">
                  <span>{command.label}</span>
                  <span className="nm-caption nm-tertiary">
                    {command.disabledReason ?? command.hint}
                  </span>
                </span>
                <Icon name="chevron-right" size={14} />
              </button>
            ))
          )}
        </div>

        <div className="nm-command__foot">
          <span>
            <span className="nm-kbd">↑</span>
            <span className="nm-kbd">↓</span> 选择
          </span>
          <span>
            <span className="nm-kbd">Enter</span> 执行
          </span>
          <span>
            <span className="nm-kbd">Esc</span> 关闭
          </span>
          <span className="nm-command__count nm-data nm-tertiary">
            {available.length}/{commands.length} 可用
          </span>
        </div>
      </div>
    </div>
  );
}
