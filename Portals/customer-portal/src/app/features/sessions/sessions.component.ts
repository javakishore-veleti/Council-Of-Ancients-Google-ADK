import { Component, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { PreferencesService } from '../../core/services/preferences.service';

@Component({
  selector: 'app-sessions',
  standalone: true,
  imports: [CommonModule, TableModule, ButtonModule],
  templateUrl: './sessions.component.html',
  styleUrl: './sessions.component.scss',
})
export class SessionsComponent {
  readonly prefs = inject(PreferencesService);
  private readonly router = inject(Router);

  /** '' means all sections; otherwise filter to one section id. */
  readonly filterSectionId = signal<string>(this.prefs.lastContentSectionId());

  readonly filteredProjects = computed(() => {
    const filter = this.filterSectionId();
    if (!filter) {
      return this.prefs.projectList();
    }
    return this.prefs.projectsForSection(filter);
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
