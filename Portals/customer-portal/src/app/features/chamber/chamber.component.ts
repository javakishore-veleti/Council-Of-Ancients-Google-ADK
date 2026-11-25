import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { TextareaModule } from 'primeng/textarea';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { SelectButtonModule } from 'primeng/selectbutton';
import { AuthService } from '../../core/services/auth.service';
import { PreferencesService } from '../../core/services/preferences.service';
import { CouncilApiService, DeliberateResponse } from '../../core/services/council-api.service';
import { CHAT_LENSES } from '../../core/models/pack';
import { ToggleSwitchModule } from 'primeng/toggleswitch';
import { CheckboxModule } from 'primeng/checkbox';

@Component({
  selector: 'app-chamber',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
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
export class ChamberComponent {
  readonly prefs = inject(PreferencesService);
  readonly auth = inject(AuthService);
  readonly lenses = CHAT_LENSES;
  private readonly council = inject(CouncilApiService);

  draft = '';
  readonly busy = signal(false);

  toneOptions = [
    { label: 'Concise', value: 'concise' },
    { label: 'Balanced', value: 'balanced' },
    { label: 'Thorough', value: 'thorough' },
  ];

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

  newSession(): void {
    this.prefs.createProject(`Session ${new Date().toLocaleString()}`);
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
