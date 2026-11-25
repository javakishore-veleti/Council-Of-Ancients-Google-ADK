import { Component, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { PreferencesService } from '../../core/services/preferences.service';
import { ChatProject } from '../../core/models/pack';

@Component({
  selector: 'app-sessions',
  standalone: true,
  imports: [CommonModule, FormsModule, TableModule, ButtonModule, InputTextModule],
  templateUrl: './sessions.component.html',
  styleUrl: './sessions.component.scss',
})
export class SessionsComponent {
  readonly prefs = inject(PreferencesService);
  private readonly router = inject(Router);

  /** '' means all sections; otherwise filter to one section id. */
  readonly filterSectionId = signal<string>(this.prefs.lastContentSectionId());
  readonly query = signal('');
  readonly pageSize = 10;

  readonly filteredProjects = computed(() => {
    const filter = this.filterSectionId();
    const q = this.query().trim().toLowerCase();
    let list = filter
      ? this.prefs.projectsForSection(filter)
      : this.prefs.projectList();
    if (q) {
      list = list.filter(
        (p: ChatProject) =>
          p.title.toLowerCase().includes(q) ||
          this.sectionName(p.sectionId).toLowerCase().includes(q),
      );
    }
    return list;
  });

  readonly filterLabel = computed(() => {
    const filter = this.filterSectionId();
    return filter ? this.prefs.sectionLabel(filter) : 'All sections';
  });

  sectionName(sectionId: string): string {
    return this.prefs.sectionLabel(sectionId || 'overview');
  }

  setFilter(sectionId: string): void {
    this.filterSectionId.set(sectionId);
    if (sectionId) {
      this.prefs.lastContentSectionId.set(sectionId);
    }
  }

  onQuery(value: string): void {
    this.query.set(value);
  }

  open(id: string): void {
    const project = this.prefs.projectList().find((p) => p.id === id);
    if (project?.sectionId) {
      this.prefs.setNav(project.sectionId);
    }
    this.prefs.selectProject(id);
    void this.router.navigate(['/app', this.prefs.activePackId(), 'chamber']);
  }

  create(): void {
    const filter = this.filterSectionId();
    if (filter) {
      this.prefs.setNav(filter);
    } else {
      this.prefs.setNav(this.prefs.lastContentSectionId());
    }
    this.prefs.createProject();
    void this.router.navigate(['/app', this.prefs.activePackId(), 'chamber']);
  }
}
