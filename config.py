from pathlib import Path
import os
from dotenv import load_dotenv

# Always read the .env at the repo root, no matter which project or cwd runs.
load_dotenv(Path(__file__).resolve().parent / ".env")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
