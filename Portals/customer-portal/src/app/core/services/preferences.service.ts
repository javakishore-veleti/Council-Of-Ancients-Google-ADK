import { Injectable, computed, signal } from '@angular/core';
import {
  ChatMessage,
  ChatProject,
  EffectiveContext,
  PackId,
  UserSettings,
} from '../models/pack';
import { packById } from '../data/packs.config';

const GLOBAL_KEY = 'coa_global_settings';
const PACK_KEY = 'coa_pack_settings';
const PROJECTS_KEY = 'coa_chat_projects';
const MESSAGES_KEY = 'coa_chat_messages';

@Injectable({ providedIn: 'root' })
export class PreferencesService {
  readonly activePackId = signal<PackId>('software_architecture');
  readonly activeNavId = signal<string>('overview');
  readonly activeProjectId = signal<string>('');
  readonly selectedOptions = signal<string[]>([]);
  readonly selectedLenses = signal<string[]>([]);
  readonly deepThink = signal(false);
  readonly sourcesOpen = signal(true);

  readonly globalSettings = signal<UserSettings>(this.loadGlobal());
  readonly packOverrides = signal<Record<string, Partial<UserSettings>>>(
    this.loadJson(PACK_KEY, {}),
  );
  private readonly chatOverrides = signal<Record<string, Record<string, unknown>>>(
    {},
  );
  private readonly projects = signal<ChatProject[]>(this.loadProjects());
  private readonly messages = signal<Record<string, ChatMessage[]>>(
    this.loadJson(MESSAGES_KEY, {}),
  );

  readonly activePack = computed(() => packById(this.activePackId())!);
  readonly domainOptions = computed(() => {
    const pack = this.activePack();
    const nav = this.activeNavId();
    return pack.optionsByNav[nav] ?? pack.optionsByNav['chamber'] ?? [];
  });

  /** All sessions for the active topic (any section). */
  readonly projectList = computed(() =>
    this.projects()
      .filter((p: ChatProject) => p.packId === this.activePackId())
      .sort(
        (a: ChatProject, b: ChatProject) =>
          b.updatedAt.getTime() - a.updatedAt.getTime(),
      ),
  );

  /** Sessions for the active left-nav section only. */
  readonly sectionProjectList = computed(() => {
    const sectionId = this.activeNavId();
    return this.projectList().filter(
      (p: ChatProject) => (p.sectionId || 'overview') === sectionId,
    );
  });

  readonly activeMessages = computed(
    () => this.messages()[this.activeProjectId()] ?? [],
  );

  readonly effectiveSettings = computed(() => {
    const global = this.globalSettings();
    const pack = this.packOverrides()[this.activePackId()] ?? {};
    const chat = this.chatOverrides()[this.activeProjectId()] ?? {};
    return { ...global, ...pack, ...chat } as UserSettings & Record<string, unknown>;
  });

  constructor() {
    if (!this.activeProjectId()) {
      this.ensureProject();
    }
  }

  setPack(id: PackId): void {
    this.activePackId.set(id);
    this.activeNavId.set('overview');
    this.selectedOptions.set([]);
    this.selectedLenses.set([]);
    this.deepThink.set(false);
    this.ensureProject();
    this.patchGlobal({ lastPackId: id });
  }

  setNav(id: string): void {
    // Chamber is a canvas, not a left-nav section id.
    this.activeNavId.set(id === 'chamber' ? 'overview' : id);
    this.selectedOptions.set([]);
  }

  toggleOption(id: string): void {
    const cur = this.selectedOptions();
    this.selectedOptions.set(
      cur.includes(id) ? cur.filter((x: string) => x !== id) : [...cur, id],
    );
  }

  toggleLens(id: string): void {
    const cur = this.selectedLenses();
    this.selectedLenses.set(
      cur.includes(id) ? cur.filter((x: string) => x !== id) : [...cur, id],
    );
    this.patchChat({ lenses: this.selectedLenses() });
  }

  setDeepThink(on: boolean): void {
    this.deepThink.set(on);
    this.patchChat({ mode: on ? 'deep_think' : 'balanced' });
  }

  patchGlobal(patch: Partial<UserSettings>): void {
    const next = { ...this.globalSettings(), ...patch };
    this.globalSettings.set(next);
    localStorage.setItem(GLOBAL_KEY, JSON.stringify(next));
  }

  patchPack(patch: Partial<UserSettings>): void {
    const all = { ...this.packOverrides(), [this.activePackId()]: {
      ...(this.packOverrides()[this.activePackId()] ?? {}),
      ...patch,
    }};
    this.packOverrides.set(all);
    localStorage.setItem(PACK_KEY, JSON.stringify(all));
  }

  patchChat(patch: Record<string, unknown>): void {
    const id = this.activeProjectId();
    const all = { ...this.chatOverrides(), [id]: { ...(this.chatOverrides()[id] ?? {}), ...patch } };
    this.chatOverrides.set(all);
  }

