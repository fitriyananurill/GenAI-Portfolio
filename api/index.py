"""Vercel entrypoint: expose the Flask app from the repo root."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app  # noqa: E402,F401
