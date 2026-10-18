#!/usr/bin/env python3
"""Zero-credit, Remote-Desktop-independent health evidence for public MJ cloud jobs.

Deliberately touches only public GitHub metadata. No account credentials, owner-PC
commands, paid model APIs, or Supabase private data are used here.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import urllib.error
import urllib.request

PROJECTS = (
    "MusicJapanLLC/mj-cloud-lab",
    "MusicJapanLLC/music-japan-cloud-inference",
)
API_ROOT = "https://api.github.com/repos/"
SCHEMA = "music-japan.remote-free-continuity/v1"


def fetch_public_run_metadata(repo: str, *, urlopen=urllib.request.urlopen) -> dict:
    if repo not in PROJECTS:
        raise ValueError("repository is not explicitly allowlisted")
    req = urllib.request.Request(
        f"{API_ROOT}{repo}/actions/runs?per_page=5",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "music-japan-public-continuity/1"},
    )
    try:
        with urlopen(req, timeout=12) as response:
            if response.status != 200:
                return {"repository": repo, "reachable": False, "http_status": response.status}
            body = response.read(1024 * 1024 + 1)
            if len(body) > 1024 * 1024:
                return {"repository": repo, "reachable": False, "error": "response_too_large"}
        parsed = json.loads(body)
        if not isinstance(parsed, dict) or not isinstance(parsed.get("workflow_runs"), list):
            raise ValueError("unrecognized_github_api_schema")
        runs = parsed["workflow_runs"]
        safe_runs = [x for x in runs if isinstance(x, dict)]
        latest = safe_runs[0] if safe_runs else {}
        successful = next((x for x in safe_runs if x.get("conclusion") == "success"), None)
        # Absence of recent runs is INACTIVITY, never proof a system is broken.
        return {
            "repository": repo, "reachable": True,
            "recent_run_count": len(safe_runs),
            "latest_run_id": latest.get("id"),
            "latest_run_status": latest.get("status"),
            "latest_run_conclusion": latest.get("conclusion"),
            "latest_run_at": latest.get("updated_at") or latest.get("created_at"),
            "last_successful_run_id_among_five": successful.get("id") if successful else None,
            "classification": "recent_public_workflow_metadata_only",
        }
    except (OSError, ValueError, urllib.error.URLError, json.JSONDecodeError) as exc:
        return {"repository": repo, "reachable": False, "error": type(exc).__name__}


def make_report(*, fetcher=fetch_public_run_metadata, now=None) -> dict:
    checked_at = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat()
    checks = [fetcher(repo) for repo in PROJECTS]
    facts = {
        "schema": SCHEMA,
        "observed_at_utc": checked_at,
        "execution_plane": "github_hosted_python",
        "remote_desktop_tool_calls_by_this_job": 0,
        "paid_model_api_calls_by_this_job": 0,
        "private_business_records_collected": False,
        "scope": "public_github_metadata_only",
        "checks": checks,
        "all_public_endpoints_observable": all(x.get("reachable") is True for x in checks),
        "pc_operating_state": "NOT_CHECKED",
        "automatic_pc_recovery": "NOT_IMPLEMENTED",
    }
    canonical = json.dumps(facts, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    facts["receipt_sha256"] = hashlib.sha256(canonical).hexdigest()
    return facts


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="optional JSON evidence destination")
    args = parser.parse_args(argv)
    report = make_report()
    serial = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    print(serial)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serial, encoding="utf-8")
    return 0 if report["all_public_endpoints_observable"] else 1


if __name__ == "__main__":
    sys.exit(main())
