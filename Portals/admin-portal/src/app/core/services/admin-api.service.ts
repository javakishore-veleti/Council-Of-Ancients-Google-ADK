import { Injectable } from '@angular/core';
import { Observable, of, throwError } from 'rxjs';
import { delay, map } from 'rxjs/operators';

/** Ingest lifecycle for a knowledge source. */
export type IngestStatus =
  | 'active'
  | 'queued'
  | 'running'
  | 'fetched'
  | 'failed'
  | 'paused'
  | 'denied'
  | 'archived';

/**
 * App Endpoint = any configurable dependency target.
 * Not limited to vector DBs — local Postgres, Chroma, pgvector, AWS/Azure/GCP,
 * HTTP origins, object stores, search, graphs, or other 3rd parties.
 */
export type AppEndpointKind =
  | 'relational_db'
  | 'vector_db'
  | 'object_store'
  | 'cloud_provider'
  | 'http_origin'
  | 'search'
  | 'graph'
  | 'queue'
  | 'other';

export type AppEndpointStatus = 'active' | 'draft' | 'disabled';

export interface AppEndpoint {
  /** Primary key: UUID as string. */
  id: string;
  name: string;
  kind: AppEndpointKind;
  /** Vendor / product: Postgres, Chroma, AWS, Azure, GCP, … */
  provider: string;
  /** Host / base URL / connection target (no secrets in UI fixtures). */
  endpoint_url: string;
  /** Collection, schema, bucket, index, database name, etc. */
  resource: string;
  region?: string;
  status: AppEndpointStatus;
  notes?: string;
  created_on: string;
}

/**
 * Download: one origin endpoint → many store-to endpoints (same content, fan-out).
 * Tech stack: separate mapped endpoints (indexes / DBs / clouds the chamber uses).
 */
export interface AdminKnowledgeSource {
  /** Primary key: UUID as string. */
  id: string;
  name: string;
  description?: string;
  citation_name: string;
  citation_desc?: string;
  category_name: string;
  category_code: string;
  subcategory_name: string;
  subcategory_code: string;
  url?: string;
  license?: string;
  ingest_status: IngestStatus;
  created_on: string;
  updated_on?: string;
  download_from_endpoint_id: string | null;
  store_to_endpoint_ids: string[];
  tech_stack_endpoint_ids: string[];
  meta?: Record<string, unknown>;
}

/** Workflow engine that runs the download/index job. */
export type WfEngine = 'airflow' | 'step_functions' | 'local';

/**
 * One download/ops run. Created on Download click; DAG / Step Functions
 * (or local runner) patches status back via admin_api.
 */
export type WfExecStatus =
  | 'queued'
  | 'started'
  | 'running'
  | 'completed'
  | 'failed'
  | 'cancelled';

export interface WfExecLog {
  /** Primary key: UUID as string. */
  id: string;
  source_id: string;
  engine: WfEngine;
  /** External run id (Airflow dag_run_id, Step Functions execution ARN, …). */
  external_run_id: string | null;
  status: WfExecStatus;
  download_from_endpoint_id: string | null;
  store_to_endpoint_ids: string[];
  tech_stack_endpoint_ids: string[];
  started_at: string | null;
  finished_at: string | null;
  created_on: string;
  updated_on: string;
  error_message?: string;
  /** Free-form progress notes from callbacks. */
  detail?: string;
}

export interface DownloadJobResponse {
  wf_exec_log_id: string;
  source_id: string;
  status: 'queued';
  download_from_endpoint_id: string | null;
  store_to_endpoint_ids: string[];
}

export const APP_ENDPOINT_KIND_LABELS: Record<AppEndpointKind, string> = {
  relational_db: 'Relational DB',
  vector_db: 'Vector DB',
  object_store: 'Object store',
  cloud_provider: 'Cloud provider',
  http_origin: 'HTTP origin',
  search: 'Search',
  graph: 'Graph',
  queue: 'Queue',
  other: 'Other',
};

/**
 * Admin UI talks ONLY to coa_admin_api.
 * Until that microservice is up, methods return local fixtures.
 */
