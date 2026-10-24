"""Core handlers for the frozen P15 G21/G24 settings wire."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from datetime import datetime, timezone
import ipaddress
import json
import time
import urllib.request
import uuid
from urllib.parse import urlsplit

from domain.books.entities import ReadingDirection
from ports.network.profiles import (
    MODE_DIRECT,
    MODE_HTTP,
    MODE_HTTPS,
    MODE_SOCKS5,
    MODE_SYSTEM,
    NetworkProfile,
)
from ports.providers.credentials import (
    CREDENTIAL_KIND_PROVIDER,
    CREDENTIAL_KIND_PROXY,
    make_credential_ref,
)
from ports.providers.profiles import ProviderProfile

P15_SNAPSHOT_KEY = "_p15_settings_snapshot"
CAPABILITY_NAMES = ("OCR", "Translation", "Inpaint", "Detection", "Rendering")
CAPABILITY_TO_MODEL = {
    "OCR": "ocr",
    "Translation": "translation",
    "Inpaint": "inpaint",
    "Detection": "detection",
    "Rendering": "rendering",
}
SETTING_KEYS = (
    "reading.direction",
    "sfx.policy",
    "context.strategy",
    "text.style",
    "font.auto_size",
    "translation.parameters",
    "repair.quality",
)
_SAFE_SETTING_KEYS = frozenset({"reading.direction", "sfx.policy"})
_RUN_PROTECTED_STATUSES = frozenset(
    {"pending", "running", "paused", "blocked", "interrupted", "failed", "completed_with_failures"}
)


class SettingsSurfaceError(ValueError):
    """A closed, non-sensitive error projection for P15 settings commands."""

    def __init__(
        self,
        category: str,
        phase: str,
        action: str,
        message_key: str,
    ) -> None:
        self.category = category
        self.phase = phase
        self.action = action
        self.message_key = message_key
        super().__init__(message_key)

    @property
    def details(self) -> dict[str, str]:
        return {
            "phase": self.phase,
            "action": self.action,
            "message_key": self.message_key,
        }


def _fail(
    category: str,
    phase: str,
    action: str,
    message_key: str,
) -> SettingsSurfaceError:
    return SettingsSurfaceError(category, phase, action, message_key)


def _is_ip_literal(host: str | None) -> bool:
    if not host:
        return False
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def _valid_network_stage_reason(stage: str, mode: str, reason: str) -> bool:
    return (
        (stage == "Proxy" and mode == MODE_SYSTEM and reason == "system_route_is_direct")
        or (stage == "ProviderAuth" and reason == "provider_auth_not_required")
    )


class P15SettingsCommands:
    """Validate and execute the Core-owned Provider and override queries."""

    def __init__(self, core) -> None:
        self._core = core

    def handle(self, command: str, payload: dict) -> dict:
        handlers = {
            "settings_provider_profiles_list": self._profiles_list,
            "settings_provider_profiles_create": self._profiles_create,
            "settings_provider_profiles_update": self._profiles_update,
            "settings_provider_profiles_delete": self._profiles_delete,
            "settings_provider_bindings_set": self._bindings_set,
            "settings_provider_bindings_clear": self._bindings_clear,
            "settings_provider_bindings_resolve": self._bindings_resolve,
            "settings_provider_run_snapshot_get": self._run_snapshot_get,
            "settings_resolve_overrides": self._resolve_overrides,
            "settings_network_profiles_list": self._network_profiles_list,
            "settings_network_profiles_create": self._network_profiles_create,
            "settings_network_profiles_update": self._network_profiles_update,
            "settings_network_profiles_delete": self._network_profiles_delete,
            "settings_network_profile_default_set": self._network_profile_default_set,
            "settings_network_profile_default_clear": self._network_profile_default_clear,
            "settings_network_profile_resolve": self._network_profile_resolve,
            "settings_network_profiles_test": self._network_profiles_test,
            "BindProfileCredential": self._bind_profile_credential,
            "ClearProfileCredential": self._clear_profile_credential,
        }
        handler = handlers.get(command)
        if handler is None:
            raise _fail("validation", "settings_resolution", "none", "SETTINGS_INVALID_INPUT")
        return handler(payload)

    def _network_profiles_list(self, payload: dict) -> dict:
        self._fields(payload, set(), phase="profile")
        profiles = sorted(
            self._network_store().list_profiles(),
            key=lambda item: item.network_profile_id,
        )
        return {"profiles": [self._network_profile_to_wire(item) for item in profiles]}

    def _network_profiles_create(self, payload: dict) -> dict:
        self._fields(
            payload,
            {"display_name", "mode", "proxy_endpoint"},
            {"verify_tls", "confirm_disable_tls_verification", "allow_proxy_failure_direct_fallback"},
            phase="profile",
        )
        values = self._network_profile_values(payload, creating=True)
        now = self._now()
        profile = NetworkProfile(
            network_profile_id=uuid.uuid4().hex,
            name=values["display_name"],
            mode=values["mode"],
            http_proxy=values["proxy_endpoint"] if values["mode"] == MODE_HTTP else "",
            https_proxy=values["proxy_endpoint"] if values["mode"] == MODE_HTTPS else "",
            socks5_proxy=values["proxy_endpoint"] if values["mode"] == MODE_SOCKS5 else "",
            verify_tls=values["verify_tls"],
            allow_proxy_failure_direct_fallback=values["allow_proxy_failure_direct_fallback"],
            created_at=now,
            updated_at=now,
        )
        self._network_store().add_profile(profile)
        return {"profile": self._network_profile_to_wire(profile)}

    def _network_profiles_update(self, payload: dict) -> dict:
        self._fields(
            payload,
            {
                "network_profile_id", "display_name", "mode", "proxy_endpoint",
                "verify_tls", "allow_proxy_failure_direct_fallback",
            },
            {"confirm_disable_tls_verification"},
            phase="profile",
        )
        profile_id = self._text(payload, "network_profile_id", "profile")
        store = self._network_store()
        existing = store.get_profile(profile_id)
        if existing is None:
            raise _fail("not_found", "profile", "edit_profile", "SETTINGS_ITEM_NOT_FOUND")
        values = self._network_profile_values(payload, creating=False, existing=existing)
        profile = replace(
            existing,
            name=values["display_name"],
            mode=values["mode"],
            http_proxy=values["proxy_endpoint"] if values["mode"] == MODE_HTTP else "",
            https_proxy=values["proxy_endpoint"] if values["mode"] == MODE_HTTPS else "",
            socks5_proxy=values["proxy_endpoint"] if values["mode"] == MODE_SOCKS5 else "",
            verify_tls=values["verify_tls"],
            allow_proxy_failure_direct_fallback=values["allow_proxy_failure_direct_fallback"],
            updated_at=self._now(),
        )
        store.update_profile(profile)
        return {"profile": self._network_profile_to_wire(profile)}

    def _network_profiles_delete(self, payload: dict) -> dict:
        self._fields(payload, {"network_profile_id"}, phase="profile")
        profile_id = self._text(payload, "network_profile_id", "profile")
        store = self._network_store()
        if store.get_profile(profile_id) is None:
            raise _fail("not_found", "profile", "edit_profile", "SETTINGS_ITEM_NOT_FOUND")
        if (
            self._global_network_profile_id() == profile_id
            or any(item.network_profile_id == profile_id for item in self._profile_store().list_profiles())
            or self._network_profile_used_by_protected_run(profile_id)
        ):
            raise _fail("conflict", "profile", "clear_binding", "SETTINGS_CONFLICT")
        store.delete_profile(profile_id)
        return {"deleted": True}

    def _network_profile_default_set(self, payload: dict) -> dict:
        self._fields(payload, {"network_profile_id"}, phase="profile")
        profile_id = self._text(payload, "network_profile_id", "profile")
        if self._network_store().get_profile(profile_id) is None:
            raise _fail("not_found", "profile", "select_profile", "SETTINGS_ITEM_NOT_FOUND")
        self._network_store().set_global_default_profile_id(profile_id)
        return {"network_profile_id": profile_id}

    def _network_profile_default_clear(self, payload: dict) -> dict:
        self._fields(payload, set(), phase="profile")
        self._network_store().set_global_default_profile_id(None)
        return {"network_profile_id": None}

    def _network_profile_resolve(self, payload: dict) -> dict:
        self._fields(payload, set(), {"provider_profile_id"}, phase="profile")
        provider_id = payload.get("provider_profile_id")
        if "provider_profile_id" in payload:
            provider_id = self._nonempty(provider_id, "profile")
            provider = self._profile_store().get_profile(provider_id)
            if provider is None:
                raise _fail("not_found", "profile", "select_profile", "SETTINGS_ITEM_NOT_FOUND")
            if provider.network_profile_id is not None:
                return self._resolved_network_profile(provider.network_profile_id, "provider")
        default_id = self._global_network_profile_id()
        if default_id is not None:
            return self._resolved_network_profile(default_id, "global")
        try:
            system_proxy = any(
                key != "no" and bool(value)
                for key, value in urllib.request.getproxies().items()
            )
        except Exception as error:
            raise _fail(
                "unavailable", "network_proxy", "contact_support", "SETTINGS_UNAVAILABLE"
            ) from error
        return {
            "network_profile_id": None,
            "mode": "System" if system_proxy else "Direct",
            "source": "system" if system_proxy else "direct",
        }

    def _network_profiles_test(self, payload: dict) -> dict:
        self._fields(
            payload,
            {"network_profile_id", "provider_profile_id"},
            phase="profile",
        )
        network_profile_id = self._nonempty(payload["network_profile_id"], "profile")
        provider_profile_id = self._nonempty(payload["provider_profile_id"], "profile")
        try:
            network = self._network_store().get_profile(network_profile_id)
            provider = self._profile_store().get_profile(provider_profile_id)
        except Exception as error:
            raise _fail(
                "unavailable", "profile", "contact_support", "SETTINGS_UNAVAILABLE"
            ) from error
        if network is None or provider is None:
            raise _fail("validation", "profile", "select_profile", "SETTINGS_INVALID_INPUT")
        endpoint = self._endpoint(provider.base_url, "profile")

        stages = []
        failed_stage = None
        context = {}
        probe = getattr(self._core, "network_profile_test_probe", None)
        for stage in ("Proxy", "DNS", "TCP", "TLS", "HTTP", "ProviderAuth"):
            if failed_stage is not None:
                stages.append({"stage": stage, "status": "not_run", "reason": "upstream_stage_failed"})
                continue

            reason = "direct_mode" if stage == "Proxy" and network.mode == MODE_DIRECT else None
            if stage == "DNS" and _is_ip_literal(urlsplit(endpoint).hostname):
                reason = "provider_endpoint_is_ip_literal"
            if stage == "TLS" and urlsplit(endpoint).scheme.lower() == "http":
                reason = "provider_endpoint_uses_http"
            if reason is not None:
                stages.append({"stage": stage, "status": "not_applicable", "reason": reason})
                continue

            started = time.perf_counter()
            try:
                reason = probe.run(stage, endpoint, provider, network, context)
                if reason is not None:
                    if not _valid_network_stage_reason(stage, network.mode, reason):
                        raise ValueError("invalid network probe outcome")
                    stages.append({"stage": stage, "status": "not_applicable", "reason": reason})
                else:
                    stages.append({
                        "stage": stage,
                        "status": "passed",
                        "duration_ms": max(0, int((time.perf_counter() - started) * 1000)),
                    })
            except Exception:
                failed_stage = stage
                stages.append({
                    "stage": stage,
                    "status": "failed",
                    "failure": {
                        "category": "unavailable",
                        "action": "retry",
                        "message_key": "NETWORK_STAGE_FAILED",
                    },
                    "duration_ms": max(0, int((time.perf_counter() - started) * 1000)),
                })

        return {
            "status": "failed" if failed_stage is not None else "passed",
            "failed_stage": failed_stage,
            "direct_fallback_used": False,
            "stages": stages,
        }

    def _bind_profile_credential(self, payload: dict) -> dict:
        self._fields(payload, {"target", "credential_ref"}, phase="credential_binding")
        store, kind, owner_id, profile = self._credential_target(payload["target"])
        credential_ref = payload["credential_ref"]
        if not self._credential_ref_owned(credential_ref, kind, owner_id):
            raise _fail(
                "validation", "credential_binding", "configure_credential", "SETTINGS_INVALID_INPUT"
            )
        credentials = self._credential_store()
        try:
            if not credentials.has_credential(credential_ref):
                raise _fail(
                    "validation", "credential_binding", "configure_credential", "SETTINGS_INVALID_INPUT"
                )
        except SettingsSurfaceError:
            raise
        except Exception as error:
            raise _fail(
                "unavailable", "credential_store", "configure_credential", "CREDENTIAL_STORE_UNAVAILABLE"
            ) from error
        if profile.credential_ref == credential_ref:
            return {"state": "configured"}
        try:
            store.update_profile(replace(profile, credential_ref=credential_ref, updated_at=self._now()))
        except Exception as error:
            try:
                credentials.delete_credential(credential_ref)
            except Exception:
                pass
            raise _fail(
                "unavailable", "credential_binding", "contact_support", "SETTINGS_UNAVAILABLE"
            ) from error
        return {"state": "configured"}

    def _clear_profile_credential(self, payload: dict) -> dict:
        self._fields(payload, {"target"}, phase="credential_binding")
        store, kind, owner_id, profile = self._credential_target(payload["target"])
        credential_ref = profile.credential_ref
        if credential_ref is None:
            return {"state": "missing"}
        if not self._credential_ref_owned(credential_ref, kind, owner_id):
            raise _fail(
                "unavailable", "credential_binding", "contact_support", "SETTINGS_UNAVAILABLE"
            )
        credentials = self._credential_store()
        try:
            if credentials.has_credential(credential_ref):
                credentials.delete_credential(credential_ref)
        except Exception as error:
            raise _fail(
                "unavailable", "credential_store", "configure_credential", "CREDENTIAL_STORE_UNAVAILABLE"
            ) from error
        try:
            store.update_profile(replace(profile, credential_ref=None, updated_at=self._now()))
        except Exception as error:
            raise _fail(
                "unavailable", "credential_binding", "contact_support", "SETTINGS_UNAVAILABLE"
            ) from error
        return {"state": "missing"}

    def _credential_target(self, target: object):
        if not isinstance(target, dict) or not isinstance(target.get("kind"), str):
            raise _fail("validation", "credential_binding", "configure_credential", "SETTINGS_INVALID_INPUT")
        kind = target["kind"]
        if kind == "provider_api":
            self._fields(target, {"kind", "profile_id"}, phase="credential_binding")
            owner_id = self._nonempty(target["profile_id"], "credential_binding")
            store = self._profile_store()
            profile = store.get_profile(owner_id)
            credential_kind = CREDENTIAL_KIND_PROVIDER
        elif kind == "proxy_auth":
            self._fields(target, {"kind", "network_profile_id"}, phase="credential_binding")
            owner_id = self._nonempty(target["network_profile_id"], "credential_binding")
            store = self._network_store()
            profile = store.get_profile(owner_id)
            credential_kind = CREDENTIAL_KIND_PROXY
        else:
            raise _fail("validation", "credential_binding", "configure_credential", "SETTINGS_INVALID_INPUT")
        if profile is None:
            raise _fail("not_found", "credential_binding", "configure_credential", "SETTINGS_ITEM_NOT_FOUND")
        return store, credential_kind, owner_id, profile

    def _credential_store(self):
        store = getattr(self._core, "credential_store", None)
        if store is None:
            raise _fail(
                "unavailable", "credential_store", "configure_credential", "CREDENTIAL_STORE_UNAVAILABLE"
            )
        return store

    @staticmethod
    def _credential_ref_owned(value: object, kind: str, owner_id: str) -> bool:
        if not isinstance(value, str) or not value or value != value.strip():
            return False
        prefix = make_credential_ref(kind, owner_id)
        if value == prefix:
            return True
        suffix = value[len(prefix) + 1:] if value.startswith(prefix + "/") else ""
        return bool(suffix) and "/" not in suffix and not any(char.isspace() or ord(char) < 32 for char in suffix)

    def _global_network_profile_id(self) -> str | None:
        try:
            return self._network_store().get_global_default_profile_id()
        except Exception as error:
            raise _fail(
                "unavailable", "settings_resolution", "contact_support", "SETTINGS_UNAVAILABLE"
            ) from error

    def _resolved_network_profile(self, profile_id: str, source: str) -> dict:
        profile = self._network_store().get_profile(profile_id)
        if profile is None:
            raise _fail("not_found", "profile", "select_profile", "SETTINGS_ITEM_NOT_FOUND")
        return {
            "network_profile_id": profile.network_profile_id,
            "mode": self._network_mode_to_wire(profile.mode),
            "source": source,
        }

    def _network_profile_values(
        self, payload: dict, *, creating: bool, existing: NetworkProfile | None = None
    ) -> dict:
        self._text(payload, "display_name", "profile")
        mode = payload["mode"]
        mode_map = {"Direct": MODE_DIRECT, "System": MODE_SYSTEM, "HTTP": MODE_HTTP, "HTTPS": MODE_HTTPS, "SOCKS5": MODE_SOCKS5}
        if not isinstance(mode, str) or mode not in mode_map:
            raise _fail("validation", "profile", "edit_profile", "SETTINGS_INVALID_INPUT")
        proxy_endpoint = payload["proxy_endpoint"]
        if mode in {"Direct", "System"}:
            if proxy_endpoint is not None:
                raise _fail("validation", "network_proxy", "edit_profile", "SETTINGS_INVALID_INPUT")
        else:
            scheme = {"HTTP": "http", "HTTPS": "https", "SOCKS5": "socks5"}[mode]
            self._proxy_endpoint(proxy_endpoint, scheme)
        verify_tls = payload.get("verify_tls", True) if creating else payload["verify_tls"]
        allow_fallback = payload.get("allow_proxy_failure_direct_fallback", False) if creating else payload["allow_proxy_failure_direct_fallback"]
        if type(verify_tls) is not bool or type(allow_fallback) is not bool:
            raise _fail("validation", "profile", "edit_profile", "SETTINGS_INVALID_INPUT")
        confirm = payload.get("confirm_disable_tls_verification", False)
        if type(confirm) is not bool:
            raise _fail("validation", "tls", "review_tls_setting", "SETTINGS_INVALID_INPUT")
        if not verify_tls and (creating or (existing is not None and existing.verify_tls)) and confirm is not True:
            raise _fail("validation", "tls", "review_tls_setting", "TLS_CONFIRMATION_REQUIRED")
        return {
            "display_name": payload["display_name"],
            "mode": mode_map[mode],
            "proxy_endpoint": proxy_endpoint,
            "verify_tls": verify_tls,
            "allow_proxy_failure_direct_fallback": allow_fallback,
        }

    @staticmethod
    def _proxy_endpoint(value: object, scheme: str) -> str:
        if not isinstance(value, str) or not value or value != value.strip() or any(char.isspace() or ord(char) < 32 for char in value):
            raise _fail("validation", "network_proxy", "edit_profile", "SETTINGS_INVALID_INPUT")
        try:
            parts = urlsplit(value)
            _ = parts.port
        except ValueError as error:
            raise _fail("validation", "network_proxy", "edit_profile", "SETTINGS_INVALID_INPUT") from error
        if (
            parts.scheme != scheme
            or not parts.hostname
            or parts.username is not None
            or parts.password is not None
            or "?" in value
            or "#" in value
        ):
            raise _fail("validation", "network_proxy", "edit_profile", "SETTINGS_INVALID_INPUT")
        return value

    def _network_profile_to_wire(self, profile: NetworkProfile) -> dict:
        endpoint = {
            MODE_HTTP: profile.http_proxy,
            MODE_HTTPS: profile.https_proxy,
            MODE_SOCKS5: profile.socks5_proxy,
        }.get(profile.mode)
        if endpoint is not None:
            endpoint = self._proxy_endpoint(endpoint, profile.mode)
        return {
            "network_profile_id": profile.network_profile_id,
            "display_name": profile.name,
            "mode": self._network_mode_to_wire(profile.mode),
            "proxy_endpoint": endpoint,
            "verify_tls": profile.verify_tls,
            "tls_verification_state": "enabled" if profile.verify_tls else "disabled_confirmed",
            "allow_proxy_failure_direct_fallback": profile.allow_proxy_failure_direct_fallback,
            "credential_state": "configured" if profile.credential_ref else "missing",
        }

    @staticmethod
    def _network_mode_to_wire(mode: str) -> str:
        return {
            MODE_DIRECT: "Direct",
            MODE_SYSTEM: "System",
            MODE_HTTP: "HTTP",
            MODE_HTTPS: "HTTPS",
            MODE_SOCKS5: "SOCKS5",
        }[mode]

    def _network_profile_used_by_protected_run(self, profile_id: str) -> bool:
        rows = self._core.conn.execute(
            "SELECT status, provider_binding_snapshot_json FROM pipeline_runs"
        ).fetchall()
        for row in rows:
            if row["status"] not in _RUN_PROTECTED_STATUSES:
                continue
            try:
                profiles = json.loads(row["provider_binding_snapshot_json"]).get(P15_SNAPSHOT_KEY, {}).get("provider_profiles", {})
            except (json.JSONDecodeError, AttributeError):
                raise _fail("unavailable", "profile", "contact_support", "SETTINGS_UNAVAILABLE")
            if any(
                item.get("network", {}).get("network_profile_id") == profile_id
                for item in profiles.values()
                if isinstance(item, dict)
            ):
                return True
        return False

    def prepare_run_snapshot(
        self, scope, overrides: Mapping[str, object]
    ) -> dict[str, object]:
        task_profiles = overrides.get("provider_profiles", {})
        if not isinstance(task_profiles, Mapping) or any(
            key not in CAPABILITY_TO_MODEL
            or not isinstance(value, str)
            or not value.strip()
            for key, value in task_profiles.items()
        ):
            raise _fail("validation", "binding", "select_profile", "SETTINGS_INVALID_INPUT")

        book_id, chapter_id = self._scope_context(scope)
        profiles: dict[str, dict] = {}
        for capability in CAPABILITY_NAMES:
            task_profile_id = task_profiles.get(capability)
            if task_profile_id is not None:
                profile = self._require_bound_profile(task_profile_id, capability)
                source = {"kind": "run"}
            else:
                profile_id, source = self._resolve_current_binding(
                    capability, book_id=book_id, chapter_id=chapter_id
                )
                if profile_id is None:
                    continue
                profile = self._require_bound_profile(profile_id, capability)
            profiles[capability] = self._snapshot_profile(profile, source)

        settings, unsupported = self._resolved_settings(
            keys=SETTING_KEYS,
            book_id=book_id,
            chapter_id=chapter_id,
            run_overrides=self._run_settings_overrides(overrides),
        )
        return {
            "provider_profiles": profiles,
            "settings": settings,
            "unsupported_settings": unsupported,
        }

    def _profiles_list(self, payload: dict) -> dict:
        self._fields(payload, set(), phase="profile")
        profiles = sorted(self._profile_store().list_profiles(), key=lambda item: item.provider_profile_id)
        return {"profiles": [self._profile_to_wire(profile) for profile in profiles]}

    def _profiles_create(self, payload: dict) -> dict:
        self._fields(
            payload,
            {"provider_id", "display_name", "capabilities", "endpoint", "model", "network_profile_id", "enabled"},
            phase="profile",
        )
        values = self._profile_values(payload)
        profile_id = uuid.uuid4().hex
        profile = ProviderProfile(
            provider_profile_id=profile_id,
            name=values["display_name"],
            provider_type=values["provider_id"],
            capabilities=frozenset(CAPABILITY_TO_MODEL[item] for item in values["capabilities"]),
            base_url=values["endpoint"],
            model=values["model"],
            network_profile_id=values["network_profile_id"],
            is_enabled=values["enabled"],
            created_at=self._now(),
            updated_at=self._now(),
        )
        self._profile_store().add_profile(profile)
        return {"profile": self._profile_to_wire(profile)}

    def _profiles_update(self, payload: dict) -> dict:
        self._fields(
            payload,
            {"profile_id", "display_name", "capabilities", "endpoint", "model", "network_profile_id", "enabled"},
            phase="profile",
        )
        profile_id = self._text(payload, "profile_id", "profile")
        existing = self._profile_store().get_profile(profile_id)
        if existing is None:
            raise _fail("not_found", "profile", "edit_profile", "SETTINGS_ITEM_NOT_FOUND")
        values = self._profile_values(payload)
        profile = ProviderProfile(
            provider_profile_id=profile_id,
            name=values["display_name"],
            provider_type=existing.provider_type,
            capabilities=frozenset(CAPABILITY_TO_MODEL[item] for item in values["capabilities"]),
            base_url=values["endpoint"],
            model=values["model"],
            credential_ref=existing.credential_ref,
            network_profile_id=values["network_profile_id"],
            proxy_policy=existing.proxy_policy,
            options=existing.options,
            is_enabled=values["enabled"],
            created_at=existing.created_at,
            updated_at=self._now(),
        )
        self._profile_store().update_profile(profile)
        return {"profile": self._profile_to_wire(profile)}

    def _profiles_delete(self, payload: dict) -> dict:
        self._fields(payload, {"profile_id"}, phase="profile")
        profile_id = self._text(payload, "profile_id", "profile")
        store = self._profile_store()
        if store.get_profile(profile_id) is None:
            raise _fail("not_found", "profile", "edit_profile", "SETTINGS_ITEM_NOT_FOUND")
        if any(row["profile_id"] == profile_id for row in self._binding_rows()):
            raise _fail("conflict", "profile", "clear_binding", "SETTINGS_CONFLICT")
        if self._profile_used_by_protected_run(profile_id):
            raise _fail("conflict", "profile", "clear_binding", "SETTINGS_CONFLICT")
        store.delete_profile(profile_id)
        return {"deleted": True}

    def _bindings_set(self, payload: dict) -> dict:
        self._fields(payload, {"scope", "capability", "profile_id"}, phase="binding")
        scope = self._parse_scope(payload["scope"])
        capability = self._capability(payload["capability"])
        profile_id = self._text(payload, "profile_id", "binding")
        self._validate_scope_exists(scope)
        self._require_bound_profile(profile_id, capability)
        rows = self._binding_rows()
        rows = [
            row for row in rows
            if (row["scope"], row["capability"]) != (scope, capability)
        ]
        binding = {"scope": scope, "capability": capability, "profile_id": profile_id}
        rows.append(binding)
        self._binding_store().save_bindings(rows)
        return {"binding": binding}

    def _bindings_clear(self, payload: dict) -> dict:
        self._fields(payload, {"scope", "capability"}, phase="binding")
        scope = self._parse_scope(payload["scope"])
        capability = self._capability(payload["capability"])
        self._validate_scope_exists(scope)
        rows = [
            row for row in self._binding_rows()
            if (row["scope"], row["capability"]) != (scope, capability)
        ]
        self._binding_store().save_bindings(rows)
        return {"cleared": True}

    def _bindings_resolve(self, payload: dict) -> dict:
        self._fields(payload, {"capability"}, {"book_id", "chapter_id", "run_id"}, phase="binding")
        capability = self._capability(payload["capability"])
        run_id = payload.get("run_id")
        if run_id is not None:
            if "book_id" in payload or "chapter_id" in payload:
                raise _fail("validation", "binding", "none", "SETTINGS_INVALID_INPUT")
            run = self._run(run_id, phase="binding")
            snapshot = run.provider_binding_snapshot.get(P15_SNAPSHOT_KEY, {})
            entry = snapshot.get("provider_profiles", {}).get(capability)
            if entry is None:
                return {"profile_id": None, "source": None}
            source = dict(entry["source"])
            if source.get("kind") == "run":
                source["run_id"] = run_id
            return {"profile_id": entry["profile_id"], "source": source}
        book_id, chapter_id = self._validated_context(
            payload.get("book_id"), payload.get("chapter_id")
        )
        profile_id, source = self._resolve_current_binding(
            capability, book_id=book_id, chapter_id=chapter_id
        )
        if profile_id is not None:
            self._require_bound_profile(profile_id, capability)
        return {"profile_id": profile_id, "source": source}

    def _run_snapshot_get(self, payload: dict) -> dict:
        self._fields(payload, {"run_id"}, phase="binding")
        run_id = self._text(payload, "run_id", "binding")
        run = self._run(run_id, phase="binding")
        snapshot = run.provider_binding_snapshot.get(P15_SNAPSHOT_KEY, {})
        entries = snapshot.get("provider_profiles", {})
        bindings = []
        for capability in CAPABILITY_NAMES:
            entry = entries.get(capability)
            if entry is None:
                continue
            bindings.append(self._snapshot_to_wire(capability, entry, run_id))
        return {"run_id": run_id, "frozen": True, "bindings": bindings}

    def _resolve_overrides(self, payload: dict) -> dict:
        self._fields(payload, {"keys"}, {"book_id", "chapter_id", "run_id"}, phase="settings_resolution")
        keys = payload["keys"]
        if not isinstance(keys, list) or any(not isinstance(key, str) or key not in SETTING_KEYS for key in keys):
            raise _fail("validation", "settings_resolution", "none", "SETTINGS_INVALID_INPUT")
        run_id = payload.get("run_id")
        if run_id is not None:
            run_id = self._text(payload, "run_id", "settings_resolution")
            run = self._run(run_id, phase="settings_resolution")
            if "book_id" in payload or "chapter_id" in payload:
                requested_book, requested_chapter = self._validated_context(
                    payload.get("book_id"), payload.get("chapter_id")
                )
                run_book, run_chapter = self._scope_context(run.scope)
                if (
                    (requested_book is not None and requested_book != run_book)
                    or (requested_chapter is not None and requested_chapter != run_chapter)
                ):
                    raise _fail("conflict", "settings_resolution", "none", "SETTINGS_CONFLICT")
            snapshot = run.provider_binding_snapshot.get(P15_SNAPSHOT_KEY)
            if snapshot is None:
                snapshot = self._legacy_run_settings_snapshot(run)
            unsupported = set(snapshot.get("unsupported_settings", []))
            if any(key in unsupported for key in keys):
                raise _fail("unavailable", "settings_resolution", "none", "SETTINGS_UNAVAILABLE")
            stored_settings = snapshot.get("settings", {})
            if not isinstance(stored_settings, Mapping):
                raise _fail("unavailable", "settings_resolution", "contact_support", "SETTINGS_UNAVAILABLE")
            frozen = {}
            for key, item in stored_settings.items():
                if (
                    key not in SETTING_KEYS
                    or not isinstance(item, Mapping)
                    or item.get("key") != key
                ):
                    raise _fail("unavailable", "settings_resolution", "contact_support", "SETTINGS_UNAVAILABLE")
                frozen[key] = item
            values = [
                self._setting_to_wire(frozen[key], run_id)
                if key in frozen else self._empty_setting(key)
                for key in keys
            ]
            return {"values": values}
        book_id, chapter_id = self._validated_context(
            payload.get("book_id"), payload.get("chapter_id")
        )
        resolved, unsupported = self._resolved_settings(
            keys=keys,
            book_id=book_id,
            chapter_id=chapter_id,
            run_overrides={},
        )
        if unsupported:
            raise _fail("unavailable", "settings_resolution", "none", "SETTINGS_UNAVAILABLE")
        return {"values": [resolved.get(key, self._empty_setting(key)) for key in keys]}

    def _legacy_run_settings_snapshot(self, run) -> dict:
        # Older runs have no provenance metadata. Their persisted settings
        # are immutable, so a typed value can still be projected from them.
        resolved, unsupported = self._resolved_settings(
            keys=SETTING_KEYS,
            book_id=None,
            chapter_id=None,
            run_overrides=run.settings_snapshot,
            include_defaults=False,
        )
        return {"settings": resolved, "unsupported_settings": unsupported}

    def _resolved_settings(
        self,
        *,
        keys,
        book_id: str | None,
        chapter_id: str | None,
        run_overrides: Mapping[str, object],
        include_defaults: bool = True,
    ) -> tuple[dict[str, dict], list[str]]:
        global_settings = self._core.pipeline_defaults.read().settings
        if not isinstance(global_settings, Mapping):
            raise _fail("unavailable", "settings_resolution", "none", "SETTINGS_UNAVAILABLE")
        book, chapter = self._entities(book_id, chapter_id)
        resolved: dict[str, dict] = {}
        unsupported: list[str] = []
        for key in keys:
            candidates: list[tuple[object, str, str | None, bool]] = []
            has_global, global_value = self._setting_value(global_settings, key)
            if has_global:
                candidates.append((global_value, "global", None, False))
            elif key == "sfx.policy" and include_defaults:
                candidates.append(("skip", "global", None, True))
            if key == "reading.direction" and book is not None:
                candidates.append((book.default_reading_direction.value, "book", book.book_id, False))
            if key == "reading.direction" and chapter is not None:
                candidates.append((chapter.reading_direction.value, "chapter", chapter.chapter_id, False))
            has_run, run_value = self._setting_value(run_overrides, key)
            if has_run:
                candidates.append((run_value, "run", None, False))
            if candidates:
                value, source, source_id, is_default = candidates[-1]
                if key not in _SAFE_SETTING_KEYS:
                    unsupported.append(key)
                    continue
                winner = self._safe_setting(
                    key, value, source, source_id=source_id, is_default=is_default
                )
                if source == "run":
                    winner["_run_source"] = True
                resolved[key] = winner
        return resolved, list(dict.fromkeys(unsupported))

    @staticmethod
    def _safe_setting(
        key: str,
        value: object,
        source: str,
        *,
        source_id: str | None = None,
        is_default: bool = False,
    ) -> dict:
        if key == "reading.direction":
            valid = {item.value for item in ReadingDirection}
        else:
            valid = {"skip", "translate", "manual"}
        if not isinstance(value, str) or value not in valid:
            raise _fail("unavailable", "settings_resolution", "none", "SETTINGS_UNAVAILABLE")
        result = {
            "key": key,
            "value": value,
            "source": source,
            "is_default": is_default,
        }
        if source_id is not None:
            result["source_id"] = source_id
        return result

    @staticmethod
    def _setting_to_wire(item: dict, run_id: str) -> dict:
        result = {
            "key": item["key"],
            "value": item["value"],
            "source": item["source"],
            "is_default": item["is_default"],
        }
        if item.get("source_id") is not None:
            result["source_id"] = item["source_id"]
        elif item.get("_run_source"):
            result["source_id"] = run_id
        return result

    @staticmethod
    def _empty_setting(key: str) -> dict:
        return {"key": key, "value": None, "source": None, "is_default": False}

    def _run(self, run_id: object, *, phase: str):
        if not isinstance(run_id, str) or not run_id.strip():
            raise _fail("validation", phase, "none", "SETTINGS_INVALID_INPUT")
        try:
            return self._core.pipeline.get_run_snapshot(run_id)
        except Exception as error:
            if getattr(error, "code", None) == "TARGET_NOT_FOUND":
                raise _fail("not_found", phase, "none", "SETTINGS_ITEM_NOT_FOUND") from error
            raise

    def _profile_store(self):
        store = getattr(self._core, "provider_profile_store", None)
        if store is None:
            raise _fail("unavailable", "profile", "contact_support", "SETTINGS_UNAVAILABLE")
        return store

    def _network_store(self):
        store = getattr(self._core, "network_profile_store", None)
        if store is None:
            raise _fail("unavailable", "profile", "contact_support", "SETTINGS_UNAVAILABLE")
        return store

    def _binding_store(self):
        store = getattr(self._core, "provider_binding_store", None)
        if store is None:
            raise _fail("unavailable", "binding", "contact_support", "SETTINGS_UNAVAILABLE")
        return store

    def _profile_values(self, payload: dict) -> dict:
        if "provider_id" in payload:
            self._text(payload, "provider_id", "profile")
        for field in ("display_name", "model"):
            self._text(payload, field, "profile")
        capabilities = payload["capabilities"]
        if (
            not isinstance(capabilities, list)
            or not capabilities
            or any(not isinstance(item, str) or item not in CAPABILITY_TO_MODEL for item in capabilities)
            or len(set(capabilities)) != len(capabilities)
        ):
            raise _fail("validation", "profile", "edit_profile", "SETTINGS_INVALID_INPUT")
        endpoint = self._endpoint(payload["endpoint"], "profile")
        network_profile_id = payload["network_profile_id"]
        if network_profile_id is not None:
            self._nonempty(network_profile_id, "profile")
            if self._network_store().get_profile(network_profile_id) is None:
                raise _fail("not_found", "profile", "edit_profile", "SETTINGS_ITEM_NOT_FOUND")
        if type(payload["enabled"]) is not bool:
            raise _fail("validation", "profile", "edit_profile", "SETTINGS_INVALID_INPUT")
        return {
            "provider_id": payload.get("provider_id", ""),
            "display_name": payload.get("display_name", ""),
            "capabilities": capabilities,
            "endpoint": endpoint,
            "model": payload.get("model", ""),
            "network_profile_id": network_profile_id,
            "enabled": payload["enabled"],
        }

    def _profile_to_wire(self, profile: ProviderProfile) -> dict:
        endpoint = self._endpoint(profile.base_url, "profile")
        capabilities = [
            capability
            for capability in CAPABILITY_NAMES
            if CAPABILITY_TO_MODEL[capability] in profile.capabilities
        ]
        return {
            "profile_id": profile.provider_profile_id,
            "provider_id": profile.provider_type,
            "display_name": profile.name,
            "capabilities": capabilities,
            "endpoint": endpoint,
            "model": profile.model,
            "network_profile_id": profile.network_profile_id,
            "enabled": profile.is_enabled,
            "credential_state": "configured" if profile.credential_ref else "missing",
        }

    def _snapshot_profile(self, profile: ProviderProfile, source: dict) -> dict:
        network = self._network_snapshot(profile.network_profile_id)
        return {
            "profile_id": profile.provider_profile_id,
            "provider_id": profile.provider_type,
            "display_name": profile.name,
            "endpoint": self._endpoint(profile.base_url, "profile"),
            "model": profile.model,
            "provider_credential_state_at_snapshot": "configured" if profile.credential_ref else "missing",
            "credential_ref": profile.credential_ref,
            "network": network,
            "source": dict(source),
        }

    def _network_snapshot(self, network_profile_id: str | None) -> dict:
        if network_profile_id is None:
            return {
                "network_profile_id": None,
                "mode": "Direct",
                "proxy_endpoint": None,
                "verify_tls": True,
                "tls_verification_state": "enabled",
                "allow_proxy_failure_direct_fallback": False,
                "credential_state_at_snapshot": "missing",
                "credential_ref": None,
            }
        profile = self._network_store().get_profile(network_profile_id)
        if profile is None:
            raise _fail("not_found", "profile", "edit_profile", "SETTINGS_ITEM_NOT_FOUND")
        endpoint = None
        if profile.mode not in {MODE_DIRECT, MODE_SYSTEM}:
            if profile.mode == "http":
                endpoint = profile.http_proxy or profile.https_proxy or None
            elif profile.mode == "https":
                endpoint = profile.https_proxy or profile.http_proxy or None
            else:
                endpoint = profile.socks5_proxy or None
            if endpoint is not None:
                endpoint = self._endpoint(endpoint, "profile", schemes={"http", "https", "socks5"})
        mode = {
            "direct": "Direct",
            "system": "System",
            "http": "HTTP",
            "https": "HTTPS",
            "socks5": "SOCKS5",
        }[profile.mode]
        return {
            "network_profile_id": profile.network_profile_id,
            "mode": mode,
            "proxy_endpoint": endpoint,
            "verify_tls": profile.verify_tls,
            "tls_verification_state": "enabled" if profile.verify_tls else "disabled_confirmed",
            "allow_proxy_failure_direct_fallback": profile.allow_proxy_failure_direct_fallback,
            "credential_state_at_snapshot": "configured" if profile.credential_ref else "missing",
            "credential_ref": profile.credential_ref,
        }

    def _snapshot_to_wire(self, capability: str, entry: dict, run_id: str) -> dict:
        source = dict(entry["source"])
        if source.get("kind") == "run":
            source["run_id"] = run_id
        network = entry["network"]
        return {
            "capability": capability,
            "profile_id": entry["profile_id"],
            "provider_id": entry["provider_id"],
            "display_name": entry["display_name"],
            "endpoint": entry["endpoint"],
            "model": entry["model"],
            "provider_credential_state_at_snapshot": entry["provider_credential_state_at_snapshot"],
            "network": {
                key: value
                for key, value in network.items()
                if key != "credential_ref"
            },
            "source": source,
        }

    def _require_bound_profile(self, profile_id: str, capability: str) -> ProviderProfile:
        profile = self._profile_store().get_profile(profile_id)
        if profile is None:
            raise _fail("not_found", "binding", "select_profile", "SETTINGS_ITEM_NOT_FOUND")
        if not profile.is_enabled or CAPABILITY_TO_MODEL[capability] not in profile.capabilities:
            raise _fail("conflict", "binding", "select_profile", "SETTINGS_CONFLICT")
        self._endpoint(profile.base_url, "profile")
        if profile.network_profile_id is not None:
            self._network_snapshot(profile.network_profile_id)
        return profile

    def _resolve_current_binding(
        self, capability: str, *, book_id: str | None, chapter_id: str | None
    ) -> tuple[str | None, dict | None]:
        rows = self._binding_rows()
        wanted = []
        if chapter_id is not None:
            wanted.append({"kind": "chapter", "chapter_id": chapter_id})
        if book_id is not None:
            wanted.append({"kind": "book", "book_id": book_id})
        wanted.append({"kind": "global"})
        for scope in wanted:
            matches = [row for row in rows if row["scope"] == scope and row["capability"] == capability]
            if not matches:
                continue
            row = matches[0]
            return row["profile_id"], dict(scope)
        return None, None

    def _binding_rows(self) -> list[dict]:
        rows = self._binding_store().list_bindings()
        if not isinstance(rows, list):
            raise _fail("unavailable", "binding", "contact_support", "SETTINGS_UNAVAILABLE")
        normalized = []
        seen = set()
        for row in rows:
            if not isinstance(row, dict) or set(row) != {"scope", "capability", "profile_id"}:
                raise _fail("unavailable", "binding", "contact_support", "SETTINGS_UNAVAILABLE")
            scope = self._parse_scope(row["scope"], stored=True)
            capability = row["capability"]
            profile_id = row["profile_id"]
            if capability not in CAPABILITY_TO_MODEL or not isinstance(profile_id, str) or not profile_id:
                raise _fail("unavailable", "binding", "contact_support", "SETTINGS_UNAVAILABLE")
            key = (json.dumps(scope, sort_keys=True), capability)
            if key in seen:
                raise _fail("unavailable", "binding", "contact_support", "SETTINGS_UNAVAILABLE")
            seen.add(key)
            normalized.append({"scope": scope, "capability": capability, "profile_id": profile_id})
        return normalized

    def _parse_scope(self, value: object, *, stored: bool = False) -> dict:
        if not isinstance(value, dict) or not isinstance(value.get("kind"), str):
            raise _fail("unavailable" if stored else "validation", "binding", "none", "SETTINGS_INVALID_INPUT" if not stored else "SETTINGS_UNAVAILABLE")
        kind = value["kind"]
        if kind == "global" and set(value) == {"kind"}:
            return {"kind": "global"}
        field = {"book": "book_id", "chapter": "chapter_id"}.get(kind)
        if field and set(value) == {"kind", field} and isinstance(value.get(field), str) and value[field].strip():
            return {"kind": kind, field: value[field]}
        raise _fail("unavailable" if stored else "validation", "binding", "none", "SETTINGS_INVALID_INPUT" if not stored else "SETTINGS_UNAVAILABLE")

    def _validate_scope_exists(self, scope: dict) -> None:
        kind = scope["kind"]
        if kind == "book":
            self._validated_context(scope["book_id"], None)
        elif kind == "chapter":
            self._validated_context(None, scope["chapter_id"])

    def _validated_context(
        self, book_id: object, chapter_id: object
    ) -> tuple[str | None, str | None]:
        if book_id is not None and (not isinstance(book_id, str) or not book_id.strip()):
            raise _fail("validation", "binding", "none", "SETTINGS_INVALID_INPUT")
        if chapter_id is not None and (not isinstance(chapter_id, str) or not chapter_id.strip()):
            raise _fail("validation", "binding", "none", "SETTINGS_INVALID_INPUT")
        book, chapter = self._entities(book_id, chapter_id)
        if chapter is not None:
            if book is not None and book.book_id != chapter.book_id:
                raise _fail("conflict", "binding", "none", "SETTINGS_CONFLICT")
            book_id = chapter.book_id
        return book_id, chapter_id

    def _entities(self, book_id: str | None, chapter_id: str | None):
        book = None
        chapter = None
        if book_id is not None:
            book = self._core.repository.get_book(book_id)
            if book is None or book.deleted:
                raise _fail("not_found", "binding", "none", "SETTINGS_ITEM_NOT_FOUND")
        if chapter_id is not None:
            chapter = self._core.repository.get_chapter(chapter_id)
            if chapter is None or chapter.deleted:
                raise _fail("not_found", "binding", "none", "SETTINGS_ITEM_NOT_FOUND")
            if book is not None and chapter.book_id != book.book_id:
                raise _fail("conflict", "binding", "none", "SETTINGS_CONFLICT")
            if book is None:
                book = self._core.repository.get_book(chapter.book_id)
                if book is None or book.deleted:
                    raise _fail("not_found", "binding", "none", "SETTINGS_ITEM_NOT_FOUND")
        return book, chapter

    def _scope_context(self, scope) -> tuple[str | None, str | None]:
        book_id = scope.book_id
        chapter_id = scope.chapter_id
        if book_id is not None or chapter_id is not None:
            return self._validated_context(book_id, chapter_id)
        selected_ids = list(scope.selected_ids)
        if scope.scope_type.value == "region" and selected_ids:
            marks = ",".join("?" for _ in selected_ids)
            rows = self._core.conn.execute(
                f"SELECT page_id FROM regions WHERE region_id IN ({marks}) AND deleted_at IS NULL",
                tuple(selected_ids),
            ).fetchall()
            selected_ids = [row["page_id"] for row in rows]
        elif scope.scope_type.value not in {"page", "page_selection"}:
            return None, None
        if not selected_ids:
            return None, None
        marks = ",".join("?" for _ in selected_ids)
        rows = self._core.conn.execute(
            "SELECT DISTINCT c.chapter_id, c.book_id FROM pages p "
            "JOIN chapters c ON c.chapter_id=p.chapter_id "
            f"WHERE p.page_id IN ({marks}) AND p.deleted_at IS NULL AND c.deleted_at IS NULL",
            tuple(selected_ids),
        ).fetchall()
        chapters = {row["chapter_id"] for row in rows}
        books = {row["book_id"] for row in rows}
        if len(chapters) == 1:
            return self._validated_context(next(iter(books)), next(iter(chapters)))
        if len(books) == 1:
            return self._validated_context(next(iter(books)), None)
        return None, None

    def _profile_used_by_protected_run(self, profile_id: str) -> bool:
        rows = self._core.conn.execute(
            "SELECT status, provider_binding_snapshot_json FROM pipeline_runs"
        ).fetchall()
        for row in rows:
            if row["status"] not in _RUN_PROTECTED_STATUSES:
                continue
            try:
                bindings = json.loads(row["provider_binding_snapshot_json"])
                entries = bindings.get(P15_SNAPSHOT_KEY, {}).get("provider_profiles", {})
            except (json.JSONDecodeError, AttributeError):
                raise _fail("unavailable", "profile", "contact_support", "SETTINGS_UNAVAILABLE")
            if any(item.get("profile_id") == profile_id for item in entries.values() if isinstance(item, dict)):
                return True
        return False

    def _setting_value(self, values: Mapping[str, object], key: str) -> tuple[bool, object]:
        section_name, field_name = key.split(".", 1)
        section = values.get(section_name)
        if section is not None:
            if not isinstance(section, Mapping):
                if key in _SAFE_SETTING_KEYS:
                    raise _fail("unavailable", "settings_resolution", "none", "SETTINGS_UNAVAILABLE")
                return True, section
            if field_name in section:
                return True, section[field_name]
        if key in values:
            return True, values[key]
        return False, None

    @staticmethod
    def _run_settings_overrides(overrides: Mapping[str, object]) -> Mapping[str, object]:
        values = overrides.get("settings")
        if values is not None:
            if not isinstance(values, Mapping):
                return {"settings": values}
            return values
        return {
            key: value
            for key, value in overrides.items()
            if key not in {"provider_bindings", "context_policy", "provider_profiles"}
        }

    @staticmethod
    def _capability(value: object) -> str:
        if not isinstance(value, str) or value not in CAPABILITY_TO_MODEL:
            raise _fail("validation", "binding", "none", "SETTINGS_INVALID_INPUT")
        return value

    @staticmethod
    def _fields(
        payload: object,
        required: set[str],
        optional: set[str] = frozenset(),
        *,
        phase: str,
    ) -> None:
        if not isinstance(payload, dict) or not required <= set(payload) or set(payload) - required - optional:
            raise _fail("validation", phase, "none", "SETTINGS_INVALID_INPUT")

    @staticmethod
    def _text(payload: dict, field: str, phase: str) -> str:
        return P15SettingsCommands._nonempty(payload.get(field), phase)

    @staticmethod
    def _nonempty(value: object, phase: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise _fail("validation", phase, "edit_profile" if phase == "profile" else "none", "SETTINGS_INVALID_INPUT")
        return value

    @staticmethod
    def _endpoint(value: object, phase: str, schemes: set[str] | None = None) -> str:
        if not isinstance(value, str) or not value.strip() or value != value.strip():
            raise _fail("validation", phase, "edit_profile", "SETTINGS_INVALID_INPUT")
        try:
            parts = urlsplit(value)
            _ = parts.port
        except ValueError as error:
            raise _fail("validation", phase, "edit_profile", "SETTINGS_INVALID_INPUT") from error
        allowed = schemes or {"http", "https"}
        if (
            parts.scheme.lower() not in allowed
            or not parts.hostname
            or parts.username is not None
            or parts.password is not None
            or parts.query
            or parts.fragment
        ):
            raise _fail("validation", phase, "edit_profile", "SETTINGS_INVALID_INPUT")
        return value

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="milliseconds")
