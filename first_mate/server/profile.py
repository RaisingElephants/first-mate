"""
server/profile.py

Server code for showing user profiles.
"""

from datetime import datetime
import pyhtml as p
from flask import Blueprint, redirect, request

from first_mate.logic.class_analysis import ClassEvent
from first_mate.logic.data import get_data, save_data
from first_mate.logic.event_overlap import MatchInfo, get_matching_times
from first_mate.logic.ical_analysis import (
    download_ical,
    find_class_events,
    get_week_range,
)
from first_mate.logic.user import get_user_by_id
from first_mate.server.session import get_user, is_user_logged_in
from first_mate.server.util import (
    error_page,
    generate_head,
    navbar,
    profile_banner_html,
    week_offset_to_str,
)

from ..consts import LOCAL_TZ


profile = Blueprint("/profile", __name__)


@profile.get("/")
def profile_root():
    user = get_user()
    if user is None:
        return redirect("/auth/login")
    return redirect(f"/profile/{user['id']}")


def format_time(t: int) -> str:
    return datetime.fromtimestamp(t).astimezone(LOCAL_TZ).strftime("%-I:%M%p")


def calendar_event_to_html(ev: ClassEvent) -> p.div:
    start_dt = datetime.fromtimestamp(ev["start"], LOCAL_TZ)
    time_str = f"{format_time(ev['start'])} - {format_time(ev['end'])}"
    day_str = start_dt.strftime("%A %B %-d")
    return p.div(_class="calendar-event")(
        p.h2(f"{ev['course_code']} {ev['class_type']}"),
        p.div(_class="event-details")(
            p.p(
                day_str,
                p.br(),
                time_str,
            ),
            p.p(ev["location"]),
        ),
    )


def match_to_html(match: MatchInfo) -> p.div:
    start_dt = datetime.fromtimestamp(match["start"], LOCAL_TZ)
    if match["before"]:
        timing = "Before"
        starting = "Starting"
        time_str = format_time(match["start"])
    else:
        timing = "After"
        starting = "Finishing"
        time_str = format_time(match["end"])
    day_str = start_dt.strftime("%A %B %-d")

    return p.div(_class="calendar-event")(
        p.p(
            p.h2(f"{timing} your {match['class_description']}"),
            p.p(f"{starting} {time_str} on {day_str}"),
        )
    )


def schedule_matches_html(matches: list[MatchInfo]):
    """Make HTML to show schedule matches"""
    return [match_to_html(match) for match in matches]


@profile.get("/<int:id>")
def profile_page(id: int):
    them = get_user_by_id(id)
    if them is None:
        return str(
            error_page(
                "Profile - Error 404",
                "Error 404",
                "User not found",
                is_user_logged_in(),
            )
        ), 404

    me = get_user()
    if me is None:
        # Don't allow unauthorized users to view profile pages
        return redirect("/auth/login")

    # NOTE: Week offset is duplicated with /calendar, perhaps use helper
    # function?
    week_offset = int(request.args.get("offset", "0"))
    start, end = get_week_range(week_offset)
    week_str = f"{week_offset_to_str(week_offset)}, {start.strftime('%x')} - {end.strftime('%x')}"

    # We are that user
    its_me = id == me["id"]

    # Whether we have matched
    liked_you = me["id"] in them["likes"]
    you_liked = id in me["likes"]

    time_picker = p.div(_class="time-picker")(
        p.a(href=f"?offset={week_offset - 1}", _class="btn btn-outline")(
            "Previous week"
        ),
        week_str,
        p.a(href=f"?offset={week_offset + 1}", _class="btn btn-outline")("Next week"),
    )

    # Give edit option if it's us
    if its_me:
        edit_option = []

        # List all matches with us
        matches = [
            user
            for user in get_data()["users"]
            if me["id"] in user["likes"] and user["id"] in me["likes"]
        ]
        matches_html = [
            p.h2("Your matches"),
            *(
                [
                    profile_banner_html(
                        user["id"],
                        liked_you=True,
                        you_liked=True,
                        link=week_offset,
                    )
                    for user in matches
                ]
                if len(matches)
                else [p.p(p.i("Nobody has matched with you yet."))]
            ),
        ]

        calendar_events = find_class_events(me["calendar"], start, end)
        calendar_html = [
            p.h2("Your calendar"),
            p.p("Your calendar is not shown to other users."),
            time_picker,
            p.div(_class="calendar")(
                [calendar_event_to_html(event) for event in calendar_events]
                if len(calendar_events)
                else [p.i("Your don't have any events this week.")]
            ),
        ]
    else:
        edit_option = []
        matches_html = []

        schedule_matches = get_matching_times(me, them, start, end)
        calendar_html = [
            p.h2("Your meet-up opportunities"),
            time_picker,
            p.div(_class="calendar")(
                schedule_matches_html(schedule_matches)
                if len(schedule_matches)
                else p.i("Your schedules don't overlap this week.")
            ),
        ]

    banner_html = profile_banner_html(
        id,
        its_you=its_me,
        liked_you=liked_you,
        you_liked=you_liked,
    )

    return str(
        p.html(
            generate_head(f"Profile - {them['display_name']}", ["/static/profile.css"]),
            p.body(
                navbar(True),
                p.main(
                    banner_html,
                    edit_option,
                    matches_html,
                    calendar_html,
                ),
            ),
        )
    )