@Injectable({ providedIn: 'root' })
export class AdminApiService {
  private readonly endpoints: AppEndpoint[] = [
    {
      id: '34031dd4-0cfb-555d-8958-dea3037de640',
      name: 'DigitalOcean community (origin)',
      kind: 'http_origin',
      provider: 'DigitalOcean',
      endpoint_url: 'https://www.digitalocean.com',
      resource: 'community/tutorials',
      status: 'active',
      created_on: '2026-10-15T08:00:00Z',
    },
    {
      id: '6f536e3f-0b54-52df-a994-017bced3c5e4',
      name: 'Wikipedia (origin)',
      kind: 'http_origin',
      provider: 'Wikimedia',
      endpoint_url: 'https://en.wikipedia.org',
      resource: 'wiki/*',
      status: 'active',
      created_on: '2026-10-15T08:05:00Z',
    },
    {
      id: '337ff920-19ad-5380-bcb0-cde8e0a46960',
      name: 'NIST CSRC (origin)',
      kind: 'http_origin',
      provider: 'NIST',
      endpoint_url: 'https://csrc.nist.gov',
      resource: 'pubs/*',
      status: 'active',
      created_on: '2026-10-15T08:10:00Z',
    },
    {
      id: '6defc77e-cdec-54f0-80b5-06f56c51d7c5',
      name: 'Local Postgres (registry)',
      kind: 'relational_db',
      provider: 'PostgreSQL',
      endpoint_url: 'postgresql://127.0.0.1:5432',
      resource: 'db:coa_knowledge',
      region: 'local',
      status: 'active',
      notes: 'Knowledge category/source registry — not a vector store.',
      created_on: '2026-10-18T09:00:00Z',
    },
    {
      id: '07c51f6f-bccf-5a1a-b92c-090bae7aff3b',
      name: 'Local Postgres + pgvector',
      kind: 'vector_db',
      provider: 'PostgreSQL pgvector',
      endpoint_url: 'postgresql://127.0.0.1:5432',
      resource: 'db:coa_vectors schema:rag',
      region: 'local',
      status: 'active',
      notes: 'Same Postgres instance, vector extension for embeddings.',
      created_on: '2026-10-18T09:15:00Z',
    },
    {
      id: '1766fa73-e2ef-58f1-9289-af5f0045f5fc',
      name: 'Local Chroma',
      kind: 'vector_db',
      provider: 'Chroma',
      endpoint_url: 'http://127.0.0.1:8000',
      resource: 'collection:coa_default',
      region: 'local',
      status: 'active',
      created_on: '2026-10-19T11:00:00Z',
    },
    {
      id: '878f0a3b-007a-5f3c-8e7b-46d87a8d917b',
      name: 'Local Qdrant',
      kind: 'vector_db',
      provider: 'Qdrant',
      endpoint_url: 'http://127.0.0.1:6333',
      resource: 'collection:coa_architecture',
      region: 'local',
      status: 'active',
      created_on: '2026-11-01T10:00:00Z',
    },
    {
      id: 'b915d3e2-0d86-560d-b324-0f6e4098f8be',
      name: 'COA KnowledgeBase (local datasets)',
      kind: 'object_store',
      provider: 'Local FS',
      endpoint_url: 'file://$HOME/runtime_data/apps/datasets/COA/KnowledgeBase',
      resource:
        '$HOME/runtime_data/apps/datasets/COA/KnowledgeBase/{category_code}/{subcategory_code}/{source_uuid}/',
      region: 'local',
      status: 'active',
      notes:
        'Base folder for downloaded files. Leaf folder is the source id (UUID string). No spaces. Example: architecture/patterns/d85e1c09-8157-5565-82d3-f9f3cf209509/.',
      created_on: '2026-10-20T12:00:00Z',
    },
    {
      id: '8f4b32ff-6723-52a8-b798-cf798fc0a8a2',
      name: 'AWS S3 — KB bucket',
      kind: 'object_store',
      provider: 'AWS S3',
      endpoint_url: 's3://coa-kb-prod',
      resource: 's3://coa-kb-prod/',
      region: 'us-east-1',
      status: 'draft',
      created_on: '2026-11-18T16:00:00Z',
    },
    {
      id: '0316cfc6-b095-5571-9ca3-782ba500a537',
      name: 'AWS Bedrock (embeddings)',
      kind: 'cloud_provider',
      provider: 'AWS Bedrock',
      endpoint_url: 'https://bedrock-runtime.us-east-1.amazonaws.com',
      resource: 'model:amazon.titan-embed-text-v2',
      region: 'us-east-1',
      status: 'draft',
      created_on: '2026-11-18T16:30:00Z',
    },
    {
      id: '663865e6-1dc5-5e9d-b9c3-132cdbe83a32',
      name: 'Azure Blob — KB container',
      kind: 'object_store',
      provider: 'Azure Blob Storage',
      endpoint_url: 'https://coakb.blob.core.windows.net',
      resource: 'container:knowledge',
      region: 'eastus',
      status: 'draft',
      created_on: '2026-11-19T10:00:00Z',
    },
    {
      id: '27c73c2c-e7c2-5e53-b12f-44def16e2bcf',
      name: 'Azure AI Search',
      kind: 'search',
      provider: 'Azure AI Search',
      endpoint_url: 'https://coa-search.search.windows.net',
      resource: 'index:coa-kb',
      region: 'eastus',
      status: 'draft',
      created_on: '2026-11-19T10:15:00Z',
    },
    {
      id: 'd6f6c3ed-f423-5c27-8fa7-aa4903a56dc0',
      name: 'GCP Cloud Storage — KB',
      kind: 'object_store',
      provider: 'GCP Cloud Storage',
      endpoint_url: 'gs://coa-kb-prod',
      resource: 'gs://coa-kb-prod/',
      region: 'us-central1',
      status: 'draft',
      created_on: '2026-11-20T12:00:00Z',
    },
    {
      id: '70f29969-6625-5da9-ae14-7e47bc455263',
      name: 'GCP Vertex Matching Engine',
      kind: 'cloud_provider',
      provider: 'GCP Vertex AI',
      endpoint_url: 'https://us-central1-aiplatform.googleapis.com',
      resource: 'Matching Engine index (eval)',
      region: 'us-central1',
      status: 'draft',
      notes: 'Eval only.',
      created_on: '2026-11-20T14:00:00Z',
    },
    {
      id: 'b60d7baa-6e67-5926-9211-91f4612c8e51',
      name: 'Pinecone (3rd party)',
      kind: 'vector_db',
      provider: 'Pinecone',
      endpoint_url: 'https://*.pinecone.io',
      resource: 'index:coa-prod',
      region: 'us-east-1-aws',
      status: 'disabled',
      notes: 'Example 3rd-party vector endpoint — not used in local stack.',
      created_on: '2026-11-21T08:00:00Z',
    },
  ];

