# AC4 prepare 写域边界检查

测试：tests/pipeline/test_fea00a_source_boundaries.py。采用 inspect.getsource 对真实 RegionStepWriter._persist 与 ArtifactStepWriter.prepare_revision 检查 SQL/API 字符串边界。

- Region prepare 必须 INSERT step_result_candidates 并写 status=prepared；断言没有 INSERT region_revisions 或 UPDATE regions。
- Artifact prepare 必须调用 write_temp 与 verify_temp；断言没有 INSERT/UPDATE media_artifacts、INSERT artifact_revisions 或 storage.publish；并核对冻结字段及排除 revision_no。
- 原始命令与逐测试结果：prepare-boundary-checks.log（PowerShell 7.6.8，EXIT=0，2 passed）。
