/**
 * Control CLI for the measurement session (session.mjs).
 *
 *   node ctl.mjs status
 *   node ctl.mjs eval "<js expression>"          # or: node ctl.mjs eval-file <path.js>
 *   node ctl.mjs click "<selector>" [index]
 *   node ctl.mjs shot <name>
 *   node ctl.mjs dpr <dpr> <width> <height>
 *   node ctl.mjs dproff
 *   node ctl.mjs quit
 */
import { readFileSync } from "node:fs";

const base = process.env.DP1_CTL || "http://127.0.0.1:9362";
const [cmd, ...rest] = process.argv.slice(2);

async function post(route, payload) {
  const res = await fetch(`${base}${route}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload ?? {}),
  });
  return { status: res.status, body: await res.text() };
}

let out;
if (cmd === "status") {
  out = await (await fetch(`${base}/status`)).text();
} else if (cmd === "eval") {
  out = (await post("/eval", { expr: rest.join(" ") })).body;
} else if (cmd === "eval-file") {
  const expr = readFileSync(rest[0], "utf8");
  out = (await post("/eval", { expr })).body;
} else if (cmd === "click") {
  out = (await post("/click", { selector: rest[0], index: Number(rest[1] || 0) })).body;
} else if (cmd === "shot") {
  out = (await post("/shot", { name: rest[0] })).body;
} else if (cmd === "dpr") {
  out = (await post("/dpr", { dpr: Number(rest[0]), width: Number(rest[1]), height: Number(rest[2]) })).body;
} else if (cmd === "dproff") {
  out = (await post("/dpr-off", {})).body;
} else if (cmd === "quit") {
  out = (await post("/quit", {})).body;
} else if (cmd === "raw") {
  out = (await post(rest[0], JSON.parse(rest[1] || "{}"))).body;
} else {
  out = `unknown command: ${cmd}`;
}
process.stdout.write(out + "\n");
