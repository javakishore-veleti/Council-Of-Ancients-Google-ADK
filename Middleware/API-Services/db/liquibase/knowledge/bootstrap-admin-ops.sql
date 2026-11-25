-- Admin ops tables + seeds for coa_admin_api.
-- Run after bootstrap.sql:
--   psql postgresql://postgres:postgres@localhost:5432/council -f bootstrap-admin-ops.sql

CREATE EXTENSION IF NOT EXISTS pgcrypto;

ALTER TABLE knowledge.knowledge_source
  DROP CONSTRAINT IF EXISTS ck_knowledge_source_status;
ALTER TABLE knowledge.knowledge_source
  ADD CONSTRAINT ck_knowledge_source_status
  CHECK (status IN (
    'active', 'paused', 'denied', 'archived',
    'queued', 'running', 'fetched', 'failed'
  ));

CREATE TABLE IF NOT EXISTS knowledge.app_endpoint (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  kind TEXT NOT NULL,
  provider TEXT NOT NULL,
  endpoint_url TEXT NOT NULL,
  resource TEXT NOT NULL,
  region TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT ck_app_endpoint_kind CHECK (kind IN (
    'relational_db', 'vector_db', 'object_store', 'cloud_provider',
    'http_origin', 'search', 'graph', 'queue', 'other'
  )),
  CONSTRAINT ck_app_endpoint_status CHECK (status IN ('active', 'draft', 'disabled'))
);

CREATE TABLE IF NOT EXISTS knowledge.knowledge_source_endpoint (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id UUID NOT NULL REFERENCES knowledge.knowledge_source(id) ON DELETE CASCADE,
  endpoint_id UUID NOT NULL REFERENCES knowledge.app_endpoint(id) ON DELETE CASCADE,
  role TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT ck_kse_role CHECK (role IN ('download_from', 'store_to', 'tech_stack')),
  CONSTRAINT uq_kse_source_endpoint_role UNIQUE (source_id, endpoint_id, role)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_kse_one_download_from
  ON knowledge.knowledge_source_endpoint (source_id)
  WHERE role = 'download_from';

CREATE TABLE IF NOT EXISTS knowledge.wf_exec_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id UUID NOT NULL REFERENCES knowledge.knowledge_source(id) ON DELETE CASCADE,
  engine TEXT NOT NULL DEFAULT 'airflow',
  external_run_id TEXT,
  status TEXT NOT NULL DEFAULT 'queued',
  download_from_endpoint_id UUID,
  store_to_endpoint_ids UUID[] NOT NULL DEFAULT '{}'::uuid[],
  tech_stack_endpoint_ids UUID[] NOT NULL DEFAULT '{}'::uuid[],
  started_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ,
  error_message TEXT,
  detail TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT ck_wf_engine CHECK (engine IN ('airflow', 'step_functions', 'local')),
  CONSTRAINT ck_wf_status CHECK (status IN (
    'queued', 'started', 'running', 'completed', 'failed', 'cancelled'
  ))
);

CREATE INDEX IF NOT EXISTS ix_wf_exec_log_source_created
  ON knowledge.wf_exec_log (source_id, created_at DESC);

-- SRE children
INSERT INTO knowledge.knowledge_category (code, name, description, parent_id, sort_order)
SELECT v.code, v.name, v.description, p.id, v.sort_order
FROM knowledge.knowledge_category p
CROSS JOIN (VALUES
  ('foundations', 'Foundations', 'SRE foundations.', 10),
  ('practices', 'Practices', 'SRE practices.', 20),
  ('security', 'Security baselines', 'Security baselines under Architecture.', 80)
) AS v(code, name, description, sort_order)
WHERE p.code = 'sre' AND v.code IN ('foundations', 'practices')
ON CONFLICT (code) DO NOTHING;

INSERT INTO knowledge.knowledge_category (code, name, description, parent_id, sort_order)
SELECT v.code, v.name, v.description, p.id, v.sort_order
FROM knowledge.knowledge_category p
CROSS JOIN (VALUES
  ('security', 'Security baselines', 'NIST and related baselines.', 80)
) AS v(code, name, description, sort_order)
WHERE p.code = 'software_architecture'
ON CONFLICT (code) DO NOTHING;

