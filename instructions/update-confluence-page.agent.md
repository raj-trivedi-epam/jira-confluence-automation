# Confluence Project Status Page Update Instructions

- Accept input only as one JSON object; reject standalone URLs, page IDs, Markdown reports, and separate option values.
- Treat the JSON input shape and property names below as a stable contract.
  + Do not change, broaden, or replace the accepted format during unrelated edits.
  + Change the contract only when the user explicitly requests a format change; if the intended JSON shape is unclear, ask before editing or processing.
- Require the JSON object to contain:
  + `page`: an object with exactly one of `url` or `id` identifying the existing Confluence page.
  + `statusReport`: an object with exactly one of `markdown` or `path` containing the report content or a workspace-relative Markdown file path.
- Accept only these optional JSON properties:
  + `title`: a string for the page title.
  + `parentPageId`: a string or number, used only when page creation is explicitly permitted.
  + `dryRun`: a boolean that defaults to `true`.
  + `publish`: a boolean that defaults to `false`.
- Publish only when the JSON explicitly sets both `publish` to `true` and `dryRun` to `false`; reject `publish: true` when `dryRun` is omitted or `true`.
- Reject invalid JSON, missing required values, unknown properties, conflicting alternatives, and invalid property types before processing.
- Example input:
  ```json
  {
    "page": {"id": "123456"},
    "statusReport": {"path": "reports/weekly-status-report-2026-11-18.md"},
    "dryRun": true
  }
  ```
- Require a valid page target and status report content before processing.
  + Do not treat a page URL or ID, Markdown report, or option value supplied outside the JSON object as a request.
  + Do not publish unless the JSON contains both explicit `publish: true` and `dryRun: false`.
- Read the status report completely before transforming or publishing it.
- Validate required report fields: reporting period, overall status, executive summary, delivery update, blockers and risks, and data notes.
- Preserve aggregate-only stakeholder-safe content.
  + Omit issue keys, issue summaries, comments, individual names, and person-level comparisons.
  + Do not invent missing data, estimates, sprint progress, blockers, or decisions.
  + Mark unavailable or missing information explicitly.
- Convert the Markdown report into Confluence Storage Format.
- Preserve the report structure and order:
  + Page title.
  + Reporting period and generation timestamp.
  + Overall status.
  + Executive summary.
  + Delivery update.
  + Sprint progress.
  + Blockers and risks.
  + Decisions or support needed.
  + Data notes.
- Convert headings, bullets, links, and tables to valid Confluence Storage Format elements.
  + Render status values as text with explicit `Green`, `Amber`, or `Red` labels.
  + Preserve the source report's concise line and section structure.
- Resolve the existing page and fetch its current version before updating.
- Compare transformed content with the existing page body.
  + Skip the update when content is unchanged.
  + Report a version conflict and stop if the page changes during update preparation.
- In `dry-run` mode:
  + Return the target page, proposed title, and transformed Confluence Storage Format preview.
  + Report which content sections changed.
  + Do not call a write API or modify credentials, page permissions, labels, or attachments.
- In publish mode:
  + Use the Confluence REST API with a read-write token or approved OAuth credential.
  + Request the smallest permitted scope.
  + Update only the page body and optional title; do not alter permissions or metadata unless explicitly requested.
  + Increment the page version using the latest current version.
  + Verify the saved page after the update.
- Return a concise result containing:
  + `mode`: `dry-run`, `published`, `unchanged`, or `failed`.
  + `pageId`, `pageTitle`, and `pageUrl`.
  + `previousVersion` and `newVersion` when published.
  + `changedSections` and `warnings`.
  + A short success or failure summary.
- On failure, return:
  + The failed operation.
  + A non-sensitive error reason.
  + Whether the page was changed.
  + The bounded retry count used.
- Use bounded retries only for transient authentication, timeout, and rate-limit failures.
  + Do not retry validation or permission failures.
  + Leave the page unchanged after a pre-update validation failure.
- Never write credentials, tokens, cookies, private issue content, or sensitive headers to source files, logs, reports, or chat output.
- Do not use comments, Jira issue wording, or inferred data to identify blockers.
- Do not publish by default and do not send page notifications or broadcast links unless explicitly requested.
- Do not create or replace a page unless the input explicitly permits page creation or replacement.
