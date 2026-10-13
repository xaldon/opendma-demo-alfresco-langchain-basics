from __future__ import annotations

from langchain_opendma.content_handlers import UnstructuredLoaderContentHandler


def build_content_handler() -> UnstructuredLoaderContentHandler:
    """Create the content handler used consistently by all examples."""
    return UnstructuredLoaderContentHandler(
        chunking_strategy="by_title",
        max_characters=4000,
        new_after_n_chars=3000,
        combine_text_under_n_chars=1000,
    )

