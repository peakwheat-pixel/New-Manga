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

/**
 * HOST-ISSUER-1 / W30: result of library_import_file or library_import_folder.
 * Handled inside host Rust layer; WebView receives the summary report.
 * When user cancels the native dialog, cancelled is true.
 */
export interface ImportSummary {
  chapter_id: string;
  cancelled: boolean;
  imported_files: number;
  skipped_files: number;
  rejected_files: number;
  pending_files: number;
}

/**
 * P09-AC3-DELETE-1 permanent delete payloads and results (contract M2-C1 rev 2.10 §5.11).
 */
export interface PermanentlyDeleteBookPayload {
  book_id: string;
  confirm_permanent_delete: true;
}

export interface PermanentlyDeleteBooksPayload {
  book_ids: string[];
  confirmed_book_ids: string[];
  confirm_count: number;
  confirm_permanent_delete: true;
}

export interface PermanentlyDeleteBookResult {
  book_id: string;
  deleted: boolean;
}

export interface BookDeleteBatchItem {
  book_id: string;
  status: "deleted" | "cleanup_pending" | "not_started";
  error_code: string | null;
}

export interface PermanentlyDeleteBooksResult {
  requested_count: number;
  completed_count: number;
  items: BookDeleteBatchItem[];
}

