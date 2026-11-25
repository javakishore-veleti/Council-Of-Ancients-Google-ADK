-- Bootstrap knowledge schema without Liquibase CLI (idempotent-ish for local).
-- psql postgresql://postgres:postgres@localhost:5432/council -f bootstrap.sql

CREATE SCHEMA IF NOT EXISTS knowledge;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS knowledge.knowledge_category (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  description TEXT,
  parent_id UUID REFERENCES knowledge.knowledge_category(id),
  sort_order INT NOT NULL DEFAULT 0,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_knowledge_category_parent
  ON knowledge.knowledge_category(parent_id);

CREATE TABLE IF NOT EXISTS knowledge.knowledge_source (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  category_id UUID NOT NULL REFERENCES knowledge.knowledge_category(id),
  name TEXT NOT NULL UNIQUE,
  description TEXT,
  citation_name TEXT NOT NULL,
  citation_desc TEXT,
  source_key TEXT NOT NULL UNIQUE,
  url TEXT,
  license TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  meta JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT ck_knowledge_source_status
    CHECK (status IN ('active', 'paused', 'denied', 'archived'))
);

CREATE INDEX IF NOT EXISTS ix_knowledge_source_category
  ON knowledge.knowledge_source(category_id);

INSERT INTO knowledge.knowledge_category (code, name, description, parent_id, sort_order) VALUES
  ('entrepreneurship', 'Entrepreneurship', 'Plan, fund, and launch with disciplined judgment.', NULL, 10),
  ('leadership', 'Leadership', 'People, culture, and one-way-door decisions.', NULL, 20),
  ('software_architecture', 'Architecture', 'Patterns, styles, data, cloud, events, and AI systems.', NULL, 30),
  ('sre', 'SRE', 'Reliability, budgets, and calm incident response.', NULL, 40),
  ('fitness', 'Fitness', 'Training and recovery guidance — not medical advice.', NULL, 50)
ON CONFLICT (code) DO NOTHING;

INSERT INTO knowledge.knowledge_category (code, name, description, parent_id, sort_order)
SELECT v.code, v.name, v.description, p.id, v.sort_order
FROM knowledge.knowledge_category p
CROSS JOIN (VALUES
  ('patterns', 'Patterns', 'Classic design pattern families.', 10),
  ('styles', 'Architecture styles', 'Monolith, modular, microservices, event-driven, serverless.', 20),
  ('data', 'Data & modeling', 'Models, consistency, and schema evolution.', 30),
  ('cloud', 'Cloud & infrastructure', 'Platform and infrastructure choices.', 40),
  ('databases', 'Databases & storage', 'Storage engines and topologies.', 50),
  ('events', 'Event systems', 'Queues, streams, and pub/sub.', 60),
  ('ai_systems', 'AI & agentic systems', 'Orchestration, RAG, evals, guardrails.', 70)
) AS v(code, name, description, sort_order)
WHERE p.code = 'software_architecture'
ON CONFLICT (code) DO NOTHING;
