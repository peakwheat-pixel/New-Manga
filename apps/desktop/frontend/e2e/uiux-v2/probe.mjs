/**
 * Diagnostic: is the real Core refusing non-ASCII (Chinese) book titles?
 * The UI path used a Chinese title; the earlier raw-IPC probe used ASCII and
 * succeeded. Call the same command with several title shapes and compare.
 */
import { launchApp } from "./lib/app.mjs";
import { evaluate, sleep } from "../p02-new-time/lib/cdp.mjs";
import { resolveRunName, runRootFor } from "./lib/env.mjs";

const scenarioRoot = runRootFor(resolveRunName());
const app = await launchApp({ scenarioRoot, tag: "diag-title" });
const cdp = app.cdp;

const titles = ["ascii-title", "中文标题", "中文 带空格", "端到端验收-808947", "雾港来信", "a中文b"];

try {
  await evaluate(cdp, `document.querySelector('[data-testid="app-root"]') !== null`);
  for (let i = 0; i < 60; i += 1) {
    const ready = await evaluate(cdp, `typeof window.__TAURI__ === "object" && !!window.__TAURI__.core`);
    if (ready) break;
    await sleep(250);
  }
  console.log("bridge ready:", await evaluate(cdp, `typeof window.__TAURI__ === "object"`));
  for (const title of titles) {
    const result = await evaluate(
      cdp,
      `(async () => {
        try {
          const v = await window.__TAURI__.core.invoke("library_create_book", { payload: { title: ${JSON.stringify(
            title,
          )} } });
          return { ok: true, id: v && v.book_id, title: v && v.title };
        } catch (e) {
          return {
            ok: false,
            message_key: e && e.message_key,
            category: e && e.category,
            phase: e && e.phase,
            raw: (() => { try { return JSON.stringify(e); } catch { return String(e); } })(),
          };
        }
      })()`,
    );
    console.log(JSON.stringify({ input: title, ...result }));
  }
  const books = await evaluate(
    cdp,
    `(async () => { try { const v = await window.__TAURI__.core.invoke("library_list_books", {}); return Array.isArray(v) ? v.map((b) => b.title) : v; } catch (e) { return String(e); } })()`,
  );
  console.log("books in core:", JSON.stringify(books));
} catch (error) {
  console.error("DIAG ERROR", error);
} finally {
  await app.teardown();
  console.log("scenarioRoot", scenarioRoot);
}
