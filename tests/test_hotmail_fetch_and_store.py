#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fetchers.hotmail_fetcher import fetch_hotmail_emails
from utils.mongo_store import store_emails

def main():
    emails = fetch_hotmail_emails()
    print(f"✅ Fetched {len(emails)} Hotmail emails.")
    store_emails(emails, collection_name="agentic_emails")

if __name__ == "__main__":
    main()