  sectionLabel(sectionId = this.activeNavId()): string {
    const id = !sectionId || sectionId === 'chamber' ? 'overview' : sectionId;
    if (id === 'overview') {
      return 'Overview';
    }
    return this.activePack().nav.find((n) => n.id === id)?.label ?? id;
  }

  ensureProject(title?: string): string {
    const existing = this.sectionProjectList()[0];
    if (existing) {
      this.activeProjectId.set(existing.id);
      return existing.id;
    }
    return this.createProject(title);
  }

  /** Open chamber for the current section: reuse latest session or start one. */
  openSectionChamber(): string {
    const list = this.sectionProjectList();
    if (list.length) {
      this.activeProjectId.set(list[0].id);
      return list[0].id;
    }
    return this.createProject();
  }

  createProject(title?: string): string {
    const rawSection = this.activeNavId();
    const sectionId = !rawSection || rawSection === 'chamber' ? 'overview' : rawSection;
    const label = this.sectionLabel(sectionId);
    const id = `proj_${crypto.randomUUID().slice(0, 8)}`;
    const project: ChatProject = {
      id,
      title: title ?? `${label} · ${new Date().toLocaleString()}`,
      packId: this.activePackId(),
      sectionId,
      updatedAt: new Date(),
    };
    const next = [project, ...this.projects()];
    this.projects.set(next);
    this.persistProjects();
    this.activeProjectId.set(id);
    this.messages.update((m: Record<string, ChatMessage[]>) => ({ ...m, [id]: [] }));
    this.persistMessages();
    return id;
  }

  selectProject(id: string): void {
    this.activeProjectId.set(id);
  }

  activeProject(): ChatProject | undefined {
    const id = this.activeProjectId();
    return this.projects().find((p: ChatProject) => p.id === id);
  }

  renameProject(id: string, title: string): void {
    const next = title.trim();
    if (!next) {
      return;
    }
    this.projects.update((ps: ChatProject[]) =>
      ps.map((p: ChatProject) => (p.id === id ? { ...p, title: next, updatedAt: new Date() } : p)),
    );
    this.persistProjects();
  }

  appendMessage(msg: Omit<ChatMessage, 'id' | 'at'> & { id?: string; at?: Date }): void {
    const id = this.activeProjectId();
    const entry: ChatMessage = {
      id: msg.id ?? crypto.randomUUID(),
      at: msg.at ?? new Date(),
      role: msg.role,
      text: msg.text,
      seat: msg.seat,
    };
    const list = [...(this.messages()[id] ?? []), entry];
    this.messages.update((m: Record<string, ChatMessage[]>) => ({ ...m, [id]: list }));
    this.persistMessages();
    this.projects.update((ps: ChatProject[]) =>
      ps.map((p: ChatProject) => (p.id === id ? { ...p, updatedAt: new Date() } : p)),
    );
    this.persistProjects();
  }

  buildCtxData(): EffectiveContext {
    const opts: Record<string, string> = {};
    for (const id of this.selectedOptions()) {
      opts[id] = 'true';
    }
    const turns = this.activeMessages()
      .slice(-8)
      .map((m: ChatMessage) => ({ role: m.role, text: m.text }));
    return {
      pack_id: this.activePackId(),
      left_nav: this.activeNavId(),
      domain_options: opts,
      lenses: this.selectedLenses(),
      mode: this.deepThink() ? 'deep_think' : 'balanced',
      settings: this.effectiveSettings(),
      chat_project_id: this.activeProjectId(),
      recent_turns: turns,
    };
  }

  private loadGlobal(): UserSettings {
    return this.loadJson(GLOBAL_KEY, {
      citeSources: true,
      tone: 'balanced' as const,
      lastPackId: 'software_architecture' as PackId,
      disclaimerAck: false,
    });
  }

  private loadProjects(): ChatProject[] {
    const raw = this.loadJson<Array<ChatProject & { updatedAt: string; sectionId?: string }>>(
      PROJECTS_KEY,
      [],
    );
    return raw.map((p) => ({
      ...p,
      sectionId: !p.sectionId || p.sectionId === 'chamber' ? 'overview' : p.sectionId,
      updatedAt: new Date(p.updatedAt),
    }));
  }

  private persistProjects(): void {
    localStorage.setItem(PROJECTS_KEY, JSON.stringify(this.projects()));
  }

  private persistMessages(): void {
    localStorage.setItem(MESSAGES_KEY, JSON.stringify(this.messages()));
  }

  private loadJson<T>(key: string, fallback: T): T {
    try {
      const raw = localStorage.getItem(key);
      return raw ? (JSON.parse(raw) as T) : fallback;
    } catch {
      return fallback;
    }
  }
}
