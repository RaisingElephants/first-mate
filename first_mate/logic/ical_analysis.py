"""
ical_analysis.py

Analyse an iCal file given its URL.
"""
import requests
from icalendar import Calendar


def download_ical(url: str) -> str:
    """
    Download the given ical file and return its contents.

    Parameters
    ----------
    url : str
        URL for calendar to download
    """
    res = requests.get(url)

    text = res.text
    return text


def calendar_events(ical_str: str):
    calendar: Calendar = Calendar.from_ical(ical_str)

    for event in calendar.events:
        print(event)

# TODO: Code for processing ical files

