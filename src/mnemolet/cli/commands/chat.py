import logging

import click

from mnemolet.cli.commands.chat_history import history
from mnemolet.config import (
    EMBED_MODEL,
    MIN_SCORE,
    OLLAMA_MODEL,
    OLLAMA_URL,
    QDRANT_COLLECTION,
    QDRANT_URL,
    TOP_K,
)
from mnemolet.cuore.storage.chat_history import ChatHistory

from .utils import requires_qdrant

logger = logging.getLogger(__name__)


@click.group()
def chat():
    """
    Chat commands.
    """
    pass


chat.add_command(history)


@chat.command("start")
@click.option(
    "--top-k",
    default=TOP_K,
    show_default=True,
    help="Number of context chunks for generation.",
)
@click.option(
    "--ollama-url",
    default=OLLAMA_URL,
    show_default=True,
    help="Ollama url",
)
@click.option(
    "--ollama-model",
    default="llama3",
    show_default=True,
    help="Local model to use for generation.",
)
@click.option(
    "--min-score", default=MIN_SCORE, show_default=True, help="Minimum score threshold."
)
@requires_qdrant
def start(ollama_url: str, top_k: int, ollama_model: str, min_score: float):
    """
    Start interactive chat session with the local LLM.
    """
    from mnemolet.cuore.query.generation.local_generator import get_llm_generator
    from mnemolet.cuore.query.retrieval.retriever import get_retriever

    retriever = get_retriever(
        url=QDRANT_URL,
        collection=QDRANT_COLLECTION,
        model=EMBED_MODEL,
        top_k=top_k,
        min_score=min_score,
    )

    generator = get_llm_generator(OLLAMA_URL, ollama_model)

    history = ChatHistory()
    session_id = history.create_session()
    logger.info(f"Chat session started (id={session_id})\n")
    click.echo("Starting chat. Type 'exit' to quit.\n")

    run_chat(
        retriever=retriever,
        generator=generator,
        initial_messages=None,
        session_id=session_id,
        history_store=history,
    )


@chat.command("replay")
@click.argument(
    "session_id",
    type=int,
)
@requires_qdrant
def replay(session_id):
    """
    Continue a chat using messages from a previous session.
    """
    from mnemolet.cuore.query.generation.local_generator import get_llm_generator
    from mnemolet.cuore.query.retrieval.retriever import get_retriever

    h = ChatHistory()
    messages = h.get_messages(session_id)

    if not messages:
        click.echo(f"No messages found for session {session_id}")
        return

    formatted = [{"role": r, "messages": m} for r, m, _ in messages]

    # print previous session messages
    if messages:
        click.echo("Loaded previous session history: \n")
        for r, m, _ in messages:
            click.echo(f"{r}: {m}\n")

    retriever = get_retriever(
        url=QDRANT_URL,
        collection=QDRANT_COLLECTION,
        model=EMBED_MODEL,
        top_k=TOP_K,
        min_score=MIN_SCORE,
    )

    generator = get_llm_generator(OLLAMA_URL, OLLAMA_MODEL)

    run_chat(
        retriever=retriever,
        generator=generator,
        initial_messages=formatted,
        session_id=session_id,
        history_store=h,
    )


def run_chat(
    retriever,
    generator,
    initial_messages=None,
    session_id=None,
    history_store=None,
):
    from mnemolet.cuore.query.generation.chat_session import ChatSession

    session = ChatSession(
        retriever=retriever,
        generator=generator,
    )

    logger.debug(f"Initial messages: {initial_messages}")
    if initial_messages:
        for msg in initial_messages:
            session.append_to_history(msg["role"], msg["messages"])

    click.echo("Starting chat. Type 'exit' to quit.\n")

    while True:
        try:
            user_input = click.prompt("> ", type=str)

            if user_input.lower() in ("exit", "quit", ":q"):
                click.echo("Bye")
                break

            # save user msg
            if history_store and session_id:
                history_store.add_message(session_id, "user", user_input)

            # stream response
            click.echo("assistant: ", nl=False)
            assistant_msg = ""

            for chunk in session.ask(user_input):
                click.echo(chunk, nl=False)
                assistant_msg += chunk

            # save assistant msg
            if history_store and session_id:
                history_store.add_message(session_id, "assistant", assistant_msg)

            click.echo()

        except (KeyboardInterrupt, EOFError):
            click.echo("\n Exiting chat..")
            break