-- App endpoints (fixed UUIDs)
INSERT INTO knowledge.app_endpoint (id, name, kind, provider, endpoint_url, resource, region, status, notes, created_at) VALUES
  ('34031dd4-0cfb-555d-8958-dea3037de640', 'DigitalOcean community (origin)', 'http_origin', 'DigitalOcean', 'https://www.digitalocean.com', 'community/tutorials', NULL, 'active', NULL, '2026-10-15T08:00:00Z'),
  ('6f536e3f-0b54-52df-a994-017bced3c5e4', 'Wikipedia (origin)', 'http_origin', 'Wikimedia', 'https://en.wikipedia.org', 'wiki/*', NULL, 'active', NULL, '2026-10-15T08:05:00Z'),
  ('337ff920-19ad-5380-bcb0-cde8e0a46960', 'NIST CSRC (origin)', 'http_origin', 'NIST', 'https://csrc.nist.gov', 'pubs/*', NULL, 'active', NULL, '2026-10-15T08:10:00Z'),
  ('6defc77e-cdec-54f0-80b5-06f56c51d7c5', 'Local Postgres (registry)', 'relational_db', 'PostgreSQL', 'postgresql://127.0.0.1:5432', 'db:coa_knowledge', 'local', 'active', 'Knowledge category/source registry — not a vector store.', '2026-10-18T09:00:00Z'),
  ('07c51f6f-bccf-5a1a-b92c-090bae7aff3b', 'Local Postgres + pgvector', 'vector_db', 'PostgreSQL pgvector', 'postgresql://127.0.0.1:5432', 'db:coa_vectors schema:rag', 'local', 'active', 'Same Postgres instance, vector extension for embeddings.', '2026-10-18T09:15:00Z'),
  ('1766fa73-e2ef-58f1-9289-af5f0045f5fc', 'Local Chroma', 'vector_db', 'Chroma', 'http://127.0.0.1:8000', 'collection:coa_default', 'local', 'active', NULL, '2026-10-19T11:00:00Z'),
  ('878f0a3b-007a-5f3c-8e7b-46d87a8d917b', 'Local Qdrant', 'vector_db', 'Qdrant', 'http://127.0.0.1:6333', 'collection:coa_architecture', 'local', 'active', NULL, '2026-11-01T10:00:00Z'),
  ('b915d3e2-0d86-560d-b324-0f6e4098f8be', 'COA KnowledgeBase (local datasets)', 'object_store', 'Local FS', 'file://$HOME/runtime_data/apps/datasets/COA/KnowledgeBase', '$HOME/runtime_data/apps/datasets/COA/KnowledgeBase/{category_code}/{subcategory_code}/{source_uuid}/', 'local', 'active', 'Base folder for downloaded files. Leaf is source UUID.', '2026-10-20T12:00:00Z'),
  ('8f4b32ff-6723-52a8-b798-cf798fc0a8a2', 'AWS S3 — KB bucket', 'object_store', 'AWS S3', 's3://coa-kb-prod', 's3://coa-kb-prod/', 'us-east-1', 'draft', NULL, '2026-11-18T16:00:00Z'),
  ('0316cfc6-b095-5571-9ca3-782ba500a537', 'AWS Bedrock (embeddings)', 'cloud_provider', 'AWS Bedrock', 'https://bedrock-runtime.us-east-1.amazonaws.com', 'model:amazon.titan-embed-text-v2', 'us-east-1', 'draft', NULL, '2026-11-18T16:30:00Z'),
  ('663865e6-1dc5-5e9d-b9c3-132cdbe83a32', 'Azure Blob — KB container', 'object_store', 'Azure Blob Storage', 'https://coakb.blob.core.windows.net', 'container:knowledge', 'eastus', 'draft', NULL, '2026-11-19T10:00:00Z'),
  ('27c73c2c-e7c2-5e53-b12f-44def16e2bcf', 'Azure AI Search', 'search', 'Azure AI Search', 'https://coa-search.search.windows.net', 'index:coa-kb', 'eastus', 'draft', NULL, '2026-11-19T10:15:00Z'),
  ('d6f6c3ed-f423-5c27-8fa7-aa4903a56dc0', 'GCP Cloud Storage — KB', 'object_store', 'GCP Cloud Storage', 'gs://coa-kb-prod', 'gs://coa-kb-prod/', 'us-central1', 'draft', NULL, '2026-11-20T12:00:00Z'),
  ('70f29969-6625-5da9-ae14-7e47bc455263', 'GCP Vertex Matching Engine', 'cloud_provider', 'GCP Vertex AI', 'https://us-central1-aiplatform.googleapis.com', 'Matching Engine index (eval)', 'us-central1', 'draft', 'Eval only.', '2026-11-20T14:00:00Z'),
  ('b60d7baa-6e67-5926-9211-91f4612c8e51', 'Pinecone (3rd party)', 'vector_db', 'Pinecone', 'https://*.pinecone.io', 'index:coa-prod', 'us-east-1-aws', 'disabled', 'Example 3rd-party vector endpoint.', '2026-11-21T08:00:00Z')
ON CONFLICT (id) DO UPDATE SET
  name = EXCLUDED.name,
  kind = EXCLUDED.kind,
  provider = EXCLUDED.provider,
  endpoint_url = EXCLUDED.endpoint_url,
  resource = EXCLUDED.resource,
  region = EXCLUDED.region,
  status = EXCLUDED.status,
  notes = EXCLUDED.notes;

