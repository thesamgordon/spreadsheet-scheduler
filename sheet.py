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



def fetch_schedule():
    sheet = service.spreadsheets()
    
    try: 
        result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE).execute()
    except Exception as e:
        print(f"Error fetching data from Google Sheets: {e}")
        return []
    
    rows = result.get('values', [])
    
    schedule = []
    
    for row in rows:
        if len(row) < 4:
            continue

        start_time = row[1].split('-')[0].strip()
        end_time = row[1].split('-')[1].strip() if '-' in row[1] else ''
        
        if start_time.endswith('AM'):
            start_time = start_time[:-2].strip()
        if end_time.endswith('AM'):
            end_time = end_time[:-2].strip()
            
        if start_time.endswith('PM'):
            start_time = start_time[:-2].strip()
            
            if not start_time.startswith('12:'):
                hour, minute = map(int, start_time.split(':'))
                hour = (hour % 12) + 12
                start_time = f"{hour}:{minute:02d}"
                
        if end_time.endswith('PM'):
            end_time = end_time[:-2].strip()
            if not end_time.startswith('12:'):
                
                hour, minute = map(int, end_time.split(':'))
                hour = (hour % 12) + 12
                end_time = f"{hour}:{minute:02d}"

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
