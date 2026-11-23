CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS jira_configurations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  jira_site_url TEXT,
  project_key TEXT,
  board_id INTEGER,
  blocker_marker TEXT,
  validation_status TEXT NOT NULL DEFAULT 'blocked',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  trigger_type TEXT NOT NULL,
  status TEXT NOT NULL,
  started_at TIMESTAMPTZ NOT NULL,
  ended_at TIMESTAMPTZ,
  safe_error_category TEXT,
  safe_error_summary TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID NOT NULL REFERENCES runs(id),
  reporting_period_start TIMESTAMPTZ NOT NULL,
  reporting_period_end TIMESTAMPTZ NOT NULL,
  generated_at TIMESTAMPTZ NOT NULL,
  canonical_file_path TEXT NOT NULL,
  review_status TEXT NOT NULL DEFAULT 'unreviewed',
  reviewer TEXT,
  review_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS reports_run_id_idx ON reports(run_id);
CREATE INDEX IF NOT EXISTS runs_created_at_idx ON runs(created_at DESC);
