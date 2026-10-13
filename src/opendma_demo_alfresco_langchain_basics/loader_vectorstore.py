from __future__ import annotations

import argparse
import logging
import sys
import warnings

from langchain.chat_models import init_chat_model
from langchain.embeddings import init_embeddings
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_opendma import AlfrescoLoader

from opendma_demo_alfresco_langchain_basics.config import load_config
from opendma_demo_alfresco_langchain_basics.content_handlers import build_content_handler
from opendma_demo_alfresco_langchain_basics.output import message_text, print_metadata_sample


SYSTEM_PROMPT = (
    "You answer questions using documents retrieved from Alfresco Content Services. "
    "Use only the provided context. If the context does not contain the answer, "
    "say that you do not know."
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load one Alfresco site into an in-memory vector store and ask questions."
    )
    parser.add_argument("site", help="Alfresco site short name to load, for example 'swsdp'.")
    parser.add_argument(
        "--question",
        help="Ask one question, print the answer, and exit instead of entering the loop.",
    )
    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="Number of chunks to retrieve for each question. Default: 5.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show third-party INFO, WARNING, and conversion messages.",
    )
    return parser.parse_args(argv)


def configure_verbosity(verbose: bool) -> None:
    if verbose:
        logging.disable(logging.NOTSET)
        return

    logging.disable(logging.WARNING)
    warnings.filterwarnings("ignore")


def load_site_documents(site: str) -> list[Document]:
    config = load_config()
    loader = AlfrescoLoader(
        endpoint=config.endpoint,
        username=config.username,
        password=config.password,
        repository_id=config.repository_id,
        sites=[site],
        content_handlers=[build_content_handler()],
    )
    return loader.load()


def build_vector_store(documents: list[Document]) -> InMemoryVectorStore:
    config = load_config()
    embeddings = init_embeddings(config.embedding_model)
    vector_store = InMemoryVectorStore(embeddings)
    vector_store.add_documents(documents)
    return vector_store


def answer_question(
    question: str,
    vector_store: InMemoryVectorStore,
    k: int,
) -> str:
    config = load_config()
    chat_model = init_chat_model(config.chat_model, temperature=0)
    context = vector_store.similarity_search(question, k=k)
    docs_content = "\n\n---\n\n".join(document.page_content for document in context)
    response = chat_model.invoke(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Question: {question}\n\nContext:\n{docs_content}",
            },
        ]
    )
    return message_text(response)


def run_question_loop(vector_store: InMemoryVectorStore, k: int) -> None:
    while True:
        question = input("Question: ").strip()
        if question.lower() in {"exit", "quit"}:
            return
        if not question:
            print("Use 'exit' or 'quit' to end the application")
            continue

        answer = answer_question(question, vector_store, k)
        print("Answer:")
        print(answer)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    configure_verbosity(args.verbose)
    print(
        f"Ingesting Alfresco site '{args.site}' and building an in-memory vector store. "
        "This can take some time."
    )
    documents = load_site_documents(args.site)
    print(f"Loaded {len(documents)} document chunks from site '{args.site}'.")
    print_metadata_sample(documents)

    vector_store = build_vector_store(documents)
    if args.question:
        print("Answer:")
        print(answer_question(args.question, vector_store, args.k))
        return 0

    run_question_loop(vector_store, args.k)
    return 0


if __name__ == "__main__":
    sys.exit(main())
