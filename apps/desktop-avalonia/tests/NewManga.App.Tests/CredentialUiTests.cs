using System.Text.Json;
using Avalonia;
using Avalonia.Automation;
using Avalonia.Automation.Peers;
using Avalonia.Automation.Provider;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Interactivity;
using NewManga.App.Services;
using NewManga.App.ViewModels;
using NewManga.App.Views;
using NewManga.CoreClient.Commands;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// CREDENTIAL-UI-1: settings-page credential UI. The tests drive the real controls headless with a
/// scripted credential port (no sidecars, no Windows vault, nothing written to %APPDATA%); the
/// scripted fake records exactly the kind/owner/intent/secret the UI would send to
/// <c>credential_put</c>/<c>credential_clear</c>. Evidence files contain booleans/codes only — the
/// marker secret must never appear in any evidence file (asserted in every test).
/// </summary>
public sealed class CredentialUiTests
{
    /// <summary>Marker secret for headless tests. Not a real key; must never reach evidence/logs.</summary>
    private const string DemoSecret = "sk-credential-ui-headless-9c1f-DO-NOT-LEAK";

    private static JsonElement Json(string text)
    {
        using var document = JsonDocument.Parse(text);
        return document.RootElement.Clone();
    }

    private static string EvidenceDirectory
    {
        get
        {
            var configured = Environment.GetEnvironmentVariable("NEWMANGA_EVIDENCE_DIR");
            var root = string.IsNullOrWhiteSpace(configured)
                ? Path.Combine(Path.GetTempPath(), "newmanga-credential-ui-evidence")
                : configured;
            var directory = Path.Combine(root, "credential-ui");
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

    /// <summary>AC3: no secret may appear in any evidence file this task writes.</summary>
    private static void AssertSecretAbsentFromEvidenceAndAutomation(string secret)
    {
        foreach (var file in Directory.GetFiles(EvidenceDirectory, "*", SearchOption.AllDirectories))
        {
            var text = File.ReadAllText(file);
            Assert.DoesNotContain(secret, text, StringComparison.Ordinal);
        }
    }

    private sealed class ScriptedCredentialPort
    {
        public List<CredentialTargetOption> Targets { get; } = new();

        public List<(string Kind, string OwnerId, string Intent, string Secret)> PutCalls { get; } = new();

        public List<(string Kind, string OwnerId)> ClearCalls { get; } = new();

        public Queue<CredentialOperationResult> ScriptedPutResults { get; } = new();

        public Queue<CredentialOperationResult> ScriptedClearResults { get; } = new();

        public int ListCalls { get; private set; }

        public Task<IReadOnlyList<CredentialTargetOption>> ListAsync(CancellationToken cancellationToken = default)
        {
            ListCalls++;
            return Task.FromResult<IReadOnlyList<CredentialTargetOption>>(Targets.ToList());
        }

        public Task<CredentialOperationResult> PutAsync(
            string kind,
            string ownerId,
            string intent,
            string secret,
            CancellationToken cancellationToken = default)
        {
            PutCalls.Add((kind, ownerId, intent, secret));
            var result = ScriptedPutResults.Count > 0
                ? ScriptedPutResults.Dequeue()
                : CredentialOperationResult.Configured();
            if (result.Status == CredentialOperationStatus.Configured)
            {
                UpdateState(kind, ownerId, "configured");
            }

            return Task.FromResult(result);
        }

        public Task<CredentialOperationResult> ClearAsync(
            string kind,
            string ownerId,
            CancellationToken cancellationToken = default)
        {
            ClearCalls.Add((kind, ownerId));
            var result = ScriptedClearResults.Count > 0
                ? ScriptedClearResults.Dequeue()
                : CredentialOperationResult.Cleared();
            if (result.Status == CredentialOperationStatus.Cleared)
            {
                UpdateState(kind, ownerId, "missing");
            }

            return Task.FromResult(result);
        }

        private void UpdateState(string kind, string ownerId, string state)
        {
            for (var index = 0; index < Targets.Count; index++)
            {
                var target = Targets[index];
                if (string.Equals(target.Kind, kind, StringComparison.Ordinal) &&
                    string.Equals(target.OwnerId, ownerId, StringComparison.Ordinal))
                {
                    Targets[index] = target with { CredentialState = state };
                }
            }
        }
    }

    private static CredentialSection BuildSection(ScriptedCredentialPort port) =>
        new(port.ListAsync, port.PutAsync, port.ClearAsync);

    private static void Click(Button button) => button.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));

    private static async Task WaitForAsync(Func<bool> condition, string because)
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

