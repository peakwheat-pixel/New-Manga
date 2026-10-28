using System.Text.Json;
using Avalonia.Headless.XUnit;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.ViewModels;
using NewManga.App.Views;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// GPU-ORT-PROBE-1: the settings page renders the packaged device probe
/// (ONNX Runtime EP list recorded in VERSION.json) so a torch-free build shows
/// "DirectML 可用"; a missing/malformed probe falls back honestly.
/// </summary>
public sealed class DeviceStatusTests : IDisposable
{
    private readonly string _root;

    public DeviceStatusTests()
    {
        _root = Path.Combine(Path.GetTempPath(), "nm-device-" + Guid.NewGuid().ToString("N")[..10]);
        Directory.CreateDirectory(_root);
    }

    public void Dispose()
    {
        try
        {
            Directory.Delete(_root, recursive: true);
        }
        catch (IOException)
        {
            // best effort
        }
    }

    private string WriteVersion(object devices)
    {
        var path = Path.Combine(_root, "VERSION.json");
        File.WriteAllText(
            path,
            JsonSerializer.Serialize(new Dictionary<string, object> { ["version"] = "0.1.0", ["devices"] = devices }));
        return _root;
    }

    [AvaloniaFact]
    public void Packaged_DirectMl_Probe_Is_Rendered_As_Available()
    {
        var root = WriteVersion(new
        {
            onnxruntime_providers = new[] { "DmlExecutionProvider", "CPUExecutionProvider" },
            gpu = new
            {
                state = "available",
                name = "NVIDIA GeForce RTX 5070 Ti",
                total_memory_mb = 16301,
                detail = "onnxruntime providers=['DmlExecutionProvider', 'CPUExecutionProvider']; execution_provider=DirectML",
            },
        });

        var status = DeviceStatus.Load(root);
        Assert.NotNull(status);
        Assert.True(status!.Available);
        Assert.True(status.HasDirectMl);
        Assert.Contains("RTX 5070 Ti", status.DisplayText);
        Assert.Contains("DirectML 可用", status.DisplayText);
    }

    [AvaloniaFact]
    public void CpuOnly_Probe_Is_Rendered_As_Unavailable()
    {
        var root = WriteVersion(new
        {
            onnxruntime_providers = new[] { "CPUExecutionProvider" },
            gpu = new
            {
                state = "unavailable",
                name = "",
                total_memory_mb = (int?)null,
                detail = "onnxruntime has no GPU execution provider (providers=['CPUExecutionProvider'])",
            },
        });

        var status = DeviceStatus.Load(root);
        Assert.NotNull(status);
        Assert.False(status!.Available);
        Assert.Contains("不可用", status.DisplayText);
        Assert.Contains("onnxruntime", status.DisplayText);
    }

    [AvaloniaFact]
    public void Missing_Or_Malformed_Metadata_Falls_Back_To_Dev_Run()
    {
        Assert.Null(DeviceStatus.Load(_root));

        var path = Path.Combine(_root, "VERSION.json");
        File.WriteAllText(path, "{ not-json");
        Assert.Null(DeviceStatus.Load(_root));

        var page = new SettingsPage(new SettingsViewModel(), () => { });
        Dispatcher.UIThread.RunJobs();
        Assert.Contains("GPU", page.DeviceStatusText.Text);
        Assert.Null(page.DeviceStatus);
    }

    [AvaloniaFact]
    public void SettingsPage_Renders_DeviceStatus_Text()
    {
        var page = new SettingsPage(new SettingsViewModel(), () => { });
        Dispatcher.UIThread.RunJobs();
        Assert.NotNull(page.DeviceStatusText);
        Assert.False(string.IsNullOrWhiteSpace(page.DeviceStatusText.Text));
    }
}
