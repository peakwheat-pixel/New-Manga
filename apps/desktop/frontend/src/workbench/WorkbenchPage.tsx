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
 * Retype write face: RegionClient.setRegionType is callable and unit-pinned
 * at the client layer; the UI interaction consuming it belongs to
 * M2-SFX-MISROUTE-UI-IMPL-1 (this slice keeps only reserved disabled
 * entries).
 */

import { useCallback, useEffect, useMemo, useState } from "react";
import { LibraryClient, LibraryClientError } from "../library/client";
import type { BookSummary } from "../library/types";
import { RegionClient, RegionClientError } from "../region/client";
import type { RegionSummary, RegionType } from "../region/types";
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
  // ---- IMPL-1 retype/mitigation state ----
  // Pure-UI suspect flags (design R1): never persisted, never sent to Core.
  const [suspects, setSuspects] = useState<Set<string>>(new Set());
  const [confirmTarget, setConfirmTarget] = useState<RegionSummary | null>(null);
  const [busyRegionId, setBusyRegionId] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<RelabelFeedbackState | null>(null);
  const [retypeError, setRetypeError] = useState<string | null>(null);

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

  // Region read loop via the EXISTING list_regions projection (rev 1.5
  // optional geometry/page_size consumed when present). Refreshable: the
  // retype flow re-reads after a successful write so the next render works
  // from Core authority (no optimistic region mutation anywhere).
  const refreshRegions = useCallback(
    (current: string, signal: { cancelled: boolean }) => {
      const trimmed = current.trim();
      if (!trimmed) {
        setRegions([]);
        setPageSize(null);
        setRegionError(null);
        return;
      }
      clients.region
        .listRegions(trimmed)
        .then((result) => {
          if (signal.cancelled) {
            return;
          }
          setRegions(result.regions);
          setPageSize(result.page_size ?? null);
          setRegionError(null);
        })
        .catch((error: unknown) => {
          if (signal.cancelled) {
            return;
          }
          setRegions([]);
          setPageSize(null);
          setRegionError(
            error instanceof RegionClientError ? error.code : "REGION_CHANNEL_UNAVAILABLE",
          );
        });
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
    const trimmedId = resourceId.trim();
    if (!trimmedId) {
      setImageUrl(null);
      setImageError(null);
      return;
    }
    let cancelled = false;
    let createdUrl: string | null = null;
    loadPageImageUrl(clients.resource, trimmedId, resourceRevision.trim() || "current")
      .then((url) => {
        if (cancelled) {
          URL.revokeObjectURL(url);
          return;
        }
        createdUrl = url;
        setImageUrl(url);
        setImageError(null);
      })
      .catch((error: unknown) => {
        if (cancelled) {
          return;
        }
        setImageUrl(null);
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
      if (createdUrl) {
        URL.revokeObjectURL(createdUrl);
      }
    };
  }, [clients, resourceId, resourceRevision]);

  const selectedRegion = useMemo(
    () => regions.find((region) => region.region_id === selectedRegionId) ?? null,
    [regions, selectedRegionId],
  );

  const onSelectRegion = useCallback((regionId: string | null) => {
    setSelectedRegionId(regionId);
  }, []);

  // ---- IMPL-1 retype flow (design §4.1; A9/A12 enforced via lookups) ----

  /** Pure-UI suspect toggle (R1: no Core call, no revision, A3: the flag
   * itself never triggers anything). */
  const onToggleSuspect = useCallback((regionId: string) => {
    setSuspects((prev) => {
      const next = new Set(prev);
      if (next.has(regionId)) {
        next.delete(regionId);
      } else {
        next.add(regionId);
      }
      return next;
    });
  }, []);

  const doSetRegionType = useCallback(
    (region: RegionSummary, to: RegionType) => {
      // plan gate: only enabled speech<->sfx transitions reach the wire (A12).
      const plan = planRetypeAction(region, to as "sfx" | "speech");
      if (plan.kind !== "execute" && plan.kind !== "confirm") {
        return;
      }
      setBusyRegionId(region.region_id);
      setRetypeError(null);
      clients.region
        // expected_revision optimistic-guard: the row we rendered from.
        .setRegionType(region.region_id, to, region.revision_no)
        .then((result) => {
          setBusyRegionId(null);
          setConfirmTarget(null);
          setFeedback({
            regionId: result.region_id,
            // The SetRegionType wire contract echoes the requested type; the
            // plan gate above pins it to speech<->sfx before the call.
            text: retypeFeedback(result.sfx_policy, result.region_type as "sfx" | "speech").text,
            isError: false,
          });
          // The warning flag is speech-scoped UI memory: a successful retype
          // re-derives the phase, so drop the flag to keep the set clean.
          setSuspects((prev) => {
            if (!prev.has(region.region_id)) {
              return prev;
            }
            const next = new Set(prev);
            next.delete(region.region_id);
            return next;
          });
          const signal = { cancelled: false };
          refreshRegions(pageId, signal);
        })
        .catch((error: unknown) => {
          // R6: failure returns to the triggering state — regions were never
          // mutated optimistically, and the suspect flag stays untouched, so
          // the warning survives as required.
          setBusyRegionId(null);
          setConfirmTarget(null);
          const code =
            error instanceof RegionClientError
              ? error.code
              : (error as { code?: string })?.code;
          setRetypeError(
            typeof code === "string"
              ? `改标失败：${code}（region 未变更；INPUT_REVISION_CHANGED 时刷新后重试）`
              : "改标失败：region 未变更",
          );
        });
    },
    [clients, pageId, refreshRegions],
  );

  /** Entry dispatcher (§4.1): sfx->speech goes through the explicit confirm
   * dialog (A5); speech->sfx executes immediately (R2). */
  const onRetypeRequest = useCallback(
    (region: RegionSummary, to: RegionType) => {
      const plan = planRetypeAction(region, to as "sfx" | "speech");
      if (plan.kind === "blocked") {
        return;
      }
      setFeedback(null);
      setRetypeError(null);
      if (plan.kind === "confirm") {
        setConfirmTarget(region);
        return;
      }
      doSetRegionType(region, to);
    },
    [doSetRegionType],
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
          onPageIdChange={setPageId}
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
          relabelBusyRegionId={busyRegionId}
          onRetypeRequest={onRetypeRequest}
          onToggleSuspect={onToggleSuspect}
        />
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <RegionInspector
            region={selectedRegion}
            suspects={suspects}
            busy={selectedRegion !== null && busyRegionId === selectedRegion.region_id}
            onRetypeRequest={onRetypeRequest}
            onToggleSuspect={onToggleSuspect}
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
          </section>
        </div>
      </div>
      {confirmTarget && (
        <RelabelConfirmDialog
          target={confirmTarget}
          busy={busyRegionId === confirmTarget.region_id}
          errorText={retypeError}
          onConfirm={() => doSetRegionType(confirmTarget, "speech")}
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
