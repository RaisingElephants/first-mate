"""
user.py

Code for managing user data
"""
from typing import TypedDict


class User(TypedDict):
    """User data dictionary"""

    zid: str
    """zID"""

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
