"""
ical_analysis.py

Analyse an iCal file given its URL.
"""


from pathlib import Path


def download_ical(url: str) -> Path:
    """
    Download the given ical file and return its location.

    It should be downloaded to the `icals` directory.

    Parameters
    ----------
    url : str
        URL for calendar to download

    Path
        Path to downloaded ical file on file system
    """
    ...


# TODO: Code for processing ical files

