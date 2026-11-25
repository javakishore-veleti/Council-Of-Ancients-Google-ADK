import { PackDefinition } from '../models/pack';

export const PACKS: PackDefinition[] = [
  {
    id: 'entrepreneurship',
    label: 'Entrepreneurship',
    shortLabel: 'Venture',
    kbReady: false,
    tagline: 'Plan, fund, and launch with disciplined judgment.',
    nav: [
      { id: 'overview', label: 'Overview', icon: 'bi-compass', route: 'overview' },
      { id: 'chamber', label: 'Chamber', icon: 'bi-chat-square-quote', route: 'chamber' },
      { id: 'sessions', label: 'Sessions', icon: 'bi-clock-history', route: 'sessions' },
      { id: 'plan', label: 'Plan & launch', icon: 'bi-rocket-takeoff', route: 'chamber' },
      { id: 'fund', label: 'Fund & grow', icon: 'bi-graph-up-arrow', route: 'chamber' },
      { id: 'settings', label: 'Pack settings', icon: 'bi-sliders', route: 'settings' },
    ],
    optionsByNav: {
      plan: [
        { id: 'stage_idea', label: 'Stage: idea' },
        { id: 'stage_validate', label: 'Stage: validate' },
        { id: 'stage_launch', label: 'Stage: launch' },
      ],
      fund: [
        { id: 'bootstrapped', label: 'Bootstrapped' },
        { id: 'debt', label: 'Debt' },
        { id: 'equity', label: 'Equity' },
      ],
      chamber: [
        { id: 'seat_vision', label: 'Seat: Vision' },
        { id: 'seat_capital', label: 'Seat: Capital' },
        { id: 'seat_execution', label: 'Seat: Execution' },
      ],
    },
  },
  {
    id: 'leadership',
    label: 'Leadership',
    shortLabel: 'Lead',
    kbReady: false,
    tagline: 'People, culture, and one-way-door decisions.',
    nav: [
      { id: 'overview', label: 'Overview', icon: 'bi-compass', route: 'overview' },
      { id: 'chamber', label: 'Chamber', icon: 'bi-chat-square-quote', route: 'chamber' },
      { id: 'sessions', label: 'Sessions', icon: 'bi-clock-history', route: 'sessions' },
      { id: 'people', label: 'People & culture', icon: 'bi-people', route: 'chamber' },
      { id: 'decisions', label: 'Decisions', icon: 'bi-signpost-2', route: 'chamber' },
      { id: 'settings', label: 'Pack settings', icon: 'bi-sliders', route: 'settings' },
    ],
    optionsByNav: {
      people: [
        { id: 'ic', label: 'Stakeholder: IC' },
        { id: 'manager', label: 'Stakeholder: manager' },
        { id: 'exec', label: 'Stakeholder: exec' },
      ],
      decisions: [
        { id: 'reversible', label: 'Reversible' },
        { id: 'one_way', label: 'One-way door' },
      ],
      chamber: [
        { id: 'seat_people', label: 'Seat: People' },
        { id: 'seat_culture', label: 'Seat: Culture' },
        { id: 'seat_judgment', label: 'Seat: Judgment' },
      ],
    },
  },
  {
    id: 'sre',
    label: 'SRE',
    shortLabel: 'SRE',
    kbReady: false,
    tagline: 'Reliability, budgets, and calm incident response.',
    nav: [
      { id: 'overview', label: 'Overview', icon: 'bi-compass', route: 'overview' },
      { id: 'chamber', label: 'Chamber', icon: 'bi-chat-square-quote', route: 'chamber' },
      { id: 'sessions', label: 'Sessions', icon: 'bi-clock-history', route: 'sessions' },
      { id: 'reliability', label: 'Reliability', icon: 'bi-shield-check', route: 'chamber' },
      { id: 'incidents', label: 'Incidents', icon: 'bi-lightning-charge', route: 'chamber' },
      { id: 'settings', label: 'Pack settings', icon: 'bi-sliders', route: 'settings' },
    ],
    optionsByNav: {
      reliability: [
        { id: 'slo', label: 'SLO class' },
        { id: 'budget', label: 'Error-budget policy' },
      ],
      incidents: [
        { id: 'sev', label: 'Severity' },
        { id: 'mitigate', label: 'Phase: mitigate' },
        { id: 'review', label: 'Phase: review' },
      ],
      chamber: [
        { id: 'seat_reliability', label: 'Seat: Reliability' },
        { id: 'seat_capacity', label: 'Seat: Capacity' },
        { id: 'seat_response', label: 'Seat: Response' },
      ],
    },
  },
  {
    id: 'fitness',
    label: 'Fitness',
    shortLabel: 'Fit',
    kbReady: false,
    tagline: 'Training and recovery guidance — not medical advice.',
    nav: [
      { id: 'overview', label: 'Overview', icon: 'bi-compass', route: 'overview' },
      { id: 'chamber', label: 'Chamber', icon: 'bi-chat-square-quote', route: 'chamber' },
      { id: 'sessions', label: 'Sessions', icon: 'bi-clock-history', route: 'sessions' },
      { id: 'training', label: 'Training', icon: 'bi-activity', route: 'chamber' },
      { id: 'recovery', label: 'Nutrition & recovery', icon: 'bi-heart-pulse', route: 'chamber' },
      { id: 'settings', label: 'Pack settings', icon: 'bi-sliders', route: 'settings' },
    ],
    optionsByNav: {
      training: [
        { id: 'strength', label: 'Goal: strength' },
        { id: 'endurance', label: 'Goal: endurance' },
        { id: 'mobility', label: 'Goal: mobility' },
      ],
      recovery: [{ id: 'constraints', label: 'Time / equipment constraints' }],
      chamber: [{ id: 'disclaimer', label: 'Disclaimer on' }],
    },
  },
  {
    id: 'software_architecture',
    label: 'Software Architecture & Design',
    shortLabel: 'Architecture',
    kbReady: true,
    tagline: 'Patterns, cloud, data, events, and AI systems with the council.',
    nav: [
      { id: 'overview', label: 'Overview', icon: 'bi-compass', route: 'overview' },
      { id: 'chamber', label: 'Chamber', icon: 'bi-chat-square-quote', route: 'chamber' },
      { id: 'sessions', label: 'Sessions', icon: 'bi-clock-history', route: 'sessions' },
      { id: 'patterns', label: 'Patterns', icon: 'bi-puzzle', route: 'chamber' },
      { id: 'styles', label: 'Architecture styles', icon: 'bi-diagram-3', route: 'chamber' },
      { id: 'data', label: 'Data & modeling', icon: 'bi-table', route: 'chamber' },
      { id: 'cloud', label: 'Cloud & infrastructure', icon: 'bi-cloud', route: 'chamber' },
      { id: 'databases', label: 'Databases & storage', icon: 'bi-database', route: 'chamber' },
      { id: 'events', label: 'Event systems', icon: 'bi-broadcast', route: 'chamber' },
      { id: 'ai_systems', label: 'AI & agentic systems', icon: 'bi-cpu', route: 'chamber' },
      { id: 'knowledge', label: 'Knowledge', icon: 'bi-journal-bookmark', route: 'overview' },
      { id: 'settings', label: 'Pack settings', icon: 'bi-sliders', route: 'settings' },
    ],
    optionsByNav: {
      patterns: [
        { id: 'creational', label: 'Family: creational' },
        { id: 'structural', label: 'Family: structural' },
        { id: 'behavioral', label: 'Family: behavioral' },
        { id: 'resilience', label: 'Resilience' },
        { id: 'compare', label: 'Compare 2 patterns' },
      ],
      styles: [
        { id: 'monolith', label: 'Monolith' },
        { id: 'modular', label: 'Modular monolith' },
        { id: 'microservices', label: 'Microservices' },
        { id: 'event_driven', label: 'Event-driven' },
        { id: 'serverless', label: 'Serverless' },
      ],
      data: [
        { id: 'normalization', label: 'Normalization vs access' },
        { id: 'consistency', label: 'Consistency model' },
        { id: 'schema', label: 'Schema evolution' },
      ],
      cloud: [
        { id: 'k8s_vs_serverless', label: 'K8s vs serverless' },
        { id: 'multi_region', label: 'Multi-region' },
        { id: 'iac', label: 'IaC modules' },
      ],
      databases: [
        { id: 'oltp_olap', label: 'OLTP vs OLAP' },
        { id: 'sharding', label: 'Sharding / partition' },
        { id: 'cap', label: 'CAP trade-offs' },
      ],
      events: [
        { id: 'pubsub_vs_queue', label: 'Pub/sub vs queue' },
        { id: 'streaming', label: 'Event streaming' },
        { id: 'idempotency', label: 'Idempotency / DLQ' },
      ],
      ai_systems: [
        { id: 'orchestration', label: 'Agent orchestration' },
        { id: 'hybrid_rag', label: 'Hybrid RAG' },
        { id: 'evals', label: 'Evals / guardrails' },
      ],
      chamber: [
        { id: 'full_council', label: 'Full council' },
        { id: 'seat_patterns', label: 'Seat: Patterns' },
        { id: 'seat_architecture', label: 'Seat: Architecture' },
        { id: 'seat_data', label: 'Seat: Data' },
      ],
    },
  },
];

export function packById(id: string): PackDefinition | undefined {
  return PACKS.find((p) => p.id === id);
}
