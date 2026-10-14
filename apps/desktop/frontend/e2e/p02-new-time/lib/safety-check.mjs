/**
 * P02-NEW-TIME-X6-AC1-AC7 — exclusive no-overwrite safety precondition test.
 *
 * Verifies that file copy into canonical verification paths enforces fail-closed
 * exclusive behavior (fs.constants.COPYFILE_EXCL). Tested inside Task-local tmp.
 */

import { copyFileSync, constants, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { launchDirs, RUN_ROOT } from "./env.mjs";

export function runNoOverwriteSafetyCheck(scenarioRoot = RUN_ROOT) {
  const tmpDir = path.join(launchDirs(scenarioRoot).tmp, "no-overwrite-check");
  mkdirSync(tmpDir, { recursive: true });

  const srcFile = path.join(tmpDir, "source.txt");
  const destFile = path.join(tmpDir, "target.txt");

  writeFileSync(srcFile, "ORIGINAL_SOURCE_CONTENT_V1", "utf8");
  writeFileSync(destFile, "PREEXISTING_TARGET_CONTENT_DO_NOT_OVERWRITE", "utf8");

  let caughtError = null;
  try {
    copyFileSync(srcFile, destFile, constants.COPYFILE_EXCL);
  } catch (err) {
    caughtError = err;
  }

  const destContentAfter = readFileSync(destFile, "utf8");
  const isPreserved = destContentAfter === "PREEXISTING_TARGET_CONTENT_DO_NOT_OVERWRITE";
  const isFailClosed = caughtError !== null && (caughtError.code === "EEXIST" || caughtError.message.includes("exists"));

  if (!isFailClosed || !isPreserved) {
    throw new Error(`SAFETY_CHECK_FAILED: COPYFILE_EXCL did not fail-closed on existing file. caught=${caughtError}`);
  }

  return {
    status: "PASS",
    failClosed: true,
    errorCode: caughtError.code,
    preexistingPreserved: isPreserved,
    verifiedPath: destFile,
  };
}

if (process.argv[1] && process.argv[1].endsWith("safety-check.mjs")) {
  const result = runNoOverwriteSafetyCheck();
  console.log(JSON.stringify(result, null, 2));
}
