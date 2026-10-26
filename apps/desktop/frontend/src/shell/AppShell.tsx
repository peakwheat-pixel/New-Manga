import { useEffect, useState } from "react";
import { BookshelfPage } from "../bookshelf/BookshelfPage";
import { onLifecycleStatusChanged } from "../events";
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

  // P20-ISOLATION-1: Core sidecar lifecycle & health status
  const [coreStatus, setCoreStatus] = useState<"healthy" | "restarting" | "recovered" | "fatal">("healthy");
  const [statusMessage, setStatusMessage] = useState<string>("");

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

  // P20-ISOLATION-1: Lifecycle event listening & proactive heartbeat probe
  useEffect(() => {
    let unlisten: (() => void) | undefined;
    let active = true;

    void onLifecycleStatusChanged((payload) => {
      if (!active) return;
      const s = payload.status;
      if (s === "restarting" || s === "recovered" || s === "fatal") {
        setCoreStatus(s);
        setStatusMessage(
          payload.message ||
            (s === "restarting"
              ? "后端服务异常，正在尝试热重启..."
              : s === "recovered"
              ? "后端服务已恢复正常"
              : "后端服务异常，自动重启失败")
        );
      } else {
        setCoreStatus("healthy");
        setStatusMessage("");
      }
    }).then((fn) => {
      unlisten = fn;
    }).catch(() => {
      // Event bridge not available
    });

    const interval = setInterval(async () => {
      if (!invoke) return;
      try {
        await invoke("core_ping");
        if (!active) return;
        setCoreStatus((prev) => {
          if (prev === "restarting") {
            setStatusMessage("后端服务已恢复正常");
            return "recovered";
          }
          return prev;
        });
      } catch {
        if (!active) return;
        setCoreStatus((prev) => {
          if (prev === "healthy") {
            setStatusMessage("后端服务异常，正在尝试热重启...");
            return "restarting";
          }
          return prev;
        });
      }
    }, 2000);

    return () => {
      active = false;
      if (unlisten) unlisten();
      clearInterval(interval);
    };
  }, [invoke]);

  useEffect(() => {
    if (coreStatus === "recovered") {
      const timer = setTimeout(() => {
        setCoreStatus("healthy");
        setStatusMessage("");
      }, 2500);
      return () => clearTimeout(timer);
    }
  }, [coreStatus]);

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
      <div
        style={{
          flex: 1,
          height: "100%",
          overflow: "hidden",
          position: "relative",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* P20-ISOLATION-1: Global sidecar health banner (AC1 / AC2) */}
        {coreStatus !== "healthy" && (
          <div
            data-testid="core-status-banner"
            role="alert"
            aria-live="assertive"
            style={{
              width: "100%",
              padding: "8px 16px",
              boxSizing: "border-box",
              backgroundColor:
                coreStatus === "fatal"
                  ? "#3b1111"
                  : coreStatus === "recovered"
                  ? "#11331a"
                  : "#3a2a0d",
              color:
                coreStatus === "fatal"
                  ? "#ff8080"
                  : coreStatus === "recovered"
                  ? "#66e080"
                  : "#ffd566",
              borderBottom: `1px solid ${
                coreStatus === "fatal"
                  ? "#5c1d1d"
                  : coreStatus === "recovered"
                  ? "#1b4d27"
                  : "#5e4517"
              }`,
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              fontSize: 13,
              fontWeight: 600,
              flexShrink: 0,
              zIndex: 1000,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span>
                {coreStatus === "fatal" ? "❌" : coreStatus === "recovered" ? "✅" : "⚠️"}
              </span>
              <span>{statusMessage}</span>
            </div>
          </div>
        )}

        <div style={{ flex: 1, width: "100%", height: "100%", overflow: "hidden", position: "relative" }}>
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
            invoke={invoke}
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
    </div>
  );
}
