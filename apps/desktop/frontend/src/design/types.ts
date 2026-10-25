export type DesignPage = "shelf" | "workbench" | "reader";

export type Theme = "dark" | "light";

export const DESIGN_PAGES: readonly DesignPage[] = ["shelf", "workbench", "reader"];

export function isDesignPage(value: string | null): value is DesignPage {
  return value === "shelf" || value === "workbench" || value === "reader";
}
