import { useRef, type KeyboardEvent } from "react";
import { Icon, type IconName } from "./Icon";
import type { DesignPage } from "../design/types";

interface TabSpec {
  id: DesignPage;
  label: string;
  icon: IconName;
}

const TABS: ReadonlyArray<TabSpec> = [
  { id: "shelf", label: "书架", icon: "book" },
  { id: "workbench", label: "工作台", icon: "tool" },
  { id: "reader", label: "阅读器", icon: "reader" },
];

export interface PrimaryNavProps {
  activePage: DesignPage;
  onNavigate: (page: DesignPage) => void;
}

/**
 * 一级页面切换栏。三个页面共用同一份实现，避免各自维护一份 tab 定义后走样。
 * 尺寸与样式来自 `.nm-tabs` / `.nm-tab`（pages.css）。
 *
 * 键盘可访问性：按 WAI-ARIA tabs 模式实现 roving tabindex —— 只有当前页的 tab
 * 在 Tab 序列里（tabIndex 0），其余为 -1；左右方向键在 tab 之间移动并同步切换
 * 页面，Home/End 跳到两端。缺了这段，`role="tablist"` 就是假的。
 */
export function PrimaryNav({ activePage, onNavigate }: PrimaryNavProps) {
  const tabRefs = useRef<Partial<Record<DesignPage, HTMLButtonElement | null>>>({});

  const moveTo = (index: number) => {
    const tab = TABS[index];
    if (!tab) return;
    onNavigate(tab.id);
    // 切换后焦点要跟着走，否则键盘用户会停在已隐藏的旧 tab 上。
    tabRefs.current[tab.id]?.focus();
  };

  const onKeyDown = (event: KeyboardEvent<HTMLButtonElement>, current: DesignPage) => {
    const index = TABS.findIndex((tab) => tab.id === current);
    let next = -1;
    if (event.key === "ArrowRight") next = (index + 1) % TABS.length;
    else if (event.key === "ArrowLeft") next = (index - 1 + TABS.length) % TABS.length;
    else if (event.key === "Home") next = 0;
    else if (event.key === "End") next = TABS.length - 1;
    if (next < 0) return;
    event.preventDefault();
    moveTo(next);
  };

  return (
    <nav className="nm-tabs" role="tablist" aria-label="一级页面">
      {TABS.map((tab) => (
        <button
          key={tab.id}
          ref={(element) => {
            tabRefs.current[tab.id] = element;
          }}
          type="button"
          role="tab"
          aria-selected={activePage === tab.id}
          tabIndex={activePage === tab.id ? 0 : -1}
          className="nm-tab"
          data-active={activePage === tab.id}
          data-testid={`tab-${tab.id}`}
          onClick={() => onNavigate(tab.id)}
          onKeyDown={(event) => onKeyDown(event, tab.id)}
        >
          <Icon name={tab.icon} size={15} />
          <span>{tab.label}</span>
        </button>
      ))}
    </nav>
  );
}
