import { describe, expect, it } from "vitest";
import { decidePhase } from "./driver";

describe("decidePhase", () => {
  it("routes an empty data root to the pipeline launch", () => {
    expect(decidePhase({ phase: "empty" })).toBe("run1");
  });

  it("routes a persisted result to the restore launch", () => {
    expect(decidePhase({ phase: "restore" })).toBe("run2");
  });

  it("fails closed on an unknown persisted phase", () => {
    expect(() => decidePhase({ phase: "unexpected" })).toThrow(/AC1_UNKNOWN_PHASE/);
    expect(() => decidePhase({})).toThrow(/AC1_UNKNOWN_PHASE/);
  });
});
