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
 */
export function PrimaryNav({ activePage, onNavigate }: PrimaryNavProps) {
  return (
    <nav className="nm-tabs" role="tablist" aria-label="一级页面">
      {TABS.map((tab) => (
        <button
          key={tab.id}
          type="button"
          role="tab"
          aria-selected={activePage === tab.id}
          className="nm-tab"
          data-active={activePage === tab.id}
          data-testid={`tab-${tab.id}`}
          onClick={() => onNavigate(tab.id)}
        >
          <Icon name={tab.icon} size={15} />
          <span>{tab.label}</span>
        </button>
      ))}
    </nav>
  );
}
