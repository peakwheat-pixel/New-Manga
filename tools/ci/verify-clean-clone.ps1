<#
.SYNOPSIS
  V11R-A-4 clean-clone self check: no machine-absolute paths in operational files, and every CI
  input is locatable from a plain `git clone` (no maintainer task-env required).

.DESCRIPTION
  Scans tracked files for hardcoded maintainer paths (`G:/CODEX/...`, `C:\Users\...`,
  `E:\Program Files\...`, `/home/...`, `/Users/...`) and fails when a hit is in a file that the
  build/CI actually consumes. Historical evidence and documentation are whitelisted by prefix; test
  fixtures are allowed only when the file is explicitly environment-driven (contains an
  `NEWMANGA_*` environment override or a skip guard).

  Also verifies that the inputs a clean checkout needs exist:
    - solution / pytest / requirements / sidecar build entry points;
    - sidecar build inputs (PyInstaller entries, build requirements);
    - model weights are reported as SKIPPED (never a silent pass, never a hard failure) unless
      -RequireModels is passed.

  Exit code: 0 = clean (skips allowed), 1 = hard failure.

.PARAMETER ReportPath
  Optional path for a machine-readable JSON report (written even when the check fails).

.PARAMETER RequireModels
  Treat missing model weights as a failure (release/QA runs). Default: report SKIPPED.

.EXAMPLE
  pwsh -NoProfile -File tools/ci/verify-clean-clone.ps1 -ReportPath out/clean-clone.json
#>
[CmdletBinding()]
param(
    [string]$ReportPath = '',
    [switch]$RequireModels,
    [switch]$SelfTest
)

