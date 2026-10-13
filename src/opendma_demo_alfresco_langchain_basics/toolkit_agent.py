from __future__ import annotations

import argparse
import sys
from typing import Any

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, ToolMessage
from langchain_opendma import AlfrescoToolkit

from opendma_demo_alfresco_langchain_basics.config import load_config
from opendma_demo_alfresco_langchain_basics.content_handlers import build_content_handler
from opendma_demo_alfresco_langchain_basics.output import message_text, truncate


SYSTEM_PROMPT = """
You answer questions using documents stored in Alfresco Content Services.

Use repository tools to find documents and inspect metadata before reading
document text. Reading document text is more expensive than listing children,
listing sites, searching, or getting metadata.

Do not answer factual repository questions unless the answer is supported by
tool results. If the repository does not contain enough information, say so.
"""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ask questions with a LangChain agent using Alfresco OpenDMA tools."
    )
    parser.add_argument(
        "--question",
        help="Ask one question, print the answer, and exit instead of entering the loop.",
    )
    return parser.parse_args(argv)


def build_agent() -> Any:
    config = load_config()
    toolkit = AlfrescoToolkit(
        endpoint=config.endpoint,
        username=config.username,
        password=config.password,
        repository_id=config.repository_id,
        content_handlers=[build_content_handler()],
    )
    model = init_chat_model(config.chat_model, temperature=0)
    return create_agent(
        model=model,
        tools=toolkit.get_tools(),
        system_prompt=SYSTEM_PROMPT,
    )


def print_step(step: dict[str, Any]) -> None:
    step_name, update = next(iter(step.items()))
    messages = update.get("messages", []) if isinstance(update, dict) else []
    if not messages:
        return

    message = messages[-1]
    tool_calls = getattr(message, "tool_calls", None)

    print()
    print(f"Step: {step_name}")
    if tool_calls:
        for tool_call in tool_calls:
            print(f"Tool call: {tool_call.get('name')}")
            print(f"Args: {tool_call.get('args')}")
    elif isinstance(message, ToolMessage):
        print(f"Tool result: {message.name}")
        print(truncate(str(message.content), 1000))
    elif isinstance(message, AIMessage):
        text = message_text(message)
        if text:
            print(truncate(text, 1000))


def ask_question(agent: Any, question: str) -> str:
    final_answer = ""
    for step in agent.stream(
        {"messages": [{"role": "user", "content": question}]},
        stream_mode="updates",
    ):
        print_step(step)
        for update in step.values():
            messages = update.get("messages", []) if isinstance(update, dict) else []
            if messages and isinstance(messages[-1], AIMessage):
                text = message_text(messages[-1])
                if text:
                    final_answer = text

    return final_answer


def run_question_loop(agent: Any) -> None:
    while True:
        question = input("Question: ").strip()
        if question.lower() in {"exit", "quit"}:
            return
        if not question:
            print("Use 'exit' or 'quit' to end the application")
            continue

        answer = ask_question(agent, question)
        print()
        print("Answer:")
        print(answer)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    agent = build_agent()

    if args.question:
        answer = ask_question(agent, args.question)
        print()
        print("Answer:")
        print(answer)
        return 0

    run_question_loop(agent)
    return 0


if __name__ == "__main__":
    sys.exit(main())
