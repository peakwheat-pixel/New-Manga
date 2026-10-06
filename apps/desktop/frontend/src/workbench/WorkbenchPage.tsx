/**
 * <WorkbenchPage> — first-slice workbench page shell (M2-UI1 §2.2 mapping:
 * QML `WorkbenchView.qml` -> five-zone grid; M2-WORKBENCH-REACT-1 read-face
 * loop).
 *
 * Zone map (mapping-contract names):
 *   Toolbar | PageListPanel | ViewerPanel(+RegionOverlay) | RegionInspector
 *   | TaskProgressPanel (static placeholder)
 *
 * Read-face loop closed on EXISTING command faces only:
 * - books via `library_list_books` (LibraryClient);
 * - regions via `list_regions` (RegionClient; rev 1.5 optional
 *   `geometry`/`page_size` consumed when the Core returns them);
 * - page image via the existing resource channel (`loadPageImageUrl`) when
 *   a resource id + revision is supplied (production page->resource
 *   catalogization is a registered gap).
 *
 * Retype, revision restore/history and page rerender consume the frozen
 * RC-4 command face; page images continue through the resource channel.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { LibraryClient, LibraryClientError } from "../library/client";
import type { BookSummary } from "../library/types";
import { RegionClient, RegionClientError } from "../region/client";
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

export type InvokeFn = (command: string, args?: Record<string, unknown>) => Promise<unknown>;

export interface WorkbenchPageProps {
  /** Injectable invoke for tests; defaults to the Tauri bridge. */
  invoke?: InvokeFn;
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
  if (error instanceof RegionClientError) return error.code;
  if (typeof error === "string") return error;
  const value = error as { code?: unknown; message?: unknown } | null;
  if (typeof value?.code === "string") return value.code;
  if (typeof value?.message === "string") return value.message;
  return fallback;
}

