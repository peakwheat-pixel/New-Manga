import { useEffect, useRef, useState } from "react";
import { ResourceChannelClient } from "../resourceChannel/client";
import { ReaderPageImage } from "./ReaderPageImage";
import type { ReaderPageProjection, ReadingMode } from "./types";

export interface WebtoonReaderViewProps {
  page: ReaderPageProjection;
  mode: ReadingMode;
  resourceClient: ResourceChannelClient;
  resolvePageResource?: (pageId: string) => Promise<{ resource_id: string; revision: string }>;
  initialSourceOffsetY?: number; // Logical page original image pixel coordinate
  onScrollOffsetChange: (sourceOffsetY: number, percent: number) => void;
}

export function WebtoonReaderView({
  page,
  mode,
  resourceClient,
  resolvePageResource,
  initialSourceOffsetY = 0,
  onScrollOffsetChange,
}: WebtoonReaderViewProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const imageWrapperRef = useRef<HTMLDivElement>(null);
  const [restored, setRestored] = useState<boolean>(false);

  // Function to calculate scale: renderedWidth / page.width_px
  const getScale = (): number => {
    if (!imageWrapperRef.current || page.width_px <= 0) return 1;
    const renderedWidth = imageWrapperRef.current.clientWidth;
    return renderedWidth > 0 ? renderedWidth / page.width_px : 1;
  };

  // Restore scroll position once page image has mounted / rendered
  const handleImageLoaded = () => {
    if (restored) return;
    const container = containerRef.current;
    if (!container) return;

    const scale = getScale();
    const targetScrollTop = Math.round(initialSourceOffsetY * scale);
    container.scrollTop = targetScrollTop;
    setRestored(true);
  };

  // Listen to viewport scroll events
  const handleScroll = () => {
    const container = containerRef.current;
    if (!container) return;

    const scale = getScale();
    const scrollTop = container.scrollTop;

    // Convert display coordinate to source-image pixel coordinate (M2-C1 §6.3)
    const sourceOffsetY = Math.max(0, Math.min(page.height_px, Math.round(scrollTop / scale)));
    const percent = page.height_px > 0 ? Math.min(100, Math.max(0, (sourceOffsetY / page.height_px) * 100)) : 0;

    onScrollOffsetChange(sourceOffsetY, percent);
  };

  // Also handle resize to maintain proportional position
  useEffect(() => {
    if (!restored && initialSourceOffsetY > 0) {
      handleImageLoaded();
    }
  }, [restored, initialSourceOffsetY]);

  return (
    <div
      ref={containerRef}
      data-testid="webtoon-reader-view"
      onScroll={handleScroll}
      style={{
        width: "100%",
        height: "100%",
        overflowY: "auto",
        overflowX: "hidden",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        boxSizing: "border-box",
        backgroundColor: "#0d1117",
      }}
    >
      <div
        ref={imageWrapperRef}
        data-testid="webtoon-page-container"
        data-page-id={page.page_id}
        style={{
          width: "100%",
          maxWidth: 960, // Width-fitted webtoon container
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        <ReaderPageImage
          page={page}
          mode={mode}
          resourceClient={resourceClient}
          resolvePageResource={resolvePageResource}
          onLoaded={handleImageLoaded}
          style={{ width: "100%", height: "auto" }}
        />
      </div>
    </div>
  );
}
