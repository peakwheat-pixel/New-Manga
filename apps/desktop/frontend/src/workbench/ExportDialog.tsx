import { useEffect, useState } from "react";
import type { ExportFormat, ExportFormatOptions, ExportHistoryEntry, ExportSnapshot, StartExportRequest } from "./client";

export interface ExportDialogProps {
  isOpen: boolean;
  bookId: string;
  chapterId: string;
  pageIds: string[];
  snapshot: ExportSnapshot | null;
  history: ExportHistoryEntry[];
  busy?: boolean;
  historyLoading?: boolean;
  error?: string | null;
  onClose: () => void;
  onStart: (request: StartExportRequest) => Promise<boolean>;
  onCancel: () => void;
  onReveal: (exportId: string) => void;
  onRefreshHistory: () => void;
}

const buttonStyle = { border: "1px solid #d9d9d6", borderRadius: 4, padding: "5px 9px", background: "#fff", color: "#1f2328", cursor: "pointer" } as const;

export function ExportDialog({
  isOpen, bookId, chapterId, pageIds, snapshot, history, busy = false, historyLoading = false, error,
  onClose, onStart, onCancel, onReveal, onRefreshHistory,
}: ExportDialogProps) {
  const [format, setFormat] = useState<ExportFormat>("zip");
  const [compression, setCompression] = useState("standard");
  const [pdfContent, setPdfContent] = useState("image_only");
  const [textRepresentation, setTextRepresentation] = useState("markdown");
  const [stalePolicy, setStalePolicy] = useState<"abort" | "continue_existing">("abort");
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    setFormat("zip"); setStalePolicy("abort"); setMessage(null);
    onRefreshHistory();
  }, [isOpen, onRefreshHistory]);

  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape" && !busy) onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, busy, onClose]);

  if (!isOpen) return null;
  let options: ExportFormatOptions = {};
  if (format === "zip") options = { compression };
  if (format === "pdf") options = { pdf_content: pdfContent };
  if (format === "text") options = { text_representation: textRepresentation };
  const startDisabled = busy || pageIds.length === 0 || (format === "png" && pageIds.length !== 1);

  const submit = async () => {
    setMessage(null);
    const accepted = await onStart({
      book_id: bookId, chapter_ids: [chapterId], ordered_page_ids: pageIds,
      format, format_options: options, stale_policy: stalePolicy,
    });
    if (!accepted) setMessage("选择已取消或导出未被接受；可以调整选项后重试。");
  };

  return (
    <div data-testid="export-dialog-backdrop" style={{ position: "fixed", inset: 0, zIndex: 1000, background: "rgba(31,35,40,.35)", display: "flex", alignItems: "center", justifyContent: "center", padding: 16 }}>
      <div role="dialog" aria-modal="true" aria-labelledby="export-title" data-testid="export-dialog" style={{ width: 560, maxHeight: "90vh", overflow: "auto", background: "#fff", color: "#1f2328", border: "1px solid #d9d9d6", borderRadius: 6, padding: 16, display: "flex", flexDirection: "column", gap: 12 }}>
        <header style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <h2 id="export-title" style={{ fontSize: 18, margin: 0, flex: 1 }}>导出页面</h2>
          <button type="button" disabled={busy} onClick={onClose}>关闭</button>
        </header>
        <p style={{ margin: 0, fontSize: 12, color: "#6b7280" }}>已选择 {pageIds.length} 页。保存位置由系统对话框选择，页面不会接收或显示路径。</p>
        <label style={{ display: "grid", gridTemplateColumns: "140px 1fr", alignItems: "center", gap: 8 }}>
          格式
          <select data-testid="export-format" value={format} disabled={busy} onChange={(event) => setFormat(event.target.value as ExportFormat)}>
            <option value="png">PNG（单页）</option><option value="zip">ZIP</option><option value="cbz">CBZ</option><option value="pdf">PDF</option><option value="text">文本</option>
          </select>
        </label>
        {format === "zip" && <label style={{ display: "grid", gridTemplateColumns: "140px 1fr", gap: 8 }}>压缩方式<select value={compression} disabled={busy} onChange={(event) => setCompression(event.target.value)}><option value="standard">标准</option><option value="fast">快速</option><option value="store">不压缩</option></select></label>}
        {format === "pdf" && <label style={{ display: "grid", gridTemplateColumns: "140px 1fr", gap: 8 }}>PDF 内容<select value={pdfContent} disabled={busy} onChange={(event) => setPdfContent(event.target.value)}><option value="image_only">仅图像</option><option value="searchable_dual_layer">可搜索双层</option></select></label>}
        {format === "text" && <label style={{ display: "grid", gridTemplateColumns: "140px 1fr", gap: 8 }}>文本格式<select value={textRepresentation} disabled={busy} onChange={(event) => setTextRepresentation(event.target.value)}><option value="txt">TXT</option><option value="json">JSON</option><option value="markdown">Markdown</option></select></label>}
        <label style={{ display: "grid", gridTemplateColumns: "140px 1fr", gap: 8 }}>过期译文<select value={stalePolicy} disabled={busy} onChange={(event) => setStalePolicy(event.target.value as "abort" | "continue_existing")}><option value="abort">发现过期时停止</option><option value="continue_existing">继续使用现有译文</option></select></label>
        {format === "png" && pageIds.length !== 1 && <p role="status" style={{ margin: 0, color: "#9a6700" }}>PNG 只能导出单页，请把选择集调整为 1 页。</p>}
        {message && <p role="status" data-testid="export-message" style={{ margin: 0 }}>{message}</p>}
        {error && <p role="alert" data-testid="export-error" style={{ margin: 0, color: "#cf222e" }}>导出操作失败：{error}{error === "EXPORT_STALE" && "。请确认后选择“继续使用现有译文”并重新提交。"}</p>}
        {snapshot && <section data-testid="export-current-snapshot" style={{ borderTop: "1px solid #e8e8e4", paddingTop: 8, fontSize: 12 }}>
          <strong>当前导出：{snapshot.status}</strong>
          <progress aria-label="导出进度" max={snapshot.total_pages || 1} value={snapshot.completed_pages} />
          <span>{snapshot.completed_pages} / {snapshot.total_pages}</span>
          {snapshot.error_code && <span> · {snapshot.error_code}</span>}
          {snapshot.status === "completed" && <button data-testid="reveal-export-folder" type="button" style={buttonStyle} onClick={() => onReveal(snapshot.export_id)}>打开所在文件夹</button>}
          {["pending", "running"].includes(snapshot.status) && <button data-testid="cancel-export" type="button" style={buttonStyle} disabled={busy} onClick={onCancel}>取消导出</button>}
        </section>}
        <section data-testid="export-history" style={{ borderTop: "1px solid #e8e8e4", paddingTop: 8 }}>
          <header style={{ display: "flex", alignItems: "center", gap: 8 }}><h3 style={{ fontSize: 14, margin: 0, flex: 1 }}>导出历史</h3><button type="button" onClick={onRefreshHistory}>刷新</button></header>
          {historyLoading && <p role="status" style={{ fontSize: 11 }}>正在读取导出历史…</p>}
          {history.length === 0 ? <p style={{ fontSize: 11, color: "#6b7280" }}>暂无导出记录。</p> : <ul style={{ margin: "6px 0 0", paddingLeft: 20, fontSize: 11 }}>
            {history.map((entry) => <li key={entry.export_id} data-testid={`export-history-${entry.status}`}>
              {entry.format.toUpperCase()} · {entry.status} · {entry.ordered_page_ids.length} 页 · {entry.created_at}
              {entry.sha256 && <span> · SHA-256 {entry.sha256}</span>}
              {entry.status === "completed" && <button type="button" style={buttonStyle} onClick={() => onReveal(entry.export_id)}>打开所在文件夹</button>}
            </li>)}
          </ul>}
        </section>
        <footer style={{ display: "flex", justifyContent: "flex-end", gap: 8 }}>
          <button type="button" style={buttonStyle} disabled={busy} onClick={onClose}>取消</button>
          <button data-testid="start-export" type="button" style={buttonStyle} disabled={startDisabled} onClick={() => { void submit(); }}>{busy ? "正在导出…" : "选择位置并导出"}</button>
        </footer>
      </div>
    </div>
  );
}
