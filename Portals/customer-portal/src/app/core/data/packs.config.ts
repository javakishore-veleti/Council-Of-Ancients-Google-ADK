import { PackDefinition } from '../models/pack';

/**
 * Five domain packs — chrome for all; KB only where kbReady (Architecture v0).
 * Left nav + options mirror Product_Ideas.md.
 */
export const PACKS: PackDefinition[] = [
  {
    id: 'entrepreneurship',
    label: 'Entrepreneurship',
    shortLabel: 'Entrepreneurship',
    kbReady: false,
    tagline: 'Plan, fund, and launch with disciplined judgment.',
    heroImage:
      'https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1200&q=80',
    howItWorksImage:
      'https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1600&q=80',
    howItWorksCaption:
      'Vision, Capital, and Execution pressure-test the venture before you lock a path.',
    howItWorksIntro:
      'Pose a founder dilemma. Counselors speak from their seats. The Facilitator brings a clear recommendation — for this venture’s stage, runway, and bet.',
    howItWorksSteps: [
      'Bring a real venture question: pricing, raise, launch timing, or what to cut.',
      'Vision, Capital, and Execution each argue the trade-offs — disagreement is useful.',
      'The Facilitator synthesizes a recommendation you can act on this week.',
    ],
    seatsLabel: 'Vision / Capital / Execution',
    nav: [
      { id: 'overview', label: 'Overview', icon: 'bi-compass', route: 'overview' },
      { id: 'chamber', label: 'Chamber', icon: 'bi-chat-square-quote', route: 'chamber' },
      { id: 'sessions', label: 'Sessions', icon: 'bi-clock-history', route: 'sessions' },
      { id: 'plan', label: 'Plan & launch', icon: 'bi-rocket-takeoff', route: 'chamber' },
      { id: 'fund', label: 'Fund & grow', icon: 'bi-graph-up-arrow', route: 'chamber' },
      {
        id: 'knowledge',
        label: 'Knowledge',
        icon: 'bi-journal-bookmark',
        route: 'overview',
        disabledUntilKb: true,
      },
      { id: 'seats', label: 'Seats', icon: 'bi-people', route: 'chamber' },
      { id: 'settings', label: 'Settings', icon: 'bi-sliders', route: 'settings' },
    ],
    optionsByNav: {
      plan: [
        { id: 'stage_idea', label: 'Stage: idea' },
        { id: 'stage_validate', label: 'Stage: validate' },
        { id: 'stage_launch', label: 'Stage: launch' },
        { id: 'risk_lens', label: 'Risk lens' },
      ],
      fund: [
        { id: 'bootstrapped', label: 'Bootstrapped' },
        { id: 'debt', label: 'Debt' },
        { id: 'equity', label: 'Equity' },
        { id: 'use_of_funds', label: 'Use of funds' },
      ],
      seats: [
        { id: 'seat_vision', label: 'Seat: Vision' },
        { id: 'seat_capital', label: 'Seat: Capital' },
        { id: 'seat_execution', label: 'Seat: Execution' },
      ],
      chamber: [
        { id: 'seat_vision', label: 'Seat: Vision' },
        { id: 'seat_capital', label: 'Seat: Capital' },
        { id: 'seat_execution', label: 'Seat: Execution' },
        { id: 'full_council', label: 'Full council' },
      ],
    },
    lenses: [
      { id: 'founder', label: 'Founder' },
      { id: 'operator', label: 'Operator' },
      { id: 'investor_lens', label: 'Investor lens' },
      { id: 'first_time', label: 'First-time founder' },
    ],
  },
  {
    id: 'leadership',
    label: 'Leadership',
    shortLabel: 'Leadership',
    kbReady: false,
    tagline: 'People, culture, and one-way-door decisions.',
    heroImage:
      'https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=1200&q=80',
    howItWorksImage:
      'https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=1600&q=80',
    howItWorksCaption:
      'People, Culture, and Judgment sit with the decision before it becomes irreversible.',
    howItWorksIntro:
      'Pose a leadership dilemma. Counselors speak from their seats. The Facilitator brings a clear recommendation — for people, culture, and one-way-door choices.',
    howItWorksSteps: [
      'Bring a people or decision question: hiring, conflict, org design, or a hard call.',
      'People, Culture, and Judgment each speak — trust, norms, and reversibility surface.',
      'The Facilitator names a path and what to watch if you choose otherwise.',
    ],
    seatsLabel: 'People / Culture / Judgment',
    nav: [
      { id: 'overview', label: 'Overview', icon: 'bi-compass', route: 'overview' },
      { id: 'chamber', label: 'Chamber', icon: 'bi-chat-square-quote', route: 'chamber' },
      { id: 'sessions', label: 'Sessions', icon: 'bi-clock-history', route: 'sessions' },
      { id: 'people', label: 'People & culture', icon: 'bi-people', route: 'chamber' },
      { id: 'decisions', label: 'Decisions', icon: 'bi-signpost-2', route: 'chamber' },
      {
        id: 'knowledge',
        label: 'Knowledge',
        icon: 'bi-journal-bookmark',
        route: 'overview',
        disabledUntilKb: true,
      },
      { id: 'seats', label: 'Seats', icon: 'bi-person-badge', route: 'chamber' },
      { id: 'settings', label: 'Settings', icon: 'bi-sliders', route: 'settings' },
    ],
    optionsByNav: {
      people: [
        { id: 'ic', label: 'Stakeholder: IC' },
        { id: 'manager', label: 'Stakeholder: manager' },
        { id: 'skip', label: 'Stakeholder: skip' },
        { id: 'exec', label: 'Stakeholder: exec' },
        { id: 'conflict', label: 'Conflict type' },
      ],
      decisions: [
        { id: 'time_horizon', label: 'Time horizon' },
        { id: 'reversible', label: 'Reversible' },
        { id: 'one_way', label: 'One-way door' },
      ],
      seats: [
        { id: 'seat_people', label: 'Seat: People' },
        { id: 'seat_culture', label: 'Seat: Culture' },
        { id: 'seat_judgment', label: 'Seat: Judgment' },
      ],
      chamber: [
        { id: 'seat_people', label: 'Seat: People' },
        { id: 'seat_culture', label: 'Seat: Culture' },
        { id: 'seat_judgment', label: 'Seat: Judgment' },
        { id: 'full_council', label: 'Full council' },
      ],
    },
    lenses: [
      { id: 'ic', label: 'IC' },
      { id: 'manager', label: 'Manager' },
      { id: 'exec', label: 'Exec' },
      { id: 'hr_partner', label: 'People partner' },
    ],
  },
  {
    id: 'sre',
    label: 'SRE',
    shortLabel: 'SRE',
    kbReady: false,
    tagline: 'Reliability, budgets, and calm incident response.',
    heroImage:
      'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=80',
    howItWorksImage:
      'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1600&q=80',
    howItWorksCaption:
      'Reliability, Capacity, and Response deliberate like an SRE review — SLOs, load, and incidents.',
    howItWorksIntro:
      'Pose a reliability dilemma. Counselors speak from their seats. The Facilitator brings a clear recommendation — for SLOs, capacity, and calm incident response.',
    howItWorksSteps: [
      'Bring an SRE question: error budgets, toil, paging noise, or a postmortem decision.',
      'Reliability, Capacity, and Response each argue risk vs cost vs recovery.',
      'The Facilitator synthesizes the next operational move and what to measure.',
    ],
    seatsLabel: 'Reliability / Capacity / Response',
    nav: [
      { id: 'overview', label: 'Overview', icon: 'bi-compass', route: 'overview' },
      { id: 'chamber', label: 'Chamber', icon: 'bi-chat-square-quote', route: 'chamber' },
      { id: 'sessions', label: 'Sessions', icon: 'bi-clock-history', route: 'sessions' },
      { id: 'reliability', label: 'Reliability', icon: 'bi-shield-check', route: 'chamber' },
      {
        id: 'incidents',
        label: 'Incidents & postmortems',
        icon: 'bi-lightning-charge',
        route: 'chamber',
      },
      {
        id: 'knowledge',
        label: 'Knowledge',
        icon: 'bi-journal-bookmark',
        route: 'overview',
        disabledUntilKb: true,
      },
      { id: 'seats', label: 'Seats', icon: 'bi-hdd-rack', route: 'chamber' },
      { id: 'settings', label: 'Settings', icon: 'bi-sliders', route: 'settings' },
    ],
    optionsByNav: {
      reliability: [
        { id: 'slo', label: 'SLO class' },
        { id: 'budget', label: 'Error-budget policy' },
        { id: 'customer_impact', label: 'Customer impact' },
      ],
      incidents: [
        { id: 'sev', label: 'Severity' },
        { id: 'detect', label: 'Phase: detect' },
        { id: 'mitigate', label: 'Phase: mitigate' },
        { id: 'review', label: 'Phase: review' },
      ],
      seats: [
        { id: 'seat_reliability', label: 'Seat: Reliability' },
        { id: 'seat_capacity', label: 'Seat: Capacity' },
        { id: 'seat_response', label: 'Seat: Response' },
      ],
      chamber: [
        { id: 'seat_reliability', label: 'Seat: Reliability' },
        { id: 'seat_capacity', label: 'Seat: Capacity' },
        { id: 'seat_response', label: 'Seat: Response' },
        { id: 'full_council', label: 'Full council' },
      ],
    },
    lenses: [
      { id: 'oncall', label: 'On-call' },
      { id: 'sre_lead', label: 'SRE lead' },
      { id: 'platform', label: 'Platform' },
      { id: 'exec_risk', label: 'Exec risk' },
    ],
  },
  {
    id: 'fitness',
    label: 'Fitness',
    shortLabel: 'Fitness',
    kbReady: false,
    tagline: 'Training and recovery guidance — not medical advice.',
    heroImage:
      'https://images.unsplash.com/photo-1476480862126-209badba8baf?auto=format&fit=crop&w=1200&q=80',
    howItWorksImage:
      'https://images.unsplash.com/photo-1476480862126-209badba8baf?auto=format&fit=crop&w=1600&q=80',
    howItWorksCaption:
      'Training, Nutrition, and Recovery balance effort with fuel and rest — not gym-only advice.',
    howItWorksIntro:
      'Pose a fitness dilemma. Counselors speak from their seats. The Facilitator brings a clear recommendation — for training, fueling, and recovery (not medical advice).',
    howItWorksSteps: [
      'Bring a whole-person question: progression, plateaus, meals, sleep, or burnout.',
      'Training, Nutrition, and Recovery each weigh sustainability vs intensity.',
      'The Facilitator synthesizes a plan that respects recovery — see a clinician for medical concerns.',
    ],
    seatsLabel: 'Training / Nutrition / Recovery',
    nav: [
      { id: 'overview', label: 'Overview', icon: 'bi-compass', route: 'overview' },
      { id: 'chamber', label: 'Chamber', icon: 'bi-chat-square-quote', route: 'chamber' },
      { id: 'sessions', label: 'Sessions', icon: 'bi-clock-history', route: 'sessions' },
      { id: 'training', label: 'Training', icon: 'bi-activity', route: 'chamber' },
      {
        id: 'recovery',
        label: 'Nutrition & recovery',
        icon: 'bi-heart-pulse',
        route: 'chamber',
      },
      {
        id: 'knowledge',
        label: 'Knowledge',
        icon: 'bi-journal-bookmark',
        route: 'overview',
        disabledUntilKb: true,
      },
      { id: 'seats', label: 'Seats', icon: 'bi-bicycle', route: 'chamber' },
      { id: 'disclaimer', label: 'Disclaimer', icon: 'bi-exclamation-triangle', route: 'overview' },
      { id: 'settings', label: 'Settings', icon: 'bi-sliders', route: 'settings' },
    ],
    optionsByNav: {
      training: [
        { id: 'strength', label: 'Goal: strength' },
        { id: 'endurance', label: 'Goal: endurance' },
        { id: 'mobility', label: 'Goal: mobility' },
        { id: 'experience', label: 'Experience level' },
      ],
      recovery: [
        { id: 'constraints', label: 'Time / equipment constraints' },
        { id: 'no_diagnosis', label: 'No medical diagnosis' },
      ],
      seats: [
        { id: 'seat_training', label: 'Seat: Training' },
        { id: 'seat_nutrition', label: 'Seat: Nutrition' },
        { id: 'seat_recovery', label: 'Seat: Recovery' },
      ],
      chamber: [
        { id: 'seat_training', label: 'Seat: Training' },
        { id: 'seat_nutrition', label: 'Seat: Nutrition' },
        { id: 'seat_recovery', label: 'Seat: Recovery' },
        { id: 'disclaimer', label: 'Disclaimer on' },
        { id: 'full_council', label: 'Full council' },
      ],
      disclaimer: [{ id: 'disclaimer', label: 'Not medical advice' }],
    },
    lenses: [
      { id: 'beginner', label: 'Beginner' },
      { id: 'intermediate', label: 'Intermediate' },
      { id: 'coach', label: 'Coach lens' },
    ],
  },
  {
    id: 'software_architecture',
    label: 'Software Architecture & Design',
    shortLabel: 'Architecture',
    kbReady: true,
    tagline: 'Patterns, cloud, data, events, and AI systems with the council.',
    heroImage:
      'https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=1200&q=80',
    howItWorksImage:
      'https://images.unsplash.com/photo-1587620962725-abab7fe55159?auto=format&fit=crop&w=1600&q=80',
    howItWorksCaption:
      'Patterns, Architecture, and Data deliberate software trade-offs — system design, not civil engineering.',
    howItWorksIntro:
      'Pose a software design dilemma. Counselors speak from their seats. The Facilitator brings a clear recommendation — for patterns, system shape, and data.',
    howItWorksSteps: [
      'Bring a software architecture question: style, boundaries, consistency, or scale.',
      'Patterns, Architecture, and Data each argue the engineering trade-offs.',
      'The Facilitator synthesizes a recommendation you can take back to the codebase.',
    ],
    seatsLabel: 'Patterns / Architecture / Data',
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
      { id: 'seats', label: 'Seats', icon: 'bi-diagram-2', route: 'chamber' },
      { id: 'settings', label: 'Settings', icon: 'bi-sliders', route: 'settings' },
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
      seats: [
        { id: 'seat_patterns', label: 'Seat: Patterns' },
        { id: 'seat_architecture', label: 'Seat: Architecture' },
        { id: 'seat_data', label: 'Seat: Data' },
      ],
      chamber: [
        { id: 'full_council', label: 'Full council' },
        { id: 'seat_patterns', label: 'Seat: Patterns' },
        { id: 'seat_architecture', label: 'Seat: Architecture' },
        { id: 'seat_data', label: 'Seat: Data' },
      ],
    },
    lenses: [
      { id: 'aspiring', label: 'Aspiring' },
      { id: 'developer', label: 'Developer' },
      { id: 'startup_cto', label: 'Startup CTO' },
      { id: 'enterprise_architect', label: 'Enterprise' },
      { id: 'coding_agent', label: 'Coding agent' },
    ],
  },
];

export function packById(id: string): PackDefinition | undefined {
  return PACKS.find((p) => p.id === id);
}
