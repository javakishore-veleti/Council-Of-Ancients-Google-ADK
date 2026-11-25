"""Council of Ancients ADK app: Facilitator + counselors + Model Armor."""

from __future__ import annotations

from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.apps import App
from google.adk.integrations.model_armor import ModelArmorConfig, ModelArmorPlugin

from .config import MODEL_ID, load_config
from .counselors import descartes, machiavelli, plato
from .observability_hooks import after_model_obs

load_dotenv()

FACILITATOR_INSTRUCTION = """
You are the impartial Facilitator of the Council of Ancients:
Plato, René Descartes, and Niccolò Machiavelli.

Triage:
- For greetings or meta questions about who is on the council, reply in 2-3 sentences.
  Do not call sub-agents.
- For any real question or dilemma:
  1) Opening: call plato, descartes, and machiavelli in parallel with the user question.
  2) Rebuttal: call all three again in parallel; each must critique the other two by name.
  3) Verdict: write ## Council Synthesis: then Recommended Action,
     Points of Convergence, Unresolved Tensions, and Counselor Contributions.
"""

facilitator = Agent(
    name="facilitator",
    model=MODEL_ID,
    description=(
        "Impartial chair of the Council of Ancients coordinating Plato, "
        "René Descartes, and Niccolò Machiavelli."
    ),
    static_instruction=FACILITATOR_INSTRUCTION,
    sub_agents=[plato, descartes, machiavelli],
    after_model_callback=after_model_obs,
)

_config = load_config()

app = App(
    name="council_of_ancients",
    root_agent=facilitator,
    plugins=[
        ModelArmorPlugin(
            config=ModelArmorConfig(
                prompt_template_name=_config.model_armor_prompt_template,
                response_template_name=_config.model_armor_response_template,
                block_on_screening_failure=True,
            )
        )
    ],
)

root_agent = app.root_agent
