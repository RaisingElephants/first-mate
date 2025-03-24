"""
server/debug.py

Server endpoints for debugging.
"""

from flask import Blueprint, redirect

from first_mate.logic.data import clear_data
from first_mate.server.session import clear_session


debug = Blueprint("/debug", __name__)


@debug.post("/clear")
def clear():
    clear_data()
    clear_session()

    return redirect("/")
