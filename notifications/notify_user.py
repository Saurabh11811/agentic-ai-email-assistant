#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
notifications/notify_user.py

Central dispatcher for all notification modes (mac/webview/flask).
Filters, triggers popup, and updates notification status centrally.
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


from datetime import datetime
from collections import Counter
import json
from config_agentic import NOTIFY_MODE, NOTIFICATION_LABELS, MONGO_COLLECTION
from notifications.notify_mac_popup import notify_mac_summary_popup
from notifications.notify_webview_popup import start_webview
from utils.mongo_connection import get_mongo_collection

def save_emails_in_session(emails):
    if not emails:
        print("✅ No actionable emails to notify.")
        return
    print(f"🗂️ Notifying {len(emails)} emails")
    with open(SESSION_FILE_PATH, "w") as f:
        json.dump([str(email["_id"]) for email in emails], f)


def notify_actionable_emails(mode=None):
    collection = get_mongo_collection(MONGO_COLLECTION)
    mode = mode or NOTIFY_MODE

    query = {
        "action_classification.status": "Success",  # ✅ ensure classification succeeded
        "action_classification.label": {"$in": NOTIFICATION_LABELS},
        "notification_status.shown": {"$ne": True}
    }


    emails = list(collection.find(query))

    if not emails:
        print("✅ No new actionable emails to notify.")
        return

    print(f"🔔 Notifying {len(emails)} actionable emails via mode: {mode}")

    # Display based on mode
    if mode == "summary":
        notify_mac_summary_popup(emails)
    elif mode == "webview":
        start_webview(emails)
    elif mode == "flask":
        notify_mac_summary_popup(emails, link="http://localhost:5050/feedback")
        # notify_and_open_summary(emails)
        save_emails_in_session(emails)
    else:
        print(f"⚠️ Unknown notify mode: {mode}")
        return

    # Mark all as notified
    collection.update_many(
        {"_id": {"$in": [email["_id"] for email in emails]}},
        {"$set": {
            "notification_status": {
                "shown": True,
                "shown_at": datetime.utcnow().isoformat(),
                "mode": mode
            }
        }}
    )

    # Breakdown summary
    label_counts = Counter([email.get("action_classification", {}).get("label") for email in emails])
    print("\n🔎 Breakdown by action label:")
    for label, count in label_counts.items():
        print(f"   • {label}: {count}")

if __name__ == "__main__":
    notify_actionable_emails(mode='flask')
