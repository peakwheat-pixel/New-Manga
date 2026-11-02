import { ResourceChannelClient } from "../resourceChannel/client";
import { ReaderPageImage } from "./ReaderPageImage";
import type { ReaderLayout, ReaderPageProjection, ReadingMode } from "./types";

export interface PagedReaderViewProps {
  pages: ReaderPageProjection[];
  currentPageIndex: number;
  layout: ReaderLayout; // "rtl" | "ltr"
  mode: ReadingMode;
  resourceClient: ResourceChannelClient;
  resolvePageResource?: (pageId: string) => Promise<{ resource_id: string; revision: string }>;
  onPageChange: (index: number) => void;
}

export function PagedReaderView({
  pages,
  currentPageIndex,
  layout,
  mode,
  resourceClient,
  resolvePageResource,
  onPageChange,
}: PagedReaderViewProps) {
  const isRtl = layout === "rtl";
  const currentPage = pages[currentPageIndex] || null;
  const hasPrev = currentPageIndex > 0;
  const hasNext = currentPageIndex < pages.length - 1;

  const handlePrev = () => {
    if (hasPrev) {
      onPageChange(currentPageIndex - 1);
    }
  };

  const handleNext = () => {
    if (hasNext) {
      onPageChange(currentPageIndex + 1);
    }
  };

  // In RTL: Left is Next, Right is Prev.
  // In LTR: Left is Prev, Right is Next.
  const handleLeftClick = () => {
    if (isRtl) {
      handleNext();
    } else {
      handlePrev();
    }
  };

  const handleRightClick = () => {
    if (isRtl) {
      handlePrev();
    } else {
      handleNext();
    }
  };

  if (!currentPage) {
    return (
      <div
        data-testid="paged-reader-empty"
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          height: "100%",
          color: "#8b949e",
        }}
      >
        该章节暂无页面
      </div>
    );
  }

  return (
    <div
      data-testid="paged-reader-view"
      data-layout={layout}
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        overflow: "auto",
        boxSizing: "border-box",
        padding: 16,
      }}
    >
      {/* Left Click Zone */}
      <button
        type="button"
        data-testid="paged-nav-left"
        onClick={handleLeftClick}
        title={isRtl ? "下一页 (左侧翻页)" : "上一页 (左侧翻页)"}
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          bottom: 0,
          width: "25%",
          background: "transparent",
          border: "none",
          cursor: isRtl ? (hasNext ? "pointer" : "default") : (hasPrev ? "pointer" : "default"),
          zIndex: 4,
          outline: "none",
        }}
        aria-label={isRtl ? "Next page" : "Previous page"}
      />

      {/* Main Single Page Image */}
      <div
        data-testid="paged-page-container"
        data-page-id={currentPage.page_id}
        style={{
          zIndex: 2,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          maxHeight: "100%",
        }}
      >
        <ReaderPageImage
          page={currentPage}
          mode={mode}
          resourceClient={resourceClient}
          resolvePageResource={resolvePageResource}
          style={{ maxHeight: "calc(100vh - 80px)" }}
        />
      </div>

      {/* Right Click Zone */}
      <button
        type="button"
        data-testid="paged-nav-right"
        onClick={handleRightClick}
        title={isRtl ? "上一页 (右侧翻页)" : "下一页 (右侧翻页)"}
        style={{
          position: "absolute",
          right: 0,
          top: 0,
          bottom: 0,
          width: "25%",
          background: "transparent",
          border: "none",
          cursor: isRtl ? (hasPrev ? "pointer" : "default") : (hasNext ? "pointer" : "default"),
          zIndex: 4,
          outline: "none",
        }}
        aria-label={isRtl ? "Previous page" : "Next page"}
      />
    </div>
  );
}
