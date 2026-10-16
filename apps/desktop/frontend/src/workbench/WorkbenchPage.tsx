/**
 * <WorkbenchPage> — first-slice workbench page shell (M2-UI1 §2.2 mapping:
 * QML `WorkbenchView.qml` -> five-zone grid; M2-WORKBENCH-REACT-1 read-face
 * loop).
 *
 * Zone map (design §3.3):
 *   Toolbar | PageListPanel | ViewerPanel(+RegionOverlay) | RegionInspector
 *   | TaskProgressPanel (fixed run projection and controls)
 *
 * Read-face loop closed on EXISTING command faces only:
 * - books via `library_list_books` (LibraryClient);
 * - regions via `list_regions` (RegionClient; rev 1.5 optional
 *   `geometry`/`page_size` consumed when the Core returns them);
 * - page image via `ResolvePageResource` and the existing resource channel
 *   (`loadPageImageUrl`); resource keys stay internal to the component.
 *
 * Retype, revision restore/history and page rerender consume the frozen
 * RC-4 command face; page images continue through the resource channel.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { LibraryClient } from "../library/client";
import type { BookSummary, ChapterNavSummary, PageNavSummary } from "../library/types";
import { RegionClient } from "../region/client";
import type {
  ListRegionRevisionsResult,
  RegionSummary,
  RegionType,
  RevisionSummary,
} from "../region/types";
import { ResourceChannelClient, TypedChannelError } from "../resourceChannel/client";
import { loadPageImageUrl } from "./pageImage";
import { PageListPanel } from "./PageListPanel";
import { ViewerPanel, type RelabelFeedbackState } from "./ViewerPanel";
import { RegionInspector } from "./RegionInspector";
import { TaskProgressPanel } from "./TaskProgressPanel";
import { WorkbenchToolbar } from "./WorkbenchToolbar";
import { RelabelConfirmDialog } from "./RelabelConfirmDialog";
import { planRetypeAction, retypeFeedback } from "./relabelMachine";
import { WorkbenchClient, isSafeUiId, newIdempotencyKey, safeWorkbenchErrorCode, type ExportHistoryEntry, type ExportSnapshot, type PipelineCommand, type PipelineScope, type TaskProjection } from "./client";
import { ExportDialog } from "./ExportDialog";
import { ImportDialog } from "../bookshelf/ImportDialog";
import { onCurrentPageStepChanged, onExportProgressChanged, onRunCompleted, onRunPaused, onTaskFailed, type ListenFn, type UnlistenFn } from "../events";

export type InvokeFn = (command: string, args?: Record<string, unknown>) => Promise<unknown>;

export interface WorkbenchPageProps {
  /** Injectable invoke for tests; defaults to the Tauri bridge. */
  invoke?: InvokeFn;
  /**
   * M2-RESOLVE-DEBOUNCE-1 (PAGE-RESOLVE r1 PR-10): quiet period before the
   * page-resource resolve fires, so typing a page id by hand costs ONE
   * invoke instead of one per keypress. Tests pass 0 to keep the
   * historical immediate timing.
   */
  resolveDebounceMs?: number;
  /**
   * M2-REGION-DEBOUNCE-1 (RESOLVE-DEBOUNCE r1 C-1): same quiet period for
   * the effect-driven region read. Write-refresh paths stay immediate.
   */
  regionDebounceMs?: number;
  bookId?: string | null;
  chapterId?: string | null;
  listen?: ListenFn;
}

interface UndoOffer {
  pageId: string;
  regionId: string;
  previousRevisionNo: number;
  expectedRevision: number;
  hadSuspect: boolean;
  expiresAt: number;
}

interface OperationContext {
  id: number;
  pageId: string;
  pageEpoch: number;
}

function errorCode(error: unknown, fallback: string): string {
  return safeWorkbenchErrorCode(error, fallback);
}

function isSafeFilename(value: unknown): value is string {
  return typeof value === "string" && value.length > 0 && value.length <= 512 && value !== "." && value !== ".." && !/[\\/\0]/.test(value) && !/^[A-Za-z]:/.test(value);
}

