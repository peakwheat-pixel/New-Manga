using System;
using System.Runtime.InteropServices;
using NewManga.Appearance;

namespace NewManga.App.Services;

/// <summary>
/// C-03 §2.3: the Windows platform motion preference source. Avalonia 11.3.22 exposes
/// no animation switch, so <c>auto</c> reads the shell animation setting. A failed or
/// unavailable read returns <c>null</c> (the resolver degrades to <c>full</c> with a
/// warning); this type never throws.
/// </summary>
public sealed class WindowsMotionPreferenceSource : IMotionPreferenceSource
{
    private const uint SpiGetClientAreaAnimation = 0x1042;
    private const uint SpifNone = 0;

    public MotionMode? Read()
    {
        if (!OperatingSystem.IsWindows())
        {
            return null;
        }

        try
        {
            var animationsEnabled = new bool[1];
            var result = SystemParametersInfo(
                SpiGetClientAreaAnimation,
                uiParam: 0,
                pvParam: animationsEnabled,
                fWinIni: SpifNone);

            if (result == 0)
            {
                return null;
            }

            return animationsEnabled[0] ? MotionMode.Full : MotionMode.Reduce;
        }
        catch (Exception exception) when (exception is DllNotFoundException or EntryPointNotFoundException)
        {
            return null;
        }
    }

    [DllImport("user32.dll", SetLastError = true)]
    private static extern int SystemParametersInfo(
        uint uiAction,
        uint uiParam,
        [Out] bool[] pvParam,
        uint fWinIni);
}
