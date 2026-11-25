import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import {
  APP_ENDPOINT_KIND_LABELS,
  AdminApiService,
  AppEndpoint,
  WfExecLog,
} from '../../core/services/admin-api.service';

/**
 * Reusable wf_exec_log detail. Open from source Ops history (or anywhere)
 * via /wf-exec-logs/:id — Back returns to the owning source detail.
 */
@Component({
  selector: 'app-wf-exec-log-detail',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './wf-exec-log-detail.component.html',
  styleUrl: './wf-exec-log-detail.component.scss',
})
export class WfExecLogDetailComponent implements OnInit {
  private readonly api = inject(AdminApiService);
  private readonly route = inject(ActivatedRoute);

  readonly log = signal<WfExecLog | null>(null);
  readonly downloadFrom = signal<AppEndpoint | null>(null);
  readonly storeTo = signal<AppEndpoint[]>([]);
  readonly techStack = signal<AppEndpoint[]>([]);
  readonly loading = signal(true);
  readonly notFound = signal(false);

  readonly kindLabel = APP_ENDPOINT_KIND_LABELS;

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id') ?? '';
    if (!id) {
      this.notFound.set(true);
      this.loading.set(false);
      return;
    }
    this.api.getWfExecLog(id).subscribe({
      next: (row) => {
        this.log.set(row);
        this.downloadFrom.set(
          row.download_from_endpoint_id
            ? this.api.resolveEndpoints([row.download_from_endpoint_id])[0] ?? null
            : null,
        );
        this.storeTo.set(this.api.resolveEndpoints(row.store_to_endpoint_ids));
        this.techStack.set(this.api.resolveEndpoints(row.tech_stack_endpoint_ids));
        this.loading.set(false);
      },
      error: () => {
        this.notFound.set(true);
        this.loading.set(false);
      },
    });
  }

  sourceBackLink(): string[] {
    const sid = this.log()?.source_id;
    return sid ? ['/knowledge/sources', sid] : ['/knowledge/sources'];
  }
}
