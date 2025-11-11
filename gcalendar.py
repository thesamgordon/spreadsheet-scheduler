import os
import ast
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import datetime

CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar']
service_account_info = ast.literal_eval(os.environ['GOOGLE_SERVICE_ACCOUNT'])
calendar_creds = Credentials.from_service_account_info(service_account_info, scopes=CALENDAR_SCOPES)
calendar_service = build('calendar', 'v3', credentials=calendar_creds)

EVENT_PREFIX = os.environ.get('EVENT_PREFIX', '')
LOCATION = os.environ.get('LOCATION', '')

def add_event(event):
    print("Adding event:", event['summary'])
    
    calendar_id = os.environ['CALENDAR_ID']
    created_event = calendar_service.events().insert(calendarId=calendar_id, body=event).execute()
    return created_event

def update_event(event_id, event):
    print("Updating event:", event['summary'])
    
    calendar_id = os.environ['CALENDAR_ID']
    calendar_service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()

def delete_event(event_id):
    print("Deleting event:", event_id)
    
    calendar_id = os.environ['CALENDAR_ID']
    calendar_service.events().delete(calendarId=calendar_id, eventId=event_id).execute()

def get_all_events():
    calendar_id = os.environ['CALENDAR_ID']
    events_result = calendar_service.events().list(calendarId=calendar_id, maxResults=2500).execute()
    return events_result.get('items', [])

def generate_natural_key(event):
    summary = event.get('summary', '')
    start = event['start'].get('dateTime', event['start'])
    end = event['end'].get('dateTime', event['end'])
    
    if '+' in start:
        start = start.split('+')[0]
    elif '-' in start[10:]:
        start = start[:19]
        
    if '+' in end:
        end = end.split('+')[0]
    elif '-' in end[10:]:
        end = end[:19]
    
    return f"{summary}__{start}__{end}"

def sync_calendar_natural_key(sheet_events):
    sheet_events = convert_entries_to_calendar_events(sheet_events)
    existing_events = get_all_events()
    try: 
        existing_map = {generate_natural_key(e): e for e in existing_events}
    except KeyError as e:
        print(f"Error generating natural key for existing events: {e}")
        existing_map = {}

    sheet_keys = set()
    
    for event in sheet_events:
        key = generate_natural_key(event)
        sheet_keys.add(key)

        if key in existing_map:
            calendar_event = existing_map[key]
            update_event(calendar_event['id'], event)
        else:

            add_event(event)

    for key, event in existing_map.items():
        if key not in sheet_keys:
            delete_event(event['id'])
    
    seen_keys = set()
    for event in existing_events:
        key = generate_natural_key(event)
        if key in seen_keys:
            delete_event(event['id'])
        else:
            seen_keys.add(key)


def parse_time_string(date_str, time_str):
    date_obj = datetime.datetime.strptime(date_str, '%A, %B %d')
    year = datetime.datetime.now().year
    date_obj = date_obj.replace(year=year)
    
    start_str, end_str = time_str.split('-')
    start_hour, start_minute = map(int, start_str.split(':'))
    end_hour, end_minute = map(int, end_str.split(':'))

    start_dt = date_obj.replace(hour=start_hour, minute=start_minute)
    end_dt = date_obj.replace(hour=end_hour, minute=end_minute)

    iso_format = '%Y-%m-%dT%H:%M:%S'
    
    return start_dt.strftime(iso_format), end_dt.strftime(iso_format)

def convert_entries_to_calendar_events(entries, timezone='America/New_York'):
    calendar_events = []
    for entry in entries:
        start_iso, end_iso = parse_time_string(entry['date'], entry['start_time'] + '-' + entry['end_time'])
        
        activity = entry['activity']
        if EVENT_PREFIX and not activity.startswith(EVENT_PREFIX):
            activity = EVENT_PREFIX + activity

        description = ''
        if entry.get('new_element'):
            description = "<strong>New Element:</strong> " + entry.get('new_element', '')
            if entry.get('schedule'):
                description = str(description) + f"\n\n<strong>Schedule:</strong>\n{entry['schedule']}"
        else:
            if entry.get('schedule'):
                description = "<strong>Schedule:</strong>\n" + entry.get('schedule', '')

        event = {
            'summary': activity,
            'description': description,
            'start': {'dateTime': start_iso, 'timeZone': timezone},
            'end': {'dateTime': end_iso, 'timeZone': timezone},
            'location': LOCATION
        }
        calendar_events.append(event)

    return calendar_events
