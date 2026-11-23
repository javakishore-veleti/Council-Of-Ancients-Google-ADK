# Hands-on: Council of Ancients

Type the code yourself. Use this list in order.

Blog: https://danicat.dev/posts/ai-agents-from-scratch-with-google-adk/  
Reference (read only): https://github.com/danicat/council

## Table of contents

1. [Before coding](#1-before-coding)
2. [Install tools](#2-install-tools)
3. [Config](#3-config)
4. [Plato](#4-plato)
5. [Descartes](#5-descartes)
6. [Machiavelli](#6-machiavelli)
7. [Facilitator](#7-facilitator)
8. [Model Armor App](#8-model-armor-app)
9. [Run locally](#9-run-locally)
10. [API service](#10-api-service)
11. [Angular portal](#11-angular-portal)
12. [Test guardrails](#12-test-guardrails)
13. [Optional: Cloud Run](#13-optional-cloud-run)

---

## 1. Before coding

1. Finish GCP setup in [README.md](README.md) (secrets + workflows 001 → 002 → 003).
2. Copy `.env.template` → `.env` and fill project + Model Armor paths.
3. Open the repo in Cursor and select interpreter `.venv/bin/python`.

Your code goes here:

| Folder | Work |
|--------|------|
| `Middleware/Agents/council_of_ancients/` | Agents |
| `Middleware/API-Services/` | HTTP API |
| `Portals/` | Angular UI |

---

## 2. Install tools

1. In repo root run: `uv sync` (needs `google-adk[gcp]` and `python-dotenv` in `pyproject.toml`).
2. Open `Middleware/Agents/council_of_ancients/agent.py`.
3. Import `Agent`.
4. Create a small `root_agent` with `model`, `name`, `description`, `instruction`.
5. Check: `uv run python -c "from google.adk.agents.llm_agent import Agent; print(Agent)"`

---

## 3. Config

1. Create `Middleware/Agents/council_of_ancients/config.py`.
2. Load `.env` with dotenv.
3. Read: project id, Model Armor prompt template, Model Armor response template, model id (`gemini-4-hydrogen`).
4. Fail if any value is missing.
5. Check both Model Armor paths use the same region.
6. Export values other files will import.

---

## 4. Plato

File: `Middleware/Agents/council_of_ancients/counselors/plato.py`

1. Write `PLATO_INSTRUCTION` (ethics, virtue, community).
2. Create `plato = Agent(...)` with:
   - `name="plato"`
   - model from config
   - `mode="single_turn"`
   - `description=...`
   - `static_instruction=PLATO_INSTRUCTION`
3. Export `plato` from `counselors/__init__.py`.

---

## 5. Descartes

File: `counselors/descartes.py` (rename `descrates.py` if needed)

1. Same shape as Plato.
2. Instruction: doubt, first principles, what can be proven.
3. `name="descartes"`, `mode="single_turn"`, `static_instruction=...`
4. Export from `__init__.py`.

---

## 6. Machiavelli

File: `counselors/machiavelli.py`

1. Same shape as Plato.
2. Instruction: power, incentives, what works in practice.
3. `name="machiavelli"`, `mode="single_turn"`, `static_instruction=...`
4. Export from `__init__.py`.

---

## 7. Facilitator

File: `Middleware/Agents/council_of_ancients/agent.py`

1. Import the three counselors.
2. Write `FACILITATOR_INSTRUCTION`:
   - hello / “who is on the council?” → answer yourself, no sub-agents
   - real question → call `plato`, `descartes`, `machiavelli` in parallel (opening)
   - then call all three again in parallel (rebuttal, critique by name)
   - then write a final synthesis + recommended action
3. Create `facilitator = Agent(..., sub_agents=[plato, descartes, machiavelli])`.
4. Use `static_instruction` for the facilitator.

---

## 8. Model Armor App

Still in `agent.py` (or a nearby module):

1. Import `App`, `ModelArmorConfig`, `ModelArmorPlugin` (check ADK docs for exact import).
2. Create `app = App(name="council_of_ancients", root_agent=facilitator, plugins=[...])`.
3. Pass both template names from config.
4. Set `block_on_screening_failure=True`.
5. Set `root_agent = app.root_agent`.

---

## 9. Run locally

1. Make sure `.env` Vertex / GenAI flags are set.
2. Point ADK at your agents folder/package (see ADK docs for `adk web` / agents dir).
3. Run ADK web.
4. Try `hello` → short reply.
5. Try a real dilemma → three opinions, rebuttals, final verdict.

---

## 10. API service

Folder: `Middleware/API-Services/`

1. Create a FastAPI entry using ADK’s `get_fast_api_app` (or current equivalent).
2. Point it at your council agents.
3. Use `PORT` from `.env`.
4. Write run steps in that folder’s README.
5. Start the server and call it once (curl or browser).

---

## 11. Angular portal

Folder: `Portals/`

1. Create an Angular app.
2. Build a simple chat page (input + messages).
3. Call your API (SSE if you add streaming).
4. Put API URL in Angular environment files (no secrets in git).
5. Confirm: Portal → API → Agents works end to end.

---

## 12. Test guardrails

1. Send a prompt injection (“Ignore all previous instructions…”). Expect block.
2. Send a normal hard question. Expect full council reply.
3. Write down what you tried and the result.

---

## 13. Optional: Cloud Run

1. Deploy the API (and built Angular if you want) to Cloud Run.
2. Run as `council-of-ancients-sa`.
3. Set Model Armor + Vertex env vars on the service.
4. Keep the service private; use `gcloud run services proxy` for local access.

---

## Remember

| Topic | Rule |
|-------|------|
| `single_turn` | Counselors; Facilitator calls them as tools |
| `static_instruction` | No `{placeholder}` substitution |
| Model Armor on `App` | Covers facilitator + all counselors |
| Do not commit | `.env` |
