import { useCallback, useEffect, useState } from "react";
import { SettingsClient, SettingsClientError } from "./client";
import { projectSettingsError, type SettingsSurfaceError } from "./errors";
import {
  DEFAULT_SFX_POLICY,
  SFX_POLICY_LABELS,
  SFX_POLICY_VALUES,
  type SfxPolicy,
} from "./types";
import { SettingsErrorBar } from "./SettingsErrorBar";
import { tokens } from "../theme/tokens";

/**
 * SFX policy — the ONLY editable key of the existing
 * `settings_update_section` channel opened by P15-C1 §7 (G25): the write is
 * always the whole-section upsert `{"section":"sfx","values":{"policy":v}}`
 * and nothing else in that section is editable from here.
 *
 * AC3/AC4: unset (JSON null) and an empty/set object are distinguished —
 * null renders the "未设置" placeholder with a default-fill action; save
 * failures keep the user's draft (the select keeps its value); saving shows
 * a busy state; load failures show the closed §9 projection with retry.
 */
export function SfxPolicyControl({ client }: { client: SettingsClient }) {
  const [phase, setPhase] = useState<"loading" | "error" | "ready">("loading");
  const [effective, setEffective] = useState<SfxPolicy | null>(null);
  const [unset, setUnset] = useState(false);
  const [draft, setDraft] = useState<SfxPolicy>(DEFAULT_SFX_POLICY);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<SettingsSurfaceError | null>(null);
  const [loadError, setLoadError] = useState<SettingsSurfaceError | null>(null);

  const load = useCallback(async () => {
    setPhase("loading");
    setLoadError(null);
    try {
      const section = await client.getSfxSection();
      setUnset(section === null);
      setEffective(section);
      setDraft(section ?? DEFAULT_SFX_POLICY);
      setPhase("ready");
    } catch (err) {
      const code = err instanceof SettingsClientError ? err.code : String(err);
      setLoadError(projectSettingsError(code, "settings_resolution"));
      setPhase("error");
    }
  }, [client]);

  useEffect(() => {
    void load();
  }, [load]);

  const save = useCallback(
    async (value: SfxPolicy) => {
      setSaving(true);
      setSaveError(null);
      try {
        await client.saveSfxPolicy(value);
        // The write is a whole-section upsert whose success returns the
        // fresh full projection in one round trip; the local effective
        // value is updated from the saved draft (the authoritative read
        // happens on the next load).
        setEffective(value);
        setUnset(false);
      } catch (err) {
        const code = err instanceof SettingsClientError ? err.code : String(err);
        setSaveError(projectSettingsError(code, "settings_resolution"));
        // Draft intentionally NOT reset — user input must survive a failed
        // save (AC4).
      } finally {
        setSaving(false);
      }
    },
    [client],
  );

  const dirty = !unset && draft !== effective;

  return (
    <section
      data-testid="sfx-policy-control"
      style={{
        padding: tokens.spacing.lg,
        backgroundColor: tokens.color.surface.card,
        border: `1px solid ${tokens.color.border.default}`,
        borderRadius: tokens.radius.card,
        maxWidth: 640,
      }}
    >
      <h3
        data-testid="sfx-policy-title"
        style={{
          margin: 0,
          marginBottom: tokens.spacing.sm,
          fontSize: tokens.typography.size.cardTitle,
          fontWeight: 600,
          color: tokens.color.text.primary,
        }}
      >
        SFX 拟声词翻译策略
      </h3>
      <p style={{ margin: 0, marginBottom: tokens.spacing.md, fontSize: tokens.typography.size.secondary, color: tokens.color.text.secondary }}>
        sfx.policy · 三值单选，保存即整节提交；仅对此后新建检出的 Region 生效（既有页面需重新检出）。
      </p>

      {phase === "loading" && (
        <div data-testid="sfx-policy-loading" aria-busy="true" style={{ display: "flex", flexDirection: "column", gap: tokens.spacing.sm }}>
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              style={{ height: 14, borderRadius: tokens.radius.button, background: tokens.color.bg.toolbar, width: `${70 - i * 15}%` }}
            />
          ))}
        </div>
      )}

      {phase === "error" && loadError && (
        <SettingsErrorBar testId="sfx-policy-load-error" error={loadError} onRetry={() => void load()} />
      )}

      {phase === "ready" && (
        <>
          {unset ? (
            <div
              data-testid="sfx-policy-unset"
              style={{
                padding: tokens.spacing.md,
                border: `1px dashed ${tokens.color.border.default}`,
                borderRadius: tokens.radius.button,
                color: tokens.color.text.secondary,
                display: "flex",
                alignItems: "center",
                gap: tokens.spacing.md,
              }}
            >
              <span>该节未设置（Core 返回 JSON null）——当前按 Core 默认值 skip 生效。</span>
              <button
                type="button"
                data-testid="sfx-policy-fill-default-btn"
                disabled={saving}
                onClick={() => void save(DEFAULT_SFX_POLICY)}
                style={{
                  padding: "2px 10px",
                  fontSize: tokens.typography.size.secondary,
                  border: `1px solid ${tokens.color.border.default}`,
                  borderRadius: tokens.radius.button,
                  background: tokens.color.surface.card,
                  color: tokens.color.text.primary,
                  cursor: saving ? "not-allowed" : "pointer",
                }}
              >
                {saving ? "保存中…" : "填充默认值 (skip)"}
              </button>
            </div>
          ) : (
            <div style={{ display: "flex", alignItems: "center", gap: tokens.spacing.md }}>
              <label htmlFor="sfx-policy-select" style={{ fontSize: tokens.typography.size.base }}>
                策略
              </label>
              <select
                id="sfx-policy-select"
                data-testid="sfx-policy-select"
                value={draft}
                disabled={saving}
                onChange={(event) => {
                  const next = event.target.value as SfxPolicy;
                  if (SFX_POLICY_VALUES.includes(next)) {
                    setDraft(next);
                  }
                }}
                style={{
                  padding: "4px 8px",
                  fontSize: tokens.typography.size.base,
                  border: `1px solid ${tokens.color.border.default}`,
                  borderRadius: tokens.radius.button,
                  background: tokens.color.surface.card,
                  color: tokens.color.text.primary,
                }}
              >
                {SFX_POLICY_VALUES.map((value) => (
                  <option key={value} value={value}>
                    {SFX_POLICY_LABELS[value]}
                  </option>
                ))}
              </select>
              <button
                type="button"
                data-testid="sfx-policy-save-btn"
                disabled={saving || !dirty}
                onClick={() => void save(draft)}
                style={{
                  padding: "4px 12px",
                  fontSize: tokens.typography.size.base,
                  border: `1px solid ${dirty && !saving ? tokens.color.accent.primary : tokens.color.border.default}`,
                  borderRadius: tokens.radius.button,
                  background: dirty && !saving ? tokens.color.accent.selected : tokens.color.bg.toolbar,
                  color: tokens.color.text.primary,
                  cursor: saving || !dirty ? "not-allowed" : "pointer",
                  opacity: saving || !dirty ? 0.45 : 1,
                }}
              >
                {saving ? "保存中…" : "保存"}
              </button>
            </div>
          )}

          <div style={{ marginTop: tokens.spacing.md, fontSize: tokens.typography.size.secondary, color: tokens.color.text.secondary }}>
            <div>
              当前生效值：
              <span data-testid="sfx-policy-effective">
                {unset ? "未设置（按默认 skip）" : `${SFX_POLICY_LABELS[effective ?? DEFAULT_SFX_POLICY]}${effective === DEFAULT_SFX_POLICY ? "（默认）" : ""}`}
              </span>
            </div>
          </div>

          {saveError && <div style={{ marginTop: tokens.spacing.md }}><SettingsErrorBar testId="sfx-policy-save-error" error={saveError} /></div>}
        </>
      )}
    </section>
  );
}
