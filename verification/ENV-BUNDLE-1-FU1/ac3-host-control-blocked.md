# AC3 frozen HostControl result

Status: `BLOCKED` after one real packaged attempt; this is not a `NOT_RUN` result.

The temporary HostControl probe ran against the same frozen `core_service.exe` pinned in [`ac1-bundle-and-frontend-manifest.md`](ac1-bundle-and-frontend-manifest.md), with `M2RC1_PACKAGED=1` and `M2RC1_SRC_ROOT` / `M2RC1_PYTHON` unset. `OpenHostSession` completed. The host then called `StdioLibraryChannel::import_from_path`, which uses `host_issuer.rs` to sign an import grant and sends `RegisterImportSource` to the Core HostControl handler. The returned error was `REF_EXPIRED`, so the subsequent `ImportPages` request did not reach the expected missing-chapter response. The exact assertion and process evidence are in [`ac2-ac3-combined-attempt.log`](ac2-ac3-combined-attempt.log).

The inspected Core registry rejects a grant as expired when `expires_at <= now` **or** `expires_at > now + 300`; the Rust host issuer creates it as `SystemTime::now() + 300.0`. The observed `REF_EXPIRED` is therefore at the Core expiry-validation boundary. A sub-second clock/serialization boundary mismatch is a plausible explanation, but the wire error does not include the timestamps, so the exact skew was not measured. Source references: `src/infrastructure/resource_channel/import_source_refs.py` (`register`) and `apps/desktop/src-tauri/src/host_issuer.rs` (`build_import_grant`).

This task cannot change those product implementations under AC5. The temporary AC3 test was removed from the committed test file; only the six AC2-required packaged tests remain. A separate authorized product-fix task is required before HostControl can be claimed as passing.
