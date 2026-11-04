"""Live API probe used to validate the documented contract.

Runs the same requests that the Postman collection encodes and writes a
machine-readable transcript to reports/api-smoke.json. The transcript is the
evidence behind docs/defect-report.md.

Usage:
    python scripts/api_smoke.py
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import requests

BASE_URL = "https://api.restful-api.dev"
TIMEOUT = 30
PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT_ROOT / "reports" / "api-smoke.json"


def call(session: requests.Session, label: str, method: str, path: str, **kwargs) -> dict:
    url = f"{BASE_URL}{path}"
    started = time.perf_counter()
    response = session.request(method, url, timeout=TIMEOUT, **kwargs)
    elapsed_ms = round((time.perf_counter() - started) * 1000)
    try:
        body = response.json()
    except ValueError:
        body = response.text
    record = {
        "label": label,
        "request": {"method": method, "url": url, **{k: v for k, v in kwargs.items() if k != "headers"}},
        "status": response.status_code,
        "elapsed_ms": elapsed_ms,
        "body": body,
    }
    print(f"[{label}] {method} {path} -> {response.status_code} ({elapsed_ms} ms)")
    return record


def main() -> None:
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})
    records: list[dict] = []
    created_id = None

    try:
        records.append(call(session, "list_objects", "GET", "/objects"))
        created = call(
            session,
            "create_object",
            "POST",
            "/objects",
            json={
                "name": "QA Portfolio Laptop",
                "data": {"year": 2026, "price": 1299.99, "CPU model": "Intel Core i7", "Hard disk size": "1 TB"},
            },
        )
        records.append(created)
        if isinstance(created["body"], dict):
            created_id = created["body"].get("id")

        if created_id:
            records.append(call(session, "get_created_object", "GET", f"/objects/{created_id}"))
            records.append(
                call(
                    session,
                    "update_object_put",
                    "PUT",
                    f"/objects/{created_id}",
                    json={
                        "name": "QA Portfolio Laptop v2",
                        "data": {"year": 2027, "price": 1399.99, "CPU model": "Intel Core i9", "Hard disk size": "2 TB"},
                    },
                )
            )
            records.append(
                call(
                    session,
                    "patch_object",
                    "PATCH",
                    f"/objects/{created_id}",
                    json={"name": "QA Portfolio Laptop v2 (patched)"},
                )
            )
            records.append(call(session, "delete_object", "DELETE", f"/objects/{created_id}"))
            records.append(call(session, "get_deleted_object", "GET", f"/objects/{created_id}"))
            created_id = None

        # ---- negative / contract checks ----
        records.append(call(session, "get_unknown_id", "GET", "/objects/does-not-exist-123456"))
        records.append(call(session, "create_missing_name", "POST", "/objects", json={"data": {"year": 2026}}))
        records.append(call(session, "delete_unknown_id", "DELETE", "/objects/does-not-exist-123456"))
        records.append(
            call(
                session,
                "create_malformed_json",
                "POST",
                "/objects",
                data="{this is not json",
                headers={"Content-Type": "application/json", "Accept": "application/json"},
            )
        )
        records.append(call(session, "filter_by_id", "GET", "/objects?id=3&id=5"))
    finally:
        if created_id:
            try:
                session.delete(f"{BASE_URL}/objects/{created_id}", timeout=TIMEOUT)
            except requests.RequestException:
                pass

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nTranscript written to {OUTPUT}")


if __name__ == "__main__":
    main()
