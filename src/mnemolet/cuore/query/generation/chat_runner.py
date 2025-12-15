from mnemolet.cuore.query.generation.chat_session import ChatSession


def run_chat_turn(
    *,
    retriever,
    generator,
    user_input: str,
    initial_messages=None,
    session_id=None,
    history_store=None,
    stream: bool = True,
):
    """
    Run a single chat turn (user => assistant).
    """

    session = ChatSession(
        retriever=retriever,
        generator=generator,
    )

    if initial_messages:
        session.load_history(initial_messages)

    # save user msg
    if history_store and session_id:
        history_store.add_message(session_id, "user", user_input)

    assistant_msg = []
    for chunk in session.ask(user_input):
        assistant_msg.append(chunk)
        if stream:
            yield chunk
    answer = "".join(assistant_msg)

    # save assistant msg
    if history_store and session_id:
        history_store.add_message(session_id, "assistant", answer)

    if not stream:
        return answer
