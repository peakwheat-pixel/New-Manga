# FEA-07-V2-F11-1 / v2-f11-native.ps1 — 默认 v2 壳：F11 打开沉浸阅读窗口 → Esc 关闭 → 主窗恢复
$ErrorActionPreference = 'Stop'
$repo = 'G:\CODEX\New Manga'
$out = Join-Path $repo 'verification\FEA-07-V2-F11-1\evidence'
$shots = 'G:\CODEX\New Manga.workspace\FEA-07-V2-F11-1\shots'
New-Item -ItemType Directory -Force -Path $out, $shots | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
Add-Type -AssemblyName System.Drawing
$cs = @'
using System; using System.Collections.Generic; using System.Runtime.InteropServices; using System.Text;
public static class V2F {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int left, top, right, bottom; }
  [StructLayout(LayoutKind.Sequential)] public struct WP { public int length, flags, showCmd, x1, y1, x2, y2; public RECT normal; }
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool GetWindowPlacement(IntPtr h, ref WP p);
  [DllImport("user32.dll")] public static extern int GetWindowLongW(IntPtr h, int i);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool PostMessageW(IntPtr h, uint m, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  public static string[] V(uint pid) { var l=new List<string>(); EnumWindows((h,x)=>{ uint p; GetWindowThreadProcessId(h,out p); if(p!=pid||!IsWindowVisible(h)) return true; var t=new StringBuilder(200); GetWindowTextW(h,t,200); RECT r; GetWindowRect(h,out r); int st=GetWindowLongW(h,-16); bool cap=(st&0x00C00000)==0x00C00000; var wp=new WP(); wp.length=Marshal.SizeOf(typeof(WP)); GetWindowPlacement(h, ref wp); l.Add(string.Format("{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}",h,r.left,r.top,r.right-r.left,r.bottom-r.top,cap?1:0,wp.showCmd,t)); return true; }, IntPtr.Zero); return l.ToArray(); }
  public static int Key(IntPtr h, int vk){ bool d=PostMessageW(h,0x0100,(IntPtr)vk,(IntPtr)0x00010001); System.Threading.Thread.Sleep(80); bool u=PostMessageW(h,0x0101,(IntPtr)vk,unchecked((IntPtr)0xC0010001)); return (d?1:0)+(u?2:0);} }
'@
Add-Type -TypeDefinition $cs
function Capture($n){ $f=Join-Path $shots ("{0}-{1}.png" -f (Get-Date -Format 'yyyyMMdd-HHmmss'),$n); $b=New-Object System.Drawing.Bitmap 2560,1440; $g=[System.Drawing.Graphics]::FromImage($b); $g.CopyFromScreen(0,0,0,0,$b.Size); $g.Dispose(); $b.Save($f,[System.Drawing.Imaging.ImageFormat]::Png); $b.Dispose(); [pscustomobject]@{file=$f;sha256=(Get-FileHash -Algorithm SHA256 -Path $f).Hash.ToLowerInvariant()} }
$root=Join-Path 'G:\CODEX\New Manga.workspace\FEA-07-V2-F11-1' ("run-"+$stamp); New-Item -ItemType Directory -Force -Path "$root\logs","$root\theme" | Out-Null
$env:NEWMANGA_CORE_SIDECAR_DIR='G:\CODEX\New Manga.workspace\FEA-07-AC5-NATIVE-1\sidecar'
$exe=Join-Path $repo 'apps\desktop-avalonia\src\NewManga.App\bin\Release\net9.0\NewManga.App.exe'
$args=@('--data-root','G:\CODEX\New Manga.workspace\FEA-07-AC5-NATIVE-1\reader-session\data','--log-dir',"$root\logs",'--theme-home',"$root\theme")
$psi=New-Object System.Diagnostics.ProcessStartInfo; $psi.FileName=$exe; $psi.WorkingDirectory=(Split-Path $exe -Parent); $psi.UseShellExecute=$false; $psi.CreateNoWindow=$true
foreach($a in $args){$psi.ArgumentList.Add($a)}
$proc=[System.Diagnostics.Process]::Start($psi); Write-Host "pid=$($proc.Id) shell=default(v2)"
$main=$null; for($i=0;$i -lt 60;$i++){ Start-Sleep -Milliseconds 500; foreach($l in [V2F]::V([uint32]$proc.Id)){ $p=$l -split '\|',8; if($p[7] -eq 'New Manga'){$main=$p} }; if($main){break} }
if(-not $main){ throw 'main window not found' }
Start-Sleep -Seconds 8
[V2F]::SetForegroundWindow([IntPtr][int64]$main[0]) | Out-Null; Start-Sleep -Milliseconds 400
$before=Capture 'v2-before'
$rc=[V2F]::Key([IntPtr][int64]$main[0],0x7A)
$imm=$null; for($i=0;$i -lt 80;$i++){ Start-Sleep -Milliseconds 150; foreach($l in [V2F]::V([uint32]$proc.Id)){ $p=$l -split '\|',8; if($p[7] -ne 'New Manga'){$imm=$p;break} }; if($imm){break} }
$after=Capture 'v2-after'
$afterEsc=$null
if($imm){ [V2F]::SetForegroundWindow([IntPtr][int64]$imm[0]) | Out-Null; Start-Sleep -Milliseconds 400; [V2F]::Key([IntPtr][int64]$imm[0],0x1B) | Out-Null; Start-Sleep -Seconds 2; $m=$null; foreach($l in [V2F]::V([uint32]$proc.Id)){ $p=$l -split '\|',8; if($p[7] -eq 'New Manga'){$m=$p} }; $afterEsc=[ordered]@{ extra=@([V2F]::V([uint32]$proc.Id) | Where-Object { ($_ -split '\|',8)[7] -ne 'New Manga' }).Count; main=if($m){[ordered]@{left=[int]$m[1];top=[int]$m[2];width=[int]$m[3];height=[int]$m[4];hasCaption=($m[5]-eq'1');showCmd=[int]$m[6]}}else{$null}; screenshot=(Capture 'v2-after-esc') } }
$doc=[ordered]@{ case='v2-f11-native'; capturedAt=(Get-Date -Format o); app=[ordered]@{pid=$proc.Id;exe=$exe;args=$args;shell='v2(default)';logDir="$root\logs"};
  postMessageRc=$rc; immersive=if($imm){[ordered]@{left=[int]$imm[1];top=[int]$imm[2];width=[int]$imm[3];height=[int]$imm[4];hasCaption=($imm[5]-eq'1');title=$imm[7]}}else{$null}; afterEsc=$afterEsc; screenshots=@($before,$after) }
$json=Join-Path $out ("v2-f11-native-{0}.json" -f $stamp); $doc|ConvertTo-Json -Depth 8|Set-Content $json -Encoding UTF8
Write-Host "saved: $json"; Write-Host ("immersive={0} afterEsc={1}" -f ($null -ne $imm), ($null -ne $afterEsc))
if(-not $proc.HasExited){ $proc.Kill($true); $proc.WaitForExit(5000)|Out-Null; Write-Host 'app closed' }