  private readonly sources: AdminKnowledgeSource[] = [
    {
      id: 'd85e1c09-8157-5565-82d3-f9f3cf209509',
      name: 'DigitalOcean GoF hub',
      description: 'Gang of Four patterns overview — personal RAG practice (NC license).',
      citation_name: 'DigitalOcean — GoF Design Patterns',
      citation_desc: 'Community tutorial overview of creational, structural, and behavioral patterns.',
      category_code: 'architecture',
      category_name: 'Architecture',
      subcategory_code: 'patterns',
      subcategory_name: 'Patterns',
      url: 'https://www.digitalocean.com/community/tutorials/gangs-of-four-gof-design-patterns',
      license: 'CC-BY-NC-SA-4.0',
      ingest_status: 'active',
      created_on: '2026-11-10T14:22:00Z',
      download_from_endpoint_id: '34031dd4-0cfb-555d-8958-dea3037de640',
      store_to_endpoint_ids: ['b915d3e2-0d86-560d-b324-0f6e4098f8be', '8f4b32ff-6723-52a8-b798-cf798fc0a8a2', '663865e6-1dc5-5e9d-b9c3-132cdbe83a32'],
      tech_stack_endpoint_ids: ['07c51f6f-bccf-5a1a-b92c-090bae7aff3b', '1766fa73-e2ef-58f1-9289-af5f0045f5fc', '6defc77e-cdec-54f0-80b5-06f56c51d7c5'],
    },
    {
      id: 'a4a5367d-c001-55c1-b041-01e5048391a2',
      name: 'Wikipedia Microservices',
      description: 'Open overview for Architecture styles: microservices.',
      citation_name: 'Wikipedia — Microservices',
      citation_desc: 'CC BY-SA encyclopedia article on the microservices style.',
      category_code: 'architecture',
      category_name: 'Architecture',
      subcategory_code: 'styles',
      subcategory_name: 'Architecture styles',
      url: 'https://en.wikipedia.org/wiki/Microservices',
      license: 'CC-BY-SA-4.0',
      ingest_status: 'active',
      created_on: '2026-11-12T09:05:00Z',
      download_from_endpoint_id: '6f536e3f-0b54-52df-a994-017bced3c5e4',
      store_to_endpoint_ids: ['b915d3e2-0d86-560d-b324-0f6e4098f8be', 'd6f6c3ed-f423-5c27-8fa7-aa4903a56dc0'],
      tech_stack_endpoint_ids: ['878f0a3b-007a-5f3c-8e7b-46d87a8d917b', '6defc77e-cdec-54f0-80b5-06f56c51d7c5'],
    },
    {
      id: '69e113bf-ed73-5443-8627-0c50201f9c2c',
      name: 'Wikipedia Event-driven architecture',
      citation_name: 'Wikipedia — Event-driven architecture',
      category_code: 'architecture',
      category_name: 'Architecture',
      subcategory_code: 'styles',
      subcategory_name: 'Architecture styles',
      url: 'https://en.wikipedia.org/wiki/Event_driven_architecture',
      license: 'CC-BY-SA-4.0',
      ingest_status: 'fetched',
      created_on: '2026-11-14T11:40:00Z',
      download_from_endpoint_id: '6f536e3f-0b54-52df-a994-017bced3c5e4',
      store_to_endpoint_ids: ['b915d3e2-0d86-560d-b324-0f6e4098f8be', '8f4b32ff-6723-52a8-b798-cf798fc0a8a2'],
      tech_stack_endpoint_ids: ['07c51f6f-bccf-5a1a-b92c-090bae7aff3b'],
    },
    {
      id: 'ded90588-34c1-556f-919d-f9814f6d75e6',
      name: 'NIST SP 800-53 Rev. 5',
      citation_name: 'NIST — Security and Privacy Controls',
      category_code: 'architecture',
      category_name: 'Architecture',
      subcategory_code: 'security',
      subcategory_name: 'Security baselines',
      url: 'https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final',
      license: 'Public Domain',
      ingest_status: 'queued',
      created_on: '2026-11-18T16:12:00Z',
      download_from_endpoint_id: '337ff920-19ad-5380-bcb0-cde8e0a46960',
      store_to_endpoint_ids: ['b915d3e2-0d86-560d-b324-0f6e4098f8be', '8f4b32ff-6723-52a8-b798-cf798fc0a8a2', 'd6f6c3ed-f423-5c27-8fa7-aa4903a56dc0'],
      tech_stack_endpoint_ids: ['07c51f6f-bccf-5a1a-b92c-090bae7aff3b', '0316cfc6-b095-5571-9ca3-782ba500a537'],
    },
    {
      id: '1bc34c61-596c-56d1-9644-24cf38697676',
      name: 'NIST SP 800-207 Zero Trust',
      citation_name: 'NIST — Zero Trust Architecture',
      category_code: 'architecture',
      category_name: 'Architecture',
      subcategory_code: 'security',
      subcategory_name: 'Security baselines',
      url: 'https://csrc.nist.gov/pubs/sp/800/207/final',
      license: 'Public Domain',
      ingest_status: 'running',
      created_on: '2026-11-19T08:30:00Z',
      download_from_endpoint_id: '337ff920-19ad-5380-bcb0-cde8e0a46960',
      store_to_endpoint_ids: ['b915d3e2-0d86-560d-b324-0f6e4098f8be'],
      tech_stack_endpoint_ids: ['1766fa73-e2ef-58f1-9289-af5f0045f5fc', '27c73c2c-e7c2-5e53-b12f-44def16e2bcf'],
    },
    {
      id: 'a6cf18ae-3e01-5555-ad2d-d81ca4306a25',
      name: 'Wikipedia Site Reliability Engineering',
      citation_name: 'Wikipedia — Site Reliability Engineering',
      category_code: 'sre',
      category_name: 'SRE',
      subcategory_code: 'foundations',
      subcategory_name: 'Foundations',
      url: 'https://en.wikipedia.org/wiki/Site_reliability_engineering',
      license: 'CC-BY-SA-4.0',
      ingest_status: 'active',
      created_on: '2026-11-08T12:00:00Z',
      download_from_endpoint_id: '6f536e3f-0b54-52df-a994-017bced3c5e4',
      store_to_endpoint_ids: ['b915d3e2-0d86-560d-b324-0f6e4098f8be'],
      tech_stack_endpoint_ids: ['07c51f6f-bccf-5a1a-b92c-090bae7aff3b', '6defc77e-cdec-54f0-80b5-06f56c51d7c5'],
    },
    {
      id: 'd7db658f-8ec7-5392-aba7-58472430c480',
      name: 'Wikipedia Chaos engineering',
      citation_name: 'Wikipedia — Chaos engineering',
      category_code: 'sre',
      category_name: 'SRE',
      subcategory_code: 'practices',
      subcategory_name: 'Practices',
      url: 'https://en.wikipedia.org/wiki/Chaos_engineering',
      license: 'CC-BY-SA-4.0',
      ingest_status: 'paused',
      created_on: '2026-11-09T10:18:00Z',
      download_from_endpoint_id: '6f536e3f-0b54-52df-a994-017bced3c5e4',
      store_to_endpoint_ids: ['b915d3e2-0d86-560d-b324-0f6e4098f8be', '663865e6-1dc5-5e9d-b9c3-132cdbe83a32'],
      tech_stack_endpoint_ids: ['878f0a3b-007a-5f3c-8e7b-46d87a8d917b'],
    },
    {
      id: '2a6008b7-62e1-5ad1-8048-d6c451335dd1',
      name: 'Wikipedia CQRS',
      citation_name: 'Wikipedia — Command–query separation',
      category_code: 'architecture',
      category_name: 'Architecture',
      subcategory_code: 'patterns',
      subcategory_name: 'Patterns',
      url: 'https://en.wikipedia.org/wiki/Command%E2%80%93query_separation',
      license: 'CC-BY-SA-4.0',
      ingest_status: 'failed',
      created_on: '2026-11-15T19:45:00Z',
      download_from_endpoint_id: '6f536e3f-0b54-52df-a994-017bced3c5e4',
      store_to_endpoint_ids: ['b915d3e2-0d86-560d-b324-0f6e4098f8be'],
      tech_stack_endpoint_ids: ['1766fa73-e2ef-58f1-9289-af5f0045f5fc'],
      meta: { last_error: 'fetch_403' },
    },
    {
      id: '9ce3af76-b631-5efd-905e-175fc05ceeef',
      name: 'Wikipedia Hexagonal architecture',
      citation_name: 'Wikipedia — Hexagonal architecture (software)',
      category_code: 'architecture',
      category_name: 'Architecture',
      subcategory_code: 'styles',
      subcategory_name: 'Architecture styles',
      url: 'https://en.wikipedia.org/wiki/Hexagonal_architecture_(software)',
      license: 'CC-BY-SA-4.0',
      ingest_status: 'active',
      created_on: '2026-11-16T07:55:00Z',
      download_from_endpoint_id: '6f536e3f-0b54-52df-a994-017bced3c5e4',
      store_to_endpoint_ids: ['b915d3e2-0d86-560d-b324-0f6e4098f8be'],
      tech_stack_endpoint_ids: ['07c51f6f-bccf-5a1a-b92c-090bae7aff3b', 'b60d7baa-6e67-5926-9211-91f4612c8e51'],
    },
    {
      id: '6bb81423-542b-5148-85ac-c03ef36cbcb0',
      name: 'Wikipedia Domain-driven design',
      citation_name: 'Wikipedia — Domain-driven design',
      category_code: 'architecture',
      category_name: 'Architecture',
      subcategory_code: 'patterns',
      subcategory_name: 'Patterns',
      url: 'https://en.wikipedia.org/wiki/Domain-driven_design',
      license: 'CC-BY-SA-4.0',
      ingest_status: 'archived',
      created_on: '2026-10-28T13:20:00Z',
      download_from_endpoint_id: '6f536e3f-0b54-52df-a994-017bced3c5e4',
      store_to_endpoint_ids: [],
      tech_stack_endpoint_ids: [],
    },
    {
      id: '06a745b6-fcf2-5c1e-85ea-ee78ebec2054',
      name: 'Wikipedia Observability',
      citation_name: 'Wikipedia — Observability',
      category_code: 'sre',
      category_name: 'SRE',
      subcategory_code: 'practices',
      subcategory_name: 'Practices',
      url: 'https://en.wikipedia.org/wiki/Observability',
      license: 'CC-BY-SA-4.0',
      ingest_status: 'active',
      created_on: '2026-11-20T15:02:00Z',
      download_from_endpoint_id: '6f536e3f-0b54-52df-a994-017bced3c5e4',
      store_to_endpoint_ids: ['b915d3e2-0d86-560d-b324-0f6e4098f8be', '8f4b32ff-6723-52a8-b798-cf798fc0a8a2', 'd6f6c3ed-f423-5c27-8fa7-aa4903a56dc0'],
      tech_stack_endpoint_ids: ['07c51f6f-bccf-5a1a-b92c-090bae7aff3b', '70f29969-6625-5da9-ae14-7e47bc455263'],
    },
    {
      id: 'b0409dad-428a-5708-a5f0-d11ec2be14ae',
      name: 'Wikipedia CAP theorem',
      citation_name: 'Wikipedia — CAP theorem',
      category_code: 'architecture',
      category_name: 'Architecture',
      subcategory_code: 'styles',
      subcategory_name: 'Architecture styles',
      url: 'https://en.wikipedia.org/wiki/CAP_theorem',
      license: 'CC-BY-SA-4.0',
      ingest_status: 'denied',
      created_on: '2026-11-21T09:10:00Z',
      download_from_endpoint_id: '6f536e3f-0b54-52df-a994-017bced3c5e4',
      store_to_endpoint_ids: ['b915d3e2-0d86-560d-b324-0f6e4098f8be'],
      tech_stack_endpoint_ids: [],
      meta: { deny_reason: 'license_review' },
    },
  ];

