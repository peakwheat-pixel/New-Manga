/**
 * Relabel state-machine pure functions (M2-SFX-MISROUTE-UI-IMPL-1).
 *
 * Design contract `M2-SFX-MISROUTE-UI-MITIGATION` is FROZEN; this module
 * implements ONLY its UI-side derivation and lookup surfaces:
 *
 * - `derivePhase` / `suspectWarningVisible` — §4.1 topology as a pure
 *   derivation of (region row, UI suspect set). The suspect set is a PURE
 *   UI signal (R1: flagging never writes a revision; the initial and only
 *   source is the human user) — its presence never gates relabelability
 *   (A2) and toggling it never triggers a domain change by itself (A3).
 * - `canRetype` — A12: the entry is enabled for speech<->sfx ONLY; every
 *   other transition is disabled WITH an explicit reason.
 * - `sfxBadgeLabel` / `retypeFeedback` — E3/E4 copy are LOOKUP TABLES over
 *   the region's own post-retype policy snapshot returned by Core (A9:
 *   display mapping, never decision logic; the gate authority stays in
 *   `gate.py::decide_sfx_translation`).
 *
 * NOT here (deliberately): any optimistic state mutation, any translation
 * decision, any restore/rerender execution — those are Core authorities or
 * later command-face slices (honest disabled entries in the UI layer).
 */

import type { RegionSummary, RegionType, SfxPolicy } from "../region/types";

/** UI-side phase, derived per design §4.1. SFX_ARB (machine-relabelled sfx)
 * is a topology state whose current READ face cannot distinguish it from a
 * detector-born sfx region (the `sfx-arb-` label prefix is not part of the
 * six-field RegionListSummary) — the derivation therefore never returns it,
 * and the ⧉ machine-pen glyph stays unrenderable until the label/revision
 * channel (RC-4 domain) lands. Registered as an implementation deviation. */
export type RegionPhase =
  | "SPEECH_PLAIN"
  | "SPEECH_SUSPECT"
  | "SFX_TYPE"
  | "OTHER_TYPE";

/**
 * UI suspect flags, keyed by region_id. PURE UI memory: not persisted, not
 * sent to Core, never written as a revision (design R1 / OPEN-2 boundary).
 */
export type SuspectSet = ReadonlySet<string>;

export function derivePhase(
  region: RegionSummary,
  suspects: SuspectSet,
): RegionPhase {
  if (region.region_type === "sfx") {
    // Speech-only warning scope (R-015): suspect flags never colour sfx.
    return "SFX_TYPE";
  }
  if (region.region_type === "speech") {
    return suspects.has(region.region_id) ? "SPEECH_SUSPECT" : "SPEECH_PLAIN";
  }
  return "OTHER_TYPE";
}

/** E1/E2 render gate: warning layers exist ONLY for speech regions the
 * user flagged (R-015 + A2: no OCR/candidate precondition is even consultable
 * here — the flag is the only input). */
export function suspectWarningVisible(
  region: RegionSummary,
  suspects: SuspectSet,
): boolean {
  return region.region_type === "speech" && suspects.has(region.region_id);
}

export interface RetypeEntry {
  enabled: boolean;
  /** Empty when enabled; a user-facing reason when disabled (A12). */
  reason: string;
}

/** A12: retype entries exist for speech<->sfx only. Everything else is
 * disabled and must SAY why (silent enablement of undefined semantics is
 * the red line). */
export function canRetype(region: RegionSummary, to: RegionType): RetypeEntry {
  const from = region.region_type;
  if (from === to) {
    return { enabled: false, reason: `已是 ${from}，无需改标` };
  }
  const speechSfx =
    (from === "speech" && to === "sfx") || (from === "sfx" && to === "speech");
  if (speechSfx) {
    return { enabled: true, reason: "" };
  }
  return {
    enabled: false,
    reason: `仅支持 对白(speech)↔拟声词(sfx) 双向改标；${from} 的改标语义未定义`,
  };
}

export interface SfxBadgeLabel {
  glyph: string;
  text: string;
}

/** E3 pill copy — a lookup of the region's OWN policy snapshot (A9). The
 * machine-pen glyph ⧉ (design §3.4) is NOT emitted here: the read face
 * cannot yet distinguish SFX_ARB from detector-born sfx (see derivePhase). */
