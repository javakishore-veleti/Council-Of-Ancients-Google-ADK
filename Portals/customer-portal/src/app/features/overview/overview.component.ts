import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { PreferencesService } from '../../core/services/preferences.service';

@Component({
  selector: 'app-overview',
  standalone: true,
  imports: [CommonModule, ButtonModule, CardModule],
  templateUrl: './overview.component.html',
  styleUrl: './overview.component.scss',
})
export class OverviewComponent {
  readonly prefs = inject(PreferencesService);
  private readonly router = inject(Router);

  openChamber(): void {
    this.prefs.setNav('chamber');
    void this.router.navigate(['/app', this.prefs.activePackId(), 'chamber']);
  }
}
