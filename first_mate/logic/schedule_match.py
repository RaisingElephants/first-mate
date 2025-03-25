# UNSW Class Schedule with Schedule Matching Feature
# Requirements: pip install flask icalendar requests pytz dateutil

from flask import Flask, request, jsonify
import requests
from icalendar import Calendar
from datetime import datetime, timedelta, time
import pytz
from collections import defaultdict
import re
import hashlib
import copy

app = Flask(__name__)

# Local timezone - using Australia/Sydney for UNSW
LOCAL_TZ = pytz.timezone('Australia/Sydney')

# Constants for schedule matching
TIME_SLOT_INTERVAL = 30  # 30-minute intervals
DEFAULT_DAY_START = 8    # 8 AM
DEFAULT_DAY_END = 22     # 10 PM

# Define complete term information with start and end dates
TERM_INFO = {
    2024: {
        1: {
            "name": "Term 1 2024",
            "start_date": LOCAL_TZ.localize(datetime(2024, 2, 12)),  # Orientation Week
            "teaching_start": LOCAL_TZ.localize(datetime(2024, 2, 19)),  # Week 1 starts
            "end_date": LOCAL_TZ.localize(datetime(2024, 5, 11)),  # End of exam period
            "exam_start": LOCAL_TZ.localize(datetime(2024, 4, 22)),  # Week 10 + study week + exam
            "teaching_weeks": 10,
            "total_weeks": 13
        },
        2: {
            "name": "Term 2 2024",
            "start_date": LOCAL_TZ.localize(datetime(2024, 5, 20)),  # Orientation Week
            "teaching_start": LOCAL_TZ.localize(datetime(2024, 5, 27)),  # Week 1 starts
            "end_date": LOCAL_TZ.localize(datetime(2024, 8, 17)),  # End of exam period
            "exam_start": LOCAL_TZ.localize(datetime(2024, 7, 29)),  # Week 10 + study week + exam
            "teaching_weeks": 10,
            "total_weeks": 13
        },
        3: {
            "name": "Term 3 2024",
            "start_date": LOCAL_TZ.localize(datetime(2024, 9, 2)),  # Orientation Week
            "teaching_start": LOCAL_TZ.localize(datetime(2024, 9, 9)),  # Week 1 starts
            "end_date": LOCAL_TZ.localize(datetime(2024, 12, 7)),  # End of exam period
            "exam_start": LOCAL_TZ.localize(datetime(2024, 11, 11)),  # Week 10 + study week + exam
            "teaching_weeks": 10,
            "total_weeks": 13
        }
    },
    2025: {
        1: {
            "name": "Term 1 2025",
            "start_date": LOCAL_TZ.localize(datetime(2025, 2, 17)),  # Orientation Week
            "teaching_start": LOCAL_TZ.localize(datetime(2025, 2, 24)),  # Week 1 starts
            "end_date": LOCAL_TZ.localize(datetime(2025, 5, 17)),  # End of exam period
            "exam_start": LOCAL_TZ.localize(datetime(2025, 4, 28)),  # Week 10 + study week + exam
            "teaching_weeks": 10,
            "total_weeks": 13
        },
        2: {
            "name": "Term 2 2025",
            "start_date": LOCAL_TZ.localize(datetime(2025, 5, 26)),  # Orientation Week
            "teaching_start": LOCAL_TZ.localize(datetime(2025, 6, 2)),  # Week 1 starts
            "end_date": LOCAL_TZ.localize(datetime(2025, 8, 23)),  # End of exam period
            "exam_start": LOCAL_TZ.localize(datetime(2025, 8, 4)),  # Week 10 + study week + exam
            "teaching_weeks": 10,
            "total_weeks": 13
        },
        3: {
            "name": "Term 3 2025",
            "start_date": LOCAL_TZ.localize(datetime(2025, 9, 8)),  # Orientation Week
            "teaching_start": LOCAL_TZ.localize(datetime(2025, 9, 15)),  # Week 1 starts
            "end_date": LOCAL_TZ.localize(datetime(2025, 12, 13)),  # End of exam period
            "exam_start": LOCAL_TZ.localize(datetime(2025, 11, 17)),  # Week 10 + study week + exam
            "teaching_weeks": 10,
            "total_weeks": 13
        }
    }
}

# UNSW course patterns with specific weeks
COURSE_PATTERNS = [
    {
        "pattern": r"exam|assessment|quiz|test|final",
        "weeks": [11, 12, 13],  # Exam weeks
        "is_exam": True
    },
    {
        "pattern": r"first half|weeks 1-5",
        "weeks": [1, 2, 3, 4, 5],  # First half classes
        "is_exam": False
    },
    {
        "pattern": r"second half|weeks 6-10",
        "weeks": [6, 7, 8, 9, 10],  # Second half classes
        "is_exam": False
    }
]

