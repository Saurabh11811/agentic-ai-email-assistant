#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 22 13:36:01 2025

@author: saurabh.agarwal
"""


import os
import sys

# Robust project root resolution
try:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
except NameError:
    project_root = os.path.abspath(os.path.join(os.getcwd(), ".."))

# Safe session path
SESSION_FILE_PATH = os.path.join(project_root, "session_ids.json")

# Ensure imports work
if project_root not in sys.path:
    sys.path.insert(0, project_root)



from flask import Flask, render_template_string, request, jsonify
from bson import ObjectId
from datetime import datetime
from collections import defaultdict, Counter
from utils.mongo_connection import get_mongo_collection
from config_agentic import MONGO_COLLECTION
import sys
import os, json, subprocess, threading, signal
from waitress import serve



app = Flask(__name__)
collection = get_mongo_collection(MONGO_COLLECTION)
session_email_ids = set()

# --- HTML UI ---
html_template = """
<!doctype html>
<html>
  <head>
    <title>Email Feedback</title>
    <style>
      body { font-family: Arial; margin: 30px; }
      h2 { margin-bottom: 5px; }
      .summary { font-weight: bold; margin-bottom: 10px; }
      .email { padding: 10px 0; border-bottom: 1px solid #ccc; }
      .buttons { margin-top: 5px; }
      button { padding: 5px 10px; margin-right: 5px; cursor: pointer; }
      details { margin-bottom: 15px; }
    </style>
    <script>
      async function sendFeedback(emailId, response) {
        const res = await fetch("/submit_feedback", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id: emailId, response: response, notes: "" })
        });
        if (res.ok) {
          document.getElementById("email-" + emailId).style.opacity = 0.4;
        }
      }
    </script>
  </head>
  <body>
    <h2>📬 You have {{ total }} actionable emails</h2>
    <div class="summary">
      {% for label, count in label_counts.items() %}
        {{ label }}: {{ count }} &nbsp;
      {% endfor %}
    </div>

    {% for label, group in grouped_emails.items() %}
    <details {% if loop.first %}open{% endif %}>
      <summary><strong>{{ label }} ({{ group|length }})</strong></summary>
      {% for email in group %}
        <div class="email" id="email-{{ email['_id'] }}">
          <strong>{{ loop.index }}.</strong> from <em>{{ email['sender'] }}</em> — {{ email['subject'] }}
          <div class="buttons">
            <button onclick="sendFeedback('{{ email['_id'] }}', '👍')">👍 Helpful</button>
            <button onclick="sendFeedback('{{ email['_id'] }}', '👎')">👎 Not Helpful</button>
            <button onclick="sendFeedback('{{ email['_id'] }}', '⏭')">⏭ Skip</button>
          </div>
        </div>
      {% endfor %}
    </details>
    {% endfor %}

    <p><em>Close this tab when you're done reviewing.</em></p>
  </body>
