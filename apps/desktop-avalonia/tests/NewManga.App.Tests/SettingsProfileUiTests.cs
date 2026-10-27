using System.Text.Json;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Interactivity;
using NewManga.App.Services;
using NewManga.App.ViewModels;
using NewManga.App.Views;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// SETTINGS-PROFILE-UI-1: headless coverage of the settings-page provider/network profile management
/// and binding slots. The UI is driven for real (controls, clicks, async operations) while the Host is
/// replaced by the scripted <see cref="FakeHostController"/>, which records the exact arguments the UI
/// would send to <c>settings_provider_profiles_*</c>, <c>settings_network_profiles_*</c>,
/// <c>settings_network_profile_*</c> and <c>settings_provider_bindings_*</c>. The network diagnostic is
/// always rendered from the (scripted here) Host result — the UI never invents a "passed" state.
/// </summary>
public sealed class SettingsProfileUiTests
{
    private static string EvidenceDirectory
    {
        get
        {
            var configured = Environment.GetEnvironmentVariable("NEWMANGA_EVIDENCE_DIR");
            var root = string.IsNullOrWhiteSpace(configured)
                ? Path.Combine(Path.GetTempPath(), "newmanga-settings-profile-ui-evidence")
                : configured;
            var directory = Path.Combine(root, "settings-profile-ui");
            Directory.CreateDirectory(directory);
            return directory;
        }
    }

    private static void WriteEvidence(string name, Action<Utf8JsonWriter> write)
    {
        using var stream = new MemoryStream();
        using (var writer = new Utf8JsonWriter(stream, new JsonWriterOptions { Indented = true }))
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC1/AC2/AC3/AC4");
            write(writer);
            writer.WriteEndObject();
        }

