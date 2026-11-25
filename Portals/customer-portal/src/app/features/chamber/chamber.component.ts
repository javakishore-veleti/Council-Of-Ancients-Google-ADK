import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { TextareaModule } from 'primeng/textarea';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { SelectButtonModule } from 'primeng/selectbutton';
import { AuthService } from '../../core/services/auth.service';
import { PreferencesService } from '../../core/services/preferences.service';
import { CouncilApiService, DeliberateResponse } from '../../core/services/council-api.service';
import { ToggleSwitchModule } from 'primeng/toggleswitch';
import { CheckboxModule } from 'primeng/checkbox';

@Component({
  selector: 'app-chamber',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
    ButtonModule,
    TextareaModule,
    ProgressSpinnerModule,
    SelectButtonModule,
    ToggleSwitchModule,
    CheckboxModule,
  ],
  templateUrl: './chamber.component.html',
  styleUrl: './chamber.component.scss',
})
export class ChamberComponent implements OnInit {
  readonly prefs = inject(PreferencesService);
  readonly auth = inject(AuthService);
  private readonly council = inject(CouncilApiService);

  draft = '';
  renameDraft = '';
  readonly busy = signal(false);
  readonly renaming = signal(false);
  /** Criteria collapsed by default so chat history has room */
  readonly criteriaOpen = signal(false);

  readonly activeChatTitle = computed(
    () => this.prefs.activeProject()?.title ?? 'New chat',
  );

  toneOptions = [
    { label: 'Concise', value: 'concise' },
    { label: 'Balanced', value: 'balanced' },
    { label: 'Thorough', value: 'thorough' },
  ];

  readonly sectionLabel = computed(() => {
    const navId = this.prefs.activeNavId();
    if (!navId || navId === 'overview' || navId === 'sessions' || navId === 'settings') {
      return 'Full topic';
    }
    const fromNav = this.prefs.activePack().nav.find((n) => n.id === navId)?.label;
    return fromNav ?? navId;
  });

  readonly criteriaSummary = computed(() => {
    const parts: string[] = [];
    parts.push(this.prefs.deepThink() ? 'Deep think' : 'Balanced mode');
    parts.push(`Tone: ${String(this.prefs.effectiveSettings()['tone'] ?? 'balanced')}`);
    const lenses = this.prefs.selectedLenses();
    if (lenses.length) {
      parts.push(`Lenses: ${lenses.length}`);
    }
    const opts = this.prefs.selectedOptions();
    if (opts.length) {
      parts.push(`Options: ${opts.length}`);
    }
    return parts.join(' · ');
  });

  get chatTone(): string {
    return String(this.prefs.effectiveSettings()['tone'] ?? 'balanced');
  }

  set chatTone(v: string) {
    this.prefs.patchChat({ tone: v });
  }

  get deepThink(): boolean {
    return this.prefs.deepThink();
  }

  set deepThink(v: boolean) {
    this.prefs.setDeepThink(v);
  }

  toggleCriteria(): void {
    this.criteriaOpen.update((v) => !v);
  }

  ngOnInit(): void {
    this.prefs.openSectionChamber();
  }

  sectionHubLink(): string[] {
    const navId = this.prefs.activeNavId();
    if (!navId || navId === 'overview' || navId === 'sessions' || navId === 'settings') {
      return ['/app', this.prefs.activePackId(), 'overview'];
    }
    return ['/app', this.prefs.activePackId(), 'section'];
  }

  startRename(): void {
    this.renameDraft = this.activeChatTitle();
    this.renaming.set(true);
  }

  saveRename(): void {
    if (!this.renaming()) {
      return;
    }
    const id = this.prefs.activeProjectId();
    if (id) {
      this.prefs.renameProject(id, this.renameDraft);
    }
    this.renaming.set(false);
  }

  cancelRename(): void {
    this.renaming.set(false);
  }

  newSession(): void {
    this.prefs.createProject();
  }

  send(): void {
    const text = this.draft.trim();
    if (!text || this.busy()) {
      return;
    }
    const user = this.auth.user();
    if (!user) {
      return;
    }

    this.prefs.appendMessage({ role: 'user', text });
    this.draft = '';
    this.busy.set(true);

    const sessionId = this.prefs.activeProjectId();
    const ctx = this.prefs.buildCtxData();

    this.council.deliberate(sessionId, user.id, text, ctx).subscribe({
      next: (res: DeliberateResponse) => {
        this.prefs.appendMessage({
          role: 'agent',
          text: res.reply,
          seat: 'Facilitator',
        });
        this.busy.set(false);
      },
      error: () => {
        this.busy.set(false);
      },
    });
  }
}
