export interface PagePlaceholderProps {
  pageNumber?: number;
  totalPages?: number;
  chapter?: string;
  className?: string;
}

/**
 * Static 2:3 manga page used by the workbench and reader skeletons. No image
 * request, no remote asset: the page is pure CSS so it renders offline.
 */
export function PagePlaceholder({
  pageNumber = 12,
  totalPages = 24,
  chapter = "第 12 话",
  className,
}: PagePlaceholderProps) {
  return (
    <div
      className={`nm-page-sheet${className ? ` ${className}` : ""}`}
      data-testid="page-placeholder"
      role="img"
      aria-label={`${chapter} 第 ${pageNumber} 页占位`}
    >
      <div className="nm-page-sheet__grain" aria-hidden="true" />
      <div className="nm-page-sheet__running" aria-hidden="true">
        <span>NEW MANGA</span>
        <span>{chapter}</span>
      </div>
      <div className="nm-page-sheet__panels" aria-hidden="true">
        <div className="nm-page-sheet__panel nm-page-sheet__panel--hero">
          <span className="nm-page-sheet__bubble">……</span>
          <span className="nm-page-sheet__speed" />
        </div>
        <div className="nm-page-sheet__panel nm-page-sheet__panel--wide">
          <span className="nm-page-sheet__bubble nm-page-sheet__bubble--small">先别回头。</span>
        </div>
        <div className="nm-page-sheet__panel nm-page-sheet__panel--left" />
        <div className="nm-page-sheet__panel nm-page-sheet__panel--right">
          <span className="nm-page-sheet__bubble nm-page-sheet__bubble--tail">就是这里。</span>
        </div>
      </div>
      <div className="nm-page-sheet__folio" aria-hidden="true">
        {String(pageNumber).padStart(3, "0")} / {String(totalPages).padStart(3, "0")}
      </div>
    </div>
  );
}
