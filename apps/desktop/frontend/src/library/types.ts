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
  page_count: number;
  created_at: string;
  updated_at: string;
}

export interface LibraryErrorDetail {
  code: string;
  category?: string;
  message?: string;
  retryable?: boolean;
}
