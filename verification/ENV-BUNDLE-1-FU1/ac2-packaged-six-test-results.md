# AC2 packaged scenario results

Command: `cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml packaged_sidecar_tests::real_ -- --nocapture --test-threads=1`.

Environment: PowerShell; `M2RC1_PACKAGED=1`, `M2RC1_SRC_ROOT=<unset>`, `M2RC1_PYTHON=<unset>`. The test module asserts those values and starts only executables under this worktree's frozen bundle. Raw log: [`ac2-packaged-six-tests.log`](ac2-packaged-six-tests.log). Result: `6 passed; 0 failed; 0 ignored; 77 filtered out`; Cargo exit code `0`.

| Packaged scenario (same source-backed scenario name) | Result | Observed assertions |
|---|---|---|
| `real_core_sidecar_round_trip` | PASS | Frozen `catalog_loader.exe` seeded SQLite; frozen `host_bridge.exe` issued/resolved/revoked; post-revoke typed `REF_REVOKED`; shutdown sent on drop. |
| `real_library_sidecar_round_trip_and_eof` | PASS | Frozen Core ping protocol 2.3; empty `ListBooks`; forced child termination surfaced typed `CORE_UNAVAILABLE`. |
| `real_core_sidecar_rc4_commands_round_trip_typed_errors` | PASS | Frozen Core returned `TARGET_NOT_FOUND` for revision list, restore, and rerender requests. |
| `real_core_sidecar_retype_pair_empty_page_and_typed_rejection` | PASS | Unknown page returned an empty regions array; unknown region returned `TARGET_NOT_FOUND/not_found`. |
| `real_core_sidecar_settings_round_trip_and_typed_rejection` | PASS | Legal setting persisted/read back; illegal value returned `INVALID_REQUEST/validation`; prior value remained. |
| `real_core_sidecar_answers_startup_ping_on_fresh_catalog` | PASS | Frozen Core startup ping returned protocol 2.3 and created the fresh catalog. |

The test log prints the absolute frozen executable path, byte size, SHA-256, and launch arguments immediately before each process start. It records `core_service.exe` (`68,717,156` bytes; SHA-256 `896bd56286b25bc8539028d52f3ef991cfbcbda24f93ae6c6d75758a7dbfd842`), `host_bridge.exe` (`1,828,219` bytes; SHA-256 `ca2defdf3ac99f6adf4f90ed2457a7cd81cc799ca10350296a50d0082b01477d`), and `catalog_loader.exe` (`1,826,114` bytes; SHA-256 `44786ca1a6338743099c14d3dd7ae395a1f4d8354ba03a14e1c31ee3e05f130d`).

Two earlier attempts are retained, not counted as the final AC2 result: [`ac2-packaged-tests-attempt-1-compile-failure.log`](ac2-packaged-tests-attempt-1-compile-failure.log) (exit `101`, new test helper used `unwrap_err()` on a non-`Debug` success type; fixed in test code), and [`ac2-ac3-combined-attempt.log`](ac2-ac3-combined-attempt.log) (six AC2 scenarios passed, one temporary AC3 HostControl probe failed with `REF_EXPIRED`, overall exit `101`). The final filtered six-test run is the AC2 result above.
