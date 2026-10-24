use crate::library_bridge::{LibraryError, P15CredentialTarget, P15SettingsCommand};
use rand::{rngs::OsRng, RngCore};
use serde::de::DeserializeOwned;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use tauri::{
    ipc::{InvokeBody, Request},
    State,
};

#[derive(Debug, Clone, Copy, Deserialize, Serialize)]
#[serde(rename_all = "snake_case")]
enum Category {
    Validation,
    NotFound,
    Conflict,
    Unavailable,
    Cancelled,
    Internal,
}

#[derive(Debug, Clone, Copy, Deserialize, Serialize)]
#[serde(rename_all = "snake_case")]
enum Phase {
    Profile,
    Binding,
    CredentialInput,
    CredentialStore,
    CredentialBinding,
    NetworkProxy,
    Dns,
    Tcp,
    Tls,
    Http,
    ProviderAuth,
    SettingsResolution,
}

#[derive(Debug, Clone, Copy, Deserialize, Serialize)]
#[serde(rename_all = "snake_case")]
enum Action {
    Retry,
    EditProfile,
    ConfigureCredential,
    SelectProfile,
    ReviewTlsSetting,
    ClearBinding,
    ContactSupport,
    None,
}

#[derive(Debug, Clone, Copy, Deserialize, Serialize)]
enum MessageKey {
    #[serde(rename = "SETTINGS_INVALID_INPUT")]
    SettingsInvalidInput,
    #[serde(rename = "SETTINGS_ITEM_NOT_FOUND")]
    SettingsItemNotFound,
    #[serde(rename = "SETTINGS_CONFLICT")]
    SettingsConflict,
    #[serde(rename = "SETTINGS_UNAVAILABLE")]
    SettingsUnavailable,
    #[serde(rename = "CREDENTIAL_INPUT_CANCELLED")]
    CredentialInputCancelled,
    #[serde(rename = "CREDENTIAL_STORE_UNAVAILABLE")]
    CredentialStoreUnavailable,
    #[serde(rename = "NETWORK_STAGE_FAILED")]
    NetworkStageFailed,
    #[serde(rename = "TLS_CONFIRMATION_REQUIRED")]
    TlsConfirmationRequired,
}

#[derive(Debug, Clone, Copy, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
struct ErrorDetails {
    phase: Phase,
    action: Action,
    message_key: MessageKey,
}

#[derive(Debug, Serialize)]
#[serde(deny_unknown_fields)]
pub struct SettingsSurfaceError {
    category: Category,
    phase: Phase,
    action: Action,
    message_key: MessageKey,
}

impl SettingsSurfaceError {
    fn unavailable() -> Self {
        Self {
            category: Category::Unavailable,
            phase: Phase::SettingsResolution,
            action: Action::ContactSupport,
            message_key: MessageKey::SettingsUnavailable,
        }
    }

    fn from_core(error: LibraryError) -> Self {
        let category = match error.category.as_str() {
            "validation" => Category::Validation,
            "not_found" => Category::NotFound,
            "conflict" => Category::Conflict,
            "unavailable" => Category::Unavailable,
            "cancelled" => Category::Cancelled,
            _ => Category::Internal,
        };
        error
            .details
            .and_then(|details| serde_json::from_value::<ErrorDetails>(details).ok())
            .map(|details| Self {
                category,
                phase: details.phase,
                action: details.action,
                message_key: details.message_key,
            })
            .unwrap_or_else(Self::unavailable)
    }

    fn credential_validation() -> Self {
        Self {
            category: Category::Validation,
            phase: Phase::CredentialInput,
            action: Action::ConfigureCredential,
            message_key: MessageKey::SettingsInvalidInput,
        }
    }

    fn credential_not_found() -> Self {
        Self {
            category: Category::NotFound,
            phase: Phase::CredentialBinding,
            action: Action::ConfigureCredential,
            message_key: MessageKey::SettingsItemNotFound,
        }
    }

    fn credential_conflict() -> Self {
        Self {
            category: Category::Conflict,
            phase: Phase::CredentialBinding,
            action: Action::ConfigureCredential,
            message_key: MessageKey::SettingsConflict,
        }
    }

    fn credential_cancelled() -> Self {
        Self {
            category: Category::Cancelled,
            phase: Phase::CredentialInput,
            action: Action::None,
            message_key: MessageKey::CredentialInputCancelled,
        }
    }

    fn credential_store_unavailable() -> Self {
        Self {
            category: Category::Unavailable,
            phase: Phase::CredentialStore,
            action: Action::ConfigureCredential,
            message_key: MessageKey::CredentialStoreUnavailable,
        }
    }
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct CredentialPutRequest {
    target: P15CredentialTarget,
    intent: CredentialIntent,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "snake_case")]
