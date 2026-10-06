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