-- Sources (category_id = subcategory)
INSERT INTO knowledge.knowledge_source (
  id, category_id, name, description, citation_name, citation_desc, source_key, url, license, status, created_at
)
SELECT
  s.id, c.id, s.name, s.description, s.citation_name, s.citation_desc, s.source_key, s.url, s.license, s.status, s.created_at::timestamptz
FROM knowledge.knowledge_category c
JOIN (VALUES
  ('d85e1c09-8157-5565-82d3-f9f3cf209509'::uuid, 'patterns', 'DigitalOcean GoF hub',
   'Gang of Four patterns overview — personal RAG practice (NC license).',
   'DigitalOcean — GoF Design Patterns',
   'Community tutorial overview of creational, structural, and behavioral patterns.',
   'do_gof_hub',
   'https://www.digitalocean.com/community/tutorials/gangs-of-four-gof-design-patterns',
   'CC-BY-NC-SA-4.0', 'active', '2026-11-10T14:22:00Z'),
  ('a4a5367d-c001-55c1-b041-01e5048391a2'::uuid, 'styles', 'Wikipedia Microservices',
   'Open overview for Architecture styles: microservices.',
   'Wikipedia — Microservices', 'CC BY-SA encyclopedia article on the microservices style.',
   'wiki_microservices', 'https://en.wikipedia.org/wiki/Microservices', 'CC-BY-SA-4.0', 'active', '2026-11-12T09:05:00Z'),
  ('69e113bf-ed73-5443-8627-0c50201f9c2c'::uuid, 'styles', 'Wikipedia Event-driven architecture',
   NULL, 'Wikipedia — Event-driven architecture', NULL,
   'wiki_eda', 'https://en.wikipedia.org/wiki/Event-driven_architecture', 'CC-BY-SA-4.0', 'fetched', '2026-11-14T11:40:00Z'),
  ('ded90588-34c1-556f-919d-f9814f6d75e6'::uuid, 'security', 'NIST SP 800-53 Rev. 5',
   NULL, 'NIST — Security and Privacy Controls', NULL,
   'nist_sp_800_53_r5', 'https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final', 'Public Domain', 'queued', '2026-11-18T16:12:00Z'),
  ('1bc34c61-596c-56d1-9644-24cf38697676'::uuid, 'security', 'NIST SP 800-207 Zero Trust',
   NULL, 'NIST — Zero Trust Architecture', NULL,
   'nist_sp_800_207', 'https://csrc.nist.gov/pubs/sp/800/207/final', 'Public Domain', 'running', '2026-11-19T08:30:00Z'),
  ('a6cf18ae-3e01-5555-ad2d-d81ca4306a25'::uuid, 'foundations', 'Wikipedia Site Reliability Engineering',
   NULL, 'Wikipedia — Site Reliability Engineering', NULL,
   'wiki_sre', 'https://en.wikipedia.org/wiki/Site_reliability_engineering', 'CC-BY-SA-4.0', 'active', '2026-11-08T12:00:00Z'),
  ('d7db658f-8ec7-5392-aba7-58472430c480'::uuid, 'practices', 'Wikipedia Chaos engineering',
   NULL, 'Wikipedia — Chaos engineering', NULL,
   'wiki_chaos', 'https://en.wikipedia.org/wiki/Chaos_engineering', 'CC-BY-SA-4.0', 'paused', '2026-11-09T10:18:00Z'),
  ('2a6008b7-62e1-5ad1-8048-d6c451335dd1'::uuid, 'patterns', 'Wikipedia CQRS',
   NULL, 'Wikipedia — Command–query separation', NULL,
   'wiki_cqrs', 'https://en.wikipedia.org/wiki/Command–query_separation', 'CC-BY-SA-4.0', 'failed', '2026-11-15T19:45:00Z'),
  ('9ce3af76-b631-5efd-905e-175fc05ceeef'::uuid, 'styles', 'Wikipedia Hexagonal architecture',
   NULL, 'Wikipedia — Hexagonal architecture (software)', NULL,
   'wiki_hexagonal', 'https://en.wikipedia.org/wiki/Hexagonal_architecture_(software)', 'CC-BY-SA-4.0', 'active', '2026-11-16T07:55:00Z'),
  ('6bb81423-542b-5148-85ac-c03ef36cbcb0'::uuid, 'patterns', 'Wikipedia Domain-driven design',
   NULL, 'Wikipedia — Domain-driven design', NULL,
   'wiki_ddd', 'https://en.wikipedia.org/wiki/Domain-driven_design', 'CC-BY-SA-4.0', 'archived', '2026-10-28T13:20:00Z'),
  ('06a745b6-fcf2-5c1e-85ea-ee78ebec2054'::uuid, 'practices', 'Wikipedia Observability',
   NULL, 'Wikipedia — Observability', NULL,
   'wiki_observability', 'https://en.wikipedia.org/wiki/Observability', 'CC-BY-SA-4.0', 'active', '2026-11-20T15:02:00Z'),
  ('b0409dad-428a-5708-a5f0-d11ec2be14ae'::uuid, 'styles', 'Wikipedia CAP theorem',
   NULL, 'Wikipedia — CAP theorem', NULL,
   'wiki_cap', 'https://en.wikipedia.org/wiki/CAP_theorem', 'CC-BY-SA-4.0', 'denied', '2026-11-21T09:10:00Z')
) AS s(id, cat_code, name, description, citation_name, citation_desc, source_key, url, license, status, created_at)
  ON c.code = s.cat_code
