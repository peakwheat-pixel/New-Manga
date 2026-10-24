import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { onReadingProgressChanged, type ListenFn } from "../events";
import { LibraryClient } from "../library/client";
import { ResourceChannelClient } from "../resourceChannel/client";
import { tokens } from "../theme/tokens";
import { PagedReaderView } from "./PagedReaderView";
import { ReaderClient } from "./client";
import { ReaderEmptyState } from "./ReaderEmptyState";
import { ReaderToolbar } from "./ReaderToolbar";
import type {
  ReaderProjection,
  ReaderStartPosition,
  ReadingMode,
} from "./types";
import { WebtoonReaderView } from "./WebtoonReaderView";

export type InvokeFn = (command: string, args?: Record<string, unknown>) => Promise<unknown>;

export interface ReaderPageProps {
  bookId?: string | null;
  chapterId?: string | null;
  chapterTitle?: string | null;
  onReturnToBookshelf?: () => void;
  invoke?: InvokeFn;
  customListen?: ListenFn;
}

export function ReaderPage({
  bookId,
  chapterId,
  chapterTitle,
  onReturnToBookshelf,
  invoke,
  customListen,
}: ReaderPageProps) {
  // Clients
  const readerClient = useMemo(() => new ReaderClient(invoke), [invoke]);
  const libraryClient = useMemo(() => new LibraryClient(invoke), [invoke]);
  const resourceClient = useMemo(() => {
    const defaultInvoke = typeof window !== "undefined" ? (window as unknown as { __TAURI__?: { core?: { invoke: InvokeFn } } }).__TAURI__?.core?.invoke : undefined;
    return new ResourceChannelClient(invoke || (defaultInvoke as InvokeFn));
  }, [invoke]);

  // Reading settings & projection states
  const [displayMode, setDisplayMode] = useState<ReadingMode>("original");
  const [startPosition, setStartPosition] = useState<ReaderStartPosition>("resume");
  const [projection, setProjection] = useState<ReaderProjection | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Position within current projection
  const isMountedRef = useRef<boolean>(true);
  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
    };
  }, []);
  const [currentPageIndex, setCurrentPageIndex] = useState<number>(0);
  const [webtoonScrollOffsetY, setWebtoonScrollOffsetY] = useState<number>(0);
  const [webtoonPercent, setWebtoonPercent] = useState<number>(0);
  const [isSaving, setIsSaving] = useState<boolean>(false);

  // Progress tracking & timing
  const lastSaveTimeRef = useRef<number>(Date.now());
  const saveTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const activePositionRef = useRef<{ pageId: string; scrollOffsetY: number }>({ pageId: "", scrollOffsetY: 0 });

  // 1. Fetch Projection from Host/Core (W18)
  const fetchProjection = useCallback(
    async (targetChapterId: string, mode: ReadingMode, startPos: ReaderStartPosition) => {
      setLoading(true);
      setError(null);
      try {
        const proj = await readerClient.getReaderProjection(targetChapterId, mode, startPos);
        setProjection(proj);

        // Position initial restoration based on Core projection response (M2-C1 §6.3)
        if (proj.pages.length > 0) {
          const initPageId = proj.initial_position?.page_id;
          const foundIdx = proj.pages.findIndex((p) => p.page_id === initPageId);
          const resolvedIdx = foundIdx >= 0 ? foundIdx : 0;
          setCurrentPageIndex(resolvedIdx);

          const initialOffset = proj.initial_position?.scroll_offset_y || 0;
          setWebtoonScrollOffsetY(initialOffset);
          activePositionRef.current = {
            pageId: proj.pages[resolvedIdx]?.page_id || "",
            scrollOffsetY: initialOffset,
          };
        }
      } catch (err) {
        const code = typeof err === "object" && err !== null && "code" in err
          ? String((err as { code: unknown }).code)
          : (err as Error)?.message || "CORE_UNAVAILABLE";
        setError(code);
      } finally {
        if (isMountedRef.current) {
          setLoading(false);
        }
      }
    },
    [readerClient],
  );

  // Initial load or when chapterId changes
  useEffect(() => {
    if (!chapterId) {
      setProjection(null);
      setError(null);
      setLoading(false);
      return;
    }
    fetchProjection(chapterId, displayMode, startPosition);
  }, [chapterId, displayMode, startPosition, fetchProjection]);

  // 2. AC3 Event Discipline: On `core:ReadingProgressChanged`, RE-QUERY snapshot!
  // MUST NOT use event payload to directly drive position!
  useEffect(() => {
    if (!chapterId) return;

    let unlisten: (() => void) | undefined;
    let active = true;

    async function subscribe() {
      try {
        const cleanup = await onReadingProgressChanged((payload) => {
          if (!active) return;
          // Event is an invalidation hint only; query Core authoritative snapshot
          if (payload.chapter_id === chapterId) {
            fetchProjection(chapterId, displayMode, "resume");
          }
        }, customListen);
        if (active) {
          unlisten = cleanup;
        } else {
          cleanup();
        }
      } catch {
        // Event forwarding bridge not available or mock environment
      }
    }

    subscribe();

    return () => {
      active = false;
      if (unlisten) {
        unlisten();
      }
    };
  }, [chapterId, displayMode, fetchProjection, customListen]);

  // 3. Progress Saving Mechanism (W19, AC2)
  const saveProgress = useCallback(
    async (pageId: string, scrollOffsetY: number) => {
      if (!chapterId || !projection) return;
      const now = Date.now();
      const elapsedDelta = (now - lastSaveTimeRef.current) / 1000;

      setIsSaving(true);
      try {
        await readerClient.saveReadingProgress({
          chapterId,
          mode: displayMode,
          pageId,
          scrollOffsetY,
          // Only send elapsedSecondsDelta if positive
          elapsedSecondsDelta: elapsedDelta > 0.5 ? Math.round(elapsedDelta * 10) / 10 : undefined,
        });
        lastSaveTimeRef.current = now;
      } catch {
        // Silent failure or background retry; does not block reading
      } finally {
        if (isMountedRef.current) {
          setIsSaving(false);
        }
      }
    },
    [chapterId, projection, displayMode, readerClient],
  );

  // Debounced progress saver
  const scheduleSave = useCallback(
    (pageId: string, scrollOffsetY: number) => {
      activePositionRef.current = { pageId, scrollOffsetY };
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
      saveTimeoutRef.current = setTimeout(() => {
        saveProgress(pageId, scrollOffsetY);
      }, 800);
    },
    [saveProgress],
  );

  // Flush on unmount or chapter change
  useEffect(() => {
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
      if (activePositionRef.current.pageId) {
        saveProgress(activePositionRef.current.pageId, activePositionRef.current.scrollOffsetY);
      }
    };
  }, [saveProgress]);

  // 4. Mode Switch: Original / Translated (independent progress keys, AC2)
  const handleModeChange = (newMode: ReadingMode) => {
    if (newMode === displayMode) return;
    // Flush current mode progress before switching
    if (activePositionRef.current.pageId) {
      saveProgress(activePositionRef.current.pageId, activePositionRef.current.scrollOffsetY);
    }
    setDisplayMode(newMode);
    // Switching mode re-queries projection to its own saved progress key
  };

  // 5. Start Position Change (resume vs beginning)
  const handleStartPositionChange = (newPos: ReaderStartPosition) => {
    if (newPos === startPosition) return;
    setStartPosition(newPos);
  };

  // 6. Navigation handlers
  const handlePagedChange = (newIndex: number) => {
    if (!projection || newIndex < 0 || newIndex >= projection.pages.length) return;
    setCurrentPageIndex(newIndex);
    const targetPageId = projection.pages[newIndex]?.page_id;
    if (targetPageId) {
      scheduleSave(targetPageId, 0);
    }
  };

  const handleWebtoonScroll = (sourceOffsetY: number, percent: number) => {
    setWebtoonScrollOffsetY(sourceOffsetY);
    setWebtoonPercent(percent);
    const pageId = projection?.pages[0]?.page_id;
    if (pageId) {
      scheduleSave(pageId, sourceOffsetY);
    }
  };

  // 7. Keyboard Navigation (§4.6)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't intercept if user is typing in an input
      if (["INPUT", "TEXTAREA", "SELECT"].includes((e.target as HTMLElement)?.tagName)) {
        return;
      }

      if (e.key === "Escape") {
        e.preventDefault();
        onReturnToBookshelf?.();
        return;
      }

      if (e.key === "o" || e.key === "O") {
        e.preventDefault();
        handleModeChange("original");
        return;
      }

      if (e.key === "t" || e.key === "T" || (e.ctrlKey && e.key.toLowerCase() === "t")) {
        e.preventDefault();
        handleModeChange("translated");
        return;
      }

      if (!projection || projection.pages.length === 0) return;

      const layout = projection.layout;
      const isRtl = layout === "rtl";

      if (layout === "webtoon_vertical") {
        // Webtoon keyboard scrolling
        const container = document.querySelector('[data-testid="webtoon-reader-view"]');
        if (!container) return;

        if (e.key === "ArrowUp") {
          e.preventDefault();
          container.scrollBy({ top: -100, behavior: "smooth" });
        } else if (e.key === "ArrowDown") {
          e.preventDefault();
          container.scrollBy({ top: 100, behavior: "smooth" });
        } else if (e.key === "PageUp") {
          e.preventDefault();
          container.scrollBy({ top: -container.clientHeight * 0.8, behavior: "smooth" });
        } else if (e.key === "PageDown") {
          e.preventDefault();
          container.scrollBy({ top: container.clientHeight * 0.8, behavior: "smooth" });
        } else if (e.key === "Home") {
          e.preventDefault();
          container.scrollTo({ top: 0, behavior: "smooth" });
        } else if (e.key === "End") {
          e.preventDefault();
          container.scrollTo({ top: container.scrollHeight, behavior: "smooth" });
        }
      } else {
        // Paged navigation: Arrow keys & PageUp / PageDown
        if (e.key === "ArrowLeft") {
          e.preventDefault();
          // RTL: ArrowLeft -> Next page; LTR: ArrowLeft -> Prev page
          if (isRtl) {
            handlePagedChange(currentPageIndex + 1);
          } else {
            handlePagedChange(currentPageIndex - 1);
          }
        } else if (e.key === "ArrowRight") {
          e.preventDefault();
          // RTL: ArrowRight -> Prev page; LTR: ArrowRight -> Next page
          if (isRtl) {
            handlePagedChange(currentPageIndex - 1);
          } else {
            handlePagedChange(currentPageIndex + 1);
          }
        } else if (e.key === "PageUp") {
          e.preventDefault();
          handlePagedChange(currentPageIndex - 1);
        } else if (e.key === "PageDown") {
          e.preventDefault();
          handlePagedChange(currentPageIndex + 1);
        } else if (e.key === "Home") {
          e.preventDefault();
          handlePagedChange(0);
        } else if (e.key === "End") {
          e.preventDefault();
          handlePagedChange(projection.pages.length - 1);
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [projection, currentPageIndex, onReturnToBookshelf, handlePagedChange]);

  const resolvePageResourceFn = useCallback(
    (pageId: string) => libraryClient.resolvePageResource(pageId),
    [libraryClient],
  );

  return (
    <div
      data-testid="reader-page"
      style={{
        display: "flex",
        flexDirection: "column",
        width: "100%",
        height: "100%",
        boxSizing: "border-box",
        backgroundColor: tokens.color.bg.app,
        overflow: "hidden",
      }}
    >
      {/* 1. Reader Toolbar (height 48px, §4.2) */}
      <ReaderToolbar
        chapterTitle={chapterTitle}
        chapterId={chapterId}
        bookId={bookId}
        mode={displayMode}
        layout={projection?.layout || "rtl"}
        currentPageIndex={currentPageIndex}
        totalPages={projection?.pages.length || 0}
        webtoonProgressPercent={webtoonPercent}
        startPosition={startPosition}
        onModeChange={handleModeChange}
        onStartPositionChange={handleStartPositionChange}
        onPageChange={handlePagedChange}
        onReturnToBookshelf={onReturnToBookshelf}
        isSaving={isSaving}
      />

      {/* 2. Reader Viewport / Main Content Area */}
      <main
        data-testid="reader-viewport"
        data-webtoon-scroll-offset={webtoonScrollOffsetY}
        style={{
          flex: 1,
          display: "flex",
          position: "relative",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "#161b22",
          color: "#e6edf3",
          overflow: "hidden",
        }}
      >
        {/* State: No chapter selected */}
        {!chapterId && (
          <ReaderEmptyState
            title="尚未选择阅读章节"
            description="请先在书架中选择一个作品及章节，然后点击「进入阅读」"
            onReturnToBookshelf={onReturnToBookshelf}
          />
        )}

        {/* State: Loading projection */}
        {chapterId && loading && !projection && (
          <div
            data-testid="reader-loading"
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              gap: tokens.spacing.md,
              color: tokens.color.text.muted,
            }}
          >
            <div style={{ fontSize: 36 }}>⌛</div>
            <div style={{ fontSize: tokens.typography.size.base }}>正在加载章节阅读数据…</div>
          </div>
        )}

        {/* State: Error loading projection */}
        {chapterId && error && !loading && (
          <div
            data-testid="reader-error"
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              gap: tokens.spacing.sm,
              backgroundColor: tokens.color.surface.card,
              color: tokens.color.text.primary,
              border: `1px solid ${tokens.color.state.failed}`,
              borderRadius: tokens.radius.card,
              padding: tokens.spacing.xl,
              maxWidth: 480,
              textAlign: "center",
              boxShadow: "0 4px 12px rgba(0,0,0,0.4)",
            }}
          >
            <div style={{ fontSize: 36, color: tokens.color.state.failed }}>⚠️</div>
            <div style={{ fontSize: tokens.typography.size.cardTitle, fontWeight: 600 }}>阅读数据加载失败</div>
            <div style={{ fontSize: tokens.typography.size.secondary, color: tokens.color.text.secondary }}>
              错误码: {error}
            </div>
            <button
              type="button"
              data-testid="reader-retry-btn"
              onClick={() => fetchProjection(chapterId, displayMode, startPosition)}
              style={{
                marginTop: tokens.spacing.md,
                padding: "6px 18px",
                fontSize: tokens.typography.size.base,
                backgroundColor: tokens.color.accent.primary,
                color: tokens.color.text.inverse,
                border: "none",
                borderRadius: tokens.radius.button,
                cursor: "pointer",
              }}
            >
              重试
            </button>
          </div>
        )}

        {/* State: Empty pages within chapter */}
        {chapterId && !loading && !error && projection && projection.pages.length === 0 && (
          <ReaderEmptyState
            title="该章节暂无页面"
            description="当前章节未包含任何漫画页面，请先在书架导入页面后再阅读"
            onReturnToBookshelf={onReturnToBookshelf}
          />
        )}

        {/* State: Active Reader View (Paged or Webtoon) */}
        {chapterId && !loading && !error && projection && projection.pages.length > 0 && (
          <>
            {projection.layout === "webtoon_vertical" ? (
              <WebtoonReaderView
                page={projection.pages[0]}
                mode={displayMode}
                resourceClient={resourceClient}
                resolvePageResource={resolvePageResourceFn}
                initialSourceOffsetY={projection.initial_position?.scroll_offset_y || 0}
                onScrollOffsetChange={handleWebtoonScroll}
              />
            ) : (
              <PagedReaderView
                pages={projection.pages}
                currentPageIndex={currentPageIndex}
                layout={projection.layout}
                mode={displayMode}
                resourceClient={resourceClient}
                resolvePageResource={resolvePageResourceFn}
                onPageChange={handlePagedChange}
              />
            )}
          </>
        )}
      </main>
    </div>
  );
}
