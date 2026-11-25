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

  open(id: string): void {
    this.prefs.selectProject(id);
    // Do not steal left-nav highlight — chamber is the canvas for the active section.
    void this.router.navigate(['/app', this.prefs.activePackId(), 'chamber']);
  }

  create(): void {
    this.prefs.createProject(`Session ${new Date().toLocaleString()}`);
    void this.router.navigate(['/app', this.prefs.activePackId(), 'chamber']);
  }
}