export function WorkbenchPage({ invoke, resolveDebounceMs = 300, regionDebounceMs = 300, bookId, chapterId, listen }: WorkbenchPageProps) {
  const [books, setBooks] = useState<BookSummary[]>([]);
  const [booksBusy, setBooksBusy] = useState(true);
  const [booksError, setBooksError] = useState<string | null>(null);
  const [selectedBookId, setSelectedBookId] = useState<string | null>(null);
  // M2-PAGE-NAV-PROJECTION-1: three-level drill-down state (book -> chapter
  // -> page over the read-only navigation projections). Expand/collapse is
  // pure local UI state; Core is never written through this face.
  const [chapters, setChapters] = useState<ChapterNavSummary[]>([]);
  const [chaptersBusy, setChaptersBusy] = useState(false);
  const [chaptersError, setChaptersError] = useState<string | null>(null);
  const [selectedChapterId, setSelectedChapterId] = useState<string | null>(null);
  const [pages, setPages] = useState<PageNavSummary[]>([]);
  const [pagesRefresh, setPagesRefresh] = useState(0);
  const [pagesBusy, setPagesBusy] = useState(false);
  const [pagesError, setPagesError] = useState<string | null>(null);
  const [pageId, setPageId] = useState("");
  const [regions, setRegions] = useState<RegionSummary[]>([]);
  const [pageSize, setPageSize] = useState<{ width: number; height: number } | null>(null);
  const [regionError, setRegionError] = useState<string | null>(null);
  const [selectedRegionId, setSelectedRegionId] = useState<string | null>(null);
  const [resourceId, setResourceId] = useState("");
  const [resourceRevision, setResourceRevision] = useState("current");
  const [resourceResolveBusy, setResourceResolveBusy] = useState(false);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [imageError, setImageError] = useState<string | null>(null);
  // M2-PAGE-RESOURCE-RESOLVE-1: the resolved resource key remains internal
  // and is never rendered as page content or an editable field.
  // ---- IMPL-1 retype/mitigation state ----
  // Pure-UI suspect flags (design R1): never persisted, never sent to Core.
  const [suspects, setSuspects] = useState<Set<string>>(new Set());
  const [confirmTarget, setConfirmTarget] = useState<RegionSummary | null>(null);
  const [busyRegionId, setBusyRegionId] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<RelabelFeedbackState | null>(null);
  const [retypeError, setRetypeError] = useState<string | null>(null);
  const [undoOffer, setUndoOffer] = useState<UndoOffer | null>(null);
  const [actionBusy, setActionBusy] = useState(false);
  const [actionBusyKind, setActionBusyKind] = useState<"retype" | "undo" | "restore" | "rerender" | null>(null);
  const [historyRegionId, setHistoryRegionId] = useState<string | null>(null);
  const [history, setHistory] = useState<ListRegionRevisionsResult | null>(null);
  const [historyBusy, setHistoryBusy] = useState(false);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [restoreError, setRestoreError] = useState<string | null>(null);
  const [selectedPageIds, setSelectedPageIds] = useState<string[]>([]);
  const [selectionAnchor, setSelectionAnchor] = useState<string | null>(null);
  const [pageFilter, setPageFilter] = useState<string | null>(null);
  const [viewerMode, setViewerMode] = useState<"view" | "pan" | "region">("view");
  const [taskProjection, setTaskProjection] = useState<TaskProjection | null>(null);
  const [runSnapshot, setRunSnapshot] = useState<{ run_id: string; command: string; scope: PipelineScope; status: string } | null>(null);
  const [runId, setRunId] = useState<string | null>(null);
  const [runBusy, setRunBusy] = useState(false);
  const [runLoading, setRunLoading] = useState(false);
  const [runError, setRunError] = useState<string | null>(null);
  const [progressCollapsed, setProgressCollapsed] = useState(false);
  const [importOpen, setImportOpen] = useState(false);
  const [exportOpen, setExportOpen] = useState(false);
  const [exportBusy, setExportBusy] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);
  const [exportSnapshot, setExportSnapshot] = useState<ExportSnapshot | null>(null);
  const [exportHistory, setExportHistory] = useState<ExportHistoryEntry[]>([]);
  const [currentExportId, setCurrentExportId] = useState<string | null>(null);
  const [exportHistoryLoading, setExportHistoryLoading] = useState(false);
  const runIdRef = useRef<string | null>(null);
  const taskProjectionRef = useRef<TaskProjection | null>(null);
  const currentExportIdRef = useRef<string | null>(null);
  const pendingRunKeyRef = useRef<{ fingerprint: string; key: string } | null>(null);
  const actionKeysRef = useRef(new Map<string, string>());
  const selectionAnchorRef = useRef<string | null>(null);
  const selectedPageIdsRef = useRef<string[]>([]);

  const pageIdRef = useRef(pageId);
  pageIdRef.current = pageId;
  const selectedRegionIdRef = useRef(selectedRegionId);
  selectedRegionIdRef.current = selectedRegionId;
  const pageEpochRef = useRef(0);
  const regionReadRef = useRef(0);
  const chapterReadRef = useRef(0);
  const pageNavReadRef = useRef(0);
  const historyReadRef = useRef(0);
  const operationRef = useRef(0);
  const actionBusyRef = useRef(false);
  const undoOfferRef = useRef<UndoOffer | null>(null);
  const undoTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const imageUrlRef = useRef<string | null>(null);
  const imageRequestRef = useRef(0);
  const resourceResolveVersionRef = useRef(0);

  const invalidateUndo = useCallback(() => {
    if (undoTimerRef.current !== null) clearTimeout(undoTimerRef.current);
    undoTimerRef.current = null;
    undoOfferRef.current = null;
    setUndoOffer(null);
  }, []);

  const exposeUndo = useCallback((offer: UndoOffer) => {
    if (undoTimerRef.current !== null) clearTimeout(undoTimerRef.current);
    undoOfferRef.current = offer;
    setUndoOffer(offer);
    undoTimerRef.current = setTimeout(() => {
      if (undoOfferRef.current === offer) {
        undoOfferRef.current = null;
        setUndoOffer(null);
      }
      undoTimerRef.current = null;
    }, Math.max(0, offer.expiresAt - Date.now()));
  }, []);

  const beginOperation = useCallback((kind: NonNullable<typeof actionBusyKind>): OperationContext | null => {
    if (actionBusyRef.current) return null;
    actionBusyRef.current = true;
    invalidateUndo();
    setActionBusy(true);
    setActionBusyKind(kind);
    return { id: ++operationRef.current, pageId: pageIdRef.current, pageEpoch: pageEpochRef.current };
  }, [invalidateUndo]);

  const operationIsCurrent = useCallback((operation: OperationContext) =>
    operation.id === operationRef.current &&
    operation.pageEpoch === pageEpochRef.current &&
    operation.pageId === pageIdRef.current,
  []);

  const finishOperation = useCallback((operation: OperationContext) => {
    if (!operationIsCurrent(operation)) return;
    actionBusyRef.current = false;
    setActionBusy(false);
    setActionBusyKind(null);
    setBusyRegionId(null);
  }, [operationIsCurrent]);

  const replaceImageUrl = useCallback((url: string | null) => {
    const previous = imageUrlRef.current;
    imageUrlRef.current = url;
    setImageUrl(url);
    if (previous && previous !== url) URL.revokeObjectURL(previous);
  }, []);

  const clients = useMemo(() => {
    // Clients are cheap; a new one per invoke identity keeps tests honest.
    // Library/Region clients default to the Tauri bridge themselves; the
    // resource client takes an explicit invoke (the same bridge default).
    const tauriInvoke: InvokeFn = invoke
      ? invoke
      : (() => {
          const globalWindow = window as unknown as {
            __TAURI__?: { core?: { invoke: InvokeFn } };
          };
          const found = globalWindow.__TAURI__?.core?.invoke;
          if (!found) {
            throw new Error("TAURI_BRIDGE_MISSING");
          }
          return found;
        })();
    return {
      library: new LibraryClient(invoke),
      region: new RegionClient(invoke),
      resource: new ResourceChannelClient(tauriInvoke),
      workbench: new WorkbenchClient(tauriInvoke),
    };
  }, [invoke]);
  const pendingRunReadsRef = useRef(new Set<string>());
  const refreshRun = useCallback(async (id: string) => {
    if (pendingRunReadsRef.current.has(id)) return;
    pendingRunReadsRef.current.add(id);
    if (!taskProjectionRef.current) setRunLoading(true);
    try {
      const [snapshot, projection] = await Promise.all([
        clients.workbench.getRunSnapshot(id),
        clients.workbench.getTaskProjection(id),
      ]);
      if (snapshot.run_id !== id || projection.run_id !== id) throw new Error("WORKBENCH_RESPONSE_MALFORMED");
      if (runIdRef.current === id) {
        setRunSnapshot(snapshot);
        setTaskProjection(projection);
        setRunError(null);
      }
    } catch (error) {
      if (runIdRef.current === id) setRunError(errorCode(error, "CORE_UNAVAILABLE"));
    } finally {
      pendingRunReadsRef.current.delete(id);
      if (runIdRef.current === id) setRunLoading(false);
    }
  }, [clients]);

  const refreshExportHistory = useCallback(async () => {
    setExportHistoryLoading(true);
    try {
      setExportHistory(await clients.workbench.getExportHistory());
      setExportError(null);
    } catch (error) {
      setExportError(errorCode(error, "CORE_UNAVAILABLE"));
    } finally {
      setExportHistoryLoading(false);
    }
  }, [clients]);

  const refreshExportSnapshot = useCallback(async (id: string) => {
    try {
      const snapshot = await clients.workbench.getExportSnapshot(id);
      if (currentExportIdRef.current === id) {
        setExportSnapshot(snapshot);
        setExportError(null);
      }
      if (["completed", "cancelled", "failed"].includes(snapshot.status)) void refreshExportHistory();
    } catch (error) {
      if (currentExportIdRef.current === id) setExportError(errorCode(error, "CORE_UNAVAILABLE"));
    }
  }, [clients, refreshExportHistory]);

  const handleStartRun = useCallback(async (command: PipelineCommand) => {
    if (!selectedChapterId || runBusy) return;
    let scope: PipelineScope;
    if (command.endsWith("_selected")) {
      if (!selectedPageIds.length) return;
      scope = { kind: "page_selection", page_ids: [...selectedPageIds] };
    } else if (command.endsWith("_single")) {
      if (!pageId.trim()) return;
      scope = { kind: "page", page_id: pageId.trim() };
    } else if (command === "ocr_region" || command.startsWith("retranslate_region") || command === "reinpaint_region" || command === "rerender_region") {
      if (!selectedRegionId) return;
      scope = { kind: "region", region_id: selectedRegionId };
    } else {
      scope = { kind: "chapter", chapter_id: selectedChapterId };
    }
    const fingerprint = JSON.stringify([command, scope]);
    const key = pendingRunKeyRef.current?.fingerprint === fingerprint
      ? pendingRunKeyRef.current.key
      : newIdempotencyKey();
    pendingRunKeyRef.current = { fingerprint, key };
    setRunBusy(true);
    setRunError(null);
    try {
      const accepted = await clients.workbench.startRun(command, scope, key);
      pendingRunKeyRef.current = null;
      runIdRef.current = accepted.run_id;
      setRunId(accepted.run_id);
      setRunSnapshot({ run_id: accepted.run_id, command, scope, status: accepted.status });
      setTaskProjection(null);
      setRunLoading(true);
      await refreshRun(accepted.run_id);
    } catch (error) {
      setRunError(errorCode(error, "CORE_UNAVAILABLE"));
    } finally {
      setRunBusy(false);
    }
  }, [clients, pageId, refreshRun, runBusy, selectedChapterId, selectedPageIds, selectedRegionId]);

  const handleRunControl = useCallback(async (action: "pause" | "stop" | "continue" | "restart" | "abandon") => {
    const id = runIdRef.current;
    if (!id || runBusy) return;
    const keyName = `${id}:${action}`;
    const key = action === "restart" ? (actionKeysRef.current.get(keyName) ?? newIdempotencyKey()) : undefined;
    if (key) actionKeysRef.current.set(keyName, key);
    setRunBusy(true);
    setRunError(null);
    try {
      const result = await clients.workbench.controlRun(id, action, key);
      actionKeysRef.current.delete(keyName);
      if (result.new_run_id) {
        runIdRef.current = result.new_run_id;
        setRunId(result.new_run_id);
        setTaskProjection(null);
        setRunSnapshot({ run_id: result.new_run_id, command: runSnapshot?.command ?? "translate_all", scope: runSnapshot?.scope ?? { kind: "chapter", chapter_id: selectedChapterId ?? "" }, status: result.new_run_status ?? "pending" });
        await refreshRun(result.new_run_id);
      } else {
        await refreshRun(id);
      }
    } catch (error) {
      setRunError(errorCode(error, "CORE_UNAVAILABLE"));
    } finally {
      setRunBusy(false);
    }
  }, [clients, refreshRun, runBusy, runSnapshot, selectedChapterId]);

  const handleResumeBlocked = useCallback(async () => {
    const id = runIdRef.current;
    if (!id || runBusy) return;
    setRunBusy(true); setRunError(null);
    try { await clients.workbench.resumeBlockedRun(id); await refreshRun(id); }
    catch (error) { setRunError(errorCode(error, "CORE_UNAVAILABLE")); }
    finally { setRunBusy(false); }
  }, [clients, refreshRun, runBusy]);

  const handleRetryFailed = useCallback(async () => {
    const id = runIdRef.current;
    if (!id || runBusy) return;
    const keyName = `${id}:retry-failed`;
    const key = actionKeysRef.current.get(keyName) ?? newIdempotencyKey();
    actionKeysRef.current.set(keyName, key);
    setRunBusy(true); setRunError(null);
    try {
      const accepted = await clients.workbench.retryFailedTargets(id, key);
      actionKeysRef.current.delete(keyName);
      runIdRef.current = accepted.run_id;
      setRunId(accepted.run_id); setTaskProjection(null);
      setRunSnapshot({ run_id: accepted.run_id, command: runSnapshot?.command ?? "translate_all", scope: runSnapshot?.scope ?? { kind: "chapter", chapter_id: selectedChapterId ?? "" }, status: accepted.status });
      await refreshRun(accepted.run_id);
    } catch (error) { setRunError(errorCode(error, "CORE_UNAVAILABLE")); }
    finally { setRunBusy(false); }
  }, [clients, refreshRun, runBusy, runSnapshot, selectedChapterId]);

  const handleStartExport = useCallback(async (request: Parameters<WorkbenchClient["startExport"]>[0]) => {
    setExportBusy(true); setExportError(null);
    try {
      const accepted = await clients.workbench.startExport(request);
      if (!accepted) return false;
      currentExportIdRef.current = accepted.export_id;
      setCurrentExportId(accepted.export_id); setExportSnapshot(null);
      await Promise.all([refreshExportSnapshot(accepted.export_id), refreshExportHistory()]);
      return true;
    } catch (error) {
      setExportError(errorCode(error, "CORE_UNAVAILABLE"));
      return false;
    } finally { setExportBusy(false); }
  }, [clients, refreshExportHistory, refreshExportSnapshot]);

  const handleCancelExport = useCallback(async () => {
    const id = currentExportIdRef.current;
    if (!id || exportBusy) return;
    setExportBusy(true); setExportError(null);
    try { setExportSnapshot(await clients.workbench.cancelExport(id)); await refreshExportHistory(); }
    catch (error) { setExportError(errorCode(error, "CORE_UNAVAILABLE")); }
    finally { setExportBusy(false); }
  }, [clients, exportBusy, refreshExportHistory]);

  const handleRevealExport = useCallback(async (id: string) => {
    setExportBusy(true); setExportError(null);
    try { await clients.workbench.revealExportFolder(id); }
    catch (error) { setExportError(errorCode(error, "CORE_UNAVAILABLE")); }
    finally { setExportBusy(false); }
  }, [clients]);

  useEffect(() => {
    let active = true;
    const unlisteners: UnlistenFn[] = [];
    const onRunChanged = (payload: { run_id: string }) => {
      const id = payload?.run_id;
      if (active && typeof id === "string" && id === runIdRef.current) void refreshRun(id);
    };
    const subscribe = async () => {
      const subscriptions = await Promise.allSettled([
        onTaskFailed(onRunChanged, listen),
        onRunPaused(onRunChanged, listen),
        onRunCompleted(onRunChanged, listen),
        onCurrentPageStepChanged(onRunChanged, listen),
        onExportProgressChanged((payload) => {
          if (active && typeof payload?.export_id === "string") void refreshExportSnapshot(payload.export_id);
        }, listen),
      ]);
      for (const subscription of subscriptions) {
        if (subscription.status !== "fulfilled") continue;
        if (active) unlisteners.push(subscription.value);
        else subscription.value();
      }
    };
    void subscribe();
    return () => {
      active = false;
      for (const unlisten of unlisteners) unlisten();
    };
  }, [listen, refreshExportSnapshot, refreshRun]);

  useEffect(() => {
    if (!runId || !["pending", "running"].includes(taskProjection?.run_status ?? runSnapshot?.status ?? "")) return;
    const timer = window.setInterval(() => { void refreshRun(runId); }, 250);
    return () => window.clearInterval(timer);
  }, [runId, runSnapshot?.status, taskProjection?.run_status, refreshRun]);

  useEffect(() => {
    if (!exportSnapshot || !["pending", "running", "publishing"].includes(exportSnapshot.status)) return;
    const timer = window.setInterval(() => { void refreshExportSnapshot(exportSnapshot.export_id); }, 250);
    return () => window.clearInterval(timer);
  }, [exportSnapshot, refreshExportSnapshot]);


  useEffect(() => {
    runIdRef.current = runId;
  }, [runId]);
  useEffect(() => { taskProjectionRef.current = taskProjection; }, [taskProjection]);
  useEffect(() => {
    currentExportIdRef.current = currentExportId;
  }, [currentExportId]);
  useEffect(() => { selectedPageIdsRef.current = selectedPageIds; }, [selectedPageIds]);
  useEffect(() => { selectionAnchorRef.current = selectionAnchor; }, [selectionAnchor]);

  useEffect(() => {
    if (isSafeUiId(bookId)) {
      setSelectedBookId(bookId);
      if (isSafeUiId(chapterId)) setSelectedChapterId(chapterId);
    }
  }, [bookId, chapterId]);

  // Book list via the EXISTING library_list_books projection.
  useEffect(() => {
    let cancelled = false;
    setBooksBusy(true);
    clients.library
      .listBooks()
      .then((rows) => {
        if (!cancelled) {
          const safeRows = rows.filter((row) => isSafeUiId(row.book_id));
          setBooks(safeRows);
          setBooksError(safeRows.length === rows.length ? null : "PAGE_NAV_MALFORMED");
        }
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setBooksError(errorCode(error, "LIBRARY_UNAVAILABLE"));
        }
      })
      .finally(() => {
        if (!cancelled) setBooksBusy(false);
      });
    return () => {
      cancelled = true;
    };
  }, [clients]);

  // M2-PAGE-NAV-PROJECTION-1: chapters of the selected book through the
  // frozen read-only projection. A null selection collapses the drill-down;
  // switching books resets the chapter selection with the list.
  useEffect(() => {
    const signal = { cancelled: false };
    if (!selectedBookId) {
      setChapters([]);
      setChaptersBusy(false);
      setChaptersError(null);
      return;
    }
    const requestId = ++chapterReadRef.current;
    const isCurrent = () => !signal.cancelled && requestId === chapterReadRef.current;
    // DSH r1 PR-06: drop the previous book's rows IMMEDIATELY (not only on
    // the reply). Otherwise the stale rows stay rendered and clickable in
    // the loading window, so a click could re-introduce a dangling
    // selectedChapterId for a chapter that belongs to the OLD book.
    setChapters([]);
    setChaptersBusy(true);
    setChaptersError(null);
    clients.library
      .listChapters(selectedBookId)
      .then((rows) => {
        if (!isCurrent()) return;
        const safeRows = rows.filter((row) => isSafeUiId(row.chapter_id));
        setChapters(safeRows);
        setChaptersBusy(false);
        setChaptersError(safeRows.length === rows.length ? null : "PAGE_NAV_MALFORMED");
      })
      .catch((error: unknown) => {
        if (!isCurrent()) return;
        setChapters([]);
        setChaptersBusy(false);
        setChaptersError(errorCode(error, "PAGE_NAV_UNAVAILABLE"));
      });
    return () => {
      signal.cancelled = true;
    };
  }, [clients, selectedBookId]);

  // M2-PAGE-NAV-PROJECTION-1: pages of the selected chapter (second
  // drill-down level). Clicking a page is handled by the panel through
  // onPageIdChange and joins the existing resolve -> image chain.
  useEffect(() => {
    const signal = { cancelled: false };
    if (!selectedChapterId) {
      setPages([]);
      setPagesBusy(false);
      setPagesError(null);
      return;
    }
    const requestId = ++pageNavReadRef.current;
    const isCurrent = () => !signal.cancelled && requestId === pageNavReadRef.current;
    // Same immediate-drop discipline as the chapter loop above: the old
    // chapter's rows must not stay clickable while the new list loads.
    setPages([]);
    setPagesBusy(true);
    setPagesError(null);
    clients.library
      .listChapterPages(selectedChapterId)
      .then((rows) => {
        if (!isCurrent()) return;
        const safeRows = rows.filter((row) => isSafeUiId(row.page_id) && isSafeFilename(row.source_filename));
        setPages(safeRows);
        setPagesBusy(false);
        setPagesError(safeRows.length === rows.length ? null : "PAGE_NAV_MALFORMED");
      })
      .catch((error: unknown) => {
        if (!isCurrent()) return;
        setPages([]);
        setPagesBusy(false);
        setPagesError(errorCode(error, "PAGE_NAV_UNAVAILABLE"));
      });
    return () => {
      signal.cancelled = true;
    };
  }, [clients, selectedChapterId, pagesRefresh]);

  // Resolve only IDs selected from the projected page list; keep the resource
  // key inside this component and feed it to the existing chunked loader.
  useEffect(() => {
    const trimmed = pageId.trim();
    if (!trimmed) { setResourceResolveBusy(false); return; }
    let cancelled = false;
    const resolveVersion = ++resourceResolveVersionRef.current;
    // Same guard discipline as the region/history/image loops below: the
    // passive-effect cleanup is a later macrotask, so a late resolve reply
    // for a PREVIOUS page can land after the new page's commit and would
    // otherwise feed page-1's key into page-2's viewer.
    const stillCurrent = () => !cancelled && resolveVersion === resourceResolveVersionRef.current && trimmed === pageIdRef.current.trim();
    setResourceResolveBusy(true);
    const fireResolve = () => {
      clients.library
        .resolvePageResource(trimmed)
        .then((resolved) => {
          if (!stillCurrent()) return;
          if (!isSafeUiId(resolved.resource_id) || !isSafeUiId(resolved.revision)) throw new Error("PAGE_RESOURCE_MALFORMED");
          setResourceId(resolved.resource_id);
          setResourceRevision(resolved.revision);
          setResourceResolveBusy(false);
        })
        .catch((error: unknown) => {
          if (!stillCurrent()) return;
          setResourceResolveBusy(false);
          setImageError(errorCode(error, "PAGE_RESOURCE_UNAVAILABLE"));
        });
    };
    let timer: ReturnType<typeof setTimeout> | undefined;
    if (resolveDebounceMs > 0) {
      timer = setTimeout(fireResolve, resolveDebounceMs);
    } else {
      fireResolve();
    }
    return () => {
      cancelled = true;
      if (timer !== undefined) clearTimeout(timer);
    };
  }, [clients, pageId, resolveDebounceMs]);

  // Region read loop via the EXISTING list_regions projection (rev 1.5
  // optional geometry/page_size consumed when present). Retype and restore
  // refresh from Core after writes; UI state never impersonates a revision.
  const refreshRegions = useCallback(
    async (current: string, signal: { cancelled: boolean }): Promise<boolean> => {
      const requestId = ++regionReadRef.current;
      const isCurrent = () =>
        !signal.cancelled &&
        current === pageIdRef.current &&
        requestId === regionReadRef.current;
      const trimmed = current.trim();
      if (!trimmed) {
        if (isCurrent()) {
          setRegions([]);
          setPageSize(null);
          setRegionError(null);
        }
        return isCurrent();
      }
      try {
        const result = await clients.region.listRegions(trimmed);
        if (!isCurrent()) return false;
        setRegions(result.regions.filter((region) => isSafeUiId(region.region_id)));
        setPageSize(result.page_size ?? null);
        setRegionError(null);
        return true;
      } catch (error: unknown) {
        if (!isCurrent()) return false;
        setRegions([]);
        setPageSize(null);
        setRegionError(errorCode(error, "REGION_CHANNEL_UNAVAILABLE"));
        return false;
      }
    },
    [clients],
  );

  useEffect(() => {
    const signal = { cancelled: false };
    // M2-REGION-DEBOUNCE-1 (RESOLVE-DEBOUNCE r1 C-1): same quiet-period
    // treatment as the resolve loop -- typing a page id by hand used to
    // fire one list_regions invoke per keypress. The write-refresh paths
    // (retype/undo/restore) call refreshRegions directly and stay
    // immediate; only this effect-driven read is deferred.
    if (regionDebounceMs > 0) {
      const timer = setTimeout(() => {
        if (!signal.cancelled) void refreshRegions(pageId, signal);
      }, regionDebounceMs);
      return () => {
        signal.cancelled = true;
        clearTimeout(timer);
      };
    }
    refreshRegions(pageId, signal);
    return () => {
      signal.cancelled = true;
    };
  }, [clients, pageId, refreshRegions, regionDebounceMs]);

  // Page image through the EXISTING resource channel, one fresh issue per
  // addressable request.
  useEffect(() => {
    const requestId = ++imageRequestRef.current;
    const requestPage = pageIdRef.current;
    const requestEpoch = pageEpochRef.current;
    const isCurrent = () =>
      requestId === imageRequestRef.current &&
      requestPage === pageIdRef.current &&
      requestEpoch === pageEpochRef.current;
    const trimmedId = resourceId.trim();
    if (!trimmedId) {
      replaceImageUrl(null);
      setImageError(null);
      return;
    }
    let cancelled = false;
    let createdUrl: string | null = null;
    replaceImageUrl(null);
    setImageError(null);
    loadPageImageUrl(clients.resource, trimmedId, resourceRevision.trim() || "current")
      .then((url) => {
        if (cancelled || !isCurrent()) {
          URL.revokeObjectURL(url);
          return;
        }
        createdUrl = url;
        replaceImageUrl(url);
        setImageError(null);
      })
      .catch((error: unknown) => {
        if (cancelled || !isCurrent()) {
          return;
        }
        replaceImageUrl(null);
        // Resource transport has its own typed error surface; show only a stable code.
        const code =
          error instanceof TypedChannelError
            ? error.code
            : (error as { code?: string })?.code;
        setImageError(safeWorkbenchErrorCode({ code }, "RESOURCE_UNAVAILABLE"));
      });
    return () => {
      cancelled = true;
      if (imageRequestRef.current === requestId) imageRequestRef.current += 1;
      if (createdUrl && imageUrlRef.current === createdUrl) {
        URL.revokeObjectURL(createdUrl);
        imageUrlRef.current = null;
      }
    };
  }, [clients, replaceImageUrl, resourceId, resourceRevision]);

  useEffect(() => () => {
    if (undoTimerRef.current !== null) clearTimeout(undoTimerRef.current);
    // RC4-07: after unmount, in-flight image/preview closures must fail
    // their isCurrent checks -- a late preview resolution would otherwise
    // replaceImageUrl a URL that no later cleanup can revoke (permanent
    // object-URL leak).
    imageRequestRef.current += 1;
    operationRef.current += 1;
    if (imageUrlRef.current) URL.revokeObjectURL(imageUrlRef.current);
  }, []);

  const selectedRegion = useMemo(
    () => regions.find((region) => region.region_id === selectedRegionId) ?? null,
    [regions, selectedRegionId],
  );
  const selectedBook = books.find((book) => book.book_id === selectedBookId) ?? null;
  const selectedChapter = chapters.find((chapter) => chapter.chapter_id === selectedChapterId) ?? null;
  const workbenchContext = selectedChapter
    ? `${selectedBook?.title ?? "作品"} · ${selectedChapter.chapter_number ? `#${selectedChapter.chapter_number} · ` : ""}${selectedChapter.title}`
    : selectedBook ? `${selectedBook.title} · 选择章节` : "选择作品与章节";

  const onSelectRegion = useCallback((regionId: string | null) => {
    if (selectedRegionIdRef.current !== regionId) {
      historyReadRef.current += 1;
      setHistoryRegionId(null);
      setHistory(null);
      setHistoryBusy(false);
      setHistoryError(null);
    }
    selectedRegionIdRef.current = regionId;
    setSelectedRegionId(regionId);
  }, []);

  // M2-PAGE-NAV-PROJECTION-1: drill-down selection toggles. Clicking the
  // open book/chapter again collapses that level (local UI state; the
  // effects above own the reads and resets).
  const onSelectBook = useCallback((bookId: string) => {
    setSelectedBookId((current) => (current === bookId ? null : bookId));
    setSelectedChapterId(null);
    setSelectedPageIds([]);
    setPageId("");
  }, []);

  const onSelectChapter = useCallback((chapterId: string) => {
    setSelectedChapterId((current) => (current === chapterId ? null : chapterId));
    setSelectedPageIds([]);
    setPageId("");
    setPageFilter(null);
  }, []);

  const onPageIdChange = useCallback((nextPageId: string) => {
    if (nextPageId.trim() && !isSafeUiId(nextPageId.trim())) {
      setImageError("INVALID_REQUEST");
      return;
    }
    pageIdRef.current = nextPageId;
    pageEpochRef.current += 1;
    regionReadRef.current += 1;
    historyReadRef.current += 1;
    operationRef.current += 1;
    actionBusyRef.current = false;
    invalidateUndo();
    setActionBusy(false);
    setActionBusyKind(null);
    setBusyRegionId(null);
    setConfirmTarget(null);
    setRetypeError(null);
    setFeedback(null);
    setSelectedRegionId(null);
    selectedRegionIdRef.current = null;
    setRegions([]);
    setPageSize(null);
    setRegionError(null);
    setHistoryRegionId(null);
    setHistory(null);
    setHistoryBusy(false);
    setHistoryError(null);
    setRestoreError(null);
    setSuspects(new Set());
    imageRequestRef.current += 1;
    replaceImageUrl(null);
    setImageError(null);
    // Discard the previous page's resource key before the new resolve runs.
    setResourceId("");
    setResourceRevision("current");
    setResourceResolveBusy(false);
    setPageId(nextPageId);
  }, [invalidateUndo, replaceImageUrl]);

  const handlePageSelect = useCallback((nextPageId: string, modifiers?: { ctrlKey: boolean; shiftKey: boolean }) => {
    const pageIndex = pages.findIndex((page) => page.page_id === nextPageId);
    const anchor = selectionAnchorRef.current;
    if (modifiers?.shiftKey && anchor && pageIndex >= 0) {
      const anchorIndex = pages.findIndex((page) => page.page_id === anchor);
      if (anchorIndex >= 0) {
        const [start, end] = [anchorIndex, pageIndex].sort((a, b) => a - b);
        setSelectedPageIds(pages.slice(start, end + 1).map((page) => page.page_id));
      }
    } else if (modifiers?.ctrlKey) {
      const current = selectedPageIdsRef.current;
      setSelectedPageIds(current.includes(nextPageId) ? current.filter((id) => id !== nextPageId) : [...current, nextPageId]);
      setSelectionAnchor(nextPageId);
    } else {
      setSelectedPageIds([nextPageId]);
      setSelectionAnchor(nextPageId);
    }
    onPageIdChange(nextPageId);
  }, [onPageIdChange, pages]);

  const locatePage = useCallback((id: string) => {
    setPageFilter(null);
    setSelectedPageIds([id]); setSelectionAnchor(id);
    onPageIdChange(id);
  }, [onPageIdChange]);

  const handleImportSuccess = useCallback(() => {
    setPagesRefresh((value) => value + 1);
  }, []);

  // ---- IMPL-1 retype flow (design §4.1; A9/A12 enforced via lookups) ----

  /** Pure-UI suspect toggle (R1: no Core call, no revision, A3: the flag
   * itself never triggers anything). */
  const onToggleSuspect = useCallback((regionId: string) => {
    if (actionBusyRef.current) return;
    invalidateUndo();
    setSuspects((prev) => {
      const next = new Set(prev);
      if (next.has(regionId)) {
        next.delete(regionId);
      } else {
        next.add(regionId);
      }
      return next;
    });
  }, [invalidateUndo]);

  const loadHistory = useCallback(async (regionId: string) => {
    const page = pageIdRef.current;
    const epoch = pageEpochRef.current;
    const requestId = ++historyReadRef.current;
    setHistoryRegionId(regionId);
    setHistoryBusy(true);
    setHistoryError(null);
    setRestoreError(null);
    try {
      const result = await clients.region.listRegionRevisions(regionId);
      if (
        requestId !== historyReadRef.current ||
        epoch !== pageEpochRef.current ||
        page !== pageIdRef.current ||
        regionId !== selectedRegionIdRef.current
      ) return null;
      setHistory(result);
      return result;
    } catch (error: unknown) {
      if (
        requestId === historyReadRef.current &&
        epoch === pageEpochRef.current &&
        page === pageIdRef.current &&
        regionId === selectedRegionIdRef.current
      ) {
        setHistory(null);
        setHistoryError(errorCode(error, "REGION_CHANNEL_UNAVAILABLE"));
      }
      return null;
    } finally {
      if (requestId === historyReadRef.current) setHistoryBusy(false);
    }
  }, [clients]);

  const doSetRegionType = useCallback(async (
    region: RegionSummary,
    to: RegionType,
    opts?: { confirmed?: boolean; fromConfirm?: boolean },
  ) => {
    const plan = planRetypeAction(region, to as "sfx" | "speech");
    if (plan.kind === "blocked" || (plan.kind === "confirm" && !opts?.confirmed)) return false;
    const operation = beginOperation("retype");
    if (!operation) return false;
    setBusyRegionId(region.region_id);
    setRetypeError(null);
    const hadSuspect = suspects.has(region.region_id);
    try {
      const result = await clients.region.setRegionType(region.region_id, to, region.revision_no);
      if (!operationIsCurrent(operation)) return false;
      setConfirmTarget(null);
      setFeedback({
        regionId: result.region_id,
        text: retypeFeedback(result.sfx_policy, result.region_type as "sfx" | "speech").text,
        isError: false,
      });
      setSuspects((prev) => {
        if (!prev.has(region.region_id)) return prev;
        const next = new Set(prev);
        next.delete(region.region_id);
        return next;
      });
      exposeUndo({
        pageId: operation.pageId,
        regionId: region.region_id,
        previousRevisionNo: region.revision_no,
        expectedRevision: result.revision_no,
        hadSuspect,
        expiresAt: Date.now() + 10_000,
      });
      await refreshRegions(operation.pageId, { cancelled: false });
      return true;
    } catch (error: unknown) {
      if (!operationIsCurrent(operation)) return false;
      const code = errorCode(error, "REGION_CHANNEL_UNAVAILABLE");
      const message = `改标失败：${code}（region 未变更；冲突后可刷新再操作）`;
      if (opts?.fromConfirm) {
        setRetypeError(message);
      } else {
        setConfirmTarget(null);
        setFeedback({ regionId: region.region_id, text: message, isError: true });
      }
      return false;
    } finally {
      finishOperation(operation);
    }
  }, [beginOperation, clients, exposeUndo, finishOperation, operationIsCurrent, refreshRegions, suspects]);

  const undoRetype = useCallback(async () => {
    const offer = undoOfferRef.current;
    if (!offer) return;
    if (Date.now() >= offer.expiresAt || pageIdRef.current !== offer.pageId || actionBusyRef.current) {
      invalidateUndo();
      return;
    }
    const operation = beginOperation("undo");
    if (!operation) return;
    setBusyRegionId(offer.regionId);
    try {
      const result = await clients.region.restoreRegionRevision(
        offer.regionId,
        offer.previousRevisionNo,
        offer.expectedRevision,
      );
      if (!operationIsCurrent(operation)) return;
      const refreshed = await refreshRegions(operation.pageId, { cancelled: false });
      if (!operationIsCurrent(operation)) return;
      if (refreshed) {
        setSuspects((prev) => {
          const next = new Set(prev);
          if (offer.hadSuspect) next.add(offer.regionId);
          else next.delete(offer.regionId);
          return next;
        });
      }
      setFeedback({
        regionId: offer.regionId,
        text: refreshed
          ? `已撤销改标：新增 restored revision ${result.revision_no}，Core 已恢复改标前状态`
          : `恢复已提交（revision ${result.revision_no}），但当前页刷新失败；请重新读取 region`,
        isError: !refreshed,
      });
      return;
    } catch (error: unknown) {
      if (!operationIsCurrent(operation)) return;
      setFeedback({
        regionId: offer.regionId,
        text: `撤销失败：${errorCode(error, "REGION_CHANNEL_UNAVAILABLE")}（未自动重试）`,
        isError: true,
      });
    } finally {
      finishOperation(operation);
    }
  }, [beginOperation, clients, finishOperation, invalidateUndo, operationIsCurrent, refreshRegions]);

  const restoreHistoryRevision = useCallback(async (revision: RevisionSummary): Promise<boolean> => {
    const regionId = selectedRegionIdRef.current;
    if (!regionId || historyRegionId !== regionId) return false;
    const expectedRevision = history?.current_revision_no;
    if (typeof expectedRevision !== "number" || expectedRevision < 1) {
      setRestoreError("修订历史缺少有效 current revision；请重新读取历史");
      return false;
    }
    const operation = beginOperation("restore");
    if (!operation) return false;
    setRestoreError(null);
    try {
      const result = await clients.region.restoreRegionRevision(
        regionId,
        revision.revision_no,
        expectedRevision,
      );
      if (!operationIsCurrent(operation)) return false;
      const regionsRefreshed = await refreshRegions(operation.pageId, { cancelled: false });
      if (!operationIsCurrent(operation)) return false;
      const refreshedHistory = await loadHistory(regionId);
      if (!operationIsCurrent(operation)) return false;
      setFeedback({
        regionId,
        text: refreshedHistory && regionsRefreshed
          ? `已恢复 revision ${revision.revision_no}；新增 current restored revision ${result.revision_no}`
          : `恢复已提交并新增 revision ${result.revision_no}；Core 刷新未完整完成，请重新读取 region 与历史`,
        isError: !refreshedHistory || !regionsRefreshed,
      });
      return true;
    } catch (error: unknown) {
      if (!operationIsCurrent(operation)) return false;
      setRestoreError(errorCode(error, "REGION_CHANNEL_UNAVAILABLE"));
      return false;
    } finally {
      finishOperation(operation);
    }
  }, [beginOperation, clients, finishOperation, history?.current_revision_no, historyRegionId, loadHistory, operationIsCurrent, refreshRegions]);

  const rerenderPage = useCallback(async () => {
    const page = pageIdRef.current.trim();
    if (!page) return;
    resourceResolveVersionRef.current += 1;
    const operation = beginOperation("rerender");
    if (!operation) return;
    const imageRequestId = ++imageRequestRef.current;
    try {
      const result = await clients.region.rerenderPage(page);
      if (!operationIsCurrent(operation)) return;
      if (imageRequestRef.current !== imageRequestId) {
        setFeedback({
          regionId: selectedRegionIdRef.current ?? "",
          text: `渲染已提交（revision ${result.revision_no}）；保留较新的手动资源选择`,
          isError: false,
        });
        return;
      }
      if (result.preview_error || !result.preview) {
        replaceImageUrl(null);
        setImageError("PREVIEW_UNAVAILABLE");
        setFeedback({
          regionId: selectedRegionIdRef.current ?? "",
          text: `渲染已提交（revision ${result.revision_no}），但预览不可用：PREVIEW_UNAVAILABLE`,
          isError: false,
        });
        return;
      }
      replaceImageUrl(null);
      setImageError(null);
      const previewRequestId = ++imageRequestRef.current;
      try {
        const url = await loadPageImageUrl(
          clients.resource,
          result.preview.resource_id,
          String(result.preview.revision),
        );
        if (!operationIsCurrent(operation) || imageRequestRef.current !== previewRequestId) {
          URL.revokeObjectURL(url);
          return;
        }
        replaceImageUrl(url);
        setImageError(null);
        setFeedback({
          regionId: selectedRegionIdRef.current ?? "",
          text: `本页已重渲染并加载预览（revision ${result.revision_no}）`,
          isError: false,
        });
      } catch (error: unknown) {
        if (!operationIsCurrent(operation) || imageRequestRef.current !== previewRequestId) return;
        replaceImageUrl(null);
        setImageError(errorCode(error, "RESOURCE_UNAVAILABLE"));
        setFeedback({
          regionId: selectedRegionIdRef.current ?? "",
          text: `渲染已提交（revision ${result.revision_no}），但预览读取失败：${errorCode(error, "RESOURCE_UNAVAILABLE")}`,
          isError: false,
        });
      }
    } catch (error: unknown) {
      if (!operationIsCurrent(operation)) return;
      setFeedback({
        regionId: selectedRegionIdRef.current ?? "",
        text: `重渲染失败：${errorCode(error, "REGION_CHANNEL_UNAVAILABLE")}`,
        isError: true,
        showRerenderAction: true,
      });
    } finally {
      finishOperation(operation);
    }
  }, [beginOperation, clients, finishOperation, operationIsCurrent, replaceImageUrl]);

  const onRetypeRequest = useCallback(
    (region: RegionSummary, to: RegionType) => {
      if (actionBusyRef.current) return;
      const plan = planRetypeAction(region, to as "sfx" | "speech");
      if (plan.kind === "blocked") return;
      invalidateUndo();
      setFeedback(null);
      setRetypeError(null);
      if (plan.kind === "confirm") {
        setConfirmTarget(region);
        return;
      }
      void doSetRegionType(region, to);
    },
    [doSetRegionType, invalidateUndo],
  );

  return (
    <div
      data-testid="workbench-page"
      style={{
        display: "flex",
        flexDirection: "column",
        width: "100%",
        height: "100%",
        minWidth: 0,
        minHeight: 0,
        overflow: "hidden",
        background: "#f5f5f4",
        color: "#1f2328",
        fontFamily: 'system-ui, "Segoe UI", "Microsoft YaHei UI", sans-serif',
      }}
    >
      <WorkbenchToolbar
        contextInfo={workbenchContext}
        regionCount={regions.length}
        hasChapter={Boolean(selectedChapterId)}
        selectedPageCount={selectedPageIds.length}
        hasPage={Boolean(pageId.trim())}
        hasRegion={Boolean(selectedRegionId)}
        runBusy={runBusy}
        viewerMode={viewerMode}
        onStartRun={(command) => { void handleStartRun(command); }}
        onOpenImport={() => setImportOpen(true)}
        onOpenExport={() => { setExportError(null); setExportOpen(true); }}
        onSetViewerMode={setViewerMode}
      />
      {(booksError || regionError) && (
        <div data-testid="workbench-error" role="alert" style={{ color: "#cf222e", fontSize: 11, padding: "4px 12px" }}>
          {booksError ? `作品列表读取失败：${booksError}` : `Region 读取失败：${regionError}`}
        </div>
      )}
      <div data-testid="workbench-main-layout" style={{ display: "flex", gap: 8, alignItems: "stretch", flex: 1, minHeight: 0, padding: 8 }}>
        <PageListPanel
          books={books}
          booksBusy={booksBusy}
          booksError={booksError}
          selectedBookId={selectedBookId}
          chapters={chapters}
          chaptersBusy={chaptersBusy}
          chaptersError={chaptersError}
          selectedChapterId={selectedChapterId}
          pages={pages}
          pagesBusy={pagesBusy}
          pagesError={pagesError}
          pageId={pageId}
          onPageIdChange={onPageIdChange}
          onPageSelect={handlePageSelect}
          onSelectBook={onSelectBook}
          onSelectChapter={onSelectChapter}
          selectedPageIds={selectedPageIds}
          taskProjection={taskProjection}
          pageFilter={pageFilter}
          onClearPageFilter={() => setPageFilter(null)}
        />
        <ViewerPanel
          imageUrl={imageUrl}
          imageError={imageError}
          isLoading={resourceResolveBusy}
          regions={regions}
          pageSize={pageSize}
          selectedRegionId={selectedRegionId}
          onSelectRegion={onSelectRegion}
          suspects={suspects}
          relabelFeedback={feedback}
          relabelBusy={actionBusy}
          relabelBusyRegionId={busyRegionId}
          undoAvailable={Boolean(undoOffer && undoOffer.pageId === pageId && Date.now() < undoOffer.expiresAt)}
          rerenderBusy={actionBusy}
          canRerender={Boolean(pageId.trim())}
          onUndo={() => { void undoRetype(); }}
          onRerender={() => { void rerenderPage(); }}
          onRetypeRequest={onRetypeRequest}
          onToggleSuspect={onToggleSuspect}
          viewerMode={viewerMode}
          onSetViewerMode={setViewerMode}
        />
        <div style={{ display: "flex", flexDirection: "column", gap: 8, width: 320, minWidth: 240, maxWidth: 420, flex: "0 0 320px", minHeight: 0, overflow: "auto" }}>
          <RegionInspector
            key={`${pageId}:${selectedRegionId ?? "none"}`}
            region={selectedRegion}
            suspects={suspects}
            busy={actionBusy}
            onRetypeRequest={onRetypeRequest}
            onToggleSuspect={onToggleSuspect}
            revisions={historyRegionId === selectedRegion?.region_id ? history?.revisions ?? null : null}
            currentRevisionNo={historyRegionId === selectedRegion?.region_id ? history?.current_revision_no ?? null : null}
            historyBusy={historyBusy}
            historyError={historyRegionId === selectedRegion?.region_id ? historyError : null}
            restoreBusy={actionBusy && actionBusyKind === "restore"}
            restoreError={restoreError}
            onLoadHistory={(regionId) => { void loadHistory(regionId); }}
            onRestoreRevision={restoreHistoryRevision}
          />
        </div>
      </div>
      <TaskProgressPanel
        projection={taskProjection}
        loading={runLoading}
        busy={runBusy}
        error={runError}
        collapsed={progressCollapsed}
        onToggleCollapsed={() => setProgressCollapsed((value) => !value)}
        onControl={(action) => { void handleRunControl(action); }}
        onResumeBlocked={() => { void handleResumeBlocked(); }}
        onRetryFailed={() => { void handleRetryFailed(); }}
        onFilterStatus={setPageFilter}
        onLocatePage={locatePage}
      />
      <ImportDialog
        isOpen={importOpen}
        books={books}
        chapters={chapters}
        initialBookId={selectedBookId}
        initialChapterId={selectedChapterId}
        client={clients.library}
        onClose={() => setImportOpen(false)}
        onImportSuccess={handleImportSuccess}
      />
      <ExportDialog
        isOpen={exportOpen}
        bookId={selectedBookId ?? ""}
        chapterId={selectedChapterId ?? ""}
        pageIds={selectedPageIds}
        snapshot={exportSnapshot}
        history={exportHistory}
        busy={exportBusy}
        historyLoading={exportHistoryLoading}
        error={exportError}
        onClose={() => setExportOpen(false)}
        onStart={handleStartExport}
        onCancel={() => { void handleCancelExport(); }}
        onReveal={(id) => { void handleRevealExport(id); }}
        onRefreshHistory={refreshExportHistory}
      />
      {confirmTarget && (
        <RelabelConfirmDialog
          target={confirmTarget}
          busy={busyRegionId === confirmTarget.region_id}
          errorText={retypeError}
          onConfirm={() => { void doSetRegionType(confirmTarget, "speech", { confirmed: true, fromConfirm: true }); }}
          onCancel={() => {
            // Guard 2: cancel returns to the originating state — nothing to
            // roll back because nothing was written.
            setConfirmTarget(null);
            setRetypeError(null);
          }}
        />
      )}
    </div>
  );
}
