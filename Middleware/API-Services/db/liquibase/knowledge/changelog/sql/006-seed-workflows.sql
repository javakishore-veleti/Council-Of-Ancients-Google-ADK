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
