# How to Complete the Weekly Status Report

Use [template.md](./template.md) for each report. The intended report is a single, aggregate-only update suitable for internal leadership and client stakeholders.

## 1. Set the reporting period

- Use the rolling seven days ending at the report’s generation time.
- Record the start and end dates, generation time, and time zone. The planned schedule is Friday at 3:00 PM Asia/Kolkata.
- Take the active-sprint snapshot at generation time and identify the sprint dates.

## 2. Gather and validate Jira data

- Use the authorized Jira Cloud project and the agreed Scrum board.
- Confirm that the Jira data covers the full reporting period and the active sprint.
- Count work as completed only when it was resolved during the reporting period and remains resolved at report time. Exclude work that has since been reopened.
- Use the project’s story-point field for sprint progress. Keep unestimated work visible as missing data; never count a missing estimate as zero.
- Identify blockers only through the Jira field, flag, or label agreed for the project. Do not infer blockers from issue wording or comments.
- If data is unavailable or inconsistent, describe the limitation in **Data Notes** instead of guessing or silently substituting a value.

## 3. Fill in the sections

- **Overall status:** Choose Green, Amber, or Red and give a concise, evidence-based reason:
  - **Green:** Delivery is on track; no material issue needs escalation.
  - **Amber:** There is a credible risk to a commitment or sprint goal, with a mitigation or decision in progress.
  - **Red:** A commitment or sprint goal is materially off track and needs timely intervention.
- **Executive Summary:** State the most important outcome, current delivery outlook, and any key concern or ask.
- **Completed:** Summarize outcomes resolved during the period.
- **In Progress:** Describe the major work currently underway and its aggregate status.
- **Upcoming:** Summarize near-term planned work or milestones; distinguish plans from commitments.
- **Sprint Progress:** Enter story-point totals only when supported by Jira data. Explain progress against the sprint goal and mention missing estimates.
- **Blockers and Risks:** Include confirmed blockers or risks, their impact, mitigation, and the next update date. If none are confirmed, use the template’s suggested wording.
- **Decisions or Support Needed:** Make each request specific, with the decision-maker or role and due date. If there are no requests, say so.
- **Data Notes:** Record material coverage gaps, assumptions, or other limitations.

## 4. Keep the report safe and concise

- Use aggregate counts, story points, milestones, and outcomes.
- Do not include individual performance comparisons, personal details, issue keys, detailed issue summaries, raw comments, or confidential project information.
- Write for both leadership and client readers; use clear, neutral language and expand unfamiliar abbreviations.
- Separate verified facts from forecasts, risks, and decisions needed. Do not invent progress or imply that a plan is complete.
- Keep each section brief and remove unused placeholders before review.

## 5. Save and review

- Save each report as `weekly-status-report-YYYY-MM-DD.md` in this folder, using the report date in Asia/Kolkata.
- Review every report before sharing. Do not email or publish it automatically.
- If required Jira data cannot be retrieved or validated, do not replace the previous report with an incomplete report. Record the failure and correct the source or access issue before generating again.

The reusable Jira fetch and report-generation core is in [weekly_status/](../weekly_status/).
It is not yet connected to a configured OAuth provider or confirmed Jira board; see
its README before running it.

