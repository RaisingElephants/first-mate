"""
consts.py

Constants shared across app
"""

import os
import pytz


def dev():
    """
    Returns whether the server is running in dev mode.
    """
    return os.getenv("FIRSTMATE_DEV") is not None


LOCAL_TZ = pytz.timezone("Australia/Sydney")


DEGREES_LIST = [
    "Computer Science",
    "Software Engineering",
    "Computer Engineering",
    "Math",
]
