import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { delay } from 'rxjs/operators';

/** Shape returned by coa_admin_api (proxies knowledge_source). */
export interface AdminKnowledgeSource {
  id: string;
  name: string;
  description?: string;
  citation_name: string;
  citation_desc?: string;
  category_code: string;
  category_name: string;
  url?: string;
  license?: string;
  status: 'active' | 'queued' | 'running' | 'fetched' | 'failed' | 'paused' | 'denied' | 'archived';
  source_key: string;
}

export interface DownloadJobResponse {
  job_id: string;
  source_id: string;
  status: 'queued';
}

/**
 * Admin UI talks ONLY to coa_admin_api.
 * Until that microservice is up, methods return local fixtures.
 */
@Injectable({ providedIn: 'root' })
export class AdminApiService {
  private readonly http = inject(HttpClient);
  private readonly base = '/admin-api';

  private readonly fixture: AdminKnowledgeSource[] = [
    {
      id: 'src-do-gof-hub',
      name: 'DigitalOcean GoF hub',
      description: 'Gang of Four patterns overview (CC BY-NC-SA 4.0) — personal RAG practice.',
      citation_name: 'DigitalOcean — GoF Design Patterns',
      citation_desc: 'Community tutorial overview of creational, structural, and behavioral patterns.',
      category_code: 'patterns',
      category_name: 'Patterns',
      url: 'https://www.digitalocean.com/community/tutorials/gangs-of-four-gof-design-patterns',
      license: 'CC-BY-NC-SA-4.0',
      status: 'active',
      source_key: 'do_gof_hub',
    },
    {
      id: 'src-wiki-microservices',
      name: 'Wikipedia Microservices',
      description: 'Open overview for Architecture styles chip: microservices.',
      citation_name: 'Wikipedia — Microservices',
      citation_desc: 'CC BY-SA encyclopedia article on the microservices style.',
      category_code: 'styles',
      category_name: 'Architecture styles',
      url: 'https://en.wikipedia.org/wiki/Microservices',
      license: 'CC-BY-SA-4.0',
      status: 'active',
      source_key: 'wiki_microservices',
    },
  ];

  listKnowledgeSources(): Observable<AdminKnowledgeSource[]> {
    // Preferred: this.http.get<AdminKnowledgeSource[]>(`${this.base}/v1/knowledge/sources`)
    return of(this.fixture).pipe(delay(120));
  }

  /** Queues download via Admin API → Knowledge API → DAG (async). */
  downloadSource(sourceId: string): Observable<DownloadJobResponse> {
    // Preferred: this.http.post<DownloadJobResponse>(`${this.base}/v1/knowledge/sources/${sourceId}/download`, {})
    return of({
      job_id: `job_${crypto.randomUUID().slice(0, 8)}`,
      source_id: sourceId,
      status: 'queued' as const,
    }).pipe(delay(180));
  }
}
