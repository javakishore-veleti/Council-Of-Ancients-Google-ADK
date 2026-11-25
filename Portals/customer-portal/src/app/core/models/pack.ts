export type PackId =
  | 'entrepreneurship'
  | 'leadership'
  | 'sre'
  | 'fitness'
  | 'software_architecture';

export interface NavItem {
  id: string;
  label: string;
  icon: string;
  route: string;
  /** Soft-disabled chrome until KB ready */
  disabledUntilKb?: boolean;
}

export interface DomainOption {
  id: string;
  label: string;
}

export interface ChatLens {
  id: string;
  label: string;
}

export interface PackDefinition {
  id: PackId;
  label: string;
  shortLabel: string;
  kbReady: boolean;
  tagline: string;
  heroImage: string;
  seatsLabel: string;
  nav: NavItem[];
  optionsByNav: Record<string, DomainOption[]>;
  /** Optional composer lenses — pack-specific; never mandatory */
  lenses: ChatLens[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'agent' | 'system';
  text: string;
  at: Date;
  seat?: string;
}

export interface ChatProject {
  id: string;
  title: string;
  packId: PackId;
  updatedAt: Date;
}

export interface UserSettings {
  citeSources: boolean;
  tone: 'concise' | 'balanced' | 'thorough';
  lastPackId: PackId;
  disclaimerAck: boolean;
}

export interface EffectiveContext {
  pack_id: PackId;
  left_nav: string;
  domain_options: Record<string, string>;
  lenses: string[];
  mode: 'balanced' | 'deep_think';
  settings: UserSettings & Record<string, unknown>;
  chat_project_id: string;
  recent_turns: Array<{ role: string; text: string }>;
}
