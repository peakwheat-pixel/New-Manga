import { useEffect, useLayoutEffect, useState } from "react";
import { isDesignPage, type DesignPage, type Theme } from "../design/types";
import { Reader } from "./Reader";
import { Shelf } from "./Shelf";
import { Workbench } from "./Workbench";
import "../design/tokens.css";
import "../design/base.css";
import "../design/acrylic.css";
import "./pages.css";

function queryPage(): DesignPage | undefined {
  if (typeof window === "undefined") return undefined;
  const value = new URLSearchParams(window.location.search).get("page");
  return isDesignPage(value) ? value : undefined;
}

function queryTheme(): Theme | undefined {
  if (typeof window === "undefined") return undefined;
  const value = new URLSearchParams(window.location.search).get("theme");
  return value === "light" || value === "dark" ? value : undefined;
}

export interface DesignPreviewProps {
  initialPage?: DesignPage;
  initialTheme?: Theme;
}

/**
 * Entry shell for the v2 static skeleton. Reached with `?view=design`
 * (optionally `&page=workbench&theme=light`). The three page roots share the
 * token layer but each one owns its own acrylic budget declaration.
 */
export function DesignPreview({ initialPage, initialTheme }: DesignPreviewProps = {}) {
  const [page, setPage] = useState<DesignPage>(() => initialPage ?? queryPage() ?? "shelf");
  const [theme, setTheme] = useState<Theme>(() => initialTheme ?? queryTheme() ?? "dark");

  useLayoutEffect(() => {
    const root = document.documentElement;
    const previous = root.dataset.theme;
    root.dataset.theme = theme;
    return () => {
      if (previous === undefined) delete root.dataset.theme;
      else root.dataset.theme = previous;
    };
  }, [theme]);

  useEffect(() => {
    const previousTitle = document.title;
    document.title = "New Manga · Design v2";

    const onKeyDown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      const typing =
        target?.tagName === "INPUT" ||
        target?.tagName === "TEXTAREA" ||
        target?.tagName === "SELECT" ||
        target?.isContentEditable === true;
      if (typing) return;

      if ((event.ctrlKey || event.metaKey) && ["1", "2", "3"].includes(event.key)) {
        event.preventDefault();
        setPage(event.key === "1" ? "shelf" : event.key === "2" ? "workbench" : "reader");
        return;
      }
      if (!event.ctrlKey && !event.metaKey && event.key.toLowerCase() === "t") {
        event.preventDefault();
        setTheme((current) => (current === "dark" ? "light" : "dark"));
      }
      if (event.key === "Escape") setPage("shelf");
    };

    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      document.title = previousTitle;
    };
  }, []);

  const toggleTheme = () => setTheme((current) => (current === "dark" ? "light" : "dark"));

  return (
    <div className="nm-preview" data-testid="design-preview" data-page={page} data-theme={theme}>
      {page === "shelf" && (
        <Shelf
          activePage={page}
          theme={theme}
          onNavigate={setPage}
          onToggleTheme={toggleTheme}
        />
      )}
      {page === "workbench" && (
        <Workbench theme={theme} onNavigate={setPage} onToggleTheme={toggleTheme} />
      )}
      {page === "reader" && (
        <Reader theme={theme} onNavigate={setPage} onToggleTheme={toggleTheme} />
      )}
    </div>
  );
}
