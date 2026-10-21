$ErrorActionPreference = 'Stop'
$script:log = @()
function Log([string]$m) {
    $line = ("[{0}] {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m)
    $script:log += $line
    try { Add-Content -LiteralPath 'C:\out\sandbox-progress.txt' -Value $line -Encoding utf8 } catch {}
}

function Get-MangaUninstallEntries {
    $paths = @(
        'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall',
        'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall',
        'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall'
    )
    $out = @()
    foreach ($p in $paths) {
        if (Test-Path $p) {
            foreach ($k in Get-ChildItem $p -ErrorAction SilentlyContinue) {
                $props = Get-ItemProperty $k.PSPath -ErrorAction SilentlyContinue
                if ($props -and $props.DisplayName -like '*m2rc1*') { $out += $props }
            }
        }
    }
    return $out
}

try {
    $out = 'C:\out'
    $inst = 'C:\installer\m2rc1-desktop_0.1.0_x64-setup.exe'
    $os = Get-CimInstance Win32_OperatingSystem
    Log "sandbox_os=$($os.Caption) build=$($os.BuildNumber) user=$env:USERNAME"
    Log "installer_exists=$(Test-Path $inst) installer_bytes=$((Get-Item $inst).Length)"
    Log "installer_sha256=$((Get-FileHash $inst -Algorithm SHA256).Hash.ToLowerInvariant())"

    $pre = @(Get-MangaUninstallEntries)
    Log "pre_install_uninstall_entries=$($pre.Count)"
    foreach ($e in $pre) { Log "pre_entry DisplayName=$($e.DisplayName) version=$($e.DisplayVersion) location=$($e.InstallLocation)" }

    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    $pr = [Security.Principal.WindowsPrincipal]::new($id)
    Log "is_admin=$($pr.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) user=$($id.Name)"
    Log "localappdata=$env:LOCALAPPDATA"
    $free = [math]::Round((Get-PSDrive C).Free / 1GB, 2)
    Log "c_free_gb=$free"
    foreach ($p in @(
        'HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}',
        'HKLM:\SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}',
        'HKCU:\SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}')) {
        if (Test-Path $p) { Log "webview2_registry=$p pv=$((Get-ItemProperty $p).pv)" }
    }

    $local = 'C:\setup.exe'
    Copy-Item -LiteralPath $inst -Destination $local -Force
    try { Unblock-File -LiteralPath $local -ErrorAction SilentlyContinue } catch {}
    Log "local_copy_exists=$(Test-Path $local) sha256=$((Get-FileHash $local -Algorithm SHA256).Hash.ToLowerInvariant())"

    Log 'install_start'
    $p = Start-Process -FilePath $local -ArgumentList '/S' -Wait -PassThru
    Log "install_exit=$($p.ExitCode)"
    Log "webview2_bootstrapper_temp_exists=$(Test-Path "$env:TEMP\MicrosoftEdgeWebview2Setup.exe")"
    Start-Sleep -Seconds 5

    $post = @(Get-MangaUninstallEntries)
    Log "post_install_uninstall_entries=$($post.Count)"
    foreach ($e in $post) {
        Log "post_entry key=$($e.PSChildName) DisplayName=$($e.DisplayName) version=$($e.DisplayVersion) location=$($e.InstallLocation) uninstall=$($e.UninstallString)"
    }

    $loc = ($post | Where-Object { $_.InstallLocation } | Select-Object -First 1).InstallLocation
    if (-not $loc -or -not (Test-Path $loc)) {
        foreach ($cand in @("$env:LOCALAPPDATA\m2rc1-desktop", "$env:LOCALAPPDATA\Programs\m2rc1-desktop", "$env:ProgramFiles\m2rc1-desktop")) {
            if (Test-Path $cand) { $loc = $cand; break }
        }
    }
    Log "install_location=$loc exists=$(if ($loc) { Test-Path $loc } else { 'n/a' })"

    if ($loc -and (Test-Path $loc)) {
        $files = @(Get-ChildItem $loc -Recurse -File -ErrorAction SilentlyContinue)
        Log "installed_file_count=$($files.Count) installed_bytes=$((($files | Measure-Object Length -Sum).Sum))"
        foreach ($f in @('m2rc1-desktop.exe', 'uninstall.exe')) {
            $fp = Join-Path $loc $f
            $exists = Test-Path $fp
            Log "${f}_exists=$exists"
            if ($exists) { Log "${f}_sha256=$((Get-FileHash $fp -Algorithm SHA256).Hash.ToLowerInvariant()) bytes=$((Get-Item $fp).Length)" }
        }
        $side = @(Get-ChildItem $loc -Recurse -Filter core_service.exe -ErrorAction SilentlyContinue | Select-Object -First 1)
        if ($side.Count -gt 0) {
            Log "core_service_exists=True path=$($side[0].FullName) bytes=$($side[0].Length) sha256=$((Get-FileHash $side[0].FullName -Algorithm SHA256).Hash.ToLowerInvariant())"
        } else {
            Log 'core_service_exists=False'
        }
        $u = Join-Path $loc 'uninstall.exe'
        if (Test-Path $u) {
            Log 'uninstall_start'
            $up = Start-Process -FilePath $u -ArgumentList '/S' -Wait -PassThru
            Log "uninstall_exit=$($up.ExitCode)"
            $gone = $false
            for ($i = 0; $i -lt 30; $i++) {
                Start-Sleep -Seconds 1
                if (-not (Test-Path $loc)) { $gone = $true; break }
            }
            Log "post_uninstall_location_exists=$(-not $gone)"
            $after = @(Get-MangaUninstallEntries)
            Log "post_uninstall_entries=$($after.Count)"
        } else {
            Log 'uninstaller_missing=True'
        }
    } else {
        Log 'installed_files_missing=True'
    }
    Log 'DONE_OK'
} catch {
    Log "ERROR=$($_.Exception.Message)"
    Log 'DONE_ERROR'
}
$script:log | Out-File 'C:\out\sandbox-result.txt' -Encoding utf8
'DONE' | Out-File 'C:\out\sandbox-done.txt' -Encoding ascii
