/**
 * Relabel state-machine unit tests (M2-SFX-MISROUTE-UI-IMPL-1 AC3/AC4).
 *
 * The design contract `M2-SFX-MISROUTE-UI-MITIGATION` §4.1 freezes the
 * state topology and §6 freezes assertions A2/A4/A5/A8/A9/A12; these tests
 * pin the UI-side pure functions against those frozen semantics:
 * phase derivation, the E3/E4 lookup tables (display mapping only -- A9),
 * entry enablement (A12: speech<->sfx only, others disabled WITH a reason),
 * and the suspect-set guard rules (A2/A3: warning presence never gates
 * relabelability nor triggers domain changes by itself).
 */

import { describe, expect, it } from "vitest";
import {
  canRetype,
  derivePhase,
  planRetypeAction,
  retypeFeedback,
  sfxBadgeLabel,
  suspectWarningVisible,
  type RegionPhase,
} from "./relabelMachine";
import type { RegionSummary } from "../region/types";

function makeRegion(overrides: Partial<RegionSummary> = {}): RegionSummary {
  return {
    region_id: "rg-1",
    region_type: "speech",
    sfx_policy: "skip",
    origin: "machine",
    revision_no: 3,
    ...overrides,
  };
}

describe("derivePhase (design §4.1 topology, UI-side derivation)", () => {
  it("speech without suspect flag -> SPEECH_PLAIN", () => {
    expect(derivePhase(makeRegion(), new Set())).toBe<RegionPhase>("SPEECH_PLAIN");
  });

  it("speech with suspect flag -> SPEECH_SUSPECT", () => {
    expect(derivePhase(makeRegion(), new Set(["rg-1"]))).toBe("SPEECH_SUSPECT");
  });

  it("sfx -> SFX_TYPE regardless of suspect flags (warning is speech-only, R-015)", () => {
    expect(derivePhase(makeRegion({ region_type: "sfx" }), new Set(["rg-1"]))).toBe(
      "SFX_TYPE",
    );
  });

  it("narration/title/note/other -> OTHER_TYPE (outside the machine, entries disabled A12)", () => {
    for (const t of ["narration", "title", "note", "other"] as const) {
      expect(derivePhase(makeRegion({ region_type: t }), new Set())).toBe("OTHER_TYPE");
    }
  });
});

describe("suspectWarningVisible (E1/E2 render gate, speech-only R-015)", () => {
  it("visible only for speech regions carrying the UI suspect flag", () => {
    expect(suspectWarningVisible(makeRegion(), new Set(["rg-1"]))).toBe(true);
    expect(suspectWarningVisible(makeRegion(), new Set())).toBe(false);
    expect(
      suspectWarningVisible(makeRegion({ region_type: "sfx" }), new Set(["rg-1"])),
    ).toBe(false);
    expect(
      suspectWarningVisible(makeRegion({ region_type: "narration" }), new Set(["rg-1"])),
    ).toBe(false);
  });
});

describe("canRetype (A12: speech<->sfx only; disabled must carry a reason)", () => {
  it("speech -> sfx enabled", () => {
    const entry = canRetype(makeRegion(), "sfx");
    expect(entry.enabled).toBe(true);
    expect(entry.reason ?? "").toBe("");
  });

  it("sfx -> speech enabled", () => {
    const entry = canRetype(makeRegion({ region_type: "sfx" }), "speech");
    expect(entry.enabled).toBe(true);
  });

  it("same-type retypes are disabled with a reason", () => {
    expect(canRetype(makeRegion(), "speech").enabled).toBe(false);
    expect(canRetype(makeRegion(), "speech").reason).toMatch(/speech/);
    expect(canRetype(makeRegion({ region_type: "sfx" }), "sfx").enabled).toBe(false);
  });

  it("narration/title/note/other entries are disabled with a reason (A12)", () => {
    for (const t of ["narration", "title", "note", "other"] as const) {
      const toSfx = canRetype(makeRegion({ region_type: t }), "sfx");
      expect(toSfx.enabled).toBe(false);
      expect(toSfx.reason).toBeTruthy();
      const toSpeech = canRetype(makeRegion({ region_type: t }), "speech");
      expect(toSpeech.enabled).toBe(false);
      expect(toSpeech.reason).toBeTruthy();
    }
  });
});