export function sfxBadgeLabel(policy: SfxPolicy): SfxBadgeLabel {
  switch (policy) {
    case "translate":
      return { glyph: "♪", text: "SFX · 拟声词翻译链" };
    case "manual":
      // §4.2 row 2: manual judges SKIP at the gate; wording must never
      // claim automatic translation.
      return { glyph: "♪", text: "SFX · 保留原文（手动处理模式）" };
    case "skip":
    default:
      return { glyph: "♪", text: "SFX · 保留原文" };
  }
}

export interface RetypeFeedback {
  text: string;
  /** E4 action offers. Both actions render honestly DISABLED in this
   * slice: Core has no restore/rerender runtime command yet
   * (PROTOCOL_MINOR=3 command face), and simulating undo with a reverse
   * retype violates A6. The buttons exist so the affordance is visible;
   * the title text carries the reason. */
  offerUndo: boolean;
  offerRerender: boolean;
}

/** E4 feedback copy (R4): retype result + the POST-retype policy snapshot
 * semantics (EV-8 CLOSED: retype re-snapshots from the current global
 * config, so translate is reachable) + the "rendered artefact needs a
 * re-render" hint (§1.3 key boundary / §4.4). */
export function retypeFeedback(
  postPolicy: SfxPolicy,
  newType: "sfx" | "speech" = "sfx",
): RetypeFeedback {
  // §4.4 / §4.3-4 (FROZEN): the relabel does NOT erase an already-rendered
  // translation — every feedback copy states the artefact boundary so the
  // user can read "original intact; the rendered page needs a re-render".
  // (The reader-projection has no artefact field yet, so the line is
  // unconditional — the conservative, more-informative direction.)
  const ARTEFACT_NOTE = "原图完好；已渲染成品图需重跑渲染才恢复原文";
  if (newType === "speech") {
    return {
      text: `已改回对白（speech）——该区域将按对白链翻译，可能产生新的译文；${ARTEFACT_NOTE}`,
      offerUndo: true,
      offerRerender: true,
    };
  }
  switch (postPolicy) {
    case "translate":
      return {
        text: `已标记为拟声词（SFX · 拟声词翻译链）——将按拟声词翻译链重新翻译；${ARTEFACT_NOTE}`,
        offerUndo: true,
        offerRerender: true,
      };
    case "manual":
      return {
        text: `已标记为拟声词——保留原文（手动处理模式），不再自动翻译；${ARTEFACT_NOTE}`,
        offerUndo: true,
        offerRerender: true,
      };
    case "skip":
    default:
      return {
        text: `已标记为拟声词（SFX · 保留原文）——按当前策略保留原文，不再翻译；${ARTEFACT_NOTE}`,
        offerUndo: true,
        offerRerender: true,
      };
  }
}

/** Flow decision (§4.1 entry dispatch, the ONLY branch logic the component
 * handler replays): forward speech->sfx executes immediately (R2), reverse
 * sfx->speech must route through the explicit confirm dialog (R3/A5), and
 * any disabled transition is blocked before any state moves (A12). */
export type RetypePlan =
  | { kind: "execute" }
  | { kind: "confirm" }
  | { kind: "blocked"; reason: string };

export function planRetypeAction(region: RegionSummary, to: "sfx" | "speech"): RetypePlan {
  const guard = canRetype(region, to);
  if (!guard.enabled) {
    return { kind: "blocked", reason: guard.reason };
  }
  return to === "speech" ? { kind: "confirm" } : { kind: "execute" };
}

/** Fixed copy (design §4.3): the user must be able to read, at all times,
 * that relabelling only edits annotations and never touches source files. */
export const RELABEL_SOURCE_SAFETY_NOTE = "改标只修改标注，不改动原图文件";

/** Reverse-retype confirmation copy (R3 / A5: explicit confirmation step
 * stating the consequence — re-entering the speech chain may produce new
 * translations). */
export const RELABEL_X2S_CONFIRM_TEXT =
  "该区域将改回对白（speech）并重新进入对白翻译链，可能产生新的译文";

/** Honest-disabled reasons for the E4 action buttons (registered deviation:
 * restore/rerender runtime commands are outside PROTOCOL_MINOR=3). */
export const UNDO_DISABLED_TITLE =
  "撤销走 revision 恢复（Core restore 命令待后续命令面 Task；不得以反向改标模拟撤销）";
export const RERENDER_DISABLED_TITLE =
  "重渲染 run 通道 runtime 未实现（契约 §5.1 PROPOSAL 层）";
