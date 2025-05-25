#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 22 13:04:23 2025

@author: saurabh.agarwal
"""

import webview
import platform
import json
import sys
from datetime import datetime
from config_agentic import MONGO_COLLECTION
from utils.mongo_connection import get_mongo_collection

# Optional: Hide dock icon on macOS
try:
    import AppKit
    AppKit.NSApp.setActivationPolicy_(AppKit.NSApplicationActivationPolicyProhibited)
except Exception:
    pass

# HTML Template for Webview
html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Email Feedback</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background-color: #f9f9f9; }
        .block { margin-bottom: 15px; }
        .label { font-weight: bold; }
        textarea { width: 100%; height: 80px; }
        button { padding: 10px 20px; margin-right: 10px; font-size: 16px; }
    </style>
</head>
<body>
    <div id="content">
        <div class="block"><span class="label">Action:</span> <span id="label"></span></div>
        <div class="block"><span class="label">From:</span> <span id="sender"></span></div>
        <div class="block"><span class="label">Subject:</span> <span id="subject"></span></div>
        <div class="block"><span class="label">Reason:</span><br><span id="reason"></span></div>
        <div class="block"><span class="label">Your Notes:</span><br><textarea id="notes"></textarea></div>
        <div class="block">
            <button onclick="submit('👍')">👍 Helpful</button>
            <button onclick="submit('👎')">👎 Not Helpful</button>
            <button onclick="submit('⏭')">⏭ Skip</button>
        </div>
    </div>
    <script>
    async function loadEmail() {
        const response = await pywebview.api.get_email();
        const email = JSON.parse(response);
        const content = document.getElementById("content");

        if (email.done) {
            content.innerHTML = "<h2>✅ All feedback collected. Closing...</h2>";
            return;
        }

        content.innerHTML = `
            <div class="block"><span class="label">Action:</span> <span id="label">${email.label}</span></div>
            <div class="block"><span class="label">From:</span> <span id="sender">${email.sender}</span></div>
            <div class="block"><span class="label">Subject:</span> <span id="subject">${email.subject}</span></div>
            <div class="block"><span class="label">Reason:</span><br><span id="reason">${email.reason}</span></div>
            <div class="block"><span class="label">Your Notes:</span><br><textarea id="notes"></textarea></div>
            <div class="block">
                <button onclick="submit('👍')">👍 Helpful</button>
                <button onclick="submit('👎')">👎 Not Helpful</button>
                <button onclick="submit('⏭')">⏭ Skip</button>
            </div>
        `;
    }

    async function submit(response) {
        const notes = document.getElementById('notes')?.value || "";
        await pywebview.api.submit_feedback(response, notes);
        await loadEmail();
    }

    window.pywebviewReady = function () {
        loadEmail();
    };
    </script>
</body>
</html>
"""

class FeedbackAPI:
    def __init__(self, emails):
        self.emails = emails
        self.current_index = 0
        self.collection = get_mongo_collection(MONGO_COLLECTION)

    def get_email(self):
        if self.current_index < len(self.emails):
            email = self.emails[self.current_index]
            return json.dumps({
                "subject": email.get("subject", "[No Subject]"),
                "sender": email.get("sender", "[Unknown]"),
                "label": email.get("action_classification", {}).get("label", "Unknown"),
                "reason": email.get("action_classification", {}).get("rationale", ""),
                "id": str(email["_id"])
            })
        return json.dumps({"done": True})

    def submit_feedback(self, response, notes):
        if self.current_index >= len(self.emails):
            return True

        email = self.emails[self.current_index]
        feedback = {
            "userResponse": response,
            "notes": notes,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "popup_webview"
        }

        self.collection.update_one(
            {"_id": email["_id"]},
            {"$set": {
                "user_feedback": feedback
            }}
        )

        self.current_index += 1

        if self.current_index >= len(self.emails):
            webview.windows[0].destroy()
            sys.exit(0)

        return True

def start_webview(emails):
    if not emails:
        print("✅ No actionable emails to display.")
        return

    api = FeedbackAPI(emails)
    first = json.loads(api.get_email())

    if first.get("done"):
        print("✅ Nothing to show.")
        return

    webview.create_window(
        "Email Feedback Assistant",
        html=html_template,
        js_api=api,
        width=700,
        height=600
    )
    gui_mode='gtk'
    #webview.start(gui='gtk')
    webview.start(func=lambda: webview.windows[0].evaluate_js("loadEmail()"), gui=gui_mode)

if __name__ == "__main__":
    print("🔁 Webview popup module (not standalone). Use from notify_user.py")