  listAppEndpoints(): Observable<AppEndpoint[]> {
    return of(this.endpoints).pipe(delay(100));
  }

  getAppEndpoint(id: string): Observable<AppEndpoint> {
    return of(this.endpoints).pipe(
      delay(60),
      map((list) => {
        const row = list.find((r) => r.id === id);
        if (!row) throw new Error('not_found');
        return row;
      }),
    );
  }

  resolveEndpoints(ids: string[]): AppEndpoint[] {
    const byId = new Map(this.endpoints.map((e) => [e.id, e]));
    return ids.map((id) => byId.get(id)).filter((e): e is AppEndpoint => !!e);
  }

  /** In-memory wf_exec_log store (fixtures + rows created by Download). */
  private readonly wfLogs: WfExecLog[] = [
    {
      id: 'c1a2b3c4-d5e6-4789-a012-3456789abc01',
      source_id: 'd85e1c09-8157-5565-82d3-f9f3cf209509',
      engine: 'airflow',
      external_run_id: 'kb_ingest_2026-11-10T19:30:00+00:00',
      status: 'completed',
      download_from_endpoint_id: '34031dd4-0cfb-555d-8958-dea3037de640',
      store_to_endpoint_ids: [
        'b915d3e2-0d86-560d-b324-0f6e4098f8be',
        '8f4b32ff-6723-52a8-b798-cf798fc0a8a2',
      ],
      tech_stack_endpoint_ids: [
        '07c51f6f-bccf-5a1a-b92c-090bae7aff3b',
        '1766fa73-e2ef-58f1-9289-af5f0045f5fc',
      ],
      started_at: '2026-11-10T19:30:12Z',
      finished_at: '2026-11-10T19:32:41Z',
      created_on: '2026-11-10T19:30:00Z',
      updated_on: '2026-11-10T19:32:41Z',
      detail: 'Stored raw + indexed into pgvector + Chroma.',
    },
    {
      id: 'c1a2b3c4-d5e6-4789-a012-3456789abc02',
      source_id: 'd85e1c09-8157-5565-82d3-f9f3cf209509',
      engine: 'airflow',
      external_run_id: 'kb_ingest_2026-11-18T11:02:00+00:00',
      status: 'failed',
      download_from_endpoint_id: '34031dd4-0cfb-555d-8958-dea3037de640',
      store_to_endpoint_ids: ['b915d3e2-0d86-560d-b324-0f6e4098f8be'],
      tech_stack_endpoint_ids: ['07c51f6f-bccf-5a1a-b92c-090bae7aff3b'],
      started_at: '2026-11-18T11:02:08Z',
      finished_at: '2026-11-18T11:02:55Z',
      created_on: '2026-11-18T11:02:00Z',
      updated_on: '2026-11-18T11:02:55Z',
      error_message: 'origin_fetch_timeout',
      detail: 'Retryable — origin timed out after 45s.',
    },

    {
      id: 'c1a2b3c4-d5e6-4789-a012-3456789abc04',
      source_id: 'd85e1c09-8157-5565-82d3-f9f3cf209509',
      engine: 'airflow',
      external_run_id: 'kb_ingest_2026-11-20T08:00:00+00:00',
      status: 'completed',
      download_from_endpoint_id: '34031dd4-0cfb-555d-8958-dea3037de640',
      store_to_endpoint_ids: ['b915d3e2-0d86-560d-b324-0f6e4098f8be'],
      tech_stack_endpoint_ids: ['07c51f6f-bccf-5a1a-b92c-090bae7aff3b'],
      started_at: '2026-11-20T08:00:10Z',
      finished_at: '2026-11-20T08:01:02Z',
      created_on: '2026-11-20T08:00:00Z',
      updated_on: '2026-11-20T08:01:02Z',
      detail: 'Re-index after prompt tweak.',
    },
    {
      id: 'c1a2b3c4-d5e6-4789-a012-3456789abc05',
      source_id: 'd85e1c09-8157-5565-82d3-f9f3cf209509',
      engine: 'local',
      external_run_id: 'local_2026-11-21T09:15:00',
      status: 'running',
      download_from_endpoint_id: '34031dd4-0cfb-555d-8958-dea3037de640',
      store_to_endpoint_ids: ['b915d3e2-0d86-560d-b324-0f6e4098f8be', '663865e6-1dc5-5e9d-b9c3-132cdbe83a32'],
      tech_stack_endpoint_ids: ['1766fa73-e2ef-58f1-9289-af5f0045f5fc'],
      started_at: '2026-11-21T09:15:05Z',
      finished_at: null,
      created_on: '2026-11-21T09:15:00Z',
      updated_on: '2026-11-21T09:15:05Z',
      detail: 'Local runner — writing Azure blob copy.',
    },
    {
      id: 'c1a2b3c4-d5e6-4789-a012-3456789abc06',
      source_id: 'd85e1c09-8157-5565-82d3-f9f3cf209509',
      engine: 'step_functions',
      external_run_id: 'arn:aws:states:us-east-1:123:execution:coa-kb:run-06',
      status: 'queued',
      download_from_endpoint_id: '34031dd4-0cfb-555d-8958-dea3037de640',
      store_to_endpoint_ids: ['8f4b32ff-6723-52a8-b798-cf798fc0a8a2'],
      tech_stack_endpoint_ids: ['0316cfc6-b095-5571-9ca3-782ba500a537'],
      started_at: null,
      finished_at: null,
      created_on: '2026-11-22T10:00:00Z',
      updated_on: '2026-11-22T10:00:00Z',
      detail: 'Future Step Functions path — not started.',
    },
    {
      id: 'c1a2b3c4-d5e6-4789-a012-3456789abc07',
      source_id: 'd85e1c09-8157-5565-82d3-f9f3cf209509',
      engine: 'airflow',
      external_run_id: 'kb_ingest_2026-11-23T12:00:00+00:00',
      status: 'cancelled',
      download_from_endpoint_id: '34031dd4-0cfb-555d-8958-dea3037de640',
      store_to_endpoint_ids: ['b915d3e2-0d86-560d-b324-0f6e4098f8be'],
      tech_stack_endpoint_ids: [],
      started_at: '2026-11-23T12:00:08Z',
      finished_at: '2026-11-23T12:00:40Z',
      created_on: '2026-11-23T12:00:00Z',
      updated_on: '2026-11-23T12:00:40Z',
      error_message: 'cancelled_by_operator',
      detail: 'Cancelled before store fan-out.',
    },
    {
      id: 'c1a2b3c4-d5e6-4789-a012-3456789abc08',
      source_id: 'd85e1c09-8157-5565-82d3-f9f3cf209509',
      engine: 'airflow',
      external_run_id: 'kb_ingest_2026-11-24T07:45:00+00:00',
      status: 'started',
      download_from_endpoint_id: '34031dd4-0cfb-555d-8958-dea3037de640',
      store_to_endpoint_ids: ['b915d3e2-0d86-560d-b324-0f6e4098f8be', 'd6f6c3ed-f423-5c27-8fa7-aa4903a56dc0'],
      tech_stack_endpoint_ids: ['07c51f6f-bccf-5a1a-b92c-090bae7aff3b'],
      started_at: '2026-11-24T07:45:04Z',
      finished_at: null,
      created_on: '2026-11-24T07:45:00Z',
      updated_on: '2026-11-24T07:45:04Z',
      detail: 'Fetch started.',
    },
    {
      id: 'c1a2b3c4-d5e6-4789-a012-3456789abc09',
      source_id: 'd85e1c09-8157-5565-82d3-f9f3cf209509',
      engine: 'airflow',
      external_run_id: 'kb_ingest_2026-11-24T16:20:00+00:00',
      status: 'completed',
      download_from_endpoint_id: '34031dd4-0cfb-555d-8958-dea3037de640',
      store_to_endpoint_ids: ['b915d3e2-0d86-560d-b324-0f6e4098f8be'],
      tech_stack_endpoint_ids: ['07c51f6f-bccf-5a1a-b92c-090bae7aff3b', '1766fa73-e2ef-58f1-9289-af5f0045f5fc'],
      started_at: '2026-11-24T16:20:06Z',
      finished_at: '2026-11-24T16:21:18Z',
      created_on: '2026-11-24T16:20:00Z',
      updated_on: '2026-11-24T16:21:18Z',
      detail: 'Nightly refresh completed.',
    },
    {
      id: 'c1a2b3c4-d5e6-4789-a012-3456789abc10',
      source_id: 'd85e1c09-8157-5565-82d3-f9f3cf209509',
      engine: 'airflow',
      external_run_id: 'kb_ingest_2026-11-25T01:00:00+00:00',
      status: 'failed',
      download_from_endpoint_id: '34031dd4-0cfb-555d-8958-dea3037de640',
      store_to_endpoint_ids: ['b915d3e2-0d86-560d-b324-0f6e4098f8be'],
      tech_stack_endpoint_ids: ['07c51f6f-bccf-5a1a-b92c-090bae7aff3b'],
      started_at: '2026-11-25T01:00:05Z',
      finished_at: '2026-11-25T01:00:22Z',
      created_on: '2026-11-25T01:00:00Z',
      updated_on: '2026-11-25T01:00:22Z',
      error_message: 'disk_full',
      detail: 'Local KnowledgeBase volume full.',
    },

    {
      id: 'c1a2b3c4-d5e6-4789-a012-3456789abc03',
      source_id: 'a4a5367d-c001-55c1-b041-01e5048391a2',
      engine: 'airflow',
      external_run_id: 'kb_ingest_2026-11-12T14:10:00+00:00',
      status: 'completed',
      download_from_endpoint_id: '6f536e3f-0b54-52df-a994-017bced3c5e4',
      store_to_endpoint_ids: [
        'b915d3e2-0d86-560d-b324-0f6e4098f8be',
        'd6f6c3ed-f423-5c27-8fa7-aa4903a56dc0',
      ],
      tech_stack_endpoint_ids: [
        '878f0a3b-007a-5f3c-8e7b-46d87a8d917b',
        '6defc77e-cdec-54f0-80b5-06f56c51d7c5',
      ],
      started_at: '2026-11-12T14:10:05Z',
      finished_at: '2026-11-12T14:11:22Z',
      created_on: '2026-11-12T14:10:00Z',
      updated_on: '2026-11-12T14:11:22Z',
      detail: 'Wikipedia microservices fetch + Qdrant upsert.',
    },
  ];

