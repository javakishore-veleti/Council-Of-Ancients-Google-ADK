import { Component, computed, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { PreferencesService } from '../../core/services/preferences.service';

@Component({
  selector: 'app-overview',
  standalone: true,
  imports: [CommonModule, ButtonModule],
  templateUrl: './overview.component.html',
  styleUrl: './overview.component.scss',
})
export class OverviewComponent {
  readonly prefs = inject(PreferencesService);
  private readonly router = inject(Router);

  readonly flowSteps = computed(() => {
    const [q, seats, synth] = this.prefs.activePack().howItWorksSteps;
    return [
      {
        n: '01',
        icon: 'bi bi-chat-left-quote',
        title: 'You bring the question',
        body: q,
      },
      {
        n: '02',
        icon: 'bi bi-people',
        title: 'Seats deliberate',
        body: seats,
      },
      {
        n: '03',
        icon: 'bi bi-signpost-split',
        title: 'Facilitator synthesizes',
        body: synth,
      },
    ];
  });

  readonly pathways = computed(() => {
    const skip = new Set(['overview', 'sessions', 'settings', 'knowledge', 'seats', 'disclaimer']);
    return this.prefs.activePack().nav.filter((n) => !skip.has(n.id) && !n.disabledUntilKb);
  });

  openChamber(): void {
    // Overview never owns chats — land on a real section, then open the chamber.
    this.prefs.openSectionChamber();
    void this.router.navigate(['/app', this.prefs.activePackId(), 'chamber']);
  }

  openSessions(): void {
    this.prefs.setNav('sessions');
    void this.router.navigate(['/app', this.prefs.activePackId(), 'sessions']);
  }

  /** Keep the final phrase on one line so titles do not orphan the last word. */
  displayTitle(): string {
    const label = this.prefs.activePack().label.trim();
    const amp = label.lastIndexOf(' & ');
    if (amp > 0) {
      return label.slice(0, amp) + ' &\u00A0' + label.slice(amp + 3);
    }
    const space = label.lastIndexOf(' ');
    if (space > 0) {
      return label.slice(0, space) + '\u00A0' + label.slice(space + 1);
    }
    return label;
  }

  openPath(navId: string, route: string): void {
    this.prefs.setNav(navId);
    void this.router.navigate(['/app', this.prefs.activePackId(), route]);
  }
}