def convert_webcal_to_https(url):
    """Convert webcal:// URL to https://"""
    if url.startswith('webcal://'):
        return url.replace('webcal://', 'https://')
    return url

def fetch_ics_data(url):
    """Fetch ICS data from URL"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return None, f"Error fetching ICS data: {str(e)}"

def find_current_term_and_week():
    """
    Find the current term and week number
    Returns (term_year, term_number, term_info, week_number, week_type)
    """
    try:
        # Get current date in local timezone
        now = datetime.now(LOCAL_TZ)
        
        # Try all years in TERM_INFO
        for year in TERM_INFO:
            for term_number, term_data in TERM_INFO[year].items():
                if term_data["start_date"] <= now <= term_data["end_date"]:
                    # We found the current term
                    # Calculate the week number
                    
                    if now < term_data["teaching_start"]:
                        # Orientation week
                        return year, term_number, term_data, "O", "Orientation Week"
                    
                    # Calculate days since teaching started
                    delta_days = (now - term_data["teaching_start"]).days
                    week_number = (delta_days // 7) + 1
                    
                    # Check if we're in exam period
                    if now >= term_data["exam_start"]:
                        # Calculate exam week
                        exam_delta = (now - term_data["exam_start"]).days
                        exam_week = (exam_delta // 7) + 1
                        return year, term_number, term_data, exam_week + 10, f"Exam Week {exam_week}"
                    
                    return year, term_number, term_data, week_number, f"Week {week_number}"
        
        # If we get here, we're not in a term
        return None, None, None, None, "Not in term"
    except Exception as e:
        print(f"Error finding current term: {e}")
        return None, None, None, None, "Error"

def get_current_week_dates():
    """Get the start and end dates of the current week (Monday to Sunday)"""
    now = datetime.now(LOCAL_TZ)
    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)
    return start_of_week, end_of_week

def extract_course_code(summary):
    """Extract course code from summary like 'MATH1081 Tutorial'"""
    match = re.search(r'([A-Z]{4}\d{4}[A-Za-z]*)', summary)
    if match:
        return match.group(1)
    return None

def extract_event_title(summary, course_code):
    """Extract the event title (e.g., 'Tutorial' from 'MATH1081 Tutorial')"""
    if course_code and course_code in summary:
        # Remove the course code from the summary
        return summary.replace(course_code, '').strip()
    return summary

def determine_event_type(summary, description, location):
    """Determine if the event is a lecture, tutorial, or exam"""
    # Check summary and description
    text = f"{summary} {description}".lower()
    
    if re.search(r'\blect', text):
        return "Lecture"
    elif re.search(r'\btut', text):
        return "Tutorial"
    elif re.search(r'\blab\b', text):
        return "Lab"
    elif re.search(r'\bexam\b|\btest\b|\bquiz\b|\bassessment\b', text):
        return "Exam"
    elif re.search(r'\bworkshop\b', text):
        return "Workshop"
    
    # Default case - try to infer from the summary
    if "lecture" in summary.lower():
        return "Lecture"
    elif "tutorial" in summary.lower() or "tut" in summary.lower():
        return "Tutorial"
    elif "lab" in summary.lower():
        return "Lab"
    elif "exam" in summary.lower() or "test" in summary.lower() or "quiz" in summary.lower():
        return "Exam"
    else:
        return "Class"  # Default

def is_event_in_current_week(event_start, event_text, term_info, current_week, is_recurring=False):
    """
    Determine if an event occurs in the current week based on:
    1. For one-time events, check if it falls within the current week
    2. For recurring events, check if it matches the pattern for the current week
    """
    # If not in a term, use simple date comparison
    if not term_info:
        now = datetime.now(LOCAL_TZ)
        start_of_week = now - timedelta(days=now.weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)
        return start_of_week <= event_start <= end_of_week
    
    # Get the current week's start and end dates
    now = datetime.now(LOCAL_TZ)
    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)
    
    # For non-recurring events, check if it falls within the current week
    if not is_recurring:
        return start_of_week <= event_start <= end_of_week
    
    # For recurring events, first check if the day of week matches
    event_day = event_start.weekday()  # 0 = Monday, 6 = Sunday
    current_day = now.weekday()
    
    # Check if this event runs on this day of the week
    if event_day != event_day:
        return False
    
    # Check special course patterns
    event_text = event_text.lower()
    
    # Check if this is an exam (only show in exam weeks)
    for pattern in COURSE_PATTERNS:
        if re.search(pattern["pattern"], event_text):
            # If this is an exam pattern, check if we're in an exam week
            if pattern["is_exam"]:
                # Exams only show in weeks 11-13
                return current_week >= 11
            else:
                # Other patterns have specific weeks
                return current_week in pattern["weeks"]
    
    # Default for regular lectures/tutorials - they run in weeks 1-10
    if current_week <= 10:
        # Check if it's a first half or second half course
        if re.search(r"first half|weeks 1-5", event_text):
            return 1 <= current_week <= 5
        elif re.search(r"second half|weeks 6-10", event_text):
            return 6 <= current_week <= 10
        else:
            # Regular course, runs all teaching weeks
            return 1 <= current_week <= 10
    
    return False

def format_duration(minutes):
    """Format duration in minutes to a human-readable string (e.g., '1 hr' or '2 hr')"""
    hours = minutes // 60
    mins = minutes % 60
    
    if hours == 0:
        return f"{mins} min"
    elif mins == 0:
        return f"{hours} hr"
    else:
        return f"{hours} hr {mins} min"

def create_event_hash(event):
    """Create a unique hash for an event to detect duplicates"""
    # Combine important fields to create a unique signature
    signature = f"{event['summary']}|{event['start_time']}|{event['end_time']}|{event['location']}|{event['day_of_week']}"
    return hashlib.md5(signature.encode()).hexdigest()

def parse_ics_data(ics_data):
    """Parse ICS data and extract events for the current week"""
    try:
        cal = Calendar.from_ical(ics_data)
        
        # Find the current term and week
        term_year, term_number, term_info, week_number, week_label = find_current_term_and_week()
        
        # For testing purposes, if not in term, use Week 5 of Term 1 2024
        if not term_info:
            term_year = 2024
            term_number = 1
            term_info = TERM_INFO[2024][1]
            week_number = 5
            week_label = "Week 5"
        
        # Get the current week's date range
        week_start, week_end = get_current_week_dates()
        
        # Dictionary to store events by day
        weekly_schedule = {
            'Monday': [],
            'Tuesday': [],
            'Wednesday': [],
            'Thursday': [],
            'Friday': [],
            'Saturday': [],
            'Sunday': []
        }
        
        # Keep track of unique events to avoid duplicates
        seen_event_hashes = set()
        
        # Process events
        for component in cal.walk():
            if component.name == "VEVENT":
                try:
                    # Get event details
                    summary = str(component.get('summary', ''))
                    description = str(component.get('description', ''))
                    location = str(component.get('location', ''))
                    
                    # Skip empty events
                    if not summary.strip():
                        continue
                    
                    # Get start and end times
                    start = component.get('dtstart')
                    end = component.get('dtend')
                    
                    if not start:
                        continue
                    
                    # If end is not provided, use start + 1 hour
                    if not end:
                        if hasattr(start.dt, 'tzinfo'):
                            end_dt = start.dt + timedelta(hours=1)
                        else:
                            end_dt = start.dt + timedelta(days=1)
                        # Create a dummy end component
                        end = start.copy()
                        end.dt = end_dt
                    
                    # Extract course code
                    course_code = extract_course_code(summary)
                    
                    # Event title (e.g., "Tutorial" from "MATH1081 Tutorial")
                    event_title = extract_event_title(summary, course_code) if course_code else summary
                    
                    # Get the start time in the local timezone
                    if hasattr(start.dt, 'tzinfo'):
                        # If already has timezone info
                        if start.dt.tzinfo is not None:
                            event_start = start.dt.astimezone(LOCAL_TZ)
                        else:
                            # If naive datetime
                            event_start = LOCAL_TZ.localize(start.dt)
                    else:
                        # If it's a date (all-day event), convert to datetime
                        event_start = LOCAL_TZ.localize(datetime.combine(start.dt, 
                                                      datetime.min.time()))
                    
                    # Get the end time in the local timezone
                    if hasattr(end.dt, 'tzinfo'):
                        # If already has timezone info
                        if end.dt.tzinfo is not None:
                            event_end = end.dt.astimezone(LOCAL_TZ)
                        else:
                            # If naive datetime
                            event_end = LOCAL_TZ.localize(end.dt)
                    else:
                        # If it's a date (all-day event), convert to datetime
                        event_end = LOCAL_TZ.localize(datetime.combine(end.dt, 
                                                    datetime.min.time()))
                    
                    # Check if this is a recurring event
                    is_recurring = component.get('rrule') is not None
                    
                    # Determine if this event occurs in the current week
                    event_in_current_week = False
                    
                    if is_recurring:
                        # For recurring events, we need to check if there's an occurrence this week
                        # Get the day of the week for this event (0 = Monday, 6 = Sunday)
                        event_day_of_week = event_start.weekday()
                        
                        # Get the date for this weekday in the current week
                        current_week_date = week_start + timedelta(days=event_day_of_week)
                        
                        # Create a datetime for this week's occurrence
                        current_week_datetime = datetime.combine(
                            current_week_date.date(),
                            event_start.time(),
                            tzinfo=LOCAL_TZ
                        )
                        
                        # Check for exclusions
                        is_excluded = False
                        for exdate in component.get('exdate', []):
                            if isinstance(exdate, list):
                                for ex_date in exdate:
                                    if hasattr(ex_date.dt, 'tzinfo'):
                                        excluded_date = ex_date.dt.astimezone(LOCAL_TZ)
                                        if excluded_date.date() == current_week_datetime.date():
                                            is_excluded = True
                                            break
                            elif hasattr(exdate.dt, 'tzinfo'):
                                excluded_date = exdate.dt.astimezone(LOCAL_TZ)
                                if excluded_date.date() == current_week_datetime.date():
                                    is_excluded = True
                            
                            if is_excluded:
                                break
                        
                        # Check if this event runs in the current week based on patterns
                        if not is_excluded:
                            event_text = f"{summary} {description}"
                            if is_event_in_current_week(current_week_datetime, event_text, term_info, week_number, is_recurring):
                                event_in_current_week = True
                                event_start = current_week_datetime  # Use this week's occurrence
                                event_end = datetime.combine(
                                    current_week_date.date(),
                                    event_end.time(),
                                    tzinfo=LOCAL_TZ
                                )
                    else:
                        # For non-recurring events, simply check if it falls in this week
                        if week_start <= event_start <= week_end:
                            event_in_current_week = True
                    
                    if event_in_current_week:
                        # Format times for display
                        start_time = event_start.strftime('%I:%M %p')
                        end_time = event_end.strftime('%I:%M %p')
                        
                        # Calculate duration in minutes
                        duration_minutes = int((event_end - event_start).total_seconds() / 60)
                        duration_str = format_duration(duration_minutes)
                        
                        # Determine day of week
                        day_of_week = event_start.strftime('%A')
                        
                        # Determine event type
                        event_type = determine_event_type(summary, description, location)
                        
                        # Create event object
                        event = {
                            'summary': summary,
                            'course_code': course_code if course_code else summary,
                            'event_title': event_title,
                            'event_type': event_type,
                            'location': location,
                            'start_time': start_time,
                            'end_time': end_time,
                            'duration': duration_str,
                            'duration_minutes': duration_minutes,
                            'day_of_week': day_of_week,
                            'start_datetime': event_start,  # Keep for sorting
                        }
                        
                        # Create a hash to detect duplicates
                        event_hash = create_event_hash(event)
                        
                        # Only add if we haven't seen this event before
                        if event_hash not in seen_event_hashes:
                            seen_event_hashes.add(event_hash)
                            weekly_schedule[day_of_week].append(event)
                
                except Exception as e:
                    # Skip this event if there's an error
                    print(f"Error processing event: {str(e)}")
                    continue
        
        # Sort events by start time within each day
        for day, events in weekly_schedule.items():
            weekly_schedule[day] = sorted(events, key=lambda x: x['start_datetime'])
        
        # Prepare result
        result = {
            "current_term": term_info["name"] if term_info else None,
            "current_week": week_number,
            "week_label": week_label,
            "week_dates": {
                "start": week_start.strftime('%d %b %Y'),
                "end": week_end.strftime('%d %b %Y')
            },
            "schedule": weekly_schedule
        }
        
        return result
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return {
            "error": f"Error parsing ICS data: {str(e)}\n{error_details}"
        }

# --- Begin Schedule Matching Functions ---

def create_day_schedule(day_date, start_hour=DEFAULT_DAY_START, end_hour=DEFAULT_DAY_END):
    """
    Create time slots for a day with the given interval
    
    Args:
        day_date: The date for the day
        start_hour: Hour to start the schedule (default 8 AM)
        end_hour: Hour to end the schedule (default 10 PM)
        
    Returns:
        List of time slots for the day
    """
    slots = []
    
    # Create day start and end datetime objects
    day_start = datetime.combine(day_date.date(), time(start_hour, 0), tzinfo=LOCAL_TZ)
    day_end = datetime.combine(day_date.date(), time(end_hour, 0), tzinfo=LOCAL_TZ)
    
    # Create slots at regular intervals
    current = day_start
    while current < day_end:
        end_time = current + timedelta(minutes=TIME_SLOT_INTERVAL)
        slots.append({
            'start': current,
            'end': end_time,
            'busy': False
        })
        current = end_time
    
    return slots

def mark_busy_slots(day_schedule, events):
    """
    Mark time slots as busy based on events
    
    Args:
        day_schedule: List of time slots for the day
        events: List of events for the day
        
    Returns:
        Updated day schedule with busy slots marked
    """
    # Create a deep copy to avoid modifying the original
    updated_schedule = copy.deepcopy(day_schedule)
    
    for slot in updated_schedule:
        for event in events:
            event_start = event['start_datetime']
            event_end = event_start + timedelta(minutes=event['duration_minutes'])
            
            # Check if event overlaps with this slot
            if (event_start < slot['end'] and event_end > slot['start']):
                slot['busy'] = True
                break
    
    return updated_schedule

def find_common_free_times(schedule1, schedule2):
    """
    Find common free time slots between two schedules
    
    Args:
        schedule1: First person's schedule
        schedule2: Second person's schedule
        
    Returns:
        List of common free time slots
    """
    common_free_slots = []
    
    for i in range(len(schedule1)):
        if not schedule1[i]['busy'] and not schedule2[i]['busy']:
            common_free_slots.append(schedule1[i])
    
    return common_free_slots

def merge_consecutive_slots(slots):
    """
    Merge consecutive free time slots into longer blocks
    
    Args:
        slots: List of free time slots
        
    Returns:
        List of merged time slots
    """
    if not slots:
        return []
    
    merged_slots = []
    current_block = None
    
    for slot in slots:
        if current_block is None:
            # Start a new block
            current_block = {
                'start': slot['start'],
                'end': slot['end']
            }
        elif slot['start'] == current_block['end']:
            # Extend the current block
            current_block['end'] = slot['end']
        else:
            # Save the current block and start a new one
            merged_slots.append(current_block)
            current_block = {
                'start': slot['start'],
                'end': slot['end']
            }
    
    # Don't forget to add the last block
    if current_block:
        merged_slots.append(current_block)
    
    return merged_slots

def format_time(dt):
    """Format datetime as HH:MM AM/PM without leading zeros"""
    # Standard format first
    formatted = dt.strftime('%I:%M %p')
    # Remove leading zero if present
    if formatted.startswith('0'):
        formatted = formatted[1:]
    return formatted

def get_matching_free_times(webcal_url1, webcal_url2, days_to_check=5):
    """
    Get matching free times between two schedules
    
    Args:
        webcal_url1: First person's WebCal URL
        webcal_url2: Second person's WebCal URL
        days_to_check: Number of days to check for free times
        
    Returns:
        Dictionary with matching free times organized by day
    """
    try:
        # Convert URLs and fetch data
        https_url1 = convert_webcal_to_https(webcal_url1)
        https_url2 = convert_webcal_to_https(webcal_url2)
        
        ics_data1 = fetch_ics_data(https_url1)
        ics_data2 = fetch_ics_data(https_url2)
        
        if isinstance(ics_data1, tuple):  # Error occurred
            return {"error": ics_data1[1]}
        if isinstance(ics_data2, tuple):  # Error occurred
            return {"error": ics_data2[1]}
        
        # Parse calendars
        schedule1 = parse_ics_data(ics_data1)
        schedule2 = parse_ics_data(ics_data2)
        
        if "error" in schedule1:
            return schedule1
        if "error" in schedule2:
            return schedule2
        
        # Get current term and week information
        term_year, term_number, term_info, week_number, week_label = find_current_term_and_week()
        
        # Get the current week's date range
        now = datetime.now(LOCAL_TZ)
        start_of_week = now - timedelta(days=now.weekday())  # Monday is 0
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Find matching free times for each day
        matching_schedule = []
        
        for day_offset in range(days_to_check):
            # Get the date for this day
            check_date = start_of_week + timedelta(days=day_offset)
            day_name = check_date.strftime('%A')  # Day of week as string
            
            # Filter events for this day from both schedules
            events1 = []
            if day_name in schedule1["schedule"]:
                events1 = schedule1["schedule"][day_name]
            
            events2 = []
            if day_name in schedule2["schedule"]:
                events2 = schedule2["schedule"][day_name]
            
            # Create time slots for the day
            day_schedule = create_day_schedule(check_date)
            
            # Mark busy slots for both people
            schedule1_day = mark_busy_slots(day_schedule, events1)
            schedule2_day = mark_busy_slots(day_schedule, events2)
            
            # Find common free times
            common_free_slots = find_common_free_times(schedule1_day, schedule2_day)
            
            # Merge consecutive slots
            merged_slots = merge_consecutive_slots(common_free_slots)
            
            # Format results for this day
            free_times = []
            for slot in merged_slots:
                duration_minutes = int((slot['end'] - slot['start']).total_seconds() / 60)
                if duration_minutes >= TIME_SLOT_INTERVAL:  # Only include slots that are at least the interval length
                    free_times.append({
                        'start_time': format_time(slot['start']),
                        'end_time': format_time(slot['end']),
                        'duration_minutes': duration_minutes,
                        'duration_str': format_duration(duration_minutes)
                    })
            
            # Only add days with free time slots
            if free_times:
                matching_schedule.append({
                    'date': check_date.strftime('%A, %B %d'),
                    'day': day_name,
                    'free_times': free_times
                })
        
        # Prepare the result
        result = {
            "current_term": term_info["name"] if term_info else None,
            "current_week": week_number,
            "week_label": week_label,
            "matching_schedule": matching_schedule
        }
        
        return result
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return {
            "error": f"Error finding matching free times: {str(e)}\n{error_details}"
        }

# --- End Schedule Matching Functions ---

@app.route('/')
def index():
    """Serve the main page directly"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UNSW Current Week Schedule</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
            color: #333;
        }
        h1, h2 {
            color: #2c3e50;
        }
        h1 {
            text-align: center;
            margin-bottom: 10px;
        }
        .term-info {
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 30px;
        }
        .week-number {
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
        }
        .container {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
        }
        form {
            margin: 20px 0;
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }
        button {
            padding: 12px 24px;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #2980b9;
        }
        .loading {
            display: none;
            margin: 20px 0;
            text-align: center;
            color: #7f8c8d;
        }
        .error {
            color: #e74c3c;
            font-weight: bold;
            margin: 20px 0;
            white-space: pre-line;
        }
        .day-header {
            background-color: #3498db;
            color: white;
            padding: 10px 20px;
            font-size: 20px;
            font-weight: bold;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            margin-bottom: 0;
        }
        .day-container {
            margin-bottom: 25px;
            border-left: 4px solid #3498db;
            background-color: white;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .event {
            padding: 15px 20px;
            border-bottom: 1px solid #eee;
        }
        .event:last-child {
            border-bottom: none;
        }
        .time {
            color: #e67e22;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .course-title {
            font-weight: bold;
            margin-bottom: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .location {
            color: #7f8c8d;
            margin-bottom: 10px;
        }
        .duration {
            float: right;
            color: #7f8c8d;
        }
        .tutorial-badge, .lecture-badge, .exam-badge, .lab-badge, .workshop-badge, .class-badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: normal;
            color: white;
            margin-left: 10px;
        }
        .tutorial-badge {
            background-color: #27ae60;
        }
        .lecture-badge {
            background-color: #9b59b6;
        }
        .exam-badge {
            background-color: #e74c3c;
        }
        .lab-badge {
            background-color: #f39c12;
        }
        .workshop-badge {
            background-color: #3498db;
        }
        .class-badge {
            background-color: #7f8c8d;
        }
        .no-events {
            padding: 15px 20px;
            color: #7f8c8d;
            font-style: italic;
        }
        .nav-links {
            margin-top: 30px; 
            text-align: center;
        }
        .nav-link {
            display: inline-block; 
            padding: 12px 24px; 
            background-color: #3498db; 
            color: white; 
            text-decoration: none; 
            border-radius: 4px; 
            font-weight: bold; 
            transition: background-color 0.3s;
        }
        .nav-link:hover {
            background-color: #2980b9;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>UNSW Class Schedule</h1>
        <div class="term-info">
            <div id="term-display">Loading...</div>
            <div id="week-display" class="week-number"></div>
            <div id="date-display"></div>
        </div>
        
        <form id="parse-form">
            <input type="text" id="webcal-url" placeholder="webcal://my.unsw.edu.au/cal/pttd/..." value="webcal://my.unsw.edu.au/cal/pttd/Kmmj3w7Y2Q.ics">
            <button type="submit">View Schedule</button>
        </form>
        
        <div id="loading" class="loading">Loading calendar data...</div>
        
        <div id="error" class="error"></div>
        
        <div id="schedule-container"></div>
        
        <div class="nav-links">
            <a href="/match" class="nav-link">Try Schedule Matching Feature</a>
            <p style="margin-top: 10px; color: #7f8c8d;">
                Find common free times between two schedules
            </p>
        </div>
    </div>

    <script>
        document.getElementById('parse-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const url = document.getElementById('webcal-url').value;
            const loading = document.getElementById('loading');
            const error = document.getElementById('error');
            const scheduleContainer = document.getElementById('schedule-container');
            const termDisplay = document.getElementById('term-display');
            const weekDisplay = document.getElementById('week-display');
            const dateDisplay = document.getElementById('date-display');
            
            // Clear previous results
            error.textContent = '';
            scheduleContainer.innerHTML = '';
            
            // Show loading
            loading.style.display = 'block';
            
            // Send request
            fetch('/parse', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'url=' + encodeURIComponent(url)
            })
            .then(response => response.json())
            .then(data => {
                loading.style.display = 'none';
                
                if (data.error) {
                    error.textContent = data.error;
                    return;
                }
                
                // Update term and week info
                termDisplay.textContent = data.current_term || 'No active term';
                weekDisplay.textContent = data.week_label || '';
                dateDisplay.textContent = `(${data.week_dates.start} - ${data.week_dates.end})`;
                
                // Days of the week in order
                const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
                
                // Display schedule for each day
                days.forEach(day => {
                    const dayEvents = data.schedule[day] || [];
                    
                    // Only create containers for days with events
                    if (dayEvents.length > 0) {
                        // Create day container
                        const dayContainer = document.createElement('div');
                        dayContainer.className = 'day-container';
                        
                        // Create day header
                        const dayHeader = document.createElement('div');
                        dayHeader.className = 'day-header';
                        dayHeader.textContent = day;
                        dayContainer.appendChild(dayHeader);
                    
                        // Add events
                        dayEvents.forEach(event => {
                            const eventDiv = document.createElement('div');
                            eventDiv.className = 'event';
                            
                            // Format the time
                            const timeDiv = document.createElement('div');
                            timeDiv.className = 'time';
                            timeDiv.textContent = `${event.start_time} - ${event.end_time}`;
                            eventDiv.appendChild(timeDiv);
                            
                            // Create badge based on event type
                            let badgeHTML = '';
                            if (event.event_type === 'Lecture') {
                                badgeHTML = '<span class="lecture-badge">Lecture</span>';
                            } else if (event.event_type === 'Tutorial') {
                                badgeHTML = '<span class="tutorial-badge">Tutorial</span>';
                            } else if (event.event_type === 'Lab') {
                                badgeHTML = '<span class="lab-badge">Lab</span>';
                            } else if (event.event_type === 'Exam') {
                                badgeHTML = '<span class="exam-badge">Exam</span>';
                            } else if (event.event_type === 'Workshop') {
                                badgeHTML = '<span class="workshop-badge">Workshop</span>';
                            } else {
                                badgeHTML = `<span class="class-badge">${event.event_type}</span>`;
                            }
                            
                            // Course title and badge
                            const courseTitleDiv = document.createElement('div');
                            courseTitleDiv.className = 'course-title';
                            
                            // Format the title correctly
                            let titleText = '';
                            if (event.course_code && event.event_title) {
                                titleText = `${event.course_code} ${event.event_title}`;
                            } else {
                                titleText = event.summary;
                            }
                            
                            courseTitleDiv.innerHTML = `
                                <span>${titleText}${badgeHTML}</span>
                                <span class="duration">${event.duration}</span>
                            `;
                            eventDiv.appendChild(courseTitleDiv);
                            
                            // Location
                            if (event.location && event.location !== 'None') {
                                const locationDiv = document.createElement('div');
                                locationDiv.className = 'location';
                                locationDiv.textContent = event.location;
                                eventDiv.appendChild(locationDiv);
                            }
                            
                            dayContainer.appendChild(eventDiv);
                        });
                        
                        // Add day container to schedule
                        scheduleContainer.appendChild(dayContainer);
                    }
                });
                
                // Check if no events were found
                if (Object.values(data.schedule).every(events => events.length === 0)) {
                    const noEventsDiv = document.createElement('div');
                    noEventsDiv.className = 'no-events';
                    noEventsDiv.textContent = 'No events scheduled for this week';
                    scheduleContainer.appendChild(noEventsDiv);
                }
            })
            .catch(err => {
                loading.style.display = 'none';
                error.textContent = 'Error: ' + err.message;
            });
        });
    </script>
