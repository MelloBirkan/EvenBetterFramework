#!/usr/bin/env python3
"""Verify that an EvenBetter guideline URL resolves to HTTP 200."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request


ALLOWED_DOMAINS = {"developer.apple.com"}
TIMEOUT_SECONDS = 5


def _domain_allowed(hostname: str | None) -> bool:
    if not hostname:
        return False
    return hostname.rstrip(".").lower() in ALLOWED_DOMAINS


def _request(url: str, method: str) -> tuple[int | None, str | None]:
    request = urllib.request.Request(
        url,
        method=method,
        headers={"User-Agent": "EvenBetter-URL-Validator/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return response.getcode(), None
    except urllib.error.HTTPError as error:
        return error.code, str(error)
    except Exception as error:  # noqa: BLE001 - deterministic CLI error reporting
        return None, str(error)


def verify(url: str) -> dict[str, object]:
    parsed = urllib.parse.urlparse(url)
    domain_allowed = _domain_allowed(parsed.hostname)
    result: dict[str, object] = {
        "url": url,
        "ok": False,
        "status_code": None,
        "domain_allowed": domain_allowed,
        "method": "HEAD",
        "error": None,
    }

    if parsed.scheme not in {"http", "https"}:
        result["error"] = "unsupported_scheme"
        return result

    if not domain_allowed:
        result["error"] = "domain_not_allowed"
        return result

    status_code, error = _request(url, "HEAD")
    result["status_code"] = status_code
    result["error"] = error

    if status_code in {405, 501}:
        status_code, error = _request(url, "GET")
        result["status_code"] = status_code
        result["method"] = "GET"
        result["error"] = error

    result["ok"] = status_code == 200
    if status_code != 200 and result["error"] is None:
        result["error"] = "non_200_status"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify an EvenBetter guideline URL.")
    parser.add_argument("url", help="URL to verify")
    args = parser.parse_args()

    result = verify(args.url)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
