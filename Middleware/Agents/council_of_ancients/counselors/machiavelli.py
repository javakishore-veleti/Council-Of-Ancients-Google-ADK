from google.adk.agents.llm_agent import Agent

from ..config import MODEL_ID
from ..observability_hooks import after_model_obs

MACHIAVELLI_INSTRUCTION = """
You are Niccolò Machiavelli. Focus on power, incentives, and what works in practice.
Keep answers concise and in character.
"""

machiavelli = Agent(
    name="machiavelli",
    model=MODEL_ID,
    mode="single_turn",
    description="Niccolò Machiavelli: power, incentives, and practical outcomes.",
    static_instruction=MACHIAVELLI_INSTRUCTION,
    after_model_callback=after_model_obs,
)
