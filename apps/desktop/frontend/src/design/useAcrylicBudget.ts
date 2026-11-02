import { useCallback, useMemo } from "react";

/**
 * Performance gate for the faux-acrylic material.
 *
 * A screen may paint at most two backdrop-filter layers at once. The page
 * declares its acrylic layer ids in visual priority order and which one is
 * currently active. When the declared layer count is within budget every
 * layer keeps its blur; when it exceeds the budget only the active layer and
 * the highest-priority remaining layers keep it, and the rest must swap
 * `.nm-acrylic*` for `.nm-acrylic-off` (tint only, no blur, no noise).
 */

export type AcrylicVariant = "acrylic" | "acrylic-24" | "acrylic-strong";

export interface AcrylicBudget {
  /** Layer ids that may keep backdrop-filter. */
  blurred: ReadonlySet<string>;
  /** Number of layers that may keep backdrop-filter (never above budget). */
  blurCount: number;
  /** Whether this layer may keep its blur tier. */
  isBlurred: (id: string) => boolean;
  /**
   * Returns `nm-acrylic`, `nm-acrylic-24` or `nm-acrylic-strong` when the
   * layer is within budget, otherwise `nm-acrylic-off`.
   */
  className: (id: string, variant?: AcrylicVariant, extra?: string) => string;
}

const VARIANT_CLASS: Record<AcrylicVariant, string> = {
  acrylic: "nm-acrylic",
  "acrylic-24": "nm-acrylic-24",
  "acrylic-strong": "nm-acrylic-strong",
};

export function useAcrylicBudget(
  activeId: string | null,
  layers: readonly string[],
  budget = 2,
): AcrylicBudget {
  // Join the ids so an inline array literal does not re-run the calculation
  // on every render.
  const layerKey = layers.join("\u0000");

  const blurred = useMemo(() => {
    // 过滤空 id：调用方偶尔会传 [""]，它会被当成一层真实图层吃掉预算。
    const ids =
      layerKey.length > 0
        ? layerKey.split("\u0000").filter((id) => id.trim().length > 0)
        : [];
    const allowed = new Set<string>();
    if (ids.length <= budget) {
      ids.forEach((id) => allowed.add(id));
      return allowed;
    }
    // Active layer first, then declaration order, up to the budget.
    if (activeId !== null && ids.includes(activeId)) allowed.add(activeId);
    for (const id of ids) {
      if (allowed.size >= budget) break;
      allowed.add(id);
    }
    return allowed;
  }, [activeId, budget, layerKey]);

  const isBlurred = useCallback((id: string) => blurred.has(id), [blurred]);

  const className = useCallback(
    (id: string, variant: AcrylicVariant = "acrylic", extra?: string) => {
      const base = isBlurred(id) ? VARIANT_CLASS[variant] : "nm-acrylic-off";
      return extra ? `${base} ${extra}` : base;
    },
    [isBlurred],
  );

  return { blurred, blurCount: blurred.size, isBlurred, className };
}
