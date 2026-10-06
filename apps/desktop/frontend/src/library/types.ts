export interface ProtocolVersion {
  major: number;
  minor: number;
}

export interface PingResult {
  status: string;
  protocol_version: ProtocolVersion;
  capabilities: string[];
}

export interface BookSummary {
  book_id: string;
  title: string;
  original_title: string;
  is_favorite: boolean;
  is_archived: boolean;
  /**
   * M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN (frozen None channel):
   * null = unknown/missing data (no qualifying-page row for this book);
   * a counted value stays a number (a KNOWN 0 is distinct from null).
   */
  page_count: number | null;
  created_at: string;
  updated_at: string;
}

export interface LibraryErrorDetail {
  code: string;
  category?: string;
  message?: string;
  retryable?: boolean;
}

/**
 * M2-PAGE-RESOURCE-RESOLVE-1: the servable resource catalog key of one
 * page's immutable managed original (contract M2-C1 rev 1.7 §5). The key
 * is deterministic (`page-original-{page_id}`), so repeated resolves of
 * the same page return the same pair.
 */
export interface PageResourceResolve {
  resource_id: string;
  revision: string;
}

/**
 * M2-PAGE-NAV-PROJECTION-1 (contract M2-C1 rev 1.8 §5): read-only page
 * navigation summaries -- wire projections, not domain entities. Core
 * returns rows already ordered by `sort_order` ascending (D03 AC-PAGE-001);
 * an unknown parent id yields an empty list, never an error.
 * `chapter_number` mirrors the domain string field and may be empty.
 */
export interface ChapterNavSummary {
  chapter_id: string;
  title: string;
  chapter_number: string;
  sort_order: number;
}

export interface PageNavSummary {
  page_id: string;
  source_filename: string;
  sort_order: number;
}
