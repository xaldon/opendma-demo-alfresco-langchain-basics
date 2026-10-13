from __future__ import annotations

import re
from typing import Any

from langchain_core.documents import Document


METADATA_KEYS = [
    "opendma:Title",
    "opendma:CheckedOut",
    "alfresco:Site",
    "alfresco:Path",
    "alfresco:cm:name",
    "alfresco:cm:creator",
    "source",
]


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r", " ").replace("\n", " ")
    return re.sub(r"\s+", " ", text).strip()


def truncate(text: str, length: int = 400) -> str:
    normalized = normalize_whitespace(text)
    if len(normalized) <= length:
        return normalized
    return normalized[: length - 3].rstrip() + "..."


def message_text(message: Any) -> str:
    """Extract printable text from common LangChain message shapes."""
    content = getattr(message, "content", message)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            else:
                parts.append(str(item))
        return "\n".join(parts)

    text_attr = getattr(message, "text", None)
    if text_attr is not None and not callable(text_attr):
        return str(text_attr)

    return str(content)


def print_document_preview(document: Document, index: int | None = None) -> None:
    prefix = f"Result {index}" if index is not None else "Document"
    print(prefix)
    print(f"Title: {document.metadata.get('opendma:Title')}")
    print(f"Site: {document.metadata.get('alfresco:Site')}")
    print(f"Path: {document.metadata.get('alfresco:Path')}")
    print(f"Source: {document.metadata.get('source')}")
    print(f"Preview: {truncate(document.page_content)}")


def print_metadata_sample(documents: list[Document], limit: int = 3) -> None:
    if not documents:
        return

    print()
    print("Metadata sample:")
    for index, document in enumerate(documents[:limit], start=1):
        print(f"Chunk {index}:")
        for key in METADATA_KEYS:
            value = document.metadata.get(key)
            if value is not None:
                print(f"  {key}: {value}")
    print()