  listKnowledgeSources(): Observable<AdminKnowledgeSource[]> {
    return of(this.sources).pipe(delay(120));
  }

  getKnowledgeSource(id: string): Observable<AdminKnowledgeSource> {
    return of(this.sources).pipe(
      delay(80),
      map((list) => {
        const row = list.find((r) => r.id === id);
        if (!row) throw new Error('not_found');
        return row;
      }),
    );
  }

  /** Ops history for a source — newest first. */
  listWfExecLogs(sourceId: string): Observable<WfExecLog[]> {
    const rows = this.wfLogs
      .filter((r) => r.source_id === sourceId)
      .slice()
      .sort((a, b) => b.created_on.localeCompare(a.created_on));
    return of(rows).pipe(delay(90));
  }

  getWfExecLog(id: string): Observable<WfExecLog> {
    return of(this.wfLogs).pipe(
      delay(70),
      map((list) => {
        const row = list.find((r) => r.id === id);
        if (!row) throw new Error('not_found');
        return row;
      }),
    );
  }

  /**
   * Queue download: creates wf_exec_log (queued), then admin_api would hand
   * the id to Airflow / future Step Functions for status callbacks.
   */
  downloadSource(sourceId: string): Observable<DownloadJobResponse> {
    const src = this.sources.find((r) => r.id === sourceId);
    if (!src) {
      return throwError(() => new Error('not_found'));
    }
    if (!src.store_to_endpoint_ids.length) {
      return throwError(() => new Error('no_store_targets'));
    }
    const now = new Date().toISOString();
    const log: WfExecLog = {
      id: crypto.randomUUID(),
      source_id: sourceId,
      engine: 'airflow',
      external_run_id: null,
      status: 'queued',
      download_from_endpoint_id: src.download_from_endpoint_id,
      store_to_endpoint_ids: [...src.store_to_endpoint_ids],
      tech_stack_endpoint_ids: [...src.tech_stack_endpoint_ids],
      started_at: null,
      finished_at: null,
      created_on: now,
      updated_on: now,
      detail: 'Created by Admin UI Download; waiting for DAG pickup.',
    };
    this.wfLogs.unshift(log);
    src.ingest_status = 'queued';

    return of({
      wf_exec_log_id: log.id,
      source_id: sourceId,
      status: 'queued' as const,
      download_from_endpoint_id: src.download_from_endpoint_id,
      store_to_endpoint_ids: [...src.store_to_endpoint_ids],
    }).pipe(delay(180));
  }
}
