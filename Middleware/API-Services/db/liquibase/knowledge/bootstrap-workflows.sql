-- Workflow registry + source/exec FKs. Run after bootstrap-admin-ops.sql:
--   psql postgresql://postgres:postgres@localhost:5432/council -f bootstrap-workflows.sql

CREATE TABLE IF NOT EXISTS knowledge.workflow (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE,
  description TEXT,
  engine TEXT NOT NULL,
  external_ref TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  meta JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT ck_workflow_status CHECK (status IN ('active', 'draft', 'disabled'))
);

CREATE INDEX IF NOT EXISTS ix_workflow_engine ON knowledge.workflow (engine);

ALTER TABLE knowledge.knowledge_source
  ADD COLUMN IF NOT EXISTS workflow_id UUID REFERENCES knowledge.workflow(id);

ALTER TABLE knowledge.wf_exec_log
  ADD COLUMN IF NOT EXISTS wf_id UUID REFERENCES knowledge.workflow(id);

ALTER TABLE knowledge.wf_exec_log DROP CONSTRAINT IF EXISTS ck_wf_engine;

CREATE INDEX IF NOT EXISTS ix_wf_exec_log_wf_id ON knowledge.wf_exec_log (wf_id);

INSERT INTO knowledge.workflow (id, name, description, engine, external_ref, status, meta, created_at)
VALUES
(
  'b0f1ace0-0001-4000-8000-000000000001',
  'kb_ingest_facade',
  'Facade ingest run for a knowledge source download. Gates license/robots, invokes extract workflow, stores under UUID leaf, patches wf_exec_log.',
  'airflow',
  'kb_ingest_facade',
  'active',
  '{"role":"facade","invokes":"kb_extract"}'::jsonb,
  '2026-11-20T10:00:00Z'
),
(
  'b0f1ace0-0001-4000-8000-000000000002',
  'kb_extract',
  'URL-agnostic extract step. Default strategy generic_markdown; host strategies swappable without changing the facade.',
  'airflow',
  'kb_extract',
  'active',
  '{"role":"extract","default_strategy":"generic_markdown"}'::jsonb,
  '2026-11-20T10:00:00Z'
)
ON CONFLICT (id) DO NOTHING;

UPDATE knowledge.knowledge_source
SET workflow_id = 'b0f1ace0-0001-4000-8000-000000000001'
WHERE workflow_id IS NULL;

UPDATE knowledge.wf_exec_log
SET wf_id = 'b0f1ace0-0001-4000-8000-000000000001'
WHERE wf_id IS NULL;
