from datetime import datetime
from dateutil import parser
import os
from reclaim_sdk.client import ReclaimClient
from reclaim_sdk.resources.task import Task, TaskPriority, EventColor
from reclaim_sdk.resources.hours import Hours
from reclaim_sdk.exceptions import (
    RecordNotFound,
    InvalidRecord,
    AuthenticationError,
    ReclaimAPIError,
)

reclaim_key = os.environ.get("RECLAIM_KEY")

ReclaimClient.configure(token=reclaim_key)

def complete(todoist_json_body):
    event_data = todoist_json_body["event_data"]

    try:
        task = Task(
                title = event_data["content"],
        )

        for existing_task in Task.list():
            if event_data["url"] in task.notes:
                task.id = existing_task.id
                break

        task.mark_complete()

    except RecordNotFound as e:
        print(f"Record not found: {e}")
    except InvalidRecord as e:
        print(f"Invalid record: {e}")
    except AuthenticationError as e:
        print(f"Authentication error: {e}")
    except ReclaimAPIError as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def create(todoist_json_body):
    event_data = todoist_json_body["event_data"]

    todoist_due_date = event_data["due"]["date"]
    reclaim_due_date = parser.isoparse(todoist_due_date)
    try:
        task = Task(
                title = event_data["content"],
                due = reclaim_due_date,
                priority = TaskPriority.P3,
        )

        task.notes              = (
            "Event Created By Tanchwa's Todoist:\n"
            f"{event_data['url']}"
        )
        task.duration           = 0.5
        task.max_work_duration  = 1.5
        task.min_work_duration  = 0.5

        # colour / time‑scheme
        label = (event_data.get("labels") or [None])[0]
        hour_ids = {h.title: h.id for h in Hours.list()}
        working  = hour_ids.get("Working Hours")
        personal = hour_ids.get("Personal Hours")

        if label == "reclaim":
            task.event_color   = EventColor.LAVENDER
            task.time_scheme_id = working
        else:  # default & "reclaim_personal"
            task.event_color   = EventColor.TANGERINE
            task.time_scheme_id = personal

        task.save()

    except RecordNotFound as e:
        print(f"Record not found: {e}")
    except InvalidRecord as e:
        print(f"Invalid record: {e}")
    except AuthenticationError as e:
        print(f"Authentication error: {e}")
    except ReclaimAPIError as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
