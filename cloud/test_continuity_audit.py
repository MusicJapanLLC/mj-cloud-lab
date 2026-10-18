"""Strict network-free unit tests for the public fallback evidence collector."""
import io
import json
import unittest

try:
    from cloud.continuity_audit import PROJECTS, fetch_public_run_metadata, make_report
except ModuleNotFoundError:
    from continuity_audit import PROJECTS, fetch_public_run_metadata, make_report


class FakeResponse:
    status = 200
    def __init__(self, body):
        self.body = io.BytesIO(body)
    def read(self, length):
        return self.body.read(length)
    def __enter__(self):
        return self
    def __exit__(self, *_):
        self.body.close()


class ContinuityTests(unittest.TestCase):
    def test_allowlist_prevents_arbitrary_domains_and_private_repos(self):
        for value in ["evil.invalid/a", "MusicJapanLLC/private", "../../secrets", "MusicJapanLLC/mj-cloud-lab?token=x"]:
            with self.assertRaises(ValueError):
                fetch_public_run_metadata(value, urlopen=lambda *_a, **_k: self.fail("unexpected request"))

    def test_successful_retrieval_reports_just_public_metadata(self):
        payload = {"workflow_runs": [{"id": 100, "status": "completed", "conclusion": "success", "updated_at": "2026-10-18T10:00:00Z", "actor": {"email": "private@example.com"}}]}
        captured=[]
        def fake_urlopen(req, timeout):
            captured.append((req.full_url, timeout))
            return FakeResponse(json.dumps(payload).encode())
        result = fetch_public_run_metadata(PROJECTS[0], urlopen=fake_urlopen)
        self.assertTrue(result["reachable"])
        self.assertEqual(result["latest_run_id"], 100)
        self.assertNotIn("actor", json.dumps(result))
        self.assertTrue(captured[0][0].startswith("https://api.github.com/repos/"))

    def test_no_run_is_not_false_failure(self):
        value = fetch_public_run_metadata(PROJECTS[0], urlopen=lambda *_a, **_kw: FakeResponse(b'{"workflow_runs":[]}'))
        self.assertTrue(value["reachable"])
        self.assertEqual(value["recent_run_count"], 0)
        self.assertIsNone(value["latest_run_id"])

    def test_bad_json_returns_unknown_without_data_leakage(self):
        result = fetch_public_run_metadata(PROJECTS[0], urlopen=lambda *_a, **_kw: FakeResponse(b'{NOT JSON'))
        self.assertFalse(result["reachable"])
        self.assertNotIn("NOT JSON", json.dumps(result))

    def test_receipt_is_deterministic_given_observations_and_timestamp(self):
        from datetime import datetime, timezone
        instant = datetime(2026,10,18,0,0,tzinfo=timezone.utc)
        fetcher = lambda repo: {"repository": repo,"reachable":True,"recent_run_count":0}
        a = make_report(fetcher=fetcher,now=instant)
        b = make_report(fetcher=fetcher,now=instant)
        self.assertEqual(a, b)
        self.assertEqual(len(a["receipt_sha256"]),64)
        self.assertEqual(a["remote_desktop_tool_calls_by_this_job"],0)
        self.assertEqual(a["paid_model_api_calls_by_this_job"],0)
        self.assertEqual(a["pc_operating_state"],"NOT_CHECKED")

    def test_partial_unavailability_never_claims_success(self):
        def fetcher(repo):
            return {"repository":repo,"reachable":repo==PROJECTS[0]}
        a=make_report(fetcher=fetcher)
        self.assertFalse(a["all_public_endpoints_observable"])
        self.assertEqual(a["automatic_pc_recovery"],"NOT_IMPLEMENTED")


if __name__ == "__main__":
    unittest.main()