enum CredentialIntent {
    Create,
    Replace,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct CredentialClearRequest {
    target: P15CredentialTarget,
}

#[derive(Debug, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
enum CredentialPutState {
    Configured,
}

#[derive(Debug, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
enum CredentialClearState {
    Missing,
}

#[derive(Debug, Serialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct CredentialPutResult {
    state: CredentialPutState,
}

#[derive(Debug, Serialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct CredentialClearResult {
    state: CredentialClearState,
}

fn parse_credential_payload<T: DeserializeOwned>(value: &Value) -> Result<T, SettingsSurfaceError> {
    serde_json::from_value(value.clone()).map_err(|_| SettingsSurfaceError::credential_validation())
}

fn parse_credential_request<T: DeserializeOwned>(
    request: &Request<'_>,
) -> Result<T, SettingsSurfaceError> {
    match request.body() {
        InvokeBody::Json(value) => parse_credential_payload(value),
        InvokeBody::Raw(_) => Err(SettingsSurfaceError::credential_validation()),
    }
}

fn credential_target_owner(target: &P15CredentialTarget) -> (&'static str, &str) {
    match target {
        P15CredentialTarget::ProviderApi { profile_id } => ("provider", profile_id),
        P15CredentialTarget::ProxyAuth { network_profile_id } => ("proxy", network_profile_id),
    }
}

fn new_credential_ref(target: &P15CredentialTarget) -> Result<String, SettingsSurfaceError> {
    let (kind, owner) = credential_target_owner(target);
    let mut bytes = [0u8; 16];
    OsRng
        .try_fill_bytes(&mut bytes)
        .map_err(|_| SettingsSurfaceError::credential_store_unavailable())?;
    let suffix = bytes
        .iter()
        .map(|byte| format!("{byte:02x}"))
        .collect::<String>();
    Ok(format!("NewManga/{kind}/{owner}/{suffix}"))
}

fn credential_is_configured(
    state: &State<'_, super::AppState>,
    target: &P15CredentialTarget,
) -> Result<bool, SettingsSurfaceError> {
    match target {
        P15CredentialTarget::ProviderApi { profile_id } => {
            let profiles: ProfileList<ProviderProfile> =
                call(state, P15SettingsCommand::ProviderProfilesList, json!({}))?;
            profiles
                .profiles
                .into_iter()
                .find(|profile| profile.profile_id == *profile_id)
                .map(|profile| profile.credential_state == "configured")
                .ok_or_else(SettingsSurfaceError::credential_not_found)
        }
        P15CredentialTarget::ProxyAuth { network_profile_id } => {
            let profiles: ProfileList<NetworkProfile> =
                call(state, P15SettingsCommand::NetworkProfilesList, json!({}))?;
            profiles
                .profiles
                .into_iter()
                .find(|profile| profile.network_profile_id == *network_profile_id)
                .map(|profile| profile.credential_state == "configured")
                .ok_or_else(SettingsSurfaceError::credential_not_found)
        }
    }
}

fn credential_intent_matches(intent: &CredentialIntent, configured: bool) -> bool {
    matches!(
        (intent, configured),
        (CredentialIntent::Create, false) | (CredentialIntent::Replace, true)
    )
}

fn acquire_credential_operation<'a>(
    state: &'a State<'_, super::AppState>,
) -> Result<std::sync::MutexGuard<'a, ()>, SettingsSurfaceError> {
    state
        .credential_operations
        .lock()
        .map_err(|_| SettingsSurfaceError::credential_store_unavailable())
}

#[tauri::command]
pub fn credential_put(
    state: State<'_, super::AppState>,
    request: Request<'_>,
) -> Result<CredentialPutResult, SettingsSurfaceError> {
    let request: CredentialPutRequest = parse_credential_request(&request)?;
    let _operation = acquire_credential_operation(&state)?;
    let configured = credential_is_configured(&state, &request.target)?;
    if !credential_intent_matches(&request.intent, configured) {
        return Err(SettingsSurfaceError::credential_conflict());
    }

    let credential_ref = new_credential_ref(&request.target)?;
    match super::credential_manager::prompt_and_store(&credential_ref) {
        Ok(super::credential_manager::PromptResult::Stored) => {}
        Ok(super::credential_manager::PromptResult::Cancelled) => {
            return Err(SettingsSurfaceError::credential_cancelled())
        }
        Err(()) => return Err(SettingsSurfaceError::credential_store_unavailable()),
    }

    let configured_after_input = match credential_is_configured(&state, &request.target) {
        Ok(configured) => configured,
        Err(error) => {
            let _ = super::credential_manager::delete(&credential_ref);
            return Err(error);
        }
    };
    if !credential_intent_matches(&request.intent, configured_after_input) {
        let _ = super::credential_manager::delete(&credential_ref);
        return Err(SettingsSurfaceError::credential_conflict());
    }

    let Some(library) = state.library.as_ref() else {
        let _ = super::credential_manager::delete(&credential_ref);
        return Err(SettingsSurfaceError::unavailable());
    };
    let bind = library.bind_profile_credential(request.target, &credential_ref);
    if let Err(error) = bind {
        return Err(SettingsSurfaceError::from_core(error));
    }

    Ok(CredentialPutResult {
        state: CredentialPutState::Configured,
    })
}

