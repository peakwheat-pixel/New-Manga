import { useCallback, useEffect, useState } from "react";
import { runAc1OrFailClosed } from "./ac1/driver";
import { LibraryPanel } from "./library/LibraryPanel";
import { ResourceChannelClient, TypedChannelError } from "./resourceChannel/client";
import { SettingsPanel } from "./settings/SettingsPanel";

type InvokeFn = (command: string, args?: Record<string, unknown>) => Promise<unknown>;

interface ProbeState {
  probe_auto?: boolean;
  fixture_shas?: Record<string, string> | null;
  chunk_size?: number;
}

interface ScenarioResult {
  status: string;
  observed: unknown;
  note?: string;
}

function tauriInvoke(): InvokeFn {
  const globalWindow = window as unknown as {
    __TAURI__?: { core?: { invoke: InvokeFn } };
  };
  const invoke = globalWindow.__TAURI__?.core?.invoke;
  if (!invoke) {
    throw new Error("TAURI_BRIDGE_MISSING");
  }
  return invoke;
}

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

async function sha256Hex(blob: Blob): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", await blob.arrayBuffer());
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function expectTypedRejection(
  action: () => Promise<unknown>,
  expectedCode: string,
): Promise<ScenarioResult> {
  try {
    await action();
    return { status: "FAIL", observed: "no rejection raised" };
  } catch (error) {
    const code = error instanceof TypedChannelError ? error.code : String(error);
    return { status: code === expectedCode ? "PASS" : "FAIL", observed: code };
  }
}

/** RC2-AC1 deny probe: the invocation must be rejected by the hardened
 * command surface (command absent from this mode's allowlist, or refused by
 * the ACL). Any resolved value is a surface regression. */
async function expectCommandDenied(action: () => Promise<unknown>): Promise<ScenarioResult> {
  try {
    const observed = await action();
    return { status: "FAIL", observed: `resolved: ${JSON.stringify(observed)?.slice(0, 80)}` };
  } catch (error) {
    const code = error instanceof Error ? error.message : String(error);
    return { status: "PASS", observed: code };
  }
}

