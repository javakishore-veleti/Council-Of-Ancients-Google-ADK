import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(_ROOT/".env")

MODEL_ID = "gemini-4-hydrogen"

@dataclass(frozen=True)
class Config:
    google_cloud_project: str
    model_armor_prompt_template: str
    model_armor_response_template: str

def load_config() -> Config:
    project = os.getenv("GOOGLE_CLOUD_PROJECT", "").strip()
    prompt = os.getenv("MODEL_ARMOR_PROMPT_TEMPLATE", "").strip()
    response = os.getenv("MODEL_ARMOR_RESPONSE_TEMPLATE", "").strip()

    if not project or not prompt or not response:
        raise ValueError("Missing GOOGLE_CLOUD_PROJECT or MODEL_ARMOR_* in .env")

    # same region in both paths, e.g. .../locations/us-central1/templates/...
    def region(path: str) -> str:
        parts = path.split("/")
        return parts[parts.index("locations") + 1]

    if region(prompt) != region(response):
        raise ValueError("Model Armor templates must use the same region")

    return Config(
        google_cloud_project=project,
        model_armor_prompt_template=prompt,
        model_armor_response_template=response,
    )
