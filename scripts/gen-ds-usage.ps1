$root = Split-Path -Parent $PSScriptRoot
$src = Join-Path $root "apps\desktop-avalonia\src\NewManga.App"
$files = Get-ChildItem $src -Recurse -File -Include *.cs,*.axaml |
  Where-Object { $_.FullName -match "V2[\\/]Studio" }
$tokens = $files | Select-String -Pattern "Nm\.[A-Za-z0-9.]+" -AllMatches |
  ForEach-Object { $_.Matches } | ForEach-Object { $_.Value.ToString() } | Sort-Object -Unique
$classes = $files | Select-String -Pattern '"(studio-[a-z0-9-]+)"' -AllMatches |
  ForEach-Object { $_.Matches } | ForEach-Object { $_.Groups[1].Value.ToString() } | Sort-Object -Unique
$lines = @(
  "# Studio design-system usage (I2c regenerated)",
  "",
  "Tokens referenced: $($tokens.Count)",
  ""
) + ($tokens | ForEach-Object { "- ``$_``" }) + @("", "Studio classes: $($classes.Count)", "") + ($classes | ForEach-Object { "- ``$_``" })
$out = Join-Path $root "verification\V11R-B-3\design-system-usage.md"
$lines | Set-Content $out -Encoding UTF8
Write-Host "tokens=$($tokens.Count) classes=$($classes.Count) -> $out"
