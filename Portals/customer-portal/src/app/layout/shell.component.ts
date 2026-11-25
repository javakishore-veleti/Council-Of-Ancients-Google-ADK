import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink, RouterOutlet } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { TooltipModule } from 'primeng/tooltip';
import { AvatarModule } from 'primeng/avatar';
import { TagModule } from 'primeng/tag';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faScaleBalanced } from '@fortawesome/free-solid-svg-icons';
import { PACKS } from '../core/data/packs.config';
import { PackId } from '../core/models/pack';
import { AuthService } from '../core/services/auth.service';
import { PreferencesService } from '../core/services/preferences.service';

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    RouterLink,
    ButtonModule,
    TooltipModule,
    AvatarModule,
    TagModule,
    FontAwesomeModule,
  ],
  templateUrl: './shell.component.html',
  styleUrl: './shell.component.scss',
})
export class ShellComponent {
  readonly packs = PACKS;
  readonly brandIcon = faScaleBalanced;
  readonly auth = inject(AuthService);
  readonly prefs = inject(PreferencesService);
  private readonly router = inject(Router);

  selectPack(id: PackId): void {
    this.prefs.setPack(id);
    void this.router.navigate(['/app', id, 'overview']);
  }

  goNav(route: string, navId: string): void {
    this.prefs.setNav(navId);
    void this.router.navigate(['/app', this.prefs.activePackId(), route]);
  }

  toggleSources(): void {
    this.prefs.sourcesOpen.update((v: boolean) => !v);
  }

  signOut(): void {
    this.auth.signout();
    void this.router.navigate(['/signin']);
  }
}
