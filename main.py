from sheet import fetch_schedule
from gcalendar import sync_calendar_natural_key
from dotenv import load_dotenv
import time

load_dotenv()

def main():
    while True:
        print("Fetching schedule from Google Sheets...")
        
        events = fetch_schedule()
        sync_calendar_natural_key(events)
        
        time.sleep(60)

if __name__ == "__main__":
    main()