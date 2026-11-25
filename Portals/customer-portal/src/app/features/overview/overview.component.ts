import { Component, computed, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { PreferencesService } from '../../core/services/preferences.service';

const SEAT_FOCUS: Record<string, string> = {
  seat_vision: 'Where the venture is going and what must stay true.',
  seat_capital: 'Funding, runway, and returns under real constraints.',
  seat_execution: 'Shipping, sequencing, and operational reality.',
  seat_people: 'Roles, trust, and how teams actually work.',
  seat_culture: 'Norms, incentives, and the story people tell.',
  seat_judgment: 'One-way doors, reversibility, and decision quality.',
  seat_reliability: 'SLOs, failure modes, and what stays up.',
  seat_capacity: 'Load, cost, and headroom before the cliff.',
  seat_response: 'Incidents, recovery, and learning from outages.',
  seat_training: 'Programming, progression, and sustainable effort.',
  seat_nutrition: 'Fueling for performance without dogma.',
  seat_recovery: 'Sleep, stress, and coming back stronger.',
  seat_patterns: 'Catalog patterns, trade-offs, and when to reach for each.',
  seat_architecture: 'System shape, boundaries, and evolution paths.',
  seat_data: 'Models, consistency, storage, and access patterns.',
};

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

  readonly flowSteps = [
    {
      n: '01',
      icon: 'bi bi-chat-left-quote',
      title: 'You bring the question',
      body: 'A dilemma, design choice, or trade-off — not a quiz. The chamber is for judgment under uncertainty.',
    },
    {
      n: '02',
      icon: 'bi bi-people',
      title: 'Seats deliberate',
      body: 'Each counselor answers from their seat. Disagreement is useful; it surfaces the real tensions.',
    },
    {
      n: '03',
      icon: 'bi bi-signpost-split',
      title: 'Facilitator synthesizes',
      body: 'A clear recommendation, the trade-offs that matter, and what to watch if you choose otherwise.',
    },
  ];

  readonly seats = computed(() => {
    const pack = this.prefs.activePack();
    const raw = pack.optionsByNav['seats'] ?? pack.optionsByNav['chamber'] ?? [];
    return raw
      .filter((o) => o.id.startsWith('seat_'))
      .map((o) => {
        const name = o.label.replace(/^Seat:\s*/i, '').trim();
        return {
          id: o.id,
          name,
          initial: name.slice(0, 1).toUpperCase(),
          focus: SEAT_FOCUS[o.id] ?? `Counsel from the ${name} seat in this topic.`,
        };
      });
  });

  readonly pathways = computed(() => {
    const skip = new Set(['overview', 'chamber', 'sessions', 'settings', 'knowledge', 'seats', 'disclaimer']);
    return this.prefs.activePack().nav.filter((n) => !skip.has(n.id) && !n.disabledUntilKb);
  });

  openChamber(): void {
    this.prefs.setNav('chamber');
    void this.router.navigate(['/app', this.prefs.activePackId(), 'chamber']);
  }

  openSessions(): void {
    this.prefs.setNav('sessions');
    void this.router.navigate(['/app', this.prefs.activePackId(), 'sessions']);
  }

  openSeat(seatId: string): void {
    this.prefs.setNav('chamber');
    this.prefs.toggleOption(seatId);
    void this.router.navigate(['/app', this.prefs.activePackId(), 'chamber']);
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