    // ------------------------------------------------------------------
    // AC1: masked input → credential_put with the exact arguments
    // ------------------------------------------------------------------

    [AvaloniaFact]
    public async Task CredentialSection_Save_Create_SendsExactPutArguments_AndClearsMaskedInput()
    {
        var port = new ScriptedCredentialPort();
        port.Targets.Add(new CredentialTargetOption(CredentialKinds.ProviderApi, "profile-1", "DeepSeek", "missing"));
        var section = BuildSection(port);
        await section.RefreshAsync();
        section.TargetSelector.SelectedIndex = 0;

        Assert.Equal('●', section.SecretInput.PasswordChar);
        Assert.True(section.SecretInput.PasswordChar != '\0', "the input must be masked");

        section.SecretInput.Text = DemoSecret;
        Click(section.SaveButton);
        await section.LastOperation;

        var call = Assert.Single(port.PutCalls);
        Assert.Equal(CredentialKinds.ProviderApi, call.Kind);
        Assert.Equal("profile-1", call.OwnerId);
        Assert.Equal("create", call.Intent);
        Assert.Equal(DemoSecret, call.Secret);
        Assert.Equal(string.Empty, section.SecretInput.Text);
        Assert.Contains("configured", (section.StatusText.Text ?? string.Empty), StringComparison.Ordinal);
        Assert.True(section.Targets[0].IsConfigured);

        // AC3: the automation peer must not expose the secret (unlike the stock TextBox peer).
        var peer = section.SecretInput.CreatePeerForVerification();
        Assert.False(
            peer is IValueProvider valueProvider &&
            (valueProvider.Value ?? string.Empty).Contains(DemoSecret, StringComparison.Ordinal),
            "automation peer must not expose the secret value");
        Assert.DoesNotContain(DemoSecret, peer.GetName(), StringComparison.Ordinal);
        Assert.DoesNotContain(DemoSecret, AutomationProperties.GetName(section.SecretInput) ?? string.Empty, StringComparison.Ordinal);

        WriteEvidence("put-create", writer =>
        {
            writer.WriteString("scenario", "masked input -> credential_put(create)");
            writer.WriteString("target_kind", call.Kind);
            writer.WriteString("owner_id", call.OwnerId);
            writer.WriteString("intent", call.Intent);
            writer.WriteNumber("secret_length", call.Secret.Length);
            writer.WriteBoolean("secret_forwarded_to_command", true);
            writer.WriteBoolean("masked_input_password_char", section.SecretInput.PasswordChar == '●');
            writer.WriteBoolean("input_cleared_after_submit", section.SecretInput.Text == string.Empty);
            writer.WriteBoolean("automation_peer_has_no_value", peer is not IValueProvider);
            writer.WriteBoolean("status_mentions_configured", (section.StatusText.Text ?? string.Empty).Contains("configured", StringComparison.Ordinal));
        });
        AssertSecretAbsentFromEvidenceAndAutomation(DemoSecret);
    }

    [AvaloniaFact]
    public async Task CredentialSection_Clear_SendsExactClearArguments_AndShowsMissing()
    {
        var port = new ScriptedCredentialPort();
        port.Targets.Add(new CredentialTargetOption(CredentialKinds.ProxyAuth, "network-1", "公司代理", "configured"));
        var section = BuildSection(port);
        await section.RefreshAsync();
        section.TargetSelector.SelectedIndex = 0;
        Assert.Contains("configured", section.TargetStateText.Text, StringComparison.Ordinal);

        Click(section.ClearButton);
        await section.LastOperation;

        var call = Assert.Single(port.ClearCalls);
        Assert.Equal(CredentialKinds.ProxyAuth, call.Kind);
        Assert.Equal("network-1", call.OwnerId);
        Assert.False(section.HasPendingSecret);
        Assert.Equal(string.Empty, section.SecretInput.Text);
        Assert.Contains("missing", (section.StatusText.Text ?? string.Empty), StringComparison.Ordinal);
        Assert.False(section.Targets[0].IsConfigured);

        WriteEvidence("clear", writer =>
        {
            writer.WriteString("scenario", "clear -> credential_clear");
            writer.WriteString("target_kind", call.Kind);
            writer.WriteString("owner_id", call.OwnerId);
            writer.WriteBoolean("status_mentions_missing", (section.StatusText.Text ?? string.Empty).Contains("missing", StringComparison.Ordinal));
            writer.WriteBoolean("state_refreshed_to_missing", !section.Targets[0].IsConfigured);
        });
        AssertSecretAbsentFromEvidenceAndAutomation(DemoSecret);
    }

    // ------------------------------------------------------------------
    // AC2: CREDENTIAL_CONFLICT is explicit and replacing needs a second confirmation
    // ------------------------------------------------------------------

