import { Component, inject } from '@angular/core';
import { Router, RouterLink, RouterOutlet } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { TooltipModule } from 'primeng/tooltip';
import { AvatarModule } from 'primeng/avatar';
import { TagModule } from 'primeng/tag';
import { DialogModule } from 'primeng/dialog';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faGraduationCap, faScaleBalanced } from '@fortawesome/free-solid-svg-icons';
import { PACKS } from '../core/data/packs.config';
import { PackId } from '../core/models/pack';
import { AuthService } from '../core/services/auth.service';
import { PreferencesService } from '../core/services/preferences.service';

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [
    RouterOutlet,
    RouterLink,
    ButtonModule,
    TooltipModule,
    AvatarModule,
    TagModule,
    DialogModule,
    FontAwesomeModule,
  ],
  templateUrl: './shell.component.html',
  styleUrl: './shell.component.scss',
})
export class ShellComponent {
  readonly packs = PACKS;
  readonly brandIcon = faScaleBalanced;
  readonly professorHat = faGraduationCap;
  readonly councilMeaning =
    'A council is a group of people gathered or chosen for consultation, advice, deliberation, or decision-making, or an assembly/meeting held for those purposes.';

  councilMeaningVisible = false;

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

  openCouncilMeaning(event: Event): void {
    event.preventDefault();
    event.stopPropagation();
    this.councilMeaningVisible = true;
  }

  signOut(): void {
    this.auth.signout();
    void this.router.navigate(['/signin']);
  }
}
