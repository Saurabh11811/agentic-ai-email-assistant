#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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


def load_session_ids():
    if os.path.exists(SESSION_FILE_PATH):
        with open(SESSION_FILE_PATH, "r") as f:
            return [ObjectId(_id) for _id in json.load(f)]
    return []



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

if __name__ == "__main__":
    if os.getenv("AGENTIC_DEV") == "1":
        print("🌍 Running Flask dev server on port 5050")
        app.run(host="0.0.0.0", port=5050, debug=False)
    else:
        print("❌ This script is meant to be run via `waitress` or `launchd` agent")
    
