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
}

export interface DomainOption {
  id: string;
  label: string;
}

export interface PackDefinition {
  id: PackId;
  label: string;
  shortLabel: string;
  kbReady: boolean;
  tagline: string;
  nav: NavItem[];
  optionsByNav: Record<string, DomainOption[]>;
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

/** Optional chat lenses — never mandatory profile roles */
export type ChatLensId =
  | 'aspiring'
  | 'developer'
  | 'startup_cto'
  | 'enterprise_architect'
  | 'coding_agent';

export const CHAT_LENSES: Array<{ id: ChatLensId; label: string }> = [
  { id: 'aspiring', label: 'Aspiring' },
  { id: 'developer', label: 'Developer' },
  { id: 'startup_cto', label: 'Startup CTO' },
  { id: 'enterprise_architect', label: 'Enterprise' },
  { id: 'coding_agent', label: 'Coding agent' },
];

export interface EffectiveContext {
  pack_id: PackId;
  left_nav: string;
  domain_options: Record<string, string>;
  lenses: ChatLensId[];
  mode: 'balanced' | 'deep_think';
  settings: UserSettings & Record<string, unknown>;
  chat_project_id: string;
  recent_turns: Array<{ role: string; text: string }>;
}
