import { useCallback, useEffect, useState } from "react";
import { ResourceChannelClient, TypedChannelError } from "./resourceChannel/client";

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

    // failsafe: an unusable invoke bridge must not hang the runner
    const failsafe = setTimeout(() => {
      if (probeWindow.__probeFinished !== true) {
        observed("FAILSAFE-CLOSE");
        window.close();
      }
    }, 60000);

    const finish = (code: number) => {
      probeWindow.__probeFinished = true;
      clearTimeout(failsafe);
      if (!cancelled) {
        void tauriInvokeSafe()(code === 0 ? "probe_exit" : "probe_exit", { code });
      }
    };
    const tauriInvokeSafe = (): InvokeFn => {
      try {
        return tauriInvoke();
      } catch {
        return () => Promise.resolve(null);
      }
    };

    void (async () => {
      const invoke = tauriInvoke();
      const call = <T,>(command: string, args?: Record<string, unknown>) =>
        invoke(command, args) as Promise<T>;
      const client = new ResourceChannelClient(invoke);
      const record = (id: string, result: ScenarioResult) => {
        results.push({ id, ...result });
        append(`${id}  ${result.status}${result.note ? ` — ${result.note}` : ""}`);
        observed(`probe running (${results.length} recorded)`);
      };
      const flush = () =>
        call<string>("probe_write_results", {
          payload: JSON.stringify(
            { probe: "M2-RC1 end-to-end matrix", results },
            null,
            2,
          ),
        });

      try {
        // the embedded page URL has no query string: probe mode comes from
        // the host (M2RC1_PROBE_OUT presence) via probe_config, not location
        const config = await call<ProbeState>("probe_config");
        if (!config.probe_auto) {
          observed("interactive mode");
          finish(0);
          return;
        }
        record("E-00-probe-mode-detected", { status: "PASS", observed: { probe_auto: true } });
        await call("register_catalog", { resourceId: "res-probe", relPath: "asset.png" });
        await call("register_catalog", { resourceId: "res-boundary", relPath: "boundary.bin" });

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

        // E-05 expiry (probe-only TTL override; the product default is 300 s)
        const expiring = await call<{ url: string; opaque_id: string }>("issue_resource_url", {
          resourceId: "res-probe",
          revision: "rev-3",
          ttlOverride: 1.0,
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

        // E-07 hot-cache first-byte-to-host P95 on a ~11.5 MiB fixture
        // (DSH F-04: a 49 KB fixture cannot speak for the <=25 MiB T3 line;
        // the cold cache measurement is S1-B6 and stays NOT_RUN). Each issue
        // mints a NEW opaque reference, so every sample includes the host's
        // first-verified full-file digest pass -- the honest per-reference
        // first-byte cost.
        await call("register_catalog", { resourceId: "res-hot", relPath: "typical.png" });
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
        record("E-07-hot-cache-p95", {
          status: p95 <= 200 ? "PASS" : "FAIL",
          observed: {
            p95_ms: Math.round(p95),
            timings_ms: timings.map((t) => Math.round(t)),
            fixture: "typical.png (~11.5 MiB)",
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

        // E-09 over-limit issue -> typed RESOURCE_TOO_LARGE (registered only
        // when the runner lab contains oversize.bin)
        try {
          await call("register_catalog", { resourceId: "res-oversize", relPath: "oversize.bin" });
          await client.issue("res-oversize", "rev-1");
          record("E-09-over-limit-typed", { status: "FAIL", observed: "issued over-limit" });
        } catch (error) {
          const code = error instanceof Error ? error.message : String(error);
          record("E-09-over-limit-typed", {
            status: code === "RESOURCE_TOO_LARGE" ? "PASS" : "NOT_RUN",
            observed: code,
          });
        }

        observed("probe done");
        await flush();
        finish(0);
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
        finish(1);
      }
    })();

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
      <h1 style={{ fontSize: 15 }}>M2-RC1 resource channel runtime</h1>
      <div>{status}</div>
      <div>
        {log.map((line, index) => (
          <div key={index}>{line}</div>
        ))}
      </div>
    </div>
  );
}
