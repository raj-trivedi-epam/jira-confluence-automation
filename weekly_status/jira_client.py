"""Small read-only Jira Cloud client for report data."""

import json
import re
import time
from datetime import date, datetime
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen


class JiraError(RuntimeError):
    """Raised when Jira data cannot be retrieved or validated."""


class JiraClient:
    def __init__(
        self,
        base_url,
        access_token_provider,
        timeout=20,
        max_attempts=3,
        opener=urlopen,
        sleep=time.sleep,
    ):
        parsed_url = urlsplit(base_url)
        if (
            parsed_url.scheme != "https"
            or not parsed_url.netloc
            or parsed_url.username
            or parsed_url.password
            or parsed_url.query
            or parsed_url.fragment
        ):
            raise ValueError("Jira base URL must be an HTTPS URL.")
        if isinstance(max_attempts, bool) or max_attempts < 1:
            raise ValueError("max_attempts must be at least 1.")
        if not callable(access_token_provider):
            raise TypeError("access_token_provider must be callable.")

        self.base_url = base_url.rstrip("/")
        self.access_token_provider = access_token_provider
        self.timeout = timeout
        self.max_attempts = max_attempts
        self.opener = opener
        self.sleep = sleep

    def get(self, path, params=None):
        url = "{}/{}".format(self.base_url, path.lstrip("/"))
        if params:
            url = "{}?{}".format(url, urlencode(params))

        for attempt in range(self.max_attempts):
            token = self.access_token_provider()
            if not token:
                raise JiraError("OAuth access token is unavailable.")
            request = Request(
                url,
                headers={
                    "Accept": "application/json",
                    "Authorization": "Bearer {}".format(token),
                },
            )
            try:
                with self.opener(request, timeout=self.timeout) as response:
                    return json.loads(response.read().decode("utf-8"))
            except HTTPError as error:
                if error.code not in (429, 500, 502, 503, 504):
                    raise JiraError(
                        "Jira request failed with HTTP {}.".format(error.code)
                    ) from error
                if attempt + 1 == self.max_attempts:
                    raise JiraError(
                        "Jira request failed after {} attempts (HTTP {}).".format(
                            self.max_attempts, error.code
                        )
                    ) from error
                self.sleep(self._retry_delay(error.headers, attempt))
            except URLError as error:
                if attempt + 1 == self.max_attempts:
                    raise JiraError(
                        "Jira request failed after {} attempts.".format(
                            self.max_attempts
                        )
                    ) from error
                self.sleep(self._retry_delay({}, attempt))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise JiraError("Jira returned invalid JSON.") from error

    def _get_all(self, path, params, collection_key):
        start_at = 0
        results = []
        while True:
            page_params = dict(params)
            page_params.update({"startAt": start_at, "maxResults": 100})
            page = self.get(path, page_params)
            if not isinstance(page, dict) or not isinstance(
                page.get(collection_key), list
            ):
                raise JiraError(
                    "Jira response is missing the '{}' list.".format(collection_key)
                )
            items = page[collection_key]
            results.extend(items)
            total = page.get("total")
            if isinstance(total, bool) or not isinstance(total, int) or total < 0:
                raise JiraError("Jira response has an invalid pagination total.")
            if start_at + len(items) >= total:
                return results
            if not items:
                raise JiraError("Jira pagination stopped before all results arrived.")
            start_at += len(items)

    def _get_all_search_pages(self, jql, fields):
        page_params = {"jql": jql, "fields": ",".join(fields), "maxResults": 100}
        results = []
        seen_tokens = set()
        while True:
            page = self.get("rest/api/3/search/jql", page_params)
            if not isinstance(page, dict) or not isinstance(page.get("issues"), list):
                raise JiraError("Jira search response is missing the 'issues' list.")
            results.extend(page["issues"])
            if page.get("isLast") is True:
                return results
            token = page.get("nextPageToken")
            if not isinstance(token, str) or not token or token in seen_tokens:
                raise JiraError("Jira search response has an invalid page token.")
            seen_tokens.add(token)
            page_params["nextPageToken"] = token

    def active_sprint(self, board_id):
        if isinstance(board_id, bool) or not isinstance(board_id, int) or board_id < 1:
            raise ValueError("board_id must be a positive integer.")
        sprints = self._get_all(
            "rest/agile/1.0/board/{}/sprint".format(board_id),
            {"state": "active"},
            "values",
        )
        if len(sprints) != 1:
            raise JiraError(
                "Expected one active sprint on board {}; found {}.".format(
                    board_id, len(sprints)
                )
            )
        return sprints[0]

    def sprint_issues(self, sprint_id, fields, project_key=None):
        if (
            isinstance(sprint_id, bool)
            or not isinstance(sprint_id, int)
            or sprint_id < 1
        ):
            raise ValueError("sprint_id must be a positive integer.")
        params = {"fields": ",".join(fields)}
        if project_key is not None:
            if not isinstance(project_key, str) or not re.fullmatch(
                r"[A-Z][A-Z0-9_]*", project_key
            ):
                raise ValueError("project_key must be an uppercase Jira project key.")
            params["jql"] = 'project = "{}"'.format(project_key)
        return self._get_all(
            "rest/agile/1.0/sprint/{}/issue".format(sprint_id),
            params,
            "issues",
        )

    def find_field_id(self, field_name):
        fields = self.get("rest/api/3/field")
        if not isinstance(fields, list):
            raise JiraError("Jira field response is not a list.")
        matches = [
            field
            for field in fields
            if isinstance(field, dict) and field.get("name") == field_name
        ]
        if len(matches) != 1:
            raise JiraError(
                "Expected one Jira field named {!r}; found {}.".format(
                    field_name, len(matches)
                )
            )
        field_id = matches[0].get("id")
        if not isinstance(field_id, str) or not field_id:
            raise JiraError("The matched Jira field has no valid ID.")
        return field_id

    def resolved_issues(self, project_key, start_date, end_date, fields):
        if not isinstance(project_key, str) or not re.fullmatch(
            r"[A-Z][A-Z0-9_]*", project_key
        ):
            raise ValueError("project_key must be an uppercase Jira project key.")
        if (
            not isinstance(start_date, date)
            or isinstance(start_date, datetime)
            or not isinstance(end_date, date)
            or isinstance(end_date, datetime)
        ):
            raise TypeError("start_date and end_date must be date objects.")
        if start_date >= end_date:
            raise ValueError("start_date must be earlier than end_date.")

        jql = (
            'project = "{}" AND resolutiondate >= "{}" '
            'AND resolutiondate < "{}" AND resolution IS NOT EMPTY'
        ).format(project_key, start_date.isoformat(), end_date.isoformat())
        return self._get_all_search_pages(jql, fields)

    @staticmethod
    def _retry_delay(headers, attempt):
        retry_after = headers.get("Retry-After") if headers else None
        if retry_after:
            try:
                return min(5.0, max(0.0, float(retry_after)))
            except ValueError:
                pass
        return min(5.0, 0.5 * (2 ** attempt))
