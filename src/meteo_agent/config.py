from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DEFAULT_BASE_URL = "http://localhost:11434/v1"
DEFAULT_API_KEY = "ollama"
DEFAULT_MODEL = "qwen2.5:7b"
DEFAULT_DB_PATH = "data/meteobeguda.sqlite"


def base_url() -> str:
    return os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE_URL)


def api_key() -> str:
    return os.environ.get("OPENAI_API_KEY", DEFAULT_API_KEY)


def model_name() -> str:
    return os.environ.get("MODEL", DEFAULT_MODEL)


def database_path() -> Path:
    return Path(os.environ.get("METEO_DB_PATH", DEFAULT_DB_PATH))


@lru_cache
def openai_client():
    from openai import OpenAI

    return OpenAI(base_url=base_url(), api_key=api_key())


def chat_model(**overrides):
    from langchain_openai import ChatOpenAI

    settings = dict(model=model_name(), base_url=base_url(), api_key=api_key())
    settings.update(overrides)
    return ChatOpenAI(**settings)
