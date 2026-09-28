import { describe, expect, it, vi } from "vitest";
import { ResourceChannelClient } from "./client";

/**
 * RC2-AC1 — WebView-facing command surface allow/deny matrix (F-03).
 *
 * The mock reproduces the hardened host semantics pinned by the Rust suite
 * (main.rs `command_allowlist` + capabilities/m2rc1-commands.json):
 *
 * - production surface = issue_resource_url / revoke_ref / revoke_resource_refs
 *   ONLY (issue has no TTL parameter shape);
 * - probe_config / probe_write_results / probe_exit / probe_issue_url exist
 *   only in probe mode;
 * - register_catalog exists in NO mode (catalog is Core/SQLite authority);
 * - invoking an absent command rejects, mirroring Tauri's behavior.
 */

const PRODUCTION_COMMANDS = ["issue_resource_url", "revoke_ref", "revoke_resource_refs"];
const PROBE_ONLY_COMMANDS = ["probe_config", "probe_write_results", "probe_exit", "probe_issue_url"];
const REMOVED_COMMANDS = ["register_catalog"];
// M2-AC1: the acceptance commands exist ONLY in the explicit test startup
// configuration (M2AC1_TEST_MODE=1) — never on the production or probe
// surface, so a page-side ac1 probe is the mode detector (App.tsx).
const AC1_TEST_COMMANDS = ["ac1_request", "ac1_write_results", "ac1_exit"];

type Mode = "production" | "probe";

function makeSurfaceInvoke(mode: Mode) {
  const calls: { command: string; args: Record<string, unknown> }[] = [];
  const invoke = vi.fn(async (command: string, args?: Record<string, unknown>) => {
    const available = [...PRODUCTION_COMMANDS, ...(mode === "probe" ? PROBE_ONLY_COMMANDS : [])];
    if (!available.includes(command)) {
      // Tauri 2 rejects invokes for commands that are not registered for the
      // window ("Command X not allowed" / not found) — the deny matrix only
      // needs the rejection itself.
      throw new Error(`unavailable on ${mode} surface: ${command}`);
    }
    const args_ = args ?? {};
    calls.push({ command, args: args_ });
    if (command === "issue_resource_url") {
      // host-side hardening (compile-time in Rust): an unknown key such as
      // ttlOverride cannot reach the Core; the shape carries two params only
      const keys = Object.keys(args_);
      if (keys.some((k) => !["resourceId", "revision"].includes(k))) {
        // the real host ignores unknown keys (serde) — record them so the
        // test can assert the client never sends any
        args_.__unknownKeys = keys.filter((k) => !["resourceId", "revision"].includes(k));
      }
      const segment = "a".repeat(43);
      return { url: `http://m2res.localhost/m2id/${segment}`, size: 1024, opaque_id: `m2id.v1.${segment}` };
    }
    if (command === "revoke_ref" || command === "revoke_resource_refs") {
      return null;
    }
    if (command === "probe_issue_url") {
      const segment = "b".repeat(43);
      return { url: `http://m2res.localhost/m2id/${segment}`, size: 1024, opaque_id: `m2id.v1.${segment}` };
    }
    if (command === "probe_config") {
      return { probe_auto: mode === "probe" };
    }
    return null;
  });
  return { invoke, calls };
}

describe("RC2 command surface allow/deny matrix", () => {
  it("register_catalog is denied on BOTH surfaces (catalog is Core authority)", async () => {
    // the removal list is pinned: exactly the catalog surface, no mode
    expect(REMOVED_COMMANDS).toEqual(["register_catalog"]);
    for (const mode of ["production", "probe"] as const) {
      const { invoke } = makeSurfaceInvoke(mode);
      await expect(
        invoke("register_catalog", { resourceId: "res-x", relPath: "asset.png" }),
      ).rejects.toThrow(/register_catalog/);
    }
  });

  it("production mode denies every probe command", async () => {
    const { invoke } = makeSurfaceInvoke("production");
    for (const command of PROBE_ONLY_COMMANDS) {
      await expect(invoke(command, {})).rejects.toThrow(new RegExp(command));
    }
  });

  // F-012 (DSH r1): the ac1 acceptance commands must be denied on BOTH the
  // production and probe surfaces — the App's ac1 mode detection relies on
  // that rejection falling through to the RC1/RC2 behaviour unchanged.
  it("ac1 commands are denied on production and probe surfaces", async () => {
    for (const mode of ["production", "probe"] as const) {
      const { invoke } = makeSurfaceInvoke(mode);
      for (const command of AC1_TEST_COMMANDS) {
        await expect(invoke(command, {})).rejects.toThrow(new RegExp(command));
      }
    }
  });

  it("production mode allows exactly the three product commands", async () => {
    const { invoke } = makeSurfaceInvoke("production");
    const issued = (await invoke("issue_resource_url", {
      resourceId: "res-a",
      revision: "rev-1",
    })) as { url: string };
    expect(issued.url.startsWith("http://m2res.localhost/m2id/")).toBe(true);
    await expect(invoke("revoke_ref", { opaqueId: "m2id.v1.aaa" })).resolves.toBeNull();
    await expect(invoke("revoke_resource_refs", { resourceId: "res-a" })).resolves.toBeNull();
  });

  it("probe mode additionally allows the probe surface", async () => {
    const { invoke } = makeSurfaceInvoke("probe");
    await expect(invoke("probe_config", {})).resolves.toMatchObject({ probe_auto: true });
    await expect(
      invoke("probe_issue_url", { resourceId: "res-a", revision: "rev-1", ttlSeconds: 1 }),
    ).resolves.toMatchObject({ opaque_id: `m2id.v1.${"b".repeat(43)}` });
  });

  it("the client's issue calls never carry a TTL override key", async () => {
    const { invoke, calls } = makeSurfaceInvoke("production");
    const client = new ResourceChannelClient(invoke);
    await client.issue("res-a", "rev-1");
    expect(calls).toHaveLength(1);
    expect(Object.keys(calls[0].args).sort()).toEqual(["resourceId", "revision"]);
  });

  it("the client only ever calls production-surface commands", async () => {
    const { invoke, calls } = makeSurfaceInvoke("production");
    const client = new ResourceChannelClient(invoke);
    const issued = await client.issue("res-a", "rev-1");
    await client.revoke(issued.opaqueId);
    const commands = calls.map((c) => c.command);
    expect(commands.every((c) => PRODUCTION_COMMANDS.includes(c))).toBe(true);
    expect(commands).toEqual(["issue_resource_url", "revoke_ref"]);
  });

  it("client typed rejection survives the hardened surface", async () => {
    const { invoke } = makeSurfaceInvoke("production");
    const client = new ResourceChannelClient(invoke);
    const fetchMock = vi.fn(async () => new Response('{"code":"REF_REVOKED"}', { status: 410 }));
    await expect(
      client.fetchAll(`http://m2res.localhost/m2id/${"a".repeat(43)}`, 1024, fetchMock as unknown as typeof fetch),
    ).rejects.toMatchObject({ code: "REF_REVOKED" });
  });
});
