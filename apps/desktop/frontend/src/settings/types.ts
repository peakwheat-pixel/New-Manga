/**
 * Settings-domain types for the React settings surface
 * (M2-SETTINGS-UI-SFX-POLICY).
 *
 * `sfx.policy` semantics come from M2-SFX-TRANSLATE-ENTRY (verification/
 * M2-SFX-TRANSLATE-ENTRY/integration.md): three values, default SKIP,
 * re-assembled per region — the policy is consumed when a region is
 * created (newly-created regions only; existing regions are never
 * retro-fitted, recovery = re-checkout or a fresh data root).
 */

/** The three SFX translation policies understood by the Python Core. */
export type SfxPolicy = "skip" | "translate" | "manual";

/** All legal values, in display order. The Core fail-fasts on anything else. */
export const SFX_POLICY_VALUES: readonly SfxPolicy[] = ["skip", "translate", "manual"] as const;

/** The Core default when `settings["sfx"]["policy"]` is unset. */
export const DEFAULT_SFX_POLICY: SfxPolicy = "skip";

/** Human-readable labels, following the bilingual style of LibraryPanel. */
export const SFX_POLICY_LABELS: Readonly<Record<SfxPolicy, string>> = {
  skip: "跳过翻译 (skip)",
  translate: "翻译 (translate)",
  manual: "手动处理 (manual)",
};

/** Runtime check for values crossing the IPC boundary (Core is the
 * authority; the UI treats anything unexpected as unset → default). */
export function isSfxPolicy(value: unknown): value is SfxPolicy {
  return (
    value === "skip" || value === "translate" || value === "manual"
  );
}
