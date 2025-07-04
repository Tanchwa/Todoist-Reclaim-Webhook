import flaskr.reclaim_task as reclaim_task
from flask import Flask, Response, request, jsonify, abort
import hashlib
import hmac
import base64
import os

app = Flask(__name__)

todoist_key = os.environ.get("TODOIST_KEY").encode()

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

        event_name = todoist_task["event_name"]
        
        if event_name == "item:added":
            reclaim_task.create(todoist_task)
        elif event_name == "item:completed":
            reclaim_task.complete(todoist_task)

        return Response(status=200)
