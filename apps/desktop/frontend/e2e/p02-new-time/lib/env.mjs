/**
 * P02-NEW-TIME-X6-AC1-AC7 — isolated Task-local launch environment.
 *
 * Every writable path the packaged app can reach is pinned INSIDE
 * `G:/CODEX/New Manga.workspace/task-envs/P02-NEW-TIME-X6-AC1-AC7/run-r1/`.
 * The launch env is rebuilt from the host env by purging every M2RC1_* /
 * M2RC2_* / NEWMANGA_* / M2AC1_* variable first (same discipline as
 * packaging/m2ac5/run_clean_start_e2e.py) and then pinning the Task-local
 * values. `M2RC1_PROBE_OUT` and `M2AC1_TEST_MODE` are NEVER set here: the
 * app must boot into the production interactive surface so the
 * Console/Workbench navigation chrome exists.
 */

import { existsSync, readdirSync, statSync } from "node:fs";
import path from "node:path";

export const TASK_ENV_ROOT = "G:/CODEX/New Manga.workspace/task-envs/P02-NEW-TIME-X6-AC1-AC7";
export const RUN_ROOT = path.join(TASK_ENV_ROOT, "run-r1");
export const PINNED_EXE =
  "G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO/apps/desktop/src-tauri/target/release/m2rc1-desktop.exe";
export const PINNED_EXE_SHA256 =
  "92AC7B8EFB646FE77DF8245B13C9AF9314BEF415B2F0E007B1CDCEA729BC13FD";
export const SOURCE_BASELINE_COMMIT = "49d2a2f9c56462f5602b00ad4b824c5381abb1ab";
export const RUN_ID = "p02-newtime-ac-20261014-r1";
export const CDP_PORT = 9333;

/** Sub-launches dir (all app-visible writable roots live under here). */
export const launchDirs = () => ({
  roaming: path.join(RUN_ROOT, "appdata-roaming"),
  localAppData: path.join(RUN_ROOT, "appdata-local"),
  tmp: path.join(RUN_ROOT, "tmp"),
  dataRoot: path.join(RUN_ROOT, "data-root"),
  derived: path.join(RUN_ROOT, "scope", "derived"),
  managed: path.join(RUN_ROOT, "scope", "managed"),
  catalogDb: path.join(RUN_ROOT, "catalog", "catalog.sqlite"),
  webview2Udd: path.join(RUN_ROOT, "webview2-udd"),
  logs: path.join(RUN_ROOT, "logs"),
});

/**
 * Safety precondition: every Task-local target that the app will create or
 * write must be absent or EMPTY before launch. Returns the observed state
 * so callers can freeze it as evidence. Anything unexpected -> throw.
 */
export function assertLaunchTargetsClean() {
  const dirs = launchDirs();
  const observed = {};
  for (const [name, target] of Object.entries(dirs)) {
    if (!existsSync(target)) {
      observed[name] = { path: target, state: "ABSENT" };
      continue;
    }
    const stat = statSync(target);
    if (!stat.isDirectory()) {
      throw new Error(`PREEXISTING_NON_DIRECTORY: ${name} at ${target}`);
    }
    const entries = readdirSync(target);
    if (entries.length > 0) {
      throw new Error(`PREEXISTING_CONTENTS: ${name} at ${target} has ${entries.length} entries: ${entries.slice(0, 10).join(", ")}`);
    }
    observed[name] = { path: target, state: "EMPTY_DIR" };
  }
  return observed;
}

/** Build the isolated launch environment (purge first, then pin). */
export function buildLaunchEnv() {
  const dirs = launchDirs();
  const env = {};
  for (const [key, value] of Object.entries(process.env)) {
    if (
      key.startsWith("M2RC1_") ||
      key.startsWith("M2RC2_") ||
      key.startsWith("M2AC1_") ||
      key.startsWith("NEWMANGA_")
    ) {
      continue;
    }
    env[key] = value;
  }
  // Minimal sane Windows env even if the host shell lacked one.
  if (!env.SystemRoot) env.SystemRoot = process.env.SystemRoot || "C:\\Windows";
  if (!env.PATH) env.PATH = process.env.PATH || "";

  // --- Task-local isolation pins (all under run-r1) ---
  env.M2RC1_PACKAGED = "1"; // unambiguous packaged-mode switch (frozen sidecar)
  env.APPDATA = dirs.roaming;
  env.LOCALAPPDATA = dirs.localAppData;
  env.TEMP = dirs.tmp;
  env.TMP = dirs.tmp;
  env.NEWMANGA_DATA_ROOT = dirs.dataRoot;
  env.M2RC1_DERIVED_ROOT = dirs.derived;
  env.M2RC1_MANAGED_ROOT = dirs.managed;
  env.M2RC2_CATALOG_DB = dirs.catalogDb;
  env.WEBVIEW2_USER_DATA_FOLDER = dirs.webview2Udd;
  env.WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS = `--remote-debugging-port=${CDP_PORT}`;
  // Deliberately NOT set: M2RC1_PROBE_OUT (probe mode), M2AC1_TEST_MODE
  // (ac1 mode), M2RC1_SRC_ROOT (would force dev mode), M2RC1_FIXTURES.
  return env;
}

/** Non-secret env manifest for evidence files. */
export function envEvidenceManifest(env) {
  const pinned = [
    "M2RC1_PACKAGED",
    "APPDATA",
    "LOCALAPPDATA",
    "TEMP",
    "TMP",
    "NEWMANGA_DATA_ROOT",
    "M2RC1_DERIVED_ROOT",
    "M2RC1_MANAGED_ROOT",
    "M2RC2_CATALOG_DB",
    "WEBVIEW2_USER_DATA_FOLDER",
    "WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS",
  ];
  const manifest = {};
  for (const key of pinned) manifest[key] = env[key];
  manifest.__purgedPrefixes = ["M2RC1_*", "M2RC2_*", "M2AC1_*", "NEWMANGA_*"];
  manifest.__neverSet = ["M2RC1_PROBE_OUT", "M2AC1_TEST_MODE", "M2RC1_SRC_ROOT", "M2RC1_PROBE_LOG"];
  return manifest;
}
