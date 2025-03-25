"""
user.py

Code for managing user data
"""

import hashlib
import sys
from uuid import uuid4
from typing import TypedDict
import secrets

from first_mate.logic.ical_analysis import download_ical
from .data import get_data, save_data
from base64 import b64encode


class User(TypedDict):
    """User data dictionary"""

    zid: str
    """zID"""

    sessions: list[int]
    """List of session IDs for a user"""

    display_name: str
    """Display name, shown to other users"""

    public_description: str
    """Public profile text, shown under name"""

    private_description: str
    """Private profile text, only shown to users who have been matched with"""

    password_hash: str
    """Hash for user's password"""

    password_salt: str
    """Salt for user's password"""

    calendar: str
    """String containing the user's calendar in ical format"""

    degrees: list[str]
    """List of degrees that the user is studying"""

    likes: list[str]
    """List of zIDs that the user has liked"""


def make_session_id() -> int:
    return secrets.randbelow(sys.maxsize)


def hash_and_salt(password: str, salt: str) -> str:
    hashed_bytes = hashlib.sha256(f"{salt}{password}".encode()).digest()
    return b64encode(hashed_bytes).decode()


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
) -> int | None:
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
        session ID if user registered successfully, else None to indicate user
        already exists
    """
    user_with_zid = get_user_by_zid(zid)
    if user_with_zid:
        return login_user(zid, password)

    # Hash and salt password
    salt = str(uuid4())
    hashed = hash_and_salt(password, salt)

    session_id = make_session_id()

    user_data: User = {
        "zid": zid,
        "display_name": display_name,
        "public_description": "",
        "private_description": "",
        "password_hash": hashed,
        "password_salt": salt,
        "calendar": download_ical(ical_url),
        "degrees": degrees,
        "sessions": [session_id],
        "likes": [],
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
    hashed = hash_and_salt(password, salt)

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
