import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { AccordionModule } from 'primeng/accordion';
import { ButtonModule } from 'primeng/button';
import { TableModule } from 'primeng/table';
import { InputTextModule } from 'primeng/inputtext';
import { SelectModule } from 'primeng/select';
import { forkJoin, of } from 'rxjs';
import { catchError, switchMap } from 'rxjs/operators';
import {
  APP_ENDPOINT_KIND_LABELS,
  AdminApiService,
  AdminKnowledgeSource,
  AppEndpoint,
  AppEndpointKind,
  WfEngine,
  WfExecLog,
  WfExecStatus,
  Workflow,
} from '../../core/services/admin-api.service';

@Component({
  selector: 'app-knowledge-source-detail',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
    AccordionModule,
    ButtonModule,
    TableModule,
    InputTextModule,
    SelectModule,
  ],
  templateUrl: './knowledge-source-detail.component.html',
  styleUrl: './knowledge-source-detail.component.scss',
})
export class KnowledgeSourceDetailComponent implements OnInit {
  private readonly api = inject(AdminApiService);
  private readonly route = inject(ActivatedRoute);

  readonly source = signal<AdminKnowledgeSource | null>(null);
  readonly workflow = signal<Workflow | null>(null);
  readonly downloadFrom = signal<AppEndpoint | null>(null);
  readonly storeTo = signal<AppEndpoint[]>([]);
  readonly techStack = signal<AppEndpoint[]>([]);
  readonly wfLogs = signal<WfExecLog[]>([]);
  readonly loading = signal(true);
  readonly busy = signal(false);
  readonly notice = signal('');
  readonly notFound = signal(false);

  readonly opsCriteriaOpen = signal(true);
  readonly criteriaStatus = signal<WfExecStatus | ''>('');
  readonly criteriaEngine = signal<WfEngine | ''>('');
  readonly criteriaFrom = signal('');
  readonly criteriaExternal = signal('');

  readonly colStatus = signal('');
  readonly colEngine = signal('');
  readonly colFrom = signal('');
  readonly colExternal = signal('');
  readonly colDetail = signal('');

  readonly pageSize = 10;
  readonly pageSizeOptions = [5, 10, 25, 50];

  readonly kindLabel = APP_ENDPOINT_KIND_LABELS;

  readonly statusOptions: { label: string; value: WfExecStatus | '' }[] = [
    { label: 'Any status', value: '' },
    { label: 'queued', value: 'queued' },
    { label: 'started', value: 'started' },
    { label: 'running', value: 'running' },
    { label: 'completed', value: 'completed' },
    { label: 'failed', value: 'failed' },
    { label: 'cancelled', value: 'cancelled' },
  ];

  readonly engineOptions: { label: string; value: WfEngine | '' }[] = [
    { label: 'Any engine', value: '' },
    { label: 'airflow', value: 'airflow' },
    { label: 'step_functions', value: 'step_functions' },
    { label: 'local', value: 'local' },
  ];

  readonly filteredLogs = computed(() => {
    const cStatus = this.criteriaStatus();
    const cEngine = this.criteriaEngine();
    const cFrom = this.criteriaFrom().trim().toLowerCase();
    const cExt = this.criteriaExternal().trim().toLowerCase();
    const hStatus = this.colStatus().trim().toLowerCase();
    const hEngine = this.colEngine().trim().toLowerCase();
    const hFrom = this.colFrom().trim().toLowerCase();
    const hExt = this.colExternal().trim().toLowerCase();
    const hDetail = this.colDetail().trim().toLowerCase();

    return this.wfLogs().filter((r) => {
      if (cStatus && r.status !== cStatus) return false;
      if (cEngine && r.engine !== cEngine) return false;
      const fromName = this.endpointName(r.download_from_endpoint_id).toLowerCase();
      if (cFrom && !fromName.includes(cFrom)) return false;
      if (cExt && !(r.external_run_id ?? '').toLowerCase().includes(cExt)) return false;
      if (hStatus && !r.status.toLowerCase().includes(hStatus)) return false;
      if (hEngine && !r.engine.toLowerCase().includes(hEngine)) return false;
      if (hFrom && !fromName.includes(hFrom)) return false;
      if (hExt && !(r.external_run_id ?? '').toLowerCase().includes(hExt)) return false;
      const detailBlob = `${r.detail ?? ''} ${r.error_message ?? ''}`.toLowerCase();
      if (hDetail && !detailBlob.includes(hDetail)) return false;
      return true;
    });
  });

