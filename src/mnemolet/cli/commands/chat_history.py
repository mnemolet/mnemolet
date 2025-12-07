import click

from mnemolet.core.storage.chat_history import ChatHistory


@click.group("history")
def history():
    """Manage chat history."""
    pass


@history.command("list")
def list_history():
    """List all chat sessions."""
    h = ChatHistory()
    sessions = h.list_sessions()
    if not sessions:
        click.echo("No chat sessions found.")
        return
    for s in sessions:
        click.echo(f"{s['id']}: created at {s['created_at']}")

@history.command("show", help="Show chat session by ID.")
@click.argument(
    "session_id",
    type=int,
)
def show(session_id):
    h = ChatHistory()
    messages = h.get_messages(session_id)

    if not messages:
        click.echo(f"No messages found for session {session_id}.")
        return

    click.echo(f"=== Chat Session {session_id} ===")
    for m in messages:
        role = "You" if m["role"] == "user" else "Assistant"
        ts = m["created_at"]
        click.echo(f"[{ts}] {role}: {m['message']}")
