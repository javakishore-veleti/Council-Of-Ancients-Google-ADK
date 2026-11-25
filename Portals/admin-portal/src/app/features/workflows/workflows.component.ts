import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { SelectModule } from 'primeng/select';
import {
  AdminApiService,
  WORKFLOW_ENGINE_LABELS,
  Workflow,
  WorkflowStatus,
} from '../../core/services/admin-api.service';

@Component({
  selector: 'app-workflows',
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
  templateUrl: './workflows.component.html',
  styleUrl: './workflows.component.scss',
})
export class WorkflowsComponent implements OnInit {
  private readonly api = inject(AdminApiService);

  readonly rows = signal<Workflow[]>([]);
  readonly loading = signal(true);
  readonly criteriaOpen = signal(true);
  readonly criteriaName = signal('');
  readonly criteriaEngine = signal('');
  readonly criteriaStatus = signal<WorkflowStatus | ''>('');
  readonly colName = signal('');
  readonly colEngine = signal('');
  readonly colExternal = signal('');

  readonly pageSize = 10;
  readonly pageSizeOptions = [5, 10, 25, 50];
  readonly engineLabel = WORKFLOW_ENGINE_LABELS;

  readonly engineOptions = computed(() => {
    const engines = new Set<string>(Object.keys(WORKFLOW_ENGINE_LABELS));
    for (const r of this.rows()) {
      if (r.engine) engines.add(r.engine);
    }
    return [
      { label: 'Any engine', value: '' as const },
      ...[...engines].sort().map((e) => ({
        label: WORKFLOW_ENGINE_LABELS[e] || e,
        value: e,
      })),
    ];
  });

  readonly statusOptions: { label: string; value: WorkflowStatus | '' }[] = [
    { label: 'Any status', value: '' },
    { label: 'active', value: 'active' },
    { label: 'draft', value: 'draft' },
    { label: 'disabled', value: 'disabled' },
  ];

  readonly filtered = computed(() => {
    const cName = this.criteriaName().trim().toLowerCase();
    const cEngine = this.criteriaEngine();
    const cStatus = this.criteriaStatus();
    const hName = this.colName().trim().toLowerCase();
    const hEngine = this.colEngine().trim().toLowerCase();
    const hExt = this.colExternal().trim().toLowerCase();

    return this.rows().filter((r) => {
      if (cName && !r.name.toLowerCase().includes(cName)) return false;
      if (cEngine && r.engine !== cEngine) return false;
      if (cStatus && r.status !== cStatus) return false;
      if (hName && !r.name.toLowerCase().includes(hName)) return false;
      const engLabel = `${r.engine} ${this.labelFor(r.engine)}`.toLowerCase();
      if (hEngine && !engLabel.includes(hEngine)) return false;
      if (hExt && !(r.external_ref || '').toLowerCase().includes(hExt)) return false;
      return true;
    });
  });

  readonly criteriaSummary = computed(() => {
    const parts: string[] = [];
    if (this.criteriaName().trim()) parts.push(`name “${this.criteriaName().trim()}”`);
    if (this.criteriaEngine()) parts.push(this.labelFor(this.criteriaEngine()));
    if (this.criteriaStatus()) parts.push(`status ${this.criteriaStatus()}`);
    return parts.length ? parts.join(' · ') : 'No criteria — all workflows';
  });

  ngOnInit(): void {
    this.reload();
  }

  labelFor(engine: string): string {
    return this.engineLabel[engine] || engine;
  }

  toggleCriteria(): void {
    this.criteriaOpen.update((v) => !v);
  }

  clearCriteria(): void {
    this.criteriaName.set('');
    this.criteriaEngine.set('');
    this.criteriaStatus.set('');
  }

  reload(): void {
    this.loading.set(true);
    this.api.listWorkflows().subscribe({
      next: (list) => {
        this.rows.set(list);
        this.loading.set(false);
      },
      error: () => {
        this.rows.set([]);
        this.loading.set(false);
      },
    });
  }
}
