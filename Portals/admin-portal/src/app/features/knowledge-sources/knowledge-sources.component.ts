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
  AdminKnowledgeSource,
  IngestStatus,
} from '../../core/services/admin-api.service';

@Component({
  selector: 'app-knowledge-sources',
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
  templateUrl: './knowledge-sources.component.html',
  styleUrl: './knowledge-sources.component.scss',
})
export class KnowledgeSourcesComponent implements OnInit {
  private readonly api = inject(AdminApiService);

  readonly rows = signal<AdminKnowledgeSource[]>([]);
  readonly loading = signal(true);
  readonly notice = signal('');
  readonly criteriaOpen = signal(true);

  readonly criteriaName = signal('');
  readonly criteriaCategory = signal('');
  readonly criteriaSubcategory = signal('');
  readonly criteriaStatus = signal<IngestStatus | ''>('');

  readonly colName = signal('');
  readonly colCategory = signal('');
  readonly colSubcategory = signal('');
  readonly colStatus = signal('');

  readonly pageSize = 10;
  readonly pageSizeOptions = [5, 10, 25, 50];

  readonly statusOptions: { label: string; value: IngestStatus | '' }[] = [
    { label: 'Any status', value: '' },
    { label: 'active', value: 'active' },
    { label: 'queued', value: 'queued' },
    { label: 'running', value: 'running' },
    { label: 'fetched', value: 'fetched' },
    { label: 'failed', value: 'failed' },
    { label: 'paused', value: 'paused' },
    { label: 'denied', value: 'denied' },
    { label: 'archived', value: 'archived' },
  ];

  readonly categoryOptions = computed(() => {
    const names = [...new Set(this.rows().map((r) => r.category_name))].sort();
    return [{ label: 'Any category', value: '' }, ...names.map((n) => ({ label: n, value: n }))];
  });

  readonly subcategoryOptions = computed(() => {
    const cat = this.criteriaCategory();
    const names = [
      ...new Set(
        this.rows()
          .filter((r) => !cat || r.category_name === cat)
          .map((r) => r.subcategory_name),
      ),
    ].sort();
    return [{ label: 'Any subcategory', value: '' }, ...names.map((n) => ({ label: n, value: n }))];
  });

  readonly filtered = computed(() => {
    const list = this.rows();
    const cName = this.criteriaName().trim().toLowerCase();
    const cCat = this.criteriaCategory().trim().toLowerCase();
    const cSub = this.criteriaSubcategory().trim().toLowerCase();
    const cStatus = this.criteriaStatus();
    const hName = this.colName().trim().toLowerCase();
    const hCat = this.colCategory().trim().toLowerCase();
    const hSub = this.colSubcategory().trim().toLowerCase();
    const hStatus = this.colStatus().trim().toLowerCase();

    return list.filter((r) => {
      if (cName && !`${r.name} ${r.citation_name}`.toLowerCase().includes(cName)) return false;
      if (cCat && r.category_name.toLowerCase() !== cCat) return false;
      if (cSub && r.subcategory_name.toLowerCase() !== cSub) return false;
      if (cStatus && r.ingest_status !== cStatus) return false;
      if (hName && !`${r.name} ${r.citation_name}`.toLowerCase().includes(hName)) return false;
      if (hCat && !r.category_name.toLowerCase().includes(hCat)) return false;
      if (hSub && !r.subcategory_name.toLowerCase().includes(hSub)) return false;
      if (hStatus && !r.ingest_status.toLowerCase().includes(hStatus)) return false;
      return true;
    });
  });

  readonly criteriaSummary = computed(() => {
    const parts: string[] = [];
    if (this.criteriaName().trim()) parts.push(`name “${this.criteriaName().trim()}”`);
    if (this.criteriaCategory()) parts.push(`category ${this.criteriaCategory()}`);
    if (this.criteriaSubcategory()) parts.push(`sub ${this.criteriaSubcategory()}`);
    if (this.criteriaStatus()) parts.push(`status ${this.criteriaStatus()}`);
    if (!parts.length) return 'No criteria — showing all sources';
    return parts.join(' · ');
  });

  ngOnInit(): void {
    this.reload();
  }

  toggleCriteria(): void {
    this.criteriaOpen.update((v) => !v);
  }

  clearCriteria(): void {
    this.criteriaName.set('');
    this.criteriaCategory.set('');
    this.criteriaSubcategory.set('');
    this.criteriaStatus.set('');
    this.colName.set('');
    this.colCategory.set('');
    this.colSubcategory.set('');
    this.colStatus.set('');
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
}
