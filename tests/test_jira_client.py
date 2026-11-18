import json
import unittest
from datetime import date
from io import BytesIO
from urllib.error import HTTPError

from weekly_status.jira_client import JiraClient, JiraError


class FakeResponse:
    def __init__(self, value):
        self.payload = json.dumps(value).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return self.payload


class JiraClientTests(unittest.TestCase):
    def test_paginates_all_results_and_sends_oauth_bearer_header(self):
        requests = []

        def opener(request, timeout):
            requests.append((request, timeout))
            start_at = int(request.full_url.split("startAt=")[1].split("&")[0])
            if start_at == 0:
                return FakeResponse(
                    {"issues": [{"id": "1"}, {"id": "2"}], "total": 3}
                )
            return FakeResponse({"issues": [{"id": "3"}], "total": 3})

        client = JiraClient(
            "https://example.atlassian.net",
            lambda: "oauth-access-token",
            opener=opener,
        )

        issues = client._get_all("rest/api/3/search", {}, "issues")

        self.assertEqual([{"id": "1"}, {"id": "2"}, {"id": "3"}], issues)
        self.assertEqual(2, len(requests))
        self.assertEqual(
            "Bearer oauth-access-token",
            requests[0][0].get_header("Authorization"),
        )
        self.assertEqual(20, requests[0][1])

    def test_retries_rate_limit_with_bounded_delay(self):
        attempts = []
        delays = []

        def opener(request, timeout):
            attempts.append(request)
            if len(attempts) == 1:
                raise HTTPError(
                    request.full_url,
                    429,
                    "rate limited",
                    {"Retry-After": "30"},
                    BytesIO(),
                )
            return FakeResponse({"values": []})

        client = JiraClient(
            "https://example.atlassian.net",
            lambda: "token",
            opener=opener,
            sleep=delays.append,
        )

        self.assertEqual({"values": []}, client.get("rest/api/3/field"))
        self.assertEqual([5.0], delays)
        self.assertEqual(2, len(attempts))

    def test_does_not_retry_unauthorized_responses(self):
        attempts = []

        def opener(request, timeout):
            attempts.append(request)
            raise HTTPError(request.full_url, 401, "unauthorized", {}, BytesIO())

        client = JiraClient(
            "https://example.atlassian.net",
            lambda: "token",
            opener=opener,
            sleep=lambda _: self.fail("401 must not be retried"),
        )

        with self.assertRaisesRegex(JiraError, "HTTP 401"):
            client.get("rest/api/3/field")
        self.assertEqual(1, len(attempts))

    def test_resolved_issue_search_rejects_invalid_project_keys(self):
        client = JiraClient("https://example.atlassian.net", lambda: "token")

        with self.assertRaisesRegex(ValueError, "project_key"):
            client.resolved_issues(
                'CLOUD" OR project IS NOT EMPTY',
                date(2026, 11, 11),
                date(2026, 11, 19),
                ["status"],
            )

    def test_field_discovery_requires_a_unique_exact_name(self):
        client = JiraClient(
            "https://example.atlassian.net",
            lambda: "token",
            opener=lambda request, timeout: FakeResponse(
                [
                    {"id": "customfield_10001", "name": "Story Points"},
                    {"id": "customfield_10002", "name": "story points"},
                ]
            ),
        )

        self.assertEqual("customfield_10001", client.find_field_id("Story Points"))

    def test_jira_issue_search_uses_cursor_pagination(self):
        requests = []

        def opener(request, timeout):
            requests.append(request.full_url)
            if len(requests) == 1:
                return FakeResponse(
                    {"issues": [{"id": "1"}], "isLast": False, "nextPageToken": "p2"}
                )
            return FakeResponse({"issues": [{"id": "2"}], "isLast": True})

        client = JiraClient(
            "https://example.atlassian.net",
            lambda: "token",
            opener=opener,
        )

        result = client.resolved_issues(
            "CLOUD",
            date(2026, 11, 10),
            date(2026, 11, 20),
            ["status"],
        )

        self.assertEqual([{"id": "1"}, {"id": "2"}], result)
        self.assertNotIn("nextPageToken", requests[0])
        self.assertIn("nextPageToken=p2", requests[1])


if __name__ == "__main__":
    unittest.main()
