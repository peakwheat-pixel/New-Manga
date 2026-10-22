import { useCallback, useEffect, useState, type Dispatch, type SetStateAction } from "react";
import { SettingsClient, SettingsClientError } from "./client";
import { projectSettingsError, type SettingsSurfaceError } from "./errors";

/**
 * SETTINGS-OPEN-A-1 batch A shared section lifecycle — one implementation of
 * the SfxPolicyControl pattern for the four new panels:
 *
 *   load  → `settings_get {section}`; JSON null stays distinguishable and
 *           renders the explicit "未设置" affordance (never an invented value);
 *   save  → `settings_update_section {section, values}` as a whole-section
 *           upsert, then RE-READ the section so the form echoes exactly what
 *           the Core persisted (no optimistic echo);
 *   error → the closed §9 projection only, with retry on load.
 *
 * `defaults` and `normalize` must be module-level constants/functions: they
 * participate in the effect's dependency chain, and a fresh identity per
 * render would re-trigger the initial load.
 */
export type SettingsSectionPhase = "loading" | "error" | "ready";

export interface SettingsSectionController<T> {
  phase: SettingsSectionPhase;
  /** True when the Core returned JSON null for this section. */
  unset: boolean;
  /** Last value read back from the Core (null = section unset). */
  effective: T | null;
  draft: T;
  setDraft: Dispatch<SetStateAction<T>>;
  saving: boolean;
  loadError: SettingsSurfaceError | null;
  saveError: SettingsSurfaceError | null;
  /** Whole-section upsert, followed by a re-read of the same section. */
  save: (values: Record<string, unknown>) => Promise<void>;
  /** Re-run the initial read (used by the load-error retry action). */
  reload: () => Promise<void>;
}

function errorCode(error: unknown): string {
  return error instanceof SettingsClientError ? error.code : String(error);
}

export function useSettingsSection<T>(options: {
  client: SettingsClient;
  section: string;
  defaults: T;
  normalize: (value: unknown) => T;
}): SettingsSectionController<T> {
  const { client, section, defaults, normalize } = options;
  const [phase, setPhase] = useState<SettingsSectionPhase>("loading");
  const [unset, setUnset] = useState(false);
  const [effective, setEffective] = useState<T | null>(null);
  const [draft, setDraft] = useState<T>(defaults);
  const [saving, setSaving] = useState(false);
  const [loadError, setLoadError] = useState<SettingsSurfaceError | null>(null);
  const [saveError, setSaveError] = useState<SettingsSurfaceError | null>(null);

  const readBack = useCallback(async () => {
    const raw = await client.getSection<unknown>(section);
    const stored = raw === null ? null : normalize(raw);
    setUnset(stored === null);
    setEffective(stored);
    setDraft(stored === null ? defaults : stored);
  }, [client, section, defaults, normalize]);

  const reload = useCallback(async () => {
    setPhase("loading");
    setLoadError(null);
    try {
      await readBack();
      setPhase("ready");
    } catch (error) {
      setLoadError(projectSettingsError(errorCode(error), "settings_resolution"));
      setPhase("error");
    }
  }, [readBack]);

  useEffect(() => {
    void reload();
  }, [reload]);

  const save = useCallback(
    async (values: Record<string, unknown>) => {
      setSaving(true);
      setSaveError(null);
      try {
        await client.saveSection(section, values);
        // Re-read: the persisted projection is the only authority for what
        // the form displays after a save (task requires the fresh echo).
        await readBack();
      } catch (error) {
        setSaveError(projectSettingsError(errorCode(error), "settings_resolution"));
        // The draft is intentionally NOT reset — user input survives a
        // failed save, exactly like SfxPolicyControl.
      } finally {
        setSaving(false);
      }
    },
    [client, section, readBack],
  );

  return {
    phase,
    unset,
    effective,
    draft,
    setDraft,
    saving,
    loadError,
    saveError,
    save,
    reload,
  };
}
