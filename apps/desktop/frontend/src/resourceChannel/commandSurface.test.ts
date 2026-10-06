import { describe, expect, it, vi } from "vitest";
import { ResourceChannelClient } from "./client";

/**
 * RC2-AC1 — WebView-facing command surface allow/deny matrix (F-03).
 *
 * The mock reproduces the hardened host semantics pinned by the Rust suite
 * (main.rs `command_allowlist` + capabilities/m2rc1-commands.json):
 *
 * - production surface = issue_resource_url / revoke_ref / revoke_resource_refs
 *   ONLY (issue has no TTL parameter shape); the M2-IPC1 production-only
 *   pair (core_ping / library_list_books), the M2-SETTINGS-IPC-CHANNEL
 *   settings pair (settings_get / settings_update_section, contract M2-C1
 *   rev 1.3 §5.3) and the M2-REGION-RETYPE-CORE region pair (set_region_type
 *   / list_regions, contract rev 1.4 §5.4 — pin 补录 deferred to this Task,
 *   now landed by M2-WORKBENCH-REACT-1) ride the same production arm and are
 *   likewise absent from every test-mode surface;
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
// M2-SETTINGS-IPC-CHANNEL: the settings read/write pair is production-only
// (main.rs SETTINGS_PRODUCTION_ONLY_COMMANDS; option-B precedent of M2-IPC1).
const SETTINGS_PRODUCTION_ONLY_COMMANDS = ["settings_get", "settings_update_section"];
// M2-RC4: region retype/read, revision history/restore and rerender are
// production-only. M2-PAGE-RESOURCE-RESOLVE-1 adds the page display image
// resolve to the same production-only family. The probe surface remains frozen.
const REGION_PRODUCTION_ONLY_COMMANDS = [
  "set_region_type",
  "list_regions",
  "list_region_revisions",
  "restore_region_revision",
  "rerender_page",
  "resolve_page_resource",
];

type Mode = "production" | "probe";

function makeSurfaceInvoke(mode: Mode) {
  const calls: { command: string; args: Record<string, unknown> }[] = [];
  const invoke = vi.fn(async (command: string, args?: Record<string, unknown>) => {
    // production arm = the three resource-channel commands + the M2-IPC1
    // pair (core_ping / library_list_books) + the M2-SETTINGS-IPC-CHANNEL
    // settings pair (settings_get / settings_update_section) + the
    // region command face (retype/read/revision/history/restore/rerender);
    // the probe arm keeps the frozen RC2 shape (settings/region pairs
    // absent, four probe commands added) — mirroring main.rs
    // command_allowlist.
    const available = [
      ...PRODUCTION_COMMANDS,
      ...(mode === "production" ? SETTINGS_PRODUCTION_ONLY_COMMANDS : []),
      ...(mode === "production" ? REGION_PRODUCTION_ONLY_COMMANDS : []),
      ...(mode === "probe" ? PROBE_ONLY_COMMANDS : []),
    ];
    if (!available.includes(command)) {
      // Tauri 2 rejects invokes for commands that are not registered for the
      // window ("Command X not allowed" / not found) — the deny matrix only
      // needs the rejection itself.
      throw new Error(`unavailable on ${mode} surface: ${command}`);
    }
    const args_ = args ?? {};
    calls.push({ command, args: args_ });
    if (command === "settings_get") {
      // contract M2-C1 rev 1.3 §5.3: the {"settings": ...} projection
      return { settings: { sfx: { policy: "skip" } } };
    }
    if (command === "settings_update_section") {
      return { settings: {} };
    }
    if (command === "list_regions") {
      // contract M2-C1 §5.4 (rev 1.5 read widening): the wrapper carries the
      // optional page_size projection beside the summaries
      return {
        regions: [
          {
            region_id: "region-1",
            region_type: "sfx",
            sfx_policy: "translate",
            origin: "user",
            revision_no: 3,
          },
        ],
        page_size: { width: 100, height: 50 },
      };
    }
    if (command === "set_region_type") {
      // the post-retype effective state (§5.4 SetRegionType result)
      return { region_id: "region-1", revision_no: 4, region_type: "narration", sfx_policy: "skip" };
    }
    if (command === "list_region_revisions") {
      return { region_id: "region-1", current_revision_no: 4, revisions: [] };
    }
    if (command === "restore_region_revision") {
      return { region_id: "region-1", revision_no: 5, region_type: "speech", sfx_policy: "skip" };
    }
    if (command === "rerender_page") {
      return {
        page_id: "page-1",
        artifact_id: "artifact-1",
        revision_no: 8,
        reports: [],
        preview: null,
        preview_error: "preview unavailable",
      };
    }
    if (command === "resolve_page_resource") {
      // contract M2-C1 rev 1.7 (M2-PAGE-RESOURCE-RESOLVE-1): the stable
      // {resource_id, revision} catalog-key pair
      return { resource_id: "page-original-page-1", revision: "original" };
    }
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

  // M2-SETTINGS-IPC-CHANNEL: the settings pair rides the production arm
  // (allow) and is absent from the frozen probe surface (deny) — the same
  // matrix the Rust suite pins via SETTINGS_PRODUCTION_ONLY_COMMANDS.
  it("settings commands are allowed on production and denied on the probe surface", async () => {
    expect(SETTINGS_PRODUCTION_ONLY_COMMANDS).toEqual(["settings_get", "settings_update_section"]);
    const { invoke } = makeSurfaceInvoke("production");
    await expect(invoke("settings_get")).resolves.toMatchObject({
      settings: { sfx: { policy: "skip" } },
    });
    await expect(
      invoke("settings_update_section", { section: "sfx", values: { policy: "skip" } }),
    ).resolves.toMatchObject({ settings: {} });
    const { invoke: probeInvoke } = makeSurfaceInvoke("probe");
    for (const command of SETTINGS_PRODUCTION_ONLY_COMMANDS) {
      await expect(probeInvoke(command, {})).rejects.toThrow(new RegExp(command));
    }
  });

  // The complete frozen region command face rides production and remains
  // absent from probe and acceptance surfaces.
  it("region commands are allowed on production and denied on the probe surface", async () => {
    expect(REGION_PRODUCTION_ONLY_COMMANDS).toEqual([
      "set_region_type",
      "list_regions",
      "list_region_revisions",
      "restore_region_revision",
      "rerender_page",
      "resolve_page_resource",
    ]);
    const { invoke } = makeSurfaceInvoke("production");
    await expect(
      invoke("list_regions", { pageId: "page-1" }),
    ).resolves.toMatchObject({
      regions: [{ region_id: "region-1", region_type: "sfx" }],
      page_size: { width: 100, height: 50 },
    });
    await expect(
      invoke("set_region_type", { regionId: "region-1", newRegionType: "narration" }),
    ).resolves.toMatchObject({ region_id: "region-1", revision_no: 4 });
    await expect(invoke("list_region_revisions", { regionId: "region-1" })).resolves.toMatchObject({
      current_revision_no: 4,
    });
    await expect(invoke("restore_region_revision", {
      regionId: "region-1",
      revisionNo: 2,
      expectedRevision: 4,
    })).resolves.toMatchObject({ revision_no: 5 });
    await expect(invoke("rerender_page", { pageId: "page-1" })).resolves.toMatchObject({
      artifact_id: "artifact-1",
      preview_error: "preview unavailable",
    });
    await expect(invoke("resolve_page_resource", { pageId: "page-1" })).resolves.toMatchObject({
      resource_id: "page-original-page-1",
      revision: "original",
    });
    const { invoke: probeInvoke } = makeSurfaceInvoke("probe");
    for (const command of REGION_PRODUCTION_ONLY_COMMANDS) {
      await expect(probeInvoke(command, {})).rejects.toThrow(new RegExp(command));
    }
  });

  it("production mode allows the product commands (resources + IPC1 pair + settings pair)", async () => {
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