  readonly opsCriteriaSummary = computed(() => {
    const parts: string[] = [];
    if (this.criteriaStatus()) parts.push(`status ${this.criteriaStatus()}`);
    if (this.criteriaEngine()) parts.push(`engine ${this.criteriaEngine()}`);
    if (this.criteriaFrom().trim()) parts.push(`from “${this.criteriaFrom().trim()}”`);
    if (this.criteriaExternal().trim()) parts.push(`run “${this.criteriaExternal().trim()}”`);
    return parts.length ? parts.join(' · ') : 'No criteria — all executions';
  });

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id') ?? '';
    this.load(id);
  }

  labelFor(kind: AppEndpointKind): string {
    return this.kindLabel[kind] ?? kind;
  }

  endpointName(id: string | null): string {
    if (!id) return '—';
    return this.api.resolveEndpoints([id])[0]?.name ?? id.slice(0, 8);
  }

  storeSummary(ids: string[]): string {
    if (!ids.length) return '—';
    return `${ids.length} endpoint${ids.length === 1 ? '' : 's'}`;
  }

  toggleOpsCriteria(): void {
    this.opsCriteriaOpen.update((v) => !v);
  }

  clearOpsCriteria(): void {
    this.criteriaStatus.set('');
    this.criteriaEngine.set('');
    this.criteriaFrom.set('');
    this.criteriaExternal.set('');
    this.colStatus.set('');
    this.colEngine.set('');
    this.colFrom.set('');
    this.colExternal.set('');
    this.colDetail.set('');
  }

  reload(): void {
    const id = this.source()?.id ?? this.route.snapshot.paramMap.get('id') ?? '';
    this.load(id);
  }

  download(): void {
    const src = this.source();
    if (!src) return;
    this.busy.set(true);
    this.notice.set('');
    this.api.downloadSource(src.id).subscribe({
      next: (job) => {
        this.busy.set(false);
        this.source.update((s) => (s ? { ...s, ingest_status: 'queued' } : s));
        this.notice.set(`Download queued (${job.wf_exec_log_id.slice(0, 8)}…).`);
        this.refreshLogs(src.id);
      },
      error: (err) => {
        this.busy.set(false);
        const msg =
          err?.message === 'no_store_targets'
            ? 'No store-to endpoints mapped — add at least one before downloading.'
            : 'Failed to queue download via Admin API.';
        this.notice.set(msg);
      },
    });
  }

  private refreshLogs(sourceId: string): void {
    this.api.listWfExecLogs(sourceId).subscribe({
      next: (logs) => this.wfLogs.set(logs),
    });
  }

  private load(id: string): void {
    if (!id) {
      this.notFound.set(true);
      this.loading.set(false);
      return;
    }
    this.loading.set(true);
    this.notFound.set(false);
    forkJoin({
      endpoints: this.api.listAppEndpoints(),
      src: this.api.getKnowledgeSource(id),
    })
      .pipe(
        switchMap(({ src }) =>
          forkJoin({
            src: of(src),
            wf: src.workflow_id
              ? this.api.getWorkflow(src.workflow_id).pipe(catchError(() => of(null)))
              : of(null),
          }),
        ),
      )
      .subscribe({
        next: ({ src, wf }) => {
          this.source.set(src);
          this.workflow.set(wf);
          this.downloadFrom.set(
            src.download_from_endpoint_id
              ? this.api.resolveEndpoints([src.download_from_endpoint_id])[0] ?? null
              : null,
          );
          this.storeTo.set(this.api.resolveEndpoints(src.store_to_endpoint_ids));
          this.techStack.set(this.api.resolveEndpoints(src.tech_stack_endpoint_ids));
          this.refreshLogs(src.id);
          this.loading.set(false);
        },
        error: () => {
          this.notFound.set(true);
          this.loading.set(false);
        },
      });
  }
}
