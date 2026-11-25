import { Component, inject } from '@angular/core';
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

  sectionName(sectionId: string): string {
    return this.prefs.sectionLabel(sectionId || 'overview');
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
    this.prefs.createProject();
    void this.router.navigate(['/app', this.prefs.activePackId(), 'chamber']);
  }
}
