$psVer = $PSVersionTable.PSVersion.ToString()
$cmd = "powershell -NoProfile -ExecutionPolicy Bypass -File verification/P03-PACKAGED-SFX-ENTRY/revision-2/preflight.ps1"
$k07Path = "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/regions/K07_R123.png"
$k07Expected = "28dab503aca3c903111488c03e857b430d309421a4a54bab335a63bbe7b9cec4"
$weightsPath = "G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights-v2b/yolo11s-seg.onnx"
$weightsExpected = "944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d"

$k07Item = Get-Item $k07Path
$k07Bytes = $k07Item.Length
$k07Actual = (Get-FileHash $k07Path -Algorithm SHA256).Hash.ToLower()
$k07Match = $k07Actual -eq $k07Expected

$weightsItem = Get-Item $weightsPath
$weightsBytes = $weightsItem.Length
$weightsActual = (Get-FileHash $weightsPath -Algorithm SHA256).Hash.ToLower()
$weightsMatch = $weightsActual -eq $weightsExpected

$exitCode = if ($k07Match -and $weightsMatch) { 0 } else { 1 }

$out = @"
PowerShell Version: $psVer
Command: $cmd
Timestamp: $(Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz')

1. K07 Anchor Page:
   Path: $k07Path
   Exists: $($k07Item.Exists)
   Bytes: $k07Bytes
   Expected SHA-256: $k07Expected
   Actual SHA-256:   $k07Actual
   Match: $k07Match

2. SFX v2b Pinned Weights:
   Path: $weightsPath
   Exists: $($weightsItem.Exists)
   Bytes: $weightsBytes
   Expected SHA-256: $weightsExpected
   Actual SHA-256:   $weightsActual
   Match: $weightsMatch

Preflight Verdict: $(if ($exitCode -eq 0) { "PASS" } else { "FAIL" })
EXIT=$exitCode
"@

$out | Out-File -FilePath 'verification/P03-PACKAGED-SFX-ENTRY/revision-2/00-input-preflight.log' -Encoding utf8
Write-Output $out
exit $exitCode
