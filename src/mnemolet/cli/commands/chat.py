import logging

import click

from mnemolet.cli.commands.chat_history import history
from mnemolet.config import (
    EMBED_MODEL,
    MIN_SCORE,
    OLLAMA_MODEL,
    OLLAMA_PROMPT,
    OLLAMA_URL,
    QDRANT_COLLECTION,
    QDRANT_URL,
    TOP_K,
)
from mnemolet.cuore.storage.chat_history import ChatHistory

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
    default=OLLAMA_MODEL,
    show_default=True,
    help="Local model to use for generation.",
)
@click.option(
    "--min-score", default=MIN_SCORE, show_default=True, help="Minimum score threshold."
)
@click.option(
    "--session-id",
    type=int,
    default=None,
    help="ID of a previous chat session to continue (replay).",
)
def start(
    ollama_url: str,
    top_k: int,
    ollama_model: str,
    min_score: float,
    session_id: int | None,
):
    """
    Start interactive chat session with the local LLM.
    """
    from mnemolet.cuore.query.generation.local_generator import get_llm_generator
    from mnemolet.cuore.query.retrieval.retriever import get_retriever

    h = ChatHistory()
    initial_messages = None

    if session_id is not None:
        # === Replay logic ===
        if not h.session_exists(session_id):
            click.echo(f"There is no session: {session_id}")
            return

        messages = h.get_messages(session_id)

        if not messages:
            click.echo(f"No messages found for session {session_id}")
            return

        initial_messages = [{"role": r, "message": m} for r, m, _ in messages]

        if messages:
            click.echo("Loaded previous session history: \n")
            for r, m, _ in messages:
                click.echo(f"{r}: {m}\n")

        logger.info(f"[CHAT]: Replaying chat session (id={session_id})")

    else:
        # === Start new session ===
        session_id = h.create_session()
        logger.info(f"Chat session started (id={session_id})\n")

    retriever = get_retriever(
        url=QDRANT_URL,
        collection=QDRANT_COLLECTION,
        model=EMBED_MODEL,
        top_k=top_k,
        min_score=min_score,
    )

    generator = get_llm_generator(
        OLLAMA_URL,
        ollama_model,
        OLLAMA_PROMPT,
    )

    run_chat(
        retriever=retriever,
        generator=generator,
        initial_messages=initial_messages,
        session_id=session_id,
        history=h,
    )


def run_chat(
    retriever,
    generator,
    initial_messages=None,
    session_id=None,
    history=None,
):
    from mnemolet.cuore.query.generation.chat_runner import run_chat_turn

    if retriever and not retriever.has_documents():
        click.echo("No documents indexed yet - chatting without context!")

    click.echo("Starting chat. Type 'exit' to quit.\n")

    while True:
        try:
            user_input = click.prompt("> ", type=str)

            if user_input.lower() in ("exit", "quit", ":q"):
                click.echo("Bye")
                break

            # stream response
            click.echo("assistant: ", nl=False)

            history.add_message(session_id, "user", user_input)

            assistant_chunks = []
            for c in run_chat_turn(
                retriever=retriever,
                generator=generator,
                user_input=user_input,
                messages=initial_messages,
                session_id=session_id,
                stream=True,
            ):
                assistant_chunks.append(c)
                click.echo(c, nl=False)

            history.add_message(session_id, "assistant", "".join(assistant_chunks))

        except (KeyboardInterrupt, EOFError):
            click.echo("\n Exiting chat..")
            break