export function WorkbenchPage({ invoke }: WorkbenchPageProps) {
  const [books, setBooks] = useState<BookSummary[]>([]);
  const [booksError, setBooksError] = useState<string | null>(null);
  const [selectedBookId, setSelectedBookId] = useState<string | null>(null);
  const [pageId, setPageId] = useState("");
  const [regions, setRegions] = useState<RegionSummary[]>([]);
  const [pageSize, setPageSize] = useState<{ width: number; height: number } | null>(null);
  const [regionError, setRegionError] = useState<string | null>(null);
  const [selectedRegionId, setSelectedRegionId] = useState<string | null>(null);
  const [resourceId, setResourceId] = useState("");
  const [resourceRevision, setResourceRevision] = useState("current");
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [imageError, setImageError] = useState<string | null>(null);
  // M2-PAGE-RESOURCE-RESOLVE-1: automatic page -> resource resolution; the
  // manual resource inputs stay as the debug fallback (e.g. previews).
  const [resourceResolveBusy, setResourceResolveBusy] = useState(false);
  const [resourceResolveError, setResourceResolveError] = useState<string | null>(null);
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

  const pageIdRef = useRef(pageId);
  pageIdRef.current = pageId;
  const selectedRegionIdRef = useRef(selectedRegionId);
  selectedRegionIdRef.current = selectedRegionId;
  const pageEpochRef = useRef(0);
  const regionReadRef = useRef(0);
  const historyReadRef = useRef(0);
  const operationRef = useRef(0);
  const actionBusyRef = useRef(false);
  const undoOfferRef = useRef<UndoOffer | null>(null);
  const undoTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const imageUrlRef = useRef<string | null>(null);
  const imageRequestRef = useRef(0);

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
    };
  }, [invoke]);

  // Book list via the EXISTING library_list_books projection.
  useEffect(() => {
    let cancelled = false;
    clients.library
      .listBooks()
      .then((rows) => {
        if (!cancelled) {
          setBooks(rows);
          setBooksError(null);
        }
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setBooksError(
            error instanceof LibraryClientError
              ? error.code
              : "LIBRARY_UNAVAILABLE",
          );
        }
      });
    return () => {
      cancelled = true;
    };
  }, [clients]);

  // M2-PAGE-RESOURCE-RESOLVE-1: resolve the page's managed original to its
  // catalog key and feed the existing image loader automatically; the manual
  // resource inputs stay as the debug fallback (a resolve failure leaves
  // them authoritative, so previews still load by hand).
  useEffect(() => {
    const trimmed = pageId.trim();
    if (!trimmed) {
      setResourceResolveBusy(false);
      setResourceResolveError(null);
      return;
    }
    let cancelled = false;
    setResourceResolveBusy(true);
    setResourceResolveError(null);
    clients.library
      .resolvePageResource(trimmed)
      .then((resolved) => {
        if (cancelled) return;
        setResourceId(resolved.resource_id);
        setResourceRevision(resolved.revision);
        setResourceResolveBusy(false);
        setResourceResolveError(null);
      })
      .catch((error: unknown) => {
        if (cancelled) return;
        setResourceResolveBusy(false);
        setResourceResolveError(
          error instanceof LibraryClientError ? error.code : "PAGE_RESOURCE_UNAVAILABLE",
        );
      });
    return () => {
      cancelled = true;
    };
  }, [clients, pageId]);

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
        setRegions(result.regions);
        setPageSize(result.page_size ?? null);
        setRegionError(null);
        return true;
      } catch (error: unknown) {
        if (!isCurrent()) return false;
        setRegions([]);
        setPageSize(null);
        setRegionError(
          error instanceof RegionClientError ? error.code : "REGION_CHANNEL_UNAVAILABLE",
        );
        return false;
      }
    },
    [clients],
  );

  useEffect(() => {
    const signal = { cancelled: false };
    refreshRegions(pageId, signal);
    return () => {
      signal.cancelled = true;
    };
  }, [clients, pageId, refreshRegions]);

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
        // r1 P4-1: the resource channel speaks TypedChannelError (its own
        // typed surface) or a generic code-shaped failure -- never a
        // RegionClientError, which belongs to the region client.
        const code =
          error instanceof TypedChannelError
            ? error.code
            : (error as { code?: string })?.code;
        setImageError(typeof code === "string" ? code : "RESOURCE_UNAVAILABLE");
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

  const onPageIdChange = useCallback((nextPageId: string) => {
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
    // M2-PAGE-RESOURCE-RESOLVE-1: the resolve loop re-runs for the new page
    // and repopulates the resource address; stale manual values must not
    // leak across pages.
    setResourceId("");
    setResourceRevision("current");
    setResourceResolveBusy(false);
    setResourceResolveError(null);
    setPageId(nextPageId);
  }, [invalidateUndo, replaceImageUrl]);

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
        gap: 8,
        marginTop: 12,
        padding: 8,
        border: "1px solid #2a3038",
        borderRadius: 8,
      }}
    >
      <WorkbenchToolbar
        contextInfo={
          pageId.trim()
            ? `page ${pageId.trim()}`
            : selectedBookId
              ? `book ${selectedBookId}`
              : "no context"
        }
        regionCount={regions.length}
      />
      {(booksError || regionError) && (
        <div data-testid="workbench-error" style={{ color: "#e07a7a", fontSize: 11 }}>
          {booksError ? `books: ${booksError}` : `regions: ${regionError}`}
        </div>
      )}
      <div style={{ display: "flex", gap: 8, alignItems: "stretch" }}>
        <PageListPanel
          books={books}
          selectedBookId={selectedBookId}
          pageId={pageId}
          onPageIdChange={onPageIdChange}
          onSelectBook={setSelectedBookId}
        />
        <ViewerPanel
          imageUrl={imageUrl}
          imageError={imageError}
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
        />
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
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
          <TaskProgressPanel />
          <section
            data-testid="resource-address-input"
            style={{
              border: "1px solid #2a3038",
              borderRadius: 6,
              padding: 8,
              display: "flex",
              flexDirection: "column",
              gap: 4,
            }}
          >
            <h2 style={{ fontSize: 12, margin: 0, color: "#d8e0e8" }}>Resource</h2>
            <label style={{ fontSize: 11, color: "#8a94a2" }}>
              resource id
              <input
                data-testid="resource-id-input"
                value={resourceId}
                onChange={(event) => setResourceId(event.target.value)}
                placeholder="resource id…"
                style={{
                  display: "block",
                  width: "100%",
                  background: "#101418",
                  color: "#d8e0e8",
                  border: "1px solid #2a3038",
                  borderRadius: 4,
                  padding: "3px 6px",
                  fontFamily: "Consolas, monospace",
                }}
              />
            </label>
            <label style={{ fontSize: 11, color: "#8a94a2" }}>
              revision
              <input
                data-testid="resource-revision-input"
                value={resourceRevision}
                onChange={(event) => setResourceRevision(event.target.value)}
                style={{
                  display: "block",
                  width: "100%",
                  background: "#101418",
                  color: "#d8e0e8",
                  border: "1px solid #2a3038",
                  borderRadius: 4,
                  padding: "3px 6px",
                  fontFamily: "Consolas, monospace",
                }}
              />
            </label>
            {resourceResolveBusy && (
              <p data-testid="resource-resolve-busy" style={{ margin: 0, fontSize: 11, color: "#8a94a2" }}>
                resolving page resource…
              </p>
            )}
            {resourceResolveError && (
              <p data-testid="resource-resolve-error" style={{ margin: 0, fontSize: 11, color: "#e8a0a0" }}>
                {resourceResolveError}
              </p>
            )}
          </section>
        </div>
      </div>
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
