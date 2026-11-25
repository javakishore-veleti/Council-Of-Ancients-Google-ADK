import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import {
  AdminApiService,
  AdminKnowledgeSource,
} from '../../core/services/admin-api.service';

@Component({
  selector: 'app-knowledge-sources',
  standalone: true,
  imports: [CommonModule, FormsModule, TableModule, ButtonModule, InputTextModule],
  templateUrl: './knowledge-sources.component.html',
  styleUrl: './knowledge-sources.component.scss',
})
export class KnowledgeSourcesComponent implements OnInit {
  private readonly api = inject(AdminApiService);

  readonly rows = signal<AdminKnowledgeSource[]>([]);
  readonly loading = signal(true);
  readonly busyId = signal<string | null>(null);
  readonly notice = signal<string>('');
  query = '';

  ngOnInit(): void {
    this.reload();
  }

  reload(): void {
    this.loading.set(true);
    this.api.listKnowledgeSources().subscribe({
      next: (list) => {
        this.rows.set(list);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.notice.set('Admin API unreachable — showing nothing until coa_admin_api is up.');
      },
    });
  }

  filtered(): AdminKnowledgeSource[] {
    const q = this.query.trim().toLowerCase();
    if (!q) {
      return this.rows();
    }
    return this.rows().filter(
      (r) =>
        r.name.toLowerCase().includes(q) ||
        r.category_name.toLowerCase().includes(q) ||
        r.source_key.toLowerCase().includes(q),
    );
  }

  download(row: AdminKnowledgeSource): void {
    this.busyId.set(row.id);
    this.notice.set('');
    this.api.downloadSource(row.id).subscribe({
      next: (job) => {
        this.busyId.set(null);
        this.rows.update((list) =>
          list.map((r) => (r.id === row.id ? { ...r, status: 'queued' } : r)),
        );
        this.notice.set(
          `Queued ${row.name} — job ${job.job_id}. Admin API will call Knowledge API; DAG reports started/completed.`,
        );
      },
      error: () => {
        this.busyId.set(null);
        this.notice.set('Failed to queue download via Admin API.');
      },
    });
  }
}
