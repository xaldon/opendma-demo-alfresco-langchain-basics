from __future__ import annotations

import argparse
import sys

from langchain_opendma import AlfrescoRetriever

from opendma_demo_alfresco_langchain_basics.config import load_config
from opendma_demo_alfresco_langchain_basics.content_handlers import build_content_handler
from opendma_demo_alfresco_langchain_basics.output import print_document_preview


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run live Alfresco full-text search through OpenDMA."
    )
    parser.add_argument("query", help="Full-text query to run against Alfresco.")
    parser.add_argument(
        "--site",
        help="Optional Alfresco site short name. Without this, search the whole repository.",
    )
    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="Maximum number of LangChain document chunks to return. Default: 5.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = load_config()

    if args.site:
        print(f"Running live Alfresco full-text search in site '{args.site}'.")
    else:
        print("Running live Alfresco full-text search across the whole repository.")
    print("This is repository search through OpenDMA, not vector similarity search.")

    retriever = AlfrescoRetriever(
        endpoint=config.endpoint,
        username=config.username,
        password=config.password,
        repository_id=config.repository_id,
        sites=[args.site] if args.site else None,
        content_handlers=[build_content_handler()],
        k=args.k,
    )
    documents = retriever.invoke(args.query)
    print(f"Retrieved {len(documents)} document chunks.")

    for index, document in enumerate(documents, start=1):
        print()
        print("-" * 80)
        print_document_preview(document, index=index)

    return 0


if __name__ == "__main__":
    sys.exit(main())