@profile.get("/<int:id>/edit")
def profile_edit_page(id: int):
    user = get_user()
    if user is None:
        return redirect("/auth/login")
    if user["id"] != id:
        return str(
            error_page(
                "Edit Profile - Error 403",
                "Error 403",
                "You cannot edit a profile that isn't yours",
                True,
            )
        ), 403

    banner_html = profile_banner_html(id, its_you=True)

    return str(
        p.html(
            generate_head(f"Profile - {user['display_name']}", ["/static/profile.css"]),
            p.body(
                navbar(True),
                p.main(
                    p.h1("Edit profile"),
                    p.form(
                        # Main profile edit
                        # Submit
                        p.div(_class="profile-edit-actions")(
                            p.input(
                                type="submit",
                                value="Save",
                                name="save",
                                _class="btn btn-primary",
                            ),
                            p.input(
                                type="submit", value="Cancel", _class="btn btn-outline"
                            ),
                        ),
                        banner_html,
                        p.p(p.i("You can edit your profile picture using Gravatar.")),
                        # Name
                        p.div(p.label(for_="edit-name")("Display name")),
                        p.input(
                            type="text",
                            id="edit-name",
                            name="name",
                            placeholder="Display name",
                            value=user["display_name"],
                            required=True,
                        ),
                        # Profile description
                        p.div(
                            p.label(for_="edit-public-description")(
                                "Public profile description. This is shown to all users."
                            )
                        ),
                        p.textarea(style="width: 100%; height: 200px;")(
                            id="edit-public-description",
                            name="public_description",
                            placeholder="Your public profile description",
                        )(user["public_description"]),
                        p.div(
                            p.label(for_="edit-private-description")(
                                "Private profile description. This is only shown to "
                                "users who you have matched with."
                            )
                        ),
                        p.textarea(style="width: 100%; height: 200px;")(
                            id="edit-private-description",
                            name="private_description",
                            placeholder="Your private profile description",
                        )(user["private_description"]),
                        # TODO: Degrees
                    ),
                    p.form(action=f"/profile/{id}/edit/calendar")(
                        p.div(p.label(for_="calendar-url")("Calendar URL")),
                        p.input(
                            type="url",
                            id="calendar-url",
                            name="calendar_url",
                            placeholder="webcal://example.com/calendar.ics",
                            required=True,
                        ),
                        p.div(
                            p.input(
                                type="submit",
                                value="Update calendar",
                                _class="btn btn-primary",
                            )
                        ),
                    ),
                ),
            ),
        )
    )


@profile.post("/<int:id>/edit")
def profile_edit_submit(id: int):
    # If save option not specified, discard changes
    if "save" not in request.form:
        return redirect(f"/profile/{id}")

    user = get_user()
    if user is None:
        return redirect("/auth/login")
    if user["id"] != id:
        return str(
            error_page(
                "Edit Profile - Error 403",
                "Error 403",
                "You cannot edit a profile that isn't yours",
                True,
            )
        ), 403

    display_name = request.form["name"]
    public_description = request.form["public_description"]
    private_description = request.form["private_description"]

    user["display_name"] = display_name
    user["public_description"] = public_description
    user["private_description"] = private_description
    save_data()

    return redirect(f"/profile/{id}")


@profile.post("/<int:id>/edit/calendar")
def profile_edit_calendar_submit(id: int):
    user = get_user()
    if user is None:
        return redirect("/auth/login")
    if user["id"] != id:
        return str(
            error_page(
                "Edit Profile - Error 403",
                "Error 403",
                "You cannot edit a profile that isn't yours",
                True,
            )
        ), 403

    calendar_url = request.form["calendar_url"]

    user["calendar"] = download_ical(calendar_url)
    save_data()

    return redirect(f"/profile/{id}")