#[tauri::command]
pub fn credential_clear(
    state: State<'_, super::AppState>,
    request: Request<'_>,
) -> Result<CredentialClearResult, SettingsSurfaceError> {
    let request: CredentialClearRequest = parse_credential_request(&request)?;
    let _operation = acquire_credential_operation(&state)?;
    state
        .library
        .as_ref()
        .ok_or_else(SettingsSurfaceError::unavailable)?
        .clear_profile_credential(request.target)
        .map_err(SettingsSurfaceError::from_core)?;
    Ok(CredentialClearResult {
        state: CredentialClearState::Missing,
    })
}

trait SafeProjection {
    fn is_safe(&self) -> bool;
}

fn call<T: DeserializeOwned + SafeProjection>(
    state: &State<'_, super::AppState>,
    command: P15SettingsCommand,
    payload: Value,
) -> Result<T, SettingsSurfaceError> {
    let raw = state
        .library
        .as_ref()
        .ok_or_else(SettingsSurfaceError::unavailable)?
        .p15_settings(command, payload)
        .map_err(SettingsSurfaceError::from_core)?;
    let result: T = serde_json::from_value(raw).map_err(|_| SettingsSurfaceError::unavailable())?;
    if result.is_safe() {
        Ok(result)
    } else {
        Err(SettingsSurfaceError::unavailable())
    }
}

fn valid_capability(value: &str) -> bool {
    matches!(
        value,
        "OCR" | "Translation" | "Inpaint" | "Detection" | "Rendering"
    )
}

fn safe_endpoint(value: &str, schemes: &[&str]) -> bool {
    if value.chars().any(char::is_whitespace) || value.chars().any(char::is_control) {
        return false;
    }
    let Some((scheme, rest)) = value.split_once("://") else {
        return false;
    };
    let authority = rest.split('/').next().unwrap_or_default();
    schemes.contains(&scheme)
        && !authority.is_empty()
        && !authority.contains('@')
        && !value.contains('?')
        && !value.contains('#')
}