    [AvaloniaFact]
    public async Task CredentialSection_Conflict_ShowsTypedPrompt_AndReplaceNeedsSecondConfirmation()
    {
        var port = new ScriptedCredentialPort();
        port.Targets.Add(new CredentialTargetOption(CredentialKinds.ProviderApi, "profile-1", "DeepSeek", "missing"));
        port.ScriptedPutResults.Enqueue(new CredentialOperationResult(CredentialOperationStatus.Conflict, "CREDENTIAL_CONFLICT"));
        var section = BuildSection(port);
        await section.RefreshAsync();
        section.TargetSelector.SelectedIndex = 0;
        section.SecretInput.Text = DemoSecret;

        Click(section.SaveButton);
        await section.LastOperation;

        Assert.Equal("create", Assert.Single(port.PutCalls).Intent);
        Assert.True(section.ConfirmPanel.IsVisible);
        Assert.Contains("CREDENTIAL_CONFLICT", (section.StatusText.Text ?? string.Empty), StringComparison.Ordinal);
        Assert.Contains("替换", (section.StatusText.Text ?? string.Empty), StringComparison.Ordinal);
        Assert.True(section.HasPendingSecret, "the pending secret only exists for the second confirmation");

        Click(section.ReplaceButton);
        await section.LastOperation;

        Assert.Equal(2, port.PutCalls.Count);
        var replace = port.PutCalls[1];
        Assert.Equal("replace", replace.Intent);
        Assert.Equal("profile-1", replace.OwnerId);
        Assert.Equal(DemoSecret, replace.Secret);
        Assert.False(section.ConfirmPanel.IsVisible);
        Assert.False(section.HasPendingSecret);
        Assert.Equal(string.Empty, section.SecretInput.Text);
        Assert.Contains("configured", (section.StatusText.Text ?? string.Empty), StringComparison.Ordinal);

        WriteEvidence("conflict-replace", writer =>
        {
            writer.WriteString("scenario", "CREDENTIAL_CONFLICT -> explicit prompt -> second confirmation -> replace");
            writer.WriteNumber("put_calls_before_confirm", 1);
            writer.WriteNumber("put_calls_after_confirm", port.PutCalls.Count);
            writer.WriteString("second_intent", replace.Intent);
            writer.WriteBoolean("confirm_panel_visible_before", true);
            writer.WriteBoolean("pending_secret_cleared_after", !section.HasPendingSecret);
        });
        AssertSecretAbsentFromEvidenceAndAutomation(DemoSecret);
    }

    [AvaloniaFact]
    public async Task CredentialSection_ConfiguredTarget_AsksBeforeSending_AndCancelSendsNothing()
    {
        var port = new ScriptedCredentialPort();
        port.Targets.Add(new CredentialTargetOption(CredentialKinds.ProviderApi, "profile-1", "DeepSeek", "configured"));
        var section = BuildSection(port);
        await section.RefreshAsync();
        section.TargetSelector.SelectedIndex = 0;
        section.SecretInput.Text = DemoSecret;

        Click(section.SaveButton);
        await section.LastOperation;

        Assert.Empty(port.PutCalls);
        Assert.True(section.ConfirmPanel.IsVisible);
        Assert.Contains("二次确认", (section.StatusText.Text ?? string.Empty), StringComparison.Ordinal);
        Assert.True(section.HasPendingSecret);

        Click(section.CancelButton);

        Assert.False(section.ConfirmPanel.IsVisible);
        Assert.False(section.HasPendingSecret);
        Assert.Empty(port.PutCalls);

        // AC3: leaving/clearing the section drops every plaintext reference.
        section.SecretInput.Text = DemoSecret;
        section.ClearSecrets();
        Assert.Equal(string.Empty, section.SecretInput.Text);
        Assert.False(section.HasPendingSecret);

        WriteEvidence("configured-target-confirm", writer =>
        {
            writer.WriteString("scenario", "configured target -> confirm before any command; cancel sends nothing");
            writer.WriteNumber("put_calls", port.PutCalls.Count);
            writer.WriteBoolean("pending_secret_cleared", !section.HasPendingSecret);
            writer.WriteBoolean("masked_input_cleared", section.SecretInput.Text == string.Empty);
        });
        AssertSecretAbsentFromEvidenceAndAutomation(DemoSecret);
    }

