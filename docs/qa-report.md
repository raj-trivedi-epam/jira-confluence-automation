# QA Report

**Test date:** 2026-11-24  
**Environment:** Local macOS development; frontend at `http://127.0.0.1:5173/`, API at `http://127.0.0.1:3001/`

## Summary

The prototype's mocked manual-report flow passed end-to-end testing. Live Jira-backed report generation is not available; the generated report is explicitly labeled demo data.

## Pages Visited

| Page | Result |
|---|---|
| `/` — Jira/Confluence Automation | Loaded successfully. This is the only implemented application page; no other routes or page-navigation links were found. |

## Elements Tested

- **Text:** “Prototype”, “Jira/Confluence Automation”, and the demo-only/no-live-Jira disclaimer.
- **Button:** “Generate report”.
- **After submission:** loading state, success status, generated-report heading, saved path, and complete Markdown report content.
- **Forms and links:** none are present on the page.

## Test Results

| Test | Result |
|---|---|
| Frontend root page | HTTP 200 |
| API health check (`GET /health`) | HTTP 200; `{"status":"ok"}` |
| Manual report (`POST /api/runs`) | HTTP 201; generated a dated mock report and displayed it in the UI |
| Run history (`GET /api/runs`) | Returned three successful manual runs from the browser test; history is process-local, not persisted |
| Report revisions | Repeated same-day runs created the base report and `-r02`/`-r03` revisions without overwriting earlier output |
| Generation failure handling | API test forced a file-write failure; returned HTTP 500 and recorded a failed run with a safe error summary |
| Browser console | No JavaScript errors or warnings on the successful page |
| PostgreSQL container | Docker Compose reported PostgreSQL 15 as `healthy`; a SQL query was not performed |
| Automated checks | API tests: 2 passed; frontend production build passed; API TypeScript check and `git diff --check` passed |

The latest generated demo artifact is [`weekly-status-report-2026-11-24-r03.md`](../work/mock-reports/weekly-status-report-2026-11-24-r03.md). Screenshots of the starting page and generated-report state were captured inline in the chat; they were not saved as workspace image files.

## Bugs Found and Fixes Applied

1. **The starting page was initially unreachable.** Chrome returned `ERR_CONNECTION_REFUSED` because the frontend server was not running. The API and frontend were restarted; the page and API then responded successfully.
2. **“Generate report” only called the health endpoint and showed no result.** The button now submits to `POST /api/runs`. The API writes a dated, revision-safe mock report under `work/mock-reports/`, records the run outcome in process memory, and returns the report. The UI displays loading, success or failure, the saved path, and report content.
3. **Mock output could be mistaken for real project data.** The UI and report now clearly state that the output is demo-only, contains no Jira data, and must not be shared as a factual update.

## Current Status and Limitations

- **Passed:** local mocked manual-report generation, display, revision naming, and explicit failure reporting.
- **No open browser console errors or warnings.**
- **Not production-ready for real reports:** Jira OAuth, approved Jira configuration, live data retrieval, PostgreSQL persistence, report review, and scheduled generation are not implemented. Run history currently resets when the API process restarts.
- The generated report has unavailable metrics rather than invented values; it is a flow-test artifact, not a stakeholder report.