</body>
</html>
    '''

@app.route('/parse', methods=['POST'])
def parse():
    """Parse the WebCal URL and return the current week's schedule"""
    webcal_url = request.form.get('url', '')
    
    if not webcal_url:
        return jsonify({"error": "No URL provided"})
    
    https_url = convert_webcal_to_https(webcal_url)
    ics_data = fetch_ics_data(https_url)
    
    if isinstance(ics_data, tuple):  # Error occurred
        return jsonify({"error": ics_data[1]})
    
    weekly_schedule = parse_ics_data(ics_data)
    
    return jsonify(weekly_schedule)

@app.route('/match')
def match_form():
    """Serve the match form page"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UNSW Schedule Matcher</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
            color: #333;
        }
        h1, h2 {
            color: #2c3e50;
        }
        h1 {
            text-align: center;
            margin-bottom: 30px;
        }
        .subtitle {
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 30px;
        }
        .container {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
        }
        form {
            margin: 20px 0;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .form-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        label {
            font-weight: bold;
            color: #2c3e50;
        }
        input[type="text"] {
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
            width: 100%;
        }
        .form-tip {
            font-size: 14px;
            color: #7f8c8d;
            margin-top: 5px;
        }
        button {
            padding: 15px 24px;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
            margin-top: 10px;
            align-self: center;
        }
        button:hover {
            background-color: #2980b9;
        }
        .loading {
            display: none;
            margin: 20px 0;
            text-align: center;
            color: #7f8c8d;
        }
        .error {
            color: #e74c3c;
            font-weight: bold;
            margin: 20px 0;
            padding: 15px;
            background-color: #fdf0f0;
            border-left: 5px solid #e74c3c;
            border-radius: 4px;
            display: none;
        }
        .instructions {
            background-color: #f5f9ff;
            border-left: 5px solid #3498db;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }
        .instructions h3 {
            margin-top: 0;
            color: #3498db;
        }
        .instructions ol {
            margin-bottom: 0;
            padding-left: 20px;
        }
        .nav-links {
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }
        .nav-link {
            display: inline-block;
            padding: 10px 15px;
            margin: 0 10px;
            color: #3498db;
            text-decoration: none;
            border: 1px solid #3498db;
            border-radius: 4px;
            transition: all 0.3s;
        }
        .nav-link:hover {
            background-color: #3498db;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>UNSW Schedule Matcher</h1>
        <p class="subtitle">Find common free times between two UNSW class schedules</p>
        
        <div class="instructions">
            <h3>How to Get Your WebCal URL</h3>
            <ol>
                <li>Go to <a href="https://my.unsw.edu.au/" target="_blank">myUNSW</a></li>
                <li>Navigate to My Student Profile → My Timetable</li>
                <li>Click on "Subscribe to timetable" and copy the WebCal URL</li>
            </ol>
        </div>
        
        <form id="match-form">
            <div class="form-group">
                <label for="webcal-url1">Person 1 WebCal URL:</label>
                <input type="text" id="webcal-url1" placeholder="webcal://my.unsw.edu.au/cal/pttd/..." required>
                <div class="form-tip">Example: webcal://my.unsw.edu.au/cal/pttd/Kmmj3w7Y2Q.ics</div>
            </div>
            
            <div class="form-group">
                <label for="webcal-url2">Person 2 WebCal URL:</label>
                <input type="text" id="webcal-url2" placeholder="webcal://my.unsw.edu.au/cal/pttd/..." required>
                <div class="form-tip">Example: webcal://my.unsw.edu.au/cal/pttd/Lnnk4x8Z3R.ics</div>
            </div>
            
            <button type="submit">Find Common Free Times</button>
        </form>
        
        <div id="loading" class="loading">Finding common free times...</div>
        
        <div id="error" class="error"></div>
        
        <div id="results-container"></div>
        
        <div class="nav-links">
            <a href="/" class="nav-link">Back to Class Schedule</a>
        </div>
    </div>

    <script>
        document.getElementById('match-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const url1 = document.getElementById('webcal-url1').value;
            const url2 = document.getElementById('webcal-url2').value;
            const loading = document.getElementById('loading');
            const error = document.getElementById('error');
            const resultsContainer = document.getElementById('results-container');
            
            // Check if URLs are provided
            if (!url1 || !url2) {
                error.style.display = 'block';
                error.textContent = 'Please provide both WebCal URLs.';
                return;
            }
            
            // Clear previous results
            error.style.display = 'none';
            error.textContent = '';
            resultsContainer.innerHTML = '';
            
            // Show loading
            loading.style.display = 'block';
            
            // Send request
            fetch('/match-schedules', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'url1=' + encodeURIComponent(url1) + '&url2=' + encodeURIComponent(url2)
            })
            .then(response => response.json())
            .then(data => {
                loading.style.display = 'none';
                
                if (data.error) {
                    error.style.display = 'block';
                    error.textContent = data.error;
                    return;
                }
                
                // Build the results HTML
                let resultsHTML = `
                    <div style="margin-top: 30px;">
                        <h2 style="text-align: center; color: #3498db; margin-bottom: 5px;">Matching Free Times</h2>
                        <p style="text-align: center; color: #7f8c8d; margin-bottom: 20px;">
                            ${data.current_term || ''} - ${data.week_label || ''}
                        </p>
                `;
                
                if (data.matching_schedule && data.matching_schedule.length > 0) {
                    data.matching_schedule.forEach(day => {
                        resultsHTML += `
                            <div style="margin-bottom: 25px; border-left: 4px solid #3498db; background-color: white; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); overflow: hidden;">
                                <div style="background-color: #3498db; color: white; padding: 10px 20px; font-size: 18px; font-weight: bold;">
                                    ${day.date}
                                </div>
                                <div style="padding: 0;">
                        `;
                        
                        day.free_times.forEach(slot => {
                            resultsHTML += `
                                <div style="padding: 15px 20px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between;">
                                    <div>
                                        <div style="font-weight: bold; color: #e67e22;">${slot.start_time} - ${slot.end_time}</div>
                                    </div>
                                    <div style="color: #7f8c8d;">${slot.duration_str}</div>
                                </div>
                            `;
                        });
                        
                        resultsHTML += `
                                </div>
                            </div>
                        `;
                    });
                } else {
                    resultsHTML += `
                        <div style="padding: 20px; text-align: center; color: #7f8c8d; font-style: italic;">
                            No common free times found for the current week.
                        </div>
                    `;
                }
                
                resultsHTML += `</div>`;
                
                // Display results
                resultsContainer.innerHTML = resultsHTML;
            })
            .catch(err => {
                loading.style.display = 'none';
                error.style.display = 'block';
                error.textContent = 'Error: ' + err.message;
            });
        });
    </script>
</body>
</html>
    '''

@app.route('/match-schedules', methods=['POST'])
def match_schedules():
    """Match schedules between two WebCal URLs"""
    webcal_url1 = request.form.get('url1', '')
    webcal_url2 = request.form.get('url2', '')
    
    if not webcal_url1 or not webcal_url2:
        return jsonify({"error": "Both WebCal URLs are required"})
    
    matching_free_times = get_matching_free_times(webcal_url1, webcal_url2)
    
    return jsonify(matching_free_times)

if __name__ == '__main__':
    app.run(debug=True, port=5000)