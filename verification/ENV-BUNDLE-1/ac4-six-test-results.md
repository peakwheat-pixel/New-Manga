# AC4：六项此前失败用例

环境：PowerShell；M2RC1_PYTHON=G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe（Python 3.12.3）；M2RC1_SRC_ROOT 与 M2RC1_PACKAGED 在本次运行中均未设置。完整日志：ac4-cargo-test.log。

| 用例 | 本次结果 |
|---|---|
| library_bridge::tests::real_core_sidecar_answers_startup_ping_on_fresh_catalog | PASS |
| library_bridge::tests::same_channel_concurrent_round_trips_keep_response_ownership | PASS |
| tests::real_core_sidecar_rc4_commands_round_trip_typed_errors | PASS |
| tests::real_core_sidecar_retype_pair_empty_page_and_typed_rejection | PASS |
| tests::real_core_sidecar_settings_round_trip_and_typed_rejection | PASS |
| tests::real_library_sidecar_round_trip_and_eof | PASS |

整套 Cargo 结果：76 passed / 0 failed / 1 ignored / exit 0。唯一 ignored 是源码中既有的 perf_chunk_request_digest_cost，没有新增 skip 或改动断言。

基线核对：用户提供的 bl11-cargo-test.log 列出的六项里，五项为 PROTOCOL_VERSION_UNSUPPORTED / CORE_UNAVAILABLE；same_channel_concurrent_round_trips_keep_response_ownership 实际因 M2RC1_PYTHON 未设置而失败，并非协议错误。本次显式设置批准解释器后通过。另有真实 frozen core_service.exe 的 2.3 core.ping、ListBooks、core.shutdown 往返证据见 ac4-packaged-core-smoke.log；使用隔离数据目录、精简 PATH、未使用 Python/source-root override。
