# AC8：G7 blast-radius outcome 对照

修前证据：baseline-test-log.md，冻结 HEAD c7b9d59e6b55b262c7523fe9dc24b2dbc331afbd 上 12 个相关文件合计 **180 passed / 0 failed / 0 skipped**。该次运行只保存了批次总数，未保存逐文件计数；因此下表的修前栏只声明每个文件被该全绿批次覆盖，不伪造逐文件基线数。修后逐文件使用同一 uv 依赖环境单独复跑，EXIT=0；完整相关回归集见 final-pytest-log.txt（194 passed）。逐文件执行头与结果见 ac8-post-per-file-log.txt。完整测试名来自 ac8-collected-test-names.json。

| 文件 | 测试名 | 修前 | 修后 | 判定 | 理由 |
|---|---|---|---|---|---|
| tests/core/test_bootstrap.py | test_smoke_startup_loads_qml_and_exits_zero | PASS（180 用例基线批次） | PASS（该文件 23 项全通过） | 无回归 | 生产 Core 装配新增 storage 注入；测试夹具通过真实编辑/导入路径建立必要 revision，不再调用已移除的 prepare 期 adopt_current。 |
| tests/core/test_bootstrap.py | test_smoke_assembles_real_stack_in_data_root | PASS（180 用例基线批次） | PASS（该文件 23 项全通过） | 无回归 | 生产 Core 装配新增 storage 注入；测试夹具通过真实编辑/导入路径建立必要 revision，不再调用已移除的 prepare 期 adopt_current。 |
| tests/core/test_bootstrap.py | test_missing_qml_returns_nonzero_with_path | PASS（180 用例基线批次） | PASS（该文件 23 项全通过） | 无回归 | 生产 Core 装配新增 storage 注入；测试夹具通过真实编辑/导入路径建立必要 revision，不再调用已移除的 prepare 期 adopt_current。 |
| tests/core/test_bootstrap.py | test_assemble_services_migrates_schema_and_managed_layout | PASS（180 用例基线批次） | PASS（该文件 23 项全通过） | 无回归 | 生产 Core 装配新增 storage 注入；测试夹具通过真实编辑/导入路径建立必要 revision，不再调用已移除的 prepare 期 adopt_current。 |
| tests/core/test_bootstrap.py | test_assemble_services_injects_and_exports_diagnostics | PASS（180 用例基线批次） | PASS（该文件 23 项全通过） | 无回归 | 生产 Core 装配新增 storage 注入；测试夹具通过真实编辑/导入路径建立必要 revision，不再调用已移除的 prepare 期 adopt_current。 |
| tests/core/test_bootstrap.py | test_assemble_engine_does_not_publish_diagnostics_to_qml | PASS（180 用例基线批次） | PASS（该文件 23 项全通过） | 无回归 | 生产 Core 装配新增 storage 注入；测试夹具通过真实编辑/导入路径建立必要 revision，不再调用已移除的 prepare 期 adopt_current。 |
| tests/core/test_bootstrap.py | test_assemble_services_refuses_newer_schema | PASS（180 用例基线批次） | PASS（该文件 23 项全通过） | 无回归 | 生产 Core 装配新增 storage 注入；测试夹具通过真实编辑/导入路径建立必要 revision，不再调用已移除的 prepare 期 adopt_current。 |
| tests/core/test_bootstrap.py | test_assemble_services_closes_connection_when_qt_assembly_fails | PASS（180 用例基线批次） | PASS（该文件 23 项全通过） | 无回归 | 生产 Core 装配新增 storage 注入；测试夹具通过真实编辑/导入路径建立必要 revision，不再调用已移除的 prepare 期 adopt_current。 |
| tests/core/test_bootstrap.py | test_assemble_services_closes_connection_when_migration_fails | PASS（180 用例基线批次） | PASS（该文件 23 项全通过） | 无回归 | 生产 Core 装配新增 storage 注入；测试夹具通过真实编辑/导入路径建立必要 revision，不再调用已移除的 prepare 期 adopt_current。 |
| tests/core/test_bootstrap.py | test_import_safety_chain | PASS（180 用例基线批次） | PASS（该文件 23 项全通过） | 无回归 | 生产 Core 装配新增 storage 注入；测试夹具通过真实编辑/导入路径建立必要 revision，不再调用已移除的 prepare 期 adopt_current。 |
| tests/core/test_bootstrap.py | test_import_unknown_chapter_fails_copy_and_writes_no_page | PASS（180 用例基线批次） | PASS（该文件 23 项全通过） | 无回归 | 生产 Core 装配新增 storage 注入；测试夹具通过真实编辑/导入路径建立必要 revision，不再调用已移除的 prepare 期 adopt_current。 |
| tests/core/test_bootstrap.py | test_assemble_engine_injects_real_workbench_stack | PASS（180 用例基线批次） | PASS（该文件 23 项全通过） | 无回归 | 生产 Core 装配新增 storage 注入；测试夹具通过真实编辑/导入路径建立必要 revision，不再调用已移除的 prepare 期 adopt_current。 |
| tests/core/test_bootstrap.py | test_production_workbench_region_writes_use_real_editing_service | PASS（180 用例基线批次） | PASS（该文件 23 项全通过） | 无回归 | 生产 Core 装配新增 storage 注入；测试夹具通过真实编辑/导入路径建立必要 revision，不再调用已移除的 prepare 期 adopt_current。 |
| tests/core/test_bootstrap.py | test_navigation_enters_real_workbench_context | PASS（180 用例基线批次） | PASS（该文件 23 项全通过） | 无回归 | 生产 Core 装配新增 storage 注入；测试夹具通过真实编辑/导入路径建立必要 revision，不再调用已移除的 prepare 期 adopt_current。 |
| tests/core/test_bootstrap.py | test_workbench_resolves_managed_original_url | PASS（180 用例基线批次） | PASS（该文件 23 项全通过） | 无回归 | 生产 Core 装配新增 storage 注入；测试夹具通过真实编辑/导入路径建立必要 revision，不再调用已移除的 prepare 期 adopt_current。 |
| tests/core/test_bootstrap.py | test_assemble_engine_registers_reader_export_and_tiled_reader | PASS（180 用例基线批次） | PASS（该文件 23 项全通过） | 无回归 | 生产 Core 装配新增 storage 注入；测试夹具通过真实编辑/导入路径建立必要 revision，不再调用已移除的 prepare 期 adopt_current。 |
| tests/core/test_bootstrap.py | test_navigation_away_from_reader_closes_it | PASS（180 用例基线批次） | PASS（该文件 23 项全通过） | 无回归 | 生产 Core 装配新增 storage 注入；测试夹具通过真实编辑/导入路径建立必要 revision，不再调用已移除的 prepare 期 adopt_current。 |
| tests/core/test_bootstrap.py | test_reader_service_and_tile_cache_live_on_the_data_root | PASS（180 用例基线批次） | PASS（该文件 23 项全通过） | 无回归 | 生产 Core 装配新增 storage 注入；测试夹具通过真实编辑/导入路径建立必要 revision，不再调用已移除的 prepare 期 adopt_current。 |
| tests/core/test_bootstrap.py | test_trash_service_is_assembled_on_the_same_data_root | PASS（180 用例基线批次） | PASS（该文件 23 项全通过） | 无回归 | 生产 Core 装配新增 storage 注入；测试夹具通过真实编辑/导入路径建立必要 revision，不再调用已移除的 prepare 期 adopt_current。 |
| tests/core/test_bootstrap.py | test_assemble_services_injects_production_clean_probe | PASS（180 用例基线批次） | PASS（该文件 23 项全通过） | 无回归 | 生产 Core 装配新增 storage 注入；测试夹具通过真实编辑/导入路径建立必要 revision，不再调用已移除的 prepare 期 adopt_current。 |
| tests/core/test_bootstrap.py | test_production_clean_probe_gates_render_only_planning | PASS（180 用例基线批次） | PASS（该文件 23 项全通过） | 无回归 | 生产 Core 装配新增 storage 注入；测试夹具通过真实编辑/导入路径建立必要 revision，不再调用已移除的 prepare 期 adopt_current。 |
| tests/core/test_bootstrap.py | test_document_import_slot_publishes_a_return_type | PASS（180 用例基线批次） | PASS（该文件 23 项全通过） | 无回归 | 生产 Core 装配新增 storage 注入；测试夹具通过真实编辑/导入路径建立必要 revision，不再调用已移除的 prepare 期 adopt_current。 |
| tests/core/test_bootstrap.py | test_assemble_services_hydrates_bookshelf_viewmodel_with_existing_books | PASS（180 用例基线批次） | PASS（该文件 23 项全通过） | 无回归 | 生产 Core 装配新增 storage 注入；测试夹具通过真实编辑/导入路径建立必要 revision，不再调用已移除的 prepare 期 adopt_current。 |
| tests/core/test_page_catalog_modes.py | test_translated_and_compare_resolve_like_the_reader | PASS（180 用例基线批次） | PASS（该文件 3 项全通过） | 无回归 | 测试种入有效的既有 artifact revision/pointer 夹具，保持 reader/catalog 模式断言且不使用 prepare 期副作用。 |
| tests/core/test_page_catalog_modes.py | test_invalid_paths_stay_diagnosable_not_silent | PASS（180 用例基线批次） | PASS（该文件 3 项全通过） | 无回归 | 测试种入有效的既有 artifact revision/pointer 夹具，保持 reader/catalog 模式断言且不使用 prepare 期副作用。 |
| tests/core/test_page_catalog_modes.py | test_page_catalog_degrades_without_a_locator | PASS（180 用例基线批次） | PASS（该文件 3 项全通过） | 无回归 | 测试种入有效的既有 artifact revision/pointer 夹具，保持 reader/catalog 模式断言且不使用 prepare 期副作用。 |
| tests/pipeline/test_regionless_rebinding.py | test_r0_regionless_page_reocr_all_completed | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，验证 regionless 重规划行为原样通过。 |
| tests/pipeline/test_regionless_rebinding.py | test_r1_backfill_replans_primary_chain_and_clones_secondary | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，验证 regionless 重规划行为原样通过。 |
| tests/pipeline/test_regionless_rebinding.py | test_r2_multiple_regions_all_get_reocr_completed | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，验证 regionless 重规划行为原样通过。 |
| tests/pipeline/test_regionless_rebinding.py | test_r3_translate_all_stops_at_capability_gap_not_lock_changed | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，验证 regionless 重规划行为原样通过。 |
| tests/pipeline/test_regionless_rebinding.py | test_r5_subsequent_run_on_same_page_avoids_duplicate_regions | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，验证 regionless 重规划行为原样通过。 |
| tests/pipeline/test_regionless_rebinding.py | test_n1_tampered_input_refs_triggers_lock_changed_and_zero_write | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，验证 regionless 重规划行为原样通过。 |
| tests/pipeline/test_regionless_rebinding.py | test_n2_region_locked_between_detect_and_ocr | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，验证 regionless 重规划行为原样通过。 |
| tests/pipeline/test_regionless_rebinding.py | test_n3_detector_zero_candidates_completes_without_regions | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，验证 regionless 重规划行为原样通过。 |
| tests/pipeline/test_regionless_rebinding.py | test_n3b_zero_candidates_fail_policy_keeps_invalid_input | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，验证 regionless 重规划行为原样通过。 |
| tests/pipeline/test_regionless_rebinding.py | test_n4_no_ocr_provider_fails_with_provider_not_configured | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，验证 regionless 重规划行为原样通过。 |
| tests/pipeline/test_regionless_rebinding.py | test_n5_page_locked_skips_execution | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，验证 regionless 重规划行为原样通过。 |
| tests/pipeline/test_regionless_rebinding.py | test_n6_primary_soft_deleted_before_ocr | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，验证 regionless 重规划行为原样通过。 |
| tests/pipeline/test_regionless_rebinding.py | test_n7_detect_committed_then_interrupted_then_plan_continue | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，验证 regionless 重规划行为原样通过。 |
| tests/pipeline/test_regionless_rebinding.py | test_multiregion_backfill_fans_out_to_every_detected_region | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，验证 regionless 重规划行为原样通过。 |
| tests/pipeline/test_regionless_rebinding.py | test_backfill_nonwhitelisted_pipeline_error_becomes_typed_failure | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，验证 regionless 重规划行为原样通过。 |
| tests/pipeline/test_regionless_rebinding.py | test_backfill_target_deleted_all_skipped_reaches_terminal | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，验证 regionless 重规划行为原样通过。 |
| tests/pipeline/test_regionless_rebinding.py | test_backfill_single_region_nonsfx_page_decisions_unchanged | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，验证 regionless 重规划行为原样通过。 |
| tests/pipeline/test_regionless_rebinding.py | test_backfill_zero_detected_regions_completes_without_fan_out | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，验证 regionless 重规划行为原样通过。 |
| tests/pipeline/test_regionless_rebinding.py | test_region_added_after_backfill_not_followed_by_current_run | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，验证 regionless 重规划行为原样通过。 |
| tests/pipeline/test_regionless_rebinding.py | test_multiregion_backfill_primary_failure_cancels_remaining_regions | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，验证 regionless 重规划行为原样通过。 |
| tests/pipeline/test_regionless_rebinding.py | test_multiregion_backfill_sfx_default_skip_closes_terminal_accounting | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，验证 regionless 重规划行为原样通过。 |
| tests/pipeline/test_regionless_rebinding.py | test_single_region_nonsfx_redecision_equals_page_level_plan | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，验证 regionless 重规划行为原样通过。 |
| tests/pipeline/test_regionless_rebinding.py | test_sfx_primary_region_gated_by_manual_policy | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，验证 regionless 重规划行为原样通过。 |
| tests/pipeline/test_regionless_rebinding.py | test_projection_fresh_polling_does_not_corrupt_execution | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，验证 regionless 重规划行为原样通过。 |
| tests/providers/test_detect_handler.py | test_page_level_plan_grows_a_leading_detect_unit | PASS（180 用例基线批次） | PASS（该文件 8 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，检测 handler outcome 断言原样通过。 |
| tests/providers/test_detect_handler.py | test_detect_fails_typed_without_a_detector | PASS（180 用例基线批次） | PASS（该文件 8 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，检测 handler outcome 断言原样通过。 |
| tests/providers/test_detect_handler.py | test_detect_lands_candidates_as_regions_and_ocr_advances | PASS（180 用例基线批次） | PASS（该文件 8 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，检测 handler outcome 断言原样通过。 |
| tests/providers/test_detect_handler.py | test_detect_passes_provider_label_for_sfx_dispatch | PASS（180 用例基线批次） | PASS（该文件 8 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，检测 handler outcome 断言原样通过。 |
| tests/providers/test_detect_handler.py | test_detect_reuses_existing_live_regions | PASS（180 用例基线批次） | PASS（该文件 8 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，检测 handler outcome 断言原样通过。 |
| tests/providers/test_detect_handler.py | test_detect_zero_candidates_completes_with_zero_regions | PASS（180 用例基线批次） | PASS（该文件 8 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，检测 handler outcome 断言原样通过。 |
| tests/providers/test_detect_handler.py | test_detect_zero_candidates_fail_policy_keeps_invalid_input | PASS（180 用例基线批次） | PASS（该文件 8 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，检测 handler outcome 断言原样通过。 |
| tests/providers/test_detect_handler.py | test_detect_zero_candidates_unknown_policy_falls_back_to_complete | PASS（180 用例基线批次） | PASS（该文件 8 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，检测 handler outcome 断言原样通过。 |
| tests/providers/test_full_chain.py | test_full_translation_chain_runs_every_step | PASS（180 用例基线批次） | PASS（该文件 4 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，完整链路 outcome 断言原样通过。 |
| tests/providers/test_full_chain.py | test_render_is_the_single_translated_pointer_writer | PASS（180 用例基线批次） | PASS（该文件 4 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，完整链路 outcome 断言原样通过。 |
| tests/providers/test_full_chain.py | test_color_and_term_extract_fail_closed_without_assembly | PASS（180 用例基线批次） | PASS（该文件 4 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，完整链路 outcome 断言原样通过。 |
| tests/providers/test_full_chain.py | test_render_fails_closed_when_clean_is_missing | PASS（180 用例基线批次） | PASS（该文件 4 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，完整链路 outcome 断言原样通过。 |
| tests/providers/test_handlers_pipeline.py | test_ocr_region_writes_only_the_target_region | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 直调 writer 的用例补充真实 pipeline/step id 并断言 artifact candidate staging；pipeline outcome 与人工文本保护断言通过。 |
| tests/providers/test_handlers_pipeline.py | test_ocr_keeps_manual_translation_and_reports_the_hint | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 直调 writer 的用例补充真实 pipeline/step id 并断言 artifact candidate staging；pipeline outcome 与人工文本保护断言通过。 |
| tests/providers/test_handlers_pipeline.py | test_locked_region_is_skipped_and_never_translated | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 直调 writer 的用例补充真实 pipeline/step id 并断言 artifact candidate staging；pipeline outcome 与人工文本保护断言通过。 |
| tests/providers/test_handlers_pipeline.py | test_translate_step_commits_but_render_remains_unwired | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 直调 writer 的用例补充真实 pipeline/step id 并断言 artifact candidate staging；pipeline outcome 与人工文本保护断言通过。 |
| tests/providers/test_handlers_pipeline.py | test_translate_with_identity_binding_echoes_source_text | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 直调 writer 的用例补充真实 pipeline/step id 并断言 artifact candidate staging；pipeline outcome 与人工文本保护断言通过。 |
| tests/providers/test_handlers_pipeline.py | test_translate_without_binding_stays_typed_not_configured | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 直调 writer 的用例补充真实 pipeline/step id 并断言 artifact candidate staging；pipeline outcome 与人工文本保护断言通过。 |
| tests/providers/test_handlers_pipeline.py | test_reinpaint_chain_persists_masks_and_clean_revisions | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 直调 writer 的用例补充真实 pipeline/step id 并断言 artifact candidate staging；pipeline outcome 与人工文本保护断言通过。 |
| tests/providers/test_handlers_pipeline.py | test_run_settings_route_policy_goes_through_the_shared_parser | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 直调 writer 的用例补充真实 pipeline/step id 并断言 artifact candidate staging；pipeline outcome 与人工文本保护断言通过。 |
| tests/providers/test_handlers_pipeline.py | test_run_settings_malformed_route_policy_fails_the_step_loudly | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 直调 writer 的用例补充真实 pipeline/step id 并断言 artifact candidate staging；pipeline outcome 与人工文本保护断言通过。 |
| tests/providers/test_handlers_pipeline.py | test_run_settings_non_mapping_inpaint_section_fails_the_step_loudly | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 直调 writer 的用例补充真实 pipeline/step id 并断言 artifact candidate staging；pipeline outcome 与人工文本保护断言通过。 |
| tests/providers/test_handlers_pipeline.py | test_unimplemented_route_blocks_without_writing_anything | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 直调 writer 的用例补充真实 pipeline/step id 并断言 artifact candidate staging；pipeline outcome 与人工文本保护断言通过。 |
| tests/providers/test_handlers_pipeline.py | test_page_scope_reinpaint_expands_to_regions_and_accumulates_clean | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 直调 writer 的用例补充真实 pipeline/step id 并断言 artifact candidate staging；pipeline outcome 与人工文本保护断言通过。 |
| tests/providers/test_handlers_pipeline.py | test_missing_provider_binding_fails_closed | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 直调 writer 的用例补充真实 pipeline/step id 并断言 artifact candidate staging；pipeline outcome 与人工文本保护断言通过。 |
| tests/providers/test_handlers_pipeline.py | test_stale_region_revision_is_refused_before_any_write | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 直调 writer 的用例补充真实 pipeline/step id 并断言 artifact candidate staging；pipeline outcome 与人工文本保护断言通过。 |
| tests/providers/test_handlers_pipeline.py | test_locked_region_refuses_ocr_and_translation_writes | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 直调 writer 的用例补充真实 pipeline/step id 并断言 artifact candidate staging；pipeline outcome 与人工文本保护断言通过。 |
| tests/providers/test_handlers_pipeline.py | test_stale_artifact_pointer_is_refused_before_publishing | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 直调 writer 的用例补充真实 pipeline/step id 并断言 artifact candidate staging；pipeline outcome 与人工文本保护断言通过。 |
| tests/providers/test_handlers_pipeline.py | test_sfx_translate_region_carries_type_and_maps_output | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 直调 writer 的用例补充真实 pipeline/step id 并断言 artifact candidate staging；pipeline outcome 与人工文本保护断言通过。 |
| tests/providers/test_handlers_pipeline.py | test_plugin_hooks_inside_ocr_run[override] | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 直调 writer 的用例补充真实 pipeline/step id 并断言 artifact candidate staging；pipeline outcome 与人工文本保护断言通过。 |
| tests/providers/test_handlers_pipeline.py | test_plugin_hooks_inside_ocr_run[disabled] | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 直调 writer 的用例补充真实 pipeline/step id 并断言 artifact candidate staging；pipeline outcome 与人工文本保护断言通过。 |
| tests/providers/test_handlers_pipeline.py | test_plugin_hooks_inside_ocr_run[crash] | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 直调 writer 的用例补充真实 pipeline/step id 并断言 artifact candidate staging；pipeline outcome 与人工文本保护断言通过。 |
| tests/providers/test_handlers_pipeline.py | test_plugin_hooks_inside_ocr_run[timeout] | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 直调 writer 的用例补充真实 pipeline/step id 并断言 artifact candidate staging；pipeline outcome 与人工文本保护断言通过。 |
| tests/providers/test_handlers_pipeline.py | test_plugin_hooks_inside_ocr_run[invalid] | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 直调 writer 的用例补充真实 pipeline/step id 并断言 artifact candidate staging；pipeline outcome 与人工文本保护断言通过。 |
| tests/providers/test_handlers_pipeline.py | test_plugin_real_detect_and_export_inputs[detect] | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 直调 writer 的用例补充真实 pipeline/step id 并断言 artifact candidate staging；pipeline outcome 与人工文本保护断言通过。 |
| tests/providers/test_handlers_pipeline.py | test_plugin_real_detect_and_export_inputs[export] | PASS（180 用例基线批次） | PASS（该文件 24 项全通过） | 无回归 | 直调 writer 的用例补充真实 pipeline/step id 并断言 artifact candidate staging；pipeline outcome 与人工文本保护断言通过。 |
| tests/providers/test_retype_redetect_persistence.py | test_p2_redetect_reuses_live_regions_and_keeps_human_retype | PASS（180 用例基线批次） | PASS（该文件 1 项全通过） | 无回归 | 生产 pipeline builder 显式注入 storage，redetect/retype 持久化 outcome 断言通过。 |

## t111_support.py（非 outcome 对照）

tests/providers/t111_support.py 是共享测试装配 helper，不作为独立测试文件计入前后 outcome。仅把 storage 传给 build_production_pipeline，维持使用生产 SQLite catalog 的测试服务装配。

## core_assembly 接线影响面

以下五个相关测试文件均包含在 194 项完整回归集，并单独复跑：

| 文件 | 修后 | 判定 |
|---|---:|---|
| tests/core/test_core_assembly.py | 8 passed | PASS |
| tests/core/test_core_detect.py | 40 passed | PASS |
| tests/core/test_sfx_assembly.py | 19 passed | PASS |
| tests/core/test_sfx_policy_settings.py | 19 passed | PASS |
| tests/pipeline/test_pipeline_production_seam.py | 7 passed | PASS |

逐文件原始输出见 ac8-blast-radius-results.json 与 core-assembly-impact-results.json。这些单文件数字与完整 193 项汇总有重叠，不应相加。