describe("planRetypeAction (§4.1 entry dispatch — the only branch logic)", () => {
  it("forward speech->sfx plans an immediate execution (R2, no confirm)", () => {
    expect(planRetypeAction(makeRegion(), "sfx")).toEqual({ kind: "execute" });
  });

  it("takes no suspect input at all (A2 by construction: the warning flag cannot gate retypeability)", () => {
    // The signature has no suspect parameter — a flagged speech region and a
    // plain one plan identically, so the A2 red line holds by construction.
    expect(planRetypeAction(makeRegion(), "sfx")).toEqual({ kind: "execute" });
  });

  it("reverse sfx->speech routes through the explicit confirm (R3/A5: no one-click path)", () => {
    expect(planRetypeAction(makeRegion({ region_type: "sfx" }), "speech")).toEqual({
      kind: "confirm",
    });
  });

  it("blocked transitions return the A12 reason before any state moves", () => {
    const plan = planRetypeAction(makeRegion({ region_type: "narration" }), "sfx");
    expect(plan.kind).toBe("blocked");
    if (plan.kind === "blocked") {
      expect(plan.reason).toBeTruthy();
    }
  });
});

describe("sfxBadgeLabel (E3 lookup table on the region policy SNAPSHOT, A9)", () => {
  it("skip snapshot -> 保留原文 copy", () => {
    const label = sfxBadgeLabel("skip");
    expect(label.text).toContain("保留原文");
    expect(label.glyph).toBe("♪");
  });

  it("manual snapshot -> manual-processing copy (never auto-translate wording, §4.2)", () => {
    const label = sfxBadgeLabel("manual");
    expect(label.text).toContain("手动");
    expect(label.text).not.toContain("自动翻译");
    expect(label.glyph).toBe("♪");
  });

  it("translate snapshot -> SFX-chain copy (EV-8 CLOSED: reachable after retype)", () => {
    const label = sfxBadgeLabel("translate");
    expect(label.text).toContain("拟声词翻译链");
    expect(label.glyph).toBe("♪");
  });
});

describe("retypeFeedback (E4 copy = result + the region's own post-retype policy snapshot, R4)", () => {
  it("post-retype skip snapshot -> preserve-original copy + re-render hint", () => {
    const fb = retypeFeedback("skip");
    expect(fb.text).toContain("保留原文");
    expect(fb.text).toContain("不再翻译");
    expect(fb.offerRerender).toBe(true);
    expect(fb.offerUndo).toBe(true);
  });

  it("every feedback copy states the artefact boundary (§4.3-4/§4.4 FROZEN: relabel != erasing a rendered page)", () => {
    for (const policy of ["skip", "manual", "translate"] as const) {
      expect(retypeFeedback(policy).text).toContain("成品图需重跑渲染");
      expect(retypeFeedback(policy).text).toContain("原图完好");
    }
    expect(retypeFeedback("skip", "speech").text).toContain("成品图需重跑渲染");
  });

  it("post-retype manual snapshot -> manual-mode copy, not auto-translate (§4.2 row 2)", () => {
    const fb = retypeFeedback("manual");
    expect(fb.text).toContain("手动");
    // Must NEGATE automatic translation, never promise it (§4.2: manual
    // judges SKIP at the gate).
    expect(fb.text).toContain("不再自动翻译");
    expect(fb.text).not.toMatch(/将自动翻译|将（自动）翻译/);
  });

  it("post-retype translate snapshot -> explicit SFX-chain re-translate wording (§4.2 row 3)", () => {
    const fb = retypeFeedback("translate");
    expect(fb.text).toContain("拟声词翻译链");
    expect(fb.text).toContain("重新翻译");
  });

  it("reverse retype (-> speech) feedback states the re-entry into the speech chain", () => {
    const fb = retypeFeedback("skip", "speech");
    expect(fb.text).toContain("对白");
    expect(fb.offerUndo).toBe(true);
  });
});
