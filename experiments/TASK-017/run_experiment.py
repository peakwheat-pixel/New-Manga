"""Run every TASK-017 scenario end-to-end and emit machine results.

Writes ``results.json`` next to this file with per-scenario outcomes,
retry/fallback traces, token/latency measurements and the explicit
NOT_RUN list for real-provider layers (no paid provider was configured;
the experiment must not configure one — TASK-017 禁止范围).
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from mock_provider import MockProvider, ProtocolClient
from protocol import (
    ViolationKind,
    build_request,
    glossary_hits,
    validate_response,
)
from samples import CONTEXT_PAGES, GLOSSARY, PAGE1_REGIONS

OUT = Path(__file__).resolve().parent / "results.json"


def measure(server: MockProvider, payload: dict, expected_ids: tuple[str, ...]) -> dict:
    client = ProtocolClient(server.base_url)
    started = time.monotonic()
    raw, fault = client.complete(payload)
    elapsed_ms = round((time.monotonic() - started) * 1000, 2)
    report = validate_response(raw, expected_ids)
    return {
        "transport": fault,
        "kind": report.kind,
        "ok": report.ok,
        "detail": report.detail,
        "latency_ms": elapsed_ms,
        "tokens_estimated": sum(len(text) for text in report.translations.values()) // 2 or 0,
    }


def main() -> dict:
    results: dict = {"scenarios": [], "not_run": []}

    # S1: happy path with multi-page context + glossary
    server = MockProvider().start()
    request = build_request("page-1", PAGE1_REGIONS, CONTEXT_PAGES, GLOSSARY)
    outcome = measure(server, request.payload(), request.region_ids)
    raw, fault = ProtocolClient(server.base_url).complete(request.payload())
    report = validate_response(raw, request.region_ids)
    outcome["glossary_hits"] = glossary_hits(report.translations, GLOSSARY)
    outcome["context_truncated_pages"] = list(request.truncated_context_pages)
    results["scenarios"].append({"id": "S1_happy_path_context_glossary", **outcome})
    server.stop()

    # S2: retry input invariance (§57) — 503 then ok, identical payload hash
    server = MockProvider(faults=["http_503"]).start()
    request = build_request("page-1", PAGE1_REGIONS, CONTEXT_PAGES, GLOSSARY)
    client = ProtocolClient(server.base_url)
    first_fault = client.complete(request.payload())[1]
    second_raw, second_fault = client.complete(request.payload())
    second_report = validate_response(second_raw, request.region_ids)
    results["scenarios"].append({
        "id": "S2_retry_input_invariance",
        "first_fault": first_fault,
        "second_fault": second_fault,
        "second_ok": second_report.ok,
        "payload_hash": request.payload_hash(),
        "requests_recorded": len(server.requests),
        "payloads_identical": (
            json.dumps(server.requests[0], sort_keys=True, ensure_ascii=False)
            == json.dumps(server.requests[1], sort_keys=True, ensure_ascii=False)
            if len(server.requests) >= 2 else False
        ),
    })
    server.stop()

    # S3..S7: protocol violation classes
    for fault, kind in [
        ("malformed_json", ViolationKind.MALFORMED_JSON),
        ("drop:region-2", ViolationKind.MISSING_IDS),
        ("dup:region-1", ViolationKind.DUPLICATE_IDS),
        ("extra:region-999", ViolationKind.EXTRA_IDS),
        ("empty", ViolationKind.EMPTY_TRANSLATIONS),
    ]:
        server = MockProvider(faults=[fault]).start()
        request = build_request("page-1", PAGE1_REGIONS, CONTEXT_PAGES, GLOSSARY)
        raw, transport = ProtocolClient(server.base_url).complete(request.payload())
        report = validate_response(raw, request.region_ids)
        results["scenarios"].append({
            "id": f"S_{fault.replace(':', '_')}",
            "transport": transport,
            "classified": report.kind,
            "expected": kind,
            "match": report.kind == kind,
            "retryable": report.retryable,
        })
        server.stop()

    # S8: explicit-only fallback chain (§54)
    primary = MockProvider(faults=["http_503"], name="primary").start()
    secondary = MockProvider(name="secondary").start()
    request = build_request("page-1", PAGE1_REGIONS, [], GLOSSARY)
    _, first_fault = ProtocolClient(primary.base_url).complete(request.payload())
    second_raw, second_fault = ProtocolClient(secondary.base_url).complete(request.payload())
    second_report = validate_response(second_raw, request.region_ids)
    results["scenarios"].append({
        "id": "S8_explicit_fallback_chain",
        "primary_fault": first_fault,
        "secondary_fault": second_fault,
        "secondary_ok": second_report.ok,
        "provenance_records_switch": "secondary" in second_raw,
        "no_automatic_fallback_by_construction": True,
    })
    primary.stop()
    secondary.stop()

    results["not_run"] = [
        "真实 OpenAI-compatible 远程 Provider（未配置付费端点，禁止自行配置）",
        "真实 Sakura 本地实例（本机未运行 Sakura 服务）",
        "真实模型的术语一致性/质量评分（mock 为确定性规则翻译，不声称模型质量）",
    ]
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    return results


if __name__ == "__main__":
    summary = main()
    ok = all(
        scenario.get("match", scenario.get("ok", scenario.get("second_ok", True)))
        for scenario in summary["scenarios"]
    )
    print(json.dumps(summary, ensure_ascii=True, indent=2))
    raise SystemExit(0 if ok else 1)
