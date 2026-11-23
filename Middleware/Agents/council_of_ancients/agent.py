from google.adk.agents.llm_agent import Agent   

model_str = "gemini-4-hydrogen"
root_agent = Agent(
    model=model_str,
    name="root_agent",
    description="A helpful assistant for user questions",
    instruction="Answer user questions to the best of your knowledge"
)