import ast
import os
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import ast

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SHEET_ID = os.environ['SHEET_ID']
RANGE = os.environ['SHEET_RANGE']

service_account_info = ast.literal_eval(os.environ['GOOGLE_SERVICE_ACCOUNT'])

creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)

service = build('sheets', 'v4', credentials=creds)

sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE).execute()
rows = result.get('values', [])

def fetch_schedule():
    schedule = []
    
    for row in rows:
        if len(row) < 4:
            continue

        start_time = row[1].split('-')[0].strip()
        end_time = row[1].split('-')[1].strip() if '-' in row[1] else ''

        entry = {
            'date': row[0],
            'start_time': start_time,
            'end_time': end_time,
            'schedule': row[2],
            'activity': row[3],
            'new_element': row[4] if len(row) > 4 else None
        }
        schedule.append(entry)
        
    return schedule
