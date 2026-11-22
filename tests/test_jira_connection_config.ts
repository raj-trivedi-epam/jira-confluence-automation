import assert from "node:assert/strict";
import test from "node:test";

import { validateJiraConnectionConfig } from "../apps/api/src/config/jira.ts";

test("blocks Jira connection config until every value is confirmed", () => {
  const result = validateJiraConnectionConfig({
    siteUrl: "https://company.atlassian.net",
    siteUrlConfirmed: false,
    projectKey: "CLOUD",
    projectKeyConfirmed: false,
    boardId: null,
    activeSprintConfirmed: false,
  });

  assert.equal(result.status, "blocked");
  assert.ok(result.errors.includes("Jira project key is not confirmed."));
  assert.ok(result.errors.includes("Jira board ID must be a positive integer."));
  assert.ok(
    result.errors.includes(
      "The board's active-sprint behavior is not confirmed.",
    ),
  );
});

test("rejects placeholder and non-HTTPS Jira site URLs", () => {
  const result = validateJiraConnectionConfig({
    siteUrl: "http://company.atlassian.net",
    siteUrlConfirmed: true,
    projectKey: "CLOUD",
    projectKeyConfirmed: true,
    boardId: 123,
    activeSprintConfirmed: true,
  });

  assert.equal(result.status, "blocked");
  assert.ok(
    result.errors.includes("Jira Cloud site URL must be an approved HTTPS URL."),
  );
});

test("accepts fully confirmed Jira connection config", () => {
  const result = validateJiraConnectionConfig({
    siteUrl: "https://approved-team.atlassian.net",
    siteUrlConfirmed: true,
    projectKey: "CLOUD",
    projectKeyConfirmed: true,
    boardId: 123,
    activeSprintConfirmed: true,
  });

  assert.deepEqual(result.errors, []);
  assert.equal(result.status, "configured");
});
