import { Component, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { PreferencesService } from '../../core/services/preferences.service';
import { ChatProject } from '../../core/models/pack';

const SECTION_INTRO: Record<string, string> = {
  patterns:
    'Classic design pattern families and when to reach for each — foundations that predate cloud runbooks.',
  styles:
    'How the system is shaped: monolith, modular, microservices, event-driven, serverless — and the trade-offs.',
  data:
    'Models, consistency, schema evolution, and access patterns that keep data trustworthy under change.',
  cloud:
    'Infrastructure and platform choices: regions, Kubernetes vs serverless, and infrastructure as code.',
  databases:
    'Storage engines and topologies: OLTP vs OLAP, sharding, and CAP trade-offs in practice.',
  events:
    'Queues, streams, pub/sub, idempotency, and dead-letter paths for reliable event systems.',
  ai_systems:
    'Agent orchestration, hybrid RAG, evals, and guardrails for software that reasons with models.',
  seats:
    'Focus the chamber on one counselor seat, or keep the full council for a broader deliberation.',
  plan:
    'Stage the venture: idea, validate, launch — with a clear eye on risk before you spend runway.',
  fund:
    'Capital paths and use of funds: bootstrapped, debt, equity — matched to stage and constraints.',
  people:
    'Stakeholders, conflict, and how teams actually work across IC, manager, skip, and exec layers.',
  decisions:
    'Time horizon, reversible moves, and one-way doors — judgment under uncertainty.',
  reliability:
    'SLOs, error budgets, and what must stay up when the system is under stress.',
  incidents:
    'Incident response and postmortems that produce learning, not blame.',
  training:
    'Programming, progression, and sustainable effort — not a one-week hero plan.',
  recovery:
    'Fueling and recovery so training sticks — sleep, stress, and nutrition in balance.',
  knowledge:
    'Curated sources for this topic. Cited answers appear in the chamber when knowledge is ready.',
  disclaimer:
    'Fitness guidance here is educational, not medical advice. See a clinician for personal health decisions.',
};

@Component({
  selector: 'app-section-hub',
  standalone: true,
  imports: [CommonModule, FormsModule, ButtonModule, InputTextModule],
  templateUrl: './section-hub.component.html',
  styleUrl: './section-hub.component.scss',
})
export class SectionHubComponent {
  readonly prefs = inject(PreferencesService);
  private readonly router = inject(Router);

  /** Recent chats on the hub; full list + filters live on Sessions. */
  readonly initialVisible = 8;
  readonly chatQuery = signal('');

  readonly section = computed(() => {
    const pack = this.prefs.activePack();
    const navId = this.prefs.activeNavId();
    const item = pack.nav.find((n) => n.id === navId);
    return {
      id: navId,
      label: item?.label ?? navId,
      icon: item?.icon ?? 'bi-compass',
      intro: SECTION_INTRO[navId] ?? `Explore ${item?.label ?? navId} with the council for this topic.`,
    };
  });

  readonly options = computed(() => this.prefs.domainOptions());

  readonly matchedChats = computed(() => {
    const q = this.chatQuery().trim().toLowerCase();
    const list = this.prefs.sectionProjectList();
    if (!q) {
      return list;
    }
    return list.filter((p: ChatProject) => p.title.toLowerCase().includes(q));
  });

  readonly visibleChats = computed(() => {
    const matched = this.matchedChats();
    // Searching: show matches here. Otherwise: recent only — full list lives in Sessions.
    if (this.chatQuery().trim()) {
      return matched.slice(0, 20);
    }
    return matched.slice(0, this.initialVisible);
  });

  readonly chatTotal = computed(() => this.prefs.sectionProjectList().length);
  readonly matchCount = computed(() => this.matchedChats().length);
  readonly hiddenCount = computed(() => {
    if (this.chatQuery().trim()) {
      return Math.max(0, this.matchCount() - this.visibleChats().length);
    }
    return Math.max(0, this.chatTotal() - this.initialVisible);
  });

  onChatQuery(value: string): void {
    this.chatQuery.set(value);
  }

  /** Full listing with filters + pagination lives on Sessions. */
  browseAllSessions(): void {
    this.prefs.setNav('sessions');
    void this.router.navigate(['/app', this.prefs.activePackId(), 'sessions']);
  }

  openChamber(): void {
    this.prefs.openSectionChamber();
    void this.router.navigate(['/app', this.prefs.activePackId(), 'chamber']);
  }

  newChat(): void {
    this.prefs.createProject();
    void this.router.navigate(['/app', this.prefs.activePackId(), 'chamber']);
  }

  openChat(id: string): void {
    this.prefs.selectProject(id);
    void this.router.navigate(['/app', this.prefs.activePackId(), 'chamber']);
  }

  toggleOption(id: string): void {
    this.prefs.toggleOption(id);
  }

  isSelected(id: string): boolean {
    return this.prefs.selectedOptions().includes(id);
  }
}
