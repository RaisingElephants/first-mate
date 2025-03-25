"""
Code for analysing classes (the university type, not the Python type)
to determine info about them.
"""

from datetime import datetime
import re
from typing import TypeVar, Protocol, TypedDict

import icalendar


class SupportsIn(Protocol):
    def __contains__(self, other: object) -> bool: ...


class ClassEvent(TypedDict):
    course_code: str
    """Course code eg COMP1531"""
    class_type: str
    """Class type eg 'Tutorial'"""
    location: str
    """Location eg Oboe Lab"""
    start: int
    """Start time, as UNIX timestamp"""
    end: int
    """End time, as UNIX timestamp"""


T = TypeVar("T", SupportsIn, str)


def extract_course_code(summary: str) -> str | None:
    """Extract course code from summary like 'MATH1081 Tutorial'"""
    match = re.search(r"([A-Z]{4}\d{4}[A-Za-z]*)", summary)
    if match:
        return match.group(1)
    return None


def any_in(needles: list[T], haystack: T) -> bool:
    for needle in needles:
        if needle in haystack:
            return True

    return False


def determine_event_type(summary: str, description: str) -> str | None:
    """Determine type of class for event

    Returns a string such as "Tutorial" or "Exam" and the like

    Parameters
    ----------
    summary : str
        event summary
    description : str
        event description

    Returns
    -------
    str | None
        event type, or None if not matched
    """
    text = f"{summary} {description}".lower()

    mappings = {
        "Lecture": ["lect", "sem"],
        "Tutorial": ["tut"],
        "Lab": ["lab"],
        "Exam": ["exam", "test", "quiz", "assessment"],
        "Workshop": ["workshop"],
    }

    for type, matchers in mappings.items():
        if any_in(matchers, text):
            return type

    return None


def event_to_class_info(
    summary: str,
    description: str,
    location: str,
    start: int,
    end: int,
) -> ClassEvent | None:
    """Given info about an event, attempt to parse info about a class.

    If the conversion fails, return None, indicating it is an unknown class
    type, or maybe not a class at all.

    Parameters
    ----------
    summary : str
        Title of event
    description : str
        Description for event
    location : str
        Event location
    start : int
        Start time (as unix timestamp)
    end : int
        End time (as unix timestamp)

    Returns
    -------
    ClassEvent | None
        ClassEvent dict if parsing succeeds, otherwise None
    """
    # Reject events where we can't find a course code
    course_code = extract_course_code(summary)
    if not course_code:
        return None

    class_type = determine_event_type(summary, description)
    if not class_type:
        return None

    return {
        "course_code": course_code,
        "class_type": class_type,
        "location": location,
        "start": start,
        "end": end,
    }
