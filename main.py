from sheet import fetch_schedule
from gcalendar import sync_calendar_natural_key
from dotenv import load_dotenv
import time
import os

load_dotenv()

wait_time_seconds = os.environ.get('CYCLE_TIME', 60)

def main():
    while True:
        print("Fetching schedule from Google Sheets...")
        
        try:
            events = fetch_schedule()
            sync_calendar_natural_key(events)

            print("Sync complete. Waiting for the next cycle...")
        except Exception as e:
            print(f"Error occurred: {e}")

        time.sleep(int(wait_time_seconds))

if __name__ == "__main__":
    main()