"""
user.py

Code for managing user data
"""

import hashlib
import sys
from uuid import uuid4
from typing import TypedDict
import secrets
from .data import get_data, save_data


class User(TypedDict):
    """User data dictionary"""

    zid: str
    """zID"""

    sessions: list[int]
    """List of session IDs for a user"""

    display_name: str
    """Display name, shown to other users"""

    password_hash: str
    """Hash for user's password"""

    password_salt: str
    """Salt for user's password"""

    ical_url: str
    """URL for the user's UNSW calendar"""

    degrees: list[str]
    """List of degrees that the user is studying"""


def make_session_id() -> int:
    return secrets.randbelow(sys.maxsize)


def get_user_by_zid(zid: str) -> User | None:
    """Return a user dict given their user ID

    Parameters
    ----------
    zid : str
        zID to search for

    Returns
    -------
    User | None
        user data, or None if not found
    """
    for user in get_data()["users"]:
        if user["zid"] == zid:
            return user

    return None


def get_user_by_session_id(session_id: int) -> User | None:
    """Return a user given one of their session IDs

    Parameters
    ----------
    session_id : int
        session ID

    Returns
    -------
    User | None
        User, if found, else None
    """
    for user in get_data()["users"]:
        if session_id in user["sessions"]:
            return user

    return None


def register_user(
    zid: str,
    display_name: str,
    password: str,
    ical_url: str,
    degrees: list[str],
) -> int:
    """
    Register a user, storing their password, and generating a session_id

    Parameters
    ----------
    zid : str
        zID
    display_name : str
        Display name
    password : str
        Password to store
    ical_url : str
        ical URL
    degrees : list[str]
        list of degrees for the user

    Returns
    -------
    int
        session ID
    """
    # Hash and salt password
    salt = str(uuid4())
    hashed = hashlib.sha256(f"{salt}{password}".encode()).digest().decode()

    session_id = make_session_id()

    user_data: User = {
        "zid": zid,
        "display_name": display_name,
        "password_hash": hashed,
        "password_salt": salt,
        "ical_url": ical_url,
        "degrees": degrees,
        "sessions": [session_id],
    }

    data = get_data()
    data["users"].append(user_data)
    save_data()

    return session_id


def login_user(zid: str, password: str) -> int | None:
    """
    Log in an existing user, returning session ID if user is found

    Parameters
    ----------
    zid : str
        zID to sign in
    password : str
        password to authenticate with

    Returns
    -------
    int
        session ID
    None
        Indicates invalid credentials
    """
    user = get_user_by_zid(zid)
    if user is None:
        return None

    # Hash password
    salt = user["password_salt"]
    hashed = hashlib.sha256(f"{salt}{password}".encode()).digest().decode()

    if hashed != user["password_hash"]:
        return None

    session_id = make_session_id()

    user["sessions"].append(session_id)
    save_data()

    return session_id


def logout_user(session_id: int) -> bool:
    """Given a session ID, invalidate it

    Parameters
    ----------
    session_id : int
        session ID to invalidate

    Returns
    -------
    bool
        whether the session was valid to begin with
    """
    user = get_user_by_session_id(session_id)
    if user is None:
        return False

    user["sessions"].remove(session_id)
    save_data()
    return True
