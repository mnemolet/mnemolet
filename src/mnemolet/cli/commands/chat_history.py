import click

from mnemolet.cuore.storage.chat_history import ChatHistory


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
        click.echo(f"{s['id']}: {s['title']} - created at {s['created_at']}")


@history.command("show", help="Show chat session by ID.")
@click.argument("session_id", type=int, required=True)
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


@history.command("rm", help="Remove chat session by ID.")
@click.argument("session_id", type=int, required=True)
def remove(session_id):
    h = ChatHistory()

    if not h.session_exists(session_id):
        click.echo(f"Session {session_id} does not exist.")
        return

    click.confirm(
        f"Are you sure you want to delete session '{session_id}'?",
        abort=True,
    )
    h.delete_session(session_id)
    click.echo(f"Removed chat session {session_id}.")


@history.command("prune", help="Remove all chat sessions.")
def remove_all():
    h = ChatHistory()

    click.confirm(
        "Are you sure you want to delete all sessions?",
        abort=True,
    )
    h.delete_all_sessions()
    click.echo("All chat sessions have been deleted.")


@history.command("rename", help="Rename session by ID.")
@click.argument("session_id", type=int, required=True)
@click.argument("title", required=False)
def rename_session(session_id, title):
    h = ChatHistory()

    if not h.session_exists(session_id):
        click.echo(f"Session {session_id} does not exist.")
        return

    if not title:
        title = click.prompt("Enter new session title: ", type=str)

    title = title.strip()
    if not title:
        click.echo("Title cannot be empty.")
        return

    title = title[:60]  # limit

    h.rename_session(session_id, title)

    click.echo(f"Session {session_id} renamed to: {title}")
