/**
 * Contract M2-C1 rev 2.1 §5 / §6.3:
 * Reader types, projections, and progress snapshots.
 *
 * CRITICAL DISCIPLINE:
 * - No OS filesystem paths, opaque references, or file bytes ever enter Reader DTOs.
 * - Missing translated artifacts are represented by null fields, NEVER by paths or fabricated refs.
 * - Original and Translated reading modes have independent progress keys.
 */

export type ReadingMode = "original" | "translated";

export type ReaderLayout = "rtl" | "ltr" | "webtoon_vertical";

export type ReaderStartPosition = "resume" | "beginning";

export interface ResolvedResourceRef {
  resource_id: string;
  revision: string;
}

export type ResourceRef = ResolvedResourceRef | string;

export interface ReaderPageOriginal {
  resource_ref: ResourceRef;
  artifact_revision_id: string;
  sha256: string;
}

export interface ReaderPageTranslated {
  resource_ref: ResourceRef | null;
  artifact_revision_id: string | null;
  rendered_from_revision_id: string | null;
  current_source_revision_id: string | null;
  sha256: string | null;
}

export interface ReaderPageProjection {
  page_id: string;
  order: number; // 0-based canonical chapter reading order
  width_px: number;
  height_px: number;
  original: ReaderPageOriginal;
  translated: ReaderPageTranslated;
}

export interface ReadingProgressSnapshot {
  book_id: string;
  chapter_id: string;
  mode: ReadingMode;
  last_page_id: string | null;
  scroll_offset_y: number;
  progress_percent: number;
  last_read_at: string | null;
  total_read_seconds: number;
}

export interface ReaderInitialPosition {
  page_id: string;
  scroll_offset_y: number;
}

export interface ReaderProjection {
  book_id: string;
  chapter_id: string;
  mode: ReadingMode;
  layout: ReaderLayout;
  pages: ReaderPageProjection[];
  saved_progress: ReadingProgressSnapshot | null;
  initial_position: ReaderInitialPosition;
}

export interface SaveReadingProgressParams {
  chapterId: string;
  mode: ReadingMode;
  pageId: string;
  scrollOffsetY?: number;
  elapsedSecondsDelta?: number;
}
