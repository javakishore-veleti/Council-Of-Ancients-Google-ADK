import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { ToggleSwitchModule } from 'primeng/toggleswitch';
import { SelectButtonModule } from 'primeng/selectbutton';
import { ButtonModule } from 'primeng/button';
import { PreferencesService } from '../../core/services/preferences.service';
import { UserSettings } from '../../core/models/pack';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ToggleSwitchModule,
    SelectButtonModule,
    ButtonModule,
  ],
  templateUrl: './settings.component.html',
  styleUrl: './settings.component.scss',
})
export class SettingsComponent {
  readonly prefs = inject(PreferencesService);
  private readonly route = inject(ActivatedRoute);

  toneOptions = [
    { label: 'Concise', value: 'concise' },
    { label: 'Balanced', value: 'balanced' },
    { label: 'Thorough', value: 'thorough' },
  ];

  scope(): 'global' | 'pack' {
    return (this.route.snapshot.data['scope'] as 'global' | 'pack') || 'pack';
  }

  get citeSources(): boolean {
    return !!this.current().citeSources;
  }
  set citeSources(v: boolean) {
    this.patch({ citeSources: v });
  }

  get tone(): string {
    return this.current().tone;
  }
  set tone(v: string) {
    this.patch({ tone: v as UserSettings['tone'] });
  }

  get disclaimerAck(): boolean {
    return !!this.current().disclaimerAck;
  }
  set disclaimerAck(v: boolean) {
    this.patch({ disclaimerAck: v });
  }

  private current(): UserSettings {
    const global = this.prefs.globalSettings();
    if (this.scope() === 'global') {
      return global;
    }
    return {
      ...global,
      ...(this.prefs.packOverrides()[this.prefs.activePackId()] ?? {}),
    };
  }

  private patch(p: Partial<UserSettings>): void {
    if (this.scope() === 'global') {
      this.prefs.patchGlobal(p);
    } else {
      this.prefs.patchPack(p);
    }
  }
}
