import { useEffect, useState } from "react";
import { BookshelfPage } from "../bookshelf/BookshelfPage";
import { LibraryClient } from "../library/client";
import { ReaderPage } from "../reader/ReaderPage";
import { SettingsClient } from "../settings/client";
import { SettingsPage } from "../settings/SettingsPage";
import { tokens } from "../theme/tokens";
import { WorkbenchPage, type InvokeFn } from "../workbench/WorkbenchPage";

export type PageId = "bookshelf" | "workbench" | "reader" | "settings";

export interface AppShellProps {
  invoke?: InvokeFn;
  initialPage?: PageId;
}

export function AppShell({ invoke, initialPage = "bookshelf" }: AppShellProps) {
  const [activePage, setActivePage] = useState<PageId>(initialPage);

  // Cross-page navigation context (bookId / chapterId passed from Bookshelf to Workbench / Reader)
  const [workbenchContext, setWorkbenchContext] = useState<{
    bookId: string | null;
    chapterId: string | null;
  }>({ bookId: null, chapterId: null });

  const [readerContext, setReaderContext] = useState<{
    bookId: string | null;
    chapterId: string | null;
  }>({ bookId: null, chapterId: null });

  // Clients
  const libraryClient = new LibraryClient(invoke);
  const settingsClient = new SettingsClient(invoke);

  // Global Keyboard Shortcuts (Ctrl+1..4) (§1.4)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        if (e.key === "1") {
          e.preventDefault();
          setActivePage("bookshelf");
        } else if (e.key === "2") {
          e.preventDefault();
          setActivePage("workbench");
        } else if (e.key === "3") {
          e.preventDefault();
          setActivePage("reader");
        } else if (e.key === "4") {
          e.preventDefault();
          setActivePage("settings");
        }
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleEnterWorkbench = (bookId: string, chapterId: string) => {
    setWorkbenchContext({ bookId, chapterId });
    setActivePage("workbench");
  };

  const handleEnterReader = (bookId: string, chapterId: string) => {
    setReaderContext({ bookId, chapterId });
    setActivePage("reader");
  };

  const handleReturnToBookshelf = () => {
    setActivePage("bookshelf");
  };

  return (
    <div
      data-testid="app-shell"
      style={{
        display: "flex",
        width: "100%",
        height: "100vh",
        minWidth: tokens.dimensions.minAppWidth,
        minHeight: tokens.dimensions.minAppHeight,
        boxSizing: "border-box",
        backgroundColor: tokens.color.bg.app,
        fontFamily: tokens.typography.fontFamily,
        overflow: "hidden",
      }}
    >
      {/* 1. Left 64px Rail (§1.1) */}
      <nav
        data-testid="app-nav-rail"
        style={{
          width: tokens.dimensions.railWidth,
          height: "100%",
          boxSizing: "border-box",
          backgroundColor: tokens.color.bg.rail,
          borderRight: `1px solid ${tokens.color.border.default}`,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          paddingTop: tokens.spacing.md,
          gap: tokens.spacing.md,
          flexShrink: 0,
        }}
      >
        {/* App Logo / Mark */}
        <div
          title="New Manga"
          style={{
            fontSize: 18,
            fontWeight: 800,
            color: tokens.color.accent.primary,
            marginBottom: tokens.spacing.xs,
            userSelect: "none",
          }}
        >
          NM
        </div>

        {/* 1. 书架 Bookshelf (Ctrl+1) */}
        <button
          type="button"
          data-testid="nav-bookshelf"
          title="书架 (Ctrl+1)"
          onClick={() => setActivePage("bookshelf")}
          data-active={activePage === "bookshelf"}
          style={{
            width: 48,
            height: 48,
            borderRadius: tokens.radius.card,
            border: "none",
            backgroundColor: activePage === "bookshelf" ? tokens.color.accent.selected : "transparent",
            color: activePage === "bookshelf" ? tokens.color.accent.primary : tokens.color.text.secondary,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            fontWeight: activePage === "bookshelf" ? 600 : 400,
            fontSize: 10,
            gap: 2,
            transition: "background-color 0.12s ease",
            outline: "none",
          }}
        >
          <span style={{ fontSize: 18, lineHeight: 1 }}>📚</span>
          <span>书架</span>
        </button>

        {/* 2. 工作台 Workbench (Ctrl+2) */}
        <div style={{ position: "relative" }}>
          <button
            type="button"
            data-testid="nav-workbench"
            title="工作台 (Ctrl+2)"
            onClick={() => setActivePage("workbench")}
            data-active={activePage === "workbench"}
            style={{
              width: 48,
              height: 48,
              borderRadius: tokens.radius.card,
              border: "none",
              backgroundColor: activePage === "workbench" ? tokens.color.accent.selected : "transparent",
              color: activePage === "workbench" ? tokens.color.accent.primary : tokens.color.text.secondary,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer",
              fontWeight: activePage === "workbench" ? 600 : 400,
              fontSize: 10,
              gap: 2,
              transition: "background-color 0.12s ease",
              outline: "none",
            }}
          >
            <span style={{ fontSize: 18, lineHeight: 1 }}>🛠️</span>
            <span>工作台</span>
          </button>
          {/* NavBadge on Workbench is HIDDEN before GAP-G15 is resolved (AC1:不得虚构运行状态) */}
        </div>

        {/* 3. 阅读器 Reader (Ctrl+3) */}
        <button
          type="button"
          data-testid="nav-reader"
          title="阅读器 (Ctrl+3)"
          onClick={() => setActivePage("reader")}
          data-active={activePage === "reader"}
          style={{
            width: 48,
            height: 48,
            borderRadius: tokens.radius.card,
            border: "none",
            backgroundColor: activePage === "reader" ? tokens.color.accent.selected : "transparent",
            color: activePage === "reader" ? tokens.color.accent.primary : tokens.color.text.secondary,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            fontWeight: activePage === "reader" ? 600 : 400,
            fontSize: 10,
            gap: 2,
            transition: "background-color 0.12s ease",
            outline: "none",
          }}
        >
          <span style={{ fontSize: 18, lineHeight: 1 }}>📖</span>
          <span>阅读器</span>
        </button>

        {/* 4. 设置 Settings (Ctrl+4) */}
        <button
          type="button"
          data-testid="nav-settings"
          title="设置 (Ctrl+4)"
          onClick={() => setActivePage("settings")}
          data-active={activePage === "settings"}
          style={{
            width: 48,
            height: 48,
            borderRadius: tokens.radius.card,
            border: "none",
            backgroundColor: activePage === "settings" ? tokens.color.accent.selected : "transparent",
            color: activePage === "settings" ? tokens.color.accent.primary : tokens.color.text.secondary,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            fontWeight: activePage === "settings" ? 600 : 400,
            fontSize: 10,
            gap: 2,
            transition: "background-color 0.12s ease",
            outline: "none",
          }}
        >
          <span style={{ fontSize: 18, lineHeight: 1 }}>⚙️</span>
          <span>设置</span>
        </button>
      </nav>

      {/* 2. Four Pages Keep-Alive Container (§1.2) */}
      <div style={{ flex: 1, height: "100%", overflow: "hidden", position: "relative" }}>
        {/* Bookshelf Page */}
        <div
          data-testid="page-container-bookshelf"
          style={{
            width: "100%",
            height: "100%",
            display: activePage === "bookshelf" ? "flex" : "none",
          }}
        >
          <BookshelfPage
            client={libraryClient}
            onEnterWorkbench={handleEnterWorkbench}
            onEnterReader={handleEnterReader}
          />
        </div>

        {/* Workbench Page */}
        <div
          data-testid="page-container-workbench"
          data-book-id={workbenchContext.bookId || undefined}
          data-chapter-id={workbenchContext.chapterId || undefined}
          style={{
            width: "100%",
            height: "100%",
            display: activePage === "workbench" ? "flex" : "none",
          }}
        >
          <WorkbenchPage
            invoke={invoke}
            bookId={workbenchContext.bookId}
            chapterId={workbenchContext.chapterId}
          />
        </div>

        {/* Reader Page */}
        <div
          data-testid="page-container-reader"
          style={{
            width: "100%",
            height: "100%",
            display: activePage === "reader" ? "flex" : "none",
          }}
        >
          <ReaderPage
            bookId={readerContext.bookId}
            chapterId={readerContext.chapterId}
            onReturnToBookshelf={handleReturnToBookshelf}
          />
        </div>

        {/* Settings Page */}
        <div
          data-testid="page-container-settings"
          style={{
            width: "100%",
            height: "100%",
            display: activePage === "settings" ? "flex" : "none",
          }}
        >
          <SettingsPage client={settingsClient} />
        </div>
      </div>
    </div>
  );
}
