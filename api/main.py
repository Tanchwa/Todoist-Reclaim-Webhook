from flask import Flask, Response, request, jsonify, abort
import hashlib
import hmac
import base64
import os
from datetime import datetime
from reclaim_sdk.client import ReclaimClient
from reclaim_sdk.resources.task import Task, TaskPriority, EventColor
from reclaim_sdk.resources.hours import Hours
from reclaim_sdk.exceptions import (
    RecordNotFound,
    InvalidRecord,
    AuthenticationError,
    ReclaimAPIError,
)

app = Flask(__name__)

todoist_key = os.environ.get("TODOIST_KEY").encode()
reclaim_key = os.environ.get("RECLAIM_KEY")

ReclaimClient.configure(token=reclaim_key)

@app.route('/webhook', methods=['POST'])
def accept_webhook_request():
    sha256sum_header = request.headers.get('X-Todoist-Hmac-SHA256')

    request_body = request.data
    digest = hmac.new(todoist_key, request_body, digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(digest).decode()

    if not hmac.compare_digest(sha256sum_header, signature):
        abort(401, description="Unable to verify integrity of incomming request")

    else:
        todoist_task = request.json
        print(todoist_task)

        event_data = todoist_task["event_data"]

        todoist_due_date = event_data["due"]["date"]
        arg1,arg2,arg3 = map(int, todoist_due_date.split("-"))
        reclaim_due_date = datetime(arg1,arg2,arg3)
        try:
            task = Task(
                    title = event_data["content"],
                    due = reclaim_due_date,
                    priority = TaskPriority.P3,
            )

            task.duration = 0.5 #will change this to be set dynamically with the AI interpriteation
            task.max_work_duration = 1.5
            task.min_work_duration = 0.5

            task.notes = (
                f" Event Created By Tanchwa's Todoist: \n{event_data['url']}"
            )
            task.event_color = EventColor.LAVENDER

            if event_data["labels"][0] == "reclaim":
                
                task.event_color = EventColor.LAVENDER
                task.time_scheme_id = Hours.list()[2].id ## should be working hours
            elif event_data["labels"][0] == "reclaim_personal":
                task.event_color = EventColor.TANGERINE
                task.time_scheme_id = Hours.list()[1].id ## should be personal hours
            else: #default to personal
                task.event_color = EventColor.TANGERINE
                task.time_scheme_id = Hours.list()[1].id ## should be personal hours
                

            task.up_next = True

            task.save()
            task.start()
            task.mark_incomplete()


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


        return Response(status=200)
