"""
logic/event_overlap.py

Find times when users events overlap.
"""

from datetime import datetime
from typing import TypedDict

from first_mate.logic.class_analysis import ClassEvent
from first_mate.logic.data import get_data
from first_mate.logic.ical_analysis import find_class_events
from first_mate.logic.user import User


ROUGHLY_THE_SAME_TIME = 15 * 60
"""
Time used to determine whether events start/finish at the same time.

15 minutes.
"""


ENOUGH_TIME_FOR_MEET_UP = 60 * 60
"""
Time used to determine whether a user has enough free time to actually meet up.

60 minutes.
"""


class MatchInfo(TypedDict):
    time: int
    """Time of match"""
    before: bool
    """Whether the meet-up should happen before or after"""
    class_description: str
    """Description of class"""


class Mate(TypedDict):
    zid: str
    """zID of mate"""
    matches: list[MatchInfo]
    """List of matches"""


def times_are_similar(t1: int, t2: int) -> bool:
    """Return whether the two given times are similar

    Parameters
    ----------
    t1 : int
        first time
    t2 : int
        second time

    Returns
    -------
    bool
        whether times are similar
    """
    return abs(t1 - t2) <= ROUGHLY_THE_SAME_TIME


def is_free_before(calendar: list[ClassEvent], time: int) -> bool:
    """
    Return whether there is free time before the given time on the calendar
    """
    # They have a full day of free time to start with
    free_time_before = 24 * 60 * 60

    for event in calendar:
        if event["start"] >= time:
            # Event starts at or after this event, so doesn't count
            continue
        else:
            # Technically this allows a user to have a negative amount of free
            # time, but that should still work with our algorithm
            free_time_between = time - event["end"]
            if free_time_between < free_time_before:
                free_time_before = free_time_between

    return free_time_before >= ENOUGH_TIME_FOR_MEET_UP


# Code duplication, but can't think of a better way :(
def is_free_after(calendar: list[ClassEvent], time: int) -> bool:
    """
    Return whether there is free time after the given time on the calendar
    """
    # They have a full day of free time to start with
    free_time_after = 24 * 60 * 60

    for event in calendar:
        if event["end"] <= time:
            # Event ends at or before this event, so doesn't count
            continue
        else:
            # Technically this allows a user to have a negative amount of free
            # time, but that should still work with our algorithm
            free_time_between = event["start"] - time
            if free_time_between < free_time_after:
                free_time_after = free_time_between

    return free_time_after >= ENOUGH_TIME_FOR_MEET_UP


def get_matching_times(
    me: User,
    them: User,
    start: datetime,
    end: datetime,
) -> list[MatchInfo]:
    my_classes = find_class_events(me["calendar"], start, end)
    their_classes = find_class_events(them["calendar"], start, end)

    matches: list[MatchInfo] = []

    for my_class in my_classes:
        for their_class in their_classes:
            # Similar start times
            if times_are_similar(my_class["start"], their_class["start"]):
                latest_finish = min(my_class["start"], their_class["start"])
                if is_free_before(my_classes, latest_finish) and is_free_before(
                    their_classes, latest_finish
                ):
                    matches.append(
                        {
                            "time": my_class["start"],
                            "before": True,
                            "class_description": f"{my_class['course_code']} {my_class['class_type']}",
                        }
                    )

            # Similar end times
            if times_are_similar(my_class["end"], their_class["end"]):
                latest_finish = max(my_class["end"], their_class["end"])
                if is_free_after(my_classes, latest_finish) and is_free_after(
                    their_classes, latest_finish
                ):
                    matches.append(
                        {
                            "time": my_class["start"],
                            "before": False,
                            "class_description": f"{my_class['course_code']} {my_class['class_type']}",
                        }
                    )

    return matches


def find_mates(
    me: User,
    start: datetime,
    end: datetime,
) -> list[Mate]:
    """
    Find possible mates for the user between the start and end dates

    This searches for other users with events which meet the following
    criteria:

    * Both users are free before the event and events start at the same time,
    * Or, both users are free after the event and events end at the same time.

    Other strategies to consider:
    * Both have at around an hour, with one person's class finishing, then the
      other's class starting an hour later (not implemented).

    Matches are sorted based on distance between their event locations (TODO).

    Parameters
    ----------
    me : User
        user to find mates for
    start : datetime
        start time
    end : datetime
        end time

    Returns
    -------
    list[MateInfo]
        list of matches
    """
    mates: list[Mate] = []

    for other_user in get_data()["users"]:
        if other_user["zid"] == me["zid"]:
            # Can't match with self
            continue
        matching_times = get_matching_times(me, other_user, start, end)
        if len(matching_times):
            # Add them to the list of potential mates
            mates.append(
                {
                    "zid": other_user["zid"],
                    "matches": matching_times,
                }
            )

    # Sort by length of "matches" value, from high to low
    return sorted(mates, key=lambda mate: len(mate["matches"]), reverse=True)
