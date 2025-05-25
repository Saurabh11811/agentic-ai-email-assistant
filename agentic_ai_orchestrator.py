#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from config_agentic import (
    EMAIL_ENABLED_GMAIL,
    EMAIL_ENABLED_HOTMAIL,
    RUN_FETCH, RUN_CLASSIFY, RUN_NOTIFY,
    MONGO_COLLECTION
)

from fetchers.gmail_fetcher import fetch_gmail_emails
from fetchers.hotmail_fetcher import fetch_hotmail_emails
from EmailCategoryClassifier import main as classify_categories
from EmailActionClassifier import main as classify_actions
from notifications.notify_user import notify_actionable_emails
from utils.mongo_store import store_emails

def fetch_all_emails():
    print("\n📥 Fetching emails...")
    all_emails = []

    if EMAIL_ENABLED_HOTMAIL:
        hotmail = fetch_hotmail_emails()
        if hotmail:
            print(f"✅ Hotmail: {len(hotmail)} emails")
            all_emails.extend(hotmail)
    else:
        print("⏭️ Skipping Hotmail (disabled in config)")

    if EMAIL_ENABLED_GMAIL:
        gmail = fetch_gmail_emails()
        if gmail:
            print(f"✅ Gmail: {len(gmail)} emails")
            all_emails.extend(gmail)
    else:
        print("⏭️ Skipping Gmail (disabled in config)")

    if all_emails:
        store_emails(all_emails, collection_name=MONGO_COLLECTION)
        print(f"📦 Stored {len(all_emails)} emails to MongoDB\n")
    else:
        print("⚠️ No new emails fetched.\n")


def classify_all():
    print("\n🤖 Running classification...")
    classify_categories()
    classify_actions()
    print("✅ Classification complete.\n")

def notify_all():
    print("\n🔔 Launching notification flow...")
    notify_actionable_emails()
    print("✅ Notification sent.\n")

def main():
    print("🚀 Starting Agentic AI Orchestration...\n")

    if RUN_FETCH:
        fetch_all_emails()
    if RUN_CLASSIFY:
        classify_all()
    if RUN_NOTIFY:
        notify_all()

    print("\n✅ Agentic AI flow complete.")

if __name__ == "__main__":
    main()
