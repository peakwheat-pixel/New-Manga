[CmdletBinding()] param([string]$OutputRoot='G:/CODEX/New Manga.workspace/task-envs/RELEASE-PACKAGE-1/out',[string]$Version='0.1.0')
$ErrorActionPreference='Stop'
$root=Resolve-Path (Join-Path $PSScriptRoot '..'); $repo=Resolve-Path (Join-Path $root '..\..')
$stage=Join-Path $OutputRoot "NewManga-$Version-win-x64"
if(Test-Path $stage){Remove-Item $stage -Recurse -Force}
New-Item -ItemType Directory -Force (Join-Path $stage 'app')|Out-Null
Push-Location $root; & dotnet publish src/NewManga.App/NewManga.App.csproj -c Release -r win-x64 --self-contained -p:PublishSingleFile=true -p:PublishTrimmed=true -p:IncludeNativeLibrariesForSelfExtract=true -p:PublishReadyToRun=true -p:EnableCompressionInSingleFile=true -o (Join-Path $stage 'app') 2>&1 | Tee-Object -FilePath (Join-Path $OutputRoot 'publish.log') | Out-Null; if ($LASTEXITCODE -ne 0) { throw 'dotnet publish failed' }; Pop-Location
$lic=@('LICENSE','NOTICE.md','THIRD_PARTY_LICENSES.md')
$licHashes=@{}; foreach($n in $lic){$src=Join-Path $repo $n; $dst=Join-Path $stage $n; Copy-Item $src $dst -Force; $a=(Get-FileHash $src -Algorithm SHA256).Hash.ToLower(); $b=(Get-FileHash $dst -Algorithm SHA256).Hash.ToLower(); if($a -ne $b){throw "license mismatch $n"}; $licHashes[$n]=$a}
@('install.ps1','uninstall.ps1','migrate-legacy-dryrun.ps1')|ForEach-Object{Copy-Item (Join-Path $PSScriptRoot $_) (Join-Path $stage $_) -Force}
$docs=Join-Path $root 'docs'; Copy-Item (Join-Path $docs 'MANUAL_VERIFY.md') $stage -Force; Copy-Item (Join-Path $docs 'UPGRADE.md') $stage -Force; Copy-Item (Join-Path $docs 'LICENSE_AUDIT.md') $stage -Force
@{version=$Version;channel='stable';data_root='%APPDATA%\com.newmanga.desktop';models='not_bundled (model separation: %APPDATA%\com.newmanga.desktop\models)';migration='runtime dry-run script included'} | ConvertTo-Json | Set-Content (Join-Path $stage 'VERSION.json') -Encoding utf8
$files=Get-ChildItem $stage -Recurse -File; $bytes=($files|Measure-Object Length -Sum).Sum
$manifest=[ordered]@{package="NewManga-$Version-win-x64";version=$Version;bytes=$bytes;files=@();licenses=$licHashes}
foreach($f in $files){$manifest.files+=@{path=$f.FullName.Substring($stage.Length+1).Replace('\','/');bytes=$f.Length;sha256=(Get-FileHash $f.FullName -Algorithm SHA256).Hash.ToLower()}}
$manifest|ConvertTo-Json -Depth 5|Set-Content (Join-Path $stage 'package-manifest.json') -Encoding utf8
$zip=Join-Path $OutputRoot "NewManga-$Version-win-x64.zip"; if(Test-Path $zip){Remove-Item $zip -Force}
Compress-Archive -Path (Join-Path $stage '*') -DestinationPath $zip -CompressionLevel Optimal
$zipBytes=(Get-Item $zip).Length; if($zipBytes -gt 150MB){throw "package exceeds 150MB: $zipBytes"}
$summary=[ordered]@{ac='AC1/AC3';version=$Version;zip=$zip;zip_bytes=$zipBytes;zip_mb=[math]::Round($zipBytes/1MB,2);uncompressed_bytes=$bytes;file_count=$files.Count;licenses_byte_identical=$true;license_hashes=$licHashes;models='separated';generated_at_utc=[DateTime]::UtcNow.ToString('o')}
$summary|ConvertTo-Json -Depth 4|Set-Content (Join-Path $OutputRoot 'package-summary.json') -Encoding utf8
$summary|ConvertTo-Json -Depth 4
