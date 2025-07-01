from flask import Flask, Response, request, jsonify, abort
import hashlib
import hmac
import base64
import os

app = Flask(__name__)

todoist_key = os.environ.get("TODOIST_KEY").encode()

@app.route('/webhook', methods=['POST'])
def check_sha256sum():
    sha256sum_header = request.headers.get('X-Todoist-Hmac-SHA256')

    request_body = request.data
    digest = hmac.new(todoist_key, request_body, digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(digest).decode()

    if sha256sum_header != signature:
        abort(401, description="Unable to verify integrity of incomming request")

    else:
        return Response(status=200)