    [Fact]
    public void CopyShortcuts_AreBlocked_AndPayloadsMatchTheHostContract()
    {
        Assert.True(CredentialSection.ShouldBlockCopyShortcut(Key.C, KeyModifiers.Control));
        Assert.True(CredentialSection.ShouldBlockCopyShortcut(Key.X, KeyModifiers.Control));
        Assert.True(CredentialSection.ShouldBlockCopyShortcut(Key.Insert, KeyModifiers.Control));
        Assert.False(CredentialSection.ShouldBlockCopyShortcut(Key.V, KeyModifiers.Control));
        Assert.False(CredentialSection.ShouldBlockCopyShortcut(Key.C, KeyModifiers.None));

        var put = CredentialCommandPayload.BuildPut(CredentialKinds.ProviderApi, "profile-1", "create", DemoSecret);
        Assert.Equal("provider_api", put.GetProperty("target").GetProperty("kind").GetString());
        Assert.Equal("profile-1", put.GetProperty("target").GetProperty("profile_id").GetString());
        Assert.Equal("create", put.GetProperty("intent").GetString());
        Assert.Equal(DemoSecret, put.GetProperty("secret").GetString());

        var proxy = CredentialCommandPayload.BuildPut(CredentialKinds.ProxyAuth, "network-1", "replace", DemoSecret);
        Assert.Equal("network-1", proxy.GetProperty("target").GetProperty("network_profile_id").GetString());

        var clear = CredentialCommandPayload.BuildClear(CredentialKinds.ProviderApi, "profile-1");
        Assert.False(clear.TryGetProperty("secret", out _));
        Assert.False(clear.TryGetProperty("intent", out _));

        Assert.Equal(CredentialOperationStatus.Conflict, CredentialResultMapper.MapCode("CREDENTIAL_CONFLICT").Status);
        Assert.Equal(CredentialOperationStatus.Unavailable, CredentialResultMapper.MapCode("CREDENTIAL_STORE_UNAVAILABLE").Status);
        Assert.Equal(CredentialOperationStatus.InvalidArguments, CredentialResultMapper.MapCode("INVALID_ARGUMENTS").Status);
        Assert.Equal(CredentialOperationStatus.NotFound, CredentialResultMapper.MapCode("CREDENTIAL_NOT_FOUND").Status);
        Assert.Equal(CredentialOperationStatus.NotReady, CredentialOperationResult.NotReady().Status);

        WriteEvidence("payload-contract", writer =>
        {
            writer.WriteString("scenario", "payload shape + shortcut policy + typed mapping");
            writer.WriteString("put_payload_keys", string.Join(",", put.EnumerateObject().Select(p => p.Name)));
            writer.WriteBoolean("clear_has_no_secret", !clear.TryGetProperty("secret", out _));
        });
        AssertSecretAbsentFromEvidenceAndAutomation(DemoSecret);
    }

    [Fact]
    public async Task Dispatcher_RoutesCredentialPutClear_ToTheHostLocalHandler_WithTheUiPayload()
    {
        string? observedName = null;
        JsonElement observedPayload = default;
        var dispatcher = new HostCommandDispatcher(
            core: null,
            bridge: null,
            hostLocal: (name, payload, _) =>
            {
                observedName = name;
                observedPayload = payload;
                return Task.FromResult(new HostCommandResult(
                    name,
                    HostCommandStatus.Implemented,
                    HostCommandChannel.HostLocal,
                    Json("{\"state\":\"configured\"}")));
            });

        using var put = JsonDocument.Parse(
            CredentialCommandPayload.BuildPut(CredentialKinds.ProviderApi, "profile-1", "create", DemoSecret).GetRawText());
        var result = await dispatcher.InvokeAsync("credential_put", put.RootElement);
        Assert.Equal("credential_put", observedName);
        Assert.Equal("HostLocal", result.Channel.ToString());
        Assert.Equal("profile-1", observedPayload.GetProperty("target").GetProperty("profile_id").GetString());
        Assert.Equal(DemoSecret, observedPayload.GetProperty("secret").GetString());

        using var clear = JsonDocument.Parse(
            CredentialCommandPayload.BuildClear(CredentialKinds.ProxyAuth, "network-1").GetRawText());
        await dispatcher.InvokeAsync("credential_clear", clear.RootElement);
        Assert.Equal("credential_clear", observedName);
        Assert.Equal("network-1", observedPayload.GetProperty("target").GetProperty("network_profile_id").GetString());
        Assert.False(observedPayload.TryGetProperty("secret", out _));
    }

    // ------------------------------------------------------------------
    // Wiring through the real SettingsPage / MainWindow seams
    // ------------------------------------------------------------------

