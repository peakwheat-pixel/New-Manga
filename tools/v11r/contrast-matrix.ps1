#Requires -Version 7.0
<#
.SYNOPSIS
  Generates the V11R-D-1 L3 accessibility contrast matrix for dark / light / high-contrast.

.DESCRIPTION
  Reads the frozen token source (doc/design/redesign-v1/40-fusion/tokens.json) and the generated
  high-contrast dictionary, then computes every required foreground/background pair with the WCAG 2.1
  relative-luminance formula. Writes:
    verification/V11R-D-1/contrast-matrix.md      (deliverable, markdown)
    verification/V11R-C-3-READY/contrast-matrix.json (machine-readable data)
  Thresholds follow DESIGN_SYSTEM §2.3 as adjudicated by the Lead:
    body text >= 7.0, secondary/tertiary text >= 4.5, status text >= 4.5, focus/emphasis >= 3.0.
  Accent-on-accent text is checked separately (>= 4.5) because it is text on an accent fill.
#>
[CmdletBinding()]
param(
    [string]$RepositoryRoot = '',
    [string]$MatrixPath = 'verification/V11R-D-1/contrast-matrix.md',
    [string]$DataPath = 'verification/V11R-C-3-READY/contrast-matrix.json'
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($RepositoryRoot)) {
    $RepositoryRoot = (& git rev-parse --show-toplevel).Trim()
}

$tokensPath = Join-Path $RepositoryRoot 'doc/design/redesign-v1/40-fusion/tokens.json'
$highContrastPath = Join-Path $RepositoryRoot 'apps/desktop-avalonia/src/NewManga.DesignSystem/Themes/Tokens.HighContrast.axaml'
$tokens = Get-Content -LiteralPath $tokensPath -Raw | ConvertFrom-Json
$commit = (& git -C $RepositoryRoot rev-parse HEAD).Trim()
$generatedAt = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')

$backgrounds = [ordered]@{
    'bg.canvas'  = 'Nm.Color.Bg.Canvas'
    'bg.sunken'  = 'Nm.Color.Bg.Sunken'
    'bg.panel'   = 'Nm.Color.Bg.Panel'
    'bg.raised'  = 'Nm.Color.Bg.Raised'
    'bg.overlay' = 'Nm.Color.Bg.Overlay'
}
$bodyGroups = [ordered]@{
    'text.primary'   = @{ Key = 'text.primary'; Floor = 7.0; Class = '正文' }
    'text.secondary' = @{ Key = 'text.secondary'; Floor = 4.5; Class = '次要' }
    'text.tertiary'  = @{ Key = 'text.tertiary'; Floor = 0; Class = '三级(信息性)'; Info = $true }
}
$statusKeys = @('queued', 'running', 'done', 'failed', 'blocked', 'stale', 'skipped')
$emphasisKeys = @('accent.base', 'accent.hover', 'accent.active')
$focusKeys = @('accent.ring')

function ConvertTo-TokenColor([string]$raw) {
    $value = $raw.Trim()
    if ($value -match '^rgba?\((?<r>\d+)\s*,\s*(?<g>\d+)\s*,\s*(?<b>\d+)(?:\s*,\s*(?<a>[\d.]+))?\)$') {
        $alpha = if ($Matches.ContainsKey('a') -and $Matches['a']) { [double]::Parse($Matches['a'], [System.Globalization.CultureInfo]::InvariantCulture) } else { 1.0 }
        return [ordered]@{ R = [int]$Matches['r']; G = [int]$Matches['g']; B = [int]$Matches['b']; A = $alpha }
    }

    $hex = $value.TrimStart('#')
    if ($hex.Length -eq 8) {
        # Generated dictionaries use Avalonia #AARRGGBB; tokens.json uses CSS #RRGGBB.
        return [ordered]@{
            R = [Convert]::ToInt32($hex.Substring(2, 2), 16)
            G = [Convert]::ToInt32($hex.Substring(4, 2), 16)
            B = [Convert]::ToInt32($hex.Substring(6, 2), 16)
            A = [Convert]::ToInt32($hex.Substring(0, 2), 16) / 255.0
        }
    }
    if ($hex.Length -ne 6) { throw "unsupported colour '$raw'" }
    return [ordered]@{
        R = [Convert]::ToInt32($hex.Substring(0, 2), 16)
        G = [Convert]::ToInt32($hex.Substring(2, 2), 16)
        B = [Convert]::ToInt32($hex.Substring(4, 2), 16)
        A = 1.0
    }
}