</html>
"""

# --- Utilities ---

# def persist_session_ids(emails):
#     with open(SESSION_FILE_PATH, "w") as f:
#         json.dump([str(email["_id"]) for email in emails], f)


def load_session_ids():
    if os.path.exists(SESSION_FILE_PATH):
        with open(SESSION_FILE_PATH, "r") as f:
            return [ObjectId(_id) for _id in json.load(f)]
    return []


# def kill_port_5050():
#     try:
#         output = subprocess.check_output(["lsof", "-ti", ":5050"]).decode().strip()
#         if output:
#             for pid in output.splitlines():
#                 print(f"🛑 Killing existing Flask process on port 5050 (PID {pid})")
#                 subprocess.run(["kill", "-9", pid])
#     except Exception as e:
#         print(f"⚠️ Could not kill port 5050: {e}")


# def shutdown_server_after_delay(seconds=120):
#     def delayed_kill():
#         global session_email_ids
#         print(f"🕒 Server will shut down in {seconds} seconds...")
#         threading.Event().wait(seconds)
#         session_email_ids.clear()
#         print("🛑 Auto-shutdown: Stopping Flask server")
#         os.kill(os.getpid(), signal.SIGTERM)
#     threading.Thread(target=delayed_kill, daemon=True).start()

# --- Flask routes ---

@app.route("/feedback")
def feedback_page():
    session_ids = load_session_ids()
    emails = list(collection.find({ "_id": {"$in": session_ids} }))

    label_counts = Counter(email.get("action_classification", {}).get("label", "Unknown") for email in emails)
    grouped = defaultdict(list)
    for email in emails:
        label = email.get("action_classification", {}).get("label", "Unknown")
        grouped[label].append(email)

    return render_template_string(
        html_template,
        total=len(emails),
        label_counts=label_counts,
        grouped_emails=grouped
    )

@app.route("/submit_feedback", methods=["POST"])
def submit_feedback():
    data = request.get_json()
    email_id = data["id"]
    response = data["response"]
    notes = data.get("notes", "")

    feedback_doc = {
        "userResponse": response,
        "notes": notes,
        "timestamp": datetime.utcnow().isoformat(),
        "source": "popup_flask"
    }

    collection.update_one(
        {"_id": ObjectId(email_id)},
        {"$set": {
            "user_feedback": feedback_doc
        }}
    )

    return jsonify(success=True)


# flask_process = None  # Track global Flask subprocess

# def start_flask_subprocess():
#     global flask_process
#     print("🚀 Starting Flask server as subprocess...")

#     import sys
#     import os

#     # Get full path to notify_flask_popup.py
#     script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "notify_flask_popup.py"))

#     # Use virtualenv Python if available
#     python_executable = os.environ.get("VIRTUAL_ENV")
#     if python_executable:
#         python_executable = os.path.join(python_executable, "bin", "python")
#     else:
#         python_executable = sys.executable  # fallback for dev use

#     # Set cwd to project root so relative imports work
#     project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

#     flask_process = subprocess.Popen(
#         [python_executable, script_path],
#         cwd=project_root
#     )


# def start_flask_subprocess():
#     global flask_process
#     print("🚀 Starting Flask server as subprocess...")

#     import sys
#     import os

#     # Use virtualenv Python
#     venv_python = os.path.join(os.environ.get("VIRTUAL_ENV", ""), "bin", "python")
#     if not os.path.exists(venv_python):
#         venv_python = sys.executable  # fallback

#     project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
#     os.chdir(project_root)

#     flask_process = subprocess.Popen([
#         venv_python, "-m", "waitress", "--host=0.0.0.0", "--port=5050", "notifications.notify_flask_popup:app"
#     ])




# def stop_flask_subprocess():
#     global flask_process
#     if flask_process and flask_process.poll() is None:
#         print("🛑 Stopping previous Flask subprocess...")
#         flask_process.send_signal(signal.SIGTERM)



# --- Entrypoint for notify_user ---
# def notify_and_open_summary(emails):
#     if not emails:
#         print("✅ No actionable emails to notify.")
#         return

#     global session_email_ids
#     session_email_ids.clear()
#     session_email_ids = set(email["_id"] for email in emails)

#     print(f"🗂️ Session emails: {len(session_email_ids)}")
#     print(f"📁 Using session file: {SESSION_FILE_PATH}")
#     if os.path.exists(SESSION_FILE_PATH):
#         print("Removing previous sessions IDs")
#         os.remove(SESSION_FILE_PATH)


#     persist_session_ids(emails)
#     kill_port_5050()
#     start_flask_subprocess()      # start fresh one with updated session




# if __name__ == "__main__":
#     print("🔁 Flask popup module (not standalone). Use from notify_user.py")
    # app.run(host="0.0.0.0", port=5050, debug=False)

    # print("🌐 Starting Flask server with Waitress on port 5050")
    # serve(app, host="0.0.0.0", port=5050)

if __name__ == "__main__":
    if os.getenv("AGENTIC_DEV") == "1":
        print("🌍 Running Flask dev server on port 5050")
        app.run(host="0.0.0.0", port=5050, debug=False)
    else:
        print("❌ This script is meant to be run via `waitress` or `launchd` agent")
    