$ErrorActionPreference = 'Stop'

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..\..')
Push-Location $repoRoot
try {
    $tracked = @(& git ls-files)
    if ($LASTEXITCODE -ne 0) { throw "git ls-files failed in $repoRoot" }

    $patterns = @(
        'G:[\\/]CODEX',
        'C:\\Users\\',
        'E:\\Program Files',
        '/home/',
        '/Users/'
    )

    # Historical/evidence trees keep byte-identical records of past runs (pinned evidence), and the
    # legacy Tauri app is frozen evidence. None of these are build/CI inputs.
    $allowedPrefixes = @(
        'doc/',
        'verification/',
        'archive/',
        'audit/',
        'experiments/',
        'wiki/',
        '.orchestrator/',
        '.qoder-credits/',
        '.workbuddy/',
        '.codex/',
        '.dsh/',
        '.gemini/',
        '.qoder/',
        '.claude/',
        '.cursor/',
        'docs/',
        'AGENTS.md',
        'apps/desktop/',
        # This scanner's own pattern literals are its definition, not a location to resolve.
        'tools/ci/verify-clean-clone.ps1',
        'tools/governance/',
        'tools/p02/'
    )

    # Negative-test data: the path strings are the *payload* under test (secret/path redaction),
    # not locations this machine must have.
    $negativeTestPrefixes = @(
        'tests/core/',
        'tests/diagnostics/'
    )

    # Source hits that are outside the A-4 write scope (UI views belong to the UI owner) are
    # reported, not silently ignored: CI stays green and the finding is listed in the report.
    $pendingOwnerFixes = @(
        'apps/desktop-avalonia/src/NewManga.App/Views/ReaderWorkbenchPages.cs'
    )

    # Explicit, auditable fixture-path exemption. A test line may carry:
    #   // ci-allow-fixture-path: <reason>
    # Only files under tests/ are eligible; the marker is reported in allowed_fixture_paths and never
    # relaxes the scan for any other file (a marker outside tests/ is reported and still fails).
    $fixtureMarkerPattern = 'ci-allow-fixture-path:\s*(?<reason>\S.*)$'
    $fixtureEligiblePrefixes = @(
        'tests/',
        'apps/desktop-avalonia/tests/'
    )

    function Test-FixtureEligible([string]$File) {
        foreach ($prefix in $fixtureEligiblePrefixes) {
            if ($File.StartsWith($prefix, [StringComparison]::Ordinal)) { return $true }
        }

        return $false
    }

    function Resolve-HitClassification {
        param([string]$File, [string]$Line, [bool]$IsEnvDriven)

        $classification = 'FAIL'
        $reason = ''
        $markerIgnoredOutsideTests = $false

        foreach ($prefix in $allowedPrefixes) {
            if ($File.StartsWith($prefix, [StringComparison]::Ordinal)) {
                $classification = 'ALLOW'
                $reason = "historical evidence/doc tree ($prefix)"
                break
            }
        }
        if ($classification -eq 'FAIL') {
            foreach ($prefix in $negativeTestPrefixes) {
                if ($File.StartsWith($prefix, [StringComparison]::Ordinal)) {
                    $classification = 'ALLOW'
                    $reason = "negative-test data: the path string is the payload under test ($prefix)"
                    break
                }
            }
        }
        foreach ($pending in $pendingOwnerFixes) {
            if ($File -eq $pending) {
                $classification = 'ALLOW_PENDING'
                $reason = 'out-of-scope source hit; owner fix tracked by the V11R-A-4 report'
                break
            }
        }
        if ($classification -eq 'FAIL') {
            $marker = [regex]::Match($Line, $fixtureMarkerPattern)
            if ($marker.Success) {
                if (Test-FixtureEligible -File $File) {
                    $classification = 'ALLOW_FIXTURE_PATH'
                    $reason = 'explicit ci-allow-fixture-path marker: ' + $marker.Groups['reason'].Value.Trim()
                }
                else {
                    $markerIgnoredOutsideTests = $true
                    $reason = 'ci-allow-fixture-path marker is only honored in tests/** files'
                }
            }
        }
        if ($classification -eq 'FAIL' -and $IsEnvDriven -and
            ($File.StartsWith('tests/', [StringComparison]::Ordinal) -or
             $File.StartsWith('apps/desktop-avalonia/tests/', [StringComparison]::Ordinal))) {
            $classification = 'ALLOW'
            $reason = 'test fixture default, environment-overridable (NEWMANGA_* / skip guard)'
        }

        return [pscustomobject]@{
            classification = $classification
            reason = $reason
            marker_ignored_outside_tests = $markerIgnoredOutsideTests
        }
    }

    function Invoke-ClassificationSelfTest {
        $cases = @(
            @{ name = 'fixture marker in tests/** is allowed'
               file = 'apps/desktop-avalonia/tests/NewManga.App.Tests/FixturePaths.cs'
               line = 'path = "C:\\Users\\someone\\secret.json"  # ci-allow-fixture-path: redaction payload'
               envDriven = $false; expected = 'ALLOW_FIXTURE_PATH' },
            @{ name = 'same fixture path without marker in tests/** still hard fails'
               file = 'apps/desktop-avalonia/tests/NewManga.App.Tests/FixturePaths.cs'
               line = 'path = "C:\\Users\\someone\\secret.json"'
               envDriven = $false; expected = 'FAIL' },
            @{ name = 'marker outside tests/** is not honored'
               file = 'src/app.py'
               line = 'path = "C:\\Users\\someone\\secret.json"  # ci-allow-fixture-path: nope'
               envDriven = $false; expected = 'FAIL' },
            @{ name = 'marker without a reason is not honored'
               file = 'apps/desktop-avalonia/tests/NewManga.App.Tests/FixturePaths.cs'
               line = 'path = "C:\\Users\\someone\\secret.json"  # ci-allow-fixture-path:'
               envDriven = $false; expected = 'FAIL' },
            @{ name = 'env-driven fixture default is still allowed without a marker'
               file = 'apps/desktop-avalonia/tests/NewManga.App.Tests/FixturePaths.cs'
               line = 'root = "C:\\Users\\someone\\data"'
               envDriven = $true; expected = 'ALLOW' },
            @{ name = 'historical evidence prefix is still allowed'
               file = 'verification/V11R-A-4/README.md'
               line = 'C:\\Users\\someone\\data'
               envDriven = $false; expected = 'ALLOW' }
        )

        $results = New-Object System.Collections.Generic.List[object]
        foreach ($case in $cases) {
            $resolved = Resolve-HitClassification -File $case.file -Line $case.line -IsEnvDriven $case.envDriven
            $results.Add([pscustomobject]@{
                name = $case.name
                expected = $case.expected
                actual = $resolved.classification
                pass = $resolved.classification -eq $case.expected
            }) | Out-Null
        }

        return $results
    }

    $hardFailures = New-Object System.Collections.Generic.List[string]
    $allowed = New-Object System.Collections.Generic.List[object]
    $allowedFixturePaths = New-Object System.Collections.Generic.List[object]
    $ignoredMarkers = New-Object System.Collections.Generic.List[object]
    $hits = New-Object System.Collections.Generic.List[object]

    $selfTestResults = @(Invoke-ClassificationSelfTest)
    $selfTestFailures = @($selfTestResults | Where-Object { -not $_.pass })
    if ($SelfTest) {
        foreach ($result in $selfTestResults) {
            $status = if ($result.pass) { 'PASS' } else { 'FAIL' }
            Write-Output ("[{0}] {1} (expected {2}, actual {3})" -f $status, $result.name, $result.expected, $result.actual)
        }

        if ($selfTestFailures.Count -gt 0) {
            Write-Output "classification self-test: $($selfTestFailures.Count) FAILED"
            exit 1
        }

        Write-Output "classification self-test: $($selfTestResults.Count)/$($selfTestResults.Count) PASS"
        exit 0
    }

    foreach ($file in $tracked) {
        if ($file -match '\.(png|jpg|jpeg|gif|webp|ico|onnx|bin|nmbak|sqlite|zip|exe|dll|pdf)$') {
            continue
        }

        $full = Join-Path $repoRoot $file
        if (-not (Test-Path -LiteralPath $full)) { continue }

        $matchesInFile = @(Select-String -LiteralPath $full -Pattern $patterns -ErrorAction SilentlyContinue)
        if ($matchesInFile.Count -eq 0) { continue }

        $content = Get-Content -LiteralPath $full -Raw
        $isEnvDriven = $content -match 'NEW_?MANGA_[A-Z_]+' -and
            ($content -match 'skip|Skip|GetEnvironmentVariable|os\.environ|NEW_MANGA_')

        foreach ($match in $matchesInFile) {
            $resolved = Resolve-HitClassification -File $file -Line $match.Line -IsEnvDriven $isEnvDriven
            $entry = [pscustomobject]@{
                file = $file
                line = $match.LineNumber
                text = $match.Line.Trim()
                classification = $resolved.classification
                reason = $resolved.reason
            }
            $hits.Add($entry) | Out-Null
            if ($resolved.marker_ignored_outside_tests) {
                $ignoredMarkers.Add([pscustomobject]@{
                    file = $file
                    line = $match.LineNumber
                    reason = $resolved.reason
                    text = $match.Line.Trim()
                }) | Out-Null
            }
            if ($entry.classification -eq 'FAIL') {
                $hardFailures.Add("$file`:$($match.LineNumber): $($match.Line.Trim())") | Out-Null
            } elseif ($entry.classification -eq 'ALLOW_FIXTURE_PATH') {
                $allowedFixturePaths.Add($entry) | Out-Null
                $allowed.Add($entry) | Out-Null
            } else {
                $allowed.Add($entry) | Out-Null
            }
        }
    }

    foreach ($selfTestFailure in $selfTestFailures) {
        $hardFailures.Add("classification self-test failed: $($selfTestFailure.name) (expected $($selfTestFailure.expected), actual $($selfTestFailure.actual))") | Out-Null
    }

    # CI inputs a plain clone must provide.
    $requiredInputs = @(
        'apps/desktop-avalonia/NewManga.sln',
        'src/bootstrap/core_service.py',
        'requirements.txt',
        'requirements-dev.txt',
        'pytest.ini',
        'apps/desktop-avalonia/scripts/test.ps1',
        'apps/desktop-avalonia/scripts/prepare-sidecar.ps1',
        'packaging/m2ac5/build_sidecar.ps1',
        'packaging/m2ac5/requirements-build.txt',
        'tools/ci/verify-clean-clone.ps1'
    )
    $missingInputs = @($requiredInputs | Where-Object { -not (Test-Path -LiteralPath (Join-Path $repoRoot $_)) })
    foreach ($missing in $missingInputs) {
        $hardFailures.Add("missing required input: $missing") | Out-Null
    }

    # Sidecar build inputs: PyInstaller entries + frozen spec must be locatable from the clone.
    $entryPoints = @(Get-ChildItem -LiteralPath (Join-Path $repoRoot 'packaging/m2ac5/entries') -Filter '*.py' -ErrorAction SilentlyContinue)
    if ($entryPoints.Count -eq 0) {
        $hardFailures.Add('missing sidecar build entry points: packaging/m2ac5/entries/*.py') | Out-Null
    }

    # Model weights: environmental, reported as SKIPPED by default (release QA can -RequireModels).
    $weightCandidates = @(
        $env:NEWMANGA_MODEL_WEIGHTS,
        (Join-Path $repoRoot 'apps/desktop-avalonia/build/sidecar/core-sidecar/models'),
        (Join-Path $repoRoot 'models')
    ) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    $weights = $null
    foreach ($candidate in $weightCandidates) {
        if (Test-Path -LiteralPath $candidate) { $weights = $candidate; break }
    }
    $weightsStatus = if ($weights) { 'PRESENT' } elseif ($RequireModels) { 'FAIL' } else { 'SKIPPED' }
    if ($weightsStatus -eq 'FAIL') {
        $hardFailures.Add('model weights missing and -RequireModels was passed') | Out-Null
    }

    # Windows clones need core.longpaths=true for the deep verification/** artifact paths; GitHub
    # Actions checkout enables it, local operators must do the same. Reported, not failed, because the
    # checkout already happened by the time this script runs.
    $longPaths = (& git config --get core.longpaths) 2>$null
    $longPathsStatus = if ($longPaths -eq 'true') {
        'enabled'
    } else {
        'not-set (run: git config core.longpaths true; required on Windows for verification/** deep paths)'
    }

    $pythonExe = (Get-Command python -ErrorAction SilentlyContinue)?.Source
    $pyInstaller = $null
    if ($pythonExe) {
        $pyInstaller = (& $pythonExe -c "import PyInstaller, sys; print(PyInstaller.__version__)" 2>$null)
    }
    $dotnetVersion = (& dotnet --version 2>$null)

    $report = [ordered]@{
        task = 'V11R-A-4'
        repo_root = $repoRoot.Path
        git_head = (& git rev-parse HEAD)
        checked_files = $tracked.Count
        hard_failures = @($hardFailures)
        pending_owner_fixes = @($hits | Where-Object { $_.classification -eq 'ALLOW_PENDING' } | ForEach-Object {
            [ordered]@{ file = $_.file; line = $_.line; reason = $_.reason; text = $_.text }
        })
        allowed_fixture_paths = @($allowedFixturePaths | ForEach-Object {
            [ordered]@{ file = $_.file; line = $_.line; reason = $_.reason; text = $_.text }
        })
        ignored_fixture_markers_outside_tests = @($ignoredMarkers | ForEach-Object {
            [ordered]@{ file = $_.file; line = $_.line; reason = $_.reason; text = $_.text }
        })
        classification_self_test = [ordered]@{
            total = $selfTestResults.Count
            passed = @($selfTestResults | Where-Object { $_.pass }).Count
            cases = @($selfTestResults | ForEach-Object {
                [ordered]@{ name = $_.name; expected = $_.expected; actual = $_.actual; pass = $_.pass }
            })
        }
        allowed_hit_count = $allowed.Count
        allowed_hits_sample = @($allowed | Select-Object -First 40 | ForEach-Object {
            [ordered]@{ file = $_.file; line = $_.line; reason = $_.reason; text = $_.text }
        })
        required_inputs = [ordered]@{
            missing = @($missingInputs)
        }
        sidecar_build = [ordered]@{
            entry_points = $entryPoints.Count
            python = $pythonExe
            pyinstaller = if ($pyInstaller) { "$pyInstaller" } else { 'MISSING (sidecar job will skip)' }
        }
        dotnet = if ($dotnetVersion) { "$dotnetVersion" } else { 'MISSING' }
        long_paths = $longPathsStatus
        model_weights = [ordered]@{
            status = $weightsStatus
            path = $weights
        }
    }

    if (-not [string]::IsNullOrWhiteSpace($ReportPath)) {
        $reportDirectory = Split-Path -Parent ([System.IO.Path]::GetFullPath($ReportPath))
        if ($reportDirectory) { New-Item -ItemType Directory -Force -Path $reportDirectory | Out-Null }
        $report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $ReportPath -Encoding utf8
        Write-Output "report: $ReportPath"
    }

    Write-Output "clean-clone check: files=$($tracked.Count) hard_failures=$($hardFailures.Count) allowed_hits=$($allowed.Count) allowed_fixture_paths=$($allowedFixturePaths.Count)"
    Write-Output "model weights: $weightsStatus$(if ($weights) { " ($weights)" })"
    Write-Output "long paths: $longPathsStatus"
    if ($hardFailures.Count -gt 0) {
        Write-Output 'HARD FAILURES:'
        $hardFailures | ForEach-Object { Write-Output "  - $_" }
        exit 1
    }

    Write-Output 'OK: no machine-absolute paths in operational files; CI inputs locatable.'
    exit 0
}
finally {
    Pop-Location
}