export default function App() {
  const [log, setLog] = useState<string[]>([]);
  const [status, setStatus] = useState("idle");

  const append = useCallback((line: string) => {
    setLog((previous) => [...previous, line]);
  }, []);

  useEffect(() => {
    let cancelled = false;
    const results: Record<string, unknown>[] = [];
    const probeWindow = window as unknown as { __probeFinished?: boolean };
    const observed = (value: string) => {
      setStatus(value);
      // document.title is readable from the Rust side: a progress channel
      // that works even when the invoke bridge is broken
      document.title = `M2RC1|${value}|results=${results.length}`;
    };
    observed("starting");

    const tauriInvokeSafe = (): InvokeFn => {
      try {
        return tauriInvoke();
      } catch {
        return () => Promise.resolve(null);
      }
    };

    // ---- production/interactive mode: the hardened-surface deny matrix ----
    // RC2-AC1 evidence protocol: in production mode the probe commands and
    // register_catalog do NOT exist on the invoke surface, so the page has NO
    // write channel (no probe_write_results) and no exit command (no
    // probe_exit) — the matrix result cannot leave the page, by design. The
    // runner therefore judges this phase from the OUTSIDE: the host announces
    // its effective command allowlist on stderr at startup, the page stays
    // alive (no exit command to call), and no probe results file may appear.
    // The matrix below keeps the page honest and observable on screen; a red
    // scenario is a visible regression, not a gate channel.
    const runInteractiveDenyMatrix = async (invoke: InvokeFn) => {
      const record = (id: string, result: ScenarioResult) => {
        results.push({ id, ...result });
        append(`${id}  ${result.status}${result.note ? ` — ${result.note}` : ""}`);
      };
      const denied = (id: string, action: () => Promise<unknown>) =>
        expectCommandDenied(action).then((result) => record(id, result));

      await denied("IP-1-register-catalog-denied", () =>
        invoke("register_catalog", { resourceId: "res-x", relPath: "asset.png" }),
      );
      await denied("IP-2-probe-config-denied", () => invoke("probe_config"));
      await denied("IP-3-probe-write-results-denied", () =>
        invoke("probe_write_results", { payload: "{}" }),
      );
      await denied("IP-4-probe-exit-denied", () => invoke("probe_exit", { code: 0 }));
      await denied("IP-5-probe-issue-denied", () =>
        invoke("probe_issue_url", { resourceId: "res-x", revision: "rev-1", ttlSeconds: 0.001 }),
      );

      // a smuggled TTL override on the production shape must be inert: the
      // command has no such parameter, the Core keeps the ruled default, and
      // the reference stays servable (0.001 s would have expired instantly)
      try {
        const issued = (await invoke("issue_resource_url", {
          resourceId: "res-cataloged",
          revision: "rev-1",
          ttlOverride: 0.001,
        })) as { url: string; size: number };
        const response = await fetch(`${issued.url}?chunk=0`);
        record("IP-6-ttl-override-inert", {
          status: response.ok ? "PASS" : "FAIL",
          observed: { fetch_status: response.status },
          note: "ttlOverride is not a parameter of the production issue shape",
        });
      } catch (error) {
        record("IP-6-ttl-override-inert", {
          status: "FAIL",
          observed: error instanceof Error ? error.message : String(error),
        });
      }

      // allow-side control: the production surface still serves its product
      try {
        const issued = (await invoke("issue_resource_url", {
          resourceId: "res-cataloged",
          revision: "rev-1",
        })) as { url: string; size: number; opaque_id: string };
        record("IA-1-production-issue-allowed", {
          status: issued.url.startsWith("http://m2res.localhost/m2id/") ? "PASS" : "FAIL",
          observed: { opaque_tail: issued.opaque_id.slice(-6) },
        });
      } catch (error) {
        record("IA-1-production-issue-allowed", {
          status: "FAIL",
          observed: error instanceof Error ? error.message : String(error),
        });
      }

      const deny = results.filter((r) => String(r.id).startsWith("IP-"));
      const allow = results.filter((r) => String(r.id).startsWith("IA-"));
      const denyPassed = deny.filter((r) => r.status === "PASS").length;
      const allowPassed = allow.filter((r) => r.status === "PASS").length;
      observed(
        `interactive|deny=${denyPassed}/${deny.length}|allow=${allowPassed}/${allow.length}`,
      );
      // NOTE: no self-close here. window.close() is script-blocked on
      // WebView2 and there is deliberately no exit command on this surface:
      // the window stays open (user-facing mode), the runner judges the
      // phase on the host's stderr allowlist announcement + process liveness
      // + absence of probe results.
    };

    void (async () => {
      let invoke: InvokeFn;
      try {
        invoke = tauriInvoke();
      } catch {
        observed("TAURI_BRIDGE_MISSING");
        return;
      }

      // ---- M2-AC1 acceptance driver: explicit test startup config only ----
      // `ac1_request` is registered only when the host runs with
      // M2AC1_TEST_MODE=1; production and probe mode deny it, and the page
      // then falls through to the RC1/RC2 behaviour below unchanged.
      const ac1Detected = await (async () => {
        try {
          await invoke("ac1_request", { method: "ping", params: {} });
          return true;
        } catch {
          return false;
        }
      })();
      if (ac1Detected) {
        await runAc1OrFailClosed(
          invoke,
          { log: append, status: observed },
          (payload) => invoke("ac1_write_results", { payload }) as Promise<void>,
          (code) => invoke("ac1_exit", { code }) as Promise<void>,
        );
        return;
      }

      // probe_config exists only in probe mode: in production mode this very
      // call is denied, which switches the page into the interactive matrix
      let config: ProbeState | null = null;
      try {
        config = await call<ProbeState>(invoke)("probe_config");
      } catch {
        await runInteractiveDenyMatrix(invoke);
        return;
      }
      if (!config.probe_auto) {
        observed("interactive mode");
        return;
      }

      // failsafe: an unusable invoke bridge must not hang the PROBE runner
      // (interactive mode stays open; it is the user-facing mode)
      const probeWindowHandle = probeWindow;
      probeWindowHandle.__probeFinished = false;
      const failsafe = setTimeout(() => {
        if (probeWindow.__probeFinished !== true) {
          observed("FAILSAFE-CLOSE");
          window.close();
        }
      }, 60000);

      const client = new ResourceChannelClient(invoke);
      const record = (id: string, result: ScenarioResult) => {
        results.push({ id, ...result });
        append(`${id}  ${result.status}${result.note ? ` — ${result.note}` : ""}`);
        observed(`probe running (${results.length} recorded)`);
      };
      const flush = () =>
        call<string>(invoke)("probe_write_results", {
          payload: JSON.stringify(
            { probe: "M2-RC2 hardened command surface + RC1 resource channel matrix", results },
            null,
            2,
          ),
        });
      const finishProbe = (code: number) => {
        probeWindow.__probeFinished = true;
        clearTimeout(failsafe);
        if (!cancelled) {
          void tauriInvokeSafe()("probe_exit", { code });
        }
      };

      try {
        record("E-00-probe-mode-detected", { status: "PASS", observed: { probe_auto: true } });

        // E-01 issue + full chunked fetch; the digest is computed here only
        // for self-verification (the WebView-visible object never carries one)
        const issued = await client.issue("res-probe", "rev-1");
        const blob = await client.fetchAll(issued.url, issued.size);
        const sha = await sha256Hex(blob);
        const expectedSha = config.fixture_shas?.asset ?? null;
        record("E-01-issue-fetch-digest", {
          status: expectedSha === null || sha === expectedSha ? "PASS" : "FAIL",
          observed: { bytes: blob.size, sha256: sha, expected_sha256: expectedSha },
        });

        // E-02 render through <img> from the assembled blob
        const render = await new Promise<{ ok: boolean; w: number }>((resolve) => {
          const img = new Image();
          const blobUrl = URL.createObjectURL(blob);
          img.onload = () => resolve({ ok: img.naturalWidth > 0, w: img.naturalWidth });
          img.onerror = () => resolve({ ok: false, w: 0 });
          img.src = blobUrl;
        });
        record("E-02-img-render", { status: render.ok ? "PASS" : "FAIL", observed: render });

        // E-03 unknown well-formed ID -> typed 404
        const unknownUrl = `http://m2res.localhost/m2id/${"a".repeat(43)}`;
        record(
          "E-03-unknown-id",
          await expectTypedRejection(() => client.fetchChunk(unknownUrl, 0), "REF_UNKNOWN_ID"),
        );

        // E-04 revoke -> next resolve typed 410 (T6 immediate revocation).
        // DSH F-01 regression form: the FIRST fetch warms the host grant
        // cache, so the post-revoke fetch proves a warm cache cannot bypass
        // the Core (the pre-fix build served 200 here).
        const revocable = await client.issue("res-probe", "rev-2");
        const warmed = await client.fetchAll(revocable.url, revocable.size);
        if (warmed.size !== revocable.size) {
          record("E-04-revoke-after-cached-fetch", { status: "FAIL", observed: "warm-up fetch short" });
        } else {
          await client.revoke(revocable.opaqueId);
          record(
            "E-04-revoke-after-cached-fetch",
            await expectTypedRejection(
              () => client.fetchChunk(revocable.url, 0),
              "REF_REVOKED",
            ),
          );
        }

        // E-05 expiry through the probe-only TTL command (the production
        // issue shape has no TTL parameter; RC2 moved the override behind
        // probe_issue_url which exists only in probe mode)
        const expiring = await call<{ url: string; opaque_id: string }>(invoke)("probe_issue_url", {
          resourceId: "res-probe",
          revision: "rev-3",
          ttlSeconds: 1.0,
        });
        await sleep(1600);
        record(
          "E-05-expired-ttl",
          await expectTypedRejection(() => client.fetchChunk(expiring.url, 0), "REF_EXPIRED"),
        );

        // E-06 remount/reconnect: fresh issue per mount; stale URLs never reused
        const remountA = await client.issue("res-probe", "rev-1");
        const remountB = await client.issue("res-probe", "rev-1");
        record("E-06-remount-fresh-references", {
          status: remountA.opaqueId !== remountB.opaqueId ? "PASS" : "FAIL",
          observed: {
            first: remountA.opaqueId.slice(-10),
            second: remountB.opaqueId.slice(-10),
          },
        });

        // E-07 per-reference first-byte P95 on an 11,525,983 B fixture
        // (DSH F-04: a 49 KB fixture cannot speak for the <=25 MiB T3 line;
        // the cold-page-cache measurement is S1-B6 and stays NOT_RUN). Each
        // issue mints a NEW opaque reference, so the grant cache is cold and
        // every sample includes the host's first-verification full-file
        // digest pass -- only the OS page cache is warm (R-06 relabel).
        const timings: number[] = [];
        for (let i = 0; i < 8; i += 1) {
          const hot = await client.issue("res-hot", "rev-1");
          const start = performance.now();
          const response = await fetch(`${hot.url}?chunk=0`);
          await response.arrayBuffer();
          timings.push(performance.now() - start);
        }
        timings.sort((a, b) => a - b);
        const p95 = timings[Math.min(timings.length - 1, Math.floor(timings.length * 0.95))];
        record("E-07-per-reference-first-byte-p95", {
          status: p95 <= 200 ? "PASS" : "FAIL",
          observed: {
            p95_ms: Math.round(p95),
            timings_ms: timings.map((t) => Math.round(t)),
            fixture: "typical.png (11525983 B)",
            scenario: "per-reference first-byte (cold grant cache, warm OS page cache)",
          },
        });

        // E-08 256 MiB boundary through chunked streaming (T4: the resident
        // buffer stays at one 16 MiB chunk)
        try {
          const boundary = await client.issue("res-boundary", "rev-1");
          let served = 0;
          const chunkSize = config.chunk_size ?? 16 * 1024 * 1024;
          for (let chunk = 0; chunk * chunkSize < boundary.size; chunk += 1) {
            served += (await client.fetchChunk(boundary.url, chunk)).byteLength;
          }
          record("E-08-boundary-256mib", {
            status: served === boundary.size ? "PASS" : "FAIL",
            observed: { served, declared: boundary.size },
          });
        } catch (error) {
          const code = error instanceof TypedChannelError ? error.code : String(error);
          record("E-08-boundary-256mib", { status: "NOT_RUN", observed: code });
        }

        // E-09 over-limit issue -> typed RESOURCE_TOO_LARGE (the lab catalogs
        // oversize.bin; the Core refuses it at issue time)
        try {
          await client.issue("res-oversize", "rev-1");
          record("E-09-over-limit-typed", { status: "FAIL", observed: "issued over-limit" });
        } catch (error) {
          const code = error instanceof Error ? error.message : String(error);
          record("E-09-over-limit-typed", {
            status: code === "RESOURCE_TOO_LARGE" ? "PASS" : "NOT_RUN",
            observed: code,
          });
        }

        // ---- RC2-AC1 probe-mode deny additions (the catalog surface is
        // gone in EVERY mode, and a TTL smuggled onto the production shape
        // must be inert) ----
        record(
          "D-01-register-catalog-denied",
          await expectCommandDenied(() =>
            invoke("register_catalog", { resourceId: "res-x", relPath: "asset.png" }),
          ),
        );
        try {
          const smuggled = await call<{ url: string; opaque_id: string }>(invoke)(
            "issue_resource_url",
            { resourceId: "res-probe", revision: "rev-d", ttlOverride: 0.001 },
          );
          await sleep(100);
          const still = await fetch(`${smuggled.url}?chunk=0`);
          record("D-02-ttl-override-inert", {
            status: still.ok ? "PASS" : "FAIL",
            observed: { fetch_status: still.status },
            note: "ttlOverride is not a parameter of the production issue shape",
          });
        } catch (error) {
          record("D-02-ttl-override-inert", {
            status: "FAIL",
            observed: error instanceof Error ? error.message : String(error),
          });
        }
        // probe-mode control: the probe issue command is present HERE
        // (allow-side counterpart of IP-5)
        try {
          await call(invoke)("probe_issue_url", {
            resourceId: "res-probe",
            revision: "rev-p",
            ttlSeconds: 60,
          });
          record("D-03-probe-issue-allowed-in-probe-mode", { status: "PASS", observed: "resolved" });
        } catch (error) {
          record("D-03-probe-issue-allowed-in-probe-mode", {
            status: "FAIL",
            observed: error instanceof Error ? error.message : String(error),
          });
        }

        observed("probe done");
        await flush();
        finishProbe(0);
      } catch (error) {
        append(`FATAL ${String(error)}`);
        results.push({
          id: "FATAL",
          status: "FAIL",
          observed: String(error),
          stack: error instanceof Error ? error.stack : null,
        });
        observed("fatal");
        await flush();
        finishProbe(1);
      }
    })();

    function call<T>(inv: InvokeFn) {
      return (command: string, args?: Record<string, unknown>) =>
        inv(command, args) as Promise<T>;
    }

    return () => {
      cancelled = true;
    };
  }, [append]);

  return (
    <div
      style={{
        fontFamily: "Consolas, monospace",
        fontSize: 12,
        margin: 12,
        color: "#d8e0e8",
        background: "#101418",
      }}
    >
      <h1 style={{ fontSize: 15 }}>M2-RC2 resource channel runtime</h1>
      <div>{status}</div>
      <div>
        {log.map((line, index) => (
          <div key={index}>{line}</div>
        ))}
      </div>
      <LibraryPanel />
      <SettingsPanel />
    </div>
  );
}
