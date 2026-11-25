from google.adk.agents.llm_agent import Agent

from ..config import MODEL_ID
from ..observability_hooks import after_model_obs

PLATO_INSTRUCTION = """
You are Plato. Argue from ethics, virtue, and the good of the community.
Keep answers concise and in character.
"""

plato = Agent(
    name="plato",
    model=MODEL_ID,
    mode="single_turn",
    description="Plato of Athens: ethics, virtue, and the common good.",
    static_instruction=PLATO_INSTRUCTION,
    after_model_callback=after_model_obs,
)
