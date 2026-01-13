import json
from typing import Literal

ExportFormat = Literal["text", "json"]


def export_session(
    session: dict,
    messages: list[dict],
    fmt: ExportFormat = "text",
) -> str:
    if fmt == "json":
        return json.dumps(
            {
                "id": session["id"],
                "title": session.get("title"),
                "created_at": session["created_at"],
                "messages": messages,
            },
            indent=2,
            ensure_ascii=False,
        )

    # === Plain text ===
    lines = [f"=== Chat Session {session['id']} ==="]

    if session.get("title"):
        lines.append(f"Title: {session['title']}")

    lines.append(f"Created at: {session['created_at']}")
    lines.append("")

    for m in messages:
        role = "You" if m["role"] == "user" else "Assistant"
        ts = m["created_at"]
        lines.append(f"[{ts}] {role}: {m['message']}")

    return "\n".join(lines)
