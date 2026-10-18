"""Reads backend/.env once and exposes the settings as plain constants."""
import os

from dotenv import load_dotenv
from llm_client import MODEL  # re-exported so the rest of the backend reads settings from one place

load_dotenv()

MAX_HISTORY_TURNS = int(os.getenv("MAX_HISTORY_TURNS", "6"))
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5500")
PROMPTS_FILE = os.getenv("PROMPTS_FILE", os.path.join(os.path.dirname(__file__), "prompts.json"))
GUARDRAILS_FILE = os.path.join(os.path.dirname(__file__), os.getenv("GUARDRAILS_FILE", "guardrails.json"))
MODELS_FILE = os.path.join(os.path.dirname(__file__), os.getenv("MODELS_FILE", "models.json"))