ON CONFLICT (id) DO UPDATE SET
  name = EXCLUDED.name,
  description = EXCLUDED.description,
  citation_name = EXCLUDED.citation_name,
  citation_desc = EXCLUDED.citation_desc,
  url = EXCLUDED.url,
  license = EXCLUDED.license,
  status = EXCLUDED.status;

-- Endpoint maps for DigitalOcean GoF
DELETE FROM knowledge.knowledge_source_endpoint
 WHERE source_id = 'd85e1c09-8157-5565-82d3-f9f3cf209509';
INSERT INTO knowledge.knowledge_source_endpoint (source_id, endpoint_id, role) VALUES
  ('d85e1c09-8157-5565-82d3-f9f3cf209509', '34031dd4-0cfb-555d-8958-dea3037de640', 'download_from'),
  ('d85e1c09-8157-5565-82d3-f9f3cf209509', 'b915d3e2-0d86-560d-b324-0f6e4098f8be', 'store_to');

-- Maps for Wikipedia Microservices
DELETE FROM knowledge.knowledge_source_endpoint
 WHERE source_id = 'a4a5367d-c001-55c1-b041-01e5048391a2';
INSERT INTO knowledge.knowledge_source_endpoint (source_id, endpoint_id, role) VALUES
  ('a4a5367d-c001-55c1-b041-01e5048391a2', '6f536e3f-0b54-52df-a994-017bced3c5e4', 'download_from'),
  ('a4a5367d-c001-55c1-b041-01e5048391a2', 'b915d3e2-0d86-560d-b324-0f6e4098f8be', 'store_to');
-- Default maps for remaining sources: wiki origin + local KB store
INSERT INTO knowledge.knowledge_source_endpoint (source_id, endpoint_id, role)
SELECT s.id, '6f536e3f-0b54-52df-a994-017bced3c5e4'::uuid, 'download_from'
FROM knowledge.knowledge_source s
WHERE s.id NOT IN (
  'd85e1c09-8157-5565-82d3-f9f3cf209509',
  'a4a5367d-c001-55c1-b041-01e5048391a2',
  'ded90588-34c1-556f-919d-f9814f6d75e6',
  '1bc34c61-596c-56d1-9644-24cf38697676'
)
AND NOT EXISTS (
  SELECT 1 FROM knowledge.knowledge_source_endpoint k
  WHERE k.source_id = s.id AND k.role = 'download_from'
);

UPDATE knowledge.knowledge_source
SET category_id = (SELECT id FROM knowledge.knowledge_category WHERE code = 'security' LIMIT 1)
WHERE id IN ('ded90588-34c1-556f-919d-f9814f6d75e6', '1bc34c61-596c-56d1-9644-24cf38697676');

INSERT INTO knowledge.knowledge_source_endpoint (source_id, endpoint_id, role)
SELECT s.id, '337ff920-19ad-5380-bcb0-cde8e0a46960'::uuid, 'download_from'
FROM knowledge.knowledge_source s
WHERE s.id IN ('ded90588-34c1-556f-919d-f9814f6d75e6', '1bc34c61-596c-56d1-9644-24cf38697676')
AND NOT EXISTS (
  SELECT 1 FROM knowledge.knowledge_source_endpoint k
  WHERE k.source_id = s.id AND k.role = 'download_from'
);

INSERT INTO knowledge.knowledge_source_endpoint (source_id, endpoint_id, role)
SELECT s.id, 'b915d3e2-0d86-560d-b324-0f6e4098f8be'::uuid, 'store_to'
FROM knowledge.knowledge_source s
WHERE NOT EXISTS (
  SELECT 1 FROM knowledge.knowledge_source_endpoint k
  WHERE k.source_id = s.id AND k.role = 'store_to'
    AND k.endpoint_id = 'b915d3e2-0d86-560d-b324-0f6e4098f8be'
);
