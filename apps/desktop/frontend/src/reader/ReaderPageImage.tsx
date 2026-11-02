import { useEffect, useState } from "react";
import { ResourceChannelClient, TypedChannelError } from "../resourceChannel/client";
import { tokens } from "../theme/tokens";
import type { ReaderPageProjection, ReadingMode, ResourceRef } from "./types";

export interface ReaderPageImageProps {
  page: ReaderPageProjection;
  mode: ReadingMode;
  resourceClient: ResourceChannelClient;
  resolvePageResource?: (pageId: string) => Promise<{ resource_id: string; revision: string }>;
  onLoaded?: () => void;
  style?: React.CSSProperties;
}

function parseResourceRef(ref: ResourceRef | null | undefined): { resourceId: string; revision: string } | null {
  if (!ref) return null;
  if (typeof ref === "object" && ref !== null && "resource_id" in ref && "revision" in ref) {
    return { resourceId: ref.resource_id, revision: ref.revision };
  }
  if (typeof ref === "string" && ref.length > 0) {
    return { resourceId: ref, revision: "original" };
  }
  return null;
}

export function ReaderPageImage({
  page,
  mode,
  resourceClient,
  resolvePageResource,
  onLoaded,
  style,
}: ReaderPageImageProps) {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [retryNonce, setRetryNonce] = useState<number>(0);

  // Check translated artifact status (AC2)
  const isTranslatedMode = mode === "translated";
  const missingTranslation = isTranslatedMode && page.translated.resource_ref === null;
  const isStaleTranslation =
    isTranslatedMode &&
    !missingTranslation &&
    Boolean(page.translated.rendered_from_revision_id) &&
    Boolean(page.translated.current_source_revision_id) &&
    page.translated.rendered_from_revision_id !== page.translated.current_source_revision_id;

  useEffect(() => {
    let active = true;
    let createdUrl: string | null = null;

    setLoading(true);
    setError(null);

    async function fetchImage() {
      try {
        let targetRef: { resourceId: string; revision: string } | null = null;

        if (isTranslatedMode && !missingTranslation) {
          targetRef = parseResourceRef(page.translated.resource_ref);
        }

        // In original mode OR when translated artifact is missing (fallback to original, AC2)
        if (!targetRef) {
          targetRef = parseResourceRef(page.original.resource_ref);
        }

        // If targetRef is still missing, attempt resolve_page_resource fallback
        if (!targetRef && resolvePageResource) {
          const resolved = await resolvePageResource(page.page_id);
          targetRef = { resourceId: resolved.resource_id, revision: resolved.revision };
        }

        if (!targetRef) {
          throw new TypedChannelError("REF_MISSING");
        }

        const issued = await resourceClient.issue(targetRef.resourceId, targetRef.revision);
        if (!active) return;

        const blob = await resourceClient.fetchAll(issued.url, issued.size);
        if (!active) return;

        createdUrl = URL.createObjectURL(blob);
        setImageUrl(createdUrl);
        setLoading(false);
        onLoaded?.();
      } catch (err) {
        if (!active) return;
        setLoading(false);
        const code = err instanceof TypedChannelError ? err.code : (err as Error)?.message || "CHANNEL_ERROR";
        setError(code);
      }
    }

    fetchImage();

    return () => {
      active = false;
      if (createdUrl) {
        URL.revokeObjectURL(createdUrl);
      }
    };
  }, [page.page_id, mode, missingTranslation, page.original, page.translated, resourceClient, resolvePageResource, retryNonce, onLoaded, isTranslatedMode]);

  return (
    <div
      data-testid={`reader-page-image-${page.page_id}`}
      style={{
        position: "relative",
        display: "inline-flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        maxWidth: "100%",
        boxSizing: "border-box",
        ...style,
      }}
    >
      {/* Badges Overlay */}
      <div
        style={{
          position: "absolute",
          top: 8,
          right: 8,
          display: "flex",
          flexDirection: "column",
          gap: 6,
          zIndex: 5,
          pointerEvents: "none",
        }}
      >
        {missingTranslation && (
          <div
            data-testid="badge-missing-translation"
            style={{
              backgroundColor: "rgba(207, 34, 46, 0.85)",
              color: "#ffffff",
              padding: "3px 8px",
              borderRadius: tokens.radius.button,
              fontSize: tokens.typography.size.secondary,
              fontWeight: 600,
              boxShadow: "0 2px 4px rgba(0,0,0,0.3)",
            }}
          >
            未翻译 (回退原文)
          </div>
        )}

        {isStaleTranslation && (
          <div
            data-testid="badge-stale-translation"
            style={{
              backgroundColor: "rgba(154, 103, 0, 0.85)",
              color: "#ffffff",
              padding: "3px 8px",
              borderRadius: tokens.radius.button,
              fontSize: tokens.typography.size.secondary,
              fontWeight: 600,
              boxShadow: "0 2px 4px rgba(0,0,0,0.3)",
            }}
          >
            译文可能过期
          </div>
        )}
      </div>

      {/* Loading Skeleton */}
      {loading && (
        <div
          data-testid="reader-image-loading"
          style={{
            width: "100%",
            minWidth: 320,
            minHeight: 480,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            backgroundColor: "#21262d",
            color: tokens.color.text.muted,
            borderRadius: tokens.radius.card,
          }}
        >
          <div style={{ fontSize: 24, marginBottom: tokens.spacing.sm }}>⌛</div>
          <div style={{ fontSize: tokens.typography.size.base }}>正在加载页面 {page.order + 1}…</div>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div
          data-testid="reader-image-error"
          style={{
            width: "100%",
            minWidth: 320,
            minHeight: 320,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            backgroundColor: "#21262d",
            color: tokens.color.state.failed,
            padding: tokens.spacing.lg,
            borderRadius: tokens.radius.card,
            boxSizing: "border-box",
          }}
        >
          <div style={{ fontSize: 32, marginBottom: tokens.spacing.sm }}>⚠️</div>
          <div style={{ fontWeight: 600, marginBottom: tokens.spacing.xs }}>页面图像加载失败</div>
          <div style={{ fontSize: tokens.typography.size.secondary, color: tokens.color.text.muted, marginBottom: tokens.spacing.md }}>
            错误代码: {error}
          </div>
          <button
            type="button"
            data-testid="reader-image-retry-btn"
            onClick={() => setRetryNonce((n) => n + 1)}
            style={{
              padding: "4px 14px",
              backgroundColor: tokens.color.surface.card,
              color: tokens.color.text.primary,
              border: `1px solid ${tokens.color.border.default}`,
              borderRadius: tokens.radius.button,
              cursor: "pointer",
            }}
          >
            重试
          </button>
        </div>
      )}

      {/* Actual Rendered Image */}
      {imageUrl && !loading && !error && (
        <img
          data-testid="reader-page-img"
          src={imageUrl}
          alt={`Page ${page.order + 1}`}
          style={{
            maxWidth: "100%",
            height: "auto",
            display: "block",
            boxShadow: "0 4px 16px rgba(0,0,0,0.5)",
            borderRadius: 2,
          }}
        />
      )}
    </div>
  );
}
