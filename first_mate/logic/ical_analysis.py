import logging
from datetime import datetime, timedelta
import hashlib
from pprint import pprint
from typing import Literal

import icalendar
import recurring_ical_events
import requests

from .class_analysis import ClassEvent, event_to_class_info
from first_mate.consts import LOCAL_TZ


log = logging.getLogger(__name__)


def convert_webcal_to_https(url: str) -> str:
    """Convert `webcal://` URL to `https://`"""
    if url.startswith("webcal://"):
        return url.replace("webcal://", "https://")
    return url


def download_ical(url: str) -> str:
    """
    Given a URL, download the calendar stored at it

    Parameters
    ----------
    url : str
        URL to download

    Returns
    -------
    str
        ical string
    """
    response = requests.get(convert_webcal_to_https(url))
    response.raise_for_status()
    return response.text


def create_event_hash(event):
    """Create a unique hash for an event to detect duplicates"""
    # Combine important fields to create a unique signature
    signature = f"{event['summary']}|{event['start_time']}|{event['end_time']}|{event['location']}|{event['day_of_week']}"
    return hashlib.md5(signature.encode()).hexdigest()


def get_week_range(week_offset: int = 0) -> tuple[datetime, datetime]:
    """
    Returns the start and end times for this week.
    """
    now = datetime.now(LOCAL_TZ) + timedelta(days=week_offset * 7)
    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)
    return start_of_week, end_of_week


def time_is_this_week(t: datetime) -> bool:
    """Returns whether the given time occurs during this week

    Parameters
    ----------
    t : datetime
        time
    """
    start, end = get_week_range()
    return start <= t <= end


def get_event_timing(
    ev: icalendar.Component,
    option: Literal["dtstart", "dtend"],
) -> datetime | None:
    """Returns start time of event

    Parameters
    ----------
    ev : icalendar.Event
        event to check

    Returns
    -------
    datetime
        Start time
    None
        Start time failed to parse
    """
    timing = ev.get(option)
    if timing is None:
        return None
    dt: datetime = timing.dt

    # If already has timezone info
    if dt.tzinfo is not None:
        return dt.astimezone(LOCAL_TZ)
    else:
        # If naive datetime
        return LOCAL_TZ.localize(dt)


def handle_event(ev: icalendar.Component) -> ClassEvent | None:
    """Given an event object, get its info and convert it into a ClassEvent
    dict if possible

    Parameters
    ----------
    ev : icalendar.Event
        Event to process

    Returns
    -------
    ClassEvent | None
        class info, or None if parsing failed
    """
    summary = str(ev.get("summary", ""))
    description = str(ev.get("description", ""))
    location = str(ev.get("location", ""))
    log.info(f"Event: {summary}, {description}, {location}")

    # Skip empty events
    if not summary.strip():
        return None

    start = get_event_timing(ev, "dtstart")
    end = get_event_timing(ev, "dtend")
    if not start or not end:
        return None

    return event_to_class_info(
        summary,
        description,
        location,
        int(start.timestamp()),
        int(end.timestamp()),
    )


def find_class_events(
    calendar: str, start: datetime, end: datetime
) -> list[ClassEvent]:
    """Given a calendar, return a list of class events that occur this week.

    Parameters
    ----------
    calendar : str
        calendar (ical format string)

    Returns
    -------
    list[ClassEvent]
        list of event dictionaries
    """
    ical = icalendar.Calendar.from_ical(calendar)

    events_this_week = recurring_ical_events.of(ical).between(start, end)

    classes_this_week = []

    for event in events_this_week:
        class_info = handle_event(event)
        if class_info is not None:
            classes_this_week.append(class_info)

    return classes_this_week


if __name__ == "__main__":
    calendar = open("calendars/ben.ics").read()

    logging.basicConfig(level="INFO")
    start = datetime(2025, 3, 1)
    end = datetime.now()
    pprint(find_class_events(calendar, start, end))
