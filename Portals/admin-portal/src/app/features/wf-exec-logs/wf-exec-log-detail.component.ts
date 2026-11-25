import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { AccordionModule } from 'primeng/accordion';
import { TableModule } from 'primeng/table';
import {
  APP_ENDPOINT_KIND_LABELS,
  AdminApiService,
  AppEndpoint,
  AppEndpointKind,
  WfExecConfigEndpoint,
  WfExecConfigInput,
  WfExecLog,
} from '../../core/services/admin-api.service';

@Component({
  selector: 'app-wf-exec-log-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, AccordionModule, TableModule],
  templateUrl: './wf-exec-log-detail.component.html',
  styleUrl: './wf-exec-log-detail.component.scss',
})
export class WfExecLogDetailComponent implements OnInit {
  private readonly api = inject(AdminApiService);
  private readonly route = inject(ActivatedRoute);

  readonly log = signal<WfExecLog | null>(null);
  readonly inputs = signal<WfExecConfigInput[]>([]);
  readonly fromEndpoints = signal<WfExecConfigEndpoint[]>([]);
  readonly toEndpoints = signal<WfExecConfigEndpoint[]>([]);
  readonly loading = signal(true);
  readonly notFound = signal(false);

  readonly kindLabel = APP_ENDPOINT_KIND_LABELS;
  readonly pageSize = 10;
  readonly pageSizeOptions = [10, 25, 50];

  readonly fromCount = computed(() => this.fromEndpoints().length);
  readonly toCount = computed(() => this.toEndpoints().length);

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id') ?? '';
    if (!id) {
      this.notFound.set(true);
      this.loading.set(false);
      return;
    }
    this.api.listAppEndpoints().subscribe({
      next: () => {
        this.api.getWfExecLog(id).subscribe({
          next: (row) => this.applyRow(row),
          error: () => {
            this.notFound.set(true);
            this.loading.set(false);
          },
        });
      },
      error: () => {
        this.api.getWfExecLog(id).subscribe({
          next: (row) => this.applyRow(row),
          error: () => {
            this.notFound.set(true);
            this.loading.set(false);
          },
        });
      },
    });
  }

  private applyRow(row: WfExecLog): void {
    this.log.set(row);
    const cfg = row.exec_config_json ?? {};
    this.inputs.set(Array.isArray(cfg.inputs) ? cfg.inputs : []);

    const fromSnap = Array.isArray(cfg.from_endpoints) ? cfg.from_endpoints : [];
    const toSnap = Array.isArray(cfg.to_endpoints) ? cfg.to_endpoints : [];

    if (fromSnap.length || toSnap.length) {
      this.fromEndpoints.set(fromSnap);
      this.toEndpoints.set(toSnap);
    } else {
      this.fromEndpoints.set(this.fallbackFrom(row));
      this.toEndpoints.set(this.fallbackTo(row));
    }
    this.loading.set(false);
  }

  private fallbackFrom(row: WfExecLog): WfExecConfigEndpoint[] {
    if (!row.download_from_endpoint_id) return [];
    const ep = this.api.resolveEndpoints([row.download_from_endpoint_id])[0];
    return ep ? [this.toConfigEp(ep)] : [];
  }

  private fallbackTo(row: WfExecLog): WfExecConfigEndpoint[] {
    return this.api.resolveEndpoints(row.store_to_endpoint_ids).map((ep) => this.toConfigEp(ep));
  }

  private toConfigEp(ep: AppEndpoint): WfExecConfigEndpoint {
    return {
      id: ep.id,
      name: ep.name,
      kind: ep.kind,
      provider: ep.provider,
      endpoint_url: ep.endpoint_url,
      resource: ep.resource,
      region: ep.region,
      status: ep.status,
      notes: ep.notes,
    };
  }

  labelFor(kind: AppEndpointKind | string): string {
    return this.kindLabel[kind as AppEndpointKind] ?? String(kind);
  }

  sourceBackLink(): string[] {
    const sid = this.log()?.source_id;
    return sid ? ['/knowledge/sources', sid] : ['/knowledge/sources'];
  }
}
