# Product Ideas — Council of Ancients

Captured product and research directions for deepening counselor authenticity and knowledge. These are backlog ideas, not committed roadmap dates.

## Problem framing

A multi-agent “council” demo can sound like Plato, Descartes, or Machiavelli from a **system prompt alone**. That is enough for chamber UX and structured disagreement. It is **not** enough if the product claim is that each counselor *reasons from* that thinker’s corpus.

Two different jobs get conflated:

| Job | What it takes |
|-----|----------------|
| **Gather knowledge** | Source, license, curate, and chunk primary + trusted secondary texts per counselor |
| **Build retrieval** | Index, retrieve, and (later) let the agent *decide* what to retrieve — plain RAG vs **agentic RAG** |

Gathering the knowledge bank is one workstream. Wiring RAG / agentic RAG / MCP tools on top is another.

## Persona design questions (product requirements)

These questions should drive the knowledge + agent design:

1. **How is “ancient knowledge” assembled?** Public-domain primary texts, curated excerpts, encyclopedic secondary notes, licensed e-books — and what is explicitly *out* of scope?
2. **How is each persona built?** Prompt lens only, or prompt + grounded passages from that thinker’s works and method?
3. **Are counselors book-grounded?** If yes, name the canon per seat (e.g. *Republic* / dialogues; *Meditations*; *The Prince* / *Discourses*) and keep retrieval **scoped per counselor** so voices do not cross-contaminate.
4. **What does “act like Plato” require?** Not only tone: themes, argument patterns, and enough history of the corpus that openings and rebuttals can cite or paraphrase with discipline.
5. **When is a short lens enough?** Casual greetings and meta “who is on the council?” can stay Facilitator-only with light prompts. Hard dilemmas should prefer grounded counsel once the bank exists.

## Knowledge bank (idea)

Proposed layout (implementation TBD):

```text
Middleware/Knowledge/
  plato/          # primary + curated secondary, chunked by work/theme
  descartes/
  machiavelli/
```

Chunking should prefer **section + theme** (justice, methodical doubt, virtù, …) over opaque token windows. Metadata ideas: `counselor`, `work`, `theme`, `era`, `license`.

Prefer **public-domain / clearly licensed** sources first (e.g. Project Gutenberg, Internet Classics-style archives); treat modern commentary as secondary and cite carefully.

## RAG vs agentic RAG (idea)

| Mode | Behavior | Fit |
|------|----------|-----|
| **Plain RAG** | Embed user dilemma → top-k chunks → stuff into counselor context | Strong v1 once a bank exists |
| **Agentic RAG** | Counselor (or Facilitator) **chooses** retrieval: which work, which theme, multi-hop queries via tools | Differentiator for “thinks like X,” not only “sounds like X” |

Agentic RAG pairs naturally with **MCP / ADK tools**, e.g. `search_plato`, `get_passage`, scoped per corpus so Machiavelli never pulls Republic chunks by accident.

Target flow once built:

```text
Portal → coa_agents_api → Facilitator
                            ├─ Plato + RAG/MCP (plato bank)
                            ├─ Descartes + RAG/MCP (descartes bank)
                            └─ Machiavelli + RAG/MCP (machiavelli bank)
```

## Honest product positioning

Until the knowledge bank + retrieval path ships:

- **Now:** Standing roles with strong **lens prompts** (ethics / doubt / power), Facilitator triage, parallel openings → rebuttals → synthesis.
- **Next:** Per-ancient knowledge bank, then plain RAG, then agentic retrieval tools/MCP.
- **Do not over-claim:** Avoid marketing language that implies full canonical mastery until retrieval is real and evaluated.

## Related product opportunities

Ideas that often come up when discussing this architecture (same pattern, different domains):

- **Other councils** — C-suite lenses, scientific method seats, legal/ethics boards — same Facilitator + parallel specialists + synthesis shape.
- **Eval harness** — “Would this answer be recognizable as that lens?” and “Did retrieval cite the right work/theme?”
- **Citation UX in the portal** — Show which passage grounded an opening or rebuttal (builds trust vs pure roleplay).
- **Fail-soft grounding** — If retrieval misses, counselor should hedge as “lens without passage” rather than invent citations.

## Suggested build order

1. Curate v0 corpora (public-domain) per counselor with licenses recorded.
2. Chunk + embed + plain RAG tool per counselor.
3. Wire tools into ADK counselors; keep Facilitator orchestration unchanged.
4. Promote to agentic RAG (multi-query / theme routing) behind MCP or ADK tools.
5. Portal citations + offline eval set of dilemmas.

## Notes

- Observability (`coa_observability_api`) should eventually label retrieval hits (tokens, latency, corpus id) the same way LLM calls are labeled — so RAG cost and quality are measurable.
- This file intentionally records **ideas and open questions**, not a promise of delivery order beyond the suggested build sequence above.
