from google.adk.agents.llm_agent import Agent

from ..config import MODEL_ID
from ..observability_hooks import after_model_obs

DESCARTES_INSTRUCTION = """
You are René Descartes. Use methodical doubt and first principles.
Ask what can be proven. Keep answers concise and in character.
"""

descartes = Agent(
    name="descartes",
    model=MODEL_ID,
    mode="single_turn",
    description="René Descartes: methodical doubt and first principles.",
    static_instruction=DESCARTES_INSTRUCTION,
    after_model_callback=after_model_obs,
)
