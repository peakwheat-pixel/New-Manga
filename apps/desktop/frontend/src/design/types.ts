export type DesignPage = "shelf" | "workbench" | "reader" | "settings";

export type Theme = "dark" | "light";

export const DESIGN_PAGES: readonly DesignPage[] = ["shelf", "workbench", "reader", "settings"];

export function isDesignPage(value: string | null): value is DesignPage {
  return value === "shelf" || value === "workbench" || value === "reader" || value === "settings";
}
