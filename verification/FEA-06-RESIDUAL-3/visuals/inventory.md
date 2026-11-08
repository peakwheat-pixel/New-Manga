# FEA-06-RESIDUAL-3 visual inventory（opt-in 证据；**像素不作 AC 判据**）

| file | state | raster-size | sha256 | signed_by | signed_at |
|---|---|---|---|---|---|
| 01-shelf-default.png | shelf · 满态（真实投影） | 1280x900 | 8016D8483547991FBAD74C32D847C12A4AA556E36EDA1FDC41FF69CA7E4D2E0E | fea06-residual3-impl | 2026-11-08T12:59:56.1524986+08:00 |
| 02-shelf-readonly.png | shelf · 只读（写入被拒） | 1280x900 | FB8E4EB6D7FD91A858947C1B20FB2D13379C068BE11963EC092CBB0DB64A7CE3 | fea06-residual3-impl | 2026-11-08T12:59:56.1524986+08:00 |
| 03-workbench-page.png | workbench · 页面（画布 + 检查器） | 1280x900 | 7B91D5192B95B707AFE7D8F534E55D3A58479919D6F07F62CC06BE69AF75F03F | fea06-residual3-impl | 2026-11-08T12:59:56.1524986+08:00 |
| 04-workbench-batch-empty.png | workbench · 批量空态（无假数据） | 1280x900 | 8316C81BEDD4C0436821CF06D9A15B5CA81B9F849538AB67503A5B073F6BB01E | fea06-residual3-impl | 2026-11-08T12:59:56.1524986+08:00 |
| 05-workbench-batch-matrix.png | workbench · 批量矩阵七状态（吸顶表头） | 1280x900 | 9FDDECD24C9CF05F0A569B0754AB4D66C170D84BC5FB046C1A0F4668B65F54CC | fea06-residual3-impl | 2026-11-08T12:59:56.1524986+08:00 |
| 06-console-nine-rows.png | console · 9 行 Run 投影 | 1280x900 | EBC304E985597B838A098AFE4AFA47C2FEBA189B6382D65A1CA462C9A596E9EC | fea06-residual3-impl | 2026-11-08T12:59:56.1524986+08:00 |
| 07-reader-single.png | reader · 单页 | 1280x900 | B917EE56E85FC0BE91BF938AB27BB821F8A954D650E035ECF12CFDB665886BB7 | fea06-residual3-impl | 2026-11-08T12:59:56.1524986+08:00 |
| 08-reader-double.png | reader · 双页 | 1280x900 | 2BF1C8A691F2A580D61B082167F8FD86B00AA2F54237CB232BDA3E969F13991D | fea06-residual3-impl | 2026-11-08T12:59:56.1524986+08:00 |
| 09-reader-webtoon.png | reader · webtoon 连续页滚动 | 1280x900 | 3A2211A8B520C33F036132FB168A3E7BA723D9F7BD8AAE81053A933F07B1A3CA | fea06-residual3-impl | 2026-11-08T12:59:56.1524986+08:00 |

- task: FEA-06-RESIDUAL-3
- capture_env: NEWMANGA_CAPTURE_RESIDUAL3_PNGS=1
- note: 运行 `$env:NEWMANGA_CAPTURE_RESIDUAL3_PNGS='1'; dotnet test ... --filter FullyQualifiedName~FluentResidual3VisualEvidenceTests` 可重放；像素不作 AC。
