from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


DEFAULT_ENDPOINT = "http://localhost:7070/opendma/alf"
DEFAULT_REPOSITORY = "Alfresco"
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin"
DEFAULT_CHAT_MODEL = "openai:gpt-4o-mini"
DEFAULT_EMBEDDING_MODEL = "openai:text-embedding-3-large"


@dataclass(frozen=True)
class AppConfig:
    endpoint: str
    repository_id: str
    username: str
    password: str
    chat_model: str
    embedding_model: str


def load_config() -> AppConfig:
    """Load shared configuration from .env and environment variables."""
    load_dotenv()
    return AppConfig(
        endpoint=os.getenv("ALFRESCO_OPENDMA_ENDPOINT", DEFAULT_ENDPOINT),
        repository_id=os.getenv("ALFRESCO_OPENDMA_REPOSITORY", DEFAULT_REPOSITORY),
        username=os.getenv("ALFRESCO_USERNAME", DEFAULT_USERNAME),
        password=os.getenv("ALFRESCO_PASSWORD", DEFAULT_PASSWORD),
        chat_model=os.getenv("LANGCHAIN_CHAT_MODEL", DEFAULT_CHAT_MODEL),
        embedding_model=os.getenv("LANGCHAIN_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL),
    )