        File.WriteAllBytes(Path.Combine(EvidenceDirectory, name + ".json"), stream.ToArray());
    }

    private static JsonElement Json(string text)
    {
        using var document = JsonDocument.Parse(text);
        return document.RootElement.Clone();
    }

    private static FakeHostController ReadyController() => new(FakeHostController.ReadySnapshot("book"));

    private static SettingsPage NewPage(FakeHostController controller) =>
        new(new SettingsViewModel(), () => { }, controller);

    private static void Click(Button button) => button.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));

    private static async Task WaitAsync(Func<bool> condition, string because)
    {
        var deadline = DateTime.UtcNow + TimeSpan.FromSeconds(5);
        while (DateTime.UtcNow < deadline)
        {
            if (condition())
            {
                return;
            }

            await Task.Delay(10);
        }

        Assert.Fail("timed out waiting for UI operation: " + because);
    }

    private static void SetCapability(ProviderProfileSection section, string capability, bool selected)
    {
        if (section.CapabilityChecks.TryGetValue(capability, out var check))
        {
            check.IsChecked = selected;
        }
    }

    // ------------------------------------------------------------------
    // AC1: provider profile list + create/update/delete + typed feedback + empty state
    // ------------------------------------------------------------------

    [AvaloniaFact]
    public async Task ProviderSection_EmptyState_ThenCreate_SendsExactDraft()
    {
        var controller = ReadyController();
        var page = NewPage(controller);
        await page.RefreshProfilesAsync();
        var section = page.ProviderProfiles;

        Assert.True(section.EmptyText.IsVisible);
        Assert.Equal(0, section.ProfileList.ItemCount);

        section.DisplayNameInput.Text = "DeepSeek";
        section.ProviderIdInput.Text = "openai";
        section.EndpointInput.Text = "https://api.deepseek.com/v1";
        section.ModelInput.Text = "deepseek-chat";
        SetCapability(section, SettingsCapabilities.Ocr, true);
        SetCapability(section, SettingsCapabilities.Translation, true);
        Click(section.SaveButton);
        await section.LastOperation;

        var save = Assert.Single(controller.ProviderSaves);
        Assert.Null(save.ProfileId);
        Assert.Equal("openai", save.Draft.ProviderId);
        Assert.Equal("DeepSeek", save.Draft.DisplayName);
        Assert.Equal(new[] { SettingsCapabilities.Ocr, SettingsCapabilities.Translation }, save.Draft.Capabilities);
        Assert.Equal("https://api.deepseek.com/v1", save.Draft.Endpoint);
        Assert.Equal("deepseek-chat", save.Draft.Model);
        Assert.Null(save.Draft.NetworkProfileId);
        Assert.True(save.Draft.Enabled);
        Assert.Contains("已创建", section.StatusText.Text ?? string.Empty, StringComparison.Ordinal);
        Assert.False(section.EmptyText.IsVisible);
        Assert.Equal(1, section.ProfileList.ItemCount);

        WriteEvidence("provider-create", writer =>
        {
            writer.WriteString("scenario", "empty state -> create provider profile");
            writer.WriteBoolean("empty_state_before", true);
            writer.WriteString("provider_id", save.Draft.ProviderId);
            writer.WriteString("display_name", save.Draft.DisplayName);
            writer.WriteString("capabilities", string.Join(",", save.Draft.Capabilities));
            writer.WriteString("endpoint", save.Draft.Endpoint);
            writer.WriteString("model", save.Draft.Model);
            writer.WriteBoolean("network_profile_null", save.Draft.NetworkProfileId is null);
            writer.WriteBoolean("profile_id_null_on_create", save.ProfileId is null);
        });
    }

    [AvaloniaFact]
    public async Task ProviderSection_UpdateAndDelete_SendProfileId()
    {
        var controller = ReadyController();
        controller.ProviderProfiles.Add(new ProviderProfileInfo(
            "profile-1", "deepl", "DeepL", new[] { SettingsCapabilities.Translation },
            "https://api-free.deepl.com/v2", "deepl", null, true, "configured"));
        var page = NewPage(controller);
        await page.RefreshProfilesAsync();
        var section = page.ProviderProfiles;

        Assert.Equal("profile-1", section.EditingProfileId);
        Assert.Equal("DeepL", section.DisplayNameInput.Text);
        section.DisplayNameInput.Text = "DeepL (edited)";
        Click(section.SaveButton);
        await section.LastOperation;

        var update = Assert.Single(controller.ProviderSaves);
        Assert.Equal("profile-1", update.ProfileId);
        Assert.Equal("DeepL (edited)", update.Draft.DisplayName);
        Assert.Equal(new[] { SettingsCapabilities.Translation }, update.Draft.Capabilities);

        Click(section.DeleteButton);
        await section.LastOperation;
        Assert.Contains("profile-1", controller.ProviderDeletes);
        Assert.True(section.EmptyText.IsVisible);

        WriteEvidence("provider-update-delete", writer =>
        {
            writer.WriteString("scenario", "select -> update -> delete provider profile");
            writer.WriteString("update_profile_id", update.ProfileId);
            writer.WriteString("deleted_profile_id", "profile-1");
            writer.WriteBoolean("empty_after_delete", true);
        });
    }

    [AvaloniaFact]
    public async Task ProviderSection_TypedError_AndLocalValidation_AreRendered()
    {
        var controller = ReadyController();
        controller.ScriptedProviderSaveResults.Enqueue(new SettingsProfileResult(
            SettingsProfileStatus.Conflict, "SETTINGS_CONFLICT"));
        var page = NewPage(controller);
        await page.RefreshProfilesAsync();
        var section = page.ProviderProfiles;

        section.DisplayNameInput.Text = "X";
        section.ProviderIdInput.Text = "openai";
        section.EndpointInput.Text = "https://x.example/v1";
        section.ModelInput.Text = "m";
        SetCapability(section, SettingsCapabilities.Ocr, true);
        Click(section.SaveButton);
        await section.LastOperation;

        Assert.Contains("SETTINGS_CONFLICT", section.StatusText.Text ?? string.Empty, StringComparison.Ordinal);
        Assert.Contains("冲突", section.StatusText.Text ?? string.Empty, StringComparison.Ordinal);

        var callsBefore = controller.ProviderSaves.Count;
        section.DisplayNameInput.Text = string.Empty;
        Click(section.SaveButton);
        await section.LastOperation;
        Assert.Equal(callsBefore, controller.ProviderSaves.Count);
        Assert.Contains("INVALID_ARGUMENTS", section.StatusText.Text ?? string.Empty, StringComparison.Ordinal);

        WriteEvidence("provider-error-feedback", writer =>
        {
            writer.WriteString("scenario", "typed SETTINGS_CONFLICT + local INVALID_ARGUMENTS");
            writer.WriteBoolean("conflict_rendered", true);
            writer.WriteBoolean("no_call_on_local_invalid_input", controller.ProviderSaves.Count == callsBefore);
        });
    }

    // ------------------------------------------------------------------
    // AC2: network profile CRUD + real test/resolve display
    // ------------------------------------------------------------------

    [AvaloniaFact]
    public async Task NetworkSection_EmptyState_Create_SendsExactDraft()
    {
        var controller = ReadyController();
        var page = NewPage(controller);
        await page.RefreshProfilesAsync();
        var section = page.NetworkProfiles;

        Assert.True(section.EmptyText.IsVisible);
        section.DisplayNameInput.Text = "公司代理";
        section.ModeInput.SelectedIndex = NetworkModes.All.ToList().IndexOf(NetworkModes.Https);
        section.ProxyEndpointInput.Text = "https://127.0.0.1:7890";
        section.AllowFallbackInput.IsChecked = true;
        Click(section.SaveButton);
        await section.LastOperation;

        var save = Assert.Single(controller.NetworkSaves);
        Assert.Null(save.NetworkProfileId);
        Assert.Equal("公司代理", save.Draft.DisplayName);
        Assert.Equal(NetworkModes.Https, save.Draft.Mode);
        Assert.Equal("https://127.0.0.1:7890", save.Draft.ProxyEndpoint);
        Assert.True(save.Draft.VerifyTls);
        Assert.False(save.Draft.ConfirmDisableTlsVerification);
        Assert.True(save.Draft.AllowProxyFailureDirectFallback);
        Assert.Contains("已创建", section.StatusText.Text ?? string.Empty, StringComparison.Ordinal);
        Assert.False(section.EmptyText.IsVisible);

        // Local rule: HTTP/HTTPS/SOCKS5 require a proxy endpoint; Direct/System must not send one.
        var callsBefore = controller.NetworkSaves.Count;
        section.DisplayNameInput.Text = "缺失地址";
        section.ModeInput.SelectedIndex = NetworkModes.All.ToList().IndexOf(NetworkModes.Http);
        section.ProxyEndpointInput.Text = string.Empty;
        Click(section.SaveButton);
        await section.LastOperation;
        Assert.Equal(callsBefore, controller.NetworkSaves.Count);
        Assert.Contains("INVALID_ARGUMENTS", section.StatusText.Text ?? string.Empty, StringComparison.Ordinal);

        section.ModeInput.SelectedIndex = NetworkModes.All.ToList().IndexOf(NetworkModes.Direct);
        section.ProxyEndpointInput.Text = "http://ignored.example:1";
        Click(section.SaveButton);
        await section.LastOperation;
        Assert.Equal(NetworkModes.Direct, controller.NetworkSaves[^1].Draft.Mode);
        Assert.Null(controller.NetworkSaves[^1].Draft.ProxyEndpoint);

        WriteEvidence("network-create", writer =>
        {
            writer.WriteString("scenario", "empty state -> create network profile (HTTPS) + mode rules");
            writer.WriteString("mode", save.Draft.Mode);
            writer.WriteString("proxy_endpoint", save.Draft.ProxyEndpoint ?? "(null)");
            writer.WriteBoolean("verify_tls", save.Draft.VerifyTls);
            writer.WriteBoolean("allow_fallback", save.Draft.AllowProxyFailureDirectFallback);
            writer.WriteBoolean("direct_mode_sends_null_proxy", controller.NetworkSaves[^1].Draft.ProxyEndpoint is null);
        });
    }

    [AvaloniaFact]
    public async Task NetworkSection_TestAndResolve_RenderCoreResult_AndNeverFabricate()
    {
        var controller = ReadyController();
        controller.NetworkProfiles.Add(new NetworkProfileInfo(
            "network-1", "公司代理", NetworkModes.Https, "https://127.0.0.1:7890", true, "enabled", false, "missing"));
        controller.ProviderProfiles.Add(new ProviderProfileInfo(
            "profile-1", "openai", "DeepSeek", new[] { SettingsCapabilities.Ocr },
            "https://api.example/v1", "m", null, true, "missing"));
        var page = NewPage(controller);
        await page.RefreshProfilesAsync();
        var section = page.NetworkProfiles;

        // Unscripted = Host/Core unavailable: the UI must say so, never show a fake pass.
        Click(section.TestButton);
        await section.LastOperation;
        Assert.Contains("不可用", section.TestResultText.Text ?? string.Empty, StringComparison.Ordinal);

        var stages = new List<NetworkTestStageInfo>
        {
            new("Proxy", "passed", null, 12),
            new("DNS", "passed", null, 3),
            new("TCP", "passed", null, 4),
            new("TLS", "not_applicable", "provider_endpoint_uses_http", null),
            new("HTTP", "passed", null, 20),
            new("ProviderAuth", "passed", null, 9),
        };
        controller.ScriptedNetworkTestResults.Enqueue(
            new NetworkTestInfo("passed", null, false, stages));
        section.ProviderForProbeInput.SelectedIndex = 0;
        Click(section.TestButton);
        await section.LastOperation;
        var testCall = controller.NetworkTests[^1];
        Assert.Equal("network-1", testCall.NetworkProfileId);
        Assert.Equal("profile-1", testCall.ProviderProfileId);
        Assert.Contains("status=passed", section.TestResultText.Text ?? string.Empty, StringComparison.Ordinal);
        Assert.Contains("ProviderAuth:passed", section.TestResultText.Text ?? string.Empty, StringComparison.Ordinal);
        Assert.Contains("TLS:not_applicable", section.TestResultText.Text ?? string.Empty, StringComparison.Ordinal);

        controller.ScriptedNetworkResolveResults.Enqueue(
            new NetworkResolveInfo("network-1", NetworkModes.Https, "global"));
        Click(section.ResolveButton);
        await section.LastOperation;
        Assert.Equal("profile-1", controller.NetworkResolves[^1]);
        Assert.Contains("network_profile_id=network-1", section.ResolveResultText.Text ?? string.Empty, StringComparison.Ordinal);
        Assert.Contains("source=global", section.ResolveResultText.Text ?? string.Empty, StringComparison.Ordinal);

        WriteEvidence("network-test-resolve", writer =>
        {
            writer.WriteString("scenario", "real Core test/resolve results rendered; unavailable is explicit");
            writer.WriteBoolean("unavailable_message_when_no_result", true);
            writer.WriteString("test_call", testCall.NetworkProfileId + "/" + testCall.ProviderProfileId);
            writer.WriteString("test_summary", section.TestResultText.Text ?? string.Empty);
            writer.WriteString("resolve_summary", section.ResolveResultText.Text ?? string.Empty);
        });
    }

    [AvaloniaFact]
    public async Task NetworkSection_Delete_And_DefaultSetClear()
    {
        var controller = ReadyController();
        controller.NetworkProfiles.Add(new NetworkProfileInfo(
            "network-1", "公司代理", NetworkModes.Http, "http://127.0.0.1:7890", true, "enabled", false, "missing"));
        var page = NewPage(controller);
        await page.RefreshProfilesAsync();
        var section = page.NetworkProfiles;
        Assert.Equal("network-1", section.EditingNetworkProfileId);

        Click(section.DefaultSetButton);
        await section.LastOperation;
        Assert.Equal("network-1", controller.NetworkDefaults[^1]);

        Click(section.DefaultClearButton);
        await section.LastOperation;
        Assert.Null(controller.NetworkDefaults[^1]);

        Click(section.DeleteButton);
        await section.LastOperation;
        Assert.Contains("network-1", controller.NetworkDeletes);
        Assert.True(section.EmptyText.IsVisible);

        WriteEvidence("network-default-delete", writer =>
        {
            writer.WriteString("scenario", "set default -> clear default -> delete network profile");
            writer.WriteBoolean("default_set", controller.NetworkDefaults.Count >= 2);
            writer.WriteBoolean("empty_after_delete", true);
        });
    }

    [AvaloniaFact]
    public async Task NetworkSection_TlsConfirmationRequired_IsRendered()
    {
        var controller = ReadyController();
        controller.NetworkProfiles.Add(new NetworkProfileInfo(
            "network-1", "公司代理", NetworkModes.Http, "http://127.0.0.1:7890", true, "enabled", false, "missing"));
        controller.ScriptedNetworkSaveResults.Enqueue(new SettingsProfileResult(
            SettingsProfileStatus.TlsConfirmationRequired, "TLS_CONFIRMATION_REQUIRED"));
        var page = NewPage(controller);
        await page.RefreshProfilesAsync();
        var section = page.NetworkProfiles;

        section.VerifyTlsInput.IsChecked = false;
        Assert.True(section.ConfirmDisableTlsInput.IsVisible);
        Click(section.SaveButton);
        await section.LastOperation;

        Assert.Contains("TLS_CONFIRMATION_REQUIRED", section.StatusText.Text ?? string.Empty, StringComparison.Ordinal);
        WriteEvidence("network-tls-confirmation", writer =>
        {
            writer.WriteString("scenario", "disabling TLS surfaces TLS_CONFIRMATION_REQUIRED from the Core contract");
            writer.WriteBoolean("confirm_checkbox_visible", section.ConfirmDisableTlsInput.IsVisible);
            writer.WriteBoolean("typed_code_rendered", true);
        });
    }

    // ------------------------------------------------------------------
    // AC3: provider binding slots + default network profile
    // ------------------------------------------------------------------

    [AvaloniaFact]
    public async Task BindingsSection_SetClear_WithGlobalAndBookScopes_SendExactArguments()
    {
        var controller = ReadyController();
        controller.ProviderProfiles.Add(new ProviderProfileInfo(
            "profile-1", "openai", "DeepSeek", new[] { SettingsCapabilities.Ocr, SettingsCapabilities.Translation },
            "https://api.example/v1", "m", null, true, "missing"));
        var page = NewPage(controller);
        await page.RefreshProfilesAsync();
        var section = page.Bindings;
        Assert.True(section.ProviderInput.ItemCount == 1);

        section.CapabilityInput.SelectedIndex = SettingsCapabilities.All.ToList().IndexOf(SettingsCapabilities.Ocr);
        Click(section.SetButton);
        await section.LastOperation;
        var global = Assert.Single(controller.BindingSets);
        Assert.Equal(ProfileBindingScope.Global, global.Scope.Kind);
        Assert.Equal(SettingsCapabilities.Ocr, global.Capability);
        Assert.Equal("profile-1", global.ProfileId);

        section.ScopeKindInput.SelectedIndex = ProfileBindingScope.Kinds.ToList().IndexOf(ProfileBindingScope.Book);
        section.BookIdInput.Text = "book-1";
        section.CapabilityInput.SelectedIndex = SettingsCapabilities.All.ToList().IndexOf(SettingsCapabilities.Translation);
        Click(section.SetButton);
        await section.LastOperation;
        var book = controller.BindingSets[^1];
        Assert.Equal(ProfileBindingScope.Book, book.Scope.Kind);
        Assert.Equal("book-1", book.Scope.BookId);
        Assert.Equal(SettingsCapabilities.Translation, book.Capability);

        Click(section.ClearButton);
        await section.LastOperation;
        var clear = controller.BindingClears[^1];
        Assert.Equal(ProfileBindingScope.Book, clear.Scope.Kind);
        Assert.Equal("book-1", clear.Scope.BookId);

        WriteEvidence("bindings-set-clear", writer =>
        {
            writer.WriteString("scenario", "bindings set(global), set(book), clear(book)");
            writer.WriteString("global", global.Capability + "->" + global.ProfileId);
            writer.WriteString("book", book.Scope.Kind + ":" + book.Scope.BookId + " " + book.Capability + "->" + book.ProfileId);
            writer.WriteString("clear", clear.Scope.Kind + ":" + clear.Scope.BookId + " " + clear.Capability);
        });
    }

    // ------------------------------------------------------------------
    // AC4: page wiring + payload schema contract
    // ------------------------------------------------------------------

    [AvaloniaFact]
    public async Task SettingsPage_WiresAllProfileSections_ToTheController()
    {
        var controller = ReadyController();
        controller.ProviderProfiles.Add(new ProviderProfileInfo(
            "profile-1", "openai", "DeepSeek", new[] { SettingsCapabilities.Ocr },
            "https://api.example/v1", "m", "network-1", true, "missing"));
        controller.NetworkProfiles.Add(new NetworkProfileInfo(
            "network-1", "公司代理", NetworkModes.Http, "http://127.0.0.1:7890", true, "enabled", false, "missing"));
        var page = NewPage(controller);

        await page.RefreshProfilesAsync();

        Assert.True(page.ProviderProfiles.ProfileList.ItemCount >= 1);
        Assert.True(page.NetworkProfiles.ProfileList.ItemCount >= 1);
        Assert.True(page.Bindings.ProviderInput.ItemCount >= 1);
        Assert.Equal("network-1", page.ProviderProfiles.NetworkProfileInput.SelectedIndex > 0
            ? controller.NetworkProfiles[page.ProviderProfiles.NetworkProfileInput.SelectedIndex - 1].NetworkProfileId
            : null);

        WriteEvidence("settings-wiring", writer =>
        {
            writer.WriteString("scenario", "SettingsPage -> IHostController seam, all three sections wired");
            writer.WriteNumber("provider_list", page.ProviderProfiles.ProfileList.ItemCount);
            writer.WriteNumber("network_list", page.NetworkProfiles.ProfileList.ItemCount);
            writer.WriteNumber("binding_providers", page.Bindings.ProviderInput.ItemCount);
        });
    }

    [Fact]
    public void PayloadContract_MatchesTheDispatcherKeys()
    {
        var provider = SettingsProfilePayload.ProviderCreate(new ProviderProfileDraft(
            "openai", "DeepSeek", new[] { SettingsCapabilities.Ocr }, "https://api.example/v1", "m", null, true));
        Assert.Equal("openai", provider.GetProperty("provider_id").GetString());
        Assert.Equal("DeepSeek", provider.GetProperty("display_name").GetString());
        Assert.Equal("OCR", provider.GetProperty("capabilities")[0].GetString());
        Assert.Equal("https://api.example/v1", provider.GetProperty("endpoint").GetString());
        Assert.Equal("m", provider.GetProperty("model").GetString());
        Assert.Equal(JsonValueKind.Null, provider.GetProperty("network_profile_id").ValueKind);
        Assert.True(provider.GetProperty("enabled").GetBoolean());

        var update = SettingsProfilePayload.ProviderUpdate("p1", new ProviderProfileDraft(
            "unused", "N", new[] { SettingsCapabilities.Translation }, "https://a.example", "m2", "net-1", false));
        Assert.Equal("p1", update.GetProperty("profile_id").GetString());
        Assert.Equal("net-1", update.GetProperty("network_profile_id").GetString());

        var network = SettingsProfilePayload.NetworkCreate(new NetworkProfileDraft(
            "proxy", NetworkModes.Http, "http://127.0.0.1:7890", true, false, true));
        Assert.Equal("proxy", network.GetProperty("display_name").GetString());
        Assert.Equal("HTTP", network.GetProperty("mode").GetString());
        Assert.Equal("http://127.0.0.1:7890", network.GetProperty("proxy_endpoint").GetString());
        Assert.True(network.GetProperty("verify_tls").GetBoolean());
        Assert.True(network.GetProperty("allow_proxy_failure_direct_fallback").GetBoolean());

        var networkUpdate = SettingsProfilePayload.NetworkUpdate("n1", new NetworkProfileDraft(
            "proxy", NetworkModes.Direct, null, false, true, false));
        Assert.Equal("n1", networkUpdate.GetProperty("network_profile_id").GetString());
        Assert.Equal(JsonValueKind.Null, networkUpdate.GetProperty("proxy_endpoint").ValueKind);
        Assert.True(networkUpdate.GetProperty("confirm_disable_tls_verification").GetBoolean());
        Assert.True(networkUpdate.GetProperty("verify_tls").ValueKind == JsonValueKind.False);

        var global = SettingsProfilePayload.BindingSet(new ProfileBindingScope(ProfileBindingScope.Global), "OCR", "p1");
        Assert.Equal("global", global.GetProperty("scope").GetProperty("kind").GetString());
        Assert.Single(global.GetProperty("scope").EnumerateObject());
        Assert.Equal("OCR", global.GetProperty("capability").GetString());
        Assert.Equal("p1", global.GetProperty("profile_id").GetString());

        var book = SettingsProfilePayload.BindingClear(new ProfileBindingScope(ProfileBindingScope.Book, BookId: "b1"), "Translation");
        Assert.Equal("b1", book.GetProperty("scope").GetProperty("book_id").GetString());
        Assert.False(book.TryGetProperty("profile_id", out _));

        var test = SettingsProfilePayload.NetworkTest("n1", "p1");
        Assert.Equal("n1", test.GetProperty("network_profile_id").GetString());
        Assert.Equal("p1", test.GetProperty("provider_profile_id").GetString());

        Assert.False(SettingsProfilePayload.NetworkResolve(null).TryGetProperty("provider_profile_id", out _));
        Assert.Equal("p1", SettingsProfilePayload.NetworkResolve("p1").GetProperty("provider_profile_id").GetString());
        Assert.Empty(SettingsProfilePayload.Empty().EnumerateObject());
        Assert.Equal("n1", SettingsProfilePayload.NetworkDefaultSet("n1").GetProperty("network_profile_id").GetString());

        Assert.Equal(SettingsProfileStatus.Conflict, SettingsProfileResultMapper.MapCode("SETTINGS_CONFLICT").Status);
        Assert.Equal(SettingsProfileStatus.NotFound, SettingsProfileResultMapper.MapCode("SETTINGS_ITEM_NOT_FOUND").Status);
        Assert.Equal(SettingsProfileStatus.InvalidArguments, SettingsProfileResultMapper.MapCode("SETTINGS_INVALID_INPUT").Status);
        Assert.Equal(SettingsProfileStatus.TlsConfirmationRequired, SettingsProfileResultMapper.MapCode("TLS_CONFIRMATION_REQUIRED").Status);

        WriteEvidence("payload-contract", writer =>
        {
            writer.WriteString("scenario", "payload shapes mirror HostCommandDispatcher keys");
            writer.WriteString("provider_create_keys", string.Join(",", provider.EnumerateObject().Select(p => p.Name)));
            writer.WriteString("network_create_keys", string.Join(",", network.EnumerateObject().Select(p => p.Name)));
            writer.WriteBoolean("global_scope_only_kind", global.GetProperty("scope").EnumerateObject().Count() == 1);
        });
    }
}
