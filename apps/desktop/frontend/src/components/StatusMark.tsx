import "./StatusMark.css";

export type StatusState =
  | "queued"
  | "running"
  | "done"
  | "failed"
  | "blocked"
  | "stale"
  | "skipped"
  | "notStarted";

interface StatusMeta {
  symbol: string;
  label: string;
  className: string;
}

/**
 * Colour + symbol + text, always all three. Emoji are deliberately absent:
 * the glyphs below are geometric shapes with a stable meaning in the data UI.
 */
export const STATUS_META: Record<StatusState, StatusMeta> = {
  queued: { symbol: "·", label: "排队", className: "queued" },
  running: { symbol: "◐", label: "进行中", className: "running" },
  done: { symbol: "●", label: "完成", className: "done" },
  failed: { symbol: "✗", label: "失败", className: "failed" },
  blocked: { symbol: "▲", label: "阻塞", className: "blocked" },
  stale: { symbol: "▨", label: "过期", className: "stale" },
  skipped: { symbol: "–", label: "跳过", className: "skipped" },
  notStarted: { symbol: "○", label: "未开始", className: "not-started" },
};

export interface StatusMarkProps {
  state: StatusState;
  showLabel?: boolean;
  className?: string;
}

export function StatusMark({ state, showLabel = true, className }: StatusMarkProps) {
  const meta = STATUS_META[state];
  return (
    <span
      className={`nm-status nm-status--${meta.className}${className ? ` ${className}` : ""}`}
      data-state={state}
      data-testid={`status-${state}`}
    >
      <span className="nm-status__mark" aria-hidden="true">
        {meta.symbol}
      </span>
      {showLabel ? (
        <span className="nm-status__label">{meta.label}</span>
      ) : (
        <span className="nm-sr-only">{meta.label}</span>
      )}
    </span>
  );
}
