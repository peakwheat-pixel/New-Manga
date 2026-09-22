"""SettingsViewModel: settings page state between QML and the settings
services (T1.2.1, D05 §43.1).

Published to QML as ``settingsViewModel``. The page's Provider and
网络/代理 categories are live: provider profiles (endpoint, model,
credential), network profiles (proxy), per-capability provider
bindings and the default network profile survive restart and feed the
pipeline through the ``pipeline_defaults`` row the run snapshot reader
already consumes.

Security posture (AC-SEC-001~005, D07 §69):

- API keys and proxy passwords are written straight into the credential
  vault; profiles persist only the ``credential_ref``. The viewmodel
  never exposes a secret — the QML forms show password fields with no
  echo-back, and the profile views carry only a ``credential_set`` flag;
- ``confirmationRequired`` fires for dangerous changes (TLS off) so QML
  can demand an explicit confirmation and re-submit with the confirm
  flag set (AC-SEC-005);
- error messages are built from ids and static text only — a
  ``SecretValue`` can never surface through ``error``/logs (AC-SEC-002).

QML never touches stores or files directly; every read/write goes
through the application services injected here.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from PySide6.QtCore import Property, QObject, Signal, Slot

from application.settings.errors import SettingsError
from application.settings.network import DangerousSettingError, NetworkProfileService
from application.settings.pipeline_defaults import PipelineDefaultsService
from application.settings.pipeline_defaults import BindingValidationError
from ports.providers.credentials import SecretValue
from ports.providers.profiles import ALL_CAPABILITIES
from ports.network.profiles import ALL_MODES


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


#: QML binds by capability name (D03 §25); the pipeline_defaults row and
#: the run snapshot reader carry the production handler step names, so
#: the viewmodel translates at the seam instead of leaking both naming
#: schemes into the persisted row.
_CAPABILITY_TO_STEP = {
    "detection": "detect",
    "ocr": "ocr",
    "translation": "translate",
    "inpaint": "inpaint",
}
_STEP_TO_CAPABILITY = {step: cap for cap, step in _CAPABILITY_TO_STEP.items()}


def _binding_profile_id(binding: Any) -> str:
    """Normalize a stored binding (id string or mapping) for display."""
    if isinstance(binding, str):
        return binding
    if isinstance(binding, dict):
        for key in ("provider_profile_id", "provider_id", "id"):
            value = binding.get(key)
            if isinstance(value, str) and value.strip():
                return value
    return ""


class SettingsViewModel(QObject):
    """Controller for the settings page (Provider / network categories)."""

    profilesChanged = Signal()
    networksChanged = Signal()
    defaultsChanged = Signal()
    saved = Signal(str)
    failed = Signal(str)
    #: A dangerous change needs explicit user confirmation; QML shows the
    #: dialog and re-submits the same form with the confirm flag set.
    confirmationRequired = Signal(str)

    def __init__(
        self,
        *,
        provider_store,
        network_service: NetworkProfileService,
        credential_store,
        pipeline_defaults: PipelineDefaultsService,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._providers = provider_store
        self._networks = network_service
        self._credentials = credential_store
        self._defaults = pipeline_defaults

    # ------------------------------------------------------------------
    # read models for QML
    # ------------------------------------------------------------------

    @Property(list, notify=profilesChanged)
    def profiles(self) -> list[dict]:
        views = []
        try:
            profiles = self._providers.list_profiles()
        except (SettingsError, ValueError, OSError) as error:
            self.failed.emit(f"读取 Provider 配置失败：{error}")
            return []
        for profile in sorted(profiles, key=lambda p: p.provider_profile_id):
            views.append(
                {
                    "provider_profile_id": profile.provider_profile_id,
                    "name": profile.name,
                    "provider_type": profile.provider_type,
                    "capabilities": sorted(profile.capabilities),
                    "base_url": profile.base_url,
                    "model": profile.model,
                    "credential_ref": profile.credential_ref or "",
                    "credential_set": self._has_credential(profile.credential_ref),
                    "network_profile_id": profile.network_profile_id or "",
                    "proxy_policy": profile.proxy_policy,
                    "is_enabled": profile.is_enabled,
                    "is_local": profile.is_local(),
                }
            )
        return views

    @Property(list, notify=networksChanged)
    def networks(self) -> list[dict]:
        views = []
        try:
            profiles = self._networks.list_profiles()
        except (SettingsError, ValueError, OSError) as error:
            self.failed.emit(f"读取网络配置失败：{error}")
            return []
        for profile in sorted(profiles, key=lambda p: p.network_profile_id):
            views.append(
                {
                    "network_profile_id": profile.network_profile_id,
                    "name": profile.name,
                    "mode": profile.mode,
                    "http_proxy": profile.http_proxy,
                    "https_proxy": profile.https_proxy,
                    "socks5_proxy": profile.socks5_proxy,
                    "username": profile.username,
                    "credential_set": self._has_credential(profile.credential_ref),
                    "bypass_hosts": sorted(profile.bypass_hosts),
                    "inherit_system": profile.inherit_system,
                    "timeout_seconds": profile.timeout_seconds,
                    "verify_tls": profile.verify_tls,
                    "allow_proxy_failure_direct_fallback": (
                        profile.allow_proxy_failure_direct_fallback
                    ),
                }
            )
        return views

    @Property(list, constant=True)
    def capabilityList(self) -> list[str]:
        return sorted(ALL_CAPABILITIES)

    @Property(list, constant=True)
    def networkModes(self) -> list[str]:
        return sorted(ALL_MODES)

    @Property("QVariantMap", notify=defaultsChanged)
    def bindings(self) -> dict[str, str]:
        try:
            defaults = self._defaults.read()
        except (SettingsError, ValueError, OSError) as error:
            self.failed.emit(f"读取管线默认绑定失败：{error}")
            return {}
        views: dict[str, str] = {}
        for step, binding in sorted(defaults.provider_bindings.items()):
            capability = _STEP_TO_CAPABILITY.get(step, step)
            views[capability] = _binding_profile_id(binding)
        return views

    @Property("QVariantMap", notify=defaultsChanged)
    def settingsSections(self) -> dict[str, dict]:
        try:
            defaults = self._defaults.read()
        except (SettingsError, ValueError, OSError) as error:
            self.failed.emit(f"读取管线设置失败：{error}")
            return {}
        return {k: dict(v) for k, v in defaults.settings.items()}

    @Property(str, notify=defaultsChanged)
    def defaultNetworkProfileId(self) -> str:
        sections = self.settingsSections
        network = sections.get("network")
        if isinstance(network, dict):
            return str(network.get("profile_id", ""))
        return ""

    @Slot()
    def refresh(self) -> None:
        self.profilesChanged.emit()
        self.networksChanged.emit()
        self.defaultsChanged.emit()

    # ------------------------------------------------------------------
    # provider profiles
    # ------------------------------------------------------------------

    @Slot("QVariantMap")
    def saveProviderProfile(self, payload: dict) -> None:
        """Create or update one provider profile (AC-PROVIDER-001).

        ``api_key`` (when non-empty) goes to the credential vault; an
        empty value keeps the stored credential. ``clear_credential``
        removes the stored secret and the reference.
        """
        profile_id = str(payload.get("provider_profile_id", "")).strip()
        if not profile_id:
            self.failed.emit("Provider 配置必须提供 provider_profile_id")
            return
        try:
            capabilities = frozenset(
                str(c) for c in (payload.get("capabilities") or [])
            )
            existing = self._providers.get_profile(profile_id)
            credential_ref = existing.credential_ref if existing else None
            if payload.get("clear_credential"):
                self._delete_credential(credential_ref)
                credential_ref = None
            api_key = str(payload.get("api_key") or "")
            if api_key:
                credential_ref = self._store_credential(
                    "provider", profile_id, api_key
                )
            from ports.providers.profiles import ProviderProfile

            profile = ProviderProfile(
                provider_profile_id=profile_id,
                name=str(payload.get("name", "") or profile_id),
                provider_type=str(payload.get("provider_type", "")).strip(),
                capabilities=capabilities,
                base_url=str(payload.get("base_url", "")).strip(),
                model=str(payload.get("model", "")).strip(),
                credential_ref=credential_ref,
                network_profile_id=(
                    str(payload.get("network_profile_id", "")).strip() or None
                ),
                proxy_policy=str(payload.get("proxy_policy", "inherit")),
                options=tuple(),
                is_enabled=bool(payload.get("is_enabled", True)),
                created_at=existing.created_at if existing else _now(),
                updated_at=_now(),
            )
            if existing is None:
                self._providers.add_profile(profile)
            else:
                self._providers.update_profile(profile)
            self._save_provider_runtime_profile(profile)
        except (SettingsError, ValueError, KeyError, OSError) as error:
            self.failed.emit(f"保存 Provider 配置失败：{error}")
            return
        self.profilesChanged.emit()
        self.saved.emit(f"Provider 配置已保存：{profile_id}")

    @Slot(str)
    def deleteProviderProfile(self, profile_id: str) -> None:
        try:
            existing = self._providers.get_profile(profile_id)
            if existing is None:
                self.failed.emit(f"Provider 配置不存在：{profile_id}")
                return
            self._providers.delete_profile(profile_id)
            self._delete_credential(existing.credential_ref)
            self._delete_provider_runtime_profile(profile_id)
        except (SettingsError, ValueError, OSError) as error:
            self.failed.emit(f"删除 Provider 配置失败：{error}")
            return
        self.profilesChanged.emit()
        self.defaultsChanged.emit()
        self.saved.emit(f"Provider 配置已删除：{profile_id}")

    # ------------------------------------------------------------------
    # network profiles
    # ------------------------------------------------------------------

    @Slot("QVariantMap")
    def saveNetworkProfile(self, payload: dict) -> None:
        """Create or update one network profile via the safety-gated
        service (AC-SEC-004/005, AC-NET-001~003).

        ``proxy_password`` (when non-empty) goes to the credential vault;
        ``confirm_disable_tls`` must be set by QML after the user accepts
        the confirmation dialog, or the service raises and the viewmodel
        emits ``confirmationRequired``.
        """
        profile_id = str(payload.get("network_profile_id", "")).strip()
        if not profile_id:
            self.failed.emit("网络配置必须提供 network_profile_id")
            return
        try:
            from ports.network.profiles import NetworkProfile

            existing = self._networks.get_profile(profile_id)
            credential_ref = existing.credential_ref if existing else None
            if payload.get("clear_credential"):
                self._delete_credential(credential_ref)
                credential_ref = None
            proxy_password = str(payload.get("proxy_password") or "")
            if proxy_password:
                credential_ref = self._store_credential(
                    "proxy", profile_id, proxy_password
                )
            bypass = payload.get("bypass_hosts")
            profile = NetworkProfile(
                network_profile_id=profile_id,
                name=str(payload.get("name", "") or profile_id),
                mode=str(payload.get("mode", "direct")),
                http_proxy=str(payload.get("http_proxy", "")).strip(),
                https_proxy=str(payload.get("https_proxy", "")).strip(),
                socks5_proxy=str(payload.get("socks5_proxy", "")).strip(),
                username=str(payload.get("username", "")).strip(),
                credential_ref=credential_ref,
                bypass_hosts=frozenset(
                    str(h) for h in bypass if str(h).strip()
                )
                if bypass is not None
                else (existing.bypass_hosts if existing else frozenset()),
                inherit_system=bool(payload.get("inherit_system", True)),
                timeout_seconds=float(payload.get("timeout_seconds") or 30.0),
                verify_tls=bool(payload.get("verify_tls", True)),
                allow_proxy_failure_direct_fallback=bool(
                    payload.get("allow_proxy_failure_direct_fallback", False)
                ),
                created_at=existing.created_at if existing else _now(),
                updated_at=_now(),
            )
            confirm = bool(payload.get("confirm_disable_tls", False))
            if existing is None:
                self._networks.create_profile(profile, confirm_disable_tls=confirm)
            else:
                self._networks.update_profile(profile, confirm_disable_tls=confirm)
            self._save_network_runtime_profile(profile)
        except DangerousSettingError as error:
            self.confirmationRequired.emit(f"危险设置需要确认：{error}")
            return
        except (SettingsError, ValueError, KeyError, OSError, TypeError) as error:
            self.failed.emit(f"保存网络配置失败：{error}")
            return
        self.networksChanged.emit()
        self.saved.emit(f"网络配置已保存：{profile_id}")

    @Slot(str)
    def deleteNetworkProfile(self, profile_id: str) -> None:
        try:
            existing = self._networks.get_profile(profile_id)
            if existing is None:
                self.failed.emit(f"网络配置不存在：{profile_id}")
                return
            self._networks.delete_profile(profile_id)
            self._delete_credential(existing.credential_ref)
            self._delete_network_runtime_profile(profile_id)
        except (SettingsError, ValueError, OSError) as error:
            self.failed.emit(f"删除网络配置失败：{error}")
            return
        self.networksChanged.emit()
        self.saved.emit(f"网络配置已删除：{profile_id}")

    # ------------------------------------------------------------------
    # pipeline bindings & settings sections
    # ------------------------------------------------------------------

    @Slot(str, str)
    def saveBinding(self, step_type: str, provider_profile_id: str) -> None:
        """Bind one pipeline capability to a provider profile
        (AC-PROVIDER-002).

        ``step_type`` is the QML-facing capability name; the persisted row
        and the run snapshot reader use the handler step name. The profile
        must already exist — a binding that cannot resolve at assembly is
        rejected here, not discovered at run time.
        """
        step = _CAPABILITY_TO_STEP.get(step_type)
        if step is None:
            self.failed.emit(f"未知的管线能力：{step_type}")
            return
        try:
            if provider_profile_id and self._providers.get_profile(
                provider_profile_id
            ) is None:
                self.failed.emit(
                    f"绑定的 Provider 配置不存在：{provider_profile_id}"
                )
                return
            self._defaults.save_provider_binding(step, provider_profile_id)
        except (SettingsError, BindingValidationError, ValueError, OSError) as error:
            self.failed.emit(f"保存绑定失败：{error}")
            return
        self.defaultsChanged.emit()
        self.saved.emit(f"绑定已保存：{step_type} → {provider_profile_id}")

    @Slot(str)
    def clearBinding(self, step_type: str) -> None:
        step = _CAPABILITY_TO_STEP.get(step_type)
        if step is None:
            self.failed.emit(f"未知的管线能力：{step_type}")
            return
        try:
            self._defaults.clear_provider_binding(step)
        except (SettingsError, BindingValidationError, ValueError, OSError) as error:
            self.failed.emit(f"清除绑定失败：{error}")
            return
        self.defaultsChanged.emit()
        self.saved.emit(f"绑定已清除：{step_type}")

    @Slot(str, str)
    def saveSettingsSectionJson(self, section: str, json_text: str) -> None:
        """Upsert one settings section from a QML-provided JSON object."""
        try:
            values = json.loads(json_text)
        except json.JSONDecodeError as error:
            self.failed.emit(f"设置内容不是有效 JSON：{error}")
            return
        try:
            self._defaults.save_settings_section(section, values)
        except (SettingsError, BindingValidationError, ValueError, TypeError, OSError) as error:
            self.failed.emit(f"保存设置失败：{error}")
            return
        self.defaultsChanged.emit()
        self.saved.emit(f"设置已保存：{section}")

    @Slot(str, str)
    def setDefaultNetworkProfile(self, section: str, profile_id: str) -> None:
        """Convenience wrapper: persist ``network.profile_id`` (D03 §27)."""
        self.saveSettingsSectionJson(
            section, json.dumps({"profile_id": profile_id}, ensure_ascii=False)
        )

    # ------------------------------------------------------------------
    # pipeline settings projection (restart recovery, R3 B-003)
    # ------------------------------------------------------------------

    def _save_provider_runtime_profile(self, profile) -> None:
        """Mirror the provider profile into the pipeline settings shape
        ``build_provider_runtime`` reads at production bootstrap.

        The JSON profile store stays the UI-facing durable source until
        the planned T3.1.1 storage migration; this mirror carries only
        the ``credential_ref``, never a secret value.
        """
        defaults = self._defaults.read()
        providers = self._providers_section(defaults)
        profiles = self._profiles_section(providers)
        profiles[profile.provider_profile_id] = {
            "base_url": profile.base_url,
            "model": profile.model,
            "credential_ref": profile.credential_ref,
            "enabled": profile.is_enabled,
            "options": profile.option_dict(),
            "provider_type": profile.provider_type,
            "network_profile_id": profile.network_profile_id or "",
        }
        providers["profiles"] = profiles
        self._defaults.save_settings_section("providers", providers)

    def _delete_provider_runtime_profile(self, profile_id: str) -> None:
        defaults = self._defaults.read()
        providers = self._providers_section(defaults)
        profiles = self._profiles_section(providers)
        profiles.pop(profile_id, None)
        providers["profiles"] = profiles
        self._defaults.save_settings_section("providers", providers)

    def _save_network_runtime_profile(self, profile) -> None:
        """Mirror the network profile so the runtime transport applies the
        configured proxy/TLS/bypass policy (R3 B-002). As above: the
        ``credential_ref`` rides the mirror; the secret stays in the vault.
        """
        defaults = self._defaults.read()
        providers = self._providers_section(defaults)
        networks = providers.get("networks")
        networks = dict(networks) if isinstance(networks, dict) else {}
        networks[profile.network_profile_id] = {
            "name": profile.name,
            "mode": profile.mode,
            "http_proxy": profile.http_proxy,
            "https_proxy": profile.https_proxy,
            "socks5_proxy": profile.socks5_proxy,
            "username": profile.username,
            "credential_ref": profile.credential_ref,
            "bypass_hosts": sorted(profile.bypass_hosts),
            "inherit_system": profile.inherit_system,
            "timeout_seconds": profile.timeout_seconds,
            "verify_tls": profile.verify_tls,
            "allow_proxy_failure_direct_fallback": (
                profile.allow_proxy_failure_direct_fallback
            ),
        }
        providers["networks"] = networks
        self._defaults.save_settings_section("providers", providers)

    def _delete_network_runtime_profile(self, profile_id: str) -> None:
        defaults = self._defaults.read()
        providers = self._providers_section(defaults)
        networks = providers.get("networks")
        networks = dict(networks) if isinstance(networks, dict) else {}
        networks.pop(profile_id, None)
        providers["networks"] = networks
        self._defaults.save_settings_section("providers", providers)

    @staticmethod
    def _providers_section(defaults) -> dict:
        raw = defaults.settings.get("providers")
        return dict(raw) if isinstance(raw, dict) else {}

    @staticmethod
    def _profiles_section(providers: dict) -> dict:
        raw = providers.get("profiles")
        return dict(raw) if isinstance(raw, dict) else {}

    # ------------------------------------------------------------------
    # credential helpers (vault only; never logs, never repr of a secret)
    # ------------------------------------------------------------------

    def _store_credential(self, kind: str, owner: str, secret_text: str) -> str:
        if self._credentials is None:
            raise SettingsError("凭据库不可用，无法存储密钥")
        from ports.providers.credentials import make_credential_ref

        ref = make_credential_ref(kind, owner)
        secret = SecretValue(secret_text)
        if self._credentials.has_credential(ref):
            self._credentials.update_credential(ref, secret)
        else:
            self._credentials.store_credential(ref, secret)
        return ref

    def _delete_credential(self, ref: str | None) -> None:
        if ref and self._has_credential(ref):
            self._credentials.delete_credential(ref)

    def _has_credential(self, ref: str | None) -> bool:
        if not ref or self._credentials is None:
            return False
        try:
            return bool(self._credentials.has_credential(ref))
        except (KeyError, OSError, RuntimeError):
            return False
