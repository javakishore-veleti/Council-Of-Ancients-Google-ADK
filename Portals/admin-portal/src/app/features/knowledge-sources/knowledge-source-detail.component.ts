import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { AccordionModule } from 'primeng/accordion';
import { ButtonModule } from 'primeng/button';
import {
  APP_ENDPOINT_KIND_LABELS,
  AdminApiService,
  AdminKnowledgeSource,
  AppEndpoint,
  AppEndpointKind,
} from '../../core/services/admin-api.service';

@Component({
  selector: 'app-knowledge-source-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, AccordionModule, ButtonModule],
  templateUrl: './knowledge-source-detail.component.html',
  styleUrl: './knowledge-source-detail.component.scss',
})
export class KnowledgeSourceDetailComponent implements OnInit {
  private readonly api = inject(AdminApiService);
  private readonly route = inject(ActivatedRoute);

  readonly source = signal<AdminKnowledgeSource | null>(null);
  readonly downloadFrom = signal<AppEndpoint | null>(null);
  readonly storeTo = signal<AppEndpoint[]>([]);
  readonly techStack = signal<AppEndpoint[]>([]);
  readonly loading = signal(true);
  readonly busy = signal(false);
  readonly notice = signal('');
  readonly notFound = signal(false);

  readonly kindLabel = APP_ENDPOINT_KIND_LABELS;

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id') ?? '';
    this.load(id);
  }

  labelFor(kind: AppEndpointKind): string {
    return this.kindLabel[kind] ?? kind;
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
        const targets = job.store_to_endpoint_ids.length;
        this.notice.set(
          `Queued job ${job.job_id} — fetch from origin, store to ${targets} endpoint${targets === 1 ? '' : 's'}.`,
        );
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

  private load(id: string): void {
    if (!id) {
      this.notFound.set(true);
      this.loading.set(false);
      return;
    }
    this.loading.set(true);
    this.notFound.set(false);
    this.api.getKnowledgeSource(id).subscribe({
      next: (src) => {
        this.source.set(src);
        this.downloadFrom.set(
          src.download_from_endpoint_id
            ? this.api.resolveEndpoints([src.download_from_endpoint_id])[0] ?? null
            : null,
        );
        this.storeTo.set(this.api.resolveEndpoints(src.store_to_endpoint_ids));
        this.techStack.set(this.api.resolveEndpoints(src.tech_stack_endpoint_ids));
        this.loading.set(false);
      },
      error: () => {
        this.notFound.set(true);
        this.loading.set(false);
      },
    });
  }
}
