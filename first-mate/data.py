"""
Data store
"""
import json
from typing import TypedDict, cast

from .user import User


class Data(TypedDict):
    users: list[User]


DATASTORE_FILE = "data.json"


__data_cache : Data | None = None
"""Cache for data, to prevent loading it from disk every time"""

def get_data():
    """Load data store from JSON file"""
    global __data_cache
    if __data_cache:
        return __data_cache
    with open(DATASTORE_FILE, "r") as f:
        __data_cache = cast(Data, json.load(f))
        return __data_cache


def save_data():
    with open(DATASTORE_FILE, "w") as f:
        assert __data_cache is not None
        json.dump(__data_cache, f)
