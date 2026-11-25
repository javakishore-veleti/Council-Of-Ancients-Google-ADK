import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

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
  provider: string;
  endpoint_url: string;
  resource: string;
  region?: string;
  status: AppEndpointStatus;
  notes?: string;
  created_on: string;
}

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
  /** Workflow used when Download is clicked. */
  workflow_id: string | null;
  meta?: Record<string, unknown>;
}

/** Open-ended engine; known values labeled in UI. */
export type WfEngine =
  | 'airflow'
  | 'step_functions'
  | 'emr'
  | 'spring_batch'
  | 'local'
  | 'other'
  | string;

export type WorkflowStatus = 'active' | 'draft' | 'disabled';

export interface Workflow {
  id: string;
  name: string;
  description?: string;
  engine: WfEngine;
  external_ref?: string | null;
  status: WorkflowStatus;
  meta?: Record<string, unknown>;
  created_on?: string;
  updated_on?: string;
}

export type WfExecStatus =
  | 'queued'
  | 'started'
  | 'running'
  | 'completed'
  | 'failed'
  | 'cancelled';

export interface WfExecConfigInput {
  key: string;
  value: string;
}

export interface WfExecConfigEndpoint {
  id: string;
  name: string;
  kind: AppEndpointKind;
  provider: string;
  endpoint_url: string;
  resource?: string;
  region?: string | null;
  status?: AppEndpointStatus;
  notes?: string | null;
}

export interface WfExecConfigJson {
  inputs?: WfExecConfigInput[];
  from_endpoints?: WfExecConfigEndpoint[];
  to_endpoints?: WfExecConfigEndpoint[];
}

export interface WfExecLog {
  id: string;
  source_id: string;
  wf_id: string | null;
  engine: WfEngine;
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
  detail?: string;
  exec_config_json?: WfExecConfigJson;
}

export interface DownloadJobResponse {
  wf_exec_log_id: string;
  source_id: string;
  wf_id: string | null;
  status: 'queued';
  download_from_endpoint_id: string | null;
  store_to_endpoint_ids: string[];
}

export const WORKFLOW_ENGINE_LABELS: Record<string, string> = {
  airflow: 'Airflow',
  step_functions: 'AWS Step Functions',
  emr: 'AWS EMR',
  spring_batch: 'Spring Batch',
  local: 'Local',
  other: 'Other',
};

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
 * Admin UI talks ONLY to coa_admin_api (:8094 via /admin-api proxy).
 * All methods hit Postgres-backed routes — no fixtures.
 */
@Injectable({ providedIn: 'root' })
export class AdminApiService {
  private readonly http = inject(HttpClient);
  private readonly base = '/admin-api';
  private readonly endpointCache = new Map<string, AppEndpoint>();

  listAppEndpoints(): Observable<AppEndpoint[]> {
    return this.http.get<AppEndpoint[]>(`${this.base}/v1/app-endpoints`).pipe(
      tap((list) => {
        this.endpointCache.clear();
        for (const ep of list) {
          this.endpointCache.set(ep.id, ep);
        }
      }),
    );
  }

  getAppEndpoint(id: string): Observable<AppEndpoint> {
    return this.http.get<AppEndpoint>(`${this.base}/v1/app-endpoints/${id}`).pipe(
      tap((ep) => this.endpointCache.set(ep.id, ep)),
    );
  }

  /** Resolve from cache (call listAppEndpoints / getAppEndpoint first). */
  resolveEndpoints(ids: string[]): AppEndpoint[] {
    return ids
      .map((id) => this.endpointCache.get(id))
      .filter((e): e is AppEndpoint => !!e);
  }

  listWorkflows(): Observable<Workflow[]> {
    return this.http.get<Workflow[]>(`${this.base}/v1/workflows`);
  }

  getWorkflow(id: string): Observable<Workflow> {
    return this.http.get<Workflow>(`${this.base}/v1/workflows/${id}`);
  }

  listKnowledgeSources(): Observable<AdminKnowledgeSource[]> {
    return this.http.get<AdminKnowledgeSource[]>(`${this.base}/v1/knowledge/sources`);
  }

  getKnowledgeSource(id: string): Observable<AdminKnowledgeSource> {
    return this.http.get<AdminKnowledgeSource>(`${this.base}/v1/knowledge/sources/${id}`);
  }

  listWfExecLogs(sourceId: string): Observable<WfExecLog[]> {
    return this.http.get<WfExecLog[]>(
      `${this.base}/v1/knowledge/sources/${sourceId}/wf-exec-logs`,
    );
  }

  getWfExecLog(id: string): Observable<WfExecLog> {
    return this.http.get<WfExecLog>(`${this.base}/v1/wf-exec-logs/${id}`);
  }

  downloadSource(sourceId: string): Observable<DownloadJobResponse> {
    return this.http.post<DownloadJobResponse>(
      `${this.base}/v1/knowledge/sources/${sourceId}/download`,
      {},
    );
  }
}
