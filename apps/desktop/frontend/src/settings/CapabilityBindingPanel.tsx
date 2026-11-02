import { useCallback, useEffect, useState } from "react";
import { SettingsClient, SettingsClientError } from "./client";
import { projectSettingsError, type SettingsSurfaceError } from "./errors";
import { CAPABILITY_VALUES, type BindingScope, type Capability } from "./types";
import { SettingsErrorBar } from "./SettingsErrorBar";
import { tokens } from "../theme/tokens";

/**
 * G21 Capability default-binding panel (P15-C1 §3.2 / G25). Persistent
 * scopes only (global | book | chapter): set / clear are the only write
 * operations — there is no arbitrary property editing. Run-scoped temporary
 * bindings exist ONLY through StartRun.overrides.provider_profiles (never
 * from this page), noted in the panel copy.
 */
type ScopeKind = "global" | "book" | "chapter";

interface BindingDraft {
  scopeKind: ScopeKind;
  scopeId: string;
  capability: Capability;
  profileId: string;
}

export function CapabilityBindingPanel({ client }: { client: SettingsClient }) {
  const [draft, setDraft] = useState<BindingDraft>({
    scopeKind: "global",
    scopeId: "",
    capability: "OCR",
    profileId: "",
  });
  const [currentBinding, setCurrentBinding] = useState<{ profile_id: string | null } | null>(null);
  const [busy, setBusy] = useState<null | "set" | "clear" | "resolve">(null);
  const [error, setError] = useState<SettingsSurfaceError | null>(null);
  const [lastAction, setLastAction] = useState<string | null>(null);

  const scopeDraftError =
    draft.scopeKind === "global" || draft.scopeId.trim() !== ""
      ? null
      : draft.scopeKind === "book"
        ? "book_id 不能为空"
        : "chapter_id 不能为空";

  const buildScope = (): BindingScope | null => {
    if (scopeDraftError) return null;
    if (draft.scopeKind === "global") return { kind: "global" };
    if (draft.scopeKind === "book") return { kind: "book", book_id: draft.scopeId.trim() };
    return { kind: "chapter", chapter_id: draft.scopeId.trim() };
  };

  const resolveCurrent = useCallback(async () => {
    setBusy("resolve");
    setError(null);
    try {
      const resolved = await client.resolveCapabilityBinding(draft.capability);
      setCurrentBinding({ profile_id: resolved.profile_id });
    } catch (err) {
      const code = err instanceof SettingsClientError ? err.code : String(err);
      setError(projectSettingsError(code, "binding"));
      setCurrentBinding(null);
    } finally {
      setBusy(null);
    }
  }, [client, draft.capability]);

  useEffect(() => {
    void resolveCurrent();
  }, [resolveCurrent]);

  const setBinding = async () => {
    const scope = buildScope();
    if (scope === null || draft.profileId === "") return;
    setBusy("set");
    setError(null);
    try {
      await client.setCapabilityBinding(scope, draft.capability, draft.profileId);
      setLastAction(`已绑定 ${draft.capability} → ${draft.profileId}`);
      await resolveCurrent();
    } catch (err) {
      const code = err instanceof SettingsClientError ? err.code : String(err);
      setError(projectSettingsError(code, "binding"));
    } finally {
      setBusy(null);
    }
  };

  const clearBinding = async () => {
    const scope = buildScope();
    if (scope === null) return;
    setBusy("clear");
    setError(null);
    try {
      await client.clearCapabilityBinding(scope, draft.capability);
      setLastAction(`已清除 ${draft.capability} 在该范围的绑定`);
      await resolveCurrent();
    } catch (err) {
      const code = err instanceof SettingsClientError ? err.code : String(err);
      setError(projectSettingsError(code, "binding"));
    } finally {
      setBusy(null);
    }
  };

  const inputStyle: React.CSSProperties = {
    padding: "4px 8px",
    fontSize: tokens.typography.size.base,
    border: `1px solid ${scopeDraftError ? tokens.color.state.failed : tokens.color.border.default}`,
    borderRadius: tokens.radius.button,
    background: tokens.color.surface.card,
    color: tokens.color.text.primary,
  };

  return (
    <section
      data-testid="capability-binding-panel"
      style={{
        padding: tokens.spacing.lg,
        backgroundColor: tokens.color.surface.card,
        border: `1px solid ${tokens.color.border.default}`,
        borderRadius: tokens.radius.card,
        maxWidth: 760,
      }}
    >
      <h3 style={{ margin: 0, marginBottom: tokens.spacing.sm, fontSize: tokens.typography.size.cardTitle, fontWeight: 600, color: tokens.color.text.primary }}>
        Capability 默认绑定
      </h3>
      <p style={{ margin: 0, marginBottom: tokens.spacing.md, fontSize: tokens.typography.size.secondary, color: tokens.color.text.secondary }}>
        解析优先级：当前 Run 临时绑定 → Chapter → Book → Global。Run 临时范围只能经工作台 StartRun.overrides.provider_profiles 设置，不在本页操作。
      </p>

      <div style={{ display: "flex", flexDirection: "column", gap: tokens.spacing.sm, maxWidth: 520 }}>
        <label style={{ fontSize: tokens.typography.size.secondary, display: "flex", flexDirection: "column", gap: 2 }}>
          scope 范围
          <select
            data-testid="binding-form-scope-kind"
            value={draft.scopeKind}
            onChange={(e) => setDraft({ ...draft, scopeKind: e.target.value as ScopeKind })}
            style={inputStyle}
          >
            <option value="global">global（全局）</option>
            <option value="book">book（作品）</option>
            <option value="chapter">chapter（章节）</option>
          </select>
        </label>

        {draft.scopeKind !== "global" && (
          <label style={{ fontSize: tokens.typography.size.secondary, display: "flex", flexDirection: "column", gap: 2 }}>
            {draft.scopeKind === "book" ? "book_id" : "chapter_id"}
            <input
              data-testid="binding-form-scope-id"
              value={draft.scopeId}
              aria-invalid={Boolean(scopeDraftError)}
              onChange={(e) => setDraft({ ...draft, scopeId: e.target.value })}
              onInput={(e) => setDraft({ ...draft, scopeId: (e.target as HTMLInputElement).value })}
              style={inputStyle}
              placeholder={draft.scopeKind === "book" ? "BookId" : "ChapterId"}
            />
          </label>
        )}
        {scopeDraftError && (
          <div data-testid="binding-field-error-scope-id" role="alert" style={{ color: tokens.color.state.failed, fontSize: tokens.typography.size.secondary }}>
            {scopeDraftError}
          </div>
        )}

        <label style={{ fontSize: tokens.typography.size.secondary, display: "flex", flexDirection: "column", gap: 2 }}>
          capability
          <select
            data-testid="binding-form-capability"
            value={draft.capability}
            onChange={(e) => setDraft({ ...draft, capability: e.target.value as Capability })}
            style={inputStyle}
          >
            {CAPABILITY_VALUES.map((capability) => (
              <option key={capability} value={capability}>
                {capability}
              </option>
            ))}
          </select>
        </label>

        <div data-testid="binding-current" style={{ fontSize: tokens.typography.size.base, color: tokens.color.text.secondary }}>
          当前绑定（global 查询）：
          {busy === "resolve" ? "查询中…" : currentBinding === null ? "—" : currentBinding.profile_id === null ? "未绑定" : currentBinding.profile_id}
        </div>

        <label style={{ fontSize: tokens.typography.size.secondary, display: "flex", flexDirection: "column", gap: 2 }}>
          要绑定的 profile_id
          <input
            data-testid="binding-form-profile-id"
            value={draft.profileId}
            onChange={(e) => setDraft({ ...draft, profileId: e.target.value })}
            onInput={(e) => setDraft({ ...draft, profileId: (e.target as HTMLInputElement).value })}
            style={inputStyle}
            placeholder="ProfileId"
          />
        </label>

        <div style={{ display: "flex", gap: tokens.spacing.sm }}>
          <button
            type="button"
            data-testid="binding-set-btn"
            disabled={busy !== null || scopeDraftError !== null || draft.profileId.trim() === ""}
            onClick={() => void setBinding()}
            style={{ padding: "4px 12px", fontSize: tokens.typography.size.base, border: `1px solid ${tokens.color.accent.primary}`, borderRadius: tokens.radius.button, background: tokens.color.accent.selected, color: tokens.color.accent.primary, cursor: busy !== null ? "not-allowed" : "pointer", opacity: busy !== null || scopeDraftError !== null || draft.profileId.trim() === "" ? 0.45 : 1 }}
          >
            {busy === "set" ? "绑定中…" : "设置绑定 (set)"}
          </button>
          <button
            type="button"
            data-testid="binding-clear-btn"
            disabled={busy !== null || scopeDraftError !== null}
            onClick={() => void clearBinding()}
            style={{ padding: "4px 12px", fontSize: tokens.typography.size.base, border: `1px solid ${tokens.color.state.failed}`, borderRadius: tokens.radius.button, background: "#fff1f0", color: tokens.color.state.failed, cursor: busy !== null ? "not-allowed" : "pointer", opacity: busy !== null ? 0.45 : 1 }}
          >
            {busy === "clear" ? "清除中…" : "清除绑定 (clear)"}
          </button>
        </div>

        {lastAction && (
          <div data-testid="binding-last-action" style={{ fontSize: tokens.typography.size.secondary, color: tokens.color.state.completed }}>
            {lastAction}
          </div>
        )}
        {error && <SettingsErrorBar testId="binding-error" error={error} onRetry={() => void resolveCurrent()} />}
      </div>
    </section>
  );
}