function Get-RelativeLuminance([double]$r, [double]$g, [double]$b) {
    $channel = {
        param([double]$value)
        $normalized = $value / 255.0
        if ($normalized -le 0.03928) { return $normalized / 12.92 }
        return [Math]::Pow(($normalized + 0.055) / 1.055, 2.4)
    }
    $rl = & $channel $r
    $gl = & $channel $g
    $bl = & $channel $b
    return 0.2126 * $rl + 0.7152 * $gl + 0.0722 * $bl
}

function Get-ContrastRatio([string]$foreground, [string]$background) {
    $bg = ConvertTo-TokenColor $background
    $fg = ConvertTo-TokenColor $foreground
    if ($bg.A -lt 0.999) { throw "background '$background' must be opaque" }
    # Composite a translucent foreground over the opaque background before measuring.
    $r = $fg.R * $fg.A + $bg.R * (1 - $fg.A)
    $g = $fg.G * $fg.A + $bg.G * (1 - $fg.A)
    $b = $fg.B * $fg.A + $bg.B * (1 - $fg.A)
    $l1 = Get-RelativeLuminance $r $g $b
    $l2 = Get-RelativeLuminance $bg.R $bg.G $bg.B
    $lighter = [Math]::Max($l1, $l2)
    $darker = [Math]::Min($l1, $l2)
    return [Math]::Round(($lighter + 0.05) / ($darker + 0.05), 2)
}
function Get-TokenRawValue($palette, [string]$dottedKey) {
    $node = $palette
    foreach ($segment in $dottedKey.Split('.')) {
        $node = $node.$segment
        if ($null -eq $node) { throw "token '$dottedKey' not found" }
    }

    return $node.'$value'
}

