import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { SelectModule } from 'primeng/select';
import {
  APP_ENDPOINT_KIND_LABELS,
  AdminApiService,
  AppEndpoint,
  AppEndpointKind,
  AppEndpointStatus,
} from '../../core/services/admin-api.service';

@Component({
  selector: 'app-app-endpoints',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
    TableModule,
    ButtonModule,
    InputTextModule,
    SelectModule,
  ],
  templateUrl: './app-endpoints.component.html',
  styleUrl: './app-endpoints.component.scss',
})
export class AppEndpointsComponent implements OnInit {
  private readonly api = inject(AdminApiService);

  readonly rows = signal<AppEndpoint[]>([]);
  readonly loading = signal(true);
  readonly criteriaOpen = signal(true);
  readonly criteriaName = signal('');
  readonly criteriaKind = signal<AppEndpointKind | ''>('');
  readonly criteriaStatus = signal<AppEndpointStatus | ''>('');
  readonly colName = signal('');
  readonly colProvider = signal('');
  readonly colKind = signal('');

  readonly pageSize = 10;
  readonly pageSizeOptions = [5, 10, 25, 50];
  readonly kindLabel = APP_ENDPOINT_KIND_LABELS;

  readonly kindOptions = computed(() => [
    { label: 'Any kind', value: '' as const },
    ...((Object.keys(APP_ENDPOINT_KIND_LABELS) as AppEndpointKind[]).map((k) => ({
      label: APP_ENDPOINT_KIND_LABELS[k],
      value: k,
    }))),
  ]);

  readonly statusOptions: { label: string; value: AppEndpointStatus | '' }[] = [
    { label: 'Any status', value: '' },
    { label: 'active', value: 'active' },
    { label: 'draft', value: 'draft' },
    { label: 'disabled', value: 'disabled' },
  ];

  readonly filtered = computed(() => {
    const cName = this.criteriaName().trim().toLowerCase();
    const cKind = this.criteriaKind();
    const cStatus = this.criteriaStatus();
    const hName = this.colName().trim().toLowerCase();
    const hProv = this.colProvider().trim().toLowerCase();
    const hKind = this.colKind().trim().toLowerCase();

    return this.rows().filter((r) => {
      if (cName && !r.name.toLowerCase().includes(cName)) return false;
      if (cKind && r.kind !== cKind) return false;
      if (cStatus && r.status !== cStatus) return false;
      if (hName && !r.name.toLowerCase().includes(hName)) return false;
      if (hProv && !r.provider.toLowerCase().includes(hProv)) return false;
      if (hKind && !(`${r.kind} ${this.kindLabel[r.kind]}`).toLowerCase().includes(hKind)) return false;
      return true;
    });
  });

  readonly criteriaSummary = computed(() => {
    const parts: string[] = [];
    if (this.criteriaName().trim()) parts.push(`name “${this.criteriaName().trim()}”`);
    if (this.criteriaKind()) parts.push(this.kindLabel[this.criteriaKind() as AppEndpointKind]);
    if (this.criteriaStatus()) parts.push(`status ${this.criteriaStatus()}`);
    return parts.length ? parts.join(' · ') : 'No criteria — all App Endpoints';
  });

  ngOnInit(): void {
    this.reload();
  }

  labelFor(kind: AppEndpointKind): string {
    return this.kindLabel[kind];
  }

  toggleCriteria(): void {
    this.criteriaOpen.update((v) => !v);
  }

  clearCriteria(): void {
    this.criteriaName.set('');
    this.criteriaKind.set('');
    this.criteriaStatus.set('');
    this.colName.set('');
    this.colProvider.set('');
    this.colKind.set('');
  }

  reload(): void {
    this.loading.set(true);
    this.api.listAppEndpoints().subscribe({
      next: (list) => {
        this.rows.set(list);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }
}
