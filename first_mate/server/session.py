from flask import session

from first_mate.logic.user import get_user_by_session_id


def is_user_logged_in() -> bool:
    session_id: int | None = session.get("session_id")

    if session_id is None:
        return False

    # Validate session
    user_with_session = get_user_by_session_id(session_id)
    if user_with_session is None:
        # Invalid session ID
        del session["session_id"]
        session.modified = True
        return False
    else:
        return True
