import os
from datetime import datetime
from langchain_core.tools import tool
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "credentials/service_account.json")
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")

def _get_calendar_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("calendar", "v3", credentials=creds)

@tool
def get_upcoming_events(max_results: int = 5) -> str:
    """Get upcoming events from the company Google Calendar. Use when user asks about meetings, schedule, or events."""
    service = _get_calendar_service()
    now = datetime.utcnow().isoformat() + "Z"
    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=now,
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime"
    ).execute()
    events = events_result.get("items", [])
    if not events:
        return "No upcoming events found."
    output = []
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        output.append(f"{event.get('summary', 'No title')} — {start}")
    return "\n".join(output)

@tool
def create_calendar_event(summary: str, start_time: str, end_time: str, description: str = "") -> str:
    """Create a new event on the company Google Calendar. start_time and end_time must be ISO format, e.g. 2026-06-20T15:00:00+05:00"""
    service = _get_calendar_service()
    event = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_time},
        "end": {"dateTime": end_time},
    }
    created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return f"Event created: {created_event.get('htmlLink')}"