    [AvaloniaFact]
    public void SecretTextBox_RendersThroughTheTextBoxTheme_NotCollapsed()
    {
        // Regression pinned by the real-machine screenshot pass: a derived TextBox without
        // StyleKeyOverride keeps its own style key, resolves no control theme and measures 0x0 (the
        // masked input was invisible in the live app while headless logic tests still passed).
        var port = new ScriptedCredentialPort();
        var section = BuildSection(port);
        var window = new Window { Width = 900, Height = 600, Content = section };
        window.Show();
        try
        {
            window.Measure(new Size(900, 600));
            window.Arrange(new Rect(0, 0, 900, 600));
            Assert.True(section.SecretInput.Bounds.Height >= 24, $"masked input must be visible, got {section.SecretInput.Bounds}");
            Assert.True(section.SecretInput.Bounds.Width >= 200, $"masked input must be wide, got {section.SecretInput.Bounds}");
        }
        finally
        {
            window.Close();
        }

        WriteEvidence("masked-input-visible", writer =>
        {
            writer.WriteString("scenario", "derived TextBox keeps the TextBox control theme");
            writer.WriteNumber("height", section.SecretInput.Bounds.Height);
            writer.WriteNumber("width", section.SecretInput.Bounds.Width);
            writer.WriteBoolean("masked_password_char", section.SecretInput.PasswordChar == '●');
        });
        AssertSecretAbsentFromEvidenceAndAutomation(DemoSecret);
    }

    [AvaloniaFact]
    public async Task SettingsPage_WiresCredentialBlock_ToTheInjectedController()
    {
        var controller = new FakeHostController(FakeHostController.ReadySnapshot("book"));
        controller.CredentialTargets.Add(new CredentialTargetOption(
            CredentialKinds.ProviderApi, "profile-1", "DeepSeek", "missing"));
        controller.CredentialTargets.Add(new CredentialTargetOption(
            CredentialKinds.ProxyAuth, "network-1", "公司代理", "configured"));
        var page = new SettingsPage(new SettingsViewModel(), () => { }, controller);

        await page.RefreshCredentialsAsync();

        Assert.Equal(2, page.Credentials.Targets.Count);
        Assert.Equal(2, page.Credentials.TargetSelector.ItemCount);
        Assert.Contains("missing", page.Credentials.Targets[0].DisplayText, StringComparison.Ordinal);
        Assert.Contains("configured", page.Credentials.Targets[1].DisplayText, StringComparison.Ordinal);
        page.Credentials.TargetSelector.SelectedIndex = 0;
        page.Credentials.SecretInput.Text = DemoSecret;
        Click(page.Credentials.SaveButton);
        await page.Credentials.LastOperation;
        Assert.Single(controller.PutCredentialCalls);
        Assert.Equal("profile-1", controller.PutCredentialCalls[0].OwnerId);

        WriteEvidence("settings-wiring", writer =>
        {
            writer.WriteString("scenario", "SettingsPage -> IHostController -> dispatcher seam");
            writer.WriteNumber("targets", page.Credentials.Targets.Count);
            writer.WriteNumber("controller_put_calls", controller.PutCredentialCalls.Count);
            writer.WriteBoolean("duplicate_list_calls_allowed", controller.CredentialListCalls >= 1);
        });
        AssertSecretAbsentFromEvidenceAndAutomation(DemoSecret);
    }

    [AvaloniaFact]
    public async Task MainWindow_Closing_ClearsTheMaskedPlaintext()
    {
        var controller = new FakeHostController(FakeHostController.ReadySnapshot("book"));
        controller.CredentialTargets.Add(new CredentialTargetOption(
            CredentialKinds.ProviderApi, "profile-1", "DeepSeek", "missing"));
        var window = new MainWindow(controller, new AppOptions());
        window.Show();
        try
        {
            window.Navigate("settings");
            await window.Settings.RefreshCredentialsAsync();
            window.Settings.Credentials.TargetSelector.SelectedIndex = 0;
            window.Settings.Credentials.SecretInput.Text = DemoSecret;
            Assert.Equal(DemoSecret, window.Settings.Credentials.SecretInput.Text);
        }
        finally
        {
            window.Close();
        }

        Assert.Equal(string.Empty, window.Settings.Credentials.SecretInput.Text);
        Assert.False(window.Settings.Credentials.HasPendingSecret);

        WriteEvidence("window-close-clears", writer =>
        {
            writer.WriteString("scenario", "window close drops the masked plaintext reference");
            writer.WriteBoolean("masked_input_cleared_on_close", window.Settings.Credentials.SecretInput.Text == string.Empty);
            writer.WriteBoolean("pending_secret_cleared_on_close", !window.Settings.Credentials.HasPendingSecret);
        });
        AssertSecretAbsentFromEvidenceAndAutomation(DemoSecret);
    }
}
