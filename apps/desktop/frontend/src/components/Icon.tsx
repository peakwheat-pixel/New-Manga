import type { ReactNode, SVGProps } from "react";

export type IconName =
  | "search"
  | "command"
  | "minus"
  | "maximize"
  | "close"
  | "sun"
  | "moon"
  | "grid"
  | "list"
  | "plus"
  | "upload"
  | "chevron-down"
  | "chevron-left"
  | "chevron-right"
  | "sliders"
  | "book"
  | "tool"
  | "reader"
  | "layers"
  | "type"
  | "image"
  | "wand"
  | "translate"
  | "export"
  | "play"
  | "settings"
  | "more"
  | "panel"
  | "check"
  | "refresh"
  | "zoom-in"
  | "zoom-out"
  | "arrow-left"
  | "filter"
  | "clock"
  | "eye"
  | "sparkles";

const PATHS: Record<IconName, ReactNode> = {
  search: (
    <>
      <circle cx="11" cy="11" r="6.5" />
      <path d="M16 16l4 4" />
    </>
  ),
  command: (
    <>
      <path d="M9 8V6a3 3 0 1 1 3 3H9Zm0 0h6m0 0v6m0 0h2a3 3 0 1 1-3 3v-3Zm0-6H9m0 0v6m0 0h6" />
    </>
  ),
  minus: <path d="M5 12h14" />,
  maximize: <rect x="5.5" y="5.5" width="13" height="13" rx="1" />,
  close: <path d="M6 6l12 12M18 6L6 18" />,
  sun: (
    <>
      <circle cx="12" cy="12" r="4" />
      <path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M18.4 5.6L17 7M7 17l-1.4 1.4" />
    </>
  ),
  moon: <path d="M20 14.2A8.2 8.2 0 0 1 9.8 4a8.3 8.3 0 1 0 10.2 10.2Z" />,
  grid: (
    <>
      <rect x="4" y="4" width="6.5" height="6.5" rx="1" />
      <rect x="13.5" y="4" width="6.5" height="6.5" rx="1" />
      <rect x="4" y="13.5" width="6.5" height="6.5" rx="1" />
      <rect x="13.5" y="13.5" width="6.5" height="6.5" rx="1" />
    </>
  ),
  list: <path d="M5 7h14M5 12h14M5 17h14" />,
  plus: <path d="M12 5v14M5 12h14" />,
  upload: <path d="M12 16V4m0 0L7 9m5-5 5 5M5 16v2.5A1.5 1.5 0 0 0 6.5 20h11a1.5 1.5 0 0 0 1.5-1.5V16" />,
  "chevron-down": <path d="M7 9.5l5 5 5-5" />,
  "chevron-left": <path d="M14.5 7l-5 5 5 5" />,
  "chevron-right": <path d="M9.5 7l5 5-5 5" />,
  sliders: (
    <>
      <path d="M4 8h6M14 8h6M4 16h10M18 16h2" />
      <circle cx="12" cy="8" r="2" />
      <circle cx="16" cy="16" r="2" />
    </>
  ),
  book: <path d="M5 5.5A1.5 1.5 0 0 1 6.5 4H19v15H6.5A1.5 1.5 0 0 0 5 20.5v-15Zm0 15A1.5 1.5 0 0 1 6.5 19H19" />,
  tool: <path d="M14.5 5.5a4 4 0 0 0-5 5L4 16v4h4l5.5-5.5a4 4 0 0 0 5-5l-2.5 2.5-2.5-2.5 2.5-2.5Z" />,
  reader: <path d="M12 6.5C10.5 5 8.3 4.5 5 4.5v13c3.3 0 5.5.5 7 2 1.5-1.5 3.7-2 7-2v-13c-3.3 0-5.5.5-7 2Zm0 0v13" />,
  layers: <path d="M12 4l8 4-8 4-8-4 8-4Zm-8 8 8 4 8-4M4 16l8 4 8-4" />,
  type: <path d="M5 6V4h14v2M12 4v16M8.5 20h7" />,
  image: (
    <>
      <rect x="4" y="5" width="16" height="14" rx="1.5" />
      <circle cx="9" cy="10" r="1.5" />
      <path d="M4.5 17l4.8-4.8 3.2 3.2 2.5-2.5 4.5 4.5" />
    </>
  ),
  wand: <path d="M5 19l9.5-9.5M14 5l1 2 2 1-2 1-1 2-1-2-2-1 2-1 1-2ZM19 13l.7 1.3L21 15l-1.3.7L19 17l-.7-1.3L17 15l1.3-.7L19 13Z" />,
  translate: <path d="M4 6h9M8.5 4v2c0 4-2 6.5-4.5 7.5M6 10c1 2 3 3.5 5 4M13 20l4-10 4 10M14.5 16.5h5" />,
  export: <path d="M12 4v11m0-11L8 8m4-4 4 4M5 15v3.5A1.5 1.5 0 0 0 6.5 20h11a1.5 1.5 0 0 0 1.5-1.5V15" />,
  play: <path d="M8 5.5l10 6.5-10 6.5v-13Z" />,
  settings: (
    <>
      <circle cx="12" cy="12" r="3" />
      <path d="M19 12a7 7 0 0 0-.1-1l2-1.5-2-3.4-2.3 1a7 7 0 0 0-1.7-1L14.5 3h-4l-.4 2.6a7 7 0 0 0-1.7 1l-2.3-1-2 3.4L6 11a7 7 0 0 0 0 2l-2 1.5 2 3.4 2.3-1a7 7 0 0 0 1.7 1l.4 2.6h4l.4-2.6a7 7 0 0 0 1.7-1l2.3 1 2-3.4-2-1.5a7 7 0 0 0 .1-1Z" />
    </>
  ),
  more: (
    <>
      <circle cx="5" cy="12" r="1.2" fill="currentColor" stroke="none" />
      <circle cx="12" cy="12" r="1.2" fill="currentColor" stroke="none" />
      <circle cx="19" cy="12" r="1.2" fill="currentColor" stroke="none" />
    </>
  ),
  panel: (
    <>
      <rect x="4" y="5" width="16" height="14" rx="1.5" />
      <path d="M15 5v14" />
    </>
  ),
  check: <path d="M5 12.5l4.5 4.5L19 7" />,
  refresh: <path d="M19 12a7 7 0 1 1-2.1-5M19 4v4h-4" />,
  "zoom-in": (
    <>
      <circle cx="11" cy="11" r="6.5" />
      <path d="M16 16l4 4M11 8.5v5M8.5 11h5" />
    </>
  ),
  "zoom-out": (
    <>
      <circle cx="11" cy="11" r="6.5" />
      <path d="M16 16l4 4M8.5 11h5" />
    </>
  ),
  "arrow-left": <path d="M19 12H5m0 0l6-6m-6 6 6 6" />,
  filter: <path d="M4 6h16l-6 7v5l-4 2v-7L4 6Z" />,
  clock: (
    <>
      <circle cx="12" cy="12" r="8" />
      <path d="M12 7.5V12l3 2" />
    </>
  ),
  eye: (
    <>
      <path d="M3.5 12S7 6.5 12 6.5 20.5 12 20.5 12 17 17.5 12 17.5 3.5 12 3.5 12Z" />
      <circle cx="12" cy="12" r="2.5" />
    </>
  ),
  sparkles: <path d="M12 4l1.4 4.1L17.5 9.5l-4.1 1.4L12 15l-1.4-4.1L6.5 9.5l4.1-1.4L12 4ZM18.5 15l.8 2.2 2.2.8-2.2.8-.8 2.2-.8-2.2-2.2-.8 2.2-.8.8-2.2Z" />,
};

export interface IconProps extends Omit<SVGProps<SVGSVGElement>, "name" | "width" | "height" | "children"> {
  name: IconName;
  size?: number;
}

export function Icon({ name, size = 16, ...rest }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth={1.6}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
      {...rest}
    >
      {PATHS[name]}
    </svg>
  );
}
