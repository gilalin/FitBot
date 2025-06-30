import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

class CalendarService:
    def __init__(self):
        self.calendar_id = os.getenv('GOOGLE_CALENDAR_ID')
        credentials = service_account.Credentials.from_service_account_file(
            os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        self.service = build('calendar', 'v3', credentials=credentials)

    def get_workouts(self, start_date=None, end_date=None):
        """Get workouts from Google Calendar."""
        if not start_date:
            start_date = datetime.now(ZoneInfo("Asia/Jerusalem"))
        if not end_date:
            end_date = start_date + timedelta(days=1)

        events_result = self.service.events().list(
            calendarId=self.calendar_id,
            timeMin=start_date.isoformat(),
            timeMax=end_date.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        workouts = []

        for event in events:
            workout = {
                'attributes': {
                    'title': event['summary'],
                    'description': event.get('description', ''),
                    'scheduled_date': event['start'].get('dateTime', event['start'].get('date')),
                    'calendar_event_id': event['id']
                }
            }
            workouts.append(workout)

        return workouts

    def create_workout(self, title, description, start_time, end_time=None):
        """Create a workout event in Google Calendar."""
        if not end_time:
            end_time = start_time + timedelta(hours=1)

        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Asia/Jerusalem',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Asia/Jerusalem',
            },
        }

        event = self.service.events().insert(
            calendarId=self.calendar_id,
            body=event
        ).execute()

        return event

    def update_workout(self, event_id, title=None, description=None, start_time=None, end_time=None):
        """Update a workout event in Google Calendar."""
        event = self.service.events().get(
            calendarId=self.calendar_id,
            eventId=event_id
        ).execute()

        if title:
            event['summary'] = title
        if description:
            event['description'] = description
        if start_time:
            event['start']['dateTime'] = start_time.isoformat()
        if end_time:
            event['end']['dateTime'] = end_time.isoformat()

        updated_event = self.service.events().update(
            calendarId=self.calendar_id,
            eventId=event_id,
            body=event
        ).execute()

        return updated_event

    def delete_workout(self, event_id):
        """Delete a workout event from Google Calendar."""
        self.service.events().delete(
            calendarId=self.calendar_id,
            eventId=event_id
        ).execute()

# Example usage
if __name__ == '__main__':
    calendar_service = CalendarService()
    
    # Get today's workouts
    today = datetime.now(ZoneInfo("Asia/Jerusalem"))
    workouts = calendar_service.get_workouts(today)
    
    for workout in workouts:
        print(f"Title: {workout['attributes']['title']}")
        print(f"Description: {workout['attributes']['description']}")
        print("---") 