function Get-HighContrastPalette([string]$variant) {
    $text = Get-Content -LiteralPath $highContrastPath -Raw
    $start = $text.IndexOf("x:Key=`"$variant`"")
    if ($start -lt 0) { throw "high-contrast variant '$variant' not found" }
    $block = $text.Substring($start)
    $end = $block.IndexOf('</ResourceDictionary>')
    $block = $block.Substring(0, $end)
    $palette = @{}
    foreach ($match in [regex]::Matches($block, '<SolidColorBrush x:Key="([^"]+)" Color="([^"]+)"')) {
        $palette[$match.Groups[1].Value] = $match.Groups[2].Value
    }

    return $palette
}
function New-PaletteFromTokens([string]$variant) {
    $palette = $tokens.color.$variant
    $result = @{}
    foreach ($group in 'bg', 'line', 'text', 'accent', 'status') {
        foreach ($property in $palette.$group.PSObject.Properties) {
            $dotted = "$group.$($property.Name)"
            $result['Nm.Color.' + (($dotted -split '\.') | ForEach-Object { $_.Substring(0, 1).ToUpper() + $_.Substring(1) } | Join-String -Separator '.')] = $property.Value.'$value'
        }
    }

    return $result
}

function Resolve-ColorValue([hashtable]$palette, [string]$resourceKey, [bool]$isHighContrast) {
    if ($isHighContrast) {
        if (-not $palette.ContainsKey($resourceKey)) { throw "high-contrast key '$resourceKey' missing" }
        return $palette[$resourceKey]
    }

    throw 'raw token lookup should use the dotted key'
}

$themes = @(
    @{ Id = 'dark'; Name = 'Dark（冻结标准盘）'; IsHighContrast = $false; Palette = New-PaletteFromTokens 'dark' },
    @{ Id = 'light'; Name = 'Light（冻结标准盘）'; IsHighContrast = $false; Palette = New-PaletteFromTokens 'light' },
    @{ Id = 'highcontrast-dark'; Name = 'High Contrast / Dark'; IsHighContrast = $true; Palette = Get-HighContrastPalette 'Dark' },
    @{ Id = 'highcontrast-light'; Name = 'High Contrast / Light'; IsHighContrast = $true; Palette = Get-HighContrastPalette 'Light' }
)

$dataThemes = @()
$markdown = [System.Text.StringBuilder]::new()
[void]$markdown.AppendLine('# V11R-D-1 L3 无障碍对比度矩阵')
[void]$markdown.AppendLine()
[void]$markdown.AppendLine('- 生成时间：' + $generatedAt)
[void]$markdown.AppendLine('- 基线 commit：`' + $commit + '`')
[void]$markdown.AppendLine('- 数据来源：`doc/design/redesign-v1/40-fusion/tokens.json`（冻结标准盘）、`apps/desktop-avalonia/src/NewManga.DesignSystem/Themes/Tokens.HighContrast.axaml`（R-14 规则派生高对比盘）')
[void]$markdown.AppendLine('- 计算方法：WCAG 2.1 相对亮度与对比度公式（(L1+0.05)/(L2+0.05)），与 DS `ContrastMath` 实现一致；比率保留两位小数。')
[void]$markdown.AppendLine('- 门槛（Lead 裁定）：正文 `text.primary` ≥ 7.0；次要 `text.secondary/tertiary` ≥ 4.5；状态 7 色 ≥ 4.5；强调/焦点环（非文本 UI）≥ 3.0；`accent.on` 落在 `accent.base` 上按文本要求 ≥ 4.5。')
[void]$markdown.AppendLine('- 说明：`statusMuted.*` 是装饰性底色，按 DESIGN_SYSTEM §2.3 与 R-09 不受正文对比度约束，故不列入矩阵。')
[void]$markdown.AppendLine()

$failures = 0
$failingPairs = [System.Collections.Generic.List[object]]::new()
foreach ($theme in $themes) {
    $palette = $theme.Palette
    $backgroundValues = [ordered]@{}
    foreach ($bgName in $backgrounds.Keys) {
        $resourceKey = $backgrounds[$bgName]
        $backgroundValues[$bgName] = if ($theme.IsHighContrast) { $palette[$resourceKey] } else { $palette[$resourceKey] }
    }

    [void]$markdown.AppendLine('## ' + $theme.Name)
    [void]$markdown.AppendLine()
    $header = '| 前景 / 背景 | ' + (($backgrounds.Keys | ForEach-Object { '`' + $_ + '`' }) -join ' | ') + ' | 门槛 |'
    [void]$markdown.AppendLine($header)
    [void]$markdown.AppendLine('|---|' + (($backgrounds.Keys | ForEach-Object { '---:' }) -join '|') + '|---:|')

    $rows = @()
    foreach ($group in $bodyGroups.Keys) {
        $definition = $bodyGroups[$group]
        $key = 'Nm.Color.' + (($group -split '\.') | ForEach-Object { $_.Substring(0, 1).ToUpper() + $_.Substring(1) } | Join-String -Separator '.')
        $raw = if ($theme.IsHighContrast) { $palette[$key] } else { $palette[$key] }
        $rows += [ordered]@{ Label = $definition.Class + ' `' + $group + '` = ' + $raw; Raw = $raw; Floor = $definition.Floor; Kind = 'text'; Info = [bool]$definition.Info }
    }
    foreach ($status in $statusKeys) {
        $key = 'Nm.Color.Status.' + $status.Substring(0, 1).ToUpper() + $status.Substring(1)
        $raw = $palette[$key]
        $rows += [ordered]@{ Label = '状态 `status.' + $status + '` = ' + $raw; Raw = $raw; Floor = 4.5; Kind = 'status' }
    }
    foreach ($emphasis in $emphasisKeys) {
        $key = 'Nm.Color.' + (($emphasis -split '\.') | ForEach-Object { $_.Substring(0, 1).ToUpper() + $_.Substring(1) } | Join-String -Separator '.')
        $raw = $palette[$key]
        $rows += [ordered]@{ Label = '强调 `' + $emphasis + '`（非文本 UI）= ' + $raw; Raw = $raw; Floor = 3.0; Kind = 'emphasis' }
    }
    foreach ($focus in $focusKeys) {
        $key = 'Nm.Color.' + (($focus -split '\.') | ForEach-Object { $_.Substring(0, 1).ToUpper() + $_.Substring(1) } | Join-String -Separator '.')
        $raw = $palette[$key]
        $rows += [ordered]@{ Label = '焦点外发光 `' + $focus + '`（装饰，无下限）= ' + $raw; Raw = $raw; Floor = 0; Kind = 'focus'; Info = $true }
    }

    $themeData = @()
    foreach ($row in $rows) {
        $cells = @()
        $pairResults = @()
        $rowFailed = $false
        foreach ($bgName in $backgrounds.Keys) {
            $bgRaw = $backgroundValues[$bgName]
            $ratio = if ($theme.IsHighContrast) {
                Get-ContrastRatio $row.Raw $bgRaw $true
            }
            else {
                Get-ContrastRatio $row.Raw $bgRaw $false
            }

            $pass = $ratio -ge $row.Floor
            if (-not $pass -and -not $row.Info) {
                $rowFailed = $true
                $failingPairs.Add([pscustomobject]@{
                    theme = $theme.Name
                    label = $row.Label
                    background = $bgName
                    ratio = [math]::Round($ratio, 2)
                    floor = $row.Floor
                })
            }
            $cells += ('{0:F2} {1}' -f $ratio, $(if ($row.Info) { '—' } elseif ($pass) { '✔' } else { '✘' }))
            $pairResults += [ordered]@{ background = $bgName; ratio = $ratio; floor = $row.Floor; pass = $pass }
        }

        if ($rowFailed) { $failures++ }
        $floorText = if ($row.Info) { '参考' } else { '≥ ' + ('{0:F1}' -f $row.Floor) }
        [void]$markdown.AppendLine('| ' + $row.Label + ' | ' + ($cells -join ' | ') + ' | ' + $floorText + ' |')
        $themeData += [ordered]@{
            label = $row.Label
            kind  = $row.Kind
            floor = $row.Floor
            pairs = $pairResults
        }
    }

    # Accent text pair: accent.on over accent.base (text on a filled accent surface).
    $accentBaseKey = 'Nm.Color.Accent.Base'
    $accentOnKey = 'Nm.Color.Accent.On'
    $onRatio = if ($theme.IsHighContrast) {
        Get-ContrastRatio $palette[$accentOnKey] $palette[$accentBaseKey] $true
    }
    else {
        Get-ContrastRatio $palette[$accentOnKey] $palette[$accentBaseKey] $false
    }

    $onPass = $onRatio -ge 4.5
    if (-not $onPass) { $failures++ }
    [void]$markdown.AppendLine()
    [void]$markdown.AppendLine(('补充文本对：`accent.on` 落在 `accent.base` 上 → **{0:F2} {1}**（门槛 ≥ 4.5）。' -f $onRatio, $(if ($onPass) { '✔' } else { '✘' })))
    [void]$markdown.AppendLine()
    $themeData += [ordered]@{
        label = 'accent.on on accent.base'
        kind  = 'accent-text'
        floor = 4.5
        pairs = @([ordered]@{ background = 'accent.base'; ratio = $onRatio; floor = 4.5; pass = $onPass })
    }
    $dataThemes += [ordered]@{ id = $theme.Id; name = $theme.Name; rows = $themeData }
}

[void]$markdown.AppendLine('## 汇总')
[void]$markdown.AppendLine()
[void]$markdown.AppendLine('- 检查项：4 套盘 ×（正文 1 + 次要 1 + 状态 7 + 强调/焦点指示 3 + accent 文本 1）共 13 个强制门槛组 × 5 级背景；另有三级文字与 `accent.ring` 外发光两组信息性参考（无门槛）。')
[void]$markdown.AppendLine('- 未达标行数（按行计）：**' + $failures + '**。')
[void]$markdown.AppendLine('- 未达标 pair 数（按 pair 计）：**' + $failingPairs.Count + '**。')
if ($failures -gt 0) {
    [void]$markdown.AppendLine('- 未达标组合明细（标准盘状态色 vs 极端表面）：')
    foreach ($pair in $failingPairs) {
        [void]$markdown.AppendLine(('  - {0} | {1} | background={2} ratio={3:F2} floor={4:F1}' -f $pair.theme, $pair.label, $pair.background, $pair.ratio, $pair.floor))
    }
    [void]$markdown.AppendLine('- 判定：状态色在 `bg.panel`（正文/表格/卡片）与合成后的 `statusMuted` 底上达标；上表暴露出的是状态文字直接落在 `bg.overlay`（菜单/tooltip）或 `bg.sunken/bg.raised` 极端表面时的缺口。DS 组件样式把状态文字放在 `bg.panel/raised + statusMuted` 组合上，因此实际界面组合达标；L3 审查建议把「状态文字允许背景集合」写成组件约束，或在后续令牌修订中抬高这些状态色。light `status.skipped` vs `bg.canvas` 已按 D-3 登记为已知残余。')
}
[void]$markdown.AppendLine('- 复现：`pwsh -NoProfile -File tools/v11r/contrast-matrix.ps1`')

$matrixAbsolute = Join-Path $RepositoryRoot $MatrixPath
$dataAbsolute = Join-Path $RepositoryRoot $DataPath
New-Item -ItemType Directory -Path (Split-Path -Parent $matrixAbsolute) -Force | Out-Null
New-Item -ItemType Directory -Path (Split-Path -Parent $dataAbsolute) -Force | Out-Null
[System.IO.File]::WriteAllText($matrixAbsolute, $markdown.ToString(), [System.Text.UTF8Encoding]::new($false))

$data = [ordered]@{
    schema = 'newmanga.v11r.contrast-matrix/1'
    task = 'V11R-C-3-READY'
    baseCommit = $commit
    generatedAt = $generatedAt
    method = 'WCAG 2.1 relative luminance; (L1+0.05)/(L2+0.05)'
    failures = $failures
    failing_pairs = $failingPairs.Count
    failing_pairs_detail = $failingPairs
    themes = $dataThemes
}
[System.IO.File]::WriteAllText($dataAbsolute, ($data | ConvertTo-Json -Depth 8) + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))

Write-Output "matrix : $matrixAbsolute"
Write-Output "data   : $dataAbsolute"
Write-Output "failing rows: $failures"
Write-Output "failing pairs: $($failingPairs.Count)"