fn safe_id(value: &str) -> bool {
    !value.is_empty()
        && !value.contains('/')
        && !value.contains('\\')
        && !value.chars().any(char::is_control)
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ProviderProfile {
    profile_id: String,
    provider_id: String,
    display_name: String,
    capabilities: Vec<String>,
    endpoint: String,
    model: String,
    #[serde(deserialize_with = "required_option")]
    network_profile_id: Option<String>,
    enabled: bool,
    credential_state: String,
    #[allow(dead_code)]
    #[serde(default, skip_serializing)]
    credential_hint: Option<String>,
}

impl SafeProjection for ProviderProfile {
    fn is_safe(&self) -> bool {
        safe_id(&self.profile_id)
            && self.network_profile_id.as_deref().is_none_or(safe_id)
            && safe_endpoint(&self.endpoint, &["http", "https"])
            && matches!(self.credential_state.as_str(), "configured" | "missing")
            && self
                .capabilities
                .iter()
                .all(|value| valid_capability(value))
            && self
                .capabilities
                .iter()
                .collect::<std::collections::HashSet<_>>()
                .len()
                == self.capabilities.len()
    }
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct NetworkProfile {
    network_profile_id: String,
    display_name: String,
    mode: String,
    #[serde(deserialize_with = "required_option")]
    proxy_endpoint: Option<String>,
    verify_tls: bool,
    tls_verification_state: String,
    allow_proxy_failure_direct_fallback: bool,
    credential_state: String,
    #[allow(dead_code)]
    #[serde(default, skip_serializing)]
    credential_hint: Option<String>,
}

impl SafeProjection for NetworkProfile {
    fn is_safe(&self) -> bool {
        let expected_scheme = match self.mode.as_str() {
            "Direct" | "System" => None,
            "HTTP" => Some("http"),
            "HTTPS" => Some("https"),
            "SOCKS5" => Some("socks5"),
            _ => return false,
        };
        let endpoint_ok = match (expected_scheme, self.proxy_endpoint.as_deref()) {
            (None, None) => true,
            (Some(scheme), Some(endpoint)) => safe_endpoint(endpoint, &[scheme]),
            _ => false,
        };
        endpoint_ok
            && safe_id(&self.network_profile_id)
            && self.tls_verification_state
                == if self.verify_tls {
                    "enabled"
                } else {
                    "disabled_confirmed"
                }
            && matches!(self.credential_state.as_str(), "configured" | "missing")
    }
}

fn required_option<'de, D, T>(deserializer: D) -> Result<Option<T>, D::Error>
where
    D: serde::Deserializer<'de>,
    T: Deserialize<'de>,
{
    Option::deserialize(deserializer)
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ProfileList<T> {
    profiles: Vec<T>,
}

impl SafeProjection for ProfileList<ProviderProfile> {
    fn is_safe(&self) -> bool {
        self.profiles.iter().all(SafeProjection::is_safe)
    }
}

impl SafeProjection for ProfileList<NetworkProfile> {
    fn is_safe(&self) -> bool {
        self.profiles.iter().all(SafeProjection::is_safe)
    }
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ProfileResult<T> {
    profile: T,
}

impl SafeProjection for ProfileResult<ProviderProfile> {
    fn is_safe(&self) -> bool {
        self.profile.is_safe()
    }
}

impl SafeProjection for ProfileResult<NetworkProfile> {
    fn is_safe(&self) -> bool {
        self.profile.is_safe()
    }
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct DeleteResult {
    deleted: bool,
}

impl SafeProjection for DeleteResult {
    fn is_safe(&self) -> bool {
        self.deleted
    }
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct BindingScope {
    kind: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    book_id: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    chapter_id: Option<String>,
}

impl BindingScope {
    fn is_safe(&self, allow_run: bool) -> bool {
        match self.kind.as_str() {
            "global" => self.book_id.is_none() && self.chapter_id.is_none(),
            "book" => self.book_id.as_deref().is_some_and(safe_id) && self.chapter_id.is_none(),
            "chapter" => self.chapter_id.as_deref().is_some_and(safe_id) && self.book_id.is_none(),
            "run" => allow_run && self.book_id.is_none() && self.chapter_id.is_none(),
            _ => false,
        }
    }
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
struct BindingSource {
    kind: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    book_id: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    chapter_id: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    run_id: Option<String>,
}

impl BindingSource {
    fn is_safe(&self) -> bool {
        match self.kind.as_str() {
            "global" => {
                self.book_id.is_none() && self.chapter_id.is_none() && self.run_id.is_none()
            }
            "book" => {
                self.book_id.as_deref().is_some_and(safe_id)
                    && self.chapter_id.is_none()
                    && self.run_id.is_none()
            }
            "chapter" => {
                self.chapter_id.as_deref().is_some_and(safe_id)
                    && self.book_id.is_none()
                    && self.run_id.is_none()
            }
            "run" => {
                self.run_id.as_deref().is_some_and(safe_id)
                    && self.book_id.is_none()
                    && self.chapter_id.is_none()
            }
            _ => false,
        }
    }
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
struct CapabilityBinding {
    scope: BindingScope,
    capability: String,
    profile_id: String,
}

impl SafeProjection for CapabilityBinding {
    fn is_safe(&self) -> bool {
        self.scope.is_safe(false) && valid_capability(&self.capability)
    }
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct BindingResult {
    binding: CapabilityBinding,
}

impl SafeProjection for BindingResult {
    fn is_safe(&self) -> bool {
        self.binding.is_safe()
    }
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ClearedResult {
    cleared: bool,
}

impl SafeProjection for ClearedResult {
    fn is_safe(&self) -> bool {
        self.cleared
    }
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct BindingResolution {
    profile_id: Option<String>,
    source: Option<BindingSource>,
}

impl SafeProjection for BindingResolution {
    fn is_safe(&self) -> bool {
        self.profile_id.as_deref().is_none_or(safe_id)
            && self.source.as_ref().is_none_or(BindingSource::is_safe)
    }
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
struct FrozenNetwork {
    #[serde(deserialize_with = "required_option")]
    network_profile_id: Option<String>,
    mode: String,
    #[serde(deserialize_with = "required_option")]
    proxy_endpoint: Option<String>,
    verify_tls: bool,
    tls_verification_state: String,
    allow_proxy_failure_direct_fallback: bool,
    credential_state_at_snapshot: String,
}

impl FrozenNetwork {
    fn is_safe(&self) -> bool {
        let expected_scheme = match self.mode.as_str() {
            "Direct" | "System" => None,
            "HTTP" => Some("http"),
            "HTTPS" => Some("https"),
            "SOCKS5" => Some("socks5"),
            _ => return false,
        };
        let endpoint_safe = match (expected_scheme, self.proxy_endpoint.as_deref()) {
            (None, None) => true,
            (Some(scheme), Some(endpoint)) => safe_endpoint(endpoint, &[scheme]),
            _ => false,
        };
        endpoint_safe
            && self.network_profile_id.as_deref().is_none_or(safe_id)
            && matches!(
                self.credential_state_at_snapshot.as_str(),
                "configured" | "missing"
            )
            && self.tls_verification_state
                == if self.verify_tls {
                    "enabled"
                } else {
                    "disabled_confirmed"
                }
    }
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
struct FrozenBinding {
    capability: String,
    profile_id: String,
    provider_id: String,
    display_name: String,
    endpoint: String,
    model: String,
    provider_credential_state_at_snapshot: String,
    network: FrozenNetwork,
    source: BindingSource,
}

impl SafeProjection for FrozenBinding {
    fn is_safe(&self) -> bool {
        valid_capability(&self.capability)
            && safe_id(&self.profile_id)
            && safe_endpoint(&self.endpoint, &["http", "https"])
            && matches!(
                self.provider_credential_state_at_snapshot.as_str(),
                "configured" | "missing"
            )
            && self.network.is_safe()
            && self.source.is_safe()
    }
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct RunSnapshot {
    run_id: String,
    frozen: bool,
    bindings: Vec<FrozenBinding>,
}

impl SafeProjection for RunSnapshot {
    fn is_safe(&self) -> bool {
        safe_id(&self.run_id) && self.frozen && self.bindings.iter().all(SafeProjection::is_safe)
    }
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
struct StageFailure {
    category: Category,
    action: Action,
    message_key: MessageKey,
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
struct StageResult {
    stage: String,
    status: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    failure: Option<StageFailure>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    duration_ms: Option<u64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    reason: Option<String>,
}

impl StageResult {
    fn is_safe(&self) -> bool {
        match self.status.as_str() {
            "passed" => self.failure.is_none() && self.reason.is_none(),
            "failed" => self.failure.is_some() && self.reason.is_none(),
            "not_run" | "not_applicable" => {
                self.failure.is_none()
                    && self.reason.as_deref().is_some_and(|reason| {
                        matches!(
                            reason,
                            "upstream_stage_failed"
                                | "provider_profile_not_selected"
                                | "direct_mode"
                                | "system_route_is_direct"
                                | "provider_endpoint_is_ip_literal"
                                | "provider_endpoint_uses_http"
                                | "provider_auth_not_required"
                        )
                    })
            }
            _ => false,
        }
    }
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct NetworkTestResult {
    status: String,
    #[serde(deserialize_with = "required_option")]
    failed_stage: Option<String>,
    direct_fallback_used: bool,
    stages: Vec<StageResult>,
}

impl SafeProjection for NetworkTestResult {
    fn is_safe(&self) -> bool {
        const STAGES: [&str; 6] = ["Proxy", "DNS", "TCP", "TLS", "HTTP", "ProviderAuth"];
        if self.direct_fallback_used
            || self.stages.len() != STAGES.len()
            || !self
                .stages
                .iter()
                .zip(STAGES)
                .all(|(actual, expected)| actual.stage == expected && actual.is_safe())
        {
            return false;
        }
        let failed: Vec<_> = self
            .stages
            .iter()
            .filter(|stage| stage.status == "failed")
            .collect();
        match self.status.as_str() {
            "passed" => self.failed_stage.is_none() && failed.is_empty(),
            "failed" => {
                failed.len() == 1 && self.failed_stage.as_deref() == Some(failed[0].stage.as_str())
            }
            _ => false,
        }
    }
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct NetworkDefaultResult {
    #[serde(deserialize_with = "required_option")]
    network_profile_id: Option<String>,
}

impl SafeProjection for NetworkDefaultResult {
    fn is_safe(&self) -> bool {
        true
    }
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct NetworkResolution {
    #[serde(deserialize_with = "required_option")]
    network_profile_id: Option<String>,
    mode: String,
    source: String,
}

impl SafeProjection for NetworkResolution {
    fn is_safe(&self) -> bool {
        matches!(
            self.mode.as_str(),
            "Direct" | "System" | "HTTP" | "HTTPS" | "SOCKS5"
        ) && matches!(
            self.source.as_str(),
            "provider" | "global" | "system" | "direct"
        )
    }
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
struct ResolvedSetting {
    key: String,
    value: Value,
    source: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    source_id: Option<String>,
    is_default: bool,
}

impl SafeProjection for ResolvedSetting {
    fn is_safe(&self) -> bool {
        const KEYS: [&str; 7] = [
            "reading.direction",
            "sfx.policy",
            "context.strategy",
            "text.style",
            "font.auto_size",
            "translation.parameters",
            "repair.quality",
        ];
        if !KEYS.contains(&self.key.as_str()) {
            return false;
        }
        if self.value.is_null() {
            return self.source.is_none() && self.source_id.is_none() && !self.is_default;
        }
        let Some(value) = self.value.as_str() else {
            return false;
        };
        let value_ok = match (self.key.as_str(), value) {
            ("reading.direction", value) => {
                matches!(value, "ltr" | "rtl" | "vertical-rtl") && self.source.is_some()
            }
            ("sfx.policy", value) => {
                matches!(value, "skip" | "translate" | "manual") && self.source.is_some()
            }
            _ => false,
        };
        value_ok
            && self
                .source
                .as_deref()
                .is_some_and(|source| matches!(source, "global" | "book" | "chapter" | "run"))
            && self.source_id.as_deref().is_none_or(safe_id)
    }
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct OverridesResult {
    values: Vec<ResolvedSetting>,
}

impl SafeProjection for OverridesResult {
    fn is_safe(&self) -> bool {
        self.values.iter().all(SafeProjection::is_safe)
    }
}

#[tauri::command(rename_all = "snake_case")]
pub fn settings_provider_profiles_list(
    state: State<'_, super::AppState>,
) -> Result<ProfileList<ProviderProfile>, SettingsSurfaceError> {
    call(&state, P15SettingsCommand::ProviderProfilesList, json!({}))
}

#[tauri::command(rename_all = "snake_case")]
pub fn settings_provider_profiles_create(
    state: State<'_, super::AppState>,
    provider_id: String,
    display_name: String,
    capabilities: Vec<String>,
    endpoint: String,
    model: String,
    network_profile_id: Option<String>,
    enabled: bool,
) -> Result<ProfileResult<ProviderProfile>, SettingsSurfaceError> {
    call(
        &state,
        P15SettingsCommand::ProviderProfilesCreate,
        json!({
            "provider_id": provider_id, "display_name": display_name, "capabilities": capabilities,
            "endpoint": endpoint, "model": model, "network_profile_id": network_profile_id,
            "enabled": enabled,
        }),
    )
}

#[tauri::command(rename_all = "snake_case")]
pub fn settings_provider_profiles_update(
    state: State<'_, super::AppState>,
    profile_id: String,
    display_name: String,
    capabilities: Vec<String>,
    endpoint: String,
    model: String,
    network_profile_id: Option<String>,
    enabled: bool,
) -> Result<ProfileResult<ProviderProfile>, SettingsSurfaceError> {
    call(
        &state,
        P15SettingsCommand::ProviderProfilesUpdate,
        json!({
            "profile_id": profile_id, "display_name": display_name, "capabilities": capabilities,
            "endpoint": endpoint, "model": model, "network_profile_id": network_profile_id,
            "enabled": enabled,
        }),
    )
}

#[tauri::command(rename_all = "snake_case")]
pub fn settings_provider_profiles_delete(
    state: State<'_, super::AppState>,
    profile_id: String,
) -> Result<DeleteResult, SettingsSurfaceError> {
    call(
        &state,
        P15SettingsCommand::ProviderProfilesDelete,
        json!({ "profile_id": profile_id }),
    )
}

#[tauri::command(rename_all = "snake_case")]
pub fn settings_provider_bindings_set(
    state: State<'_, super::AppState>,
    scope: BindingScope,
    capability: String,
    profile_id: String,
) -> Result<BindingResult, SettingsSurfaceError> {
    call(
        &state,
        P15SettingsCommand::ProviderBindingsSet,
        json!({
            "scope": scope, "capability": capability, "profile_id": profile_id,
        }),
    )
}

#[tauri::command(rename_all = "snake_case")]
pub fn settings_provider_bindings_clear(
    state: State<'_, super::AppState>,
    scope: BindingScope,
    capability: String,
) -> Result<ClearedResult, SettingsSurfaceError> {
    call(
        &state,
        P15SettingsCommand::ProviderBindingsClear,
        json!({ "scope": scope, "capability": capability }),
    )
}

#[tauri::command(rename_all = "snake_case")]
pub fn settings_provider_bindings_resolve(
    state: State<'_, super::AppState>,
    capability: String,
    book_id: Option<String>,
    chapter_id: Option<String>,
    run_id: Option<String>,
) -> Result<BindingResolution, SettingsSurfaceError> {
    let mut payload = json!({ "capability": capability });
    for (name, value) in [
        ("book_id", book_id),
        ("chapter_id", chapter_id),
        ("run_id", run_id),
    ] {
        if let Some(value) = value {
            payload[name] = json!(value);
        }
    }
    call(&state, P15SettingsCommand::ProviderBindingsResolve, payload)
}

#[tauri::command(rename_all = "snake_case")]
pub fn settings_provider_run_snapshot_get(
    state: State<'_, super::AppState>,
    run_id: String,
) -> Result<RunSnapshot, SettingsSurfaceError> {
    call(
        &state,
        P15SettingsCommand::ProviderRunSnapshotGet,
        json!({ "run_id": run_id }),
    )
}

#[tauri::command(rename_all = "snake_case")]
pub fn settings_network_profiles_list(
    state: State<'_, super::AppState>,
) -> Result<ProfileList<NetworkProfile>, SettingsSurfaceError> {
    call(&state, P15SettingsCommand::NetworkProfilesList, json!({}))
}

#[tauri::command(rename_all = "snake_case")]
pub fn settings_network_profiles_create(
    state: State<'_, super::AppState>,
    display_name: String,
    mode: String,
    proxy_endpoint: Option<String>,
    verify_tls: Option<bool>,
    confirm_disable_tls_verification: Option<bool>,
    allow_proxy_failure_direct_fallback: Option<bool>,
) -> Result<ProfileResult<NetworkProfile>, SettingsSurfaceError> {
    let mut payload =
        json!({ "display_name": display_name, "mode": mode, "proxy_endpoint": proxy_endpoint });
    for (name, value) in [
        ("verify_tls", verify_tls),
        (
            "confirm_disable_tls_verification",
            confirm_disable_tls_verification,
        ),
        (
            "allow_proxy_failure_direct_fallback",
            allow_proxy_failure_direct_fallback,
        ),
    ] {
        if let Some(value) = value {
            payload[name] = json!(value);
        }
    }
    call(&state, P15SettingsCommand::NetworkProfilesCreate, payload)
}

#[tauri::command(rename_all = "snake_case")]
pub fn settings_network_profiles_update(
    state: State<'_, super::AppState>,
    network_profile_id: String,
    display_name: String,
    mode: String,
    proxy_endpoint: Option<String>,
    verify_tls: bool,
    confirm_disable_tls_verification: Option<bool>,
    allow_proxy_failure_direct_fallback: bool,
) -> Result<ProfileResult<NetworkProfile>, SettingsSurfaceError> {
    let mut payload = json!({
        "network_profile_id": network_profile_id, "display_name": display_name, "mode": mode,
        "proxy_endpoint": proxy_endpoint, "verify_tls": verify_tls,
        "allow_proxy_failure_direct_fallback": allow_proxy_failure_direct_fallback,
    });
    if let Some(value) = confirm_disable_tls_verification {
        payload["confirm_disable_tls_verification"] = json!(value);
    }
    call(&state, P15SettingsCommand::NetworkProfilesUpdate, payload)
}

#[tauri::command(rename_all = "snake_case")]
pub fn settings_network_profiles_delete(
    state: State<'_, super::AppState>,
    network_profile_id: String,
) -> Result<DeleteResult, SettingsSurfaceError> {
    call(
        &state,
        P15SettingsCommand::NetworkProfilesDelete,
        json!({ "network_profile_id": network_profile_id }),
    )
}

#[tauri::command(rename_all = "snake_case")]
pub fn settings_network_profiles_test(
    state: State<'_, super::AppState>,
    network_profile_id: String,
    provider_profile_id: Option<String>,
) -> Result<NetworkTestResult, SettingsSurfaceError> {
    let mut payload = json!({ "network_profile_id": network_profile_id });
    if let Some(value) = provider_profile_id {
        payload["provider_profile_id"] = json!(value);
    }
    call(&state, P15SettingsCommand::NetworkProfilesTest, payload)
}

#[tauri::command(rename_all = "snake_case")]
pub fn settings_network_profile_default_set(
    state: State<'_, super::AppState>,
    network_profile_id: String,
) -> Result<NetworkDefaultResult, SettingsSurfaceError> {
    call(
        &state,
        P15SettingsCommand::NetworkProfileDefaultSet,
        json!({ "network_profile_id": network_profile_id }),
    )
}

#[tauri::command(rename_all = "snake_case")]
pub fn settings_network_profile_default_clear(
    state: State<'_, super::AppState>,
) -> Result<NetworkDefaultResult, SettingsSurfaceError> {
    call(
        &state,
        P15SettingsCommand::NetworkProfileDefaultClear,
        json!({}),
    )
}

#[tauri::command(rename_all = "snake_case")]
pub fn settings_network_profile_resolve(
    state: State<'_, super::AppState>,
    provider_profile_id: Option<String>,
) -> Result<NetworkResolution, SettingsSurfaceError> {
    let mut payload = json!({});
    if let Some(value) = provider_profile_id {
        payload["provider_profile_id"] = json!(value);
    }
    call(&state, P15SettingsCommand::NetworkProfileResolve, payload)
}

#[tauri::command(rename_all = "snake_case")]
pub fn settings_resolve_overrides(
    state: State<'_, super::AppState>,
    keys: Vec<String>,
    book_id: Option<String>,
    chapter_id: Option<String>,
    run_id: Option<String>,
) -> Result<OverridesResult, SettingsSurfaceError> {
    let mut payload = json!({ "keys": keys });
    for (name, value) in [
        ("book_id", book_id),
        ("chapter_id", chapter_id),
        ("run_id", run_id),
    ] {
        if let Some(value) = value {
            payload[name] = json!(value);
        }
    }
    call(&state, P15SettingsCommand::ResolveOverrides, payload)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn closed_projection_rejects_credential_refs_and_projects_only_safe_errors() {
        let leaked_snapshot = json!({
            "run_id": "run-1", "frozen": true, "bindings": [{
                "capability": "OCR", "profile_id": "p-1", "provider_id": "provider",
                "display_name": "Profile", "endpoint": "https://api.example/v1", "model": "m",
                "provider_credential_state_at_snapshot": "configured",
                "network": {
                    "network_profile_id": null, "mode": "Direct", "proxy_endpoint": null,
                    "verify_tls": true, "tls_verification_state": "enabled",
                    "allow_proxy_failure_direct_fallback": false,
                    "credential_state_at_snapshot": "missing", "credential_ref": "private-ref"
                },
                "source": { "kind": "global" }
            }]
        });
        assert!(serde_json::from_value::<RunSnapshot>(leaked_snapshot).is_err());

        let mut error = LibraryError::new("UNKNOWN", "internal", false, Some("private text"));
        error.details = Some(json!({
            "phase": "profile", "action": "contact_support",
            "message_key": "SETTINGS_UNAVAILABLE", "credential_ref": "private-ref"
        }));
        let projected = SettingsSurfaceError::from_core(error);
        let projected = serde_json::to_value(projected).unwrap();
        assert_eq!(projected.as_object().unwrap().len(), 4);
        assert!(!projected.to_string().contains("private"));
    }

    #[test]
    fn credential_requests_reject_secret_and_reference_fields() {
        let target = json!({ "kind": "provider_api", "profile_id": "profile-1" });
        let secret_attempt = json!({
            "target": target,
            "intent": "create",
            "secret": "host-only-marker"
        });
        let error = parse_credential_payload::<CredentialPutRequest>(&secret_attempt).unwrap_err();
        let error_wire = serde_json::to_string(&error).unwrap();
        assert!(error_wire.contains("validation"));
        assert!(!error_wire.contains("host-only-marker"));

        let reference_attempt = json!({
            "target": {
                "kind": "provider_api",
                "profile_id": "profile-1",
                "credential_ref": "private-ref-marker"
            },
            "intent": "replace"
        });
        assert!(parse_credential_payload::<CredentialPutRequest>(&reference_attempt).is_err());
        assert!(parse_credential_payload::<CredentialClearRequest>(&json!({
            "target": target,
            "secret": "host-only-marker"
        }))
        .is_err());
    }

    #[test]
    fn credential_intent_conflicts_before_any_input_or_binding_step() {
        assert!(!credential_intent_matches(&CredentialIntent::Create, true));
        assert!(!credential_intent_matches(
            &CredentialIntent::Replace,
            false
        ));
        assert!(credential_intent_matches(&CredentialIntent::Create, false));
        assert!(credential_intent_matches(&CredentialIntent::Replace, true));
        let error = SettingsSurfaceError::credential_conflict();
        let projected = serde_json::to_value(error).unwrap();
        assert_eq!(projected["category"], "conflict");
        assert_eq!(projected["message_key"], "SETTINGS_CONFLICT");
    }

    #[test]
    fn credential_results_expose_only_contract_state() {
        let put = serde_json::to_value(CredentialPutResult {
            state: CredentialPutState::Configured,
        })
        .unwrap();
        let clear = serde_json::to_value(CredentialClearResult {
            state: CredentialClearState::Missing,
        })
        .unwrap();
        assert_eq!(put, json!({ "state": "configured" }));
        assert_eq!(clear, json!({ "state": "missing" }));
        assert!(!put.to_string().contains("credential_ref"));
        assert!(!clear.to_string().contains("secret"));
    }
}
