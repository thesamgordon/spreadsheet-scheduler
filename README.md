# Spreadsheet Scheduler

Spreadsheet Scheduler copies events from a Google Sheet into a Google Calendar on a repeating schedule.

The app reads rows from a spreadsheet, converts each row into a calendar event, then keeps the configured calendar in sync. It can add new events, update matching events, delete events that are no longer in the sheet, and remove duplicates.

## Requirements

- Python 3
- `uv`
- A Google Cloud service account with access to the Google Sheets API and Google Calendar API
- A Google Sheet that contains the schedule rows
- A Google Calendar that the service account can edit

Use a dedicated calendar for this tool. The sync deletes events from the configured calendar when they are not present in the spreadsheet.

## Prepare The Template And Calendar

Make a copy of the [schedule template](https://docs.google.com/spreadsheets/d/1ySKnRdMRhkE0adIUnV_zsGf0r4J8bKObOKk5XyXa0k8/edit?gid=0#gid=0).

Then prepare Google access:

1. Create or choose a Google Cloud project.
2. Enable the Google Sheets API and Google Calendar API.
3. Create a service account and download its JSON key.
4. Share the Google Sheet with the service account email as a viewer.
5. Share the target Google Calendar with the service account email and allow it to make changes to events.

## Setup

Clone the repository:

```sh
git clone https://github.com/thesamgordon/spreadsheet-scheduler.git
cd spreadsheet-scheduler
```

Install `uv`:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

If `uv` is not found after installation, open a new terminal and return to this folder.

## Configuration

Copy the example environment file:

```sh
cp .env.example .env
```

Fill in `.env` with your Google Sheet, Google Calendar, and service account details.

| Variable | Required | Description |
| --- | --- | --- |
| `SHEET_ID` | Yes | The ID from the Google Sheet URL. |
| `SHEET_RANGE` | Yes | The range to read, such as `Sheet1!A2:E`. |
| `CALENDAR_ID` | Yes | The target Google Calendar ID. |
| `GOOGLE_SERVICE_ACCOUNT` | Yes | The service account JSON key as a single-line dictionary or JSON object. |
| `CYCLE_TIME` | No | Seconds to wait between syncs. Defaults to `60`. |
| `EVENT_PREFIX` | No | Text to add before event titles when missing. |
| `LOCATION` | No | Location to put on every calendar event. |

You can find the sheet ID in a Google Sheet URL:

```text
https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit
```

For `GOOGLE_SERVICE_ACCOUNT`, paste the downloaded service account JSON onto one line. Keep the private key line breaks escaped as `\n`.

## Run

Start the scheduler:

```sh
uv run --with-requirements requirements.txt python main.py
```

The app prints each sync cycle in the terminal. Leave it running for continuous sync.

## Expected Result

Each row from the template becomes one calendar event. Events use the `America/New_York` time zone, and `LOCATION` becomes the event location when configured.

On each cycle, the app makes the calendar match the spreadsheet range.

## Notes

- The app reads the configured sheet range only. Header rows should be left out of `SHEET_RANGE`.
- The sync currently uses all events in the configured calendar when deciding what to delete, so a dedicated calendar is recommended.
