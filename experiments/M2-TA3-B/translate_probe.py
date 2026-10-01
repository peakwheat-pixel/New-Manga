"""M2-TA3-B2 step-0 translation probe (AC6 / DSH r2 closure item 7).

Runs the REAL production endpoint sequence on ONE assembled core, exactly as
corrected in phase2-plan §3(a) (r2 N4 wording, landed by commit b7806dac):

  1. profile write    - ``PipelineDefaultsService.save_settings_section``
                        (upsert+commit; whole-section semantics), profile
                        ``credential_ref`` built by ``make_credential_ref``
                        (frozen ``NewManga/provider/<name>`` convention);
  2. binding          - ``save_provider_binding("translate", PROVIDER_ID)``;
  3. re-assemble      - second ``assemble_core_services`` over the SAME db
                        (settings are consumed by ``build_provider_runtime``
                        at assemble time only, core_assembly.py:781-786);
                        the re-assembled slot is expected NOT_CONFIGURED
                        because the vault-style KIND_CREDENTIAL requirement
                        cannot resolve from settings — recorded honestly,
                        this is the reason step 4 exists;
  4. re-register      - registry re-register of the same provider id with a
                        custom ``credential_resolver`` reading the env var
                        (phase2-plan §3(a)(ii)), endpoint-only descriptor
                        (this path does not use the vault; a missing env
                        key still fails closed as ``MissingCredential`` at
                        request time) + ``registry.invalidate``;
  5. readiness READY  - asserted, not assumed;
  6. one REAL region  - the text is a real line the PaddleOCR smoke read
                        off the K11 page (ocr-smoke-results.md §3), speech
                        type, target language zh (quality-thresholds §0
                        default, ruling point T-3).

Credential discipline: the API key enters this process ONLY through the
environment variable ``TA3B_TRANSLATE_API_KEY`` (injected by the caller);
it is never printed, never written to the record, never logged.  The
record keeps provider_id + base_url HOST + model + latency + translation.

Exit codes: 0 = probe OK; 2 = configuration/precondition failure;
3 = probe failed (any step).

Run (fused single venv, after phase2-plan §2.4 venv fusion):
  export TA3B_TRANSLATE_API_KEY=$(cat "G:/CODEX/New Manga.task-envs/M2-TA3-B/deepseek.key")
  PYTHONPATH=src "G:/CODEX/New Manga.task-envs/M2-TA3-B-ocr/Scripts/python.exe" \
    experiments/M2-TA3-B/translate_probe.py \
    --out verification/M2-TA3-B/phase2/translate-probe.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

ENV_KEY_NAME = "TA3B_TRANSLATE_API_KEY"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"
PROVIDER_ID = "openai-compatible-translation"
CRED_REF_NAME = "ta3b-translate-key"
TARGET_LANGUAGE = "zh"  # quality-thresholds §0 default (user ruling point T-3)
#: real page text, first lines of the PaddleOCR smoke output on K11
REAL_REGION_TEXT = "당근아? 이렇게까지는 할 필요없을줄"

DETECTOR_WEIGHTS_DEFAULT = (
    r"G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL/weights/fast_base-688a8b34.pt"
)


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_translation_profile(core, *, base_url: str, model: str) -> str:
    """Steps 1-2 of the AC6 sequence (phase2-plan §3(a) r2-N4 form).

    Returns the ``credential_ref`` written into the profile (a
    ``make_credential_ref`` product, never the secret itself).
    """
    from ports.providers.credentials import make_credential_ref

    credential_ref = make_credential_ref("provider", CRED_REF_NAME)
    defaults = core.pipeline_defaults.read()
    providers_section = dict(defaults.settings.get("providers", {}))
    profiles = dict(providers_section.get("profiles", {}))
    profiles[PROVIDER_ID] = {
        "base_url": base_url,
        "model": model,
        "credential_ref": credential_ref,
        "enabled": True,
    }
    providers_section["profiles"] = profiles
    # save_settings_section upserts + commits the whole section in one call
    # (pipeline_defaults.py:105); nested keys need read-modify-whole-section
    core.pipeline_defaults.save_settings_section("providers", providers_section)
    core.pipeline_defaults.save_provider_binding("translate", PROVIDER_ID)
    return credential_ref


def translation_readiness(core) -> dict:
    """Readiness of the translation slot from the live registry report."""
    for entry in core.providers.readiness_report():
        if entry.get("provider_id") == PROVIDER_ID:
            return entry
    return {"provider_id": PROVIDER_ID, "state": "ABSENT"}


def reregister_env_resolver(core, *, base_url: str, model: str) -> None:
    """Step 4 (phase2-plan §3(a)(ii)): env-resolver re-register + invalidate.

    The descriptor carries the endpoint requirement only: this credential
    path is the environment variable, not the vault — a missing env key
    still fails closed as ``MissingCredential`` when the request is built.
    The gate mirrors the production network gate (proxy semantics only,
    imported from the runtime module like the assembly itself does).
    """
    from infrastructure.providers.dependencies import KIND_ENDPOINT, Requirement
    from infrastructure.providers.openai_client import (
        OpenAiCompatibleClient,
        OpenAiCompatibleConfig,
    )
    from infrastructure.providers.registry import ProviderDescriptor
    from infrastructure.providers.runtime import _network_gate
    from infrastructure.providers.translation_openai import (
        PROVIDER_OPENAI_TRANSLATION as _pid_check,
    )
    from infrastructure.providers.translation_openai import OpenAiTranslationProvider
    from ports.providers.profiles import CAPABILITY_TRANSLATION

    if _pid_check != PROVIDER_ID:  # pragma: no cover - pin the production id
        raise RuntimeError(f"provider id drifted: {_pid_check!r}")

    settings = core.pipeline_defaults.read().settings
    config = OpenAiCompatibleConfig(
        provider_id=PROVIDER_ID,
        provider_type="openai-compatible",
        base_url=base_url,
        model=model,
        credential_ref=ENV_KEY_NAME,  # env var NAME used as the resolver ref
    )
    descriptor = ProviderDescriptor(
        provider_id=PROVIDER_ID,
        provider_type="openai-compatible",
        capabilities=frozenset({CAPABILITY_TRANSLATION}),
        requirements=(
            Requirement(KIND_ENDPOINT, f"{base_url}|{model}", detail="remote endpoint"),
        ),
        note="M2-TA3-B2 phase-2 re-register: credential via env resolver",
    )

    def factory():
        return OpenAiTranslationProvider(
            config=config,
            client=OpenAiCompatibleClient(
                config,
                core.transport,
                credential_resolver=lambda ref: os.environ.get(ref),
            ),
            provider_id=PROVIDER_ID,
            provider_type="openai-compatible",
            target_language=TARGET_LANGUAGE,
        )

    registry = core.providers.registry
    registry.register(
        descriptor,
        factory,
        gate=_network_gate(PROVIDER_ID, settings),
        enabled=True,
    )
    registry.invalidate(PROVIDER_ID)  # registry.py:302 — drop stale instances


def assemble(db_path: Path, managed_root: Path):
    """Production assembly (Qt offscreen), the run_smoke.py verified form."""
    from PySide6.QtGui import QGuiApplication

    if QGuiApplication.instance() is None:
        QGuiApplication(["m2-ta3b2-probe"])
    from application.translation.color.service import SourceStyleService
    from bootstrap.core_assembly import assemble_core_services
    from infrastructure.importing import QtImageDecoder
    from infrastructure.rendering.font_catalog import QtFontCatalog
    from infrastructure.rendering.pixel_source_style import PixelSourceStyleAnalyzer
    from infrastructure.rendering.qt_compositor import QtImageCompositor
    from infrastructure.rendering.qt_layout import QtTextLayoutEngine

    os.environ.setdefault("NEWMANGA_DETECTOR_WEIGHTS", DETECTOR_WEIGHTS_DEFAULT)
    os.environ.setdefault("NEWMANGA_DETECTOR_DEVICE", "cpu")
    return assemble_core_services(
        db_path,
        managed_root,
        image_decoder=QtImageDecoder(),
        font_catalog=(font_catalog := QtFontCatalog()),
        layout_engine=QtTextLayoutEngine(font_catalog),
        compositor=QtImageCompositor(),
        source_styles=SourceStyleService(PixelSourceStyleAnalyzer()),
        mock_local_providers=False,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(REPO_ROOT / "verification/M2-TA3-B/phase2/translate-probe.json"))
    parser.add_argument("--base-url", default=DEEPSEEK_BASE_URL)
    parser.add_argument("--model", default=DEEPSEEK_MODEL)
    args = parser.parse_args()

    record: dict = {
        "probe": "translate-step0-ac6",
        "started_at_utc": _now_utc(),
        "base_url_host": urlsplit(args.base_url).netloc,
        "model": args.model,
        "provider_id": PROVIDER_ID,
        "target_language": TARGET_LANGUAGE,
        "sequence": {},
    }

    if not os.environ.get(ENV_KEY_NAME):
        print(f"FAIL: environment variable {ENV_KEY_NAME} is not set", file=sys.stderr)
        return 2

    status = 3
    try:
        case_root = Path(tempfile.mkdtemp(prefix="m2-ta3b2-probe-"))
        db_path = case_root / "library.sqlite"
        core = assemble(db_path, case_root / "managed")
        record["sequence"]["assemble"] = "OK"

        credential_ref = write_translation_profile(
            core, base_url=args.base_url, model=args.model
        )
        record["sequence"]["profile_write"] = "OK (save_settings_section + binding)"
        record["credential_ref"] = credential_ref  # convention string, not the secret

        # step 3: same-db re-assemble (settings consumed at assemble time)
        core.conn.close()
        core2 = assemble(db_path, case_root / "managed")
        pre = translation_readiness(core2)
        record["sequence"]["reassemble"] = "OK"
        record["reassemble_readiness"] = pre  # expected NOT_CONFIGURED (vault path)

        # step 4: env-resolver re-register + invalidate
        reregister_env_resolver(core2, base_url=args.base_url, model=args.model)
        record["sequence"]["reregister"] = "OK"

        post = translation_readiness(core2)
        record["readiness"] = post
        if post.get("state") != "ready":  # ProviderState.READY == "ready"
            record["error"] = f"readiness is {post.get('state')!r}, expected 'ready'"
            print(f"FAIL: {record['error']}", file=sys.stderr)
            raise RuntimeError(record["error"])

        # steps 5-6: resolve the provider and translate one real region
        from ports.translation.protocol import RegionInput, TranslationRequestPayload

        payload = TranslationRequestPayload(
            page_id="probe-page",
            regions=(
                RegionInput(region_id="probe-r1", text=REAL_REGION_TEXT, region_type="speech"),
            ),
        )
        provider = core2.providers.registry.resolve(
            "translation", PROVIDER_ID
        )
        t0 = time.perf_counter()
        result = provider.translate(payload)
        elapsed_s = round(time.perf_counter() - t0, 2)
        translations = result.translations
        record["translation"] = {
            "region_id": "probe-r1",
            "source_text": REAL_REGION_TEXT,
            "translated_text": translations.get("probe-r1", ""),
            "elapsed_s": elapsed_s,
            "provider_elapsed_ms": result.elapsed_ms,
            "model": result.model,
        }
        record["status"] = "OK"
        record["finished_at_utc"] = _now_utc()
        status = 0
        print(
            f"probe_status=OK translated={record['translation']['translated_text']!r} "
            f"elapsed_s={elapsed_s} readiness=READY"
        )
    except Exception as exc:  # noqa: BLE001 - honest probe record, no key ever printed
        record["status"] = "FAIL"
        record["error"] = f"{type(exc).__name__}: {exc}"[:400]
        print(f"probe_status=FAIL error={record['error']}", file=sys.stderr)
        status = 3

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"record -> {out}")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
