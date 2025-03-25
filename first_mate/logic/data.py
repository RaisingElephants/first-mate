"""
Data store
"""

from __future__ import annotations
import json
import os
from typing import TYPE_CHECKING, TypedDict, cast

if TYPE_CHECKING:
    from .user import User


class Data(TypedDict):
    users: list["User"]


DATA_DIR = os.getenv("FIRSTMATE_DATA", ".")
DATASTORE_FILE = f"{DATA_DIR}/data.json"


__data_cache: Data | None = None
"""Cache for data, to prevent loading it from disk every time"""


def default_data() -> Data:
    """Return the default data"""
    return {
        "users": [],
    }


def get_data() -> Data:
    """Load data store from JSON file"""
    global __data_cache
    if __data_cache:
        return __data_cache
    try:
        with open(DATASTORE_FILE, "r") as f:
            __data_cache = cast(Data, json.load(f))
            return __data_cache
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        print("Data file not found, starting from empty")
        __data_cache = default_data()
        save_data()
        return __data_cache


def save_data():
    """
    Save data to JSON file. Data is accessed from reference returned by
    get_data
    """
    with open(DATASTORE_FILE, "w") as f:
        assert __data_cache is not None
        json.dump(__data_cache, f, indent=2)


def clear_data():
    """Clear all data"""
    global __data_cache
    __data_cache = default_data()
    save_data()
